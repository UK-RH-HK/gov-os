
## 69. Delegated decision on W1-34's package DP-1 (register v0.69, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the one package the W1-34 (`DAEO-egm9`) ticket lead
returned. The designer's, the lead's and the orchestrator's recommendations agree, the confidence is medium, and the
choice is reversible until W1-11 reads the state.

### DEC-328 — W1-34 DP-1: a gate record holds its state in `status` alone
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-34 package DP-1 option (a); confidence medium · **Under:** CAP-34.d, DEC-308
- **Decision:**
  - A decision package holds its gate state in `status` alone, with no second key: `PROPOSED` is open, `ACCEPTED` is
    answered, `DECLINED` is declined, `REVOKED` is revoked and `STALE` is stale. The template states the mapping.
  - The key that names the CIT a package belongs to is `cit`.
  - The READY rule (DEC-308) and W1-11's checker read the same value. One test pins the five values and the key.

| Version | Date | Change |
|---|---|---|
| 0.69 | 2026-10-04 | Delegated under DEC-220: DEC-328 (W1-34 DP-1: a gate record holds its state in `status` alone, `PROPOSED`, `ACCEPTED`, `DECLINED`, `REVOKED`, `STALE`; the CIT key is `cit`). |
