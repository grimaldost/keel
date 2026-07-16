# Spec — Add source-host field to record contract

- **Date:** 2026-07-16
- **Status:** ready (DoR passed; CONDITIONAL-CERTIFY with 5 MAJOR findings folded)
- **Audience:** tempo contributors, external consumer maintainers
- **Output artifact(s):** `src/tempo/contract.py`, `src/tempo/parse.py`, `src/tempo/report.py`, `tests/test_tempo.py`, consumer codebases

## Context

The record contract in `src/tempo/contract.py:1-13` (`make_record`) currently carries three fields:
`(epoch_seconds, level, message)`. This is imported by the parser (`src/tempo/parse.py`), the
reporter (`src/tempo/report.py`), and external consumers — a shared boundary imported by
≥~50 modules across the ecosystem.

Multi-host log aggregation requires knowing the source hostname of each record. Today, that
information is unavailable downstream of the parser, so reporters and external consumers cannot
correlate records to their originating host. This refactor adds `source_host` as the fourth field
of the tuple, enabling downstream correlation and filtering.

See **ADR-0001** (`docs/adr/0001-add-source-host-to-record.md`) for the decision and alternatives.

## Goal

Extend the record tuple from 3 to 4 elements: `(epoch_seconds, level, message, source_host)`,
validate source_host across all code paths, and update the parser, reporter, and tests to
correctly handle the new field. This is a breaking change requiring coordinated updates across
all consumers.

## Gate commands

- `python3 -m pytest tests/ -v` — all existing tests plus new tests for source_host pass
- `python3 -m mypy src/` — full type checking of src/tempo modules
- Manual inspection: every unpacking of `(epoch, level, msg, …) = record` is updated

## Non-goals

- Consumer codebases outside this repo are NOT updated in this wave (external consumers are
  responsible for their own updates).
- The input file format for the parser is not extended beyond `EPOCH LEVEL SOURCE_HOST MESSAGE`
  (no extra metadata fields).
- The reporter's output format is not changed (source_host is propagated internally but may not
  appear in summary counts, unless explicitly decided in §3).
- Performance optimization of tuple access is not in scope (type-based optimization is a follow-up).

## Invariants touched

1. **Record shape contract** — The record tuple must always be a 4-tuple `(epoch_seconds: int, level: str, message: str, source_host: str)` with runtime validation: epoch_seconds must be int, level must be in LEVELS, message and source_host must be non-empty strings.
   *ADR: docs/adr/0001-add-source-host-to-record.md.*

2. **LEVELS enforcement** — The `level` field must always be one of the LEVELS in `LEVELS`,
   validated at record-creation time. This invariant persists; source_host does not affect it.

3. **Parser input format** — The parser's input format is extended from `EPOCH LEVEL MESSAGE`
   to `EPOCH LEVEL SOURCE_HOST MESSAGE` (4 whitespace-delimited fields with MESSAGE preserving spaces).
   Any code reading the parser's input must adapt.

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| Record shape contract | enforced | `mypy src/` (type annotations) + `pytest tests/` (tuple unpacking tests) |
| LEVELS enforcement | enforced | `make_record` validation (existing) + `pytest tests/` |
| Parser input format | enforced | `pytest tests/` (test fixtures assert new format) + manual code review |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| Record tuple structure (4-tuple) | `src/tempo/contract.py` |
| source_host field and validation | `src/tempo/contract.py` |
| Parser extraction of source_host | `src/tempo/parse.py` |
| Reporter handling of 4-tuple | `src/tempo/report.py` |
| Test fixtures for 4-tuple records | `tests/test_tempo.py` |

## Numbered sections

### §1 Extend contract.py with source_host field

**What changes:** Modify `src/tempo/contract.py` to:
- Add `source_host` as the fourth element of the record tuple.
- Update `make_record(epoch_seconds: int, level: str, message: str, source_host: str) -> Tuple[int, str, str, str]` signature with full type annotations.
- Validate `source_host` as a non-empty string (non-empty string required; None or empty string raises ValueError).
- Update module docstring to reflect the new tuple shape: `(epoch_seconds, level, message, source_host)`.

**Anchor:** `src/tempo/contract.py:1-13` — the entire contract module.

**Acceptance criterion:** 
- `make_record(1700000000, 'INFO', 'message', 'myhost')` creates `(1700000000, 'INFO', 'message', 'myhost')` — 4-tuple with source_host in position [3].
- `make_record(..., '', 'msg', '')` raises ValueError (empty source_host rejected).
- `make_record(..., 'msg', None)` raises ValueError (None source_host rejected).
- Type annotations are present for all parameters and return type.
- `mypy src/` passes with no suppressions.
- Existing LEVELS validation persists (invalid level raises ValueError).

### §2 Update parser to extract source_host from input

**What changes:** Modify `src/tempo/parse.py:6-8` to:
- Expect input format `EPOCH LEVEL SOURCE_HOST MESSAGE` (split on first 3 whitespace chars).
- Extract source_host as the third whitespace-delimited token.
- Call `make_record(epoch, level, message, source_host)` in that exact parameter order (EPOCH→epoch_seconds, LEVEL→level, MESSAGE→message, SOURCE_HOST→source_host).
- Use `split(' ', 3)` to split at most 3 times, preserving MESSAGE containing spaces.

