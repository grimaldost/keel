"""The two kit files a sibling project points at by reference, pinned line by line (T0.6/T0.7).

`definition-of-done.md` and `review-checklist.md` stopped being local copies in two other
projects and became references to this kit. That makes their line text a published surface: a
reordering is free, a rewording is not, and nothing here may be removed until the consumer has
moved. So the foregrounding pass reorders and adds one framing sentence to each, and this module
asserts the part that could actually break a pointer — that every consumed line survives
byte-identical.

The blast-radius row is the other half: a measured null on danger framing is NOT a licence to
delete the field, because the field does not carry danger framing. It names a target. This pins
the distinction so the register cannot drift into the thing the null was about.
"""

from keel.templates import templates_root

# Byte-identical fragments, not paraphrases: each is the text a consumer's pointer resolves to.
CONSUMED = {
    'definition-of-done.md': [
        'Each tool-wrapping gate asserts the tool **ran to completion** (exit status / no fatal',
        'halt), not just that error count ≤ baseline',
        'is **tracked in version control** —',
        '`git ls-files --error-unmatch <path>` succeeds for each referenced path',
        '- [ ] Reviewer verdict is APPROVE (or the salvage round closed every finding).',
        '- [ ] The change is single-concern and cites exactly one spec section.',
        "- [ ] The cited spec section's acceptance criterion is met.",
        '**Merge only when every box is checked.**',
    ],
    'review-checklist.md': [
        '- [ ] **Gate completion** — every type/lint/test gate ran to completion (exit 0, no',
        '      "fatal" / "source file found twice" halt), not merely error-count ≤ baseline; a',
        '      checker that bailed early must fail the gate, not pass it.',
        '- [ ] **Scope** — single concern; cites exactly one spec section; no unrelated',
        '- [ ] **Invariants** — respects every boundary/lock/immutability/contract named in',
        '- [ ] **Tests** — behavior changes have tests; tests assert behavior, not',
        '- [ ] **No coupling smell** — no reaching through `getattr`/private attrs to dodge',
    ],
}

# The `blast_radius:` field's own text. It names WHAT THE FIX REACHES — a target, which is the
# highest-value property a pre-mortem finding carries. It is not danger framing, and the danger
# framing null does not reach it.
BLAST_RADIUS_FORM = 'one line naming what else the fix reaches'
DANGER_REGISTER = (
    'catastroph',
    'disaster',
    'devastat',
    'dangerous',
    'severe damage',
    'irreversible harm',
)


def _lines(name: str) -> list[str]:
    return (templates_root() / name).read_text(encoding='utf-8').splitlines()


def test_consumed_lines_are_byte_identical():
    for name, needles in CONSUMED.items():
        text = (templates_root() / name).read_text(encoding='utf-8')
        for needle in needles:
            assert needle in text, (
                f'{name}: a consumed line changed or was removed — {needle!r}. Two sibling '
                'projects resolve a pointer to this text; reorder freely, reword only after the '
                'consumer has moved.'
            )


def test_the_two_field_derived_dod_traps_lead_the_deterministic_gates():
    # The foregrounding itself: the two non-inferable traps are what this list ADDS over a
    # project's own toolchain, so they are read first and the generic block is labelled a stub.
    lines = _lines('definition-of-done.md')
    boxes = [line for line in lines if line.startswith('- [ ]')]
    assert 'ran to completion' in boxes[0], boxes[0]
    assert 'tracked in version control' in boxes[1], boxes[1]
    assert 'stub' in '\n'.join(lines), 'the generic block is no longer labelled as the stub it is'


def test_gate_completion_leads_the_review_checklist():
    lines = _lines('review-checklist.md')
    first_box = next(line for line in lines if line.startswith('- [ ]'))
    assert 'Gate completion' in first_box


def test_generic_review_is_delegated_in_words_not_only_by_omission():
    # Without this sentence a later collapse of the generic items reads as amputation rather than
    # delegation, and a reviewer cannot tell which it was.
    text = (templates_root() / 'review-checklist.md').read_text(encoding='utf-8')
    assert 'delegated' in text


def test_blast_radius_names_a_target_and_carries_no_danger_register():
    # The recorded non-change. A measurement found danger framing inert in agent-directed prose;
    # the only agent-directed blast-radius text in the kit is not danger framing, so the null
    # licenses nothing here. This tripwire is what keeps that true.
    text = (templates_root() / 'pre-mortem-prompt.md').read_text(encoding='utf-8')
    assert BLAST_RADIUS_FORM in text, (
        'the blast_radius field no longer names what the fix reaches — target naming is the '
        'measured-valuable property, and rewording it into a danger register would trade it for '
        'the property measured inert'
    )
    field_line = next(line for line in text.splitlines() if 'blast_radius:' in line)
    assert not any(word in field_line.lower() for word in DANGER_REGISTER), field_line
