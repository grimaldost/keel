"""`keel vocabulary`: the resolver's result, printed as text and as one JSON object.

Every fixture is bounded: a git repository made with `git init` inside `tmp_path`, with git's
discovery stopped at the fixture. The nouns are invented.
"""

import json
import os
import re
import stat
import subprocess
from dataclasses import asdict
from pathlib import Path

import pytest
from typer.testing import CliRunner

import keel
from keel.cli import app
from keel.vocabulary import (
    BLOCK_BEGIN,
    BLOCK_END,
    BLOCK_RE,
    DIGEST_CHARS,
    SCHEMA,
    TOOL_NOUNS,
    block_marker,
    render_block,
    resolve,
)

runner = CliRunner()

CLI_REFERENCE = Path(__file__).resolve().parents[1] / 'docs' / 'cli-reference.md'

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


@pytest.fixture(autouse=True)
def _away_from_the_checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run every test from its own folder, so a root regression cannot write this checkout."""
    monkeypatch.chdir(tmp_path)


def _plain(value):
    """What JSON holds for a dataclass dump: tuples read back as lists."""
    return json.loads(json.dumps(value))


def _noun(vocabulary, name: str):
    return next(noun for noun in vocabulary.nouns if noun.name == name)


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
    lines = out.splitlines()
    assert f'  keel: {keel.__version__}' in lines
    assert f'  user: {user} ({SCHEMA})' in lines
    for noun in vocabulary.nouns:
        assert f'{noun.name} [{noun.layer}] axis: {noun.axis}' in lines
        for sense in noun.senses:
            assert f'  sense: {sense.text}' in lines
    wave = lines.index(f'wave [keel] axis: {_noun(vocabulary, "wave").axis}')
    assert lines[wave + 1] == '  sense: the batch a task ships with'
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
        'source': keel.__version__,
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
    assert f'  project: {project} ({SCHEMA})' in result.output.splitlines()
    assert 'berth [project] axis: place' in result.output.splitlines()
    assert 'a mooring' in result.output
    assert 'where a vessel ties up' in result.output
    assert not re.search(r'^voyage ', result.output, re.MULTILINE)


def test_not_bound_prints_its_reason_and_exits_zero(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    project = _project_file(repo, PROJECT_NOT_BOUND)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert 'not bound — the crew names its own work' in lines
    assert f'  project: {project} ({SCHEMA})' in lines
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


def test_text_first_line_is_the_resolved_path(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == f'path: {repo.resolve()}'


def test_text_not_bound_first_line_is_the_resolved_path(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _project_file(repo, PROJECT_NOT_BOUND)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == f'path: {repo.resolve()}'


def test_text_prints_each_sense_with_its_glossary_phrase(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _repo(tmp_path)
    vocabulary = resolve(repo)

    lines = runner.invoke(app, ['vocabulary', str(repo)]).output.splitlines()

    for noun in vocabulary.nouns:
        if not noun.senses:
            continue
        start = lines.index(f'{noun.name} [{noun.layer}] axis: {noun.axis}')
        body = lines[start + 1 : start + 1 + 2 * len(noun.senses)]
        expected = []
        for sense in noun.senses:
            expected += [f'  sense: {sense.text}', f'    glossary: {sense.glossary}']
        assert body == expected
    wave = lines.index(f'wave [keel] axis: {_noun(vocabulary, "wave").axis}')
    assert lines[wave + 4] == '    glossary: more often, a whole series'


def test_text_indents_a_multi_line_rule(tmp_path: Path, monkeypatch) -> None:
    body = USER_VOYAGE.replace(
        'rule = "Say voyage for the whole crossing."',
        'rule = """Say voyage for the whole crossing.\nAsk the purser when unsure.\nKeep a log."""',
    )
    _user_file(tmp_path, monkeypatch, body)
    repo = _repo(tmp_path)

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    start = lines.index('rule: Say voyage for the whole crossing.')
    assert lines[start + 1 : start + 4] == [
        '  Ask the purser when unsure.',
        '  Keep a log.',
        'retired:',
    ]


@pytest.mark.parametrize('flags', [[], ['--json'], ['--write'], ['--check']])
def test_missing_path_exits_two(tmp_path: Path, flags: list[str]) -> None:
    missing = tmp_path / 'missing'
    args = ['vocabulary', str(missing), *flags]

    result = runner.invoke(app, args)

    assert result.exit_code == 2, result.output
    assert f'{missing}: not a directory' in result.output.splitlines()
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert not (tmp_path / 'AGENTS.md').exists()


def test_file_path_exits_two(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    file = repo / 'AGENTS.md'

    result = runner.invoke(app, ['vocabulary', str(file)])

    assert result.exit_code == 2, result.output
    assert f'{file}: not a directory' in result.output.splitlines()
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


def test_undecodable_instruction_file_exits_two_and_names_it(tmp_path: Path) -> None:
    repo = _repo(tmp_path, block=False)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Agents\n\xff\xfe\xfa not utf-8\n')

    result = runner.invoke(app, ['vocabulary', str(repo)])

    assert result.exit_code == 2, result.output
    assert str(claude) in result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)


def _reference_row() -> str:
    rows = [
        line
        for line in CLI_REFERENCE.read_text(encoding='utf-8').splitlines()
        if line.startswith('| `keel vocabulary ')
    ]
    assert len(rows) == 1, rows
    return rows[0]


def test_reference_row_names_the_json_flag() -> None:
    assert '--json' in _reference_row()


def test_reference_row_states_the_exit_codes() -> None:
    cells = [cell.strip() for cell in _reference_row().strip('|').split(' | ')]
    assert cells[2] == (
        'Print and `--json`: 0 resolved, a not-bound project included; 2 a malformed vocabulary '
        'file, an unreadable instruction file, or a PATH that is not a directory. `--write`: 0 '
        'written or unchanged; 2 refused, changing nothing (a generated file, a malformed block, '
        'a file that cannot be written, an unreadable or undecodable instruction file, a `--file` '
        'whose folder does not exist, a not-bound project, a malformed vocabulary file, a PATH '
        'that is not a directory). `--check`: 0 every file current, a not-bound project '
        'included; 1 a file absent, without a block, with a stale one, or with a malformed one '
        '(two begin markers, a begin marker without an end, or a digest that is not 12 lowercase '
        'hex digits); 2 a malformed vocabulary file, an unreadable or undecodable instruction '
        'file, a `--file` whose folder does not exist, or a PATH that is not a directory. Usage '
        'errors, each 2: `--write` with `--check`, `--json` with either, `--file` without either'
    )


# --- the instruction-file block: --write, --check, --file ---------------------------------------

PROJECT_FLEET = f"""\
schema = "{SCHEMA}"
rule = "Say voyage for the whole crossing.\\nSay leg between two ports."

