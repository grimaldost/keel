import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from keel import __version__
from keel.cli import app
from keel.models import DOR_CHECK_IDS
from keel.vocabulary import BLOCK_END, DIGEST_CHARS, block_marker

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


# --- the newer-keel warning (SW17) ---------------------------------------------


def _ledger_with(tmp_path, monkeypatch, gate: str) -> Path:
    ledger = tmp_path / 'newer-ledger.jsonl'
    ledger.write_text(json.dumps({'gate': gate}) + '\n', encoding='utf-8')
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(ledger))
    return ledger


def _write_spec(tmp_path, *, ready: bool) -> Path:
    spec = tmp_path / 'spec.md'
    text = READY_SPEC
    if not ready:
        text = text.replace('- **Verdict:** CERTIFIED', '- **Verdict:** not yet certified')
    spec.write_text(text, encoding='utf-8')
    return spec


def test_check_ready_warns_when_a_newer_keel_has_run_on_this_machine(tmp_path, monkeypatch):
    _ledger_with(tmp_path, monkeypatch, '99.0.0')
    spec = _write_spec(tmp_path, ready=True)
    result = runner.invoke(app, ['check-ready', str(spec)])
    warn = [line for line in result.output.splitlines() if line.startswith('WARN: keel 99.0.0')]
    assert len(warn) == 1
    assert f'this is keel {__version__}' in warn[0]
    assert 'uv tool upgrade keel' in warn[0]
    assert result.exit_code == 0


def test_the_newer_keel_warning_leaves_the_failing_exit_code_alone(tmp_path, monkeypatch):
    _ledger_with(tmp_path, monkeypatch, '99.0.0')
    spec = _write_spec(tmp_path, ready=False)
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert 'WARN: keel 99.0.0 has run on this machine' in result.output
    assert result.exit_code == 1


def test_no_newer_keel_warning_for_an_equal_or_older_version(tmp_path, monkeypatch):
    spec = _write_spec(tmp_path, ready=True)
    for gate in (__version__, '0.0.1'):
        _ledger_with(tmp_path, monkeypatch, gate)
        result = runner.invoke(app, ['check-ready', str(spec)])
        assert 'has run on this machine' not in result.output
        assert result.exit_code == 0


def test_no_newer_keel_warning_when_the_ledger_is_off_or_missing(tmp_path, monkeypatch):
    spec = _write_spec(tmp_path, ready=True)
    monkeypatch.setenv('KEEL_GATE_LEDGER', 'off')
    assert 'has run on this machine' not in runner.invoke(app, ['check-ready', str(spec)]).output
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(tmp_path / 'missing.jsonl'))
    assert 'has run on this machine' not in runner.invoke(app, ['check-ready', str(spec)]).output


def test_an_unreadable_ledger_leaves_check_ready_passing_without_a_warning(tmp_path, monkeypatch):
    ledger = _ledger_with(tmp_path, monkeypatch, '99.0.0')
    spec = _write_spec(tmp_path, ready=True)
    real_read_text = Path.read_text

    def read_text(self, *args, **kwargs):
        if self == ledger:
            raise PermissionError(13, 'Permission denied')
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', read_text)
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert result.exit_code == 0, result.output
    assert 'has run on this machine' not in result.output


def test_the_default_test_ledger_is_not_the_developers_real_one(tmp_path):
    # The autouse fixture in conftest.py: no test may append to the real ledger.
    from keel.gate_ledger import ledger_path

    path = ledger_path()
    assert path is not None and path != Path.home() / '.keel' / 'gate-ledger.jsonl'


# The stale-block notice: `keel check-ready` judges the vocabulary block nearest the spec. Every
# fixture is a git repository inside `tmp_path`, with git's discovery stopped above it.

