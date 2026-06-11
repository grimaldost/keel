# CLI reference

Run via `uvx --from <repo> keel <command>` or, installed, `keel <command>`.

| Command | Purpose | Exit codes | Status |
|---|---|---|---|
| `keel check-ready <spec>` | Definition-of-Ready gate (Part A + pre-mortem cert) | 0 pass, 1 fail, 2 not-runnable | **real** (0.2.0) |
| `keel bind-check <bindings>` | All method-binding slots filled | 0 / 1 / 2 | stub |
| `keel budget-drift <series> <actuals>` | Wave cost drift past threshold | 0 / 1 / 2 | stub |
| `keel init <target> [--force]` | Copy the template kit into a project | 0 ok, 2 exists | **real** |

The still-stubbed commands (`bind-check`, `budget-drift`) print an actionable message and exit 2 until their logic is implemented.
