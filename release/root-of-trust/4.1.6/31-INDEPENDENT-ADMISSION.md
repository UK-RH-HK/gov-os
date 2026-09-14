# Output 31 — Independent admission of the TCB on every machine (CP-1)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** concretises this file to CP-1 (`35`) and closes, for admission:
> - RV6-H1 / RV6-H2 (BC6-1, BC6-2): first contact follows `32` (the First-Contact Authority record at root threshold, both
>   sources, the compiled 24-hour state age); re-admission applies the stores (AP-R1…AP-R6);
> - RV6-M6 (CR6-C-10): two stores are specified, and first admission is decided only by the protected admission store
>   (R-STORE-1, R-STORE-2, R-ADM-8″);
> - RV6-L5 (CR6-B-02, CR6-C-12): the accepted-TBM high-water applies at re-admission (AP-R6) and at use (GB-7);
> - RV6-L9: full 64-hex lineage store names; records bound to the lineage; a store without a marker is a first admission;
> - OP-12 (a), OP-14 (b), OP-15 (a) (OWNER-DESIGN-REQUIREMENTS-0001): compiled admitter only; every record expires; a revoked
>   binary runs C0-R only. Script and helper-machine admission are excluded (EX-02, EX-03).
> Revisions 5–6 established one predicate with two executors, installation from the measured buffer, serialised admissions and
> records honoured only inside the store; those are kept. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Root cause accepted

**Revision 5.** The inductive chain "binary N accepts binary N+1" had a base case that was a different, weaker predicate. The
fix was one predicate evaluated by code other than the candidate.

**Revision 6.** Review r5 found that the base case's selectors were chosen by the values they governed (RV5-H1).

**Revision 7.** Review r6 found that the base case's selectors were composed, designated or submitted by parties outside the
stated root, had no bound on currency, and that re-admission ignored the store (RV6-H1, RV6-H2). It also found that "first
admission" was decided by an unsigned file the governed account can write (RV6-M6).

## 2. Invariant

Every TCB acceptance on a machine is the same predicate (`25` §5, admission-predicate/1): for the first binary, a CI image's
binary, a legacy consumer's first RoT-1 binary, a re-admitted binary and every later binary. It is evaluated by code other than
the candidate, over bytes that code measured. Its selector of state is either a currency proof of at most 24 hours naming the
selected state (running mode) or the state code both sources publish, at most 24 hours old (bootstrap mode). At first contact
the lineage and evaluator come from the First-Contact Authority record at root threshold (`32`). No admission selects anything
below the monotonic state a store already holds, and no file the governed account can write decides whether an admission is
the first.

## 3. One predicate, two executors

| Executor | When | Selector of state (AP-3) | Candidate executed? |
|---|---|---|---|
| `gov trust verify-artifact` (the admitted binary N) | every later binary | inclusion anchor plus a currency proof of at most 24 hours naming the selected Trust State (`24` §4.4: P1 two-source state codes, P2 in-gate state codes) | never |
| **`gov-admit`** (compiled independent executor, OP-12 (a)) | first admission, re-admission, CI image build, legacy consumer (Phase 4), build from source | the Trust State whose state code both sources show, at most 24 hours old, naming the FCA whose trust code both sources show (`32` FC-4′…FC-10), never below the stores' floors (AP-R1…AP-R6) | never |

Both implement `admission-predicate/1` from one normative specification and **one shared set of conformance vectors**:
`evidence/r7/FA7-first-contact-authority.py` S4 R1–R16 (bootstrap mode) and the scenarios of `evidence/r6/P4r6-conformance-oracle.py`
retained for running mode (R-ADM-14). A difference in result on a shared vector is a release-blocking defect of both.

## 4. `gov-admit` (R-ADM)

