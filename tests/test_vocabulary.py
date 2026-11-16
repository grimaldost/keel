"""The vocabulary resolver: keel's own nouns, a user-level file, a project file, scope and digest.

Every fixture is bounded: a git repository made with `git init`, or a plain folder holding an
instruction file at its root, so no scope walk ever leaves `tmp_path`. The nouns are invented.
"""

import re
import subprocess
from pathlib import Path

import pytest

from keel import __version__
from keel.vocabulary import (
    BLOCK_BEGIN,
    BLOCK_END,
    DEFAULT_RULE,
    INSTRUCTION_FILES,
    SCHEMA,
    TOOL_ALLOWED,
    TOOL_NOUNS,
    Layer,
    VocabularyError,
    compute_digest,
    git_toplevel,
    in_scope,
    resolve,
    user_file,
)

ROOT = Path(__file__).resolve().parent.parent
TOOL_NAMES = ['program', 'series', 'task', 'wave', 'phase', 'round']
BLOCK = BLOCK_BEGIN.format(digest='0123456789ab') + '\n- voyage\n' + BLOCK_END + '\n'


@pytest.fixture(autouse=True)
def _no_git_above(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stop git's discovery at the fixture, so a folder outside git stays outside git."""
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.resolve().parent))


def _git_init(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(path)], check=True, capture_output=True)
    return path


def _user_vocabulary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str) -> Path:
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

