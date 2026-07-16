# Spec — Add source-host field to record contract

- **Date:** 2026-07-16
- **Status:** draft
- **Audience:** parser, reporter, and external consumers of tempo records
- **Output artifact(s):** `src/tempo/contract.py`, `src/tempo/parse.py`, `src/tempo/report.py`, `tests/test_tempo.py`

*Optional header field for a declared non-series round: `- **Phases:** Decide+Specify
(Decompose: skipped)` — when Decompose is explicitly named as skipped, `check-ready` (A4) relaxes
the PR↔section manifest requirement to absent-ok. A manifest that IS present is still fully
checked, everything else in Part A applies regardless, and the declaration is content the
pre-mortem can challenge — not an escape hatch (ADR-0014).*

## Context

Tempo records currently lack a source identifier. The record contract (defined in `src/tempo/contract.py:10-13`)
defines records as `(epoch_seconds, level, message)` tuples, with no host or source information.
When logs are aggregated from multiple machines, the current contract cannot distinguish their
origin. Adding a `source_host` field (a string identifying the source host) to the contract enables
consumers to filter, group, and route records by source. This is a breaking contract change that
affects the parser, the reporter, and all external consumers that import `tempo.contract`.

## Goal

Extend the record contract to include a `source_host` field as the fourth element of every record tuple,
enabling source identification across aggregated logs. The refactor touches the contract definition,
all internal consumers (parse, report), tests, and will require migration by external consumers.

## Gate commands

All work in this wave must pass these deterministic gates before merge:

- `python3 -m unittest discover -s tests -v` — all tests pass
- `ruff check .` — no linting violations in src/ and tests/
- `ruff format --check .` — code formatting is consistent

## Non-goals

- Migration or notification of external consumers (out-of-repo modules that import `tempo.contract`).
- Backward-compatibility layer or deprecation period.
- Encoding or validation rules for `source_host` values (left to consumers).
- Automatic host detection (source_host is passed by callers; no automatic hostname resolution).

## Invariants touched

Per `docs/adr/0001-record-contract-source-host.md`: the record contract shape is now `(int, str, str, str)` —
a 4-tuple: epoch_seconds, level, message, source_host. This invariant is enforced by `make_record()` and
must be upheld by all modules that import or create records (parse, report, external consumers).

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| Record contract shape: (int, str, str, str) | enforced | `make_record()` type checks; test coverage via `python3 -m unittest discover -s tests` |
| `make_record()` requires 4 args | enforced | Tests verify signature and reject 3-arg calls |
| All record unpacking updated | review-only | PR review checklist: every `for ...level... in records` loop updated |

*No invariant is claimed as "enforced" without a gate listed above.*

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| source_host field (4th tuple element) | `src/tempo/contract.py` |
| make_record(epoch_seconds, level, message, source_host) | `src/tempo/contract.py` |
| Parse-time source_host extraction | `src/tempo/parse.py` |
| Report-time source_host handling | `src/tempo/report.py` |
| Test coverage for source_host | `tests/test_tempo.py` |

*All concepts are grounded in existing modules; no new files created.*

## Numbered sections

Each numbered section is a unit of work a single PR can cite. Keep them small and
single-concern.

### §1 Update contract definition

**What changes:** The `make_record()` function (defined at `src/tempo/contract.py:10-13`) signature changes from
`make_record(epoch_seconds, level, message)` to `make_record(epoch_seconds, level, message, source_host)`.
The returned record tuple changes from `(int(epoch_seconds), level, message)` to
`(int(epoch_seconds), level, message, source_host)`, adding source_host as the fourth element.

The `LEVELS` constant at `src/tempo/contract.py:7` remains unchanged.

All input validation in `make_record()` is retained; type and level checking continue. `source_host`
is accepted as a string with no validation (consumers enforce encoding rules).

**Acceptance criterion:** `make_record()` accepts 4 arguments (epoch_seconds, level, message, source_host),
returns a 4-tuple with source_host as the fourth element, and all existing validation (epoch-to-int,
level-in-LEVELS check) passes.

### §2 Update parser to extract and pass source_host

**What changes:** The `parse_line()` function (defined at `src/tempo/parse.py:6`) parses input lines to extract source_host
and pass it to `make_record()`. The input line format changes from `'EPOCH LEVEL MESSAGE'` to
`'EPOCH LEVEL SOURCE_HOST MESSAGE'` (source_host as the third whitespace-delimited token).

The split operation at line 7 (`line.strip().split(' ', 2)`) changes to split 4 fields: epoch, level, source_host, message.
The call to `make_record()` at line 8 is updated to pass the extracted source_host.

