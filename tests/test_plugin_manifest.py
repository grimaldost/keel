import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifests_parse_and_name_keel():
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    assert plugin['name'] == 'keel'
    assert plugin['version'] == '0.6.1'
    assert any(p['name'] == 'keel' for p in market['plugins'])


def test_referenced_assets_exist():
    assert (ROOT / 'skills' / 'apply-method' / 'SKILL.md').exists()
    assert (ROOT / 'agents' / 'pre-mortem-review.md').exists()
    assert (ROOT / 'hooks' / 'hooks.json').exists()
    for command in ('keel-apply', 'keel-check-ready', 'keel-premortem', 'keel-triage'):
        assert (ROOT / 'commands' / f'{command}.md').exists()
