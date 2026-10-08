"""Doctrine/bindings currency guard: the Route & Budget row names a role, not a dead tool.

Per ADR-0003, the doctrine names ROLES; specific tools are reference bindings, bound per
project in `method-bindings.md`. The mechanism map's Route & Budget row still pointed at two
skills that exist nowhere, orphaned when the series orchestrator was replaced by convoy. This
guard pins the fix: the doctrine row is role-generic, the concrete tool
appears only as an 'e.g.' in the bindings sheet, and keel-on-keel answers the new slot (the
kit's own rule: a slot left unbound is a method-not-fully-applied warning).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def test_the_route_and_budget_row_names_a_role_not_a_tool():
    # The row once named two skills that exist nowhere. Pinning the row's own cells holds the fix
    # without the test carrying the dead names: the System cell is the role, and the reference
    # cell defers to the bindings sheet, where a tool appears only as an 'e.g.'.
    doctrine = _read('docs/doctrine.md')
    row = next(
        (line for line in doctrine.splitlines() if line.startswith('| Route & Budget |')), ''
    )
    assert row, 'the mechanism map lost its Route & Budget row'
    cells = [cell.strip() for cell in row.strip().strip('|').split('|')]
    assert cells[1] == 'capacity-dispatch policy', cells
    assert '`method-bindings.md`' in cells[2], cells


def test_capacity_dispatch_is_bound_role_generically():
    # ADR-0003 shape: doctrine states the ROLE role-generically; the concrete tool name lives in
    # the bindings sheet, and only as an 'e.g.'.
    assert 'capacity-dispatch' in _read('docs/doctrine.md'), (
        'doctrine does not name the capacity-dispatch role'
    )
    bindings = _read('src/keel/templates/method-bindings.md')
    # Scope the check to the Capacity dispatch row itself: 'e.g.' occurs on unrelated
    # rows (Series runner, Single-unit discipline) on origin/main, so a whole-file
    # substring check would pass even if this row named its tool without the hedge.
    dispatch_row = next((line for line in bindings.splitlines() if 'Capacity dispatch' in line), '')
    assert dispatch_row, 'template method-bindings.md lacks the Capacity dispatch slot'
    assert 'e.g.' in dispatch_row, (
        'the Capacity dispatch row names a concrete tool but not as an e.g.'
    )


def test_keel_answers_the_capacity_dispatch_slot():
    # The kit's own rule: a slot left unbound is a method-not-fully-applied warning. keel-on-keel
    # must answer the new template slot — 'not bound' is a valid, honest answer.
    assert 'Capacity dispatch' in _read('docs/method-bindings.md'), (
        'keel-on-keel bindings do not answer the Capacity dispatch slot'
    )
