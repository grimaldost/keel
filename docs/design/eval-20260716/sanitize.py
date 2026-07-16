#!/usr/bin/env python3
"""Blind the judge: copy a run's produced artifacts with arm-identifying tokens neutralized.

Usage: sanitize.py <sandbox_dir> <out_dir>
Copies every *.md and scripts/*.py the run produced (AGENTS.md and the toy project's own
pre-existing files excluded), replacing version strings, wheel/worktree paths, and
version-specific CLI forms with neutral placeholders (eval spec §3, blinding).
"""

import re
import sys
from pathlib import Path

PRE_EXISTING = {'AGENTS.md', 'README.md', 'test_tempo.py', 'contract.py', 'parse.py', 'report.py'}

# The enumerated token set the eval spec (§3, round-1 FM-3) requires neutralized: versions
# (incl. the propagated kit stamp), dist paths, uvx forms, the 0.14.0-only `keel show` shape,
# the plugin-root token, wrapper paths, and the skill/plugin-vs-snippet vocabulary.
RULES = [
    (re.compile(r'0\.1[34]\.\d+'), 'X.Y.Z'),
    (re.compile(r'/tmp/\S*?(keel[\w.-]*\.whl|keel-0131)\S*'), '<KEEL-DIST>'),
    (re.compile(r'uvx --from \S+ keel'), '<KEEL-CLI>'),
    (re.compile(r'(\./)?bin/keel'), '<KEEL-CLI>'),
    (re.compile(r'\bkeel show (\w[\w-]*)'), r'<KEEL-CLI> read \1'),
    (re.compile(r'\$\{?CLAUDE_PLUGIN_ROOT\}?'), '<KEEL-DIST>'),
    (re.compile(r'\bskills?\b', re.IGNORECASE), 'guide'),
    (re.compile(r'\bplugins?\b', re.IGNORECASE), 'toolkit'),
    (re.compile(r'\bsnippets?\b', re.IGNORECASE), 'note'),
    (re.compile(r'\bplaybook\b', re.IGNORECASE), 'procedure'),
]

LEAK_PATTERN = re.compile(
    r'0\.1[34]\.\d+|keel show|CLAUDE_PLUGIN_ROOT|\.whl|keel-0131|uvx --from'
    r'|\bskills?\b|\bplugins?\b|\bsnippets?\b|\bplaybook\b',
    re.IGNORECASE,
)


def sanitize(text: str) -> str:
    for pattern, repl in RULES:
        text = pattern.sub(repl, text)
    return text


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.rglob('*')):
        if not path.is_file() or path.name in PRE_EXISTING:
            continue
        if path.suffix not in ('.md', '.py', '.toml'):
            continue
        if 'bin/' in str(path.relative_to(src)):
            continue
        rel = path.relative_to(src)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            sanitize(path.read_text(encoding='utf-8', errors='replace')), encoding='utf-8'
        )
    # Residual-leak gate (eval spec §3): judging may not start unless this comes back clean.
    leaks = []
    for path in sorted(out.rglob('*')):
        if path.is_file():
            for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
                if LEAK_PATTERN.search(line):
                    leaks.append(f'{path}: {line.strip()[:80]}')
    if leaks:
        print('RESIDUAL-LEAKS:')
        print('\n'.join(leaks))
        sys.exit(1)
    print(f'sanitized -> {out} (leak gate clean)')


if __name__ == '__main__':
    main()
