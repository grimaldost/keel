# ADR-0001 — Add source-host field to record contract

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

Tempo aggregates logs from multiple machines. The current record contract `(epoch_seconds, level, message)`
lacks a source identifier. Without it, aggregated logs cannot be traced back to their origin.
Adding a `source_host` field would enable filtering and routing by source, but requires a breaking
change to the contract that every internal consumer (parse, report) and external consumer must migrate.

## Decision

The record contract is extended from `(epoch_seconds, level, message)` to `(epoch_seconds, level, message, source_host)`.
The `source_host` is a string (hostname or identifier) passed by the caller, not auto-detected.
The `make_record()` function signature changes to accept `source_host` as a required argument.

## Alternatives considered

- **Embed source_host in message:** Rejected. Would require parsing and regex logic in consumers; opaque to the record contract.
- **Use a dict instead of tuple:** Rejected. Breaks existing code more severely; a 4-tuple is backward-compatible at the import level (still unpacks, can be accessed by index).
- **Add source_host as optional (5th element with default):** Rejected. A default hides the decision; callers must be explicit.

## Consequences

**Invariant created:** The record contract shape is `(int, str, str, str)` — epoch, level, message, source_host.
This invariant is enforced by `make_record()` and must be respected by all importers.

**Breaking changes:**
- Any code unpacking records by position must shift indices for code after the third element.
- `make_record()` requires 4 arguments instead of 3.
- Report functions unpacking records must account for the new field.

**Guardrails:** All tests must verify the new field is present and correctly propagated through parse → report → output.
