
## 51. Delegated decision on W1-18's package DP-3 (register v0.51, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on one of the three packages the W1-18 (`DAEO-1ve2`) ticket
lead returned. The designer's, the lead's and the orchestrator's recommendations agree, the confidence is medium, and
the choice is reversible: W1-19 and W1-21, the only callers, are not written. DP-1 (the module's public interface) and
DP-2 (whether `gov` stops the daemon) are not decided here and go to the owner: on DP-1 the confidence in the names is
low and it changes the ticket's `allowed_paths`; DP-2 sets aside a phrase of ADR-0002.

### DEC-257 — W1-18 DP-3: "the facet state recorded" is the state in the module's result
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-18 package DP-3 option (a); confidence medium · **Under:** DEC-033, DEC-034, DEC-037, DEC-074 Q4
- **Decision:**
  - When Ollama is unavailable, the lifecycle module's result names the facet `semantic`, the state
    `FACET_UNAVAILABLE` and a non-empty warning that names Ollama and says results are FTS-only. The warning is
    also written once to standard error. No file is written.
  - The module reports the state; it does not set a bundle's stopping reason. W1-21 copies the state into the
    bundle, and how an FTS-only bundle's stopping reason (CAP-55) relates to it is settled there.
  - The form in which the result is returned follows the owner's answer on DP-1.

| Version | Date | Change |
|---|---|---|
| 0.51 | 2026-10-04 | Delegated under DEC-220: DEC-257 (W1-18 DP-3: facet `semantic`, state `FACET_UNAVAILABLE` and a warning in the module's result and on standard error; no file). |
