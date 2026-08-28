"""The keel CLI: deterministic gates + the init scaffolder."""

import sys
from collections.abc import Callable
from pathlib import Path

import typer

from keel import __version__
from keel.bindings import check_bindings
from keel.budget_drift import check_budget_drift
from keel.check_ready import check_spec_ready, spec_hash
from keel.gate_ledger import ledger_path, read_lines, record_run
from keel.models import CHECK_IDS, GateResult
from keel.reanchor import reanchor
from keel.show import available, body
from keel.survey import survey
from keel.templates import copy_templates, stamp_spec

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help='keel - method gates and scaffolding',
)


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

    _emit(run, hint=_spec_template_hint)


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
        rows = [row for row in rows if row.get('repo') == repo]
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
    typer.echo('check  applicable  revisions-fired-on  causes  fire-rate')
    for check in sorted(CHECK_IDS, key=_check_order):
        applicable = [row for row in rows if row.get('probes', {}).get(check, [0])[0] > 0]
        fired_on = {
            (row.get('repo'), row.get('spec'), row.get('rev'))
            for row in applicable
            if row['probes'][check][1] > 0
        }
        causes = sum(row['probes'][check][2] for row in applicable)
        rate = f'{len(fired_on) / len(applicable):.2f}' if applicable else 'n/a'
        typer.echo(f'{check:<6} {len(applicable):>10}  {len(fired_on):>18}  {causes:>6}  {rate:>9}')
    typer.echo(
        'A check with applicable runs and no fires is CLEAN; one with no applicable runs never '
        'had an opportunity, and its silence says nothing either way.'
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


@app.command('re-anchor')
def reanchor_cmd(
    spec: Path,
    check: bool = typer.Option(False, '--check', help='Report what would change; write nothing.'),
    body: bool = typer.Option(
        False, '--body', help='Also repoint prose anchors — this MOVES the spec hash.'
    ),
) -> None:
    """Repoint a spec's drifted anchors from the snippets that identify them."""
    try:
        report = reanchor(spec, body=body, write=not check)
    except FileNotFoundError as exc:
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
    """Copy the template kit into a target directory."""
    try:
        copied = copy_templates(target, force=force)
    except FileExistsError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    typer.echo(f'Copied {len(copied)} templates to {target}')


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
