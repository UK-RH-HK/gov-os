# Output 30 — Release registration, verification records and the reproduction quorum (BC4-1)

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 5. Closes blocking class **BC4-1** (review r4 RV4-H1: independent decisions for the TCB) by applying
> rule FD-1 (`29`) to the decision "binary *B* is the trusted computing base". Mechanism: specialist A's release registration
> and first-person reproduction quorum, combined with specialist B's canonical source identity, admitted build profile and
> single-valued publication (`4.1.6-alternatives-r5/SYNTHESIS.md` §2). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Root cause accepted

Revision 4 counted **statements per purpose**. Two `release-artifact` custodians signed a threshold-2 statement whose only
first-hand content was "a build attestation exists", so one threshold-1 `build-attestation` key plus control of the release
pipeline yielded an accepted malicious binary (RV4-B-A01, AF1; D-A07 showed a root co-signature over the same check adds
nothing). The source fact rested on one `verification-attestation` key (RV4-B-A02). And nothing selected the **build
inputs** at the authority the binary carries: the release process named them (specialist A, N02). Each fact that makes a
binary the TCB had a selector below the authority of the TCB.

## 2. The facts and their selectors

| Fact | Selector (FD-1) | Authority | Restrictors | Carriers |
|---|---|---|---|---|
| **F-SRC** the source identity is the production source of release *R* | the **Release Registration Statement** (§5), signed only against first-hand verification records (§6) | root threshold (OP-2 (a)) or a delegated `release-registration` quorum ≥ 2 (OP-2 (b)) | a REJECTED verification attestation; revocations; OP-8 verification records visible to the verifier | Git host, pipeline |
| **F-INPUTS** the build inputs are the admitted inputs | the same registration, naming the **input manifest** digest (§4.2), checked against upstream signed checksums before signing | as F-SRC | revocations | mirrors, caches, CI configuration |
| **F-BYTES** *B* and its TBM digest are the output of building F-SRC with F-INPUTS for target *T* | a **quorum of first-person reproductions** (§7), confirmed first-hand to the publisher; under OP-9 (d) also the registration custodians' own reproduction | ≥ 2 distinct `reproducer` keys that hold no other purpose (rank 2) | a conflicting reproduction refuses; revoked reproductions and keys count for nothing | pipeline, download host |
| **F-PUB/F-CUR** *B* is published and not revoked as of a currency proof | the **selected Trust State** (`24`; `31` §4 for first admission) | trust-state purpose within an anchored, currency-proven chain, or a typed fingerprint | negative set; accepted-TBM high-water; `min_binary_version` | transport |
| **F-T0** the roots, policies, state and rules compiled into *B* are genuine | none separately: files of F-SRC, covered by F-BYTES; TBM consistency is a restrictor (`25` §4) | — | TBM resolution | — |

## 3. Purposes (changes to `05`)

| Purpose | Revision 5 | Change from revision 4 |
|---|---|---|
| **`release-registration`** (new) | signs `release-registration.v1+json` (§5) | new; KS-10′: threshold ≥ 2; keys are root keys at root threshold (OP-2 (a)) or hold no other purpose (OP-2 (b)) |
| **`reproducer`** (new) | signs `binary-reproduction.v1+json` (§7), exactly one signature per statement | new; KS-9′: compiled quorum ≥ 2 distinct keys; keys hold no other purpose |
| `verification-attestation` | the verdict for one candidate over its source identity and input manifest (§6); REJECTED refuses; ACCEPTED counts only when the registration lists it | no longer a selector of source; KS-12: shares no key with `reproducer` or `release-registration` |
| `release-final` | authenticity of the final release statement; a **restrictor**: the registered final must verify under it | selects nothing: no final becomes a policy root, and no binary is accepted, without the registration that names its digest |
| `release-candidate` | candidates for gated evaluation projects only | unchanged |
| `trust-state` | publishes `registrations[]` and `published_binaries[]` cumulatively (§8) | `artifacts[]` replaced; never selects legitimacy |
| **`release-artifact`** | **withdrawn** (KS-13) | its threshold-2 statement asserted nothing first-hand |
| **`build-attestation`** | **withdrawn** (KS-13) | replaced by the reproduction quorum |

## 4. Source identity, input manifest and build profile

### 4.1 Source identity (`source`)

`{release_commit, content_digest}`.
- `content_digest` is SHA-256 over the sorted lines `<mode> <path> <SHA-256 of blob bytes>` of the whole tree. Any holder of
  the tree recomputes it, independently of commit history, archive tool and time.
