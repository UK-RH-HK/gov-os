# Output 31 — Independent admission of the TCB on every machine (BC4-2, BC5-1)

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 6** amends this file for review r5:
> - first contact follows `32` (BC5-1): R-ADM-2 and R-ADM-3 are restated; the first-contact code selects lineage, state and
>   evaluator list; the quorum is compiled; the evaluator is bound;
> - first admission is defined and re-admission keeps the verifier trust store (RV5-M3, CR5-B-03, RV5-C-L3): R-ADM-7′,
>   R-ADM-8′;
> - admissions are serialised (RV5-C-A11): R-ADM-13;
> - records are honoured only inside the store (CR5-B-07): GB-1′;
> - an effective uid of 0 is writable (CR5-B-12): GB-6;
> - the user-writable installation consequence is restated (RV5-M8 option (a)): GB-4′ and §7;
> - the shared vectors are extended (RV5-M9): R-ADM-14;
> - AD-1 is restated as the first-contact root (§9).
>
> New in revision 5; it closed blocking class **BC4-2** (review r4 RV4-H2). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Root cause accepted

**Revision 5.** The inductive chain "binary N accepts binary N+1" had a base case that was a different, weaker predicate. The
fix was one predicate evaluated by code other than the candidate.

**Revision 6.** Review r5 found that the base case's *selectors* were still chosen by the values they governed. One channel
page selected the lineage, the Trust Policy that set the channel quorum, and, through a single-channel digest comparison, the
evaluator (RV5-H1). Operationally, re-admission discarded the monotonic store that made later decisions safe (RV5-M3).

## 2. Invariant

Every TCB acceptance on a machine is the same predicate (`25` §5, admission-predicate/1). That covers the first binary, a CI
runner image's binary, a legacy consumer's first RoT-1 binary, a re-admitted binary and every later binary. The predicate is
evaluated by code other than the candidate, over bytes that code measured. Its selector of state has currency established
now or within a window that names that state. At first contact, every selector is the first-contact root of `32` or is
authenticated independently of the values it governs. The bytes that later run as `gov` are the bytes accepted. No
ceremony whose purpose is TA-5 runs before that acceptance, and no admission discards the monotonic state of an earlier one.

## 3. One predicate, two executors

| Executor | When | Selector of state (AP-3) | Candidate executed? |
|---|---|---|---|
| `gov trust verify-artifact` (the admitted binary N) | every later binary | inclusion anchor plus a currency proof naming the selected TSS (P1 naming it, P2 typed fingerprint, P3 witnesses) | never |
| **`gov-admit`** (independent executor) | first admission (§4 R-ADM-8′), re-admission, CI image build, legacy consumer (Phase 4), build from source | the TSS whose epoch equals the first-contact manifest bound by the code typed from the OP-13 sources (`32`) | never |

Both implement `admission-predicate/1` from one normative specification and **one shared set of conformance vectors**. Those
are the vectors of `evidence/r6/FA6-first-admission.py` (bootstrap mode) and the scenarios of
`evidence/r6/P4r6-conformance-oracle.py` (running mode), which share rows R1–R5 (R-ADM-14). A difference in result on a
shared vector is a release-blocking defect of both.

## 4. `gov-admit` (R-ADM)

