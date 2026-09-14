# Output 1 — Root-of-Trust Threat Model

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 restates goals and assumptions from the review-r3 findings, and adds threats TH-67…TH-88 for every review-r3
> finding and held-out attack class:
> - G17, G18, G19 and G21 restated; G22 (anchor and approval integrity) and G23 (clock-poisoning resistance) added;
> - TA-7 limited to pins, the C3 window and owner-selected options; TA-9 restated to cover integrity after provisioning;
>   TA-11 (independent verification of source) added;
> - AS-19 (source identity) and AS-20 (currency evidence) added;
> - A18 (repository-controlled code executed by `gov`) added.

## 1. Assets

| ID | Asset | Why it is privileged |
|---|---|---|
| AS-1 | **Constitutional Surface.** Every file and leaf of the release kernel payload: policies, ROLES, hard invariants, precedence, schemas (formerly AS-2), agent-facing content (formerly AS-4), tool registry (formerly AS-5), command contract, taxonomies, overlay templates, `KERNEL.yaml` | decides what is indexed, exported, gated, executable, by whom, and what agents are told (`23`) |
| AS-3 | Framework migrations | declaratively mutate the overlay during update |
| AS-6 | Release identity: release and artefact statements | decide which content and binaries are authentic |
| AS-7 | Trust-root metadata, purpose grants, private signing keys | the anchor |
| AS-8 | `governance/trust/**` including lock 3.0.0 | the consumer's record of what was adopted |
| AS-9 | The `gov` binary and its **Trust Base Manifest** | carries T0; the trusted computing base (`25`) |
| AS-10 | Reference retrieval profile | determines what semantic memory returns |
| AS-11 | Project data classified `restricted` or `secret` | the harm target |
| AS-12 | **Trust Policy**: Constitutional Surface Inventory, eligibility, historical releases, install authority, gating, bootstrap, lowering history | decides which authentic release may govern and what it may contain |
| AS-13 | **Lifecycle state**: Trust State, certification, attestations, revocations, build attestations | certification visibility, refusal, binary acceptance |
| AS-14 | **Verifier Trust Store**: knowledge, high-water, **anchors**, per-project records, **trust-gate confirmations** | per-machine monotonic state (`24` §8) |
| AS-15 | Protected Path Set, **occupation entries**, transaction area | the only place installed trust state is written; the legacy-binary barrier (`26`) |
| AS-16 | **Pins**: root, state and decision pins in the account configuration | operator-provisioned anchors and approvals (TA-9) |
| AS-17 | **Build inputs and reproduction record** | tie binary bytes to tagged source (`build-attestation`) |
| AS-18 | **Project-strength vector** | detects silent removal of project-owned strengthening (`26` §6) |
| **AS-19** | **Source identity and verification record**: `release.source`, verification attestations v2 | decides which source a production binary may be built from (`25` §5.1) |
| **AS-20** | **Currency evidence**: pin validity, in-gate confirmations, freshness witnesses, the clock high-water | decides whether a machine may perform trust ingress (`24` §4.4) |

## 2. Security goals

| ID | Goal |
|---|---|
| G1 | **Ingress authenticity**: nothing privileged is staged, installed, restored or executed unless bound by a statement verified under T0 for the right purpose |
| G2 | **Use-time integrity**: enforcement reads only verified snapshot bytes |
| G3 | **No self-certification**: certification, compatibility, gate requirements and identity come only from signed statements |
| G4 | **Replay and downgrade resistance** |
| G5 | **Offline verifiability** |
| G6 | **Compromise and loss recoverability** |
| G7 | **Fail closed, typed** |
| G8 | **No masquerade** of development or test material |
| G9 | **Transport independence** |
| G10 | **Single boundary** |
| G11 | **Currency**: authenticity never implies eligibility; eligibility and floors come from T0 and the root-signed Trust Policy lineage, never from the candidate; floors never move down except by a computed, declared, per-project-gated lowering |
| G12 | **Byte binding**, including every unit of work of a long-lived process |
| G13 | **Monotonic lifecycle state**: omission or replay never relaxes or forgets; minimums only from the trust-state lineage |
| G14 | **Purpose separation**: compiled whitelist |
| G15 | **Protected paths** |
| G16 | **Legacy containment**: no pre-RoT binary writes a byte of a RoT-1 project outside its runtime directory |
| **G17** | **Surface totality and soundness**: every constitutional file and leaf has floor semantics; unknown content is denied; **registered content that is absent is refused**; the project layer's precedence comes only from registrations; no change removes admitted project strengthening without a computed reduction and a per-project gate |
| **G18** | **Freshness honesty**: an anchor is satisfied only by inclusion; no surface says `current`; trust ingress needs a currency proof; governed use without an anchor only per OP-7 |
| **G19** | **Binary authentication at least as strong as carried authority, including the source**: a production binary is built from source that an independent verification accepted |
| **G20** | **Trust decisions are local**: no repository record authorises a trust decision |
| **G21** | **Project strength over effective policy**: silent loss of recorded project-owned strength, through any change, is reported before security-relevant mutation resumes |
| **G22** | **Anchor and approval integrity**: no process the repository writer controls can write an honoured pin or decision pin, and no stale pin or single witness key yields trust ingress |
| **G23** | **Clock-poisoning resistance**: no statement can move a verifier's clock high-water forward except a verified witness; far-future statements are refused |

