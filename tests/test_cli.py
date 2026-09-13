import os
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from keel import __version__
from keel.cli import app
from keel.models import DOR_CHECK_IDS

runner = CliRunner()
_CLI_REFERENCE = Path(__file__).resolve().parents[1] / 'docs' / 'cli-reference.md'

READY_SPEC = """# Spec — widget

## Numbered sections

### §1 Add the widget
Introduce `src/widget.py`. **Acceptance criterion:** `src/widget.py` exposes a
make() function and a unit test asserts the returned value is a Widget.

## Concept → module map

| Concept | Module / file it lives in |
|---|---|
| widget | `src/widget.py` (to be created) |

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** CERTIFIED
"""

# A spec that fails A4 (§2 uncovered) and A5 (missing path) — both produce violations
# whose section labels contain non-ASCII characters (↔ and →).
CRASHY_SPEC = """# Spec — x

## Numbered sections

### §1 One
Do a thing. **Acceptance criterion:** a unit test asserts the first behaviour holds.

### §2 Two
Do another. **Acceptance criterion:** a unit test asserts the second behaviour holds.

## Concept → module map

| Concept | Module / file it lives in |
|---|---|
| x | `src/ghost.py` |

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |

## Pre-mortem certification

- **Reviewer:** r (non-author)
- **Verdict:** CERTIFIED
"""


def test_help_lists_all_commands():
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0
    for command in ('check-ready', 'new-spec', 'bind-check', 'budget-drift', 'init'):
        assert command in result.output


def test_cli_reference_documents_every_command():
    # F9/ARCH-10: the published CLI reference must not lag the typer app (new-spec was 4 releases
    # stale). Every registered command name appears in docs/cli-reference.md.
    reference = _CLI_REFERENCE.read_text(encoding='utf-8')
    names = {c.name for c in app.registered_commands if c.name}
    assert names, 'no commands registered'
    missing = sorted(n for n in names if f'keel {n}' not in reference)
    assert not missing, f'cli-reference.md is missing: {missing}'


