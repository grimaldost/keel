---
description: Run the Definition-of-Ready gate on a spec file.
argument-hint: <path-to-spec.md>
---

Run the keel Definition-of-Ready gate on the spec at $ARGUMENTS from the installed
plugin bundle (no separate CLI install needed):

`uvx --from ${CLAUDE_PLUGIN_ROOT} keel check-ready $ARGUMENTS`

A persistent `keel` on PATH is equivalent only when `keel --version` prints this
plugin's version; otherwise upgrade it (`uv tool upgrade keel`) or use the command
above.

Report the verdict and any violations. The gate checks Part A well-formedness and
requires a recorded blind pre-mortem certification (ADR-0002): exit 0 = Ready,
1 = violations, 2 = not runnable (a missing/undecodable spec, or a directory).
