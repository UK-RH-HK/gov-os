# Output 15 — Supersession of D-0007

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved.**
> D-0007 is not edited. D-0008 remains PROPOSED until the owner answers its Human Decision Gate: record status field
> `PROVISIONAL`, `in_effect: false`, no `chosen_option`, `supersedes: []`.
>
> Revision 6 revises rules (6), (7), (9), (10), (12), (16), (17), (19), (22), (23) and (24), and adds rules (25), (26) and (27),
> following review r5 `11-CORRECTION-DELTA.md` §5 and the class closures of `32`–`34` and `29`.
> Revision 5 revised rules (6), (7), (8), (9), (10), (12), (16), (17), (19) and (21), and added rules (22), (23) and (24),
> following review r4 `11-CORRECTION-DELTA.md` §5 and the class closures of `29`–`31` and `23` §12. (Revision 4 revised (3),
> (6), (7), (9), (12), (17)–(20) and added (21).)

## 1. Decision

D-0008 **supersedes D-0007 in full** and restates the parts that remain correct. The supersession takes effect only when
the D-0008 approval gate is answered. Until then D-0007 remains ACTIVE and unedited.

## 2. Diagnosis — what D-0007 got wrong

| # | Error | Evidence |
|---|---|---|
| 1 | T1 decided by agreement among artefacts from the untrusted source | `kernel.rs:248-256`, `lock.rs:12-35`, `kernel_trust.rs:125-169`; E4 |
| 2 | Incoming material had no class | `update.rs:29-43`; E1 |
| 3 | An authorisation fact read from the source | `update.rs:82-94`; E2 |
| 4 | The embedded anchor consumed through a mutable cache | `kernel.rs:31-80`; E3 |
| 5 | Rules constrained readers, not writers | `update.rs:378-386`, `migrations/executor.rs:304-350`, `cit/mod.rs:704`; E5 |
| 6 | "Verified" conflated integrity and authenticity | doctor D029 |
| 7 | Git-tracked T2 records used for trust-relevant decisions | review r1; review r2 P2 |
| 8 | Agent-approved (`human_approved: false`) | `spec/decisions/D-0007.yaml` |
| 9 | Authenticity conflated with currency | review r1 RV-H1 |
| 10 | Registered floor keys conflated with constitutional policy | review r2 R2-H1; P1 |
| 11 | Compiled or repository knowledge conflated with current state | review r2 R2-H2; P4-B5 |
| 12 | A release key's authenticity conflated with binary authenticity | review r2 R2-H3 |
| 13 | A sentinel read after acting conflated with a boundary | review r2 R2-H4; P3 |
| 14 | A refusal-only precedence order taken as a strength order; the presence of classified content taken as the registered constitution (D-0008 revision 3) | review r3 RV3-H1 |
| 15 | An anchor number taken as the anchored state; an anchor established once taken as current (D-0008 revision 3) | review r3 RV3-H2 |
| 16 | "Reproduced from the named commit" taken as "built from verified source" (D-0008 revision 3) | review r3 RV3-H3 |
| 17 | The typed fingerprint taken as a selector of everything it commits to: lineage, channel quorum and evaluator (D-0008 revision 5) | review r5 RV5-H1 |
| 18 | "Every input named by digest" taken as "every input legitimately selected": the build environment (D-0008 revision 5) | review r5 RV5-H2 |
| 19 | "The registration authority signed the unit map" taken as "the registration authority established it" (D-0008 revision 5) | review r5 RV5-H3 |

Errors 10–13 were present in D-0008 revision 2, and errors 14–16 in revision 3. Revision 4 corrects them; `28` explains why each earlier correction left a remainder. They are the same class throughout: **a
lower-trust input yielding a current, higher-trust fact.**

## 3. Rules retained from D-0007

| D-0008 rule | Text | Change from D-0007 |
|---|---|---|
| (1) | An enforcement decision reads its floor from the highest **eligible** class only, **with every leaf of the Constitutional Surface joined with the effective Trust Policy**. When that cannot be established, the embedded baseline is substituted explicitly and mutating operations fail closed. | eligible; surface-wide join |
| (2) | *registered*, *approved*, *verified*, *eligible*, *certified*, *current*, *anchored*, *human_approved*, *authority*, *provenance* are facts of T0/T1/T2 or of local machine authority (§4) only. A lower-class field carrying such a name is a request. | *current*, *anchored* added |
| (3) | A project layer may specialise or strengthen, never weaken. **Admitted project strengthening is removed only by a computed reduction accepted per project; no refusal of a weakening discards an admitted strengthening.** | directed join; reductions in both directions (revision 4) |
| (4) | Every refusal is typed and auditable. | unchanged |

