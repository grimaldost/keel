"""Word budgets for the bodies that only ever grow (KEEL-B06).

The Definition-of-Ready sheet carries TWO budgets, because it is two bodies with two jobs. Its
prose is read end to end and is capped in words like the others. Its fenced reference block is a
lookup table whose length is a function of the CHECK CATALOGUE, not of prose discipline —
`tests/test_templates_valid.py` makes a new letter mandatory there — so a single sheet-wide cap
made every check the gate gains cost prose budget forever, and the two would eventually deadlock.
The block is capped PER CHECK LINE instead, at its measured maximum: the catalogue may grow, a
line may not sprawl.

The operator's stated promotion rule is that prose added to a shipped body names what it
displaces. It was visibly failing: the pre-mortem directive pair grew one clause per finding
across six ADRs (its drift guard's marker count, 22 -> 33 -> 34, is the record), and the
spec-template's italic gate-contract notes reached 64 of its 185 lines. Neither had a number to
exceed, so no edit ever had to argue for itself.

Three bodies are capped here, each because it is dispatched or read in full every time it is
used, and each cap is stated in CONTRIBUTING ("Body budgets") — the last test asserts the doc and
the machine carry the same numbers, so the budget cannot be quietly relaxed in one place only.

A cap is not a target: an edit that lands under it still owes the displacement. The cap is what
makes the ADR-0017 compression hold instead of refilling.
"""

import re
from pathlib import Path

from keel.models import CHECK_IDS

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING = ROOT / 'CONTRIBUTING.md'

# body -> cap (words)
BUDGETS = {
    'pre-mortem directive block': 2050,
    'spec-template contract notes': 500,
    'pre-mortem agent wrapper': 550,
    'definition-of-ready prose': 950,
}
# The reference block's own budget, per check line rather than in total, set at the measured
# maximum (W2, 61 words). A check's contract is a sentence or two; anything longer belongs in the
# ADR or the CHANGELOG entry that shipped it.
MAX_CHECK_LINE_WORDS = 61
_CHECK_LINE_RE = re.compile(r'^([ABRW]\d+) ')


def _directive_block_words() -> int:
    """The fenced prompt body in pre-mortem-prompt.md — the text dispatched on every pass."""
    text = (ROOT / 'src' / 'keel' / 'templates' / 'pre-mortem-prompt.md').read_text(
        encoding='utf-8'
    )
    block = text.split('## Prompt', 1)[1]
    fenced = block.split('```')[1]
    return len(fenced.split())


def _contract_note_words() -> int:
    """The italic `*…*` gate-contract notes in spec-template.md (the scaffolded reader's tax)."""
    text = (ROOT / 'src' / 'keel' / 'templates' / 'spec-template.md').read_text(encoding='utf-8')
    notes = [
        para
        for para in re.split(r'\n\s*\n', text)
        if para.strip().startswith('*')
        and para.strip().endswith('*')
        and not para.strip().startswith('**')
    ]
    return sum(len(para.split()) for para in notes)


def _agent_words() -> int:
    return len((ROOT / 'agents' / 'pre-mortem-review.md').read_text(encoding='utf-8').split())


def _dor_sheet() -> str:
    return (ROOT / 'src' / 'keel' / 'templates' / 'definition-of-ready.md').read_text(
        encoding='utf-8'
    )


def _dor_prose_words() -> int:
    """The DoR sheet MINUS its reference block — the part a reader actually reads end to end."""
    parts = _dor_sheet().split('```')
    assert len(parts) >= 3, 'the DoR sheet lost its fenced reference block'
    return len((parts[0] + '```'.join(parts[2:])).split())


def _check_lines() -> list[tuple[str, int]]:
    """(check id, words) per entry of the reference block, continuation lines included."""
    entries: list[list[str]] = []
    for line in _dor_sheet().split('```')[1].splitlines():
        if _CHECK_LINE_RE.match(line):
            entries.append([line])
        elif entries:
            entries[-1].append(line)
    return [
        (_CHECK_LINE_RE.match(entry[0]).group(1), len(' '.join(entry).split()))  # type: ignore[union-attr]
        for entry in entries
    ]


MEASURED = {
    'pre-mortem directive block': _directive_block_words,
    'spec-template contract notes': _contract_note_words,
    'pre-mortem agent wrapper': _agent_words,
    'definition-of-ready prose': _dor_prose_words,
}


def test_bodies_are_within_budget():
    over = {
        name: (MEASURED[name](), cap) for name, cap in BUDGETS.items() if MEASURED[name]() > cap
    }
    assert not over, (
        f'over budget (words, cap): {over} — a promotion that adds prose names the one it '
        'displaces or merges into (CONTRIBUTING, Body budgets). Raising the cap is a recorded '
        'decision, not a fix.'
    )


def test_no_reference_block_line_sprawls():
    # The block may GROW with the catalogue; a single entry may not become an essay. Without this,
    # splitting the sheet's cap would have been a relaxation rather than a re-aim.
    over = [(check, words) for check, words in _check_lines() if words > MAX_CHECK_LINE_WORDS]
    assert not over, (
        f'reference-block entries over {MAX_CHECK_LINE_WORDS} words: {over} — a check line states '
        'the contract; the reasoning belongs in the ADR or the CHANGELOG entry that shipped it.'
    )


def test_every_reference_block_entry_is_a_catalogued_check():
    # The counterpart to test_templates_valid's "the block names every check": this one holds that
    # nothing ELSE parses as an entry, so the per-line cap cannot be dodged by an unlettered line.
    assert {check for check, _ in _check_lines()} == CHECK_IDS


def test_contributing_states_the_same_caps():
    # The budget is only a budget if the doc a contributor reads carries the number the suite
    # enforces; a cap raised in one place only is the drift this pins.
    text = CONTRIBUTING.read_text(encoding='utf-8')
    assert '## Body budgets' in text
    for name, cap in BUDGETS.items():
        assert f'{cap:,}' in text or str(cap) in text, (
            f'CONTRIBUTING does not state the {name} cap ({cap})'
        )
