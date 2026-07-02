# Contributing to keel

keel improves by dogfooding its own "close the loop" principle on itself.

## The loop

1. **Feedback in** — each application of keel drops a report in `docs/feedback/<date>-<source>.md`
   (format in `docs/feedback/README.md`).
2. **Triage** — cluster reports by underlying cause (`src/keel/templates/reflection-triage.md`).
3. **Promote** each recurring / high-cost trap to exactly one home:
   - a **template / doctrine** edit (`src/keel/templates/`, `docs/doctrine.md`),
   - a **new / upgraded gate** (`src/keel/`, wired in `cli.py`, tested),
   - or an **ADR** (`docs/adr/`).
4. **Record** in `CHANGELOG.md` and **bump SemVer**.

## Gate health (closing the loop)

So "a bug bites once", these hold. Be honest about which are machine-enforced and which are
maintainer disciplines — the repo should not claim enforcement it does not ship (its own A10
gate exists to catch exactly that over-claim in a spec):

1. **Every promoted gate ships a regression test** that fails on the originating defect and
   passes after the fix — no gate lands without the test that proves it bites. *Machine-enforced:*
   the suite (and CI) runs it; the version-consistency and cli-reference-coverage tests are the
   same idea applied to cross-artifact drift.
2. **A tool-wrapping gate asserts the tool ran to completion**, not just error-count ≤
   baseline (a fatal early-exit emits fewer errors and would false-pass). *Machine-enforced where
   the gate is wired.*
3. **Track each gate's hit-rate** — a gate that has fired zero times across N series is a triage
   input: sharpen it, or cut it as decayed ritual. *Maintainer discipline, not yet mechanized:*
   there is no hit-rate ledger in the tree today; treat this as a review question, not a guarantee.
4. **Reflection-triage should gate the next series** — recurring traps promoted before the next
   DoR. *Maintainer discipline, not yet mechanized:* `check-ready` does not read a triage state, so
   nothing blocks a spec on an untriaged backlog; the operator holds this by hand.

## Quality gates (Definition of Done)

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check src
uv run pytest
```

All green before merge. keel holds itself to the gates it preaches.
