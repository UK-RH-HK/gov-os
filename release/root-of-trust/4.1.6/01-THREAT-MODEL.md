# Output 1 — Root-of-Trust Threat Model

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 adds currency, lifecycle freshness, purpose separation, byte binding, protected paths and the trust-format
> boundary. It incorporates the independent review's TH-R1…TH-R10 as TH-24…TH-43.

## 1. Assets

| ID | Asset | Why it is privileged |
|---|---|---|
| AS-1 | Constitutional floors: `SECURITY_POLICY`, `AUTHORITY_POLICY`, `POLICY_PRECEDENCE`, `HUMAN_GATE_POLICY`, `TOOL_POLICY`, `constitution/HARD_INVARIANTS`, `roles/ROLES` | decide what is indexed, exported, gated, executable and by whom |
| AS-2 | Kernel schemas | decide which records, overlays, exceptions, migrations and registries are valid |
| AS-3 | Framework migrations | declaratively mutate overlay and generated state during update |
| AS-4 | Agent-facing kernel content: skills, adapters, command contract, taxonomy, overlay templates | instruct agents; generate adapter views |
| AS-5 | Framework tool registry | declares executable tools, health and install commands |
| AS-6 | Release identity: release, artifact and historical-identity statements | decide what content is authentic |
| AS-7 | Trust-root metadata, purpose grants and private signing keys | the anchor |
| AS-8 | `framework.lock`, `governance/trust/**` | the consumer's record of what was adopted |
| AS-9 | The `gov` binary | carries T0; the trusted computing base |
| AS-10 | Reference retrieval profile: plugin code, runtime lock, model weights | determines what semantic memory returns |
| AS-11 | Project data classified `restricted`/`secret` | the harm target (V-H3, E2, review R2b) |
| AS-12 | **Trust Policy**: floors, eligibility, install-authority floor, gating mode | decides which authentic release may govern and the minimum values it enforces |
| AS-13 | **Lifecycle state**: Trust State, certification, verification attestations, revocations | decides certification visibility and refusal |
| AS-14 | **Verifier Trust Store** and lineage pin | per-machine knowledge, confirmation and per-project high-water |
| AS-15 | **Protected Path Set** and the install transaction area (`governance/.tx/`) | the only place installed trust state is written |

## 2. Security goals

| ID | Goal |
|---|---|
| G1 | **Ingress authenticity** — no privileged framework material is staged, installed, restored or executed unless its digests are bound by a statement verified under T0 for the right purpose |
| G2 | **Use-time integrity** — enforcement reads only installed content that still matches the authenticated statement; otherwise the authenticated embedded baseline |
| G3 | **No self-certification** — certification, compatibility, gate requirements and identity come only from signed statements |
| G4 | **Replay and downgrade resistance** — a genuine statement cannot be paired with other content, reused for another release, or used to move a project backwards without an authorised rollback |
| G5 | **Offline verifiability** — an installed release, a cloned repository and a local bundle are verifiable without network |
| G6 | **Compromise and loss recoverability** — rotation, revocation and re-attestation without re-bootstrapping, except for threshold root compromise |
| G7 | **Fail closed, typed** — every trust failure is `ok: false` with a stable code, before any trusted write |
| G8 | **No masquerade** — development and test material never appear production-authenticated, eligible or certified |
| G9 | **Transport independence** — any host or mirror can be adversarial without affecting authenticity decisions |
| G10 | **Single boundary** — one authentication constructor, one use-time snapshot, enumerated writers |
| G11 | **Currency** — authenticity never implies eligibility; eligibility, floors and install authority come from T0 and protected trust state, never from the candidate; floors never move down except by an explicit root-signed lowering |
| G12 | **Byte binding** — the bytes verified are the bytes installed and enforced |
| G13 | **Monotonic lifecycle state** — omission or replay of signed metadata never produces a relaxation or forgets a known negative fact |
| G14 | **Purpose separation** — a key acts only within the purposes root grants it; certification never creates authenticity |
| G15 | **Protected paths** — generic project mutation mechanisms cannot write trust or kernel authority paths |
| G16 | **Format boundary** — no older binary interprets a newer trust format as verified |

## 3. Adversaries

