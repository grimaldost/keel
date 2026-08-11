# CLI reference

Run via `uvx --from <repo> keel <command>` or, installed, `keel <command>` — or
`python -m keel <command>` where an application-control policy blocks the
console-script executable.

| Command | Purpose | Exit codes | Status |
|---|---|---|---|
| `keel check-ready <spec> [--structure-only]` | Definition-of-Ready gate (Part A + pre-mortem cert); `--structure-only` runs Part A only, for the author loop | 0 pass, 1 fail, 2 not-runnable | **real** |
| `keel spec-hash <spec>` | Print the canonical certification hash (the spec minus its certification section and its header `Status:` line) — what a saved pre-mortem artifact records as `Spec-hash:` (B2) | 0 ok, 2 not-runnable | **real** |
| `keel new-spec <target> [--force]` | Stamp `spec-template.md` to a new spec path (the author on-ramp) | 0 ok, 2 exists | **real** |
| `keel init <target> [--force]` | Copy the full template kit into a project | 0 ok, 2 exists | **real** |
| `keel bind-check <bindings>` | All method-binding slots filled | 0 / 1 / 2 | stub |
| `keel budget-drift <series> <actuals>` | Wave cost drift past threshold | 0 / 1 / 2 | stub |
| `keel --version` | Print the installed keel version and exit | 0 | **real** |

`check-ready` exit 2 (not-runnable) covers a missing path, a directory, and an undecodable
(non-UTF-8) spec — distinct from exit 1, which means the spec has real violations.

**The hash's scope is pinned per gate MINOR**, exactly as W1's kit-skew semantics are. Changing
what `spec_hash` covers invalidates every `Spec-hash:` already recorded in a saved pre-mortem
artifact, which surfaces as a one-time wave of W5 "certified against an earlier revision"
warnings — expected, not a defect, and re-recorded by re-running `keel spec-hash` on the current
spec. 0.14.0 → next minor is such a change: the header `Status:` line left the hashed span, so
that W2's advice ("update the Status field") stopped invalidating the certification the same run
had just verified.

The still-stubbed commands (`bind-check`, `budget-drift`) print an actionable message and exit 2
until their logic is implemented (deferred, ADR-0003).

*This table is pinned by `tests/test_cli.py` — every registered command appears here.*