_NOTICE = 'WARN: the vocabulary block'
_OLD_DIGEST = '0123456789ab'
_STALE_BLOCK = f'{block_marker(_OLD_DIGEST)}\n- voyage\n{BLOCK_END}\n'
_SCHEMA_LINE = 'schema = "work-vocabulary/v1"\n'
_USER_VOYAGE = _SCHEMA_LINE + '\n[[nouns]]\nname = "voyage"\naxis = "scope"\n'
_PROJECT_BERTH = _SCHEMA_LINE + '\n[[nouns]]\nname = "berth"\naxis = "place"\n'
_PROJECT_NOT_BOUND = _SCHEMA_LINE + 'status = "not bound"\nreason = "the crew names its own work"\n'


def _vocabulary_repo(tmp_path, monkeypatch, agents: str | bytes = _STALE_BLOCK) -> Path:
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.resolve().parent))
    repo = tmp_path / 'repo'
    (repo / 'docs').mkdir(parents=True)
    subprocess.run(['git', 'init', '-q', str(repo)], check=True, capture_output=True)
    path = repo / 'AGENTS.md'
    if isinstance(agents, bytes):
        path.write_bytes(agents)
    else:
        path.write_text(agents, encoding='utf-8')
    return repo.resolve()


def _user_vocabulary(tmp_path, monkeypatch, body: str = _USER_VOYAGE) -> Path:
    path = tmp_path / 'config' / 'vocabulary.toml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    monkeypatch.setenv('KEEL_VOCABULARY', str(path))
    return path


def _project_vocabulary(repo: Path, body: str) -> Path:
    path = repo / '.keel' / 'vocabulary.toml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    return path


def _repo_spec(repo: Path, *, ready: bool) -> Path:
    spec = repo / 'docs' / 'spec.md'
    text = READY_SPEC if ready else READY_SPEC.replace('**Verdict:** CERTIFIED', '**Verdict:** no')
    spec.write_text(text, encoding='utf-8')
    return spec


def _resolved_head(repo: Path) -> str:
    from keel.vocabulary import resolve

    digest = resolve(repo, assume_scope=True).digest
    assert digest is not None
    return digest[:DIGEST_CHARS]


def _notice_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.startswith(_NOTICE)]


def _exit_without_block(spec: Path, repo: Path) -> int:
    """The same spec's exit code once no instruction file carries a block."""
    (repo / 'AGENTS.md').write_text('# Agents\n', encoding='utf-8')
    (repo / 'CLAUDE.md').unlink(missing_ok=True)
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert not _notice_lines(result.output), result.output
    return result.exit_code


def test_check_ready_warns_on_a_stale_vocabulary_block(tmp_path, monkeypatch):
    for ready in (True, False):
        case = tmp_path / ('ready' if ready else 'failing')
        case.mkdir()
        repo = _vocabulary_repo(case, monkeypatch)
        _user_vocabulary(case, monkeypatch)
        spec = _repo_spec(repo, ready=ready)
        result = runner.invoke(app, ['check-ready', str(spec)])
        expected = (
            f'WARN: the vocabulary block in {repo / "AGENTS.md"} is stale '
            f'(block {_OLD_DIGEST}, resolved {_resolved_head(repo)}) — run keel vocabulary --write'
        )
        assert _notice_lines(result.output) == [expected], result.output
        assert result.exit_code == (0 if ready else 1), result.output
        assert result.exit_code == _exit_without_block(spec, repo)


def test_the_stale_block_notice_is_not_ledgered(tmp_path, monkeypatch):
    ledger = tmp_path / 'ledger.jsonl'
    monkeypatch.setenv('KEEL_GATE_LEDGER', str(ledger))
    repo = _vocabulary_repo(tmp_path, monkeypatch)
    _user_vocabulary(tmp_path, monkeypatch)
    spec = _repo_spec(repo, ready=True)
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert _notice_lines(result.output), result.output
    with_notice = json.loads(ledger.read_text(encoding='utf-8').splitlines()[-1])
    _exit_without_block(spec, repo)
    rows = ledger.read_text(encoding='utf-8').splitlines()
    assert len(rows) == 2
    without_block = json.loads(rows[-1])
    # The notice adds no GateResult warning: the run's counts match the same spec with no block.
    assert with_notice['warns'] == without_block['warns']
    assert with_notice['probes'] == without_block['probes']


