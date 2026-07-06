"""Drift guard: the bundled pre-mortem agent must carry the prompt template's contract.

The 0.4.0 release upgraded `pre-mortem-prompt.md` but left `agents/pre-mortem-review.md` on the
0.2.0 "top 5" prose — so the agent that actually runs lagged keel's own doctrine. Two guarantees,
each with a named limit (0.11.0, honest after the skeptic panel found a live divergence the marker
check missed):

- **Marker presence** — every pinned marker in `MARKERS` appears in BOTH files. Catches a directive
  *dropped* from one side. Limit: it cannot see a directive *reworded* while its marker survives, or
  a marker that recurs in cross-references (deleting one occurrence keeps the token).
- **Clause identity** — every distinctive clause in `SHARED_CLAUSES` appears VERBATIM (modulo
  whitespace) in BOTH files. Catches a pinned directive reworded on one side only (the divergence
  class the panel exploited: "and sibling repos" added to the prompt but not the agent). Limit: it
  only pins the enumerated clauses, not the whole directive set.

Full byte-identity of the shared span stays deferred (V3b); these two together are what actually
holds today, stated as such rather than over-claimed as "neither can ever drift".
"""

import re
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
    'resolution audit',  # 0.12.0 §2: re-gate posture (round >=2 audits prior findings first)
    'cleared:',  # 0.12.0 §2: verified-correct claims recorded as confirmations (colon: bare word pre-exists)
    'conditions:',  # 0.12.0 §2: CONDITIONAL-CERTIFY carries a structured conditions list
    'blast_radius',  # 0.12.0 §2: shared/global-config fixes state their spread in-schema
)


# Distinctive directive clauses carried VERBATIM in both files. Each must appear (whitespace-
# normalized) in the agent AND the prompt; rewording one side drops its count there and fails. Seed
# set — extend it when a directive's exact wording is load-bearing.
SHARED_CLAUSES = (
    'the scope read (src AND tests AND docs, and sibling repos) must be named.',
    'folding a wrong fix verbatim ships the bug it named',
    'a grep of the ground truth is both a defeat and a side channel',
    "the SECOND pass attacks the FIRST pass's folds",
    'a store the measured call recomputes live',
    "recording the `## Pre-mortem certification` block is the caller's step",
    'so a cached or stale copy self-announces on every verdict it returns',
)


def _normalized(path: Path) -> str:
    return re.sub(r'\s+', ' ', path.read_text(encoding='utf-8'))


def test_shared_directive_clauses_are_identical():
    agent, prompt = _normalized(AGENT), _normalized(PROMPT)
    for clause in SHARED_CLAUSES:
        needle = re.sub(r'\s+', ' ', clause)
        assert needle in agent, f'agent missing verbatim clause: {clause!r}'
        assert needle in prompt, f'prompt missing verbatim clause: {clause!r}'


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
    assert len(MARKERS) == 32