**Reuse:** The `make_record()` function from §1 is imported and called with 4 arguments.

**Acceptance criterion:** `parse_line('1700000000 INFO host1 started')` returns a 4-tuple with
source_host='host1' as the fourth element. Invalid input (missing source_host, too few fields) raises
a clear error.

### §3 Update reporter to handle source_host

**What changes:** The `count_by_level()` function (defined at `src/tempo/report.py:6`) unpacks records correctly.
The line `for _, level, _ in records:` changes to `for _, level, _, _ in records:` to account for the
source_host field. The logic (counting by level) is unchanged; source_host is ignored in the sum.

No other changes to report.py are needed for this PR (optional extension: add `count_by_source_host()`,
but that is out-of-scope).

**Acceptance criterion:** `count_by_level()` unpacks 4-tuple records correctly without index errors.
Counts remain accurate when records include source_host.

### §4 Expand test coverage

**What changes:** The `test_parse_and_count()` test method (at `tests/test_tempo.py:12-15`) is updated to exercise
the new source_host field. Test input lines include source_host tokens; assertions verify that
`parse_line()` correctly extracts source_host and `count_by_level()` handles 4-tuples.

Additional test cases cover:
- Parsing with different source_host values.
- Verifying source_host is correctly placed as the fourth tuple element.
- Verifying `make_record()` rejects 3-argument calls (old signature).

**Acceptance criterion:** All tests pass. Test coverage includes at least one parse call with a
non-empty source_host and verification that the returned tuple is a 4-tuple.

### §5 Document migration for external consumers

**What changes:** A brief MIGRATION.md or README section explains the breaking change to external consumers.
(This section is informational; no code change is required in THIS repo. External consumers update their own code.)

- Record tuple is now 4-tuple: (epoch_seconds, level, message, source_host).
- `make_record()` signature: `make_record(epoch_seconds, level, message, source_host)`.
- `parse_line()` input format: lines must include source_host as the third whitespace-delimited field.
- Callers must provide source_host or extract it from the input line.

**Acceptance criterion:** A concise migration note exists in the repo (e.g., as a section in README.md
or a standalone MIGRATION.md), visible to external consumers.

---

*All sections use anchors to ground claims in the actual code.*

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |
| PR05 | §5 | yes |

*Every section must be covered by exactly one PR, and every PR must cite exactly
one section. PR01 must merge first (contract change prerequisite); PR02–PR04 have no ordering
constraint but all must be complete before merge. PR05 (documentation) lands in the same wave.*

## Definition of Done (this spec)

Concrete, checkable conditions for the whole spec (beyond per-section criteria).

- **Generated / mirrored artifacts:** none (this refactor does not generate downstream artifacts).
- **Release notes:** A CHANGELOG entry (or README update) documenting the breaking change must land in PR05 (§5).
  Format: "Breaking: record contract changed to 4-tuple (epoch, level, message, source_host)."
- **All gate commands pass:** `python3 -m unittest discover -s tests -v`, `ruff check .`, `ruff format --check .`.
- **No external consumer notifications:** External consumers are responsible for migrating; the repo provides
  migration guidance in MIGRATION.md or README but does NOT coordinate notification.

## Pre-mortem certification

*The externalized correctness pass (`pre-mortem-prompt.md`), certified by a fresh
reviewer who did NOT author this spec. `keel check-ready` does not pass until the
verdict is `CERTIFIED` (ADR-0002). A freshly-scaffolded spec is, correctly, not Ready.
Save the pass's returned output to the sibling `<spec-stem>.premortem.md` (header: spec path,
date, reviewer, `Spec-hash:` from `keel spec-hash`) and name it below — `check-ready` B2 verifies
a named artifact's existence, verdict agreement, and spec-hash currency. B2 raises the cost of
forging a certification; it does not prove the pass was blind — that residual trust stays named.*

- **Reviewer:** (pending pre-mortem)
- **Verdict:** not yet certified
- **Operator:** (not applicable for initial certification)
- **Certification artifact:** (pending: docs/spec-add-source-host.premortem.md)
- **Date:** (pending)
- **Reviewed against:** None (no external dependencies)
- **Post-fold coherence:** (pending)
- **Failure modes considered & folded in:** None (pre-mortem not yet certified)


---
*This template is structured so that most of the deterministic Definition-of-Ready
checks (`definition-of-ready.md`) pass by construction: numbered sections,
per-section acceptance criteria, the concept→module map, and the PR↔section
manifest are all required fields. The one field NOT satisfied by construction is the
pre-mortem certification — a non-author reviewer must sign it, which is the point
(ADR-0002).*

<!-- keel kit X.Y.Z -->