- It replaces revision 4's `source_tree_digest` (SHA-256 of `git archive`). Executed evidence
  (`evidence/r5/SRC5-source-identity.json`): an archive of a commit binds the commit id, and an archive of a tree is
  time-stamped, so the revision-4 digest is not recomputable by an independent party holding the same tree.

### 4.2 Input manifest (`input-manifest.v1+json`, published; its digest is `inputs_manifest_digest`)

`{toolchain [{name, version, archive_sha256, upstream_checksum_reference}], lockfile_sha256, build_image_digest,
build_profile {remap_path_prefixes [source, cargo_home, toolchain_home], profile, flags, target_features}, targets[]}`.
- Every input is named by digest. A reproducer obtains each input by that digest from any carrier (R-REP-2).
- The build profile is normative (IR-REP-2): specialist B's F5 shows plain release builds differ across Cargo home paths
  (188 embedded path strings) and path-remapped builds are bit-identical across four paths on one machine and toolchain.

## 5. Release Registration Statement (`release-registration.v1+json`)

Fields: `{release_id, sequence, final_statement_digest, candidate_statement_digest, source {release_commit, content_digest},
inputs_manifest_digest, targets[], verification_records[] (attestation digests), constitution {kernel_tree_digest, units
{unit → value}}, migrations {path → digest}, admitter (optional: the `gov-admit` target, `31` §4), binary_digests
{target → digest} (OP-9 (d) only), lowering_history[]}`.

| ID | Rule |
|---|---|
| R-REG-1 | Every release that ships a kernel, binaries or the admitter is registered **exactly once**, by the registration authority of OP-2. |
| R-REG-2 | A registration is effective on a machine only when the effective Trust State references its digest in `registrations[]` (knowledge follows state). |
| R-REG-3 | **The ceremony checks, before signing:** (a) each toolchain archive digest against the upstream release's own signed checksums; (b) the lockfile digest against the file in the registered source; (c) the build image digest against the owner's image record; (d) OP-8 verification records received **first-hand** from each independent verifier over the owner's authenticated ceremony channel (never from the pipeline, never inferred from a signature alone), each ACCEPTED for exactly this `source` and `inputs_manifest_digest`, and no REJECTED record; (e) the `content_digest` recomputed by each custodian from its own fetch; (f) under OP-9 (d), each custodian's own reproduction. `gov trust draft-registration` refuses without (a)–(f) evidence. |
| R-REG-4 | Registrations are **append-only**: a second registration for a `release_id` with different content, or two releases at one `sequence`, is malformed and refuses both (`REGISTRATION_REWRITE`, `REGISTRATION_SEQUENCE_EQUIVOCATION`, `REGISTRATION_EQUIVOCATION` at the verifier). A release is retired only by revocation or `min_release_sequence`. |
| R-REG-5 | The registration delivers itself **first-hand** to the reproducers and to the trust-state publisher. Neither acts on a registration received from the pipeline. |
| R-REG-6 | The `constitution` block fixes every non-join unit of the release and its kernel tree digest (`23` §12). The registration is therefore the one ceremony per release that covers source, inputs, content, final and targets. |
| R-REG-7 | V8 (final source equal to candidate source) is a producer restrictor: `gov release promote` refuses a final whose source differs from the verified candidate's. It no longer protects the TCB; the registration does. |
| R-REG-8 | A registration's `lowering_history` declares every computed reduction it introduces (`23` §12.4). |
| R-REG-9 | Under OP-2 (b), root grants, rotates and revokes the delegated keys; the compiled Fact Threshold Check applies (`29` §5.2). |
| R-REG-10 | Re-registration after a key rotation is a new release; a registration is never re-signed to change its content. |

## 6. Verification records (restrictor and counted evidence)

| ID | Rule |
|---|---|
| R-VER-1 | An independent verifier reproduces the candidate payload from `source` with the manifest inputs, checks the manifest against upstream signed checksums, reviews the source under the owner's verification scope, and returns its record first-hand to the ceremony. It signs `verification-attestation.v3+json` `{candidate_statement_digest, verdict, source, inputs_manifest_digest}`. |
| R-VER-2 | At the verifier, at least OP-8 ACCEPTED attestations by distinct keys, each listed in the registration's `verification_records`, unrevoked, and with the registered `source` and inputs, are required (`VERIFICATION_RECORDS_BELOW_MINIMUM`). A held REJECTED attestation for the registered candidate refuses (`ARTIFACT_SOURCE_REJECTED`). |
| R-VER-3 | A verification key never selects source: without the registration authority, stolen verification keys yield nothing (CS5 INV-SRC-KEYS). |
| R-VER-4 | The verifier in this programme is an AI session run by the owner; its independence is a process property (TA-11). OP-8 sets how many independent verification processes a registration requires. |