[[nouns]]
name = "voyage"
axis = "scope"
definition = "every leg between two ports"

[[nouns]]
name = "leg"
axis = "scope"

[[nouns]]
name = "berth"
axis = "place"
reading = "a mooring"

[[allowed]]
term = "tally"
note = "a count, not a unit of work"
"""

_BEGIN = re.compile(r'<!-- keel:vocabulary begin digest=([0-9a-f]{12}) -->')


def _bare_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(path)], check=True, capture_output=True)
    return path


def _digest12(path: Path) -> str:
    digest = resolve(path, assume_scope=True).digest
    assert digest is not None
    return digest[:DIGEST_CHARS]


def _begins(path: Path) -> list[str]:
    return _BEGIN.findall(path.read_bytes().decode('utf-8'))


def test_write_creates_agents_md_with_one_block_and_says_so(tmp_path: Path, monkeypatch) -> None:
    _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _bare_repo(tmp_path / 'repo')
    agents = repo / 'AGENTS.md'

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    assert 'created' in result.output
    assert str(agents) in result.output
    # scope is assumed: the user-level noun is in the block although no block existed before
    vocabulary = resolve(repo, assume_scope=True)
    assert vocabulary.digest is not None
    assert _begins(agents) == [vocabulary.digest[:DIGEST_CHARS]]
    text = agents.read_bytes().decode('utf-8')
    names = ', '.join(noun.name for noun in vocabulary.nouns)
    assert f'Work-unit nouns: {names}.' in text
    assert 'Say voyage for the whole crossing.' in text
    assert '`keel vocabulary`' in text
    assert text.endswith(BLOCK_END + '\n')
    assert '\r' not in text
    # nothing but the names, the rule and the pointer
    for absent in ('a crossing', 'every leg between two ports', 'tally', 'sprint-x', 'axis'):
        assert absent not in text
    assert not (repo / 'CLAUDE.md').exists()


def test_write_renders_exactly_the_names_the_rule_and_the_pointer(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    assert (repo / 'AGENTS.md').read_bytes().decode('utf-8') == (
        f'<!-- keel:vocabulary begin digest={_digest12(repo)} -->\n'
        'Work-unit nouns: voyage, leg, berth.\n'
        'Say voyage for the whole crossing.\n'
        'Say leg between two ports.\n'
        'Senses, allowed terms and sources: run `keel vocabulary`.\n'
        '<!-- keel:vocabulary end -->\n'
    )


def test_write_from_a_nested_repository_writes_the_inner_agents_md(
    tmp_path: Path, monkeypatch
) -> None:
    outer = _bare_repo(tmp_path / 'outer')
    (outer / 'AGENTS.md').write_bytes(b'# Outer\n')
    inner = _bare_repo(outer / 'inner')
    _project_file(inner, PROJECT_FLEET)
    monkeypatch.chdir(inner)

    result = runner.invoke(app, ['vocabulary', '--write'])

    assert result.exit_code == 0, result.output
    assert _begins(inner / 'AGENTS.md') == [_digest12(inner)]
    assert (outer / 'AGENTS.md').read_bytes() == b'# Outer\n'


def test_write_from_a_subfolder_writes_the_top_level(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    sub = repo / 'deck' / 'hold'
    sub.mkdir(parents=True)
    _project_file(repo, PROJECT_FLEET)

    result = runner.invoke(app, ['vocabulary', str(sub), '--write'])

    assert result.exit_code == 0, result.output
    assert _begins(repo / 'AGENTS.md') == [_digest12(repo)]
    assert not (sub / 'AGENTS.md').exists()


def test_write_outside_git_writes_path_not_the_current_directory(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / 'loose'
    target.mkdir()
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = runner.invoke(app, ['vocabulary', str(target), '--write'])

    assert result.exit_code == 0, result.output
    assert len(_begins(target / 'AGENTS.md')) == 1
    assert not (elsewhere / 'AGENTS.md').exists()


def test_second_write_after_a_change_replaces_the_block_and_leaves_one(
    tmp_path: Path, monkeypatch
) -> None:
    user = _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _bare_repo(tmp_path / 'repo')
    agents = repo / 'AGENTS.md'
    agents.write_bytes(b'# Agents\n\nKeep the log.\n')
    assert runner.invoke(app, ['vocabulary', str(repo), '--write']).exit_code == 0
    first = _begins(agents)
    agents.write_bytes(agents.read_bytes() + b'\n## Tail\n\nStow the lines.')
    head, _, rest = agents.read_bytes().partition(b'<!-- keel:vocabulary begin')
    tail = rest.partition(b'<!-- keel:vocabulary end -->\n')[2]
    user.write_text(USER_VOYAGE.replace('whole crossing', 'entire crossing'), encoding='utf-8')

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    assert 'replaced' in result.output
    second = _begins(agents)
    assert len(second) == 1
    assert second != first
    assert second == [_digest12(repo)]
    raw = agents.read_bytes()
    assert raw.startswith(head)
    assert raw.endswith(tail)
    assert tail == b'\n## Tail\n\nStow the lines.'
    assert b'entire crossing' in raw
    assert b'whole crossing' not in raw


def test_write_appends_after_a_blank_line_keeping_the_bytes(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    original = b'# Agents\n\nKeep the log.'
    agents.write_bytes(original)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    raw = agents.read_bytes()
    assert raw.startswith(original + b'\n\n<!-- keel:vocabulary begin')
    assert str(agents) in result.output


def test_unchanged_block_is_left_alone(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    assert runner.invoke(app, ['vocabulary', str(repo), '--write']).exit_code == 0
    before = (repo / 'AGENTS.md').read_bytes()

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    assert 'unchanged' in result.output
    assert (repo / 'AGENTS.md').read_bytes() == before


def test_claude_md_is_written_when_present(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    assert _begins(claude) == [_digest12(repo)]
    assert claude.read_bytes().startswith(b'# Claude\n\n<!-- keel:vocabulary begin')
    assert _begins(repo / 'AGENTS.md') == [_digest12(repo)]
    assert str(claude) in result.output


def test_claude_md_is_not_created_when_absent(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 0, result.output
    assert not (repo / 'CLAUDE.md').exists()
    assert (repo / 'AGENTS.md').is_file()


@pytest.mark.parametrize(
    'banner',
    [
        b'<!-- GENERATED by tally-gen from deck.toml -->\n',
        b'# Agents\n\n<!-- Do Not Hand-Edit: tally-gen writes this file -->\n',
    ],
)
def test_generated_file_is_refused_with_its_bytes_unchanged(tmp_path: Path, banner: bytes) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    original = banner + b'\nKeep the log.\n'
    agents.write_bytes(original)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 2, result.output
    assert agents.read_bytes() == original
    assert str(agents) in result.output
    assert "put the block in that file's generator" in result.output
    assert 'Traceback' not in result.output


def test_a_refusal_writes_no_file_at_all(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'<!-- GENERATED -->\n')

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 2, result.output
    assert not (repo / 'AGENTS.md').exists()
    assert claude.read_bytes() == b'<!-- GENERATED -->\n'


def test_not_bound_project_is_refused_with_its_reason(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_NOT_BOUND)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 2, result.output
    assert 'the crew names its own work' in result.output
    assert not (repo / 'AGENTS.md').exists()
    assert claude.read_bytes() == b'# Claude\n'


def test_check_on_a_not_bound_project_has_nothing_to_judge(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_NOT_BOUND)

    result = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert result.exit_code == 0, result.output
    assert 'not bound — the crew names its own work' in result.output


@pytest.mark.parametrize(
    'body',
    [
        BLOCK + '\n' + BLOCK,
        BLOCK_BEGIN.format(digest='0123456789ab') + '\n- voyage\n',
    ],
    ids=['two-begins', 'no-end'],
)
def test_a_malformed_block_is_refused_naming_the_file(tmp_path: Path, body: str) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    agents.write_bytes(body.encode('utf-8'))

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 2, result.output
    assert str(agents) in result.output
    assert agents.read_bytes() == body.encode('utf-8')


def test_malformed_vocabulary_file_refuses_the_write(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    project = _project_file(repo, 'this is = = not toml\n')

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 2, result.output
    assert str(project) in result.output
    assert not (repo / 'AGENTS.md').exists()


def test_check_exits_zero_on_a_current_block(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    (repo / 'CLAUDE.md').write_bytes(b'# Claude\n')
    assert runner.invoke(app, ['vocabulary', str(repo), '--write']).exit_code == 0

    result = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert result.exit_code == 0, result.output
    assert 'current' in result.output
    assert _digest12(repo) in result.output


def test_check_exits_one_on_a_stale_block_printing_both_digests(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    project = _project_file(repo, PROJECT_FLEET)
    assert runner.invoke(app, ['vocabulary', str(repo), '--write']).exit_code == 0
    old = _digest12(repo)
    project.write_text(PROJECT_FLEET.replace('name = "leg"', 'name = "jetty"'), encoding='utf-8')
    new = _digest12(repo)
    assert new != old

    result = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert result.exit_code == 1, result.output
    assert old in result.output
    assert new in result.output
    assert str(repo / 'AGENTS.md') in result.output


def test_check_exits_one_after_a_rule_only_edit(tmp_path: Path, monkeypatch) -> None:
    user = _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _bare_repo(tmp_path / 'repo')
    assert runner.invoke(app, ['vocabulary', str(repo), '--write']).exit_code == 0
    assert runner.invoke(app, ['vocabulary', str(repo), '--check']).exit_code == 0
    user.write_text(USER_VOYAGE.replace('whole crossing', 'entire crossing'), encoding='utf-8')

    result = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert result.exit_code == 1, result.output


def test_check_exits_one_when_a_file_or_its_block_is_missing(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)

    absent = runner.invoke(app, ['vocabulary', str(repo), '--check'])
    (repo / 'AGENTS.md').write_bytes(b'# Agents\n')
    blockless = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert absent.exit_code == 1, absent.output
    assert blockless.exit_code == 1, blockless.output
    assert str(repo / 'AGENTS.md') in blockless.output
    assert (repo / 'AGENTS.md').read_bytes() == b'# Agents\n'


def test_check_exits_two_on_a_malformed_vocabulary_file(tmp_path: Path, monkeypatch) -> None:
    user = _user_file(tmp_path, monkeypatch, 'schema = "work-vocabulary/v1"\nnouns = 3\n')
    repo = _bare_repo(tmp_path / 'repo')
    (repo / 'AGENTS.md').write_bytes(BLOCK.encode('utf-8'))

    result = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert result.exit_code == 2, result.output
    assert str(user) in result.output


def test_write_and_check_together_is_a_usage_error(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')

    result = runner.invoke(app, ['vocabulary', str(repo), '--write', '--check'])

    assert result.exit_code == 2, result.output
    assert not (repo / 'AGENTS.md').exists()


def test_crlf_line_endings_are_kept(tmp_path: Path, monkeypatch) -> None:
    user = _user_file(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _bare_repo(tmp_path / 'repo')
    agents = repo / 'AGENTS.md'
    original = b'# Agents\r\n\r\nKeep the log.\r\n'
    agents.write_bytes(original)

    first = runner.invoke(app, ['vocabulary', str(repo), '--write'])
    user.write_text(USER_VOYAGE.replace('whole crossing', 'entire crossing'), encoding='utf-8')
    second = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    raw = agents.read_bytes()
    assert raw.startswith(original + b'\r\n<!-- keel:vocabulary begin')
    assert raw.count(b'\n') == raw.count(b'\r\n')
    assert raw.endswith(b'<!-- keel:vocabulary end -->\r\n')
    assert b'entire crossing' in raw
    assert len(_begins(agents)) == 1


def test_file_names_the_files_instead(tmp_path: Path, monkeypatch) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    (repo / 'CLAUDE.md').write_bytes(b'# Claude\n')
    notes = repo / 'docs' / 'crew.md'
    notes.parent.mkdir()
    notes.write_bytes(b'# Crew\n')
    monkeypatch.chdir(repo)

    result = runner.invoke(
        app, ['vocabulary', str(repo), '--write', '--file', 'docs/crew.md', '--file', 'HELM.md']
    )

    assert result.exit_code == 0, result.output
    assert _begins(notes) == [_digest12(repo)]
    assert _begins(repo / 'HELM.md') == [_digest12(repo)]
    assert not (repo / 'AGENTS.md').exists()
    assert (repo / 'CLAUDE.md').read_bytes() == b'# Claude\n'

    checked = runner.invoke(app, ['vocabulary', str(repo), '--check', '--file', 'docs/crew.md'])
    assert checked.exit_code == 0, checked.output


_REPAIR = 'leave exactly one begin and one end marker'
_WRITE_HINT = 'run `keel vocabulary --write`'


@pytest.mark.skipif(
    hasattr(os, 'geteuid') and os.geteuid() == 0, reason='root can write a read-only file'
)
def test_an_unwritable_file_is_refused_before_anything_is_written(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')
    os.chmod(claude, stat.S_IREAD)
    try:
        result = runner.invoke(app, ['vocabulary', str(repo), '--write'])
    finally:
        os.chmod(claude, stat.S_IREAD | stat.S_IWRITE)

    assert result.exit_code == 2, result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert str(claude) in result.output
    assert not (repo / 'AGENTS.md').exists()
    assert claude.read_bytes() == b'# Claude\n'


def test_a_failing_write_exits_two_and_undoes_the_earlier_ones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')
    real_write = Path.write_bytes

    def failing_write(self: Path, data: bytes) -> int:
        if self.name == 'CLAUDE.md':
            raise PermissionError(13, 'Permission denied', str(self))
        return real_write(self, data)

    monkeypatch.setattr(Path, 'write_bytes', failing_write)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert result.exit_code == 2, result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert str(claude) in result.output
    assert 'Why:' in result.output
    assert 'could not restore' not in result.output
    assert 'nothing written.' in result.output
    assert not (repo / 'AGENTS.md').exists()
    assert claude.read_bytes() == b'# Claude\n'


def test_a_write_that_fails_midway_puts_back_its_own_file_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')
    real_write = Path.write_bytes
    failed: list[Path] = []

    def failing_write(self: Path, data: bytes) -> int:
        if self.name == 'CLAUDE.md' and not failed:
            failed.append(self)
            real_write(self, b'')
            raise OSError(28, 'No space left on device', str(self))
        return real_write(self, data)

    monkeypatch.setattr(Path, 'write_bytes', failing_write)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert failed == [claude]
    assert result.exit_code == 2, result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert 'could not restore' not in result.output
    assert not (repo / 'AGENTS.md').exists()
    assert claude.read_bytes() == b'# Claude\n'


def test_a_restore_that_fails_is_reported_with_the_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')
    real_write = Path.write_bytes
    failed: list[Path] = []

    def failing_write(self: Path, data: bytes) -> int:
        if self.name == 'CLAUDE.md':
            if not failed:
                failed.append(self)
                real_write(self, b'')
            raise OSError(28, 'No space left on device', str(self))
        return real_write(self, data)

    monkeypatch.setattr(Path, 'write_bytes', failing_write)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert failed == [claude]
    assert result.exit_code == 2, result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert any(
        line.startswith('could not restore:') and str(claude) in line
        for line in result.output.splitlines()
    )
    assert 'nothing written.' not in result.output
    assert not (repo / 'AGENTS.md').exists()


def test_a_file_that_cannot_be_read_back_is_restored_anyway(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    claude = repo / 'CLAUDE.md'
    claude.write_bytes(b'# Claude\n')
    real_write = Path.write_bytes
    real_read = Path.read_bytes
    writes: list[bytes] = []
    failed: list[Path] = []

    def failing_write(self: Path, data: bytes) -> int:
        if self.name == 'CLAUDE.md':
            writes.append(data)
            if not failed:
                failed.append(self)
                raise PermissionError(13, 'Permission denied', str(self))
        return real_write(self, data)

    def failing_read(self: Path) -> bytes:
        if self.name == 'CLAUDE.md' and failed:
            raise OSError(5, 'Input/output error', str(self))
        return real_read(self)

    monkeypatch.setattr(Path, 'write_bytes', failing_write)
    monkeypatch.setattr(Path, 'read_bytes', failing_read)

    result = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert failed == [claude]
    assert len(writes) == 2
    assert writes[1] == b'# Claude\n'
    assert result.exit_code == 2, result.output
    assert 'Traceback' not in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert 'could not restore' not in result.output
    assert 'nothing written.' in result.output
    assert not (repo / 'AGENTS.md').exists()
    assert real_read(claude) == b'# Claude\n'


def test_a_rule_naming_the_banner_words_does_not_block_the_next_write(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(
        repo,
        PROJECT_FLEET.replace(
            'Say leg between two ports.',
            'GENERATED tallies are not legs.\\nDo not hand-edit the log.',
        ),
    )
    agents = repo / 'AGENTS.md'

    first = runner.invoke(app, ['vocabulary', str(repo), '--write'])
    second = runner.invoke(app, ['vocabulary', str(repo), '--write'])

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    text = agents.read_bytes().decode('utf-8')
    assert any('GENERATED tallies' in line for line in text.split('\n')[:5])
    assert _begins(agents) == [_digest12(repo)]


def test_the_rendered_begin_line_is_the_resolver_marker(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    vocabulary = resolve(repo, assume_scope=True)
    assert vocabulary.digest is not None

    first = render_block(vocabulary).split('\n')[0]

    assert first == block_marker(vocabulary.digest)
    assert BLOCK_RE.match(first)


@pytest.mark.parametrize('digest', ['0123456789AB', 'abc', '', '0123456789abc'])
def test_a_begin_line_with_a_bad_digest_is_a_malformed_block(tmp_path: Path, digest: str) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    body = BLOCK_BEGIN.format(digest=digest) + '\n- voyage\n' + BLOCK_END + '\n'
    agents.write_bytes(body.encode('utf-8'))

    written = runner.invoke(app, ['vocabulary', str(repo), '--write'])
    checked = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert written.exit_code == 2, written.output
    assert str(agents) in written.output
    assert agents.read_bytes() == body.encode('utf-8')
    assert checked.exit_code == 1, checked.output
    assert _REPAIR in checked.output
    assert _WRITE_HINT not in checked.output
    assert 'stale' not in checked.output


@pytest.mark.parametrize(
    'body',
    [
        BLOCK + '\n' + BLOCK,
        BLOCK_BEGIN.format(digest='0123456789ab') + '\n- voyage\n',
    ],
    ids=['two-begins', 'no-end'],
)
def test_check_prints_the_repair_for_a_malformed_block(tmp_path: Path, body: str) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    agents.write_bytes(body.encode('utf-8'))

    result = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert result.exit_code == 1, result.output
    assert str(agents) in result.output
    assert _REPAIR in result.output
    assert _WRITE_HINT not in result.output
    assert agents.read_bytes() == body.encode('utf-8')


@pytest.mark.parametrize('mode', ['--write', '--check'])
def test_a_file_in_a_missing_folder_exits_two(tmp_path: Path, mode: str) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    missing = repo / 'nowhere' / 'HELM.md'

    result = runner.invoke(app, ['vocabulary', str(repo), mode, '--file', str(missing)])

    assert result.exit_code == 2, result.output
    assert str(missing) in result.output
    assert 'Traceback' not in result.output
    assert not missing.parent.exists()


@pytest.mark.parametrize('mode', ['--write', '--check'])
def test_an_undecodable_file_exits_two(tmp_path: Path, mode: str) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    agents.write_bytes(b'# Agents\n\xff\xfe not utf-8\n')

    result = runner.invoke(app, ['vocabulary', str(repo), mode])

    assert result.exit_code == 2, result.output
    assert str(agents) in result.output
    assert 'Traceback' not in result.output
    assert agents.read_bytes() == b'# Agents\n\xff\xfe not utf-8\n'


@pytest.mark.parametrize(
    'flags',
    [['--write', '--check'], ['--json', '--write'], ['--json', '--check'], ['--file', 'HELM.md']],
)
def test_usage_errors_exit_two_and_write_nothing(tmp_path: Path, flags: list[str]) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)

    result = runner.invoke(app, ['vocabulary', str(repo), *flags])

    assert result.exit_code == 2, result.output
    assert not (repo / 'AGENTS.md').exists()
    assert not (repo / 'HELM.md').exists()
    assert not (tmp_path / 'HELM.md').exists()


def test_a_bom_file_keeps_its_bom_and_every_byte_outside_the_block(tmp_path: Path) -> None:
    repo = _bare_repo(tmp_path / 'repo')
    _project_file(repo, PROJECT_FLEET)
    agents = repo / 'AGENTS.md'
    tail = b'\n# Crew\n\nKeep the log.\n'
    agents.write_bytes(b'\xef\xbb\xbf' + BLOCK.encode('utf-8') + tail)

    written = runner.invoke(app, ['vocabulary', str(repo), '--write'])
    checked = runner.invoke(app, ['vocabulary', str(repo), '--check'])

    assert written.exit_code == 0, written.output
    assert checked.exit_code == 0, checked.output
    raw = agents.read_bytes()
    assert raw.startswith(b'\xef\xbb\xbf' + block_marker(_digest12(repo)).encode('utf-8'))
    assert raw.count(b'\xef\xbb\xbf') == 1
    assert raw.endswith(BLOCK_END.encode('utf-8') + b'\n' + tail)
    assert _begins(agents) == [_digest12(repo)]


def test_reference_row_names_write_check_and_file() -> None:
    row = _reference_row()

    for word in ('--write', '--check', '--file', '--json', 'AGENTS.md', 'keel init'):
        assert word in row
    assert 'on this machine' in row
    assert 'stub' not in row.lower()
