# D-0007 / D-0008 assessment

## D-0007

Status should remain `ACTIVE` until a lawful owner-approved replacement exists.

### Valid core

- lower-trust inputs cannot manufacture higher-trust facts;
- project configuration may strengthen but not weaken constitutional floors;
- descriptors, caller fields and model/plugin output are requests/evidence, not authority;
- refusals must be typed and observable.

### Defect

D-0007's T1 installed-kernel definition is sufficient for post-install integrity but circular for first install/update when the manifest and lock are generated from the same unauthenticated source. Contract A2 now makes that deficiency normative to repair.

### Disposition

Retain the principle and existing controls. A future owner decision should amend or supersede the circular T1 wording only when the replacement architecture is approved. This meta-review does not perform that mutation.

## D-0008 / ARCH-0002

Current state is correct:

- `PROVISIONAL` / `PROPOSED`;
- `human_approved: false`;
- `in_effect: false`;
- no `chosen_option`;
- D-0007 not superseded.

### Strengths

- explicit separation of authenticity, eligibility, certification and currency;
- threshold/purpose separation;
- verified-byte install/use intent;
- monotonic rollback protection;
- honest acknowledgement that unseen metadata cannot be known;
- detailed threat/evidence corpus;
- one concrete profile instead of an option explosion.

### Problems

- it is a bespoke, very large protocol with a large trusted-computing and proof surface;
- it couples distribution authenticity to compiler/bootstrap/environment certification;
- it makes local availability depend on complex mutable-state/freshness machinery;
- it creates new authorities and selectors faster than they can be proven;
- it relies on custom registers/calculators/schemas for properties better supported by established update/attestation patterns;
- it has no accepted implementation and Revision 7 falsifies its own claims.

### Disposition

Do not activate, supersede D-0007 with, or repair D-0008 as Revision 8. Preserve it as high-assurance research and a source of later certification requirements. Any replacement or substantial narrowing requires an explicit new owner decision because OP-1…OP-16 are binding design inputs today.

## Owner decision required

The owner should choose between:

1. retaining CP-1 as a long-term high-assurance certification profile while adopting a smaller Phase-1 distribution root; or
2. keeping CP-1 as the sole production target and accepting that Phase 1 remains blocked pending substantial operational/toolchain infrastructure.

The meta-review recommends option 1.
