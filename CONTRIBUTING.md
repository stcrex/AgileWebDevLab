# Contributing to AgileWebDevLab

This guide is for **group members and reviewers** working in this repository for Agile Web Development checkpoints and submission.

## Local setup

Use the same steps as **README.md** under **section 3 (How to launch the application)** (virtual environment + `pip install -r requirements.txt` + `python run.py`).

Before every push that touches Python code:

```bash
pytest -v
```

If you changed templates, auth, or navigation, also run **Selenium** locally when Chrome is available:

```bash
pytest tests/selenium -v
```

## Git and GitHub hygiene

1. **Configure Git identity** (must match how you want commits attributed on GitHub):

   ```bash
   git config user.name "Your Name"
   git config user.email "you@example.com"
   ```

2. **Branch names:** prefer short prefixes, e.g. `feat/…`, `fix/…`, `docs/…`.

3. **Commits:** imperative subject line, ~72 characters or less; body optional but explain *why* when the diff is not obvious.

4. **Pull requests:** link the **issue** you close or continue; describe scope, how to test, and any DB reset (`instance/lab.db`) the reviewer must perform.

5. **Do not commit** `instance/`, `.venv/`, `.env`, or local IDE junk (see `.gitignore`).

## Code expectations

- Match existing patterns: **Flask blueprints**, **SQLAlchemy** models, **JSON + CSRF** for mutating APIs used from jQuery.
- Keep changes **scoped** to the issue; avoid unrelated refactors in the same PR.
- If you add a new dependency, pin a sensible range in `requirements.txt` and mention it in the PR.

## Documentation

- **README.md** is the rubric-facing runbook (purpose, members table, launch, tests). Update it when behaviour or commands change.
- **This file** is for workflow and review expectations.

## Questions

Use your unit’s preferred channel (LMS forum, lab, or GitHub Discussions if enabled). For grading-related requirements, treat the official unit outline and rubric as authoritative.
