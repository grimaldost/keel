# Spec — Add `source_host` to the tempo record contract

- **Date:** 2026-07-16
- **Status:** draft
- **Audience:** the tempo maintainer, and the per-PR implementation subagents for PR01-PR06 of the source-host refactor wave
- **Output artifact(s):** `src/tempo/contract.py`, `src/tempo/parse.py`, `src/tempo/report.py`, `tests/test_tempo.py`, `CHANGELOG.md`
- **Phases:** Decide + Specify + Decompose (this round). Route & Budget, Implement, Gate, Review, and Reflect are deferred to the execution wave — not run in this round, and this spec does not implement any of its own six sections.

## Context

`src/tempo/contract.py:1-5` defines the record shape shared by the parser, the reporter, and
external consumers: `"""The shared record contract: every tempo record is (epoch_seconds,
level, message). Imported by parse.py, report.py, and external consumers - changing this
tuple shape or the LEVELS set is a breaking contract change. """`. We need every record to
also carry the host it came from. Because the tuple shape is a shared, additive contract with
an unknown number of external consumers, this cannot land atomically — `docs/adr/0001-source-host-field.md`
records the decision to use the expand/contract (parallel change) pattern instead, and this
spec decomposes that decision into the six single-concern PRs of the wave.

## Goal

Add a `source_host` field to every tempo record via the expand/contract pattern
(`docs/adr/0001-source-host-field.md`), migrating the parser, the reporter, and (via a
documented migration window) external consumers, across the six sections below, without
breaking any 3-tuple consumer during the transition.

## Gate commands

`python3 -m unittest discover -s tests` — per `AGENTS.md:4` `python3 -m unittest discover -s tests`.
This is the only deterministic gate configured in this project; there is no ruff/mypy/lint
config in the repo (recorded in `docs/method/method-bindings.md`), so no additional command
gates this work.

## Non-goals

- Does **not** convert the record from a bare tuple to a `NamedTuple`/dataclass — considered
  and rejected for this wave in `docs/adr/0001-source-host-field.md`'s alternatives, left as a
  possible future ADR.
- Does **not** add any new reporting capability keyed on host (e.g. a `count_by_host`
  function) — only the field itself is added; grouping/reporting by host is out of scope.
- Does **not** implement any of the six sections below — this round is Specify + Decompose
  only, per the header's `Phases` field.
- Does **not** touch the `LEVELS` closed set (`src/tempo/contract.py:7`) or level validation —
  unaffected by this change.

## Invariants touched

- **Record contract tuple shape** (`docs/adr/0001-source-host-field.md`) — the additive field
  must not break any existing 3-argument call site during the migration window; §1 protects
  this by adding a transitional default rather than an immediately-required parameter.
- **No fixed-arity positional unpack of a full record** — a new invariant created by
  `docs/adr/0001-source-host-field.md`: once `source_host` exists, a consumer must not
  destructure a record with an exact-arity pattern (e.g. `for _, level, _ in records`), since
  that raises the moment a 4-tuple record arrives. §2 migrates the one known in-repo violator.

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| record contract tuple shape | review-only | no lint rule exists in this project (see `docs/method/method-bindings.md`); enforced only by the review checklist |
| no fixed-arity positional unpack of a full record | review-only | `tests/test_tempo.py` regression test added in §4 pins the behavior, but it is a single test, not a general-purpose lint rule |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| `source_host` field + transitional `UNKNOWN_HOST` default on the record contract | `src/tempo/contract.py` |
| shape-tolerant record destructuring in the reporter | `src/tempo/report.py` |
| 4-column host parsing in the line parser | `src/tempo/parse.py` |
| regression coverage for `source_host` and the unpack invariant | `tests/test_tempo.py` |
| migration/changelog documentation for external consumers | `CHANGELOG.md` (to be created — see §5) |

## Numbered sections

### §1 Expand `make_record` with an optional `source_host` field
`src/tempo/contract.py:10-13` defines `make_record` as:
```
def make_record(epoch_seconds, level, message):
    if level not in LEVELS:
        raise ValueError(f'unknown level: {level!r}')
    return (int(epoch_seconds), level, message)
```
Add a fourth parameter, `source_host`, with a transitional default. Introduce a new
module-level constant `UNKNOWN_HOST = "unknown"` next to `LEVELS`
(`src/tempo/contract.py:7` `LEVELS = frozenset({'INFO', 'WARN', 'ERROR'})`), and change the
return to `(int(epoch_seconds), level, message, source_host)`, so every existing 3-argument
call site keeps working unchanged during the migration window (the expand step of
`docs/adr/0001-source-host-field.md`). Update the module docstring
(`src/tempo/contract.py:1-5`) to document the fourth field, the transitional default, and the
new "no fixed-arity unpack" invariant. **Acceptance criterion:** `make_record('1700000000',
'INFO', 'hi')` (3 args) and `make_record('1700000000', 'INFO', 'hi', 'host-a')` (4 args) both
return a 4-tuple whose last element is, respectively, `UNKNOWN_HOST` and `'host-a'`.

