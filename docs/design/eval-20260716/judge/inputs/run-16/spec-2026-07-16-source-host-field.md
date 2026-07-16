# Spec — add `source_host` to the tempo record contract

- **Date:** 2026-07-16
- **Status:** draft
- **Audience:** engineers implementing this PR series, and the maintainers of any
  external consumer that imports `tempo.contract`
- **Output artifact(s):** `src/tempo/contract.py`, `src/tempo/parse.py`,
  `src/tempo/report.py`, `tests/test_tempo.py`, `CHANGELOG.md`

## Context

`src/tempo/contract.py:1` states the record contract plainly: every tempo record
is `(epoch_seconds, level, message)`, and `src/tempo/contract.py:3` warns that
"changing this tuple shape ... is a breaking contract change" because it is
"Imported by parse.py, report.py, and external consumers." `src/tempo/parse.py:8`
(`parse_line`) constructs a record via `make_record`, and `src/tempo/report.py:8`
(`count_by_level`) destructures records positionally as a 3-tuple.

We need to attribute every record to the host that emitted it, so downstream
tooling (and the external consumers named in the module docstring) can filter or
group by `source_host`. Because the contract is shared beyond this repository, a
single-PR breaking change is not viable — `docs/adr/0001-source-host-additive-expand-contract.md`
records the decision to roll this out as an additive expand/contract migration
instead, and this spec decomposes that migration into the PR series.

**Out-of-wave consumers:** any external consumer that reads tempo records is, by
definition, outside this repository's import graph and cannot be edited by a PR in
this series. §5 publishes the coordination artifact those consumers read to
migrate on their own schedule; §6 (the contract phase) is the mechanical flip this
repo makes once that migration window has closed. This spec does not — and
cannot — enumerate or edit those external repositories' source.

## Goal

Add a `source_host` field to every tempo record, landing it as a staged
expand → migrate → contract rollout (per `docs/adr/0001-source-host-additive-expand-contract.md`)
so the parser, the reporter, and every external consumer of `tempo.contract` can
adopt the new field without a flag-day break.

## Gate commands

`python3 -m unittest discover -s tests` — the project's one deterministic gate,
named precisely in `AGENTS.md:4` (`python3 -m unittest discover -s tests`)
and equivalently, with verbose output, in `README.md:6`
(`python3 -m unittest discover -s tests -v`). No `ruff`/`mypy`/lint configuration
exists in this project yet (per `docs/method/method-bindings.md`), so this test
command is the whole gate — every PR in the manifest below must leave it green.

## Non-goals

- Does **not** change the wire/log-line text format. `source_host` is threaded
  into `parse_line` as an explicit caller-supplied parameter (§2), not parsed out
  of the `EPOCH LEVEL MESSAGE` line text — the host is stream/file-level metadata
  a log-ingestion caller already knows, not a per-line token, so this avoids
  inventing an ambiguous fourth wire field.
- Does **not** touch `LEVELS` or the level-validation branch in `make_record`.
- Does **not** edit any external consumer's source — out of this repository's
  reach (see "Out-of-wave consumers" above); this wave publishes the migration
  guide (§5) those consumers act on, and performs the contract-phase flip (§6) on
  this repo's own side only.
- Does **not** introduce a general extra-metadata mechanism (no `**kwargs` bag on
  `make_record`) — `source_host` is the one field this wave adds.
