# Pre-mortem profiles — the kind-selected sheets

A spec declares its `Profile:` in the header — `code`, `data-pipeline` or `measurement`. That is
the SUBJECT axis, and it is not `Kind:`, which declares decomposition shape; the two were collapsed
onto one field name until A14 separated them. The material below is dispatched only for the profile
that names it, so a `code` spec's author and reviewer never pay for any of it. One home per fact:
what lives here does not also live in `spec-template.md` or `definition-of-ready.md`, which point
here instead.

## Profile: `measurement`

### The design sheet (paste into the spec)

Fill the `<...>` placeholders. This is a `##` section in the spec, so it needs no acceptance
criterion and carries no anchors; the reviewer certifies the design, `keel check-ready` the
certification.

```markdown
## Experiment design (Part B)

- **Estimand + unit of analysis:** <the effect measured, at what grain — per-item delta vs aggregate>
- **Reps / power & MEWD:** <N per arm; the minimum effect worth detecting; why N can detect it — a 1-rep delta is noise>
- **Blinding + held-constant factors:** <what is blinded; what is held equal across arms>
- **Correctness oracle (not "ran green"):** <what decides "correct", distinct from the run completing>
- **Measured-unit causal path:** <treatment end — the measured path READS what the treatment changes (not inert); measured-unit end — capabilities beyond the intended input enumerated, no side channel to the ground truth>
- **Enforcement of isolation invariants:** <each leakage/isolation invariant, and the buildable mechanism that enforces it, claimed by a numbered section/PR>
- **Pre-registered analysis plan:** <the analysis fixed before results are seen>
```

### The reviewer's items (Definition of Ready, Part B)

These are Part B items: a fresh, non-author reviewer certifies them with evidence. They gate the
axes the design sheet names, and they are ordered — feasibility short-circuits the rest.

- [ ] **Feasibility-grounding ran FIRST** — before internal-validity attacks, the reviewer grounded
      the headline's key variable against the empirical record it needs (prior-run data / ledger,
      the reused instrument). If that record cannot supply the variation the study measures, the
      study is null on these instruments and the rest of the review short-circuits.
- [ ] **Baseline expectation per criterion** — each measured criterion carries a one-line baseline
      expectation (will the control / `bare` arm plausibly pass it?), and the reviewer flagged
      ceiling/floor risk: a procedurally-perfect spec still measures nothing if its criteria cannot
      vary across arms.
- [ ] **Instrument defeatability** — the reviewer asked the cheapest way an agent sidesteps the
      planted difficulty (a tool, a shortcut, a grep) so the run measures nothing. An instrument
      trivially bypassed yields a null for a reason the design never controlled — distinct from the
      ceiling/floor question above.
- [ ] **The experimental design is named, not just the subject** — the estimand and unit of analysis
      (per-item delta vs aggregate); enough reps to detect the minimum effect worth detecting, since
      a 1-rep delta is noise (a power question, distinct from feasibility: power is whether N can
      detect the effect, feasibility is whether the record supplies the variable); blinding and
      held-constant factors; and a correctness oracle distinct from "ran green".
- [ ] **The causal path is traced against code from BOTH ends** — the measured path actually READS
      what the treatment changes (a treatment the measured call recomputes live, or never reads, is
      inert — mis-built, not null), and the measured unit's capabilities beyond the intended input
      (tools, network, filesystem and cwd, prior/session state) include no side channel to the
      ground truth. A side channel CONFOUNDS the result — distinct from defeatability's null.
- [ ] **Every isolation / safety / leakage invariant names a buildable enforcement mechanism**
      claimed by a numbered §/PR — not a bare assertion, and not a smoke test that tests a jail no
      PR creates.
- [ ] **The analysis plan is pre-registered** — fixed before results are seen, not chosen after.

## Profile: `data-pipeline`

For a spec whose deliverable is data, a migration, or a load — where a unit-green suite is not a
data-level gate, and where every defect below reached production or a paid run past a green
Part A and multiple blind rounds.

### The design sheet (paste into the spec)

```markdown
## Population and cutover (Part B)

- **Discriminating field + real distribution:** <the field the design branches on, and what the REAL input population does over it — measured, not assumed>
- **Heterogeneity axes:** <the axes the corpus actually varies on, each with the gate that exercises it>
- **Pilot sample:** <constructed to contain one instance per named axis, not the first N rows>
- **Write-side reconciliation:** <the exact ledger that proves the write moved what it claimed>
- **Read-side cutover check:** <what DISCRIMINATES the new read path from the old one; a check both paths pass proves nothing>
- **Pinned clocks:** <every clock pin the spec fixes, and what each read predicate admits AT those values>
- **Closed vocabularies consumed:** <each staged column read by an enum or accepted-values list, and the owner of that list>
```

### The reviewer's items (Definition of Ready, Part B)

- [ ] **Population before schema** — the real input population was characterized over the
      discriminating field before the design assumed a shape. A spec that assumes the schema and
      is right about 21% of rows passes every offline gate and loses the rest silently.
- [ ] **Every heterogeneity axis has a gate** — the axes are named, and each is exercised by a
      check rather than by a fixture that happens to contain one. Homogeneous fixtures over a
      heterogeneous corpus are the shape that gets certified and then fails on contact.
- [ ] **The pilot contains one instance per axis** — constructed, not sampled. A pilot drawn from
      the head of the corpus tests the head of the corpus.
- [ ] **The write side reconciles exactly, and the read side DISCRIMINATES** — a read check that
      the pre-cutover path also passes is a check of nothing. Name what would differ.
- [ ] **Every pinned clock pair is evaluated against every read predicate the spec defines**, at
      the exact pinned values. A read minted before its own load clock resolves every view empty,
      and the suite stays green because the fixture generates zero rows.
- [ ] **Every staged literal is checked against the closed vocabulary that OWNS it** — the enum's
      member list or the accepted-values set, read from the owner rather than from the spec. A
      value minted upstream against a closed vocabulary ships until first consumption raises.
