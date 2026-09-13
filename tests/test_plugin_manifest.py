import json
import re
import tomllib
from collections import Counter
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifests_parse_and_name_keel():
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    assert plugin['name'] == 'keel'
    assert any(p['name'] == 'keel' for p in market['plugins'])


@dataclass(frozen=True, slots=True)
class VersionSite:
    """One place the release version is written, and the pattern that reads it.

    The registry lives HERE, in the test that enforces agreement, and `scripts/bump_version.py`
    imports it: the bump and the gate then cannot disagree about what a version site is. The
    release loop used to be a second, hand-kept list — nine sites, a five-round
    run-test/read-failure/fix-one-site cycle per release — and this is that list deleted rather
    than duplicated.

    `authored` marks the site whose value is written with its own content: the newest CHANGELOG
    heading arrives with a section under it, so a script that rewrote the number would rename the
    PREVIOUS release. It is checked and reported, never written.
    """

    label: str
    path: str
    pattern: str
    authored: bool = False


_V = r'([0-9]+\.[0-9]+\.[0-9]+)'
# 0.12.0 §2 added the bundled agent's identity line as a fifth site (a stale plugin-cache copy
# then self-announces its lag on every verdict it returns) and §9 the kit stamp and the skill.
# The core spec-template's stamp joins in 0.19.0: it was the ninth site by CONTRIBUTING's count
# and the one held only by `test_core_variants`, where a stale stamp fails as a strict-subset
# error whose message says nothing about versions.
VERSION_SITES = (
    VersionSite('plugin.json', '.claude-plugin/plugin.json', rf'"version":\s*"{_V}"'),
    VersionSite('pyproject.toml', 'pyproject.toml', rf"(?m)^version = ['\"]{_V}['\"]"),
    VersionSite('src/keel/__init__.py', 'src/keel/__init__.py', rf"__version__ = '{_V}'"),
    VersionSite('CHANGELOG.md (newest)', 'CHANGELOG.md', rf'(?m)^##\s*\[{_V}\]', authored=True),
    VersionSite(
        'agents/pre-mortem-review.md',
        'agents/pre-mortem-review.md',
        rf'bundled `pre-mortem-review` agent from keel {_V}',
    ),
    VersionSite(
        'spec-template.md (kit stamp)',
        'src/keel/templates/spec-template.md',
        rf'(?m)^-\s*\*\*Kit:\*\*\s*{_V}\s*$',
    ),
    VersionSite(
        'core/spec-template.md (kit stamp)',
        'src/keel/templates/core/spec-template.md',
        rf'(?m)^-\s*\*\*Kit:\*\*\s*{_V}\s*$',
    ),
    VersionSite(
        'skills/apply-method/SKILL.md',
        'skills/apply-method/SKILL.md',
        rf'ships with keel {_V}',
    ),
)


def read_versions(root: Path = ROOT) -> dict[str, str | None]:
    """What each site currently reads, with None for a site whose pattern matched nothing."""
    found: dict[str, str | None] = {}
    for site in VERSION_SITES:
        match = re.search(site.pattern, (root / site.path).read_text(encoding='utf-8'))
        found[site.label] = match.group(1) if match else None
    return found


def disagreement(versions: dict[str, str | None]) -> str:
    """'' when every site agrees; otherwise ONE message naming every site that does not.

    One message, because the failure used to be read one site at a time: the test named whichever
    assertion fired first, the author fixed that site, re-ran, and met the next one — five rounds
    for a patch bump. What the author needs is the whole disagreement in one read.
    """
    readable = {label: value for label, value in versions.items() if value}
    unreadable = [label for label, value in versions.items() if not value]
    tally = Counter(readable.values())
    if not unreadable and len(tally) <= 1:
        return ''
    expected = tally.most_common(1)[0][0] if tally else '(nothing readable)'
    wrong = [f'{label} reads {value}' for label, value in readable.items() if value != expected]
    wrong += [f'{label} matched no version at all' for label in unreadable]
    return f'{len(wrong)} of {len(versions)} version sites disagree with {expected}: ' + '; '.join(
        sorted(wrong)
    )


def test_version_is_consistent_across_all_sites():
    # F8: every version site and the newest CHANGELOG heading agree, so a partial bump
    # (pyproject bumped, plugin.json forgotten) fails CI instead of shipping a mislabelled build.
    assert not (report := disagreement(read_versions())), report


def test_the_disagreement_names_every_site_in_one_message():
    # The property that ends the five-round loop: one run, the whole truth.
    report = disagreement(
        {
            'a': '0.19.0',
            'b': '0.19.0',
            'c': '0.18.1',
            'd': '0.17.0',
            'e': None,
        }
    )
    assert 'c reads 0.18.1' in report
    assert 'd reads 0.17.0' in report
    assert 'e matched no version at all' in report
    assert report.count(';') == 2, f'not one message: {report}'


def test_each_patterned_site_reads_the_field_its_parser_would():
    # The registry is regexes, because a bump must WRITE them; a regex that reads the wrong field
    # would be invisible to every assertion above. The two structured sites are parsed properly
    # here and compared, so the pattern cannot quietly point at some other version literal.
    versions = read_versions()
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    pyproject = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
    assert versions['plugin.json'] == plugin['version']
    assert versions['pyproject.toml'] == pyproject['project']['version']


