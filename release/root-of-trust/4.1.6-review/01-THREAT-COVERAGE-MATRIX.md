# Output 2 — RoT-1 Threat-Coverage Matrix (independent review)

Legend. **COVERED**: the design closes the threat at the root, for every in-scope adversary, and a test is named.
**PARTIAL**: closed for some adversaries or paths only. **NOT COVERED**: the design does not close it.
**NOT SPECIFIED**: the design is silent, so an implementation may go either way. Evidence types: **E** executed in this
review (scratch directories, 4.1.5 binary rebuilt from the unchanged runtime at HEAD), **C** code citation, **D** design reading.

Findings `RV-*` are defined in `10-BLOCKING-FINDINGS.md`; attacks `RV-A*` in `08-HELDOUT-ATTACK-REGISTER.md`.

## 1. Architect's threat register (TH-01 … TH-23), re-assessed

| ID | Threat (short) | 4.1.5 status, independently checked | RoT-1 control | Review verdict | Why / residual | Finding |
|---|---|---|---|---|---|---|
| TH-01 | Tampered source, stale manifests | open (V-H3 evidence; C `kernel.rs:248-256`, `lock.rs:12-35`) | quarantine + V9 full file-map compare before any trusted write | **COVERED** | reference digests come only from a signed payload; nothing is written before V14 | — |
| TH-02 | Tampered source, regenerated manifests | open (**E** E1b reproduced: `release verify` ok, regenerated hash `aa8fb66a…`) | manifests ignored for trust | **COVERED** | same | — |
| TH-03 | Source self-certifies to skip the update gate | open (**E** E2 reproduced: `human_gate_required:false`, applied without `--approve`) | gate requirement from signed release + certification statements; gate bound to statement digest | **PARTIAL** | a *self-declared* CERTIFIED is closed, but a *genuinely signed, stale* CERTIFIED statement can be replayed while the later WITHDRAWN/REJECTED statement is omitted (V13 “highest sequence among those present”). This is the E2 pattern with signed data. | RV-H2 |
| TH-04 | Forged statement with attacker key | n/a | key must be in the T0 root for the payloadType's role | **COVERED** | — | — |
| TH-05 | Trusted key of the wrong role signs | n/a | payloadType→role binding; disjoint role key sets | **PARTIAL** | holds for release statements. The **legacy-identity** payloadType, which confers kernel authenticity and policy-root status, is bound to the *certification* role (`05` §1). | RV-H4 |
| TH-06 | Genuine statement with other content / another release's statement reused | open | V8 identity + V9 file map; use-time statement ≡ files | **PARTIAL** | closed for mixing. Not closed for replacing the whole set (kernel + statement + lock) with an **older genuine** release at use time. | RV-H1 |
| TH-07 | Downgrade to an older or revoked genuine release | partial (semver from a self-declared source) | V12 against the installed authenticated identity; ledger-bound rollback | **PARTIAL** | V12 runs only at `authenticate` ingress. Git delivery, adoption-snapshot restore and forged journal + lock bypass it. The rollback bound is `spec/reports/framework-updates.jsonl`, which A2 can write. `kernel_trust` v2 has no version, sequence or floor check (`04` §5). | RV-H1, RV-M1 |
| TH-08 | Coherent kernel + manifest + lock replacement via Git | open (**E** E4 reproduced: `verified:true`, D003/D004/D029 ok) | use-time authentication against `governance/trust/release.dsse.json` | **PARTIAL** | a forged or regenerated statement is closed (RT-07b). A **genuine older or legacy** set is accepted as `verified:true`, and legacy floors are weaker (**E** R1). | RV-H1 |
| TH-09 | Poisoned embedded cache as source or baseline | open (**E** E3a/E3b reproduced) | embedded bytes authenticated in memory; marker never evidence | **COVERED** | — | — |
| TH-10 | Tampered rollback snapshot | open (**E** E5 reproduced) | snapshot authenticated before restore | **PARTIAL** | authenticity is covered. Downgrade policy is bound to an A2-writable ledger, and a second snapshot mechanism (adoption batches) is unmapped. | RV-H1, RV-M1 |
| TH-11 | Environment redirects source, schemas or scanner policy | open (C `kernel.rs:83-112`, `project.rs:127-139`, `adopt.rs:74-95`) | env = source selection only; `GOV_KERNEL_SOURCE` removed | **PARTIAL** | `XDG_CONFIG_HOME` selects the trust high-water store (`05` §5), so A4 can reset revocation and root high-water to the compiled floor | RV-H2 |
| TH-12 | Tampered migration executes | open (C `update.rs:19-27`, `kernel.rs:226-232`, `migrations/framework.rs:236-242`) | migrations bound by id/path/digest; lock-field allowlist | **PARTIAL** | authenticity is covered. A signed migration may delete or weaken project-owned strengthening overlay entries (for example DATA_SENSITIVITY classifications) without a gate, because only signer-declared `breaking`/`human_gates` trigger one. Migration-chain uniqueness is unspecified. | RV-M8 |
| TH-13 | In-place edit after install | closed for static edits by V-H2 | installed files ≡ statement map | **PARTIAL** | a same-user racer that swaps bytes after verification defeats it. **E** R2/R2b against 4.1.5: the swap landed 0.07–0.10 ms after `kernel_trust` read the file, and enforcement consumed the swapped floor. RoT-1 keeps a `TrustedKernel` “over installed dir”. | RV-H3 |
| TH-14 | Use-time readers bypass the boundary | open (C `context/mod.rs:93-97` etc.) | `TrustedKernel` only; architecture test on `kernel_dir()` | **PARTIAL** | the symbol-grep enforcement misses writers and readers that compute paths (CIT, adoption executor, `adapters.rs:168`, `adopt.rs:816,1363`) | RV-M1 |
| TH-15 | Interrupted install leaves verifying mixed state | open (C `update.rs:185-233`) | journal; lock commit point; recovery table | **COVERED** (with AC-F criteria) | the swap is four renames over two directories. Readers must see the journal and fail closed; staging directories need no-follow/exclusive creation. | — |
| TH-16 | TOCTOU source → copy | n/a | single read into quarantine; re-digest before swap; post-commit verify | **COVERED** for ingress | the use-time equivalent is not covered | RV-H3 |
| TH-17 | Parser / canonicalisation differential | n/a | strict DSSE, GOV-JCS-1 re-serialisation equality | **COVERED** | minor spec inconsistencies only | RV-L1 |
| TH-18 | Dev/test statement accepted by production | n/a | compiled trust profile; deny-list; labels | **COVERED** | cargo feature-unification hazard | RV-L2 |
| TH-19 | Private key committed | n/a | producer refusal + conformance scan | **COVERED** | **E** repository and history scan: only detection patterns (`SECURITY_POLICY`, `secrets.rs`, the pack, `harness_v3.py`); the example key is ephemeral | — |
| TH-20 | Substituted model weights or plugin code | open | signed profile statement | **PARTIAL** | per-start integrity relies on digests reported by the plugin (T6) and on size/mtime gating (A3-controllable) | RV-M7 |
| TH-21 | Malicious commit signed as a release | open | sign-what-you-reproduced; separate certifier | **PARTIAL** (procedural) | verifier acceptance is not attested by any key; see also signed-migration weakening | RV-M5, RV-M8 |
| TH-22 | Stolen release key | n/a | root rotation, revocation, re-attestation | **PARTIAL** | rotation and revocation delivered after ship are strippable by A2 on any machine without the user trust store (fresh clone, CI) and resettable by A4. This is broader than the “offline freeze” residual the pack states. | RV-H2 |
| TH-23 | Trust-root rollback / single-key takeover | n/a | TUF dual-threshold rule; monotonic version | **COVERED** per machine | cross-machine rollback to the compiled root is the same residual as TH-22 | RV-H2 |

