"""Locate and copy the packaged template kit."""

import shutil
from importlib.resources import files
from pathlib import Path

from keel.errors import format_error


def templates_root() -> Path:
    """Return the directory holding the packaged templates.

    keel is built with uv_build (src layout) and installed unpacked (editable or a
    regular wheel), so package data is on a real path and str() of the Traversable is
    safe. Revisit with importlib.resources.as_file if ever shipped as a zipapp.
    """
    return Path(str(files('keel') / 'templates'))


def list_templates() -> list[Path]:
    """Return all packaged template files, sorted by name."""
    return sorted(templates_root().glob('*.md'))


def copy_templates(target_dir: Path, *, force: bool = False) -> list[Path]:
    """Copy the template kit into target_dir; refuse to overwrite unless force."""
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for template in list_templates():
        dest = target_dir / template.name
        if dest.exists() and not force:
            raise FileExistsError(
                format_error(
                    what=f'{dest} already exists.',
                    why='keel init does not overwrite existing files by default.',
                    fix='Re-run with --force to overwrite, or choose an empty target.',
                )
            )
        shutil.copy2(template, dest)
        copied.append(dest)
    return copied


def stamp_spec(target: Path, *, force: bool = False) -> Path:
    """Copy spec-template.md to target as a single-file scaffold; refuse overwrite unless force.

    A single-file stamp (not the directory-copy copy_templates): `keel new-spec` gives an author
    the keel spec shape directly, so a spec is not hand-written in a foreign format (the on-ramp the
    field flagged).
    """
    source = templates_root() / 'spec-template.md'
    if target.exists() and not force:
        raise FileExistsError(
            format_error(
                what=f'{target} already exists.',
                why='keel new-spec does not overwrite an existing file by default.',
                fix='Re-run with --force to overwrite, or choose a new path.',
            )
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target
