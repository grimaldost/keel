"""N8a drift guard: the bundled pre-mortem agent must carry the prompt template's contract.

The 0.4.0 release upgraded `pre-mortem-prompt.md` but left `agents/pre-mortem-review.md` on the
0.2.0 "top 5" prose — so the agent that actually runs lagged keel's own doctrine. These tests hold
the two files to the SAME contract markers: a marker removed from EITHER side fails, so neither can
silently drift from the other again.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / 'agents' / 'pre-mortem-review.md'
PROMPT = ROOT / 'src' / 'keel' / 'templates' / 'pre-mortem-prompt.md'

# Structured-findings schema + severity + one distinctive token per directive section, so the
# bundled agent and the prompt template cannot drift apart (ADR-0005 agent <-> prompt fidelity).
# Each token is the verbatim string the directive carries; removing a directive from EITHER file
# drops its token and fails the shared-markers test below.
MARKERS = (
    'smallest_fix',
    'target_section',
    'BLOCKER',
    'population',  # DC1 ground-the-verification
    'staged',  # DC2 mechanical consumers
    'fold ledger',  # DC3 verify-the-transformation
    'evidence-timeline',  # DC1 overturn
    'CONDITIONAL-CERTIFY',  # convergence
    'cross-pr',  # 0.6.0 §5: cross-PR generated-artifact invalidation
    'intent vs. executable',  # 0.6.0 §5: intent -> executable cross-artifact
    'predicted signal',  # 0.6.0 §7: stress-test recorded predictions
    'stress-test',  # 0.6.0 §7: stress-test recorded predictions
)


def test_agent_preserves_frontmatter():
    head = '\n'.join(AGENT.read_text(encoding='utf-8').splitlines()[:5])
    assert head.startswith('---')
    assert 'name: pre-mortem-review' in head
    assert 'tools:' in head


def test_agent_is_not_the_stale_top5_prompt():
    assert 'top 5' not in AGENT.read_text(encoding='utf-8').lower()


def test_agent_and_prompt_share_the_contract_markers():
    agent = AGENT.read_text(encoding='utf-8').lower()
    prompt = PROMPT.read_text(encoding='utf-8').lower()
    for marker in MARKERS:
        needle = marker.lower()
        assert needle in agent, f'agent missing contract marker: {marker!r}'
        assert needle in prompt, f'prompt template missing contract marker: {marker!r}'