## 4. Trust classes (replacement table)

| Class | D-0008 revision 3 |
|---|---|
| **T0** | Compiled into the running binary and named by its **Trust Base Manifest**: root chain; purpose table and whitelist; schemas; floor vocabulary v3; the two-directional precedence order and YAML profile; the newest Trust Policy (Constitutional Surface, historical releases, bootstrap rules); Trust State; EmbeddedSnapshot and its statement; trust-format and layout readers; the binary's source. Genuine only when the binary was accepted by `verify-artifact` or built from attested source. |
| **T1** | Authenticated material: statements verified under the T0-rooted chain for their purpose; content equal to a verified statement's file map |
| **T1-E** | Eligible authenticated release: T1 release material satisfying E1–E10, including the E7 surface check. Only T1-E may be the policy root. |
| **LA** (local machine authority) | Anchors, trust-gate confirmations and per-project records in this OS account's Verifier Trust Store, and operator pins in the system pin directory or, under the integrity predicate, the account configuration. Valid only on this machine; never transferable through a repository. A3 can forge its own VTS records (same-user boundary) but not protected pins. |
| T2 | OS-written project state. Git-tracked T2 records (gates, ledgers, registries, locks) are **requests** for every trust decision (rule 18). |
| T3 | Derived state bound to CI and effective-policy digest |
| T4 | Repository- or user-writable artefacts not currently verified: installed files before snapshot verification, lock fields, trust files before verification, the transaction area, journals, snapshots, adapter bodies, the project overlay |
| T5 | CLI arguments, environment variables, source paths and contents, bundles before authentication, descriptive manifests |
| T6 | Plugin and model data, including plugin-reported digests |

## 5. Rules (5)–(24)

The eight rules the owner required for revision 2 are marked [O1]…[O8]. **Bold** marks revision-4 changes.

