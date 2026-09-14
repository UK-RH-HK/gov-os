# D-synthesis 03 — Held-out attack register RV5-D-A01 … A08 (review r5 synthesis)

Authored by AR-0014. None of these attacks is:
- an acceptance case of `12-ACCEPTANCE-TEST-PLAN.md` (§4c RT-128…RT-155, §7c);
- an architect self-attack (`28` §6 A-R5-01…13);
- a specialist falsification (`4.1.6-alternatives-r5/`);
- a reviewer B or C attack of this round (RV5-B-A01…A19, RV5-C-A01…A13);
- an attack of reviews r2, r3 or r4.

For each attack the nearest existing case is named, with the reason it does not cover the attack.

## Evidence classes

| Class | Meaning |
|---|---|
| **E** | Executed: the pack checker `constitutional-surface/csi_check.py` (unmodified), the reference executor `evidence/r5/gov_admit_reference.py` (unmodified; real Ed25519 through OpenSSL), or the real legacy 4.1.5 binary as consumer |
| **C** | Computed: the architect's P4r5 and P4r4 functions or CS5 module, loaded unmodified |
| **D** | Design or code reading at `cdb4e14` |

Probes and outputs: `evidence/probes/RV5-D-A0*.py` and `evidence/outputs/RV5-D-A0*.json`. A second run of each probe was
byte-identical (`01-REPRODUCTION.md` §5).

## Register

