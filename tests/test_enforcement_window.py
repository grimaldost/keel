"""A10's three reproduced defeats, and the window that must not over-fire fixing them (T1.3).

A10 has 17 status tables in the census and zero fires. Silence is what a working check and a
broken one both look like, so before any disposition could be argued the defeats had to be found
and closed. Three were reproduced against a realistic spec:

1. the invariant key was matched over a prev/this/next line window, so a claim three lines below
   its key was invisible;
2. the negation window DELETED backtick spans, so a backticked invariant name right before the
   claim vanished and the four-word lookback reached past it into an unrelated "not";
3. the negation rule matched common words anywhere in those four words, so "is, once again,
   enforced" read as a deferral.

The fixes are a paragraph-scoped key window, an unwrapping (not deleting) lookback, and a
lookback that stops at the clause boundary. A10 is a neighbourhood check, and the 0.11.0/0.13.0
lesson is that widening one to catch a false negative is exactly how a false-positive wave starts
— so the corpus's clean spec must stay silent, and this module additionally runs the check over
the repo's own shipped prose, which is where window logic tuned on synthetic fixtures goes wrong.
"""

from pathlib import Path

from keel.check_ready import _check_enforcement_claims, _split_top_sections

ROOT = Path(__file__).resolve().parents[1]

TABLE = """## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| region codes come from a closed set | planned | the §3 normaliser |
| one entry per region | enforced | a unit test |

## Notes

"""


def _fires(prose: str) -> list[str]:
    text = TABLE + prose + '\n'
    return [v.message for v in _check_enforcement_claims(_split_top_sections(text), text)]


def test_a_claim_three_lines_below_its_key_now_fires():
    assert _fires(
        'The rule that region codes come from a closed set is what §3 lands,\n'
        'and every caller depends on it,\n'
        'so today it is already enforced.'
    )


def test_a_backticked_key_no_longer_lets_an_earlier_negation_suppress_the_claim():
    assert _fires('The row is not optional. `region codes come from a closed set` is enforced.')


def test_a_negation_in_another_clause_no_longer_suppresses():
    assert _fires('The region codes come from a closed set rule is, once again, enforced today.')


def test_the_plain_over_claim_still_fires():
    assert _fires('The region codes come from a closed set rule is enforced by the loader.')


def test_a_real_deferral_is_still_suppressed():
    for deferral in (
        'region codes come from a closed set is not enforced yet.',
        'region codes come from a closed set will be enforced once §3 lands.',
        'region codes come from a closed set is to be enforced by the normaliser.',
        'region codes come from a closed set is planned to be enforced.',
        'region codes come from a closed set is never enforced today.',
    ):
        assert not _fires(deferral), deferral


def test_a_backticked_claim_word_is_still_meta_discussion():
    assert not _fires('The region codes come from a closed set row reads `enforced` in the table.')


def test_an_unrelated_paragraph_does_not_borrow_the_key():
    # The window widened from three lines to a paragraph; a paragraph away is still out of reach.
    assert not _fires(
        'The region codes come from a closed set rule lands in §3.\n'
        '\n'
        'Separately, one entry per region is enforced by a unit test.'
    )


def test_the_repos_own_shipped_prose_does_not_false_fire():
    # The 0.11.0 lesson, as a standing test: window logic that only ever saw synthetic fixtures
    # false-fires on the very artifacts the project ships. CONTRIBUTING carries a real
    # Enforcement-status table with non-enforced rows and pages of prose around it.
    for name in ('CONTRIBUTING.md', 'docs/doctrine.md', 'README.md'):
        text = (ROOT / name).read_text(encoding='utf-8')
        found = _check_enforcement_claims(_split_top_sections(text), text)
        assert not found, (name, [(v.where, v.message) for v in found])
