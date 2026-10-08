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
    is_suite_row,
    ledger_path,
    line_for_run,
    newest_gate_version,
    read_lines,
    serialize,
)
from keel.models import DOR_CHECK_IDS, Probe

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
    assert set(probes) == DOR_CHECK_IDS


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


def _row(
    repo: str, rev: str, a7: int, *, fired: int = 0, gate: str = '0.20.0', ts: str = ''
) -> dict:
    """A ledger row reduced to what gate-health reads, with A7 the only check that saw anything."""
    return {
        'ts': ts or '2026-09-01T00:00:00Z',
        'gate': gate,
        'repo': repo,
        'spec': 'aaaa0000',
        'rev': rev,
        'mode': 'full',
        'passed': True,
        'probes': {'A7': [a7, fired, fired]},
    }


def _gate_health(monkeypatch, tmp_path: Path, rows: list[dict], *args: str):
    ledger = tmp_path / 'ledger.jsonl'
    ledger.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(ledger))
    out = runner.invoke(app, ['gate-health', *args])
    assert out.exit_code == 0, out.output
    return out.output


def _columns(output: str, check: str) -> dict[str, str]:
    lines = output.splitlines()
    header = next(line for line in lines if line.startswith('check '))
    row = next(line for line in lines if line.startswith(f'{check} '))
    return dict(zip(header.split()[1:], row.split()[1:], strict=True))


@pytest.mark.parametrize(
    ('repo', 'gate', 'suite'),
    [
        ('test_check_ready_passes_on_rea0', '0.20.0', True),  # the 30-character cut, a counter
        ('test_x12', '0.21.0', True),  # 0.21.0 still wrote them, until its conftest landed
        ('test_the_grouped_checks_report1', '0.14.0', True),
        ('keel', '0.20.0', False),
        ('test-harness0', '0.20.0', False),  # pytest writes `\W` as `_`; a hyphen is not its shape
        ('tests', '0.20.0', False),  # no counter
        ('my_test_0', '0.20.0', False),
        ('test_' + 'a' * 30 + '0', '0.20.0', False),  # 35 characters before the counter
        ('testbed2', '0.22.0', False),  # a real repository so named, after the suite stopped
        ('test_x12', '0.21.1', False),
        ('test_x12', 'not-a-version', False),
    ],
)
def test_a_suite_row_is_a_pytest_tmp_path_repo_from_keel_0_21_0_or_older(repo, gate, suite):
    assert is_suite_row({'repo': repo, 'gate': gate}) is suite


def test_gate_health_leaves_out_the_rows_keels_own_suite_wrote(monkeypatch, tmp_path):
    # Until 0.21.0's hermetic conftest, every CLI test appended to the developer's real ledger, and
    # on the maintainer's those rows were 2,394 of 2,898. Read with them, a check's opportunity is
    # mostly the suite's, and a pre-registered disposition cannot be read off the command at all.
    output = _gate_health(
        monkeypatch,
        tmp_path,
        [
            _row('proj-a', '11111111', 3),
            _row('proj-a', '11111111', 3),  # the same revision run twice: counted once
            _row('proj-a-worktree', '11111111', 3),  # and from a second directory: still once
            _row('proj-b', '22222222', 2),
            _row('test_adr_number_collision_fai0', '33333333', 9, fired=1),
        ],
    )
    assert '4 runs' in output, output
    assert "1 row written by keel's own test suite left out" in output, output
    assert _columns(output, 'A7') == {
        'applicable': '4',
        'candidates': '5',
        'revisions': '2',
        'repos': '3',
        'revisions-fired-on': '0',
        'causes': '0',
        'fire-rate': '0.00',
    }


