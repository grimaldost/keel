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
    'hypothesis, not an instruction',  # 0.6.1: re-ground a proposed fix before folding
    'rising bar',  # 0.7.0 §1: rising-bar / convergence directive
    'source-ground capability claims',  # 0.7.0 §3: source-ground capability claims
    'series-pass checklist',  # 0.7.0 §4: first-class SERIES-pass checklist
    'instrument defeatability',  # 0.7.0 §6: eval-spec instrument defeatability
    'feasibility',  # 0.8.0 §1: feasibility-grounding-first (measurable on the record?)
    'generated-artifact behavior',  # 0.8.0 §2: generated-output grounding on the target
    'not deferrable',  # 0.8.0 §3: un-deferrable-when-gated cross-PR artifact
    'caller folds and records',  # 0.8.0 §5: read-only agent returns, caller folds
    'premortem-verdict',  # 0.8.0 §5: machine-greppable verdict line
    'unit of analysis',  # 0.9.0 §1: measurement-design attack (experiment specs)
    'disconfirming',  # 0.9.0 §3: each predicted mode names its disconfirming test
    'inert-treatment',  # 0.10.0 §1: causal path (treatment must reach the measured path)
    'side channel',  # 0.10.0 §1: measured-unit capability audit (no back channel to ground truth)
    'enforcement mechanism',  # 0.10.0 §1: each isolation invariant names a buildable mechanism
    'newly-introduced',  # 0.10.0 §2: re-cert hunts the fold's own newly-introduced errors
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


def test_markers_tuple_length_is_pinned():
    # A marker added to the files but dropped from the guard (or vice-versa) is caught here:
    # the count is the single source of truth for "how many directives are pinned".
    assert len(MARKERS) == 28
