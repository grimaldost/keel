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

`--by-content <git-ref>` is the second strategy, and the one the shipped template's own rows need:
the ledger block calls the backticked snippet OPTIONAL, so the rows an author actually writes carry
no identity for the snippet strategy to repair from — two programmes hit a drifted snippetless
ledger (8 of 35 rows wrong, then 90 of 125) and both wrote the same throwaway difflib script. The
identity those rows do have is the tree they were anchored against: read the line each row cited as
of `<ref>`, find where that content sits now, repoint. It repairs the unbackticked cell the
template emits and the range the snippet strategy cannot, and it refuses the same way — a line
inside a changed or deleted hunk is reported, never guessed at.
"""

import re
import subprocess
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from keel.check_ready import (
    _ANCHOR_RE,
    _LEDGER_ANCHOR_RE,
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


def _committed_lines(base: Path, ref: str, path: str) -> list[str] | None:
    """The file's lines as of `ref`, or None when that ref does not carry it."""
    shown = subprocess.run(
        ['git', '-C', str(base), 'show', f'{ref}:{path}'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        check=False,
    )
    return shown.stdout.splitlines() if shown.returncode == 0 else None


def _line_map(old: list[str], new: list[str]) -> dict[int, int]:
    """Old line number -> new line number, for every line whose content survived unchanged.

    A line inside a changed or deleted hunk is deliberately ABSENT from the map rather than
    approximated: where its content went is not knowable from a diff, and a repair that guesses is
    the failure this verb exists to prevent.
    """
    moved: dict[int, int] = {}
    for tag, i1, i2, j1, _ in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == 'equal':
            moved.update({i1 + step + 1: j1 + step + 1 for step in range(i2 - i1)})
    return moved


@dataclass
class _ContentRemap:
    """Where each cited line went, read from the tree at a git ref instead of from a snippet."""

    base: Path
    ref: str
    _maps: dict[str, tuple[dict[int, int] | None, str]] = field(default_factory=dict)

    def _for(self, path: str) -> tuple[dict[int, int] | None, str]:
        if path not in self._maps:
            target = self.base / path
            old = _committed_lines(self.base, self.ref, path) if target.is_file() else None
            if not target.is_file():
                self._maps[path] = None, 'the file does not resolve'
            elif old is None:
                self._maps[path] = None, f'{self.ref} does not carry that file'
            else:
                now = target.read_text(encoding='utf-8', errors='replace').splitlines()
                self._maps[path] = _line_map(old, now), ''
        return self._maps[path]

    def locate(self, path: str, line: int) -> tuple[int, str]:
        """(the line that content sits on now, '') or (0, why the move cannot be read)."""
        moved, refusal = self._for(path)
        if moved is None:
            return 0, refusal
        return (
            (moved[line], '')
            if line in moved
            else (
                0,
                f'the line it cites was changed or removed since {self.ref}',
            )
        )

    def lines_now(self, path: str) -> list[str]:
        target = self.base / path
        return target.read_text(encoding='utf-8', errors='replace').splitlines()


def _remap_anchor(
    remap: _ContentRemap, path: str, lo: int, hi: int | None, snippet: str | None, line_no: int
) -> Repair | None:
    """What to do with one anchor: a Repair carrying the correction, one carrying the refusal,

    or None when there is nothing to say — the path is not anchor-shaped, or the content it cites
    has not moved.
    """
    anchor = f'{path}:{lo}-{hi}' if hi else f'{path}:{lo}'
    if not _anchor_shaped(path):
        return None
    new_lo, refusal = remap.locate(path, lo)
    new_hi, hi_refusal = remap.locate(path, hi) if hi else (0, '')
    if refusal or hi_refusal:
        return Repair(line_no, anchor, refused=refusal or hi_refusal)
    if (new_lo, new_hi) == (lo, hi or 0):
        return None
    corrected = f'{path}:{new_lo}-{new_hi}' if hi else f'{path}:{new_lo}'
    if snippet is not None:
        window = ' '.join(' '.join(remap.lines_now(path)[new_lo - 1 : new_hi or new_lo]).split())
        if ' '.join(snippet.split()) not in window:
            # The row's two identities already disagreed; moving the coordinate would carry the
            # disagreement forward under a row that looks repaired.
            return Repair(
                line_no, anchor, refused='the snippet does not match the line the content moved to'
            )
    return Repair(line_no, anchor, corrected=corrected)


def _remap_line(line: str, remap: _ContentRemap, line_no: int) -> tuple[str, list[Repair]]:
    """Rewrite one line's anchors from the content they cited at the ref.

    A ledger row is rewritten CELL-WISE, through the gate's own row grammar, so the unbackticked
    confirmation cell the template emits is repairable and a `§N` or a finding id in a neighbouring
    cell is never touched. A prose line (`--body`) keeps the backticked form A6 reads.
    """
    outcomes: list[Repair] = []
    if '|' in line:
        cells = line.split('|')
        for index, cell in enumerate(cells):
            match = _LEDGER_ANCHOR_RE.match(re.sub(r'\*', '', cell).strip())
            if match is None:
                continue
            hi = int(match.group(3)) if match.group(3) else None
            outcome = _remap_anchor(
                remap, match.group(1), int(match.group(2)), hi, match.group(4), line_no
            )
            if outcome is None:
                continue
            outcomes.append(outcome)
            if outcome.corrected:
                cells[index] = cell.replace(outcome.anchor, outcome.corrected, 1)
        return '|'.join(cells), outcomes

    def replace(match: re.Match[str]) -> str:
        outcome = _remap_anchor(
            remap, match.group(1), int(match.group(2)), None, match.group(3), line_no
        )
        if outcome is None:
            return match.group(0)
        outcomes.append(outcome)
        if not outcome.corrected:
            return match.group(0)
        return match.group(0).replace(outcome.anchor, outcome.corrected, 1)

    return _ANCHOR_RE.sub(replace, line), outcomes


def reanchor(
    spec_path: Path, *, body: bool = False, write: bool = True, by_content: str = ''
) -> RepairReport:
    """Repoint drifted anchors — from their snippets, or from the tree at `by_content`."""
    text = _read_spec_text(spec_path, purpose='re-anchor')
    base = _resolve_base(spec_path)
    lines = text.splitlines(keepends=True)
    in_ledger = _in_fold_ledger(lines)
    report = RepairReport(spec=spec_path, body_touched=body)
    remap = _ContentRemap(base, by_content) if by_content else None
    for index, line in enumerate(lines):
        if not (in_ledger[index] or body):
            continue
        # A range anchor carries no repairable coordinate for the snippet strategy: `_ANCHOR_RE`
        # does not match a `lo-hi` token, so a range row is simply never touched by it. That is
        # the intended refusal, and `--by-content` is the strategy that can move both ends.
        repaired, outcomes = (
            _remap_line(line, remap, index + 1)
            if remap is not None
            else _repair_line(line, base, index + 1)
        )
        lines[index] = repaired
        for outcome in outcomes:
            (report.applied if outcome.corrected else report.refused).append(outcome)
    if write and report.applied:
        spec_path.write_text(''.join(lines), encoding='utf-8')
    return report
