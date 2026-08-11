import pytest

from keel.errors import format_error
from keel.models import CHECK_IDS, GateResult, Violation, Warning


def test_violation_and_gate_result_are_frozen():
    v = Violation(where='spec.md:3', message='no acceptance criterion')
    r = GateResult(passed=False, violations=(v,))
    assert r.passed is False
    assert r.violations[0].where == 'spec.md:3'
    with pytest.raises(AttributeError):
        r.passed = True  # type: ignore[misc]


def test_gate_result_defaults_to_no_violations():
    assert GateResult(passed=True).violations == ()


def test_violation_carries_a_check_id():
    # T0.1: `where` is a coordinate, not an identity — it collides across checks (`line N` from
    # both A3 and A8, `path:line` from A6 and A11). Counting a check's fires needs a field that
    # names the check.
    assert Violation(where='line 3', message='x', check='A3').check == 'A3'
    assert Violation(where='line 3', message='x').check == ''


def test_warning_is_a_typed_finding_not_a_bare_string():
    # A bare-string warning is uncountable, and an uncountable warning cannot be defended.
    warning = Warning(check='W1', message='WARN: unstamped')
    assert (warning.check, warning.message) == ('W1', 'WARN: unstamped')
    with pytest.raises(AttributeError):
        warning.check = 'W2'  # type: ignore[misc]


def test_check_ids_is_a_closed_catalogue():
    assert 'A0' in CHECK_IDS and 'R1' in CHECK_IDS and 'W5' in CHECK_IDS
    assert '' not in CHECK_IDS
    # No `"W1: …"` message prefix: identity lives in the field, not in a string a consumer would
    # have to re-parse (the class 0.14.0's shared leading-token field parser removed).
    assert all(':' not in check for check in CHECK_IDS)


def test_format_error_includes_all_three_parts():
    msg = format_error(what='X failed', why='because Y', fix='do Z')
    assert 'X failed' in msg
    assert 'because Y' in msg
    assert 'do Z' in msg
