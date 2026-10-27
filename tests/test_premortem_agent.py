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
from tests.test_plugin_manifest import frontmatter

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / 'agents' / 'pre-mortem-review.md'
PROMPT = ROOT / 'src' / 'keel' / 'templates' / 'pre-mortem-prompt.md'
PROFILES = ROOT / 'src' / 'keel' / 'templates' / 'pre-mortem-profiles.md'

TEMPLATE_REF = '${CLAUDE_PLUGIN_ROOT}/src/keel/templates/pre-mortem-prompt.md'

# Directive clauses and the ONE kit body that carries each. Sampled across the directive layers
# (DC1 grounding, DC2 mechanical consumers, DC3 the fold) and across the always-on/selected split,
# so a partial re-inlining is caught, not only a wholesale one.
#
# The always-on directive and the profile sheet are now two homes for two audiences, not one home
# and a restatement: a lens that only a `measurement` spec pays for lives in the sheet its
# `Profile:` selects (KEEL-B10), and the same clause appearing in both would put the reader back
# where the split started. So the assertion runs in both directions over both files.
PROMPT_CLAUSES = (
    'the scope read (src AND tests AND docs, and sibling repos) must be named',
    "the SECOND pass attacks the FIRST pass's folds",
    'a wave that plans no regeneration can still leave a mirror stale',
    'the concrete input the dependent actually consumes',
)
PROFILE_CLAUSES = (
    'the measured call recomputes live',
    'a grep of the ground truth is both a defeat and a side channel',
    'the cheapest way an agent sidesteps the planted difficulty',
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
    '.premortem.md',
    'keel spec-hash',
)


def _normalized(path: Path) -> str:
    return re.sub(r'\s+', ' ', path.read_text(encoding='utf-8'))


def test_agent_preserves_frontmatter():
    head = '\n'.join(AGENT.read_text(encoding='utf-8').splitlines()[:5])
    assert head.startswith('---')
    assert 'name: pre-mortem-review' in head
    assert 'tools:' in head


def test_agent_frontmatter_fixes_the_reviewers_tier():
    """The pass runs on the tier its job was scored for, not the tier of whoever dispatched it.

    Until 0.22.0 the agent named no `model` or `effort`, so it inherited the calling session's:
    a frontier session at maximum effort ran a frontier pass, and a cheap one ran a cheap pass, on
    the same spec. A cold reading of a spec against the code is judgment work (choosing-models
    score 85, the strong tier), so the front matter fixes it. `omitClaudeMd` keeps the caller's
    CLAUDE.md files out: the reviewer takes its directives from the template and its facts from
    the code it reads. Plugin agents honour all three fields (Claude Code docs, "Frontmatter
    fields in plugin agents"); a Claude Code too old to know one ignores it.
    """
    fields = frontmatter(AGENT)
    assert fields.get('name') == 'pre-mortem-review'
    assert fields.get('tools') == 'Read, Grep, Glob', 'the reviewer stays read-only'
    assert fields.get('model') == 'opus', (
        f'model reads {fields.get("model")!r}: the tier is a recorded choosing-models decision '
        '(CHANGELOG 0.22.0), never `inherit`'
    )
    assert fields.get('effort') == 'high', f'effort reads {fields.get("effort")!r}'
    assert fields.get('omitClaudeMd') == 'true', (
        f'omitClaudeMd reads {fields.get("omitClaudeMd")!r}'
    )


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
    for clause in PROMPT_CLAUSES:
        needle = re.sub(r'\s+', ' ', clause).lower()
        assert needle in prompt, f'template lost the directive clause: {clause!r}'
        assert needle not in agent, (
            f'agent re-carries a directive the template owns: {clause!r} — the fold is refilling'
        )


def test_the_domain_lenses_live_in_the_profile_sheet_only():
    """The moved lenses have one home each, and it is the sheet a `Profile:` selects.

    The always-on directive is the body every pass pays for; a lens only one profile needs
    belongs in the sheet that profile selects. A clause in both is the duplication the move
    exists to end, and a clause in neither is a lens that silently stopped being dispatched.
    """
    agent, prompt = _normalized(AGENT).lower(), _normalized(PROMPT).lower()
    profiles = _normalized(PROFILES).lower()
    for clause in PROFILE_CLAUSES:
        needle = re.sub(r'\s+', ' ', clause).lower()
        assert needle in profiles, (
            f'the profile sheet lost the lens clause: {clause!r} — it was moved out of the '
            'always-on directive to live here, so losing it here retires it entirely'
        )
        assert needle not in prompt, (
            f'the always-on directive re-carries a profile lens: {clause!r} — every `code` spec '
            'pays for it again, which is what the move displaced'
        )
        assert needle not in agent, f'agent carries a directive the kit owns elsewhere: {clause!r}'


