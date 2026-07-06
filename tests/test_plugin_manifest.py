import json
import re
import tomllib
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
    stamp_match = re.search(r'<!-- keel kit ([0-9]+\.[0-9]+\.[0-9]+) -->', template_src)
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


def test_referenced_assets_exist():
    assert (ROOT / 'skills' / 'apply-method' / 'SKILL.md').exists()
    assert (ROOT / 'agents' / 'pre-mortem-review.md').exists()
    # hooks.json is an empty placeholder kept deliberately: it reserves the edit-time-hook slot
    # (doctrine's "invariants → machines" face) and whether the plugin loader tolerates its
    # absence is unverifiable offline — decision recorded in the 0.12.0 spec (T2g); revisit if
    # the plugin API documents optionality.
    assert (ROOT / 'hooks' / 'hooks.json').exists()
    for command in ('keel-apply', 'keel-check-ready', 'keel-premortem', 'keel-triage'):
        assert (ROOT / 'commands' / f'{command}.md').exists()
