# OWNER-DESIGN-REQUIREMENTS-0001 — Product-owner design requirements for RoT-1 Revision 7

| Field | Value |
|---|---|
| Record | OWNER-DESIGN-REQUIREMENTS-0001 |
| Source | the product owner, in the Phase 1 orchestration chat, 2026-09-14 (owner-initiated after the orchestrator's summary of revision verdicts and OP-1…OP-16) |
| Classification | **binding design inputs** to Root-of-Trust architecture revision 7 |
| Not | formal approval, activation or ratification of D-0008; not the `GATE-OWNER-D0008` answer |
| D-0008 state required by the owner | `status = PROVISIONAL`, `proposal_state = PROPOSED`, `human_approved = false` |
| D-0007 | remains ACTIVE until the final independently accepted D-0008 package is presented to and formally approved by the product owner |
| Revision 6 | review panel and synthesis finish normally; all evidence is preserved |
| Recorded by | the Phase 1 orchestrator. The text below is the owner's message **verbatim** and is authoritative. The index in `OWNER-DESIGN-REQUIREMENTS-0001.yaml` is a derived convenience; where they differ, this text governs. |

## Verbatim owner text

```text
Record the following as PRODUCT-OWNER DESIGN REQUIREMENTS for the next Root-of-Trust architecture revision.

These are binding inputs to Revision 7 architecture design, but they are NOT yet formal activation/approval of D-0008.

Keep:

- "D-0008.status = PROVISIONAL"
- "D-0008.proposal_state = PROPOSED"
- "D-0008.human_approved = false"
- D-0007 ACTIVE until the final independently accepted D-0008 package is presented to and formally approved by the product owner.

Let the current Revision 6 reviewers/synthesis finish normally and preserve all evidence.

Whether Revision 6 is accepted or rejected, use its complete findings plus the owner requirements below to produce a concretised Revision 7 architecture with the unnecessary option branches removed from the certified production profile.

The goal is to stop reviewers having to reason about a combinatorial tree of optional trust modes.

D-0008 architectural direction

Selected design target: Option C — RoT-1.

A, B, D, E and F are not supported production alternatives for the certified Governance OS profile.

Revision 7 should retain useful mechanisms inspired by TUF/transparency/reproducible-build systems where appropriate, but the certified architecture is RoT-1 Option C.

This is a DESIGN DIRECTION, not yet formal activation of D-0008.

---

OP-1 — Root keys

"keys = 3"

"threshold = 2-of-3"

Custodial roles:

1. Product Owner Root Custodian
2. Independent Security Root Custodian
3. Recovery Root Custodian

Requirements:

- physically separate custody;
- offline hardware-backed signing devices;
- root private keys never stored in repository, CI, cloud build environment or ordinary development workstation;
- no single custodian can exercise root authority;
- root ceremony required for Trust Policy/root-lineage changes, not ordinary releases.

If named human custodians are not yet appointed, preserve these as required custodial ROLES rather than collapsing them into one person's ordinary workstation.

---

OP-2 — Release registration

Select:

"(b) delegated registration quorum"

Use:

"2-of-3"

single-purpose hardware-backed registration keys delegated by the root.

Root keys remain offline for normal release operation.

Registration authority must be purpose-separated from:

- candidate signing;
- certification;
- trust state;
- revocation;
- retrieval-profile signing.

No individual registration key may register a production release alone.

---

OP-3 — Gating

Select:

"Mode A — always_gate"

Require a LOCAL Human Trust Gate for:

- adoption;
- production installation;
- update;
- rollback;
- downgrade/recovery where policy requires.

Certification never silently removes the local human trust gate.

Repository gate records are requests only and cannot authorise trust operations.

Do not implement Mode B in the initial certified production profile.

---

OP-4 — Candidate key and key custody

Separate candidate key:

"YES"

The candidate key is single-purpose and may create evaluation candidates only. It cannot create production release authenticity/certification.

Required purpose separation for other trust functions:

Registration

2-of-3 dedicated registration custodians as OP-2.

Production release artifact/final identity

Require threshold protection; no threshold-1 key may by itself mint a production "gov" binary.

Use at least 2 independent authorised signatures consistent with the accepted Revision-7 trust chain.

Trust state

2-of-3 dedicated trust-state authority.

Certification

Two independently produced verifier/certifier records are required under OP-8.

Revocation

2-of-3 dedicated revocation authority, with root-threshold emergency recovery/rotation capability where the architecture specifies.

Retrieval profile

Separate retrieval-profile signing purpose. This key cannot sign kernel/release/trust-state material.

Witness

No witness service in the initial certified profile because OP-7 is anchored-only.

Every key/statement purpose must remain domain-separated and mechanically enforced.

---

OP-5 — Metadata age warning

"30 days"

Informational only.

It must never silently change security decisions or become a hidden clock-based trust root.

---

OP-6 — Lineage confirmation

Select:

"(a) once per machine"

After successful first admission, require the human operator to confirm the expected trust-root/lineage fingerprint once for that verifier trust store/machine.

Do not require confirmation at every "gov init".

A later root-lineage change requires re-admission/reconfirmation according to the trust architecture.

---

OP-7 — Machines unable to prove trust-state currency

Select:

"(a) anchored only"

No witness-service path in the initial certified profile.

Parameters:

- normal workstation/local trust-state anchor validity: 90 days maximum;
- CI admission/image anchor validity: 7 days maximum;
- production install/update/rollback requires a fresh local trust confirmation/state anchor no older than 24 hours;
- after the applicable anchor expires, governed mutation degrades to C0/read-only diagnostics until re-anchored;
- no stale/unanchored state may be presented as current;
- locally retained high-water trust state may never move backwards during re-admission.

A machine that has never received newer metadata cannot be claimed to know it. The architecture must state this honestly.

Do not implement OP-7(b), (c) or (d) in the initial certified production profile.

---

OP-8 — Independent verification records

Require:

"2"

independent verification records for every production release.

They must originate from genuinely separate verifier executions/evidence, not two signatures over one self-produced conclusion.

Neither verifier alone creates production eligibility.

---

OP-9 — Independent reproducers

Select:

"(b) 2-of-3"

plus:

"(d) registration includes final binary digests"

Requirements:

- three eligible independent reproducer roles;
- any two matching reproducible results required;
- final binary/content digests become part of the release registration;
- mismatched reproduction blocks production registration;
- reproduction evidence identifies exact source, toolchain and build-environment identities.

---

OP-10 — Compiler toolchain

Select:

"(b) diverse, independently bootstrapped compiler agreement"

The certified release must not rely solely on an upstream binary compiler archive as the root of build correctness.

Define "independent" by provenance/build lineage, not merely by different filenames or mirrors.

The architecture must establish how compiler/toolchain identities become registered inputs.

If a target platform cannot satisfy this requirement, that target is not certified rather than silently falling back to OP-10(a).

---

OP-11 — Superseded security-relevant content

Select:

"(b) raise the minimum release sequence at every security-relevant content change"

An older authentic release may remain historically authentic but becomes ineligible where the security minimum has advanced.

Do not use grace periods/clocks for the initial certified profile.

The repository/transport must never choose among eligible release versions on behalf of the local trust authority.

---

OP-12 — First-install admitter

Select:

"(a) separate compiled program, registered and reproduced"

The admitter:

- must not be "gov" validating itself;
- has a smaller fixed responsibility;
- is authenticated under the root/first-contact trust chain;
- is independently reproduced;
- verifies and admits the first "gov" binary;
- cannot be replaced by an arbitrary repository copy.

Do not implement helper-machine admission or script-based admission as certified alternatives in the initial profile.

---

OP-13 — First-contact/new-machine source

Select:

"(b) two owner-controlled sources under genuinely separate custody; both must match"

Initial concrete channels:

1. authenticated private release channel;
2. separately controlled immutable/offline release mirror/media channel.

They must provide byte-identical first-contact/admitter/trust-base material.

A mismatch fails closed.

Neither source alone is sufficient.

Do NOT support in the initial certified production profile:

- OP-13(c) "either suffices";
- platform/OS package manager as an independent root;
- OP-13(d) as the sole generic admission route.

The architecture must not permit one trust-state publisher to compose the first-contact code carried by both channels.

---

OP-14 — Admission-record expiry

Select:

"(b) all admission records expire"

Use the OP-7 validity limits.

Re-admission MUST preserve and enforce the machine's stored trust high-water mark.

Re-admission may never reset or lower previously known:

- revocations;
- root versions;
- trust-state sequence;
- minimum eligible release;
- security floors.

---

OP-15 — Genuine but revoked binary

Select:

"(a) read-only only"

A revoked binary may perform bounded diagnostics sufficient for recovery, but:

- no governed mutation;
- no installation/update;
- no policy enforcement relied upon for production work;
- no release/certification operation.

Recovery proceeds using a newly admitted eligible binary.

---

OP-16 — Build environment

Select:

"(b) require matching builds from at least two genuinely independent supplier classes"

"Independent supplier" must be defined by actual provenance separation, including:

- base OS/build image lineage;
- package source;
- build-system provenance;
- signing/control infrastructure;

not by distribution label alone.

Use static/self-contained linking wherever practical to reduce environment dependence.

For the initial certified release, it is acceptable to certify a narrow platform/target set rather than weaken this rule.

The architecture remains portable, but an OS/architecture target is not labelled CERTIFIED until its independent build-environment requirements are satisfied.

---

First-contact composer/signer

The first-contact/admitter trust base must NOT be composed by the ordinary trust-state publisher.

The canonical first-contact trust base/admitter identity is approved by:

"root threshold 2-of-3"

after independent reproduction/verification appropriate to the admitter.

Ordinary release/trust-state keys may not redefine the first-contact root.

---

Build-environment manifest author/signer

No single manifest author is authoritative.

The environment manifest must be generated deterministically from the measured build inputs/environment and content identities.

It becomes authoritative for a release only when:

1. the required independent build/reproducer evidence agrees with it; and
2. the delegated registration quorum "2-of-3" signs/registers that exact manifest/content identity.

A different label naming the same upstream/provenance chain is NOT independent.

---

Initial certified-scope limits

Reduce architecture combinations aggressively.

The INITIAL CERTIFIED profile supports only:

- D-0008 Option C / RoT-1;
- OP-2(b);
- OP-3 Mode A;
- OP-7(a);
- OP-10(b);
- OP-12(a);
- OP-13(b);
- OP-16(b).

Explicitly exclude initially:

- witness service;
- helper-machine admission;
- script-based certified admission;
- OP-13(c) "either suffices";
- platform package signing as an alternate independent root;
- Mode-B no-human-gate updates;
- clock/grace-period trust;
- unanchored governed mutation.

Keep unsupported paths out of the certified executable surface where practical rather than implementing dormant combinations.

The architecture should be extensible later through a separately governed/verified release.

For initial platform certification, prefer a small number of reproducible/static targets. Additional Windows/macOS/Linux targets can be certified individually when their build-environment/reproduction requirements are satisfied; do not weaken the trust model merely for immediate platform breadth.

---

Revision-7 requirement

Let Revision 6 review and synthesis finish and preserve its evidence.

Then, unless the orchestrator proves that the accepted Revision-6 architecture already implements these exact owner requirements without architectural change, create RoT-1 Revision 7 using:

1. all Revision-6 reviewer/synthesis findings;
2. these owner design requirements;
3. one concrete supported production profile rather than the previous option tree.

Update the D-0008 PACKAGE so that OP-1 through OP-16 and the first-contact/environment/scope decisions are represented explicitly.

Unused alternatives may remain documented historically, but they must not remain active production modes in Revision 7.

Do not set D-0008 ACTIVE yet.

Do not set "human_approved: true" yet.

Do not supersede D-0007 yet.

Have fresh independent reviewers attack the concrete Revision-7 configuration, including its real combinations and exclusions.

Only after:

"ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED"

present the final D-0008 package back to the product owner for formal ratification.

Unless an independent reviewer identifies a genuinely new owner trade-off, do not reopen these selected design parameters merely because another implementation is possible.
```
