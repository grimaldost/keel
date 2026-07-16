# ADR-0001 — add `source_host` to the record contract via expand/contract, not a breaking bump

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

`src/tempo/contract.py:1-4` documents the record contract as a fixed 3-tuple —
`(epoch_seconds, level, message)` — and states plainly that "changing this tuple
shape ... is a breaking contract change." `src/tempo/parse.py:6-8` (`parse_line`)
and `src/tempo/report.py:6-10` (`count_by_level`) both construct or destructure that
exact shape, and the module docstring records that external consumers import the
contract too, so any shape change is felt outside this repository as well as inside
it.

We need to add a `source_host` field to every record so downstream consumers can
attribute a log line to the host that emitted it. Because the contract is imported
by the parser, the reporter, and consumers we do not control in this repository, a
single-PR breaking change is not viable: every consumer would need to update in
lockstep with no rollback window. This decision record exists because the rollout
shape (single breaking bump vs. staged expand/contract) has non-obvious trade-offs
and later code (every future PR touching `contract.py`) must respect whichever
invariant we pick.

## Decision

We add `source_host` using the expand/contract (parallel-change) pattern, staged
across the wave this ADR accompanies:

1. **Expand:** `make_record` gains a `source_host` parameter with a default
   sentinel (so existing 3-arg callers keep working unchanged) and the returned
   tuple grows to `(epoch_seconds, level, message, source_host)`.
2. **Migrate:** the parser and reporter are updated to produce/consume the 4-tuple;
   external consumers are given a migration window in which both the old
   (positional, 3-field-shaped read) and new reads keep working because the
   appended field is additive and the default keeps old call sites valid.
3. **Contract:** once consumers have migrated, the default sentinel is removed and
   `source_host` becomes a required, explicit argument — closing the window and
   making the 4-tuple the one true shape.

The tuple shape (`LEVELS` frozenset, positional field order) remains the invariant
this ADR governs: the ordering `(epoch_seconds, level, message, source_host)` is
fixed once step 1 lands, and no later PR may reorder it or make `source_host`
optional again without superseding this ADR.

## Alternatives considered

- **Single breaking bump (flip the tuple shape in one PR).** Rejected: every
  consumer of `contract.py` — inside and outside this repository — would need to
  update atomically, with no window to migrate and no rollback path if a consumer
  is missed. Directly contradicts the "additive-on-a-shared-contract" handling the
  method calls for.
- **Replace the tuple with a dataclass / NamedTuple.** Rejected for this wave:
  it would change both the shape AND the access pattern (attribute vs. positional
  unpacking) in the same step, doubling the blast radius for every consumer and
  making the migration non-additive. Left as a possible future ADR once the field
  itself has landed.
- **New parallel function (`make_record_v2`) instead of extending `make_record`.**
  Rejected: it forks the contract into two call paths that must be kept in sync by
  hand, and does not converge — expand/contract converges to one shape by design.

## Consequences

- **Easier:** existing 3-arg call sites keep working during the migration window;
  each PR in the wave stays single-concern (expand, then migrate each consumer,
  then contract) instead of one atomic flag-day change.
- **Harder:** the contract carries a temporary default sentinel during the
  migration window, so `make_record`'s signature is not "clean" until the
  contract-phase PR lands; two call shapes (3-arg and 4-arg) are simultaneously
  valid for the duration of the wave and reviewers must check which phase a given
  PR is in.
- **New invariant:** once the expand phase lands, every record is a 4-tuple
  `(epoch_seconds, level, message, source_host)` in that fixed order — any code
  that destructures records positionally (as `report.py` does today) must be
  updated in the same PR that changes what it destructures, and no PR after the
  contract phase may reintroduce a 3-tuple or reorder the fields.
