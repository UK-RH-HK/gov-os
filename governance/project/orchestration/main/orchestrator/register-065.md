
## 65. Delegated decisions on W1-12's packages DP-1 to DP-4 (register v0.65, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on four of the five packages the W1-12 (`DAEO-lc4q`) ticket
lead returned. For each, the designer's, the lead's and the orchestrator's recommendations agree, the confidence is
medium or higher, and the choice is reversible before W1-13 reads the schema. DP-5 (what W1-12 shows of the CIT-E
half of its third KPI line) is not decided here: it moves part of a KPI's enforcement to another ticket, so it goes
to the owner, and W1-12 is not merged before the answer.

### DEC-302 — W1-12 DP-1: the schema carries the readiness data under the YAML's own keys
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-1 option (a); confidence medium-high · **Under:** CAP-30.a, DEC-085
- **Decision:** The forked OpenSpec schema `feature-readiness` carries the rows, the states and the capability-type
  table under the key names and entry shapes of `docs/contract/readiness-dimensions.yaml` (`dimensions`,
  `cell_states`, `capability_types`), as top-level keys of its `schema.yaml`. W1-13 reads that structure.

### DEC-303 — W1-12 DP-2: W1-12 delivers `template/openspec/config.yaml`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-2 option (a); confidence medium · **Under:** CAP-30.a
- **Decision:** `template/openspec/config.yaml`, with `schema: feature-readiness`, is added to W1-12's
  `allowed_paths`, in a commit with the trailer `Task: DAEO-lc4q`, so that a new change gets the readiness record
  without `--schema` being passed. One test covers it.

### DEC-304 — W1-12 DP-3: the kernel `templates/openspec/` folder stays unused for now
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-3 option (1), the lead's fallback; confidence medium · **Under:** DEC-198, DEC-222
- **Decision:** OpenSpec reads templates only from the schema's own `templates/` folder, so the templates the KPI
  validates live there, and `template/governance/kernel/templates/openspec/**` holds nothing. That is recorded as a
  residual. The text of G-07 and G-09 is in the S0b2 output in the workbench, not in the archived sources; whether
  it is read before W1-12 closes is asked of the owner, and an answer may put a file in that folder.

### DEC-305 — W1-12 DP-4: the readiness record is YAML
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-4 option (a); confidence medium · **Under:** CAP-30.a
- **Decision:** The readiness record is `readiness.yaml`, artifact id `readiness`: one entry per row with `n`, `key`,
  `state`, `evidence`, `reason` and `gap_ticket`. A fresh record has all 26 rows `MISSING`: empty is invalid, N/A is
  never a default, and the other states need content.

| Version | Date | Change |
|---|---|---|
| 0.65 | 2026-10-04 | Delegated under DEC-220: DEC-302 (W1-12 DP-1: the schema carries the YAML's own keys), DEC-303 (DP-2: W1-12 delivers `template/openspec/config.yaml`), DEC-304 (DP-3: the kernel `templates/openspec/` folder stays unused for now), DEC-305 (DP-4: the readiness record is YAML, fresh rows `MISSING`). DP-5 goes to the owner. |
