# Output 30 — Release registration, verification records and the reproduction quorum (BC4-1, BC5-2, BC5-3)

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 6** amends this file for review r5:
> - the build environment becomes a registered, first-hand-established input (BC5-2; `33`): §2 F-ENV, §4.2 input manifest
>   v2, R-REG-3 (c′), R-VER-1, R-REP-2;
> - registered constitutional content is derived first-hand and verification is bound to exactly the registered candidate and
>   kernel (BC5-3; `34`): §2 F-CON, R-REG-3 (d) and (g), R-REG-6, R-VER-1, R-VER-2, R-PUB-1′;
> - restrictors are removed only under the registration authority (CR5-B-01): R-REG-11, R-REP-5′;
> - source identity v2 (RV5-M4): §4.1;
> - the honest-party model and every minimum-set statement come from the revision-6 calculator CS6 (§9, §10; FD-3).
>
> New in revision 5; it closed blocking class **BC4-1** (review r4 RV4-H1: independent decisions for the TCB) by applying rule
> FD-1 (`29`) to the decision "binary *B* is the trusted computing base". Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Root cause accepted

**Revision 5.** Revision 4 counted **statements per purpose**. Two `release-artifact` custodians signed a threshold-2 statement
whose only first-hand content was "a build attestation exists". So one threshold-1 `build-attestation` key plus control of the
release pipeline yielded an accepted malicious binary (RV4-B-A01). Each fact that makes a binary the TCB had a selector below
the authority of the TCB.

**Revision 6.** Review r5 found the same shape in three facts revision 5 did not assign:
- the **build environment**, which every reproducer had to use (RV5-H2);
- the **registered constitutional content**, which the ceremony signed but CI derived (RV5-H3);
- the **removal of restrictors**, which a trust-state key could effect by listing honest reproductions in `revocations`
  (RV5-M1).

Each now has a first-hand selector at the registration's authority, or a stated residual.

## 2. The facts and their selectors

| Fact | Selector (FD-1) | Authority | Restrictors | Carriers |
|---|---|---|---|---|
| **F-SRC** the source identity is the production source of release *R* | the **Release Registration Statement** (§5), signed only against first-hand verification records (§6) | root threshold (OP-2 (a)) or a delegated `release-registration` quorum ≥ 2 (OP-2 (b)) | a REJECTED verification attestation for the registered candidate; revocations; OP-8 verification records visible to the verifier | Git host, pipeline |
| **F-INPUTS** the toolchain archives and lockfile are the admitted inputs | the same registration, naming the **input manifest** digest (§4.2), checked against upstream signed checksums before signing | as F-SRC | revocations | mirrors, caches, CI configuration |
| **F-ENV** (revision 6) the build environment of each target is the admitted environment | the same registration, naming each **environment manifest** (`33` §3), established by at least two first-hand environment reproductions from components checked against upstream signed checksums (`33` R-BENV-1, R-BENV-2) | as F-SRC | environment reproduction conflict; OP-16 (b) diversity | mirrors, caches, image registries |
| **F-CON** (revision 6) the kernel tree digest, non-join units and migrations are the content of release *R* | the same registration, whose `constitution` block each custodian **derives first-hand** from the source it fetched (`34` R-CON-1) | as F-SRC | OP-8 ACCEPTED attestations for exactly the registered candidate and kernel (`34` R-CON-2); E7 restrictors (`34` R-CON-3) | pipeline, kernel payload, Git delivery |
| **F-BYTES** *B* and its TBM digest are the output of building F-SRC with F-INPUTS in F-ENV for target *T* | a **quorum of first-person reproductions** (§7), confirmed first-hand to the publisher; under OP-9 (d) also the registration custodians' own reproduction | ≥ 2 distinct `reproducer` keys that hold no other purpose (rank 2) | a conflicting reproduction refuses until the registration authority revokes one side (R-REP-5′); revoked reproductions and keys count for nothing | pipeline, download host |
| **F-PUB/F-CUR** *B* is published and not revoked as of a currency proof | the **selected Trust State** (`24`; first admission: the first-contact manifest the agreed code names, `32`) | trust-state purpose within an anchored, currency-proven chain, or the first-contact root | negative set; accepted-TBM high-water; `min_binary_version` | transport |
| **F-T0** the roots, policies, state and rules compiled into *B* are genuine | none separately: files of F-SRC, covered by F-BYTES; TBM consistency is a restrictor (`25` §4) | — | TBM resolution | — |

