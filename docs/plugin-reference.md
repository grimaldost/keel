# Plugin reference

What the Claude Code plugin installs (`/plugin marketplace add grimaldost/keel` then
`/plugin install keel` — see `docs/installation.md`). The `keel` CLI is documented
separately in `docs/cli-reference.md`; the two halves overlap where a command runs the
bundled engine with `uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`.

| Entry point | Kind | Argument | What it does |
|---|---|---|---|
| `/keel-check-ready <path-to-spec.md>` | command | `<path-to-spec.md>` | Runs the Definition-of-Ready gate from the bundled engine; reports the verdict and violations. Exit 0 Ready, 1 violations, 2 not-runnable. A person types it; the model does not run it on its own (`disable-model-invocation: true`) and calls `keel check-ready` directly instead. |
| `apply-method` | skill | — | The method playbook an agent reads: setup in a new project, the entry-read-the-bindings rule, and the phase-by-phase gates. It loads when a request matches its description ("apply the method here"); no command is needed to start it. |
| `pre-mortem-review` | agent | — | Read-only fresh reviewer (Read/Grep/Glob). Reads `src/keel/templates/pre-mortem-prompt.md` at run start for its directives (ADR-0017) and returns findings ending in a machine-greppable `PREMORTEM-VERDICT:` line; it never edits the spec. Its front matter fixes `model: opus`, `effort: high` and `omitClaudeMd: true`, so the pass runs on the same tier whatever session dispatches it, and without the user, project and local CLAUDE.md files (managed policy files still load). A model passed on the dispatch itself still wins over `model`. |

`/keel-check-ready` declares its argument (`argument-hint: <path-to-spec.md>`), and its body
reads it through the `$ARGUMENTS` token. The substitution itself is Claude Code's, not keel's.
Claude Code also lists the command under the plugin's namespace, `/keel:keel-check-ready`.

## Where the 0.22.0 commands went

0.22.0 deleted three commands that none of the maintainer's sessions ran in the 2026-07-26..09-26
field window. Each one's work already had a home in the skill, the agent, or Claude Code's own
mechanisms:

- **`/keel-apply`** — ask for the method in plain words and the `apply-method` skill loads. To see
  the phases laid out before anything is edited, start in Claude Code's plan mode.
- **`/keel-premortem`** — dispatch the `pre-mortem-review` agent as a native subagent:
  `@agent-keel:pre-mortem-review <path-to-spec.md>`, or ask Claude to run the pre-mortem on the
  spec and it delegates through the Agent tool. What the caller does with the result — fold, save
  the artifact (B2), record the certification — is `docs/getting-started.md` steps 4 to 6, with
  `definition-of-ready.md` Part B as the reference. The same agent runs the SERIES pass when the
  dispatch names the generated series (the PR prompts and their DAG): save its output as
  `<spec-stem>.series-premortem.md`, record it under `### Series review` in the certification
  block, and run `keel decompose-check <spec>` before any PR runs. The `apply-method` skill's
  Decompose step is the reference for that pass.
- **`/keel-triage`** — the `reflection-triage.md` procedure (`keel show reflection-triage`, or the
  copy `keel init` placed in the project), which the `apply-method` skill's Reflect step runs.

The template kit ships with the plugin too — `docs/templates-reference.md` lists its
files, and `keel init <target>` copies them into a project.
