
## 71. Delegated decision on W1-11's package DP-3 (register v0.71, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, after a product-spec worker read the archived sources under
DEC-222 (Contract v3 Gate L3 and A1, Framework §47). The originals name no key; they say only that a declined,
revoked, stale or other-CIT gate cannot authorise execution. The designer's, the lead's, the worker's and the
orchestrator's recommendations agree, the confidence is medium, and the choice only adds two optional keys and a
check that fails closed. DP-2 (the owner approval fact) goes to the owner.

### DEC-331 — W1-11 DP-3: a record cites its gate in `approval` and names its change in `cit`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-3 option (a); the gap worker's draft; confidence medium · **Under:** CAP-34.d, DEC-328, DEC-277
- **Decision:**
  - A ticket or change that claims a gate as its approval carries `approval`, a list of gate ids, and `cit`, a
    scalar. A gate authorises it only when the gate's `status` is `ACCEPTED` and the two `cit` values are the same
    string. A `PROPOSED` gate does not authorise.
  - The check fails closed, with the finding `GATE_NOT_AUTHORISING`: a cited id that is no record or is not a
    decision package; a citing record with `approval` and no `cit`; a gate with no `cit`.
  - A record with no `approval` is not checked. `approval` is not a graph edge (DEC-277).
  - The CIT id has no grammar yet; the ticket that builds the CIT-P and CIT-E records fixes it. The schema lines for
    `approval` and `cit` on a ticket are outside W1-11's paths and are a residual.
  - Whether setting a gate's `status` to `ACCEPTED` needs an owner approval fact is asked by no KPI; it is a residual
    of W1-11, to be raised with the owner's answer on DP-2.

| Version | Date | Change |
|---|---|---|
| 0.71 | 2026-10-04 | Delegated under DEC-220: DEC-331 (W1-11 DP-3: a record cites its gate in `approval` and names its change in `cit`; the check fails closed). DP-2 goes to the owner. |