## 3. Adversaries

| ID | Adversary | Capability |
|---|---|---|
| A1 | Source controller | arbitrary bytes at a source; any subset of genuine statements |
| A2 | Repository writer (collaborator, CI token, agent with commit rights, merged PR) | arbitrary tracked files, including `governance/**`, `spec/**`, gate records, symlinks, and CI job definitions stored in the repository |
| A3 | Local same-user process (including plugins and tool subprocesses) | anything the user can do: VTS, runtime directory, installed files, pseudo-terminals |
| A4 | Environment manipulator | environment variables, working directory, arguments |
| A5 | Transport attacker | arbitrary download bytes |
| A6 | Canonical-repository insider | malicious commit reaching a build |
| A7 | Thief of one non-root purpose key | signs statements of that purpose |
| A8 | Root threshold compromise | re-roots trust |
| A9 | Replay and downgrade attacker | serves genuine old, revoked, rejected or legacy material |
| A10 | Social engineer | persuades an operator |
| A11 | Model or package supply-chain attacker | substitutes weights or packages |
| A12 | Trust-metadata withholder | serves stale genuine metadata (specialises A1, A2, A5) |
| A13 | Clock manipulator | sets the local clock |
| A14 | Legacy-binary operator | runs 4.1.2–4.1.5 against a RoT-1 project |
| A15 | Fork distributor | ships a binary with a substituted root |
| **A16** | **Build-host attacker** | controls a build machine or toolchain producing release binaries |
| **A17** | **Unanchored verifier operator** | runs `gov` on a fresh machine or clean CI runner without provisioning an anchor |
| **A18** | **Repository-controlled code executed by `gov`** (product and test commands, tool commands, plugins, hooks) | runs as the invoking account unless confined; can write any file that account can write |

## 4. Trust assumptions (TCB)

| ID | Assumption | Holds when |
|---|---|---|
| TA-1 | The running `gov` binary and its compiled T0 (TBM) are genuine | the binary was accepted by `verify-artifact` (`25` §5) or built from source at a verified tag |
| TA-2 | OS process isolation | always |
| TA-3 | SHA-256 and Ed25519 (strict) sound | always |
| TA-4 | Keys under `05` custody; fewer than threshold root keys compromised; compiled whitelist holds | always |
| TA-5 | A human compared the lineage id and the state fingerprint with a channel independent of the release host | OP-6 (a), (c); human anchors |
| TA-6 | Secure-open, atomic-exchange and locking primitives present | production profile |
| TA-7 | The local clock is honest | **only** for pin validity, the C3 currency window, OP-3 mode B, OP-7 (b) and (c); the clock high-water is raised only by witnesses |
| TA-8 | Non-trust Human Decision Gate answers come from humans; the acting role is caller-declared | documented limit (`27` §5) |
| **TA-9** (restated) | Pins and decision pins are provisioned by an operator the repository writer does not control, **and no process the repository writer controls runs, before `gov`'s trust decision, with an identity that can write the pin location** | whenever pins are used (`24` §3.5 (4)) |
| **TA-10** | The independent rebuilder's environment is not controlled by the release signers | `build-attestation` (`25`) |
| **TA-11** | The independent verifier reproduces the candidate from the source it attests, and its process is not controlled by the release signers | binary source legitimacy (`25` TB-4) |

