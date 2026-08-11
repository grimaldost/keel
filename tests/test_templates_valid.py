import re

from keel import __version__
from keel.check_ready import _ANCHOR_RE, _anchor_shaped, _declared_kind, _field
from keel.templates import list_templates, templates_root

REQUIRED_SECTIONS = {
    'definition-of-ready.md': ['Part A', 'Part B'],
    'definition-of-done.md': ['Deterministic gates', 'Review gate', 'git ls-files'],
    'review-checklist.md': ['Scope', 'Correctness'],
    'reflection-triage.md': [
        'Procedure',
        'Exit gate',
        'method-promotions',
        'sweep the sink',
        'lists its doc as input',
    ],
    'spec-template.md': [
        'Non-goals',
        'Acceptance',
        'Pre-mortem certification',
        'Gate commands',
        'IS its snippet',
        '§ that creates it',
        'not just the address',
    ],
    'series-toml-skeleton.md': ['Tier vocabulary', 'model-family names', 'method-bindings.md'],
}


def test_all_templates_present():
    names = {p.name for p in list_templates()}
    assert len(names) >= 10
    assert 'definition-of-ready.md' in names


def test_required_sections_present():
    for name, needles in REQUIRED_SECTIONS.items():
        text = (templates_root() / name).read_text(encoding='utf-8')
        for needle in needles:
            assert needle in text, f'{name} missing section marker: {needle!r}'


def test_skeleton_keeps_model_family_tier_names():
    # The skeleton's tiers are model-FAMILY names by decision (haiku / sonnet), the method's own
    # words — deliberately not any one orchestrator's tier vocabulary. Owned upstream by
    # choosing-models' models.toml; keel is a downstream mirror, so it must NOT swap these for an
    # orchestrator's weak/mid/strong/frontier (ADR-0003: the agnostic kit does not import a
    # consumer's words). Pinning the literals also preserves the grep tripwire a capacity-dispatch
    # policy relies on when its model lineup changes.
    text = (templates_root() / 'series-toml-skeleton.md').read_text(encoding='utf-8')
    assert 'tier = "haiku"' in text, 'skeleton lost the haiku model-family tier example'
    assert 'tier = "sonnet"' in text, 'skeleton lost the sonnet model-family tier example'


def _spec_template_header() -> str:
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    first_heading = re.search(r'^##[ \t]+', text, re.MULTILINE)
    return text[: first_heading.start()] if first_heading else text


def test_scaffold_declares_one_resolved_kind():
    # T0.3, and the latent trap it closes: `Kind:` shipped as a MENU (`series | single-change`)
    # and `_declared_kind` reads the leading token, so an untouched scaffold silently declared
    # whichever kind was written first. Reorder the menu and every untouched scaffold silently
    # relaxes A1/A4/A5. A resolved default cannot be reordered into a relaxation.
    header = _spec_template_header()
    raw = _field(header, 'kind')
    assert '|' not in raw, (
        f'the scaffold ships a Kind MENU ({raw!r}) — resolve it to one kind and name the '
        'alternative in prose'
    )
    kind, violation = _declared_kind(header)
    assert violation is None
    assert kind == 'series', f'the scaffolded default must be the STRICT kind, got {kind!r}'


def test_scaffold_names_the_alternative_kind_in_prose():
    # Resolving the menu must not lose the alternative: the note says single-change exists.
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    assert 'single-change' in text


def test_scaffold_carries_the_kit_stamp_in_its_visible_header():
    # T0.3 / KEEL-B17's residual: the stamp was an HTML comment below the closing rule, so a
    # hand-copied spec dropped it silently — no authored spec in the census carried one. A header
    # field beside Date and Status is copied with the rest of the header.
    header = _spec_template_header()
    assert _field(header, 'kit') == __version__, (
        'spec-template.md must stamp the kit in its visible header (`- **Kit:** x.y.z`)'
    )


def test_spec_template_has_no_gate_parseable_anchor():
    # §3 (P4a): a template example anchor must never itself trip A6 in an author's loop, so no
    # backticked `path:line` example in the template resolves as a real anchor — the template
    # documents the form with a non-parseable placeholder (`path:line`, `src/pkg/mod.py:NN`).
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    live = [m.group(0) for m in _ANCHOR_RE.finditer(text) if _anchor_shaped(m.group(1))]
    assert not live, f'spec-template.md carries gate-parseable anchor tokens: {live}'
