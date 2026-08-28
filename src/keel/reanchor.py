"""Rewrite a spec's drifted anchor coordinates from the snippets that identify them.

Nine field reports across two rounds wrote the same throwaway script: find the line carrying each
fold-ledger row's snippet, repoint the row, run the gate again. Three re-anchor cycles in one
session over sixteen rows, one of them producing a malformed row from a slipped `sed`; five cycles
across two specs the next day; twenty-one rows after one section rewrite. The gate already
computes the correction — `_snippet_line` is what W6 reports — so the repair is the computation
applied instead of described.

Two boundaries make the default safe rather than merely convenient:

- **The fold ledger only, unless asked otherwise.** The ledger sits inside the
  `## Pre-mortem certification` span, which `spec_hash` removes, so repairing it cannot invalidate
  the certification it serves. Prose anchors are body content: rewriting one MOVES the hash and
  invalidates the recorded certification, so it takes an explicit flag and says so.
- **A repair is never a guess.** A row is rewritten only when its snippet is strong, resolves on
  exactly one line, and cites a single line rather than a range — a range's snippet could have sat
  anywhere inside the window, so the shift is underdetermined. Everything else is REPORTED by name
  and left alone.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from keel.check_ready import (
    _ANCHOR_RE,
    _anchor_shaped,
    _read_spec_text,
    _resolve_base,
    _snippet_line,
    _strong_snippet,
)

_LEDGER_HEADING_RE = re.compile(r'^#{2,6}[ \t]+')


@dataclass
class Repair:
    """One anchor the pass touched or refused, with the reason it was refused."""

    line_no: int
    anchor: str
    corrected: str = ''
    refused: str = ''


@dataclass
class RepairReport:
    """What a re-anchor pass did, and what it deliberately would not do."""

    spec: Path
    applied: list[Repair] = field(default_factory=list)
    refused: list[Repair] = field(default_factory=list)
    body_touched: bool = False

    @property
    def changed(self) -> bool:
        return bool(self.applied)


def _in_fold_ledger(lines: list[str]) -> list[bool]:
    """Per source line, whether it belongs to the `### Fold ledger` sub-table."""
    inside, flags = False, []
    for line in lines:
        if _LEDGER_HEADING_RE.match(line):
            inside = 'fold ledger' in line.lower()
            flags.append(False)
            continue
        flags.append(inside)
    return flags


def _repair_line(line: str, base: Path, line_no: int) -> tuple[str, list[Repair]]:
    """Rewrite every repairable anchor on one line; return the line and what happened."""
    outcomes: list[Repair] = []

    def replace(match: re.Match[str]) -> str:
        path, claimed, snippet = match.group(1), int(match.group(2)), match.group(3)
        anchor = f'{path}:{claimed}'
        if snippet is None or not _anchor_shaped(path):
            return match.group(0)
        target = base / path
        if not target.is_file():
            outcomes.append(Repair(line_no, anchor, refused='the file does not resolve'))
            return match.group(0)
        if not _strong_snippet(snippet):
            outcomes.append(
                Repair(line_no, anchor, refused='the snippet is too short to repair from')
            )
            return match.group(0)
        lines = target.read_text(encoding='utf-8', errors='replace').splitlines()
        found = _snippet_line(lines, snippet)
        if found is None:
            outcomes.append(
                Repair(line_no, anchor, refused='the snippet is on no line, or on several')
            )
            return match.group(0)
        if found == claimed:
            return match.group(0)
        outcomes.append(Repair(line_no, anchor, corrected=f'{path}:{found}'))
        return match.group(0).replace(f'{path}:{claimed}', f'{path}:{found}', 1)

    return _ANCHOR_RE.sub(replace, line), outcomes


def reanchor(spec_path: Path, *, body: bool = False, write: bool = True) -> RepairReport:
    """Repoint drifted anchors from their snippets; the fold ledger by default."""
    text = _read_spec_text(spec_path, purpose='re-anchor')
    base = _resolve_base(spec_path)
    lines = text.splitlines(keepends=True)
    in_ledger = _in_fold_ledger(lines)
    report = RepairReport(spec=spec_path, body_touched=body)
    for index, line in enumerate(lines):
        if not (in_ledger[index] or body):
            continue
        # A range anchor carries no repairable coordinate: `_ANCHOR_RE` does not match a
        # `lo-hi` token, so a range row is simply never touched. That is the intended refusal.
        repaired, outcomes = _repair_line(line, base, index + 1)
        lines[index] = repaired
        for outcome in outcomes:
            (report.applied if outcome.corrected else report.refused).append(outcome)
    if write and report.applied:
        spec_path.write_text(''.join(lines), encoding='utf-8')
    return report
