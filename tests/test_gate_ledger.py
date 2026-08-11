"""KEEL-B07 — the probe ledger, and the three states a hit-rate count needs.

CONTRIBUTING has said for eleven minor versions that a gate firing zero times across N series is
a triage input, and admitted in the same breath that no hit-rate ledger exists. Every keep verdict
on the Part-A checks has therefore rested on design reasoning. This is the instrument that changes
that, and it is the cheapest one in the surface.

A zero-fire count is ambiguous between *inert* and *never had an opportunity* — eight checks are
verify-when-present and three more are conditionally relaxed — so a two-state count would record
the two indistinguishably and answer nothing. `Probe` carries three: `candidates == 0` is n/a,
`candidates > 0 with fired == 0` is CLEAN, and that middle state is the load-bearing one the code
did not compute before.

Privacy is enforced by construction rather than by remembering: the writer only ever sees a
`LedgerLine` whose every field is a closed enum, an int, a bool, a hex digest or a slug, so a
free-text field is unrepresentable, and `Violation.message` never reaches it.
"""

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from keel.check_ready import check_spec_ready
from keel.cli import app
from keel.gate_ledger import (
    SCHEMA_VERSION,
    LedgerLine,
    ledger_path,
    line_for_run,
    read_lines,
    serialize,
)
from keel.models import CHECK_IDS, Probe

from .test_adversarial_corpus import MUTANTS, materialize

runner = CliRunner()


def _clean(tmp_path: Path) -> Path:
    return materialize(tmp_path, {'id': 'clean'})


def _probes(result) -> dict[str, Probe]:
    return {probe.check: probe for probe in result.probes}


# --- the three states ---------------------------------------------------------


def test_a_probe_carries_candidates_fired_and_causes():
    probe = Probe(check='A6', candidates=23, fired=5, causes=2)
    assert (probe.candidates, probe.fired, probe.causes) == (23, 5, 2)


def test_clean_is_distinguishable_from_no_opportunity(tmp_path):
    # The whole point. On a clean spec A6 examined anchors and found nothing wrong (CLEAN); A0
    # examined a declared Kind (CLEAN). A check with no construct present reports n/a, and the two
    # must not collapse into the same zero.
    probes = _probes(check_spec_ready(_clean(tmp_path)))
    assert probes['A6'].candidates > 0 and probes['A6'].fired == 0
    assert probes['A12'].candidates > 0 and probes['A12'].fired == 0
    assert probes['A0'].candidates == 1


def test_every_catalogued_check_reports_a_probe(tmp_path):
    probes = _probes(check_spec_ready(_clean(tmp_path)))
    assert set(probes) == CHECK_IDS


def test_a_check_that_fired_always_had_a_candidate(tmp_path):
    # The invariant that keeps the counters honest as the checks change: firing without a counted
    # candidate would report a fire rate above 1 and mean the counter drifted from its check.
    for index, mutant in enumerate(MUTANTS):
        result = check_spec_ready(materialize(tmp_path / str(index), mutant))
        for probe in result.probes:
            assert not (probe.fired and not probe.candidates), (mutant['id'], probe)
            assert probe.causes <= probe.fired, (mutant['id'], probe)
            assert (probe.causes == 0) == (probe.fired == 0), (mutant['id'], probe)


def test_structure_only_marks_the_certification_checks_not_applicable(tmp_path):
    probes = _probes(check_spec_ready(_clean(tmp_path), structure_only=True))
    for check in ('B1', 'B2', 'W2', 'W4', 'W5'):
        assert probes[check].candidates == 0, check


# --- the line -----------------------------------------------------------------


def test_the_line_carries_the_pre_registered_schema(tmp_path):
    spec = _clean(tmp_path)
    line = json.loads(serialize(line_for_run(spec, check_spec_ready(spec), structure_only=False)))
    assert line['v'] == SCHEMA_VERSION
    assert line['mode'] == 'full' and line['kind'] == 'series'
    assert line['passed'] is True and line['exit'] == 0
    assert line['probes']['A6'][0] > 0 and line['probes']['A6'][1] == 0
    assert line['cert'] == {'present': True, 'verdict': 'CERTIFIED', 'operator': False}
    assert len(line['spec']) == 8 and len(line['rev']) == 8


def test_the_spec_id_is_a_digest_not_a_stem(tmp_path):
    # Spec stems in this corpus name the project's roadmap; the id must not carry one.
    spec = _clean(tmp_path)
    line = serialize(line_for_run(spec, check_spec_ready(spec), structure_only=False))
    assert 'clean-series' not in line
    assert 'region' not in line and 'tinyetl' not in line