## 3. Purposes (changes to `05`)

| Purpose | Revision 6 | Change |
|---|---|---|
| **`release-registration`** | signs `release-registration.v2+json` (§5) and **`registration-revocation.v1+json`** (R-REG-11) | revision 6 adds the revocation statement and the `environments` block |
| **`reproducer`** | signs `binary-reproduction.v2+json` (§7) and **`environment-reproduction.v1+json`** (`33` R-BENV-2), exactly one signature per statement | revision 6 adds `environment_id` and environment reproductions |
| `verification-attestation` | **`verification-attestation.v4+json`** `{candidate_statement_digest, verdict, source, inputs_manifest_digest, kernel_tree_digest}` (§6) | revision 6 adds `kernel_tree_digest`; ACCEPTED counts only for exactly the registered candidate and kernel (R-VER-2) |
| `release-final` | authenticity of the final release statement; a **restrictor** (promoted from the registered candidate, registered kernel tree) | selects nothing |
| `release-candidate` | candidates; the registered candidate is a restrictor of E7 and AP-5 | revision 6: the registered candidate must carry the registered kernel |
| `trust-state` | publishes `registrations[]` and `published_binaries[]` cumulatively (§8) | its `revocations` never remove a restrictor (R-REP-5′) |
| `release-artifact`, `build-attestation` | withdrawn (KS-13) | unchanged |

## 4. Source identity, input manifest and build profile

### 4.1 Source identity v2 (`source`; RV5-M4)

`{release_commit, git_tree, content_digest}`.
- **`content_digest`** (`governance-os.source-content-digest/2`) is computed from Git objects only:
  1. Enumerate the registered commit's tree recursively, NUL-separated (`git ls-tree -r -z --full-tree`).
  2. Refuse the source (`SOURCE_PATH_REFUSED`) if any path holds a byte below 0x20 or equal to 0x7f, any path is not UTF-8,
     or any entry is a submodule or not a blob.
  3. For each entry in ascending byte order of the path, form the record
     `u64be(len(mode)) ‖ mode ‖ u64be(len(path)) ‖ path ‖ u64be(32) ‖ SHA-256(blob)`.
  4. The digest is SHA-256 of `"governance-os.source-content-digest/2\n" ‖ u64be(count) ‖ records`.
- **`git_tree`** is the Git tree object id of `release_commit`. Either identity alone detects a different tree; a verifier and
  a custodian recompute both.
- Revision 5's line encoding (`<mode> <path> <sha256>` joined by newlines) was ambiguous for newline-bearing paths: two trees
  with different file sets had equal digests (RV5-B-A05). Revision 5's SRC5 hashed `git archive` output, which is
  time-dependent. Evidence: `evidence/r6/SRC6-source-identity-v2.json`. Reviewer B's two-tree construction is refused, and
  with the refusal disabled the two digests differ. Paths with spaces, prefixes, empty files, moved content and Unicode
  normalisation forms all differ. The executable bit and link targets change the digest; commit metadata does not. The
  digest is identical across two clones and two wall-clock times, and two runs are byte-identical.

### 4.2 Input manifest v2 (`input-manifest.v2+json`, published; its digest is `inputs_manifest_digest`)

`{toolchain [{name, version, archive_sha256, upstream_checksum_reference}], lockfile_sha256, environments [{target,
environment_id, environment_tree_digest, supplier_class}], build_profile {remap_path_prefixes [source, cargo_home,
toolchain_home], profile, flags, target_features}, targets[]}`.
- Every input is named by digest. A reproducer obtains each input by that digest from any carrier (R-REP-2).
- `build_image_digest` (revision 5) is **withdrawn**. The environment is registered by its manifest and reproduced first-hand
  (`33`).
