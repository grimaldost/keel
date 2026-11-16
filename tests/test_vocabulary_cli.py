"""`keel vocabulary`: the resolver's result, printed as text and as one JSON object.

Every fixture is bounded: a git repository made with `git init` inside `tmp_path`, with git's
discovery stopped at the fixture. The nouns are invented.
"""

import json
import re
import subprocess
from dataclasses import asdict
from pathlib import Path

import pytest
from typer.testing import CliRunner

from keel.cli import app
from keel.vocabulary import BLOCK_BEGIN, BLOCK_END, SCHEMA, TOOL_NOUNS, resolve

runner = CliRunner()

BLOCK = BLOCK_BEGIN.format(digest='0123456789ab') + '\n- voyage\n' + BLOCK_END + '\n'

USER_VOYAGE = f"""\
schema = "{SCHEMA}"
rule = "Say voyage for the whole crossing."

[[nouns]]
name = "voyage"
axis = "scope"
reading = "a crossing"
definition = "every leg between two ports"

[[allowed]]
term = "tally"
note = "a count, not a unit of work"

[[retired]]
noun = "sprint-x"
instead = "voyage"
"""

PROJECT_BERTH = f"""\
schema = "{SCHEMA}"
rule = "Say berth for a place in port."

[[nouns]]
name = "berth"
axis = "place"
reading = "a mooring"
definition = "where a vessel ties up"
"""

PROJECT_NOT_BOUND = f"""\
schema = "{SCHEMA}"
status = "not bound"
reason = "the crew names its own work"
"""


@pytest.fixture(autouse=True)
def _no_git_above(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stop git's discovery at the fixture, so a folder outside git stays outside git."""
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.resolve().parent))


def _plain(value):
    """What JSON holds for a dataclass dump: tuples read back as lists."""
    return json.loads(json.dumps(value))


def _repo(tmp_path: Path, *, block: bool = True) -> Path:
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True, capture_output=True)
    (repo / 'AGENTS.md').write_text(BLOCK if block else '# Agents\n', encoding='utf-8')
    return repo


def _user_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str) -> Path:
    path = tmp_path / 'config' / 'vocabulary.toml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    monkeypatch.setenv('KEEL_VOCABULARY', str(path))
    return path


def _project_file(repo: Path, body: str) -> Path:
    path = repo / '.keel' / 'vocabulary.toml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    return path


def test_text_prints_every_item_for_a_user_file_in_scope(tmp_path: Path, monkeypatch) -> None:
    user = _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    vocabulary = resolve(repo)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    out = result.output
    assert vocabulary.digest is not None
    assert re.fullmatch(r'[0-9a-f]{64}', vocabulary.digest)
    assert vocabulary.digest in out
    for layer in vocabulary.layers:
        assert layer.source in out
    assert str(user) in out
    assert SCHEMA in out
    for noun in vocabulary.nouns:
        assert noun.name in out
        assert f'axis: {noun.axis}' in out
        for sense in noun.senses:
            assert sense.text in out
    assert 'a crossing' in out
    assert 'every leg between two ports' in out
    assert 'tally' in out
    assert 'a count, not a unit of work' in out
    assert 'Say voyage for the whole crossing.' in out
    assert 'sprint-x' in out
    assert 'voyage' in out.split('retired', 1)[1]
    # each noun carries the layer it came from
    assert re.search(r'^wave \[keel\]', out, re.MULTILINE)
    assert re.search(r'^voyage \[user\]', out, re.MULTILINE)


def test_text_orders_the_items(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    vocabulary = resolve(repo)

    out = runner.invoke(app, ['vocabulary', str(repo)]).output

    assert vocabulary.digest is not None
    marks = [
        out.index('layers:'),
        out.index('nouns:'),
        out.index('allowed:'),
        out.index('rule:'),
        out.index('retired:'),
        out.index(vocabulary.digest),
    ]
    assert marks == sorted(marks)


def test_text_prints_the_notes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv('KEEL_VOCABULARY', str(tmp_path / 'missing' / 'vocabulary.toml'))
    repo = _repo(tmp_path)
    vocabulary = resolve(repo)
    assert vocabulary.notes

    out = runner.invoke(app, ['vocabulary', str(repo)]).output

    for note in vocabulary.notes:
        assert note in out


def test_text_out_of_scope_resolves_keel_alone(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path, block=False)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    assert 'voyage' not in result.output
    for noun in TOOL_NOUNS:
        assert noun.name in result.output


def test_path_defaults_to_the_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)

    result = runner.invoke(app, ['vocabulary', '--json'])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)['path'] == str(repo.resolve())
    assert json.loads(result.output)['in_scope'] is True