## 7. Reproduction quorum (`binary-reproduction.v1+json`)

Fields: `{release_id, source, inputs_manifest_digest, target, binary_digest, tbm_digest, environment_digest, reproduced_at}`.

| ID | Rule |
|---|---|
| R-REP-1 | A reproduction is **first-person**: exactly one `reproducer` signature, attesting a build that reproducer performed. A statement with several signatures counts for none. |
| R-REP-2 | A reproducer obtains **every** input by digest from the registered manifest, from any carrier, and refuses on mismatch. No mirror, CI variable or cache is a selector. |
| R-REP-3 | A reproducer confirms its digest **first-hand** to the trust-state publisher over the owner's authenticated channel, and publishes its statement. The publisher never learns a reproduction only through the pipeline. |
| R-REP-4 | Acceptance needs ≥ max(2, OP-9 quorum) distinct unrevoked reproducer keys on the same `(release_id, source, inputs_manifest_digest, target, binary_digest, tbm_digest)`. |
| R-REP-5 | **Conflict refuses.** Any valid reproduction for the same `(release_id, target)` with another digest refuses every digest of that pair (`REPRODUCTION_CONFLICT`) until a revocation removes one side. |
| R-REP-6 | Revoked reproduction statements, and statements by keys revoked in any held root version, count for nothing (CR4-B-10). |
| R-REP-7 | Rotation never re-signs a reproduction: a reproduction by a removed key is replaced only by a new reproduction (specialist B, N19). |
| R-REP-8 | Reproducers are independent of each other and of the pipeline in custody and environment (TA-10′; not verifier-checkable; recorded in the ceremony record). |
| R-REP-9 | Under OP-10 (b) at least one reproducer builds with an independently bootstrapped compiler; under OP-10 (c) the toolchain archive in the manifest is the owner's own, itself registered and reproduced. |

## 8. Publication (trust-state publisher)

| ID | Rule |
|---|---|
| R-PUB-1 | The publisher references a registration only when received first-hand from the ceremony (R-REG-5), and a binary digest only when: OP-8 ACCEPTED verification statements exist and no REJECTED is visible; ≥ quorum distinct reproducers confirmed that digest first-hand; no reproducer confirmed another digest; under OP-9 (d) the digest equals the registered digest. |
| R-PUB-2 | `registrations[]` and `published_binaries[]` are cumulative: a TSS never drops either (admissibility, `17` S4 (d); oracle row RET-D-admissibility). |
| R-PUB-3 | Exactly one published digest per `(release_id, target)`. |
| R-PUB-4 | The state fingerprint of every TSS is published in the independent channels (`06` §2). |

## 9. Honest-party model

The honest-party rules above are encoded exactly as H-PIPE, H-VER, H-REG, H-REP, H-PUB, H-CH and VICTIM in
`evidence/r5/CS5-tcb-capability-sets.py`. An implementation or process that deviates from any of them changes the minimal
sets, and the owner re-runs the calculator (FD-3).

## 10. Minimum capability sets (computed; `evidence/r5/CS5-tcb-capability-sets.json`)

Atoms: `pipeline` (release CI), `insider` (route I), `vpN` (verification process N compromised), `vaN` (verification key N
stolen), `cust1+cust2` (registration custodians at threshold compromised), `regk1+regk2` (registration keys at threshold
stolen), `rpN` (reproducer process N), `repN` (reproducer key N), `ts` (trust-state key), `transport` (withholding at the
victim), `chN` (independent channel N), `mirror`, `toolchain_up`, `diverse_tc`, `owner_tc`. Victims: **P1** running binary
with a pin or confirmation naming the TSS used (`24` §4.4 revision 5); **P2** running binary with an in-gate typed
fingerprint; **FA1/FA2** first admission typing one / two agreeing channels (OP-13). The tables use OP-2 (a) or (b) (identical
sets; the labels differ), with q and n from OP-9.

**Malicious bytes for a genuine registration (G_BYTES):**

