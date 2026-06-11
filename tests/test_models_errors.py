import pytest

from keel.errors import format_error
from keel.models import GateResult, Violation


def test_violation_and_gate_result_are_frozen():
    v = Violation(where='spec.md:3', message='no acceptance criterion')
    r = GateResult(passed=False, violations=(v,))
    assert r.passed is False
    assert r.violations[0].where == 'spec.md:3'
    with pytest.raises(AttributeError):
        r.passed = True  # type: ignore[misc]


def test_gate_result_defaults_to_no_violations():
    assert GateResult(passed=True).violations == ()


def test_format_error_includes_all_three_parts():
    msg = format_error(what='X failed', why='because Y', fix='do Z')
    assert 'X failed' in msg
    assert 'because Y' in msg
    assert 'do Z' in msg
