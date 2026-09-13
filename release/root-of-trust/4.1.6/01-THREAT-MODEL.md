# Output 1 — Root-of-Trust Threat Model

## 1. Assets

| ID | Asset | Why it is privileged |
|---|---|---|
| AS-1 | Constitutional floors: `policies/SECURITY_POLICY`, `AUTHORITY_POLICY`, `POLICY_PRECEDENCE`, `HUMAN_GATE_POLICY`, `TOOL_POLICY`, `constitution/HARD_INVARIANTS`, `roles/ROLES` | decide what is indexed, exported, gated, executable and by whom |
| AS-2 | Kernel schemas | decide which records, overlays, exceptions, migrations and registries are valid |
| AS-3 | Framework migrations | declaratively mutate overlay, lock and generated state during update |
| AS-4 | Agent-facing kernel content: skills, adapters, command contract, taxonomy, overlay templates | instruct agents; generate adapter views |
| AS-5 | Framework tool registry (`tools/registry/TOOLS.yaml`, `tools/mcp/registry.yaml`) | declares executable tools, health commands, install commands |
| AS-6 | Release identity: statements, certification, revocation, legacy registry | decide what counts as authentic, certified, revoked |
| AS-7 | Trust-root metadata and signing keys | the anchor itself |
| AS-8 | `framework.lock`, `governance/trust/**` | the consumer's record of what was adopted |
| AS-9 | The `gov` binary | carries T0; is the trusted computing base |
| AS-10 | Reference retrieval profile: plugin code, runtime lock, model weights | determines what semantic memory returns |
| AS-11 | Protected project data classified `restricted`/`secret` | the harm target demonstrated by V-H3/E2 |

## 2. Security goals

| ID | Goal |
|---|---|
| G1 | **Ingress authenticity** — no privileged framework material is staged, installed, restored or executed unless its digests are bound by a statement authenticated under T0 |
| G2 | **Use-time integrity** — floors are read only from installed content that still matches the authenticated statement; otherwise from the authenticated embedded baseline |
| G3 | **No self-certification** — certification, compatibility, gate requirements and identity come only from signed statements, never from descriptive files |
| G4 | **Replay and downgrade resistance** — a genuine statement cannot be paired with other content, reused for another release, or used to move a project backwards without an explicit governed rollback |
| G5 | **Offline verifiability** — an already-downloaded release, a cloned consumer repository and a rollback are verifiable with no network |
| G6 | **Key compromise and loss recoverability** — rotation, revocation and re-attestation without re-bootstrapping every consumer, except for threshold root compromise |
| G7 | **Fail closed, typed** — every trust failure is `ok: false` with a stable machine-readable code and stage, before any trusted write |
| G8 | **No masquerade** — development and test material cannot produce a state represented as production-authenticated or certified |
| G9 | **Transport independence** — GitHub or any mirror can be fully adversarial without affecting authenticity decisions |
| G10 | **Single boundary** — one authentication function and one use-time trust handle; conformance tests enumerate all writers |

## 3. Adversaries

| ID | Adversary | Capability | Current successful attack |
|---|---|---|---|
| A1 | **Source controller** — malicious or compromised release directory, shared drive, archive, mirror | arbitrary bytes at the path passed to `--source`, including all manifests | V-H3; E1; E2 (no gate needed) |
| A2 | **Repository writer** — collaborator, compromised CI token, an agent with commit rights, a malicious PR merged by mistake | arbitrary tracked files under `governance/` delivered through Git | E4 |
| A3 | **Local user-space process** — another tool, a compromised dependency, a malicious plugin running as the same user | write to `~/.cache/gov`, `$GOV_KERNEL_CACHE`, `.governance-runtime/` | E3, E5 |
| A4 | **Environment manipulator** — shell profile, CI configuration, `.envrc` | `GOV_CANONICAL_ROOT`, `GOV_KERNEL_SOURCE`, `GOV_KERNEL_CACHE`, `GOV_PLUGINS_DIR` | redirects install source, schema fallback, adoption scanner policy, baseline cache |
| A5 | **Transport attacker** — network MITM, compromised hosting account, replaced release asset | arbitrary download bytes | none today (no fetch), but any future fetch inherits A1 |
| A6 | **Canonical-repository insider or compromise** | malicious commit that reaches `gov release build` | would be released unchanged; no two-person control on release identity |
| A7 | **Release-key thief** | can sign release statements | (post-RoT-1 threat) |
| A8 | **Root-key compromise** (at or above threshold) | can re-root trust | (post-RoT-1 threat; catastrophic) |
| A9 | **Replay / downgrade attacker** | serves a genuine old or revoked release, or another release's statement | would succeed today (no identity binding) |
| A10 | **Social engineer** | persuades an operator to pass a dev flag or approve a gate | partially mitigated by gates today |
| A11 | **Model / package supply-chain attacker** | substitutes model weights or Python packages behind a pinned model *name* | reference plugin pins `--model <hub id>` only, no revision or file digests |

## 4. Trust assumptions (trusted computing base)

1. The running `gov` executable and its compiled-in trust-root metadata, revocation floor and embedded kernel bytes.
2. OS process isolation; an attacker cannot rewrite the process memory or the executable itself.
3. SHA-256 collision/second-preimage resistance; Ed25519 (RFC 8032) unforgeability with strict verification.
4. Private keys held under the custody rules of `05-KEY-MANAGEMENT.md`; fewer than threshold root keys compromised.
5. At bootstrap, a human compares the trust-root fingerprint with an out-of-band published value (`06-BOOTSTRAP.md`).

## 5. Explicitly out of scope, with residual statement

