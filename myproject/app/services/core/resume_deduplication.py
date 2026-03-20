import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from sqlalchemy.orm import Session

from ... import models
from ...schemas import Resume

FINGERPRINT_SECTION = "__fuzzyhash__"
FINGERPRINT_VERSION = 1
SIMHASH_BITS = 64
DUPLICATE_SIMILARITY_THRESHOLD = 0.97
UPDATE_SIMILARITY_THRESHOLD = 0.78


@dataclass
class CandidateMatch:
    resume: models.Resume
    fingerprint: Optional[dict]
    similarity: float
    identity_overlap: int


@dataclass
class ResumeDecision:
    action: str
    existing_resume: Optional[models.Resume] = None
    similarity: float = 0.0


NORMALIZE_SPACE_RE = re.compile(r"\s+")
NON_ALNUM_RE = re.compile(r"[^a-z0-9@+]+")


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    lowered = value.strip().lower()
    lowered = NORMALIZE_SPACE_RE.sub(" ", lowered)
    return lowered


def _normalize_identifier(value: Optional[str]) -> str:
    text = _normalize_text(value)
    return NON_ALNUM_RE.sub("", text)


def build_resume_canonical_text(data: Dict[str, Any]) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return NORMALIZE_SPACE_RE.sub(" ", serialized).strip().lower()


def _word_ngrams(tokens: list[str], n: int = 3) -> Iterable[str]:
    if len(tokens) < n:
        if tokens:
            yield " ".join(tokens)
        return

    for index in range(len(tokens) - n + 1):
        yield " ".join(tokens[index:index + n])


