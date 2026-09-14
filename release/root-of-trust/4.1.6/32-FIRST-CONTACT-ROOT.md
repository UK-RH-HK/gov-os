# Output 32 — The first-contact root of CP-1: an authority record at root threshold, first-hand publication, bounded currency (BC6-1, BC6-2)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Rewritten in revision 7 for the certified profile CP-1 (`35`). It closes blocking classes **BC6-1** (review r6 RV6-H1:
> first-contact values composed, designated and submitted by parties outside the stated root) and **BC6-2** (RV6-H2: unbounded
> first-contact currency), under the stricter reading of HO-0019 §2b and the owner requirements OP-7 (a), OP-12 (a), OP-13 (b),
> OP-14 (b) and "First-contact composer/signer" (OWNER-DESIGN-REQUIREMENTS-0001).
> Removed from the certified profile (history at `4106885`): revision 6's first-contact manifest composed per Trust State
> (EX-23), the unselected source answers (EX-04, EX-05, EX-17, EX-18) and `gov trust fc-procedure` (EX-24).
> Amended to match: `31` §3–§4, §9; `25` AP-1…AP-3; `06` §2–§3; `05` KS-18; `01` TA-5′; `24` §4.4.
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

Review r6 found two mistaken equivalences:

| Mistaken equivalence (revision 6) | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| *a value agreed across independent sources is established by those sources* (RV6-H1) | the trust-state publisher process that composed the first-contact manifest (rank 3); the carrier or unadmitted binary that printed which sources to read and which steps to run (rank 5); the platform package submitter (rank 5) | the lineage, the evaluator and the first TCB of a machine |
| *the value the operator uses at first contact is current* (RV6-H2) | a replayed package, stored media or CI codes, a stale or designated page (rank 5); a re-admission that ignored the store | a revoked, even malicious, binary as the current TCB, also on a machine that holds its revocation |

Agreement between sources shows that they carry the same value. It does not show who composed it, whether it is recent, or
whether the operator read the right sources.

## 2. Invariant (CP-1)

1. **Lineage and evaluator.** At first contact the lineage and the evaluator are selected only by a statement signed at the
   root threshold (the **First-Contact Authority record**, §3), issued after the admitter's registration, reproduction and two
   verification records, under the lineage compiled into every admitter build.
2. **State.** The state is selected only by a Trust State signed by 2 of 3 trust-state keys that names that authority record.
   Each of the two sources publishes its code only after verifying it first-hand (§5). The admitter refuses a state older than
   24 hours, and on a machine with a store never selects below what the store holds.
3. **No other selector.** No value that selects lineage, state or evaluator is composed or supplied solely by the trust-state
   publisher, an unadmitted binary, a carrier or a package submitter. The source identities come from the root ceremony record,
   delivered to operators outside any release carrier.
4. **Stated remainder.** What remains is the **first-contact root** of §9, computed by CS7 and equal to the executed minima.

## 3. The First-Contact Authority record (FCA)

`governance-os.first-contact-authority` payload (`schemas/first-contact-authority.schema.json`), statement type
`first-contact-authority+json`, purpose `first-contact-authority`:

| Field | Content |
|---|---|
| `fca_sequence` | strictly increasing per lineage |
| `lineage` | the trust-root id (digest of root v1) |
| `root_version` | the root version whose thresholds signed it |
| `profile_id` | `governance-os.rot1/CP-1` |
| `admitters` | `{certified target → SHA-256 of the registered, reproduced gov-admit}` (OP-12 (a)) |
| `certified_targets` | the targets meeting CC-1…CC-9 (`35` §5) |
| `sources` | exactly two: `{source_id, kind, locator, custodian_role, custody_domain}`; kinds `authenticated-private-release-channel` and `immutable-release-mirror` (OP-13 (b)) |
| `procedure_digest` | SHA-256 of the published operator procedure text (FC-PROC) |
| `admitter_evidence` | `{registration_digest, reproduction_digests[], verification_records[]}` of the admitter release |
| `supersedes_fca_digest`, `issued_at` | the previous record; issuance time |

