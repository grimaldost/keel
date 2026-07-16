"""Packaged method-corpus assets and their public names (the `keel show` registry)."""

from importlib.resources import files

# Public asset name -> package-relative file. The corpus ships inside the package so a
# CLI-only install carries the method (ADR-0017); `keel show <name>` prints these.
ASSETS: dict[str, str] = {
    'doctrine': 'method/doctrine.md',
    'playbook': 'method/playbook.md',
    'pre-mortem': 'templates/pre-mortem-prompt.md',
}


def read_asset(name: str) -> str:
    """Return a packaged asset's text; an unknown name raises KeyError (the CLI translates)."""
    resource = files('keel')
    for part in ASSETS[name].split('/'):
        resource = resource / part
    return resource.read_text(encoding='utf-8')
