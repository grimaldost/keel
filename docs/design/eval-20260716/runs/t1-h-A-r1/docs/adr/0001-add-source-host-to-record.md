# ADR-0001 — Add source-host field to record contract

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

The record contract (defined in `src/tempo/contract.py`) currently carries three fields:
`(epoch_seconds, level, message)`. This contract is imported by the parser (`src/tempo/parse.py`),
the reporter (`src/tempo/report.py`), and external consumers outside this repo.

Multi-host log aggregation requires knowing the source hostname of each record. Today, that
information is unavailable downstream of the parser, so reporters and external consumers cannot
correlate records to their originating host. The refactor to add this field spans ≥6 PRs across
the parser, reporter, and external-facing boundaries — a blast-radius trigger that warrants method
governance.

## Decision

We will add a `source_host` field to the record contract as the fourth element of the tuple,
yielding `(epoch_seconds, level, message, source_host)`. This is a breaking change to a
shared contract. The parser will extract it; the reporter will propagate it; external consumers
will need to adapt.

## Alternatives considered

- **Option A: Nested struct / dataclass** — More type-safe, clearer intent. Rejected: adds
  breaking complexity and loses the simplicity that makes the contract portable to external
  systems; Python dataclasses are not universally understood by non-Python consumers.
- **Option B: Add to the message field** — Encode source-host in the message string (e.g.,
  `[host] message`). Rejected: breaks the message's semantic role; ambiguous parsing; breaks
  existing regexes in consumers.
- **Option C: Defer to external mapping** — Carry records without source-host, map via a
  separate host lookup. Rejected: adds latency, complexity, and a new failure mode (lookup
  downtime severs the association).

## Consequences

- The record tuple shape changes from 3 to 4 elements. This is a breaking change to a shared
  contract imported by ≥~50 modules (the parser, reporter, and external consumers).
- Any unpacking of the tuple (e.g., `epoch, level, msg = record`) will fail at runtime until
  updated.
- The parser must extract source-host from its input; the report module must adapt its tuple
  unpacking; external consumers must update their tuple handling.
- The parser's input format must be extended to include the source-host (e.g., `EPOCH LEVEL
  SOURCE_HOST MESSAGE` instead of `EPOCH LEVEL MESSAGE`).
- **Invariant created:** The record contract MUST always be a 4-tuple with the shape
  `(int, str from LEVELS, str, str)` where the fourth element is the source hostname. Any code
  that creates, unpacks, or validates records must respect this shape.
