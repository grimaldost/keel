# Spec — add a source-host field to the tempo record contract

- **Date:** 2026-07-16
- **Status:** draft
- **Audience:** tempo maintainers and any out-of-tree consumer importing `tempo.contract`
- **Output artifact(s):** `src/tempo/contract.py`, `src/tempo/parse.py`, `src/tempo/report.py`,
  `tests/test_tempo.py`, `README.md`, `CHANGELOG.md`

## Context

`src/tempo/contract.py` defines the record shape shared by the parser, the reporter, and
external consumers (`src/tempo/contract.py:3-4` `Imported by parse.py, report.py, and
external consumers - changing this tuple shape or the` / `LEVELS set is a breaking contract
change.`). The upcoming multi-host deployment needs every record to carry the host that
emitted it. ADR-0001 (`docs/adr/0001-source-host-additive-field.md`) decides *how*: append
`source_host` as a fourth, trailing, keyword-only field with a `None` default, so the field is
added without reordering or breaking any existing positional call or index-based read. This
spec sequences that decision into a wave of small, single-concern PRs across the contract, the
parser, the reporter, and the in-tree surfaces an out-of-tree consumer relies on (the compat
accessor, the README, and the CHANGELOG) — the parts of "external consumers" this repo can
actually act on, since the consumers themselves live outside it.

## Goal

Add an additive `source_host` field to the tempo record contract and thread it through the
parser and reporter, while keeping every pre-existing 3-field call shape working for the
duration of the migration, so downstream consumers can adopt the new field on their own
schedule.

## Gate commands

`python3 -m unittest discover -s tests -v` — the project's only configured gate (per
`README.md:6` and `AGENTS.md:3-4`). No linter or type-checker is configured in this repo; this
spec does not introduce one and no section below claims one runs.

## Non-goals

- Changing the `'EPOCH LEVEL MESSAGE'` text line format that `parse_line` reads
  (`src/tempo/parse.py:1`) to *carry* `source_host` in the text itself. This wave only lets a
  caller pass `source_host` as a Python argument; teaching the text format to encode it is a
  breaking wire-format change deserving its own ADR and is out of scope here.
- Making `source_host` a required (non-optional) field. It stays optional, defaulting to
  `None`, for this whole wave.
- Auto-detecting the host (e.g. via `socket.gethostname()`). `source_host` is caller-supplied
  only; no section adds host-detection code.
- Changing `LEVELS` or any level-validation behavior in `make_record`.
- Implementing any of the sections below. This spec is the plan; no code in this wave is
  written or reviewed as part of authoring it.
- Migrating actual out-of-tree consumer repositories. They are not in this tree; this wave's
  "external consumers" work is limited to the in-repo compatibility accessor, the README, and
  the CHANGELOG entry a consumer would read (§2, §6).

## Invariants touched

- **Backward-compatible 3-arg `make_record` call shape** (established by ADR-0001): every
  existing call of the form `make_record(epoch, level, message)` must keep returning a usable
  record for the whole wave.
- **No fixed-arity record unpacking left in-tree** (ADR-0001 consequences): once a producer
  populates `source_host`, any consumer that unpacks a record with a fixed 3-name pattern
  (`a, b, c = record`) raises `ValueError`; every in-tree unpack site must be found and fixed
  before this wave is done.
- **Record tuple field order and count outside this wave's declared change** (contract.py's own
  module docstring, `src/tempo/contract.py:3-4`): nothing in this wave reorders existing fields
  or changes `LEVELS`.

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| Backward-compatible 3-arg `make_record` call shape | enforced | `tests/test_tempo.py` regression test added in §5 |
| No fixed-arity record unpacking left in-tree | enforced | `src/tempo/report.py` change in §4 + regression test in §5 |
| Record tuple field order/count outside this wave's declared change | review-only | `review-checklist.md`'s "Contract shape" item |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| `source_host` field on the record contract | `src/tempo/contract.py` |
| `get_source_host` compatibility accessor | `src/tempo/contract.py` |
| Parser support for a caller-supplied `source_host` | `src/tempo/parse.py` |
| Reporter consumption of the 4-field record | `src/tempo/report.py` |
| Regression + new-field test coverage | `tests/test_tempo.py` |
| External-consumer changelog entry | `CHANGELOG.md` (to be created) |
| README contract description update | `README.md` |

## Numbered sections

### §1 Add `source_host` to the contract
Add a keyword-only `source_host=None` parameter to `make_record` in
`src/tempo/contract.py:10` `def make_record(epoch_seconds, level, message):`, and append it as
the record's fourth element in the return, changing `src/tempo/contract.py:13`
`return (int(epoch_seconds), level, message)` to also return `source_host` last. Update the
module docstring (`src/tempo/contract.py:1` `The shared record contract`) to describe the new
4-field shape and to point at ADR-0001 for the additive-field rationale. Every existing 3-arg
positional call in the repo must keep working unmodified after this section lands — this
section does not touch any call site. **Acceptance criterion:** `make_record(epoch, level,
msg)` returns a 4-tuple whose last element is `None`, and
`make_record(epoch, level, msg, source_host='h1')` returns a 4-tuple whose last element is
`'h1'`, verified by a test that exercises both call shapes.

