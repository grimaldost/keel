---
description: Run the Definition-of-Ready gate on a spec file.
argument-hint: <path-to-spec.md>
---

Run the keel Definition-of-Ready gate on the spec at $ARGUMENTS with the installed
keel CLI (setup: `installation.md`):

`keel check-ready $ARGUMENTS`

Report the verdict and any violations. The gate checks Part A well-formedness and
requires a recorded blind pre-mortem certification (ADR-0002): exit 0 = Ready,
1 = violations, 2 = not runnable (e.g. missing spec).
