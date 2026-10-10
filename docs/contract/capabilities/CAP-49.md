---
id: CAP-49
type: capability
status: PROPOSED
state_class: DERIVED
title: Qualification oracle (synthetic repos, fault injection, hidden tests)
depends_on:
- CONTRACT-v4
---

# CAP-49: Qualification oracle (synthetic repos, fault injection, hidden tests)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can qualify the Gov OS on two synthetic programmes against a held-out oracle before Release 1.
- **Acceptance:** A fresh qualification executor runs both qualification tiers and produces a scorecard in SCORECARD_FORMAT; any forbidden outcome fails; the builder sessions had no read access to the oracle. The oracle is hidden from a launched worker's Bash by the sandbox, and from every session started in the repository root by a `Read` deny rule and by the guard refusing any tool call that names its path.
- **Wave:** W3
- **Disposition:** KEPT
- **Covers:** CAP-49.a, CAP-49.b, CAP-49.c
