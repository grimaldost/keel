# Spec — Add source-host field to record contract

- **Date:** 2026-07-16
- **Status:** draft
- **Audience:** developers authoring the refactor PRs; reporters consuming this change
- **Output artifact(s):** updated `src/tempo/contract.py`, `src/tempo/parse.py`, `src/tempo/report.py`, `tests/test_tempo.py`, and a migration guide for external consumers

## Context

The tempo record contract (imported by parse.py, report.py, and external consumers)
currently defines records as 3-tuples: `(epoch_seconds, level, message)`. As multi-host
logging becomes a requirement, we need to track the originating host for each record.

This work is guided by ADR-0001, which established the decision to extend the tuple
to 4 fields: `(epoch_seconds, level, message, source_host)`.

## Goal

Add a `source_host` field (the fourth element) to every tempo record, updating the contract,
the parser to extract it from input, the reporter to handle it, and all tests to use the new
4-tuple format. External consumers will be notified of this breaking change via migration guide.

## Gate commands

- `python3 -m unittest discover -s tests -v` — all unit tests must pass
- `python3 -m py_compile src/tempo/*.py` — all source files must compile without syntax errors

## Non-goals

- Implementing external consumer updates (out-of-scope; they own their code)
- Changing the reporting output format (source_host is logged but does not change report output)
- Adding version negotiation or compatibility shims (this is a straightforward breaking change)
- Defining the input line format for source_host (that is §2's job; this spec does not mandate it)

## Invariants touched

| Invariant | Status | Gate/mechanism |
|---|---|---|
| Record tuple shape | enforced | unit tests verify 4-tuple structure; make_record() enforces it |
| Contract import correctness | enforced | Python compilation gate catches import errors |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| source_host field (new) | `src/tempo/contract.py` |
| source_host extraction | `src/tempo/parse.py` |
| source_host handling in reports | `src/tempo/report.py` |

## Numbered sections

Each section is one PR in the refactor series.

### §1 Update contract.py to add source_host parameter

Update `src/tempo/contract.py:10` to modify the `make_record()` function signature to accept a
4th parameter `source_host`, and validate that it is a non-empty string. The record
tuple returned must be a 4-tuple `(int(epoch_seconds), level, message, source_host)`.

The LEVELS constant remains unchanged.

**Acceptance criterion:** `make_record(1700000000, 'INFO', 'test', 'host1')` returns
a 4-tuple where the 4th element is the string `'host1'`; calling `make_record()` with
an empty string for source_host raises ValueError.

### §2 Update parse.py to extract and pass source_host

Update `src/tempo/parse.py:6` to modify the `parse_line()` function to extract a source_host value
from the input line (format to be determined by this PR's implementation) and pass it
to `make_record()` as the 4th argument.

The parser must handle a source_host that is present in every log line (no default fallback).

**Acceptance criterion:** Given an input line with an embedded source_host field,
`parse_line()` returns a 4-tuple record where the 4th element matches the extracted host.

### §3 Update report.py to handle 4-tuple records

Update `src/tempo/report.py:6` to modify the `count_by_level()` function to correctly unpack the 4-tuple
records (currently it unpacks 3-tuple). The function's logic and output format remain
unchanged — it still counts by level, ignoring the source_host field.

**Acceptance criterion:** `count_by_level([record1, record2])` where each record is a 4-tuple
correctly iterates and counts by the level field (2nd element), producing the same output
counts as before (unchanged format).

### §4 Update tests to use new 4-tuple format

Update `tests/test_tempo.py:13-14` to modify test_parse_and_count() to create records using the new
4-tuple format. Each parse_line() call must now include a source_host in the input, and the
test must verify that the returned record is a 4-tuple with the correct source_host.

**Acceptance criterion:** All tests pass; the test_parse_and_count test creates records with
source_host and asserts that they are 4-tuples.

### §5 Document breaking change for external consumers

Create a migration guide document (`docs/MIGRATION.md`) that explains the 4-tuple change,
shows before/after code examples, and instructs external consumers on how to update their
unpacking code. The guide must cite this spec's URL and ADR-0001.

**Acceptance criterion:** The file `docs/MIGRATION.md` exists and contains clear before/after
examples showing the unpacking change from 3-tuple to 4-tuple.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |
| PR05 | §5 | yes |

## Definition of Done (this spec)

- No generated artifacts downstream (the change is source-code only, no lockfiles or config)
- Migration guide for external consumers is in the wave (§5)
- All gate commands pass on the combined PRs
