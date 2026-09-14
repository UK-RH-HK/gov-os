# Output 14 — Risks and trade-offs

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 5 risks added: **RK-38** bit-for-bit reproducibility across operating systems and distributions not yet shown
> (IR-REP-3; a target is not registered until shown); **RK-39** reproducer availability blocks releases (OP-9 (a), (c));
> **RK-40** one registration ceremony per release (OP-2 (a) touches root keys per release); **RK-41** a second implementation of
> the admission predicate must stay conformant (shared vectors; OP-12); **RK-42** first install unavailable while a channel is
> unreachable (OP-13 (b)); **RK-43** CI image rebuild cadence tied to pin and record validity; **RK-44** a delegated
> registration quorum concentrates source and content selection (OP-2 (b)); **RK-45** CR4-B-07 option 1 refuses C3 on pinned
> runners against a TSS published after the pin until re-provisioned.
> Revision 4 restates RK-01, RK-02, RK-11, RK-24, RK-25 and RK-29, and adds RK-31…RK-37.

| ID | Risk / trade-off | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|---|
| RK-01 | Key custody grows to twelve purposes: `release-artifact` needs two custodians, `build-attestation` an independent rebuilder, and `freshness-witness` (only under OP-7 c) a scheduled service with two keys | medium | high | the compiled whitelist allows only the stated sharing; standby keys; ceremony records | reconfirmation cost if the root threshold is lost |
| RK-02 | A machine never receives newer metadata | medium | medium | inclusion anchors; pin validity; currency proofs for trust ingress; OP-7 governs unanchored use; no surface says `current` | RS-1, RS-1b, RS-1c (`24` §10) |
| RK-03 | Signing friction per final release: candidate, attestation, final, build attestation, two artefact signatures, certification, TSS, fingerprint publication | high | low | tooling produces payloads; builder iterates on the test profile | multiple custodians per release |
| RK-04 | A signature proves origin, not correctness | low | high | reproduce-and-sign; verification attestation; independent build attestation; certification; revocation | collusion across custodians |
| RK-05 | Parser, canonicalisation, state-algorithm or surface-evaluator bugs | medium | high | compiled schemas; cross-implementation vectors; reference models (`P4r3`, `csi_lib`) the implementation must reproduce; fuzzing | implementation defects are testable |
| RK-06 | Development-flag misuse | medium | medium | never eligible; override trust gate | operator accepts the risk |
| RK-07 | Historical set depends on correct reproduction of old payloads | low | low | independently reproduced; recognition only | none |
| RK-08 | Prior harness behaviour changes (layout, historical refusals) | certain | low | classification rules (`13` §8) | verifier judgement |
| RK-09 | Ed25519 dependency supply chain | low | high | pinned version, review | standard dependency risk |
| RK-10 | Trust files and occupation entries add repository noise | medium | low | changed only by transactions | minor |
| RK-11 | The binary remains the TCB | — | high | `verify-artifact` A1–A10 with attested source; build attestation; accepted-TBM high-water; first-run self-check (`25`) | TB-1…TB-4 |
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
| RK-24 | Clock assumptions: pin validity and the C3 window under every option; OP-3 B and OP-7 (b)/(c) when chosen | depends | medium | witness-only high-water; SV-11; root-signed reset; in-gate proofs need no clock | RS-2 |
| **RK-25** | **CI runners need protected state pins provisioned outside the repository writer's control (OP-7 a)** | high | medium | root-owned system pin directory in runner images; the job runs as another user; re-provisioning within `pin_max_validity_days`; OP-7 (c) as the owner alternative | RS-4 when provisioning is repository-controlled |
| **RK-26** | **Layout renames break tools and documents that read `governance/project`, `governance/generated`, `governance/kernel`, `governance/framework.lock` or `spec/audits/GOVERNANCE-ADOPTION` directly** | high | medium | WP-10 path changes; migration ledger lists moves; doctor explains | third-party scripts need updates |
| **RK-27** | **Independent rebuilder cost and reproducible-build brittleness** | medium | medium | pinned toolchain and lockfile digests; build inputs published | TB-2 |
| **RK-28** | **Surface classification errors** (too strict, or wrongly weak) | medium | medium | lint (never weaker than precedence; no catch-alls; consumer register); root-ceremony review | CS-1 |
| **RK-29** | **OP-7 (c) requires a scheduled `freshness-witness` service with at least two keys** | depends | medium | dedicated custody (KS-11); validity window chosen by the owner | RS-5 under witness-key compromise |
| **RK-30** | **Project-strength weakening reports on legitimate overlay edits** | medium | low | gated CIT path records the new vector; trust gate accepts it | friction |

| ID | Risk / trade-off (added in revision 4) | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|---|
| **RK-31** | **Pin re-provisioning**: CI pins expire every `pin_max_validity_days` | high | medium | runner-image rebuild cadence; doctor D035 warns before expiry | a lapsed pin makes the runner C0 (fails closed) |
| **RK-32** | **Confinement availability**: platforms or containers without Landlock, sandbox profiles or restricted tokens cannot run repository commands under `gov` | medium | medium | `REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE` with a remedy; mount-namespace fallback on Linux | reduced platform coverage |
| **RK-33** | **Currency friction**: C3 on long-idle machines needs a fresh confirmation or witness | high | low | in-gate typed fingerprint (no clock); `c3_currency_window_hours` | friction by design |
| **RK-34** | **Exact precedence registration**: every kernel precedence change needs a root-signed TPS | high | medium | `gov trust draft-policy` lists precedence changes and reductions in both directions; batched with the release ceremony | CS-2 |
| **RK-35** | **Re-issued migrations**: the historical 4.1.5 migrations fail the revision-4 checker (`set_lock_field`); 4.1.6 must re-issue its chain | certain | low | WP-18 | none |
| **RK-36** | **OP-2 (S1) ceremony timing**: root-registered production sources add a root signature per binary-shipping release | depends | medium | merged with the kernel registration ceremony | owner option |
| **RK-37** | **The directed join changes 4.1.5 override semantics**: a refused weakening component no longer discards the admitted strengthening components of the same override | medium | low | `OVERRIDE_COMPONENT_REFUSED` reports refused components; `gov policy effective` shows the result | intended |
