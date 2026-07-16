# Pre-mortem pass — round 2 re-gate (final certifying artifact, B2)

- Spec: docs/design/2026-07-16-agent-equivalence-eval-spec.md
- Date: 2026-07-16
- Reviewer: pre-mortem-review@0.14.0 (fresh subagent, round 2 — non-author)
- Spec-hash: 460e4d7c28021faf0e6b7b127960e277c426b943d643b359c7783bd553ef9e18
- Prior round: docs/design/2026-07-16-agent-equivalence-eval-spec.premortem-r1.md (NEEDS-REVISION, FM-1 BLOCKER + FM-2..FM-6)

---

Audit complete. I have verified each prior finding against the current spec text, the executable harness (`oracle.py`, `sanitize.py`), and the arm materials, plus both pinned wheels' CLIs. Findings below.

---

## Resolution audit (round-1 findings FM-1 … FM-6)

**FM-1 (BLOCKER — verdict-driving oracles insensitive to the routing hop; inert treatment) → RESOLVED.**
The fold puts the hop on the measured path in both prose and harness. Spec §3 adds **o-hop** and §"Experiment design" makes it flag-capable; `oracle.py:92-99` (`o_hop`) reads the sandbox `.keel-cli.log` and returns `True` for arm B iff `'show playbook'`/`'show doctrine'` appears, `'inline'` for arm A. Both arm materials route the CLI through `./bin/keel` (armA-AGENTS.md:7, armB-AGENTS.md "./bin/keel"), and I confirmed `keel show` is **0.14-only** — the 0.13.1 wheel exposes only `check-ready/spec-hash/bind-check/budget-drift/init/new-spec` (no `show`). The treatment (fetch-via-CLI) is therefore genuinely read by the measured path. Minor narrowing: the oracle checks hop *presence anywhere* in the log, not "before the spec-authoring commands" as §3 words it — does not corrupt the signal (a hop taken at all satisfies the intent).

**FM-2 (MAJOR — arm A baseline stranded without a resolvable plugin root) → RESOLVED.**
Spec §3 now provisions a full 0.13.1 checkout for `${CLAUDE_PLUGIN_ROOT}`. armA-AGENTS.md's routes resolve to `…/eval/keel-0131`, which exists with `docs/doctrine.md` (20 KB) and the full `src/keel/templates/` dir — so the skill body's doctrine, templates, and bundle-CLI routes all resolve. o3 uses `uvx --from <wheel>` per arm; I confirmed the 0.13.1 wheel supports `check-ready --structure-only` (`keel/cli.py:100-110`), so arm A's o3 baseline (2/2) is feasible, not stranded.

