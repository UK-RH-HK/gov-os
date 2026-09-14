# 01 — Alternative mechanism: the Selection-Authority Model (SAM) for RoT-1

> **Proposal by specialist A (AR-0009) for the revision-5 synthesis architect. Not an architecture revision, not approved,
> not implemented.** D-0008 and ARCH-0002 are unchanged. Normative keywords describe the proposal.

SAM keeps revision 4's verification core, trust-state machine, constitutional surface and legacy containment. It changes
**who may select** in the three decisions that kept failing, and it makes selection a compiled, testable register for every
decision. Root cause: `00-ROOT-CAUSE.md`. Attacks: `02-FALSIFICATION.md`. Trade-offs: `03-OWNER-CHOICES.md`.

## 1. Principle and the selector register

### 1.1 SEL-1

For every trust decision:
- each selector's authority and currency must be at least what the decision confers;
- restrictors may only refuse, or strengthen through a monotone join;
- carriers only transport bytes whose identity a selector has fixed.

Ranks and definitions: `00` §5.

### 1.2 The compiled selector register (new; R-SEL-1…4)

| ID | Rule |
|---|---|
| R-SEL-1 | The binary compiles a **decision register**: for every trust decision (every E1–E10 condition, every A-step of `accept`, every anchor, currency and gate decision, and installation-state determination), the selectors, restrictors and carriers, with each selector's authority and currency. |
| R-SEL-2 | A decision implementation may read a selector only from the source the register names. The type system enforces it: a `Selected<T>` value is constructible only from the registered source, as ARCH-0002 already does for `Anchor` and `PrecedenceRule`. |
| R-SEL-3 | A new decision, or a new input to an existing decision, fails the build until it is registered. This is the selector counterpart of the compiled consumer register (`23` §6.5). |
| R-SEL-4 | The conformance oracle includes, for each registered selector, a mutant that substitutes the next-lower-authority input, with a distinguishing vector. That is the measure that failed in RV3-M9 and RV4-M7. |

## 2. BC4-1 — release registration and reproduction quorum

### 2.1 Trust inputs of the TCB decision

| Component of the TCB | Selector | Restrictors | Carriers |
|---|---|---|---|
| Source tree (`release_commit`, `source_tree_digest`) | the **release registration authority** | a held REJECTED verification attestation for the candidate; revocations | Git host, pipeline |
| Build inputs (toolchain archives by digest, lockfile, build image digest, flags): `build_inputs_digest` over a published **input manifest** | the **release registration authority** | revocations | mirrors, CI configuration, caches |
| Bytes (`binary_digest`, which includes the compiled TBM) | a **reproduction quorum**: ≥ q distinct `reproducer` keys (compiled minimum q = 2), each attesting its **own** reproduction from the registered source and inputs | a conflicting reproduction refuses; revocation of the digest or of a reproduction | pipeline, download host |
| Current acceptability | the machine's current selector of state (`§3`) | negative set of the selected state; `min_binary_version` | transport |
| Publication | — | the selected Trust State must list the digest in `published_binaries[]` | — |

### 2.2 Release registration (R-REG-1…7)