[[patterns]]
id = "voyage-word"
regex = "\\\\bvoyages?\\\\b"
word = "voyage"
ignore_case = true
dialect = "python-re"
"""


def _names(vocabulary) -> list[str]:
    return [noun.name for noun in vocabulary.nouns]


# The tool layer


def test_tool_layer_alone(tmp_path: Path) -> None:
    folder = tmp_path / 'plain'
    folder.mkdir()
    (folder / 'AGENTS.md').write_text('# Agents\n', encoding='utf-8')

    vocabulary = resolve(folder)

    assert _names(vocabulary) == TOOL_NAMES
    assert all(noun.layer == 'keel' for noun in vocabulary.nouns)
    assert [a.term for a in vocabulary.allowed] == ['pass']
    assert vocabulary.rule == DEFAULT_RULE
    assert vocabulary.layers == (Layer('keel', __version__),)
    assert vocabulary.in_scope is False
    assert vocabulary.not_bound is None
    assert vocabulary.digest == compute_digest(TOOL_NAMES, DEFAULT_RULE)


def test_tool_nouns_carry_their_senses() -> None:
    counts = {noun.name: len(noun.senses) for noun in TOOL_NOUNS}
    assert counts == {'program': 1, 'series': 1, 'task': 1, 'wave': 2, 'phase': 2, 'round': 3}
    assert [a.term for a in TOOL_ALLOWED] == ['pass']
    assert 'review' in TOOL_ALLOWED[0].note
    assert '\n' not in DEFAULT_RULE


def test_tool_layer_found_in_glossary() -> None:
    glossary = (ROOT / 'docs' / 'glossary.md').read_text(encoding='utf-8')
    collapsed = ' '.join(glossary.split())
    for noun in TOOL_NOUNS:
        assert re.search(rf'\b{noun.name}\b', glossary), noun.name
        for sense in noun.senses:
            assert ' '.join(sense.glossary.split()) in collapsed, sense.glossary
    assert re.search(r'\bpass\b', glossary)


# The user-level file and scope


def test_user_file_adds_a_noun_inside_scope(tmp_path: Path, monkeypatch) -> None:
    path = _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _git_init(tmp_path / 'repo')
    (repo / 'AGENTS.md').write_text(BLOCK, encoding='utf-8')

    vocabulary = resolve(repo)

    assert vocabulary.in_scope is True
    assert _names(vocabulary) == [*TOOL_NAMES, 'voyage']
    assert vocabulary.nouns[-1].layer == 'user'
    assert vocabulary.nouns[-1].definition == 'every leg between two ports'
    assert [a.term for a in vocabulary.allowed] == ['pass', 'tally']
    assert vocabulary.allowed[-1].layer == 'user'
    assert [(r.noun, r.instead) for r in vocabulary.retired] == [('sprint-x', 'voyage')]
    assert vocabulary.rule == 'Say voyage for the whole crossing.'
    assert vocabulary.layers == (Layer('keel', __version__), Layer('user', str(path), SCHEMA))
    assert vocabulary.digest == compute_digest(_names(vocabulary), vocabulary.rule)


def test_user_file_ignored_outside_scope(tmp_path: Path, monkeypatch) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _git_init(tmp_path / 'repo')
    (repo / 'AGENTS.md').write_text('# Agents\n', encoding='utf-8')

    vocabulary = resolve(repo)

    assert vocabulary.in_scope is False
    assert _names(vocabulary) == TOOL_NAMES
    assert vocabulary.rule == DEFAULT_RULE
    assert vocabulary.layers == (Layer('keel', __version__),)


def test_assume_scope_reads_the_user_file(tmp_path: Path, monkeypatch) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _git_init(tmp_path / 'repo')

    vocabulary = resolve(repo, assume_scope=True)

    assert vocabulary.in_scope is True
    assert _names(vocabulary) == [*TOOL_NAMES, 'voyage']


def test_series_folder_outside_git_in_scope_through_its_root_file(
    tmp_path: Path, monkeypatch
) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    series = tmp_path / 'voyage-folder'
    leg = series / 'leg-1'
    leg.mkdir(parents=True)
    (series / 'CLAUDE.md').write_text(BLOCK, encoding='utf-8')

    assert git_toplevel(leg) is None
    assert in_scope(leg) is True
    assert _names(resolve(leg)) == [*TOOL_NAMES, 'voyage']


def test_outside_git_the_folders_own_file_decides(tmp_path: Path, monkeypatch) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    series = tmp_path / 'voyage-folder'
    berth = series / 'berth'
    berth.mkdir(parents=True)
    (series / 'AGENTS.md').write_text(BLOCK, encoding='utf-8')
    (berth / 'AGENTS.md').write_text('# Berth\n', encoding='utf-8')

    assert in_scope(series) is True
    assert in_scope(berth) is False
    assert _names(resolve(berth)) == TOOL_NAMES


def test_nested_file_without_block_stays_in_scope_inside_git(tmp_path: Path, monkeypatch) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _git_init(tmp_path / 'repo')
    berth = repo / 'berth'
    leg = berth / 'leg'
    leg.mkdir(parents=True)
    (repo / 'AGENTS.md').write_text(BLOCK, encoding='utf-8')
    (berth / 'CLAUDE.md').write_text('# Berth\n', encoding='utf-8')

    assert git_toplevel(leg) == repo.resolve()
    assert in_scope(leg) is True
    assert _names(resolve(leg)) == [*TOOL_NAMES, 'voyage']


def test_block_with_crlf_line_endings_counts(tmp_path: Path) -> None:
    folder = tmp_path / 'plain'
    folder.mkdir()
    (folder / 'AGENTS.md').write_bytes(BLOCK.replace('\n', '\r\n').encode('utf-8'))
    assert in_scope(folder) is True


def test_unreadable_instruction_file_names_it(tmp_path: Path) -> None:
    folder = tmp_path / 'plain'
    folder.mkdir()
    (folder / 'AGENTS.md').write_bytes(b'\xff\xfe\xfa not utf-8')
    with pytest.raises(VocabularyError, match=re.escape('AGENTS.md')):
        in_scope(folder)


# The project file


def test_project_list_replaces_both_layers_with_default_rule(tmp_path: Path, monkeypatch) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _git_init(tmp_path / 'repo')
    (repo / 'AGENTS.md').write_text(BLOCK, encoding='utf-8')
    path = _project_vocabulary(
        repo,
        f'schema = "{SCHEMA}"\n\n'
        '[[nouns]]\nname = "leg"\naxis = "scope"\n\n'
        '[[nouns]]\nname = "berth"\naxis = "batch"\n\n'
        '[[allowed]]\nterm = "tally"\nnote = "a count"\n',
    )

    vocabulary = resolve(repo)

    assert _names(vocabulary) == ['leg', 'berth']
    assert all(noun.layer == 'project' for noun in vocabulary.nouns)
    assert [(a.term, a.layer) for a in vocabulary.allowed] == [('tally', 'project')]
    assert vocabulary.rule == DEFAULT_RULE
    assert vocabulary.layers == (Layer('project', str(path), SCHEMA),)
    assert vocabulary.digest == compute_digest(['leg', 'berth'], DEFAULT_RULE)


def test_project_list_keeps_its_own_rule(tmp_path: Path) -> None:
    repo = _git_init(tmp_path / 'repo')
    _project_vocabulary(
        repo,
        f'schema = "{SCHEMA}"\nrule = "Ask the bosun."\n\n'
        '[[nouns]]\nname = "leg"\naxis = "scope"\n',
    )
    assert resolve(repo).rule == 'Ask the bosun.'


def test_project_not_bound_with_its_reason(tmp_path: Path, monkeypatch) -> None:
    _user_vocabulary(tmp_path, monkeypatch, USER_VOYAGE)
    repo = _git_init(tmp_path / 'repo')
    path = _project_vocabulary(
        repo, f'schema = "{SCHEMA}"\nstatus = "not bound"\nreason = "the tally is still open"\n'
    )

    vocabulary = resolve(repo, assume_scope=True)

    assert vocabulary.not_bound == 'the tally is still open'
    assert vocabulary.nouns == ()
    assert vocabulary.allowed == ()
    assert vocabulary.rule == ''
    assert vocabulary.digest is None
    assert vocabulary.notes == ()
    assert vocabulary.layers == (Layer('project', str(path), SCHEMA),)


@pytest.mark.parametrize(
    ('body', 'defect'),
    [
        ('status = "not bound"\nreason = ""\n', 'reason'),
        ('status = "bound"\nreason = "x"\n', 'status'),
        (
            'status = "not bound"\nreason = "x"\n\n[[nouns]]\nname = "leg"\naxis = "scope"\n',
            'nouns',
        ),
        ('rule = "only a rule"\n', 'nouns'),
    ],
)
def test_project_file_shape_errors(tmp_path: Path, body: str, defect: str) -> None:
    repo = _git_init(tmp_path / 'repo')
    _project_vocabulary(repo, f'schema = "{SCHEMA}"\n{body}')
    with pytest.raises(VocabularyError, match=defect) as caught:
        resolve(repo)
    assert 'vocabulary.toml' in str(caught.value)


def test_status_is_unknown_in_the_user_file(tmp_path: Path, monkeypatch) -> None:
    path = _user_vocabulary(
        tmp_path, monkeypatch, f'schema = "{SCHEMA}"\nstatus = "not bound"\nreason = "x"\n'
    )
    with pytest.raises(VocabularyError, match='status') as caught:
        resolve(_git_init(tmp_path / 'repo'), assume_scope=True)
    assert str(path) in str(caught.value)


# Failure


def test_missing_user_file_resolves_the_tool_layer_with_a_note(tmp_path: Path, monkeypatch) -> None:
    missing = tmp_path / 'nowhere' / 'vocabulary.toml'
    monkeypatch.setenv('KEEL_VOCABULARY', str(missing))

    vocabulary = resolve(_git_init(tmp_path / 'repo'), assume_scope=True)

    assert _names(vocabulary) == TOOL_NAMES
    assert vocabulary.layers == (Layer('keel', __version__),)
    assert len(vocabulary.notes) == 1
    assert str(missing) in vocabulary.notes[0]


def test_vocabulary_off_adds_no_note(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv('KEEL_VOCABULARY', 'OFF')
    vocabulary = resolve(_git_init(tmp_path / 'repo'), assume_scope=True)
    assert vocabulary.notes == ()
    assert _names(vocabulary) == TOOL_NAMES


@pytest.mark.parametrize(
    ('body', 'defect'),
    [
        ('schema = "work-vocabulary/v1"\n[[nouns]\nname = "leg"\n', ''),
        ('schema = "work-vocabulary/v9"\n', 'work-vocabulary/v9'),
        ('rule = "no schema"\n', 'schema'),
        (f'schema = "{SCHEMA}"\nharbour = "x"\n', 'harbour'),
        (f'schema = "{SCHEMA}"\n[[nouns]]\nname = "leg"\naxis = "scope"\nkeel = "x"\n', 'keel'),
        (f'schema = "{SCHEMA}"\n[[nouns]]\nname = "leg"\n', 'axis'),
        (f'schema = "{SCHEMA}"\n[[allowed]]\nterm = "tally"\n', 'note'),
        (
            f'schema = "{SCHEMA}"\n[[patterns]]\nid = "bad-leg"\nregex = "(leg"\nword = "leg"\n'
            'ignore_case = false\ndialect = "python-re"\n',
            'bad-leg',
        ),
        (
            f'schema = "{SCHEMA}"\n[[patterns]]\nid = "p"\nregex = "leg"\nword = "leg"\n'
            'ignore_case = "yes"\n',
            'ignore_case',
        ),
        (
            f'schema = "{SCHEMA}"\n[[patterns]]\nid = "p"\nregex = "leg"\nword = "leg"\n'
            'dialect = "pcre"\n',
            'dialect',
        ),
    ],
    ids=[
        'unparsable',
        'unknown-schema',
        'missing-schema',
        'unknown-top-key',
        'unknown-table-key',
        'missing-axis',
        'missing-note',
        'regex-does-not-compile',
        'ignore-case-not-bool',
        'unknown-dialect',
    ],
)
def test_defective_user_file_raises_naming_the_file(
    tmp_path: Path, monkeypatch, body: str, defect: str
) -> None:
    path = _user_vocabulary(tmp_path, monkeypatch, body)
    with pytest.raises(VocabularyError) as caught:
        resolve(_git_init(tmp_path / 'repo'), assume_scope=True)
    assert str(path) in str(caught.value)
    assert defect in str(caught.value)


# The digest


def _rendered(tmp_path: Path, monkeypatch, name: str, body: bytes) -> str | None:
    path = tmp_path / name / 'vocabulary.toml'
    path.parent.mkdir(parents=True)
    path.write_bytes(body)
    monkeypatch.setenv('KEEL_VOCABULARY', str(path))
    return resolve(tmp_path, assume_scope=True).digest


TRAILING = '   '
MULTI_LINE_RULE = f'''\
schema = "{SCHEMA}"
rule = """
Say voyage for the whole crossing.{TRAILING}
Ask the bosun when no noun fits.
"""

[[nouns]]
name = "voyage"
axis = "scope"
definition = "every leg between two ports"
'''


def test_same_content_same_digest_from_two_paths_and_crlf(tmp_path: Path, monkeypatch) -> None:
    lf = MULTI_LINE_RULE.encode('utf-8')
    crlf = MULTI_LINE_RULE.replace('\n', '\r\n').encode('utf-8')

    first = _rendered(tmp_path, monkeypatch, 'one', lf)
    second = _rendered(tmp_path, monkeypatch, 'two', lf)
    third = _rendered(tmp_path, monkeypatch, 'three', crlf)

    assert first is not None
    assert first == second == third
    assert re.fullmatch(r'[0-9a-f]{64}', first)


def test_definition_edit_keeps_digest_and_rule_edit_moves_it(tmp_path: Path, monkeypatch) -> None:
    base = _rendered(tmp_path, monkeypatch, 'base', MULTI_LINE_RULE.encode('utf-8'))
    redefined = MULTI_LINE_RULE.replace('every leg between two ports', 'one crossing, end to end')
    reworded = MULTI_LINE_RULE.replace('Ask the bosun', 'Ask the purser')

    assert _rendered(tmp_path, monkeypatch, 'def', redefined.encode('utf-8')) == base
    assert _rendered(tmp_path, monkeypatch, 'rule', reworded.encode('utf-8')) != base


def test_compute_digest_normalizes_the_rule() -> None:
    assert compute_digest(['leg'], 'a  \r\nb\rc') == compute_digest(['leg'], 'a\nb\nc')
    assert compute_digest(['leg', 'berth'], 'r') != compute_digest(['berth', 'leg'], 'r')


# Locating the user-level file


def test_user_file_resolution_order(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv('KEEL_VOCABULARY', '  off ')
    assert user_file() is None
    monkeypatch.setenv('KEEL_VOCABULARY', f' {tmp_path / "v.toml"} ')
    assert user_file() == tmp_path / 'v.toml'
    monkeypatch.setenv('KEEL_VOCABULARY', '')
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg'))
    assert user_file() == tmp_path / 'xdg' / 'keel' / 'vocabulary.toml'
    monkeypatch.setenv('XDG_CONFIG_HOME', '  ')
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: Path('/home/user')))
    assert user_file() == Path('/home/user') / '.config' / 'keel' / 'vocabulary.toml'


def test_instruction_files_and_block_markers() -> None:
    assert INSTRUCTION_FILES == ('AGENTS.md', 'CLAUDE.md')
    assert BLOCK_END == '<!-- keel:vocabulary end -->'
