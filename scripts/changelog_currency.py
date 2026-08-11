"""Fail a change that ships kit or doctrine without recording it (CONTRIBUTING step 4).

The version-consistency lock proves the eight version sites AGREE; nothing proved any of them
MOVED. So a shipped-kit or doctrine promotion could merge CI-green with no CHANGELOG entry and no
bump — which is what happened to the two docs PRs that landed between 0.13.0 and 0.13.1, and what
makes "count the promotions that shipped" unanswerable (KEEL-B08).

Reads a changed-file list (arguments, else stdin, one path per line) and exits 1 when it touches a
shipped-kit path while `CHANGELOG.md` is untouched. Repo-local tooling, deliberately not part of
the `keel` package: it enforces this repo's release loop, not a consumer's (ADR-0003).

    git diff --name-only "origin/$BASE...HEAD" | uv run python scripts/changelog_currency.py
"""

import sys
from collections.abc import Iterable

# What a consumer receives when this repo ships: the template kit, the doctrine, and the three
# plugin entry-point directories. `src/keel/*.py` is deliberately absent — a gate's behaviour
# change reaches a consumer through a release, and the release's own diff carries the CHANGELOG.
KIT_PREFIXES = ('src/keel/templates/', 'agents/', 'skills/', 'commands/')
KIT_FILES = ('docs/doctrine.md',)
RECORD = 'CHANGELOG.md'


def unrecorded_kit_paths(changed: Iterable[str]) -> list[str]:
    """The shipped-kit paths in `changed` that no CHANGELOG edit accompanies ([] when fine)."""
    paths = [path.strip().replace('\\', '/') for path in changed if path.strip()]
    if RECORD in paths:
        return []
    return [path for path in paths if path.startswith(KIT_PREFIXES) or path in KIT_FILES]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    changed = args or sys.stdin.read().splitlines()
    unrecorded = unrecorded_kit_paths(changed)
    if not unrecorded:
        print('OK: no shipped-kit change, or the CHANGELOG records it.')
        return 0
    print('Shipped-kit paths changed with no CHANGELOG.md entry:')
    for path in unrecorded:
        print(f'  {path}')
    print(
        'Record the promotion in CHANGELOG.md and bump SemVer (CONTRIBUTING, "The loop" step 4). '
        'An unrecorded promotion is uncountable.'
    )
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
