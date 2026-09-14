# Output 21 — Owner options OP-1 … OP-15 (revision 5)

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved.**
> Rewritten in revision 5 for blocking class **BC4-4** (review r4 CD4-4). This page asks the owner for nothing yet and
> **decides nothing. Revision 5 states no proposal and no default for any option** (revision 4's labelled proposals are
> withdrawn). For each option it records the choices, the consequences derived from the revision-5 rules, the evidence
> (the derivation calculator `evidence/r5/CS5-tcb-capability-sets.json` wherever a capability set is stated), whether the
> choice is security-material, and where the answer is encoded.

## 0. One option set

Revision 4 had OP-1 … OP-7. Specialist A listed OC-1 … OC-8 and specialist B OC-1 … OC-5, with overlapping numbers. They
are reconciled here into one set. An item is an owner option only if every choice satisfies rule FD-1 (`29`) and HO-0001
§3, and the choices differ in security margin, availability or cost.

| Revision 5 | Revision 4 | Specialist A | Specialist B | Subject |
|---|---|---|---|---|
| **OP-1** | OP-1 | retained | retained | root keys, threshold, custodians |
| **OP-2** | OP-2 source authority (S0–S3), `release-artifact` (i)–(iii) — replaced | OC-1 | OC-1 L1 (registration part) | who registers each release |
| **OP-3** | OP-3 | retained | retained | gating for adoption, update, rollback |
| **OP-4** | OP-4 and the custody rows of OP-2 | retained | OP-4 restated | separate candidate key; custody of the remaining purposes |
| **OP-5** | OP-5 | retained | retained | trust-metadata age warning |
| **OP-6** | OP-6 (b) removed | R-CER-2 | OP-6 restated | lineage confirmation after admission |
| **OP-7** | OP-7 | OC-7 | OP-7 restated | currency for machines without a current proof |
| **OP-8** | OP-2 verification threshold | TA-11 | OC-1 (verification count) | independent verification records per registration |
| **OP-9** | OP-2 rebuilder count | OC-2 | OC-2 | reproducer set and whether the registration names binary digests |
| **OP-10** | — | OC-3 | TB-2′ | common-mode toolchain |
| **OP-11** | — | OC-5 | — | retention of releases whose non-orderable content was superseded |
| **OP-12** | — | OC-8 | OC-4 | form of the independent admitter |
| **OP-13** | — | RS-B1 | two channels (M2) | channel agreement for typed state fingerprints |
| **OP-14** | — | R-SUB-3 | OC-5 | admission-record validity on workstations |
| **OP-15** | — | OC-6 | genuine-binary rule | what a genuine but revoked running binary may do |

**Not owner options (architecture minima), with the reason:**

| Item | Reason |
|---|---|
| Revision 4 OP-2 (S0) attested source only; (S2) verification threshold 2 without registration; (S3) certification binding; `release-artifact` (i)–(iii) | each leaves the source, inputs or bytes selected below the TCB's authority (RV4-H1; CS5 controls) |
| Specialist B OC-1 L2 (two verification attestations counted by machines instead of a registration) | the pipeline still names the build inputs and constitutional content; dominated by OP-2 (b), which gives the same "no per-release root ceremony" without a lower selector |
| Specialist B OC-3 E2-open (open-ended registration ranges) | a `release-final` key selects sequence position: gap, inflation and stale-policy releases become eligible (specialist A E4; REG5 `ranges_excluded`) |
| Specialist B OC-3 E1 versus E2-closed | both are exact per-release registration, which revision 5 adopts (`23` §12) |
| Specialist A OC-4 (b)/(c) (C3 from a user-writable install) | carried requirement CR4-B-01 (b) refuses C3 there (`31` GB-4) |
| Specialist B OC-5 (c) (no validity on CI image admission records) | unbounded exposure of a runner that never receives a revocation; the image record expires with the pin (`31` R-ADM-7) |
| Trust on first use for production (revision 4 OP-6 (b)) | first admission requires a typed fingerprint, which commits to the lineage (`31` R-CER-2) |
| Distribution channel of the admitter (package manager versus owner site) | a carrier: the digest comparison selects the admitter (`31` R-ADM-2) |

## 1. Summary

