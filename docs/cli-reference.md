# CLI reference

Run via `uvx --from <repo> keel <command>` or, installed, `keel <command>` — or
`python -m keel <command>` where an application-control policy blocks the
console-script executable.

| Command | Purpose | Exit codes | Status |
|---|---|---|---|
| `keel check-ready <spec> [--structure-only]` | Definition-of-Ready gate (Part A + pre-mortem cert); `--structure-only` runs Part A only, for the author loop | 0 pass, 1 fail, 2 not-runnable | **real** |
| `keel new-spec <target> [--force]` | Stamp `spec-template.md` to a new spec path (the author on-ramp) | 0 ok, 2 exists | **real** |
| `keel init <target> [--force]` | Copy the full template kit into a project | 0 ok, 2 exists | **real** |
| `keel bind-check <bindings>` | All method-binding slots filled | 0 / 1 / 2 | stub |
| `keel budget-drift <series> <actuals>` | Wave cost drift past threshold | 0 / 1 / 2 | stub |
| `keel --version` | Print the installed keel version and exit | 0 | **real** |

`check-ready` exit 2 (not-runnable) covers a missing path, a directory, and an undecodable
(non-UTF-8) spec — distinct from exit 1, which means the spec has real violations.

The still-stubbed commands (`bind-check`, `budget-drift`) print an actionable message and exit 2
until their logic is implemented (deferred, ADR-0003).

*This table is pinned by `tests/test_cli.py` — every registered command appears here.*
