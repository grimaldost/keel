"""T1.2 — the report unit: 146 violations traced to about ten causes.

The census's sharpest number: one insertion above a self-anchored fold ledger produced 57 A12
violations at a uniform shift. Counting those as 57 findings misreports the gate in two directions
at once — it makes A12 look like the noisiest check in the surface, and it makes "how many things
are actually wrong with this spec?" unanswerable from the output. The corpus's own complaint about
A12 is that its errors *under-specify how to conform*, not that it fires wrongly.

So a violation now carries a `cause` key, and violations sharing it are one cause. `fired` still
counts every violation — the ledger has to be able to measure whether this change helped, which it
cannot do if the change also rewrites the number it is measured on. That is why the ledger line
carries a schema version, bumped here.

Grouping rule, and its limit: anchors failing against the same target are one cause; where a
snippet lets the shift be computed, only anchors sharing the same delta group together. An
out-of-range anchor has no measurable delta, so it groups by target alone — which will under-count
causes when two unrelated anchors into one file both overflow. That is the deliberate direction to
err: a check that over-reports causes looks noisier than it is, which is the failure this change
exists to stop.
"""

from pathlib import Path

import pytest

from keel.check_ready import check_spec_ready
from keel.gate_ledger import SCHEMA_VERSION

from .test_adversarial_corpus import MUTANTS, materialize

BASE = """# Spec — pipeline

- **Status:** ready (DoR passed)
- **Kind:** single-change

## Goal

A one-change spec. **Acceptance criterion:** the loader emits one row per region
and a unit test asserts it.

{body}

## Pre-mortem certification

- **Reviewer:** a non-author reviewer
- **Verdict:** CERTIFIED
- **Failure modes considered & folded in:** none outstanding
"""


def _write(tmp_path: Path, body: str) -> Path:
    (tmp_path / '.git').mkdir(exist_ok=True)
    spec = tmp_path / 'spec.md'
    spec.write_text(BASE.format(body=body), encoding='utf-8')
    return spec


def _probe(spec: Path, check: str):
    return next(p for p in check_spec_ready(spec).probes if p.check == check)


def _module(tmp_path: Path, name: str, lines: int = 6) -> None:
    (tmp_path / name).write_text(''.join(f'row {n}\n' for n in range(1, lines + 1)), 'utf-8')


def test_a_uniform_ledger_shift_is_one_cause_and_still_counts_every_row(tmp_path):
    mutant = next(m for m in MUTANTS if m['id'] == 'A12-drift-57')
    probe = _probe(materialize(tmp_path, mutant), 'A12')
    assert probe.fired == 57, 'the raw count must survive, or the change rewrites its own baseline'
    assert probe.causes == 1


def test_anchors_into_three_files_are_three_causes(tmp_path):
    for name in ('a.py', 'b.py', 'c.py'):
        _module(tmp_path, name)
    body = 'Notes: `a.py:99`, `b.py:99` and `c.py:99` all overflow.'
    probe = _probe(_write(tmp_path, body), 'A6')
    assert (probe.fired, probe.causes) == (3, 3)


def test_two_anchors_overflowing_one_file_are_one_cause(tmp_path):
    _module(tmp_path, 'a.py')
    probe = _probe(_write(tmp_path, 'Notes: `a.py:41` and `a.py:42`.'), 'A6')
    assert (probe.fired, probe.causes) == (2, 1)


def test_snippet_drifts_sharing_a_delta_are_one_cause(tmp_path):
    _module(tmp_path, 'a.py', lines=9)
    # Both snippets sit two lines below where they are cited: one insertion, one cause.
    body = 'See `a.py:2` `row 4` and `a.py:5` `row 7`.'
    probe = _probe(_write(tmp_path, body), 'A6')
    assert (probe.fired, probe.causes) == (2, 1)


def test_snippet_drifts_with_different_deltas_are_two_causes(tmp_path):
    _module(tmp_path, 'a.py', lines=9)
    body = 'See `a.py:2` `row 4` and `a.py:5` `row 9`.'
    probe = _probe(_write(tmp_path, body), 'A6')
    assert (probe.fired, probe.causes) == (2, 2)


def test_a_check_with_no_grouping_rule_reports_one_cause_per_violation(tmp_path):
    # A4's violations are independent claims about different sections; nothing groups them, and
    # inventing a grouping would hide findings rather than summarise them.
    body = """## Numbered sections

### §1 One
Text. **Acceptance criterion:** the loader emits one row and a test asserts it.

### §2 Two
Text. **Acceptance criterion:** the writer emits one file and a test asserts it.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
"""
    spec = _write(tmp_path, body.replace('- **Kind:** single-change', ''))
    probe = _probe(spec, 'A4')
    assert probe.fired == probe.causes >= 1


def test_causes_never_exceed_fires_anywhere_in_the_corpus(tmp_path):
    for index, mutant in enumerate(MUTANTS):
        for probe in check_spec_ready(materialize(tmp_path / str(index), mutant)).probes:
            assert 0 <= probe.causes <= probe.fired, (mutant['id'], probe)


def test_the_ledger_schema_version_moved_with_the_report_unit():
    # `causes` means something different before and after this change. Without the bump the two
    # eras mix silently in one file and the comparison the ledger exists for is lost.
    assert SCHEMA_VERSION == 2


@pytest.mark.parametrize('check', ['A6', 'A12'])
def test_the_grouped_checks_report_a_cause_summary_on_the_cli(tmp_path, check):
    from typer.testing import CliRunner

    from keel.cli import app

    mutant = next(m for m in MUTANTS if m['id'] == 'A12-drift-57')
    spec = materialize(tmp_path, mutant)
    out = CliRunner().invoke(app, ['check-ready', str(spec)])
    assert out.exit_code == 1
    assert '57' in out.output
    if check == 'A12':
        assert 'cause' in out.output.lower()
