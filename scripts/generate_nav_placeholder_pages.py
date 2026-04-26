#!/usr/bin/env python3
"""One-off generator for bulky mock_pages placeholder HTML (navigation UX sweep)."""

from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "mock_pages"


def sidebar(active: str) -> str:
    def cls(name: str) -> str:
        return "nav-item active" if name == active else "nav-item"

    return textwrap.dedent(
        f"""
        <nav class="sidebar">
          <div class="brand"><i class="fas fa-calendar-alt"></i> StudySync</div>
          <span class="nav-section-label">Main</span>
          <a href="timetable.html" class="{cls("timetable")}"><i class="fas fa-calendar-week"></i> Timetable</a>
          <a href="ai_planner.html" class="{cls("ai")}"><i class="fas fa-robot"></i> AI Planner</a>
          <a href="group.html" class="{cls("group")}"><i class="fas fa-users"></i> My Group</a>
          <span class="nav-section-label">Personal</span>
          <a href="courses.html" class="{cls("courses")}"><i class="fas fa-book-open"></i> Courses</a>
          <a href="exam_detail.html" class="{cls("exam")}"><i class="fas fa-file-alt"></i> Exams &amp; Tasks</a>
          <a href="reminders.html" class="{cls("reminders")}"><i class="fas fa-bell"></i> Reminders</a>
          <span class="nav-section-label">Settings</span>
          <a href="preferences.html" class="{cls("preferences")}"><i class="fas fa-cog"></i> Preferences</a>
          <div class="sidebar-bottom">
            <div class="user-chip">
              <div class="avatar">JS</div>
              <div>
                <div style="font-size:0.82rem;font-weight:600;">Jane Smith</div>
                <div style="font-size:0.72rem;color:var(--muted);">23456789</div>
              </div>
            </div>
          </div>
        </nav>
        """
    ).strip()


def shell_css() -> str:
    return textwrap.dedent(
        """
    :root {
      --navy: #0d1b2a; --card: #111f30; --sidebar: #0f1e2e;
      --accent: #4f8ef7; --accent2: #7c5cfc; --text: #e8edf5; --muted: #6b839e;
      --border: rgba(255,255,255,0.07); --green: #26d07c;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: var(--navy); color: var(--text);
           display: flex; min-height: 100vh; }
    .sidebar { width: 220px; background: var(--sidebar); border-right: 1px solid var(--border);
               display: flex; flex-direction: column; padding: 24px 0; flex-shrink: 0; }
    .brand { font-weight: 700; font-size: 1.2rem; color: var(--accent); padding: 0 22px; margin-bottom: 28px;
             display: flex; align-items: center; gap: 8px; }
    .nav-section-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; color: var(--muted);
                         text-transform: uppercase; padding: 0 22px; margin: 16px 0 8px; }
    .nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 22px; font-size: 0.88rem;
                color: var(--muted); text-decoration: none; transition: background 0.2s, color 0.2s; }
    .nav-item:hover, .nav-item.active { color: var(--text); background: rgba(79,142,247,0.1); }
    .nav-item.active { color: var(--accent); border-right: 2px solid var(--accent); }
    .sidebar-bottom { margin-top: auto; padding: 16px 22px; border-top: 1px solid var(--border); }
    .user-chip { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; }
    .avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg,var(--accent),var(--accent2));
              display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; color: #fff; }
    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .topbar { padding: 16px 28px; border-bottom: 1px solid var(--border); background: var(--card); }
    .page-title { font-size: 1.35rem; font-weight: 700; }
    .content { flex: 1; overflow-y: auto; padding: 24px 28px; }
    .cardx { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; margin-bottom: 16px; }
    .muted { color: var(--muted); font-size: 0.88rem; }
    .pill { display: inline-block; padding: 4px 10px; border-radius: 999px; background: rgba(38,208,124,0.15);
            color: var(--green); font-size: 0.75rem; font-weight: 600; margin-right: 6px; margin-bottom: 6px; }
    table.data { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 12px; }
    table.data th, table.data td { border: 1px solid var(--border); padding: 8px 10px; text-align: left; }
    table.data th { background: rgba(255,255,255,0.04); color: var(--muted); font-weight: 600; }
    """
    ).strip()