def compute_simhash(text: str, bits: int = SIMHASH_BITS) -> int:
    tokens = NON_ALNUM_RE.sub(" ", text.lower()).split()
    shingles = list(_word_ngrams(tokens, n=3)) or tokens or [text.lower()]
    weights = [0] * bits

    for shingle in shingles:
        digest = hashlib.sha256(shingle.encode("utf-8")).digest()
        value = int.from_bytes(digest[: bits // 8], byteorder="big", signed=False)

        for bit in range(bits):
            mask = 1 << bit
            weights[bit] += 1 if value & mask else -1

    fingerprint = 0
    for bit, weight in enumerate(weights):
        if weight >= 0:
            fingerprint |= 1 << bit
    return fingerprint


def build_fingerprint_payload(text: str) -> dict:
    simhash = compute_simhash(text)
    return {
        "version": FINGERPRINT_VERSION,
        "algorithm": "simhash-64",
        "simhash": format(simhash, "016x"),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "length": len(text),
    }


def fingerprint_to_content(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True)


def parse_fingerprint_content(content: Optional[str]) -> Optional[dict]:
    if not content:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def hamming_similarity(left_hex: str, right_hex: str, bits: int = SIMHASH_BITS) -> float:
    left = int(left_hex, 16)
    right = int(right_hex, 16)
    distance = (left ^ right).bit_count()
    return 1 - (distance / bits)


def extract_candidate_identity(resume: Resume) -> dict:
    return {
        "email": _normalize_identifier(resume.email),
        "phone": _normalize_identifier(resume.phone),
        "linkedin": _normalize_identifier(resume.linkedin),
        "github": _normalize_identifier(resume.github),
        "name": _normalize_text(resume.name),
    }


def _identity_overlap(left: dict, right: dict) -> int:
    overlap = 0
    for key in ("email", "phone", "linkedin", "github"):
        if left.get(key) and left.get(key) == right.get(key):
            overlap += 1
    if left.get("name") and left.get("name") == right.get("name"):
        overlap += 1
    return overlap


def load_resume_fingerprints(db: Session) -> dict:
    rows = (
        db.query(models.ResumeChunk.resume_id, models.ResumeChunk.content)
        .filter(models.ResumeChunk.section == FINGERPRINT_SECTION)
        .all()
    )
    return {resume_id: parse_fingerprint_content(content) for resume_id, content in rows}


def upsert_resume_from_json(
    db: Session,
    jd: models.JobDescription,
    file_name: str,
    resume_json: Dict[str, Any],
    mapper,
) -> dict:
    """Upsert one parsed resume payload and flush fingerprint chunks immediately.

    The extra flush makes newly created fingerprints visible to later files in the
    same batch, so duplicate detection also works within a single upload request.
    """
    resume, chunks = mapper(resume_json)
    canonical_text = build_resume_canonical_text(resume_json)
    fingerprint = build_fingerprint_payload(canonical_text)
    decision = decide_resume_action(db, resume, fingerprint)

    if decision.action == "duplicate":
        return {
            "action": "duplicate",
            "resume_id": str(decision.existing_resume.resume_id) if decision.existing_resume else None,
            "duplicate": {
                "file_name": file_name,
                "existing_resume_id": str(decision.existing_resume.resume_id) if decision.existing_resume else None,
                "similarity": round(decision.similarity, 4),
                "message": "Duplicate resume rejected",
            },
            "refresh_resume_id": None,
        }

    target_resume: Optional[models.Resume] = decision.existing_resume
    action = "created"

    if target_resume is None:
        target_resume = models.Resume()
        db.add(target_resume)
        db.flush()
    else:
        action = "updated"
        (
            db.query(models.ScreenResult)
            .filter(
                models.ScreenResult.resume_id == target_resume.resume_id,
                models.ScreenResult.jd_id == jd.jd_id,
            )
            .delete(synchronize_session=False)
        )
        (
            db.query(models.ResumeChunk)
            .filter(models.ResumeChunk.resume_id == target_resume.resume_id)
            .delete(synchronize_session=False)
        )

    target_resume.name = resume.name
    target_resume.email = resume.email
    target_resume.phone = resume.phone
    target_resume.linkedin = resume.linkedin
    target_resume.github = resume.github
    target_resume.location = resume.location
    target_resume.years_of_experience = resume.years_of_experience
    db.flush()

    for chunk in chunks:
        db.add(models.ResumeChunk(
            resume_id=target_resume.resume_id,
            section=chunk.section,
            content=chunk.content,
            embedding=chunk.embedding,
        ))

    db.add(models.ResumeChunk(
        resume_id=target_resume.resume_id,
        section=FINGERPRINT_SECTION,
        content=fingerprint_to_content(fingerprint),
        embedding=None,
    ))
    db.flush()

    return {
        "action": action,
        "resume_id": str(target_resume.resume_id),
        "duplicate": None,
        "refresh_resume_id": str(target_resume.resume_id),
    }

def decide_resume_action(
    db: Session,
    incoming_resume: Resume,
    incoming_fingerprint: dict,
) -> ResumeDecision:
    incoming_identity = extract_candidate_identity(incoming_resume)
    existing_fingerprints = load_resume_fingerprints(db)

    candidates: list[CandidateMatch] = []
    for existing_resume in db.query(models.Resume).all():
        fingerprint = existing_fingerprints.get(existing_resume.resume_id)
        similarity = 0.0
        if fingerprint and fingerprint.get("simhash") and incoming_fingerprint.get("simhash"):
            similarity = hamming_similarity(
                fingerprint["simhash"],
                incoming_fingerprint["simhash"],
            )

        existing_identity = extract_candidate_identity(existing_resume)
        candidates.append(
            CandidateMatch(
                resume=existing_resume,
                fingerprint=fingerprint,
                similarity=similarity,
                identity_overlap=_identity_overlap(incoming_identity, existing_identity),
            )
        )

    exact_duplicate = next(
        (
            candidate
            for candidate in sorted(candidates, key=lambda item: item.similarity, reverse=True)
            if candidate.fingerprint
            and candidate.fingerprint.get("sha256") == incoming_fingerprint.get("sha256")
        ),
        None,
    )
    if exact_duplicate:
        return ResumeDecision("duplicate", exact_duplicate.resume, exact_duplicate.similarity)

    strong_duplicate = next(
        (
            candidate
            for candidate in sorted(candidates, key=lambda item: item.similarity, reverse=True)
            if candidate.similarity >= DUPLICATE_SIMILARITY_THRESHOLD
        ),
        None,
    )
    if strong_duplicate:
        return ResumeDecision("duplicate", strong_duplicate.resume, strong_duplicate.similarity)

    identity_match = next(
        (
            candidate
            for candidate in sorted(
                candidates,
                key=lambda item: (item.identity_overlap, item.similarity),
                reverse=True,
            )
            if candidate.identity_overlap > 0
        ),
        None,
    )
    if identity_match:
        return ResumeDecision("update", identity_match.resume, identity_match.similarity)

    fuzzy_update = next(
        (
            candidate
            for candidate in sorted(candidates, key=lambda item: item.similarity, reverse=True)
            if candidate.similarity >= UPDATE_SIMILARITY_THRESHOLD
            and incoming_identity.get("name")
            and incoming_identity.get("name") == _normalize_text(candidate.resume.name)
        ),
        None,
    )
    if fuzzy_update:
        return ResumeDecision("update", fuzzy_update.resume, fuzzy_update.similarity)

    return ResumeDecision("create")
