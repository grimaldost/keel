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
1a. **Every check carries a positive control** — `tests/fixtures/adversarial/` holds one realistic
   spec that fires nothing plus one minimal edit per check that must make exactly that check fire
   (set equality, not membership). A check that has never fired in the field is either sharp and
   internalised or broken, and those look identical from outside; the corpus is what tells them
   apart, and it costs a pytest run rather than a measured trial. A mutant that does NOT fire is a
   reproduced defeat, marked `xfail(strict=True)` with its mechanism — until it passes, that
   check's silence is uninformative and no keep-or-cut argument may rest on it. *Machine-enforced:*
   the suite, including a coverage assertion that every catalogued check has a control.
2. **A tool-wrapping gate asserts the tool ran to completion**, not just error-count ≤
   baseline (a fatal early-exit emits fewer errors and would false-pass). *Machine-enforced where
   the gate is wired.*
2a. **A check that reads a line window or neighbourhood is tested against the shipped template's
   own artifacts** — the 0.11.0 A10-adjacency lesson: window logic that only ever saw synthetic
   fixtures false-fires (or dozes) on the very template the kit ships. *Maintainer discipline at
   review time.*
3. **Track each gate's hit-rate** — a gate that has fired zero times across N series is a triage
   input: sharpen it, or cut it as decayed ritual. *Machine-recorded:* `keel check-ready` appends
   one line per run to a local ledger and `keel gate-health` reads it back
   (`docs/cli-reference.md`). Read it in three states, not two — a check with **no applicable
   runs** never had an opportunity and its silence says nothing in either direction; only a check
   with applicable runs and no fires is evidence of anything. The ledger records the counts; the
   disposition is still a judgement, and the standing bar for a cut is opportunity **and** a
   positive control **and** no open defeat, all three.
3a. **A measured null is scoped to what was measured.** A pre-mortem ablation found *danger
   framing* inert in agent-directed prose. That is not a licence to delete the `blast_radius:`
   field, whose text names *what else the fix reaches* — target naming, the highest-value measured
   property in that same body — nor to touch doctrine's blast-radius language, which routes a
   human's second-pass decision and was never in the study's scope. Recorded here as a
   **non-change**, with `tests/test_consumed_lines.py` pinning the field's target-naming form so
   the register cannot drift later into the thing the null was actually about.
4. **Reflection-triage should gate the next series** — recurring traps promoted before the next
   DoR. *Maintainer discipline, not yet mechanized:* `check-ready` does not read a triage state, so
   nothing blocks a spec on an untriaged backlog; the operator holds this by hand.

## Body budgets

Five budgets cover the four shipped bodies that are dispatched or read **in full** every time they are used, and each has
only ever grown — one clause per finding. Each now carries a number, enforced by
`tests/test_body_budgets.py`:

| Body | Cap (words) | Why it is capped |
|---|---|---|
| The pre-mortem directive block — the fenced prompt in `src/keel/templates/pre-mortem-prompt.md` | 2,050 | dispatched on every pre-mortem; the most expensive prompt in the surface, and since ADR-0017 the only copy of it |
| The spec-template's italic gate-contract notes (`src/keel/templates/spec-template.md`) | 500 | read by every author the scaffold reaches. Ratcheted from 925 when the duplicated notes moved to their one home |
| The bundled agent wrapper (`agents/pre-mortem-review.md`) | 550 | identity + dispatch + output contract only (ADR-0017); the directives live in the template |
| The Definition-of-Ready sheet's PROSE (`src/keel/templates/definition-of-ready.md` minus its fenced reference block) | 950 | read end-to-end at adoption and by every reviewer. Set at the measured size |
| Each entry of that sheet's reference block, per check | 61 | the block's length is a function of the CHECK CATALOGUE, not of prose discipline — a test makes a new letter mandatory there — so capping the sheet as one body made every check the gate gains cost prose budget forever. Capped per line instead, at the measured maximum: the catalogue may grow, a line may not sprawl |

The DoR caps are deliberately set where the body actually is, not where it should end up: the
remaining candidates (Part-B prose beyond the reference block, the certification framing, the
operator close) are held behind a measurement that has not run, and a cap chosen to force an
unlicensed cut would be a verdict dressed as a budget. The split into prose-and-block is a
re-aim, not a raise: the sheet measures 948 prose words and 698 block words today, and the
block half is now bounded per entry rather than in total, because a lookup table whose length
the check catalogue determines cannot also be a prose budget without one of the two winning.

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

A release bumps **nine version sites**, in one commit with the `## [x.y.z]` CHANGELOG heading
(inserted above the previous one, never replacing it): `.claude-plugin/plugin.json`,
`pyproject.toml`, `src/keel/__init__.py`, the newest `CHANGELOG.md` heading,
`agents/pre-mortem-review.md` (the agent identity line), `src/keel/templates/spec-template.md`
(the header `- **Kit:**` stamp), and `skills/apply-method/SKILL.md` are the seven the version-consistency test
asserts; `uv.lock` is the eighth — bump it with `uv lock` after `pyproject.toml`, and CI's
`uv lock --check` reds a stale committed lock. The ninth is
`src/keel/templates/core/spec-template.md`, whose stamp line is coupled to the template's by a
different test (`tests/test_core_variants.py`: every core line appears, in order, in the body it
was cut from) — bump it with the template, or the strict-subset assertion fails and the ablation
arms stop differing by deletion alone. It is not a consumer-facing site: `keel init` cannot reach
the `core/` subdirectory.

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
| The four capped bodies stay within budget | enforced | `tests/test_body_budgets.py` |
| A shipped-kit change carries a CHANGELOG entry | enforced | CI's `changelog-currency` job, on every PR |
| Every released version carries a tag | enforced where tags are present | `tests/test_release_flow.py`; it skips a checkout with no tags at all, which is what CI's default checkout is — so today this bites locally and on any clone that fetched tags |
| All method-binding slots filled (`keel bind-check`) | available, operator-run | `keel bind-check` (ADR-0018), tested in `tests/test_bindings.py` — a CLI gate run at phase start, not wired into this repo's CI |
| Wave cost drift (`keel budget-drift`) | absent | a documented stub that exits 2; its disposition is removal, sequenced behind a bound orchestrator's live measurement window (backlog KEEL-B30) |
| An edit-time invariant hook | absent | consciously unbound (`docs/method-bindings.md`); the empty `hooks.json` placeholder that claimed the slot was deleted (KEEL-B29) |
