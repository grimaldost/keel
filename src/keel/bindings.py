"""Method-bindings completeness gate: is every portability slot bound to something concrete?

Deferred by ADR-0003 "until a real failure demands it", and deferral was the live state for
fourteen releases. Two field failures now meet that condition, and both are the same shape — the
binding sheet answers when asked and never fires:

- a phase with a clear blast radius (six-plus planned PRs across three repositories, shared
  contracts) was specified in four hand-written documents with no Definition-of-Ready and no
  pre-mortem, and nothing accused: not doctrine's trigger, which exists only as prose to be
  remembered, and not the bindings sheet, which lived in a fourth repository and is read by no
  mechanism at phase start;
- the executor was left to session judgement, and the session resolved it by whatever was already
  in context.

What the gate reads, and why it is not a positional rule: the two sheets that exist are three-,
four- and two-column, and one of the template's tables carried only the WORKED EXAMPLE. A
last-column rule reads those examples as bindings — a permanent false negative — and a
first-column rule reads slot names. So the binding column is resolved by HEADER: the column headed
`This project` when the table has one, else the last column, which is the right answer for a sheet
that carries no example column at all.

Three states, not two. An empty cell is unbound and fails. A cell that opens `not bound` with a
reason is the *declared* state ADR-0003 sanctions — deferral named rather than faked — and warns.
Anything else is bound.

Findings here carry no check letter, deliberately. `CHECK_IDS` is the SPEC gate's closed catalogue:
it is what the Part-A reference block enumerates, what the hit-rate ledger counts, and what the
adversarial corpus stages a positive control for — and that corpus stages specs, so a bindings
letter could never earn one. The identity problem those letters solved does not arise here either:
this gate's `where` IS the slot name, and slot names do not collide. `Violation.check` defaults to
empty for exactly this case (ADR-0018).
"""

import re
from pathlib import Path

from keel.errors import format_error
from keel.models import GateResult, Violation, Warning

_PROJECT_HEADER_RE = re.compile(r'^\**\s*this project\s*\**$', re.IGNORECASE)
_NOT_BOUND_RE = re.compile(r'^not\s+bound\b[\s—:-]*(.*)$', re.IGNORECASE | re.DOTALL)

_UNBOUND = (
    'this slot is unbound — the method is bound to a project by naming a concrete mechanism for '
    'every slot. Write the mechanism, or write `not bound — <reason>`, which is a recorded '
    'decision rather than a gap.'
)
_NO_REASON = (
    '`not bound` with no reason is a gap with a label on it — name what the project does instead, '
    'or what would have to change to bind it.'
)


def _tables(text: str) -> list[list[list[str]]]:
    """Every markdown table in the sheet, as rows of cells (header separators dropped)."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith('|'):
            if current:
                tables.append(current)
                current = []
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if all(set(cell) <= set('-: ') for cell in cells):
            continue
        current.append(cells)
    if current:
        tables.append(current)
    return [table for table in tables if len(table) > 1 and len(table[0]) >= 2]


def _binding_column(header: list[str]) -> int:
    """Which column holds THIS project's binding — by header, never by position."""
    for index, cell in enumerate(header):
        if _PROJECT_HEADER_RE.match(re.sub(r'`', '', cell).strip()):
            return index
    return len(header) - 1


def _slot_name(cells: list[str]) -> str:
    """The row's slot, read from its first non-empty cell so a leading blank column is harmless."""
    for cell in cells:
        if name := re.sub(r'[`*]', '', cell).strip():
            return name
    return '(unnamed slot)'


def check_bindings(bindings_path: Path) -> GateResult:
    """Assert every portability slot in a method-bindings sheet is bound to a concrete mechanism."""
    if not bindings_path.is_file():
        raise FileNotFoundError(
            format_error(
                what=f'No bindings sheet at {bindings_path}.',
                why='`keel bind-check` reads a filled `method-bindings.md`; there is nothing to '
                'check without one.',
                fix='Run `keel init <dir>` to copy the kit, fill `method-bindings.md`, and point '
                'this command at it.',
            )
        )
    text = bindings_path.read_text(encoding='utf-8', errors='replace')
    violations: list[Violation] = []
    warnings: list[Warning] = []
    for table in _tables(text):
        header, rows = table[0], table[1:]
        column = _binding_column(header)
        for cells in rows:
            if len(cells) <= column:
                continue
            slot = _slot_name(cells)
            binding = re.sub(r'[`*]', '', cells[column]).strip()
            declared = _NOT_BOUND_RE.match(binding)
            reason = declared.group(1).strip(' .:—-') if declared is not None else ''
            if not binding:
                violations.append(Violation(slot, _UNBOUND))
            elif declared is not None and not reason:
                violations.append(Violation(slot, _NO_REASON))
            elif declared is not None:
                warnings.append(
                    Warning(
                        '',
                        f'WARN: {slot} is deliberately unbound — {reason}. Recorded, not missing; '
                        'the method runs partially applied here.',
                    )
                )
    return GateResult(passed=not violations, violations=tuple(violations), warnings=tuple(warnings))