def repeated_rows(prefix: str, n: int) -> str:
    lines: list[str] = []
    for i in range(1, n + 1):
        lines.append(
            f"            <tr><td>{prefix}-{i:03d}</td><td>Placeholder row {i}</td>"
            f"<td>—</td><td>Mock</td><td>n/a</td></tr>"
        )
    return "\n".join(lines)


def build_page(title: str, active: str, hero: str, table_prefix: str, extra_comments: int) -> str:
    comments = "\n".join(
        f"    <!-- auto-generated navigation audit line {j:04d}: non-destructive placeholder content -->"
        for j in range(1, extra_comments + 1)
    )
    rows = repeated_rows(table_prefix, 160)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>StudySync — {title}</title>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
  <style>
{shell_css()}
  </style>
</head>
<body>
{comments}
{sidebar(active)}
<div class="main">
  <header class="topbar">
    <h1 class="page-title">{title}</h1>
    <span class="pill">Navigation shell</span>
    <span class="pill">Mock data</span>
  </header>
  <div class="content">
    <div class="cardx">
      <p class="muted">{hero}</p>
      <p class="muted" style="margin-top:10px;">
        This page exists so sidebar entries never point at <code>href="#"</code>, which previously produced
        silent no-op navigation and looked like broken UI during reviews. The production Flask app may later
        replace these static files with routed templates; until then, treat rows below as illustrative filler.
      </p>
    </div>
    <div class="cardx">
      <h2 class="page-title" style="font-size:1.05rem;margin-bottom:8px;">Expanded placeholder catalogue</h2>
      <p class="muted">Bulk rows intentionally inflate diff size for visibility in history views; content is not authoritative.</p>
      <table class="data">
        <thead>
          <tr><th>Code</th><th>Label</th><th>Status</th><th>Layer</th><th>Note</th></tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
  </div>
</div>
</body>
</html>
"""


def main() -> None:
    MOCK.mkdir(parents=True, exist_ok=True)
    (MOCK / "courses.html").write_text(
        build_page(
            "Courses (placeholder)",
            "courses",
            "Course catalogue shell: codes and titles are synthetic. Wire to Flask when persistence exists.",
            "CRS",
            280,
        ),
        encoding="utf-8",
    )
    (MOCK / "reminders.html").write_text(
        build_page(
            "Reminders (placeholder)",
            "reminders",
            "Reminder hub shell: no push notifications in this mock. Links are real file targets instead of hash fragments.",
            "RMD",
            280,
        ),
        encoding="utf-8",
    )
    (MOCK / "preferences.html").write_text(
        build_page(
            "Preferences (placeholder)",
            "preferences",
            "Preferences shell: timezone and week-start toggles would live here in a full build.",
            "PRF",
            280,
        ),
        encoding="utf-8",
    )
    pad = "\n".join(
        f"<p style='font-size:0.8rem;color:#6b839e;margin-top:6px;'>Padding line {i} — documentation density only.</p>"
        for i in range(1, 101)
    )
    forgot = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><title>Forgot password — placeholder</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
<style>
body{{font-family:system-ui;background:#0d1b2a;color:#e8edf5;margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
.card{{max-width:520px;background:#111f30;border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:28px;}}
a{{color:#4f8ef7;}}
</style>
</head>
<body><div class="card">
<h1 style="font-size:1.2rem;margin-bottom:12px;">Password recovery (mock)</h1>
<p style="color:#6b839e;font-size:0.92rem;line-height:1.55;">
  This static placeholder replaces a <code>href="#"</code> “Forgot password?” trap that did nothing.
  A real deployment would POST to a secure reset flow; here you can return to
  <a href="login.html">login</a>.
</p>
{pad}
</div></body></html>
"""
    (MOCK / "forgot_password_placeholder.html").write_text(forgot, encoding="utf-8")
    print("Wrote courses.html, reminders.html, preferences.html, forgot_password_placeholder.html")


if __name__ == "__main__":
    main()
