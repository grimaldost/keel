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
4. **Record** in `CHANGELOG.md` and **bump SemVer**. *Machine-enforced:* a PR whose diff touches a
   shipped-kit path (`src/keel/templates/**`, `docs/doctrine.md`, `agents/**`, `skills/**`,
   `commands/**`) while `CHANGELOG.md` stays untouched fails CI's `changelog-currency` job
   (`scripts/changelog_currency.py`). The version lock proves the eight sites agree, never that
   any of them moved — this is the complement, and an unrecorded promotion is uncountable.

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

## Body budgets

Three shipped bodies are dispatched or read **in full** every time they are used, and each has
only ever grown — one clause per finding. Each now carries a number, enforced by
`tests/test_body_budgets.py`:

| Body | Cap (words) | Why it is capped |
|---|---|---|
| The pre-mortem directive block — the fenced prompt in `src/keel/templates/pre-mortem-prompt.md` | 2,050 | dispatched on every pre-mortem; the most expensive prompt in the surface, and since ADR-0017 the only copy of it |
| The spec-template's italic gate-contract notes (`src/keel/templates/spec-template.md`) | 925 | read by every author the scaffold reaches — 64 of the template's 185 lines |
| The bundled agent wrapper (`agents/pre-mortem-review.md`) | 550 | identity + dispatch + output contract only (ADR-0017); the directives live in the template |

The rule the caps enforce: **a promotion that adds prose to one of these bodies names the one it
displaces or merges into**, in the CHANGELOG entry that ships it. That rule was already stated and
was already failing — the drift guard's marker count went 22 → 33 → 34 across six ADRs, one clause
per finding — because nothing made the cost visible at edit time. A cap is not a target: an edit
that lands under it still owes the displacement.

Raising a cap is a recorded decision with its reason in the CHANGELOG, not the way to make a red
suite green. And the directive body carries one further constraint: **net-new** directive prose
waits for the ablation that measures the body's marginal effect (backlog KEEL-B09); a rewrite that
displaces existing text does not.

## Release discipline

A post-certification change to an open release lands as a **spec amendment section** (a new or
amended `### §N` with its own acceptance criterion), never as an unnumbered rider on the release
commit — the coordinate system stays current (doctrine sharpening 2), and every shipped behavior
change keeps a numbered section a commit can cite. (The 0.11.0 release itself broke this once —
the A10 adjacency fix rode the release commit with tests but no §; panel ARCH-8.)

The release pre-mortem's record states whether the cross-vendor enrichment panel (standing
non-blocking practice since 0.9.0) ran; skipping it stays legal but is a recorded decision, not an
omission — the 0.12.0 release skipped it silently and nothing flagged the empty slot.

**A released version carries a tag.** After a release PR merges, tag the release commit on main
(`git tag vX.Y.Z <commit>`) and publish it (`git push --tags`). Without it, "which versions
actually shipped" is answerable only from memory: 0.11.1, 0.12.0, 0.13.0 and 0.13.1 all shipped
untagged and were tagged retroactively, at the release commit on main.
`tests/test_release_flow.py` asserts the rule from 0.4.0 (the first public release — 0.2.0, 0.2.1
and 0.3.0 are pre-publication history squashed into that commit, so there is nothing to tag) and
exempts the newest CHANGELOG heading, which is tagged when its release merges rather than when its
section is written.

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

Install the commit-time hook once per clone:

```bash
git config core.hooksPath .githooks
```

That points git at the tracked `.githooks/pre-commit`, which runs the first three gates through
`uv run python -m pre_commit`. `pre-commit install` is deliberately **not** the instruction: it
writes a hook that invokes the `pre-commit` console script, and an application-control policy on
at least one machine this repo is developed on blocks that shim while running git-invoked hooks
fine — so the shim form would leave the claim below as untrue as no hook at all.

### Enforcement status (the same table this repo's A10 gate demands of a spec)

A10 fails a spec whose prose claims an invariant "enforced" while its own status table marks it
planned or absent. Turned on the repo itself:

| Invariant | Status | Gate/mechanism |
|---|---|---|
| The four DoD gates hold before a merge | enforced | `.github/workflows/ci.yml`, every PR, on two OSes |
| ruff-format, ruff and `ty check src` hold before a commit lands | enforced | `.githooks/pre-commit` + `.pre-commit-config.yaml`, once `core.hooksPath` is set — a clone that skips that one command is covered by CI only |
| `uv run pytest` before a commit | review-only | CI's by choice: the one gate whose cost belongs on a push. Run it yourself before you push |
| The pre-mortem directives have one home | enforced | `tests/test_premortem_agent.py` (ADR-0017) |
| The three capped bodies stay within budget | enforced | `tests/test_body_budgets.py` |
| A shipped-kit change carries a CHANGELOG entry | enforced | CI's `changelog-currency` job, on every PR |
| Every released version carries a tag | enforced where tags are present | `tests/test_release_flow.py`; it skips a checkout with no tags at all, which is what CI's default checkout is — so today this bites locally and on any clone that fetched tags |
| All method-binding slots filled (`keel bind-check`) | absent | the command is a documented stub that exits 2 (ADR-0003; the build is backlog KEEL-B17) |
| Wave cost drift (`keel budget-drift`) | absent | a documented stub that exits 2; its disposition is removal, sequenced behind a bound orchestrator's live measurement window (backlog KEEL-B30) |
| An edit-time invariant hook | absent | consciously unbound (`docs/method-bindings.md`); the empty `hooks.json` placeholder that claimed the slot was deleted (KEEL-B29) |
