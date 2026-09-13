"""The Decompose exit gate: the generated series was reviewed before anything ran it.

keel gates the spec and had no gate on its own executable output. The evidence is the corpus's
one controlled measurement: ten reviewers over a generated series returned 16 BLOCKER, 18 MAJOR
and 14 MINOR findings — three of them structural defects that seven rounds of spec pre-mortem
could not reach, because they were defects in an artifact no phase read. One of those was an
irreversible publication scheduled as an ordinary node of an autonomous DAG.

**Why this is a second gate and not four more checks in `check_spec_ready`.** The DoR sheet states
the boundary: `check-ready` is the exit gate of Specify and the entry gate of Decompose, and a
series may not be decomposed until it passes. At that moment the decomposition does not exist, so
a DoR check over it could only fire on every well-formed spec in the method — which is not a gate,
it is noise. This gate runs one boundary later (3->4), on the artifact that by then exists.

**Why the record lives inside `## Pre-mortem certification`.** That span is the one `spec_hash`
removes (ADR-0014), so writing the series verdict cannot move the hash the design pass was
certified against — a gate whose own record invalidated a neighbouring certification would be the
W2 trap, where the gate's advice defeated the gate. The field labels are prefixed (`Series
reviewer:`, not a second `Reviewer:`) so B1's one-verdict-per-block rule still reads exactly one
Verdict line and neither check can pick up the other's field.

D1/D2 are deliberately B1/B2's shape: a record naming a non-author reviewer and a terminal verdict
(D1), and a saved artifact that agrees with it (D2). That raises the cost of forging this review
to the cost of forging the other one; it does not prove the pass was blind, and that residual
trust stays named rather than hidden (ADR-0002).

What this gate does NOT do: read the series file. keel is consumer-agnostic (ADR-0003) — the DAG's
format belongs to the orchestrator that runs it, so the method gates the review's record, and what
the reviewer read is named in the record rather than parsed here.
"""

import re
from pathlib import Path

from keel.check_ready import (
    _declared_kind,
    _field,
    _find_section,
    _first_path_token,
    _read_spec_text,
    _resolve_base,
    _split_top_sections,
    _subsections,
    _verdict_head,
)
from keel.models import DECOMPOSE_CHECK_IDS, GateResult, Probe, Violation, Warning, count_causes

WHERE = 'Series review'
# The pre-mortem's own terminal verdicts, not a new vocabulary. CONDITIONAL-CERTIFY is accepted
# for the reason the round economy gives: a bounded, named fix does not buy a full extra round.
_TERMINAL = ('CERTIFIED', 'CONDITIONAL-CERTIFY')
# The grammar D1 parses, quoted in its own rejection — six field grammars were discovered by
# iteration in one rite, each costing its own run-read-fix cycle (0.19.0).
_GRAMMAR = (
    'a `### Series review` sub-block of `## Pre-mortem certification` carrying '
    '`- **Series reviewer:** <non-author>`, `- **Series verdict:** CERTIFIED` (or '
    '`CONDITIONAL-CERTIFY`) and `- **Series artifact:** <path>`, each on a line of its own'
)


def _series_review(cert_body: str | None) -> str | None:
    """The `### Series review` sub-block of the certification section, or None."""
    if cert_body is None:
        return None
    for heading, body in _subsections(cert_body):
        if 'series' in heading.lower() and 'review' in heading.lower():
            return body
    return None


def _declares_no_decomposition(header: str) -> str:
    """The header declaration that says this boundary is never crossed, or ''.

    The same two declarations A4 already honours (ADR-0014, KEEL-B01). The gate does not invent a
    requirement they relax: a spec with nothing to decompose has no series to review, and that is
    `n/a` — a different fact from a clean run, and the probe records it as such.
    """
    if _declared_kind(header)[0] == 'single-change':
        return '`Kind: single-change`'
    phases = _field(header, 'phases').lower()
    if 'decompose' in phases and 'skipped' in phases:
        return '`Phases: … (Decompose: skipped)`'
    return ''


