"""Behaviour of the Definition-of-Ready gate (check_spec_ready)."""

import pytest

from keel.check_ready import check_spec_ready, spec_hash

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


def test_wrapped_acceptance_marker_is_found_a2(tmp_path):
    # §1: the **Acceptance criterion:** marker hard-wrapped across a newline must still be found.
    spec = READY_SPEC.replace(
        '**Acceptance criterion:** `src/widget.py` exposes `make()`',
        '**Acceptance\ncriterion:** `src/widget.py` exposes `make()`',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_wrapped_marker_counts_criterion_after_newline_a2(tmp_path):
    # FM-6: marker wrapped across a newline; the >=5-word criterion that follows is still counted.
    spec = READY_SPEC.replace(
        '**Acceptance criterion:** `src/widget.py` exposes `make()`\nand a unit test '
        'asserts it returns a Widget instance.',
        '**Acceptance\ncriterion:** the module exposes make and a unit test asserts a Widget.',
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_missing_acceptance_marker_still_fails_a2(tmp_path):
    # widening to \\s+ must not pass a section that has no acceptance marker at all.
    bad = READY_SPEC.replace(
        '**Acceptance criterion:** `src/widget.py` exposes `make()`\nand a unit test '
        'asserts it returns a Widget instance.',
        'The module is added.',
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


def test_verdict_certified_with_trailing_prose_passes_b1(tmp_path):
    # §2: a bare leading CERTIFIED token followed by prose is accepted.
    good = READY_SPEC.replace(
        '- **Verdict:** CERTIFIED',
        '- **Verdict:** CERTIFIED. All round-1 blockers addressed.',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_verdict_non_leading_or_compound_fails_b1(tmp_path):
    # §2: a hyphenated compound or a non-leading token must NOT pass (no new hole).
    # CONDITIONAL-CERTIFY is here because READY_SPEC carries NO `Operator:` field — without an
    # operator it is not recordable and still fails B1 (the 0.7.0 widen accepts it ONLY with one;
    # the positive path is test_conditional_certify_with_operator_passes_b1 below).
    for bad_verdict in ('CERTIFIED-NOT', 'CERTIFIEDISH', 'CONDITIONAL-CERTIFY', 'NEEDS-REVISION'):
        bad = READY_SPEC.replace('- **Verdict:** CERTIFIED', f'- **Verdict:** {bad_verdict}')
        result = check_spec_ready(_write(tmp_path, bad))
        assert not result.passed, bad_verdict
        assert any('certif' in v.message.lower() for v in result.violations), bad_verdict


def test_conditional_certify_with_operator_passes_b1(tmp_path):
    # §2 / T1b: CONDITIONAL-CERTIFY + a named Operator passes B1 (operator-accepted), with a WARN.
    good = READY_SPEC.replace(
        '- **Verdict:** CERTIFIED',
        '- **Verdict:** CONDITIONAL-CERTIFY — ready modulo a named fix\n- **Operator:** grimaldo',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]
    assert any('grimaldo' in w for w in result.warnings)


def test_conditional_certify_without_operator_fails_b1(tmp_path):
    # §2 / T1b: CONDITIONAL-CERTIFY with no Operator is not recordable — fails, names the contract.
    bad = READY_SPEC.replace(
        '- **Verdict:** CERTIFIED', '- **Verdict:** CONDITIONAL-CERTIFY — ready modulo a named fix'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('operator' in v.message.lower() for v in result.violations)


def test_clean_certified_emits_only_the_b2_adoption_warn(tmp_path):
    # 0.12.0 §1: a plain CERTIFIED with no artifact reference passes; the single delta vs 0.11.1
    # is the B2 adoption WARN (verify-when-present nudge) — no other warning.
    result = check_spec_ready(_write(tmp_path, READY_SPEC))
    assert result.passed
    assert len(result.warnings) == 1
    assert 'artifact' in result.warnings[0].lower()


def test_b1_error_states_bare_token_contract(tmp_path):
    # §2: the B1 error names the bare-token contract (mentions both "token" and "certified").
    bad = READY_SPEC.replace('- **Verdict:** CERTIFIED', '- **Verdict:** not yet certified')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any(
        'token' in v.message.lower() and 'certified' in v.message.lower() for v in result.violations
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


def test_dotfile_anchor_resolves_passes_a6(tmp_path):
    # A dotfile anchor (leading dot, no extension) is path-like and must resolve like any path.
    (tmp_path / '.git').mkdir()
    (tmp_path / '.gitignore').write_text('first\nsecond\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `.gitignore:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_dotfile_anchor_out_of_range_fails_a6(tmp_path):
    # ... and it is genuinely RESOLVED, not silently ignored: an out-of-range line still fires.
    (tmp_path / '.git').mkdir()
    (tmp_path / '.gitignore').write_text('only one line\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `.gitignore:99`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('out of range' in v.message.lower() for v in result.violations)


def test_bare_colon_number_is_not_an_anchor_a6(tmp_path):
    # The false-positive guard holds: a backticked `N:M` with no dot/slash is not a path anchor.
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. A `3:4` ratio at `9:30`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


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


def test_fold_ledger_dotfile_anchor_resolves_passes_a12(tmp_path):
    # The 0.10.0 self-build friction: a fold-ledger anchor to a dotfile (`.gitignore:N`) was
    # rejected as "no resolving anchor" because the parser required a name.ext shape.
    (tmp_path / '.git').mkdir()
    (tmp_path / '.gitignore').write_text('line one\nline two\n', encoding='utf-8')
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `.gitignore:2` | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_no_fold_ledger_dozes_a12(tmp_path):
    result = check_spec_ready(_write(tmp_path, READY_SPEC))
    assert result.passed, [v.message for v in result.violations]


def test_fold_ledger_snippet_matches_passes_a12(tmp_path):
    # 0.12.0 §8: an optional backticked snippet after the anchor is verified against the line.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('line one\nline two\n', encoding='utf-8')
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `mod.py:2` `line two` | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_fold_ledger_snippet_mismatch_fails_a12(tmp_path):
    # 0.12.0 §8: in-range drift becomes detectable — a stale snippet fires, a bare anchor cannot.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('line one\nline two\n', encoding='utf-8')
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `mod.py:2` `moved text` | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('snippet' in v.message.lower() for v in result.violations)


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


def test_fold_ledger_error_teaches_path_line_format_a12(tmp_path):
    # §5(b) / T4b: the A12 error teaches the accepted format with a concrete path:line example.
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC + _ledger('| FM-1 | §1 |  | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    msg = ' '.join(v.message for v in result.violations)
    assert 'e.g.' in msg.lower() and ':' in msg


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


# --- §4/U3b: first-table-only fold-ledger parse -----------------------------


def test_fold_ledger_ignores_sibling_table_in_subsection_a12(tmp_path):
    # §4/U3b: a 4-col sibling table AFTER the ledger in the same `### Fold ledger` subsection must
    # NOT be parsed as ledger rows. The OLD whole-span sweep read its cells (3rd col not an
    # artifact:line) and failed A12; first-table-only reads only the ledger.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('a\nb\n', encoding='utf-8')
    sibling = (
        '\n| Finding | Round | Disposition | Note |\n'
        '|---|---|---|---|\n'
        '| FM-9 | R1 | rejected | out of scope |\n'
    )
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `mod.py:2` | yes |\n') + sibling
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_fold_ledger_stops_at_prose_before_sibling_table_a12(tmp_path):
    # §4/U3b: a prose line ends the ledger table; a later table is not parsed as ledger rows.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('a\nb\n', encoding='utf-8')
    trailer = (
        '\nRound-1 dispositions (historical):\n\n'
        '| Finding | Round | Disposition | Note |\n'
        '|---|---|---|---|\n'
        '| FM-9 | R1 | rejected | out of scope |\n'
    )
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `mod.py:2` | yes |\n') + trailer
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_fold_ledger_header_only_dozes_a12(tmp_path):
    # §4/U3b: a `### Fold ledger` with a header row but no data rows dozes (clean certify).
    spec = (
        READY_SPEC
        + '\n\n### Fold ledger\n\n'
        + '| Finding | Target | artifact:line | Confirmed |\n|---|---|---|---|\n'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


# --- §4/U3a + U3c: error-string teaching ------------------------------------


def test_absent_sections_error_names_parent_and_child_a1(tmp_path):
    # §4/U3a: the absent-sections error names the `## Numbered sections` parent AND the `### §N`
    # child shape, and keeps its leading "no " token (the CLI template pointer depends on it).
    bad = '# Spec — empty\n\nNo numbered sections here.\n'
    result = check_spec_ready(_write(tmp_path, bad))
    nv = [v for v in result.violations if v.where == 'Numbered sections']
    assert nv, [v.where for v in result.violations]
    assert nv[0].message.startswith('no ')
    assert '## Numbered sections' in nv[0].message and '### §' in nv[0].message


def test_anchor_error_teaches_repo_root_relative_a6(tmp_path):
    # §4/U3c: the A6 anchor error teaches the repo-root-relative rule.
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `ghost.py:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    nv = [v for v in result.violations if 'ghost.py' in v.message]
    assert nv and 'repo-root-relative' in nv[0].message.lower()


def test_concept_to_be_created_error_teaches_body_mention_a5(tmp_path):
    # §4/U3c: the A5 'to be created' error teaches the path must also appear in a section body.
    (tmp_path / '.git').mkdir()
    bad = READY_SPEC.replace(
        '| widget | `src/widget.py` (to be created) |',
        '| widget | `src/ghost.py` (to be created) |',
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    nv = [v for v in result.violations if 'ghost.py' in v.message]
    assert nv and 'body' in nv[0].message.lower()


# --- §4 (0.12.0): unique-basename resolution --------------------------------


def test_anchor_unique_basename_gets_did_you_mean_a6(tmp_path):
    (tmp_path / '.git').mkdir()
    pkg = tmp_path / 'src' / 'pkg'
    pkg.mkdir(parents=True)
    (pkg / 'mod.py').write_text('one\ntwo\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    hinted = [v for v in result.violations if 'mod.py' in v.message]
    assert hinted and 'did you mean' in hinted[0].message
    assert 'src/pkg/mod.py:2' in hinted[0].message


def test_anchor_ambiguous_basename_no_hint_a6(tmp_path):
    (tmp_path / '.git').mkdir()
    for sub in ('a', 'b'):
        d = tmp_path / sub
        d.mkdir()
        (d / 'mod.py').write_text('one\ntwo\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    hinted = [v for v in result.violations if 'mod.py' in v.message]
    assert hinted and 'did you mean' not in hinted[0].message


def test_anchor_vendor_tree_excluded_from_uniqueness_a6(tmp_path):
    # FM-12: a .venv copy must not defeat exactly-one; the hint points at the real file.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'mod.py').write_text('one\ntwo\n', encoding='utf-8')
    venv = tmp_path / '.venv' / 'lib'
    venv.mkdir(parents=True)
    (venv / 'mod.py').write_text('one\ntwo\n', encoding='utf-8')
    spec = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. See `mod.py:2`.'
    )
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    hinted = [v for v in result.violations if 'did you mean' in v.message]
    assert hinted and 'src/mod.py:2' in hinted[0].message


def test_fold_ledger_bare_basename_gets_did_you_mean_a12(tmp_path):
    (tmp_path / '.git').mkdir()
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'mod.py').write_text('one\ntwo\n', encoding='utf-8')
    spec = READY_SPEC + _ledger('| FM-1 | §1 | `mod.py:2` | yes |\n')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    hinted = [v for v in result.violations if 'did you mean' in v.message]
    assert hinted, [v.message for v in result.violations]


def test_to_be_created_basename_claim_passes_a5(tmp_path):
    # A body naming the file by its unique basename claims the map's full path (0.12.0 §4).
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        '| widget | `src/widget.py` (to be created) |',
        '| widget | `src/pkg/server.py` (to be created) |',
    ).replace('Introduce `src/widget.py`.', 'Introduce `server.py` as the entry module.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert result.passed, [v.message for v in result.violations]


def test_to_be_created_ambiguous_basename_still_fails_a5(tmp_path):
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        '| widget | `src/widget.py` (to be created) |',
        '| widget | `a/server.py` (to be created) |\n| gadget | `b/server.py` (to be created) |',
    ).replace('Introduce `src/widget.py`.', 'Introduce `server.py` as the entry module.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert sum('server.py' in v.message for v in result.violations) == 2


def test_to_be_created_basename_substring_does_not_claim_a5(tmp_path):
    # `server.py` inside `myserver.py` is not a claim of server.py.
    (tmp_path / '.git').mkdir()
    spec = READY_SPEC.replace(
        '| widget | `src/widget.py` (to be created) |',
        '| widget | `src/pkg/server.py` (to be created) |',
    ).replace('Introduce `src/widget.py`.', 'Introduce `myserver.py` here.')
    result = check_spec_ready(_write(tmp_path, spec))
    assert not result.passed
    assert any('server.py' in v.message for v in result.violations)


# --- B2: certification artifact + canonical spec hash (0.12.0 §1) ------------


def _with_artifact_field(ref: str) -> str:
    return READY_SPEC.replace(
        '- **Reviewer:** review-panel (non-author)',
        f'- **Reviewer:** review-panel (non-author)\n- **Certification artifact:** {ref}',
    )


def _artifact_text(verdict_line: str, hash_value: str = '') -> str:
    hash_line = f'- **Spec-hash:** {hash_value}\n' if hash_value else ''
    return (
        '# Pre-mortem artifact — widget\n\n'
        '- **Spec:** spec.md\n'
        '- **Reviewer:** review-panel (non-author)\n'
        f'{hash_line}\n'
        'Findings prose here.\n\n'
        f'{verdict_line}\n'
    )


def test_absent_artifact_field_warns_b2(tmp_path):
    result = check_spec_ready(_write(tmp_path, READY_SPEC))
    assert result.passed
    assert any('artifact' in w.lower() for w in result.warnings)


def test_empty_artifact_field_is_absent_b2(tmp_path):
    # FM-22: the template ships the field empty-valued; empty ≡ absent (WARN, no violation).
    result = check_spec_ready(_write(tmp_path, _with_artifact_field('').rstrip() + '\n'))
    assert result.passed, [v.message for v in result.violations]
    assert any('artifact' in w.lower() for w in result.warnings)


def test_artifact_missing_file_fails_b2(tmp_path):
    result = check_spec_ready(_write(tmp_path, _with_artifact_field('ghost.premortem.md')))
    assert not result.passed
    assert any('ghost.premortem.md' in v.message for v in result.violations)


def test_artifact_without_verdict_line_fails_b2(tmp_path):
    (tmp_path / 'premortem.md').write_text('# artifact\n\nno verdict here\n', encoding='utf-8')
    result = check_spec_ready(_write(tmp_path, _with_artifact_field('premortem.md')))
    assert not result.passed
    assert any('PREMORTEM-VERDICT' in v.message for v in result.violations)


def test_artifact_verdict_mismatch_fails_b2(tmp_path):
    (tmp_path / 'premortem.md').write_text(
        _artifact_text('PREMORTEM-VERDICT: NEEDS-REVISION'), encoding='utf-8'
    )
    result = check_spec_ready(_write(tmp_path, _with_artifact_field('premortem.md')))
    assert not result.passed
    assert any('disagrees' in v.message.lower() for v in result.violations)


def test_artifact_matching_hash_and_verdict_passes_clean_b2(tmp_path):
    spec = _write(tmp_path, _with_artifact_field('premortem.md'))
    (tmp_path / 'premortem.md').write_text(
        _artifact_text('PREMORTEM-VERDICT: CERTIFIED', spec_hash(spec)), encoding='utf-8'
    )
    result = check_spec_ready(spec)
    assert result.passed, [v.message for v in result.violations]
    assert result.warnings == ()


def test_artifact_hash_mismatch_warns_b2(tmp_path):
    spec = _write(tmp_path, _with_artifact_field('premortem.md'))
    (tmp_path / 'premortem.md').write_text(
        _artifact_text('PREMORTEM-VERDICT: CERTIFIED', 'deadbeef' * 8), encoding='utf-8'
    )
    result = check_spec_ready(spec)
    assert result.passed, [v.message for v in result.violations]
    assert any('earlier revision' in w.lower() for w in result.warnings)


def test_artifact_identity_suffixed_verdict_passes_b2(tmp_path):
    # FM-16 seventh case: §2's identity suffix after the token is inert trailing text.
    spec = _write(tmp_path, _with_artifact_field('premortem.md'))
    (tmp_path / 'premortem.md').write_text(
        _artifact_text('PREMORTEM-VERDICT: CERTIFIED — pre-mortem-review@0.12.0', spec_hash(spec)),
        encoding='utf-8',
    )
    result = check_spec_ready(spec)
    assert result.passed, [v.message for v in result.violations]
    assert result.warnings == ()


def test_artifact_column_zero_schema_quote_does_not_shadow_b2(tmp_path):
    # FM-8: B2 reads the LAST line-anchored verdict line; a column-0 schema quote above it is inert.
    spec = _write(tmp_path, _with_artifact_field('premortem.md'))
    body = _artifact_text('PREMORTEM-VERDICT: CERTIFIED', spec_hash(spec)).replace(
        'Findings prose here.',
        'Findings prose here.\nPREMORTEM-VERDICT: <CERTIFIED | CONDITIONAL-CERTIFY | '
        'NEEDS-REVISION> is the contract line.',
    )
    (tmp_path / 'premortem.md').write_text(body, encoding='utf-8')
    result = check_spec_ready(spec)
    assert result.passed, [v.message for v in result.violations]


def test_kit_stamp_minor_skew_warns_even_structure_only(tmp_path):
    # 0.12.0 §9: a spec stamped from an older kit self-announces — and the author loop
    # (--structure-only) is where skew bites first, so the WARN reaches it.
    spec = READY_SPEC + '\n<!-- keel kit 0.10.0 -->\n'
    result = check_spec_ready(_write(tmp_path, spec), structure_only=True)
    assert result.passed, [v.message for v in result.violations]
    assert any('kit' in w.lower() for w in result.warnings)


def test_kit_stamp_current_version_is_silent(tmp_path):
    from keel import __version__

    spec = READY_SPEC + f'\n<!-- keel kit {__version__} -->\n'
    result = check_spec_ready(_write(tmp_path, spec), structure_only=True)
    assert result.passed
    assert not any('kit' in w.lower() for w in result.warnings)


def test_no_kit_stamp_is_silent(tmp_path):
    # Every pre-0.12.0 spec lacks the stamp; absence stays quiet (verify-when-present).
    result = check_spec_ready(_write(tmp_path, READY_SPEC), structure_only=True)
    assert result.passed
    assert result.warnings == ()


def test_structure_only_skips_b2(tmp_path):
    result = check_spec_ready(
        _write(tmp_path, _with_artifact_field('ghost.premortem.md')), structure_only=True
    )
    assert result.passed, [v.message for v in result.violations]
    assert result.warnings == ()


def test_spec_hash_stable_across_cert_block_growth(tmp_path):
    # FM-1: appending ledger rows CHANGES the cert section's line count; the hash must not move.
    before = spec_hash(_write(tmp_path, READY_SPEC))
    grown = READY_SPEC + (
        '\n### Fold ledger\n\n'
        '| Finding | Target | artifact:line | Confirmed |\n'
        '|---|---|---|---|\n'
        '| FM-1 | §1 | `spec.md:1` | yes |\n'
        '| FM-2 | §2 | `spec.md:1` | yes |\n'
    )
    after = spec_hash(_write(tmp_path, grown))
    assert before == after


def test_spec_hash_changes_on_body_edit(tmp_path):
    before = spec_hash(_write(tmp_path, READY_SPEC))
    after = spec_hash(_write(tmp_path, READY_SPEC.replace('Introduce', 'Rework')))
    assert before != after


def test_spec_hash_indifferent_to_crlf(tmp_path):
    lf = spec_hash(_write(tmp_path, READY_SPEC))
    crlf_spec = tmp_path / 'crlf.md'
    crlf_spec.write_bytes(READY_SPEC.replace('\n', '\r\n').encode('utf-8'))
    assert spec_hash(crlf_spec) == lf


def test_spec_hash_fenced_cert_heading_does_not_shift_span(tmp_path):
    # A fenced example `## Pre-mortem certification` heading must not truncate the hashed span.
    fenced = READY_SPEC.replace(
        'Introduce `src/widget.py`.',
        'Introduce `src/widget.py`.\n\n```\n## Pre-mortem certification\n```\n',
    )
    with_fence = spec_hash(_write(tmp_path, fenced))
    without = spec_hash(_write(tmp_path, READY_SPEC))
    assert with_fence != without  # the fence lines themselves are hashed (raw), but…
    # …the real cert section is still excluded: editing ITS content moves neither hash.
    grown = fenced.replace(
        '- **Failure modes considered & folded in:** none outstanding',
        '- **Failure modes considered & folded in:** none outstanding\n- extra cert line',
    )
    assert spec_hash(_write(tmp_path, grown)) == with_fence
