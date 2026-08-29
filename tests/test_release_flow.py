"""CONTRIBUTING step 4, machine-enforced (KEEL-B08).

The release loop had no machine layer for "record in CHANGELOG and bump": the version lock proves
the version sites AGREE (CONTRIBUTING's "Release discipline" section owns their enumeration),
never that any of them MOVED. So a shipped kit or doctrine
promotion could merge CI-green with no CHANGELOG entry and no bump — and did, twice, in the two
docs PRs that shipped between 0.13.0 and 0.13.1. Two halves:

- **Changelog currency** — the predicate `scripts/changelog_currency.py` runs in CI over a PR's
  changed-file list: a diff touching a shipped-kit path with `CHANGELOG.md` unchanged fails. The
  pure part is tested here; the git plumbing is the CI step's.
- **Tag currency** — every released version carries a `vX.Y.Z` tag, so "which versions actually
  shipped" is answerable from the repo rather than from memory.

Both are scoped honestly. The tag assertion skips a checkout with no tags at all (the skip
protects a genuinely tagless or shallow clone; CI's `check` job checks out full history and
tags precisely so these assertions run there), exempts the newest CHANGELOG heading (a release
in flight is tagged when it merges, not when its section is written), and exempts anything
below the first public release — 0.2.0/0.2.1/0.3.0 are pre-publication history, squashed into
the 0.4.0 initial public release commit, and there is no commit to tag.

Since the v0.17.0 mistag, two more assertions. v0.17.0 was tagged lightweight at the
section-cut commit, mid-stack, and six wave PRs then merged while appending to the
already-tagged [0.17.0] section — so the published tag lacked most of what its own notes
described, and, being lightweight, could not even say when it was laid. So: a release tag from
v0.18.0 on is annotated (`git tag -a` on the release PR's merge commit), and a tagged
version's CHANGELOG entry set never changes after the tag exists — checked for every SemVer
tag, with the known historical edits exempted BY NAME rather than by a silent floor.
"""

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIRST_PUBLIC_RELEASE = (0, 4, 0)
# The annotated-tag rule starts at the first release after the v0.17.0 mistag.
ANNOTATED_FROM = (0, 18, 0)
# The section lock applies to every SemVer tag, with the known historical edits exempted BY
# NAME — a named exemption over a silent unknown. v0.16.0 is the same append-after-tag defect
# one release before v0.17.0; v0.10.0 and v0.12.0 are older post-tag section edits found by
# this guard's first sweep over history. v0.17.0 itself is NOT exempt: the 0.18.0 cut
# reconciled its section to exactly what the tag contains, so the lock holds it like any other.
SECTION_LOCK_GRANDFATHERED = frozenset({'v0.10.0', 'v0.12.0', 'v0.16.0'})
# A tag outside this shape (a release candidate, a scratch tag) is not a release tag and is
# not asserted over — without the guard the first `v0.19.0-rc1` reds the suite with a
# ValueError instead of a verdict.
TAG_SHAPE = re.compile(r'^v\d+\.\d+\.\d+$')


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        check=False,
    )


def _semver_tags() -> list[str]:
    tags = _git('tag', '--list', 'v*')
    if tags.returncode != 0 or not tags.stdout.strip():
        pytest.skip('no tags in this checkout (a shallow or tagless clone) — nothing to assert')
    names = [line.strip() for line in tags.stdout.splitlines() if line.strip()]
    return [name for name in names if TAG_SHAPE.match(name)]


def _section_entries(changelog_text: str, version: str) -> list[str]:
    """The top-level `- ` entry lines recorded under one `## [version]` heading."""
    inside = False
    entries: list[str] = []
    for line in changelog_text.splitlines():
        if line.startswith('## '):
            inside = line.startswith(f'## [{version}]')
            continue
        if inside and line.startswith('- '):
            entries.append(line.strip())
    return entries


