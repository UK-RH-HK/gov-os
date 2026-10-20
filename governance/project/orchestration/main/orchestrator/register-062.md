
## 62. Delegated decision on W1-15's reviewer finding F9 (register v0.62, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the one reviewer finding the W1-15 (`DAEO-7nne`) ticket
lead returned as needing a decision. The lead's recommendation and the orchestrator's agree, the confidence is
medium, the choice is reversible, and it makes the filter stricter.

### DEC-298 — W1-15 F9: the pre-index filter ignores every allowlist of the project's gitleaks file
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 reviewer finding F9 and the lead's recommendation; confidence medium · **Extends:** DEC-290 · **Under:** CAP-03.a
- **Decision:** DEC-290 made the filter ignore path allowlists. It also ignores the other ways a project's
  `.gitleaks.toml` can shelter a secret: allowlist `regexes` and `stopwords`, per-rule allowlists, and disabled
  rules. A file that holds a secret by the rules never reaches an index, whatever the project's file allows. The
  finding lets a secret through, so it is fixed before W1-15 closes: a test design batch first, as a described
  behaviour, then a fresh engineer.

| Version | Date | Change |
|---|---|---|
| 0.62 | 2026-10-04 | Delegated under DEC-220: DEC-298 (W1-15 F9: the filter ignores every allowlist and disabled rule of the project's gitleaks file; fixed before the ticket closes). |
