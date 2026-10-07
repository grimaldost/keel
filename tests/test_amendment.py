"""W7: an amendment is recomputed, not declared.

The tempting design was a declared field — `Amends spec-hash: <hex>` compared against the hash the
artifact recorded. Both sides are literals the author types, so it proves nothing and lowers the
forgery cost to one copy-paste; today's W5 at least compares a recorded literal against a
RECOMPUTED digest. So B2 recomputes instead: remove every declared amendment span and hash again.
Agreement means the certified content is provably intact and what changed was added after the
pass. `spec_hash` itself is untouched, so the amendment still moves the canonical hash and the
block stays tamper-evident — and the list of spans the hash removes stays at two, which is the
pressure this exists to relieve.
"""

import re

from keel.check_ready import check_spec_ready, spec_hash, spec_hash_without_amendments
from keel.templates import templates_root

NL = chr(10)

BASE = """# Spec — widget

- **Status:** ready (DoR passed)

## Numbered sections

### §1 Add the widget
Introduce the widget. **Acceptance criterion:** the widget exists and a unit test
asserts it returns a Widget instance.

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** {verdict}
{operator}- **Certification artifact:** `spec.premortem.md`
- **Date:** 2026-08-28
- **Failure modes considered & folded in:** none outstanding
"""

AMENDMENT = """
## Amendment

The currency normaliser is deferred to the next wave; nothing certified here changes.
"""

SECOND = """
## Amendment

And the report format waits on it, for the same reason.
"""


def _spec(tmp_path, *, tail='', verdict='CERTIFIED', operator='', body='Introduce the widget.'):
    (tmp_path / '.git').mkdir(exist_ok=True)
    spec = tmp_path / 'spec.md'
    text = BASE.format(verdict=verdict, operator=operator).replace('Introduce the widget.', body)
    spec.write_text(text + tail, encoding='utf-8')
    return spec


def _certify(spec, recorded):
    verdict = (
        'CONDITIONAL-CERTIFY' if 'Operator' in spec.read_text(encoding='utf-8') else 'CERTIFIED'
    )
    (spec.parent / 'spec.premortem.md').write_text(
        f'# saved pass{NL}{NL}PREMORTEM-VERDICT: {verdict}{NL}Spec-hash: {recorded}{NL}',
        encoding='utf-8',
    )


def _warns(spec):
    return {w.check for w in check_spec_ready(spec).warnings}


def test_an_amendment_over_intact_content_warns_w7_not_w5(tmp_path):
    spec = _spec(tmp_path)
    certified_hash = spec_hash(spec)
    spec.write_text(spec.read_text(encoding='utf-8') + AMENDMENT, encoding='utf-8')
    _certify(spec, certified_hash)
    warns = _warns(spec)
    assert 'W7' in warns and 'W5' not in warns


def test_a_second_amendment_keeps_the_guarantee(tmp_path):
    # The release discipline makes an amendment section the sanctioned form for EVERY
    # post-certification change, so a once-only mechanism reverts silently on the second one.
    spec = _spec(tmp_path)
    certified_hash = spec_hash(spec)
    spec.write_text(spec.read_text(encoding='utf-8') + AMENDMENT + SECOND, encoding='utf-8')
    _certify(spec, certified_hash)
    warns = _warns(spec)
    assert 'W7' in warns and 'W5' not in warns


def test_a_body_edit_alongside_an_amendment_still_warns_w5(tmp_path):
    spec = _spec(tmp_path)
    certified_hash = spec_hash(spec)
    edited = spec.read_text(encoding='utf-8').replace(
        'Introduce the widget.', 'Introduce the widget and the gadget.'
    )
    spec.write_text(edited + AMENDMENT, encoding='utf-8')
    _certify(spec, certified_hash)
    warns = _warns(spec)
    assert 'W5' in warns and 'W7' not in warns


def test_the_amendment_still_moves_the_canonical_hash(tmp_path):
    # The block is not a hole in the certification: `spec_hash` is unchanged, so the amendment's
    # own text is hashed and the record is tamper-evident.
    spec = _spec(tmp_path)
    before = spec_hash(spec)
    spec.write_text(spec.read_text(encoding='utf-8') + AMENDMENT, encoding='utf-8')
    assert spec_hash(spec) != before
    assert spec_hash_without_amendments(spec) == before


def test_the_operator_close_keeps_its_own_signal(tmp_path):
    # The DoR sheet calls the stale-certification warning the EXPECTED honest state of an
    # operator close, and the release discipline puts the discharging change in an amendment
    # section. Without this exclusion the new letter would eat a signal the method keeps.
    spec = _spec(
        tmp_path,
        verdict='CONDITIONAL-CERTIFY',
        operator='- **Operator:** A. Owner\n',
    )
    certified_hash = spec_hash(spec)
    spec.write_text(spec.read_text(encoding='utf-8') + AMENDMENT, encoding='utf-8')
    _certify(spec, certified_hash)
    warns = _warns(spec)
    assert 'W5' in warns and 'W7' not in warns
    message = next(w.message for w in check_spec_ready(spec).warnings if w.check == 'W5')
    assert 'operator' in message.lower()


