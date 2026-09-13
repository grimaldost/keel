"""Write a release version to every site the consistency test holds (KEEL-B*, field E9a).

    uv run python scripts/bump_version.py 0.19.0

The release loop's remaining hand work was nine sites, found one at a time: run the suite, read
whichever assertion fired first, fix that site, run again — five rounds for a patch bump, twice
measured. The fix is not a second list of sites to keep in step with the first. This script
imports `VERSION_SITES` from `tests/test_plugin_manifest.py`, which is the test that FAILS when
the sites disagree, so the bump and the gate read the same registry by construction.

Two sites it deliberately does not write, and says so instead:

- the newest `CHANGELOG.md` heading, which arrives with its own section under it — rewriting the
  number would rename the previous release;
- `uv.lock`, which is regenerated (`uv lock`) rather than edited, and which CI checks separately.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_plugin_manifest import VERSION_SITES, disagreement, read_versions  # noqa: E402

_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')


def bump(root: Path, version: str) -> tuple[list[str], list[str]]:
    """Write `version` to every writable site; return (what moved, what is left to the author)."""
    moved: list[str] = []
    left: list[str] = []
    for site in VERSION_SITES:
        path = root / site.path
        text = path.read_text(encoding='utf-8')
        match = re.search(site.pattern, text)
        if match is None:
            left.append(f'{site.label}: no version matched its pattern — read {site.path} by hand')
            continue
        if match.group(1) == version:
            continue
        if site.authored:
            left.append(
                f'{site.label}: still {match.group(1)} — write the `## [{version}] - <date>` '
                'heading and its entries above the previous section'
            )
            continue
        start, end = match.span(1)
        path.write_text(text[:start] + version + text[end:], encoding='utf-8')
        moved.append(f'{site.label}: {match.group(1)} -> {version}')
    return moved, left


def main(argv: list[str]) -> int:
    # The same legacy-console guard `keel.cli` carries: a release script that half-bumps a tree and
    # then dies encoding an em dash would be a worse loop than the one it replaces.
    reconfigure = getattr(sys.stdout, 'reconfigure', None)
    if reconfigure is not None:
        reconfigure(encoding='utf-8', errors='replace')
    if len(argv) != 1 or not _VERSION_RE.match(argv[0]):
        print('usage: bump_version.py <x.y.z>')
        return 2
    version = argv[0]
    moved, left = bump(ROOT, version)
    for line in moved:
        print(f'bumped {line}')
    if not moved:
        print(f'nothing to bump: every writable site already reads {version}')
    for line in left:
        print(f'by hand: {line}')
    print('by hand: uv.lock — run `uv lock` after pyproject.toml moves (CI reds a stale lock)')
    report = disagreement(read_versions(ROOT))
    print(report or f'every version site reads {version}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
