"""Sweep a design directory: which spec-shaped documents here carry no certification?

The field failure this answers: a phase with a clear blast radius — six-plus planned PRs across
three repositories, shared contracts — was specified in four hand-written documents with no
Definition-of-Ready and no pre-mortem, and nothing accused. Doctrine's invocation trigger exists
only as prose to be remembered, at exactly the moment memory is worst. One of those four documents
was later condemned whole by a rigour review; the one respecified with the method survived its
implementation without a red.

`check-ready` cannot answer the question because it gates ONE spec and its exit codes are pinned
(0 ready, 1 violations, 2 not runnable). A sweep is a report, not a gate on a spec, so it is its
own verb — and mixing the two would muddy the contract that exit 1 means "this spec is not ready".

**Spec-shaped** is the predicate the exit code turns on, and it is stated rather than implied: a
document carrying a numbered-sections heading or a PR-to-section manifest heading. A design
directory also holds triage documents, ADR drafts, saved pre-mortem artifacts and requirements
registers, none of which want a certification; they are listed as not-a-spec and never affect the
exit code.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from keel.errors import format_error

_SPEC_SHAPE_RE = re.compile(
    r'^##[ \t]+(numbered\s+sections|pr\s*(?:↔|<->|->)?\s*section\s+manifest)', re.IGNORECASE | re.M
)
_CERT_HEADING_RE = re.compile(r'^##[ \t]+.*pre-mortem.*certification', re.IGNORECASE | re.M)
_VERDICT_RE = re.compile(
    r'^[\-*\s]*verdict[\s*]*:[\s*]*(CERTIFIED|CONDITIONAL-CERTIFY|NEEDS-REVISION)\b',
    re.IGNORECASE | re.M,
)


@dataclass(frozen=True)
class Surveyed:
    """One document in the directory, and what the sweep could say about it."""

    path: Path
    spec_shaped: bool
    verdict: str = ''

    @property
    def certified(self) -> bool:
        return self.spec_shaped and bool(self.verdict)


def survey(directory: Path) -> list[Surveyed]:
    """Every markdown document in the directory, in name order, with its certification state."""
    if not directory.is_dir():
        raise NotADirectoryError(
            format_error(
                what=f'{directory} is not a directory.',
                why='`keel survey` sweeps a design directory; a single spec is `keel check-ready`.',
                fix='Point it at the directory your specs live in (often `docs/design/`).',
            )
        )
    results: list[Surveyed] = []
    for path in sorted(directory.glob('*.md')):
        text = path.read_text(encoding='utf-8', errors='replace')
        if _SPEC_SHAPE_RE.search(text) is None:
            results.append(Surveyed(path, spec_shaped=False))
            continue
        verdict = ''
        if _CERT_HEADING_RE.search(text) is not None:
            match = _VERDICT_RE.search(text)
            verdict = match.group(1).upper() if match else ''
        results.append(Surveyed(path, spec_shaped=True, verdict=verdict))
    return results
