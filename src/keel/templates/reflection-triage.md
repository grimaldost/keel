# Reflection triage (closing the loop)

The exit gate of **Reflect** (phase 8). Reflections are worthless if nothing
consumes them; this step turns them into new external checks so the learning
compounds. A series is not "done reflecting" until recurring traps are promoted.

## Inputs

- `reflections.jsonl` (or wherever the project's reflection sink writes), plus the
  review/fix logs from the series.

## Procedure

1. **Read** all reflections from the series.
2. **Cluster** them — group by underlying cause, not by symptom.
3. **Ground each candidate promotion against current source before writing it** — verify the
   mechanism it names is actually absent (or present) and cite the check. A promotion naming a
   mechanism that already exists collapses to already-shipped or a docs gap; catching it here
   keeps a no-op out of the backlog (a CHANGELOG window cannot see work shipped releases ago —
   only the source can).
4. For each grounded cluster that is **recurring or high-cost**, **promote** it to exactly
   one external destination:
   - a new **review-checklist item** (`review-checklist.md`) — for "a reviewer
     should have caught this";
   - a new **guardrail script / gate** — for "a machine should catch this
     deterministically";
   - a **spec-template change** (`spec-template.md`) — for "the spec should have
     required this up front" (often a new DoR check).
5. **Record** what was promoted and where (one line per promotion), citing the
   round/PR that motivated it — and emit the triage document with an H1 beginning
   `# Triage —`: the feedback-loop tooling that indexes such directories can detect
   a triage doc by that heading (the filename is not a signal there).

## What to promote vs. decline (feedback flows up)

Reflections flow **up** into the method; the method never reaches back down into the
reporting project. Promote only the **project-agnostic** lesson. Decline, with a one-line
reason, the residue that belongs to someone else — and do not track its fate:

- **Engine / execution-resilience** faults (orchestrator stalls, runner bugs, the salvage
  workflow) → the orchestrator's ledger, not a method gate. Keep method-correctness and
  engine-resilience as **separate ledgers**, so a healthy method is not blamed for an engine
  fault, nor an executor fix smuggled into a method gate.
- **Project-specific** knowledge (one codebase's typing/dispatch rule) → that project's own
  review checklist. keel stays project-agnostic; it does not file into or track a consumer.

## Exit gate

- [ ] Every recurring/high-cost cluster has been promoted to a checklist item, a
      guardrail, or a spec-template/DoR change — or explicitly logged as "accepted,
      no action" with a reason.

*A reflection that is read but never promoted is the write-only failure mode this
step exists to prevent.*
