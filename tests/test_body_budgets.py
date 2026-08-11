"""Word budgets for the bodies that only ever grow (KEEL-B06).

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

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING = ROOT / 'CONTRIBUTING.md'

# body -> (cap, what it measures)
BUDGETS = {
    'pre-mortem directive block': 2050,
    'spec-template contract notes': 925,
    'pre-mortem agent wrapper': 550,
}


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


MEASURED = {
    'pre-mortem directive block': _directive_block_words,
    'spec-template contract notes': _contract_note_words,
    'pre-mortem agent wrapper': _agent_words,
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


def test_contributing_states_the_same_caps():
    # The budget is only a budget if the doc a contributor reads carries the number the suite
    # enforces; a cap raised in one place only is the drift this pins.
    text = CONTRIBUTING.read_text(encoding='utf-8')
    assert '## Body budgets' in text
    for name, cap in BUDGETS.items():
        assert f'{cap:,}' in text or str(cap) in text, (
            f'CONTRIBUTING does not state the {name} cap ({cap})'
        )
