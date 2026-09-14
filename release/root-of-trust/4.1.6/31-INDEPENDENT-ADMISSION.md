# Output 31 — Independent admission of the TCB on every machine (BC4-2)

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 5. Closes blocking class **BC4-2** (review r4 RV4-H2: anchored, non-circular first TCB acceptance) by
> applying rule FD-1 (`29`) to the base case of TCB acceptance. Mechanism: one acceptance predicate with two executors
> (specialists A and B), a typed state fingerprint as the only selector of state (A), installation from the measured buffer,
> the genuine-binary rule and a fresh verifier trust store at first admission (B), and ceremony order (A)
> (`4.1.6-alternatives-r5/SYNTHESIS.md` §3). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Root cause accepted

Anchors, negative sets and currency proofs existed only inside `gov`. The chain was proven for "binary N accepts binary N+1"
and extended to the machine by assumption. Its base case was a different, weaker predicate: tooling checking A2–A6 (no
negatives, no anchor, no currency), or a build compared with values the built binary printed. `11` Phase 4 had a legacy
consumer verify its first RoT-1 binary with that binary, and every first-install ceremony ran on the unaccepted binary
(RV4-B-A03, A04, D-A04). An inductive chain whose base case does not satisfy the inductive predicate proves nothing for the
machine.

## 2. Invariant

Every TCB acceptance on a machine — the first binary, a CI runner image's binary, a legacy consumer's first RoT-1 binary, and
every later binary — is the same predicate (`25` §5, admission-predicate/1), evaluated by code other than the candidate over
bytes that code measured, with a selector of state whose currency is established now or within a window that names that
state; the bytes that later run as `gov` are the bytes accepted; and no ceremony whose purpose is TA-5 runs before that
acceptance.

## 3. One predicate, two executors

| Executor | When | Selector of state (AP-3) | Negatives, registration, quorum, publication, TBM | Candidate executed? |
|---|---|---|---|---|
| `gov trust verify-artifact` (the admitted binary N) | every later binary | inclusion anchor plus a currency proof naming the selected TSS (P1 naming it, P2 typed fingerprint, P3 witnesses) | AP-4…AP-8 | never |
| **`gov-admit`** (independent executor) | first binary on a machine; CI image build; legacy consumer (Phase 4); build from source | the TSS whose epoch fingerprint equals the value typed now from the independent channels (OP-13) | AP-4…AP-8, identical | never |

Both implement `admission-predicate/1` from one normative specification and one shared set of conformance vectors
(`evidence/r5/FA5-first-admission.py` vectors; `evidence/r5/P4r5-conformance-oracle.py` for running mode). A difference in
result on a shared vector is a release-blocking defect of both.

## 4. `gov-admit` (R-ADM)

