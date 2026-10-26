"""`keel init` points the project's AGENTS.md at the method and its bindings file.

The kit normally goes in a subdirectory (`keel init docs/method`), so AGENTS.md is looked up at
the project root: the git top level of the target, else the current directory.
"""

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from keel.cli import app

runner = CliRunner()

POINTER = (
    'This project applies the keel method; its bindings are in `docs/method/method-bindings.md`.'
)
AGENTS = '# Agent instructions\n\nRead the README first.\n'


def _git_init(root: Path) -> None:
    subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)


@pytest.fixture
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A scratch directory no enclosing repository can claim."""
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path))
    return tmp_path


def test_init_appends_the_method_line_to_root_agents_md_once(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    root = isolated / 'project'
    root.mkdir()
    _git_init(root)
    (root / 'AGENTS.md').write_text(AGENTS, encoding='utf-8')
    monkeypatch.chdir(root)

    first = runner.invoke(app, ['init', 'docs/method'])
    assert first.exit_code == 0, first.output
    after_first = (root / 'AGENTS.md').read_text(encoding='utf-8')
    assert after_first == AGENTS + POINTER + '\n'
    assert 'AGENTS.md' in first.output

    second = runner.invoke(app, ['init', 'docs/method'])
    assert second.exit_code == 2, second.output
    assert 'already exists' in second.output
    assert (root / 'AGENTS.md').read_text(encoding='utf-8') == after_first
    assert 'AGENTS.md' in second.output


def test_init_adds_the_line_even_when_the_copy_refuses(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    # The kit already exists (an earlier init, before AGENTS.md was written): the copy refuses with
    # exit 2, and the AGENTS.md step still runs.
    root = isolated / 'project'
    root.mkdir()
    _git_init(root)
    monkeypatch.chdir(root)
    assert runner.invoke(app, ['init', 'docs/method']).exit_code == 0
    (root / 'AGENTS.md').write_text(AGENTS, encoding='utf-8')

    result = runner.invoke(app, ['init', 'docs/method'])
    assert result.exit_code == 2, result.output
    assert (root / 'AGENTS.md').read_text(encoding='utf-8') == AGENTS + POINTER + '\n'


def test_init_finds_the_git_top_level_from_another_working_directory(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    root = isolated / 'project'
    root.mkdir()
    _git_init(root)
    (root / 'AGENTS.md').write_text(AGENTS, encoding='utf-8')
    elsewhere = isolated / 'elsewhere'
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = runner.invoke(app, ['init', str(root / 'docs' / 'method')])
    assert result.exit_code == 0, result.output
    assert (root / 'AGENTS.md').read_text(encoding='utf-8') == AGENTS + POINTER + '\n'
    assert not (elsewhere / 'AGENTS.md').exists()


def test_init_outside_git_uses_the_current_directory(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    root = isolated / 'plain'
    root.mkdir()
    (root / 'AGENTS.md').write_text(AGENTS, encoding='utf-8')
    monkeypatch.chdir(root)

    result = runner.invoke(app, ['init', 'docs/method'])
    assert result.exit_code == 0, result.output
    assert (root / 'AGENTS.md').read_text(encoding='utf-8') == AGENTS + POINTER + '\n'


def test_init_outside_git_and_outside_the_cwd_leaves_the_cwd_agents_md_alone(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    # The current directory is the root only for a kit inside it: `keel init /tmp/kit` run from
    # some repository must not point that repository's AGENTS.md at a scratch kit.
    here = isolated / 'here'
    here.mkdir()
    (here / 'AGENTS.md').write_text(AGENTS, encoding='utf-8')
    monkeypatch.chdir(here)

    result = runner.invoke(app, ['init', str(isolated / 'scratch' / 'kit')])
    assert result.exit_code == 0, result.output
    assert (here / 'AGENTS.md').read_text(encoding='utf-8') == AGENTS
    assert 'AGENTS.md' in result.output


def test_init_leaves_agents_md_that_already_carries_the_line(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    root = isolated / 'project'
    root.mkdir()
    _git_init(root)
    carried = f'# Agent instructions\n\n{POINTER}\n\nRead the README first.\n'
    (root / 'AGENTS.md').write_bytes(carried.encode('utf-8'))
    monkeypatch.chdir(root)

    result = runner.invoke(app, ['init', 'docs/method'])
    assert result.exit_code == 0, result.output
    assert (root / 'AGENTS.md').read_bytes() == carried.encode('utf-8')
    assert 'unchanged' in result.output


def test_init_terminates_an_unterminated_last_line_and_keeps_crlf(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    root = isolated / 'project'
    root.mkdir()
    _git_init(root)
    (root / 'AGENTS.md').write_bytes(b'# Agent instructions\r\n\r\nRead the README first.')
    monkeypatch.chdir(root)

    result = runner.invoke(app, ['init', 'docs/method'])
    assert result.exit_code == 0, result.output
    expected = f'# Agent instructions\r\n\r\nRead the README first.\r\n{POINTER}\r\n'
    assert (root / 'AGENTS.md').read_bytes() == expected.encode('utf-8')


def test_init_without_agents_md_creates_none_and_says_so(
    isolated: Path, monkeypatch: pytest.MonkeyPatch
):
    root = isolated / 'project'
    root.mkdir()
    _git_init(root)
    monkeypatch.chdir(root)

    result = runner.invoke(app, ['init', 'docs/method'])
    assert result.exit_code == 0, result.output
    assert not (root / 'AGENTS.md').exists()
    assert 'No AGENTS.md' in result.output
    assert (root / 'docs' / 'method' / 'method-bindings.md').exists()


def test_the_method_line_names_no_consumer_toolkit():
    # keel ADR-0003: keel names no consumer toolkit. The line names keel and the bindings file only.
    for name in ('convoy', 'session-workflow', 'craft-collection', 'humblepowers'):
        assert name not in POINTER
    from keel.cli import _agents_pointer_line

    assert _agents_pointer_line('docs/method/method-bindings.md') == POINTER
