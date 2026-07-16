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

RULES = [
    (re.compile(r'0\.1[34]\.\d+'), 'X.Y.Z'),
    (re.compile(r'/tmp/\S*?(keel[-_]?[\w.]*\.whl|keel-0131)\S*'), '<KEEL-DIST>'),
    (re.compile(r'uvx --from \S+ keel'), '<KEEL-CLI>'),
    (re.compile(r'\bkeel show (\w[\w-]*)'), r'<KEEL-CLI> read \1'),
    (re.compile(r'\$\{?CLAUDE_PLUGIN_ROOT\}?'), '<KEEL-DIST>'),
]


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
        rel = path.relative_to(src)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            sanitize(path.read_text(encoding='utf-8', errors='replace')), encoding='utf-8'
        )
    print(f'sanitized -> {out}')


if __name__ == '__main__':
    main()