| Rule | Text | Mechanism |
|---|---|---|
| (5) [O1] | **Derivation, not agreement.** Authenticity cannot be derived from mutually consistent candidate files. | `04` §3 |
| (6) [O2] | Authenticity does not imply eligibility, and floors are total and sound. Eligibility, security floors and install authority are rooted in T0 and the root-signed Trust Policy lineage, never in the kernel judged. Every file and leaf of the Constitutional Surface has exactly one floor semantics from a closed, compiled vocabulary. Unclassified content is denied. Registered content that is absent is refused, or resolves to a registered value or a typed refusal. Floors are joins. POLICY_PRECEDENCE must equal its registration exactly; the project layer's precedence comes only from registrations, applied as a directed join; the strength order that compares registrations is sound in both directions. **Non-join constitutional units (pinned leaves and members, member-id sets, pinned and migration files, owner binding groups) are fixed per registered release **by a registration whose content each custodian established first-hand**: exactly one value per unit per release, append-only; eligibility and effective values use only the registration of the release judged; presence is release-scoped. **For non-orderable units "down" means: a later registration that restores a superseded value, removes a unit or narrows a member set; these are computed reductions, computed by the verifier over every registration the effective Trust State references (`INCOMPLETE` when one is not held) and refused when undeclared. Every other change of a security-classified non-orderable unit is selected by the registration authority and listed in the per-project gate before security-relevant use (revision 6).** Exceptions never relax floor-, pinned-, members- or precedence-class keys or compiled-prefix keys. Values and admitted project strengthening move down only through a computed, cumulatively declared reduction accepted per project by a trust gate. | `19`, `23` §12 |
| (7) [O3] | Trust state is monotonic, anchors are satisfied by inclusion, and currency needs a proof. Negative facts are sticky; a lift needs certification, a trust-state reference and an attestation naming the negative. Absence is never positive. Trust-state minimums come only from the trust-state lineage; references elsewhere are release-local. Equivocations and forks are refused, and statements outside an anchored chain are never effective. Pins carry mandatory validity. Trust ingress and binary acceptance need a currency proof **that names the selected Trust State**. No surface says `current`. Time is used only for pin validity, the C3 window and owner-selected options; **on a machine with a verifier trust store every ingested non-future statement raises the clock high-water, and a statement refused as issued in the future makes clock-based proofs unusable (revision 6).** | `17`, `24` |
| (8) [O4] | The bytes verified are the bytes installed and enforced, in every unit of work of every process; **a binary is installed from the buffer its evaluator measured.** | `18`, `31` R-ADM-6 |
| (9) [O5] | Key purposes and statement types are domain-separated. **A production binary is accepted only by admission-predicate/1: a release registration at root threshold or a root-granted quorum of at least two keys, referenced by the selected Trust State, fixing source identity, input manifest, **build environments (established by first-hand environment reproduction from upstream-checked components; revision 6)**, final, targets and verification records **counted only for exactly the registered candidate and kernel (revision 6)**; at least two first-person reproductions by distinct reproducer keys that hold no other purpose, **under registered environments**, confirmed first-hand and free of conflict, **a conflict or REJECTED attestation removed only by the registration authority (revision 6)**; publication in the selected Trust State; the negative set; a resolving Trust Base Manifest at or above the accepted-TBM high-water; and a currency proof naming the selected state. No purpose signs a fact its signer did not establish; `release-artifact` and `build-attestation` are withdrawn; root versions pass the Fact Threshold Check.** Currency is never signed by the trust-state purpose. | `05`, `25`, `30` |
| (10) [O6] | Protected trust paths (`governance/trust/**`, occupation entries, the transaction area) are written only by the install transaction; **RoT-1 commands refuse a working directory inside them, including the transaction area, and the installation state is `COMPLETE` only when their closed entry sets hold; legacy litter in the transaction area is reported and inert (its journals are not VTS-registered) (revision 6).** | `18` §8–§9 |
| (11) [O7] | Incoming releases never define the authority required to install themselves, nor the actor levels used to check it. | `19` §8 |
| (12) [O8] | Pre-RoT binaries fail before any write on RoT-1 projects **for invocations rooted at the project** while the occupation layout is intact. The layout occupies every authority path and every no-install write or restore root of pre-RoT binaries with entries of the wrong type. **For invocations rooted in a subdirectory, every write under `governance/trust/**` or the occupation directory leaves a state that RoT-1 binaries treat as not `COMPLETE`, and every nested legacy install and stray `governance/spec` or `governance/views/spec` tree is reported (revision 6, LP-1s restated).** No binary interprets a format or layout it does not implement. Once occupation entries are removed, or pre-migration paths are restored by Git, RoT-1 binaries fail closed and report lost project strength where it was recorded (LR-2). | `26`, `18` §9, `13` |
| (13) | Statement facts only. | `07` §3 |
| (14) | No fallback on failure. | `04` §8 |
| (15) | Flags, environment and repository files cannot add trust: no anchors, confirmations, keys, policies, state, certification or eligibility. | `09` R-ENV |
| (16) | No self-validation: **no binary evaluates its own acceptance — first acceptance, CI image acceptance and legacy migration included — and no trust ceremony runs on a binary that an evaluator other than itself has not admitted on the machine; the evaluator of a first admission is selected by the code agreed across the OP-13 sources, never by one source (revision 6).** | `31` |
| (17) | Distinct facts, distinct authorities: **release authenticity, source selection, build-input and build-environment selection, constitutional-content selection, byte observation, verification result, certification state, publication, currency and eligibility are distinct facts with distinct selectors; `release-final` selects none of them, including constitutional content, which the registration authority derives first-hand (revision 6).** | `05` §5, `29` §4 |
| (18) | Authorisation for trust decisions is never a repository record **or a file the governed account can write**. Trust gates are answered only by local confirmations bound to the decision's digests (**and, for C3 kinds, a typed state fingerprint**), **or by protected, expiring decision pins**. Repository gate records are requests. | `27` |
| (19) | No trust ingress without an anchor and a currency proof **naming the selected state; first admission of a binary uses the first-contact manifest bound by a code agreed across the sources of the owner's OP-13 answer as its only selector of lineage, state and evaluator, with a compiled source quorum; the first-contact root that remains is stated with its computed minimum (revision 6)**; governed use without an anchor only as OP-7 allows. | `24`, `31` |
| (20) | Project-owned strength is recorded **as requirements over the effective policy and overlay** by every install transaction and gated overlay change. A weakening made outside a gated transaction, **by any change,** is reported, and security-relevant mutation is refused until a trust gate accepts it. No remedy clears it. **Migrations write only root-registered Overlay Surface targets.** | `26` §6, `23` §11 |
| (21) | Repository- and plugin-supplied commands that `gov` runs are write-confined **by an allow list** away from pins, the verifier trust store, trust paths, `PATH` directories, the running executable and shell start-up files, and run only after the unit of work's trust decisions; **code the account later runs unconfined is A3.** | `24` §3.5, `27` §3.3 |
| **(22)** | **Fact derivation and selection authority (FD-1).** Every input of a trust decision is a selector, a restrictor or a carrier in a **complete** compiled decision register (`decision-register/DECISION_REGISTER.yaml`; revision 6), every selector substitution of which is a strategy of the derivation calculator and every consequence statement of which is generated by it; every selector has authority and currency at least those the decision confers; a signature counts only for a fact its signer established first-hand; the artefact under judgement is never a selector or its own evaluator; a shortfall fails closed or is a stated, labelled, tested residual; minimum capability sets are computed, never argued. | `29` |
| **(23)** | **Independent admission.** A RoT-1 binary without an admission record **held in its protected verifier trust store** naming its own digest runs C0 only; C3 and ceremonies need a protected executable and record **(an effective uid of 0 is writable)**; **only a first admission (no store, or no admission record ever written in it)** starts a fresh verifier trust store, **and re-admission keeps it (revision 6)**; a genuine binary that holds its own revocation restricts itself as OP-15 decides. | `31` §4–§5 |
| **(24)** | **Append-only, single-valued registration.** A release is registered once, **with its content established first-hand by the registration authority (revision 6)**; a registration that changes a registered release, gives one sequence two releases, or registers several values for one unit is malformed and refused. | `23` §12, `30` R-REG-4, `34` |
| **(25)** | **First-contact root (revision 6).** On a machine with no prior trust, lineage, state, source quorum and evaluator are selected only through a first-contact manifest bound by a code agreed across the sources the owner's OP-13 answer names; the quorum is compiled and never read from the selected state; lineage comes from the typed value; the evaluator is bound to the selected state; the remainder is the first-contact root, stated with calculator-computed minima equal to executed results. | `32` |
| **(26)** | **Build environment established first-hand (revision 6).** Every byte-determining build input has a registered selector whose content is established first-hand (components against upstream signed checksums; environments by a first-hand reproduction quorum; reproducers re-assemble), or is the stated residual of the owner's OP-16 answer; the pipeline selects none. | `33` |
| **(27)** | **Root threshold and restrictor authority (revision 6).** Every root version has a root threshold of at least 2; a restrictor (a conflicting reproduction, a REJECTED attestation) is removed only by a revocation under the registration authority. | `05` §3, `25` AP-5r |