def _check_record(review: str | None) -> list[Violation]:
    """D1: the SERIES pass is recorded — a non-author reviewer, a terminal verdict, an artifact."""
    if review is None:
        return [
            Violation(
                WHERE,
                'no series review is recorded: the decomposition this spec produced has not been '
                'read by a fresh reviewer, which is the defect class a spec pre-mortem '
                f'structurally cannot reach. The gate parses {_GRAMMAR}.',
                'D1',
            )
        ]
    violations: list[Violation] = []
    head = _verdict_head(_field(review, 'series verdict'))
    if head not in _TERMINAL:
        recorded = _field(review, 'series verdict') or '(none)'
        violations.append(
            Violation(
                WHERE,
                f'series verdict is {recorded!r}, not one of {" | ".join(_TERMINAL)} — a review '
                'that returned NEEDS-REVISION is a review that said no, and execution starts '
                'only once the decomposition it read is the one that will run. The line this '
                'gate parses is `- **Series verdict:** CERTIFIED`, trailing prose allowed.',
                'D1',
            )
        )
    if not _field(review, 'series reviewer'):
        violations.append(
            Violation(
                WHERE,
                'the series review names no reviewer (must be a non-author, and not the reviewer '
                'who certified the spec — the two passes read different artifacts). The line this '
                'gate parses is `- **Series reviewer:** <name>`, the label carrying no '
                'parenthesis of its own.',
                'D1',
            )
        )
    if not _first_path_token(_field(review, 'series artifact')):
        violations.append(
            Violation(
                WHERE,
                'the series review names no artifact — a recorded verdict is one typed line, and '
                'the saved pass is what raises the cost of forging it (the same trade B2 makes '
                "for the design pass). Save the reviewer's returned output beside the spec "
                '(`<spec-stem>.series-premortem.md`) and name it: '
                '`- **Series artifact:** <path>`.',
                'D1',
            )
        )
    return violations


def _check_artifact(review: str, spec_path: Path) -> list[Violation]:
    """D2: the named artifact exists, is a saved pass, and its verdict agrees with the record."""
    ref = _first_path_token(_field(review, 'series artifact'))
    if not ref:
        return []  # D1 owns the absence; reporting it twice would double-count one defect
    target = _resolve_base(spec_path) / ref
    if not target.is_file():
        return [
            Violation(
                WHERE,
                f'referenced series-review artifact {ref!r} does not exist as a file — that is '
                'the leading path token of the field; the path is repo-root-relative, like an '
                'anchor, and any trailing prose is ignored.',
                'D2',
            )
        ]
    text = target.read_text(encoding='utf-8', errors='replace')
    anchored = [
        line for line in text.splitlines() if line.lstrip().startswith('PREMORTEM-VERDICT:')
    ]
    if not anchored:
        return [
            Violation(
                WHERE,
                f'artifact {ref!r} carries no line-anchored `PREMORTEM-VERDICT:` line — it does '
                "not look like a saved pass's output. The line this gate reads starts the line "
                '(indentation aside) and leads with the bare token: '
                '`PREMORTEM-VERDICT: CERTIFIED`, trailing prose allowed; where several appear, '
                'the LAST one is the verdict.',
                'D2',
            )
        ]
    artifact_head = _verdict_head(anchored[-1].split(':', 1)[1])
    recorded = _verdict_head(_field(review, 'series verdict'))
    if artifact_head != recorded:
        return [
            Violation(
                WHERE,
                f'artifact verdict token {artifact_head!r} disagrees with the recorded series '
                f'verdict {recorded!r} — the saved pass is the record; re-run or re-record.',
                'D2',
            )
        ]
    return []


def check_decomposition(spec_path: Path) -> GateResult:
    """Assert the generated series was reviewed, by a named non-author, before execution.

    Returns a `GateResult` in `check_spec_ready`'s own contract: pass with no violations, and one
    `Probe` per D-check whose `candidates` is 0 exactly when the spec declares that this boundary
    is never crossed — so a run over a `single-change` spec reads as `n/a`, never as a clean gate.
    """
    text = _read_spec_text(spec_path, purpose='decompose-check')
    first_heading = re.search(r'^##[ \t]+', text, re.MULTILINE)
    header = text[: first_heading.start()] if first_heading else text
    relaxed = _declares_no_decomposition(header)

    violations: list[Violation] = []
    warnings: tuple[Warning, ...] = ()
    review = _series_review(_find_section(_split_top_sections(text), 'pre-mortem', 'certification'))
    if not relaxed:
        violations += _check_record(review)
        if review is not None:
            violations += _check_artifact(review, spec_path)

    candidates = {
        'D1': 0 if relaxed else 1,
        # D2's opportunity is a recorded review to verify — absent, there is nothing for it to
        # read and its silence says nothing (the three-state rule, KEEL-B07).
        'D2': 0 if relaxed or review is None else 1,
    }
    fired: dict[str, int] = dict.fromkeys(DECOMPOSE_CHECK_IDS, 0)
    for violation in violations:
        fired[violation.check] += 1
    probes = tuple(
        Probe(
            check=check,
            candidates=candidates[check],
            fired=fired[check],
            causes=count_causes(v for v in violations if v.check == check) or fired[check],
        )
        for check in sorted(DECOMPOSE_CHECK_IDS)
    )
    return GateResult(
        passed=not violations, violations=tuple(violations), warnings=warnings, probes=probes
    )
