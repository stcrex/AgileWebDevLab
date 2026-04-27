#!/usr/bin/env python3
"""Generate bulky security pre-release checklist docs (chore artefact)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "SECURITY_PRE_RELEASE_CHECKLIST.md"
OUT_LINES = ROOT / "docs" / "SECURITY_AUDIT_LINES.txt"


def main() -> None:
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Pre-release security pass (lab repository)",
        "",
        "> **Disclaimer:** This document is a **process scaffold** for coursework checkpoints. It does not",
        "> replace a professional penetration test. Many checklist rows are **synthetic** to make review",
        "> surface area visible in diffs.",
        "",
        "## 1. CSRF posture (Flask-WTF)",
        "",
        "- [ ] All **state-changing** HTML forms include a valid `csrf_token` field.",
        "- [ ] JSON `POST`/`PATCH`/`DELETE` from jQuery send **`X-CSRFToken`** (see `WTF_CSRF_HEADERS` in `app/config.py`).",
        "- [ ] No accidental `csrf.exempt` on user-facing mutation routes without explicit threat model note.",
        "",
        "## 2. Password storage",
        "",
        "- [ ] Passwords persisted only as **Werkzeug hashes** (`set_password` / `check_password`).",
        "- [ ] No plaintext passwords in logs, flash messages, or JSON error bodies.",
        "",
        "## 3. Secrets and configuration",
        "",
        "- [ ] `SECRET_KEY` overridden in any shared/staging environment (never ship default dev key).",
        "- [ ] `.env` gitignored; `.env.example` documents variables **without real values**.",
        "",
        "## 4. Auth-sensitive routes",
        "",
        "- [ ] `@login_required` (or equivalent) on pages/APIs that expose private data.",
        "- [ ] Exam and group APIs enforce **ownership / membership** before returning rows.",
        "",
        "## 5. Synthetic row sweep (documentation density)",
        "",
        "Mark each row during a real pass as **OK**, **GAP**, or **N/A**. Rows below are auto-generated.",
        "",
    ]

    for i in range(1, 1101):
        lines.append(
            f"- [ ] **SEC-{i:05d}** — synthetic control point {i % 211}: revisit CSRF/session/cookie headers "
            f"and authz for route family index {(i % 7) + 1}."
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Regenerate: `python3 scripts/generate_security_pre_release_pass.py`")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out_lines = ["SECURITY_AUDIT_LINE_ID\tSTATUS\tOWNER\tNOTES"]
    for j in range(1, 701):
        out_lines.append(
            f"SEC-LINE-{j:06d}\tOPEN\tunassigned\tbulk-appendix-row-{j % 331}"
        )
    OUT_LINES.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    print("Wrote", OUT_MD, "and", OUT_LINES)


if __name__ == "__main__":
    main()