| ID | Rule | Refusal |
|---|---|---|
| **R-FCA-1** | **Issued at root threshold after the admitter's evidence.** The root custodians sign an FCA only after each listed admitter is registered by the 2-of-3 registration quorum, reproduced bit for bit by at least 2 of 3 reproducers under CC-1…CC-5, and verified by two independent records (OP-8). Each root custodian checks those statements itself and recomputes each admitter digest from bytes it obtained by digest. The FCA names that evidence. | ceremony refuses (`draft-policy`) |
| **R-FCA-2** | **Targets.** `admitters` keys equal `certified_targets`, and every listed target is `CERTIFIED` in the root-signed Trust Policy (CC-9). | `TARGET_NOT_CERTIFIED` |
| **R-FCA-3** | **Supersession.** A new FCA carries the next `fca_sequence` and the digest of the one it supersedes. A machine's stores hold the highest `fca_sequence` seen, and admission never selects a lower one. | `FIRST_CONTACT_AUTHORITY_BELOW_HELD` |
| **R-FCA-4** | **Root keys only.** The `first-contact-authority` purpose is granted only to the root keys at the root threshold (`05` KS-18). Trust-state, registration, release and revocation keys cannot redefine the first-contact root. | `FIRST_CONTACT_AUTHORITY_UNVERIFIED`; root version `PROFILE_NONCONFORMANT` |

## 4. Codes

- **Trust code:** `gov-fct:<8 hex of lineage id>:<fca_sequence>:<64 hex SHA-256 of the canonical FCA payload>`.
- **State code:** `gov-fcs:<8 hex of lineage id>:<sequence>:<64 hex digest of the Trust State statement>`.
- Every Trust State references the FCA in force: `references.first_contact_authority {fca_sequence, digest}`
  (`trust-state-statement.schema.json` v4).
- The state code is also the value typed at trust gates and anchoring confirmations on admitted binaries (`24` §3, `27` §3.1),
  read from both sources.

## 5. Sources and designation

### 5.1 Source custodians publish first-hand (R-FCS)

| ID | Rule | Refusal (custodian) |
|---|---|---|
| **R-FCS-1** | **Authority verified first-hand.** Each source custodian holds the lineage id from the root ceremony record, not from any channel. It publishes a trust code only for an FCA it verified itself at the root threshold of a root chain starting at that lineage, using its own admitted binary. | `FIRST_CONTACT_AUTHORITY_UNVERIFIED` (not published) |
| **R-FCS-2** | **State verified first-hand, monotonic.** It publishes a state code only for a Trust State that (a) verifies at the trust-state threshold within that chain, (b) references the FCA it publishes, (c) is newer than the last state it published and lists it in `prior_states`, and (d) drops no revocation, registration or published binary of that state. | `TRUST_STATE_UNVERIFIED`, `FIRST_CONTACT_AUTHORITY_MISMATCH`, `STATE_NOT_NEWER_THAN_PUBLISHED`, `STATE_NOT_DESCENDANT`, `STATE_DROPS_REVOCATIONS` / `…_REGISTRATIONS` / `…_PUBLISHED_BINARIES` |
| **R-FCS-3** | **Byte-identical material, separate custody.** Both sources publish byte-identical trust code, state code, FCA payload, procedure text and `gov-admit` bytes. The two custody domains are distinct in the ceremony record; `gov trust draft-policy` flags a shared custodian or host. | `FIRST_CONTACT_SOURCES_SHARE_CUSTODY` (draft) |

The trust-state publisher signs Trust States only as one of the trust-state keys' holders. It composes no first-contact value:
the codes are digests of statements that each source custodian verifies against thresholds it checks itself.

### 5.2 Designation (R-FCD)

| ID | Rule |
|---|---|
| **R-FCD-1** | The identities of the two sources (locator, custodian role, custody domain) and the procedure text are fixed in the root ceremony record and in the FCA's `sources` and `procedure_digest`. |
| **R-FCD-2** | Operators receive the two source identities and the procedure at onboarding, from the organisation's copy of the root ceremony record, outside every release carrier. No unadmitted binary prints anything an operator uses to select. The certified command register has no `gov trust fc-procedure` (excluded, EX-24). |
| **R-FCD-3** | The operator's prior knowledge of the two source identities is TA-5′ (`01`). Its failure is represented in the stated root by the atoms `desig1` and `desig2` (§9). |

## 6. The operator procedure (FC-1′…FC-3′): platform tools only, before any evaluator runs

