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
  `## [x.y.z]` heading, it must be a strict SemVer increase over the base's — the version lock
  (tests/test_plugin_manifest.py) then holds the version sites to that heading in the same CI
  run (CONTRIBUTING, "Release discipline", owns the enumeration).

- **Marker arm** (`--marker DIFF_FILE HEAD_FILE`, changed paths on stdin; advisory, always
  exits 0): a diff touching a contract-surface file should carry the literal
  `(consumer-affecting)` marker on an added `- ` entry line under HEAD_FILE's newest release
  heading — the header paragraph that defines the marker, and edits to older sections, cannot
  satisfy it. In CI a miss is a `::warning` annotation and a step-summary line, never a red.
  Advisory until the convention has a release of practice behind it; the escalation to a hard
  fail is the recorded next step.

Repo-local tooling, deliberately not part of the `keel` package: it enforces this repo's
release loop, not a consumer's (ADR-0003).
"""

import os
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


def _newest_section_entries(head_text: str) -> set[str]:
    """The top-level `- ` entry lines under the newest `## [x.y.z]` heading of `head_text`."""
    newest = _newest_version(head_text)
    if newest is None:
        return set()
    version = '.'.join(map(str, newest))
    inside = False
    entries: set[str] = set()
    for line in head_text.splitlines():
        if line.startswith('## '):
            inside = line.startswith(f'## [{version}]')
            continue
        if inside and line.startswith('- '):
            entries.add(line)
    return entries


def unmarked_contract_paths(
    changed: Iterable[str], changelog_diff: str, head_text: str
) -> list[str]:
    """The contract-surface paths in `changed` when no qualifying CHANGELOG line is marked.

    Qualifying: an ADDED `- ` entry line that lives under the newest release heading of
    `head_text`. The first cut of this arm scanned every added line, and the header paragraph
    that DEFINES the marker satisfied it on the arm's first real exercise — scoping to
    newest-section entry lines closes that false OK.
    """
    paths = [path.strip().replace('\\', '/') for path in changed if path.strip()]
    touched = [path for path in paths if path in CONTRACT_FILES]
    if not touched:
        return []
    entries = _newest_section_entries(head_text)
    added_entries = (
        line[1:]
        for line in changelog_diff.splitlines()
        if line.startswith('+- ') and line[1:] in entries
    )
    if any(MARKER in line for line in added_entries):
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


def _marker_mode(diff_file: str, head_file: str, changed: list[str]) -> int:
    unmarked = unmarked_contract_paths(
        changed,
        Path(diff_file).read_text(encoding='utf-8'),
        Path(head_file).read_text(encoding='utf-8'),
    )
    if not unmarked:
        print('OK: no contract-surface change, or a newest-section entry carries the marker.')
        return 0
    names = ', '.join(unmarked)
    # The ::warning line is what makes the advisory visible in a collapsed CI log: it surfaces
    # as an annotation on the run and on the PR's checks tab.
    print(
        f'::warning file=CHANGELOG.md::contract-surface change without {MARKER}: {names} — '
        'mark the entry if the change moves what a consuming tool parses (advisory)'
    )
    print('NOTICE (advisory): contract-surface files changed and no added `- ` entry line')
    print(f'under the newest release heading carries `{MARKER}`:')
    for path in unmarked:
        print(f'  {path}')
    print(
        'If the change moves what a consuming tool parses (ledger schema, exit codes), mark its '
        'CHANGELOG entry; if not, nothing to do — this arm is advisory.'
    )
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8') as handle:
            handle.write(
                f'**Changelog marker arm (advisory):** contract-surface change without '
                f'`{MARKER}`: {names}\n'
            )
    return 0


USAGE = """usage: changelog_currency.py [CHANGED_PATH ...]      (paths on stdin when absent)
       changelog_currency.py --headings BASE_FILE HEAD_FILE
       changelog_currency.py --marker DIFF_FILE HEAD_FILE  (changed paths on stdin)"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0].startswith('--'):
        if args[0] == '--headings' and len(args) == 3:
            return _headings_mode(args[1], args[2])
        if args[0] == '--marker' and len(args) == 3:
            return _marker_mode(args[1], args[2], sys.stdin.read().splitlines())
        print(USAGE)
        return 2
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