### §2 Migrate the reporter off the fixed-arity unpack
`src/tempo/report.py:8` performs `for _, level, _ in records:` — a fixed 3-tuple unpack that
raises `ValueError` on any record with more than 3 fields, so it must migrate before §1's
4-tuples reach it (this is the invariant `docs/adr/0001-source-host-field.md` creates: no
consumer may fixed-arity-unpack a full record). Change it to a shape-tolerant destructure,
`for _, level, *_ in records:`, so `count_by_level` (`src/tempo/report.py:6`) tolerates both
3- and 4-field records across the transition window. **Acceptance criterion:**
`count_by_level` returns correct per-level counts when given a mix of 3-tuple and 4-tuple
records in the same call, without raising `ValueError`.

### §3 Migrate the parser to populate real `source_host` values
`src/tempo/parse.py:1` documents the grammar as `"""Parse 'EPOCH LEVEL MESSAGE' lines into
contract records."""`, and `src/tempo/parse.py:6-8` implements it:
```
def parse_line(line):
    epoch, level, message = line.strip().split(' ', 2)
    return make_record(epoch, level, message)
```
Extend the grammar to `'EPOCH LEVEL SOURCE_HOST MESSAGE'`: split on the first three spaces
(`split(' ', 3)`) into `epoch, level, source_host, message`, and pass `source_host` through to
`make_record` (the parameter §1 adds) instead of relying on its transitional default. Update
the module docstring (`src/tempo/parse.py:1`) to document the new 4-column grammar.
**Acceptance criterion:** `parse_line('1700000000 INFO host-a started')` returns a record
whose fourth field is `'host-a'` and whose message field is `'started'`.

### §4 Add regression coverage for the new field and the unpack invariant
`tests/test_tempo.py:13-14` currently exercises `parse_line` and `count_by_level` together,
but only against the pre-existing 3-column line format:
```
        records = [parse_line('1700000000 INFO started'), parse_line('1700000001 ERROR boom')]
        counts = count_by_level(records)
```
Add a test that parses a 4-column line using the grammar §3 introduces and asserts the
resulting record's `source_host` field, and add a test that calls `count_by_level` directly
with a hand-built 4-tuple record (bypassing `parse_line`) to pin the shape-tolerant
destructure §2 introduces as a regression guard against reintroducing a fixed-arity unpack.
**Acceptance criterion:** the two new tests fail against the pre-§2/§3 code and pass once §2
and §3 land; `python3 -m unittest discover -s tests` is green.

### §5 Document the migration for external consumers
`src/tempo/contract.py:3` records that the record shape is "Imported by parse.py, report.py,
and external consumers", so this additive change — and the eventual removal of the
transitional default in §6 — must be documented outside this repo's own call sites. Create
`CHANGELOG.md` (to be created, repo root) with a dated entry naming the new `source_host`
field, the transitional `UNKNOWN_HOST` default §1 introduces, and the two-step
(optional-then-required) migration plan, explicitly naming §6 as the section that will remove
the default. **Acceptance criterion:** `CHANGELOG.md` exists, is tracked in version control,
and its newest entry names `source_host`, the `UNKNOWN_HOST` default, and §6 as the point the
default is removed.

### §6 Contract: make `source_host` required, remove the transitional default
Once §2 (reporter), §3 (parser), and §5 (external-consumer notice) have landed, remove the
transitional default `make_record` gained in §1, so `source_host` becomes a required,
explicit 4th positional argument, and remove the now-unused `UNKNOWN_HOST` constant from
`src/tempo/contract.py`. Update `src/tempo/contract.py`'s docstring to state the field is
required, completing the contract step of `docs/adr/0001-source-host-field.md`.
**Acceptance criterion:** calling `make_record` with only 3 positional arguments raises
`TypeError`, and the full test suite (`python3 -m unittest discover -s tests`) is green with
no remaining reference to `UNKNOWN_HOST`.

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
  project has no generated/mirrored/snapshot artifact directory (no `docs/api`, no committed
  lockfile, no golden-fixture directory exist in this repo), so there is nothing to
  regenerate downstream of `src/tempo/contract.py`, `src/tempo/parse.py`, or
  `src/tempo/report.py`.
- `CHANGELOG.md`'s entry lands in-wave, in §5, rather than as a terminal cleanup — satisfying
  the release-notes-in-wave requirement for the public/consumer-facing surface this wave adds.
- Every section (§1-§6) has exactly one implementing PR (PR01-PR06) per the manifest above,
  and every PR's diff is reviewed against `docs/method/review-checklist.md` before merge.

## Pre-mortem certification

- **Reviewer:**
- **Verdict:** not yet certified
- **Operator:** N/A — no CONDITIONAL-CERTIFY has been recorded for this spec.
- **Certification artifact:**
- **Date:**
- **Reviewed against:** N/A — no external dependency SHAs/versions are reasoned against in this spec.
- **Post-fold coherence:**
- **Failure modes considered & folded in:** none yet — the pre-mortem pass (`docs/method/pre-mortem-prompt.md`) has not been run. It must be run by a reviewer who did not author this spec before the `## Pre-mortem certification` block above can be filled in and the full `keel check-ready` (not `--structure-only`) gate can pass.

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|

---
*This template is structured so that most of the deterministic Definition-of-Ready
checks (`definition-of-ready.md`) pass by construction: numbered sections,
per-section acceptance criteria, the concept→module map, and the PR↔section
manifest are all required fields. The one field NOT satisfied by construction is the
pre-mortem certification — a non-author reviewer must sign it, which is the point
(ADR-0002).*

<!-- keel kit X.Y.Z -->
