"""A13: a spec that declares a requirements register accounts for every order in it.

The motivating failure is not a spec defect the gate could already see. A programme's opening
instruction ("the sources are abstracted via the config layer") was replaced by hand-rolled
readers as an unlabelled design decision; three later specs certified Ready and four blind
pre-mortems returned real findings, and none of them could see the substitution, because the
order existed nowhere a reviewer or a gate could cite. A13 does not judge whether a disposition
is right — that stays Part B. It makes the omission impossible and refuses the one disposition a
session must not write for itself.
"""

from keel import __version__
from keel.check_ready import check_spec_ready, register_ids

REGISTER = """# Requirements register — widget

### RR-01 — the widget is exposed by the CLI

- **Order (verbatim):** "the widget has to come out of the CLI, not a library call"
- **Status:** live

### RR-02 — no new dependency

- **Order (verbatim):** "do it with what is already in the lockfile"
- **Status:** live
"""

SPEC = f"""# Spec — widget

- **Status:** ready (DoR passed)
- **Kit:** {__version__}
- **Requirements:** docs/requirements/orders.md

## Numbered sections

### §1 Add the widget module
Introduce `src/widget.py`. **Acceptance criterion:** `src/widget.py` exposes `make()`
and a unit test asserts it returns a Widget instance.

### §2 Wire the widget into the CLI
Expose the widget. **Acceptance criterion:** running `app widget` prints the widget
id and exits zero in an integration test.

## Requirements ledger

| Order | Verbatim | Disposition |
|---|---|---|
| RR-01 | "the widget has to come out of the CLI, not a library call" | §2 |
| RR-02 | "do it with what is already in the lockfile" | OUT-OF-SCOPE |

## Concept → module map

| Concept | Module / file it lives in |
|---|---|
| widget | `src/widget.py` (to be created) |

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** CERTIFIED
- **Date:** 2026-08-28
- **Failure modes considered & folded in:** none outstanding
"""


def _write(tmp_path, spec_text=SPEC, register_text=REGISTER):
    (tmp_path / '.git').mkdir()
    if register_text is not None:
        register = tmp_path / 'docs' / 'requirements'
        register.mkdir(parents=True)
        (register / 'orders.md').write_text(register_text, encoding='utf-8')
    spec = tmp_path / 'spec.md'
    spec.write_text(spec_text, encoding='utf-8')
    return spec


def _a13(result):
    return [v for v in result.violations if v.check == 'A13']


def test_a_complete_ledger_passes(tmp_path):
    result = check_spec_ready(_write(tmp_path))
    assert result.passed, [(v.check, v.where, v.message) for v in result.violations]


def test_a_spec_with_no_register_is_silent(tmp_path):
    # n/a, not clean: a project that keeps no register presents no candidates, and A13 says
    # nothing about it in either direction.
    spec = SPEC.replace('- **Requirements:** docs/requirements/orders.md\n', '')
    result = check_spec_ready(_write(tmp_path, spec, register_text=None))
    assert result.passed, [(v.check, v.message) for v in result.violations]
    assert all(probe.candidates == 0 for probe in result.probes if probe.check == 'A13')


def test_requirements_none_is_a_declaration_of_no_register(tmp_path):
    spec = SPEC.replace(
        '- **Requirements:** docs/requirements/orders.md', '- **Requirements:** none'
    )
    result = check_spec_ready(_write(tmp_path, spec, register_text=None))
    assert result.passed, [(v.check, v.message) for v in result.violations]


def test_a_declared_register_that_does_not_resolve_fails(tmp_path):
    result = check_spec_ready(_write(tmp_path, register_text=None))
    assert not result.passed
    assert _a13(result) and 'no file resolves there' in _a13(result)[0].message


def test_a_register_with_no_ids_fails(tmp_path):
    result = check_spec_ready(_write(tmp_path, register_text='# Register\n\nNothing here yet.\n'))
    assert not result.passed
    assert _a13(result) and 'declares no orders' in _a13(result)[0].message


def test_a_declared_register_with_no_ledger_section_fails(tmp_path):
    head, _, tail = SPEC.partition('## Requirements ledger')
    spec = head + tail.partition('## Concept')[1] + tail.partition('## Concept')[2]
    assert 'Requirements ledger' not in spec
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert _a13(result) and 'carries no' in _a13(result)[0].message


