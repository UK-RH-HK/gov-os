# Output 30 — Release registration, verification records and the reproduction quorum (CP-1)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** concretises this file to CP-1 (`35`) under OP-2 (b), OP-8 = 2, OP-9 (b) + (d), OP-10 (b), OP-11 (b) and OP-16 (b)
> (OWNER-DESIGN-REQUIREMENTS-0001), and to review r6:
> - the environment is selected by the lock in registered source and derived, never authored (BC6-3; `33`): §2 F-ENV, §4.2
>   input manifest v3, R-REG-3 (c″), R-VER-1, R-REP-2, R-REP-4;
> - toolchains are registered lineages independent by provenance (OP-10 (b)): R-REG-3 (a), R-REP-9;
> - verification records name their environments and are two independent executions (RV6-L3, OP-8): R-VER-1, R-VER-2;
> - derivation tools come from registered source or an admitted binary (RV6-L4): R-REG-3 (g);
> - the registration carries `binary_digests` and `security_relevant_change` (OP-9 (d), OP-11 (b)): §5, R-REG-3 (h);
> - every minimum-set statement is a CS7 block for CP-1 (§10; RV6-M1).
> The unselected answers of OP-2, OP-8, OP-9 and OP-10 are excluded (EX-09, EX-13, EX-14, EX-15). New in revision 5 for BC4-1.
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Root cause accepted

**Revision 5.** Revision 4 counted statements per purpose; one threshold-1 key plus the pipeline yielded an accepted malicious
binary (RV4-B-A01). Each fact that makes a binary the TCB had a selector below the authority of the TCB.

**Revision 6.** Review r5 found the same shape in the build environment, the registered content and the removal of restrictors;
each got a first-hand selector.

**Revision 7.** Review r6 found that the environment manifest itself had no establishing party (RV6-H3). The lock now lives in
registered source, the manifest is derived, and diversity counts provenance. The owner fixed every remaining option.

## 2. The facts and their selectors

