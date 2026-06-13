"""Behaviour of the Definition-of-Ready gate (check_spec_ready)."""

import pytest

from keel.check_ready import check_spec_ready

# A well-formed, pre-mortem-certified spec in the spec-template.md shape.
READY_SPEC = """# Spec — widget

- **Status:** ready (DoR passed)

## Numbered sections

### §1 Add the widget module
Introduce `src/widget.py`. **Acceptance criterion:** `src/widget.py` exposes `make()`
and a unit test asserts it returns a Widget instance.

### §2 Wire the widget into the CLI
Expose the widget. **Acceptance criterion:** running `app widget` prints the widget
id and exits zero in an integration test.

## Concept → module map

| Concept | Module / file it lives in |
|---|---|
| widget | `src/widget.py` (to be created) |

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** CERTIFIED
- **Date:** 2026-06-05
- **Failure modes considered & folded in:** none outstanding
"""


def _write(tmp_path, text):
    spec = tmp_path / 'spec.md'
    spec.write_text(text, encoding='utf-8')
    return spec


def test_ready_spec_passes(tmp_path):
    result = check_spec_ready(_write(tmp_path, READY_SPEC))
    assert result.passed, [(v.where, v.message) for v in result.violations]
    assert result.violations == ()


def test_unnumbered_section_fails_a1(tmp_path):
    bad = READY_SPEC.replace(
        '### §2 Wire the widget into the CLI', '### Wire the widget into the CLI'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('number' in v.message.lower() for v in result.violations)


def test_trivial_acceptance_criterion_fails_a2(tmp_path):
    bad = READY_SPEC.replace(
        '**Acceptance criterion:** `src/widget.py` exposes `make()`\nand a unit test '
        'asserts it returns a Widget instance.',
        '**Acceptance criterion:** done.',
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('acceptance criterion' in v.message.lower() for v in result.violations)


def test_placeholder_token_fails_a3(tmp_path):
    bad = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. TODO: finalize.'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('TODO' in v.message for v in result.violations)


def test_uncovered_section_fails_a4(tmp_path):
    bad = READY_SPEC.replace('| PR02 | §2 | yes |\n', '')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('§2' in v.message and 'cover' in v.message.lower() for v in result.violations)


def test_missing_path_fails_a5(tmp_path):
    (tmp_path / '.git').mkdir()  # pin the path-resolution base to tmp_path
    bad = READY_SPEC.replace(
        '| widget | `src/widget.py` (to be created) |', '| widget | `src/ghost.py` |'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('ghost.py' in v.message for v in result.violations)


def test_existing_path_passes_a5(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'real.py').write_text('', encoding='utf-8')
    good = READY_SPEC.replace(
        '| widget | `src/widget.py` (to be created) |', '| widget | `real.py` |'
    )
    good = good.replace('Introduce `src/widget.py`.', 'Introduce `real.py`.')
    good = good.replace('`src/widget.py` exposes', '`real.py` exposes')
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_uncertified_premortem_fails_b1(tmp_path):
    bad = READY_SPEC.replace('- **Verdict:** CERTIFIED', '- **Verdict:** not yet certified')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any(
        'certif' in v.message.lower() or 'pre-mortem' in v.message.lower()
        for v in result.violations
    )


def test_missing_certification_block_fails_b1(tmp_path):
    bad = READY_SPEC.split('## Pre-mortem certification')[0]
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any(
        'certif' in v.message.lower() or 'pre-mortem' in v.message.lower()
        for v in result.violations
    )


def test_missing_spec_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_spec_ready(tmp_path / 'nope.md')


_MOD = 'line one\ndef make():\n    return 1\n'


def test_valid_anchor_resolves_and_passes(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text(_MOD, encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_valid_anchor_with_matching_snippet_passes(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text(_MOD, encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:2` `def make():`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_anchor_missing_file_fails(tmp_path):
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `ghost.py:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('ghost.py' in v.message for v in result.violations)


def test_anchor_line_out_of_range_fails(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('only one line\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:99`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('out of range' in v.message.lower() for v in result.violations)


def test_anchor_snippet_mismatch_fails(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text(_MOD, encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:2` `return 42`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('snippet' in v.message.lower() for v in result.violations)


def _with_adr(tmp_path, existing_name, declared_ref):
    (tmp_path / '.git').mkdir()
    adr = tmp_path / 'docs' / 'adr'
    adr.mkdir(parents=True)
    (adr / existing_name).write_text('# adr\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', f'Introduce `src/widget.py`. Decision: `{declared_ref}`.'
    )
    return check_spec_ready(_write(tmp_path, spec))


def test_adr_number_collision_fails(tmp_path):
    result = _with_adr(tmp_path, '0001-existing-decision.md', 'docs/adr/0001-new-thing.md')
    assert not result.passed
    assert any(
        '0001' in v.message and 'already used' in v.message.lower() for v in result.violations
    )


def test_adr_number_free_passes(tmp_path):
    result = _with_adr(tmp_path, '0001-existing-decision.md', 'docs/adr/0099-new-thing.md')
    assert result.passed, [v.message for v in result.violations]


def test_adr_number_self_reference_passes(tmp_path):
    result = _with_adr(tmp_path, '0007-the-decision.md', 'docs/adr/0007-the-decision.md')
    assert result.passed, [v.message for v in result.violations]


# --- A9: Model-on / Reuse reference resolution ------------------------------


def test_reuse_missing_path_fails_a9(tmp_path):
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.',
        'Introduce `src/widget.py`.\n- **Model-on:** `ghost.py`',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('ghost.py' in v.message for v in result.violations)


def test_reuse_undefined_symbol_fails_a9(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('def make():\n    return 1\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.',
        'Introduce `src/widget.py`.\n- **Reuse:** `mod.py::nope`',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('nope' in v.message for v in result.violations)


def test_reuse_defined_symbol_passes_a9(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('def make():\n    return 1\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.',
        'Introduce `src/widget.py`.\n- **Reuse:** `mod.py::make`',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


# --- A8: intra-spec section-reference resolution ----------------------------


def test_section_ref_dangling_fails_a8(tmp_path):
    bad = READY_SPEC.replace(
        'Expose the widget.', 'Expose the widget. See §9 for the rollback plan.'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('§9' in v.message for v in result.violations)


def test_section_ref_resolves_passes_a8(tmp_path):
    good = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See §1 for context.')
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_section_ref_subdecimal_and_crossdoc_dont_false_fail_a8(tmp_path):
    good = READY_SPEC.replace(
        'Expose the widget.',
        'Expose the widget. Per doctrine §6 and §1.4 the cutover is staged.',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_section_ref_quoted_crossdoc_ignored_a8(tmp_path):
    # a cue word keeps its surrounding punctuation: "doctrine §6" must still be ignored
    good = READY_SPEC.replace(
        'Expose the widget.',
        'Expose the widget. The cross-doc "doctrine §6" reference must be ignored.',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


# --- A10: enforcement-claim honesty lint ------------------------------------

_ENFORCE_TABLE = """
## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| boundary-rule | review-only | reviewer judgment |
"""


def test_enforcement_overclaim_fails_a10(tmp_path):
    bad = READY_SPEC + _ENFORCE_TABLE + '\nThe boundary-rule is enforced at every commit.\n'
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('boundary-rule' in v.message for v in result.violations)


def test_enforcement_honest_prose_passes_a10(tmp_path):
    good = (
        READY_SPEC
        + _ENFORCE_TABLE
        + '\nThe boundary-rule is NOT enforced yet; the `enforced` token is fine.\n'
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_enforcement_no_table_dozes_a10(tmp_path):
    good = READY_SPEC + '\nThe boundary-rule is enforced at every commit.\n'
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


# --- A11: anchor-range closes-structure -------------------------------------

# a 5-line set literal: the brace opens on line 1 and closes on line 5.
_LITERAL = 'ALLOWED = {\n    "a",\n    "b",\n    "c",\n}\n'


def test_anchor_range_unclosed_fails_a11(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'lit.py').write_text(_LITERAL, encoding='utf-8')
    spec = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See `lit.py:1-3` for it.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('1-3' in v.message and 'close' in v.message.lower() for v in result.violations)


def test_anchor_range_balanced_passes_a11(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'lit.py').write_text(_LITERAL, encoding='utf-8')
    spec = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See `lit.py:1-5` for it.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_anchor_range_bracket_in_string_or_comment_passes_a11(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 's.py').write_text('label = "a ] b"\nz = 10  # ) not real\n', encoding='utf-8')
    spec = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See `s.py:1-2` here.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_single_line_anchor_untouched_by_a11(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'lit.py').write_text(_LITERAL, encoding='utf-8')
    spec = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See `lit.py:1` here.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


# --- A12: fold-ledger anchor-resolution -------------------------------------


def _ledger(rows: str) -> str:
    return (
        '\n\n### Fold ledger\n\n'
        '| Finding | Target | artifact:line | Confirmed |\n'
        '|---|---|---|---|\n' + rows
    )


def test_fold_ledger_blank_anchor_fails_a12(tmp_path):
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC + _ledger('| FM-1 | §1 |  | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('ledger' in v.message.lower() for v in result.violations)


def test_fold_ledger_bad_anchor_fails_a12(tmp_path):
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `ghost.py:5` | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('ghost.py' in v.message for v in result.violations)


def test_fold_ledger_resolves_passes_a12(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('line one\nline two\n', encoding='utf-8')
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `mod.py:2` | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_no_fold_ledger_dozes_a12(tmp_path):
    result = check_spec_ready(_write(tmp_path, READY_SPEC))
    assert result.passed, [v.message for v in result.violations]


def test_anchor_range_non_code_file_passes_a11(tmp_path):
    # A11's bracket-balance is Python-only; a range into prose with a stray { must not fire.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'doc.md').write_text(
        'Use {placeholder and ${VAR}\nmore prose here\n', encoding='utf-8'
    )
    spec = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See `doc.md:1-2` here.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


_MULTILINE_STR = 's = """\n[ a bracket inside a multi-line string\n"""\nx = 1\n'


def test_anchor_range_multiline_string_passes_a11(tmp_path):
    # a [ inside a triple-quoted string spanning the range must not count as unclosed.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'ml.py').write_text(_MULTILINE_STR, encoding='utf-8')
    spec = READY_SPEC.replace('Expose the widget.', 'Expose the widget. See `ml.py:1-4` now.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_fold_ledger_header_word_in_data_cell_still_fails_a12(tmp_path):
    # the header skip is positional, so a data row whose cell is the word "artifact" still fires.
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC + _ledger('| FM-1 | §1 | artifact | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('ledger' in v.message.lower() for v in result.violations)


# --- R1: a claimed fold must carry a ledger ---------------------------------


def test_fold_claimed_without_ledger_fails_r1(tmp_path):
    # a CERTIFIED spec whose "folded in" field claims a fold but has no ledger fails (R1).
    bad = READY_SPEC.replace(
        '- **Failure modes considered & folded in:** none outstanding',
        '- **Failure modes considered & folded in:** 3 findings folded (1 BLOCKER, 2 MINOR).',
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('ledger' in v.message.lower() for v in result.violations)


def test_fold_claimed_with_resolving_ledger_passes_r1(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('a\nb\n', encoding='utf-8')
    good = READY_SPEC.replace(
        '- **Failure modes considered & folded in:** none outstanding',
        '- **Failure modes considered & folded in:** 1 finding folded.',
    ) + _ledger('| FM-1 | §1 | `mod.py:2` | yes |\n')
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_clean_certify_dozes_r1(tmp_path):
    # "none outstanding" claims no fold, so no ledger is required (clean certs do not retro-break).
    result = check_spec_ready(_write(tmp_path, READY_SPEC))
    assert result.passed, [v.message for v in result.violations]
