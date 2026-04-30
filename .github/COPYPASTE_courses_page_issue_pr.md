# Copy-paste: GitHub Issue + PR (English only)

Use the fenced blocks below in GitHub. **Issue title, issue body, PR title, and PR description are entirely in English.**

---

## Issue — Title

```
Improve /courses page: replace stub with planner + catalog aligned to Exams UI
```

---

## Issue — Body

```markdown
## Problem

The `/courses` route was backed by a generated **stub template** (`courses_stub.html`) with hundreds of placeholder lines and a navbar layout that did not match **Exams** and other lab pages. The page felt disconnected from the rest of the application and provided little value beyond avoiding dead navigation targets.

## Goals

- **Visual consistency**: use the same top navigation pattern as `exams_list.html` (Bootstrap dark shell, aligned button group).
- **Useful, read-only content** for this iteration:
  - **From exam planner**: aggregate the signed-in user’s `ExamSession` rows by `course_code`, show how many sessions exist and the next start time, and link to the relevant exam detail view.
  - **Saved catalog**: list `Course` rows where `owner_id` is the current user.
  - **Shortcuts**: quick links to Exams, Group, and Reminders.
- **Demo data**: if the seeded `alice@lab.local` account has no `Course` rows, insert two sensible default rows on startup (idempotent).
- **Maintenance**: stop the sidebar stub generator from overwriting courses; maintain `templates/courses.html` by hand.

## Acceptance criteria

- [ ] `/courses` requires authentication and renders without the old bulk stub paragraphs.
- [ ] Navbar matches the Exams page structure; **Courses** is the active tab.
- [ ] “From your exam planner” shows a table or a clear empty state backed by real `ExamSession` data.
- [ ] “Saved catalog” lists `Course` records for `owner_id == current_user.id`.
- [ ] `pytest -m "not selenium"` passes.
- [ ] `scripts/generate_flask_sidebar_stub_templates.py` no longer writes `courses_stub.html`.

## Out of scope

- Browser CRUD for creating or editing `Course` entities.
- Surfacing `TimetableEvent` on this page.
- Full internationalisation or accessibility audit beyond basic markup.

## Implementation notes

- Route endpoint remains `sidebar_stubs.courses_stub`; template is `templates/courses.html` so existing `url_for` calls keep working.
- Seed helper: `_seed_default_courses_if_missing()` in `app/__init__.py` (runs only when Alice has zero owned courses).
```

---

## PR — Title

```
feat(ui): redesign Courses page with exam rollup and saved catalog
```

---

## PR — Description

```markdown
## Summary

Replaces the generated **courses stub** with **`templates/courses.html`**, aligned with the **Exams** page shell. The view aggregates **course codes** from the user’s **exam sessions** and lists **saved `Course` rows** for that account. Adds an **idempotent seed** for the demo Alice user so the catalog is non-empty on fresh databases.

## Motivation

The previous `/courses` page looked and behaved unlike the rest of the lab app. This change turns it into a small hub grounded in existing models (`ExamSession.course_code`, `Course`).

## Changes

| Location | Description |
|----------|-------------|
| `app/blueprints/sidebar_stubs.py` | `courses_stub` computes `from_exams` and `catalog_courses`, renders `courses.html`. |
| `templates/courses.html` | New UI: planner table, catalog card, shortcuts; navbar matches exams. |
| `templates/courses_stub.html` | Removed (superseded). |
| `app/__init__.py` | `_seed_default_courses_if_missing()` after exam seed; adds CITS3403 and LAB for Alice when missing. |
| `scripts/generate_flask_sidebar_stub_templates.py` | Regenerates only reminders and preferences templates; courses is documented as hand-maintained. |

## How to test

1. `pytest -m "not selenium" -q`
2. Sign in as `alice@lab.local`, open **Courses**: expect a planner row for **LAB** (seeded exam) and two catalog rows when the catalog was previously empty.
3. Sign in as `bob@lab.local`, open **Courses**: planner empty if Bob has no exams; catalog empty unless Bob owns `Course` rows.

## Risk

**Low.** Read-only UI plus optional seed; public URL and blueprint name unchanged.

## Rollback

Revert this pull request. Restore a stub template only if you depend on the old generator workflow.

---

Closes #[ISSUE_NUMBER]
```

Replace `[ISSUE_NUMBER]` with the GitHub issue number (or paste the full issue URL on the `Closes` line if your team uses that convention).

---

_End of file._
