---
id: CAP-56
type: capability
status: PROPOSED
state_class: DERIVED
title: Retrieval in disposable subagent context
depends_on:
- CONTRACT-v4
---

# CAP-56: Retrieval in disposable subagent context

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent keeps retrieval out of its own context: facet retrieval runs in disposable subagents and only the cited bundle returns.
- **Acceptance:** On RETR-X-02 the main session's transcript contains the bundle and none of the intermediate retrieval batches.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-56.a
