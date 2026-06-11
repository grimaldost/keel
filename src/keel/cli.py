"""The keel CLI: deterministic gates + the init scaffolder."""

import sys
from collections.abc import Callable
from pathlib import Path

import typer

from keel.bindings import check_bindings
from keel.budget_drift import check_budget_drift
from keel.check_ready import check_spec_ready
from keel.models import GateResult
from keel.templates import copy_templates

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help='keel - method gates and scaffolding',
)


def _emit(run: Callable[[], GateResult]) -> None:
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
    raise typer.Exit(code=1)


@app.command('check-ready')
def check_ready_cmd(spec: Path) -> None:
    """Definition-of-Ready gate for a spec."""
    _emit(lambda: check_spec_ready(spec))


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
