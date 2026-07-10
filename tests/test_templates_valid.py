from keel.check_ready import _ANCHOR_RE, _anchor_shaped
from keel.templates import list_templates, templates_root

REQUIRED_SECTIONS = {
    'definition-of-ready.md': ['Part A', 'Part B'],
    'definition-of-done.md': ['Deterministic gates', 'Review gate'],
    'review-checklist.md': ['Scope', 'Correctness'],
    'reflection-triage.md': ['Procedure', 'Exit gate'],
    'spec-template.md': ['Non-goals', 'Acceptance', 'Pre-mortem certification', 'Gate commands'],
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


def test_spec_template_has_no_gate_parseable_anchor():
    # §3 (P4a): a template example anchor must never itself trip A6 in an author's loop, so no
    # backticked `path:line` example in the template resolves as a real anchor — the template
    # documents the form with a non-parseable placeholder (`path:line`, `src/pkg/mod.py:NN`).
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    live = [m.group(0) for m in _ANCHOR_RE.finditer(text) if _anchor_shaped(m.group(1))]
    assert not live, f'spec-template.md carries gate-parseable anchor tokens: {live}'
