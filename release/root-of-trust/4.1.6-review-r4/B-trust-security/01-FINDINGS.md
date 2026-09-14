# 01 — Findings (review r4 B, trust and security)

Revision reviewed: RoT-1 revision 4, `bca05a7e2c2791126fde1d3d812facdaa45b2e45` (`release/root-of-trust/4.1.6/`,
`spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`). Reviewer: AR-0006, role `rot-reviewer-trust-security`.
This reviewer does not issue the architecture verdict.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV4-B-H1, RV4-B-H2, RV4-B-H3 |
| MEDIUM | 4 | RV4-B-M1 … RV4-B-M4 |
| LOW | 7 | RV4-B-L1 … RV4-B-L7 |
| INFO | 1 | RV4-B-I1 |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | the real legacy 4.1.5 binary as a stand-in consumer or command runner, real Git, or the pack's own checker (`constitutional-surface/csi_check.py`, unmodified) |
| **computed** | the architect's own rule functions (`evidence/P4r4-trust-state-model.py`, loaded unmodified: `evidence/RV4-B-arch-functions.py`) or this review's independent model (`evidence/RV4-B-M-reference-model.py`, written from the text) |
| **design** | pack text at `bca05a7` |
| **code** | 4.1.5 runtime, unchanged since `da9c851` |

"A-nn" means held-out attack RV4-B-A-nn (`02-HELDOUT-ATTACKS.md`). File names are under `evidence/`.

No CRITICAL finding: the compiled root chain, purpose-bound statements and the single authentication boundary remain
non-circular for subsequent binaries and releases.

---

## RV4-B-H1 — HIGH — A production binary's bytes, or its source, rest on one threshold-1 attestation: honest custodians re-check signatures, not the decision, so one stolen `build-attestation` key (or one `verification-attestation` key) plus release-pipeline input yields an accepted malicious binary

### Statement

1. **Who decides "these bytes are a build of the attested source".** Only the rebuilder, by signing `build-attestation`.
   - Threshold 1 (`05` §1); the OP-2 proposal is one rebuilder (`21` OP-2).
   - The two `release-artifact` custodians run `verify-artifact --stage custodian`: A1, A3, A4a, A4b, A6 (`25` §9;
     `05` §7 rule 6). A4a checks that a build attestation names this digest, TBM and source. They do not rebuild.
   - The trust-state publisher runs A1–A4b and A6 (`25` §9; `05` §7 rule 7). It does not rebuild.
2. **Who decides "this source was independently verified".** Only the verifier, by signing `verification-attestation`.
   - Threshold 1 (`21` OP-2 proposal).
   - Candidate and final signers "rebuild the unsigned payload from `git archive` of `release.source.release_commit`"
     (`05` §7 rule 2). That is reproduction, not legitimacy. Promotion requires an ACCEPTED attestation (`09` R-REL-6).
   - The rebuilder "rebuilds from that source and attests only when the binary digest and TBM digest are identical"
     (`05` §7 rule 6), so an attested malicious source is reproduced faithfully.
3. **Consequence.**
   - **Route B′:** {one `build-attestation` key, pipeline input}. The pipeline hands the custodians malicious bytes for
     the genuine attested source. The attacker signs the build attestation. Every honest downstream check passes, and
     `verify-artifact` accepts.
   - **Route S′:** {one `verification-attestation` key, pipeline input}. Honest candidate and final signers, rebuilder,
     custodians and publisher all act. The result is accepted unless the honest verifier's REJECTED attestation is held
     where A4b runs.
4. **Pack claims contradicted.**
   - `25` §7: route B "4 keys over 3 purposes, no pipeline control needed", and "No single key of any purpose, at any
     threshold, can mint an accepted production binary".
   - `05` §3 minimum-keys table and the sentence that follows it; `05` §1 `build-attestation` "nothing alone".
   - `25` TB-3; `00` §1 BC-3 row.
   - `21` OP-2 (S1): "route S needs the root threshold; the minimum becomes route B (4 keys over 3 purposes)"; OP-2
     "owner must know" item 2.

   The pack's own route S counts "control of the build input" as an available capability. Route B was evaluated without
   it.
