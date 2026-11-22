---
id: CAP-51
type: capability
status: ACCEPTED
state_class: DERIVED
title: Decisions register (structured, versioned, authoritative)
depends_on:
- CONTRACT-v5
---

# CAP-51: Decisions register (structured, versioned, authoritative)

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can rely on one structured, versioned register of decisions with supersession.
- **Acceptance:** Superseding a decision updates both records' status and links, and the checker flags an ACTIVE record that is superseded, a duplicate id or a cycle. The checker also runs on the register that replaces the archived one, and an id cited from the archive is a finding that points to it.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-51.a, CAP-51.b
