import json
import re
import tomllib
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifests_parse_and_name_keel():
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    assert plugin['name'] == 'keel'
    assert any(p['name'] == 'keel' for p in market['plugins'])


def test_version_is_consistent_across_all_sites():
    # F8: the version sites and the newest CHANGELOG heading must agree, so a partial bump
    # (pyproject bumped, plugin.json forgotten) fails CI instead of shipping a mislabelled build.
    # 0.12.0 §2 adds the bundled agent's identity line as a fifth site: a stale plugin-cache copy
    # then self-announces its lag on every verdict it returns.
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    pyproject = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
    init_src = (ROOT / 'src' / 'keel' / '__init__.py').read_text(encoding='utf-8')
    init_match = re.search(r"__version__\s*=\s*'([^']+)'", init_src)
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    changelog_match = re.search(r'^##\s*\[([0-9]+\.[0-9]+\.[0-9]+)\]', changelog, re.MULTILINE)
    agent_src = (ROOT / 'agents' / 'pre-mortem-review.md').read_text(encoding='utf-8')
    agent_match = re.search(
        r'bundled `pre-mortem-review` agent from keel ([0-9]+\.[0-9]+\.[0-9]+)', agent_src
    )
    template_src = (ROOT / 'src' / 'keel' / 'templates' / 'spec-template.md').read_text(
        encoding='utf-8'
    )
    # T0.3: the stamp's home is the visible header (`- **Kit:** x.y.z`). It used to be an HTML
    # comment below the closing rule, which every hand-copied spec silently dropped.
    stamp_match = re.search(
        r'^-\s*\*\*Kit:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$', template_src, re.MULTILINE
    )
    skill_src = (ROOT / 'skills' / 'apply-method' / 'SKILL.md').read_text(encoding='utf-8')
    skill_match = re.search(r'ships with keel ([0-9]+\.[0-9]+\.[0-9]+)', skill_src)
    assert init_match is not None and changelog_match is not None
    assert agent_match is not None, 'agent identity line missing (0.12.0 §2 fifth version site)'
    assert stamp_match is not None, 'kit stamp missing from spec-template (0.12.0 §9 sixth site)'
    assert skill_match is not None, 'apply-method version line missing (0.12.0 §9 seventh site)'
    versions = {
        'plugin.json': plugin['version'],
        'pyproject.toml': pyproject['project']['version'],
        '__init__.py': init_match.group(1),
        'CHANGELOG.md (newest)': changelog_match.group(1),
        'agents/pre-mortem-review.md': agent_match.group(1),
        'spec-template.md (kit stamp)': stamp_match.group(1),
        'skills/apply-method/SKILL.md': skill_match.group(1),
    }
    assert len(set(versions.values())) == 1, f'version sites disagree: {versions}'


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
