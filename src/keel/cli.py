"""The keel CLI: deterministic gates + the init scaffolder."""

import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path

import typer

from keel import __version__
from keel.bindings import check_bindings
from keel.budget_drift import check_budget_drift
from keel.check_ready import check_spec_ready, spec_hash
from keel.decompose_check import check_decomposition
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
from keel.vocabulary import Vocabulary, VocabularyError, resolve

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

    _emit(run, hint=_spec_template_hint)


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


def _vocabulary_text(vocab: Vocabulary) -> list[str]:
    lines = ['layers:']
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
        lines.extend(f'  sense: {sense.text}' for sense in noun.senses)
        if noun.reading:
            lines.append(f'  reading: {noun.reading}')
        if noun.definition:
            lines.append(f'  definition: {noun.definition}')
    lines.append('allowed:')
    lines.extend(f'  {item.term} [{item.layer}]: {item.note}' for item in vocab.allowed)
    lines.append(f'rule: {vocab.rule}')
    lines.append('retired:')
    lines.extend(f'  {item.noun} -> {item.instead}' for item in vocab.retired)
    if vocab.notes:
        lines.append('notes:')
        lines.extend(f'  {note}' for note in vocab.notes)
    lines.append(f'digest: {vocab.digest}')
    return lines


@app.command('vocabulary')
def vocabulary_cmd(
    path: str = typer.Argument(
        '.', help='The directory whose vocabulary to resolve; default: the current one.'
    ),
    as_json: bool = typer.Option(False, '--json', help='Print one JSON object instead of text.'),
) -> None:
    """Print the work-unit vocabulary that applies to a directory, with its layers and digest."""
    resolved = Path(path).resolve()
    try:
        vocab = resolve(resolved)
    except VocabularyError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
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
        typer.echo('\n'.join(_vocabulary_text(vocab)))
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