def test_the_serializer_refuses_a_field_that_could_carry_prose(tmp_path):
    spec = _clean(tmp_path)
    line = line_for_run(spec, check_spec_ready(spec), structure_only=False)
    for bad in ('a repo name with spaces', 'src/keel/check_ready.py'):
        with pytest.raises(ValueError):
            serialize(LedgerLine(**{**vars_of(line), 'repo': bad}))
    with pytest.raises(ValueError):
        serialize(LedgerLine(**{**vars_of(line), 'verdict': 'REJECTED — see the note below'}))
    with pytest.raises(ValueError):
        serialize(LedgerLine(**{**vars_of(line), 'probes': {'NOT-A-CHECK': (1, 0, 0)}}))


def vars_of(line: LedgerLine) -> dict:
    return {field: getattr(line, field) for field in LedgerLine.__slots__}


def test_no_four_word_run_of_the_spec_survives_into_the_line(tmp_path):
    # The property that makes "we do not log content" checkable rather than remembered.
    for index, mutant in enumerate(MUTANTS):
        spec = materialize(tmp_path / str(index), mutant)
        emitted = serialize(line_for_run(spec, check_spec_ready(spec), structure_only=False))
        words = spec.read_text(encoding='utf-8').split()
        for start in range(len(words) - 3):
            run = ' '.join(words[start : start + 4])
            assert run not in emitted, (mutant['id'], run)


# --- where it is written ------------------------------------------------------


def test_the_ledger_is_user_level_with_an_env_override_and_an_off_switch(monkeypatch, tmp_path):
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(tmp_path / 'l.jsonl'))
    assert ledger_path() == tmp_path / 'l.jsonl'
    monkeypatch.setenv('KEEL_GATE_LEDGER', 'off')
    assert ledger_path() is None
    monkeypatch.delenv('KEEL_GATE_LEDGER')
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path / 'state'))
    assert ledger_path() == tmp_path / 'state' / 'keel' / 'gate-ledger.jsonl'
    monkeypatch.delenv('XDG_STATE_HOME')
    assert ledger_path() == Path.home() / '.keel' / 'gate-ledger.jsonl'


def test_check_ready_appends_one_line_per_run(monkeypatch, tmp_path):
    ledger = tmp_path / 'ledger.jsonl'
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(ledger))
    spec = _clean(tmp_path / 'repo')
    for _ in range(2):
        assert runner.invoke(app, ['check-ready', str(spec)]).exit_code == 0
    lines = read_lines(ledger)
    assert len(lines) == 2
    assert {line['mode'] for line in lines} == {'full'}


def test_telemetry_never_colours_the_exit_code(monkeypatch, tmp_path):
    # 0/1/2 is a documented contract. An unwritable ledger, or none at all, changes nothing.
    spec = _clean(tmp_path / 'repo')
    monkeypatch.setenv('KEEL_GATE_LEDGER', 'off')
    assert runner.invoke(app, ['check-ready', str(spec)]).exit_code == 0
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(tmp_path / 'nope' / 'x' / 'l.jsonl'))
    monkeypatch.setattr(os, 'makedirs', _raise_oserror, raising=False)
    assert runner.invoke(app, ['check-ready', str(spec)]).exit_code == 0
    assert runner.invoke(app, ['check-ready', str(tmp_path / 'ghost.md')]).exit_code == 2


def _raise_oserror(*args, **kwargs):
    raise OSError('no')


# --- the readout --------------------------------------------------------------


def test_gate_health_reports_applicable_runs_and_fire_rate(monkeypatch, tmp_path):
    ledger = tmp_path / 'ledger.jsonl'
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(ledger))
    clean = _clean(tmp_path / 'clean')
    broken = materialize(tmp_path / 'broken', next(m for m in MUTANTS if m['id'] == 'A4-uncovered'))
    runner.invoke(app, ['check-ready', str(clean)])
    runner.invoke(app, ['check-ready', str(broken)])
    runner.invoke(app, ['check-ready', str(clean), '--structure-only'])
    out = runner.invoke(app, ['gate-health'])
    assert out.exit_code == 0
    assert 'A4' in out.output and 'A7' in out.output
    assert 'author loop' in out.output.lower() or 'structure-only' in out.output.lower()


def test_gate_health_on_an_absent_ledger_says_so_and_exits_zero(monkeypatch, tmp_path):
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(tmp_path / 'missing.jsonl'))
    out = runner.invoke(app, ['gate-health'])
    assert out.exit_code == 0
    assert 'no runs' in out.output.lower()