def test_a_spec_with_no_amendment_is_unaffected(tmp_path):
    spec = _spec(tmp_path)
    _certify(spec, spec_hash(spec))
    assert 'W7' not in _warns(spec)
    assert 'W5' not in _warns(spec)


def test_a_mention_of_the_word_is_not_a_section(tmp_path):
    # Matched on the heading, never on a mention — the same discipline the truncation incident
    # taught: a backticked `## Amendment` in prose is content, not structure.
    spec = _spec(tmp_path, body='Introduce the widget, per the `## Amendment` convention.')
    _certify(spec, spec_hash(spec))
    assert spec_hash_without_amendments(spec) == spec_hash(spec)


# --- E7b: a declared body amendment is named in W5 ---------------------------------------------
# The method has no sanctioned form for editing a certified body, so the edit lands as W5 "certified
# against an earlier revision" — the same text an accidental drift gets. An `Edits sections:` line
# in an `## Amendment` records what the author says they edited. It is a declaration: the message
# says so, and nothing recomputes it (W7's "certified content intact" stays the only derived claim).

GADGET = """### §2 Add the gadget
Build the gadget.

"""

EDITING_AMENDMENT = """
## Amendment

Reworded the gadget after the pass.

- **Edits sections:** §2
"""


def _two_sections(tmp_path):
    spec = _spec(tmp_path)
    marker = '## Pre-mortem certification'
    text = spec.read_text(encoding='utf-8').replace(marker, GADGET + marker)
    spec.write_text(text, encoding='utf-8')
    return spec


def _w5_message(spec):
    return next(w.message for w in check_spec_ready(spec).warnings if w.check == 'W5')


def _edit_section_two(spec, tail):
    certified_hash = spec_hash(spec)
    edited = spec.read_text(encoding='utf-8').replace('Build the gadget.', 'Build the new gadget.')
    spec.write_text(edited + tail, encoding='utf-8')
    _certify(spec, certified_hash)


def test_a_declared_body_edit_is_named_in_w5(tmp_path):
    spec = _two_sections(tmp_path)
    _edit_section_two(spec, EDITING_AMENDMENT)
    warns = _warns(spec)
    assert 'W5' in warns and 'W7' not in warns
    message = _w5_message(spec)
    assert 'declared amendment' in message and '§2' in message
    assert 'not verified' in message and 'reviewer has not seen' in message
    assert 'earlier revision' not in message


def test_an_undeclared_body_edit_keeps_the_stale_certification_text(tmp_path):
    spec = _two_sections(tmp_path)
    _edit_section_two(spec, AMENDMENT)
    message = _w5_message(spec)
    assert 'earlier revision' in message and 'declared amendment' not in message


def test_a_declaration_with_no_amendment_edit_still_gives_w7(tmp_path):
    # Nothing certified changed, so W7's derived claim wins over a (here redundant) declaration.
    spec = _two_sections(tmp_path)
    certified_hash = spec_hash(spec)
    spec.write_text(spec.read_text(encoding='utf-8') + EDITING_AMENDMENT, encoding='utf-8')
    _certify(spec, certified_hash)
    warns = _warns(spec)
    assert 'W7' in warns and 'W5' not in warns


def test_the_declaration_is_read_from_any_amendment_span(tmp_path):
    spec = _two_sections(tmp_path)
    _edit_section_two(spec, AMENDMENT + EDITING_AMENDMENT.replace('§2', '§1, §2'))
    message = _w5_message(spec)
    assert '§1, §2' in message


def test_a_declaration_outside_an_amendment_section_is_not_read(tmp_path):
    spec = _two_sections(tmp_path)
    _edit_section_two(spec, '\n## Notes\n\n- **Edits sections:** §2\n')
    assert 'declared amendment' not in _w5_message(spec)


def test_an_operator_close_keeps_its_suffix_when_an_edit_is_declared(tmp_path):
    spec = _two_sections(tmp_path)
    text = spec.read_text(encoding='utf-8').replace(
        '- **Verdict:** CERTIFIED', '- **Verdict:** CONDITIONAL-CERTIFY\n- **Operator:** A. Owner'
    )
    spec.write_text(text, encoding='utf-8')
    _edit_section_two(spec, EDITING_AMENDMENT)
    message = _w5_message(spec)
    assert 'operator' in message.lower() and '§2' in message


