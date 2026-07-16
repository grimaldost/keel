# ADR-0001 — Add `source_host` to the record contract via expand/contract

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

`src/tempo/contract.py:1-13` defines the record shape shared by the parser, the reporter,
and external consumers (`src/tempo/contract.py:3` — "Imported by parse.py, report.py, and
external consumers - changing this tuple shape or the LEVELS set is a breaking contract
change."). Records are a bare positional tuple `(epoch_seconds, level, message)` built by
`make_record` (`src/tempo/contract.py:10-13`).

We need to add a `source_host` field to every record so downstream consumers can attribute
a log line to the host it came from. Because the tuple shape is a shared contract with an
unknown number of external consumers, this cannot land as a single atomic change: any
consumer that destructures the full tuple by fixed arity breaks the instant the shape
changes. `src/tempo/report.py:8` already does exactly this — `for _, level, _ in records:`
is a fixed 3-tuple unpack that raises `ValueError: too many values to unpack` the moment a
4-tuple record reaches it. This is an in-repo instance of the general problem external
consumers also face, and it is why this spans a multi-PR wave rather than one PR (method
doctrine §6: "additive-only on a shared contract with many consumers").

## Decision

We extend the record contract using the **expand/contract (parallel change) pattern**:

1. **Expand** — `make_record` gains an optional `source_host` parameter (4th field, appended
   at the end) with a sentinel default, so both old 3-arg call sites and any 3-tuple-shaped
   consumer keep working during the migration window.
2. **Migrate** producers and shape-sensitive consumers one concern at a time (parser emits
   real host values; the reporter stops doing a fixed-arity unpack; external consumers are
   notified via a CHANGELOG/migration note).
3. **Contract** — once every in-repo consumer is migrated and external consumers have been
   given a documented migration window, `source_host` becomes a required, positional 4th
   field and the transitional sentinel default is removed.

`source_host` is appended as the **last** field (`(epoch_seconds, level, message,
source_host)`), not inserted before existing fields, so no existing field's position shifts
for any consumer that accesses by index rather than by full unpack.

## Alternatives considered

- **Convert the record from a bare tuple to a `NamedTuple`/dataclass in the same wave** —
  rejected for this ADR's scope. It would fix the fixed-arity-unpack fragility at the root,
  but bundling a representation change with a field addition is two concerns in one PR and a
  larger single-PR blast radius than the method's one-concern-per-PR discipline allows. Left
  as a candidate follow-up ADR, not part of this wave.
- **Insert `source_host` as the first field** — rejected. It would shift the positional index
  of `epoch_seconds`, `level`, and `message` for every consumer that accesses by index
  (`record[0]`, `record[1]`, …), which is a strictly larger blast radius than an append.
- **Pass `source_host` via an implicit side channel (thread-local / call-context) instead of
  as a record field** — rejected. It reintroduces hidden coupling that `contract.py`'s own
  docstring warns against by making the tuple shape the single explicit source of truth; an
  implicit channel would be invisible to any consumer reading the contract module alone.
- **Land the change as a single atomic PR across parser + reporter + external consumers** —
  rejected. External consumers are, by definition, outside this repo's PR boundary; an atomic
  change cannot coordinate their migration, and it violates the additive-contract discipline
  the doctrine calls out for a shared, many-consumer surface.

## Consequences

- **New invariant this ADR creates:** no record consumer may perform a **fixed-arity
  positional unpack of the full record tuple** (e.g. `epoch, level, message = record` or
  `for _, level, _ in records`). Only shape-tolerant destructuring (`epoch, level, *_ =
  record`) or field access by name/index is permitted, from the point `source_host` is
  introduced onward. This invariant is enforced review-only (no lint rule exists in this
  project); see `docs/method/method-bindings.md` for the current (absent) enforcement
  mechanism.
- Every existing fixed-arity unpack site must be migrated to shape-tolerant destructuring
  **before or in the same PR** that starts emitting 4-tuples, or it breaks immediately.
  `src/tempo/report.py:8` is the one known in-repo site; the spec names it explicitly.
- External consumers get a documented two-step migration window (optional field, then
  required) rather than an instant breaking change — easier to adopt, but it means the
  contract module carries a transitional sentinel default for the span of this wave, which
  must be explicitly removed in the wave's last PR (not left to a future cleanup that may
  never happen).
- `make_record`'s signature changes twice across the wave (optional param added, then made
  required) — this is intentional and is the wave's own justification for spanning multiple
  PRs rather than being a single-PR change.

---
*Number ADRs sequentially. Never edit an Accepted ADR's decision; supersede it with a new
ADR and set this one's status to "Superseded by ADR-MMMM".*
