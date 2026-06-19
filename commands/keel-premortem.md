---
description: Run a fresh-eyes pre-mortem on a Ready spec before execution.
argument-hint: <path-to-spec.md>
---

Dispatch the `pre-mortem-review` agent against the spec at $ARGUMENTS — the agent is read-only and
RETURNS its findings. Then YOU, the caller, fold its top failure modes back into the spec/prompts
(re-grounding each fix first) as the closing step of the Definition-of-Ready gate.
