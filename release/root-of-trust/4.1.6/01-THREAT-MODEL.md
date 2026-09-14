# Output 1 — Root-of-Trust Threat Model

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 7 amendments (normative; certified profile CP-1, `35`; they supersede conflicting rows below): TA-5′ restated (both
> first-contact sources, their identities from the root ceremony record at onboarding, state codes); TA-7 restated (anchor
> validity 90/7 days, 24-hour currency and admission-state age, R-CLK-1); TA-12″ (supplier classes and toolchain lineages
> independent by registered provenance); TA-13 and TA-14 removed by exclusion (EX-05, EX-18); residuals restated for CP-1; threats
> TH-111…TH-119 (§6.5) for review r6's findings.
> Revision 6 amendments (normative; they supersede conflicting rows below): TA-5′ (first-contact procedure over the OP-13
> sources), TA-7 (clock high-water from every ingested non-future statement; future statements disable clock proofs),
> TA-10′ extended to environment reproducers, TA-12′, TA-13, TA-14; adversaries A20 restated, A21, A22; goals G23 restated,
> G24, G25; threats TH-101…TH-110 (§6.4); residuals for the first-contact root, the common-mode environment and RS-2b.
> Revision 5 amendments (normative; they supersede conflicting rows below):
> - **Assumptions.** TA-1 restated: the running `gov` was admitted on this machine by an evaluator other than itself
>   (`31`), or is a binary N+1 accepted by an admitted binary N. TA-5 restated: the operator reads the independent channels
>   now, types the state fingerprint (OP-13) and compares the admitter digest. New: **TA-1b** the platform hash tool (and,
>   under OP-12 (b), interpreter) on the first machine is genuine; **TA-10′** reproducers and registration custodians are
>   independent of each other and of the pipeline (not verifier-checkable); **TA-11** verification processes are honest
>   (OP-8 sets how many); **TA-12** the upstream toolchain release that passes the checksum check is not malicious (OP-10).
> - **Adversaries.** A16 (build host) includes reproducer environments; **A19** input-mirror and upstream-toolchain
>   attacker; **A20** independent-channel attacker (stale or forged channel page).
> - **Threats added:** TH-89 one attestation key plus pipeline (RV4-B-A01, A02, A06, D-A07) → `30`; TH-90 first binary
>   selected by transport or source host (RV4-B-A03, A04) → `31`; TH-91 ceremonies on an unadmitted binary (D-A04) → `31`
>   GB-1; TH-92 superseded non-orderable content restored by a later final (RV4-B-A08, D-A02, D-A06) → `23` §12; TH-93
>   subdirectory-rooted legacy writes (RV4-C-A01, D-A01, D-A09) → `18` §9; TH-94 persistence from confined children
>   (RV4-B-A05) → `27` §3.3; TH-95 witness input (RV4-B-A14) → `24` §3.3; TH-96 clock set back (RV4-B-A13) → `24` §8; TH-97
>   poisoned mirror / malicious named toolchain → `30` §4; TH-98 measured bytes differ from installed bytes → `31` R-ADM-6;
>   TH-99 reproduction laundering by rotation re-signing → `05` §8; TH-100 hash-bound owner contract set mixed across
>   versions (D-A08) → `23` §7.2.
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
| **G23** | **Clock-poisoning resistance** (restated in revision 6): no statement moves a verifier's clock high-water beyond the local clock plus the compiled skew; a far-future statement is refused at ingest and makes clock-based currency proofs unusable for that unit of work (`24` §8) |
| **G24** | **First-contact honesty** (revision 6): no first-contact value selects the rule that governs it (lineage, source quorum, evaluator); the first-contact root of the owner's OP-13 answer is stated with its computed minimum (`32`) |
| **G25** | **First-hand facts** (revision 6): every byte-determining build input and every registered constitutional unit is established first-hand by the registration authority, or is a stated residual (`33`, `34`) |

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
| **A19** | Input-mirror and upstream-toolchain attacker (revision 5) | serves inputs; publishes a malicious upstream toolchain release |
| **A20** | **First-contact source attacker** (restated in revision 6) | controls one or more first-contact sources: a stale or forged page, a code of a lineage it generated, a manifest naming a substituted admitter |
| **A21** | **Build-environment supplier** (revision 6) | publishes a malicious environment component with a valid upstream checksum |
| **A22** | **Second-path signing service** (revision 6; OP-13 (c)) | signs an attacker's admitter package |

## 4. Trust assumptions (TCB)

