---
description: Apply the keel method to the current project (bind slots, run the phases).
---

Invoke the `apply-method` skill to set up or run the keel method here. It routes through the
packaged playbook: `uvx --from ${CLAUDE_PLUGIN_ROOT} keel show playbook` (the doctrine:
`… keel show doctrine`). If this project already carries a `method-bindings.md` or prior method
artifacts, read the bindings first and match the established formats (the playbook's entry
step). Otherwise run `keel init` to copy the template kit into this project, then bind every
portability slot in the COPIED `method-bindings.md` (in this project, not the packaged
template) — then walk the phases (or the round's named subset).
$ARGUMENTS
