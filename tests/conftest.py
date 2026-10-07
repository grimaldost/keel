"""Shared fixtures."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _hermetic_gate_ledger(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
):
    """Point the gate ledger at a per-test file.

    Without this every CLI test appends to the developer's real ledger, and once that ledger holds
    a newer keel version the check-ready upgrade WARN would leak into every test. A test that sets
    KEEL_GATE_LEDGER itself still wins: its own `monkeypatch.setenv` runs after this one.
    """
    ledger: Path = tmp_path_factory.mktemp('gate-ledger') / 'gate-ledger.jsonl'
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(ledger))
