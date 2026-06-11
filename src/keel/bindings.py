"""Method-bindings completeness gate (stub). See docs/extension-points.md."""

from pathlib import Path

from keel.errors import format_error
from keel.models import GateResult  # part of the pinned return-type contract


def check_bindings(bindings_path: Path) -> GateResult:
    """Assert every portability slot in a method-bindings sheet is bound to a concrete mechanism."""
    raise NotImplementedError(
        format_error(
            what='`keel bind-check` is not implemented yet.',
            why='The deterministic bindings-completeness gate is scaffolded; '
            'its logic lands via the feedback->triage->release loop.',
            fix='Implement check_bindings in src/keel/bindings.py per docs/extension-points.md.',
        )
    )
