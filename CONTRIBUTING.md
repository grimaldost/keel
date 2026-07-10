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
2a. **A check that reads a line window or neighbourhood is tested against the shipped template's
   own artifacts** — the 0.11.0 A10-adjacency lesson: window logic that only ever saw synthetic
   fixtures false-fires (or dozes) on the very template the kit ships. *Maintainer discipline at
   review time.*
3. **Track each gate's hit-rate** — a gate that has fired zero times across N series is a triage
   input: sharpen it, or cut it as decayed ritual. *Maintainer discipline, not yet mechanized:*
   there is no hit-rate ledger in the tree today; treat this as a review question, not a guarantee.
4. **Reflection-triage should gate the next series** — recurring traps promoted before the next
   DoR. *Maintainer discipline, not yet mechanized:* `check-ready` does not read a triage state, so
   nothing blocks a spec on an untriaged backlog; the operator holds this by hand.

## Release discipline

A post-certification change to an open release lands as a **spec amendment section** (a new or
amended `### §N` with its own acceptance criterion), never as an unnumbered rider on the release
commit — the coordinate system stays current (doctrine sharpening 2), and every shipped behavior
change keeps a numbered section a commit can cite. (The 0.11.0 release itself broke this once —
the A10 adjacency fix rode the release commit with tests but no §; panel ARCH-8.)

The release pre-mortem's record states whether the cross-vendor enrichment panel (standing
non-blocking practice since 0.9.0) ran; skipping it stays legal but is a recorded decision, not an
omission — the 0.12.0 release skipped it silently and nothing flagged the empty slot.

A release bumps **eight version sites**, in one commit with the `## [x.y.z]` CHANGELOG heading
(inserted above the previous one, never replacing it): `.claude-plugin/plugin.json`,
`pyproject.toml`, `src/keel/__init__.py`, the newest `CHANGELOG.md` heading,
`agents/pre-mortem-review.md` (the agent identity line), `src/keel/templates/spec-template.md`
(the kit stamp), and `skills/apply-method/SKILL.md` are the seven the version-consistency test
asserts; `uv.lock` is the eighth — bump it with `uv lock` after `pyproject.toml`, and CI's
`uv lock --check` reds a stale committed lock.

## Quality gates (Definition of Done)

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check src
uv run pytest
```

All green before merge, and run them **unpiped** — a pipe (`| tail -1`) substitutes the filter's
exit status for the gate's, so a red gate reads green. keel holds itself to the gates it preaches.
