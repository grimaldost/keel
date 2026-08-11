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
    if hint is not None and (message := hint(result)):
        typer.echo(message)
    raise typer.Exit(code=1)


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


@app.command('spec-hash')
def spec_hash_cmd(spec: Path) -> None:
    """Print the canonical certification hash of a spec (its certification section excluded)."""
    try:
        digest = spec_hash(spec)
    except FileNotFoundError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from exc
    typer.echo(digest)


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
