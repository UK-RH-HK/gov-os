
## 67. Delegated decision on the kernel `templates/openspec/` folder (register v0.67, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the draft a product-spec worker returned after reading
G-07 and G-09 by exact path (DEC-310). The worker's and the orchestrator's recommendations agree, the confidence is
high, and the choice is reversible: a later ticket can add the path and a file.

### DEC-326 — W1-12: the kernel `templates/openspec/` folder stays empty and leaves the ticket's paths
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** the product-spec worker's package, option 1; confidence high that no file is required, medium-high on removing the path · **Closes:** the question DEC-304 left open · **Under:** DEC-310, CAP-30.a
- **Decision:**
  - G-07 and G-09 are single rows of the S0b2 glue requirements. Neither names a path, a folder or the kernel. They
    require no file in `template/governance/kernel/templates/openspec/`: G-09 asks for templates that pass
    `validate --strict` on first use, and OpenSpec reads templates only from the schema's own folder.
  - The folder stays empty, and `template/governance/kernel/templates/openspec/**` leaves W1-12's `allowed_paths`,
    in a commit with the trailer `Task: DAEO-lc4q`.
  - G-08, a source of W1-13, says the checker reads `feature-readiness.md`. DEC-305 supersedes that file name: the
    record is `readiness.yaml`. W1-13's test designer is told so.

| Version | Date | Change |
|---|---|---|
| 0.67 | 2026-10-04 | Delegated under DEC-220: DEC-326 (W1-12: G-07 and G-09 require no file in the kernel `templates/openspec/` folder; the path leaves the ticket's `allowed_paths`; DEC-305 supersedes G-08's file name for W1-13). |
