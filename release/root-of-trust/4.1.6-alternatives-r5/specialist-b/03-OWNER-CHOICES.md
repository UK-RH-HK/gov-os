# 03 — Owner choices raised by the specialist-B alternative (AR-0010)

Only genuine trade-offs are listed: choices where every option satisfies the invariants of `00` §2, and the options
differ in cost, exposure or availability. **None is decided or proposed.** Minimal attack sets come from
`evidence/F1-tcb-fact-derivation.json`, F2 and F3.

Architecture minima are **not** options:
- two independent verifications for source legitimacy;
- a reproduction quorum of at least 2;
- no pass-through purposes;
- a single-valued registration;
- an evaluator that is not the candidate.

Revision 4's OP-2 (S0), and a threshold-1 source or build authority, do not meet them and are not offered.

## OC-1 — How machines check source legitimacy

| Option | What machines verify | Minimal accepted sets for a malicious source (F1) | Cost |
|---|---|---|---|
| **L1** root-threshold Release Admission Statement, signed only against two first-hand verification records | one root-threshold statement per release | `{root1, root2}`; `{vp1, vp2, pipeline}` (two compromised verification processes). Stolen verifier keys alone do not help: `{va1, va2, pipeline}` → `NO_FINAL`. | one root ceremony per binary-shipping release; two verifiers; a smaller predicate for the admitter |
| **L2** two verification attestations counted by machines | two attestations referenced by the TSS | REJECTED verdict can be suppressed by the pipeline: `{va1, va2, pipeline}` (and process variants). REJECTED verdict visible: `{vp1, vp2, pipeline}` or seven-capability sets. `{root1, root2}` in both. | two verifiers; no per-release root ceremony for the source |

**Consequences to know.**
- L1 takes verifier keys off every attack path, at the price of root custody being touched per release.
- L2 keeps root keys offline between policy changes. Under L2, two stolen verifier keys suffice unless the REJECTED
  verdict reaches the publisher and signers through a channel the pipeline does not control.

## OC-2 — Reproduction quorum and custody

| Option | Minimal accepted sets for malicious bytes of genuine source (F1) | Cost |
|---|---|---|
| (a) *q* = 2 independent reproducers | `{ba1, ba2, pipeline}`, `{ba1, ba2, ts}`, `{root1, root2}` | two reproducer services, disjoint custody |
| (b) *q* = 3 | `{ba1, ba2, ba3, pipeline}`, `{ba1, ba2, ba3, ts}`, `{root1, root2}` | three services |
| (c) *q* = 2, at least one reproducer key under root-grade custody (offline hardware) | as (a) in key count; one key is harder to steal | an offline reproduction step per release |
| (d) root co-signers reproduce, and binary digests are admitted at root threshold | root threshold for bytes | a root ceremony after every build, run on reproduction hardware |

**Consequences to know.**
- Reproducer keys are online more often than root keys, so *q* counts keys, not custody strength.
- Every option depends on bit-for-bit reproducibility under a normative build profile. F5: plain builds differ across
  Cargo home paths; path-remapped builds are identical on one machine and toolchain. Cross-OS reproduction is unproven.

## OC-3 — Form of release-scoped registration

| Option | `release-final` blast radius | Machine holding only an older TPS | Availability and ceremony (F3) |
|---|---|---|---|
| **E1** admission by exact final digest | no policy root | forged later finals refused (not admitted) | a root registration per release; a genuine release is unusable until admitted |
| **E2-closed** sequence-scoped registration, every sequence registered | tunable, `release_bound` and informational leaves of registered sequences | forged later finals refused (exit 3) | a root registration per release; genuine 4.1.8 exit 3 until registered, then 0 |
| **E2-open** last range open-ended | as E2-closed, plus later-sequence finals carrying that TPS's content | **forged later final with the registered content eligible** (exit 0; residual RS-E2o) | a root ceremony only when non-orderable content changes; genuine 4.1.8 with unchanged content exit 0 |

**Consequences to know.**
- E1 and E2-closed need no ceremony beyond L1 when combined with it: one root ceremony per release covers source,
  content and final.
- E2-open is the only form without a per-release root ceremony, and the only one with RS-E2o.

## OC-4 — Form and distribution of the admitter

| Option | Trust added | Cost |
|---|---|---|
| (a) separate reproducible binary `gov-admit`, root-registered, digest in both channels | the operator's `sha256sum` and TA-5 | a second implementation of AP and a differential conformance suite |
| (b) auditable script over standard tools (hash, Ed25519 verification, canonical JSON), digest in both channels | those tools; a human-readable procedure | the tools must implement GOV-JCS-1 and DSSE PAE exactly; weaker on Windows |
| (c) an already-admitted `gov` on another machine performs AP and hands over the Admission Record and binary | that machine's integrity and the transfer channel | the other machine becomes part of the new machine's TCB for first admission |

**Consequences to know.** Every option keeps TA-5 as the root. (c) adds a machine to the base case. (b) moves
complexity into the operator's environment.

## OC-5 — Admission-record validity on images and workstations

| Option | Exposure of a binary revoked after admission, on a machine that never receives the revocation | Cost |
|---|---|---|
| (a) validity on image records only (proposal text of `01` §4.1) | workstations: RS-1 core. Images: bounded by record validity (F2 `CI_image_record_within_validity`). | image re-provisioning with pins |
| (b) validity on every record | also bounded on workstations | periodic re-admission on workstations: an availability loss when offline |
| (c) no validity | unbounded on images until the runner receives the revocation | none |

## Existing options restated under the alternative (not decided)

| Option | Restatement |
|---|---|
| OP-1 | unchanged; the root also signs admissions under L1/E1 |
| OP-2 | replaced by OC-1, OC-2 and OC-3; `release-artifact` (i)–(iii) no longer exist |
| OP-3 | unchanged (review r4: accurate); a decision pin cannot approve an admission |
| OP-4 | not security-material for the TCB under the alternative: the smallest attack sets are unchanged in all 32 F1 rows. It still affects forged candidates for evaluation projects. |
| OP-5 | unchanged |
| OP-6 | TA-5 ceremonies establish a trust fact only on an admitted binary; OP-6 (a)/(c) run after admission |
| OP-7 | unchanged, with RS-2 restated per RV4-M4 and the witness input and custody per RV4-M3. Admission always uses the channel as currency; no OP-7 answer relaxes it. |

## Combinations that change security

| Combination | Consequence |
|---|---|
| L1 + E1 (or E2-closed) + *q* = 2 | one root ceremony per release covers source, content and final. Malicious bytes: 2 reproducer keys + pipeline or trust-state key. Malicious source: root threshold or two verification processes + pipeline. `release-final`: no policy root (E1). |
| L2 + E2-open + *q* = 2 | no per-release root ceremony. Malicious source: 2 verifier keys + pipeline when REJECTED can be suppressed. RS-E2o applies. |
| any + OC-2 (d) | bytes at root threshold; a root ceremony per build |
| any + OC-4 (c) | the helper machine is in every first-admission TCB it serves |
