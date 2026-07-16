# Installation

## Plugin (Claude Code)

```
/plugin marketplace add grimaldost/keel
/plugin install keel
```

Installs the `apply-method` skill, the `/keel-*` commands, the `pre-mortem-review` agent,
and the template kit.

## CLI

Self-contained (no install), runs the bundled engine — pin a tag so gate
semantics don't shift under you:

```
uvx --from git+https://github.com/grimaldost/keel@v0.11.1 keel --help
```

Persistent binary on PATH (so a bare `keel` works, e.g. from a slash command):

```
uv tool install git+https://github.com/grimaldost/keel@v0.11.1
```

Or pin it as a project dependency straight from the repository:

```
uv add git+https://github.com/grimaldost/keel@v0.11.1
```

Requires Python >= 3.11 and `uv`. The `/keel-check-ready` slash command runs the
engine straight from the installed plugin bundle
(`uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`), so it works with only the plugin
installed — no separate CLI step needed.

Where an application-control policy blocks console-script executables (`keel.exe`
on a locked-down Windows machine), the module entry point sidesteps the shim:
`python -m keel <command>` (or `uv run python -m keel <command>` in a uv project)
is equivalent to `keel <command>`.

## Any agent (CLI-only)

Any AI agent that can run a shell applies the full method from the CLI alone — no plugin
needed (ADR-0017). The method corpus ships inside the package; pin the tag that first carries
`keel show` (or newer):

```
uvx --from git+https://github.com/grimaldost/keel@v0.14.0 keel show playbook
```

- `keel show doctrine | playbook | pre-mortem` prints the packaged corpus (the thesis and
  phases; the apply-method procedure; the pre-mortem prompt to run in a fresh non-author
  context).
- `keel init <target>` drops the template kit — including `method-agents-snippet.md`, a
  paste-ready block for your project's `AGENTS.md` that routes every future agent session
  into the method.
- The gates (`keel check-ready`, `keel spec-hash`) run as ordinary commands, so enforcement
  lives in your shell, pre-commit, or CI — independent of which agent wrote the code.

Honest scope line: this path serves any agent that can run a shell. An agent with no shell
cannot run the deterministic gates either way; an MCP wrapper for that case is a named
deferral (ADR-0017).