def test_check_ready_passes_on_ready_spec(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(READY_SPEC, encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 0
    assert 'OK' in result.output


def test_check_ready_fails_on_uncertified_spec(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace('- **Verdict:** CERTIFIED', '- **Verdict:** not yet certified'),
        encoding='utf-8',
    )
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 1
    assert 'certif' in result.output.lower() or 'pre-mortem' in result.output.lower()


def test_check_ready_missing_spec_exits_2(tmp_path):
    result = runner.invoke(app, ['check-ready', str(tmp_path / 'nope.md')])
    assert result.exit_code == 2
    assert 'not found' in result.output.lower()


def test_check_ready_survives_non_ascii_violations_on_legacy_console(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(CRASHY_SPEC, encoding='utf-8')
    proc = subprocess.run(
        [sys.executable, '-m', 'keel', 'check-ready', str(spec)],
        capture_output=True,
        env={**os.environ, 'PYTHONIOENCODING': 'cp1252'},
        check=False,
    )
    assert b'UnicodeEncodeError' not in proc.stderr, proc.stderr.decode('cp1252', 'replace')
    assert proc.returncode == 1
    assert b'cover' in proc.stdout


def test_init_copies_template_kit(tmp_path):
    target = tmp_path / 'kit'
    result = runner.invoke(app, ['init', str(target)])
    assert result.exit_code == 0
    assert (target / 'definition-of-ready.md').exists()
    assert (target / 'spec-template.md').exists()


def test_init_refuses_overwrite_without_force(tmp_path):
    target = tmp_path / 'kit'
    runner.invoke(app, ['init', str(target)])
    result = runner.invoke(app, ['init', str(target)])
    assert result.exit_code == 2
    assert 'already exists' in result.output


def test_init_force_overwrites(tmp_path):
    target = tmp_path / 'kit'
    runner.invoke(app, ['init', str(target)])
    result = runner.invoke(app, ['init', '--force', str(target)])
    assert result.exit_code == 0


def test_new_spec_stamps_template(tmp_path):
    target = tmp_path / 'specs' / 'my-spec.md'
    result = runner.invoke(app, ['new-spec', str(target)])
    assert result.exit_code == 0, result.output
    assert target.exists()
    text = target.read_text(encoding='utf-8')
    assert 'Numbered sections' in text and 'Pre-mortem certification' in text


def test_new_spec_refuses_overwrite_without_force(tmp_path):
    target = tmp_path / 'my-spec.md'
    runner.invoke(app, ['new-spec', str(target)])
    result = runner.invoke(app, ['new-spec', str(target)])
    assert result.exit_code == 2
    assert 'already exists' in result.output


def test_new_spec_force_overwrites(tmp_path):
    target = tmp_path / 'my-spec.md'
    runner.invoke(app, ['new-spec', str(target)])
    result = runner.invoke(app, ['new-spec', '--force', str(target)])
    assert result.exit_code == 0


def test_check_ready_structural_failure_points_at_template(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text('# Spec — empty\n\nNo structure at all here.\n', encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' in result.output or 'new-spec' in result.output


def test_check_ready_content_failure_no_pointer(tmp_path):
    # content-only failure (structure present, trivial criterion): must NOT print the pointer.
    content_fail = READY_SPEC.replace(
        '`src/widget.py` exposes a\nmake() function and a unit test asserts the returned value '
        'is a Widget.',
        'done.',
    )
    spec = tmp_path / 'spec.md'
    spec.write_text(content_fail, encoding='utf-8')
    result = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' not in result.output and 'new-spec' not in result.output


def test_malformed_unnumbered_heading_points_at_template(tmp_path):
    # §5(a) / T4a: a present-but-malformed structure (un-numbered heading) also gets the pointer.
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace('### §1 Add the widget', '### Add the widget'), encoding='utf-8'
    )
    result = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' in result.output or 'new-spec' in result.output


def test_malformed_many_to_one_manifest_points_at_template(tmp_path):
    # §5(a) / T4a: a many-to-one manifest (not a bijection) gets the pointer.
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace('| PR01 | §1 | yes |', '| PR01 | §1 | yes |\n| PR02 | §1 | yes |'),
        encoding='utf-8',
    )
    result = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' in result.output or 'new-spec' in result.output


def test_malformed_empty_manifest_points_at_template(tmp_path):
    # §5(a) / T4a: an empty/header-only manifest (the `has no PR` trigger) gets the pointer.
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace('|---|---|---|\n| PR01 | §1 | yes |', '|---|---|---|'), encoding='utf-8'
    )
    result = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' in result.output or 'new-spec' in result.output


def test_coverage_slip_no_pointer(tmp_path):
    # §5(a) / T4a: a §2 uncovered by the manifest is a content slip on a template-shaped spec —
    # no pointer (ADR-0006: do not re-open author-loop noise on a content failure).
    two_section = READY_SPEC.replace(
        '\n## Concept → module map',
        '\n### §2 Wire it\nWire it. **Acceptance criterion:** an integration test asserts the '
        'wired behaviour holds.\n\n## Concept → module map',
    )
    spec = tmp_path / 'spec.md'
    spec.write_text(two_section, encoding='utf-8')
    result = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' not in result.output and 'new-spec' not in result.output


def test_missing_concept_path_no_pointer(tmp_path):
    # §5(a) / T4a: an A5 grounding failure (path does not exist) is content, not shape — no pointer.
    (tmp_path / '.git').mkdir()
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace(
            '| widget | `src/widget.py` (to be created) |', '| widget | `src/ghost.py` |'
        ),
        encoding='utf-8',
    )
    result = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert result.exit_code == 1
    assert 'spec-template.md' not in result.output and 'new-spec' not in result.output


def test_version_flag_prints_version():
    from keel import __version__

    result = runner.invoke(app, ['--version'])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_structure_only_skips_b1(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace('- **Verdict:** CERTIFIED', '- **Verdict:** not yet certified'),
        encoding='utf-8',
    )
    # Part A is clean but B1 would fail; --structure-only skips B1 only.
    structure = runner.invoke(app, ['check-ready', '--structure-only', str(spec)])
    assert structure.exit_code == 0, structure.output
    assert 'OK' in structure.output
    # Without the flag, B1 fires.
    full = runner.invoke(app, ['check-ready', str(spec)])
    assert full.exit_code == 1


def test_conditional_certify_with_operator_passes_with_warn(tmp_path):
    # §2 / T1b: an operator-accepted CONDITIONAL-CERTIFY passes (exit 0) and prints a WARN line.
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace(
            '- **Verdict:** CERTIFIED',
            '- **Verdict:** CONDITIONAL-CERTIFY — ready modulo a fix\n- **Operator:** grimaldo',
        ),
        encoding='utf-8',
    )
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 0, result.output
    assert 'WARN' in result.output and 'grimaldo' in result.output
    assert 'OK' in result.output