def _load_predicate():
    path = ROOT / 'scripts' / 'changelog_currency.py'
    spec = importlib.util.spec_from_file_location('changelog_currency', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _changelog_versions() -> list[tuple[int, int, int]]:
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    return [
        (int(major), int(minor), int(patch))
        for major, minor, patch in re.findall(
            r'^## \[([0-9]+)\.([0-9]+)\.([0-9]+)\]', text, re.MULTILINE
        )
    ]


def test_kit_change_without_a_changelog_entry_is_unrecorded():
    unrecorded = _load_predicate().unrecorded_kit_paths
    assert unrecorded(['src/keel/templates/spec-template.md']) == [
        'src/keel/templates/spec-template.md'
    ]
    assert unrecorded(['docs/doctrine.md', 'README.md']) == ['docs/doctrine.md']
    assert unrecorded(['agents/pre-mortem-review.md']) == ['agents/pre-mortem-review.md']
    assert unrecorded(['skills/apply-method/SKILL.md']) == ['skills/apply-method/SKILL.md']
    assert unrecorded(['commands/keel-apply.md']) == ['commands/keel-apply.md']


def test_kit_change_with_a_changelog_entry_is_recorded():
    unrecorded = _load_predicate().unrecorded_kit_paths
    assert unrecorded(['src/keel/templates/spec-template.md', 'CHANGELOG.md']) == []


def test_non_kit_changes_need_no_changelog_entry():
    unrecorded = _load_predicate().unrecorded_kit_paths
    assert unrecorded(['src/keel/check_ready.py', 'tests/test_check_ready.py', 'README.md']) == []


BASE_CHANGELOG = '# Changelog\n\n## [0.17.0] - 2026-08-28\n\n### Added\n\n- **A thing.**\n'


def test_a_release_cut_moves_the_newest_heading_forward():
    # The version arm: a PR whose CHANGELOG gains a new newest heading must move the version
    # strictly forward — the version lock (tests/test_plugin_manifest.py) then holds the
    # version sites to that same heading in the same CI run.
    regression = _load_predicate().heading_regression
    cut = '# Changelog\n\n## [0.18.0] - 2026-08-29\n\n' + BASE_CHANGELOG.split('\n', 2)[2]
    stale = '# Changelog\n\n## [0.16.0] - 2026-08-29\n\n' + BASE_CHANGELOG.split('\n', 2)[2]
    assert regression(BASE_CHANGELOG, cut) is None
    assert regression(BASE_CHANGELOG, BASE_CHANGELOG) is None, 'no cut is not a regression'
    assert regression(BASE_CHANGELOG, stale) is not None
    assert regression(BASE_CHANGELOG, '# Changelog\n') is not None, 'losing every heading fails'


MARKED_HEAD = (
    'header prose defining the literal (consumer-affecting) marker.\n'
    '\n'
    '## [0.18.0] - 2026-08-29\n'
    '\n'
    '### Changed\n'
    '\n'
    '- **The ledger schema moves to v4** (consumer-affecting).\n'
    '- **A quiet entry.**\n'
    '\n'
    '## [0.17.0] - 2026-08-28\n'
    '\n'
    '- **An old entry** (consumer-affecting).\n'
)


def test_a_contract_surface_change_wants_the_marker():
    # The marker arm (advisory in CI): a diff touching a file that defines what a consuming
    # tool parses — the gate ledger's schema, the CLI's exit-code surface — should carry the
    # literal `(consumer-affecting)` marker on an added `- ` entry line under the NEWEST
    # heading. The first cut scanned the whole diff and the header paragraph defining the
    # marker satisfied it — the cases below pin that closed hole.
    unmarked = _load_predicate().unmarked_contract_paths
    marked = '+- **The ledger schema moves to v4** (consumer-affecting).'
    assert unmarked(['src/keel/gate_ledger.py', 'CHANGELOG.md'], marked, MARKED_HEAD) == []
    quiet = '+- **A quiet entry.**'
    assert unmarked(['src/keel/gate_ledger.py', 'CHANGELOG.md'], quiet, MARKED_HEAD) == [
        'src/keel/gate_ledger.py'
    ]
    header_only = '+header prose defining the literal (consumer-affecting) marker.'
    assert unmarked(['src/keel/cli.py'], header_only, MARKED_HEAD) == ['src/keel/cli.py'], (
        'the header paragraph defining the marker must not satisfy the arm'
    )
    old_section = '+- **An old entry** (consumer-affecting).'
    assert unmarked(['src/keel/cli.py'], old_section, MARKED_HEAD) == ['src/keel/cli.py'], (
        'an entry added under an older heading must not satisfy the arm'
    )
    removed = '-- **The ledger schema moves to v4** (consumer-affecting).'
    assert unmarked(['src/keel/cli.py'], removed, MARKED_HEAD) == ['src/keel/cli.py'], (
        'a removed line does not satisfy the marker'
    )
    assert unmarked(['src/keel/check_ready.py'], '', MARKED_HEAD) == [], 'not a contract surface'


def test_the_cli_modes_guard_their_operands():
    # A mode flag with missing or extra operands is a usage error (exit 2), never an
    # IndexError over sys.argv.
    main = _load_predicate().main
    assert main(['--headings']) == 2
    assert main(['--headings', 'only-one']) == 2
    assert main(['--marker', 'only-one']) == 2
    assert main(['--bogus']) == 2


def test_released_versions_carry_a_tag():
    tags = subprocess.run(
        ['git', 'tag', '--list', 'v*'], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if tags.returncode != 0 or not tags.stdout.strip():
        pytest.skip('no tags in this checkout (a shallow or tagless clone) — nothing to assert')
    tagged = {line.strip().lstrip('v') for line in tags.stdout.splitlines() if line.strip()}
    versions = _changelog_versions()
    assert versions, 'parse rot: no release headings found'
    expected = [v for v in versions[1:] if v >= FIRST_PUBLIC_RELEASE]
    missing = ['.'.join(map(str, v)) for v in expected if '.'.join(map(str, v)) not in tagged]
    assert not missing, (
        f'released versions carry no tag: {missing} — tag the release commit on main '
        '(`git tag vX.Y.Z <commit>`) and publish it with `git push --tags`.'
    )


def test_release_tags_are_annotated():
    # A lightweight tag records no tagger date, so "when was this laid, relative to its
    # content" — the exact question the v0.17.0 mistag turns on — is unanswerable from the tag
    # itself. From v0.18.0 a release tag is annotated and carries its own date and message.
    for tag in _semver_tags():
        if tuple(int(part) for part in tag.lstrip('v').split('.')) < ANNOTATED_FROM:
            continue
        kind = _git('cat-file', '-t', tag).stdout.strip()
        assert kind == 'tag', (
            f'{tag} is not an annotated tag (`git cat-file -t` says {kind!r}) — lay release '
            f"tags with `git tag -a {tag} <release-merge-commit> -m 'keel "
            f"{tag.lstrip('v')}'`."
        )


def test_a_tagged_section_matches_its_tag():
    # The v0.17.0 mistag as a standing check: the tag was laid at the section-cut commit and
    # six wave PRs then appended to the already-tagged [0.17.0] section, so the published tag
    # lacked most of what its own notes described. For every SemVer tag (minus the named
    # historical exemptions), the entry lines under a tagged version's heading are exactly the
    # ones in that tag's own CHANGELOG — appending to (or thinning) a released section after
    # its tag exists fails here. Only the `- ` entry lines are compared: a typo fix in an
    # entry's continuation prose stays legal; the entry set is the contract.
    head_text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    for tag in _semver_tags():
        if tag in SECTION_LOCK_GRANDFATHERED:
            continue
        version = tag.lstrip('v')
        shown = _git('show', f'{tag}:CHANGELOG.md')
        assert shown.returncode == 0, f'{tag} carries no CHANGELOG.md'
        tagged = _section_entries(shown.stdout, version)
        current = _section_entries(head_text, version)
        assert tagged, f'{tag}: no entries under its own [{version}] heading — parse rot'
        assert current == tagged, (
            f'the [{version}] section changed after {tag} was laid — a released section is '
            'closed by its tag; post-tag work belongs under the next heading '
            f'(tagged entries: {len(tagged)}, current: {len(current)})'
        )
