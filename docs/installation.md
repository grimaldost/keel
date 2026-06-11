# Installation

## Plugin (Claude Code)

```
/plugin marketplace add grimaldost/keel
/plugin install keel
```

Installs the `apply-method` skill, the `/keel-*` commands, the `pre-mortem-review` agent,
and the template kit.

## CLI

Self-contained (no install), runs the bundled engine:

```
uvx --from git+https://github.com/grimaldost/keel keel --help
```

Or pin it as a dependency straight from the repository:

```
uv add keel --git https://github.com/grimaldost/keel
```

Requires Python >= 3.11 and `uv`.
