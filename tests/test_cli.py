import os
import subprocess
import sys

from typer.testing import CliRunner

from keel.cli import app

runner = CliRunner()

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
    for command in ('check-ready', 'bind-check', 'budget-drift', 'init'):
        assert command in result.output


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
