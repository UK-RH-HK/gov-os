# Output 1 — Root-of-Trust Threat Model

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 expands the constitutional asset to the whole Constitutional Surface (R2-H1). It also adds:
> - freshness honesty and anchors (R2-H2);
> - binary and trust-base authenticity (R2-H3);
> - legacy-binary containment (R2-H4);
> - local trust-gate authorisation (R2-M1);
> - threats TH-44…TH-66 for every review r2 finding and held-out attack class.

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
| **G17** | **Surface totality**: every constitutional file and leaf has floor semantics; unknown constitutional content is denied |
| **G18** | **Freshness honesty**: unanchored knowledge is never presented or used as current for trust ingress; governed use without an anchor only per OP-7 |
| **G19** | **Binary authentication at least as strong as carried authority** |
| **G20** | **Trust decisions are local**: no repository record authorises a trust decision |
| **G21** | **Project strength**: silent weakening of recorded project-owned strengthening is reported before security-relevant mutation resumes |

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

## 4. Trust assumptions (TCB)

| ID | Assumption | Holds when |
|---|---|---|
| TA-1 | The running `gov` binary and its compiled T0 (TBM) are genuine | the binary was accepted by `verify-artifact` (`25` §5) or built from source at a verified tag |
| TA-2 | OS process isolation | always |
| TA-3 | SHA-256 and Ed25519 (strict) sound | always |
| TA-4 | Keys under `05` custody; fewer than threshold root keys compromised; compiled whitelist holds | always |
| TA-5 | A human compared the lineage id and the state fingerprint with a channel independent of the release host | OP-6 (a), (c); human anchors |
| TA-6 | Secure-open, atomic-exchange and locking primitives present | production profile |
| TA-7 | The local clock is honest | **only** under OP-3 mode B, OP-7 (b), OP-7 (c) |
| TA-8 | Non-trust Human Decision Gate answers come from humans; the acting role is caller-declared | documented limit (`27` §5) |
| **TA-9** | Pins (root, state, decision) are provisioned by an operator the repository writer does not control | whenever pins are used |
| **TA-10** | The independent rebuilder's environment is not controlled by the release signers | `build-attestation` (`25`) |

## 5. Out of scope and accepted residuals

| Residual | Reason | Bound | Defined in |
|---|---|---|---|
| A machine that never receives newer metadata | offline verification | RS-1, restated exactly: bounded by the compiled T0, retained anchor or pin, and witness; no governed mutation when unanchored under OP-7 (a)–(c) | `24` §10 |
| Clock trust | owner-optional | RS-2 | `24` §10 |
| A3 deletes or forges its own VTS, anchors or confirmations | same-user boundary | RS-3, TG-2 | `24`, `27` |
| Pins provisioned by a party the repository writer controls | outside TA-9 | RS-4 | `24` |
| A3 between units of work; ignored locks; non-`gov` subprocess writes | same-user boundary | VR-1…VR-3 | `18` §11 |
| Profile runtimes by path | Python/model runtime | VR-4 | `10` |
| Classification correctness; ceremony frequency | root-ceremony review | CS-1, CS-2 | `23` §10 |
| Binary is the TCB; rebuilder environment; four-key binary compromise | TCB | TB-1…TB-3 | `25` §9 |
| Legacy binaries on unconverted working copies; A3 removes occupation; explicit output paths; fresh clones accept the overlay | by design or same-user boundary | LR-1…LR-4 | `26` §8 |
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
| TH-22 | Stolen `release-final` key signs malicious releases | A7 | E7 (only root-registered surfaces become policy roots); local trust gate at ingress; cannot sign binaries | RT-20, RT-73 |
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
| TH-38 | Clock manipulation | A13 | clock only in mode B, OP-7 (b)/(c); rollback detection | RT-56 |
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
| TH-51 | **Witness replay** | A1, A13 | highest witness `issued_at`; expiry | P4r3 R2 |
| TH-52 | **Non-trust-state purpose asserts global minimums** (reference inflation) | A7 | minimums only from the trust-state lineage; release-local references | P4r3 B1; RV2-A15 |
| TH-53 | **Unresolvable trust-state references freeze honest successors** | A7 | resolution before admissibility | P4r3 B4; RV2-A16 |
| TH-54 | **Certification key alone lifts WITHDRAWN** | A7 | MS-2 lifting rule | P4r3 B2; RV2-A17 |
| TH-55 | **Trust-state or policy equivocation and forks** | A7 | S3/S4 equivocation, `prior_states`, anchor orphans | P4r3 B3, E1–E3, R5; RV2-A18, A19 |
| TH-56 | **Lowering across a skipped policy version** | owner error, A8 | computed reductions; cumulative `lowering_history` | P4r3 B6; RV2-A20 |
| TH-57 | **Release key or build host mints a malicious binary** | A7, A16 | `release-artifact` ≥ 2, build attestation, TSS reference, TBM resolution | P4r3 A27–A27e; RV2-A27 |
| TH-58 | **Genuine older binary presented as an upgrade** | A5 | TBM high-water (`BINARY_T0_ROLLBACK`) | P4r3 A28; RV2-A28 |
| TH-59 | **Candidate key signs binaries under OP-4 "no"** | A7 | separate purpose | P4r3 A29; RV2-A29 |
| TH-60 | **Separation gap: one key spans trust-state and certification** | owner error | compiled whitelist, KS-8 | P4r3 K1…K3; RV2-A30 |
| TH-61 | **Pre-RoT adoption stages or residue write a RoT-1 project** | A14 | occupation of `spec/audits/GOVERNANCE-ADOPTION`, `.governance-runtime/migration` | P3r3 (L3 vs L3A); G1; RV2-A35 |
| TH-62 | **Gate record committed or written by a plugin authorises a trust decision** | A2, A3 | local trust-gate confirmation (`27`) | P4r3 R3; RV2-A13, A14 |
| TH-63 | **Long-lived process enforces a superseded snapshot** | A7, honest update | VU-11 | RV2-A21 |
| TH-64 | **Agent follows a rewritten adapter body** | A2 | adapters carry pointers; VTS rendering record | RV2-A22 |
| TH-65 | **Committed journal, dropped trust statements, weakened `overlay.prev`** | A2, A3, honest rollback | foreign artefacts; union PTR; weakening gate | RV2-A24…A26 |
| TH-66 | **Hard-linked staged file** | A3 | `st_nlink == 1` | RV2-A23 |