| Option | Choices | Security-material | Encoded in |
|---|---|---|---|
| OP-1 | key count, threshold, custodians | yes | root v1 |
| OP-2 | (a) root threshold; (b) delegated `release-registration` quorum ≥ 2 | yes | root grants |
| OP-3 | mode A `always_gate`; mode B | yes | TPS `gating` |
| OP-4 | separate candidate key yes/no; custody of trust-state, certification, revocation, retrieval-profile, witness keys | yes (evaluation candidates, negatives, witnesses) | root grants |
| OP-5 | warning age | no (informational) | binary default |
| OP-6 | (a) once per verifier trust store; (c) on every `init` | yes | TPS `bootstrap.op6_mode` |
| OP-7 | (a) anchored only; (b) maximum anchor age; (c) expiring witnesses; (d) compiled epoch; parameters | yes | TPS `bootstrap` |
| OP-8 | number of independent verification records: 1 or 2 (or more) | yes | TPS `registration.min_verification_records` |
| OP-9 | (a) n=2, q=2; (b) n=3, q=2; (c) n=3, q=3; each with or without (d) the registration naming binary digests after the custodians' own reproduction | yes | root grants (`quorums.reproducer`), TPS `registration.binary_digests_registered` |
| OP-10 | (a) accept TA-12; (b) diverse reproducer; (c) owner-built toolchain | yes | ceremony record; input manifest |
| OP-11 | (a) keep older releases eligible; (b) raise `min_release_sequence` on security-relevant change; (c) grace period | yes | TPS `eligibility` |
| OP-12 | (a) separate compiled program; (b) auditable script over platform tools; (c) helper machine | yes | release protocol; registration `admitter` |
| OP-13 | (a) one channel; (b) two agreeing channels | yes | TPS `bootstrap.channel_quorum` |
| OP-14 | (a) validity on image records only; (b) on every record | yes | TPS `bootstrap.workstation_record_max_validity_days` |
| OP-15 | (a) C0 only; (b) C0–C2 | yes | TPS `bootstrap.revoked_self_scope` |

Every TPS field above changes only through a computed reduction when moved in the weaker direction (`19` §10.6).

## OP-1 — Root role

- **Choices.** Key count and threshold; custodian independence; hardware and locations.
- **What the root threshold signs in revision 5.** Every Trust Policy (Constitutional Surface classification, floors,
  precedence registration, Overlay Surface, owner-domain slots and binding groups, eligibility, bootstrap and registration
  parameters, lowering history) and every root version (grants, including the reproducer quorum and, under OP-2 (b), the
  delegated registration keys). Under OP-2 (a) it also signs every release registration.
- **Consequences.** Losing the threshold means a new lineage and re-admission everywhere. Root-threshold compromise (A8) is
  outside TA-4; CS5 labels every minimal set that needs it.

## OP-2 — Who registers each release

