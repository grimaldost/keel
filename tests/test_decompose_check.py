"""The Decompose exit gate (E3a): the generated series was reviewed before anything ran it.

The method gates the spec and had no gate on its own executable output. One measured run says what
that costs: ten reviewers over a generated series returned 16 BLOCKER, 18 MAJOR and 14 MINOR
findings, three of them structural defects that seven rounds of spec pre-mortem could not reach,
because they were defects in an artifact no phase read. The spec gate cannot close that: the DoR
gate is the exit gate of Specify and the entry gate of Decompose, so at the moment it runs the
series does not exist yet.

So the review is recorded where the design pass is recorded — inside `## Pre-mortem certification`,
which `spec_hash` excludes, so writing the record cannot invalidate the certification it sits next
to — and a second gate at the 3->4 boundary reads it. D1/D2 are B1/B2's shape one boundary later.

This module carries the D-family's positive controls, in the adversarial corpus's own form and for
its reason (CONTRIBUTING, gate health 1a): one record that fires nothing, and one MINIMAL edit per
check that must make exactly that check fire — set equality, never membership. The DoR corpus in
`tests/fixtures/adversarial/` cannot host them, because every fixture there is scored by
`check_spec_ready`, which does not run these checks.
"""

from pathlib import Path

import pytest

from keel.decompose_check import check_decomposition
from keel.models import DECOMPOSE_CHECK_IDS

CLEAN = """# Spec - the sample wave

- **Kind:** series
- **Date:** 2026-09-13

## Numbered sections

### §1 Do the thing

Acceptance criterion: the thing is done, and a committed test proves it.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |

## Pre-mortem certification

- **Reviewer:** a non-author
- **Verdict:** CERTIFIED

### Series review

- **Series reviewer:** a second non-author
- **Series verdict:** CERTIFIED
- **Series artifact:** sample.series-premortem.md
"""

ARTIFACT = 'findings, then the verdict\n\nPREMORTEM-VERDICT: CERTIFIED\n'

# id -> (one edit as (find, replace), the artifact body, the checks that must fire, why)
MUTANTS = [
    (
        'D1-no-record-at-all',
        ('### Series review\n\n', '### Not the review\n\n'),
        ARTIFACT,
        {'D1'},
        'a decomposition nobody reviewed is the state this gate exists to refuse',
    ),
    (
        'D1-no-series-reviewer',
        ('- **Series reviewer:** a second non-author\n', ''),
        ARTIFACT,
        {'D1'},
        'an unattributed review cannot be shown to be non-author, which is the whole mechanism',
    ),
    (
        'D1-verdict-is-not-terminal',
        ('- **Series verdict:** CERTIFIED', '- **Series verdict:** NEEDS-REVISION'),
        # The artifact moves with it: a record and a saved pass that disagree is D2's defect, and
        # a fixture that plants two is not a control for either.
        'PREMORTEM-VERDICT: NEEDS-REVISION\n',
        {'D1'},
        'NEEDS-REVISION is a review that ran and said no; execution may not start on it',
    ),
    (
        'D1-no-artifact-named',
        ('- **Series artifact:** sample.series-premortem.md\n', ''),
        ARTIFACT,
        {'D1'},
        'a typed line is a claim; the saved pass is what raises the cost of forging one',
    ),
    (
        'D2-artifact-does-not-exist',
        ('sample.series-premortem.md', 'nowhere/absent.md'),
        ARTIFACT,
        {'D2'},
        'the named artifact is the evidence; a path to nothing is a record of nothing',
    ),
    (
        'D2-artifact-verdict-disagrees',
        None,
        'PREMORTEM-VERDICT: NEEDS-REVISION\n',
        {'D2'},
        'the saved pass is the record: a CERTIFIED line over a NEEDS-REVISION artifact is forgery',
    ),
    (
        'D2-artifact-is-not-a-saved-pass',
        None,
        'some notes with no verdict line at all\n',
        {'D2'},
        'a file that carries no verdict line is not the pass output the record claims',
    ),
]


def _materialize(tmp_path: Path, edit, artifact: str = ARTIFACT) -> Path:
    text = CLEAN
    if edit is not None:
        find, replace = edit
        assert text.count(find) == 1, (
            f'`find` must match the clean record exactly once (matched {text.count(find)}) — a '
            'fixture that edits two places is not a one-edit delta'
        )
        text = text.replace(find, replace)
    tmp_path.mkdir(parents=True, exist_ok=True)
    spec = tmp_path / 'sample.md'
    spec.write_text(text, encoding='utf-8')
    (tmp_path / 'sample.series-premortem.md').write_text(artifact, encoding='utf-8')
    return spec