The procedure uses the platform hash tool only (TA-1b: `sha256sum`, `shasum -a 256`, `certutil -hashfile`). There is no
signature-verification step and no single-source route: those modes are excluded (EX-04, EX-05, EX-17, EX-18) and refused
when offered (`PROFILE_MODE_EXCLUDED`).

| ID | Step | Stop code |
|---|---|---|
| **FC-1′** | Read the trust code, the state code and the procedure digest from **both** sources named at onboarding. Continue only if all three are identical across both. | `FIRST_CONTACT_SOURCES_BELOW_QUORUM` / `FIRST_CONTACT_DISAGREEMENT` |
| **FC-2′** | Fetch the FCA payload from any carrier. Its SHA-256 must equal the trust code's hash part. The machine's target must be in its `certified_targets`. Its `procedure_digest` must equal the digest read. | `FIRST_CONTACT_AUTHORITY_MISMATCH` / `TARGET_NOT_CERTIFIED` / `FIRST_CONTACT_PROCEDURE_MISMATCH` |
| **FC-3′** | Fetch `gov-admit` from any carrier. Its SHA-256 must equal `admitters[target]` of that FCA. | `ADMITTER_DIGEST_MISMATCH` |

**What no code can enforce.** A substituted evaluator ignores FC-4′…FC-10. The defence against evaluator substitution is that
FC-1′…FC-3′ select the evaluator through the trust code both sources show, which names a root-threshold statement. An operator
who reads one source and types its values for both (atom `op1src`), or who is directed to look-alike sources (`desig1`,
`desig2`), is inside the stated root (§9).

## 7. Admitter rules (FC-4′…FC-10): compiled into `gov-admit`, never read from what they select