- The build profile is normative (IR-REP-2).

## 5. Release Registration Statement (`release-registration.v2+json`)

Fields: `{release_id, sequence, final_statement_digest, candidate_statement_digest, source {release_commit, git_tree,
content_digest}, inputs_manifest_digest, environments [{target, environment_id, environment_tree_digest, supplier_class,
environment_reproductions[]}], targets[], verification_records[] (attestation digests), constitution {kernel_tree_digest,
units {unit → value}}, migrations {path → digest}, admitter (optional: the `gov-admit` targets, `31` §4), binary_digests {target
→ digest} (OP-9 (d) only), lowering_history[]}`.

| ID | Rule |
|---|---|
| R-REG-1 | Every release that ships a kernel, binaries or the admitter is registered **exactly once**, by the registration authority of OP-2. |
| R-REG-2 | A registration is effective on a machine only when the effective Trust State references its digest in `registrations[]` and no registration revocation names it (knowledge follows state). |
| R-REG-3 | **The ceremony checks, before signing (every custodian itself):** (a) each toolchain archive digest against the upstream release's own signed checksums; (b) the lockfile digest against the file in the registered source; **(c′)** each environment manifest: every component against its upstream signed checksum, and at least two agreeing first-hand environment reproductions (`33` R-BENV-1, R-BENV-2); **(d)** OP-8 verification records received **first-hand** from each independent verifier over the owner's authenticated ceremony channel, each ACCEPTED for **exactly this candidate**, this `source`, `inputs_manifest_digest` and `kernel_tree_digest`, and no first-hand REJECTED record for this candidate; (e) `content_digest` and `git_tree` recomputed from the custodian's own fetch; (f) under OP-9 (d), the custodian's own reproduction; **(g)** the `constitution` and `migrations` blocks derived first-hand from the custodian's own kernel build (`34` R-CON-1). `gov trust draft-registration` refuses without (a)–(g) evidence (`REGISTRATION_CONTENT_NOT_ESTABLISHED`, `ENVIRONMENT_COMPONENT_UNVERIFIED`, `ENVIRONMENT_NOT_REPRODUCED`, `VERIFICATION_RECORDS_NOT_FIRST_HAND_FOR_CANDIDATE`). |
| R-REG-4 | Registrations are **append-only**: a second registration for a `release_id` with different content, or two releases at one `sequence`, is malformed and refuses both (`REGISTRATION_REWRITE`, `REGISTRATION_SEQUENCE_EQUIVOCATION`, `REGISTRATION_EQUIVOCATION` at the verifier). A release is retired only by revocation or `min_release_sequence`. |
| R-REG-5 | The registration delivers itself **first-hand** to the reproducers and to the trust-state publisher. Neither acts on a registration received from the pipeline. |
| R-REG-6 | The `constitution` block fixes every non-join unit of the release and its kernel tree digest (`23` §12). It is **derived first-hand** by each custodian (R-REG-3 (g)); a CI-derived map is a proposal only. |
| R-REG-7 | V8 (final source equal to candidate source; revision 6: final kernel tree equal to candidate kernel tree) is a producer restrictor. The registration and E7 protect the TCB and content. |
| R-REG-8 | A registration's `lowering_history` declares every computed reduction it introduces (`23` §12.4). |
| R-REG-9 | Under OP-2 (b), root grants, rotates and revokes the delegated keys; the compiled Fact Threshold Check applies (`29` §5.2). |
| R-REG-10 | Re-registration after a key rotation is a new release; a registration is never re-signed to change its content. |
| **R-REG-11** | **Registration revocation** (revision 6; CR5-B-01). A `registration-revocation.v1+json` statement `{revokes [statement digests], reason}` at the registration threshold is the only statement that removes a **restrictor**: a conflicting reproduction (R-REP-5′) or a REJECTED verification attestation (`25` AP-5r). It is issued through the `05` §9 playbook after the custodians have established, first-hand, that the named statement is forged. A trust-state or `revocation` key's `revocations` entry for such a statement lowers positive counts only and never clears a refusal. |

