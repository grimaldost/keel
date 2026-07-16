# Pre-mortem pass — round 1 (saved artifact, B2)

- Spec: docs/design/2026-07-16-agent-equivalence-eval-spec.md
- Date: 2026-07-16
- Reviewer: pre-mortem-review@0.14.0 (fresh subagent, round 1 — non-author)
- Spec-hash: 2d18a1c3187a292444316337ee94371113aabfe6e58584d26e529346d96b049e

---

I have enough to ground my findings. Engine modules are byte-identical between the wheels (E1 §1d / E2 "identical behavior" are well-grounded), the feasibility variation exists (`keel show` is 0.14.0-only), but the causal-path and oracle-sensitivity problems are the core defects. Here is my certification artifact.

---

```yaml
findings:

- id: FM-1
  severity: BLOCKER
  evidence: src/keel/templates/method-agents-snippet.md:15-24 (snippet carries new-spec, check-ready --structure-only, the readiness definition, and the pre-mortem/fresh-context rule inline); spec §3 oracles o1-o4; spec §4 + Part B verdict rule
  summary: >
    The verdict-driving oracles are insensitive to the treatment. T1's o1-o4 (kit present, bindings
    filled, spec passes --structure-only, not-self-certified) are ALL satisfiable in arm B from the
    AGENTS.md snippet alone, without ever invoking `keel show playbook` — the routing hop the spec
    (§Context, §3) says the behavioral layer measures. None of o1-o4 reads anything the hop uniquely
    determines, so a broken hop cannot flip them. The one treatment-sensitive dimension (procedure
    fidelity) is a rubric score, and Part B fixes rubric deltas as "descriptive only (no significance
    testing at N=2)" — it cannot raise a RED/AMBER flag. Therefore "no gross degradation" is
    near-predetermined on the flagship above-threshold task regardless of hop quality; the screen
    cannot detect the degradation it exists to screen for. Part B's claim "the treatment is not inert"
    is true only trivially (oracles read the outputs); the outputs are invariant to the independent
    variable, which is the inert-treatment failure.
  smallest_fix: >
    Add a deterministic T1 oracle that is ON the routing-hop path — e.g. o-hop: the run transcript
    shows `keel show playbook`/`keel show doctrine` was invoked before authoring (arm A's equivalent
    is reading the inline body) — and let RED/AMBER gate on it; OR promote procedure-fidelity to a
    scored oracle with a pre-registered flip threshold. If neither, state in Non-goals that NO
    deterministic oracle is sensitive to the routing hop and the screen cannot detect hop degradation.
  disconfirming_test: >
    Run one arm-B T1 rep and grep its transcript for `keel show`; if o1-o4 all pass with zero
    `keel show playbook` invocations, the hop is off the measured path (confirms). If o1-o4 cannot be
    satisfied without the hop, refutes.
  consumed_input: >
    The oracle scripts consume the sandbox artifacts (kit files, method-bindings.md, the authored
    spec, the certification block) — verified against method-agents-snippet.md, which supplies every
    step o1-o4 require without the CLI route.
  target_section: "section 3 (Oracles) + section 4 (verdict rule) + Non-goals"

- id: FM-2
  severity: MAJOR
  evidence: git show a8520b9:skills/apply-method/SKILL.md (routes to `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md`, `${CLAUDE_PLUGIN_ROOT}/src/keel/templates/`, `uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`); 0.13.1 wheel file list (no `keel/method/`, no doctrine.md; templates only at `keel/templates/`); 0.13.1 cli.py has no `show` command
  summary: >
    Arm A's baseline is mis-constructed. The 0.13.1 skill body routes the agent to
    `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md` and `${CLAUDE_PLUGIN_ROOT}/src/keel/templates/`, none of
    which exist in a wheel-only sandbox: the 0.13.1 wheel ships NO doctrine.md and defines no
    CLAUDE_PLUGIN_ROOT, and 0.13.1 has no `keel show` to print the doctrine. So an arm-A agent cannot
    reach the doctrine at all, while arm B's `keel show doctrine` works. This handicaps the baseline,
    and because the verdict only flags A-passes-then-B-fails, an artificially weak A makes RED flags
    even rarer — biasing the screen toward "no gross degradation." "As the plugin would present it"
    (§3) is not reproduced by a bare wheel.
  smallest_fix: >
    §3 must provision arm A with a resolvable CLAUDE_PLUGIN_ROOT containing 0.13.1's doctrine +
    templates so the skill-body paths resolve in-sandbox (fidelity to a real plugin install), and
    record that provisioning in the material inventory the o-vector script logs.
  disconfirming_test: >
    In an arm-A sandbox, resolve `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md`; if it does not exist and no
    `keel show` prints it, arm A cannot reach doctrine (confirms).
  target_section: "section 3 (Arms) + Part B (held-constant factors)"

- id: FM-3
  severity: MAJOR
  evidence: 0.14.0 cli.py `show_cmd` (command exists only in 0.14.0); spec-template.md:184 `<!-- keel kit 0.14.0 -->` vs `<!-- keel kit 0.13.1 -->`; templates.py `stamp_spec` = `shutil.copy2` (stamp propagates into every `keel new-spec` output); SKILL.md `${CLAUDE_PLUGIN_ROOT}` / "skill" vocabulary; spec §3 sanitizer clause
  summary: >
    Judge de-blinding via side channels a version-number sanitizer misses. The sanitizer is specified
    only as "version strings and any arm-identifying token ... replaced," with no enumeration. But
    `keel show` exists ONLY in 0.14.0, so any arm-B artifact quoting that command is a definitive
    arm-B tell; arm-A artifacts carry `${CLAUDE_PLUGIN_ROOT}`, "skill"/"plugin", and "keel 0.13.1"
    vocabulary; and the kit stamp comment propagates into every authored spec (a judged artifact) via
    shutil.copy2. A `\d+\.\d+\.\d+` regex catches the stamp version but none of the vocabulary tells.
  smallest_fix: >
    Enumerate in §3 the exact token set the sanitizer MUST neutralize — kit-stamp comment, `keel show`,
    `${CLAUDE_PLUGIN_ROOT}`, "skill"/"plugin" vs "AGENTS.md snippet", `uvx --from git+…` — and add a
    residual-leak grep over sanitized inputs as a gate that must be clean before judging.
  disconfirming_test: >
    Grep sanitized arm-B judge inputs for `keel show`; a hit proves the version-string sanitizer leaks
    an arm-identifying token (confirms).
  target_section: "section 3 (Blinding and side channels)"

- id: FM-4
  severity: MAJOR
  evidence: method-bindings.md "## Portability slots" table is 3-column (`Slot | acme-ledger binding (example) | This project`) with the example column pre-filled; bindings.py `check_bindings` raises NotImplementedError in BOTH wheels
  summary: >
    o2 ("every portability-slot row of method-bindings.md has a non-empty project cell") is
    under-specified against the real table shape. The table has THREE columns and the middle
    (`acme-ledger` example) column is pre-populated in the template; a parser that checks "the row has
    a non-empty cell after the slot" false-passes on an unfilled sheet by reading the example column.
    o2 must name the 3rd ("This project") column as the target. It also cannot fall back to
    `keel bind-check`, which is a NotImplementedError stub in both wheels (exit 2), so the runner must
    define "filled" itself and cannot reuse the packaged definition.
  smallest_fix: >
    Reword o2: "the 3rd ('This project') column cell of every row under the '## Portability slots'
    heading is non-empty," and note `keel bind-check` is unavailable (stub) so o2 is a bespoke parse.
  disconfirming_test: >
    Run the o2 script against the UNEDITED template; if it passes, it is reading the example column
    (confirms the ambiguity).
  target_section: "section 3 (Oracles, o2)"

- id: FM-5
  severity: MINOR
  evidence: spec §3 oracle list + Part B thresholds (RED/AMBER given, per-oracle baseline expectation absent); engine modules check_ready.py/models.py/errors.py byte-identical between wheels (E2 identical by construction)
  summary: >
    No pre-registered per-oracle baseline expectation (the eval-spec requirement that each measured
    criterion carry a one-line baseline). o1/o3/o4 are expected 2/2 in both arms (ceiling); E2 is
    identical by construction because the engine is byte-identical across wheels; o5 is expected pass
    in both with a rare over-apply. Without recorded baselines, a ceilinged oracle reads as
    "equivalent" when it is actually uninformative, and the report cannot distinguish
    equivalence-because-both-good from instrument-insensitive.
  smallest_fix: >
    Add a one-line baseline-expectation column to the §3 oracle list (and an E2 note "identical by
    construction — engine byte-identical") flagging which criteria are expected to ceiling and thus
    contribute no discriminating power.
  disconfirming_test: >
    Diff the two wheels' check_ready.py; byte-identical confirms E2 ceilings by construction.
  target_section: "section 3 (Oracles) + section 4"

- id: FM-6
  severity: MINOR
  evidence: spec §3 oracle o6 ("the sandbox project's own test command passes"); §3 "toy consumer project" unspecified as to test command
  summary: >
    o6 presupposes the toy consumer ships a test command that actually exercises the added flag; §3
    does not specify the toy project provides one, nor that it covers the flag. o6 is uncomputable if
    no test command exists and trivially green if the test ignores the flag.
  smallest_fix: >
    §3 must specify the toy project's test command and that it asserts the flag's effect (not just
    that the script still runs).
  disconfirming_test: >
    Inspect the toy project; absence of a flag-covering test command makes o6 uncomputable (confirms).
  target_section: "section 3 (Tasks/Oracles, o6)"

cleared:
- claim: "Feasibility — instruments supply the measured variation"
  cite: "0.14.0 cli.py defines `show_cmd` (doctrine/playbook/pre-mortem via keel/assets.py ASSETS); 0.13.1 cli.py has no `show` command. Both wheels present at scratchpad/eval/wheels/. The routing-hop difference the study needs exists."
- claim: "E1 §1d — engine diff empty"
  cite: "check_ready.py (54917 B), models.py (392 B), errors.py (238 B), budget_drift.py byte-identical between the 0.13.1 and 0.14.0 wheels."
- claim: "E1 §1a — packaged doctrine mirror byte-equal"
  cite: "diff /home/user/keel/docs/doctrine.md vs 0.14.0 keel/method/doctrine.md = BYTE-EQUAL (at current tree; §1a should record the SHA it re-verifies against, per DC1 stale-referent)."
- claim: "E1 §1e — templates delta is exactly the kit-stamp version + new snippet"
  cite: "diff of the two wheels' keel/templates/: only-in-0.14.0 method-agents-snippet.md; spec-template.md differs solely at line 184 (`keel kit 0.13.1`→`0.14.0`); all other templates identical."
- claim: "E1 §1f — playbook covers the 0.13.1 skill's load-bearing directives"
  cite: "0.14.0 method/playbook.md carries when-not-to threshold, bindings-first entry, setup steps, per-phase gate list, subset-of-phases rule, source-of-truth boundary — each present in a8520b9:skills/apply-method/SKILL.md."
- claim: "o3 is not a trivial ceiling"
  cite: "Ran check_spec_ready(spec-template.md, structure_only=True) → passed=False (A2 trivial acceptance, ~18 unfilled-placeholder violations, A5 path). The agent must genuinely author the spec to pass o3."

notes:
- "FM-2/FM-3 are the same asymmetry seen from two angles: arm A's inline plugin surface (skill body + `${CLAUDE_PLUGIN_ROOT}`) vs arm B's thin snippet + `keel show` hop. FM-2 is the internal-validity harm (handicapped baseline); FM-3 is the de-blinding harm."
- "T2/o5 (over-application) is the ONE channel with genuine assay sensitivity to the hop, because the snippet omits the when-not-to threshold that the 0.13.1 skill body carries inline — arm B must take the hop to reach it. But o5's failure base rate is low and N=2, so it is underpowered, not null; it does not rescue FM-1."
- "check_bindings and the `bind-check` command are a NotImplementedError stub in both wheels — a run agent that tries `keel bind-check` gets exit 2; harmless to the oracles (o2 is a bespoke script) but worth knowing for transcript interpretation."
```

Unverified-offline: 1

PREMORTEM-VERDICT: NEEDS-REVISION pre-mortem-review@0.14.0 (fresh subagent, round 1)
