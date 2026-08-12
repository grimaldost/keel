# Plugin reference

What the Claude Code plugin installs (`/plugin marketplace add grimaldost/keel` then
`/plugin install keel` — see `docs/installation.md`). The `keel` CLI is documented
separately in `docs/cli-reference.md`; the two halves overlap where a command runs the
bundled engine with `uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`.

| Entry point | Kind | Argument | What it does |
|---|---|---|---|
| `/keel-apply` | command | none | Invokes the `apply-method` skill to bind the method's slots in this project and run the phases (or the round's named subset). |
| `/keel-check-ready <path-to-spec.md>` | command | `<path-to-spec.md>` | Runs the Definition-of-Ready gate from the bundled engine; reports the verdict and violations. Exit 0 Ready, 1 violations, 2 not-runnable. |
| `/keel-premortem <path-to-spec.md>` | command | `<path-to-spec.md>` | Dispatches the `pre-mortem-review` agent, then the caller folds the findings, saves the artifact (B2) and records the certification block. |
| `/keel-triage` | command | none | Runs the `reflection-triage.md` procedure over the series' feedback: sweep open rows, cluster by cause, promote each recurring trap to one durable check, and land it. |
| `apply-method` | skill | — | The method playbook an agent reads: setup in a new project, the entry-read-the-bindings rule, and the phase-by-phase gates. |
| `pre-mortem-review` | agent | — | Read-only fresh reviewer (Read/Grep/Glob). Reads `src/keel/templates/pre-mortem-prompt.md` at run start for its directives (ADR-0017) and returns findings ending in a machine-greppable `PREMORTEM-VERDICT:` line; it never edits the spec. |

Only `/keel-check-ready` and `/keel-premortem` declare an argument (both carry
`argument-hint: <path-to-spec.md>` in their front matter); `/keel-apply` and `/keel-triage`
declare none. All four bodies do reference the `$ARGUMENTS` token — the two that declare no
hint end on a bare `$ARGUMENTS` line, the intent being that trailing text arrives as free
context. The substitution itself is Claude Code's, not keel's.

The template kit ships with the plugin too — `docs/templates-reference.md` lists its
files, and `keel init <target>` copies them into a project.