## 6. Verification records (restrictor and counted evidence)

| ID | Rule |
|---|---|
| R-VER-1 | An independent verifier reproduces the candidate payload, including the kernel payload, from `source` with the manifest inputs in a registered environment. It checks the toolchain archives and every environment component against upstream signed checksums, and reviews the source under the owner's verification scope. It returns its record first-hand to the ceremony. It signs `verification-attestation.v4+json` `{candidate_statement_digest, verdict, source, inputs_manifest_digest, kernel_tree_digest}`. `kernel_tree_digest` is the digest of the kernel payload it reproduced, never a value supplied to it. |
| R-VER-2 | At the verifier, at least OP-8 ACCEPTED attestations by distinct keys are required (`VERIFICATION_RECORDS_BELOW_MINIMUM`). Each MUST be listed in the registration's `verification_records` and unrevoked, and MUST name **exactly the registered candidate**, the registered `source`, inputs and `kernel_tree_digest` (`34` R-CON-2). A held REJECTED attestation for the registered candidate refuses (`ARTIFACT_SOURCE_REJECTED`) unless a registration revocation names it. |
| R-VER-3 | A verification key never selects source or content: without the registration authority, stolen verification keys yield nothing (CS6 INV-SRC, INV-CONTENT). |
| R-VER-4 | The verifier in this programme is an AI session run by the owner; its independence is a process property (TA-11). OP-8 sets how many independent verification processes a registration requires. |

## 7. Reproduction quorum (`binary-reproduction.v2+json`)

Fields: `{release_id, source, inputs_manifest_digest, environment_id, target, binary_digest, tbm_digest, reproduced_at}`.

| ID | Rule |
|---|---|
| R-REP-1 | A reproduction is **first-person**: exactly one `reproducer` signature, attesting a build that reproducer performed. A statement with several signatures counts for none. |
| R-REP-2 | A reproducer obtains **every** input by digest from the registered manifest, from any carrier, and refuses on mismatch. It re-assembles the registered environment from its pinned components, or verifies an environment obtained by digest by re-assembly (`33` R-BENV-4). No mirror, CI variable, cache or image registry is a selector. |
| R-REP-3 | A reproducer confirms its digest **first-hand** to the trust-state publisher over the owner's authenticated channel, and publishes its statement. The publisher never learns a reproduction only through the pipeline. |
| R-REP-4 | Acceptance needs ≥ max(2, OP-9 quorum) distinct unrevoked reproducer keys on the same `(release_id, source, inputs_manifest_digest, target, binary_digest, tbm_digest)`, each under an `environment_id` registered for the target; under OP-16 (b) from at least two supplier classes (`33` R-BENV-5). |
| **R-REP-5′** | **Conflict refuses** (revision 6: CR5-B-01). Any valid reproduction for the same `(release_id, target)` with another digest refuses every digest of that pair (`REPRODUCTION_CONFLICT`). Only a registration revocation (R-REG-11) naming the conflicting statement removes it. A trust-state or `revocation` key's revocation of it does not. |
| R-REP-6 | Revoked reproduction statements, and statements by keys revoked in any held root version, count for nothing toward the quorum (CR4-B-10). |
| R-REP-7 | Rotation never re-signs a reproduction: a reproduction by a removed key is replaced only by a new reproduction. |
| R-REP-8 | Reproducers are independent of each other and of the pipeline in custody and environment (TA-10′; not verifier-checkable; recorded in the ceremony record). |
| R-REP-9 | Under OP-10 (b) at least one reproducer builds with an independently bootstrapped compiler; under OP-10 (c) the toolchain archive in the manifest is the owner's own, itself registered and reproduced. |

## 8. Publication (trust-state publisher)