### §2 Add a compatibility accessor for external consumers
Add `get_source_host(record)` to `src/tempo/contract.py`, returning `record[3]` when the
record has at least 4 elements and `None` otherwise, so an out-of-tree consumer that builds or
receives records without going through `make_record` (e.g. a legacy 3-tuple literal in its own
test fixtures) can read the field defensively during the migration window without touching its
own unpacking logic. Document the helper in the module docstring alongside the field
description from §1. **Acceptance criterion:** `get_source_host` returns `None` when given a
plain 3-tuple `(epoch, level, message)` and returns the fourth element when given a 4-tuple,
each covered by its own test.

### §3 Update the parser to accept a caller-supplied source host
Extend `parse_line` in `src/tempo/parse.py` (currently `src/tempo/parse.py:6`
`def parse_line(line):`) with an optional `source_host=None` parameter, forwarded to
`make_record` as its keyword argument from §1. `src/tempo/parse.py:7`
`epoch, level, message = line.strip().split(' ', 2)` and the text-splitting logic are
unchanged — this section adds a parameter, not new text parsing (per the Non-goals text-format
exclusion). **Acceptance criterion:** `parse_line(line)` returns the same records as before
this wave (now 4-tuples with `source_host` equal to `None`), and
`parse_line(line, source_host='h1')` returns a 4-tuple whose `source_host` is `'h1'`, both
covered by tests.

### §4 Update the reporter to consume the 4-field record
Fix the fixed-arity unpack in `count_by_level` — `src/tempo/report.py:8`
`for _, level, _ in records:` — which raises `ValueError: too many values to unpack` once a
producer passes a real (non-`None`) `source_host`, since every record is a 4-tuple after §1
regardless of whether `source_host` is populated. Change the loop to index or star-unpack the
level field (e.g. `for record in records: level = record[1]`), so it works uniformly for every
record `make_record` can produce. **Acceptance criterion:** `count_by_level` returns correct
per-level counts for a list of 4-tuple records with populated `source_host` values, verified by
a test using records built via `make_record(..., source_host=...)`.

### §5 Regression and new-field test coverage
Add tests to `tests/test_tempo.py` covering: (a) the pre-existing 3-arg
`make_record`/`parse_line` call path still round-trips through `count_by_level` unchanged —
the regression test enforcing the "backward-compatible 3-arg call shape" invariant; (b) a
`source_host`-populated record, produced via `parse_line(line, source_host=...)`, round-trips
through `count_by_level` correctly — the test enforcing "no fixed-arity unpacking left
in-tree"; (c) `get_source_host` from §2 against both a legacy 3-tuple and a real 4-tuple. The
existing test `tests/test_tempo.py:13`
`records = [parse_line('1700000000 INFO started'), parse_line('1700000001 ERROR boom')]` stays
green unmodified, since it already only relies on the 3-arg call shape §1 preserves.
**Acceptance criterion:** `python3 -m unittest discover -s tests -v` passes, and the test file
contains at least one distinctly-named test for the backward-compatible path (a) and at least
one for the new `source_host` path (b), plus tests for (c).

### §6 Document the contract change for external consumers
Create `CHANGELOG.md` (to be created) at the repo root with an entry naming the additive
`source_host` field, the `get_source_host` compatibility accessor, and the backward-compatible
migration window this wave establishes (per ADR-0001), so a consumer who does not read this
repo's PR history still sees the change and how to adopt it. Update `README.md`'s description
of the contract to mention the new field and the CHANGELOG. **Acceptance criterion:**
`CHANGELOG.md` exists at the repo root with an entry naming `source_host`, `get_source_host`,
and this wave, and `README.md` mentions the `source_host` field in its contract description.

*Ground factual claims with `path:line` anchors, repo-root-relative (`src/pkg/mod.py:NN`). A
backticked token on the same line right after an anchor IS its note: `check-ready` (A6)
requires it be an exact substring of that line — don't backtick prose emphasis or `...` elision
there. A bare anchor verifies only that the file and line exist; a claim-supporting anchor SHOULD
carry its note, so the gate verifies the evidence, not just the address. Cite a new ADR as
`docs/adr/NNNN-slug.md` using the next free number on your base, never a hardcoded guess.*

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |
| PR05 | §5 | yes |
| PR06 | §6 | yes |

## Definition of Done (this spec)

- Generated / mirrored / snapshot artifacts downstream of touched surfaces: none — this
  project has no generated files, golden fixtures, or lockfiles downstream of
  `contract.py`/`parse.py`/`report.py`.
- Release-notes-in-wave: §6 lands the `CHANGELOG.md` entry for this wave's new public surface
  (`source_host`, `get_source_host`) in the same wave that adds it, per the doctrine's
  release-notes-in-wave note.

## Pre-mortem certification

*The externalized correctness pass (`pre-mortem-prompt.md`), certified by a fresh
reviewer who did NOT author this spec. `keel check-ready` does not pass until the
verdict is `CERTIFIED` (ADR-0002). A freshly-scaffolded spec is, correctly, not Ready.
Save the pass's returned output to the sibling `<spec-stem>.premortem.md` (header: spec path,
date, reviewer, `Spec-hash:` from `keel spec-hash`) and name it below — `check-ready` B2 verifies
a named artifact's existence, verdict agreement, and spec-hash currency. B2 raises the cost of
forging a certification; it does not prove the pass was blind — that residual trust stays named.*

- **Reviewer:**
- **Verdict:** not yet certified
- **Operator:**
- **Certification artifact:**
- **Date:**
- **Reviewed against:**
- **Post-fold coherence:**
- **Failure modes considered & folded in:**

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|

<!-- keel kit X.Y.Z -->
