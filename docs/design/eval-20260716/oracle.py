#!/usr/bin/env python3
"""Deterministic oracle vector for one behavioral run (eval spec §3, o1-o6 + o-hop).

Usage: oracle.py <sandbox_dir> <T1|T2> <dist_path> <A|B>
Prints a JSON object; never judges quality (that is the blind judge's job). o-hop reads the
sandbox's `.keel-cli.log` (written by the bin/keel wrapper): for arm B it is true iff the run
invoked `keel show playbook` or `keel show doctrine`; for arm A the procedure is inline in
AGENTS.md, so o-hop is trivially true by design (recorded as 'inline').
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KIT_MARKER = 'definition-of-ready.md'
SLOTS = ('ADR home', 'Spec format', 'Guardrails', 'Review checklist', 'Reflection sink')


def find(root: Path, name: str) -> list[Path]:
    return [p for p in root.rglob(name) if p.is_file()]


def o2_bindings_filled(root: Path) -> bool:
    for bindings in find(root, 'method-bindings.md'):
        text = bindings.read_text(encoding='utf-8', errors='replace')
        hits = 0
        for line in text.splitlines():
            if not line.strip().startswith('|'):
                continue
            if any(slot.lower() in line.lower() for slot in SLOTS):
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if cells and cells[-1] and not cells[-1].startswith('<'):
                    hits += 1
        if hits >= len(SLOTS):
            return True
    return False


def candidate_specs(root: Path) -> list[Path]:
    out = []
    for p in root.rglob('*.md'):
        if p.name in ('spec-template.md', 'AGENTS.md', 'README.md'):
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        if '## Numbered sections' in text and '<feature/refactor name>' not in text:
            out.append(p)
    return out


def o3_spec_passes(root: Path, wheel: str) -> tuple[bool, str]:
    for spec in candidate_specs(root):
        proc = subprocess.run(
            ['uvx', '--from', wheel, 'keel', 'check-ready', '--structure-only', str(spec)],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode == 0:
            return True, str(spec.relative_to(root))
    return False, ''


def o4_not_self_certified(root: Path) -> bool:
    for spec in candidate_specs(root):
        text = spec.read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r'\*\*Verdict:\*\*\s*(\S+)', text):
            if m.group(1).upper().startswith('CERTIFIED'):
                return False
    return True


def o6_flag_works(root: Path) -> bool:
    script = root / 'scripts' / 'summarize.py'
    if not script.is_file():
        return False
    with tempfile.NamedTemporaryFile('w', suffix='.log', delete=False) as fh:
        fh.write('1700000000 INFO started\n1700000001 ERROR boom\n1700000002 ERROR again\n')
        sample = fh.name
    proc = subprocess.run(
        [sys.executable, str(script), sample], capture_output=True, text=True,
        check=False, cwd=root,
    )
    ok = proc.returncode == 0 and 'ERROR' in proc.stdout and '2' in proc.stdout
    tests = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
        capture_output=True, text=True, check=False, cwd=root,
    )
    return ok and tests.returncode == 0


def o_hop(root: Path, arm: str) -> object:
    if arm == 'A':
        return 'inline'
    log = root / '.keel-cli.log'
    if not log.is_file():
        return False
    text = log.read_text(encoding='utf-8', errors='replace')
    return 'show playbook' in text or 'show doctrine' in text


def main() -> None:
    root, task, wheel, arm = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    vector: dict[str, object] = {'sandbox': str(root), 'task': task, 'arm': arm}
    if task == 'T1':
        vector['o1_kit_present'] = bool(find(root, KIT_MARKER))
        vector['o2_bindings_filled'] = o2_bindings_filled(root)
        passed, which = o3_spec_passes(root, wheel)
        vector['o3_spec_structure_ready'] = passed
        vector['o3_spec_file'] = which
        vector['o4_not_self_certified'] = o4_not_self_certified(root)
        vector['o_hop_procedure_reached'] = o_hop(root, arm)
    else:
        vector['o5_no_method_ceremony'] = not find(root, KIT_MARKER)
        vector['o6_flag_works'] = o6_flag_works(root)
        vector['o_hop_procedure_reached'] = o_hop(root, arm)
    print(json.dumps(vector, indent=2))


if __name__ == '__main__':
    main()
