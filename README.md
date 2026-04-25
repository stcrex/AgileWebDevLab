# AgileWebDevLab

Repository for Agile Web Development coursework (lab submission).

## Issue #1 slice: Book common free slot → calendar event

This branch adds a **minimal runnable Flask app** (not the full StudySync draft) that implements the group feature from **Issue #1**: members see **common free time** for the current week, and **Book** persists a `CalendarEvent` for the **logged-in user** only (`event_type=group_study`), with JSON APIs, **CSRF** on mutating requests, and **SQLAlchemy** on SQLite under `instance/lab.db` (created on first run; `instance/` is gitignored).

Static UI mocks remain under `mock_pages/` for reference.

## Prerequisites

- Python 3.11+ (tested with 3.13)

## Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:5000/** — you will be redirected to log in, then to **/group/1**.

### Seeded demo accounts

| Email            | Password   |
|------------------|------------|
| `alice@lab.local` | `labdemo123` |
| `bob@lab.local`   | `labdemo123` |

Both users belong to **Demo Lab Group** (join code `LABDEMO1`). Seeded calendar events leave **common free slots** you can book from the UI.

## Tests

```bash
pytest
```

Uses a temporary SQLite file per test run (`WTF_CSRF_ENABLED=False` in the test app only).