## 5. Out of scope and accepted residuals

| Residual | Reason | Bound | Defined in |
|---|---|---|---|
| A machine anchored before a revocation that never receives later metadata | offline verification | RS-1 core: C1–C2 at descendants of its anchor, shown with age and `CURRENCY_UNPROVEN`, never `current`, never C3 without a currency proof; RS-1b (C3 window) and RS-1c (pin validity) bounded | `24` §10 |
| Clock trust | owner-optional | RS-2 | `24` §10 |
| A3 deletes or forges its own VTS, anchors or confirmations | same-user boundary | RS-3, TG-2 | `24`, `27` |
| Pins provisioned by a party the repository writer controls | outside TA-9 | RS-4 | `24` |
| A3 between units of work; ignored locks; non-`gov` subprocess writes | same-user boundary | VR-1…VR-3 | `18` §11 |
| Profile runtimes by path | Python/model runtime | VR-4 | `10` |
| Classification correctness; ceremony frequency | root-ceremony review | CS-1, CS-2 | `23` §10 |
| Binary is the TCB; rebuilder environment; minimum capability sets (route S and route B); insider source accepted by an honest verifier | TCB | TB-1…TB-4 | `25` §10 |
| Legacy binaries on unconverted working copies; occupation removed or pre-migration paths restored by Git (legacy verified install, legacy writes to `governance/trust/**` and the overlay); explicit output paths; fresh clones accept the overlay | by design, or no design stops Git restoring history | LR-1…LR-4; RoT-1 fails closed and strength loss is reported where recorded | `26` §8 |
| Non-trust gate records forgeable by A2 | TA-8 limit | TG-3 | `27` |
| Threshold root compromise | anchor compromise | re-bootstrap | `05` §9 |

## 6. Threat register

### 6.1 Revision 1 and revision 2 threats (controls as in revision 3)