def test_an_unaccounted_order_fails_and_names_it(tmp_path):
    spec = SPEC.replace(
        '| RR-02 | "do it with what is already in the lockfile" | OUT-OF-SCOPE |\n', ''
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert _a13(result) and 'RR-02' in _a13(result)[0].message


def test_a_ledger_row_naming_no_order_fails(tmp_path):
    spec = SPEC.replace('| RR-02 | "do it', '| RR-07 | "do it')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    messages = ' '.join(v.message for v in _a13(result))
    assert 'RR-02' in messages and 'RR-07' in messages


def test_a_self_ratified_deviation_fails(tmp_path):
    spec = SPEC.replace(
        '| RR-01 | "the widget has to come out of the CLI, not a library call" | §2 |',
        '| RR-01 | "the widget has to come out of the CLI, not a library call" | DEVIATED — a '
        'library call is cleaner |',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert _a13(result) and 'cannot grant itself' in _a13(result)[0].message


def test_a_ratified_deviation_passes(tmp_path):
    # The state is blocking until the owner answers, not blocking forever: a recorded answer is
    # what unblocks it, and the record is what a later reader can audit.
    spec = SPEC.replace(
        '| RR-01 | "the widget has to come out of the CLI, not a library call" | §2 |',
        '| RR-01 | "the widget has to come out of the CLI, not a library call" | DEVIATED — '
        'ratified by A. Owner: the CLI surface is frozen, so the library call stands |',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [(v.check, v.message) for v in result.violations]


def test_a_deferral_without_a_trigger_fails(tmp_path):
    spec = SPEC.replace('| OUT-OF-SCOPE |', '| DEFERRED |').replace(
        '"do it with what is already in the lockfile" | OUT-OF-SCOPE',
        '"do it with what is already in the lockfile" | DEFERRED',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert _a13(result) and 'no trigger' in _a13(result)[0].message


def test_a_deferral_with_a_trigger_passes(tmp_path):
    spec = SPEC.replace(
        '"do it with what is already in the lockfile" | OUT-OF-SCOPE',
        '"do it with what is already in the lockfile" | DEFERRED — when the lockfile is next cut',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [(v.check, v.message) for v in result.violations]


def test_a_disposition_naming_no_section_fails(tmp_path):
    spec = SPEC.replace(
        '"the widget has to come out of the CLI, not a library call" | §2 |',
        '"the widget has to come out of the CLI, not a library call" | §9 |',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('not a numbered section' in v.message for v in _a13(result))


def test_an_unrecognised_disposition_fails(tmp_path):
    spec = SPEC.replace(
        '"the widget has to come out of the CLI, not a library call" | §2 |',
        '"the widget has to come out of the CLI, not a library call" | handled |',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('none of the four dispositions' in v.message for v in _a13(result))


def test_a13_runs_in_the_author_loop(tmp_path):
    # Part A, so the ledger is answered before the expensive round, not after it.
    spec = SPEC.replace(
        '| RR-02 | "do it with what is already in the lockfile" | OUT-OF-SCOPE |\n', ''
    )
    result = check_spec_ready(_write(tmp_path, spec), structure_only=True)
    assert not result.passed
    assert _a13(result)


def test_register_ids_reads_entries_not_mentions():
    text = (
        '# Register\n\n'
        '### RR-01 — the first\n\nSee RR-01 and RR-99 below for the argument.\n\n'
        '- **RR-02** the second\n\n'
        '| RR-03 | a table row |\n'
    )
    assert register_ids(text) == ['RR-01', 'RR-02', 'RR-03']


def test_the_cause_note_does_not_give_anchor_advice_for_a_ledger_defect(tmp_path, capsys):
    # A13 groups its violations by register, so the report-unit note reached a reader with the
    # A12 instruction "re-anchor the block" about a mechanism their finding does not have.
    from typer.testing import CliRunner

    from keel.cli import app

    spec = SPEC.replace(
        '| RR-01 | "the widget has to come out of the CLI, not a library call" | §2 |\n', ''
    ).replace('| RR-02 | "do it with what is already in the lockfile" | OUT-OF-SCOPE |\n', '')
    path = _write(tmp_path, spec)
    result = CliRunner().invoke(app, ['check-ready', str(path), '--structure-only'])
    assert result.exit_code == 1
    assert 'A13 2 in 1' in result.output, result.output
    assert 'Re-anchor the block' not in result.output
    assert 'one defect' in result.output
