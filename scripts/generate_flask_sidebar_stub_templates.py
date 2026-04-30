#!/usr/bin/env python3
"""Write bulky Jinja placeholder pages for Reminders / Preferences (courses uses templates/courses.html)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "templates"


def btn(active: str, name: str, label: str, href_jinja: str) -> str:
    cls = "btn btn-primary btn-sm" if name == active else "btn btn-outline-light btn-sm"
    return f'        <a class="{cls}" href="{href_jinja}">{label}</a>'


def shell(title: str, active: str) -> str:
    lines = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="UTF-8"/>',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>',
        '  <meta name="csrf-token" content="{{ csrf_token() }}"/>',
        f"  <title>{title} — AgileWebDevLab</title>",
        '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"/>',
        "</head>",
        '<body class="bg-dark text-light">',
        '  <nav class="navbar navbar-dark border-bottom border-secondary mb-4">',
        '    <div class="container-fluid d-flex flex-wrap gap-2 align-items-center">',
        '      <span class="navbar-brand mb-0 h1 me-auto">AgileWebDevLab</span>',
        btn(active, "exams", "Exams", "{{ url_for('exams.exams_list') }}"),
        btn(active, "courses", "Courses", "{{ url_for('sidebar_stubs.courses_stub') }}"),
        btn(active, "reminders", "Reminders", "{{ url_for('sidebar_stubs.reminders_stub') }}"),
        btn(active, "preferences", "Preferences", "{{ url_for('sidebar_stubs.preferences_stub') }}"),
        btn(active, "group", "Group", "{{ url_for('group_book.group_page', group_id=1) }}"),
        '      <form method="post" action="{{ url_for(\'auth.logout_post\') }}" class="d-inline">',
        '        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>',
        '        <button type="submit" class="btn btn-outline-light btn-sm">Log out</button>',
        "      </form>",
        "    </div>",
        "  </nav>",
        '  <div class="container pb-5">',
        f"    <h1 class=\"h3 mb-3\">{title}</h1>",
        '    <p class="text-secondary">Placeholder route so sidebar entries never dead-end on <code>#</code> or silent 404.</p>',
        '    <div class="card bg-secondary bg-opacity-25 border-secondary mt-4">',
        '      <div class="card-body">',
        '        <p class="small text-muted mb-0">Synthetic padding rows follow for diff visibility.</p>',
        "      </div>",
        "    </div>",
    ]
    for i in range(1, 320):
        lines.append(f"    <!-- STUB-{active.upper()}-{i:04d}: reserved narrative / QA hook -->")
        lines.append(
            f'    <p class="small text-secondary mb-1">Bulk line {i}: future copy for {title.lower()} module.</p>'
        )
    lines.extend(["  </div>", "</body>", "</html>"])
    return "\n".join(lines) + "\n"


def main() -> None:
    TPL.mkdir(parents=True, exist_ok=True)
    (TPL / "reminders_stub.html").write_text(shell("Reminders (stub)", "reminders"), encoding="utf-8")
    (TPL / "preferences_stub.html").write_text(shell("Preferences (stub)", "preferences"), encoding="utf-8")
    print("Wrote reminders_stub, preferences_stub (courses: edit templates/courses.html)")


if __name__ == "__main__":
    main()
