---
id: CAP-02
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Release authenticity (lite: signed git tags)'
depends_on:
- CONTRACT-v4
---

# CAP-02: Release authenticity (lite: signed git tags)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can confirm that an installed kernel matches a released version.
- **Acceptance:** `gov doctor` reports MATCH for the pinned `framework.lock` manifest, and DRIFT naming the edited file after a one-byte edit; at Release 1, `git tag -v` verifies the release tag (CAP-02.c, W3).
- **Wave:** W1
- **Disposition:** LITE
- **Covers:** CAP-02.a, CAP-02.b, CAP-02.c
