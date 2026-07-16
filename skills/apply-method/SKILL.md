---
name: apply-method
description: Apply the keel method — the author's externalized development method — to a project. Use when the user wants to set up the method in a new repo, plan or run a governed multi-PR series, check whether a spec is ready to decompose (Definition of Ready), wire the quality gates, close the reflection loop, or asks "apply my method / my dev method / the method". Routes to the playbook, the templates, and the per-project bindings. Do NOT use for one-off scripts or single short artifacts — the method is overhead below the coordination threshold (see "When not to").
---

# Apply the method

This skill ships with keel 0.13.1 and is a **thin router**: the procedure lives in the packaged
playbook, one command away. Run

```
uvx --from ${CLAUDE_PLUGIN_ROOT} keel show playbook
```

(bare `keel show playbook` when a persistent `keel` is on PATH) and follow what it returns —
the entry rule (read the project's `method-bindings.md` first; the playbook covers the
established-format fallback when it is absent), setup in a new project (`keel init`), the 8
phases with their gates, the portable pre-mortem procedure (`keel show pre-mortem`), and the
subset-of-phases rule are all there. The doctrine itself is `keel show doctrine`. If this
copy's version line lags `keel --version`, your plugin cache is stale (reinstall) — the
packaged playbook you just fetched is the current one either way.

## When NOT to use

A throwaway script or a single short artifact is below the threshold where coordination cost
pays. Implement it directly. Apply the method when the work clears the blast-radius trigger in
doctrine §6 (read it via `keel show doctrine`): ≥5 PRs, a chokepoint imported by ≥~50 modules,
additive-on-a-shared-contract, a boundary crossing, or a >1-quarter lifetime.

---
*Deploy: this skill lives in `skills/apply-method/` within the keel plugin. It is
active whenever the keel plugin is installed in Claude Code.*
