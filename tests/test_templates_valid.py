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
