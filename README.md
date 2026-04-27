# AgileWebDevLab

Minimal **Flask** web application for Agile Web Development coursework: study-group scheduling, exam preparation resources, and optional read-only exam sharing. This document is written so a marker or new teammate can **clone the repo once** and follow **sections 3–5** without guesswork.

---

## 1. Purpose and design

**Purpose:** give students a small but coherent **client–server** example: HTML templates and jQuery on the browser, JSON APIs with **CSRF** protection, **Flask-Login** sessions, and **SQLite** persistence via **SQLAlchemy**.

**Design (high level):**

| Area | Behaviour |
|------|-----------|
| **Study groups** | Two seeded users share a group. The server computes **common free time** for Monday–Friday and lets a member **book** a slot, persisting a personal **`CalendarEvent`** (`event_type=group_study`). |
| **Exams** | Each user owns **exam sessions**. A session has many **`exam_resources`** (title + URL) with validation and JSON CRUD. |
| **Sharing** | The exam owner may enable a random **`share_token`**. Visitors hit a **public read-only** URL without logging in; revoked or unknown tokens yield a generic **404** page. |
| **Sign-in UX** | **Email + password** is the only working path on **`/login`**. OAuth-style tiles are **disabled** with clear copy; see `templates/login.html`, `static/css/auth_sso_facade.css`, and **`mock_pages/login.html`** for the parallel static mock. |

**Who uses it:** demo markers and the project group for checkpoints and final submission. **Not** intended for production deployment; default `SECRET_KEY` is for local use only.

---

## 2. Group members

Replace the placeholder rows below with your **actual** group data before final submission (UWA policy: use the identifiers your unit expects).

| UWA ID | Full name | GitHub username |
|--------|-----------|-------------------|
| *e.g. 12345678* | *Replace with legal name* | *@github-handle* |
| *e.g. 23456789* | *Replace* | *@github-handle* |
| *e.g. 34567890* | *Replace* | *@github-handle* |

If your group has fewer than three people, delete extra rows. If you have four, add another row.

---

## 3. How to launch the application

### 3.1 Prerequisites

- **Python 3.11+** (development verified on Python 3.13).
- A terminal and a modern browser.

### 3.2 First-time setup (virtual environment + dependencies)

From the repository root:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (cmd.exe)**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Start the development server

With the virtual environment **activated**:

```bash
python run.py
```

You should see logging similar to `Running on http://127.0.0.1:5000`.

Open **http://127.0.0.1:5000/** in the browser. Unauthenticated visitors are sent to the **login** page; after sign-in you land on **Exams**.

### 3.4 Demo accounts (seeded on first run)

| Email | Password |
|-------|----------|
| `alice@lab.local` | `labdemo123` |
| `bob@lab.local` | `labdemo123` |

Alice owns a sample exam with one starter link; both users are in **Demo Lab Group** (`LABDEMO1`) with calendar events so **Group → common free slots** is non-empty.

### 3.5 Useful URLs (after login)

| Path | Description |
|------|-------------|
| `/exams` | List of your exam sessions |
| `/exams/<id>` | Exam detail: resources + share link controls |
| `/group/1` | Group workspace for the seeded group |
| `/exams/shared/<token>` | **Public** read-only exam (only when a share token exists) |

### 3.6 Database and local files

- SQLite file: **`instance/lab.db`** (created automatically; the `instance/` directory is gitignored).
- To **reset all data** (including schema migrations applied at runtime), stop the server, delete `instance/lab.db`, and start again so seeds re-run.

### 3.7 Optional configuration

| Variable | Meaning |
|----------|---------|
| `SECRET_KEY` | Flask session signing. Set in production; defaults to an insecure dev value in code. |

Example (Unix):

```bash
export SECRET_KEY="choose-a-long-random-string"
python run.py
```

---

## 4. How to run the tests

There are two layers:

| Layer | Location | What it checks |
|--------|----------|----------------|
| **Unit / API** | `tests/test_*.py` | Flask test client, isolated SQLite per `tmp_path`, CSRF **disabled** for speed. |
| **Browser (Selenium)** | `tests/selenium/` | A **real HTTP server** in a background thread + **Chrome** driving the UI (CSRF **enabled** on that app instance). |

### 4.1 Unit and API tests (default, no browser)

Activate the same `.venv` as in section 3, then from the repo root:

```bash
pytest
```