| OP-9 | Process compromise | Key theft (P2 / FA1; FA2 adds `ch2`; P1: none) |
|---|---|---|
| (a) n = 2, q = 2 | {rp1, rp2} | {ch1, rep×2, ts, transport}; {ch1, regk1, regk2, rep×2, ts} |
| (b) n = 3, q = 2 | {rp1, rp2, rp3} | {ch1, any 2 rep, ts, transport}; {ch1, regk1, regk2, any 2 rep, ts} |
| (c) n = 3, q = 3 | {rp1, rp2, rp3} | {ch1, rep×3, ts, transport}; {ch1, regk1, regk2, rep×3, ts} |
| (d) with (a) | {cust1, cust2, rp1, rp2} | {ch1, regk1, regk2, rep×2, ts} |
| (d) with (b) / (c) | {cust1, cust2, rp1, rp2, rp3} | {ch1, regk1, regk2, 2 / 3 rep, ts} |

**Malicious source faithfully built (G_SRC), any OP-9:** {insider} (TB-4); {pipeline, vp1} under OP-8 = 1, {pipeline, vp1,
vp2} under OP-8 = 2 (TB-4′); {cust1, cust2, va1(, va2)} (OP-2 (a): root threshold, A8; OP-2 (b): delegated quorum); key theft
(P2/FA1): {ch1, regk1, regk2, rep×q, ts, va×OP-8} (FA2 adds `ch2`; P1: none).

**Malicious named build inputs (G_INPUTS):** {cust1, cust2, va×OP-8}; key theft as G_SRC without `insider`/`vp` routes. The
pipeline alone never succeeds (the ceremony and verifiers check upstream checksums).

**Poisoned mirror (G_MIRROR):** the mirror appears in no minimal set (inputs by digest). **Compromised upstream toolchain
(G_TOOLCHAIN):** OP-10 (a) {toolchain_up} (TA-12); (b) {toolchain_up, diverse_tc} or {toolchain_up, rp1}; (c) {owner_tc}.

**Invariants (0 failures in 1,752 checks):** every G_BYTES set contains ≥ q reproducer compromises (and under (d) the
registration threshold); every non-residual G_SRC set contains ≥ OP-8 verification compromises and the registration
threshold or pipeline input; every key-theft-only G_SRC set contains the registration threshold keys; no key-theft-only set
has one key; `release-final` and `release-candidate` keys appear in no minimal set.

**Review r4 routes under these rules:** RV4-B-A01 {one reproducer or build key, pipeline} → refused; RV4-B-A02 {one
verification key, pipeline} → refused; RV4-D-A07 (root co-signature pass-through) → the purpose does not exist; its
revision-5 analogue (custodians naming a digest handed to them) is shown by control to lower the minimum, which is why
OP-9 (d) requires the custodians' own reproduction (R-REG-3 (f)).

## 11. Implementation requirements (product source is not changed by this revision)

| ID | Requirement | Acceptance test |
|---|---|---|
| IR-REP-1 | The production build reads provenance only from the registered source archive. `runtime/build.rs` today falls back to `git rev-parse HEAD` when no release manifest is present (line 73); the production profile MUST NOT. | RT-133: two builds of `git archive` of the registered commit in directories without `.git` are bit-identical. |
| IR-REP-2 | The normative build profile remaps source, Cargo home and toolchain home paths (`--remap-path-prefix`) and fixes flags and target features. | RT-133: four builds at different paths and homes are bit-identical; `strings` finds no build path. |
| IR-REP-3 | Cross-OS and cross-distribution reproducibility for each registered target is shown before that target is registered. | RT-133 per target |
| IR-REP-4 | `gov trust draft-registration` implements R-REG-3 and refuses without its evidence; `gov trust draft-policy --derivation` implements FD-3. | RT-130, RT-131 |

## 12. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-S1 | Reproducer compromise at the quorum (processes, or keys plus the trust-state key and a channel) | §10 minimal sets; OP-9 raises them | RT-131 (calculator re-run on the implementation's rules) |
| TB-S2 (TA-12) | A malicious upstream toolchain release that passes the ceremony's checksum check | not bounded by the verifier; OP-10 | CS5 G_TOOLCHAIN rows |
| TB-S3 (TA-10′) | Reproducers or registration custodians under common custody | procedural; ceremony record | — |
| TB-4 (route I) | An insider change accepted by honest but deceived verification | process; OP-8 | — |
| TB-4′ (TA-11) | OP-8 compromised verification processes plus pipeline input | §10; OP-8 | CS5 G_SRC rows |
| AV-S1 | One reproducer key forces `REPRODUCTION_CONFLICT` for one release (availability) | remedy: revoke the forged reproduction | P4r5 `AP-R5_conflicting_reproduction` |
