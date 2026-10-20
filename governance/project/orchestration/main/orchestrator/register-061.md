
## 61. Delegated decisions on W1-09's test design packages (register v0.61, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on seven of the nine packages the W1-09 (`DAEO-topz`)
ticket lead returned from its test design. For each, the designer's, the lead's and the orchestrator's
recommendations agree, the confidence is medium or higher, and the choice is reversible. The suite on the branch
already follows them. DP-4 (how the READY rule knows a specification is not closed) and DP-6 (what an open decision
package is before W1-34 and W1-11) are not decided here: the confidence is below medium, so they go to the owner.
Meanwhile the engineer builds to the suite as written, and the branch is not merged until both are answered.

### DEC-291 — W1-09 DP-1: claims and the READY rule have a Python interface
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-1 option (a); confidence high · **Under:** CAP-23.a, CAP-23.b, DEC-275
- **Decision:** W1-09 delivers `gov.tasks.claim`, `release`, `holder`, `ready`, `blocked` and `create`, raising
  `GovError` with the codes `CLAIM_HELD`, `CLAIM_NOT_HELD`, `TICKET_NOT_FOUND` and `TICKET_CLOSED`. No `gov`
  command is added: `gov claim` stays in Wave 3 (CAP-23.b), and the twelve-command registry is unchanged.

### DEC-292 — W1-09 DP-2: the claim convention
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-2 option (a); confidence medium-high, medium for the closed ticket and `in_progress` · **Under:** CAP-23.a, DEC-116
- **Decision:**
  - The lock is `.tickets/.claims/<ticket id>`, created with O_EXCL, a text file naming the holder. The holder is a
    string the caller gives, by convention `<role>:<session>`.
  - Only the holder releases. Nothing expires: a dead session's claim is released by whoever names its recorded
    holder, which is the main orchestrator's job.
  - A closed ticket cannot be claimed (`TICKET_CLOSED`). A lock and `status: in_progress` both count as claimed.
  - Left open and untested: whether `claim` also sets `in_progress`; a second claim by the same holder; an empty
    holder.

### DEC-293 — W1-09 DP-3: which acceptance tests folder makes a ticket READY
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-3 option (a); confidence high for the folder, medium for the classes · **Under:** DEC-069, CAP-31.c
- **Decision:** The folder is the ticket's `acceptance_tests.path`, else `tests/acceptance/<wbs_id>/`, else
  `tests/acceptance/<ticket id>/`. It must be a directory. The rule applies to tickets of every class.

### DEC-294 — W1-09 DP-5: a ticket's mandatory inputs
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-5 option (a); confidence medium · **Under:** CAP-31.d, DEC-277
- **Decision:** A ticket key `inputs` holds a list of record ids. An input is absent when no such record exists,
  and superseded when a SUPERSEDES edge points at it. A ticket with an absent or superseded input is not READY.
  Adding `inputs` to W1-08's ticket schema and template is a residual for the next ticket that touches them; the
  schema accepts unknown keys today.

### DEC-295 — W1-09 DP-7: `gov.tasks.create` adds `state_class` to a new ticket
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-7 option (a); confidence medium · **Under:** DEC-229
- **Decision:** `gov.tasks.create(root, title)` runs the kernel's `tk create` and adds `state_class: AUTHORITATIVE`
  to the new ticket, so the vendored script keeps its hash. W1-09 gets a KPI line for it, in a commit with the
  trailer `Task: DAEO-topz`. Which copy of the script `create` runs in this repository, where the kernel is under
  `template/` until it is installed here, stays open and is a residual.

### DEC-296 — W1-09 DP-8: what W1-09 shows of "verified by gov doctor"
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-8 option (a); confidence medium-high · **Under:** DEC-196
- **Decision:** W1-09's tests check the vendored file against its pinned sha256. The check by `gov doctor` goes to
  W1-27's test design as a described behaviour.

### DEC-297 — W1-09 DP-9: claims are made in the main tree; the claims folder is untracked
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-9 option (a); confidence medium · **Under:** DEC-235, DEC-236
- **Decision:** In Wave 1 claims are made only in the main tree, by the main orchestrator; a claim is not shared
  across worktrees. `.tickets/.claims/` is untracked: the orchestrator adds it to `.gitignore`. A claims folder
  that is a symbolic link is an untested residual; exclusive creation cannot overwrite a file.

| Version | Date | Change |
|---|---|---|
| 0.61 | 2026-10-04 | Delegated under DEC-220: DEC-291 (W1-09 DP-1: a `gov.tasks` Python interface, no `gov` command), DEC-292 (DP-2: the claim convention), DEC-293 (DP-3: the acceptance tests folder, for every class), DEC-294 (DP-5: `inputs` as record ids), DEC-295 (DP-7: `create` adds `state_class`; a KPI line), DEC-296 (DP-8: the doctor check goes to W1-27), DEC-297 (DP-9: claims in the main tree only; the folder is untracked). DP-4 and DP-6 go to the owner. |
