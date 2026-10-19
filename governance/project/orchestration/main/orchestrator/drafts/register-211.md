
## 211. The W1-41 round of DEC-694: one delegated, stricter-only reading (register v0.211, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-700 — At adoption, a namespace without `embedding_policy` is refused like a namespace with another value
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416 as a stricter-only decision, 2026-10-14; told to the owner, who may replace it) · **Under:** DEC-380, DEC-388, DEC-694
- **Why now:** the owner's scope (DEC-694) has adoption refuse a target path map "where a namespace has another value". The template's own path map states no `embedding_policy` for any namespace, so if a missing field passed, every project adopted from the template would still end with nothing embedded and no refusal: the gap of DEC-686 would stay open.
- **Decision** (P3, reversible, confidence medium-high; it only makes adoption refuse more, and it does not block the owner's own actions):
  - At adoption's path-map stage a namespace without the field counts as "another value": adoption states every namespace's policy explicitly, as one of `embedded` and `not embedded`.
  - Outside adoption nothing changes: a missing or unknown value is still read as "not embedded" (DEC-380, DEC-388).

| Version | Date | Change |
|---|---|---|
| 0.211 | 2026-10-14 | Orchestrator: DEC-700 (delegated, stricter-only: at adoption a namespace without `embedding_policy` is refused like another value; outside adoption DEC-380 and DEC-388 stand). Next free id: DEC-701. |