def test_the_returned_message_opening_lines_do_not_collide():
    """SW12: line 1 is the save path, line 2 the spec-hash instruction, so the missing-directive
    notice takes the line after them; and the instruction names the SPEC as the file to leave
    alone until the hash is stamped, since editing it first makes B2 compare a post-edit spec."""
    agent = _normalized(AGENT)
    assert 'Its first line is the save path' in agent
    assert 'its second line is: "After the last fold this pass read' in agent
    assert 'before editing the spec' in agent
    assert 'say so in your third line' in agent


def test_agent_keeps_the_output_contract_tokens():
    agent = AGENT.read_text(encoding='utf-8')
    for token in OUTPUT_CONTRACT:
        assert token in agent, f'agent lost an output-contract token a caller greps: {token!r}'


# The saved file's name is one rule, stated by the agent and echoed by the templates: round 1 is the
# unsuffixed file, round N is `-r<N>`, and the certification field leads with the LATEST round's
# file because B2 reads the field's leading path token (ADR-0014 section 1).
TEMPLATES = ROOT / 'src' / 'keel' / 'templates'
SPEC_TEMPLATES = (TEMPLATES / 'spec-template.md', TEMPLATES / 'core' / 'spec-template.md')
DOR_SHEETS = (TEMPLATES / 'definition-of-ready.md', TEMPLATES / 'core' / 'definition-of-ready.md')
ADR_0014 = ROOT / 'docs' / 'adr' / '0014-certification-artifact-and-round-economy.md'
ROUND_SIBLINGS = (
    PROMPT,
    ROOT / 'skills' / 'apply-method' / 'SKILL.md',
    ROOT / 'docs' / 'getting-started.md',
    ROOT / 'docs' / 'glossary.md',
    ROOT / 'docs' / 'method-bindings.md',
    *DOR_SHEETS,
)


def test_agent_states_the_round_file_rule():
    agent = _normalized(AGENT)
    assert (
        '`<spec-stem>.premortem.md` is round 1; round N is `<spec-stem>.premortem-r<N>.md`'
    ) in agent
    assert 'premortem-r1' not in agent, 'round 1 is the unsuffixed file, never -r1'


def test_spec_templates_state_the_round_file_rule_and_the_leading_latest_round():
    for path in SPEC_TEMPLATES:
        text = _normalized(path)
        assert 'premortem-r1' not in text, f'{path.name}: round 1 is the unsuffixed file'
        assert 'premortem-r<N>.md' in text, f'{path.name}: later rounds are -r<N>'
        assert re.search(r'round 1 is `<stem>\.premortem\.md`', text), path
        assert 'leads with the latest round' in text.lower(), (
            f'{path.name}: the field leads with the LATEST round (B2 reads the leading token)'
        )


def test_the_certification_artifact_bullet_is_byte_identical_in_both_templates():
    bullets = [
        next(
            line
            for line in path.read_text(encoding='utf-8').splitlines()
            if line.startswith('- **Certification artifact:**')
        )
        for path in SPEC_TEMPLATES
    ]
    assert bullets[0] == bullets[1]


def test_round_file_siblings_name_the_later_round_suffix():
    for path in ROUND_SIBLINGS:
        assert '-r<N>' in _normalized(path), f'{path.relative_to(ROOT)} still states one file name'


def test_adr_0014_carries_the_dated_round_file_note():
    text = _normalized(ADR_0014)
    assert '2026-10-27' in text
    assert '`<spec-stem>.premortem-r<N>.md`' in text


def test_a12_names_its_first_anchor_cell_in_both_definition_of_ready_files():
    lines = []
    for path in DOR_SHEETS:
        a12 = [
            line
            for line in path.read_text(encoding='utf-8').splitlines()
            if line.startswith('A12 ')
        ]
        assert len(a12) == 1, path
        assert 'in its first anchor cell' in a12[0] and 'in any cell' not in a12[0], path
        lines.append(a12[0])
    assert lines[0] == lines[1]