def test_warnings_print_on_a_failing_spec(tmp_path):
    # 0.12.0 §1 (FM-2): a failing run still shows its WARN lines — they carry this release's
    # new signals and were previously dropped on the violations path.
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC.replace(
            '- **Verdict:** CERTIFIED',
            '- **Verdict:** CONDITIONAL-CERTIFY — ready modulo a fix\n- **Operator:** grimaldo',
        ).replace('Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See §9 for it.'),
        encoding='utf-8',
    )
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 1
    assert '§9' in result.output  # the violation
    assert 'WARN' in result.output and 'grimaldo' in result.output  # the warning, not dropped


def test_spec_hash_prints_stable_hex(tmp_path):
    # 0.12.0 §1: `keel spec-hash` prints the canonical hash; stable across invocations.
    spec = tmp_path / 'spec.md'
    spec.write_text(READY_SPEC, encoding='utf-8')
    first = runner.invoke(app, ['spec-hash', str(spec)])
    second = runner.invoke(app, ['spec-hash', str(spec)])
    assert first.exit_code == 0 and second.exit_code == 0
    digest = first.output.strip()
    assert digest == second.output.strip()
    assert len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)


def test_spec_hash_missing_file_exits_2(tmp_path):
    result = runner.invoke(app, ['spec-hash', str(tmp_path / 'nope.md')])
    assert result.exit_code == 2
    assert 'not found' in result.output.lower()


# --- E2c: a verdict names the copy that produced it --------------------------
#
# `_emit` printed warnings, then `OK`, and exited. Two plugin caches were live on one machine and
# nothing in any keel output distinguished them: a session ran 0.18.0 by `uvx` while 0.18.1 was
# installed, reconstructed that fact from paths afterwards, and filed a finding whose premise was
# wrong. The same line answers the other half — an `OK` from a gate that had nothing applicable to
# check reads exactly like an `OK` from a thorough one.


def test_the_passing_verdict_names_the_running_version_and_what_was_checked(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(READY_SPEC, encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 0
    assert f'keel {__version__} —' in result.output
    assert 'checks applicable' in result.output and 'fired' in result.output


def test_the_failing_verdict_names_the_running_version_too(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(CRASHY_SPEC, encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 1
    assert f'keel {__version__} —' in result.output


def test_the_summary_counts_applicable_checks_not_the_catalogue(tmp_path):
    # The count that makes a vacuous run visible: checks with a construct to read, not all of them.
    spec = tmp_path / 'spec.md'
    spec.write_text(READY_SPEC, encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(spec)])
    summary = next(line for line in result.output.splitlines() if line.startswith('keel '))
    applicable = int(summary.split('—')[1].split()[0])
    assert 0 < applicable < len(DOR_CHECK_IDS)


def test_a_gate_with_no_probes_still_names_the_version(tmp_path):
    # `bind-check` returns findings without probes; the attribution half holds for every gate.
    bindings = tmp_path / 'bindings.md'
    bindings.write_text('# Method bindings\n\nno table here\n', encoding='utf-8')
    result = runner.invoke(app, ['bind-check', str(bindings)])
    assert f'keel {__version__}' in result.output


def test_decompose_check_fails_when_no_series_review_is_recorded(tmp_path):
    # The gate's whole point: a decomposition nobody read does not reach execution. READY_SPEC is
    # a spec that PASSES the DoR gate, which is exactly the state this one must still refuse.
    spec = tmp_path / 'spec.md'
    spec.write_text(READY_SPEC, encoding='utf-8')
    result = runner.invoke(app, ['decompose-check', str(spec)])
    assert result.exit_code == 1
    assert 'series review' in result.output.lower()
    assert 'Series verdict' in result.output, 'the rejection does not print the grammar it parses'


def test_decompose_check_passes_on_a_recorded_review(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(
        READY_SPEC
        + '\n### Series review\n\n'
        + '- **Series reviewer:** a second non-author\n'
        + '- **Series verdict:** CERTIFIED\n'
        + '- **Series artifact:** spec.series-premortem.md\n',
        encoding='utf-8',
    )
    (tmp_path / 'spec.series-premortem.md').write_text(
        'PREMORTEM-VERDICT: CERTIFIED\n', encoding='utf-8'
    )
    result = runner.invoke(app, ['decompose-check', str(spec)])
    assert result.exit_code == 0, result.output
    assert 'OK' in result.output
    assert f'keel {__version__}' in result.output


def test_decompose_check_missing_spec_exits_2(tmp_path):
    result = runner.invoke(app, ['decompose-check', str(tmp_path / 'nope.md')])
    assert result.exit_code == 2
    assert 'not found' in result.output.lower()
