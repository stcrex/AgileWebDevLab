"""Table-driven regression tests built from ``profile_form_edge_cases_data``."""

from __future__ import annotations

import pytest

from app.services import profile_preferences as pp
from tests.profile_form_edge_cases_data import PROFILE_FORM_EDGE_CASES


@pytest.mark.parametrize("case_id,form,expected_keys", PROFILE_FORM_EDGE_CASES)
def test_profile_edge_case_matrix(case_id: str, form: dict, expected_keys: tuple[str, ...]):
    payload = pp.parse_profile_form(form)
    errors = pp.validate_profile_payload(payload, current_colour="purple")
    err_keys = tuple(sorted(errors))
    assert err_keys == tuple(sorted(expected_keys)), f"{case_id}: got {err_keys!r} want {expected_keys!r}"


def test_matrix_has_expected_cardinality():
    assert len(PROFILE_FORM_EDGE_CASES) == 80