| ID | Attack | Required area (HO-0014 §2.3) | Revision 5 as written | Class | Nearest case (why not covered) | Finding |
|---|---|---|---|---|---|---|
| **RV5-D-A01** | **Registered constitutional content not established first-hand.** Genuine 4.1.8 extends the `aws-access-key` regex, and the honest verifiers accept that candidate. With release CI plus the `release-candidate` and `release-final` keys (one everyday key under OP-4 "no"), the attacker signs a second candidate and final: same source and inputs, regex `(?:AKIA\|ABIA)` (drops `ASIA`). It hands them, with the CI-derived unit map, to the honest registration ceremony. | class interaction BC-1 × BC-3; option combination OP-4; forward compatibility | **Custodians sign:** R-REG-3 (d) records accepted for source and inputs; (e) content digest equal. **Diff list** identical to the genuine release's (the one regex unit). **Reductions:** none. **V8** holds. **E7 as written:** eligible; with a source-bound verification restrictor: still eligible; with a candidate-bound restrictor and consistency: refused. **OP-4 "no":** root valid under the Fact Threshold Check, eligible. **Checker:** attacker kernel exit 0 under the CI-derived registration, exit 3 under a first-hand registration. **4.1.5:** the `ASIA…` file is indexed and served under the attacker kernel and excluded under the genuine one. | E + C | RT-140 and REG5 (a `release-final` mix against a registration derived from the genuine kernel); RV5-B-A06, A09 (the registration authority as actor); CS5 (binary goals only); P4r5 `E7-*` rows (units differ from the registration); RT-115 (a final naming another source) | **RV5-H3** |
| **RV5-D-A02** | **Evaluator selected by one channel under OP-13 (b).** The owner chooses two agreeing channels. One compromised channel leaves the fingerprints genuine and publishes the digest of a substituted admitter. | owner options OP-12 × OP-13; BC4-1 × BC4-2 | `31` R-ADM-2 compares the admitter digest with "the channels" and sets no quorum. `21` OP-13 governs "typed state fingerprints" only. FA5 `operator_compare_admitter(measured, tps_admitter_list, channel_digest)` takes one channel digest, and the TPS list cannot be held before the admitter runs. Any substituted evaluator admits anything (RV5-B-A02 shows a negative-skipping one). | D | FA5 ADM1 (the genuine digest on the one channel consulted); RV5-B-A01 (the attacker changes the fingerprint, not the admitter digest) | **RV5-H1** (extension) |
| **RV5-D-A03** | **User-writable installation versus anchoring.** An admitted binary lives in a user-owned directory (a developer workstation without administrator rights). Which operation classes can that machine ever reach? | class interaction BC-2 × BC4-2; option combination OP-7 × GB-4; R2-H4 × BC4-2 (Phase 4) | `gov_run`: C0, C1, C2 `ALLOWED`; C3, `confirm-root`, `confirm-state` and trust-gate confirmation `TCB_WRITABLE_BY_GOVERNED_ACCOUNT`. P4r4 decision rule: fresh store and writable account pin → `UNANCHORED`, C0 only under OP-7 (a), (b), and (c) without witnesses; C0–C2 under (d). Reachable classes without an administrator or witnesses: (a) C0, (b) C0, (c) C0, (d) C0–C2. `31` GB-4 says "C0–C2 only"; `12` RT-138 expects "C0–C2 still available"; `24` §4.2 lists `confirm-state` in C0. Phase 4 `update --apply` (C3) is unreachable on such a workstation. | C + D | RT-138 (expects C0–C2); FA5 INS2, DA04 (the refusal only); RV5-B-A12 (no user-writable machine class) | **RV5-M8** |
| **RV5-D-A04** | **The two executors of admission-predicate/1 disagree, and neither oracle carries the case.** Four rows: (R1) the registered final revoked; (R2) the registered candidate revoked; (R3) an ACCEPTED attestation issued for another candidate with the same source; (R4) `min_binary_version` above the binary. | implementation plan's ability to detect regressions | **Bootstrap reference executor (real Ed25519, 44 verifications):** R1, R2, R3, R4 all `ACCEPTED`. **Running-mode oracle (P4r5):** R1 `BINARY_REVOKED`, R2 `BINARY_REVOKED`, R3 `VERIFICATION_RECORDS_BELOW_MINIMUM`, R4 not modelled. **FA5 vectors and scenarios:** no revocation of a final or candidate; no candidate-binding case; `min_binary_version` appears in no instrument. **P4r5:** `AP-A8_candidate_revoked` only. `31` §3: "A difference in result on a shared vector is a release-blocking defect of both"; these are not shared vectors. | E + C | RT-134 and RT-135 (take their shapes from P4r5 and FA5); RT-70 (binary floor for the running binary, not admission of a candidate); RT-153 (revoked attestation counts) | **RV5-M9** |
| **RV5-D-A05** | **Forward compatibility: a new constitutional file set shipped in the kernel.** Capability Acceptance Contract Markdown plus compiled YAML, in five steps N1–N5. | forward-compatibility constraint | **N1** unclassified files exit 2 (default deny). **N2** classified `pinned_file` by a TPS change; exit 0 under the release's own registration; units `file:contracts/…` for both files. **N3** attacker YAML (evidence minimum 0) exit 0 under the CI-derived registration. **N4** exit 3 under a first-hand registration. **N5** no reduction reported. | E | RV5-B-A11 (unknown file exit 2); selftest S02, S22; RT-143 (owner-domain binding group) | classification holds; content inherits **RV5-H3**; derivation note **RV5-I2** |
| **RV5-D-A06** | **Owner-option combinations that change security** (OP-1 … OP-15; §A06 below) | owner-option combinations | 10 combinations change security and are not stated, or are stated incorrectly; 5 are stated correctly | D, with C/E references | `21` "Combinations that change security" (7 rows) | RV5-H1, H2, H3, M3, M8, L6, **L9** |
| **RV5-D-A07** | **Can the implementation plan detect the defects of this review?** | implementation plan's ability to detect regressions | Not detectable by any RT as written, or by the instruments RT-128/RT-131 use: RV5-H1 (no register row for lineage selection or channel quorum; FA5 CH2 types the genuine fingerprint), RV5-H2 (no image atom, goal or substitution row), RV5-H3 (no content goal; no first-hand unit-map row), RV5-D-A04 R1 (no final-revocation row in either oracle), R3 and R4 (no row), RV5-M3 (no re-admission row). RT-138 expects an outcome that is unreachable under OP-7 (a)/(b). | C | RT-128 (asserts only the `29` §4 rows); RT-131 (re-runs the calculator's own model); RT-127 (compares option text with calculator output) | RV5-M5, RV5-M9; closure criteria of CD5-4 |
| **RV5-D-A08** | **Class-level interactions between the four R2 closures** (§A08 below) | class-level interactions of the R2 closures | 3 interactions fail (RV5-H3, RV5-M8, RV5-H1 evaluator), 3 hold (reproduced rows), 2 are observations | D, with E/C references | RT-126 (review r3 interaction rows under revision-4 rules) | RV5-H1, H3, M8 |

## RV5-D-A01 — detail

**Pack text relied on.**

