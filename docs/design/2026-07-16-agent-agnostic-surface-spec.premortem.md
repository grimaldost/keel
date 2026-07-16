# Pre-mortem pass — round 2 re-gate + targeted confirmatory pass (final certifying artifact, B2)

- Spec: docs/design/2026-07-16-agent-agnostic-surface-spec.md
- Date: 2026-07-16
- Reviewer: pre-mortem-review@0.13.1 (fresh subagent, round 2 — non-author)
- Spec-hash: 0792f370669f2083e2bcf47c8a19114e87ea503f11e86dfdeeb702fbcfead487
  (the spec the closing confirmatory pass re-read end to end; the round-2 re-gate body read
  82cc76ad3340b471a45befb233a60ec0467ba2af675f91d69d5e918e0506842b — the sole body delta
  between the two is the gate-prompted Status flip `draft` → `ready (DoR passed)`, confirmed
  by the pass appended at the end of this artifact)
- Prior round: docs/design/2026-07-16-agent-agnostic-surface-spec.premortem-r1.md (NEEDS-REVISION, FM-1..FM-4)

---

Grounding complete. All four prior findings audited against current text, and the fold-introduced claims re-grounded against the tree. `format_error` is a real helper (`src/keel/errors.py:4`), the typer.echo default-newline hazard is real (cli.py uses `typer.echo` throughout), the exit-2 convention exists, and every `${CLAUDE_PLUGIN_ROOT}/` path-form in the guard's scan surface maps to §4's edit set. Here is the certification artifact.

---

## Pre-mortem review — the agent-agnostic surface (any-agent keel) — ROUND 2 RE-GATE

Reviewed against: `docs/design/2026-07-16-agent-agnostic-surface-spec.md` @ working tree; the round-1 verdict record; ADR-0017; and the cited source at each anchor. I did not author this spec or its folds. I re-verified every prior finding's fold against current text, and re-grounded each NEW or REWORDED claim the fold added against the real tree.

### Resolution audit (prior findings FM-1..FM-4)

