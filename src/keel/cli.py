"""The keel CLI: deterministic gates + the init scaffolder."""

import sys
from collections.abc import Callable
from pathlib import Path

import typer

from keel import __version__
from keel.bindings import check_bindings
from keel.budget_drift import check_budget_drift
from keel.check_ready import check_spec_ready
from keel.models import GateResult
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


def _spec_template_hint(result: GateResult) -> str | None:
    """Point a hand-written spec at the template when a top-level section is absent (A1/A4/A5)."""
    absent = any(
        v.where in _STRUCTURAL_WHERES and v.message.startswith('no ') for v in result.violations
    )
    if not absent:
        return None
    return (
        'hint: a required top-level section is missing — '
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
    _emit(lambda: check_spec_ready(spec, structure_only=structure_only), hint=_spec_template_hint)


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