| Fact | Selector (FD-1) | Authority | Restrictors | Carriers |
|---|---|---|---|---|
| **F-SRC** the source identity is the production source of release *R* | the **Release Registration Statement** (§5), signed only against two first-hand verification records (§6) | 2 of 3 delegated `release-registration` keys (OP-2 (b)) | a REJECTED attestation for the registered candidate; revocations; the two verification records visible to the verifier | Git host, pipeline |
| **F-INPUTS** the toolchains, lockfile and environment lock are the admitted inputs | the same registration, naming the input manifest (§4.2) and the environment lock digest, with toolchains checked against the pinned toolchain registry | as F-SRC | revocations | mirrors, caches, CI configuration |
| **F-ENV** each environment of each target is the admitted environment | the same registration, naming each `environment_id` derived from the lock and pinned registry, with at least two agreeing environment reproductions (`33` R-BENV-3″, R-BENV-7″) | as F-SRC | environment reproduction conflict; supplier independence by provenance | mirrors, caches, image registries |
| **F-CON** the kernel tree digest, non-join units and migrations are the content of release *R* | the same registration, whose `constitution` block each custodian derives first-hand (`34` R-CON-1) | as F-SRC | two ACCEPTED attestations for exactly the registered candidate and kernel (`34` R-CON-2); E7 restrictors (R-CON-3) | pipeline, kernel payload, Git delivery |
| **F-BYTES** *B* and its TBM digest are the output of building F-SRC with F-INPUTS in F-ENV for target *T* | a quorum of first-person reproductions from two independent supplier classes and two independent toolchain lineages (§7), confirmed first-hand to the publisher, and the registration's `binary_digests` from the custodians' own reproduction (OP-9 (d)) | 2 of 3 reproducer roles (rank 2) under the 2-of-3 registration | a conflicting reproduction refuses until the registration authority revokes one side (R-REP-5′); revoked reproductions and keys count for nothing | pipeline, download host |
| **F-PUB/F-CUR** *B* is published and not revoked as of a currency proof | the selected Trust State (`24`; first admission: both sources' state code, `32`) | 2 of 3 trust-state keys within an anchored, currency-proven chain, or the first-contact root | negatives; accepted-TBM high-water; `min_binary_version`; the computed security minimum | transport |
| **F-T0** the roots, policies, state and rules compiled into *B* are genuine | none separately: files of F-SRC, covered by F-BYTES; TBM consistency is a restrictor (`25` §4) | — | TBM resolution | — |

## 3. Purposes (see `05`)

| Purpose | Revision 7 |
|---|---|
| `release-registration` | 3 single-purpose keys, threshold 2; signs `release-registration.v3+json` (§5) and `registration-revocation.v1+json` (R-REG-11) |
| `reproducer` | 3 single-purpose keys, quorum 2; signs `binary-reproduction.v3+json` (§7) and `environment-reproduction.v2+json` (`33` R-BENV-7″), one signature per statement |
| `verification-attestation` | `verification-attestation.v5+json` `{candidate_statement_digest, verdict, source, inputs_manifest_digest, kernel_tree_digest, environment_ids, toolchain_ids, verifier_execution_id, verification_report_digest}` (§6) |
| `release-final` | ≥ 2 keys, threshold ≥ 2; a restrictor |
| `release-candidate` | one separate key; the registered candidate is a restrictor of E7 and AP-5 |
| `trust-state` | 3 keys, threshold 2; publishes `registrations[]` and `published_binaries[]` cumulatively (§8); never removes a restrictor |

## 4. Source identity, input manifest and build profile

### 4.1 Source identity v2 (`source`)

`{release_commit, git_tree, content_digest}`.
- **`content_digest`** (`governance-os.source-content-digest/2`) is computed from Git objects only:
  1. Enumerate the registered commit's tree recursively, NUL-separated (`git ls-tree -r -z --full-tree`).
  2. Refuse the source (`SOURCE_PATH_REFUSED`) if any path holds a byte below 0x20 or equal to 0x7f, any path is not UTF-8, or
     any entry is a submodule or not a blob.
  3. For each entry in ascending byte order of the path, form the record
     `u64be(len(mode)) ‖ mode ‖ u64be(len(path)) ‖ path ‖ u64be(32) ‖ SHA-256(blob)`.
  4. The digest is SHA-256 of `"governance-os.source-content-digest/2\n" ‖ u64be(count) ‖ records`.
- **`git_tree`** is the Git tree object id of `release_commit`; a verifier and a custodian recompute both.
- Evidence: `evidence/r6/SRC6-source-identity-v2.json` (retained; unchanged rule).

### 4.2 Input manifest v3 (`input-manifest.v3`, published; its digest is `inputs_manifest_digest`)

`{toolchains [{toolchain_id, compiler_version, archive_sha256}] (at least 2), lockfile_sha256, environment_lock_digest,
build_profile {remap_path_prefixes [source, cargo_home, toolchain_home], profile, flags, linking: static-self-contained,
target_features}, targets[]}` (`schemas/input-manifest.schema.json` 3.0.0).
- Every input is named by digest. A reproducer obtains each input by that digest from any carrier (R-REP-2).
- Environments are not named here: they are derived from the environment lock (`33` §4) and named by the registration.
- The build profile is normative (IR-REP-2); static self-contained linking is a certification criterion (CC-4).

## 5. Release Registration Statement (`release-registration.v3+json`)

Fields (`schemas/release-registration.schema.json` 3.0.0): `{release_id, sequence, final_statement_digest,
candidate_statement_digest, source, inputs_manifest_digest, environment_lock_digest, targets[], verification_records[] (at least
2), constitution {kernel_tree_digest, units}, migrations, environments [{target, environment_id, supplier_id,
environment_reproductions[]}] (at least 2), toolchains [{target, toolchain_id}] (at least 2), binary_digests {target → digest}
(required), security_relevant_change (required), admitter {targets} (optional), lowering_history[], issued_at, trust_root_id}`.

| ID | Rule |
|---|---|
| R-REG-1 | Every release that ships a kernel, binaries or the admitter is registered **exactly once**, by 2 of the 3 registration custodians. |
| R-REG-2 | A registration is effective on a machine only when the effective Trust State references its digest in `registrations[]` and no registration revocation names it. |
| **R-REG-3** | **The ceremony checks, before signing (every signing custodian itself):** **(a)** each toolchain lineage against the root-signed toolchain registry: the archive digest against the upstream signed checksum under the registry's key, or the bootstrap registration of an independently bootstrapped lineage (`33` R-BENV-6″); **(b)** the lockfile and environment lock digests against the files in the registered source; **(c″)** each environment: the manifest derived by `gov-envmanifest/1` from the lock and the pinned supplier registry, at least two agreeing first-hand environment reproductions, and supplier independence by provenance (`33` R-BENV-3″, R-BENV-5″, R-BENV-7″); **(d)** two verification records received first-hand from two independent verifiers over the owner's authenticated ceremony channel, from distinct keys, executions and reports, each ACCEPTED for exactly this candidate, source, input manifest, kernel tree digest and the registered environments and toolchains, and no first-hand REJECTED record for this candidate; **(e)** `content_digest` and `git_tree` recomputed from the custodian's own fetch; **(f)** the custodian's own reproduction of every target, whose digest becomes `binary_digests` (OP-9 (d)); **(g)** the `constitution` and `migrations` blocks derived first-hand from the custodian's own kernel build (`34` R-CON-1), with derivation tools from an admitted `gov` or the custodian's own build of the registered source (`33` R-BENV-9); **(h)** `security_relevant_change` decided from the `registration-changes` listing of security-classified units (`34` R-CON-5). `gov trust draft-registration` refuses without (a)–(h) evidence (`REGISTRATION_CONTENT_NOT_ESTABLISHED`, `ENVIRONMENT_COMPONENT_UNVERIFIED`, `ENVIRONMENT_MANIFEST_NOT_DERIVED`, `ENVIRONMENT_NOT_REPRODUCED`, `ENVIRONMENT_DIVERSITY_NOT_MET`, `TOOLCHAIN_DIVERSITY_NOT_MET`, `VERIFICATION_RECORDS_NOT_FIRST_HAND_FOR_CANDIDATE`, `DERIVATION_TOOL_UNREGISTERED`). |
| R-REG-4 | Registrations are **append-only**: a second registration for a `release_id` with different content, or two releases at one `sequence`, refuses both (`REGISTRATION_REWRITE`, `REGISTRATION_SEQUENCE_EQUIVOCATION`, `REGISTRATION_EQUIVOCATION` at the verifier). A release is retired only by revocation or the security minimum. |
| R-REG-5 | The registration delivers itself **first-hand** to the reproducers and to the trust-state publisher. Neither acts on a registration received from the pipeline. |
| R-REG-6 | The `constitution` block fixes every non-join unit of the release and its kernel tree digest (`23` §12). It is derived first-hand by each custodian (R-REG-3 (g)); a CI-derived map is a proposal only. |
| R-REG-7 | V8 (final source and kernel tree equal to the candidate's) is a producer restrictor. |
| R-REG-8 | A registration's `lowering_history` declares every computed reduction it introduces (`23` §12.4). |
| **R-REG-9′** | The root grants, rotates and revokes the three delegated registration keys; the compiled CP-1 shape applies (KS-10″). Registration at root threshold is excluded (EX-09). |
| R-REG-10 | Re-registration after a key rotation is a new release; a registration is never re-signed to change its content. |
| **R-REG-11** | **Registration revocation.** A `registration-revocation.v1+json` `{revokes [statement digests], reason}` at the registration threshold is the only statement that removes a restrictor: a conflicting reproduction (R-REP-5′) or a REJECTED attestation (`25` AP-5r). A trust-state or revocation-key entry for such a statement lowers positive counts only. |

## 6. Verification records (restrictor and counted evidence)

| ID | Rule |
|---|---|
| **R-VER-1′** | An independent verifier reproduces the candidate payload, including the kernel payload, from `source` with the manifest inputs, in the environments it derived itself from the candidate's environment lock and pinned registry (`33` R-BENV-8) and with the registered toolchain lineages. It checks toolchain archives and environment components under the pinned keys and reviews the source under the owner's verification scope. It returns its record first-hand to the ceremony. It signs `verification-attestation.v5+json` naming its `verifier_execution_id`, `verification_report_digest`, `environment_ids` and `toolchain_ids`. `kernel_tree_digest` is the digest of the kernel payload it reproduced. |
| **R-VER-2′** | At the verifier, **two** ACCEPTED attestations are required from distinct keys, distinct executions and distinct report digests (OP-8; `VERIFICATION_RECORDS_BELOW_MINIMUM`). Each MUST be listed in the registration's `verification_records`, unrevoked, and name exactly the registered candidate, source, inputs, kernel tree digest and every registered environment of the target (`34` R-CON-2). A held REJECTED attestation for the registered candidate refuses (`ARTIFACT_SOURCE_REJECTED`) unless a registration revocation names it. |
| R-VER-3 | A verification key never selects source or content: without the registration authority, stolen verification keys yield nothing (INV-SRC, INV-CONTENT). |
| R-VER-4 | The verifier in this programme is an AI session run by the owner; its independence is a process property (TA-11). The two records come from genuinely separate verifier executions (OP-8). |

## 7. Reproduction quorum (`binary-reproduction.v3+json`)

Fields: `{release_id, source, inputs_manifest_digest, environment_id, toolchain_id, target, binary_digest, tbm_digest, reproduced_at}`.

| ID | Rule |
|---|---|
| R-REP-1 | A reproduction is **first-person**: exactly one `reproducer` signature, attesting a build that reproducer performed. |
| **R-REP-2′** | A reproducer obtains every input by digest from any carrier and refuses on mismatch. It derives the environment manifest from the registered lock and pinned registry and re-assembles it (`33` R-BENV-3″, R-BENV-4″). No mirror, CI variable, cache, image registry or pipeline manifest is a selector. |
| R-REP-3 | A reproducer confirms its digest **first-hand** to the trust-state publisher over the owner's authenticated channel, and publishes its statement. |
| **R-REP-4′** | Acceptance needs at least 2 distinct unrevoked reproducer keys on the same `(release_id, source, inputs_manifest_digest, target, binary_digest, tbm_digest)`, each under an `environment_id` and a `toolchain_id` registered for the target; among them, two supplier classes and two toolchain lineages independent by provenance (`33` R-BENV-5″, R-BENV-6″); the digest equals the registered `binary_digests[target]`. |
| **R-REP-5′** | **Conflict refuses.** Any valid reproduction for the same `(release_id, target)` with another digest refuses every digest of that pair (`REPRODUCTION_CONFLICT`). Only a registration revocation (R-REG-11) naming the conflicting statement removes it. |
| R-REP-6 | Revoked reproduction statements, and statements by keys revoked in any held root version, count for nothing toward the quorum. |
| R-REP-7 | Rotation never re-signs a reproduction: a reproduction by a removed key is replaced only by a new reproduction. |
| R-REP-8 | The three reproducer roles are independent of each other and of the pipeline in custody and environment (TA-10′; recorded in the ceremony record). |
| **R-REP-9′** | **OP-10 (b).** Reproductions come from at least two toolchain lineages independent by provenance, at least one not rooted in an upstream binary compiler archive (`33` R-BENV-6″). An upstream archive alone is not sufficient for acceptance (EX-15). |

## 8. Publication (trust-state publisher)

| ID | Rule |
|---|---|
| **R-PUB-1′** | The publisher references a registration only when it is received first-hand from the ceremony (R-REG-5) **and** E7's restrictors hold on the statements it holds (`34` R-CON-3; defence in depth). It references a binary digest only when two ACCEPTED verification statements for the registered candidate and kernel exist, no unremoved REJECTED is visible, at least the quorum of reproducers from two supplier classes and two toolchain lineages confirmed that digest first-hand, no reproducer confirmed another digest, and the digest equals the registered digest. |
| R-PUB-2 | `registrations[]` and `published_binaries[]` are cumulative: a TSS never drops either (admissibility, `17` S4 (d)). |
| R-PUB-3 | Exactly one published digest per `(release_id, target)`. |
| **R-PUB-4′** | Every Trust State references the FCA in force; its state code and the trust code are published by both first-contact sources after their first-hand verification (`32` R-FCS-1…R-FCS-3). The publisher composes no first-contact value. |

## 9. Honest-party model

The rules above are encoded as rules of the revision-7 derivation calculator, one switch each
(`evidence/r7/CS7-derivation-calculator.py` `RULES`):

| CS7 rule | Pack rule |
|---|---|
| `H_VER_UPSTREAM` | R-VER-1′ checks under pinned keys |
| `H_VER_BINDS_CANDIDATE` | R-VER-1′ / `34` R-CON-2 |
| `H_REG_RECORDS_FIRST_HAND` | R-REG-3 (d) |
| `H_REG_UPSTREAM` | R-REG-3 (a), (c″) |
| `H_REG_ENV_QUORUM` | `33` R-BENV-7″ |
| `H_REP_ENV_REASSEMBLE` | `33` R-BENV-4″, R-REP-2′ |
| `H_ENV_LOCK_IN_SOURCE` | `33` R-BENV-2″, R-BENV-3″ |
| `H_REG_CONTENT_FIRST_HAND` | R-REG-3 (g), `34` R-CON-1 |
| `H_REG_OWN_REPRODUCTION` | R-REG-3 (f) |
| `H_REP_BY_DIGEST`, `H_REP_FIRST_HAND` | R-REP-2′, R-REP-3 |
| `H_SIGN_REPRODUCE` | `05` §7 rule 2 |
| `H_PUB_REGISTRATION_RESTRICTORS` | R-PUB-1′ |
| `V_QUORUM`, `V_CONFLICT`, `V_OP9D_DIGEST` | R-REP-4′, R-REP-5′, `25` AP-6 |
| `V_VERIFICATION_COUNT`, `V_CANDIDATE_BINDING`, `V_REJECTED` | R-VER-2′, `25` AP-5 |
| `V_SUPPLIER_PINNED_KEYS`, `V_SUPPLIER_PROVENANCE`, `V_ENV_DIVERSITY`, `V_TOOLCHAIN_DIVERSITY` | `33` R-BENV-1″, R-BENV-5″, R-BENV-6″ |
| `V_FINAL_THRESHOLD_2` | `05` KS-15 |

An implementation or process that deviates from any of them changes the minimal sets, and the owner re-runs the calculator
(FD-3). `29` §4 names, for each rule, the calculator mutation or the executed scenario that fails when it is removed.

## 10. Minimum capability sets (computed for CP-1)

Atoms: `pipeline` (release CI input); `insider` (route I); `vp1`, `vp2` (verification processes); `va1`, `va2` (verification
keys); `cust1`, `cust2` (registration custodians); `regk1`, `regk2` (registration keys); `rp1`…`rp3` (reproducer processes);
`repk1`…`repk3` (reproducer keys); `tsk1`, `tsk2` (trust-state keys); `rck` (release-candidate key); `rfk1`, `rfk2`
(release-final keys); `transport` (withholding at the victim); `repo` (the repository writer delivers a release); `fcpub` (the
trust-state publication process); `src1`, `src2`, `desig1`, `desig2`, `op1src` (first contact, `32` §9); `pinprov` (a pin
provisioner under the repository writer's control, RS-4); `mirror`. A process compromise implies its key.

Victims: **P1** (anchored by a confirmation or pin naming the state, made before the compromise); **P1A** (the same anchoring
event made after it); **P2** (in-gate state codes from both sources); **CIR** (CI runner with record and pin); **FA** (first
admission); **RA_held**, **RA_unheld** (re-admission over a store that holds, or predates, the revocation).

**Malicious bytes for a genuine registration (G_BYTES):**

<!-- CS7:BEGIN CP-BYTES -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: malicious bytes for a genuine registration (CP-1) |
|---|---|
| P1 | {2 registration custodians, 3 reproducer processes} |
| P1A | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, src2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, desig1}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig2, op1src} |
| P2 | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, src2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, desig1}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig2, op1src} |
| CIR | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, pinprov} |
| FA | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
| RA_held | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
| RA_unheld | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
<!-- CS7:END CP-BYTES -->

