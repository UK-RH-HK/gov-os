
## 56. Delegated decisions on W1-46's packages DP-8, DP-9 and DP-13 (register v0.56, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on three of the nine packages the W1-46 (`DAEO-jdqr`)
ticket lead returned after implementation and review. For each, the lead's recommendation and the orchestrator's
agree, the confidence is medium, the choice is reversible, and none loosens the guard, the sandbox or the network
grant. The other six go to the owner: DP-10, DP-11, DP-12, DP-14 and DP-16 are P1 or set how strong the sandbox and
the guard are; DP-15 changes the owner's list of research hosts.

### DEC-271 — W1-46 DP-8: which tickets each role may be launched on
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-8 option (a); confidence medium · **Under:** DEC-242, DEC-161
- **Decision:** `gov launch` starts an engineer or a research session only on a ticket of its own role. An
  independent test designer and an independent auditor are launched on any ticket that is `in_progress`: their work
  is always on another role's ticket. This is how "a ticket of another role" in DEC-242 is read.

### DEC-272 — W1-46 DP-9: the key of `research-allowlist.yaml`, and a project without the file
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-9 option (a); confidence medium · **Under:** DEC-241
- **Decision:** The list is under the key `hosts`. A project without `governance/project/research-allowlist.yaml`
  launches a research session on the kernel default alone: no file means no extension. One test covers the missing
  file.

### DEC-273 — W1-46 DP-13: an experiment folder lies under a root the project names
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-13 option (a); confidence medium · **Under:** DEC-242, DEC-163
- **Decision:** The one folder of a research ticket must lie under a root the project names, `experiments/` by
  default. `gov launch` refuses a research ticket whose folder is anywhere else, so a research ticket on `.claude/`,
  `.tickets/`, `governance/project/`, `src/` or `.git/` does not launch.

| Version | Date | Change |
|---|---|---|
| 0.56 | 2026-10-04 | Delegated under DEC-220: DEC-271 (W1-46 DP-8: engineer and research on their own role's ticket; test designer and auditor on any ticket in progress), DEC-272 (DP-9: key `hosts`; no project file means the kernel default alone), DEC-273 (DP-13: an experiment folder lies under a named root, `experiments/` by default). DP-10, DP-11, DP-12, DP-14, DP-15 and DP-16 go to the owner. |