| Residual | Reason | Mitigation that remains |
|---|---|---|
| Attacker replaces the `gov` binary | the binary is the TCB | artifact statements, bootstrap verification with independent tooling, `gov trust verify-artifact` for upgrades |
| Semantic defect in a genuinely signed release | signatures authenticate origin, not quality | independent verification + separate certification role + revocation |
| Freeze attack on a permanently offline machine (never learns of a revocation) | no online freshness role by design (G5) | revocation floor in every new binary and bundle; doctor reports metadata age (OP-5) |
| Threshold root compromise | anchor compromise | 2-of-3 offline custody; documented re-bootstrap |
| Caller-declared acting role (V-L5) | adapter authentication boundary, unchanged | human gates remain the authorisation boundary; RoT-1 authenticates material, not people |

## 6. Threat → defect → control register

| ID | Threat | Adversary | 4.1.5 status (evidence) | RoT-1 control | Acceptance test |
|---|---|---|---|---|---|
| TH-01 | Tampered source with stale manifests installs as verified | A1 | **open** (V-H3) | quarantine + signature + full file-map digest compare before any trusted write | RT-01, RT-02 |
| TH-02 | Tampered source with regenerated manifests passes source verification | A1 | **open** (E1) | reference digests come only from a signed statement; `manifest.json`/`KERNEL_MANIFEST.json` are ignored for trust | RT-13 |
| TH-03 | Source self-certifies to skip the update gate | A1 | **open** (E2) | gate requirement derived from authenticated statement + certification statement only; gate bound to statement digest | RT-13, RT-25 |
| TH-04 | Attacker signs a forged statement with own key | A1, A5 | n/a | key must exist in T0 root for the payload type's role | RT-03, RT-05 |
| TH-05 | A trusted key of the wrong role signs a release | A7 (other role) | n/a | role binding by payloadType; disjoint role key sets | RT-04 |
| TH-06 | Genuine statement paired with other content, or another release's statement reused | A1, A9 | **open** | file-map compare; `release_id` bound to tree digest; version equality with `KERNEL.yaml`; lock/statement identity cross-check | RT-09, RT-10 |
| TH-07 | Downgrade to older or revoked genuine release | A9 | partially (semver compare only, from self-declared source version) | version + sequence comparison against the *installed authenticated* identity; revocation list; rollback only to the ledger-recorded previous identity | RT-11, RT-20 |
| TH-08 | Coherent kernel+manifest+lock replacement via Git | A2 | **open** (E4) | use-time authentication against `governance/trust/release.dsse.json` under T0; lock is cross-checked, never trusted | RT-07b, RT-26 |
| TH-09 | Poisoned embedded cache used as install source or fail-closed baseline | A3, A4 | **open** (E3) | embedded bytes authenticated in memory; any materialisation re-verified against compiled-in digests; marker files never sufficient | RT-17 |
| TH-10 | Tampered rollback snapshot restored as verified | A3 | **open** (E5) | snapshots carry the statement; restore = authenticate + downgrade rule | RT-18 |
| TH-11 | Environment redirects source, schemas or scanner policy | A4 | **open** | env may only select a source for authentication or opt into a labelled dev state; never schemas, never anchors | RT-19 |
| TH-12 | Tampered migration executes during update | A1 | **open** (migrations loaded from the unauthenticated installed kernel and from the source's parent directory; `set_lock_field` writes any key) | migrations bound by id+digest in the statement, loaded only from the authenticated object; lock-field allowlist | RT-08 |
| TH-13 | Installed kernel edited in place after install | A2, A3 | **closed** by V-H2 (integrity) | preserved; now compared with the signed map | RT-07 |
| TH-14 | Use-time readers bypass the trust boundary | A2, A3 | **open** (`Project::schemas`, `tools::kernel_tools`, skills, context invariants, intents, readiness, verification, adapters invariants read `kernel_dir()` directly) | `TrustedKernel` handle is the only reader; architecture test forbids `kernel_dir()` outside the trust module | RT-27 |
| TH-15 | Interrupted install leaves mixed kernel/lock/statement state that verifies | A3 / crash | **open** (non-transactional copy, lock written after migrations) | journaled install transaction with atomic swap and lock as commit point | RT-16 |
| TH-16 | TOCTOU: source changed between check and copy | A1, A3 | n/a today | single read into quarantine; install only from quarantine bytes | RT-22 |
| TH-17 | Parser / canonicalisation differential (duplicate keys, non-canonical bytes, floats) | A1 | n/a | strict DSSE + RFC 8785 profile; payload must be byte-identical to its canonical re-serialisation | RT-23 |
| TH-18 | Development or test statement accepted by production installs | A10, A4 | n/a | trust profile compiled into the binary; production refuses test keys, test roots, test locks; unsigned dev path requires flag and keeps floors from the embedded baseline | RT-14 |
| TH-19 | Private signing key committed to repository or payload | A6 | n/a | producer refuses (`PRIVATE_KEY_MATERIAL_DETECTED`); conformance scan; custody rules | RT-24 |
| TH-20 | Substituted model weights or plugin code in the reference profile | A11, A3 | **open** (model pinned by hub name only) | signed profile statement with plugin, runtime-lock and model file digests and model revision; verified at install, registration, rebuild and plugin start | RT-15 |
| TH-21 | Malicious commit in canonical repository becomes a signed release | A6 | **open** | sign-what-you-reproduced on an isolated host; independent verification; certification by a different key holder; revocation | procedural (`05-KEY-MANAGEMENT.md` §3) |
| TH-22 | Stolen release key signs malicious releases | A7 | n/a | revocation of the key, root rotation, re-attestation of genuine statements (payload digest unchanged) | RT-20 |
| TH-23 | Trust-root rollback or single-key root takeover | A7, A8 | n/a | root chain: each version signed by threshold of previous **and** new root keys; monotonic version floor compiled in | RT-21 |