| ID | Rule |
|---|---|
| **R-ADM-1″** | `gov-admit` is a separate compiled program implementing only statement verification, admission-predicate/1, installation and record writing. It is a registered, reproduced artefact (the registration's `admitter` entry, `30` §5), verified by two records, and its digest per certified target is listed in the First-Contact Authority record (`32` R-FCA-1). It is never `gov` validating itself. Auditable-script and helper-machine admitters are excluded (EX-02, EX-03). |
| **R-ADM-2″** | **Evaluator selection.** Before running `gov-admit`, the operator performs `32` FC-1′…FC-3′ with platform tools: trust code, state code and procedure digest identical across both sources; the FCA payload hashes to the trust code; the target is certified; the admitter's SHA-256 equals the FCA's entry. A failure stops the procedure (`FIRST_CONTACT_SOURCES_BELOW_QUORUM`, `FIRST_CONTACT_DISAGREEMENT`, `FIRST_CONTACT_AUTHORITY_MISMATCH`, `TARGET_NOT_CERTIFIED`, `FIRST_CONTACT_PROCEDURE_MISMATCH`, `ADMITTER_DIGEST_MISMATCH`). |
| **R-ADM-3″** | **State, lineage, quorum and age.** The operator enters both sources' trust codes and state codes. `gov-admit` enforces `32` FC-4′…FC-10 with its compiled lineage and compiled constants. No Trust Policy field, clock value beyond FC-9's age check, repository file or environment variable is an input. |
| R-ADM-4 | `gov-admit` reads the candidate once into a buffer and **never executes it**. No value the candidate prints is an input. |
| R-ADM-5 | `gov-admit` refuses to evaluate a candidate whose digest equals its own (`SELF_EVALUATION_REFUSED`). |
| R-ADM-6 | **Installation from the measured buffer:** temporary file in the destination directory, `fsync`, atomic rename, re-read and compare. Installing by re-reading the source path is forbidden. |
| **R-ADM-7″** | **Admission record** v3 `{binary_digest, target, release_id, lineage, trust_code, state_code, admitted_at, admitter_digest, admitter_kind: compiled-gov-admit, path_class, valid_until}` (`schemas/admission-record.schema.json`). It is written **only** in the protected admission store for the lineage (`24` §8), as `admissions/<binary digest>.json`, atomically, one file per admitted binary; earlier records are kept. `valid_until` is `admitted_at` plus 90 days (`workstation`) or 7 days (`ci-image`) and is never null (OP-14 (b)). The same transaction raises the store's floors to the selected state's values and `clock_high_water` to `admitted_at`; no floor is lowered. |
| **R-ADM-8″** | **First admission and re-admission.** *First admission* is the case where the protected admission store for the lineage has no `admission-store.json` marker. Then, under the lock of R-ADM-13, `gov-admit` creates the marker and moves the account verifier trust store for the lineage aside (never read again; AD-2′). *Re-admission* is every other run (for example after `ADMISSION_RECORD_EXPIRED`, an OP-15 (a) incident, or a new admitter). It keeps both stores, applies their floors (AP-R1…AP-R6) and adds the new record. |
| R-ADM-9 | The admission record is not an anchor. The admitted binary's first trust operation establishes its own anchor (`24` §3.2). |
| R-ADM-10 | `gov-admit` shows the selected state's `issued_at` and age, both sources used, the FCA sequence, the OP-5 age warning when due, and never the word `current`. |
| R-ADM-11 | **Build from source is not a separate trust path.** A self-built binary is measured by `gov-admit`; it is a production binary only if its digest equals a registered, quorum-reproduced, published digest. |
| R-ADM-12 | `gov-admit` implements the Fact Threshold Check and the CP-1 shape checks on every root version (`05` §3), and the append-only and equivocation rules of registrations, exactly as `gov`. |
| **R-ADM-13** | **Serialised admissions.** `gov-admit` holds an exclusive lock on the protected store's parent from the first-admission determination until the record and floors are written. |
| **R-ADM-14** | **Shared vectors.** The shared conformance vectors contain, for both executors, at least FA7 S4 R1–R16: registered final revoked; registered candidate revoked; attestation for another candidate with the same source; binary below `min_binary_version`; attestation for another kernel; two signatures over one verification execution; reproductions from one supplier class; a relabelled supplier; a relabelled toolchain lineage; a registered digest that differs; a release below the computed security minimum; the excluded shapes (witness purpose, mode B, registration on root keys, release-final threshold 1, shared candidate key); an authority signed by trust-state keys. |

### 4.1 Re-admission applies the stores (AP-R; RV6-H2, RV6-L5, OP-14 (b))

The floors are read from both stores and merged as maxima and unions (`24` §8); a floor planted in the account store can only
refuse.

| ID | Rule | Refusal |
|---|---|---|
| **AP-R1** | The selected state's sequence is at least the held sequence; at an equal sequence its digest equals the held digest. | `READMISSION_STATE_BELOW_HELD` / `TRUST_STATE_EQUIVOCATION` |
| **AP-R2** | The root version and the Trust Policy version the state references are at least the held versions. | `READMISSION_ROOT_BELOW_HELD` / `READMISSION_POLICY_BELOW_HELD` |
| **AP-R3** | The FCA's `fca_sequence` is at least the held sequence. | `FIRST_CONTACT_AUTHORITY_BELOW_HELD` |
| **AP-R4** | Held negatives apply to the candidate binary, its registration, the registered final and candidate, and the admitter. | `BINARY_REVOKED_IN_HELD_STATE` / `ADMITTER_REVOKED_IN_HELD_STATE` |
| **AP-R5** | The computed security minimum is at least the held minimum. | `RELEASE_BELOW_SECURITY_MINIMUM` |
| **AP-R6** | The candidate's TBM `(root version, policy version, state sequence)` is at least the accepted-TBM high-water. | `BINARY_T0_ROLLBACK` |

### 4.2 Two stores (R-STORE)

| ID | Rule |
|---|---|
| **R-STORE-1** | Two stores exist per lineage (`24` §8): the **protected admission store** (per-platform, root- or administrator-owned, written only by `gov-admit`) and the **account verifier trust store** (written by the admitted `gov`). Both are named by the full 64-hex lineage id. |
| **R-STORE-2** | The first-admission determination, the move-aside and the honoured admission records read **only** the protected admission store. No file the governed account can write decides first admission or authorises anything; account-store floors are restrictors only. A record of another lineage is never honoured for this lineage. |

## 5. Genuine-binary rule (GB) — what a RoT-1 `gov` does at process start

| ID | Rule |
|---|---|
| **GB-1″** | A RoT-1 binary measures its own executable once at start. C0-R (`version`, `doctor`, `status`, `kernel trust` report, `trust show`) always runs. Everything else needs an honoured admission record: one held in the protected admission store for the compiled lineage, naming its digest, with `admitter_kind` `compiled-gov-admit` and an `admitter_digest` listed in the FCA the effective Trust State references (or a later FCA the store holds). A record beside the binary, in the account store, in a moved-aside store, or naming an unlisted admitter is ignored (`BINARY_NOT_ADMITTED`, `RECORD_ADMITTER_NOT_LISTED`, `TRUST_ROOT_LINEAGE_MISMATCH`). |
| **GB-2′** | A clock below the recorded high-water leaves C0-R (`24` R-CLK-1, `TRUST_CLOCK_BELOW_HIGH_WATER`). A record whose `valid_until` has passed leaves C0-R (`ADMISSION_RECORD_EXPIRED`); the remedy is re-admission. |
| **GB-3′** | When held negatives name its own digest or release, the binary runs C0-R only (`BINARY_REVOKED_SELF`; OP-15 (a)): no governed mutation, installation, update, policy enforcement relied on for production work, or release or certification operation. Recovery uses a newly admitted eligible binary. |
| **GB-4′** | C3 and every anchoring ceremony (`confirm-root`, `confirm-state`, in-gate state codes, trust-gate confirmations) additionally require that the executable, the admission record and every ancestor directory satisfy the TCB-location predicate (`TCB_WRITABLE_BY_GOVERNED_ACCOUNT` otherwise). A user-writable installation never anchors, and account-location pins are not honoured for anchoring (§7.1). |
| GB-5 | An account-location artefact is writable by A3; A3 can equally replace a user-writable binary. The rule binds the transport and repository adversaries, not A3 (RS-3 class). |
| **GB-6** | **Effective uid 0.** The TCB-location and pin-integrity predicates treat every path as writable by an effective uid of 0: pins are ignored and C3 refuses. Runner-image documentation (WP-21) states that jobs running as root violate TA-9. |
| **GB-7** | **R-ART-2 at use** (`09`; CR6-C-12). A running binary whose TBM is below the accepted-TBM high-water runs C0-R only (`BINARY_T0_ROLLBACK`) until a root-signed `accepted_tbm_reset`. A rollback to an admitted lower-TBM binary keeps its record but gains no trusted operation. |

Order at process start (reference `gov_run`): C0-R → record held and listed → lineage → R-CLK-1 → expiry → own revocation →
GB-7 → anchor and anchor validity (`24` §4.3) → C1–C2 → C3 with the TCB-location predicate and currency.

## 6. Ceremony order (R-CER)

| ID | Rule |
|---|---|
| R-CER-1 | No TA-5′ ceremony is performed by a binary that has not been admitted on this machine (GB-1″). |
| **R-CER-2′** | The trust code names an FCA under the compiled lineage, so lineage selection is part of admission. After the first admission of a store, the operator confirms the lineage fingerprint once for that store (OP-6 (a)); a new lineage needs re-admission and re-confirmation. Trust on first use is not available. |
| R-CER-3 | `confirm-root` and `confirm-state` on an admitted binary follow `24` §3; in-gate state codes follow `27` §3.1. |
| R-CER-4 | Every surface that shows a ceremony result shows the admission record it relied on. |

## 7. Machine classes (HO-0001 §3.2)

| Machine | TCB | Trust state (`24`) | Before a currency proof |
|---|---|---|---|
| First install (M1) | `gov-admit` after FC-1′…FC-10; install from buffer; record in the protected store | the admitted binary anchors with both sources' state codes (protected installation) | C0-R until admitted; then C0 until anchored |
| Clean CI runner (M2) | image build runs FC-1′…FC-10 within 24 hours of the state; root-owned protected store; record and pin ≤ 7 days; jobs run as another user (GB-6) | CI pin naming the state (`24` §5.2) | per pin; C0 after expiry |
| Restored from backup (M3) | admitted; GB rules apply; re-admission keeps both stores | `24` §5.3 | as `24` |
| Old epoch (M4), no epoch (M5), two machines (M6), long offline (M7) | admitted, or first admission if none | `24` §5.4–§5.7 | as `24` |
| Legacy consumer, first RoT-1 binary (`11` Phase 4) | `gov-admit`; a legacy 4.1.5 binary never verifies a RoT-1 binary | first anchor on the admitted binary | `LEGACY` until `update --apply` by the admitted binary from a protected installation |
| Build from source | R-ADM-11 | — | — |

### 7.1 User-writable installation

| Provisioning | Classes reachable on a user-writable installation |
|---|---|
| no administrator-provisioned system pin | C0 (anchoring ceremonies refused by GB-4′) |
| an administrator-provisioned system pin within validity | C0–C2 (C3 refused by GB-4′) |
| a protected installation instead | `24` §4.3 |

Evidence: `evidence/r6/UW6-user-writable-install.json`, whose OP-7 (a) and system-pin rows equal these classes (the other rows of
that retained instrument model excluded answers and are history). A legacy consumer's Phase 4 `update --apply` from a
user-writable installation is refused. Test: RT-138.

## 8. Admitter distribution

`32` states the first-contact root, the procedure and the admitter rules. The distribution channel of the admitter is a carrier:
FC-3′ selects the admitter through the FCA. A platform or distribution package is only a carrier (EX-05);
platform signing is excluded as a root.

## 9. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| **AD-1″** | The first-contact root | exactly the sets of `32` §9 (FC-R1′) | FA7 S3; RT-184 |
| CUR-R1 | A revocation within the 24 hours before admission | `32` §8 | CUR7 W; RT-191 |
| TB-1′ | A malicious binary run directly, outside admission, ignores every rule | GB rules bind genuine binaries, including revoked ones; the procedure never runs a candidate | FA7 S1 |
| **AD-2′** | Same-account code executed before the first admission | the account store is moved aside at first admission; the protected store is outside its reach (R-STORE-2); afterwards RS-3/TG-2 | ADM7 A07 |
| VR-B1′ | A same-account replacement of a user-writable binary is A3 | such an installation reaches only §7.1 | UW6 |
| RS-2 | A machine without any store, stored codes and a clock set back | `32` §12 | CUR7 A08 |

## 10. Evidence

| Evidence | Kind | Result |
|---|---|---|
| `evidence/r7/gov_admit_reference_r7.py`, `FA7-first-contact-authority.{py,json}` | executed (real Ed25519 through OpenSSL; `sha256sum`) | S1 honest admission and procedure refusals; S2 first contact under CP-1 and every excluded answer; S3 executed first-contact minima equal CS7; S4 shared vectors R1–R16; S5 restrictors and shapes; S7 revision-7 rule mutants detected |
| `evidence/r7/CUR7-first-contact-currency.{py,json}` | executed | replayed, stored, designated and CI values refused by age; re-admission applies the store (AP-R1…AP-R5); AP-R6 and GB-7; CUR-R1 exactly |
| `evidence/r7/ADM7-admission-stores.{py,json}` | executed (reference executor) | A07 planted account record does not suppress the move-aside; A08 crash between install and record; A09 floors never lowered; A11 eight concurrent first admissions; A15 records outside the protected store; EX02/EX03; L9; X14 expiry; X15 C0-R; X7 decision rule; CLK R-CLK-1 |
| `evidence/r6/UW6-user-writable-install.{py,json}` | retained (revision 6) | the CP-1 rows of §7.1 |

Counts are in `22` §1.