def test_check_ready_warns_on_a_stale_block_under_a_project_list_without_a_user_file(
    tmp_path, monkeypatch
):
    repo = _vocabulary_repo(tmp_path, monkeypatch)
    _project_vocabulary(repo, _PROJECT_BERTH)
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    expected = (
        f'WARN: the vocabulary block in {repo / "AGENTS.md"} is stale '
        f'(block {_OLD_DIGEST}, resolved {_resolved_head(repo)}) — run keel vocabulary --write'
    )
    assert _notice_lines(result.output) == [expected], result.output
    assert result.exit_code == 0


def test_check_ready_is_silent_with_no_vocabulary_block(tmp_path, monkeypatch):
    repo = _vocabulary_repo(tmp_path, monkeypatch, agents='# Agents\n')
    _user_vocabulary(tmp_path, monkeypatch)
    _project_vocabulary(repo, _PROJECT_BERTH)
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    assert 'vocabulary' not in result.output
    assert result.exit_code == 0


def test_check_ready_is_silent_on_an_estate_block_without_the_user_file(tmp_path, monkeypatch):
    repo = _vocabulary_repo(tmp_path, monkeypatch)
    spec = _repo_spec(repo, ready=True)
    # The hermetic user-level path does not exist.
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert 'vocabulary' not in result.output
    assert result.exit_code == 0
    _user_vocabulary(tmp_path, monkeypatch)
    monkeypatch.setenv('KEEL_VOCABULARY', 'off')
    result = runner.invoke(app, ['check-ready', str(spec)])
    assert 'vocabulary' not in result.output
    assert result.exit_code == 0


def test_check_ready_is_silent_on_a_not_bound_project(tmp_path, monkeypatch):
    repo = _vocabulary_repo(tmp_path, monkeypatch)
    _user_vocabulary(tmp_path, monkeypatch)
    _project_vocabulary(repo, _PROJECT_NOT_BOUND)
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    assert 'vocabulary' not in result.output
    assert result.exit_code == 0


@pytest.mark.parametrize('silence', ['user file off', 'user file absent', 'not bound'])
def test_a_silent_notice_reads_no_instruction_file(tmp_path, monkeypatch, silence):
    # An AGENTS.md saved as UTF-16 cannot be read as UTF-8; where a silence rule applies, the
    # notice never opens it, so a repository that never adopted the vocabulary sees no line.
    utf16_agents = '# Agents\n'.encode('utf-16')
    for ready in (True, False):
        case = tmp_path / ('ready' if ready else 'failing')
        case.mkdir()
        repo = _vocabulary_repo(case, monkeypatch, agents=utf16_agents)
        if silence == 'user file off':
            _user_vocabulary(case, monkeypatch)
            monkeypatch.setenv('KEEL_VOCABULARY', 'off')
        elif silence == 'user file absent':
            monkeypatch.setenv('KEEL_VOCABULARY', str(case / 'nowhere' / 'vocabulary.toml'))
        else:
            _user_vocabulary(case, monkeypatch)
            _project_vocabulary(repo, _PROJECT_NOT_BOUND)
        spec = _repo_spec(repo, ready=ready)
        result = runner.invoke(app, ['check-ready', str(spec)])
        assert 'vocabulary' not in result.output, result.output
        assert result.exit_code == _exit_without_block(spec, repo)


