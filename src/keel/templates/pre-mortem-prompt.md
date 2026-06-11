# Pre-mortem prompt

A generative complement to the deterministic DoR checks. Deterministic checks find
structural gaps; the pre-mortem finds "this approach is wrong." Run it after DoR
Part A passes and before execution.

## When / who

- **When:** the end of Specify — the closing step of the DoR gate (2→3 boundary).
  The spec and its PR↔section manifest already exist; this runs before the spec
  becomes a runnable series and before any code.
- **Who:** a fresh agent that has not authored the spec (a stateless pass, so the
  judgment is externalized, not the author's own). keel's bundled
  `pre-mortem-review` agent can execute it, or run it as an orchestrator
  pre-series hook (e.g. pr-pilot's), or a manual pass.

## Prompt

```
You are reviewing a spec and its PR manifest before any code is written.

Assume this series shipped and then FAILED — the refactor broke something, the
scope sprawled, or the result was incoherent across PRs.

List the failure modes — all BLOCKER and MAJOR modes, plus any notable MINOR —
most likely first. For each:
- the failure (one line),
- the most likely cause (which section, which assumption, which missing invariant),
- the smallest change to the SPEC or a PR PROMPT that would prevent it.

Do not propose implementation. Only changes to the spec/manifest/prompts.

Ground every claim: read the referenced code and cite file:line; default skeptical.
Apply these grounding checks (the failure class the method most often misses):
- For each "reuse / port / model-on the proven X" instruction, READ X and confirm it
  handles THIS wave's shapes — "proven" means proven on the original caller's inputs.
- Scrutinize each "what already exists" claim by grepping that the seam is built.
- When a design supersedes a prior version, verify decisions against the committed
  register, not the superseded doc.

Emit findings as a YAML list, one entry per failure mode, then the prose:
  - id: FM-1
    severity: BLOCKER      # BLOCKER | MAJOR | MINOR
    evidence: path/to/file.py:line
    smallest_fix: "<one-line spec/prompt edit>"
    target_section: "section N"

<paste: the spec + the PR↔section manifest>
```

## Output handling

Fold the proposed changes back in **from the structured findings list** — apply each
`smallest_fix` to its `target_section` mechanically. Then run a **post-fold coherence
re-read**: read each edited artifact end to end and confirm every finding was applied
consistently across ALL of its sections (Task / pre-read / Process / file-list); for any
finding that NARROWED scope (removed a deletion / relocation / file), re-derive every
dependent count (blast radius, file-list, DoD counts) and reconcile contradictions. This
post-fold hop is where a fix lands in one section while a contradicting instruction
survives in another — nothing else reviews the delta.

Record the verdict in the spec's `## Pre-mortem certification` block: `CERTIFIED` once no
blocking failure mode remains (else leave it uncertified and list the outstanding modes),
with a `Reviewer:` and a `Post-fold coherence:` line. The pre-mortem is **required** — DoR
does not pass without a recorded certification by a non-author reviewer (`keel check-ready`
checks for it, B1). Its findings frequently become new DoR checks — the loop closing again.
