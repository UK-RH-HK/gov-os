---
id: CAP-49
type: capability
status: ACCEPTED
state_class: DERIVED
title: Qualification oracle (synthetic repos, fault injection, hidden tests)
depends_on:
- CONTRACT-v5
---

# CAP-49: Qualification oracle (synthetic repos, fault injection, hidden tests)

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can prove the Gov OS on synthetic repositories against a held-out oracle before the release.
- **Acceptance:** A fresh executor runs the proving run on W2-81's synthetic repositories and produces a scorecard in SCORECARD_FORMAT; any forbidden outcome fails; the hidden sets are protected by the transcript scan (CAP-66): the transcripts written between a set's writing and the end of its measure contain neither its path nor its question ids, or the measure is void.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-49.a, CAP-49.b, CAP-49.c