## 6. Record changes on approval (4.1.6 implementation, not now)

| Record / document | Change |
|---|---|
| `spec/decisions/D-0008.yaml` | status ACTIVE, `state_class: AUTHORITATIVE`, `in_effect: true`, `human_approved: true`, `chosen_option`, `supersedes: [D-0007]`, owner answers to OP-1…OP-16, ceremony appendix (public data: root, registration and reproducer keys, quorum, verifier and reproducer identities, admitter digest) |
| `spec/decisions/D-0007.yaml` | status SUPERSEDED, `superseded_by: [D-0008]` |
| `spec/architecture/ARCH-0002.yaml` | status ACTIVE |
| record schema | a `PROPOSED` status, or `in_effect: false` excluded from `RecordStore::active()` |
| `docs/ARCHITECTURE.md` §4.4a | integrity, authenticity, eligibility, surface, freshness distinguished; T0, T1-E, LA added |
| doctor | D030–D038 per `09` §5 |
| release/distribution protocol | statements, surface and precedence registration, attested source and custodial stages, binary acceptance, fingerprints (root and state), pin provisioning and validity, confinement, OP-6/OP-7 ceremony, retirement of legacy binaries |

## 7. Revision history

| Revision | Commit | Outcome |
|---|---|---|
| 1 | `676dfce` | review `1c6027c`: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` |
| 2 | `d37b05c` | review `e5a6b8a`: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (R2-H1…R2-H4, R2-M1…R2-M10, R2-L1…R2-L3) |
| 3 | `ca77a43` (AR-0001) | review `79a09a1`: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (RV3-H1…RV3-H3, RV3-M1…M9, RV3-L1…L8, RV3-I1) |
| 4 | `bca05a7` (AR-0005) | review `97a5545`: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (RV4-H1…RV4-H3) |
| 5 | `cdb4e14` (AR-0011) | review `d1228cb`: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (RV5-H1…RV5-H3, RV5-M1…M9, RV5-L1…L9, RV5-I1, I2) |
| 6 | this amendment (branch `phase1/rot1-r6-architect`, AR-0015) | pending fresh independent reviews; response matrix in `22` |