| ID | Assumption | Holds when |
|---|---|---|
| TA-1 | The running `gov` binary and its compiled T0 (TBM) are genuine | the binary was accepted by `verify-artifact` (`25` §5) or built from source at a verified tag |
| TA-2 | OS process isolation | always |
| TA-3 | SHA-256 and Ed25519 (strict) sound | always |
| TA-4 | Keys under `05` custody; fewer than threshold root keys compromised; compiled whitelist holds | always |
| TA-5′ | (Restated in revision 7.) The operator knows the identities of the two first-contact sources from the root ceremony record received at onboarding, performs the first-contact procedure over both, reading each now (`32` FC-1′…FC-3′), and types the state codes of both sources for human anchors and in-gate proofs | first admission (under the stated first-contact root, `32` §9, atoms `desig1`, `desig2`, `op1src`); OP-6 (a); human anchors |
| TA-6 | Secure-open, atomic-exchange and locking primitives present | production profile |
| TA-7 | The local clock is honest | (Restated in revision 7.) **only** for anchor and pin validity (90 days, CI 7 days), the 24-hour currency window and the 24-hour admission-state age. A clock below the machine's recorded high-water leaves C0-R (R-CLK-1); statements issued in the future are refused. Residuals RS-2 (no store) and RS-2b. |
| TA-8 | Non-trust Human Decision Gate answers come from humans; the acting role is caller-declared | documented limit (`27` §5) |
| **TA-9** (restated) | Pins and decision pins are provisioned by an operator the repository writer does not control, **and no process the repository writer controls runs, before `gov`'s trust decision, with an identity that can write the pin location** | whenever pins are used (`24` §3.5 (4)) |
| **TA-10** | The independent rebuilder's environment is not controlled by the release signers | `build-attestation` (`25`) |
| **TA-11** | The independent verifier reproduces the candidate from the source it attests, and its process is not controlled by the release signers | binary source legitimacy (`25` TB-4) |
| **TA-10′** | (Revision 5, extended in revision 6.) Reproducers, environment reproducers and registration custodians are independent of each other and of the pipeline | not verifier-checkable; ceremony record (CR5-B-02) |
| **TA-12″** | (Revision 7.) Not every registered toolchain lineage is compromised together and the compiler source is not malicious; not every registered supplier class is compromised together, and the classes share no provenance the root-signed registry does not show | OP-10 (b), OP-16 (b) (`33`); residual TB-S2″ |
| TA-12′ | (Revision 6; superseded by TA-12″ in CP-1.) | — |
| TA-13 | (Revision 6; removed by exclusion EX-05: no platform or distribution signing path exists in CP-1.) | — |
| TA-14 | (Revision 6; removed by exclusion EX-18: media carry the immutable mirror's material only, within 24 hours.) | — |

## 5. Out of scope and accepted residuals

| Residual | Reason | Bound | Defined in |
|---|---|---|---|
| A machine anchored before a revocation that never receives later metadata | offline verification | RS-1 core: C1–C2 at descendants of its anchor, shown with age and `CURRENCY_UNPROVEN`, never `current`, never C3 without a currency proof; RS-1b (C3 window) and RS-1c (pin validity) bounded | `24` §10 |
| Clock trust | machines without any store | RS-2 (a store fails closed below the high-water, R-CLK-1) | `24` §10 |
| A3 deletes or forges its own VTS, anchors or confirmations | same-user boundary | RS-3, TG-2 | `24`, `27` |
| Pins provisioned by a party the repository writer controls | outside TA-9 | RS-4 | `24` |
| A3 between units of work; ignored locks; non-`gov` subprocess writes | same-user boundary | VR-1…VR-3 | `18` §11 |
| Profile runtimes by path | Python/model runtime | VR-4 | `10` |
| Classification correctness; ceremony frequency | root-ceremony review | CS-1, CS-2 | `23` §10 |
| Binary is the TCB; rebuilder environment; minimum capability sets (route S and route B); insider source accepted by an honest verifier | TCB | TB-1…TB-4 | `25` §10 |
| Legacy binaries on unconverted working copies; occupation removed or pre-migration paths restored by Git (legacy verified install, legacy writes to `governance/trust/**` and the overlay); explicit output paths; fresh clones accept the overlay | by design, or no design stops Git restoring history | LR-1…LR-4; RoT-1 fails closed and strength loss is reported where recorded | `26` §8 |
| Non-trust gate records forgeable by A2 | TA-8 limit | TG-3 | `27` |
| Threshold root compromise | anchor compromise | re-bootstrap | `05` §9 |
| **The first-contact root** (restated in revision 7) | a machine with no prior trust accepts what both first-contact sources jointly present, or what look-alike sources an operator is directed to present | AD-1″ / FC-R1′: the sets of CP-FC-ROOT, computed and executed equal; CUR-R1 within 24 hours | `32` §9, §12 |
| **Common-mode build environment and toolchain** (restated in revision 7) | every supplier class or toolchain lineage compromised together, hidden common provenance, or the compiler source | TB-S2″, TA-12″ (CP-ENV, CP-TOOLCHAIN) | `33` §8 |
| **Restored store with the clock set back and every newer statement withheld** (revision 6) | the machine cannot distinguish the past | RS-2b | `24` §10 |

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

### 6.4 Threats added in revision 6 (review r5 classes and held-out attacks)

| ID | Threat | Adversary | Control | Evidence / tests |
|---|---|---|---|---|
| TH-101 | **One first-contact source selects the lineage, the source quorum and the evaluator** (RV5-H1; B-A01, B-A02, D-A02) | A20 | first-contact code and manifest; FC-1…FC-8; the stated first-contact root (OP-13) | FA6 S2, S3, S7; CS6 FC-ROOT; RT-156…RT-159 |
| TH-102 | **The build environment selects the bytes of every reproducer** (RV5-H2; B-A08) | A16, A21, pipeline | environments registered and reproduced first-hand from upstream-checked components (R-BENV-1…6); OP-16 | ENV6; CS6 G_ENV; RT-160…RT-162 |
| TH-103 | **CI-derived registered content and attestations reused across candidates** (RV5-H3; D-A01, D-A05, B-A06) | A7 ×2 + pipeline | R-CON-1…R-CON-5; AP-5 binding; E7 restrictors | CON6; P4r6 G; CSI S71–S77; RT-163…RT-167 |
| TH-104 | **A trust-state key removes restrictors** (RV5-M1; B-A03, B-A07) | A7 | AP-5r; R-REG-11 | P4r6 AP5r; FA6 S5; RT-168 |
| TH-105 | **Undeclared or non-identical registration changes** (RV5-M2; B-A09, B-A10) | registration authority | R-CON-4 at the verifier; R-CON-5 per-project listing | CON6; CSI S73–S76; RT-166, RT-167 |
| TH-106 | **Re-admission discards the monotonic store; concurrent admissions** (RV5-M3; C-A09…A11, B-A13) | operator procedure | R-ADM-8′, R-ADM-13 | ADM6; FA6 S6; RT-170, RT-181 |
| TH-107 | **Ambiguous source identity** (RV5-M4; B-A05) | A1 | source identity v2 | SRC6; RT-172 |
| TH-108 | **Line-ending conversion and out-of-project ignore sources** (RV5-M6, RV5-M7; C-A05, C-A06) | ordinary user | `.gitattributes` member; stated conditions with detection | LAY6 gitops; ATTR6; RT-173, RT-174 |
| TH-109 | **Shipped admission record; jobs as root** (CR5-B-07, CR5-B-12; B-A15) | package, A2 | GB-1′, GB-6 | FA6 S6; ADM6 A15; RT-171 |
| TH-110 | **Restored store with the clock set back** (CR5-B-08; B-A12) | A13 | future statements disable clock proofs; RS-2b | P4r6 CLOCK; RT-178 |

### 6.5 Threats added in revision 7 (review r6 classes and held-out attacks)

| ID | Threat | Finding | Control | Evidence |
|---|---|---|---|---|
| TH-111 | The trust-state publication process composes first-contact values both sources carry | RV6-H1, RV6-B-A01 P | First-Contact Authority record at root threshold; codes published only after each source custodian's first-hand verification (`32` R-FCA, R-FCS) | FA7 S2 P |
| TH-112 | A carrier or unadmitted binary designates the sources or prints the procedure | RV6-H1, RV6-D-A01 | designation from the root ceremony record at onboarding; no `gov trust fc-procedure` command (`32` R-FCD; EX-24) | FA7 S2 D |
| TH-113 | A package submitter selects the admitter under a platform signing path | RV6-H1, RV6-B-A06 | excluded (EX-05) | FA7 S2 X; PROF7 |
| TH-114 | A replayed, stored or designated first-contact value selects a stale state | RV6-H2, RV6-D-A08 | compiled 24-hour state age on every path (`32` FC-9) | CUR7 R, A08, S2 |
| TH-115 | Re-admission ignores the store's anchors, negatives and high-waters | RV6-H2, RV6-D-A02, RV6-L5 | AP-R1…AP-R6 and GB-7 (`31`) | CUR7 A02, A04 |
| TH-116 | The environment manifest's author, a supplier label or a manifest-named key selects bytes | RV6-H3, RV6-B-A02 | lock in registered source; derived manifests; pinned registry; provenance independence (`33`) | ENV7 |
| TH-117 | A planted account-store record decides first admission | RV6-M6, RV6-D-A07 | the protected admission store decides (`31` R-STORE-2) | ADM7 A07 |
| TH-118 | A selector outside the register's rule ids; a renderer merging atom classes | RV6-M2, RV6-M1 | register over every input (`29` C9–C11); atom-level statement checks (S1a, S3) | DA09r7; DA06r7 |
| TH-119 | A clock set back below the recorded high-water on an anchored machine keeps a revoked release usable | A-R7-07 (BA11r7) | R-CLK-1 (`24` §4.5) | ADM7 CLK; BA11r7 |