- Does **not** replace the tuple shape with a dataclass/NamedTuple — rejected in
  `docs/adr/0001-source-host-additive-expand-contract.md` ("Alternatives
  considered") as doubling this wave's blast radius.

## Invariants touched

- **Record contract tuple shape** — the positional order
  `(epoch_seconds, level, message, source_host)` fixed by
  `docs/adr/0001-source-host-additive-expand-contract.md`. Every PR in this
  series that reads or builds a record (§1-§3, §6) must respect whatever shape is
  current after the immediately-preceding PR; no PR may reorder the fields.

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| record contract tuple shape | planned | `tests/test_tempo.py` regression test added in §4, run by `python3 -m unittest discover -s tests` |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| `source_host` field on the record contract, with a migration-window default | `src/tempo/contract.py` |
| `source_host` threaded through line parsing | `src/tempo/parse.py` |
| `source_host` consumed by the reporter (`count_by_level` unpacking, new `count_by_host`) | `src/tempo/report.py` |
| Contract-shape regression tests guarding the invariant above | `tests/test_tempo.py` |
| Migration guide / release notes for external consumers | `CHANGELOG.md` (to be created) |

## Numbered sections

### §1 Expand the contract: add `source_host` with a migration-window default
`make_record` (`src/tempo/contract.py:10` `def make_record(epoch_seconds, level, message):`,
returning `src/tempo/contract.py:13` `return (int(epoch_seconds), level, message)`) gains a
fourth parameter, `source_host`, defaulting to a documented sentinel value so every
existing 3-arg call site keeps working unchanged. The returned tuple grows to
`(epoch_seconds, level, message, source_host)`, fixing the field order
`docs/adr/0001-source-host-additive-expand-contract.md` names as the invariant.
The module docstring (`src/tempo/contract.py:1`
`The shared record contract: every tempo record is (epoch_seconds, level, message).`)
is updated to describe the 4-tuple and the migration-window default.
**Acceptance criterion:** `make_record(epoch, level, msg)` (no fourth argument)
returns a 4-tuple whose last element is the documented default sentinel, and
`make_record(epoch, level, msg, 'db01')` returns a 4-tuple whose last element is
`'db01'`.

### §2 Migrate the parser: thread `source_host` through `parse_line`
`parse_line` (`src/tempo/parse.py:6` `def parse_line(line):`, currently calling
`src/tempo/parse.py:8` `return make_record(epoch, level, message)`) gains an
explicit `source_host` parameter that it forwards to `make_record` unchanged — the
host is supplied by the caller (the process that already knows which file/stream
it is reading), consistent with the Non-goals decision not to parse it out of the
line text. Existing single-argument calls to `parse_line(line)` keep returning a
record with the §1 default sentinel as the fourth field.
**Acceptance criterion:** `parse_line('1700000000 INFO started')` still returns a
record whose fourth field is the §1 default sentinel, and
`parse_line('1700000000 INFO started', source_host='db01')` returns a record
whose fourth field is `'db01'`.

### §3 Migrate the reporter: consume the 4-tuple shape
`count_by_level` (`src/tempo/report.py:6-10` currently unpacking
`src/tempo/report.py:8` `for _, level, _ in records:`) is updated to unpack the
4-tuple shape without changing its return value, and a new `count_by_host`
function groups records by their fourth (`source_host`) field the same way
`count_by_level` groups by level.
**Acceptance criterion:** given a list of 4-tuple records with mixed hosts,
`count_by_level` returns the same per-level counts it returned before this PR,
and `count_by_host` returns a dict mapping each distinct `source_host` value to
the number of records carrying it.

### §4 Add contract-shape regression tests
`tests/test_tempo.py` (its existing case at `tests/test_tempo.py:12`
`def test_parse_and_count(self):`) gains tests that assert the 4-tuple shape and
the §1 default-sentinel behavior directly, so the "record contract tuple shape"
invariant this spec names moves from "planned" toward a machine-checked gate
instead of resting on review alone.
**Acceptance criterion:** `tests/test_tempo.py` contains at least one test
asserting `len(make_record(...)) == 4` and one asserting the default-sentinel
value from §1, and `python3 -m unittest discover -s tests` passes with both
included.

### §5 Publish the migration guide for external consumers
`CHANGELOG.md` (to be created at the repository root) gets a dated entry
documenting: the new `source_host` field and its position in the tuple, the
exact default sentinel value from §1, the caller-supplied (not line-parsed)
threading model from §2, and the condition under which §6 removes the default —
this is the coordination artifact the "Out-of-wave consumers" named in Context
read to migrate on their own schedule, since this repository cannot edit their
source directly.
**Acceptance criterion:** `CHANGELOG.md` exists at the repository root with an
entry naming the `source_host` field, its default sentinel value, and a pointer
to both this spec and `docs/adr/0001-source-host-additive-expand-contract.md`.

### §6 Contract phase: require `source_host` explicitly
Once the migration window §5 announced has closed, the default sentinel added in
§1 and threaded in §2 is removed: `make_record` and `parse_line` both require
`source_host` as an explicit argument, closing the invariant
`docs/adr/0001-source-host-additive-expand-contract.md` fixes. `count_by_level`
and `count_by_host` are unaffected (they already consume the 4-tuple shape from
§3) and continue passing against fully-specified records.
**Acceptance criterion:** calling `make_record(epoch, level, msg)` or
`parse_line(line)` without a `source_host` argument raises `TypeError`, and
`python3 -m unittest discover -s tests` — including the §4 regression tests —
still passes.

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

- Generated / mirrored / snapshot artifacts downstream of touched surfaces: none.
- Release-notes-in-wave: satisfied by §5, which lands the `CHANGELOG.md` entry in
  the same wave that introduces the `source_host` field — not deferred to a
  terminal cleanup.

## Pre-mortem certification

- **Reviewer:**
- **Verdict:** not yet certified
- **Operator:**
- **Certification artifact:**
- **Date:**
- **Reviewed against:** n/a
- **Post-fold coherence:**
- **Failure modes considered & folded in:**

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|

<!-- keel kit X.Y.Z -->
