import os
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from keel.cli import app

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
    for command in ('check-ready', 'new-spec', 'bind-check', 'budget-drift', 'init', 'show'):
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
    # 2026-07-16 spec §5: the any-agent routing snippet ships with the kit.
    assert (target / 'method-agents-snippet.md').exists()


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


def test_show_doctrine_is_byte_equal_to_the_mirror():
    # §3 (round-1 FM-4): no added trailing newline — the output IS the packaged mirror.
    mirror = (
        Path(__file__).resolve().parents[1] / 'src' / 'keel' / 'method' / 'doctrine.md'
    ).read_text(encoding='utf-8')
    result = runner.invoke(app, ['show', 'doctrine'])
    assert result.exit_code == 0
    assert result.output == mirror


def test_show_list_names_exactly_the_asset_set():
    result = runner.invoke(app, ['show', '--list'])
    assert result.exit_code == 0
    assert result.output.split() == ['doctrine', 'playbook', 'pre-mortem']


def test_show_unknown_asset_exits_2_and_names_the_valid_set():
    result = runner.invoke(app, ['show', 'nonesuch'])
    assert result.exit_code == 2
    for name in ('doctrine', 'playbook', 'pre-mortem'):
        assert name in result.output
