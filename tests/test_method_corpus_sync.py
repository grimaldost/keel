"""Freshness guard: the packaged method corpus matches its source and ships in the wheel.

`src/keel/method/doctrine.md` is a byte-identical MIRROR of `docs/doctrine.md` — the doctrine
stays the source of truth (`AGENTS.md` conflict policy); the package ships a copy so a CLI-only
install carries the method's thesis and phases (ADR-0017). Regeneration rule (the doctrine's own
per-change freshness rule for committed mirrors): a PR that edits `docs/doctrine.md` re-copies
the mirror in the SAME PR — this gate is never deferrable to a later PR.

The wheel-namelist check exists because every other gate runs against the editable install,
which resolves `files('keel')` to the source tree and would stay green even if a packaging
change dropped `method/` from the built wheel (2026-07-16 spec §1; round-1 pre-mortem FM-3).
"""

import subprocess
import zipfile
from importlib.resources import files
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_doctrine_mirror_is_byte_identical():
    source = (ROOT / 'docs' / 'doctrine.md').read_text(encoding='utf-8')
    mirror = (ROOT / 'src' / 'keel' / 'method' / 'doctrine.md').read_text(encoding='utf-8')
    assert mirror == source, (
        'src/keel/method/doctrine.md drifted from docs/doctrine.md — re-copy the mirror in the '
        'same PR that edits the doctrine (never a later one)'
    )


def test_mirror_is_readable_as_package_data():
    text = (files('keel') / 'method' / 'doctrine.md').read_text(encoding='utf-8')
    assert len(text) > 0


def test_playbook_is_agent_neutral():
    # §2: the packaged playbook is the any-agent procedure — no plugin-only path resolution,
    # and it carries the entry rule the thinned skill routes to (§4 retargets its guard here).
    text = (files('keel') / 'method' / 'playbook.md').read_text(encoding='utf-8')
    assert '${CLAUDE_PLUGIN_ROOT}' not in text, 'playbook leaks a plugin-only path resolution'
    assert 'established format IS the binding' in text, 'playbook lost the bindings entry rule'


def test_wheel_ships_the_method_corpus(tmp_path):
    subprocess.run(
        ['uv', 'build', '--wheel', '--out-dir', str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    [wheel] = tmp_path.glob('*.whl')
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    for member in ('keel/method/doctrine.md', 'keel/method/playbook.md'):
        assert member in names, (
            f'the built wheel does not ship {member} — the editable-install gates cannot see '
            'this; fix the packaging, not the test'
        )