**FM-3 (MAJOR — judge de-blinding via tokens a version sanitizer misses) → RESOLVED (with a MINOR residual).**
`sanitize.py` enumerates the FM-3 token set as `RULES` (versions, `/tmp` dist+`keel-0131` paths, `uvx --from`, `keel show <asset>`, `${CLAUDE_PLUGIN_ROOT}`, skill/plugin/snippet/playbook vocabulary) and gates on a `LEAK_PATTERN` residual grep that `sys.exit(1)`s on any leak. The kit stamp `<!-- keel kit 0.14.0 -->` (spec-template.md:184) is caught by the `0\.1[34]\.\d+` rule. `keel show playbook` → `<KEEL-CLI> read procedure` (rules compose correctly). The `init` vs `new-spec` concern is void — **both** wheels carry both commands, so neither is arm-distinctive. Residuals are fail-safe, not false-pass: the full 0.14.0 wheel *filename* path (`keel-0.14.0-py3-none-any.whl`) is not matched by the dist-path rule (the `[\w.]*` can't cross the `-py3` hyphen), but `\.whl` in `LEAK_PATTERN` catches it and halts — see FM-a.

**FM-4 (MAJOR — o2 ambiguous vs the 3-column bindings table; bind-check stub) → RESOLVED.**
`oracle.py:26-39` reads `cells[-1]` (the third "This project" column of the real template) and guards `non-empty and not startswith('<')`. Traced against the actual `method-bindings.md`: the five slot rows (`ADR home`, `Spec format`, `Guardrails`, `Review checklist`, `Reflection sink`) all have an empty last cell → `hits=0` → unfilled, matching the empirical claim; the Upgrade/Orchestrator tables contain none of the slot substrings, so the parse is effectively scoped without needing the heading. `bind-check` confirmed a stub in 0.13.1 (`keel/cli.py:124`), consistent with the "stub (exit 2) in both versions" claim.

**FM-5 (MINOR — no per-oracle baselines; E2 identical-by-construction) → RESOLVED.**
§3 now carries a parenthetical baseline on every oracle (o1 ceiling/sanity-floor, o2 "A 2/2, B is the question", o3 "raw template fails so authoring required", o4/o5/o6, o-hop "unknown — primary question"); §4 requires baselines quoted next to observations and adds the E2 "identical **by construction** … confirms packaging, not behavior" honesty note. Analysis-plan items, not harness-executable — appropriately in prose.

**FM-6 (MINOR — o6 under-specified test command) → RESOLVED (with a MINOR residual).**
o6 now names `python3 scripts/summarize.py <sample.log>` exit 0 + known ERROR count AND `python3 -m unittest discover -s tests` green; `oracle.py:73-89` implements exactly this. Residual: the count check is `'2' in proc.stdout`, and the sample log's timestamp `1700000002` already contains `'2'` — see FM-b.

---

## New / residual findings (rising-bar, round 2)

```yaml
- id: FM-a
  severity: MINOR
  evidence: docs/design/eval-20260716/sanitize.py:21
  smallest_fix: "Broaden the dist-path rule to match a keel wheel filename with build tags (…-py3-none-any.whl), so it neutralizes in one pass instead of only tripping the leak gate."
  disconfirming_test: "Run sanitize.py on a judged .md containing the literal 0.14.0 wheel path; if it exits 0 clean the rule already covers it."
  target_section: "section 3 (sanitizer RULES)"
- id: FM-b
  severity: MINOR
  evidence: docs/design/eval-20260716/oracle.py:84
  smallest_fix: "Replace `'2' in proc.stdout` with a parse of the printed ERROR count == 2, since the sample's `1700000002` timestamp makes the bare-substring check pass even for a script that only echoes the log."
  disconfirming_test: "Feed o6 a summarize.py that cats the sample log; if o6 returns False the check is already tight."
  target_section: "section 3 (o6)"
- id: FM-c
  severity: MINOR
  evidence: docs/design/eval-20260716/oracle.py:26
  smallest_fix: "Scope o2's row scan to the `## Portability slots` section (or assert the 3-column shape), so a bindings table collapsed to 2 columns can't let the example cell satisfy the last-cell test."
  disconfirming_test: "Run o2 on a bindings file whose This-project column is deleted but example column filled; if it returns False the guard already holds."
  target_section: "section 3 (o2)"
```

None of these plausibly corrupts the decision the eval gates. The primary question (routing-hop equivalence) is well-instrumented: o-hop sits on the measured path, both poles (hop-always-taken and snippet-suffices) are handled as explicit named findings rather than silent nulls (§"Experiment design"), and the fidelity RED/AMBER thresholds are detectable at N=2 with no floor/ceiling hole. The sanitizer's residuals are fail-safe (leak gate halts) or symmetric across arms (vocabulary replacement applies identically to both), so they cannot silently de-blind or bias one arm.

## cleared

- o-hop treatment-on-measured-path: `oracle.py:92-99` reads the wrapper log; both arms route through `./bin/keel`; `keel show` is 0.14-only (0.13.1 CLI has no `show` command) — hop is real and observable.
- Arm A routes resolve: `…/eval/keel-0131/docs/doctrine.md` + full `templates/` dir exist; 0.13.1 wheel supports `--structure-only` (`keel/cli.py:100-110`) so o3 baseline is feasible.
- o2 returns unfilled on the unedited template (`hits=0`, last cell empty) and reads the third column, not the example — verified against `src/keel/templates/method-bindings.md`.
- Kit-stamp neutralized: `<!-- keel kit 0.14.0 -->` matched by `0\.1[34]\.\d+` (spec-template.md:184; sanitize.py:20).
- init/new-spec not arm-distinctive: both wheels carry both commands.
- Leak gate composes: `keel show playbook` → `<KEEL-CLI> read procedure`; `.keel-cli.log` (`.log`) and `bin/` excluded from judge copy (sanitize.py:51-53).
- o3 candidate-spec filter (`'<feature/refactor name>'` exclusion) correctly rejects an unedited template copy, so o3 requires genuine authoring.

Unverified-offline: 3
PREMORTEM-VERDICT: CONDITIONAL-CERTIFY pre-mortem-review@0.14.0 (fresh subagent, round 2)

Conditions (each ≤2 lines, all MINOR — fold as advisories, no further round required):
1. FM-b — tighten o6's ERROR-count check to an exact parse (not `'2' in stdout`), which the `1700000002` timestamp trivially satisfies.
2. FM-a — extend the sanitizer dist-path rule to cover build-tagged wheel filenames so it neutralizes rather than only halting the leak gate.
3. FM-c — scope o2 to the `## Portability slots` section (or assert 3-column shape) to close the column-collapse example-cell edge.
