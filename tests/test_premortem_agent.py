"""Single-source guard: the directive text has one home, and the agent points at it.

Until 0.13.1 the directive text lived in two ~90%-identical files (`agents/pre-mortem-review.md`
and `src/keel/templates/pre-mortem-prompt.md`), held together by a drift guard that pinned a
34-marker tuple and a clause-identity set — a guard bumped on every release, over a duplication
that had only ever grown. KEEL-B02 folds the pair: the template is the single home of the
directives (it is the copy that reaches consumers running the method without the plugin), and the
agent body is a thin identity + dispatch + output-contract wrapper that READS it at run start.

The drift guard goes with the duplication it existed to hold together. What replaces it is the
arrangement itself, pinned here:

- **Delegation** — the agent names the template by its `${CLAUDE_PLUGIN_ROOT}` path, so the body
  that actually runs cannot silently stop consuming the directives.
- **Non-duplication** — directive clauses appear in the template and NOT in the agent, so the
  fold cannot quietly refill (the failure mode the 34-marker guard could never catch: growth).
- **Identity** — the agent's version line still matches the package (the fifth version site,
  0.12.0 §2), so a stale plugin-cache copy self-announces on every verdict it returns.

The agent's word cap lives with the other body budgets in `test_body_budgets.py`.
"""

import re
from pathlib import Path

from keel import __version__

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / 'agents' / 'pre-mortem-review.md'
PROMPT = ROOT / 'src' / 'keel' / 'templates' / 'pre-mortem-prompt.md'

TEMPLATE_REF = '${CLAUDE_PLUGIN_ROOT}/src/keel/templates/pre-mortem-prompt.md'

# Directive clauses that used to be carried verbatim in both files. Each must now appear in the
# template and NOT in the agent — one home per directive. Sampled across the directive layers
# (DC1 grounding, DC2 mechanical consumers, DC3 the fold, the measurement lane) so a partial
# re-inlining is caught, not only a wholesale one.
DIRECTIVE_CLAUSES = (
    'the scope read (src AND tests AND docs, and sibling repos) must be named',
    "the SECOND pass attacks the FIRST pass's folds",
    'a store the measured call recomputes live',
    'a wave that plans no regeneration can still leave a mirror stale',
    'the concrete input the dependent actually consumes',
    'a grep of the ground truth is both a defeat and a side channel',
)

# Output-contract invariants the agent DOES carry: a caller greps these, so they must survive in
# the body that runs even if the template is unreachable.
OUTPUT_CONTRACT = (
    'PREMORTEM-VERDICT:',
    'Unverified-offline:',
    'smallest_fix',
    'target_section',
    'disconfirming_test',
    'CONDITIONAL-CERTIFY',
)


def _normalized(path: Path) -> str:
    return re.sub(r'\s+', ' ', path.read_text(encoding='utf-8'))


def test_agent_preserves_frontmatter():
    head = '\n'.join(AGENT.read_text(encoding='utf-8').splitlines()[:5])
    assert head.startswith('---')
    assert 'name: pre-mortem-review' in head
    assert 'tools:' in head


def test_agent_identity_line_states_the_running_version():
    # The fifth version site (0.12.0 §2). test_plugin_manifest asserts all sites AGREE; this
    # asserts the agent's own line resolves to the running package, so the wrapper cannot lose it.
    match = re.search(
        r'bundled `pre-mortem-review` agent from keel ([0-9]+\.[0-9]+\.[0-9]+)',
        AGENT.read_text(encoding='utf-8'),
    )
    assert match is not None, 'agent identity line missing'
    assert match.group(1) == __version__


def test_agent_dispatches_to_the_single_source_template():
    agent = AGENT.read_text(encoding='utf-8')
    assert TEMPLATE_REF in agent, f'agent no longer reads the directive template ({TEMPLATE_REF})'
    assert PROMPT.is_file()


def test_directives_live_in_the_template_only():
    agent, prompt = _normalized(AGENT).lower(), _normalized(PROMPT).lower()
    for clause in DIRECTIVE_CLAUSES:
        needle = re.sub(r'\s+', ' ', clause).lower()
        assert needle in prompt, f'template lost the directive clause: {clause!r}'
        assert needle not in agent, (
            f'agent re-carries a directive the template owns: {clause!r} — the fold is refilling'
        )


def test_agent_keeps_the_output_contract_tokens():
    agent = AGENT.read_text(encoding='utf-8')
    for token in OUTPUT_CONTRACT:
        assert token in agent, f'agent lost an output-contract token a caller greps: {token!r}'
