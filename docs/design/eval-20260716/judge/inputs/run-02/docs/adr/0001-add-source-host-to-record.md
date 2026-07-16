# ADR-0001 — Add source-host field to record contract

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

The tempo record contract currently represents each log record as a 3-tuple:
`(epoch_seconds, level, message)`. As the toolkit scales to handle multi-host
logging, we need to track the originating host for each record — both for 
reporting aggregation ("logs from which hosts?") and for operational debugging
("where did this log come from?").

The contract is imported by:
- The parser module (`parse.py`) — creates records
- The reporter module (`report.py`) — consumes records
- External consumers (not in this repo but real) — also consume records

Any change to the record tuple shape is a breaking change for all consumers.

## Decision

We add a fourth field, `source_host`, to the record tuple, making it:
`(epoch_seconds, level, message, source_host)`.

The `make_record()` factory function will require `source_host` as a parameter.
The parser will extract it from the log input line. The reporter will ignore it
(for backward compatibility of its output format). External consumers will have
to update their code to unpack the 4-tuple instead of 3.

## Alternatives considered

- **Option A (Namedtuple):** Use `collections.namedtuple` instead of a plain tuple.
  - Rejected: adds a class-level dependency, complicates external consumers who
    expect a bare tuple, and doesn't buy us much beyond explicit field names
    (which can live in comments).
- **Option B (Dict/attrs):** Switch to a dict or attrs class.
  - Rejected: external consumers are accustomed to tuple unpacking; dict/attrs
    would break their code more severely. This is a minimal expansion, not a
    redesign.
- **Option C (Keep tuple, extend later):** Keep the 3-tuple and pass source_host
  separately through a parallel channel.
  - Rejected: creates a coordination problem across the codebase and two sources
    of truth for a single logical record.

## Consequences

- **Parser:** must extract source_host from input (format TBD per-phase).
- **Reporter:** must handle the 4th field (unpack it, but may ignore or log it).
- **External consumers:** must update their unpacking code to handle 4 fields.
- **This is a breaking contract change:** requires coordination across PRs and
  forces a version bump or deprecation path for external consumers.
- **Invariant created:** "Every record is a 4-tuple with the 4th field being a
  non-empty string (the source host)" — this will be enforced by make_record()
  and checked by the gate commands.