| Rule | Text at `cdb4e14` |
|---|---|
| `30` R-REG-3 (d) | verification records "each ACCEPTED for exactly this `source` and `inputs_manifest_digest`". No candidate digest; no kernel tree digest. |
| `30` R-REG-3 (e) | "the `content_digest` recomputed by each custodian from its own fetch". No rule derives the unit map, kernel tree digest or migrations from that fetch. |
| `23` §12.5 | "`gov release build`, canonical CI: `csi_check.py derive-registration` produces the unit map". The ceremony "lists every unit that differs from the previous registration". |
| `04` V8 | the final's candidate verifies under `release-candidate`; kernel tree digest and source are equal in final and candidate |
| `19` E7, `23` §12.3 | the registration is referenced by the effective TSS, names R's final, and units and kernel tree digest are equal. No verification or candidate condition. |
| `05` §1 | `release-final`: "nothing becomes effective: a final is a policy root ... only if a registration names its digest"; "`release-final` appears in no minimal set" |

**Part A (computed on P4r5 functions, unmodified).**

| Check | Result |
|---|---|
| Ceremony R-REG-3 (d), (e) as written | signs |
| V8 as written | holds |
| E7 as written | eligible |
| E7 + verification restrictor bound to source (RV5-B-H3 correction as worded) | eligible |
| E7 + restrictor bound to the registered candidate + final/registration consistency | refused (`verification_records_below_minimum`) |
| Variant: the registration names the attested candidate; the final promotes from the attacker's candidate | E7 as written eligible; source-bound eligible; candidate-bound refused (`final_not_promoted_from_registered_candidate`) |
| OP-4 "no" (one key holds `release-final` and `release-candidate`) | Fact Threshold Check: no violation; E7 eligible |
| Control: the registration derived first-hand from the verified source | `surface_unregistered_for_release` |

**Part B (executed).**

| Check | Result |
|---|---|
| Ceremony diff list vs 4.1.7, genuine | `leaf:SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex` |
| Ceremony diff list vs 4.1.7, attacker | the same single unit |
| `registration-reductions` [4.1.6, 4.1.7, attacker 4.1.8] | exit 0, no reduction |
| E7: attacker kernel under the CI-derived registration | exit 0 |
| E7: attacker kernel under the first-hand registration | exit 3 (`value digest not registered`; `kernel_tree_digest_mismatch`) |
| E7: genuine kernel under the first-hand registration | exit 0 |
| 4.1.5 consumer, genuine 4.1.8 kernel | `ASIA…` file not indexed, not returned |
| 4.1.5 consumer, attacker 4.1.8 kernel | `product/notes/deploy.md` indexed and returned by `memory query` |

**Minimal capability sets.**

| Owner answers | Set | Notes |
|---|---|---|
| any OP-2, OP-8, OP-9 | {pipeline, `release-candidate`, `release-final`} | honest custodians, verifiers and publisher |
| OP-4 "no" | {pipeline, one everyday key} | |
| additionally under OP-2 (b) | {two delegated custodians, `release-final`} | RV5-B-H3 |

**Detection.**
- Honest reproducers build from the source. The embedded kernel differs from the registered kernel tree digest, so a
  publisher running AP-4…AP-8 (`25` §9) will not publish the release's binaries.
- That is a signal only for releases that ship binaries. No rule requires anyone to investigate it, and it does not
  un-register the content: R-REG-4 makes registrations append-only, and the remedy is revocation. A kernel-only release
  gives no signal.

## RV5-D-A06 — owner-option combinations