| ID | Rule |
|---|---|
| **R-PUB-1′** | The publisher references a registration only when it is received first-hand from the ceremony (R-REG-5) **and** E7's restrictors hold on the statements the publisher holds (`34` R-CON-3; defence in depth). It references a binary digest only when all of these hold: OP-8 ACCEPTED verification statements for the registered candidate and kernel exist; no unremoved REJECTED is visible; at least quorum distinct reproducers under registered environments confirmed that digest first-hand; no reproducer confirmed another digest; under OP-9 (d) the digest equals the registered digest. |
| R-PUB-2 | `registrations[]` and `published_binaries[]` are cumulative: a TSS never drops either (admissibility, `17` S4 (d)). |
| R-PUB-3 | Exactly one published digest per `(release_id, target)`. |
| R-PUB-4 | The first-contact code and state fingerprint of every TSS are published in the independent channels (`06` §2, `32` §3). |

## 9. Honest-party model

The rules above are encoded as the rules of the revision-6 derivation calculator, one switch each
(`evidence/r6/CS6-derivation-calculator.py` `RULES`):

| CS6 rule | Pack rule |
|---|---|
| `H_VER_UPSTREAM` | R-VER-1 upstream checks (toolchain and environment components) |
| `H_VER_BINDS_CANDIDATE` | R-VER-1 / `34` R-CON-2: the verifier attests exactly the candidate and kernel it reproduced |
| `H_REG_RECORDS_FIRST_HAND` | R-REG-3 (d) |
| `H_REG_UPSTREAM` | R-REG-3 (a), (c′) |
| `H_REG_ENV_QUORUM` | `33` R-BENV-2 |
| `H_REP_ENV_REASSEMBLE` | `33` R-BENV-4, R-REP-2 |
| `H_REG_CONTENT_FIRST_HAND` | R-REG-3 (g), `34` R-CON-1 |
| `H_REG_OWN_REPRODUCTION` | R-REG-3 (f) |
| `H_REP_BY_DIGEST`, `H_REP_FIRST_HAND` | R-REP-2, R-REP-3 |
| `H_SIGN_REPRODUCE` | `05` §7 rule 2 |
| `H_PUB_REGISTRATION_RESTRICTORS` | R-PUB-1′ |

An implementation or process that deviates from any of them changes the minimal sets, and the owner re-runs the calculator
(FD-3). `29` §4 names, for each rule, the calculator mutation or the oracle scenario that fails when it is removed.

## 10. Minimum capability sets (computed)