| ID | Rule |
|---|---|
| R-ADM-1 | `gov-admit` is a separate program implementing only statement verification, admission-predicate/1 and installation. Its form and distribution are OP-12. It is itself a registered, quorum-reproduced artefact (the registration's `admitter` entry, `30` §5). |
| R-ADM-2 | Before running it, the operator compares its SHA-256, with a platform tool (`sha256sum`, `shasum -a 256`, `certutil -hashfile`), with the admitter digest published in the independent channels (TA-5). A mismatch stops the procedure (`ADMITTER_DIGEST_MISMATCH`). |
| R-ADM-3 | The operator types the **current** state fingerprint from the channels (OP-13 (a) one channel; (b) two channels whose values must be equal, else `CHANNEL_DISAGREEMENT`). The fingerprint is the only selector of root chain, Trust Policy, Trust State and therefore the negative set. No compiled value, clock, repository file or environment variable is an input. |
| R-ADM-4 | `gov-admit` reads the candidate once into a buffer and **never executes it**. No value the candidate prints is an input; `gov version --trust` is diagnostics only. |
| R-ADM-5 | `gov-admit` refuses to evaluate a candidate whose digest equals its own (`SELF_EVALUATION_REFUSED`). |
| R-ADM-6 | **Installation from the measured buffer:** write to a temporary file in the destination directory, `fsync`, atomic rename, re-read and compare the digest. Installing by re-reading the source path is forbidden (a swap between measurement and install is otherwise installed). |
| R-ADM-7 | **Admission record** `{binary_digest, target, release_id, lineage, state_fingerprint, admitted_at, admitter_digest, valid_until, location_protected}` (`schemas/admission-record.schema.json`), written beside the binary. `valid_until` is mandatory for CI image records (≤ `pin_max_validity_days`) and, under OP-14 (b), for every record. |
| R-ADM-8 | **Fresh verifier trust store at first admission:** any verifier trust store present for the lineage before the first admission is moved aside, never read, so records written by code that ran before admission are not used (AD-2). |
| R-ADM-9 | The admission record is not an anchor. The admitted binary's first trust operation establishes its own anchor (`gov trust confirm-state`, typed again, or a protected pin; `24` §3). |
| R-ADM-10 | `gov-admit` shows the selected state's `issued_at` and age, and never the word `current`. |
| R-ADM-11 | **Build from source is not a separate trust path.** A self-built binary is measured by `gov-admit`; it is a production binary only if its digest equals a registered, quorum-reproduced, published digest. Otherwise it is `build: development`, whatever it prints. |
| R-ADM-12 | `gov-admit` implements the Fact Threshold Check on every root version and the append-only and equivocation rules of registrations, exactly as `gov`. |

## 5. Genuine-binary rule (GB) — what a RoT-1 `gov` does at process start

| ID | Rule |
|---|---|
| GB-1 | A RoT-1 binary measures its own executable once at start. Without an admission record naming that digest it runs **C0 only** and refuses C1–C3 and every TA-5 ceremony (`confirm-root`, `confirm-state`, in-gate fingerprints, trust-gate confirmations) with `BINARY_NOT_ADMITTED`, naming `gov-admit` as the remedy. |
| GB-2 | A record with `valid_until` in the past refuses above C0 (`ADMISSION_RECORD_EXPIRED`). |
| GB-3 | When the held negative set names its own digest or release, the binary refuses per OP-15 (`BINARY_REVOKED_SELF`): (a) everything above C0, or (b) C3 and ceremonies. This protects against genuine-but-revoked binaries; malicious binaries are excluded by admission, not by this rule. |
| GB-4 | C3 and every ceremony additionally require that the executable, the admission record and every ancestor directory satisfy the TCB-location predicate (owned by another uid and not writable by the effective uid, or on a read-only mount): `TCB_WRITABLE_BY_GOVERNED_ACCOUNT` otherwise (CR4-B-01 (b)). A user-writable install is therefore C0–C2 only. |
| GB-5 | An account-location record (C1–C2) is writable by A3; A3 can equally replace the binary. The rule binds the transport and repository adversaries, not A3 (RS-3 class). |

## 6. Ceremony order (R-CER)

| ID | Rule |
|---|---|
| R-CER-1 | No TA-5 ceremony is performed by a binary that has not been admitted on this machine (GB-1 enforces it). |
| R-CER-2 | On first install the typed fingerprint commits to the lineage id, so lineage confirmation is part of admission. Trust on first use is not available for production (OP-6 restated). |
| R-CER-3 | `confirm-root` and `confirm-state` on an admitted binary follow `24` §3; the in-gate fingerprint follows `27` §3.1. |
| R-CER-4 | Every surface that shows a ceremony result shows the admission record it relied on. |

## 7. Machine classes (HO-0001 §3.2)

| Machine | TCB | Trust state (`24`) | What it may do before a current proof |
|---|---|---|---|
| First install (M1) | `gov-admit` with typed fingerprint(s); install from buffer; admission record | admitted binary anchors by `confirm-state` (typed again) or a pin | C0 until admitted; after admission per `24` §4.3 and OP-7 |
| Clean CI runner (M2) | image build runs `gov-admit` with the operator-provisioned fingerprint, writes a root-owned record with `valid_until` ≤ `pin_max_validity_days` beside the root-owned pin; images are rebuilt before either expires | pin naming the TSS used for C3 (`24` §4.4) | per pin; C0 after record or pin expiry |
| Restored from backup (M3) | binary already admitted; GB-1…GB-3 apply | as `24` §5.3 | as `24` |
| Old epoch (M4), no epoch (M5), two machines (M6), long offline (M7) | admitted, or first install if none | as `24` §5.4–§5.7 | as `24`; binary upgrade needs a proof naming the TSS that publishes it |
| Legacy consumer, first RoT-1 binary (`11` Phase 4) | `gov-admit`; the legacy 4.1.5 binary has no `verify-artifact` and never verifies a RoT-1 binary | first anchor on the admitted binary | legacy project is `LEGACY` until `update --apply` by the admitted binary |
| Build from source | R-ADM-11 | — | — |

## 8. Channels and admitter distribution

- **OP-13** decides whether first admission (and, by the same rule, `confirm-state`) needs one channel or two agreeing
  channels. The consequence for malicious binaries is computed (`30` §10: FA1 versus FA2 rows).
- **OP-12** decides the admitter's form. Every form keeps R-ADM-2…R-ADM-5; the distribution channel of the admitter is a
  carrier, because the digest comparison selects it.

## 9. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| RS-B1 | A fingerprint typed from a stale page of the channel(s) selects the state it names | the channels' own currency (TA-5); `issued_at` and age shown; OP-13 (b) needs both channels stale | FA5 `CH1` |
| TB-1′ | A malicious binary run directly, outside admission, ignores every rule | GB rules bind genuine binaries, including revoked ones; the documented procedure never runs a candidate | FA5 `DA04`, P4r5 |
| AD-1 | All channels the operator uses are compromised together with the trust-state key and reproducer quorum keys | `30` §10 FA rows | CS5 |
| AD-2 | Same-account code executed before the first admission | fresh verifier trust store (R-ADM-8); afterwards RS-3/TG-2 | FA5 `VTS1` |
| VR-B1 | none beyond RS-3: a same-account replacement of a user-writable binary is A3, and such an install is C0–C2 only (GB-4) | GB-4 | FA5 `INS2` |

## 10. Evidence

`evidence/r5/gov_admit_reference.py` (reference executor: real Ed25519 through the platform OpenSSL, never executes the
candidate) and `evidence/r5/FA5-first-admission.{py,json}`: scenarios V00, FB1a/b, FB2a/b/c, FB3, BUILD1, PH4 (real legacy
4.1.5 register), CI1, DA04, CH1, CH2, ADM1, INS1, INS2, VTS1, K1, K2, the conformance vectors and single-rule mutants;
revision-4 paths (b) and (c) run as controls. Results are recorded in `22` §1.
