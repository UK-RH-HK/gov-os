---
id: CAP-02
type: capability
status: ACCEPTED
state_class: DERIVED
title: 'Release authenticity (lite: pinned and hash-verified)'
depends_on:
- CONTRACT-v5
---

# CAP-02: Release authenticity (lite: pinned and hash-verified)

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can confirm that an installed kernel matches a released version.
- **Acceptance:** `gov doctor` reports MATCH for the pinned `framework.lock` manifest against the release's own manifest and file hashes, and DRIFT naming the edited file after a one-byte edit; a release is pinned and hash-verified, and no tag signature is required.
- **Wave:** W1
- **Disposition:** LITE
- **Covers:** CAP-02.a, CAP-02.b, CAP-02.c
