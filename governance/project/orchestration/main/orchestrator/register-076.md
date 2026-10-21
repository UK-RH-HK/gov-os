
## 76. Delegated decision on W1-17's package DP-8 (register v0.76, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220. The engineer's, the lead's and the orchestrator's
recommendations agree, the confidence is medium, the choice is one condition and it is the stricter one.

### DEC-345 — W1-17 DP-8: the index-freshness check is not green on an index that holds no chunk
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-8 option (a); confidence medium · **Under:** DEC-342, CAP-38.b
- **Decision:** An index that matches the tracked blobs and holds no chunk does not pass the check, as built: a
  filter that wrongly drops every file cannot pass, and the check agrees with `search`, which reports `empty` as
  unavailable. A project with no governance-class file can therefore never be green; that is a residual.

| Version | Date | Change |
|---|---|---|
| 0.76 | 2026-10-04 | Delegated under DEC-220: DEC-345 (W1-17 DP-8: the index-freshness check is not green on an empty index). |
