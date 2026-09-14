# 10 — Consolidated findings (review r4 synthesis D), CRITICAL to LOW

Revision reviewed: RoT-1 revision 4, `bca05a7e2c2791126fde1d3d812facdaa45b2e45`. Panel: reviewer B `152e68e`, reviewer C
`c6b8ba9`. Synthesis run AR-0008. D-0008 and ARCH-0002 remain PROPOSED; nothing here approves them.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV4-H1, RV4-H2, RV4-H3 |
| MEDIUM | 7 | RV4-M1 … RV4-M7 |
| LOW | 10 | RV4-L1 … RV4-L10 |
| INFO | 1 | RV4-I1 |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | the real legacy binaries (4.1.5 unless stated), real Git, or the pack's checker `constitutional-surface/csi_check.py`, unmodified |
| **computed** | the architect's own rule functions (`evidence/P4r4-trust-state-model.py`, loaded unmodified or with exactly one line changed where a mutant is named), or reviewer B's independent model (reproduced byte-identical) |
| **design** | pack text at `bca05a7` |
| **code** | 4.1.5 runtime and CLI, unchanged since `da9c851` |

Every panel probe cited was re-run by this review (`D-synthesis/01-REPRODUCTION.md`). "B-Axx", "C-Axx" and "D-Axx" mean
RV4-B-Axx (`B-trust-security/02-HELDOUT-ATTACKS.md`), RV4-C-Axx (`C-compat-transaction/02-HELDOUT-ATTACKS.md`) and
RV4-D-Axx (`D-synthesis/03-HELDOUT-ATTACKS-RV4-D.md`).