## 2. Threats missing from the architect's register

| ID | Threat | Adversary | Evidence | Review verdict | Finding |
|---|---|---|---|---|---|
| TH-R1 | **Authenticated downgrade at use.** Replace kernel + `governance/trust/` + lock with an older genuine release or a legacy 4.1.2–4.1.5 kernel (Git, adoption-snapshot restore, manual copy); it verifies as a policy root with weaker floors | A2, A3 | **E** R1: same binary, L3 `change-controller`: `update --apply` passes authority and `resume` succeeds on the genuine 4.1.2 kernel; both `AUTHORITY_DENIED` on 4.1.5; both kernels `verified:true`. **D** `04` §5 (no floor), `06` §6 and `11` Phase 4 (“legacy … operates”) | **NOT COVERED** | RV-H1 |
| TH-R2 | **Stale positive / omitted negative lifecycle facts** (CERTIFIED replay, omission of WITHDRAWN/REJECTED, revocation or root-link stripping, trust-store redirection) | A1, A2, A4 | **D** `04` V4/V13, `05` §5–§6, OP-3 | **NOT COVERED** | RV-H2 |
| TH-R3 | **Non-release role mints kernel authenticity** via the legacy-identity statement (certification role, threshold 1) | A7-cert (certification-key thief), A6 | **D** `05` §1 payloadType table, `08` §5, `06` §6 | **NOT COVERED** | RV-H4 |
| TH-R4 | **Verified bytes ≠ used bytes** (use-time race; symlinked `governance/` ancestors; readers mid-swap) | A3, A2+A3 | **E** R2, R2b | **NOT COVERED** | RV-H3 |
| TH-R5 | **Unregistered writers of trust locations** (CIT file operations; adoption batch rollback; A7/A11 kernel checks; adapters check) | A2 (approved CIT), A3 (snapshot) | **C** `cit/mod.rs:704`, `migrations/executor.rs:9-13,304-350`, `adopt.rs:816,1363`, `adapters.rs:168` | **NOT COVERED** | RV-M1 |
| TH-R6 | **Partial-install fail-open** (lock or manifest missing ⇒ “uninstalled” ⇒ guard passes, policy root = installed dir) | A2, A3 | **C** `kernel_trust.rs:128-130, 289-291`; `cli/src/main.rs:743, 865` | **NOT SPECIFIED** | RV-M2 |
| TH-R7 | **Target self-authorisation** (a first install or dev install takes AUTHORITY_POLICY from the release being installed) | A1 + any signed or dev release with weaker authority | **D** `09` §1 step 2, `04` §8; **C** `init.rs:246` | **NOT COVERED** | RV-M3 |
| TH-R8 | **Pre-RoT-1 binaries** keep treating RoT-1 projects as `verified` through the 1.1.0 lock fields that RoT-1 retains | A2 against a collaborator on ≤4.1.5 | **C** `kernel_trust.rs:156-169`; **D** `13` row 4 | **NOT COVERED** | RV-M4 |
| TH-R9 | **Signed migration weakens project-owned strengthening** (deletes DATA_SENSITIVITY classifications or overlay minimum trust) with no gate | A6/A7 (insider or stolen release key) | **C** `migrations/framework.rs:124-170`; `update.rs:235-242` accepts any migration-declared change | **NOT COVERED** | RV-M8 |
| TH-R10 | **Bootstrap TOFU / co-hosted fingerprint channels** | A5 + A6 (repository host compromise at first install) | **D** `06` §2.1, OP-6, `01` §4 assumption 5 | **PARTIAL** | RV-M6 |

## 3. Summary

RoT-1 closes the **authenticity** half of the class: no unsigned, forged, regenerated, self-labelled, cached or
transport-supplied byte can become T1 (TH-01, 02, 04, 09, 16, 17, 19 COVERED; E1–E5 all addressed at the root). It does
not yet close **currency**: authenticated but superseded, withdrawn, rejected or legacy facts can still become the
*current* policy root or relax a gate (TH-R1, TH-R2). It does not bind the bytes enforcement reads to the bytes that
were verified (TH-R4, executed: persistent restricted-content indexing with every check green). It also lets a
non-release role confer authenticity (TH-R3). These four are the same defect class the escalation was meant to end: a
lower-trust, stale or unverified input manufacturing a current higher-trust fact.
