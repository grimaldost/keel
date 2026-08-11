"""T0.1: every finding the gate emits names the check that raised it.

`Violation` was `(where, message)` only, and `where` is a coordinate, not an identity: `line N`
comes from both A3 and A8, `path:line` from A6, A11 and A12, and four separate B1 conditions all
report against the literal `Pre-mortem certification`. Warnings were bare strings and carried no
identity at all. Counting a check's fires — the whole point of the hit-rate ledger — is not
possible against a coordinate that collides, so the id is a prerequisite, not a convenience.

The messages keep their `WARN: ` prose prefix and gain no `W1: ` string prefix: identity lives in
the field, so no consumer has to re-parse a message to learn which check spoke.
"""

from keel import __version__
from keel.check_ready import check_spec_ready
from keel.models import CHECK_IDS

BASE = f"""# Spec — orders rollup

- **Status:** ready (DoR passed)
- **Kit:** {__version__}

## Numbered sections

### §1 Add the rollup
What changes, in `orders.py`. **Acceptance criterion:** the rollup returns one row
per region and a unit test asserts the totals.

## Concept → module map

| Concept | Module / file it lives in |
|---|---|
| rollup | `orders.py` (to be created) |

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** CERTIFIED
- **Date:** 2026-08-11
- **Failure modes considered & folded in:** none outstanding
"""


def _write(tmp_path, text):
    spec = tmp_path / 'spec.md'
    spec.write_text(text, encoding='utf-8')
    return spec


def _run(tmp_path, text, **kwargs):
    return check_spec_ready(_write(tmp_path, text), **kwargs)


def _checks(result):
    return {v.check for v in result.violations} | {w.check for w in result.warnings}


def test_every_finding_names_a_check_in_the_closed_catalogue(tmp_path):
    result = _run(tmp_path, BASE.replace('- **Verdict:** CERTIFIED', '- **Verdict:** REJECTED'))
    assert not result.passed
    assert all(v.check in CHECK_IDS for v in result.violations), [
        (v.check, v.where) for v in result.violations
    ]
    assert all(w.check in CHECK_IDS for w in result.warnings), [w.check for w in result.warnings]


def test_a3_and_a8_share_a_where_and_are_told_apart_by_check(tmp_path):
    # Both report `line N`. Before T0.1 a ledger counting by `where` would fuse them.
    spec = BASE.replace(
        'What changes, in `orders.py`.',
        'What changes, in `orders.py`, see §9 for context; TODO: finish.',
    )
    result = _run(tmp_path, spec)
    by_check = {v.check for v in result.violations}
    assert {'A3', 'A8'} <= by_check, [(v.check, v.where, v.message) for v in result.violations]
    wheres = [v.where for v in result.violations if v.check in ('A3', 'A8')]
    assert len(set(wheres)) < len(wheres), 'the where-collision this test exists for is gone'


def test_a6_and_a11_share_a_where_and_are_told_apart_by_check(tmp_path):
    (tmp_path / 'orders.py').write_text('x = (1,\n2)\ny = 3\n', encoding='utf-8')
    spec = BASE.replace(
        'What changes, in `orders.py`.',
        'What changes, in `orders.py`: `orders.py:99` and `orders.py:80-90`.',
    )
    result = _run(tmp_path, spec)
    assert {v.check for v in result.violations} >= {'A6', 'A11'}, [
        (v.check, v.where) for v in result.violations
    ]


def test_b1_conditions_share_a_where_and_all_carry_b1(tmp_path):
    spec = BASE.replace(
        '- **Verdict:** CERTIFIED',
        '- **Verdict:** NEEDS-REVISION\n- **Verdict:** CERTIFIED',
    ).replace('- **Reviewer:** review-panel (non-author)\n', '')
    result = _run(tmp_path, spec)
    b1 = [v for v in result.violations if v.where == 'Pre-mortem certification']
    assert len(b1) >= 2, [(v.check, v.message) for v in result.violations]
    assert {v.check for v in b1} == {'B1'}


def test_w1_unstamped_and_w2_status_currency_are_lettered(tmp_path):
    spec = BASE.replace(f'- **Kit:** {__version__}\n', '').replace(
        '- **Status:** ready (DoR passed)', '- **Status:** draft'
    )
    result = _run(tmp_path, spec)
    assert {'W1', 'W2'} <= _checks(result), [(w.check, w.message) for w in result.warnings]


def test_w3_basename_expansion_is_lettered(tmp_path):
    (tmp_path / 'pkg').mkdir()
    (tmp_path / 'pkg' / 'orders.py').write_text('a = 1\nb = 2\n', encoding='utf-8')
    result = _run(
        tmp_path,
        BASE.replace('What changes, in `orders.py`.', 'What changes, in `orders.py:2`.'),
    )
    assert 'W3' in _checks(result), [(w.check, w.message) for w in result.warnings]


def test_w4_adoption_nudge_and_w5_hash_mismatch_are_lettered(tmp_path):
    # B2's two warnings were unlettered, so B2's whole warning output was uncountable — and an
    # uncountable warning cannot be defended when its keep verdict is questioned.
    nudge = _run(tmp_path, BASE)
    assert 'W4' in _checks(nudge), [(w.check, w.message) for w in nudge.warnings]

    (tmp_path / 'pass.md').write_text(
        f'PREMORTEM-VERDICT: CERTIFIED\nSpec-hash: {"deadbeef" * 8}\n', encoding='utf-8'
    )
    stale = _run(
        tmp_path,
        BASE.replace('- **Date:** 2026-08-11', '- **Certification artifact:** `pass.md`'),
    )
    assert 'W5' in _checks(stale), [(w.check, w.message) for w in stale.warnings]


def test_no_warning_message_carries_a_letter_prefix(tmp_path):
    # The id is a field. A `W1: …` string prefix would recreate the parsing class 0.14.0's shared
    # leading-token field parser removed.
    result = _run(tmp_path, BASE.replace(f'- **Kit:** {__version__}\n', ''))
    assert result.warnings
    for warning in result.warnings:
        assert not warning.message.startswith(f'{warning.check}:'), warning.message
        assert warning.message.startswith('WARN: ')