| Choice | Minimal sets that involve the registration authority (CS5) | Operational consequence |
|---|---|---|
| (a) root threshold | malicious source or inputs: {cust1, cust2, OP-8 verification keys} = root threshold compromise (A8); key theft: {root keys ×2, OP-8 verification keys, q reproducer keys, trust-state key, the victim's channel(s)} | a root ceremony per release (the same ceremony registers source, inputs, content, final and targets; `30` R-REG-6); a security fix waits for it; root custodians perform R-REG-3 themselves |
| (b) delegated `release-registration` quorum (compiled threshold ≥ 2; keys hold no other purpose; root grants and rotates) | the same sets with two delegated custodians or keys in place of the root threshold: two delegated custodians plus OP-8 verification keys register malicious source, inputs or non-orderable content for new releases, accepted everywhere | root keys stay offline between rotations; the delegated quorum is the concentrated target; remedy: root rotation and revocation of its registrations. Floors and registered precedence (root) still bound constitutional content |

Neither choice changes the verifier. Both choices refuse one stolen key plus pipeline input.

## OP-3 — Gating for adoption, update and rollback

Unchanged from revision 4 (review r4 found OP-3 accurate), with one restatement from carried RV4-M2: mode A's "never
answerable by any agent path" holds for `gov decide` and every `gov`-executed child under allow-list confinement
(CR4-B-01); an agent with an unconfined shell in the same account is A3. Decision pins now have a maximum validity
(CR4-B-09). Mode B adds TA-7 for currency.

## OP-4 — Separate candidate key; custody of the remaining purposes

- **Separate candidate key (yes/no).** Under revision 5 neither `release-candidate` nor `release-final` selects a
  production binary or a policy root; they appear in no minimal set (CS5 INV-RF). "No" lets the everyday key forge
  evaluation candidates for gated evaluation projects, and a final whose registration does not exist. The revision-4 key
  counts that depended on OP-4 no longer apply (RV4-L7).
- **Custody and sharing** of `trust-state`, `certification-status`, `revocation`, `retrieval-profile` and
  `freshness-witness` within the compiled whitelist (`05` §3). The trust-state key's reach is `17` §15; on pinned machines
  it no longer carries C3 to a later descendant (`24` §4.4).

## OP-5 — Trust-metadata age warning

Informational only; measured from the latest anchoring event; always shown when `UNANCHORED` or `CURRENCY_UNPROVEN`.

## OP-6 — Lineage confirmation after admission

| Choice | Consequence |
|---|---|
| (a) once per verifier trust store | the lineage is confirmed by the admission fingerprint (`31` R-CER-2) and not asked again on this machine |
| (c) on every `init` | the operator re-types the lineage id per project; more friction; no additional protection against a transport adversary once admitted |

TA-5 ceremonies establish nothing on a binary that has not been admitted (`31` GB-1; D-A04).

## OP-7 — Currency for machines without a current proof

Choices and parameters as revision 4 `24` §9. Restated consequences:
- **(a), (b), (d) and stateless runners (RV4-M4, CR4-B-03).** On a machine with a verifier trust store, every ingested
  non-future statement raises the clock high-water, so a clock set back below it fails closed (P4r5
  `CLOCK-RV4-B-A13`). On a machine without one, pin validity and the C3 window rest entirely on TA-7: a clock set back makes
  an expired pin valid (P4r5 residual demonstration).
- **(c) (RV4-M3, CR4-B-02).** The witness service takes the fingerprint to witness only from the owner's ceremony or the
  independent channel, and the C3 witness threshold is met by keys under at least two custodians. If one service holds
  both keys, compromise of that service alone presents any genuine older TSS as latest on witness-reliant machines
  (one-custody consequence).
- **First admission** does not depend on OP-7 (typed fingerprint, no clock).
- **Pinned machines (all choices):** a pin proves currency only for the TSS it names (CR4-B-07 option 1); C3 against a
  later TSS needs a new pin, a typed fingerprint or witnesses.

## OP-8 — Independent verification records per registration

| Choice | Malicious source (CS5 G_SRC) | Cost |
|---|---|---|
| 1 | {pipeline, vp1}; {cust1, cust2, va1}; key theft {ch…, reg keys ×2, rep×q, ts, va1} | one verifier |
| 2 | {pipeline, vp1, vp2}; {cust1, cust2, va1, va2}; key theft adds `va2` | a second, independent verification process |

`vpN` is compromise of a verification *process* (a verifier that lies), not key theft; under either choice stolen
verification keys alone register nothing (INV-SRC-KEYS). Route I (an insider change honest verification accepts) is TB-4 under
both.

## OP-9 — Reproducer set; registration of binary digests

| Choice | Malicious bytes for a genuine registration (CS5 G_BYTES) | Availability and cost |
|---|---|---|
| (a) n=2, q=2 | processes {rp1, rp2}; key theft (P2/FA1) {ch1, rep×2, ts, transport} or {ch1, reg keys ×2, rep×2, ts}; FA2 adds `ch2`; P1: none | one unavailable reproducer blocks a binary release; one stolen key blocks a release by conflict |
| (b) n=3, q=2 | processes {rp1, rp2, rp3}; key theft with any 2 reproducer keys as in (a) | tolerates one unavailable reproducer; a third independent environment and custodian |
| (c) n=3, q=3 | processes {rp1, rp2, rp3}; key theft with all 3 reproducer keys | any one unavailable blocks a release |
| (d) added to (a) | {cust1, cust2, rp1, rp2}; key theft {ch1, reg keys ×2, rep×2, ts} (FA2 adds `ch2`) | a registration ceremony after every build, on reproduction hardware |
| (d) added to (b) or (c) | {cust1, cust2, rp1, rp2, rp3}; key theft with 2 or 3 reproducer keys | as above |

Reproducer keys are online more often than root keys; the quorum counts keys and processes, not custody strength. Every
choice needs bit-for-bit reproducibility under the normative build profile (IR-REP-1…3).

## OP-10 — Common-mode toolchain

| Choice | Consequence (CS5 G_TOOLCHAIN) | Cost |
|---|---|---|
| (a) accept TA-12 | {toolchain_up}: a compromised upstream toolchain release that passes the checksum check yields identical malicious bytes from every honest reproducer | none |
| (b) diverse reproducer (one reproducer uses an independently bootstrapped compiler and must match) | {toolchain_up, diverse_tc} or {toolchain_up, rp1} | high engineering and build-time cost; may restrict compiler features |
| (c) owner-built toolchain archive registered as an input | {owner_tc} (the owner's toolchain build) | the owner's toolchain build is itself registered and reproduced |

## OP-11 — Retention of releases whose non-orderable content was superseded

Exact per-release registration guarantees that a later release never carries superseded content without a gated reduction
(`23` §12). It does not decide whether older releases stay eligible at their own registration.

| Choice | Consequence |
|---|---|
| (a) keep eligible | installed projects keep working; on machines without a per-project record, a repository writer can deliver an older eligible release with its older content (RR-2); machines with a record refuse the downgrade (E10) |
| (b) raise `min_release_sequence` in the ceremony of every security-relevant content change | older releases become ineligible where the Trust Policy reaches; installed projects fall back to the embedded snapshot or refuse at decision points until they update; the classification of "security-relevant" is a ceremony judgement |
| (c) grace period (`eligible_until` on the older registration) | as (a) before the date, (b) after it; adds TA-7 to eligibility |

## OP-12 — Form of the independent admitter

| Choice | Trust added | Cost |
|---|---|---|
| (a) separate compiled program, registered and reproduced, digest in the channels | the platform hash tool; TA-5 | a second implementation of the predicate and a differential conformance suite |
| (b) auditable script over platform tools (hash, Ed25519 verification, canonical JSON), digest in the channels | those tools and interpreter (TA-1b) | the tools must implement GOV-JCS-1 and DSSE PAE exactly; weaker on Windows |
| (c) an admitted `gov` on another machine performs the predicate and hands over the binary and record | that machine and the transfer channel become part of the new machine's first-admission TCB | none extra; concentrates risk on helper machines |

## OP-13 — Channel agreement for typed state fingerprints

| Choice | Consequence |
|---|---|
| (a) one channel | a stale or compromised channel selects the state it names for first admission (RS-B1); malicious-bytes key-theft sets need `ch1` (CS5 FA1 rows) |
| (b) two agreeing channels | a single stale or compromised channel gives `CHANNEL_DISAGREEMENT`; key-theft sets need `ch1` and `ch2` (FA2 rows); first install is unavailable while either channel is unreachable |

## OP-14 — Admission-record validity on workstations

| Choice | Consequence |
|---|---|
| (a) validity on CI image records only | a workstation binary revoked after admission that never receives the revocation keeps working: RS-1 core |
| (b) validity on every record | also bounded on workstations; periodic re-admission, unavailable while offline past the validity |

## OP-15 — What a genuine but revoked running binary may do

| Choice | Consequence |
|---|---|
| (a) C0 only | strongest; incident response needs a new binary admitted first |
| (b) C0–C2, C3 refused | governed work continues while a replacement is obtained; a binary revoked for a C1–C2 enforcement defect keeps enforcing with that defect until replaced |

## Combinations that change security (computed)

| Combination | Consequence |
|---|---|
| OP-2 (b) + OP-8 = 1 | {two delegated custodians, one verification key} registers malicious source, inputs or non-orderable content for new releases, accepted everywhere |
| OP-8 = 1 + any OP-9 | one compromised verification process plus pipeline input yields a malicious source faithfully built (TB-4′) |
| OP-9 (a) + OP-13 (a) | first admission: {ch1, 2 reproducer keys, trust-state key, transport} |
| OP-9 (c) or (d) + OP-13 (b) | first admission key-theft sets need both channels and all three reproducer keys, or the registration keys |
| OP-10 (a) + any | {toolchain_up} yields identical malicious bytes (TA-12) |
| OP-7 (c) + one witness service holding both keys | stale state witnessed by one service compromise (CR4-B-02 consequence) |
| OP-12 (c) + any | the helper machine is in the TCB of every first admission it serves |

No option is approved by this document.
