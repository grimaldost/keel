"""The keel CLI: deterministic gates + the init scaffolder."""

import json
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import NamedTuple

import typer

from keel import __version__
from keel.bindings import check_bindings
from keel.budget_drift import check_budget_drift
from keel.check_ready import check_spec_ready, spec_hash
from keel.decompose_check import check_decomposition
from keel.errors import format_error
from keel.gate_ledger import (
    is_suite_row,
    ledger_path,
    newest_gate_version,
    read_lines,
    record_run,
    version_key,
)
from keel.models import DOR_CHECK_IDS, GateResult
from keel.reanchor import CertifiedBodyError, reanchor
from keel.show import available, body
from keel.survey import survey
from keel.templates import copy_templates, stamp_spec
from keel.vocabulary import (
    DIGEST_CHARS,
    INSTRUCTION_FILES,
    Vocabulary,
    VocabularyError,
    declares_generated,
    find_block,
    git_toplevel,
    nearest_block_dir,
    newline_of,
    place_block,
    project_file,
    render_block,
    resolve,
    user_file,
)

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help='keel - method gates and scaffolding',
)

# The commands whose logic is deliberately unimplemented (ADR-0003; `budget-drift`'s recorded
# disposition is removal, backlog KEEL-B30). One home: tests/test_claim_currency.py holds the
# docs that enumerate stubs to this set, in both directions, so a stub that becomes real (or a
# command that joins the set) cannot merge while the prose says otherwise.
STUB_COMMANDS = frozenset({'budget-drift'})


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def _root(
    version: bool = typer.Option(
        False,
        '--version',
        help='Show the keel version and exit.',
        is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    """keel - method gates and scaffolding."""


def _summary(result: GateResult) -> str:
    """The one line that says which copy ran, and how much of it had anything to read.

    A verdict that cannot name the copy that produced it is not auditable: two plugin caches were
    live on one machine, a session ran the older one by `uvx` while the newer was installed, and
    the fact had to be reconstructed from paths afterwards. The counts answer the other half — a
    gate with three applicable checks prints the same `OK` as a gate with twenty, and only one of
    those verdicts means much. A gate that reports no probes still names the version.
    """
    applicable = [probe for probe in result.probes if probe.candidates > 0]
    if not applicable:
        return f'keel {__version__}'
    fired = sum(1 for probe in applicable if probe.fired > 0)
    return f'keel {__version__} — {len(applicable)} checks applicable, {fired} fired'


def _emit(
    run: Callable[[], GateResult],
    *,
    hint: Callable[[GateResult], str | None] | None = None,
) -> None:
    """Run a gate; exit 0 pass, 1 violations, 2 not runnable (stub or missing input)."""
    try:
        result = run()
    except (NotImplementedError, FileNotFoundError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    # Warnings print on BOTH exit paths: they carry standing signals (operator-conditional B1,
    # B2 artifact/hash, kit skew) and a failing spec must not hide them (0.12.0 §1).
    for warning in result.warnings:
        typer.echo(warning.message)
    if result.passed:
        typer.echo('OK')
        typer.echo(_summary(result))
        raise typer.Exit(code=0)
    for violation in result.violations:
        typer.echo(f'{violation.where}: {violation.message}')
    # The report unit: dozens of anchor violations behind one edit are one thing to fix, and the
    # standing complaint about these messages is that they under-specify how to conform.
    grouped = [probe for probe in result.probes if probe.fired > probe.causes > 0]
    if grouped:
        detail = ', '.join(f'{p.check} {p.fired} in {p.causes}' for p in grouped)
        # The re-anchor instruction is true of the anchor checks and of nothing else: A13 groups
        # by register, and telling its reader to re-anchor a block would be advice about a
        # mechanism their finding does not have.
        advice = (
            ' — anchors failing against the same target, or sharing one drift delta, are one '
            'cause. Re-anchor the block (`keel re-anchor <spec>`); do not delete the rows.'
            if any(probe.check in _ANCHOR_CHECKS for probe in grouped)
            else ' — findings sharing a cause are one defect, not that many.'
        )
        typer.echo(f'note: {detail}{advice}')
    if hint is not None and (message := hint(result)):
        typer.echo(message)
    typer.echo(_summary(result))
    raise typer.Exit(code=1)


# The checks whose cause keys group by a moved or missing anchor.
_ANCHOR_CHECKS = frozenset({'A6', 'A11', 'A12', 'W3', 'W6'})
_STRUCTURAL_WHERES = frozenset(
    {'Numbered sections', 'PR ↔ section manifest', 'Concept → module map'}
)
# Shape failures (not absence) that still mean "not built from the template": an un-numbered
# heading (A1), a non-bijection manifest (A4), an empty manifest (A4). Matched lowercase against
# the (capital-PR) violation strings; `not covered by any PR` and A5 path failures are absent.
_MALFORMED_MARKERS = ('not numbered', 'bijection', 'has no pr')


def _spec_template_hint(result: GateResult) -> str | None:
    """Point a hand-written spec at the template when a top-level structure is absent or malformed.

    Fires on the structural-`where` set when the structure is absent (message begins `no `) OR
    malformed in shape: an un-numbered heading (A1), a non-bijection manifest (A4), an empty
    manifest (A4). A coverage slip (`not covered by any PR`) and an A5 path-grounding failure are
    content, not shape — they do NOT fire it, keeping the author loop quiet (ADR-0006).
    """
    suspect = any(
        v.where in _STRUCTURAL_WHERES
        and (
            v.message.startswith('no ')
            or any(marker in v.message.lower() for marker in _MALFORMED_MARKERS)
        )
        for v in result.violations
    )
    if not suspect:
        return None
    return (
        'hint: a required top-level section is missing or malformed — '
        'start from spec-template.md (run `keel new-spec <path>`).'
    )


@app.command('check-ready')
def check_ready_cmd(
    spec: Path,
    structure_only: bool = typer.Option(
        False,
        '--structure-only',
        help='Run Part A (well-formedness) only; skip the B1 pre-mortem check.',
    ),
) -> None:
    """Definition-of-Ready gate for a spec."""

    def run() -> GateResult:
        # The gate is the pure core; recording is the shell's job and is fail-open, so a
        # telemetry fault can change what is written and never what the gate returns.
        result = check_spec_ready(spec, structure_only=structure_only)
        record_run(spec, result, structure_only=structure_only)
        return result

    # Not a GateResult warning: it is about the machine, not the spec, so it has no check letter
    # and no ledger field, and it never changes the exit code.
    newest = newest_gate_version(ledger_path())
    if newest is not None and (version_key(newest) or ()) > (version_key(__version__) or ()):
        typer.echo(
            f'WARN: keel {newest} has run on this machine; this is keel {__version__} — '
            "upgrade (uv tool upgrade keel) or run the plugin's copy"
        )

    # Also not a GateResult warning, for the same reason: it judges the instruction files near the
    # spec, never the spec, and it runs outside `run()` so nothing of it reaches the ledger.
    for line in _vocabulary_notice(spec):
        typer.echo(line)

    _emit(run, hint=_spec_template_hint)


_NOTICE_FIX = 'run keel vocabulary --write'


def _vocabulary_notice(spec: Path) -> list[str]:
    """One WARN line per instruction file beside the nearest block that lacks the current one.

    Silent when no project file applies and no user-level file is present (such a machine cannot
    judge a block that depends on a user-level file), when the project binds no vocabulary, and
    when no block sits on the spec's walk. Any fault yields one line naming it and nothing else;
    it never raises.
    """
    try:
        return _judge_vocabulary_blocks(spec)
    except Exception as exc:  # a notice never breaks the gate, whatever the fault
        defect = str(exc).split('\n', 1)[0].strip() or type(exc).__name__
        return [f'WARN: the vocabulary block could not be judged — {defect}']


def _declares_not_bound(directory: Path) -> bool:
    """Whether the project file that applies to `directory` declares the project not bound.

    A malformed file declares nothing: its fault is reported once a block is found, when the
    vocabulary is resolved there, and a project with no block stays silent.
    """
    try:
        return resolve(directory, assume_scope=True).not_bound is not None
    except VocabularyError:
        return False


def _judge_vocabulary_blocks(spec: Path) -> list[str]:
    start = spec.resolve().parent
    # The silences that need no instruction file come first, so a repository that never adopted
    # the vocabulary has none of its instruction files read.
    project = project_file(start)
    if project is None or not project.is_file():
        user = user_file()
        if user is None or not user.exists():
            return []
    elif _declares_not_bound(start):
        return []
    directory = nearest_block_dir(start)
    if directory is None:
        return []
    vocab = resolve(directory, assume_scope=True)
    if vocab.not_bound is not None or vocab.digest is None:
        return []
    resolved = vocab.digest[:DIGEST_CHARS]
    lines: list[str] = []
    for name in INSTRUCTION_FILES:
        path = directory / name
        if not path.is_file():
            continue
        _, text = _read_instruction_file(path)
        try:
            span = find_block(text)
        except ValueError as exc:
            raise VocabularyError(f'{path}: {exc}') from exc
        if span is None:
            lines.append(
                f'WARN: the vocabulary block in {path} is missing (resolved {resolved}) — '
                + _NOTICE_FIX
            )
        elif span.digest != resolved:
            lines.append(
                f'WARN: the vocabulary block in {path} is stale '
                f'(block {span.digest}, resolved {resolved}) — {_NOTICE_FIX}'
            )
    return lines


@app.command('decompose-check')
def decompose_check_cmd(spec: Path) -> None:
    """Decompose exit gate: the generated series was reviewed before execution."""
    # Deliberately not ledgered: the ledger's `mode` is a closed enum over the DoR gate's two
    # modes, so a third one is a schema bump and belongs with the next ledger change, not smuggled
    # in here. Until then `gate-health` reads DoR runs only, which is what it says it reads.
    _emit(lambda: check_decomposition(spec))


@app.command('gate-health')
def gate_health_cmd(
    since: str = typer.Option('', '--since', help='Only runs on or after this date (YYYY-MM-DD).'),
    repo: str = typer.Option('', '--repo', help='Only runs recorded in this repo.'),
) -> None:
    """Read back the gate hit-rate ledger: per check, opportunity and fire rate."""
    path = ledger_path()
    rows = read_lines(path) if path is not None else []
    if since:
        rows = [row for row in rows if row.get('ts', '') >= since]
    if repo:
        # A repo named on the command line is read whole, whatever its name looks like.
        rows = [row for row in rows if row.get('repo') == repo]
    else:
        field = [row for row in rows if not is_suite_row(row)]
        if len(field) < len(rows):
            suite = len(rows) - len(field)
            typer.echo(
                f"{suite} {'row' if suite == 1 else 'rows'} written by keel's own test suite left "
                'out (keel 0.21.0 or older, in a repo named like a pytest tmp_path: test…N).'
            )
        rows = field
    if not rows:
        typer.echo(
            'no runs recorded yet — the ledger is written by `keel check-ready` '
            f'({path or "disabled by KEEL_GATE_LEDGER=off"}).'
        )
        raise typer.Exit(code=0)
    author = [row for row in rows if row.get('mode') == 'structure-only']
    submitted = [row for row in rows if row.get('mode') == 'full']
    typer.echo(
        f'{len(rows)} runs: {len(author)} author loop (--structure-only), '
        f'{len(submitted)} full-gate on a spec submitted as ready. '
        f'{sum(1 for row in submitted if not row.get("passed"))} of the latter were rejected.'
    )
    # candidates, revisions and repos are the units docs/evidence.md's pre-registered dispositions
    # are written in. A revision is the spec's content (`rev`, a prefix of its spec hash), so one
    # revision run twice, or from two directories, is one revision and its candidates count once.
    typer.echo(
        'check  applicable  candidates  revisions  repos  revisions-fired-on  causes  fire-rate'
    )
    for check in sorted(DOR_CHECK_IDS, key=_check_order):
        applicable = [row for row in rows if row.get('probes', {}).get(check, [0])[0] > 0]
        per_revision: dict[object, int] = {}
        for row in applicable:
            key = row.get('rev')
            per_revision[key] = max(per_revision.get(key, 0), row['probes'][check][0])
        repos = {row.get('repo') for row in applicable}
        fired_on = {row.get('rev') for row in applicable if row['probes'][check][1] > 0}
        causes = sum(row['probes'][check][2] for row in applicable)
        rate = f'{len(fired_on) / len(per_revision):.2f}' if per_revision else 'n/a'
        typer.echo(
            f'{check:<6} {len(applicable):>10}  {sum(per_revision.values()):>10}  '
            f'{len(per_revision):>9}  {len(repos):>5}  {len(fired_on):>18}  {causes:>6}  {rate:>9}'
        )
    typer.echo(
        'A check with applicable runs and no fires is CLEAN; one with no applicable runs never '
        "had an opportunity, and its silence says nothing either way. A revision is a spec's "
        'content, counted once wherever it ran, and fire-rate is revisions fired on over '
        'revisions with an opportunity; `repos` counts the directory names runs recorded, so two '
        'worktrees of one repository count twice.'
    )


def _check_order(check: str) -> tuple[str, int]:
    return check[0], int(check[1:])


@app.command('show')
def show_cmd(
    name: str = typer.Argument('', help='The body to print; omit with --list to see the names.'),
    list_names: bool = typer.Option(False, '--list', help='List the bodies this kit serves.'),
) -> None:
    """Print a body from the serving kit — the directive, the check reference, any template."""
    if list_names or not name:
        for key, description in available().items():
            typer.echo(f'{key:<24} {description}')
        raise typer.Exit(code=0)
    try:
        typer.echo(body(name))
    except LookupError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc


def _vocabulary_text(path: Path, vocab: Vocabulary) -> list[str]:
    lines = [f'path: {path}', 'layers:']
    for layer in vocab.layers:
        schema = f' ({layer.schema})' if layer.schema else ''
        lines.append(f'  {layer.name}: {layer.source}{schema}')
    lines.append(f'scope: {"in scope" if vocab.in_scope else "not in scope"}')
    if vocab.not_bound is not None:
        lines.append(f'not bound — {vocab.not_bound}')
        return lines
    lines.append('nouns:')
    for noun in vocab.nouns:
        lines.append(f'{noun.name} [{noun.layer}] axis: {noun.axis}')
        for sense in noun.senses:
            lines.append(f'  sense: {sense.text}')
            lines.append(f'    glossary: {sense.glossary}')
        if noun.reading:
            lines.append(f'  reading: {noun.reading}')
        if noun.definition:
            lines.append(f'  definition: {noun.definition}')
    lines.append('allowed:')
    lines.extend(f'  {item.term} [{item.layer}]: {item.note}' for item in vocab.allowed)
    first, *rest = vocab.rule.split('\n')
    lines.append(f'rule: {first}')
    lines.extend(f'  {line}' if line else '' for line in rest)
    lines.append('retired:')
    lines.extend(f'  {item.noun} -> {item.instead}' for item in vocab.retired)
    if vocab.notes:
        lines.append('notes:')
        lines.extend(f'  {note}' for note in vocab.notes)
    lines.append(f'digest: {vocab.digest}')
    return lines


def _block_files(root: Path, named: list[str]) -> list[Path]:
    """The files the block goes in: those named, else the root's AGENTS.md and any CLAUDE.md."""
    if named:
        return list(dict.fromkeys(Path(name).resolve() for name in named))
    first, *others = INSTRUCTION_FILES
    return [root / first, *(root / name for name in others if (root / name).is_file())]


_BLOCK_REPAIR = (
    'leave exactly one begin and one end marker in the file, the begin marker carrying '
    f'{DIGEST_CHARS} lowercase hex digits, or remove both'
)


class _Plan(NamedTuple):
    """What `--write` does to one file, decided before any file is written."""

    path: Path
    raw: bytes | None  # the bytes to write; None leaves the file as it is
    original: bytes | None  # the bytes the file holds now; None when it does not exist
    message: str


def _missing_folder(path: Path) -> VocabularyError:
    return VocabularyError(
        format_error(
            what=f'{path}: its folder does not exist',
            why='keel creates an instruction file, never the folders above it, and a missing '
            'folder is most often a mistyped path',
            fix='create the folder, or name another file with --file',
        )
    )


def _unwritable(path: Path, reason: str) -> VocabularyError:
    return VocabularyError(
        format_error(
            what=f'{path}: cannot be written ({reason})',
            why='the block is placed in every file or in none, so one file keel cannot write '
            'stops them all',
            fix='make it writable, or name other files with --file',
        )
    )


def _read_instruction_file(path: Path) -> tuple[bytes, str]:
    """The file's bytes and their text, or a VocabularyError naming the file."""
    try:
        raw = path.read_bytes()
        return raw, raw.decode('utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        raise VocabularyError(
            format_error(
                what=f'{path}: the instruction file cannot be read as UTF-8 ({exc})',
                why='the block is placed only in a file whose every other byte can be kept',
                fix='save it as UTF-8, or make it readable',
            )
        ) from exc


def _plan_block(vocab: Vocabulary, path: Path) -> _Plan:
    """What `path` should hold, or a VocabularyError naming why it cannot take the block."""
    digest = (vocab.digest or '')[:DIGEST_CHARS]
    if not path.exists():
        if not path.parent.is_dir():
            raise _missing_folder(path)
        if not os.access(path.parent, os.W_OK):
            raise _unwritable(path, 'its folder is not writable')
        raw = render_block(vocab).encode('utf-8')
        return _Plan(path, raw, None, f'created {path} holding the vocabulary block ({digest})')
    original, text = _read_instruction_file(path)
    if declares_generated(text):
        raise VocabularyError(
            format_error(
                what=f'{path}: its first lines declare it generated',
                why='a block written into a generated file is lost when it is next generated',
                fix="put the block in that file's generator, or name other files with --file",
            )
        )
    try:
        had_block = find_block(text) is not None
        placed = place_block(text, render_block(vocab, newline_of(text)))
    except ValueError as exc:
        raise VocabularyError(
            format_error(
                what=f'{path}: {exc}',
                why='keel replaces exactly one block and cannot tell which span is its own',
                fix=_BLOCK_REPAIR,
            )
        ) from exc
    raw = placed.encode('utf-8')
    if raw == original:
        message = f'{path} already carries the current vocabulary block ({digest}); unchanged'
        return _Plan(path, None, original, message)
    if not os.access(path, os.W_OK):
        raise _unwritable(path, 'it is read-only')
    verb = 'replaced the vocabulary block in' if had_block else 'added the vocabulary block to'
    return _Plan(path, raw, original, f'{verb} {path} ({digest})')


def _undo(written: list[_Plan]) -> list[Path]:
    """Put back what each written file held before; return the files that could not be."""
    left: list[Path] = []
    for plan in reversed(written):
        try:
            if plan.original is None:
                plan.path.unlink(missing_ok=True)
            else:
                plan.path.write_bytes(plan.original)
        except OSError:
            left.append(plan.path)
    return left


def _write_block(vocab: Vocabulary, files: list[Path]) -> None:
    """Place the block in every file, or, on any refusal or failed write, change nothing; exit 2."""
    if vocab.not_bound is not None:
        typer.echo(
            format_error(
                what=f'not bound — {vocab.not_bound} ({vocab.layers[0].source})',
                why='a project that binds no vocabulary has no block to place',
                fix='list the nouns in the project vocabulary file, or leave the files as they are',
            )
        )
        raise typer.Exit(code=2)
    plans: list[_Plan] = []
    refusals: list[str] = []
    for path in files:
        try:
            plans.append(_plan_block(vocab, path))
        except VocabularyError as exc:
            refusals.append(str(exc))
    if refusals:
        typer.echo('\n\n'.join(refusals))
        typer.echo('nothing written.')
        raise typer.Exit(code=2)
    written: list[_Plan] = []
    for plan in plans:
        if plan.raw is None:
            continue
        try:
            plan.path.write_bytes(plan.raw)
        except OSError as exc:
            left = _undo([*written, plan])
            typer.echo(str(_unwritable(plan.path, str(exc))))
            if left:
                typer.echo('could not restore: ' + ', '.join(str(path) for path in left))
            else:
                typer.echo('nothing written.')
            raise typer.Exit(code=2) from exc
        written.append(plan)
    for plan in plans:
        typer.echo(plan.message)
    raise typer.Exit(code=0)


def _check_block(vocab: Vocabulary, files: list[Path]) -> None:
    """Exit 0 when every file's block is current, 1 when one is missing, stale or malformed."""
    if vocab.not_bound is not None:
        typer.echo(f'not bound — {vocab.not_bound}')
        raise typer.Exit(code=0)
    digest = (vocab.digest or '')[:DIGEST_CHARS]
    behind = 0
    malformed = 0
    for path in files:
        if not path.exists():
            if not path.parent.is_dir():
                typer.echo(str(_missing_folder(path)))
                raise typer.Exit(code=2)
            behind += 1
            typer.echo(f'{path}: absent, no vocabulary block (resolved {digest})')
            continue
        try:
            _, text = _read_instruction_file(path)
        except VocabularyError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2) from exc
        try:
            span = find_block(text)
        except ValueError as exc:
            malformed += 1
            typer.echo(f'{path}: malformed vocabulary block: {exc} (resolved {digest})')
            continue
        if span is None:
            behind += 1
            typer.echo(f'{path}: no vocabulary block (resolved {digest})')
        elif span.digest != digest:
            behind += 1
            typer.echo(f'{path}: stale block {span.digest}, resolved {digest}')
        else:
            typer.echo(f'{path}: current ({digest})')
    if behind:
        typer.echo('run `keel vocabulary --write` to place the current block.')
    if malformed:
        typer.echo(f'repair each malformed block by hand: {_BLOCK_REPAIR}.')
    if behind or malformed:
        raise typer.Exit(code=1)
    typer.echo(f'every file carries the current vocabulary block ({digest}).')
    raise typer.Exit(code=0)


_FILE_OPTION = typer.Option(
    None,
    '--file',
    metavar='FILE',
    help='With --write or --check: a file to use instead of AGENTS.md and CLAUDE.md; repeatable.',
)


@app.command('vocabulary')
def vocabulary_cmd(
    path: str = typer.Argument(
        '.', help='The directory whose vocabulary to resolve; default: the current one.'
    ),
    as_json: bool = typer.Option(False, '--json', help='Print one JSON object instead of text.'),
    write: bool = typer.Option(
        False, '--write', help="Write the vocabulary block into the root's instruction files."
    ),
    check: bool = typer.Option(
        False, '--check', help='Exit 1 when an instruction file lacks the current block.'
    ),
    files: list[str] | None = _FILE_OPTION,
) -> None:
    """Print the work-unit vocabulary that applies to a directory, with its layers and digest."""
    if write and check:
        typer.echo('--write and --check are exclusive: write the block, or check it.')
        raise typer.Exit(code=2)
    if files and not (write or check):
        typer.echo('--file takes effect with --write or --check.')
        raise typer.Exit(code=2)
    if as_json and (write or check):
        typer.echo('--json prints the vocabulary; it does not combine with --write or --check.')
        raise typer.Exit(code=2)
    if not Path(path).is_dir():
        typer.echo(
            format_error(
                what=f'{path}: not a directory',
                why='`keel vocabulary` resolves the vocabulary for a directory, and git answers '
                'only for one that exists.',
                fix='Point it at an existing directory, or leave PATH out for the current one.',
            )
        )
        raise typer.Exit(code=2)
    resolved = Path(path).resolve()
    try:
        vocab = resolve(resolved, assume_scope=write or check)
    except VocabularyError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    if write or check:
        targets = _block_files(git_toplevel(resolved) or resolved, files or [])
        (_write_block if write else _check_block)(vocab, targets)
    if as_json:
        payload = {
            'path': str(resolved),
            'in_scope': vocab.in_scope,
            'layers': [asdict(layer) for layer in vocab.layers],
            'nouns': [asdict(noun) for noun in vocab.nouns],
            'allowed': [asdict(item) for item in vocab.allowed],
            'rule': vocab.rule,
            'retired': [asdict(item) for item in vocab.retired],
            'notes': list(vocab.notes),
            'not_bound': vocab.not_bound,
            'digest': vocab.digest,
        }
        typer.echo(json.dumps(payload, ensure_ascii=False))
    else:
        typer.echo('\n'.join(_vocabulary_text(resolved, vocab)))
    raise typer.Exit(code=0)


@app.command('re-anchor')
def reanchor_cmd(
    spec: Path,
    check: bool = typer.Option(False, '--check', help='Report what would change; write nothing.'),
    body: bool = typer.Option(
        False, '--body', help='Also repoint prose anchors — this MOVES the spec hash.'
    ),
    by_content: str = typer.Option(
        '',
        '--by-content',
        metavar='GIT-REF',
        help='Repoint by content: find where each line cited at this git ref sits now.',
    ),
) -> None:
    """Repoint a spec's drifted anchors — from their snippets, or by content against a git ref."""
    try:
        report = reanchor(spec, body=body, write=not check, by_content=by_content)
    except (FileNotFoundError, CertifiedBodyError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    for repair in report.applied:
        verb = 'would repoint' if check else 'repointed'
        typer.echo(f'line {repair.line_no}: {verb} {repair.anchor} -> {repair.corrected}')
    for repair in report.refused:
        typer.echo(f'line {repair.line_no}: left {repair.anchor} alone — {repair.refused}')
    if not report.applied and not report.refused:
        typer.echo('nothing to repoint: every anchor with a snippet is on the line it cites.')
    if report.applied and body and not check:
        typer.echo(
            'NOTE: --body rewrote anchors outside the certification span, so `keel spec-hash` has '
            'moved and the recorded certification now reads as stale (B2/W5). Re-stamp it.'
        )
    raise typer.Exit(code=0)


@app.command('spec-hash')
def spec_hash_cmd(spec: Path) -> None:
    """Print the canonical certification hash of a spec (its certification section excluded)."""
    try:
        digest = spec_hash(spec)
    except FileNotFoundError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    typer.echo(digest)


@app.command('survey')
def survey_cmd(directory: Path) -> None:
    """Sweep a design directory: which spec-shaped documents carry no certification?"""
    try:
        results = survey(directory)
    except NotADirectoryError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    uncertified = [row for row in results if row.spec_shaped and not row.certified]
    for row in results:
        if not row.spec_shaped:
            typer.echo(f'{row.path.name}: not a spec (no numbered sections, no PR manifest)')
        elif row.certified:
            typer.echo(f'{row.path.name}: {row.verdict}')
        else:
            typer.echo(f'{row.path.name}: SPEC, no certification recorded')
    specs = [row for row in results if row.spec_shaped]
    typer.echo(
        f'{len(specs)} spec-shaped document(s), {len(uncertified)} without a recorded '
        f'certification; {len(results) - len(specs)} other document(s) not counted.'
    )
    raise typer.Exit(code=1 if uncertified else 0)


@app.command('bind-check')
def bind_check_cmd(bindings: Path) -> None:
    """Assert every method-binding slot is filled."""
    _emit(lambda: check_bindings(bindings))


@app.command('budget-drift')
def budget_drift_cmd(series: Path, actuals: Path) -> None:
    """Flag wave cost drift past the threshold."""
    _emit(lambda: check_budget_drift(series, actuals))


@app.command('init')
def init_cmd(
    target: Path,
    force: bool = typer.Option(False, '--force', help='Overwrite existing files.'),
) -> None:
    """Copy the template kit into a target directory and point AGENTS.md at it."""
    try:
        copied = copy_templates(target, force=force)
    except FileExistsError as exc:
        typer.echo(str(exc))
        typer.echo(_point_agents_md(target))
        raise typer.Exit(code=2) from exc
    typer.echo(f'Copied {len(copied)} templates to {target}')
    typer.echo(_point_agents_md(target))


def _agents_pointer_line(bindings: str) -> str:
    """The one line `keel init` adds to a project's AGENTS.md. It names keel only (ADR-0003)."""
    return f'This project applies the keel method; its bindings are in `{bindings}`.'


def _project_root(target: Path) -> Path:
    """The git top level of `target`, else the current directory."""
    try:
        proc = subprocess.run(
            ['git', '-C', str(target), 'rev-parse', '--show-toplevel'],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False,
        )
    except OSError:
        proc = None
    if proc is not None and proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve()
    return Path.cwd().resolve()


def _point_agents_md(target: Path) -> str:
    """Append the method line to the root AGENTS.md when it lacks it; say what was done.

    The kit usually lands in a subdirectory (`keel init docs/method`), so AGENTS.md is looked up
    at the project root, and the bindings path is written relative to that root. A missing
    AGENTS.md is reported, never created. Outside git, the current directory is the root only for
    a kit inside it, so `keel init <scratch dir>` run from a repository leaves its AGENTS.md alone.
    """
    root = _project_root(target)
    agents = root / 'AGENTS.md'
    try:
        bindings = (target / 'method-bindings.md').resolve().relative_to(root).as_posix()
    except ValueError:
        return f'{target} is in no git repository and outside {root}; no AGENTS.md to point at it.'
    if not agents.is_file():
        return f'No AGENTS.md at {root}; nothing written there.'
    raw = agents.read_bytes()
    text = raw.decode('utf-8', errors='replace')
    if any('keel method' in line and bindings in line for line in text.splitlines()):
        return f'{agents} already names the keel method and {bindings}; unchanged.'
    newline = b'\r\n' if b'\r\n' in raw else b'\n'
    addition = _agents_pointer_line(bindings).encode('utf-8') + newline
    if raw and not raw.endswith(b'\n'):
        addition = newline + addition
    with agents.open('ab') as handle:
        handle.write(addition)
    return f'Added the keel method line to {agents} (bindings: {bindings}).'


@app.command('new-spec')
def new_spec_cmd(
    target: Path,
    force: bool = typer.Option(False, '--force', help='Overwrite an existing file.'),
) -> None:
    """Stamp spec-template.md to a new spec path (the keel spec on-ramp)."""
    try:
        stamped = stamp_spec(target, force=force)
    except FileExistsError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    typer.echo(f'Wrote {stamped}')


def _force_utf8(stream: object) -> None:
    """Emit UTF-8 so spec content (§, →, ↔) never crashes a legacy (cp1252) console."""
    reconfigure = getattr(stream, 'reconfigure', None)
    if reconfigure is not None:
        reconfigure(encoding='utf-8', errors='replace')


def main() -> None:
    """Console-script entry point."""
    _force_utf8(sys.stdout)
    _force_utf8(sys.stderr)
    app()
