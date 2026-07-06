# Getting started

The first full loop with keel, end to end, with the exact commands. Vocabulary:
`docs/glossary.md`; the reasoning behind each step: `docs/doctrine.md`.

## 0. Install

See `docs/installation.md`. Everything below assumes `keel` on PATH — substitute
`python -m keel` or `uvx --from <repo> keel` per your setup.

## 1. Drop the kit into your project

```
keel init docs/method
```

Copies the template kit (spec/ADR templates, the DoR/DoD gate checklists, the review checklist,
reflection-triage, the series skeleton, method-bindings). Then fill `docs/method/method-bindings.md`
— bind each slot (ADR home, spec format, gates, review checklist, reflection sink) to a concrete
mechanism in YOUR project. keel's own filled sheet is a worked example: `docs/method-bindings.md`.

## 2. Scaffold a spec

```
keel new-spec docs/design/my-feature-spec.md
```

Stamps `spec-template.md`. A fresh stamp is deliberately not Ready: the placeholders fail A3 until
replaced, and the certification is empty until a reviewer signs.

## 3. The author loop (structure only)

```
keel check-ready docs/design/my-feature-spec.md --structure-only
```

Runs Part A (well-formedness: numbered sections, acceptance criteria, the PR↔section manifest,
anchor resolution…) and skips the certification check, so you can iterate the spec's shape without
the expected not-yet-certified failure. Fix what it names; re-run until `OK`.

## 4. The blind pre-mortem

Run the pre-mortem pass with a reviewer that did NOT author the spec — the bundled
`pre-mortem-review` agent (or any fresh context given `pre-mortem-prompt.md`). Size the arc by the
doctrine's round economy: two rounds for a BLOCKER-bearing / shared-contract / fresh-from-catalog
spec, one pass for a LOW-stakes reversible round. See `commands/keel-premortem.md` for the full
caller protocol.

## 5. Fold, ledger, save the artifact

Fold each finding's `smallest_fix` back into the spec (re-grounding it first — it is a hypothesis),
record one `### Fold ledger` row per folded finding (`finding · target · path:line · confirmed` —
optionally with a verified snippet), and save the pass's returned output verbatim to
`docs/design/my-feature-spec.premortem.md` with a `Spec-hash:` from:

```
keel spec-hash docs/design/my-feature-spec.md
```

## 6. Certify and gate

Record the certification block (Reviewer, Verdict, the artifact reference; an operator-accepted
`CONDITIONAL-CERTIFY` needs an `Operator:`), update the header `Status:`, then:

```
keel check-ready docs/design/my-feature-spec.md
```

`OK` (possibly with named WARNs) means the spec is Ready: decompose it (one PR per numbered
section, per the manifest) and implement — each PR cites its section, gates run after each.

## 7. Close the loop

After the wave, run the reflection triage (`reflection-triage.md`): cluster what the round taught,
ground each candidate promotion against current source, and promote the recurring traps into a
checklist item, a gate, or a template change — so the next round starts sharper than this one.
