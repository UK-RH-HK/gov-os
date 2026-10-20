
## 70. Delegated decisions on W1-11's packages DP-1 and DP-4 (register v0.70, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on two of the four packages the W1-11 (`DAEO-be7u`) ticket
lead returned. The designer's, the lead's and the orchestrator's recommendations agree, the confidence is medium, and
both are reversible. DP-2 (the owner approval fact) and DP-3 (how a gate is cited) are with a product-spec worker,
who reads the archived sources under DEC-222; DP-2 goes to the owner afterwards.

### DEC-329 — W1-11 DP-1: the decision checker reads frontmatter and git, never prose
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-1 option (a); confidence medium · **Under:** CAP-51.a
- **Decision:**
  - The checker is deterministic: it reads frontmatter and git only. It does not read a decision's body for
    statements such as "superseded by DEC-003".
  - On the b-dev tier as planted it flags the overlapping ids across `docs/adr/` and `decisions/`. The other hazard
    classes (ACTIVE while superseded, a supersession cycle) are tested on a clone where the test writes the link the
    hazard describes, because HZ-B-03 states its link only in prose and the tier holds no cycle.
  - G-04 is in the S0b2 output and was not read. If it requires prose reading, this decision is revisited.

### DEC-330 — W1-11 DP-4: the checker fails a ticket that waits on a declined, revoked or stale package
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-4 option (a); confidence medium · **Under:** CAP-34.d, DEC-308, DEC-328
- **Decision:**
  - The checker fails every ticket that is not closed and is named in the `constrains` of a package whose `status` is
    `DECLINED`, `REVOKED` or `STALE`.
  - The READY rule in `gov.tasks` is unchanged in this ticket: it still releases a ticket once its package is no
    longer `PROPOSED`, so the queue can list such a ticket until W1-26 runs the checker. Closing that at the queue is
    a residual of W1-11, for the ticket that next changes `gov.tasks`.

| Version | Date | Change |
|---|---|---|
| 0.70 | 2026-10-04 | Delegated under DEC-220: DEC-329 (W1-11 DP-1: the checker reads frontmatter and git, never prose), DEC-330 (W1-11 DP-4: the checker fails a ticket waiting on a declined, revoked or stale package; the READY rule is unchanged). |