**Model-on:** `src/tempo/contract.py` — adopt the signature defined by `make_record` in §1.

**Anchor:** `src/tempo/parse.py:6-8` — the parse_line function.

**Acceptance criterion:** 
- `parse_line('1700000000 INFO myhost started')` calls `make_record(1700000000, 'INFO', 'started', 'myhost')` and yields `(1700000000, 'INFO', 'started', 'myhost')` with source_host in position [3].
- `parse_line('1700000001 WARN host message with spaces')` preserves "message with spaces" in MESSAGE field.
- `parse_line('1700000002 INFO  message')` (doubled space, missing SOURCE_HOST) raises ValueError via make_record validation.
- `mypy src/` passes.
- All tests pass (pytest tests/ -v).

### §3 Update reporter to handle 4-tuple records

**What changes:** Modify `src/tempo/report.py:6-10` to:
- Update loop unpacking from `for _, level, _ in records:` to `for _, level, _, _ in records:` (or `epoch, level, msg, host = record`).
- Ensure `count_by_level()` correctly iterates over 4-tuple records without ValueError on unpacking.
- Preserve the counting behavior (source_host does not change the counting logic, only the tuple
  shape).
- Add type annotations to accept records as a sequence of 4-tuples.

**Anchor:** `src/tempo/report.py:6-10` — the count_by_level function.

**Acceptance criterion:** 
- `count_by_level([(1700000000, 'INFO', 'message1', 'host1'), (1700000000, 'ERROR', 'message2', 'host2')])` returns `{'ERROR': 1, 'INFO': 1}`.
- Tuple unpacking handles 4-element tuples without ValueError.
- `mypy src/` passes.
- The reporter's output shape is unchanged (counts are still `{level: count}` dicts).
- All tests pass (pytest tests/ -v).

### §4 Extend tests to validate source_host field and new input format

**What changes:** Modify `tests/test_tempo.py` to:
- Add test fixtures that use the new 4-tuple structure.
- Update existing test_parse_and_count to parse input in `EPOCH LEVEL SOURCE_HOST MESSAGE` format.
- Add test_invalid_source_host to validate source_host rejection of empty string and None.
- Add test_invalid_input_format to validate parse_line rejection when SOURCE_HOST is missing.
- Ensure all tests pass against the new contract shape.

**Anchor:** `tests/test_tempo.py:12-16` — the existing test_parse_and_count test.

**Acceptance criterion:**
- test_parse_and_count: `parse_line('1700000000 INFO host1 started')` creates `(1700000000, 'INFO', 'started', 'host1')`.
- test_invalid_source_host: `make_record(..., 'msg', '')` raises ValueError; `make_record(..., 'msg', None)` raises ValueError.
- test_invalid_input_format: `parse_line('1700000000 INFO msg')` (missing SOURCE_HOST) raises ValueError.
- `pytest tests/ -v` passes all tests (100% success).
- `mypy src/` passes.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |

## Definition of Done (this spec)

Concrete, checkable conditions for the whole spec (beyond per-section criteria):

- All four numbered sections implemented per acceptance criteria.
- `pytest tests/ -v` passes (100% of tests, including new source_host tests).
- `mypy src/` passes with no suppressions.
- No tuple unpacking of records outside contract.py and tested modules.
- The record shape contract is documented in contract.py module docstring.
- Downstream consumers (external to this repo) are NOT updated in this wave — this is out of scope.

## Pre-mortem certification

*The externalized correctness pass (`pre-mortem-prompt.md`), certified by a fresh
reviewer who did NOT author this spec. `keel check-ready` does not pass until the
verdict is `CERTIFIED` (ADR-0002).*

- **Reviewer:** pre-mortem-review agent (general-purpose)
- **Verdict:** CONDITIONAL-CERTIFY (5 MAJOR issues identified; fixes applied below)
- **Operator:** (not required; fixes are surgical amendments to acceptance criteria)
- **Certification artifact:** spec-add-source-host-field.premortem.md
- **Date:** 2026-07-16
- **Reviewed against:** tempo main branch HEAD (contract.py 3-tuple, parse.py, report.py, test_tempo.py)
- **Post-fold coherence:** all 5 MAJOR findings addressed via amendments to §1–§4 acceptance criteria; no scope changes required
- **Failure modes considered & folded in:** FM-2 (parameter order), FM-3 (type annotations), FM-4 (validation location), FM-5 (test coverage), FM-6 (split maxsplit)

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|
| FM-2: Parser parameter order | §2 | spec-add-source-host-field.md:100 |
| FM-3: Type annotations | §1 | spec-add-source-host-field.md:81 |
| FM-4: Validation location | §1 | spec-add-source-host-field.md:89 |
| FM-5: Empty source_host test | §4 | spec-add-source-host-field.md:145 |
| FM-6: split() maxsplit | §2 | spec-add-source-host-field.md:101 |

---
*This template is structured so that most of the deterministic Definition-of-Ready
checks (`definition-of-ready.md`) pass by construction: numbered sections,
per-section acceptance criteria, the concept→module map, and the PR↔section
manifest are all required fields. The one field NOT satisfied by construction is the
pre-mortem certification — a non-author reviewer must sign it, which is the point
(ADR-0002).*

<!-- keel kit X.Y.Z -->