Run only non-browser tests:

```bash
pytest -m "not selenium"
```

Single-file examples:

```bash
pytest tests/test_exam_share.py -v
pytest tests/test_group_book.py -v
```

`tests/conftest.py` builds the app with **`TESTING=True`**, **`WTF_CSRF_ENABLED=False`**, and a **temporary SQLite** file so tests never touch your personal `instance/lab.db`.

### 4.2 Selenium end-to-end tests (live server)

**Prerequisites:** Google **Chrome** or **Chromium** installed on the machine running tests. Selenium **4.6+** resolves a matching **ChromeDriver** automatically in most setups.

From the repo root:

```bash
pytest tests/selenium -v
```

What is covered today:

- **Happy path:** open `/login`, sign in as `alice@lab.local` / `labdemo123`, expect the **Exams** page (`<title>` contains “Exams”, heading “My exam sessions”).
- **Auth failure:** wrong password → **danger** flash on the login page; visiting **`/exams`** afterwards redirects to **`/login`** (still unauthenticated).

Optional: run the browser **visibly** (debugging):

```bash
HEADLESS=0 pytest tests/selenium -v
```

If Chrome or the driver cannot start, the affected tests **`pytest.skip`** with a short reason so headless CI without a browser can still run **`pytest -m "not selenium"`** cleanly.

### 4.3 Configuration

**`pytest.ini`** sets `pythonpath = .` and registers the **`selenium`** marker (see `@pytest.mark.selenium` on browser tests).

### 4.4 Expected result

After `pip install -r requirements.txt`, **`pytest -m "not selenium"`** should be fully green on any machine. **`pytest tests/selenium`** should be green on a workstation with Chrome available; otherwise those tests **skip** instead of failing the job, unless you treat skips as failures in your own CI policy.

---

## 5. Repository layout (quick reference)

| Path | Role |
|------|------|
| `app/` | Application package (`create_app`, models, blueprints, services) |
| `templates/` | Jinja HTML |
| `static/js/` | Client scripts (jQuery + CSRF header on mutating calls) |
| `static/css/auth_sso_facade.css` | Bulky, token-oriented stylesheet attached to the login page so disabled “social” controls stay visually subordinate |
| `tests/` | Pytest modules (API/unit) |
| `tests/selenium/` | Selenium E2E tests (live `werkzeug` server + Chrome) |
| `mock_pages/` | Static HTML mocks (open files in a browser; not served by Flask). **Global sidebar** links for **Courses**, **Reminders**, and **Preferences** resolve to real placeholder files (`courses.html`, `reminders.html`, `preferences.html`) instead of `href="#"`. Optional audit log: `NAV_AUDIT.txt`. Regenerate bulky placeholders with `python3 scripts/generate_nav_placeholder_pages.py`. The timetable mock uses **grid-only** list control (disabled + hint). |
| `source_pages/` | **Alias / audit hub** for brief terminology: points to the same static story as `mock_pages/`; see `source_pages/README.md` and the drift appendix. |
| `docs/SOURCE_PAGES_DRIFT_AUDIT.md` | **Bulk drift matrix** (`mock_pages` ↔ `templates`) + synthetic checklist rows; regenerate via `python3 scripts/generate_source_pages_drift_audit.py`. |
| `scripts/` | Helper generators (`generate_nav_placeholder_pages.py`, `generate_source_pages_drift_audit.py`, …). |
| `run.py` | Dev entrypoint |
| `requirements.txt` | Python dependencies |

---

## 6. Contributor guide

For branching conventions, PR checklist, and Git attribution, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

---

## 7. Troubleshooting

| Problem | Things to try |
|---------|----------------|
| `ModuleNotFoundError: No module named 'app'` | Run `pytest` from the **repository root**, or use `pytest` (not `python -m pytest` from a wrong cwd). `pytest.ini` sets `pythonpath`. |
| `Address already in use` | Another process uses port 5000. Stop it or change the port in `run.py`. |
| Old database missing new columns | Delete `instance/lab.db` and restart once, or rely on the small SQLite `ALTER` helpers in `app/__init__.py` where present. |
| Login always fails | Use the **seeded** emails exactly (`alice@lab.local`), password `labdemo123`. |
| Selenium tests skip | Install **Chrome**; run with `HEADLESS=0` to see errors; ensure no corporate proxy blocks driver download. |