**No CRITICAL.** For every binary after a machine's first accepted binary, the compiled root chain, purpose-bound
statements and the single authentication boundary remain non-circular (VA4, P4r4 and B's model reproduced). The
first-binary defect (RV4-H2) is HIGH, not CRITICAL, because the documented tooling path still authenticates genuine
signatures and the build path is one of three documented paths; it is the recurring class on one machine class, not a
failure of the chain for every machine.

---

## RV4-H1 — HIGH — The two decisions that make a binary the TCB each rest on one threshold-1 attestation key: with release-pipeline input, one `build-attestation` key (or one `verification-attestation` key) yields an accepted malicious production binary through honest custodians

**Origin.** RV4-B-H1, extended by D-A07. **Adjudication:** CONFIRMED HIGH.

### Statement

1. **Bytes.** "These bytes are a faithful build of source S" is decided only by `build-attestation`, threshold 1 (`05`
   §1; `21` OP-2 proposal: one rebuilder).
   - The two `release-artifact` custodians run `verify-artifact --stage custodian`: A1, A3, A4a, A4b, A6 (`25` §9,
     `05` §7 rule 6). A4a checks that a build attestation names the digest; nobody downstream rebuilds.
   - The publisher runs A1–A4b and A6 (`05` §7 rule 7). It does not rebuild.
   - Under OP-2 (iii) the root co-signers "run the same stage and compare the source with the owner's verification
     record" (`05` §7 rule 6, `21` OP-2). For malicious bytes claimed as a build of the genuine attested source, that
     comparison matches, so (iii) adds no protection against this route (D-A07).
2. **Source.** "S is the independently verified source" is decided only by `verification-attestation`, threshold 1
   (proposal). Honest release signers reproduce the payload from the commit they are given (`05` §7 rule 2); that is
   reproduction, not legitimacy.
3. **Consequence.**
   - Route B′ = {one `build-attestation` key, pipeline input}: accepted under OP-2 (S0), (S1), (S2), (S3), with OP-4
     yes or no, and under `release-artifact` (i), (ii) and (iii). Two rebuilders raise it to two keys plus pipeline
     input; no offered option raises it to the `release-artifact` or root threshold.
   - Route S′ = {one `verification-attestation` key, pipeline input}: accepted under (S0) and (S3) unless the honest
     verifier's REJECTED attestation is held where A4b runs; two keys under (S2); refused under (S1).
4. **Pack claims contradicted:** `25` §7 ("route B: 4 keys over 3 purposes, no pipeline control needed"; "No single key
   of any purpose, at any threshold, can mint an accepted production binary"); `05` §1 (`build-attestation`: "nothing
   alone") and §3 minimum-keys table; `25` TB-3; `21` OP-2 (S0)–(S3) minimum sets and "owner must know" item 2; `00` §1
   BC-3 row. The pack's own route S counts "control of the build input"; route B was evaluated without it.
5. **The oracle encodes the defect.** VA4's "route B" row is object-for-object this attack and expects `ACCEPTED` as a
   "documented minimum set" labelled as four stolen keys. RT-115 (g) and RT-127 follow that row, so an implementation
   with this defect passes them.

### Evidence

- **computed** (architect's functions; reviewer B's `RV4-B-arch-functions.py`, reproduced byte-identical): AF1 custodian
  stage `PASS`, publisher stage `PASS`, `verify_artifact` `ACCEPTED`, `identical_to_VA4_route_B_world: true`. AF2
  `ACCEPTED`; with the REJECTED attestation held `ARTIFACT_SOURCE_REJECTED`; under (S1) `ARTIFACT_SOURCE_UNREGISTERED`.
- **computed** (reviewer B's independent model, reproduced byte-identical): `BC_binary_capability_sets` minimal sets as
  stated in 3.
- **design** `05` §1, §3, §7 rules 2, 3, 6, 7; `25` §5, §7, §9, TB-3; `07` §7 steps 10–14; `21` OP-2, OP-4; VA4 `world()`.

### Failure scenario

The rebuilder's `build-attestation` token is stolen (A7). The attacker controls the job that produces release binaries
(A5/A6) and hands the custodians binary X built from the genuine attested source with a backdoored dependency. The
attacker signs a build attestation for X. Both custodians' A1/A3/A4a/A4b/A6 pass; the owner's publisher stage passes;
TSS *m* references X. Every machine with a currency proof accepts X, and X ignores E7, anchors and trust gates.

### Why HIGH

TCB compromise with one threshold-1 key plus pipeline input: the same shape as RV3-H3 and R2-H3. HO-0001 §3.3: "A single
lower-threshold release key must not be able to mint a malicious binary." The owner-option consequence statements for
OP-2 and OP-4 are false.

### Class and novelty

**Narrowed remainder of R2-H3 / BC-3.** Revision 4 removed `release-final` from the choice of source (RV3-H3 as stated is
closed: VA4 `RELEASE_IDENTITY_MISMATCH(source)` reproduced). The threshold-1 decision moved to the attestation purposes.
**Unestablished invariant:** each fact that makes a binary the TCB — faithful build of S, and S legitimately verified —
is established by independent parties at a verifier-checked threshold at least as strong as the authority the binary
carries; a downstream signature counts toward that threshold only if its signer attests a fact it established itself.

---

## RV4-H2 — HIGH — First-binary acceptance is outside the anchor, negative-set and currency rules and compares values the candidate binary prints about itself; every first-install trust ceremony runs on that unaccepted binary

**Origin.** RV4-B-H2, extended by D-A04. **Adjudication:** CONFIRMED HIGH.

### Statement

1. **Three documented first-binary paths** (`06` §2 step 6, `25` §6, `01` TA-1):
   - (b) independent tooling verifying A2–A6 with root metadata whose id matches a channel. No A7, no A8 (revocations,
     REJECTED, WITHDRAWN), no A9 (inclusion anchor, currency proof). The channel publishes the current state fingerprint
     (`06` §2 step 2); path (b) does not use it.
   - (c) build from source "at the final tag" and compare `gov version --trust` (lineage and TBM digest) with the channel
     and the build attestation. The compared value is printed by the binary under test (`09` R-ART-4). The TBM carries no
     code digest, and the procedure compares neither the built binary's SHA-256 with the attested artefact digest nor the
     checked-out tree with the attested `source_tree_digest`.
   - (a) an already trusted `gov`, which a first-install machine does not have.
2. **Migration.** `11` Phase 4 has every legacy consumer run `gov trust verify-artifact` for its first RoT-1 binary with
   that binary: self-validation, which D-0008 rule (16) forbids.
3. **Ceremonies (D-A04).** On a first-install machine, `gov trust confirm-root` (OP-6 (a)), `gov trust confirm-state`, the
   in-gate typed state fingerprint (the P2 currency proof) and trust-gate confirmations are all evaluated by the binary
   whose authenticity is in question. A binary that is not genuine displays the genuine lineage id and accepts the typed
   values. TA-5 therefore establishes nothing until TA-1 holds; `21` OP-6 states no such dependency.
4. **Consequences (zero keys).**
   - A transport or repository adversary serves a genuine binary revoked for a security defect, with the TSS that
     referenced it and without the revocation: path (b) accepts it.
   - After a remediated binary-key compromise (`05` §9: root N+1 removes the keys, the digest is revoked, the artefact
     reference kept), path (b) with root v1 metadata (lineage id equal to the channel's) accepts the known-malicious
     binary.
   - A source-host adversary moves the tag or serves a modified tree; the built binary prints the genuine lineage and TBM
     digest; path (c) accepts it.

### Evidence

- **computed** (architect's functions, B's AF3, reproduced): tooling A2–A6 `PASS (A2–A6)` on the revoked binary;
  `verify_artifact` on a machine holding the revoking TSS `ARTIFACT_REVOKED`.
- **computed** (B's model `FB1`, `FB2`, reproduced): tooling accepts the revoked and the remediated-malicious binary.
- **executed** (B's `RV4-B-confinement-and-first-binary.py` part B, reproduced byte-identical):
  `tbm_schema_has_code_or_binary_digest_field: false`; a planted binary reports the genuine lineage and TBM digest;
  `procedure_c_as_written_passes: true`; `binary_sha256_equals_attested_artefact_digest: false`.
- **design** `06` §2 step 6, §3; `25` §4, §6, TB-1; `01` TA-1, TA-5; `09` R-ART-4, R-BOOT-4; `11` Phase 4; `15` rule (16);
  `21` OP-6.

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A machine must start by trusting some code that is not `gov` (tooling, a compiler) | core, accepted when stated as an assumption |
| That code checks signatures but not the published current state, so a revoked or remediated binary becomes the TCB | **not core**: the channel already publishes the state fingerprint; applying it as an inclusion anchor with the negative set removes the selection |
| A build compares a value the built binary prints about itself | **not core**: an externally computed digest removes it |
| Ceremonies establishing TA-5 run on the unaccepted binary | **not core**: ordering the ceremony after acceptance, or performing it with the independent tool, removes it |

### Why HIGH

Attacker-selected stale signed state (a revoked TCB) becomes the current trusted binary on the first-install machine
class of HO-0001 §3.2, with zero keys; paths (c) and Phase 4 make the chain circular at its root, contrary to HO-0001 §3.3.
Every later `verify-artifact` on that machine is run by the accepted binary.

### Class and novelty

**Narrowed remainder of R2-H2 / BC-2 at its intersection with R2-H3 / BC-3.** BC-2's trust-state rules hold (336-row model
reproduced); BC-3's source binding holds for binaries accepted by `verify-artifact`. The first binary on a machine is the
remaining instance; no earlier review attacked it (review r3 accepted TB-1). **Unestablished invariant:** every TCB
acceptance on a machine, including the first binary and every legacy consumer's first RoT-1 binary, applies the same
anchored, negative-set-checked and currency-proven decision as `verify-artifact`, over digests measured by code other
than the binary under test; no ceremony whose purpose is TA-5 runs before that acceptance.

---

## RV4-H3 — HIGH — Non-orderable constitutional registrations are not bound to releases: a Trust Policy that keeps a superseded digest lets a threshold-1 `release-final` restore superseded pinned content, member content or pinned files in a higher-sequence release, with no reduction, gate or detector

**Origin.** RV4-B-H3, extended by D-A02 and D-A06. **Adjudication:** CONFIRMED HIGH, class broadened.

### Statement

1. **Registration shape.** `pinned` leaves, whole keyed-collection members and `pinned_file` paths register a **list** of
   permitted digests per key or path (`23` §3.1, §3.2; draft inventory `digests: {key|path: [sha256…]}`). No digest is
   related to a release identity or sequence. `23` §7 treats removal of a registered digest as a strengthening, so
   multi-digest registrations are anticipated.
2. **Retention is forced.** At a TPS that drops an installed release's digest, that release's pinned value becomes
   `SURFACE_VALUE_UNAVAILABLE` and its decision points refuse (`19` §5.2). An owner who keeps existing installs working
   retains the superseded digest. `23` CS-2 presents per-release TPS ceremonies as operational cost only.
3. **The attack.** A `release-final` thief signs a final at a sequence above the fix whose content is the newer release's
   except one fixed target, which carries the superseded registered content. E7 passes; `reductions` does not examine
   registered digest sets; a pinned target has no strength direction, so the project-strength vector records nothing;
   E10 does not apply to a higher sequence; the `framework_update` gate lists no weakening; and Git-delivered use of a
   higher-sequence release needs no gate at all (`20` §9, `19` E10; D-A06).
4. **Breadth (D-A02).** The same holds for a tool descriptor whose install and health commands `gov` executes
   (`TOOLS_REGISTRY.tools[tool_id=TOOL-GIT-001]`), a hard invariant copied into agent adapters
   (`HARD_INVARIANTS.invariants[id=INV-001]`), a schema (`schemas/adapter-manifest.schema.json`) and an agent skill
   (`skills/SKL-API-CONTRACT-REVIEW.yaml`). New constitutional files of the forward-compatibility constraint that use these
   shapes inherit it.
5. **Blast radius mis-stated.** `05` §1 and `21` OP-2 say `release-final` "sets the kernel value of the 52
   `project_tunable` and 32 `release_bound` leaves" and becomes a policy root only if "it passes a local trust gate at
   ingress". They omit the choice among registered pinned, member and file digests, and Git-delivered use passes no gate.

### Evidence

- **executed** (B's `RV4-B-surface-probes.py` part P, reproduced byte-identical, pack checker and real 4.1.5 as consumer):
  mixed kernel exit 0 under a TPS retaining both `aws-access-key` regex digests, exit 3 under a TPS registering only the
  fix; `reductions` exit 0 for retaining and for re-adding a superseded digest; leaf direction `none`; the file carrying an
  `ASIA…` key is excluded under the fixed release and indexed and returned by `memory query` under the mixed one.
- **executed** (D-A02, pack checker): for T1 tool descriptor, T2 hard invariant, T3 schema file and T4 skill file, the mixed
  release with the superseded content exits 0 under RETAIN and 3 under ONLY; the release with every fix exits 0 under both;
  `reductions` v1→RETAIN exit 0 and ONLY→RETAIN (re-adding) exit 0 with no reduction listed.
- **design** `23` §3.1, §3.2, §6.3, §7, CS-2; `19` §5.2, §6 E7/E10, §10.6; `20` §9; `26` §6; `05` §1; `21` OP-2, OP-3.

### Failure scenario

4.1.7 fixes `SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex` to catch `ASIA` keys, and TPS v2 keeps the
4.1.6 digest so installed 4.1.6 projects keep indexing. A `release-final` thief signs 4.1.8-x with the old regex; A2 commits
it. On every machine holding TPS v2 it is an eligible policy root at use; temporary AWS keys are indexed and served to
agents; no machine reports a weakening. The same thief can restore an older tool descriptor whose install command was
fixed.

### Why HIGH

Authentic, eligible content confers weaker effective secret handling, tool execution or agent instruction while every
check passes: the R2-H1 / RV3-H1 class. HO-0001 §3.1 requires values to move down only by a computed, declared,
per-project-gated reduction, and lists sensitivity and indexing exclusions and the tool permission floor among the cases.
Trigger: one threshold-1 key, A2, and a routine owner Trust Policy.

### Class and novelty

**Narrowed remainder of R2-H1 / BC-1.** BC-1 as stated by review r3 (precedence and absence) is closed: P1r4 byte-identical
on real 4.1.5, checker exits 3 and 2, lattice 0 unsound. The remaining lower-trust choice is among permitted non-orderable
values. **Unestablished invariant:** a registration fixes, for each release sequence, the effective value of every
constitutional leaf, member and file; content registered only for an earlier sequence is never effective in a later one
except through a computed, cumulatively declared, per-project-gated reduction.

---

## MEDIUM

Every MEDIUM is carried with a bound acceptance test (`11-CORRECTION-DELTA.md` §6). None needs an architecture change, for
the reason given.

| ID | Statement | Evidence | Origin → adjudication | Carried as |
|---|---|---|---|---|
| **RV4-M1** | **Subdirectory-rooted legacy commands escape the occupation defence.** Legacy `init`, `adopt baseline` and `migrate baseline` root at the working directory (`cli/src/main.rs`: `cli.root.clone().unwrap_or(std::env::current_dir()?)`) and skip `require_installed`. From any subdirectory of an intact revision-4 project they install a nested legacy project, including inside `governance/trust/**` (56 invocations), while `18` §9 stays `COMPLETE`. Beyond reviewer C: (i) from `governance/` and from `governance/trust/kernel/` too; (ii) the nested install makes every legacy command operational beneath it (`kernel trust` `verified: true` from `governance/views`; `status` from `governance/trust/kernel/policies`; `rebuild-memory` from `governance/trust/state`); (iii) a legacy CIT rooted at the nested install, approved `--by orchestrator --method auto` with no human gate, rewrites RoT-1 files through nested-root-relative paths. **Reach:** an edited installed kernel file is `KERNEL_TAMPERED` (`18` §6.1) and a deleted `governance/trust/framework.lock` makes the state `PARTIAL` (fail closed); PPS litter changes no trust fact; an overlay-only rewrite leaves the state `COMPLETE`, is `PROJECT_STRENGTH_WEAKENED` on a machine that recorded the vector, and is accepted by fresh clones (LR-4). **Claims contradicted:** `26` §3 class argument; property LP-1 "every invocation derived from its own register" (every P3r3 invocation carried `--root`); D-0008 rule (10) and rule (12) "every no-install write or restore root"; VU-10; `18` §9 `COMPLETE` examines no foreign entry; RoT-1 root discovery for nested roots is unspecified (D-A09). | **executed** C `subdir_escape.json`, `matrix-rows.jsonl` (reproduced: identical JSON; matrix 10,618 rows with identical aggregates); D-A01 on copies of C's R4 tree with real 4.1.5 and two re-encodings of `18` §9 plus the architect's LR2 strength functions. **code** `cli/src/main.rs` lines 729, 747. | RV4-C-H1 → **CONFIRMED, re-rated HIGH → MEDIUM.** C's blocking bar was "a state a legacy operation produces that RoT-1 treats as valid". D-A01 shows no kernel file, trust statement, lock or occupation entry changes silently: each such change is `KERNEL_TAMPERED` or `PARTIAL`. The only `COMPLETE` outcomes are PPS litter that enters no trust decision and overlay changes, which are repository-writer authority (LR-4) and detected where recorded, the bounds review r3 accepted for LR-2. C itself states no enforcement bypass was demonstrated. The fix tightens a state predicate, root discovery, rule text and a test position; it changes no trust relationship. | closed trust entry sets for `COMPLETE`; RoT-1 root discovery and PPS working-directory refusal; restated LP-1, rules (10), (12), LR-2; RT-50/RT-50b from subdirectories |
| **RV4-M2** | Write confinement is a deny list: a `gov`-run repository command plants `gov` on `PATH`, a shell start-up line or a Git hook that later runs unconfined and forges VTS anchors and confirmations or replaces the binary. `28` §2.2 "removes the governed account from the anchor's writers" and `27` §3.3 (2) hold only for direct writes. | executed B part A (reproduced byte-identical) | RV4-B-M1 → CONFIRMED MEDIUM. Code running as the account is already scoped as A3 (RS-3, TG-2); system pins stay outside it; an allow list plus a TCB-location predicate is a bound rule. | CR4-B-01 |
| **RV4-M3** | OP-7 (c): the witness service's input (how it learns the newest TSS) and custody (two keys in one service) are unspecified; the (c) bound is exact only with an independent input. | design; B model RS-5 rows (reproduced) | RV4-B-M2 → CONFIRMED MEDIUM (not the proposal; bound custody and input rule) | CR4-B-02 |
| **RV4-M4** | RS-2's detection bound does not exist under OP-7 (a), (b), (d) or on stateless runners: only witnesses raise `clock_high_water`. A clock set back (including by an unauthenticated time source) makes an expired pin valid and its P1 proof current. | computed B model LB3 (reproduced) | RV4-B-M3 → CONFIRMED MEDIUM (TA-7 is declared; the defect is a mis-stated bound). Since SV-11 refuses future statements at ingest, the high-water may again be raised by any ingested statement on stateful machines; the stateless case is TA-7 and must be stated. | CR4-B-03 |
| **RV4-M5** | Computed weakening needs a recorded vector: a release-signed migration's registered weakening (P1r4 M5) on a machine without a record is committed ungated and reaches fresh clones. | design; P1r4 part C (reproduced) | RV4-B-M4 → CONFIRMED MEDIUM | CR4-B-04 |
| **RV4-M6** | The RV3-L7 fix holds only for a replace-form `.gitignore`; a migrated project that keeps the legacy `.governance-runtime/` line lists `.governance-runtime/migration` to the untracking idiom, and later clones are `PARTIAL(occupation)`. | executed C `durability.json` R4 vs R4APP (reproduced identical) | RV4-C-M1 → CONFIRMED MEDIUM (fail closed) | C's requirement and RT-122 on a real legacy `.gitignore` |
| **RV4-M7** | **The mandated conformance oracle cannot detect most plausible regressions outside the nine review-r3 defects.** Twenty single-line mutants of the architect's own P4r4 rule functions, each regressing a rule the pack declares normative: P4r4 (54 scenarios) and VA4 (16 rows) detect 9. Each of the 11 undetected mutants is an effective regression (a distinguishing scenario built from the architect's constructors gives a different result, 11 of 11). Five have neither an oracle scenario nor a named RT: A8 omitting the candidate from the negative-set check (`ARTIFACT_REVOKED` → `ACCEPTED`); A4b accepting an attestation the effective TSS does not reference (`ARTIFACT_SOURCE_UNVERIFIED` → `ACCEPTED`); **inclusion without the "held" clause** of `24` §3.4 rule 1, where a trust-state thief's TSS naming the pinned `(10, t10)` in `prior_states` makes a machine that holds neither t9 nor t10 `ANCHORED` with C3 (`BELOW_ANCHOR` → C0–C3); a witness naming a non-effective TSS honoured (`UNANCHORED` → `WITNESSED`, C3); a lift through an attestation the TSS does not reference. Two are ambiguous against RT-95 and RT-108 (top TPS omitting a held lower TPS; `op7_mode` a→c). | computed D-A03, D-A03b | NEW (D) → MEDIUM (review r2 R2-M10 and r3 RV3-M9 remainder); carriable: scenarios and RT rows | distinguishing scenarios and RT rows for all 20 mutants; D-A03 re-run detects 20 of 20 |

## LOW

| ID | Statement | Evidence | Origin → adjudication | Carried as |
|---|---|---|---|---|
| RV4-L1 | The wildcard `informational` rule `ROLES.authority_levels.*.*` admits unknown keys (a new key under a level, a new level L6): an exception to default deny. | executed B U01, U02 exit 0 (reproduced) | RV4-B-L1 → CONFIRMED LOW (no runtime reader in 4.1.5; consumer register would catch a new reader) | CR4-B-05 |
| RV4-L2 | `24` §4.3 and §5.2 allow C3 for `WITNESSED` at threshold; `24` §4.4 defines a currency proof only for `ANCHORED` machines; A9 requires a proof. | computed B LB2 (reproduced) | RV4-B-L2 → CONFIRMED LOW | CR4-B-06 |
| RV4-L3 | A P1 proof is labelled "published as of *t*" although the effective descendant may have been issued after *t*. | computed B LB1 (reproduced) | RV4-B-L3 → CONFIRMED LOW (window-bounded, no revocation bypass beyond RS-1b) | CR4-B-07 |
| RV4-L4 | The accepted-TBM high-water is absent on stateless runners (an older genuine unrevoked binary is accepted there); first-run recording of a non-resolving TBM is unspecified and has no reset. | computed B AT1, AT2 (reproduced) | RV4-B-L4 → CONFIRMED LOW | CR4-B-08 |
| RV4-L5 | Decision pins have no maximum validity (schema and TPS). | design | RV4-B-L5 → CONFIRMED LOW | CR4-B-09 |
| RV4-L6 | A4a and A4b do not consult the negative set for attestations; a binary accepted through a revoked attestation stays acceptable until revoked itself. | design | RV4-B-L6 → CONFIRMED LOW | CR4-B-10 |
| RV4-L7 | The `21` OP-4 consequence bullet is duplicated and garbled, and its key counts inherit RV4-H1. | design | RV4-B-L7 → CONFIRMED LOW | CR4-B-11; CD4-4 |
| RV4-L8 | `05` §1 and `21` OP-2 ("owner must know" item 1) list "passes a local trust gate at ingress" as a condition for a forged final to become a policy root. A Git-delivered higher-sequence release becomes the policy root at use with no gate (`20` §9, `19` E10; `21` OP-3 says so for mode A). | design D-A06 | NEW (D) → LOW (consequence text; the reach is RV4-H3's) | CD4-4 |
| RV4-L9 | `19` §10.6 makes every `eligibility.production_sources[]` addition a computed reduction (cumulative `lowering_history`, per-project `policy_lowering` gate, `local_terminal_only` by default). Under the proposed OP-2 (S1) every binary-shipping release adds one. `21` OP-2 (S1) states the cost as one TPS entry per release. Either the cost is omitted or the reduction rule is mis-scoped. | design D-A05 | NEW (D) → LOW (option cost and rule consistency; fails closed) | CD4-4; restate rule scope |
| RV4-L10 | Owner-domain slots register one digest per path per machine (`csi_lib.evaluate_owner_domain`). The forward-compatibility Capability Acceptance Contract is a hash-bound set (Markdown, compiled YAML, schema, evidence map); no slot binds the set, and the resolution of several still-valid `owner_constitutional_file` decision pins (no maximum validity, RV4-L5) on a machine without a record is undefined, so mismatched or superseded members of the set can be consumed on pinned machines. | design D-A08; code reference `csi_lib.py` | NEW (D) → LOW (classification works; set binding and pin resolution are bound rules; confirmed machines fail closed on change) | binding groups for slots; pin resolution rule; RT-120 extension |

## INFO

| ID | Statement | Origin → adjudication |
|---|---|---|
| RV4-I1 | The acting role remains caller-declared (V-L5). No trust gate depends on it (`27` §5). D-A01 shows the legacy binary approves a CIT `--by orchestrator --method auto`. | RV4-B-I1 → CONFIRMED INFO |
