
## 63. Delegated decision on W1-15's package DP-7 (register v0.63, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the package the W1-15 (`DAEO-7nne`) test designer
returned in its third batch. The designer's, the lead's and the orchestrator's recommendations agree, the
confidence is medium, and the choice is reversible.

### DEC-299 — W1-15 DP-7: a project that removes or rewrites a template rule is out of DEC-298's scope
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-7 option (a); confidence medium · **Under:** DEC-287, DEC-298
- **Decision:** The project's `.gitleaks.toml` stays the one source of rules (DEC-287). DEC-298 strips its
  allowlists and disabled rules; it does not put back a rule the project deleted or rewrote. A file with no rules
  at all is refused. That a project can remove a template rule, such as the canary rule, and so let that secret
  through the filter and the check, is recorded as a residual in `governance/project/bootstrap.md`; a kernel rule
  set that always applies would be a second rule source and a later decision.

| Version | Date | Change |
|---|---|---|
| 0.63 | 2026-10-04 | Delegated under DEC-220: DEC-299 (W1-15 DP-7: the project's gitleaks file stays the one source of rules; a removed template rule is a residual). |
