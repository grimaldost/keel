"""The pre-mortem reviewer's noun lens, and the text that dispatches it, stay in place.

The lens lives in the fenced block of the pre-mortem prompt template, and the skill's two dispatch
steps (the spec pass and the series pass) tell the dispatcher to paste `keel vocabulary` output.
Both are text a later compression could trim without any other test noticing, so each clause is
pinned as its own case: a deleted clause turns exactly its case red and shows the clause.

No word count is pinned here: the cap on the block lives in `tests/test_body_budgets.py`.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'src' / 'keel' / 'templates' / 'pre-mortem-prompt.md'
SKILL = ROOT / 'skills' / 'apply-method' / 'SKILL.md'


def _flat(text: str) -> str:
    return ' '.join(text.split())


def _template() -> str:
    return TEMPLATE.read_text(encoding='utf-8')


def _block() -> str:
    """The fenced prompt body, taken as the body-budget test takes it."""
    return _flat(_template().split('## Prompt', 1)[1].split('```')[1])


def _step(start: str, end: str) -> str:
    text = SKILL.read_text(encoding='utf-8')
    return _flat(text.split(start, 1)[1].split(end, 1)[0])


LENS_CLAUSES = [
    'keel vocabulary',
    'MINOR at most',
    'never a condition',
    'a verdict other than CERTIFIED',
    'an allowed term is never a finding',
    'With no vocabulary pasted, infer none and raise no noun findings',
    'is an advisory finding',
    'a listed noun in a sense it does not record',
]


@pytest.mark.parametrize('clause', LENS_CLAUSES)
def test_the_fenced_block_carries_the_lens_clause(clause):
    block = _block()
    assert clause in block


@pytest.mark.parametrize('step', ['specify', 'decompose'])
@pytest.mark.parametrize('phrase', ['keel vocabulary', 'reports `not bound` or an error'])
def test_the_skill_dispatch_step_names_the_vocabulary(step, phrase):
    bounds = {
        'specify': ('- **Specify', '- **Decompose'),
        'decompose': ('- **Decompose', '- **Route'),
    }
    text = _step(*bounds[step])
    assert phrase in text


def test_when_who_tells_the_dispatcher_to_paste_the_vocabulary():
    section = _flat(_template().split('## When / who', 1)[1].split('## Prompt', 1)[0])
    assert 'keel vocabulary' in section
    assert 'not bound' in section
