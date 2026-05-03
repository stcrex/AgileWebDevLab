from __future__ import annotations

import pytest

from app.services import profile_preferences as pp


def test_parse_profile_form_trims_and_optional_none():
    p = pp.parse_profile_form(
        {
            "full_name": "  Jane  ",
            "uwa_id": "",
            "program": "  ",
            "bio": "\t",
            "skills": "",
            "availability": "",
            "avatar_colour": "BLUE",
        }
    )
    assert p.full_name == "Jane"
    assert p.uwa_id is None
    assert p.program is None
    assert p.bio is None
    assert p.avatar_colour == "blue"


def test_validate_uwa_id_digits():
    err = pp.validate_profile_payload(
        pp.ProfileFormPayload(
            full_name="X",
            uwa_id="12345",
            program=None,
            bio=None,
            skills=None,
            availability=None,
            avatar_colour="purple",
        ),
        current_colour="purple",
    )
    assert "uwa_id" in err


def test_validate_uwa_id_ok():
    err = pp.validate_profile_payload(
        pp.ProfileFormPayload(
            full_name="X",
            uwa_id="12345678",
            program=None,
            bio=None,
            skills=None,
            availability=None,
            avatar_colour="purple",
        ),
        current_colour="purple",
    )
    assert "uwa_id" not in err


def test_normalise_avatar_colour():
    assert pp.normalise_avatar_colour("blue", fallback="purple") == "blue"
    assert pp.normalise_avatar_colour("nope", fallback="teal") == "teal"
    assert pp.normalise_avatar_colour("nope", fallback="bogus") == "purple"


@pytest.mark.parametrize(
    "filled,expect_min",
    [
        ({}, 20),
        ({"full_name": "A"}, 40),
        ({"full_name": "A", "uwa_id": "1"}, 40),
    ],
)
def test_profile_completeness_score_monotonic(filled, expect_min):
    class U:
        pass

    u = U()
    for k, v in filled.items():
        setattr(u, k, v)
    assert pp.profile_completeness_score(u) >= expect_min


def test_profile_summary_lines_email():
    class U:
        email = "a@b.c"
        uwa_id = None
        program = None

    lines = pp.profile_summary_lines(U())
    assert any("a@b.c" in ln for ln in lines)


def test_field_limits_table_non_empty():
    rows = pp.field_limits_table()
    assert len(rows) >= 6
    assert all(isinstance(n, int) and n > 0 for _, n in rows)


def test_squash_multiline_whitespace():
    assert pp.squash_multiline_whitespace("  a  \n\n  b  ") == "a\n\nb"
    assert pp.squash_multiline_whitespace("   ") is None


def test_preview_text_truncates():
    long = "word " * 80
    out = pp.preview_text(long, limit=40)
    assert len(out) <= 41
    assert out.endswith("…")


def test_first_validation_error_order():
    p = pp.ProfileFormPayload(
        full_name="",
        uwa_id="1",
        program=None,
        bio=None,
        skills=None,
        availability=None,
        avatar_colour="purple",
    )
    msg = pp.first_validation_error(p, current_colour="purple")
    assert msg and "Full name" in msg