| ID | Threat | Adversary | Revision 3 control | Tests (`12`) |
|---|---|---|---|---|
| TH-01 | Tampered source with stale manifests installs as verified | A1 | V1/V9 blob digests | RT-01, RT-02 |
| TH-02 | Regenerated manifests | A1 | statement digests only | RT-13 |
| TH-03 | Source self-certifies to skip a gate | A1 | manifests never read; mode A trust gate | RT-13, RT-25, RT-35 |
| TH-04 | Forged statement | A1, A5 | SV-6 | RT-03, RT-05 |
| TH-05 | Wrong-purpose key | A7 | SV-5/SV-6, compiled whitelist | RT-04, RT-46 |
| TH-06 | Statement paired with other content | A1, A9 | V8, V9, snapshot compare | RT-09, RT-10, RT-51 |
| TH-07 | Downgrade | A9 | E3/E4/E9/E10, downgrade trust gate | RT-11, RT-33, RT-34, RT-52 |
| TH-08 | Coherent kernel + trust + lock replacement via Git | A2 | use-time authenticity, E7 surface, eligibility, freshness | RT-07b, RT-26, RT-31, RT-32 |
| TH-09 | Poisoned embedded cache | A3, A4 | no cache | RT-17, RT-45 |
| TH-10 | Tampered rollback snapshot | A3 | authenticated restore | RT-18, RT-44 |
| TH-11 | Environment redirection | A4 | account database; source selection only | RT-19, RT-64 |
| TH-12 | Tampered migration | A1 | V10; computed weakenings trust-gated | RT-08, RT-53, RT-54 |
| TH-13 | Installed kernel edited after install | A2, A3 | snapshot per unit of work | RT-07, RT-42 |
| TH-14 | Readers bypass the boundary | A2, A3 | GovernedFs read guard | RT-27 |
| TH-15 | Interrupted install | crash | journal + VTS registry | RT-16 |
| TH-16 | Source changed between check and copy | A1, A3 | read once | RT-22, RT-40 |
| TH-17 | Parser differential | A1 | SV-1, SV-3 | RT-23 |
| TH-18 | Development or test as production | A10, A4 | profiles; separate binary | RT-14, RT-68 |
| TH-19 | Private key committed | A6 | producer refusal | RT-24 |
| TH-20 | Substituted model or plugin | A11, A3 | profile statement; host verification | RT-15, RT-67 |
| TH-21 | Malicious commit becomes a signed release | A6 | reproduce-and-sign; attestation; separate certification; surface registration by root threshold | procedural, RT-62 |
| TH-22 | Stolen `release-final` key signs malicious releases | A7 | E7 (registered surface, exact precedence, presence); local trust gate at ingress; cannot sign binaries or choose a binary's source (V8) | RT-20, RT-73, RT-115 |
| TH-23 | Root rollback or single-key re-rooting | A7, A8 | dual-threshold chain | RT-21 |
| TH-24 | Genuine older, legacy or rejected release lowers floors | A2, A3, A9 | E1, E7 surface, joins over the whole surface, TPS historical releases | RT-31…RT-34, RT-70 |
| TH-25 | Stale CERTIFIED replay | A1, A12 | mode A; freshness proof in mode B | RT-35 |
| TH-26 | REJECTED omitted | A1, A12 | absence never positive; trust gate | RT-36 |
| TH-27 | Revocation or trust metadata stripped | A2, A4, A12 | knowledge union; anchors; OP-7 | RT-37, RT-64, RT-80 |
| TH-28 | Root rotation stripped | A2, A12, A7 | unresolved TSS → `INCOMPLETE`; anchors | RT-38 |
| TH-29 | Signed trust-state regression | A7 | admissibility with `prior_states` | RT-60 |
| TH-30 | Purpose confusion | A7, A1 | compiled table, whitelist | RT-39, RT-46, RT-47 |
| TH-31 | Verified bytes ≠ enforced bytes | A3 | VU-1…VU-13 | RT-41, RT-42 |
| TH-32 | Unregistered writers of protected paths | A2, A3 | GovernedFs; OS-level tracing | RT-48 |
| TH-33 | Partial-install fail-open | A2, A3 | installation state machine including occupation | RT-43, RT-81 |
| TH-34 | Incoming release defines its install authority or actor levels | A1 | install-authority floor; ROLES floors (`19` §8) | RT-49, RV2-A01 |
| TH-35 | Pre-RoT binary interprets or writes a RoT-1 project | A14, A2 | legacy-path occupation; LP-1 (`26`) | RT-50 |
| TH-36 | Signed migration removes project strengthening | A6, A7 | computed weakening + trust gate | RT-53, RT-54 |
| TH-37 | First install from a compromised release host | A5 + A6, A15 | independent channels; OP-6 + state anchoring; `verify-artifact` | RT-65, RT-66 |
| TH-38 | Clock manipulation | A13 | clock used only for pins, the C3 window, mode B and OP-7 (b)/(c); witness-only high-water; SV-11 | RT-56, RT-113 |
| TH-39 | Forged install journal | A3, A2 | VTS open-transaction registry; foreign artefacts ignored | RT-58, RV2-A24 |
| TH-40 | Profile runtime substituted at use | A3, A11 | host-side digests | RT-67 |
| TH-41 | Test profile unified into production | A6 | separate binary; TBM profile | RT-68 |
| TH-42 | Candidate installed as production | A1, A9 | E2 | RT-63 |
| TH-43 | Certification forged with a single key | A7 | three purposes, pairwise non-shareable | RT-61, RT-62 |

### 6.2 Threats added in revision 3 (review r2 classes and held-out attacks)

