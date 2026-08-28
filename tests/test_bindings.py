"""`keel bind-check`: is every portability slot bound to something concrete? (ADR-0018)

Two properties carry this gate, and both are inversions the pre-mortem caught before any code:

- The binding column is resolved by HEADER. A last-column rule reads the shipped template's worked
  examples as bindings — a permanent false negative on the one table that carries no project
  column — and a first-column rule reads slot names. The sheets that exist are three-, four- and
  two-column, so position proves nothing.
- There are three states. `not bound — <reason>` is the declared idiom this repo's own sheet uses
  for three slots and its closing line describes; an emptiness-only predicate would fail the blank
  scaffold and PASS the one real record with three admittedly unbound slots — the exact inverse of
  what the gate is for.
"""

import pytest

from keel.bindings import check_bindings
from keel.templates import templates_root

THREE_COLUMN = """# Method bindings — acme

| Slot | `acme` binding (example) | This project |
|---|---|---|
| **ADR home** | `docs/adr/` | {adr} |
| **Spec format** | a committed spec | {spec} |
"""

TWO_COLUMN = """# Method bindings — keel

| Slot | keel's binding |
|---|---|
| **ADR home** | `docs/adr/` |
| **Wave budget** | {budget} |
"""


def _write(tmp_path, text):
    path = tmp_path / 'method-bindings.md'
    path.write_text(text, encoding='utf-8')
    return path


def test_a_filled_sheet_passes(tmp_path):
    sheet = _write(tmp_path, THREE_COLUMN.format(adr='`docs/decisions/`', spec='`docs/spec.md`'))
    assert check_bindings(sheet).passed


def test_an_empty_binding_fails_and_names_the_slot(tmp_path):
    sheet = _write(tmp_path, THREE_COLUMN.format(adr='`docs/decisions/`', spec=''))
    result = check_bindings(sheet)
    assert not result.passed
    assert [v.where for v in result.violations] == ['Spec format']


def test_the_example_column_is_not_read_as_a_binding(tmp_path):
    # The inversion: with a `This project` header present, a last-column rule would be right by
    # accident here and wrong on the table that has no project column at all. This pins that the
    # example column is never what the gate reads.
    sheet = _write(tmp_path, THREE_COLUMN.format(adr='', spec=''))
    result = check_bindings(sheet)
    assert {v.where for v in result.violations} == {'ADR home', 'Spec format'}


def test_a_two_column_sheet_reads_its_only_value_column(tmp_path):
    # keel's own record has no example column; its last column IS the binding.
    sheet = _write(tmp_path, TWO_COLUMN.format(budget='a `[budget]` block'))
    assert check_bindings(sheet).passed


def test_a_declared_deferral_warns_rather_than_fails(tmp_path):
    sheet = _write(tmp_path, TWO_COLUMN.format(budget='not bound — waves run in-session'))
    result = check_bindings(sheet)
    assert result.passed
    assert result.warnings and 'deliberately unbound' in result.warnings[0].message


def test_a_deferral_with_no_reason_still_fails(tmp_path):
    sheet = _write(tmp_path, TWO_COLUMN.format(budget='not bound'))
    result = check_bindings(sheet)
    assert not result.passed
    assert 'a label on it' in result.violations[0].message


def test_the_shipped_template_is_unbound_by_design(tmp_path):
    # The scaffold is blank on purpose; it is the fixture, not the target.
    result = check_bindings(templates_root() / 'method-bindings.md')
    assert not result.passed
    assert len(result.violations) >= 10


def test_keels_own_record_passes_with_its_three_declared_deferrals():
    # The sheet whose closing line says three slots are consciously unbound. An emptiness-only
    # predicate would have passed this file silently; this asserts the third state instead.
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    result = check_bindings(root / 'docs' / 'method-bindings.md')
    assert result.passed, [(v.where, v.message) for v in result.violations]
    assert len(result.warnings) == 3


def test_a_missing_sheet_is_not_runnable(tmp_path):
    with pytest.raises(FileNotFoundError) as exc:
        check_bindings(tmp_path / 'nope.md')
    assert 'Fix:' in str(exc.value)


def test_findings_carry_no_check_letter(tmp_path):
    # ADR-0018 decision 3: CHECK_IDS is the SPEC gate's catalogue, and the corpus that would have
    # to control a new letter stages specs.
    sheet = _write(tmp_path, THREE_COLUMN.format(adr='', spec=''))
    result = check_bindings(sheet)
    assert all(v.check == '' for v in result.violations)