| ID | Rule | Refusal |
|---|---|---|
| **FC-4′** | **Compiled quorum.** Two identical trust codes and two identical state codes are required (OP-13 (b)). No statement can lower or raise the number. | `FIRST_CONTACT_SOURCES_BELOW_QUORUM` / `FIRST_CONTACT_DISAGREEMENT` |
| **FC-5′** | **Authority.** The FCA is the statement whose digest the trust code names. It MUST verify at the `first-contact-authority` threshold and the root threshold of the root version it names, within the chain from the compiled lineage, and conform to CP-1. | `FIRST_CONTACT_AUTHORITY_NOT_HELD` / `FIRST_CONTACT_AUTHORITY_UNVERIFIED` / `PROFILE_NONCONFORMANT:fca` |
| **FC-6** | **Lineage.** Root v1 is the root whose digest is the compiled lineage. Bundle order never changes the result. | `ROOT_CHAIN_INVALID` |
| **FC-7′** | **Compiled lineage in every admitter build.** The FCA's `lineage` and the trust code's lineage prefix equal the compiled lineage. | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` |
| **FC-8′** | **Evaluator and target.** The target is in the FCA's `certified_targets`. The FCA lists this admitter's own digest for it. The admitter is not revoked in the selected state or in held state. The candidate's digest is not the admitter's. | `TARGET_NOT_CERTIFIED` / `ADMITTER_NOT_LISTED` / `ADMITTER_REVOKED` / `ADMITTER_REVOKED_IN_HELD_STATE` / `SELF_EVALUATION_REFUSED` |
| **FC-9** | **State age (compiled, 24 hours).** The selected Trust State's `issued_at` is no later than the admission clock plus the compiled skew and no more than 24 hours before it (OP-7 (a)). No Trust Policy field changes the ceiling. | `STATEMENT_ISSUED_IN_FUTURE` / `FIRST_CONTACT_STATE_TOO_OLD` |
| **FC-10** | **State binding.** The Trust State the state code names verifies at the trust-state threshold under a root version in the chain, its state code equals the one typed, and it references the FCA of the trust code. | `STATE_NOT_HELD` / `TRUST_STATE_UNVERIFIED` / `FIRST_CONTACT_STATE_CODE_MISMATCH` / `FIRST_CONTACT_AUTHORITY_MISMATCH` |

After FC-4′…FC-10, admission applies `31` AP-R1…AP-R6 (re-admission floors) and `25` AP-4…AP-8. These rules apply to every
first admission and re-admission: first install, CI image build, a legacy consumer's first RoT-1 binary (`11` Phase 4), and
every re-admission (`31` R-ADM-8″).

## 8. Currency (BC6-2)

| Path | Selector of state | Bound |
|---|---|---|
| Workstation first install | codes read now from both sources | FC-9: state ≤ 24 hours |
| CI image build | codes read from both sources by the image build | FC-9 at admission; image records and anchors ≤ 7 days (`24` §4.3, `31` R-ADM-7″) |
| Air-gapped machine | media carrying the immutable mirror's material | FC-9: the state on the media ≤ 24 hours at admission; otherwise refused (owner trade-off OT-1, `35` §6) |
| Re-admission (record expired; OP-15 (a) incident; new lineage) | codes read now from both sources | FC-9, and never below held state, anchors, revocations, security minimum or accepted-TBM high-water (`31` AP-R1…AP-R6) |

Stored values, replayed pages and designated stale pages older than 24 hours are refused (`FIRST_CONTACT_STATE_TOO_OLD`). On a
machine with a store, a value within 24 hours but below the held state is refused (`READMISSION_STATE_BELOW_HELD`).

Computed consequence (goal: a binary revoked in the newest Trust State is admitted; victims FA, a re-admission over a store that
holds the revocation, and one that does not):

<!-- CS7:BEGIN CP-REVOKED -->
| Victim | Minimal sets: a binary revoked in the newest state is admitted (CP-1) |
|---|---|
| FA | {win}; {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {stored_old, clockback} |
| RA_held | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {win, store_admin}; {stored_old, clockback, store_admin} |
| RA_unheld | {win}; {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {stored_old, clockback} |
<!-- CS7:END CP-REVOKED -->

Atoms: `win` is a revocation issued after the state both sources show, within the 24-hour ceiling (residual **CUR-R1**).
`stored_old` is a code stored or replayed from earlier than the ceiling. `clockback` is a clock set back on a machine without a
store (A13; residual **RS-2**). `store_admin` is an administrator-level attacker who rewrites the protected admission store
(outside TA-9).

## 9. The first-contact root (computed)

The **first-contact root** of CP-1 is the family of minimal capability sets with which an attacker holding **no key** makes a
machine with no prior trust admit a malicious first TCB. Atoms: `src1`, `src2` (the content of source 1 and source 2);
`desig1`, `desig2` (the operator directed to a look-alike of source 1 or 2); `op1src` (the operator reads one source and types
its values for both). The calculator also offers `fcpub` (the trust-state publication process) and `carrier` (a download host
or the unadmitted candidate presenting source names or steps); neither appears in any minimal set (INV7-NO-COMPOSER,
INV7-NO-CARRIER).

<!-- CS7:BEGIN CP-FC-ROOT -->
| Victim | First-contact root: minimal sets that admit a malicious first TCB with no key | Other minimal sets |
|---|---|---|
| FA (first admission) | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src} | 49 |
<!-- CS7:END CP-FC-ROOT -->

Key theft at first contact still needs the stated thresholds (no set holds one key of a threshold purpose):

<!-- CS7:BEGIN CP-FC-KEY-THEFT -->
| Victim | Key-theft minimal sets for malicious bytes at first admission |
|---|---|
| FA | {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
<!-- CS7:END CP-FC-KEY-THEFT -->

**Executed equality.** FA7 S3 attacks every subset of the first-contact capabilities with the reference procedure, the custodian
publication rule and the reference admitter (real Ed25519 through OpenSSL; `sha256sum`). The minimal accepting subsets equal the
calculator's root sets, and neither `fcpub` nor `carrier` is in any of them.

## 10. The stricter reading, value by value (HO-0019 §2b note 1)

| First-contact selector | Established by | Composed or selected solely by the trust-state publisher, an unadmitted binary or a package submitter? | Mechanism | Evidence |
|---|---|---|---|---|
| lineage | root ceremony; compiled into every admitter build; the FCA at root threshold | no | FC-5′, FC-6, FC-7′, R-FCS-1 | FA7 S2 D `both_pages_attacker_lineage_genuine_admitter`; S2 P `authority_of_attacker_lineage` |
| evaluator (admitter digest) and certified targets | the FCA at root threshold after the admitter's registration, reproduction and verification | no | R-FCA-1, R-FCA-2, FC-8′ | FA7 S2 P `authority_signed_by_two_trust_state_keys`, `authority_signed_by_one_root_key`; S4 R16 |
| state | a Trust State at 2 of 3 trust-state keys naming the FCA, published only after each source custodian's first-hand verification; at most 24 hours old; never below held state | no: the publisher alone signs with at most its own key share and cannot make a custodian publish | FC-9, FC-10, R-FCS-2, `31` AP-R1 | FA7 S2 P `genuine_authority_state_signed_by_one_trust_state_key`, `two_trust_state_keys_descendant_drops_revocation`; CUR7 |
| source identities and procedure | root ceremony record; onboarding outside release carriers; digest in the FCA | no | R-FCD-1…R-FCD-3, FC-2′ | FA7 S2 D; `command_register_has_no_fc_procedure` |
| platform package, submitter | none: excluded | not applicable | EX-04, EX-05 (`PROFILE_MODE_EXCLUDED`) | FA7 S2 X |

**Mapping to review r6's options F1-a…F1-c** (owner requirement "First-contact composer/signer" applies; nothing is decided
here beyond it). Lineage and evaluator follow F1-b (a root-threshold record carried and checked by the sources). The state
follows F1-a for its code (each source custodian derives it from a Trust State it verified) on top of the 2-of-3 trust-state
threshold. F1-c (the composer as a root atom) is excluded (EX-23). The state portion is therefore established first-hand
within the owner's selections, and no F1 trade-off remains open. The currency trade-off that remains is OT-1 (`35` §6).

## 11. Machine classes

| Machine | Sources used | Remark |
|---|---|---|
| First install (M1) | both sources, now | `31` §7 |
| CI runner image | both sources at image build; image admission within 24 hours of the state; record and anchor ≤ 7 days | TA-9; the job runs as another user (GB-6) |
| Air-gapped machine | media carrying the mirror's material, state ≤ 24 hours | OT-1 |
| Legacy consumer, first RoT-1 binary | both sources, now | `11` Phase 4 |
| Re-admission | both sources, now; store floors applied | `31` R-ADM-8″, AP-R1…AP-R6 |

## 12. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| **FC-R1′** | The first-contact root admits a malicious first TCB with no key | exactly the sets of the CP-FC-ROOT block; `gov-admit` names both sources, the FCA sequence and the state's `issued_at` and age | FA7 S3; RT-184 |
| FC-R2′ (TA-5′/A10) | An operator who types one source's values for both | inside FC-R1′ (`op1src`) | FA7 S2 D; RT-184 |
| FC-R3′ (TA-5′) | An operator directed to look-alike sources | inside FC-R1′ (`desig1`, `desig2`); onboarding outside release carriers | FA7 S2 D |
| FC-R5 | Key theft at first contact | CP-FC-KEY-THEFT block | FA7 S2 P; BA12r7 |
| **CUR-R1** | A revocation issued within the 24 hours before admission, not yet in the state both sources show | `{win}`; 24 hours; any machine whose store holds the newer state refuses | CUR7 W; RT-191 |
| RS-2 | A machine without a store, stored codes and a clock set back | `{stored_old, clockback}`; a machine with a store fails closed (`24` R-CLK-1) | CUR7 A08; ADM7 CLK; RT-191 |

## 13. Evidence

- `evidence/r7/FA7-first-contact-authority.{py,json}` (executed): S1 honest admission and procedure refusals; S2 P the publication
  process composes (every case refused by the custodian rule and by the genuine admitter; the revision-6 control admits); S2 D
  designation (attacker lineage refused; substituted evaluator only inside the stated root); S2 X every unselected answer
  refused, CP-1 accepted; S3 executed minima equal CS7; S4 shared vectors R1–R16; S5 restrictors; S7 revision-7 rule mutants.
- `evidence/r7/CUR7-first-contact-currency.{py,json}` (executed): replayed, stored, designated and CI-image values; re-admission
  over a store; accepted-TBM high-water at re-admission and at use; the CUR-R1 window exactly.
- `evidence/r7/CS7-derivation-calculator.{py,json}` (computed): the blocks above; INV7-FC, INV7-NO-COMPOSER, INV7-NO-CARRIER,
  INV7-AGE, INV7-STORE.

Counts are in `22` §1.