def test_a_user_level_file_makes_an_undecodable_instruction_file_a_fault_line(
    tmp_path, monkeypatch
):
    # The user-level file applies to the whole machine: with one present, a repository that has no
    # block and no project list is still judged, so its UTF-16 AGENTS.md prints the fault line.
    # With the user-level file off the same run prints nothing, and the exit code is the same.
    utf16_agents = '# Agents\n'.encode('utf-16')
    for ready in (True, False):
        case = tmp_path / ('ready' if ready else 'failing')
        case.mkdir()
        repo = _vocabulary_repo(case, monkeypatch, agents=utf16_agents)
        _user_vocabulary(case, monkeypatch)
        spec = _repo_spec(repo, ready=ready)
        result = runner.invoke(app, ['check-ready', str(spec)])
        faults = _notice_lines(result.output)
        assert len(faults) == 1, result.output
        assert faults[0].startswith('WARN: the vocabulary block could not be judged'), faults
        assert 'AGENTS.md' in faults[0], faults
        assert result.exit_code == (0 if ready else 1), result.output
        monkeypatch.setenv('KEEL_VOCABULARY', 'off')
        silent = runner.invoke(app, ['check-ready', str(spec)])
        assert 'vocabulary' not in silent.output, silent.output
        assert result.exit_code == silent.exit_code


def test_the_reference_says_the_user_level_file_applies_to_the_whole_machine():
    row = next(
        line
        for line in _CLI_REFERENCE.read_text(encoding='utf-8').splitlines()
        if line.startswith('| `keel check-ready <spec> [--structure-only]`')
    )
    row = ' '.join(row.split())
    fault_sentence = 'WARN: the vocabulary block could not be judged'
    assert fault_sentence in row
    after = row.split(fault_sentence, 1)[1]
    sentence, _, rest = after.partition('Like the upgrade line,')
    assert rest, 'the sentence must come before "Like the upgrade line,"'
    for words in (
        'user-level file applies to the whole machine',
        'never adopted the vocabulary',
        'on every run',
        'not valid UTF-8',
    ):
        assert words in sentence, words


def test_outside_git_the_notice_judges_the_nearest_folder_with_an_instruction_file(
    tmp_path, monkeypatch
):
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.resolve().parent))
    _user_vocabulary(tmp_path, monkeypatch)
    folder = (tmp_path / 'voyage-folder').resolve()
    sub = folder / 'sub'
    sub.mkdir(parents=True)
    (folder / 'AGENTS.md').write_text(_STALE_BLOCK, encoding='utf-8')
    (sub / 'CLAUDE.md').write_text('# Claude\n', encoding='utf-8')
    (sub / 'spec.md').write_text(READY_SPEC, encoding='utf-8')
    (folder / 'spec.md').write_text(READY_SPEC, encoding='utf-8')

    # Outside git, sub's own instruction file ends the walk and decides alone: no block, silent.
    result = runner.invoke(app, ['check-ready', str(sub / 'spec.md')])
    assert 'vocabulary' not in result.output, result.output
    assert result.exit_code == 0

    result = runner.invoke(app, ['check-ready', str(folder / 'spec.md')])
    expected = (
        f'WARN: the vocabulary block in {folder / "AGENTS.md"} is stale '
        f'(block {_OLD_DIGEST}, resolved {_resolved_head(folder)}) — run keel vocabulary --write'
    )
    assert _notice_lines(result.output) == [expected], result.output
    assert result.exit_code == 0


