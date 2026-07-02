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
    # F8: the four version sites and the newest CHANGELOG heading must agree, so a partial bump
    # (pyproject bumped, plugin.json forgotten) fails CI instead of shipping a mislabelled build.
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    pyproject = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
    init_src = (ROOT / 'src' / 'keel' / '__init__.py').read_text(encoding='utf-8')
    init_match = re.search(r"__version__\s*=\s*'([^']+)'", init_src)
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    changelog_match = re.search(r'^##\s*\[([0-9]+\.[0-9]+\.[0-9]+)\]', changelog, re.MULTILINE)
    assert init_match is not None and changelog_match is not None
    versions = {
        'plugin.json': plugin['version'],
        'pyproject.toml': pyproject['project']['version'],
        '__init__.py': init_match.group(1),
        'CHANGELOG.md (newest)': changelog_match.group(1),
    }
    assert len(set(versions.values())) == 1, f'version sites disagree: {versions}'


def test_referenced_assets_exist():
    assert (ROOT / 'skills' / 'apply-method' / 'SKILL.md').exists()
    assert (ROOT / 'agents' / 'pre-mortem-review.md').exists()
    assert (ROOT / 'hooks' / 'hooks.json').exists()
    for command in ('keel-apply', 'keel-check-ready', 'keel-premortem', 'keel-triage'):
        assert (ROOT / 'commands' / f'{command}.md').exists()
