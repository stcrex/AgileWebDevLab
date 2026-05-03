"""Validation, parsing, and display helpers for the Preferences / profile screen.

Keeping this logic outside the blueprint makes it easier to unit-test and reuse
(e.g. future JSON API or CLI import) without pulling in Flask request context.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

# --- Limits (must stay aligned with SQLAlchemy column sizes on User) ---

MAX_FULL_NAME = 120
MAX_UWA_ID = 30
MAX_PROGRAM = 120
MAX_SKILLS = 250
MAX_AVAILABILITY = 250
MAX_BIO = 8000

ALLOWED_AVATAR_COLOURS: tuple[str, ...] = (
    "purple",
    "blue",
    "green",
    "orange",
    "teal",
    "pink",
    "slate",
    "red",
)

# Human-readable hints for the template / markers (not shown as error strings).
FIELD_HELP: dict[str, str] = {
    "full_name": "Shown across the lab wherever your name appears in lists.",
    "uwa_id": "Optional; use the student number format your unit expects.",
    "program": "Optional degree or major label for dashboards.",
    "bio": "Free text; keep it professional if markers review the demo.",
    "skills": "Comma-separated or short phrases work well.",
    "availability": "Helps teammates pick meeting times outside the group grid.",
    "avatar_colour": "Stored for future UI theming; constrained to a safe palette.",
}

_UWA_RE = re.compile(r"^\d{6,10}$")


@dataclass(frozen=True)
class ProfileFormPayload:
    full_name: str
    uwa_id: str | None
    program: str | None
    bio: str | None
    skills: str | None
    availability: str | None
    avatar_colour: str


def parse_profile_form(form: Mapping[str, Any]) -> ProfileFormPayload:
    """Normalise raw multipart form values into a payload object."""

    def opt(key: str) -> str | None:
        v = (form.get(key) or "").strip()
        return v or None

    colour = (form.get("avatar_colour") or "").strip().lower() or "purple"
    return ProfileFormPayload(
        full_name=(form.get("full_name") or "").strip(),
        uwa_id=opt("uwa_id"),
        program=opt("program"),
        bio=opt("bio"),
        skills=opt("skills"),
        availability=opt("availability"),
        avatar_colour=colour,
    )


def validate_profile_payload(payload: ProfileFormPayload, *, current_colour: str | None) -> dict[str, str]:
    """
    Return a dict of field -> error message. Empty dict means the payload is acceptable.

    ``current_colour`` is used when ``avatar_colour`` is not in the allow-list so the
    caller can fall back without treating it as a hard validation failure.
    """
    errors: dict[str, str] = {}
    if not payload.full_name:
        errors["full_name"] = "Full name is required."
    elif len(payload.full_name) > MAX_FULL_NAME:
        errors["full_name"] = "Full name is too long."

    if payload.uwa_id is not None and len(payload.uwa_id) > MAX_UWA_ID:
        errors["uwa_id"] = "UWA ID is too long."
    elif payload.uwa_id is not None and not _UWA_RE.match(payload.uwa_id):
        # Soft rule: allow empty; if provided, prefer digits-only student-style IDs.
        errors["uwa_id"] = "UWA ID should be 6–10 digits only, or leave blank."

    if payload.program is not None and len(payload.program) > MAX_PROGRAM:
        errors["program"] = "Program is too long."

    if payload.skills is not None and len(payload.skills) > MAX_SKILLS:
        errors["skills"] = "Skills field is too long."

    if payload.availability is not None and len(payload.availability) > MAX_AVAILABILITY:
        errors["availability"] = "Availability is too long."

    if payload.bio is not None and len(payload.bio) > MAX_BIO:
        errors["bio"] = "Bio is too long."

    if payload.avatar_colour not in ALLOWED_AVATAR_COLOURS:
        # Not a hard error for the dict — caller flashes info and keeps old colour.
        pass

    return errors


def normalise_avatar_colour(requested: str, *, fallback: str | None) -> str:
    """Return a safe colour key, never an arbitrary string."""
    c = (requested or "").strip().lower()
    if c in ALLOWED_AVATAR_COLOURS:
        return c
    fb = (fallback or "purple").strip().lower()
    return fb if fb in ALLOWED_AVATAR_COLOURS else "purple"


def profile_completeness_score(user: Any) -> int:
    """
    Rough 0–100 score for demo dashboards: rewards filled optional fields.

    Weights: name always required for save; optional fields each add a slice.
    """
    if user is None:
        return 0
    score = 20  # base for having an account row
    if getattr(user, "full_name", None):
        score += 20
    if getattr(user, "uwa_id", None):
        score += 10
    if getattr(user, "program", None):
        score += 10
    if getattr(user, "bio", None):
        score += 15
    if getattr(user, "skills", None):
        score += 10
    if getattr(user, "availability", None):
        score += 10
    if getattr(user, "avatar_colour", None):
        score += 5
    return min(score, 100)


def profile_summary_lines(user: Any) -> list[str]:
    """Short bullet lines for the Preferences sidebar card."""
    lines: list[str] = []
    if not user:
        return lines
    email = getattr(user, "email", "") or ""
    if email:
        lines.append(f"Signed in as {email}")
    uid = getattr(user, "uwa_id", None)
    if uid:
        lines.append(f"Student ID on file: {uid}")
    prog = getattr(user, "program", None)
    if prog:
        lines.append(f"Program: {prog}")
    if not lines:
        lines.append("Complete the form to enrich your demo profile.")
    return lines


def field_limits_table() -> list[tuple[str, int]]:
    """Return (field_name, max_length) pairs for documentation and admin tooling."""

    return [
        ("full_name", MAX_FULL_NAME),
        ("uwa_id", MAX_UWA_ID),
        ("program", MAX_PROGRAM),
        ("skills", MAX_SKILLS),
        ("availability", MAX_AVAILABILITY),
        ("bio", MAX_BIO),
    ]


def squash_multiline_whitespace(value: str | None, *, max_lines: int = 24) -> str | None:
    """
    Collapse repeated blank lines inside optional long text fields.

    This keeps stored bios readable without implementing full rich-text sanitisation.
    """

    if value is None:
        return None
    raw = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return None
    chunks: list[str] = []
    for block in raw.split("\n\n"):
        inner = " ".join(line.strip() for line in block.split("\n") if line.strip())
        if inner:
            chunks.append(inner)
        if len(chunks) >= max_lines:
            break
    return "\n\n".join(chunks) if chunks else None


def preview_text(value: str | None, *, limit: int = 220) -> str:
    """Single-line preview for logs or compact UI chips."""

    if not value:
        return ""
    one = " ".join(value.split())
    if len(one) <= limit:
        return one
    return one[: limit - 1].rstrip() + "…"


def apply_payload_to_user(user: Any, payload: ProfileFormPayload, *, colour: str) -> None:
    """
    Mutate an ORM ``User`` instance in-place. Caller is responsible for ``db.session.commit()``.

    Centralising assignments avoids drift between POST handlers and hypothetical JSON APIs.
    """

    user.full_name = payload.full_name
    user.uwa_id = payload.uwa_id
    user.program = payload.program
    user.bio = payload.bio
    user.skills = payload.skills
    user.availability = payload.availability
    user.avatar_colour = colour


def describe_allowed_colours() -> str:
    """Comma-separated list for CLI help or markdown tables."""

    return ", ".join(sorted(ALLOWED_AVATAR_COLOURS))


def first_validation_error(payload: ProfileFormPayload, *, current_colour: str | None) -> str | None:
    """Return the first human-facing error string, or ``None`` if the payload is valid."""

    errors = validate_profile_payload(payload, current_colour=current_colour)
    if not errors:
        return None
    order = ("full_name", "uwa_id", "program", "skills", "availability", "bio")
    for key in order:
        if key in errors:
            return errors[key]
    return next(iter(errors.values()), None)