| Combination | Effect on security | Stated in `21`? | Evidence | Finding |
|---|---|---|---|---|
| OP-4 "no" × registration path | {pipeline, one everyday key} makes malicious constitutional content effective | **No.** OP-4 says the candidate and final keys "appear in no minimal set". | D-A01 part A | RV5-H3 |
| OP-2 (a) vs (b) × registration path | D-A01 route independent of OP-2; (b) adds {2 delegated custodians, `release-final`} | **No** | D-A01; RV5-B-A06 | RV5-H3 |
| OP-8 = 2 × registration path | no effect: records are reused by source and inputs | **No** (OP-8 is presented as protecting source legitimacy) | D-A01 | RV5-H3 |
| OP-9 (d) × registration path | no effect by rule: custodians' own reproduction is compared with binary digests, not with the registered kernel | **No** | design `30` R-REG-3 (f) | RV5-H3 |
| OP-13 (b) × OP-12 (any form) | evaluator selected by one channel; the fingerprint quorum is read from the selected Trust Policy | **No** (states that both channels are needed) | D-A02; RV5-B-A01 | RV5-H1 |
| OP-10 (b) × build environment | the diverse reproducer must match bit for bit, so it shares the registered image | **No** | RV5-B-A08, A04 part I | RV5-H2 |
| OP-7 (a) or (b) × a user-writable install | C0 only (not C0–C2); governed use needs an administrator-provisioned pin or a protected install | **No** (`31` GB-4 says C0–C2) | D-A03 | RV5-M8 |
| OP-14 (b) or OP-15 (a) × OP-11 (a) | each expiry or self-revocation forces `gov-admit`, which discards the store; E10 no longer refuses a repository-delivered older eligible release | **No** | RV5-B-A12 M8, `admit_tx` A09 | RV5-M3 |
| OP-3 mode B × CR4-B-07 option 1 | without a trust gate there is no in-gate proof (P2); a P1 proof names only the anchored TSS, so each certified update needs a fresh `confirm-state` or pin naming the publishing TSS, or witnesses; mode B's "no human step" holds only under OP-7 (c) | **No** (OP-3 "Mode B adds TA-7 for currency") | design `24` §4.4, `27` §3.1 | **RV5-L9** |
| OP-1 root threshold 1 × any | one root key signs every Trust Policy (floors, `channel_quorum`, `clock_reset`, `accepted_tbm_reset`) | **No** minimum stated | RV5-B-A18 | RV5-L6 |
| OP-7 (d) × OP-11 (b) | a raised `min_release_sequence` does not reach machines that do not hold the raising Trust Policy | yes ("where the Trust Policy reaches") | design | — |
| OP-6 (c) × first admission | no added protection once admitted | yes | design | — |
| OP-12 (c) × any | the helper machine joins every first admission's TCB | yes | design | — |
| OP-7 (c) × one witness service | one service compromise witnesses stale state | yes | design | — |
| OP-5 × any | informational | yes | design | — |

## RV5-D-A08 — interactions between the four R2 closures

| Interaction | Question | Result | Evidence |
|---|---|---|---|
| R2-H1 (constitutional floors) × R2-H3 (TCB first-hand) | Does the first-hand rule of the TCB closure (FD-1 rule 3) reach the constitutional content the registration fixes? | **Fails.** The registration signs content it did not establish. | D-A01 (RV5-H3) |
| R2-H2 (anchoring) × R2-H3/BC4-2 (TCB location) | Can a machine whose TCB is user-writable anchor? | **Fails (availability, statement).** C0 only under OP-7 (a)/(b). | D-A03 (RV5-M8) |
| R2-H3 × R2-H2 (first admission) | Is the evaluator selected at the authority of the state selector? | **Fails.** One channel selects it. | D-A02 (RV5-H1) |
| R2-H4 (legacy) × BC4-2 (Phase 4 on a user-writable workstation) | Can a legacy consumer migrate? | Fails closed: `update --apply` is C3 and refused, so the project stays `LEGACY` | D-A03 |
| R2-H4 × BC4-3 (registration statement in the trust entry set) | Can a legacy write alter `registration.dsse.json` or the trust entry set and stay `COMPLETE`? | **Holds.** 0 violations over 30,165 rows. | reviewer C `matrix5`, reproduced |
| R2-H2 × R2-H4 (restored machine plus Git restore of pre-migration paths) | Does a legacy restore create a state RoT-1 treats as valid? | **Holds.** `LEGACY` or `PARTIAL(occupation)`. | reviewer C `gitops` RESTORE_PRE_GOV and CHECKOUT_PRE, reproduced |
| R2-H1 × R2-H2 (trust-state thief descendant referencing a registration) | Can stale-state selection make content effective without the registration authority? | **Holds** for key theft without the registration keys; under OP-2 (b) two delegated keys plus the trust-state and `release-final` keys reach C1–C2 (RV5-B-A06) | RV5-B-A04 part P, reproduced |
| BC4-1 × BC4-3 (binaries embed the source's kernel; the registration names the pipeline's kernel) | Is the divergence refused by rule? | Observation: AP-8 makes the release's binaries unpublishable, a signal only; no rule acts on it | D-A01 detection note |