- **FM-1 (MAJOR, keel-check-ready.md path-form) — RESOLVED.** §4 now explicitly names `commands/keel-check-ready.md` in the edit set and converts its line-12 `${CLAUDE_PLUGIN_ROOT}/docs/installation.md` to `docs/installation.md` (spec §4, lines 192–196). Grounded: `commands/keel-check-ready.md:12` does carry that exact path-form; line 9 carries the surviving `uvx --from ${CLAUDE_PLUGIN_ROOT} keel check-ready $ARGUMENTS` locator (var+space, not var+slash). Sibling sweep verified: a grep of `${CLAUDE_PLUGIN_ROOT}/` across `skills/`+`commands/` returns exactly 8 path-forms in 4 files (SKILL.md ×5, triage:5, apply:6, check-ready:12) — every one falls inside §4's edit set (SKILL body rewritten; triage/apply covered by the "`…/docs/…` or `…/src/keel/templates/…`" clause; check-ready named). `keel-premortem.md` carries no path-form, consistent with §4 only ADDING a line to it. The guard's "variable followed by a slash" wording correctly spares the surviving locator form.
- **FM-2 (MINOR, stale v0.11.1 pin) — RESOLVED.** §6 now mandates the any-agent one-liner pin `v0.14.0` and explicitly forbids copying the `docs/installation.md:19` `@v0.11.1` example (spec §6, lines 232–236). Grounded: `docs/installation.md:19` does carry `@v0.11.1`; `docs/installation.md:36` does carry `uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`. Both anchors accurate.
- **FM-3 (MINOR, no wheel-build gate) — RESOLVED.** §1 test now has clause (c): builds a wheel via `uv build --wheel` subprocess and asserts `keel/method/doctrine.md` in the namelist, with the rationale that the editable install would otherwise mask a packaging regression (spec §1, lines 118–125; acceptance line 130). This is the exact gate FM-3 requested; round-1 empirically confirmed the sibling `templates/*.md` ship by the same rule.
- **FM-4 (MINOR, trailing-newline byte-equality) — RESOLVED.** §3 now specifies `keel show <asset>` writes asset text with no trailing newline (`typer.echo(..., nl=False)` or `sys.stdout.write`), citing round-1 FM-4 (spec §3, lines 165–168). Grounded: cli.py uses `typer.echo` (click's default `nl=True` appends `\n`), so the hazard was real and the fix is applicable and correct.

### New findings (fold-introduced, under the rising bar)

None. No fold silently narrowed a promoted item; each fold matches or exceeds its finding's scope. No new claim the fold added is false against the tree.

```yaml
findings: []
```

```yaml
cleared:
  - claim: "§4's path-form guard wording spares the surviving locator (no false positive that trips the guard on the intended-to-survive `uvx --from ${CLAUDE_PLUGIN_ROOT}` form)"
    cite: "guard = '${CLAUDE_PLUGIN_ROOT}/' (var+slash); every surviving locator in the tree is var+space (keel-check-ready.md:9, SKILL.md:21) — grep confirms the only var+slash hits are the path-forms in §4's edit set."
  - claim: "§4 edit set covers the FULL path-form population in the guard's scan surface, not just the exemplar"
    cite: "grep '${CLAUDE_PLUGIN_ROOT}/' over {skills,commands}/**/*.md → 8 hits across SKILL.md, keel-triage.md:5, keel-apply.md:6, keel-check-ready.md:12; all inside §4's named edits."
  - claim: "the `format_error` symbol §3 cites for the unknown-asset exit-2 path exists"
    cite: "src/keel/errors.py:4 `def format_error(*, what, why, fix)`, consumed by check_ready.py/templates.py/bindings.py/budget_drift.py — a real helper, not invented."
  - claim: "the exit-2 convention §3 assigns to an unknown asset matches the CLI's existing not-runnable convention"
    cite: "src/keel/cli.py:47-52 `_emit` raises typer.Exit(code=2) for NotImplementedError/FileNotFoundError; §3's KeyError→exit-2 translation is consistent."
  - claim: "per-PR version-site consistency holds across PR04→PR06 (SKILL version line kept, all 7 bumped in §6)"
    cite: "SKILL.md:8 'ships with keel 0.13.1' is one site; §4 keeps the version line, §6 bumps all seven in PR06 — each PR head internally consistent (round-1 clear re-verified against current §4/§6 text)."
```

### Prose

This is a clean re-gate. The one round-1 blocker (FM-1) is fully resolved with a correctly-scoped fold: the spec now names `commands/keel-check-ready.md` in §4, converts its line-12 path-form, and — critically — the fold specified the guard as the *path-form* (`${CLAUDE_PLUGIN_ROOT}/`, var+slash) rather than a bare-variable grep, which is exactly what preserves the intended `uvx --from` locator while catching every real violation. I re-ran the population sweep the fold rests on: the guard's scan surface (`skills/` + `commands/`) contains 8 path-forms across 4 files, and every one is inside §4's edit set. No sibling was missed; no surviving locator will trip the guard.

The three MINOR folds (FM-2 tag pin, FM-3 wheel-namelist gate, FM-4 no-trailing-newline) are each present, correctly anchored, and grounded against the tree — the `@v0.11.1` and `${CLAUDE_PLUGIN_ROOT}` anchors in installation.md are real, `format_error` and the exit-2 convention are real, and the typer default-newline hazard is real. None was narrowed in the fold.

Second-pass hunt for fold-introduced defects surfaced nothing decision-corrupting. The pass surfaces zero new BLOCKER/MAJOR findings, so under the convergence rule it stops. The single execution-dependent claim I could not run offline is the §1 wheel-build namelist assertion (`uv build --wheel` in a subprocess); round-1 empirically built the wheel and confirmed the identical-mechanism sibling ships, so this is a low-residual-risk gate, not an open question.

Unverified-offline: 1
PREMORTEM-VERDICT: CERTIFIED pre-mortem-review@0.13.1 (fresh subagent, round 2)

---

## Targeted confirmatory pass (same reviewer, post-certification deltas only)

Re-read the current spec `/home/user/keel/docs/design/2026-07-16-agent-agnostic-surface-spec.md` end to end (lines 1-305).

Delta confirmation, scoped to the two prompted edits:

1. Header status (line 4): now `- **Status:** ready (DoR passed)` — flipped from `draft` as described. Confirmed, no collateral change to surrounding header block (Date, Audience, Output artifacts intact).

2. Fold-ledger anchor (line 299): the FM-1 sibling-sweep row now reads `...agent-agnostic-surface-spec.md:188` with snippet `keel show doctrine`. Line 188 of the current file is exactly `` `keel show doctrine`,``, so the anchor now matches the anchored line. Confirmed the previous 187 → 188 correction; other four ledger rows (191, 232, 119, 165) and their snippets unchanged and still correctly anchored.

Otherwise the body I certified in round 2 is byte-consistent: Context, Goal, Gate commands, Non-goals, Invariants, Enforcement table, Concept→module map, §1-§6 with acceptance criteria, PR↔section manifest, Definition of Done, and the Pre-mortem certification block (Verdict CERTIFIED, FM-1..FM-4 all RESOLVED, zero new findings) all match my round-2 read. No body drift beyond the two described deltas.

Both edits are exactly as described and neither touches certified technical content (a status-currency flip and a masked-region anchor correction that improves internal consistency). My round-2 verdict stands.

PREMORTEM-VERDICT: CERTIFIED pre-mortem-review@0.13.1 (fresh subagent, round 2 + targeted confirmatory pass)