def test_changelog_heading_chain_is_intact():
    # F1 (0.12.0 pre-cut audit; repaired in e5ede82): a release edit REPLACED the previous
    # release's heading instead of inserting above it, so the 0.11.1 entry read as absorbed into
    # 0.12.0's section — and only the blind audit caught it, because the version-consistency test
    # reads the NEWEST heading only and the broken chain was still strictly descending. Three
    # layers, one per failure shape:
    #   shape — every H2 is a strict `## [x.y.z] - YYYY-MM-DD` heading. This file has never used
    #     an `## [Unreleased]` heading (a deliberate deviation from Keep a Changelog), and the
    #     newest-heading version site above assumes the first heading IS the current release, so a
    #     non-SemVer H2 is a violation, not a form to tolerate.
    #   order — strict descending SemVer with no duplicates, comparing parsed integer tuples (not
    #     strings, since '0.10.0' < '0.9.0' lexically) — catches an entry pasted below an older
    #     release, a double-pasted heading, a typo'd version.
    #   absorption — no `### kind` repeats inside one release section: replacing a heading merges
    #     two bodies (`### Changed` twice under one release) — the assertion that actually fails on
    #     the originating F1 file; the order layer alone passes it.
    heading = re.compile(r'^## \[([0-9]+\.[0-9]+\.[0-9]+)\] - [0-9]{4}-[0-9]{2}-[0-9]{2}$')
    lines = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8').splitlines()
    versions: list[tuple[int, int, int]] = []
    section = 'preamble'
    kinds: list[str] = []
    for line in lines:
        if line.startswith('## '):
            match = heading.match(line)
            assert match is not None, f'malformed release heading: {line!r}'
            major, minor, patch = match.group(1).split('.')
            versions.append((int(major), int(minor), int(patch)))
            section, kinds = match.group(1), []
        elif line.startswith('### '):
            kind = line.removeprefix('### ').strip()
            assert kind not in kinds, (
                f'`### {kind}` repeats inside the [{section}] section — a release edit likely '
                'replaced the previous heading and absorbed its entry (the F1 class)'
            )
            kinds.append(kind)
    assert len(versions) >= 2, 'parse rot: fewer than two release headings found'
    for newer, older in pairwise(versions):
        assert newer > older, (
            f'headings not in strict descending SemVer order: {newer} before {older}'
        )


def test_referenced_assets_exist():
    assert (ROOT / 'skills' / 'apply-method' / 'SKILL.md').exists()
    assert (ROOT / 'agents' / 'pre-mortem-review.md').exists()
    for command in ('keel-apply', 'keel-check-ready', 'keel-premortem', 'keel-triage'):
        assert (ROOT / 'commands' / f'{command}.md').exists()


def test_no_empty_hooks_placeholder(hooks_json=ROOT / 'hooks' / 'hooks.json'):
    # KEEL-B29. `hooks/hooks.json` shipped `{"hooks": {}}` — a slot reserved for an edit-time hook
    # that never arrived, absent from the plugin-reference entry-point table and from that table's
    # coverage test, while the doctrine names hooks as one of the two deterministic machines: the
    # repo's own A10 failure class, in its own tree.
    #
    # The 0.12.0 decision (T2g) kept it because "whether the plugin loader tolerates its absence is
    # unverifiable offline". It is verifiable by inspection, and now verified: four installed,
    # loading plugins in this operator's environment ship no `hooks/` directory at all. The empty
    # placeholder is deleted; a hooks.json that exists must declare a real hook, so the placeholder
    # cannot come back while a genuine edit-time hook still can.
    if hooks_json.exists():
        declared = json.loads(hooks_json.read_text(encoding='utf-8')).get('hooks')
        assert declared, 'hooks/hooks.json declares no hook — an empty placeholder claims a machine'


def test_plugin_reference_documents_every_entry_point():
    # The CLI half has had a coverage test since F9/ARCH-10; the plugin half had none, and two of
    # the four slash commands were named in no published doc at all. Same shape as
    # test_cli_reference_documents_every_command: every shipped entry point appears in the
    # published reference, so a new one cannot land undocumented.
    # All three entry-point directories are globbed, not listed by hand — docs/extension-points.md
    # tells a contributor that adding under `commands/`, `skills/` or `agents/` requires a row
    # here, and a hardcoded list would leave that claim unenforced for two of the three.
    # The command match requires the table's backticked form (`` `/name` `` or `` `/name <arg>` ``)
    # rather than a bare substring: `f'/{name}' in reference` passes vacuously for any name that
    # is a prefix of an existing one (`/keel-check` matches inside `/keel-check-ready`), and an
    # `\b` anchor does not close that hole either, since `-` is already a word boundary.
    reference = (ROOT / 'docs' / 'plugin-reference.md').read_text(encoding='utf-8')
    commands = sorted(p.stem for p in (ROOT / 'commands').glob('*.md'))
    skills = sorted(p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md'))
    agents = sorted(p.stem for p in (ROOT / 'agents').glob('*.md'))
    assert commands and skills and agents, 'an entry-point directory enumerated empty'
    missing = [
        f'/{name}' for name in commands if not re.search(rf'`/{re.escape(name)}(?=[ `])', reference)
    ]
    missing += [
        name for name in skills + agents if not re.search(rf'`{re.escape(name)}`', reference)
    ]
    assert not missing, f'plugin-reference.md is missing: {missing}'


def test_apply_method_routes_through_bindings():
    # §8 (c1-T4): the router consumes the project's bindings record on the already-established
    # path instead of pointing every entry at the packaged templates.
    skill = (ROOT / 'skills' / 'apply-method' / 'SKILL.md').read_text(encoding='utf-8')
    assert 'established format IS the binding' in skill
