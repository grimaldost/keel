"""The work-unit vocabulary resolver: keel's nouns, a user-level file and a project file.

Pure functions, no CLI. Three layers resolve in order: keel's own nouns (the tool layer), then a
user-level file whose additions apply only to a directory in scope, and a project file at the git
top level that, when present, replaces both. The digest covers exactly what the instruction-file
block renders (noun names and the rule), so one source yields one digest on every machine.
"""

import hashlib
import json
import os
import re
import subprocess
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from keel import __version__
from keel.errors import format_error

SCHEMA = 'work-vocabulary/v1'
INSTRUCTION_FILES = ('AGENTS.md', 'CLAUDE.md')
BLOCK_BEGIN = '<!-- keel:vocabulary begin digest={digest} -->'
BLOCK_END = '<!-- keel:vocabulary end -->'
DEFAULT_RULE = (
    'When no listed noun fits, use the nearest listed noun with a description and ask whoever '
    "owns the project's vocabulary."
)
# The begin marker carries this many leading hex digits of the digest.
DIGEST_CHARS = 12

_MARKER_HEAD, _MARKER_TAIL = BLOCK_BEGIN.split('{digest}')
# A whole begin-marker line, built from BLOCK_BEGIN so the two cannot drift apart.
BLOCK_RE = re.compile(
    f'^{re.escape(_MARKER_HEAD)}(?P<digest>[0-9a-f]{{{DIGEST_CHARS}}}){re.escape(_MARKER_TAIL)}$'
)
_PROJECT_FILE = Path('.keel') / 'vocabulary.toml'
_NOT_BOUND = 'not bound'
_DIALECT = 'python-re'

_TOP_KEYS = frozenset({'schema', 'rule', 'nouns', 'allowed', 'retired', 'patterns'})
_PROJECT_KEYS = _TOP_KEYS | {'status', 'reason'}
# table -> (required string fields, optional fields)
_TABLES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    'nouns': (('name', 'axis'), ('reading', 'definition')),
    'allowed': (('term', 'note'), ()),
    'retired': (('noun', 'instead'), ()),
    'patterns': (('id', 'regex', 'word'), ('ignore_case', 'dialect')),
}


@dataclass(frozen=True)
class Sense:
    text: str
    glossary: str


@dataclass(frozen=True)
class Noun:
    name: str
    axis: str
    layer: str
    senses: tuple[Sense, ...] = ()
    reading: str = ''
    definition: str = ''


@dataclass(frozen=True)
class Allowed:
    term: str
    note: str
    layer: str


@dataclass(frozen=True)
class Retired:
    noun: str
    instead: str


@dataclass(frozen=True)
class Layer:
    name: str
    source: str
    schema: str = ''


@dataclass(frozen=True)
class Vocabulary:
    layers: tuple[Layer, ...]
    nouns: tuple[Noun, ...]
    allowed: tuple[Allowed, ...]
    rule: str
    retired: tuple[Retired, ...]
    notes: tuple[str, ...]
    not_bound: str | None
    in_scope: bool
    digest: str | None


TOOL_NOUNS: tuple[Noun, ...] = (
    Noun(
        'program',
        'scope',
        'keel',
        (Sense('the scope that spans several series', 'spans several series'),),
    ),
    Noun(
        'series',
        'scope',
        'keel',
        (
            Sense(
                'the governed set of tasks under one spec and one gate set',
                'the governed set of tasks under one spec and one gate set',
            ),
        ),
    ),
    Noun(
        'task',
        'scope',
        'keel',
        (Sense('one briefed, gated unit of work', 'one briefed, gated unit of work'),),
    ),
    Noun(
        'wave',
        'batch',
        'keel',
        (
            Sense('the batch a task ships with', 'the batch a task ships with'),
            Sense('a whole series, the more frequent sense', 'more often, a whole series'),
        ),
    ),
    Noun(
        'phase',
        'stage',
        'keel',
        (
            Sense('one of the eight lifecycle phases', 'one of the eight lifecycle phases'),
            Sense(
                'a larger stretch of work: a series or a stage of a program',
                'a larger stretch of work, a series or a stage of a program',
            ),
        ),
    ),
    Noun(
        'round',
        'repetition',
        'keel',
        (
            Sense('one repetition of a review pass', 'one repetition of a review'),
            Sense(
                'a work round, which runs a named subset of the phases',
                'runs a named subset of the phases',
            ),
            Sense(
                "a whole series, in doctrine §1's three governed waves",
                'doctrine §1 calls each of its three governed waves a round, meaning a whole '
                'series',
            ),
        ),
    ),
)

