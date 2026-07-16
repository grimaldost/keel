# ADR-0001 — Add `source_host` as an additive, trailing field on the record contract

- **Status:** Accepted
- **Date:** 2026-07-16

## Context

The record contract in `src/tempo/contract.py` is shared by the parser, the reporter, and
external consumers (`src/tempo/contract.py:3-4`: "Imported by parse.py, report.py, and
external consumers - changing this tuple shape or the LEVELS set is a breaking contract
change."). The upcoming multi-host deployment needs every record to carry which host emitted
it, so a `source_host` field must be added to the shared record shape. Because the exact set
of external consumers is not enumerable from this repo (the docstring names them but they live
outside it), any change to the tuple's field *order* is unauditable for breakage; a change to
its field *count* (an append) is not.

## Decision

Add `source_host` as a fourth, trailing field on the record tuple, produced by a new
keyword-only parameter on `make_record` that defaults to `None` when the caller does not
supply one: `make_record(epoch_seconds, level, message, *, source_host=None)` returning
`(int(epoch_seconds), level, message, source_host)`. The field is *appended*, not inserted —
every existing positional call (`make_record(epoch, level, message)`) keeps working
unchanged, and every existing index-based read (`record[0]`, `record[1]`, `record[2]`) keeps
returning what it always returned.

## Alternatives considered

- **Option A — prepend `source_host` as the first field** (`(source_host, epoch_seconds,
  level, message)`) — rejected. Reordering breaks every positional unpack silently: a 3-tuple
  unpack against a reordered 4-tuple either raises `ValueError` (best case) or, if a consumer
  is itself mid-migration to 4 fields in the wrong order, silently misassigns `level` and
  `message`. Strictly worse than an append for an additive-only shared contract with
  externally-unknown consumers.
- **Option B — replace the tuple with a dict or dataclass** — rejected for this wave. It is
  not additive: every consumer's access pattern (index reads, tuple unpacks) changes at once,
  which is a bigger single-PR blast radius than this wave's per-concern sections, and it
  changes more than the one thing this wave is scoped to (adding a field). Worth its own ADR
  if a future wave wants it.
- **Option C — make `source_host` a required 4th positional argument immediately** — rejected.
  It forces the parser's call site and every external consumer's call site to change in the
  same PR as the contract change, violating single-concern PRs and the additive-only framing
  that justifies running this refactor under the method (doctrine §6: "additive-only on a
  shared contract with many consumers").

## Consequences

`make_record`'s signature grows a keyword-only parameter with a default; every existing 3-arg
positional caller is unaffected by the contract PR alone. Once a producer starts passing a
real `source_host`, any consumer that unpacks a record with a *fixed-arity* pattern (e.g.
`a, b, c = record`) raises `ValueError: too many values to unpack` — this is the one call-site
class every later section (parser, reporter, external-consumer migration notes) must
specifically re-check, not just the direct-import graph. This is the "backward compatibility
during the multi-PR window" invariant the spec tracks explicitly, enforced by regression tests
covering both the pre-migration 3-field call shape and the post-migration 4-field shape until
a future wave (out of scope here) decides whether to ever make `source_host` non-optional.
