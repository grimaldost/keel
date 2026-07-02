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
uvx --from git+https://github.com/grimaldost/keel@v0.11.0 keel --help
```

Persistent binary on PATH (so a bare `keel` works, e.g. from a slash command):

```
uv tool install git+https://github.com/grimaldost/keel@v0.11.0
```

Or pin it as a project dependency straight from the repository:

```
uv add git+https://github.com/grimaldost/keel@v0.11.0
```

Requires Python >= 3.11 and `uv`. The `/keel-check-ready` slash command runs the
engine straight from the installed plugin bundle
(`uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`), so it works with only the plugin
installed — no separate CLI step needed.