| ID | Rule |
|---|---|
| R-REG-1 | Every release that ships a kernel or binaries is **registered exactly once** by the registration authority, which is either the root threshold (`03` OC-1 (a)) or a delegated `release-registration` purpose with a compiled minimum threshold of 2, keys shared with no other purpose and granted by root (OC-1 (b)). |
| R-REG-2 | A registration names: `{release_id, sequence, release_statement_digest, source {release_commit, source_tree_digest}, build_inputs {manifest_digest, toolchain_digests[], lockfile_digest, build_image_digest}, targets[], constitution {unit → digest, for every non-join unit of §4}, migrations {path → digest}}`. |
| R-REG-3 | **The ceremony checks the build inputs.** Before signing, the ceremony verifies: <br>(a) each toolchain archive digest against the upstream release's own signed checksums; <br>(b) the lockfile digest against the file in the registered source tree; <br>(c) the build image digest against the owner's image record; <br>(d) the verification record (the independent verifier's report) against the source digest. <br>`gov trust draft-registration` refuses without (a)–(d) evidence. |
| R-REG-4 | Registrations are **append-only**. A Trust Policy or registration statement that changes or removes an existing registration entry is invalid (`TRUST_POLICY_REGISTRATION_REWRITE`). A release is retired only by `min_release_sequence` or revocation. |
| R-REG-5 | Under OC-1 (a), registrations are a Trust Policy section. Under OC-1 (b), they are separate statements, effective only when the selected Trust State references them (`registrations[]`). |
| R-REG-6 | `release-final` is **withdrawn as an authority**. The final release statement is a carrier whose digest the registration names. A `release-final` signature may remain for provenance display; no decision reads it. `release-candidate` remains for evaluation-candidate installs only (gated, never production). |
| R-REG-7 | V8 source equality becomes a producer restrictor: `gov release promote` refuses a final whose source differs from the verified candidate's. It no longer protects the TCB, because the registration is the selector. |

### 2.3 Reproduction quorum (R-REP-1…7)

| ID | Rule |
|---|---|
| R-REP-1 | Purpose `reproducer` signs `binary-reproduction.v1`: `{release_id, source, build_inputs.manifest_digest, target, binary_digest, tbm_digest, environment_digest, reproduced_at}`. Every statement is **first-person**: exactly one reproducer key, attesting a build that reproducer performed. A statement with several signatures counts for none. |
| R-REP-2 | A reproducer obtains **every** build input by digest from the registered manifest, from any carrier, and refuses on mismatch. It never uses a mirror, CI variable or cache as a selector. |
| R-REP-3 | Reproducers submit statements **to the owner's statement store directly**, outside the release pipeline, and publish them to the release bundle. The owner's publisher never learns about a reproduction only through the pipeline. |
| R-REP-4 | Compiled minimum quorum q = 2 distinct reproducer keys, for the same `(release_id, source, build_inputs, target, binary_digest, tbm_digest)`. Keys granted `reproducer` share no key with any other purpose (KS-12). |
| R-REP-5 | **Conflict refuses.** Two valid reproductions for the same `(release_id, source, build_inputs, target)` with different digests refuse every digest of that tuple (`REPRODUCTION_CONFLICT`) until a revocation removes one side. |
| R-REP-6 | A reproduction by a revoked key, or a revoked reproduction statement, counts for nothing. KS-7 (no revoked key granted) is checked on every root version. |
| R-REP-7 | The build must be deterministic from `(source archive, input manifest)` alone. `runtime/build.rs` today falls back to `git rev-parse HEAD` for provenance when no release manifest is present. The production build must read provenance only from the registered source archive, so that reproducers building from `git archive` obtain identical bytes. |

`release-artifact` and `build-attestation` are **withdrawn**. The custodial pre-check signatures of `25` §9 established no fact
their signers observed; the reproduction quorum replaces both.

### 2.4 The acceptance function `accept()` (one definition, two executors; R-ACC-1)

Inputs:
- **(i)** the candidate's bytes, read once by the executor (never executed);
- **(ii)** a state selector: a typed fingerprint (P2), or an anchor plus a currency proof (P1/P3) on a machine running an
  accepted binary;
- **(iii)** statements from any source;
- **(iv)** the target.

| Step | Check | Refusal |
|---|---|---|
| A1 | Measure the digest of the bytes read. | — |
| A2 | Build the root chain from root v1 by dual-threshold links, with KS-1…KS-12 (including KS-7) on every version. The lineage comes from the typed fingerprint's epoch, or from the running accepted binary's compiled lineage. | `ROOT_CHAIN_INVALID` |
| A3 | Select the Trust State. **Bootstrap:** the TSS whose epoch fingerprint equals the typed value, with its root and Trust Policy verified. **Running:** the effective TSS by inclusion anchors with a currency proof (`24` §3.4, §4.4; retained). | `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH` / `TRUST_STATE_*` |
| A4 | Negative set of the selected state: the digest, the registration, the counted reproductions and the candidate are not revoked; `min_binary_version` holds. | `BINARY_REVOKED` / `BINARY_BELOW_TRUST_POLICY` |
| A5 | Registration of the release, effective in the selected state. | `RELEASE_UNREGISTERED` |
| A6 | Reproduction quorum per R-REP-1…6 for (A1 digest, target, registered source and inputs). | `REPRODUCTION_QUORUM_NOT_MET` / `REPRODUCTION_CONFLICT` |
| A7 | TBM consistency: the quorum's `tbm_digest`; TBM `binary.source` and inputs equal the registration; TBM root, policy and state resolve to verified statements. **Running executor only:** accepted-TBM high-water (retained `25` A7). | `BINARY_T0_UNVERIFIED` / `BINARY_T0_ROLLBACK` |
| A8 | Publication: the selected TSS lists the digest in `published_binaries[]`. A TSS never drops a published digest (retained S4 (d) rule for `artifacts[]`). | `BINARY_NOT_PUBLISHED` |
| A9 | Record in the verifier trust store: `accepted_binaries[] {digest, target, release_id, state selector used, install path}`. | — |

Reference implementation of A1–A6 and A8 for the bootstrap executor: `evidence/gov_accept_reference.py`. It has 16
conformance vectors and 13 single-rule mutants: 12 detected, 1 equivalent under KS-7 (`evidence/outputs/E3-*.json`).

### 2.5 What it removes, adds, assumes and costs (BC4-1)

| | |
|---|---|
| **Removes** | `release-final` as selector of source (and of everything else, §4); the verification key as selector of source; the release process as selector of build inputs; custodial signatures that re-check upstream signatures; `release-artifact` and `build-attestation` purposes; OP-2 S0–S3 and `release-artifact` (i)–(iii) as security options; OP-4 as a production security option |
| **Adds** | the registration authority for every release; the `reproducer` purpose with compiled q ≥ 2; first-person, conflict-refusing reproductions; digest-addressed input manifests; submission outside the pipeline; KS-12 |
| **Assumes** | TA-4 custody of the registration keys; **TA-10′** reproducers' environments and custody are independent of each other and of the pipeline (not verifier-checkable); **TA-12** the upstream toolchain release that the ceremony verified is not itself malicious; TA-11 the verification record the ceremony reviews is honest (route I, TB-4, retained) |
| **Costs** | one registration ceremony per release; at least q independent reproducers per target per release; hermetic, byte-reproducible builds, including removal of the `git rev-parse HEAD` provenance fallback from the production build; an input-manifest publication per release |

### 2.6 Minimum capability sets (computed, `evidence/E2-tcb-capability-sets.py`)

Registration Q2 (delegated quorum), n = 3 reproducers, q = 2, reproductions submitted outside the pipeline:

| Goal | Victim selects state by | Minimal capability sets |
|---|---|---|
| malicious bytes for the registered source | typed fingerprint (first install) | {2 reproducer keys, trust-state key, channel, transport} |
| malicious bytes | protected pin within window (P1) | {2 reproducer keys, trust-state key, transport} |
| malicious source or malicious named inputs | P1 | {2 registration keys, trust-state key, pipeline, transport} or {2 registration keys, 2 reproducer keys, trust-state key, transport} |
| malicious source or inputs | typed fingerprint | the P1 sets plus `channel` |
| poisoned input mirror | any | **no set without reproducer keys**; the mirror alone yields nothing |
| compromised upstream toolchain release | any | **{toolchain_upstream}**: residual TA-12 (`03` OC-3) |

- **Q1 (root threshold).** The same sets, with two root keys in place of two registration keys.
- **Submission through the pipeline** (R-REP-3 violated). Malicious bytes need only {pipeline, 2 reproducer keys}. R-REP-3 is
  load-bearing.
- **Floor.** No row of 64 (4 goals × 2 authorities × 2 reproducer counts × 2 victim types × 2 submission rules) accepts with
  fewer than two keys, excluding TA-12.
- **Control.** Revision 4 as written: {1 build-attestation key, pipeline}, and, under the stated reading, {pipeline} for
  malicious named inputs.

## 3. BC4-2 — one acceptance function, externally executed, with a typed selector

### 3.1 What each machine class can prove (lens A)

| Machine | Compiled trust it may use | Current selector available | Therefore |
|---|---|---|---|
| First install | none (no `gov`) | fingerprint typed now from an independent channel | full `accept()` by the independent executor, clockless |
| Clean CI runner | the image's accepted binary; its protected pin | the pin within its window (P1) | binary accepted at image build; each job anchored by the pin |
| Restored from backup | the binary accepted before the backup | none until re-anchored | C3, including binary upgrade, needs a fresh typed fingerprint |
| Old epoch or long offline | its accepted binary and anchor | none current | RS-1 for C1–C2; C3 needs a typed fingerprint and the statements it names |
| Legacy consumer (Phase 4) | none RoT-1 | typed fingerprint | same as first install; the legacy `gov` has no `verify-artifact` (E3 FB4) |

### 3.2 First acceptance procedure (R-FA-1…8)

| ID | Rule |
|---|---|
| R-FA-1 | The first `gov` on a machine is accepted only by the **independent executor** `gov-accept`. It is a separately published program in a different language and code base, using platform OpenSSL and the language standard library only, and implementing `accept()` from the same conformance vectors as `gov`. |
| R-FA-2 | The operator compares `gov-accept`'s SHA-256 with the digest published in the independent channels (`06` §2 step 2, which also publishes every state fingerprint) before running it (TA-5). |
| R-FA-3 | The operator types the **current** state fingerprint from the channel. It is the only selector of state, root chain and negative set. No compiled value, clock, repository file or environment variable is an input. |
| R-FA-4 | `gov-accept` reads the candidate once and **never executes it**. No value the candidate prints is an input. `gov version --trust` is diagnostics only. |
| R-FA-5 | **Build from source is not a separate trust path.** A self-built binary is measured by `gov-accept`. It is production only if its digest equals a quorum-reproduced digest; otherwise it is `build: development`, whatever it prints. |
| R-FA-6 | **Installation binding.** `gov-accept install <candidate> <dest>` writes the bytes it read, re-reads and compares them, and evaluates the TCB-location predicate: `dest` and every ancestor are owned by another uid and not writable by the effective uid. The result is recorded. What the predicate gates is `03` OC-4. |
| R-FA-7 | The accepted binary's first trust operation requires its own state anchor (`gov trust confirm-state`, typed again; P2). `gov-accept`'s result is never imported as an anchor, so no file that another program wrote becomes one. |
| R-FA-8 | `gov-accept` displays the selected state's `issued_at` and its age, and never the word `current`. |

### 3.3 Ceremony order (R-CER-1…3; closes D-A04)

| ID | Rule |
|---|---|
| R-CER-1 | No TA-5 ceremony (`confirm-root`, `confirm-state`, in-gate fingerprint, trust-gate confirmation) is performed by a binary that `accept()` has not accepted on this machine. |
| R-CER-2 | `confirm-root` is subsumed on first install, because the typed fingerprint commits to the lineage id. The lineage is shown for information. OP-6 (b) (trust on first use) is incompatible with production acceptance and is withdrawn for production. |
| R-CER-3 | A binary that finds no `accepted_binaries[]` record for its own digest in the verifier trust store runs C0 only and names `gov-accept` as the remedy. The record is same-uid writable (RS-3 class), so this is a guard against ordering mistakes, not against A3. |

### 3.4 Subsequent binaries and self-restriction (R-SUB-1…3)

| ID | Rule |
|---|---|
| R-SUB-1 | Binary N accepts binary N+1 with `accept()` in running mode: A3 by inclusion anchors plus a P1, P2 or P3 currency proof (retained `24` §4.4), A7 against the accepted-TBM high-water (retained). |
| R-SUB-2 | **Self-restriction.** At every unit of work, a running binary measures its own executable once and checks the effective negative set. If its digest or release is revoked, it refuses the classes `03` OC-6 selects. This protects against a genuine-but-revoked binary only; a malicious binary is excluded by acceptance, not by this check. |
| R-SUB-3 | **CI runner images.** The image build is a first install: `gov-accept` with the fingerprint the operator provisions into the root-owned pin, in the same step and within the C3 window. Images are rebuilt before `pin_max_validity_days`; each rebuild re-runs acceptance. |

### 3.5 What it removes, adds, assumes and costs (BC4-2)

| | |
|---|---|
| **Removes** | path (b) A2–A6 tooling; path (c) self-report; Phase 4 self-verification; ceremonies on the unaccepted binary; compiled T0 and the clock as inputs to first acceptance; OP-6 (b) for production |
| **Adds** | `gov-accept` and its published digest; shared conformance vectors; installation binding and the TCB-location predicate; the `accepted_binaries[]` record; self-restriction; image acceptance cadence |
| **Assumes** | TA-5 (the operator reads the channel now and compares the executor digest); TA-1b (the platform interpreter and OpenSSL on the first machine are genuine); TA-9 for CI pins; TA-7 for P1 windows |
| **Costs** | one extra program to maintain and publish; typing the fingerprint twice on first install; a privileged install location if OC-4 (a); image rebuild at least every pin validity period |

## 4. BC4-3 — constitutional content as a function of the registered release

### 4.1 Units

A **non-join unit** is:
- every `pinned` leaf, and every whole member content of a keyed collection;
- every `pinned_file` path;
- every `transaction_input` (migration) file;
- every owner-domain **binding group** (§4.3).

The draft TPS v1 has 276 digest units, each registered with exactly one digest (E4).

**Join units**, where the join is the selector and they stay as revision 4:
- `floor` leaves (joined with the effective Trust Policy);
- the project-layer precedence (registration only, `23` §4.1);
- additive collections whose consumer is monotone in additions (§4.3).

### 4.2 Rules (R-CON-1…8)

| ID | Rule |
|---|---|
| R-CON-1 | **Exact per-release registration.** The registration of release *R* (R-REG-2) lists the digest of **every** non-join unit present in *R* ("closed"). A unit absent from *R*'s registration is not required for *R* and is unregistered for *R*. |
| R-CON-2 | **E7 at ingress and at use.** Every non-join unit of *R*'s kernel equals the digest registered for *R* in the effective registrations. A release with no registration, or with any unit different from its registration, is ineligible (`surface_unregistered_for_release`). Ranges and "latest registered" are never used. |
| R-CON-3 | **Effective value.** The root kernel's unit if *R* is eligible; else the EmbeddedSnapshot's unit, as registered for the **running binary's** release; else `SURFACE_VALUE_UNAVAILABLE` (retained fallback, now release-scoped). |
| R-CON-4 | **Presence is release-scoped.** Required presence (`23` §3.5) is evaluated against *R*'s registration. A member introduced for 4.1.7 is not required of 4.1.6. |
| R-CON-5 | **Reversion is a computed reduction.** A registration whose unit digest equals a digest that an earlier registration of the same unit superseded is a reduction (`registration_reversion`). It needs cumulative `lowering_history` and, for projects whose record holds the newer registration, the `policy_lowering` gate. On machines without a record, requirements are computed from the pre-transaction inputs (CR4-B-04). |
| R-CON-6 | **Retention is legitimate and does not widen.** Installed releases stay eligible at their own registration. A later registration can never make superseded content eligible under a different release. Whether to retire older releases is `03` OC-5. |
| R-CON-7 | **Knowledge of registrations follows state.** Registrations are effective only as the selected state makes them effective (Trust Policy referenced by the effective TSS, or registrations it references). A machine that has not received a registration treats the release as unregistered and refuses; it never falls back to an earlier release's content. |
| R-CON-8 | The producer (`gov release build`) and the canonical CI run the unmodified surface checker against the projection "registration of *R*". E4 shows that this projection plus the existing checker suffices. |

### 4.3 Migrations, owner-domain groups and additive collections

| Surface | Rule | Closes |
|---|---|---|
| Migration files | registered per release like any unit (R-REG-2 `migrations`). The Overlay Surface whitelist (`23` §11.3) and the strength vector stay as restrictors. | RV4-M5's selector (`release-final` choosing migration content); E4 part M |
| Owner-domain slots | a slot may declare a **binding group** (for example the Capability Acceptance Contract Markdown, compiled YAML, schema and evidence map). The local confirmation or decision pin registers the **group digest** over sorted `(path, digest)`. Any member mismatch refuses (`OWNER_CONSTITUTIONAL_GROUP_UNCONFIRMED`). Several valid pins resolve by exact group match only. | RV4-L10; E4 part G |
| Additive collections | an unregistered added member is admitted only where the consumer register declares the decision point **monotone in additions**, and a test shows that an invalid or pathological addition cannot disable registered members. For `secret_content_patterns`, `runtime/src/security/secrets.rs` compiles each pattern independently (`Regex::new(rx).ok()`), and the `regex` crate matches in linear time. | E4 parts A and C: an invalid extra pattern leaves the `ASIA…` file excluded on 4.1.5 |

### 4.4 Blast radius restated (BC4-4 input)

| Key purpose | Worst case alone under SAM |
|---|---|
| `release-final` (if a signature is kept) | nothing: no decision reads it |
| `release-candidate` | evaluation-candidate statements; only gated evaluation projects |
| one `reproducer` key | refusal of one release's binaries for one target (conflict, availability only) |
| `reproducer` keys at quorum | malicious bytes for a registered release, accepted only where the state selector also admits the attacker's publication (trust-state key plus transport on P1 machines; plus the channel on first install) |
| registration quorum (OC-1 (b)) or root threshold (OC-1 (a)) | registers malicious source, inputs or constitutional content for a new release. Accepted where the release is published in selected state and reproduced (pipeline, trust-state key and transport, or reproducer keys). Floors and registered precedence still hold under OC-1 (b). |
| `trust-state` | as revision 4 (`17` §15); plus, on P1 machines, publication of a quorum-reproduced digest |
| `verification-attestation` | REJECTED attestations refuse (denial of service); ACCEPTED selects nothing |
| `freshness-witness`, `certification-status`, `revocation`, `retrieval-profile` | as revision 4 |

## 5. Residuals (stated exactly)

| ID | Residual | Bound | Test that fails if exceeded |
|---|---|---|---|
| RS-1, RS-1b, RS-1c, RS-3, RS-4, RS-5 | retained from revision 4 `24` §10, with RS-5 conditioned by CR4-B-02 | as revision 4 | as revision 4 |
| RS-2 (restated per CR4-B-03) | under OP-7 (a), (b), (d) and on stateless runners a clock set back makes an expired pin valid; only the pin validity and the C3 window bound the staleness a clock adversary can reach | TA-7; no detection claimed | RT-56 with RV4-B-A13 |
| **RS-B1** | a fingerprint typed from a stale channel page selects the state it names | the channel's own currency (TA-5); `gov-accept` shows `issued_at` and age | E3 N-FB1 as a conformance vector (accepted, labelled) |
| **TB-S1** | reproducer keys at quorum plus the capabilities of §2.6 | §2.6 minimal sets | E2 re-run on the implementation's rules |
| **TB-S2** (TA-12) | a malicious upstream toolchain release verified by the ceremony | not bounded by the verifier; `03` OC-3 | E2 `toolchain_upstream` row |
| **TB-S3** (TA-10′) | reproducers under common custody | not verifier-checkable; ceremony record | procedural |
| TB-4 (route I) | an insider commit accepted by an honest but deceived verifier and ceremony | process | procedural |
| **VR-B1** (OC-4 (b) only) | same-uid replacement of an accepted binary in a user-writable location | RS-3 class | E3 N-FB8 |
| **AV-S1** | one reproducer key refuses a release by a conflicting reproduction | availability; remedy is revoking the forged reproduction | E3 V07 |
| LR-1…LR-4, VR-1…VR-4, RR-1…RR-3, TG-1…TG-3, CS-1 | retained, with the conditions of review r4 `05-RESIDUALS.md` | as revision 4 | as revision 4 |
| CS-2 | **replaced**: a registration ceremony per release is an operational cost, and retention no longer widens what later releases may carry | — | E4 |

## 6. Retained from revision 4 (review r4 CD4-0, review r3 CD3-0) and carried items

**Retained unchanged:**
- **Authentication core.** Compiled root chain; purpose-bound DSSE; `authenticate`; VerifiedBlobs; KernelSnapshot and
  EmbeddedSnapshot; GovernedFs and the Protected Path Set.
- **Purpose whitelist.** KS-1…KS-11, with KS-12 added and the withdrawn purposes removed.
- **Constitutional Surface.** The CSI as a root-signed section; default deny; closed floor vocabulary; exact precedence
  registration and registration-only precedence; the two-directional order; the directed join; required presence; one YAML
  profile; the Overlay Surface with default-deny migration targets; project strength over effective policy.
- **Trust state.** Release-local references; resolution; equivocation; cumulative `prior_states` and `prior_policies`;
  computed lowering with cumulative history; sticky negatives; the lift attestation; far-future refusal.
- **Anchors and currency.** Inclusion anchors; mandatory pin validity; currency proofs P1/P2/P3; the `freshness-witness`
  purpose with a compiled C3 threshold of 2; no `current` label; the pin integrity predicate; confined children.
- **Binaries.** The accepted-TBM high-water; the rule that published binaries are never un-referenced (formerly the artefact
  playbook); rotation re-signing.
- **Authorisation.** Local trust gates; repository records as requests.
- **Legacy containment and transactions.** The occupation layout and LP-1 for root-anchored invocations; LR-2's bounds; the
  transaction area and union records; VU-11 and VU-12.

**Absorbed by SAM** (the selector is removed, not patched):

| Item | How SAM absorbs it |
|---|---|
| RV4-M5 | migrations are registered units, plus CR4-B-04 |
| RV4-L10 | binding groups |
| RV4-L6 | attestations are not selectors; reproduction revocation is checked (R-REP-6) |
| RV4-L8, RV4-L9 | `release-final` has no authority; production sources are registrations, not TPS reductions |
| RV4-L7, BC4-4 | options restated in `03` |
| RV4-M3 | the witness service takes its input from the owner ceremony or the channel (CR4-B-02), now a registered selector |

**Carried unchanged:**
- RV4-M1 (closed trust entry sets for `COMPLETE`, which is SEL-1 applied to installation state; RoT-1 root discovery;
  subdirectory test positions);
- RV4-M2 (allow-list confinement; TCB-location predicate, now also R-FA-6);
- RV4-M4 (as RS-2 above);
- RV4-M6;
- RV4-M7, extended by R-SEL-4 and the E3 and E4 mutants;
- RV4-L1 … L5;
- C-2 … C-6.

## 7. HO-0001 §3 and §4 requirements, as classes

### 7.1 §3.1 Constitutional-floor closure

| Sub-item | SAM mechanism | Evidence |
|---|---|---|
| Complete inventory; default deny; floor mode per field; coverage check | retained CSI and checker | E0: selftest 56/56; framework exit 0 |
| Schema evolution cannot silently introduce an unfloored setting | retained default deny; **non-orderable changes are per-release registrations**; reversion is a computed reduction; rewrite invalid | E4 parts P, T, R |
| Role→authority map | floors (join) plus the `ROLES.roles` membership registered per release | P1r4 retained (E0) |
| Sensitivity and indexing exclusions | secret patterns registered per release; additive members monotone; overlay classifications (project) | E4 P and C: mixed refused, `ASIA…` excluded on 4.1.5 |
| Irreversible Human Gate authority | floor (join) | P1r4 retained |
| Plugin and tool permission floor | TOOL_POLICY floors; tool descriptors registered per release | E4 T1 |
| Outbound and export controls | floor `shrink_only` | P1r4 retained |
| Project override controls | registered precedence plus directed join | E0: RV3-B-A01 exit 3; lattice 0 unsound |
| Install and update authority | floor plus TPS `install_authority` | P1r4 retained |
| Exception authority | compiled prefixes; registered `exception_relaxable` | selftest S16, S55 |
| Future unknown constitutional field | default deny; a new non-orderable unit is registered with the release that introduces it | E0: removal and forward-compatibility probe identical |

### 7.2 §3.2 New-machine trust bootstrap

| Machine | Safe without freshness | Gated or read-only | Needs a current selector | Monotonic local state | OP-7 effect |
|---|---|---|---|---|---|
| First install | C0; `gov-accept` verification | everything above C0 until acceptance and anchor | binary: typed fingerprint (P2); C3: typed again in the gate or P1 | `accepted_binaries[]`, human anchor, statements | none on acceptance; C1–C2 per OP-7 after anchoring |
| Clean CI runner | C0 | C3 outside the pin's C3 window | protected pin (P1); image acceptance at build | nothing beyond the run | (a)–(c) as revision 4; (d) C1–C2 labelled |
| Restored from backup | C1–C2 at the anchored chain (RS-1) | C3 and binary upgrade | typed fingerprint | never below the restored anchor | as revision 4 |
| Old epoch | as restored | C3 | typed fingerprint or fresh pin | as revision 4 | as revision 4 |
| No epoch | C0 | C1–C3 under (a)–(c) | anchor | — | (d) C1–C2 labelled |
| Two machines at different epochs | each by inclusion | as revision 4 | per machine | per machine | as revision 4 |
| Offline long absence | C1–C2 at the anchor (RS-1) | C3 | typed fingerprint plus the statements it names (else `BELOW_ANCHOR`) | as revision 4 | (b) refuses C2 past the maximum age |

- **Signed-state replay:** retained (knowledge union; admissibility).
- **Gate records from repository state:** retained (requests).
- **Attacker-selected old signed state cannot become current:** no current fact is selected by a transport or repository
  input (SEL-1). The first binary is selected by the typed fingerprint (E3 FB1a, FB2a refused).

### 7.3 §3.3 Binary and root authenticity

| Evaluated option | SAM position |
|---|---|
| Threshold root signature | registration by root threshold (OC-1 (a)), or a delegated quorum ≥ 2 that root grants and rotates (OC-1 (b)) |
| Separate binary or root-bundle attestation | reproduction statements, first-person, quorum ≥ 2 |
| Certification binding | not a selector; optional restrictor; not required |
| Reproducible-build and provenance evidence | **mandatory**: digest-addressed inputs; R-REP-7 |
| Compiled trust-state digest; binary trust-policy digest (TBM) | retained as consistency checks (A7), not selectors |
| Multi-signature | the quorum |

| Protected asset | Protection |
|---|---|
| the binary | quorum-reproduced digest; installation binding |
| compiled trust roots, minimum floors, trust-policy identity, historical-release set, trust state and bootstrap rules | all are bytes of the binary built from registered source and inputs, so they are covered by the same digest; A7 checks consistency |

**Non-circular chain.**
1. The registration authority (root, or a root-granted quorum) selects source and inputs.
2. Reproducers observe the bytes.
3. The state selector (typed or anchored) selects publication and the negative set.
4. The executor is `gov-accept` for the first binary and binary N for binary N+1.

Nothing in a binary authenticates that binary, and no candidate output is an input.

### 7.4 §3.4 Legacy-binary damage containment

- **Retained:** revision 4's occupation layout; the reproduced 2,504 root-anchored invocations writing nothing; LR-2's bounds.
- **Carried:** RV4-M1, which applies SEL-1 to `COMPLETE`. The selector of installation validity is the entry set recorded by
  the install transaction, not the presence of named entries. RV4-M6 is carried as well.
- **Unchanged by SAM:** the defence does not depend on old binaries understanding RoT-1.

### 7.5 §4 Forward compatibility

- **New constitutional files and keys** classify with the existing vocabulary and default deny.
- **New non-orderable units** are registered with the release that introduces them; no new mechanism is needed.
- **The Capability Acceptance Contract** is a kernel unit set or an owner-domain binding group.
- **Gate W and G0–G6 keys** are floors or registered units.

## 8. Rule deltas for D-0008 (input for the synthesis architect; D-0008 not edited)

| Rule | Delta |
|---|---|
| new (0) | SEL-1 and the compiled selector register (R-SEL-1…4) |
| (6) | non-join constitutional units are fixed per registered release; presence is release-scoped; reversion is a computed reduction; registrations are append-only |
| (9) | binary acceptance = registration of source and inputs + reproduction quorum ≥ 2 (first-person, conflict-refusing, submitted outside the pipeline) + publication in selected state + negative set; `release-artifact` and `build-attestation` withdrawn |
| (16) | no self-validation, including first acceptance, Phase 4 and ceremonies; the independent executor implements the same `accept()` |
| (17) | source selection, build-input selection, byte observation, publication, currency and eligibility are distinct facts with distinct selectors; `release-final` confers none of them |
| (19) | every TCB acceptance consumes a current state selector; first acceptance by typed fingerprint; installation binding per OC-4 |
| (21) | extended: build inputs are fetched by digest; CI configuration is a carrier |

## 9. Operational costs (summary)

1. One registration ceremony per release: root threshold (OC-1 (a)) or a delegated quorum (OC-1 (b)), including an
   input-manifest check.
2. At least two independent reproducers per target per release, with byte-reproducible builds and no VCS-state provenance.
3. `gov-accept`: maintenance, a published digest, and shared conformance vectors.
4. First install: download `gov-accept`, compare its digest, type the fingerprint for acceptance, and type it again for the
   first C3.
5. CI: image acceptance at every image build; rebuilds at least every `pin_max_validity_days`; a privileged install location
   under OC-4 (a).
6. A per-project gate whenever the owner reverts non-orderable content.