| ID | Adversary | Capability |
|---|---|---|
| A1 | Source controller: malicious or compromised release directory, shared drive, archive, mirror | arbitrary bytes at a source path, including all manifests and a chosen subset of genuine signed statements |
| A2 | Repository writer: collaborator, compromised CI token, agent with commit rights, mistakenly merged PR | arbitrary tracked files (including `governance/**`, `spec/**`, symlinks) delivered through Git |
| A3 | Local same-user process: other tool, compromised dependency, malicious plugin | read and write anything the user can, including the VTS, `.governance-runtime/`, installed files, concurrently with `gov` |
| A4 | Environment manipulator: shell profile, CI configuration, `.envrc` | environment variables (`HOME`, `XDG_*`, `GOV_*`), working directory, arguments passed by automation |
| A5 | Transport attacker: network MITM, compromised hosting account, replaced release asset | arbitrary download bytes |
| A6 | Canonical-repository insider or compromise | malicious commit that reaches a build |
| A7 | Thief of one non-root purpose key | can sign statements of that purpose only |
| A8 | Root threshold compromise | can re-root trust (catastrophic) |
| A9 | Replay and downgrade attacker | serves genuine old, revoked, rejected or legacy releases and statements |
| A10 | Social engineer | persuades an operator to pass a flag, answer a gate or skip confirmation |
| A11 | Model or package supply-chain attacker | substitutes weights or packages behind a pinned name |
| A12 | Trust-metadata withholder | serves stale-but-genuine metadata and withholds newer statements (a specialisation of A1/A5) |
| A13 | Clock manipulator | sets the local clock (an A3/A4 capability; relevant only to OP-3 mode B) |
| A14 | Legacy-binary operator | runs a pre-RoT binary (4.1.2–4.1.5) against a RoT-1 project, possibly unknowingly |
| A15 | Fork distributor | ships a `gov` binary compiled with a substituted trust root |

## 4. Trust assumptions (trusted computing base)

| ID | Assumption | Holds when |
|---|---|---|
| TA-1 | The running `gov` executable and its compiled T0 (root chain, purposes, schemas, floor operators, TPS, TSS, historical-identity registry, embedded kernel) are genuine | always (TCB) |
| TA-2 | OS process isolation: an attacker cannot rewrite the process's memory or executable | always (same-user debugging disabled or out of scope) |
| TA-3 | SHA-256 collision and second-preimage resistance; Ed25519 (RFC 8032) unforgeability with strict verification | always |
| TA-4 | Private keys under the custody of `05`; fewer than threshold root keys compromised; KS-1…KS-7 hold | always |
| TA-5 | A human compared the trust-root id with a channel independent of the release host before the lineage was pinned | OP-6 modes (a) and (c); **not** mode (b) |
| TA-6 | The platform offers the secure-open, atomic-rename and locking primitives of `18` §3 | production profile only on such platforms |
| TA-7 | The local clock is honest | **only relied on** under OP-3 mode B |
| TA-8 | Human Decision Gate answers come from humans; the acting role is caller-declared (V-L5 boundary) | unchanged documented boundary |

## 5. Out of scope and accepted residuals

| Residual | Reason | Mitigation that remains | Defined in |
|---|---|---|---|
| Replacement of the `gov` binary | the binary is the TCB | artifact statements; bootstrap verification; verification of upgrades by the previous binary | `06` |
| Semantic defect in a genuinely signed release | signatures authenticate origin, not quality | independent verification, attestation, certification, revocation, min-sequence raise | `17`, `19` |
| A verifier that never receives newer metadata | offline verification | no relaxation, no forgetting, no floor lowering, no certification (RS-1) | `17` §15 |
| Mode B relies on the local clock | owner-optional | disabled by default (RS-2) | `17` §13 |
| A3 deletes its own VTS | same-user boundary | forgetting only (RS-3, RR-3) | `17`, `20` |
| A3 modifies files after a process built its snapshot; ignores locks; non-`gov` subprocesses write protected paths | same-user boundary | detected by the next process; never enforced (VR-1…VR-3) | `18` §11 |
| Profile runtimes consumed by path by external processes | Python/model runtime | host verification before and after use; fs-verity where available (VR-4) | `10` |
| Older eligible release delivered by A2 on a machine without a VTS record | offline verification | floors and install authority unaffected (RR-2) | `20` §10 |
| Pre-RoT binary behaviour (overwrite by 4.1.5 remedies; no trust boundary in 4.1.2–4.1.4) | cannot change old binaries | fail closed on RoT-1 data; detected by RoT-1 binaries (LC-1…LC-3) | `13` §3.3 |
| Threshold root compromise | anchor compromise | 2-of-3 custody; re-bootstrap | `05` §9 |
| Caller-declared acting role | adapter boundary | gates remain the human authorisation boundary | TA-8 |

## 6. Threat register

### 6.1 Revision 1 threats, updated

