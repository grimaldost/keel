"""Tag currency for the release loop (KEEL-B08).

The release loop had no machine layer for "record in CHANGELOG and bump". Railform's changelog
gate now judges whether a change is recorded (`changelog.records` in `railform.toml`) and
`railform version-sites` holds the version sites to one version; both run in CI's `railform` job.
What stays here is the tag half: every released version carries a `vX.Y.Z` tag, so "which
versions actually shipped" is answerable from the repo rather than from memory.

The tag assertions are scoped honestly. The first skips a checkout with no tags at all (the skip
protects a genuinely tagless or shallow clone; CI's `checks` job (railform's, with the full
history the `ci.setup.fetch_depth` exceptions row gives it) checks out tags precisely so these
assertions run there), exempts the newest CHANGELOG heading (a release
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
# v0.5.0, v0.6.0 and v0.7.0 each carry one entry edited in 0.22.0 to redact a private tool's name
# from the published tree; the entries say the same thing with the name replaced by `…`.
SECTION_LOCK_GRANDFATHERED = frozenset(
    {'v0.5.0', 'v0.6.0', 'v0.7.0', 'v0.10.0', 'v0.12.0', 'v0.16.0'}
)
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


def _changelog_versions() -> list[tuple[int, int, int]]:
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    return [
        (int(major), int(minor), int(patch))
        for major, minor, patch in re.findall(
            r'^## \[([0-9]+)\.([0-9]+)\.([0-9]+)\]', text, re.MULTILINE
        )
    ]


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
