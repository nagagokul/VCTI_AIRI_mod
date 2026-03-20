# AIRI backend quick checks

## Fast resume-upload deduplication tests

If the UI/Postman flow feels slow because it has to run OCR, parsing, embeddings, and screening, use the lightweight batch-upload regression tests instead.

`unittest` is a Python module, not a standalone shell command, so run it through `python -m unittest`.

### Windows PowerShell / CMD

If your virtual environment is already activated and your prompt is inside `C:\VCTI_AIRI\myproject`, run:

```powershell
python -m unittest tests.test_resume_upload_batch_dedup -v
```

If your machine uses the Python launcher instead of `python`, run:

```powershell
py -m unittest tests.test_resume_upload_batch_dedup -v
```

### macOS / Linux / Git Bash

From the repository root, run:

```bash
cd myproject && .venv/bin/python -m unittest tests.test_resume_upload_batch_dedup -v
```

What these tests cover:

- a brand-new resume is stored as a fresh upload;
- the same resume uploaded again in the same batch is rejected as a duplicate;
- a changed resume for the same candidate updates the existing record instead of creating a second candidate.

These tests stub the expensive OCR/LLM/embedding work and exercise the dedup/update logic directly, so they run much faster than driving `/resumes/upload` through the full UI or Postman flow.