| ID | Rule |
|---|---|
| R-ADM-1 | `gov-admit` is a separate program implementing only statement verification, admission-predicate/1 and installation. Its form and distribution are OP-12. It is itself a registered, quorum-reproduced artefact (the registration's `admitter` entry, `30` §5), and its digest per target is listed in the Trust Policy's `bootstrap.admitter_digests` and in every first-contact manifest. |
| **R-ADM-2′** | **Evaluator selection** (revision 6). Before running `gov-admit`, the operator performs `32` FC-1…FC-3 with platform tools: the code agrees across the OP-13 sources; the manifest hashes to it; the admitter's SHA-256 equals the manifest's entry; under OP-13 (c) the platform signature verifies. A failure stops the procedure (`FIRST_CONTACT_DISAGREEMENT`, `FIRST_CONTACT_MANIFEST_MISMATCH`, `ADMITTER_DIGEST_MISMATCH`, `PLATFORM_SIGNATURE_INVALID`). |
| **R-ADM-3′** | **State, lineage and quorum** (revision 6). The operator types the first-contact code from each OP-13 source. `gov-admit` enforces `32` FC-4…FC-8: the compiled quorum; the manifest bound by the code as the only selector of lineage, state epoch and admitter set; lineage from the typed value; compiled lineage under OP-13 (c) and (d); evaluator binding. No compiled value other than the owner's OP-13 answer and lineage (under (c)/(d)), and no clock, repository file or environment variable, is an input. |
| R-ADM-4 | `gov-admit` reads the candidate once into a buffer and **never executes it**. No value the candidate prints is an input. |
| R-ADM-5 | `gov-admit` refuses to evaluate a candidate whose digest equals its own (`SELF_EVALUATION_REFUSED`). |
| R-ADM-6 | **Installation from the measured buffer:** temporary file in the destination directory, `fsync`, atomic rename, re-read and compare. Installing by re-reading the source path is forbidden. |
| **R-ADM-7′** | **Admission record** `{binary_digest, target, release_id, lineage, first_contact_code, admitted_at, admitter_digest, valid_until, location_protected}` (`schemas/admission-record.schema.json` v2). It is written **only** inside the verifier trust store for the lineage, as `vts-<lineage prefix>/admissions/<binary digest>.json`, atomically, **one file per admitted binary**. Earlier records are kept, so a rollback to an admitted binary keeps its record. `valid_until` is mandatory for CI image records (≤ `pin_max_validity_days`) and, under OP-14 (b), for every record. |
| **R-ADM-8′** | **First admission and re-admission** (revision 6; CR5-B-03). *First admission* is the case where no verifier trust store exists for the lineage, or the store holds no admission record ever written. Only at first admission is a pre-existing store moved aside and never read (AD-2). *Re-admission* is every other `gov-admit` run, for example after `ADMISSION_RECORD_EXPIRED` or under OP-15 (a). It keeps the store: anchors, clock and accepted-TBM high-waters, per-project records, earlier admission records. It adds the new record. |
| R-ADM-9 | The admission record is not an anchor. The admitted binary's first trust operation establishes its own anchor (`gov trust confirm-state`, or a protected pin; `24` §3). |
| R-ADM-10 | `gov-admit` shows the selected state's `issued_at` and age, the first-contact sources used, and never the word `current`. |
| R-ADM-11 | **Build from source is not a separate trust path.** A self-built binary is measured by `gov-admit`; it is a production binary only if its digest equals a registered, quorum-reproduced, published digest. |
| R-ADM-12 | `gov-admit` implements the Fact Threshold Check (including KS-14) on every root version and the append-only and equivocation rules of registrations, exactly as `gov`. |
| **R-ADM-13** | **Serialised admissions** (revision 6; RV5-C-A11). `gov-admit` holds an exclusive lock on the record directory from the first-admission determination until the record is written, so concurrent admissions never move aside a store that already holds a record. |
| **R-ADM-14** | **Shared vectors** (revision 6; RV5-M9). The shared conformance vectors contain, for both executors, at least: registered final revoked; registered candidate revoked; registration revoked; an ACCEPTED attestation for another candidate with the same source; an ACCEPTED attestation for the registered candidate with another kernel tree; binary version below `min_binary_version`, a TBM without a version while the floor is set (fail closed), and a binary at the floor (control). |

## 5. Genuine-binary rule (GB) — what a RoT-1 `gov` does at process start

| ID | Rule |
|---|---|
| **GB-1′** | A RoT-1 binary measures its own executable once at start. It honours an admission record only when the record is held in the protected verifier trust store location that `gov-admit` writes (R-ADM-7′). A record beside the binary, supplied by a package, found by walking a directory, or in a moved-aside store is ignored (CR5-B-07). Without an honoured record naming its digest, the binary runs **C0 only** and refuses C1–C3 and every TA-5 ceremony with `BINARY_NOT_ADMITTED`. |
| GB-2 | A record with `valid_until` in the past refuses above C0 (`ADMISSION_RECORD_EXPIRED`). |
| GB-3 | When the held negative set names its own digest or release, the binary refuses per OP-15 (`BINARY_REVOKED_SELF`). |
| **GB-4′** | C3 and every anchoring ceremony (`confirm-root`, `confirm-state`, in-gate fingerprints, trust-gate confirmations) additionally require that the executable, the admission record and every ancestor directory satisfy the TCB-location predicate: `TCB_WRITABLE_BY_GOVERNED_ACCOUNT` otherwise. **Consequence (revision 6; RV5-M8 option (a)).** A user-writable installation can never anchor, and account-location pins fail the integrity predicate (`24` §3.5). The operation classes it can reach are therefore those of §7.1. Governed use (C1–C2) on a workstation needs one of: an administrator-protected installation, an administrator-provisioned system pin, OP-7 (c) witnesses, or OP-7 (d). C3 always needs a protected installation. |
| GB-5 | An account-location record (C1–C2) is writable by A3; A3 can equally replace the binary. The rule binds the transport and repository adversaries, not A3 (RS-3 class). |
| **GB-6** | **Effective uid 0** (revision 6; CR5-B-12). The TCB-location and pin-integrity predicates treat every path as writable by an effective uid of 0: pins are ignored and C3 refuses (`TCB_WRITABLE_BY_GOVERNED_ACCOUNT`). Runner-image documentation (WP-21) states that jobs running as root violate TA-9. |

## 6. Ceremony order (R-CER)

| ID | Rule |
|---|---|
| R-CER-1 | No TA-5 ceremony is performed by a binary that has not been admitted on this machine (GB-1′ enforces it). |
| R-CER-2 | The first-contact code commits to the lineage id, so lineage confirmation is part of admission. Trust on first use is not available for production. |
| R-CER-3 | `confirm-root` and `confirm-state` on an admitted binary follow `24` §3; the in-gate fingerprint follows `27` §3.1. |
| R-CER-4 | Every surface that shows a ceremony result shows the admission record it relied on. |

## 7. Machine classes (HO-0001 §3.2)

| Machine | TCB | Trust state (`24`) | What it may do before a current proof |
|---|---|---|---|
| First install (M1) | `gov-admit` after FC-1…FC-8; install from buffer; record in the store | admitted binary anchors by `confirm-state` or a pin (protected installation) | C0 until admitted; after admission per `24` §4.3, OP-7 and §7.1 |
| Clean CI runner (M2) | image build runs FC-1…FC-8 with codes provisioned from the OP-13 sources (or media under (d)); root-owned store and record with `valid_until`; jobs run as another user (GB-6) | pin naming the TSS used for C3 (`24` §4.4) | per pin; C0 after record or pin expiry |
| Restored from backup (M3) | binary already admitted; GB rules apply; re-admission keeps the restored store | `24` §5.3 (CR5-B-08) | as `24` |
| Old epoch (M4), no epoch (M5), two machines (M6), long offline (M7) | admitted, or first admission if none | `24` §5.4–§5.7 | as `24` |
| Legacy consumer, first RoT-1 binary (`11` Phase 4) | `gov-admit`; the legacy 4.1.5 binary never verifies a RoT-1 binary | first anchor on the admitted binary | legacy project is `LEGACY` until `update --apply` by the admitted binary **from a protected installation** (§7.1) |
| Build from source | R-ADM-11 | — | — |

### 7.1 User-writable installation (revision 6; RV5-M8 option (a); computed and executed)

| OP-7 answer or provisioning | Classes reachable on a user-writable installation |
|---|---|
| (a) anchored only | C0 |
| (b) maximum anchor age | C0 |
| (c) witnesses, none held | C0 |
| (c) witnesses at the C3 threshold held | C0–C2 (C3 refused by GB-4′) |
| (d) compiled epoch | C0–C2, labelled `FRESHNESS_UNPROVEN` |
| administrator-provisioned system pin (any answer) | C0–C2 (C3 refused by GB-4′) |

Evidence: `evidence/r6/UW6-user-writable-install.json` (re-run of RV5-D-A03 on the revision-6 executor and the retained
decision rule). Every stated row equals the computed classes. Ceremonies and C3 are refused on the user-writable binary.
A legacy consumer's Phase 4 `update --apply` from a user-writable installation is refused. Test: RT-138 (revised).

## 8. Channels and admitter distribution

`32` states the first-contact root, the procedure, the admitter rules and OP-13. OP-12 decides the admitter's form. Every
form keeps R-ADM-2′…R-ADM-5. The distribution channel of the admitter is a carrier: FC-3 selects it. OP-13 (c) is not
supported together with OP-12 (b) or (c) (`32` §7).

## 9. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| **AD-1′** | **The first-contact root** (restated in revision 6). The first-contact sources the operator consults under the owner's OP-13 answer admit a malicious first TCB with no key. | exactly the root sets of `32` §6 (FC-R1…FC-R4) | FA6 S3; RT-159 |
| RS-B1 | A stale page selects the state its code names | `32` §10 | FA6 S1 (FA5 `CH1`) |
| TB-1′ | A malicious binary run directly, outside admission, ignores every rule | GB rules bind genuine binaries, including revoked ones; the documented procedure never runs a candidate | FA6 S1 (FA5 `DA04`) |
| AD-2 | Same-account code executed before the first admission | fresh store at first admission (R-ADM-8′); afterwards RS-3/TG-2 | FA6 S6; ADM6 A09b |
| VR-B1′ | A same-account replacement of a user-writable binary is A3 | such an installation reaches only §7.1 | UW6 |

## 10. Evidence

| Evidence | Kind | Result |
|---|---|---|
| `evidence/r6/gov_admit_reference_r6.py`, `FA6-first-admission.{py,json}` | executed (real Ed25519 through OpenSSL; `sha256sum`) | S1 FA5 unchanged on revision 6: 45/45 scenarios, 17/17 vectors, 26/27 mutants. S2 first contact per OP-13 answer (`32` §11). S3 executed first-contact minima equal to CS6 for all seven answers. S4 shared vectors R1–R5 refused with the same codes as P4r6. S5 restrictor revocation and root threshold. S6 records. S7 every revision-6 rule mutant detected. |
| `evidence/r6/ADM6-admission-transactions.{py,json}` | executed (reference executor) | A08 crash between install and record: C0 only. A09 re-admission keeps store, anchors, high-waters, per-project records and the earlier record (the revision-5 mutant discards them); a store without a record is moved aside. A10 rollback keeps the record. A11 eight concurrent admissions with the lock: one store, no record moved aside (the unlocked mutant moves a record-holding store aside in most trials). A15 shipped and moved-aside records not honoured. |
| `evidence/r6/UW6-user-writable-install.{py,json}` | executed and computed | §7.1 table equals the computed classes |