def test_inside_git_the_notice_walks_past_a_nested_file_without_a_block(tmp_path, monkeypatch):
    repo = _vocabulary_repo(tmp_path, monkeypatch)
    _user_vocabulary(tmp_path, monkeypatch)
    (repo / 'docs' / 'AGENTS.md').write_text('# Docs\n', encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    expected = (
        f'WARN: the vocabulary block in {repo / "AGENTS.md"} is stale '
        f'(block {_OLD_DIGEST}, resolved {_resolved_head(repo)}) — run keel vocabulary --write'
    )
    assert _notice_lines(result.output) == [expected], result.output
    assert result.exit_code == 0


def test_check_ready_is_silent_on_a_current_block(tmp_path, monkeypatch):
    from keel.vocabulary import render_block, resolve

    repo = _vocabulary_repo(tmp_path, monkeypatch, agents='# Agents\n')
    _user_vocabulary(tmp_path, monkeypatch)
    (repo / 'AGENTS.md').write_text(render_block(resolve(repo, assume_scope=True)), 'utf-8')
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    assert 'vocabulary' not in result.output
    assert result.exit_code == 0


def test_check_ready_warns_on_an_instruction_file_beside_the_block_without_one(
    tmp_path, monkeypatch
):
    from keel.vocabulary import render_block, resolve

    repo = _vocabulary_repo(tmp_path, monkeypatch, agents='# Agents\n')
    _user_vocabulary(tmp_path, monkeypatch)
    (repo / 'AGENTS.md').write_text(render_block(resolve(repo, assume_scope=True)), 'utf-8')
    (repo / 'CLAUDE.md').write_text('# Claude\n', encoding='utf-8')
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    expected = (
        f'WARN: the vocabulary block in {repo / "CLAUDE.md"} is missing '
        f'(resolved {_resolved_head(repo)}) — run keel vocabulary --write'
    )
    assert _notice_lines(result.output) == [expected], result.output
    assert result.exit_code == 0


def _assert_one_fault_line(result, names: str, expected_exit: int) -> None:
    lines = [line for line in result.output.splitlines() if 'vocabulary' in line]
    assert len(lines) == 1, result.output
    assert lines[0].startswith('WARN: the vocabulary block could not be judged — '), lines[0]
    assert names in lines[0], lines[0]
    assert result.exit_code == expected_exit, result.output


def test_a_malformed_user_file_prints_one_warning_and_keeps_the_exit_code(tmp_path, monkeypatch):
    for ready in (True, False):
        case = tmp_path / ('ready' if ready else 'failing')
        case.mkdir()
        repo = _vocabulary_repo(case, monkeypatch)
        user = _user_vocabulary(case, monkeypatch, body='schema = [broken\n')
        spec = _repo_spec(repo, ready=ready)
        result = runner.invoke(app, ['check-ready', str(spec)])
        _assert_one_fault_line(result, str(user), _exit_without_block(spec, repo))


def test_a_malformed_project_file_prints_one_warning_and_keeps_the_exit_code(tmp_path, monkeypatch):
    for ready in (True, False):
        case = tmp_path / ('ready' if ready else 'failing')
        case.mkdir()
        repo = _vocabulary_repo(case, monkeypatch)
        project = _project_vocabulary(repo, _SCHEMA_LINE + 'tally = 3\n')
        spec = _repo_spec(repo, ready=ready)
        result = runner.invoke(app, ['check-ready', str(spec)])
        _assert_one_fault_line(result, str(project), _exit_without_block(spec, repo))


def test_an_undecodable_agents_file_prints_one_warning_and_keeps_the_exit_code(
    tmp_path, monkeypatch
):
    undecodable = b'# Agents \xff\xfe\n' + _STALE_BLOCK.encode('utf-8')
    for ready in (True, False):
        case = tmp_path / ('ready' if ready else 'failing')
        case.mkdir()
        repo = _vocabulary_repo(case, monkeypatch, agents=undecodable)
        _user_vocabulary(case, monkeypatch)
        spec = _repo_spec(repo, ready=ready)
        result = runner.invoke(app, ['check-ready', str(spec)])
        _assert_one_fault_line(result, 'AGENTS.md', _exit_without_block(spec, repo))


def test_an_unexpected_fault_in_the_notice_prints_one_warning(tmp_path, monkeypatch):
    def broken(*args, **kwargs):
        raise OSError(5, 'Input/output error', 'AGENTS.md')

    repo = _vocabulary_repo(tmp_path, monkeypatch)
    _user_vocabulary(tmp_path, monkeypatch)
    monkeypatch.setattr('keel.cli.resolve', broken)
    result = runner.invoke(app, ['check-ready', str(_repo_spec(repo, ready=True))])
    _assert_one_fault_line(result, 'AGENTS.md', 0)


def test_cli_reference_documents_the_stale_block_notice():
    reference = _CLI_REFERENCE.read_text(encoding='utf-8')
    row = next(line for line in reference.splitlines() if line.startswith('| `keel check-ready'))
    assert (
        '`WARN: the vocabulary block in <file> is stale (block <a>, resolved <b>) — '
        'run keel vocabulary --write`'
    ) in row