Atoms: `pipeline` (release CI); `insider` (route I); `vpN` (verification process N); `vaN` (verification key N); `cust1+cust2`
(registration custodians at threshold); `regk1+regk2` (registration keys at threshold); `rpN` (reproducer process N); `repN`
(reproducer key N); `ts` (trust-state key); `rc`, `rf`, `kc` (candidate, final, shared everyday key); `transport`
(withholding at the victim); `chN` (first-contact or in-gate source N); `op1src` (one source typed for all); `wk1+wk2`
(witness keys); `pinprov` (a pin provisioner under the repository writer's control, RS-4); `mirror`; `toolchain_up`,
`diverse_tc`, `owner_tc`; `env_up_a`, `env_up_b`, `owner_env`.

Victims:
- **P1**: running binary with a pin or confirmation naming the TSS used.
- **P2k1/P2k2**: running binary with an in-gate fingerprint typed from one or two sources.
- **WR**: witness-reliant runner (OP-7 (c)).
- **CIR**: CI runner with an admission record and pin.
- **FA**: first admission under each OP-13 answer (`32` §6).

**Malicious bytes for a genuine registration (G_BYTES):**

<!-- CS6:BEGIN OP-9-BYTES -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| OP-9 | Victim | Minimal sets: malicious bytes for a genuine registration (OP-2 (a), OP-8 = 1) |
|---|---|---|
| n2q2 | P1 | {2 reproducer processes} |
| n2q2 | P2k1 | {2 reproducer processes}; {2 reproducer keys, transport, ts, ch1}; {2 registration keys, 2 reproducer keys, ts, ch1} |
| n2q2 | P2k2 | {2 reproducer processes}; {2 reproducer keys, transport, ts, ch1, ch2}; {2 reproducer keys, transport, ts, ch1, op1src}; {2 registration keys, 2 reproducer keys, ts, ch1, ch2}; {2 registration keys, 2 reproducer keys, ts, ch1, op1src} |
| n2q2 | WR | {2 reproducer processes}; {2 reproducer keys, transport, ts, wk1, wk2}; {2 registration keys, 2 reproducer keys, ts, wk1, wk2} |
| n2q2 | CIR | {2 reproducer processes}; {2 reproducer keys, transport, ts, pinprov}; {2 registration keys, 2 reproducer keys, ts, pinprov} |
| n3q2 | P1 | {3 reproducer processes} |
| n3q2 | P2k1 | {3 reproducer processes}; {2 reproducer keys, transport, ts, ch1}; {2 registration keys, 2 reproducer keys, ts, ch1} |
| n3q2 | P2k2 | {3 reproducer processes}; {2 reproducer keys, transport, ts, ch1, ch2}; {2 reproducer keys, transport, ts, ch1, op1src}; {2 registration keys, 2 reproducer keys, ts, ch1, ch2}; {2 registration keys, 2 reproducer keys, ts, ch1, op1src} |
| n3q2 | WR | {3 reproducer processes}; {2 reproducer keys, transport, ts, wk1, wk2}; {2 registration keys, 2 reproducer keys, ts, wk1, wk2} |
| n3q2 | CIR | {3 reproducer processes}; {2 reproducer keys, transport, ts, pinprov}; {2 registration keys, 2 reproducer keys, ts, pinprov} |
| n3q3 | P1 | {3 reproducer processes} |
| n3q3 | P2k1 | {3 reproducer processes}; {3 reproducer keys, transport, ts, ch1}; {2 registration keys, 3 reproducer keys, ts, ch1} |
| n3q3 | P2k2 | {3 reproducer processes}; {3 reproducer keys, transport, ts, ch1, ch2}; {3 reproducer keys, transport, ts, ch1, op1src}; {2 registration keys, 3 reproducer keys, ts, ch1, ch2}; {2 registration keys, 3 reproducer keys, ts, ch1, op1src} |
| n3q3 | WR | {3 reproducer processes}; {3 reproducer keys, transport, ts, wk1, wk2}; {2 registration keys, 3 reproducer keys, ts, wk1, wk2} |
| n3q3 | CIR | {3 reproducer processes}; {3 reproducer keys, transport, ts, pinprov}; {2 registration keys, 3 reproducer keys, ts, pinprov} |
| d_n2q2 | P1 | {2 registration custodians, 2 reproducer processes} |
| d_n2q2 | P2k1 | {2 registration custodians, 2 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, ch1} |
| d_n2q2 | P2k2 | {2 registration custodians, 2 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, ch1, ch2}; {2 registration keys, 2 reproducer keys, ts, ch1, op1src} |
| d_n2q2 | WR | {2 registration custodians, 2 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, wk1, wk2} |
| d_n2q2 | CIR | {2 registration custodians, 2 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, pinprov} |
| d_n3q2 | P1 | {2 registration custodians, 3 reproducer processes} |
| d_n3q2 | P2k1 | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, ch1} |
| d_n3q2 | P2k2 | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, ch1, ch2}; {2 registration keys, 2 reproducer keys, ts, ch1, op1src} |
| d_n3q2 | WR | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, wk1, wk2} |
| d_n3q2 | CIR | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, ts, pinprov} |
| d_n3q3 | P1 | {2 registration custodians, 3 reproducer processes} |
| d_n3q3 | P2k1 | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 3 reproducer keys, ts, ch1} |
| d_n3q3 | P2k2 | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 3 reproducer keys, ts, ch1, ch2}; {2 registration keys, 3 reproducer keys, ts, ch1, op1src} |
| d_n3q3 | WR | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 3 reproducer keys, ts, wk1, wk2} |
| d_n3q3 | CIR | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 3 reproducer keys, ts, pinprov} |
<!-- CS6:END OP-9-BYTES -->

**Malicious source faithfully built (G_SRC):**

