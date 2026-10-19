
## 54. Delegated decision on W1-08's package DP-10 (register v0.54, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the package the W1-08 (`DAEO-uudf`) ticket lead returned
with its DONE. The designer's, the repair worker's, the lead's and the orchestrator's recommendations agree, the
confidence is medium-high, and the choice is reversible: no reader of the key exists yet.

### DEC-265 — W1-08 DP-10: `languages` is required only when `code_intelligence` is enabled
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-10 option (a); confidence medium-high · **Under:** DEC-251, CAP-06.e
- **Decision:** When `code_intelligence` has `enabled: true`, `languages` is required and is a non-empty list of
  strings. When it has `enabled: false`, `languages` may be left out or be any list of strings. The schema is
  already written this way. The one test case for the disabled form goes to the next test design batch that
  touches the path-map schema (W1-27, DEC-228), as a described behaviour.

| Version | Date | Change |
|---|---|---|
| 0.54 | 2026-10-04 | Delegated under DEC-220: DEC-265 (W1-08 DP-10: `languages` is required only when `code_intelligence` is enabled; the test case goes to W1-27's test design). |