TOOL_ALLOWED: tuple[Allowed, ...] = (
    Allowed('pass', 'a named kind of review, not a unit of work', 'keel'),
)


class VocabularyError(Exception):
    """A vocabulary or instruction file keel cannot use; the message names the file and defect."""


_VOCABULARY_WHY = 'a defective vocabulary file is never treated as absent'
_INSTRUCTION_WHY = (
    'an instruction file on the scope walk that cannot be read or decoded leaves the scope '
    'undecided, so it is never skipped'
)


def _error(path: Path, defect: str, fix: str, why: str = _VOCABULARY_WHY) -> VocabularyError:
    return VocabularyError(format_error(what=f'{path}: {defect}', why=why, fix=fix))


def _normalize_rule(rule: str) -> str:
    return '\n'.join(
        line.rstrip() for line in rule.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    )


def compute_digest(names: Sequence[str], rule: str) -> str:
    """sha256 over the canonical JSON of the noun names and the normalized rule."""
    payload = json.dumps(
        {'nouns': list(names), 'rule': _normalize_rule(rule)},
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def block_marker(digest: str) -> str:
    """The begin-marker line for a block whose vocabulary has `digest`."""
    return BLOCK_BEGIN.format(digest=digest[:DIGEST_CHARS])


def user_file() -> Path | None:
    """Where the user-level file lives, or None when it is switched off."""
    override = os.environ.get('KEEL_VOCABULARY', '').strip()
    if override.lower() == 'off':
        return None
    if override:
        return Path(override)
    config = os.environ.get('XDG_CONFIG_HOME', '').strip()
    if config:
        return Path(config) / 'keel' / 'vocabulary.toml'
    return Path.home() / '.config' / 'keel' / 'vocabulary.toml'


def git_toplevel(directory: Path) -> Path | None:
    """The git top level git reports for `directory`, or None outside a git repository."""
    try:
        proc = subprocess.run(
            ['git', '-C', str(directory), 'rev-parse', '--show-toplevel'],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return Path(proc.stdout.strip()).resolve()


def _carries_block(path: Path) -> bool:
    try:
        text = path.read_bytes().decode('utf-8-sig')
    except (OSError, UnicodeDecodeError) as exc:
        raise _error(
            path,
            f'the instruction file cannot be read as UTF-8 ({exc})',
            'save it as UTF-8, or make it readable',
            _INSTRUCTION_WHY,
        ) from exc
    return any(BLOCK_RE.match(line.rstrip()) for line in text.split('\n'))


def _instruction_files(directory: Path) -> list[Path]:
    return [directory / name for name in INSTRUCTION_FILES if (directory / name).is_file()]


def in_scope(directory: Path) -> bool:
    """Whether the user-level file's additions apply to `directory`.

    Inside git, every instruction file from the directory up to the top level counts, and any one
    carrying the block puts the directory in scope. Outside git, the first directory (itself
    included) holding an instruction file ends the walk, and its files alone decide.

    Raises VocabularyError naming the file when an instruction file on the walk cannot be read or
    decoded as UTF-8.
    """
    current = directory.resolve()
    top = git_toplevel(directory)
    if top is not None:
        while True:
            if any(_carries_block(path) for path in _instruction_files(current)):
                return True
            if current == top or current.parent == current:
                return False
            current = current.parent
    while True:
        files = _instruction_files(current)
        if files:
            return any(_carries_block(path) for path in files)
        if current.parent == current:
            return False
        current = current.parent


def nearest_block_dir(directory: Path) -> Path | None:
    """The nearest directory on `directory`'s walk whose instruction file carries the block.

    The walk is `in_scope`'s: inside git, from the directory up to the top level; outside git, up
    to and including the first directory holding an instruction file. None when no file on it
    carries the block.
    """
    current = directory.resolve()
    top = git_toplevel(directory)
    while True:
        files = _instruction_files(current)
        if any(_carries_block(path) for path in files):
            return current
        if top is None and files:
            return None
        if current == top or current.parent == current:
            return None
        current = current.parent


def _string(path: Path, where: str, key: str, value: Any) -> str:
    if not isinstance(value, str):
        raise _error(path, f'{where}: `{key}` must be a string', f'write `{key}` as a TOML string')
    return value


def _tables(path: Path, data: dict[str, Any], table: str) -> list[dict[str, Any]]:
    """Validate one array of tables: known keys, required string fields, optional field types."""
    raw = data.get(table, [])
    if not isinstance(raw, list) or not all(isinstance(entry, dict) for entry in raw):
        raise _error(path, f'`{table}` must be an array of tables', f'write it as [[{table}]]')
    required, optional = _TABLES[table]
    for index, entry in enumerate(raw, start=1):
        where = f'[[{table}]] #{index}'
        for key in entry:
            if key not in required and key not in optional:
                raise _error(
                    path,
                    f'{where}: unknown key `{key}`',
                    f'remove `{key}`; [[{table}]] takes {", ".join((*required, *optional))}',
                )
        for key in required:
            if key not in entry:
                raise _error(path, f'{where}: missing `{key}`', f'add `{key}`')
            _string(path, where, key, entry[key])
        for key in optional:
            if key in entry and key not in ('ignore_case',):
                _string(path, where, key, entry[key])
    return raw


def _check_patterns(path: Path, patterns: list[dict[str, Any]]) -> None:
    for entry in patterns:
        ident = entry['id']
        ignore_case = entry.get('ignore_case', False)
        if not isinstance(ignore_case, bool):
            raise _error(
                path,
                f'pattern `{ident}`: `ignore_case` must be a boolean',
                'write ignore_case = true or false',
            )
        dialect = entry.get('dialect', _DIALECT)
        if dialect != _DIALECT:
            raise _error(
                path,
                f'pattern `{ident}`: unknown dialect `{dialect}`',
                f'write dialect = "{_DIALECT}"',
            )
        try:
            re.compile(entry['regex'], re.IGNORECASE if ignore_case else 0)
        except re.error as exc:
            raise _error(
                path,
                f'pattern `{ident}`: the regex does not compile ({exc})',
                'fix the regex so Python `re` compiles it',
            ) from exc


@dataclass(frozen=True)
class _File:
    path: Path
    schema: str
    rule: str | None
    nouns: tuple[Noun, ...]
    allowed: tuple[Allowed, ...]
    retired: tuple[Retired, ...]
    not_bound: str | None


def _load(path: Path, layer: str) -> _File:
    """Read and validate one vocabulary file; raise VocabularyError naming the file and defect."""
    try:
        data = tomllib.loads(path.read_bytes().decode('utf-8-sig'))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise _error(path, f'the file does not parse as TOML ({exc})', 'fix the TOML') from exc
    except OSError as exc:
        raise _error(path, f'the file cannot be read ({exc})', 'make it readable') from exc

    schema = data.get('schema')
    if schema != SCHEMA:
        defect = 'missing `schema`' if schema is None else f'unknown schema `{schema}`'
        raise _error(path, defect, f'write schema = "{SCHEMA}"')

    known = _PROJECT_KEYS if layer == 'project' else _TOP_KEYS
    for key in data:
        if key not in known:
            raise _error(
                path,
                f'unknown key `{key}`',
                f'remove `{key}`; the file takes {", ".join(sorted(known))}',
            )

    rule = data.get('rule')
    if rule is not None:
        rule = _string(path, 'the top level', 'rule', rule)
    nouns = _tables(path, data, 'nouns')
    seen: set[str] = set()
    for entry in nouns:
        if entry['name'] in seen:
            raise _error(
                path,
                f'noun `{entry["name"]}` is declared twice',
                f'keep one [[nouns]] entry named `{entry["name"]}`',
            )
        seen.add(entry['name'])
    allowed = _tables(path, data, 'allowed')
    retired = _tables(path, data, 'retired')
    _check_patterns(path, _tables(path, data, 'patterns'))

    not_bound: str | None = None
    if 'status' in data:
        status = data['status']
        if status != _NOT_BOUND:
            raise _error(path, f'unknown status `{status}`', f'write status = "{_NOT_BOUND}"')
        reason = data.get('reason')
        if not isinstance(reason, str) or not reason.strip():
            raise _error(
                path,
                'status = "not bound" needs a non-empty `reason`',
                'say why the project binds no vocabulary',
            )
        for key in ('rule', 'nouns', 'allowed', 'retired'):
            if key in data:
                label = '`rule`' if key == 'rule' else f'[[{key}]]'
                raise _error(
                    path,
                    f'status = "not bound" beside {label}',
                    f'keep either {label} or the status, not both',
                )
        not_bound = reason
    elif 'reason' in data:
        raise _error(path, '`reason` without status = "not bound"', 'remove `reason`')
    elif layer == 'project' and not nouns:
        raise _error(
            path,
            'a project file needs a non-empty [[nouns]] list',
            f'list the project\'s nouns, or write status = "{_NOT_BOUND}" with a reason',
        )

    return _File(
        path=path,
        schema=schema,
        rule=rule if rule and rule.strip() else None,
        nouns=tuple(
            Noun(
                name=n['name'],
                axis=n['axis'],
                layer=layer,
                reading=n.get('reading', ''),
                definition=n.get('definition', ''),
            )
            for n in nouns
        ),
        allowed=tuple(Allowed(term=a['term'], note=a['note'], layer=layer) for a in allowed),
        retired=tuple(Retired(noun=r['noun'], instead=r['instead']) for r in retired),
        not_bound=not_bound,
    )


def _vocabulary(
    *,
    layers: tuple[Layer, ...],
    nouns: tuple[Noun, ...],
    allowed: tuple[Allowed, ...],
    rule: str,
    retired: tuple[Retired, ...],
    notes: tuple[str, ...],
    scope: bool,
) -> Vocabulary:
    rule = _normalize_rule(rule)
    return Vocabulary(
        layers=layers,
        nouns=nouns,
        allowed=allowed,
        rule=rule,
        retired=retired,
        notes=notes,
        not_bound=None,
        in_scope=scope,
        digest=compute_digest([noun.name for noun in nouns], rule),
    )


# Any begin-marker line whatever its digest, so a malformed one is found and named; built from
# BLOCK_BEGIN, as BLOCK_RE is.
_ANY_BEGIN_LINE = re.compile(f'{re.escape(_MARKER_HEAD)}(\\S*){re.escape(_MARKER_TAIL)}')
_BOM = '\ufeff'
_GENERATED = 'GENERATED'
_HAND_EDIT = 'do not hand-edit'


def render_block(vocab: Vocabulary, newline: str = '\n') -> str:
    """The instruction-file block: the noun names, the rule and a pointer, between the markers.

    Each line ends in `newline`. A not-bound vocabulary has no digest and renders no block.
    """
    if vocab.digest is None:
        raise ValueError('a not-bound vocabulary renders no block')
    lines = [
        block_marker(vocab.digest),
        f'Work-unit nouns: {", ".join(noun.name for noun in vocab.nouns)}.',
        *vocab.rule.strip('\n').split('\n'),
        'Senses, allowed terms and sources: run `keel vocabulary`.',
        BLOCK_END,
    ]
    return ''.join(line + newline for line in lines)


@dataclass(frozen=True)
class BlockSpan:
    """Where a block sits in a text: `start` is its begin line, `end` is past its end line."""

    start: int
    end: int
    digest: str


def find_block(text: str) -> BlockSpan | None:
    """Locate the vocabulary block in `text`, or None when it carries none.

    Raises ValueError naming the defect when the text holds more than one begin line, a begin line
    whose digest is not `DIGEST_CHARS` lowercase hex digits (one `BLOCK_RE` rejects), or a begin
    line with no end line after it.
    """
    begins: list[tuple[int, str]] = []
    ends: list[int] = []
    offset = 0
    for line in text.split('\n'):
        stop = offset + len(line)
        start = offset + 1 if line.startswith(_BOM) else offset
        content = line.rstrip().lstrip(_BOM)
        if match := _ANY_BEGIN_LINE.fullmatch(content):
            begins.append((start, match.group(1)))
        elif content == BLOCK_END:
            ends.append(min(stop + 1, len(text)))
        offset = stop + 1
    if not begins:
        return None
    if len(begins) > 1:
        raise ValueError(f'{len(begins)} vocabulary begin markers, where one block takes one')
    start, digest = begins[0]
    if not BLOCK_RE.match(BLOCK_BEGIN.format(digest=digest)):
        raise ValueError(
            f'a vocabulary begin marker whose digest {digest!r} is not {DIGEST_CHARS} lowercase '
            'hex digits'
        )
    end = next((end for end in ends if end > start), None)
    if end is None:
        raise ValueError('a vocabulary begin marker with no end marker after it')
    return BlockSpan(start=start, end=end, digest=digest)


def newline_of(text: str) -> str:
    """The text's newline style: CRLF when it holds one, else LF."""
    return '\r\n' if '\r\n' in text else '\n'


def place_block(text: str, block: str) -> str:
    """`text` with `block` in place: its existing block replaced, else appended after a blank line.

    Every character outside the replaced span is kept. Raises ValueError as `find_block` does.
    """
    span = find_block(text)
    if span is not None:
        if not text[: span.end].endswith('\n'):
            block = block.rstrip('\r\n')
        return text[: span.start] + block + text[span.end :]
    if not text:
        return block
    newline = newline_of(text)
    return text + ('' if text.endswith('\n') else newline) + newline + block


def declares_generated(text: str) -> bool:
    """Whether the first five lines declare the text generated (`GENERATED`, `do not hand-edit`).

    The vocabulary block's own lines, begin marker through end marker, are left out first: a rule
    that says those words is not a banner.
    """
    head: list[str] = []
    inside = False
    for line in text.split('\n'):
        content = line.rstrip().lstrip(_BOM)
        if inside:
            inside = content != BLOCK_END
        elif _ANY_BEGIN_LINE.fullmatch(content):
            inside = True
        elif len(head) < 5:
            head.append(line)
    return any(_GENERATED in line or _HAND_EDIT in line.lower() for line in head)


def resolve(directory: Path, *, assume_scope: bool = False) -> Vocabulary:
    """Resolve the vocabulary that applies to `directory`, reading every file afresh."""
    scope = True if assume_scope else in_scope(directory)
    top = git_toplevel(directory)
    project = top / _PROJECT_FILE if top is not None else None
    if project is not None and project.is_file():
        loaded = _load(project, 'project')
        layers = (Layer('project', str(project), loaded.schema),)
        if loaded.not_bound is not None:
            return Vocabulary(
                layers=layers,
                nouns=(),
                allowed=(),
                rule='',
                retired=(),
                notes=(),
                not_bound=loaded.not_bound,
                in_scope=scope,
                digest=None,
            )
        return _vocabulary(
            layers=layers,
            nouns=loaded.nouns,
            allowed=loaded.allowed,
            rule=loaded.rule or DEFAULT_RULE,
            retired=loaded.retired,
            notes=(),
            scope=scope,
        )

    keel_layer = (Layer('keel', __version__),)
    path = user_file() if scope else None
    if path is None:
        return _vocabulary(
            layers=keel_layer,
            nouns=TOOL_NOUNS,
            allowed=TOOL_ALLOWED,
            rule=DEFAULT_RULE,
            retired=(),
            notes=(),
            scope=scope,
        )
    if not path.exists():
        return _vocabulary(
            layers=keel_layer,
            nouns=TOOL_NOUNS,
            allowed=TOOL_ALLOWED,
            rule=DEFAULT_RULE,
            retired=(),
            notes=(f"no user-level vocabulary file at {path}; keel's own nouns resolve",),
            scope=scope,
        )
    loaded = _load(path, 'user')
    keel_names = {noun.name for noun in TOOL_NOUNS}
    added = tuple(noun for noun in loaded.nouns if noun.name not in keel_names)
    notes = tuple(
        f"user-level noun `{noun.name}` in {path} repeats a keel noun; keel's is kept"
        for noun in loaded.nouns
        if noun.name in keel_names
    )
    return _vocabulary(
        layers=(*keel_layer, Layer('user', str(path), loaded.schema)),
        nouns=(*TOOL_NOUNS, *added),
        allowed=(*TOOL_ALLOWED, *loaded.allowed),
        rule=loaded.rule or DEFAULT_RULE,
        retired=loaded.retired,
        notes=notes,
        scope=scope,
    )
