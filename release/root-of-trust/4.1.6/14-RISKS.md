# Output 14 — Risks and trade-offs

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**

| ID | Risk / trade-off | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|---|
| RK-01 | Key custody grows from nine to eleven purposes: `release-artifact` needs two custodians, `build-attestation` an independent rebuilder | medium | high | the compiled whitelist allows the stated sharing only; standby keys; ceremony records | reconfirmation cost if the root threshold is lost |
| RK-02 | A machine never receives newer metadata | medium | medium | anchors; no trust ingress unanchored; OP-7 governs unanchored use; the freshness axis never shows `current` unanchored | RS-1 restated (`24` §10) |
| RK-03 | Signing friction per final release: candidate, attestation, final, build attestation, two artefact signatures, certification, TSS, fingerprint publication | high | low | tooling produces payloads; builder iterates on the test profile | multiple custodians per release |
| RK-04 | A signature proves origin, not correctness | low | high | reproduce-and-sign; verification attestation; independent build attestation; certification; revocation | collusion across custodians |
| RK-05 | Parser, canonicalisation, state-algorithm or surface-evaluator bugs | medium | high | compiled schemas; cross-implementation vectors; reference models (`P4r3`, `csi_lib`) the implementation must reproduce; fuzzing | implementation defects are testable |
| RK-06 | Development-flag misuse | medium | medium | never eligible; override trust gate | operator accepts the risk |
| RK-07 | Historical set depends on correct reproduction of old payloads | low | low | independently reproduced; recognition only | none |
| RK-08 | Prior harness behaviour changes (layout, historical refusals) | certain | low | classification rules (`13` §8) | verifier judgement |
| RK-09 | Ed25519 dependency supply chain | low | high | pinned version, review | standard dependency risk |
| RK-10 | Trust files and occupation entries add repository noise | medium | low | changed only by transactions | minor |
| RK-11 | The binary remains the TCB | — | high | `verify-artifact` A1–A10; build attestation; TBM high-water; first-run self-check (`25`) | TB-1…TB-3 |
| RK-12 | Signatures never expire | — | medium | revocation, withdrawal, minimum-sequence raise; optional expiry only for owner-selected freshness proofs | intended |
| RK-13 | Large model verification cost | medium | low | fs-verity; change-triggered digests | VR-4 |
| RK-14 | Caller-declared acting role (V-L5) | — | medium | trust gates are local confirmations independent of `--role` | non-trust gates: TA-8 limit |
| RK-15 | Scope growth delays 4.1.6 | high | medium | work packages (`11`); profiles may slip | the bounded patch is not a substitute |
| RK-16 | Trust gates need local confirmation on each machine | high | medium | operator decision pins for automation; `local_terminal_only` for downgrade-class kinds | friction by design |
| RK-17 | **Every final release that changes constitutional content needs a root-threshold TPS registration** | high | medium | `gov trust draft-policy` change lists; ceremony batched with the final | CS-2 |
| RK-18 | Consumers on legacy kernels become read-only until they update | certain | medium | doctor remediation; offline update from a bundle | intended |
| RK-19 | Platform primitives differ; the transaction area must share a device with `governance/` | medium | medium | `SecureDir`; `TRUST_PLATFORM_UNSUPPORTED(cross_device_tx)` | reduced platform coverage |
| RK-20 | Rewiring every mutation and reader may regress | high | medium | interception and OS tracing across all commands; prior harnesses | handled by verification |
| RK-21 | Legacy binaries and legacy tooling break on RoT-1 projects | certain | medium | intended containment (LP-1 executed); release protocol retires 4.1.2–4.1.5 | LR-1…LR-4 |
| RK-22 | Mis-issued TPS or TSS | low | high | lint and change lists; `prior_states` admissibility; computed lowering; chain reset | operational window |
| RK-23 | Per-machine lineage confirmation and state anchoring add onboarding friction | medium | low | one ceremony; pins for CI | friction by design |
| RK-24 | Owner-chosen clock assumptions (OP-3 B, OP-7 b/c) | depends | medium | default proposals avoid the clock; rollback detection | RS-2 |
| **RK-25** | **CI runners need state pins provisioned outside the repository writer's control (OP-7 a)** | high | medium | runner images or protected organisation jobs; OP-7 (c) as the owner alternative | RS-4 when provisioning is repository-controlled |
| **RK-26** | **Layout renames break tools and documents that read `governance/project`, `governance/generated`, `governance/kernel`, `governance/framework.lock` or `spec/audits/GOVERNANCE-ADOPTION` directly** | high | medium | WP-10 path changes; migration ledger lists moves; doctor explains | third-party scripts need updates |
| **RK-27** | **Independent rebuilder cost and reproducible-build brittleness** | medium | medium | pinned toolchain and lockfile digests; build inputs published | TB-2 |
| **RK-28** | **Surface classification errors** (too strict, or wrongly weak) | medium | medium | lint (never weaker than precedence; no catch-alls; consumer register); root-ceremony review | CS-1 |
| **RK-29** | **OP-7 (c) requires scheduled trust-state signing (heartbeats)** | depends | medium | dedicated scheduled custody; expiry window chosen by the owner | staleness bounded by the window |
| **RK-30** | **Project-strength weakening reports on legitimate overlay edits** | medium | low | gated CIT path records the new vector; trust gate accepts it | friction |
