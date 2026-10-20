
## 79. Delegated decisions on W1-33's packages P-2 to P-4 (register v0.79, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on three of the four packages the W1-33 (`DAEO-xog0`)
ticket lead returned. The test designer's, the lead's and the orchestrator's recommendations agree, the confidence
is medium or higher, and each is reversible; none grants a role anything. P-1 (placing the five definitions under
`.claude/agents/`) is an owner action.

### DEC-352 — W1-33 P-2, P-3 and P-4: what "generated" means, the permission-class families, and the two unsandboxed roles' grants
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-33 packages P-2 option (a), confidence medium-high; P-3 option (a), confidence medium; P-4 as written, confidence medium · **Under:** CAP-22.a, CAP-58.b, DEC-066, DEC-158
- **Decision:**
  - P-2: until the rulesync adapters of W1-38 exist, a definition under `.claude/agents/` that is placed by hand
    and agrees field by field with its kernel role file is a "generated definition" for W1-33. W1-38 later produces
    the same files from the same sources.
  - P-3: a role file maps the `NETWORK_*`, `DB_*`, `CLOUD_*` and `DEPLOY_*` families as CAP-58.b writes them; it
    does not list each member class of the archived Framework §32. Listing them is a residual, for the mid-wave
    audit to weigh.
  - P-4: the definitions stand as written: the orchestrator has `NETWORK_*` allowed (DEC-158: it is unsandboxed)
    and the database, cloud, CI-trigger and deploy classes denied; product-spec has all of them denied. The tests
    require only that each class has a stated disposition.

| Version | Date | Change |
|---|---|---|
| 0.79 | 2026-10-05 | Delegated under DEC-220: DEC-352 (W1-33 P-2: a hand-placed definition that agrees with its kernel role file counts as generated until W1-38; P-3: permission-class families as CAP-58.b writes them; P-4: the orchestrator's and product-spec's grants as written). P-1 is an owner action. |