<!-- CS6:BEGIN OP-8-SRC -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| OP-8 | OP-2 | Minimal sets: malicious source faithfully built (victim P1, OP-9 (a)) |
|---|---|---|
| 1 | root | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf} |
| 1 | delegated | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf} |
| 2 | root | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf} |
| 2 | delegated | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf} |
<!-- CS6:END OP-8-SRC -->

**Compromised upstream toolchain (G_TOOLCHAIN):**

<!-- CS6:BEGIN OP-10-TOOLCHAIN -->
| OP-10 | Minimal sets: compromised common-mode toolchain (victim P1, OP-9 (a)) |
|---|---|
| accept | {toolchain_up}; {2 reproducer processes} |
| diverse | {2 reproducer processes}; {1 reproducer process, toolchain_up}; {1 reproducer process, diverse_tc}; {toolchain_up, diverse_tc} |
| owner_built | {owner_tc}; {2 reproducer processes} |
<!-- CS6:END OP-10-TOOLCHAIN -->

**Build environment (G_ENV):** `33` §6. **Registered content (G_CONTENT):** `34` §4. **First admission:** `32` §6.

**Invariants** (every configuration; 0 failures, `22` §1):
- **INV-BYTES:** every G_BYTES set contains ≥ q reproducer compromises (under (d) also the registration threshold), or is a
  residual.
- **INV-SRC:** every non-residual G_SRC and G_INPUTS set contains ≥ OP-8 verification compromises and either the
  registration threshold or pipeline input.
- **INV-MIRROR:** the mirror appears in no set.
- **INV-ONE:** no key-theft-only set has at most one key; residual and first-contact root sets are excepted.
- **INV-RF:** `release-final`, `release-candidate`, the shared everyday key, pipeline and trust-state key never select content
  or bytes, alone or together.

## 11. Implementation requirements (product source is not changed by this revision)

| ID | Requirement | Acceptance test |
|---|---|---|
| IR-REP-1 | The production build reads provenance only from the registered source. `runtime/build.rs` today falls back to `git rev-parse HEAD` when no release manifest is present (line 73); the production profile MUST NOT. | RT-133 |
| IR-REP-2 | The normative build profile remaps source, Cargo home and toolchain home paths and fixes flags and target features. | RT-133 |
| IR-REP-3 | Cross-OS and cross-distribution reproducibility for each registered target is shown before that target is registered; under OP-16 (b) across the registered supplier classes. | RT-133 |
| IR-REP-4 | `gov trust draft-registration` implements R-REG-3 (a)–(g) and refuses without their evidence; `gov trust draft-policy --derivation` implements FD-3 with the CS6 rule set. | RT-130, RT-131 |
| IR-REP-5 | (Revision 6.) Environment reproduction tooling assembles an environment from its manifest deterministically and signs `environment-reproduction.v1+json` (`33`). | RT-160, RT-161 |
| IR-REP-6 | (Revision 6.) Source identity v2 is computed from Git objects in `gov`, `gov-admit` and the ceremony tooling, with the refusals of §4.1. | RT-172 |

## 12. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-S1 | Reproducer compromise at the quorum (processes; or keys with the trust-state key and a victim-specific currency input) | §10 G_BYTES; OP-9 raises it | RT-131 |
| TB-S2 (TA-12) | A malicious upstream toolchain release that passes the ceremony's checksum check | §10 G_TOOLCHAIN; OP-10 | CS6 |
| TB-S2′ (TA-12′) | A malicious upstream environment component, or every supplier class used | `33` §6; OP-16 | CS6; ENV6 |
| TB-S3 (TA-10′) | Reproducers, environment reproducers or registration custodians under common custody | procedural; ceremony record | — |
| TB-4 (route I) | An insider change accepted by honest but deceived verification | process; OP-8 | — |
| TB-4′ (TA-11) | OP-8 compromised verification processes plus pipeline input | §10 G_SRC; `34` §4; OP-8 | CS6 |
| AV-S1 | One reproducer key forces `REPRODUCTION_CONFLICT` for one release (availability) | remedy: registration revocation of the forged reproduction (R-REG-11) | P4r6 `R6-AP5r_registration_authority_revocation_clears_forged_conflict`; FA6 S5 |
