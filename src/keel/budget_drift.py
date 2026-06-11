"""Per-wave budget drift gate (stub). See docs/phases-reference.md (Route & Budget)."""

from pathlib import Path

from keel.errors import format_error
from keel.models import GateResult  # part of the pinned return-type contract


def check_budget_drift(series_path: Path, actuals_path: Path) -> GateResult:
    """Flag when cumulative actual spend exceeds the wave estimate past the drift threshold."""
    raise NotImplementedError(
        format_error(
            what='`keel budget-drift` is not implemented yet.',
            why='The deterministic wave-budget drift gate is scaffolded; its logic lands via the '
            'feedback->triage->release loop.',
            fix='Implement check_budget_drift in src/keel/budget_drift.py'
            ' per docs/phases-reference.md.',
        )
    )
