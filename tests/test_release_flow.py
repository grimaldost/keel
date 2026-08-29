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

Both are scoped honestly. The tag assertion skips a checkout with no tags at all (CI checks out
shallow and fetches none), exempts the newest CHANGELOG heading (a release in flight is tagged
when it merges, not when its section is written), and exempts anything below the first public
release — 0.2.0/0.2.1/0.3.0 are pre-publication history, squashed into the 0.4.0 initial public
release commit, and there is no commit to tag.
"""

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIRST_PUBLIC_RELEASE = (0, 4, 0)


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
    # strictly forward — the nine-site version lock (tests/test_plugin_manifest.py) then holds
    # every site to that same heading in the same CI run.
    regression = _load_predicate().heading_regression
    cut = '# Changelog\n\n## [0.18.0] - 2026-08-29\n\n' + BASE_CHANGELOG.split('\n', 2)[2]
    stale = '# Changelog\n\n## [0.16.0] - 2026-08-29\n\n' + BASE_CHANGELOG.split('\n', 2)[2]
    assert regression(BASE_CHANGELOG, cut) is None
    assert regression(BASE_CHANGELOG, BASE_CHANGELOG) is None, 'no cut is not a regression'
    assert regression(BASE_CHANGELOG, stale) is not None
    assert regression(BASE_CHANGELOG, '# Changelog\n') is not None, 'losing every heading fails'


def test_a_contract_surface_change_wants_the_marker():
    # The marker arm (advisory in CI): a diff touching a file that defines what a consuming
    # tool parses — the gate ledger's schema, the CLI's exit-code surface — should carry the
    # literal `(consumer-affecting)` marker on an added CHANGELOG line.
    unmarked = _load_predicate().unmarked_contract_paths
    assert unmarked(['src/keel/gate_ledger.py', 'CHANGELOG.md'], '+- **A quiet entry.**') == [
        'src/keel/gate_ledger.py'
    ]
    marked = '+- **The ledger schema moves to v4** (consumer-affecting).'
    assert unmarked(['src/keel/gate_ledger.py', 'CHANGELOG.md'], marked) == []
    assert unmarked(['src/keel/check_ready.py'], '') == [], 'not a contract surface'
    removed = '-- **An old entry** (consumer-affecting).'
    assert unmarked(['src/keel/cli.py'], removed) == ['src/keel/cli.py'], (
        'a removed line does not satisfy the marker'
    )


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
