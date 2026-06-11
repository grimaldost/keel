from pathlib import Path

import pytest

from keel.bindings import check_bindings
from keel.budget_drift import check_budget_drift

# check_spec_ready is implemented as of 0.2.0 (see tests/test_check_ready.py); the
# remaining gates are still stubs whose interface is pinned by this contract.


@pytest.mark.parametrize(
    'call',
    [
        lambda: check_budget_drift(Path('series.toml'), Path('actuals.json')),
        lambda: check_bindings(Path('method-bindings.md')),
    ],
)
def test_gate_stub_raises_with_actionable_message(call):
    with pytest.raises(NotImplementedError) as exc:
        call()
    text = str(exc.value)
    assert 'not implemented yet' in text
    assert 'Fix:' in text