| ID | Threat | Adversary | 4.1.5 status (evidence) | Revision 2 control | Tests (`12`) |
|---|---|---|---|---|---|
| TH-01 | Tampered source with stale manifests installs as verified | A1 | open (V-H3) | secure read into VerifiedBlobs; V9 digest compare before any trusted write | RT-01, RT-02 |
| TH-02 | Tampered source with regenerated manifests passes | A1 | open (E1) | reference digests only from a signed statement; manifests never read | RT-13 |
| TH-03 | Source self-certifies to skip the update gate | A1 | open (E2) | manifests never read; certification never relaxes a gate in OP-3 mode A | RT-13, RT-25, RT-35 |
| TH-04 | Forged statement with an attacker key | A1, A5 | n/a | SV-6 key in effective root for the purpose | RT-03, RT-05 |
| TH-05 | Trusted key of the wrong purpose signs | A7 | n/a | SV-5/SV-6 purpose mapping; KS-1…KS-7 | RT-04, RT-46, RT-47 |
| TH-06 | Genuine statement paired with other content, or reused | A1, A9 | open | V8 identity, V9 per-file digests, use-time snapshot compare | RT-09, RT-10, RT-51 |
| TH-07 | Downgrade to an older or revoked genuine release | A9 | partial | E3/E4/E9/E10; downgrade policy on every restoring path | RT-11, RT-33, RT-34, RT-52 |
| TH-08 | Coherent kernel + trust + lock replacement via Git | A2 | open (E4) | use-time authenticity, eligibility and floors | RT-07b, RT-26, RT-31, RT-32 |
| TH-09 | Poisoned embedded cache used as source or baseline | A3, A4 | open (E3) | no cache on any trust path; in-memory EmbeddedSnapshot | RT-17, RT-45 |
| TH-10 | Tampered rollback snapshot restored as verified | A3 | open (E5) | snapshot authenticated and eligibility-checked under current policy | RT-18, RT-44 |
| TH-11 | Environment redirects source, schemas, scanner policy or trust store | A4 | open | env selects sources only; VTS path from the account database | RT-19, RT-64 |
| TH-12 | Tampered migration executes | A1 | open | V10 binding, unique chain, computed weakening gate, no lock operation | RT-08, RT-53, RT-54 |
| TH-13 | Installed kernel edited in place after install | A2, A3 | closed for static edits (V-H2); open for races (review R2b) | per-process snapshot; enforcement from snapshot bytes | RT-07, RT-42 |
| TH-14 | Use-time readers bypass the boundary | A2, A3 | open | KernelSnapshot is the only reader; GovernedFs read guard | RT-27 |
| TH-15 | Interrupted install leaves verifying mixed state | A3, crash | open | journaled transaction, atomic exchange, lock commit point | RT-16 |
| TH-16 | Source changed between check and copy | A1, A3 | n/a | read once; install from buffers; read-back re-digest | RT-22, RT-40 |
| TH-17 | Parser or canonicalisation differential | A1 | n/a | SV-1, SV-3 strict envelope and canonical bytes | RT-23 |
| TH-18 | Development or test material accepted as production | A10, A4 | n/a | profile in every statement; separate test-profile binary; deny-list | RT-14, RT-68 |
| TH-19 | Private signing key committed | A6 | n/a | producer refusal; conformance scan | RT-24 |
| TH-20 | Substituted model weights or plugin code | A11, A3 | open | signed profile statement; host-side verification | RT-15, RT-67 |
| TH-21 | Malicious commit becomes a signed release | A6 | open | sign-what-you-reproduced; attestation by verifier; certification by a separate key | procedural, RT-62 |
| TH-22 | Stolen release key signs malicious releases | A7 | n/a | purpose limits; gates (mode A); certification needs two more keys; root removal; TPS min-sequence raise | RT-20 |
| TH-23 | Trust-root rollback or single-key re-rooting | A7, A8 | n/a | dual-threshold chain; monotonic versions; KS-1 | RT-21 |

### 6.2 Threats added in revision 2

