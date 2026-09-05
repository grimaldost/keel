import re
from pathlib import Path

from keel import __version__
from keel.check_ready import _ANCHOR_RE, _anchor_shaped, _declared_kind, _field
from keel.models import CHECK_IDS
from keel.templates import list_templates, templates_root

REQUIRED_SECTIONS = {
    'definition-of-ready.md': ['Part A', 'Part B'],
    'definition-of-done.md': [
        'Deterministic gates',
        'Review gate',
        'git ls-files',
        'Release notes in wave',  # followed the fact here from spec-template.md (T0.5)
    ],
    'pre-mortem-profiles.md': [
        'Experiment design (Part B)',
        'Feasibility-grounding ran FIRST',
        'Instrument defeatability',
        'pre-registered',
    ],
    'review-checklist.md': ['Scope', 'Correctness'],
    'reflection-triage.md': [
        'Procedure',
        'Exit gate',
        'method-promotions',
        'sweep the sink',
        'lists its doc as input',
    ],
    'spec-template.md': [
        'Non-goals',
        'Acceptance',
        'Pre-mortem certification',
        'Gate commands',
        'IS its snippet',
        '§ that creates it',
        'not just the address',
    ],
    'series-toml-skeleton.md': ['Tier vocabulary', 'model-family names', 'method-bindings.md'],
    # The one binding that rots by itself: a consumer that pins a cache version names a
    # directory the next plugin update deletes. Pinned here so the resolved forms cannot be
    # quietly dropped back to a version-pinned example.
    'method-bindings.md': [
        'Invoking the kit',
        'Gate command',
        'CLAUDE_PLUGIN_ROOT',
        'python -m keel',
    ],
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


def test_skeleton_keeps_model_family_tier_names():
    # The skeleton's tiers are model-FAMILY names by decision (haiku / sonnet), the method's own
    # words — deliberately not any one orchestrator's tier vocabulary. Owned upstream by
    # choosing-models' models.toml; keel is a downstream mirror, so it must NOT swap these for an
    # orchestrator's weak/mid/strong/frontier (ADR-0003: the agnostic kit does not import a
    # consumer's words). Pinning the literals also preserves the grep tripwire a capacity-dispatch
    # policy relies on when its model lineup changes.
    text = (templates_root() / 'series-toml-skeleton.md').read_text(encoding='utf-8')
    assert 'tier = "haiku"' in text, 'skeleton lost the haiku model-family tier example'
    assert 'tier = "sonnet"' in text, 'skeleton lost the sonnet model-family tier example'


def test_skeleton_holds_no_api_model_id_in_a_tier_field():
    """Every `tier =` value stays a family name, never an api model id.

    The sibling test above pins the two examples that exist. This one catches the
    failure that actually happens: a hand pastes a resolved lineup in, and the
    skeleton silently becomes a mirror with a shelf life. It is also the only
    tripwire that can fire here, because a lineup refresh greps for outgoing MODEL
    ids and this file, by decision, contains none to find.

    Registered as a walked mirror site in the operator's model-mirrors registry; see
    "Tier vocabulary" for why the family names are deliberate and where they are
    translated. KEEL-B44.
    """
    text = (templates_root() / 'series-toml-skeleton.md').read_text(encoding='utf-8')
    for value in re.findall(r'^\s*tier\s*=\s*"([^"]+)"', text, re.MULTILINE):
        assert not value.startswith('claude-'), (
            f'tier = "{value}" is an api model id, not a model-family name. '
            'The skeleton carries examples, not a lineup: giving it one adds a site '
            'to re-sync on every model release in exchange for nothing.'
        )
        assert value.islower() and value.isalnum(), f'unexpected tier literal: {value!r}'


# T0.5 / the R4 mapping table, kept as data rather than prose so it stays true.
#
# `definition-of-ready.md` carried a hand-written Part-A checklist above the fenced reference
# block, restating the same contract in looser words. When one design called it duplication and
# another called the claim unproven, the tie-break was mechanical rather than editorial: enumerate
# the facts in the surviving home and map every deleted line to one of them. A line with no
# counterpart is not duplication — it moves, or it stays. Every line had one, and the table below
# is that proof; the test under it asserts the surviving home still names every check, so the
# mapping cannot rot into a claim about a block that changed.
DELETED_PART_A_LINES = {
    'Every section is numbered': 'A1',
    'Every numbered section has a non-trivial acceptance criterion': 'A2',
    'No TBD / TODO / FIXME / ??? anywhere in the spec': 'A3',
    'PR ↔ section manifest exists; every section covered by exactly one PR': 'A4',
    'Decompose-skipped relaxes an absent manifest': 'A4',
    'Every concept→module path exists or is "to be created" and claimed': 'A5',
    'Kind: single-change relaxes the structural trio': 'A0',
    'Every path:line anchor resolves and its snippet matches': 'A6',
    'Every cited docs/adr/NNNN- uses a number free on the base': 'A7',
    'Every Model-on / Reuse reference present resolves': 'A9',
    'Every in-text §N reference resolves to a numbered section': 'A8',
    'No prose claims "enforced" against a non-enforced status row': 'A10',
    'Every path:lo-hi range anchor resolves and closes its brackets': 'A11',
    'A claimed fold carries a resolving Fold ledger row per finding': 'R1',
    'When ledger rows are present each anchor resolves': 'A12',
}


def _reference_block() -> str:
    text = (templates_root() / 'definition-of-ready.md').read_text(encoding='utf-8')
    return text.split('```')[1]


def test_the_reference_block_names_every_check_the_deleted_checklist_covered():
    block = _reference_block()
    for line, check in DELETED_PART_A_LINES.items():
        assert re.search(rf'^{check} ', block, re.MULTILINE), (
            f'the deleted Part-A line {line!r} mapped to {check}, which the surviving reference '
            'block no longer names — that line was not duplication after all; restore it or '
            'give it a home'
        )


def test_the_reference_block_is_the_only_home_for_the_part_a_contract():
    # The cut is only information-preserving while the block stays complete: a later edit that
    # drops a letter would silently lose a fact the prose checklist used to carry as well.
    block = _reference_block()
    named = set(re.findall(r'^([ABRW]\d+) ', block, re.MULTILINE))
    assert named == CHECK_IDS, f'reference block and check catalogue disagree: {named ^ CHECK_IDS}'


def _spec_template_header() -> str:
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    first_heading = re.search(r'^##[ \t]+', text, re.MULTILINE)
    return text[: first_heading.start()] if first_heading else text


def test_scaffold_declares_one_resolved_kind():
    # T0.3, and the latent trap it closes: `Kind:` shipped as a MENU (`series | single-change`)
    # and `_declared_kind` reads the leading token, so an untouched scaffold silently declared
    # whichever kind was written first. Reorder the menu and every untouched scaffold silently
    # relaxes A1/A4/A5. A resolved default cannot be reordered into a relaxation.
    header = _spec_template_header()
    raw = _field(header, 'kind')
    assert '|' not in raw, (
        f'the scaffold ships a Kind MENU ({raw!r}) — resolve it to one kind and name the '
        'alternative in prose'
    )
    kind, violation = _declared_kind(header)
    assert violation is None
    assert kind == 'series', f'the scaffolded default must be the STRICT kind, got {kind!r}'


def test_scaffold_names_the_alternative_kind_in_prose():
    # Resolving the menu must not lose the alternative: the note says single-change exists.
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    assert 'single-change' in text


def test_scaffold_carries_the_kit_stamp_in_its_visible_header():
    # T0.3 / KEEL-B17's residual: the stamp was an HTML comment below the closing rule, so a
    # hand-copied spec dropped it silently — no authored spec in the census carried one. A header
    # field beside Date and Status is copied with the rest of the header.
    header = _spec_template_header()
    assert _field(header, 'kit') == __version__, (
        'spec-template.md must stamp the kit in its visible header (`- **Kit:** x.y.z`)'
    )


def test_spec_template_has_no_gate_parseable_anchor():
    # §3 (P4a): a template example anchor must never itself trip A6 in an author's loop, so no
    # backticked `path:line` example in the template resolves as a real anchor — the template
    # documents the form with a non-parseable placeholder (`path:line`, `src/pkg/mod.py:NN`).
    text = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    live = [m.group(0) for m in _ANCHOR_RE.finditer(text) if _anchor_shaped(m.group(1))]
    assert not live, f'spec-template.md carries gate-parseable anchor tokens: {live}'


def test_templates_reference_documents_every_packaged_template():
    # The third of the three coverage gates, and the one that was missing: the CLI reference and
    # the plugin reference each have one, so a new command or entry point cannot land undocumented
    # — but a new kit TEMPLATE could, and `keel init` ships it to every adopting project. Same
    # shape as the other two: glob the shipped set, never a hand-kept list.
    root = Path(__file__).resolve().parents[1]
    reference = (root / 'docs' / 'templates-reference.md').read_text(encoding='utf-8')
    missing = [p.name for p in list_templates() if f'`{p.name}`' not in reference]
    assert not missing, f'templates-reference.md is missing: {missing}'
