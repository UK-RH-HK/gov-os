
## 80. Delegated decisions on what W1-13 and W1-16 built beyond the decisions' wording (register v0.80, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the points the two ticket leads asked to have recorded.
Each is a detail of built code, reversible, and none makes a check weaker; the leads' and the orchestrator's views
agree; confidence medium-high.

### DEC-353 — W1-13: the details of `gov readiness` as built are accepted
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** the W1-13 lead's list of choices no decision fixes, and its reviewer's two fixed findings · **Under:** DEC-348 to DEC-351, DEC-085, CAP-30.e
- **Decision:**
  - The bare command's result is `{closed, specifications: [...]}`. Both selectors together is a usage error
    (exit 2). The error codes `SPECIFICATION_NOT_FOUND`, `TICKET_NOT_FOUND` and `AUDIT_TICKET_FAILED` end with 1.
  - A STANDARD specification with no capability type is invalid. A PRESENT row with no evidence is invalid, not
    open.
  - The audit ticket also carries `audits`, `assignee: independent-auditor`,
    `allowed_paths: [docs/audit/<id>/**]`, `profile` and `sources`.
  - From the review: a change folder that holds no specification record makes the bare command answer
    `READINESS_INVALID`, and a project readiness schema whose rows or capability-type table differ from the
    Contract's makes every specification in that project `READINESS_INVALID`. The rows and the table are constants
    in the checker, so a governed taxonomy change (CAP-30.e) changes the checker with the schema and the Contract.

### DEC-354 — W1-16: `stores_with_secrets` also runs the second scan
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** the W1-16 lead's third return · **Under:** DEC-347, DEC-287
- **Decision:** The secrets-indexing check's `stores_with_secrets` shares the filter's helper and therefore also
  scans with the project's rules alone, which DEC-347 did not name. It is accepted: it only makes the check find
  more. Where a project's rules have no expression of their own (they only modify a built-in rule), one scan stays;
  that is a residual.

| Version | Date | Change |
|---|---|---|
| 0.80 | 2026-10-05 | Delegated under DEC-220: DEC-353 (W1-13: result shape, codes, the audit ticket's fields and the two review fixes are accepted as built), DEC-354 (W1-16, stricter-only: `stores_with_secrets` also runs the second scan). |
