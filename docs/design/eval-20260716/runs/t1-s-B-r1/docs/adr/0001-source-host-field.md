# ADR-0001 — Extend the record contract with a source-host field, phased

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

`src/tempo/contract.py:1-3` documents the record shape as `(epoch_seconds, level, message)`,
a plain positional tuple, and states plainly: "changing this tuple shape or the LEVELS set is
a breaking contract change." `make_record` (`src/tempo/contract.py:9-12`) constructs it;
`parse.py:6-8` constructs records from log lines; `report.py:8` consumes records via a
fixed-arity unpack (`for _, level, _ in records:`); and the contract's own docstring names
"external consumers" as import-time dependents beyond this repo.

We need every record to carry a `source_host` field. Because the contract is shared by the
parser, the reporter, and consumers outside this repo, and the change is expected to land
across 6+ PRs, a single flag-day change that breaks every consumer atomically is not viable —
the rollout must be sequenced so each PR stays reviewable and single-concern, and no PR in the
middle of the wave leaves the tree in a state where `report.py` raises on every call.

## Decision

We extend `make_record` to accept a fourth, trailing parameter, `source_host`, defaulting to
`None` for the duration of the rollout. The reporter is migrated off fixed-arity tuple
unpacking (index/slice access instead) *before* the contract's arity changes under it, so the
two changes are decoupled and can land in independent, reviewable PRs. Only once every
in-repo consumer no longer depends on 3-arity does `source_host` become a required positional
argument (no default), completing the cutover. External consumers (per the contract's own
docstring) are notified via a CHANGELOG entry landed in the same wave as the shape change
(release-notes-in-wave).

## Alternatives considered

- **Insert `source_host` as the first field** (`host, epoch, level, message`) — rejected: it
  silently reorders every existing positional access, including already-migrated callers,
  which is a strictly worse blast radius than appending a trailing field.
- **Ship the new arity in one atomic PR** across contract + parser + reporter + tests —
  rejected: collapses the wave into a single non-reviewable mega-change, defeats the
  one-concern-per-PR discipline this wave exists to buy, and forces every downstream consumer
  to migrate in lockstep with this repo's release instead of on their own schedule.
- **Represent a record as a dict or dataclass** instead of a tuple — rejected: an out-of-scope
  shape change beyond "add a field"; keeps the tuple-contract invariant the docstring already
  names, and stays additive rather than a rewrite.

## Consequences

- New invariant this ADR creates: **no in-repo consumer of a contract record unpacks it at
  fixed arity.** A positional `for _, level, _ in records:` breaks the instant the tuple gains
  a 4th element, so every consumer must move to index/slice access strictly before (or in the
  same PR as) the arity change that would otherwise break it. This is the invariant the spec's
  section ordering exists to protect, and the one a reviewer should check first on every PR in
  this wave.
- `source_host` defaults to `None` during the rollout and becomes a required positional
  argument only in the cutover section; any PR touching `make_record`'s signature must state
  which of the two states (optional vs. required) it targets, so a PR can't silently jump the
  sequence.
- External consumers must be notified in the CHANGELOG in the same wave that changes the shape
  they depend on — a shape change with no release note is, from the outside, an unannounced
  breaking change even when it is internally sequenced.
- `LEVELS` and the `ValueError` validation in `make_record` are unaffected — this ADR touches
  only the record's arity/fields, not its level-validation invariant.

---
*Number ADRs sequentially. Never edit an Accepted ADR's decision; supersede it with a new ADR
and set this one's status to "Superseded by ADR-MMMM".*
