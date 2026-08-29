"""Fail a change that ships kit or doctrine without recording it (CONTRIBUTING step 4).

The version-consistency lock proves the version sites AGREE (CONTRIBUTING's "Release
discipline" section owns their enumeration); nothing proved any of them MOVED. So a
shipped-kit or doctrine promotion could merge CI-green with no CHANGELOG entry and no bump —
which is what happened to the two docs PRs that landed between 0.13.0 and 0.13.1, and what
makes "count the promotions that shipped" unanswerable (KEEL-B08).

Three arms, all run by CI's `changelog-currency` job (the estate's porting source):

- **Kit arm** (default; exits 1): a changed-file list (arguments, else stdin, one path per line)
  touching a shipped-kit path while `CHANGELOG.md` is untouched is an unrecorded promotion.

      git diff --name-only "origin/$BASE...HEAD" | uv run python scripts/changelog_currency.py

- **Version arm** (`--headings BASE_FILE HEAD_FILE`; exits 1): when the PR cuts a new newest
  `## [x.y.z]` heading, it must be a strict SemVer increase over the base's — the nine-site
  version lock (tests/test_plugin_manifest.py) then holds every site to that heading in the
  same CI run.

- **Marker arm** (`--marker DIFF_FILE`, changed paths on stdin; advisory, always exits 0): a
  diff touching a contract-surface file should carry the literal `(consumer-affecting)` marker
  on an added CHANGELOG line. Advisory until the convention has a release of practice behind
  it; the escalation to a hard fail is the recorded next step.

Repo-local tooling, deliberately not part of the `keel` package: it enforces this repo's
release loop, not a consumer's (ADR-0003).
"""

import re
import sys
from collections.abc import Iterable
from pathlib import Path

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


HEADING = re.compile(r'^## \[([0-9]+)\.([0-9]+)\.([0-9]+)\]', re.MULTILINE)

# What a consuming tool parses, as files: the gate ledger's schema (its own contract forbids
# reading a count across a schema version silently) and the CLI's registered surface with its
# 0/1/2 exit codes. An entry that moves either carries the literal marker the CHANGELOG header
# defines.
CONTRACT_FILES = ('src/keel/gate_ledger.py', 'src/keel/cli.py')
MARKER = '(consumer-affecting)'


def _newest_version(changelog_text: str) -> tuple[int, int, int] | None:
    match = HEADING.search(changelog_text)
    if match is None:
        return None
    major, minor, patch = match.groups()
    return (int(major), int(minor), int(patch))


def heading_regression(base_text: str, head_text: str) -> str | None:
    """Why the newest-heading move is wrong (None when there is no cut, or the cut is forward)."""
    head = _newest_version(head_text)
    if head is None:
        return 'parse rot: no `## [x.y.z]` heading left in CHANGELOG.md'
    base = _newest_version(base_text)
    if base is None or head == base or head > base:
        return None
    dotted_head, dotted_base = ('.'.join(map(str, v)) for v in (head, base))
    return (
        f'the newest CHANGELOG heading moved from {dotted_base} to {dotted_head} — a release '
        'cut inserts a strictly greater version above the previous heading, never at or below it'
    )


def unmarked_contract_paths(changed: Iterable[str], changelog_diff: str) -> list[str]:
    """The contract-surface paths in `changed` when no added CHANGELOG line carries the marker."""
    paths = [path.strip().replace('\\', '/') for path in changed if path.strip()]
    touched = [path for path in paths if path in CONTRACT_FILES]
    if not touched:
        return []
    added = (
        line
        for line in changelog_diff.splitlines()
        if line.startswith('+') and not line.startswith('+++')
    )
    if any(MARKER in line for line in added):
        return []
    return touched


def _headings_mode(base_file: str, head_file: str) -> int:
    problem = heading_regression(
        Path(base_file).read_text(encoding='utf-8'),
        Path(head_file).read_text(encoding='utf-8'),
    )
    if problem is None:
        print('OK: no release cut, or the newest heading moved strictly forward.')
        return 0
    print(problem)
    return 1


def _marker_mode(diff_file: str, changed: list[str]) -> int:
    unmarked = unmarked_contract_paths(changed, Path(diff_file).read_text(encoding='utf-8'))
    if not unmarked:
        print('OK: no contract-surface change, or its CHANGELOG entry carries the marker.')
        return 0
    print('NOTICE (advisory): contract-surface files changed with no `(consumer-affecting)`')
    print('marker on an added CHANGELOG line:')
    for path in unmarked:
        print(f'  {path}')
    print(
        'If the change moves what a consuming tool parses (ledger schema, exit codes), mark its '
        'CHANGELOG entry; if not, nothing to do — this arm is advisory.'
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ['--headings']:
        return _headings_mode(args[1], args[2])
    if args[:1] == ['--marker']:
        return _marker_mode(args[1], sys.stdin.read().splitlines())
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
