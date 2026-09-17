# 11 — Bounded R0 correction delta (AR-0023)

## Scope discipline

This delta is limited to the **two confirmed R0 blocking defects** in
`10-BLOCKING-FINDINGS.md`. It is deliberately not a replacement architecture, and
I have not authored one.

It contains **no** R1 implementation mechanic, **no** R2 production evidence
requirement and **no** R3 high-assurance control. None of the nine non-blocking
conditions in `20-LATER-LIFECYCLE-CONDITIONS.md` is routed into this delta. The
trust chain, the metadata model, the metadata role table, the domain-separation
table, the lifecycle ingress set, the transaction invariant, the bootstrap
assumption, the CI/headless model, the D-0007 transition rule and the non-goals are
all **unchanged and uncontested** — the candidate got them right and they should
not be reopened.

Two corrections, in two documents. Both are text-level. Neither changes any
component, boundary or trust direction.

---

## CD-R0-1 — Scope the signed floors explicitly across all six ingresses, and resolve the below-floor recovery case

**Closes:** `SRR-R0-H1` (HIGH). **Touches:** `spec/architecture/ARCH-0003.yaml` §7,
`release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md` §"Lifecycle
ingress invariant" and §"Freshness and revocation".

### What must become true

1. **The floor rule must be stated over ingresses, not over the word `rollback`.** The architecture must say that no ingress — `init`, `adopt`, `update`, `reinstall`, `rollback` or `recovery` — may place the machine on a release below the protected local high-water or below the signed minimum secure release. Today every floor statement names only `rollback`, which is also the name of one specific ingress, leaving the other five unscoped by construction.

2. **The `recovery` ingress's second admissible object must be qualified.** "Installed valid recovery path" must state that local installed-integrity records (D-0007 payload ↔ `KERNEL_MANIFEST.json` ↔ `framework.lock`) establish *that the local copy is intact*, and do **not** establish that it is admissible. Admissibility remains the floor check. This is already the owner's position in OWNER-DIRECTIVE-0004 ("they are not the first-install authenticity root"); the architecture must not let it be read away at the one ingress that consults no metadata.

3. **The below-floor recovery case must be decided and stated** — see the owner decision below. Whatever the owner chooses, the architecture must state the outcome for a machine whose only complete local state is below its own floor, because both possible behaviours are currently consistent with the text and they fail in opposite directions.

4. **The revoked-binary allowance must be made consistent with (1).** `ARCH-0003.yaml:91` permits a known-revoked binary to perform `recovery`. The architecture must state that this allowance restores an admissible state and cannot be used to re-establish the revoked release itself.

### Owner decision required inside this item

`NEW-OWNER-DECISION-REQUIRED` — one bounded trade-off, security against
availability:

- **(a) Strict.** Below-floor recovery is always refused. A machine with no at-or-above-floor complete local state must be re-initialised from an authenticated release. Strongest downgrade protection; accepts an unrecoverable-in-place case.
- **(b) Break-glass.** Below-floor recovery is permitted only under an explicit, separately authorised local authority (not a repository record, not an environment variable, not a caller field), is recorded, and marks the machine's reported state accordingly until it returns to an at-or-above-floor release.

I do not choose between these, and I do not specify the break-glass mechanism if
(b) is chosen — that is architecture authoring, and it is not mine to do. Either
choice closes `SRR-R0-H1` provided items 1, 2 and 4 above are also stated.

### Out of scope for this item

Journalling design, filesystem primitives, how recovery targets are enumerated,
recovery UX, and any test or implementation. Those are R1.

---

## CD-R0-2 — Declare the time assumption and make the currency-honesty claim conditional on it

**Closes:** `SRR-R0-M1` (MEDIUM). **Touches:** `spec/architecture/ARCH-0003.yaml`
§1, `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md` §"Declared
Phase-1 environment" (and, if the owner wishes, the §"R0 traceability" row for
assumptions).

### What must become true

1. **The declared-assumptions statement must name the local time source**, alongside the OS, administrator and bootstrap boundary that it already names, and must say whether it is treated as inside the trusted local boundary or as an untrusted input. The frozen boundary enumerates "time" separately from "OS/admin" and from "network" precisely because a clock is ordinarily derived from both, and this architecture trusts one and distrusts the other.

2. **The non-guarantee must be stated**, in the same register as the existing non-guarantees: that expiry, staleness and currency determinations are evaluated against that time source, and what the architecture does and does not promise when it is materially wrong in either direction (accepting expired metadata as fresh; rejecting fresh metadata as expired).

3. **The currency-honesty claim must be made conditional.** `00-ARCHITECTURE.md:32` "stale/unknown currency is reported honestly" and `ARCH-0003.yaml:92` should carry the same conditional form the rest of the document already uses for its other claims ("Given an authentic bootstrap verifier/root set and an uncompromised local OS/admin boundary, …"), so that an R1 verifier can write a test with a defined premise.

### Explicitly NOT required by this item

I am **not** requiring a trusted-time service, a monotonic-time source, a
time-attestation mechanism, a signed-time floor, roughtime, or any freshness
mechanism that does not depend on the clock. Any of those would be a
stronger-assurance proposal requiring explicit owner adoption under the frozen
boundary's change-control rule, and none is a condition of R0 acceptance. Expiry
**durations** remain profile parameters correctly deferred to R1/R2 and are not
touched by this item.

### Owner decision required inside this item

**None.** This completes an assumption list the owner already mandated in frozen
boundary R0 item 12.

---

## What this delta does not ask for

To be unambiguous, because the forensic meta-review documented lifecycle drift as
a recurring failure of this review loop, none of the following is requested,
implied or required by this rejection:

- any change to the trust chain, the bootstrap profile or the metadata roles;
- any restatement of TUF-standard client semantics the candidate imports by reference;
- release channel binding, root succession chaining, trust-mode identity, high-water/journal ordering, plugin source signing or offline-envelope install — all recorded as non-blocking later-lifecycle conditions, none of them here;
- any production ceremony, key, library, algorithm, duration, test, runtime, kernel, CLI, capability or migration work;
- a new architecture lineage, a RoT-1 Revision 8, resumption of CP-1, or any change to D-0007, D-0008 or ARCH-0002.

## Expected disposition after correction

Both corrections are text-level edits to two existing documents. On a corrected
candidate, the fourteen R0 items would stand at fourteen satisfied on the evidence
in this review, and the remaining conditions in
`20-LATER-LIFECYCLE-CONDITIONS.md` would carry forward to their labelled gates.
A re-review should be scoped to the corrected text and to the owner's answer on
CD-R0-1, not reopened across the whole candidate.