5. **The conformance evidence encodes the defect.**
   - `VA4`'s "route B" row is, object for object, this attack. Its `world()` has the honest publisher sign TSS 11, and
     the artefact carries the custodians' own key ids. The only attacker-signed statement is the build attestation.
   - The row is an expected `ACCEPTED` "documented minimum set" labelled as needing four stolen keys.
   - RT-92, RT-115 and RT-127 (which follows `21`) would therefore pass an implementation with this defect.

### Evidence

- **computed** (architect's functions, `RV4-B-arch-functions.json` AF1):
  - custodian stage on the draft `PASS`; publisher stage `PASS`;
  - `verify_artifact` `ACCEPTED` on an anchored machine with a currency proof;
  - `identical_to_VA4_route_B_world: true`.
- **computed** (AF2): route S′ `ACCEPTED`. With the REJECTED attestation also held: `ARTIFACT_SOURCE_REJECTED`. Under
  OP-2 (S1): `ARTIFACT_SOURCE_UNREGISTERED`.
- **computed** (independent model, `RV4-B-M-reference-model.json` `BC_binary_capability_sets`): every subset of {rc, rf,
  va, va2, ba, ba2, ra1, ra2, ts, cs, pipeline}, with honest actors acting only on their stated checks.
  - **Malicious bytes:** minimal set {ba, pipeline} under OP-2 (S0), (S1), (S2) and (S3), with OP-4 yes or no and one
    rebuilder. {ba, ba2, pipeline} with two rebuilders. Without pipeline input: {ba, ra1, ra2, ts}, the pack's four keys.
  - **Malicious source, REJECTED verdict not held:** {va, pipeline} under (S0) and (S3); {va, va2, pipeline} under (S2);
    no set under (S1). With the REJECTED verdict held: no set.
- **design:**
  - `05` §7 rules 2, 3, 6, 7; `25` §5, §7, §9, TB-3; `07` §7 steps 4, 6–14;
  - `09` R-REL-6, R-ART-6; `21` OP-2, OP-4; `evidence/VA4-verify-artifact-source-scenarios.py` `world()`.

### Failure scenario

1. A7 steals the rebuilder's `build-attestation` token: one custodian, threshold 1.
2. A6 or A5 controls the binary build step (`07` §7 step 10), for example the CI job that produces release binaries.
3. The pipeline builds binary X from the genuine attested source S with a backdoored dependency.
4. The honest rebuilder reproduces S, gets a different digest, and attests nothing for X. The attacker signs a build
   attestation for X (digest X, the TBM of X naming S).
5. Both custodians run `--stage custodian`:
   - A1: the digest of X;
   - A3: the final verifies;
   - A4a: an attestation for X is present;
   - A4b: S is attested;
   - A6: the TBM resolves.

   The check passes and they sign. The owner's `gov trust publish --stage publisher` passes, and TSS *m* references X.
6. Every machine with a currency proof accepts X through `verify-artifact`. X ignores E7, anchors and trust gates.

### Why HIGH

- **TCB compromise below the declared threshold.** It needs one threshold-1 key.
- **Owner requirement.** HO-0001 §3.3 requires that "a single lower-threshold release key must not be able to mint a
  malicious binary".
- **Same shape as RV3-H3:** one threshold-1 key plus pipeline input yields the TCB.
- **Owner options.** The OP-2 (S0)–(S3) consequence statements are false (BC-4).
- **Oracle.** The mandated oracle expects the defect.

### Correction direction (architectural)

1. **No single threshold-1 decision fixes the bytes or the source at verify time.**
   - **Bytes:** require independent reproduction by at least two parties whose signatures `verify-artifact` checks (a
     compiled `build-attestation` threshold ≥ 2 with distinct custody), or make the custodians' own reproduction a
     verifier-checked fact rather than a procedure.
   - **Source:** do not let one verification key decide it under the proposed option. Either make root-registered source
     (or verification threshold ≥ 2) the minimum, or make the REJECTED-verdict path independent of the pipeline.
2. **Re-derive every route's minimum capability set** with pipeline input and honest custodians acting on their stated
   checks. Restate `25` §7, `05` §1 and §3, TB-3, `21` OP-2 and OP-4.
3. **Replace the VA4 "documented minimum" rows** with distinguishing scenarios.

---

## RV4-B-H2 — HIGH — First-binary acceptance is outside the rules that protect later binaries: tooling checks A2–A6 only, build-from-source compares a value the binary prints about itself, and the migration plan verifies each consumer's first RoT-1 binary with that same binary

### Statement

1. **Where TA-1 comes from.** TA-1 holds when "the binary was accepted by `verify-artifact` (`25` §5) or built from
   source at a verified tag" (`01` §4). "Verified tag" is not defined. `06` §2 step 6 and `25` §6 give three ways to
   obtain the first binary on a machine:
   - **(b) Independent tooling.** It verifies A2–A6 with root metadata whose id matches the channel. It has no A7, no A8
     (negative set: revocations, REJECTED or WITHDRAWN) and no A9 (inclusion anchor, currency proof). The channel
     publishes the state fingerprint of every TSS (`06` §2 step 2), but (b) does not use it.
   - **(c) Build from source.** It builds "at the final tag" and compares `gov version --trust` (lineage id and TBM
     digest) with the channel and the build attestation.
     - The compared value is printed by the binary under verification (`09` R-ART-4).
     - The TBM (`25` §4; `schemas/trust-base-manifest.schema.json`) has no field that binds the code.
   - **(a)/(iii) An already trusted `gov`.** It needs an earlier RoT-1 binary.
2. **Every existing consumer is a first-binary case.** `11` Phase 4 has legacy-layout consumers run "`gov trust
   verify-artifact` for the binary". No earlier RoT-1 binary exists on those machines, so the verifier is the binary
   under verification. That is self-validation, which rule (16) forbids.
3. **Consequences, with zero keys.**
   - **Revoked binary.** A transport or repository adversary (A5, A9) serves a genuine binary revoked for a security
     defect, together with the TSS that referenced it and without the revocation. Path (b) accepts it.
   - **Remediated malicious binary.** After a binary-key compromise is remediated per `05` §9, a machine using (b) with
     root v1 metadata (lineage id equal to the channel's) accepts the known-malicious binary. The remediation removes the
     keys in root N+1, revokes the digest, and keeps the `artifacts[]` reference in every later TSS.
   - **Moved tag.** A source controller (A1/A5) moves the tag or serves a modified tree. The binary built from it prints
     the genuine lineage and TBM digest, and path (c) accepts it.
   - **Self-verified first binary.** Each legacy consumer's first RoT-1 binary is accepted on its own verdict.

### Evidence

- **computed** (architect's functions, `RV4-B-arch-functions.json` AF3): independent tooling A2–A6 on the revoked binary:
  `PASS (A2–A6)`. `verify_artifact` on a machine holding the revoking TSS: `ARTIFACT_REVOKED`.
- **computed** (independent model, `FB_first_binary`):
  - FB1: tooling `PASS`, full `verify-artifact` `ARTIFACT_REVOKED`.
  - FB2 (remediated compromise): tooling with root v1 `PASS`; with root v2 `ARTIFACT_BUILD_UNATTESTED`.
- **executed** (`RV4-B-confinement-and-first-binary.json` part B):
  - `tbm_schema_has_code_or_binary_digest_field: false`;
  - a planted binary reports the genuine lineage and TBM digest, so `procedure_c_as_written_passes: true`;
  - `binary_sha256_equals_attested_artifact_digest: false`.
- **design:** `06` §2 step 6; `25` §4, §6, TB-1; `01` TA-1; `09` R-ART-4, R-BOOT-4; `11` Phase 4; `05` §9; `15` rule (16).

### Failure scenario

1. Binary 4.1.6-b1 is found to skip E7 under a condition. The owner revokes it (TSS 9) and publishes b2.
2. A new team member, or a new CI runner image, obtains its first `gov` by the documented independent-tooling path. An
   attacker on the download path serves b1 with TSS 6, which references it, and withholds TSS 9 and the revocation.
3. The tooling checks A2–A6: signatures, the build attestation, the attested source, the TSS reference and TBM
   resolution. Every check passes.
4. The machine's TCB is now the revoked b1, and every later `verify-artifact` on that machine is run by b1.

### Why HIGH

- **The recurring class, with zero keys.** Attacker-selected stale signed state (a revoked TCB) becomes a current trusted
  fact on the first-install machine class of HO-0001 §3.2.
- **Circular chain.** Path (c) and the Phase 4 path break the non-circular chain HO-0001 §3.3 requires, at the root of
  every later acceptance.

### Correction direction (architectural)

1. **Tooling path.** Define first-binary acceptance as the full `verify-artifact` semantics (A1–A9), executed by tooling
   independent of the binary: an inclusion anchor from the channel's state fingerprint, the anchored chain's negative set,
   and a currency proof.
2. **Build-from-source path.** Bind the checked-out tree to the attested `source_tree_digest`, and the built binary's
   SHA-256 to the build attestation and artefact statement. Never compare a value the binary reports about itself.
3. **Migration.** The migration plan must never accept a binary on its own verdict.
4. **Assumption text.** Restate TA-1 and `25` §6.

---

## RV4-B-H3 — HIGH — Pinned constitutional content is registered per leaf with no release binding: once a Trust Policy keeps an earlier release's digest beside a fixed one, a threshold-1 `release-final` key issues a higher-sequence release that restores the earlier content; every check passes and no detector sees it

### Statement

1. **What registration means.**
   - `23` §3.2: for `pinned` leaves "the TPS registers permitted digests", as a list per leaf.
   - `pinned_file` rules (schemas, skills, adapters, command contract, enforcement map, MCP registry) register digests
     per path.
   - `19` §5.2: the effective pinned value is the root-kernel value if its digest is registered in the effective TPS.
     E7 judges pins against the TPS the release names.
   - `23` §7 treats "removal of a registered digest" as a strengthening, so registrations with several digests are
     anticipated.
2. **Retention is the steady state.** The architecture relates no digest to a release. An installed 4.1.6 release stays
   eligible against its named TPS, but at a newer TPS that dropped its digest its pinned values become
   `SURFACE_VALUE_UNAVAILABLE` at their decision points (`19` §5.2). Owners therefore keep the earlier digest beside the
   fixed one. CS-2 requires a TPS for every pinned change and says nothing about retention.
3. **The attack.** A `release-final` thief signs a final whose content is 4.1.7's, except that one fixed pinned leaf has
   4.1.6's registered value. Nothing detects it:
   - E7 passes;
   - `reductions` does not examine pinned digests (`csi_check.run_reductions` compares leaf classes, floors, memberships,
     presence, precedence and overlay writability);
   - a pinned leaf has no strength direction, so the project-strength vector (`26` §6) records nothing;
   - E10 does not apply to a higher sequence;
   - the `framework_update` gate lists no weakening, and Git-delivered use has no gate.
4. **Blast radius mis-stated.** `05` §1 and `21` OP-2 say `release-final` "sets the kernel value of the 52
   `project_tunable` and 32 `release_bound` leaves". They omit its choice among registered pinned and `pinned_file`
   digests.

### Evidence

**executed** (`RV4-B-surface-probes.json` part P), with the pack checker and the real 4.1.5 binary as stand-in consumer,
`kernel trust verified: true` in both consumers:

| Check | Result |
|---|---|
| Mixed kernel (old `aws-access-key` regex plus a new registered member) under a TPS retaining both digests | checker exit 0 |
| Same kernel under a TPS registering only the fixed digest | exit 3 |
| `reductions`, retaining the old digest | exit 0 |
| `reductions`, re-adding a superseded digest | exit 0 |
| Leaf direction | `none` |
| Consumption: release with the fixed pattern | a file containing an `ASIA…` key is excluded (`secret_content`) |
| Consumption: mixed release | the same file is indexed and returned by `memory query` |

**design:** `23` §3.2, §6.3, §7, CS-2; `19` §5.2, §6 E7, E10; `26` §6; `05` §1; `21` OP-2.

### Failure scenario

1. 4.1.7 fixes `SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex` to catch temporary (`ASIA`) keys.
   TPS v2 registers the new digest and keeps the old one so that 4.1.6 installs keep working.
2. A `release-final` thief signs final 4.1.8-x, at a sequence above 4.1.7, with the old regex. A2 commits it.
3. On every machine holding TPS v2, 4.1.8-x is an eligible policy root. Temporary AWS keys are indexed and retrievable by
   agents. Recorded machines report no `PROJECT_STRENGTH_WEAKENED` and no downgrade.

### Why HIGH

- **The R2-H1 / RV3-H1 class.** Authentic, eligible content confers weaker effective secret handling while every check
  passes. HO-0001 §3.1 and G11 require that values never move down except by a computed, declared, per-project-gated
  lowering.
- **Trigger.** One threshold-1 key, plus A2, plus a routine owner TPS.
- **Harm.** Executed on a real consumer.

### Correction direction (architectural)

1. **Bind registrations to releases.** Bind `pinned` and `pinned_file` registrations to release identity: a per-release
   registered digest set, or a sequence range per digest. Evaluate E7 and effective values against the set registered
   for that release.
2. **Treat retention as a reduction.** Retaining or re-adding a superseded digest is a computed reduction, with
   `lowering_history` and the per-project gate.
3. **Restate the blast radius** of `release-final`.

---

## MEDIUM

Every MEDIUM is carried with a bound acceptance test in `04-CARRIED-REQUIREMENTS.md`. None needs an architecture change,
for the reason given in each row.

| ID | Statement | Evidence | Failure scenario | Why MEDIUM, not blocking | Correction direction |
|---|---|---|---|---|---|
| **RV4-B-M1** | **Write confinement is a deny list, so a `gov`-run repository command plants code that later runs unconfined as the account.** **Rule.** `24` §3.5 (3) and `09` R-CONF-1 deny writes only to the pin locations, the VTS, `governance/trust/**`, the occupation entries and the transaction area. **What stays writable.** Executables on `PATH` (including `gov` itself when installed in a user directory), shell start-up files, and the governed repository's `.git/hooks` and `.git/config`. **Effect.** Code planted there runs later, unconfined, as the account (A3). It then forges VTS human anchors (with a P1 currency proof) and trust-gate confirmations (RS-3, TG-2), or replaces the TCB. The integrity predicate covers pin files but not the binary that evaluates them. **Claims contradicted.** `28` §2.2 "removes the governed account from the anchor's writers"; `27` §3.3 (2) "an agent path that runs through `gov` cannot create a confirmation or a decision pin" holds only for direct writes. | **executed** `RV4-B-confinement-and-first-binary.json` part A: the 4.1.5 `gov verify product` child writes `$HOME/.local/bin/gov`, `.bashrc` and `.git/hooks/post-checkout`; none is in the deny list; the next login shell runs the planted `gov`, which writes a VTS anchor and a `framework_update` confirmation; `git checkout` runs the hook. **computed** model matrix: 27 rows admit revoked state once A3 forges the VTS. | (1) A2 commits `tests.product_test_command`. (2) A developer runs `gov verify product`; the child is confined, and `~/.local/bin` is writable. (3) A later shell runs the planted `gov`. (4) The planted code records a local confirmation, and `update --apply` of an A2-chosen weaker eligible release proceeds. | **Bounded by existing scoping.** Code running as the account is already scoped as same-user (RS-3, TG-2) for paths outside `gov`, and system pins in `/etc/gov` remain outside A3. **Carriable.** Default-deny confinement plus a TCB-location predicate is a bound rule. | Confinement allow list (working tree without `.git`, a per-command temporary directory); deny `PATH` directories, the running binary and its ancestors, and shell start-up files; C3 and trust-gate confirmation refuse when the running binary or an ancestor is writable by the effective uid. |
| **RV4-B-M2** | **OP-7 (c): the witness service's input and custody are unspecified.** **Input.** `05` §7 rule 10 says the service "signs a witness only for the TSS the owner published most recently", and `07` §7 step 16 says "naming the newest TSS". Neither says how the service learns which TSS that is. If it reads the repository, the Git host or a bundle, A2/A5 choose the witnessed state without any key compromise. **Custody.** Two keys in one scheduled service satisfy "≥ 2 distinct keys", so one service compromise reaches the consequence stated for keys at threshold. **Owner option.** The `21` OP-7 (c) "within `witness_max_validity_hours` of the newest honest witness" bound is exact only when the service's input is independent. | **design** `05` §7 rule 10; `07` §7 step 16; `24` §3.3, §10 RS-5; `21` OP-7 (c). **computed** model: 9 RS-5 rows (witness keys at threshold) admit revoked state and C3. | (1) The witness service polls the Git host for the newest TSS. (2) A5 serves TSS 5 and withholds TSS 9. (3) The service witnesses TSS 5. (4) Stateless runners reach `WITNESSED` and C3 on revoked state. | OP-7 (c) is not the proposal. The fix is a bound custody and input rule. | The witness service takes the state fingerprint from the owner's signing ceremony or the independent channel, never from the repository or the transport. Witness keys at the C3 threshold need independent custodians, or the one-custody consequence is stated. |
| **RV4-B-M3** | **RS-2's rollback bound does not exist under the proposed OP-7 (a), nor on stateless runners.** **The bound.** `24` §10 RS-2: "clock rollback below `clock_high_water` makes clock-based proofs and pins unusable". **Why it never fires.** `clock_high_water` rises only from `freshness-witness` statements (`24` §8), and those exist only under (c). Under (a), (b) and (d) it never rises, and a clean CI runner has no VTS at all. **Effect.** A clock set back makes an expired pin valid and its P1 proof current: C3, and `verify-artifact` of a revoked binary. | **computed** model LB3 (OP-7 (a): `allowed` C0–C3, `bound_applies: false`); matrix: 23 rows with a clock adversary. | A CI runner's clock is set back 395 days. A pin provisioned 400 days before true time is honoured with a P1 proof, and `verify-artifact` accepts revoked B7. | TA-7 is a declared assumption. The defect is a mis-stated bound, not a new trust input. | Restate RS-2 and the `21` OP-7 (a) consequence: under (a), (b) and (d), and on stateless runners, pin validity and the C3 window rest on an unchecked clock. Add RT-56/RT-102 cases. |
| **RV4-B-M4** | **Computed weakening needs a recorded vector, so a release-signed migration's weakening on a machine without a record is committed ungated.** **Rule.** `19` §9 evaluates "the project's **recorded** strength vector". `26` §6 (1) records it only at install transactions. **Gap.** A machine with no record (a fresh clone, or a CI runner running `update --apply`) has nothing to evaluate. **Reach.** `REPOSITORY_CONTRACT.paths` is migration-writable, and a registered target can weaken (P1r4 M5: `**/.env*` indexed). On such a machine the weakening needs no `weakening` gate and the `framework_update` gate lists none. The committed overlay then becomes every fresh clone's configuration (LR-4). | **design** `19` §9; `26` §6 (1), (4); `23` §11.3. **executed** P1r4 part C, reproduced byte-identical (`ARCH-RERUN-LOG.json`): the M5 target passes the whitelist. | A `release-final` thief ships a migration that marks `product/customers/**` indexable. A CI runner without a record applies the update and commits the overlay. Fresh clones index customer data. | Recorded machines still report the weakening, and the fix is a bound rule. | When no record exists, compute requirements from the pre-transaction effective policy and overlay before applying migrations. |

## LOW

| ID | Statement | Evidence | Carried as |
|---|---|---|---|
| RV4-B-L1 | The wildcard `informational` rule `ROLES.authority_levels.*.*` classifies any new key under it. **Effect.** A new key under an authority level, and a new level L6, both pass the checker. That is an exception to default deny. No 4.1.5 runtime reader exists, so only the build-time consumer register would catch a future reader. | executed `RV4-B-surface-probes.json` U01, U02 (exit 0); code: no reader of `ROLES.authority_levels` | CR4-B-05 |
| RV4-B-L2 | The decision rule contradicts the currency-proof definition. **Table.** `24` §4.3, and the §5.2 M2 table, allow C3 for `WITNESSED` at the C3 threshold. **Definition.** `24` §4.4 says a currency proof exists "iff the machine is `ANCHORED` and `KNOWN`". **Consumer.** `25` A9 requires a currency proof. | computed model LB2 | CR4-B-06 |
| RV4-B-L3 | A P1 proof's label is inexact. `24` §4.4 says a proof "establishes that *n* was the published state as of the proof time". Under P1, *n* may be a descendant of the anchor issued after the proof. With a trust-state key thief, C3 proceeds on a statement that did not exist at the proof time. The window bounds it, and it adds no revocation bypass beyond RS-1b. | computed model LB1 (`statement_existed_at_proof_time: false`, `C3_allowed: true`) | CR4-B-07 |
| RV4-B-L4 | The accepted-TBM high-water has two gaps. **Stateless runners.** It is absent there, so an older genuine unrevoked binary is accepted as an upgrade on a clean CI runner; `25` §7 states the refusal universally. **First-run recording.** It is unspecified ("first run of a verified binary"). A non-resolving TBM recorded at first run makes every later genuine binary `BINARY_T0_ROLLBACK`, and no reset exists. | computed model AT1 (`ACCEPTED` on the runner, `BINARY_T0_ROLLBACK` with the high-water); AT2 under both readings | CR4-B-08 |
| RV4-B-L5 | Decision pins have no maximum validity. `schemas/trust-decision-pin.schema.json` bounds nothing, and the TPS `bootstrap` has no cap, unlike state pins. Non-C3 kinds (`weakening`, `project_strength`, `owner_constitutional_file`), and `init_ack` for project `*`, can be approved indefinitely. | design `27` §3.2; schema | CR4-B-09 |
| RV4-B-L6 | A4a and A4b rely on attestations without consulting the negative set. A8 lists only the artefact, final and candidate. The `05` §9 verification-attestation playbook revokes attestations, but a binary accepted through a revoked attestation stays acceptable until that binary is revoked individually. | design `25` §5 A4a, A4b, A8; `05` §9 | CR4-B-10 |
| RV4-B-L7 | The OP-4 consequence text (`21` lines 132–134) is duplicated and garbled ("…malicious binary under (S0), (S2 with one verifier key stolen: no) and (S3 without the certification key: no)…"), and its key counts inherit RV4-B-H1. | design `21` OP-4 | CR4-B-11 (option text) |

## INFO

| ID | Statement |
|---|---|
| RV4-B-I1 | The acting role remains caller-declared (RV3-I1, V-L5), unchanged. No trust gate depends on it (`27` §5). |