| ID | Threat | Adversary | 4.1.5 status (evidence) | Revision 2 control | Tests |
|---|---|---|---|---|---|
| TH-24 | **Genuine older, legacy or rejected release lowers current floors** or becomes current policy root (via Git, snapshot, recovery, rollback) | A2, A3, A9 | open (review R1: L3 passes `update_apply`/`resume` on the genuine 4.1.2 kernel) | eligibility predicate (`19` §6); floors from the TPS lineage joined with the kernel (`19` §5); floor registration and monotonic policy (`19` §10); historical identities never eligible | RT-31, RT-32, RT-33, RT-34, RT-70 |
| TH-25 | **Stale CERTIFIED replayed** without the later WITHDRAWN | A1, A12 | n/a in 4.1.5 form; open in rev 1 design | certification never relaxes in mode A; mode B needs a freshness proof (`17` §6, §13) | RT-35 |
| TH-26 | **REJECTED state omitted** to avoid a gate | A1, A12 | open in rev 1 design | absence is never positive; every production ingress gated (`17` MS-1, §7) | RT-36 |
| TH-27 | **Revocation or trust metadata stripped or rolled back** (repository deletion, redirected store) | A2, A4, A12 | open in rev 1 design | sticky negative set; admissibility; signed required minimums; VTS location not env-selectable (`17` §5, §11) | RT-37, RT-64 |
| TH-28 | **Root rotation stripped** so a removed key still verifies | A2, A12 + A7 | open in rev 1 design | `trust_references.root_version`; `TRUST_ROOT_STALE`; residual RS-1 bounded | RT-38 |
| TH-29 | **Signed trust-state regression** by a trust-state key thief | A7 | n/a | admissibility (`17` S4); `TRUST_STATE_REGRESSION` | RT-60 |
| TH-30 | **Purpose confusion**: certification key asserts authenticity; historical identity from a non-compiled source; cross-type or cross-lineage replay | A7, A1 | open in rev 1 design (review RV-H4) | purpose table, SV-2/SV-6/SV-9/SV-10, KS-3…KS-6, compiled-only historical identities | RT-39, RT-46, RT-47 |
| TH-31 | **Verified bytes ≠ enforced bytes**: use-time race, symlinked ancestors, reader mid-swap | A3, A2+A3 | open (review R2b: restricted records indexed while `verified:true`) | secure reader; KernelSnapshot; VU-1…VU-10; locks | RT-41, RT-42 |
| TH-32 | **Unregistered writers of protected paths**: CIT `write_file`/`move_file`/`delete_file`, adoption batch rollback, recovery, `gov`-run git subprocesses | A2, A3 | open (`cit/mod.rs:704`, `migrations/executor.rs:304-350`) | Protected Path Set and GovernedFs with interception conformance (`18` §8) | RT-48 |
| TH-33 | **Partial-install fail-open** to an unverified directory | A2, A3 | open (`kernel_trust.rs:128-130, 289-291`) | installation state machine (`18` §9); EmbeddedSnapshot for non-complete states | RT-43 |
| TH-34 | **Incoming release defines its own install authority** | A1 + low-authority actor | open (`init.rs:246`) | install-authority floor from TPS ⊔ embedded ⊔ current eligible (`19` §8) | RT-49 |
| TH-35 | **Pre-RoT binary interprets a RoT-1 project as verified** | A14, A2 | open in rev 1 design (lock kept 1.1.0 fields) | trust-format boundary: sentinels, tombstone manifest, `FORMAT` (`13` §3); executed F1 | RT-50 |
| TH-36 | **Signed migration removes project-owned strengthening**, or a forked migration chain | A6, A7 | open (`update.rs:235-242`, `migrations/framework.rs:36-58`) | computed weakening gate; unique chain; field equality (`19` §9, `07` §3) | RT-53, RT-54 |
| TH-37 | **First install from a compromised release host** (binary, root and repository fingerprint copies replaced); fork binary of another lineage | A5 + A6, A15 | n/a | independent publication channels; OP-6 confirmation; fail-closed lineage mismatch (`06` §2–§4) | RT-65, RT-66 |
| TH-38 | **Clock manipulation** to create a false freshness proof | A13 | n/a | clock used only in OP-3 mode B, with rollback detection (`17` §13) | RT-56 |
| TH-39 | **Forged install journal** planting an older genuine release as the previous state | A3, A2+A3 | n/a | recovery re-authenticates and applies eligibility and downgrade policy (`20` §5) | RT-58 |
| TH-40 | **Profile runtime or model substituted at use** while the plugin reports expected digests | A3, A11 | open | host-side digests; plugin reports informational (`10` §5) | RT-67 |
| TH-41 | **Test profile unified into the production binary** by a workspace build | A6 (mistake) | n/a | separate test-profile binary; `compile_error!` guard; pipeline check (`05` §10) | RT-68 |
| TH-42 | **Candidate installed as production** or promoted from different content | A1, A9 | n/a | signed stage; E2; promotion tree-digest check (`04` V8) | RT-63 |
| TH-43 | **Certification forged with a single key** (without attestation or trust-state reference) | A7 | n/a | CERTIFIED view requires attestation + certification + TSS reference (`17` §6) | RT-61, RT-62 |
