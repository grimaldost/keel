# Ancillary observation — t1-s-B-r2 (sonnet, arm B)

The run agent, following the playbook it fetched via the CLI, dispatched its OWN fresh
non-author subagent to run the blind pre-mortem on the spec it had authored (honoring the
"do not self-certify" instruction by delegating to a fresh context — the method's actual
mechanism). The harness had not asked for this. The child pass executed the sandbox code
in memory, found a real PR-sequencing BLOCKER (PR01's contract change breaks the repo-wide
unittest gate before PR04's consumer fix lands), and returned NEEDS-REVISION with grounded
evidence. The parent, per the harness nudge, left the certification block honestly
uncertified. Sandbox files were not modified by the child (stated in its output; the
oracle vector was computed after).

Read: the 0.14.0 surface routed a consumer agent end-to-end into a working, genuinely
blind pre-mortem — treatment-positive fidelity evidence, recorded outside the
pre-registered oracle set (it gates nothing).
