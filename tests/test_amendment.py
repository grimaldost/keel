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

from keel.check_ready import check_spec_ready, spec_hash, spec_hash_without_amendments

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
