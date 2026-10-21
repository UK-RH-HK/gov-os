
## 81. Delegated decisions on W1-14's packages (register v0.81, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the five packages the W1-14 (`DAEO-w9l3`) ticket lead
returned. For each the test designer's, the lead's and the orchestrator's recommendations agree on option (a), the
confidence is medium or higher, and the choice is reversible until W1-35 teaches the format. The lead had the
engineer build to the recommended options before they were decided; the result is accepted, and later briefs say
again that an engineer waits for the decision.

### DEC-355 — W1-14 DP-1 and DP-2: the bridge is `gov.tasks.bridge.derive`, and a task carries its fields in a YAML block
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-14 packages DP-1 option (a) and DP-2 option (a); confidence medium · **Under:** CAP-31.a, DEC-307, DEC-350
- **Decision:**
  - `gov.tasks.bridge.derive(root, change)` takes the change's folder name under `openspec/changes/` and returns
    `{"change", "specification", "tickets": [{"task", "ticket"}, ...]}`, one entry per task in file order. It
    commits nothing. A faulty `tasks.md` is refused with `TASKS_INVALID`, whose details name each faulty task.
  - A task carries `kpis`, `role`, `allowed_paths`, `profile` and `class` in a fenced `yaml` block indented under
    its checkbox line. A task that lacks one, `profile` and `class` included, refuses the whole derivation and
    nothing is written.
  - W1-12's `tasks.md` template does not show the block yet, so a change written from it is refused: a residual,
    for W1-35 or a template change.

### DEC-356 — W1-14 DP-3, DP-4 and DP-5: a hand-set `CLOSED` is not trusted, dependencies form one DAG, and a second run adds only new tasks
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-14 packages DP-3 option (a), confidence medium-high; DP-4 option (a), confidence medium; DP-5 option (a), confidence medium-high · **Under:** MR-2, DEC-348, CAP-31.a
- **Decision:**
  - The bridge derives only when the specification's status is `CLOSED` and `gov.readiness.check` passes.
  - `depends_on` holds quoted task numbers of the same file or ids of existing tickets, written to the ticket's
    `deps` as ticket ids. A name that resolves to nothing, an unquoted number, a cycle among tasks, or a dependency
    that reaches an existing cycle is `TASKS_INVALID`.
  - On a second run a task that has a ticket keeps it byte for byte, only new tasks get tickets, and a refused
    run changes nothing. A task is matched to its ticket by `specification` and the `task` key the bridge writes.
    A task edited or removed after derivation is a residual.

| Version | Date | Change |
|---|---|---|
| 0.81 | 2026-10-05 | Delegated under DEC-220: DEC-355 (W1-14 DP-1, DP-2: `gov.tasks.bridge.derive`; a task's fields in a YAML block; a faulty task refuses the whole derivation), DEC-356 (DP-3 to DP-5: `CLOSED` and a passing readiness check; one DAG; a second run adds only new tasks). |
