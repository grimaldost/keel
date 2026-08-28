from pathlib import Path

import pytest

from keel.budget_drift import check_budget_drift

# check_spec_ready is implemented as of 0.2.0 and check_bindings as of 0.17.0 (ADR-0018);
# budget-drift is the one gate still stubbed, and its interface is pinned by this contract.
# When it is built or removed (backlog KEEL-B30/B35) this module has nothing left to pin.


@pytest.mark.parametrize(
    'call',
    [
        lambda: check_budget_drift(Path('series.toml'), Path('actuals.json')),
    ],
)
def test_gate_stub_raises_with_actionable_message(call):
    with pytest.raises(NotImplementedError) as exc:
        call()
    text = str(exc.value)
    assert 'not implemented yet' in text
    assert 'Fix:' in text