| ID | Threat | Adversary | Control | Evidence / tests |
|---|---|---|---|---|
| TH-44 | **Authentic release weakens an unfloored constitutional leaf** (ROLES levels, secret patterns, gate resolution, precedence attributes, invariant text, change gating, memory namespaces, schemas, tools) | A7+A2, future or older release | Constitutional Surface default deny; E7; joins (`23`, `19`) | P1r3; CSI selftest; RV2-A01…A08 |
| TH-45 | **Future constitutional key or file introduced without floor semantics** | A6, A7 | default deny; consumer register; `floor_schema_version` | CSI S01–S03, S19; RT-74 |
| TH-46 | **Precedence reordering or re-scoping weakens a key** | A7+A2 | per-key lattice | CSI S12–S14; RV2-A05 |
| TH-47 | **Exception relaxes a floor or security key** | A2+A7 | exceptions after join; compiled prefixes; registered ∧ kernel | P1r3 part 2; RV2-A04 |
| TH-48 | **Repository writer selects older genuine state for a stateless verifier** | A2, A12 | anchors; C3 refused unanchored; OP-7 | P4r3 B5, M2, M5; RV2-A09…A12 |
| TH-49 | **Clean CI runner without an anchor performs governed mutation** | A2, A17 | OP-7 (a)–(c) refuse; pins (TA-9) | P4r3 M2 |
| TH-50 | **Restored or long-absent machine treated as current** | A12 | anchor age shown; OP-7 (b)/(c) limits | P4r3 M3, M7 |
| TH-51 | **Witness replay or minting** | A1, A13, A7 | separate `freshness-witness` purpose; C3 threshold 2; names the effective TSS; validity bound; highest witness `issued_at` | P4r4 R2, RV3-B-A06; RT-98, RT-104 |
| TH-52 | **Non-trust-state purpose asserts global minimums** (reference inflation) | A7 | minimums only from the trust-state lineage; release-local references | P4r3 B1; RV2-A15 |
| TH-53 | **Unresolvable trust-state references freeze honest successors** | A7 | resolution before admissibility | P4r3 B4; RV2-A16 |
| TH-54 | **Certification key alone lifts WITHDRAWN** | A7 | MS-2 lifting rule | P4r3 B2; RV2-A17 |
| TH-55 | **Trust-state or policy equivocation and forks** | A7 | S3/S4 equivocation, `prior_states`, anchor orphans | P4r3 B3, E1–E3, R5; RV2-A18, A19 |
| TH-56 | **Lowering across a skipped policy version** | owner error, A8 | computed reductions; cumulative `lowering_history` | P4r3 B6; RV2-A20 |
| TH-57 | **Release key or build host mints a malicious binary** | A7, A16 | `release-artifact` ≥ 2, build attestation, attested source, TSS reference, TBM resolution | P4r4 A27–A27e; VA4; RV2-A27 |
| TH-58 | **Genuine older binary presented as an upgrade** | A5 | TBM high-water (`BINARY_T0_ROLLBACK`) | P4r3 A28; RV2-A28 |
| TH-59 | **Candidate key signs binaries under OP-4 "no"** | A7 | separate purpose | P4r3 A29; RV2-A29 |
| TH-60 | **Separation gap: one key spans trust-state and certification** | owner error | compiled whitelist, KS-8 | P4r3 K1…K3; RV2-A30 |
| TH-61 | **Pre-RoT adoption stages or residue write a RoT-1 project** | A14 | occupation of `spec/audits/GOVERNANCE-ADOPTION`, `.governance-runtime/migration` | P3r3 (L3 vs L3A); G1; RV2-A35 |
| TH-62 | **Gate record committed or written by a plugin authorises a trust decision** | A2, A3 | local trust-gate confirmation (`27`) | P4r3 R3; RV2-A13, A14 |
| TH-63 | **Long-lived process enforces a superseded snapshot** | A7, honest update | VU-11 | RV2-A21 |
| TH-64 | **Agent follows a rewritten adapter body** | A2 | adapters carry pointers; VTS rendering record | RV2-A22 |
| TH-65 | **Committed journal, dropped trust statements, weakened `overlay.prev`** | A2, A3, honest rollback | foreign artefacts; union PTR; weakening gate | RV2-A24…A26 |
| TH-66 | **Hard-linked staged file** | A3 | `st_nlink == 1` | RV2-A23 |

### 6.3 Threats added in revision 4 (review r3 classes and held-out attacks)