**Malicious source faithfully built (G_SRC):**

<!-- CS7:BEGIN CP-SRC -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: malicious source faithfully built (CP-1) |
|---|---|
| P1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck} |
<!-- CS7:END CP-SRC -->

**Malicious named build inputs (G_INPUTS):**

<!-- CS7:BEGIN CP-INPUTS -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: malicious named build inputs (CP-1) |
|---|---|
| P1 | {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck} |
<!-- CS7:END CP-INPUTS -->

**Toolchain and environment:** `33` §6. **Registered content:** `34` §4. **First admission:** `32` §9.

**Invariants** (every configuration; 0 failures, `22` §1):
- **INV-BYTES:** every other G_BYTES set contains at least 2 reproducer compromises.
- **INV-SRC:** every non-residual G_SRC and G_INPUTS set contains two verification compromises and either the registration
  threshold or pipeline input.
- **INV-MIRROR:** the mirror appears in no set.
- **INV-ONE:** no key-theft-only set has at most one key; residual and first-contact root sets are excepted.
- **INV-RF:** `release-final` and `release-candidate` keys, pipeline, trust-state keys and delivery never select content.

## 11. Implementation requirements (product source is not changed by this revision)

| ID | Requirement | Acceptance test |
|---|---|---|
| IR-REP-1 | The production build reads provenance only from the registered source. `runtime/build.rs` today falls back to `git rev-parse HEAD` when no release manifest is present (line 73); the production profile MUST NOT. | RT-133 |
| IR-REP-2 | The normative build profile remaps source, Cargo home and toolchain home paths, fixes flags and target features, and links statically and self-contained. | RT-133 |
| IR-REP-3 | Bit-for-bit reproducibility of `gov` and `gov-admit` across two independent supplier classes and two independent toolchain lineages is shown before a target is certified (CC-1…CC-5). | RT-133, RT-194 |
| IR-REP-4 | `gov trust draft-registration` implements R-REG-3 (a)–(h) and refuses without their evidence; `gov trust draft-policy --derivation` runs CS7 for CP-1 and refuses a non-conforming draft. | RT-130, RT-131 |
| IR-REP-5 | Environment tooling implements `gov-envmanifest/1` and `gov-envassemble/1` deterministically and signs `environment-reproduction.v2+json` (`33`). | RT-160, RT-161, RT-186 |
| IR-REP-6 | Source identity v2 is computed from Git objects in `gov`, `gov-admit` and the ceremony tooling, with the refusals of §4.1. | RT-172 |

## 12. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-S1 | Reproducer compromise at the quorum with the registration custodians (processes), or the reproducer, registration and trust-state thresholds of keys with a currency or publication input | §10 CP-BYTES | RT-131; CS7 |
| TB-S2″ (TA-12, TA-12′, TA-12″) | Both toolchain lineages or the compiler source; both supplier classes or hidden common provenance | `33` §6 CP-TOOLCHAIN, CP-ENV | CS7; ENV7 T3 |
| TB-S3 (TA-10′) | Reproducers, environment reproducers or registration custodians under common custody | procedural; ceremony record | — |
| TB-4 (route I) | An insider change accepted by honest but deceived verification | process; two independent records | — |
| TB-4′ (TA-11) | Two compromised verification processes plus pipeline input | §10 CP-SRC; `34` §4 | CS7 |
| AV-S1 | One reproducer key forces `REPRODUCTION_CONFLICT` for one release (availability) | remedy: registration revocation of the forged reproduction (R-REG-11) | FA7 S5 |
