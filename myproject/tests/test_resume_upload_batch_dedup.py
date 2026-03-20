import os
import unittest
from uuid import uuid4

os.environ.setdefault("DATABASE_HOSTNAME", "localhost")
os.environ.setdefault("DATABASE_PORT", "5432")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("SECRET_KEY", "secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app import models, schemas
from app.services.core.resume_deduplication import FINGERPRINT_SECTION, upsert_resume_from_json


class FakeQuery:
    def __init__(self, session, entities):
        self.session = session
        self.entities = entities
        self.conditions = []

    def filter(self, *conditions):
        self.conditions.extend(conditions)
        return self

    def all(self):
        if len(self.entities) == 1 and self.entities[0] is models.Resume:
            return list(self.session.persisted_resumes)

        if (
            len(self.entities) == 2
            and getattr(self.entities[0], "class_", None) is models.ResumeChunk
            and getattr(self.entities[0], "key", None) == "resume_id"
            and getattr(self.entities[1], "class_", None) is models.ResumeChunk
            and getattr(self.entities[1], "key", None) == "content"
        ):
            rows = self._apply_filters(self.session.persisted_chunks)
            return [(chunk.resume_id, chunk.content) for chunk in rows]

        if len(self.entities) == 1 and self.entities[0] is models.ResumeChunk:
            return list(self._apply_filters(self.session.persisted_chunks))

        if len(self.entities) == 1 and self.entities[0] is models.ScreenResult:
            return list(self._apply_filters(self.session.persisted_screen_results))

        raise AssertionError(f"Unsupported query entities: {self.entities!r}")

    def delete(self, synchronize_session=False):
        if len(self.entities) == 1 and self.entities[0] is models.ResumeChunk:
            rows = self._apply_filters(self.session.persisted_chunks)
            self.session.persisted_chunks = [chunk for chunk in self.session.persisted_chunks if chunk not in rows]
            return len(rows)

        if len(self.entities) == 1 and self.entities[0] is models.ScreenResult:
            rows = self._apply_filters(self.session.persisted_screen_results)
            self.session.persisted_screen_results = [
                result for result in self.session.persisted_screen_results if result not in rows
            ]
            return len(rows)

        raise AssertionError(f"Unsupported delete entities: {self.entities!r}")

    def _apply_filters(self, rows):
        return [row for row in rows if all(self._matches(row, condition) for condition in self.conditions)]

    @staticmethod
    def _matches(row, condition):
        left = getattr(condition, "left", None)
        right = getattr(condition, "right", None)
        field_name = getattr(left, "key", None)
        if field_name is None:
            raise AssertionError(f"Unsupported filter condition: {condition!r}")
        expected = getattr(right, "value", None)
        return getattr(row, field_name) == expected


class FakeSession:
    def __init__(self):
        self.pending = []
        self.persisted_resumes = []
        self.persisted_chunks = []
        self.persisted_screen_results = []

    def add(self, obj):
        self.pending.append(obj)

    def flush(self):
        for obj in self.pending:
            if isinstance(obj, models.Resume):
                if obj.resume_id is None:
                    obj.resume_id = uuid4()
                if obj not in self.persisted_resumes:
                    self.persisted_resumes.append(obj)
            elif isinstance(obj, models.ResumeChunk):
                if obj.chunk_id is None:
                    obj.chunk_id = uuid4()
                self.persisted_chunks.append(obj)
            elif isinstance(obj, models.ScreenResult):
                if obj.screen_result_id is None:
                    obj.screen_result_id = uuid4()
                self.persisted_screen_results.append(obj)
            else:
                raise AssertionError(f"Unsupported object type: {type(obj)!r}")
        self.pending = []

    def commit(self):
        self.flush()

    def query(self, *entities):
        return FakeQuery(self, entities)


class ResumeUploadBatchDedupTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeSession()
        self.jd = models.JobDescription(jd_id=101, requirement_id="REQ-101", job_title="Engineer")

    @staticmethod
    def mapper_factory(name, email, experience_text):
        def mapper(_resume_json):
            resume = schemas.Resume(
                name=name,
                email=email,
                phone="1234567890",
                linkedin="https://linkedin.com/in/test",
                github="https://github.com/test",
                location="Remote",
                years_of_experience=4.0,
            )
            chunks = [
                schemas.ResumeChunk(section="experience", content=experience_text, embedding=[0.1, 0.2]),
                schemas.ResumeChunk(section="skills", content="python,sql", embedding=[0.3, 0.4]),
            ]
            return resume, chunks

        return mapper

    def test_fresh_resume_is_created(self):
        result = upsert_resume_from_json(
            db=self.db,
            jd=self.jd,
            file_name="fresh.pdf",
            resume_json={"candidate": "fresh"},
            mapper=self.mapper_factory("Jane Fresh", "jane@example.com", "Built APIs"),
        )

        self.assertEqual(result["action"], "created")
        self.assertEqual(len(self.db.persisted_resumes), 1)
        self.assertEqual(len(self.db.persisted_chunks), 3)
        self.assertEqual(self.db.persisted_chunks[-1].section, FINGERPRINT_SECTION)

    def test_duplicate_resume_is_rejected_within_same_batch(self):
        first = upsert_resume_from_json(
            db=self.db,
            jd=self.jd,
            file_name="candidate-a.pdf",
            resume_json={"candidate": "same"},
            mapper=self.mapper_factory("Jane Batch", "jane@example.com", "Built APIs"),
        )
        second = upsert_resume_from_json(
            db=self.db,
            jd=self.jd,
            file_name="candidate-a-copy.pdf",
            resume_json={"candidate": "same"},
            mapper=self.mapper_factory("Jane Batch", "jane@example.com", "Built APIs"),
        )

        self.assertEqual(first["action"], "created")
        self.assertEqual(second["action"], "duplicate")
        self.assertEqual(second["duplicate"]["existing_resume_id"], first["resume_id"])
        self.assertEqual(len(self.db.persisted_resumes), 1)
        self.assertEqual(len([chunk for chunk in self.db.persisted_chunks if chunk.section == FINGERPRINT_SECTION]), 1)

    def test_changed_resume_updates_existing_candidate(self):
        first = upsert_resume_from_json(
            db=self.db,
            jd=self.jd,
            file_name="candidate-v1.pdf",
            resume_json={"candidate": "version-1"},
            mapper=self.mapper_factory("Jane Update", "jane@example.com", "Built APIs"),
        )

        refreshed_screen = models.ScreenResult(
            resume_id=self.db.persisted_resumes[0].resume_id,
            jd_id=self.jd.jd_id,
            match_score=70,
            skills_match="python",
            summary="old",
        )
        self.db.add(refreshed_screen)
        self.db.flush()

        second = upsert_resume_from_json(
            db=self.db,
            jd=self.jd,
            file_name="candidate-v2.pdf",
            resume_json={"candidate": "version-2", "new_skill": "kafka"},
            mapper=self.mapper_factory("Jane Update", "jane@example.com", "Built APIs and Kafka pipelines"),
        )

        self.assertEqual(first["action"], "created")
        self.assertEqual(second["action"], "updated")
        self.assertEqual(second["resume_id"], first["resume_id"])
        self.assertEqual(len(self.db.persisted_resumes), 1)
        self.assertFalse(self.db.persisted_screen_results)
        fingerprint_chunks = [chunk for chunk in self.db.persisted_chunks if chunk.section == FINGERPRINT_SECTION]
        self.assertEqual(len(fingerprint_chunks), 1)
        self.assertIn("Kafka pipelines", self.db.persisted_chunks[0].content)


if __name__ == "__main__":
    unittest.main()