def _fired(spec: Path) -> set[str]:
    result = check_decomposition(spec)
    return {v.check for v in result.violations} | {w.check for w in result.warnings}


def test_the_clean_record_is_the_false_positive_floor(tmp_path):
    # Every mutant is diffed against this. A corpus whose base is not silent measures the base.
    result = check_decomposition(_materialize(tmp_path, None))
    assert result.passed, [(v.check, v.where, v.message) for v in result.violations]
    assert result.warnings == (), [(w.check, w.message) for w in result.warnings]


@pytest.mark.parametrize(
    ('mutant_id', 'edit', 'artifact', 'fires', 'why'),
    MUTANTS,
    ids=[m[0] for m in MUTANTS],
)
def test_mutant_fires_exactly_its_target(tmp_path, mutant_id, edit, artifact, fires, why):
    assert _fired(_materialize(tmp_path, edit, artifact)) == fires, why


def test_every_decompose_check_has_a_positive_control():
    # The corpus is only a power probe if it covers the surface, and a gate that ships with an
    # uncontrolled check ships a check whose silence will never be informative.
    covered = {
        check
        for *_, fires, _ in ((m[0], m[1], m[2], m[3], m[4]) for m in MUTANTS)
        for check in fires
    }
    assert covered == DECOMPOSE_CHECK_IDS, f'uncontrolled: {sorted(DECOMPOSE_CHECK_IDS - covered)}'


def test_a_conditional_certify_review_passes_the_gate(tmp_path):
    # The verdict vocabulary is the pre-mortem's, not a new one: CONDITIONAL-CERTIFY is a terminal
    # verdict the directive emits, and a gate that refused it would push a bounded, named fix into
    # a re-run the round economy already prices as over-process.
    spec = _materialize(
        tmp_path,
        ('- **Series verdict:** CERTIFIED', '- **Series verdict:** CONDITIONAL-CERTIFY'),
        'PREMORTEM-VERDICT: CONDITIONAL-CERTIFY\n',
    )
    assert check_decomposition(spec).passed


def test_a_spec_that_declares_no_decomposition_has_nothing_to_gate(tmp_path):
    # `Kind: single-change` and `Phases: … (Decompose: skipped)` are the method's own declarations
    # that this boundary is not crossed. The gate does not invent a requirement they relax: it
    # passes with NO applicable probe, which is a different fact from a clean run and reads as
    # `n/a` wherever the counts are read back.
    for declaration in (
        ('- **Kind:** series', '- **Kind:** single-change'),
        ('- **Kind:** series', '- **Phases:** Decide+Specify (Decompose: skipped)'),
    ):
        spec = _materialize(tmp_path, (declaration[0] + '\n', ''))
        spec.write_text(
            spec.read_text(encoding='utf-8').replace(
                '# Spec - the sample wave\n', f'# Spec - the sample wave\n\n{declaration[1]}\n'
            ),
            encoding='utf-8',
        )
        result = check_decomposition(spec)
        assert result.passed, declaration
        assert all(probe.candidates == 0 for probe in result.probes), (
            f'{declaration[1]}: the gate counted an opportunity it was told does not exist'
        )


def test_a_missing_spec_is_not_runnable(tmp_path):
    # The 0/1/2 contract: exit 2 is "not runnable", and the CLI maps FileNotFoundError onto it.
    with pytest.raises(FileNotFoundError):
        check_decomposition(tmp_path / 'absent.md')


def test_every_finding_names_a_catalogued_check(tmp_path):
    # The ledger counts by id; an anonymous finding is one nothing can count, and a check whose
    # fires cannot be counted cannot be kept or cut on evidence.
    for mutant_id, edit, artifact, _, _why in MUTANTS:
        result = check_decomposition(_materialize(tmp_path / mutant_id, edit, artifact))
        for finding in (*result.violations, *result.warnings):
            assert finding.check in DECOMPOSE_CHECK_IDS, (mutant_id, finding)


def test_a_check_never_fires_without_a_counted_candidate(tmp_path):
    # The invariant the DoR gate's probes hold, held here too: a fire with no candidate makes the
    # fire rate's denominator a lie.
    for mutant_id, edit, artifact, _, _why in MUTANTS:
        result = check_decomposition(_materialize(tmp_path / mutant_id, edit, artifact))
        for probe in result.probes:
            assert probe.fired == 0 or probe.candidates > 0, (mutant_id, probe)