# --- Amendment review subsection --------------------------------------------------------
# Inside `## Pre-mortem certification`, a subsection `### Amendment review — <date>, round <N>`
# records a certification pass on an amendment, following the Series review pattern.
# The Amendment review is part of the Pre-mortem certification section, which spec_hash excludes.

AMENDMENT_REVIEW_SECTION = """

### Amendment review — 2026-10-06, round 1

- **Amendment reviewer:** review-panel (non-author)
- **Amendment verdict:** CERTIFIED
- **Amendment artifact:** `spec.amendment-r1.md`
- **Edits sections:** §1

The latest dated amendment subsection supersedes earlier ones.
"""


def test_filled_amendment_review_leaves_spec_hash_unchanged(tmp_path):
    # The Amendment review subsection is part of the Pre-mortem certification section,
    # which spec_hash excludes. Adding it should not move the canonical hash.
    spec = _spec(tmp_path)
    before = spec_hash(spec)
    # Insert the Amendment review subsection before the closing separator of the
    # Pre-mortem certification section
    text = spec.read_text(encoding='utf-8')
    # Find the position of the closing separator after Series review
    series_end = text.find('### Series review')
    closing_sep = text.find('\n---', series_end)
    inserted = text[:closing_sep] + AMENDMENT_REVIEW_SECTION + text[closing_sep:]
    spec.write_text(inserted, encoding='utf-8')
    assert spec_hash(spec) == before
    # And verify it's part of the Pre-mortem certification section
    assert spec_hash_without_amendments(spec) == before


def test_amendment_review_subsection_does_not_affect_certification(tmp_path):
    # The Amendment review subsection is part of the Pre-mortem certification section,
    # which is excluded from the hash. Adding it should:
    # 1. Not change the hash (already tested above)
    # 2. Not prevent certification from working (B2 checks still pass)
    # 3. Not be scanned for Verdict lines (B1 only reads the first one)
    spec = _spec(tmp_path)
    certified_hash = spec_hash(spec)
    # Insert the Amendment review subsection
    text = spec.read_text(encoding='utf-8')
    series_end = text.find('### Series review')
    closing_sep = text.find('\n---', series_end)
    inserted = text[:closing_sep] + AMENDMENT_REVIEW_SECTION + text[closing_sep:]
    spec.write_text(inserted, encoding='utf-8')
    _certify(spec, certified_hash)
    warns = _warns(spec)
    # No W7 because the certified content is intact (the Amendment review is part of the
    # Pre-mortem certification section which is excluded from the hash)
    assert 'W7' not in warns and 'W5' not in warns


# --- the template's own Edits sections field is read by W5 -----------------------------------
# `### Amendment review` inside the certification carries an `Edits sections:` field. W5 reads that
# field (the latest subsection) as well as an `## Amendment` span, so an author who fills the
# template's own field gets the declared-amendment message and not the generic one.

_EDITS_FIELD_RE = re.compile(r'(?m)^- \*\*Edits sections:\*\*.*$')


def _template_amendment_review(edits=None):
    """The template's own `### Amendment review` subsection, its Edits field filled when given."""
    template = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    start = template.index('### Amendment review')
    block = template[start : template.index(NL + '---', start)]
    if edits is None:
        return block
    block, count = _EDITS_FIELD_RE.subn(f'- **Edits sections:** {edits}', block)
    assert count == 1
    return block


def _edit_section_two_in_cert(spec, review):
    """Certify, edit section 2 afterwards, then record `review` at the end of the certification."""
    certified_hash = spec_hash(spec)
    edited = spec.read_text(encoding='utf-8').replace('Build the gadget.', 'Build the new gadget.')
    spec.write_text(edited.rstrip(NL) + NL + NL + review, encoding='utf-8')
    _certify(spec, certified_hash)


def test_the_templates_own_edits_field_is_named_in_w5(tmp_path):
    spec = _two_sections(tmp_path)
    _edit_section_two_in_cert(spec, _template_amendment_review('§2'))
    message = _w5_message(spec)
    assert 'declared amendment' in message and '§2' in message
    assert 'earlier revision' not in message


def test_the_templates_unfilled_edits_field_declares_nothing(tmp_path):
    spec = _two_sections(tmp_path)
    _edit_section_two_in_cert(spec, _template_amendment_review())
    message = _w5_message(spec)
    assert 'earlier revision' in message and 'declared amendment' not in message


def test_only_the_latest_amendment_review_declares_edits(tmp_path):
    spec = _two_sections(tmp_path)
    first = _template_amendment_review('§1')
    second = _template_amendment_review('§2').replace('round <N>', 'round 2')
    _edit_section_two_in_cert(spec, first + NL + NL + second)
    message = _w5_message(spec)
    assert '§2' in message and '§1' not in message
