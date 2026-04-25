# AgileWebDevLab

Repository for Agile Web Development coursework (lab submission).

## Application overview

A **minimal Flask + SQLAlchemy + SQLite** app (Bootstrap + jQuery on the client) demonstrating:

1. **Study group common free time** — see merged free slots for the week and **book** a slot; the server stores a **`CalendarEvent`** for the signed-in user (`event_type=group_study`), with CSRF-protected JSON APIs.
2. **Exam preparation resources** — each **exam session** can have **multiple structured links** (`exam_resources`: title + URL), with list/create/patch/delete JSON APIs, URL validation (`http`/`https` only), and an exam detail page to manage links.

Static HTML mocks for early UI exploration remain under `mock_pages/`.

## Prerequisites

- Python 3.11+ (tested with 3.13)

## Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:5000/** — after sign-in you land on **Exams**. Use the navbar to open **Group** for the booking flow, or open an exam to add/remove resource links.

### Seeded demo accounts

| Email             | Password     |
|-------------------|--------------|
| `alice@lab.local` | `labdemo123` |
| `bob@lab.local`   | `labdemo123` |

Alice has a sample **exam session** with one starter resource; both users belong to **Demo Lab Group** (join code `LABDEMO1`) with seeded calendar events so common free slots exist for booking.

## Tests

```bash
pytest
```

Uses a temporary SQLite file per test run (`WTF_CSRF_ENABLED=False` in the test app only).