def test_the_fire_rate_is_revisions_fired_on_over_revisions_with_an_opportunity(
    monkeypatch, tmp_path
):
    # Both counts beside it are revisions, so the rate is too: one of two revisions fired, however
    # often the fired one was re-run. Dividing by runs read 1/3 here.
    output = _gate_health(
        monkeypatch,
        tmp_path,
        [
            _row('proj-a', '11111111', 1, fired=1),
            _row('proj-a', '11111111', 1, fired=1),
            _row('proj-b', '22222222', 1),
        ],
    )
    columns = _columns(output, 'A7')
    assert (columns['revisions'], columns['revisions-fired-on']) == ('2', '1'), columns
    assert columns['fire-rate'] == '0.50', columns


def test_gate_health_with_only_suite_rows_reports_no_runs(monkeypatch, tmp_path):
    output = _gate_health(monkeypatch, tmp_path, [_row('test_x0', '44444444', 1)])
    assert 'no runs' in output.lower()
    assert "1 row written by keel's own test suite left out" in output


def test_gate_health_counts_only_the_suite_rows_its_window_would_have_read(monkeypatch, tmp_path):
    rows = [
        _row('proj-a', '11111111', 3, ts='2026-10-01T00:00:00Z'),
        _row('test_x0', '44444444', 1, ts='2026-08-01T00:00:00Z'),
    ]
    output = _gate_health(monkeypatch, tmp_path, rows, '--since', '2026-09-01')
    assert 'left out' not in output, output
    assert '1 runs' in output, output


def test_gate_health_reads_a_named_repo_whole(monkeypatch, tmp_path):
    # A repository whose directory happens to look like a pytest tmp_path, named on the command
    # line: the caller asked for it, so none of its rows is set aside as the suite's.
    output = _gate_health(
        monkeypatch, tmp_path, [_row('test1', '55555555', 2, gate='0.20.0')], '--repo', 'test1'
    )
    assert 'left out' not in output and 'no runs' not in output.lower(), output
    assert _columns(output, 'A7')['applicable'] == '1'


def test_gate_health_on_an_absent_ledger_says_so_and_exits_zero(monkeypatch, tmp_path):
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(tmp_path / 'missing.jsonl'))
    out = runner.invoke(app, ['gate-health'])
    assert out.exit_code == 0
    assert 'no runs' in out.output.lower()


# --- newest_gate_version (SW17) ------------------------------------------------


def _write_rows(path: Path, *gates: object) -> Path:
    path.write_text(''.join(json.dumps({'gate': gate}) + '\n' for gate in gates), encoding='utf-8')
    return path


def test_newest_gate_version_compares_numerically_not_lexically(tmp_path):
    ledger = _write_rows(tmp_path / 'l.jsonl', '0.9.0', '0.10.0', '0.2.0')
    assert newest_gate_version(ledger) == '0.10.0'


def test_newest_gate_version_ignores_malformed_rows(tmp_path):
    ledger = tmp_path / 'l.jsonl'
    ledger.write_text(
        '{"gate": "0.3.0"}\n'
        'not json at all\n'
        '{"no_gate": 1}\n'
        '{"gate": 7}\n'
        '{"gate": "99.0"}\n'
        '{"gate": "v99.0.0"}\n'
        '{"gate": "99.0.0-rc1"}\n'
        '[1, 2]\n'
        '{"gate": "0.4.1"}\n',
        encoding='utf-8',
    )
    assert newest_gate_version(ledger) == '0.4.1'


def test_newest_gate_version_is_none_without_a_usable_ledger(tmp_path):
    assert newest_gate_version(None) is None
    assert newest_gate_version(tmp_path / 'missing.jsonl') is None
    assert newest_gate_version(_write_rows(tmp_path / 'junk.jsonl', 'x', 3)) is None


def test_newest_gate_version_is_none_when_the_ledger_cannot_be_read(tmp_path, monkeypatch):
    ledger = _write_rows(tmp_path / 'l.jsonl', '0.9.0')

    def refuse(self, *args, **kwargs):
        raise PermissionError(13, 'Permission denied')

    monkeypatch.setattr(Path, 'read_text', refuse)
    assert newest_gate_version(ledger) is None