def test_json_parses_back_to_the_resolved_values(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    vocabulary = resolve(repo)

    result = runner.invoke(app, ['vocabulary', str(repo), '--json'])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert list(data) == [
        'path',
        'in_scope',
        'layers',
        'nouns',
        'allowed',
        'rule',
        'retired',
        'notes',
        'not_bound',
        'digest',
    ]
    assert data['path'] == str(repo.resolve())
    assert data['in_scope'] is True
    assert data['layers'] == [asdict(layer) for layer in vocabulary.layers]
    assert data['layers'][0] == {
        'name': 'keel',
        'source': data['layers'][0]['source'],
        'schema': '',
    }
    assert data['layers'][1]['schema'] == SCHEMA
    assert data['nouns'] == _plain([asdict(noun) for noun in vocabulary.nouns])
    assert data['allowed'] == [asdict(item) for item in vocabulary.allowed]
    assert data['rule'] == vocabulary.rule
    assert data['retired'] == [asdict(item) for item in vocabulary.retired]
    assert data['notes'] == list(vocabulary.notes)
    assert data['not_bound'] is None
    assert data['digest'] == vocabulary.digest
    voyage = next(noun for noun in data['nouns'] if noun['name'] == 'voyage')
    assert voyage['layer'] == 'user'
    assert voyage['reading'] == 'a crossing'
    wave = next(noun for noun in data['nouns'] if noun['name'] == 'wave')
    assert wave['senses'][0]['text'] == 'the batch a task ships with'
    assert set(wave['senses'][0]) == {'text', 'glossary'}


def test_json_keeps_non_ascii_text_unescaped(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE.replace('a crossing', 'a crossing — whole'))
    repo = _repo(tmp_path)

    result = runner.invoke(app, ['vocabulary', str(repo), '--json'])

    assert result.exit_code == 0, result.output
    assert '— whole' in result.output
    assert '\\u2014' not in result.output


def test_project_file_replaces_the_lower_layers(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    project = _project_file(repo, PROJECT_BERTH)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    assert str(project) in result.output
    assert re.search(r'^berth \[project\]', result.output, re.MULTILINE)
    assert 'a mooring' in result.output
    assert 'where a vessel ties up' in result.output
    assert not re.search(r'^voyage ', result.output, re.MULTILINE)


def test_not_bound_prints_its_reason_and_exits_zero(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    project = _project_file(repo, PROJECT_NOT_BOUND)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    assert 'not bound — the crew names its own work' in result.output
    assert str(project) in result.output
    assert 'nouns:' not in result.output
    assert not re.search(r'[0-9a-f]{64}', result.output)


def test_not_bound_json(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    _project_file(repo, PROJECT_NOT_BOUND)

    result = runner.invoke(app, ['vocabulary', str(repo), '--json'])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data['not_bound'] == 'the crew names its own work'
    assert data['digest'] is None
    assert data['nouns'] == []
    assert data['layers'][0]['name'] == 'project'


def test_malformed_user_file_exits_two_and_names_the_file(tmp_path: Path, monkeypatch) -> None:
    user = _user_file(tmp_path, monkeypatch, 'schema = "work-vocabulary/v1"\nnouns = 3\n')
    repo = _repo(tmp_path)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 2
    assert str(user) in result.output
    assert 'Traceback' not in result.output


def test_malformed_project_file_exits_two_in_json_mode_too(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    project = _project_file(repo, 'this is = = not toml\n')

    result = runner.invoke(app, ['vocabulary', str(repo), '--json'])

    assert result.exit_code == 2
    assert str(project) in result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
