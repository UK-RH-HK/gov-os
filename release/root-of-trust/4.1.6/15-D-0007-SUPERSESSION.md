# Output 15 — Supersession of D-0007

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved.**
> D-0007 is not edited. D-0008 remains PROPOSED until the owner answers its Human Decision Gate: record status field
> `PROVISIONAL`, `in_effect: false`, no `chosen_option`, `supersedes: []`.
>
> Revision 4 revises rules (3), (6), (7), (9), (12), (17), (18), (19) and (20), and adds rule (21). This follows review
> r3 `11-CORRECTION-DELTA.md` §5.

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

## 5. Rules (5)–(20)

The eight rules the owner required for revision 2 are marked [O1]…[O8]. **Bold** marks revision-4 changes.

| Rule | Text | Mechanism |
|---|---|---|
| (5) [O1] | **Derivation, not agreement.** Authenticity cannot be derived from mutually consistent candidate files. | `04` §3 |
| (6) [O2] | Authenticity does not imply eligibility, and floors are total **and sound**. Eligibility, security floors and install authority are rooted in T0 and the root-signed Trust Policy lineage, never in the kernel judged. Every file and leaf of the Constitutional Surface has exactly one floor semantics from a closed, compiled vocabulary. Unclassified content is denied. **Registered content that is absent is refused, or resolves to a registered value or a typed refusal.** Floors are joins. **POLICY_PRECEDENCE must equal its registration exactly; the project layer's precedence comes only from registrations, and a project override is applied as a directed join. The strength order that compares registrations is sound in both directions.** Exceptions never relax floor-, pinned-, members- or precedence-class keys or compiled-prefix keys. Values, **and admitted project strengthening,** move down only through a computed, cumulatively declared reduction accepted per project by a trust gate. | `19`, `23` |
| (7) [O3] | Trust state is monotonic, **anchors are satisfied by inclusion, and currency needs a proof.** Negative facts are sticky; a lift needs certification, a trust-state reference **and an attestation naming the negative**. Absence is never positive. Trust-state minimums come only from the trust-state lineage; references elsewhere are release-local. Equivocations and forks are refused, **and statements outside an anchored chain are never effective. Pins carry mandatory validity. Trust ingress and binary acceptance need a currency proof. No surface says `current`.** Time is used only for **pin validity, the C3 window** and owner-selected options, **and only witnesses raise the clock high-water**. | `17`, `24` |
| (8) [O4] | The bytes verified are the bytes installed and enforced, in every unit of work of every process. | `18` VU-1…VU-14 |
| (9) [O5] | Key purposes and statement types are domain-separated, and binary authenticity is its own purpose. Each type maps to one purpose; keys act only within granted purposes under a compiled pairwise whitelist. A production binary is accepted only with all of: `release-artifact` at threshold ≥ 2; an independent build attestation; a trust-state reference; a Trust Base Manifest resolving at or above the machine's **accepted-TBM** high-water; **and a source equal to the source an ACCEPTED independent verification attested for its candidate**. **A final names the same source as its candidate. Currency is never signed by the trust-state purpose.** | `05`, `25` |
| (10) [O6] | Protected trust paths (`governance/trust/**`, occupation entries, the transaction area) are written only by the install transaction. | `18` §8 |
| (11) [O7] | Incoming releases never define the authority required to install themselves, nor the actor levels used to check it. | `19` §8 |
| (12) [O8] | Pre-RoT binaries fail before any write on RoT-1 projects **while the occupation layout is intact**. The layout occupies every authority path and every no-install write or restore root of pre-RoT binaries with entries of the wrong type, so that no pre-RoT command changes a byte outside the runtime directory. No binary interprets a format or layout it does not implement. **Once occupation entries are removed, or pre-migration paths are restored by Git, RoT-1 binaries fail closed and report lost project strength where it was recorded (LR-2).** | `26`, `13` |
| (13) | Statement facts only. | `07` §3 |
| (14) | No fallback on failure. | `04` §8 |
| (15) | Flags, environment and repository files cannot add trust: no anchors, confirmations, keys, policies, state, certification or eligibility. | `09` R-ENV |
| (16) | No self-validation. | `05` SV-8, `23` §2 |
| (17) | Distinct facts, distinct authorities, including binary acceptance, **binary source** and currency. | `05` §5 |
| (18) | Authorisation for trust decisions is never a repository record **or a file the governed account can write**. Trust gates are answered only by local confirmations bound to the decision's digests (**and, for C3 kinds, a typed state fingerprint**), **or by protected, expiring decision pins**. Repository gate records are requests. | `27` |
| (19) | No trust ingress without an anchor **and a currency proof**; governed use without an anchor only as OP-7 allows. | `24` |
| (20) | Project-owned strength is recorded **as requirements over the effective policy and overlay** by every install transaction and gated overlay change. A weakening made outside a gated transaction, **by any change,** is reported, and security-relevant mutation is refused until a trust gate accepts it. No remedy clears it. **Migrations write only root-registered Overlay Surface targets.** | `26` §6, `23` §11 |
| **(21)** | **Repository- and plugin-supplied commands that `gov` runs are write-confined away from pins, the Verifier Trust Store and trust paths, and run only after the unit of work's trust decisions.** | `24` §3.5 |

## 6. Record changes on approval (4.1.6 implementation, not now)

| Record / document | Change |
|---|---|
| `spec/decisions/D-0008.yaml` | status ACTIVE, `state_class: AUTHORITATIVE`, `in_effect: true`, `human_approved: true`, `chosen_option`, `supersedes: [D-0007]`, owner answers to OP-1…OP-7, ceremony appendix (public data) |
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
| 4 | this amendment (branch `phase1/rot1-r4-architect`, AR-0005) | pending fresh independent reviews; response matrix in `22` |
