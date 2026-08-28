# CLI reference

Run via `uvx --from <repo> keel <command>` or, installed, `keel <command>` — or
`python -m keel <command>` where an application-control policy blocks the
console-script executable.

| Command | Purpose | Exit codes | Status |
|---|---|---|---|
| `keel check-ready <spec> [--structure-only]` | Definition-of-Ready gate (Part A + pre-mortem cert); `--structure-only` runs Part A only, for the author loop | 0 pass, 1 fail, 2 not-runnable | **real** |
| `keel spec-hash <spec>` | Print the canonical certification hash (the spec minus its certification section and its header `Status:` line — an `## Amendment` section is NOT removed, so an amendment still moves the hash; B2 recomputes without it to tell an addition from an edit, W7) — what a saved pre-mortem artifact records as `Spec-hash:` (B2) | 0 ok, 2 not-runnable | **real** |
| `keel re-anchor <spec> [--check] [--body]` | Repoint drifted anchors from the snippets that identify them. The fold ledger by default — it sits inside the span `spec-hash` removes, so the repair cannot invalidate the certification it serves; `--body` also rewrites prose anchors and says that the hash moves. A weak snippet, a range anchor, or a snippet on no line is reported and left alone | 0 | **real** |
| `keel new-spec <target> [--force]` | Stamp `spec-template.md` to a new spec path (the author on-ramp) | 0 ok, 2 exists | **real** |
| `keel gate-health [--since] [--repo]` | Read back the local hit-rate ledger: per check, applicable runs / distinct revisions it fired on / causes / fire rate, split by author-loop vs full-gate runs | 0 | **real** |
| `keel show <name> [--list]` | Print a body from the serving kit — `checks` (the Part-A reference block), `directive` (the dispatched pre-mortem prompt), or any template by stem. A projection read at run time, never a copy, so it cannot drift from the shipped file | 0 ok, 2 unknown name | **real** |
| `keel init <target> [--force]` | Copy the full template kit into a project | 0 ok, 2 exists | **real** |
| `keel bind-check <bindings>` | Every portability slot in a method-bindings sheet is bound to something concrete. The binding column is resolved by HEADER (`This project` when the table has one, else the last column), and `not bound — <reason>` WARNs rather than fails — a named deferral is a decision, a blank is a gap (ADR-0018) | 0 ok, 1 unbound, 2 no sheet | **real** |
| `keel survey <dir>` | Sweep a design directory: which spec-shaped documents carry no certification? Spec-shaped means a numbered-sections or PR-manifest heading; triage docs, ADR drafts, pre-mortem artifacts and registers are listed and never counted | 0 ok, 1 an uncertified spec, 2 not a directory | **real** |
| `keel budget-drift <series> <actuals>` | Wave cost drift past threshold | 0 / 1 / 2 | stub |
| `keel --version` | Print the installed keel version and exit | 0 | **real** |

`check-ready` exit 2 (not-runnable) covers a missing path, a directory (use `keel survey` for
a directory) and an undecodable (non-UTF-8) spec — distinct from exit 1, which means the spec
has real violations.

An anchor that leaves the repository (`../sibling/path.py:12`) resolves normally when the
sibling is checked out beside this repo. When it is not, it FAILS rather than falling back to
the basename search: expanding it would repoint the citation at an unrelated in-repo file of
the same name and warn that the expansion is unique, which reads as resolved.

## The gate hit-rate ledger

`keel check-ready` appends one JSONL line per run to a **local** ledger, and `keel gate-health`
reads it back. It records ids, counts, verdict buckets and hashes — never spec text: the writer
only accepts fields that are ints, bools, closed enums, hex digests or slugs, so a free-text field
is unrepresentable, and the spec is identified by a digest because stems name a project's roadmap.
Nothing is uploaded.

Location, in order: `$KEEL_GATE_LEDGER` → `$XDG_STATE_HOME/keel/gate-ledger.jsonl` →
`~/.keel/gate-ledger.jsonl`. **Set `KEEL_GATE_LEDGER=off` to disable it.** It is user-level rather
than per-repo on purpose: the question a hit-rate answers is how a check behaves across every repo
it runs in, and one repo rarely holds enough specs to answer it.

Each check reports three states, not two — `candidates == 0` means no construct of that shape was
present (**n/a**), `candidates > 0` with no fires means the check looked and found nothing
(**clean**), and only the second is evidence. Writing is fail-open: a full disk or a read-only
home changes what is recorded and never the 0/1/2 exit codes.

**The hash's scope is pinned per gate MINOR**, exactly as W1's kit-skew semantics are. Changing
what `spec_hash` covers invalidates every `Spec-hash:` already recorded in a saved pre-mortem
artifact, which surfaces as a one-time wave of W5 "certified against an earlier revision"
warnings — expected, not a defect, and re-recorded by re-running `keel spec-hash` on the current
spec. 0.14.0 → 0.15.0 is such a change: the header `Status:` line left the hashed span, so
that W2's advice ("update the Status field") stopped invalidating the certification the same run
had just verified.

The still-stubbed commands (`bind-check`, `budget-drift`) print an actionable message and exit 2
until their logic is implemented (deferred, ADR-0003).

*This table is pinned by `tests/test_cli.py` — every registered command appears here.*