| ID | Threat | Adversary | Control | Evidence / tests |
|---|---|---|---|---|
| TH-67 | **A kernel precedence change removes admitted project strengthening** (RV3-B-A01) | A7+A2 | exact precedence registration; effective precedence from registrations only; directed join | P1r4 parts A–B; rerun RV3-B-A01; RT-106 |
| TH-68 | **A deleted registered constitutional file changes semantics** (RV3-D-A10) | A7+A2 | required presence; `SURFACE_VALUE_UNAVAILABLE` | P1r4 A3 and R07; CSI S31–S40; RT-107 |
| TH-69 | **A root-signed TPS tightening silently removes project strengthening** (RV3-D-A02) | honest owner, A8 | two-directional order; computed reduction; per-project gate | P1r4 A4 and part B; RT-108 |
| TH-70 | **A release-signed migration writes unregistered overlay targets** (RV3-B-A18) | A7 | Overlay Surface whitelist; strength vector | P1r4 part C; RT-109 |
| TH-71 | **Parser differential between checker and runtime** (RV3-B-A14) | A7 | one YAML profile | rerun RV3-B-A14; CSI S41–S43; RT-110 |
| TH-72 | **A security decision point reads a tunable key** (RV3-B-A16) | A7+A2 | CR-07 reclassification; consumer register | rerun RV3-B-A16; CSI S44; RT-111 |
| TH-73 | **A higher unchained TSS satisfies an anchor by number** (RV3-B-A12, D-A12) | A2/A5 + A7 `trust-state` | inclusion anchors | P4r4; mutant `M-sequence-anchor`; RT-105 |
| TH-74 | **A stale pin anchors a CI runner indefinitely** (RV3-B-A02) | A2/A5 | mandatory pin validity; currency proof | P4r4 RV3-B-A02, PIN_WINDOW; RT-102 |
| TH-75 | **One threshold-1 key mints witnesses** (RV3-B-A06) | A7 | `freshness-witness` purpose, KS-11, C3 threshold 2 | P4r4 RV3-B-A06; RT-104 |
| TH-76 | **An aged anchor admits a revoked binary or C3** (RV3-D-A15) | A2/A5 | currency proof for C3 and A9 | P4r4 RV3-D-A15, INGATE; RT-101 |
| TH-77 | **Pins or decision pins written by governed-account processes, including `gov`-run commands** (RV3-B-A03, A04) | A2, A3, A18 | integrity predicate; confined execution; TA-9 restated | rerun RV3-B-A03; P4r4; RT-103 |
| TH-78 | **A far-future statement poisons the clock high-water** (RV3-B-A07) | A7 | SV-11; witness-only high-water; root-signed reset | P4r4 RV3-B-A07; RT-113 |
| TH-79 | **A lift reuses a pre-negative attestation** (RV3-B-A05) | A7 ×2 | `lifts_negative_statement_digest` | P4r4 RV3-B-A05; RT-112 |
| TH-80 | **The artefact playbook freezes verifiers** (RV3-B-A09) | honest owner | revoke, never un-reference | P4r4 RV3-B-A09; RT-114 |
| TH-81 | **A threshold-1 final chooses the binary's source** (RV3-B-A08, D-A03) | A7 + A5/A6 | V8 source equality; A4b attested source; custodial stages; OP-2 source authority | VA4; RT-115 |
| TH-82 | **Realisable binaries refused against the TSS high-water** (RV3-D-A13) | none (availability) | accepted-TBM high-water | P4r4 A_valid, RV3-D-A13; RT-116 |
| TH-83 | **Rotation invalidates anchored honest history** (RV3-D-A16) | honest owner | re-signing playbook | P4r4 RV3-D-A16; RT-117 |
| TH-84 | **Reinstall identity taken from the lock** (RV3-B-A15) | A2 | VTS per-project record (CR-09) | design; RT-118 |
| TH-85 | **Non-surface TPS lowering without a gate** (RV3-B-A17) | A8, owner error | CR-10 computed reductions | P4r4 CR-10; RT-108 |
| TH-86 | **Occupation removal or a Git restore gives a legacy binary a verified install** (RV3-M6; C A04–A06; D-A05, A06) | A2, A14, ordinary user | LR-2 restated; RoT-1 fails closed; strength vector over effective policy | rerun of D-A05…A07; LR2; RT-81, RT-50b |
| TH-87 | **Untracking ignored files drops the migration occupation** (RV3-D-A07) | ordinary maintainer | ignore-rule negation | rerun of D-A05…A07 on the revision-4 layout; LR2; RT-122 |
| TH-88 | **An owner-supplied constitutional file is absent or replaced** (RV3-D-A18) | A2 | owner-domain slots; presence; strength vector | CSI S50–S52; RT-120 |
