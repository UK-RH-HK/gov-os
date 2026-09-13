# Output 14 — Risks and trade-offs

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**

| ID | Risk / trade-off | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|---|
| RK-01 | Key custody burden grows from four roles to nine purposes; threshold root loss forces re-bootstrap | medium | high | purposes may share keys where KS-1…KS-7 allow (`21` OP-2); standby keys; ceremony records; re-attestation keeps digests stable | reconfirmation cost if root threshold is lost |
| RK-02 | A verifier never receives newer metadata (fresh machine, stripped repository, older binary, no refresh) | medium | medium | no relaxation without freshness; sticky negatives; signed references detect most staleness; compiled TPS floors | RS-1 (`17` §15) |
| RK-03 | Signing friction: candidate, attestation, final, certification and TSS per release | high | low | separate candidate key for iterations; tooling (`promote`, `publish`) produces payloads; builder iterates on the test profile | four signatures per accepted release |
| RK-04 | A signature proves origin, not correctness; a malicious commit can be signed | low | high | sign-what-you-reproduced; verifier attestation; separate certification key; revocation; min-sequence raise | builder–verifier–certifier collusion |
| RK-05 | Parser, canonicalisation or state-algorithm bugs | medium | high | compiled schemas; cross-implementation vectors; property tests and fuzzing of DSSE, JCS, admissibility and floor-join code; a small reference model for `17` S1–S10 | implementation defects are testable |
| RK-06 | Development flag misuse through social engineering or CI | medium | medium | development installs never eligible; floors from the EmbeddedSnapshot; override gate; D030 HIGH | an operator answering the gate accepts the risk |
| RK-07 | Historical registry depends on correct reproduction of old payloads | low | low | independently reproduced by the review; registry grants recognition only, never eligibility | none |
| RK-08 | Prior harness behaviour changes | certain | low | classification rules and signed re-proof (`13` §8) | verifier judgement |
| RK-09 | New dependency supply chain (Ed25519 crate) | low | high | pinned version; recorded review; algorithm abstraction | standard dependency risk |
| RK-10 | Trust files add repository noise and merge conflicts | medium | low | small signed files changed only by transactions; conflicts resolve to one authenticated identity or `PARTIAL` | minor |
| RK-11 | The binary remains the TCB | — | high | artifact statements; bootstrap verification; OP-6 confirmation | out of scope by definition |
| RK-12 | Signatures never expire | — | medium | lifecycle through revocation, certification withdrawal, min-sequence raise; optional TSS expiry only for mode B | intended (offline verification) |
| RK-13 | Large model verification slows plugin start and rebuilds | medium | low | fs-verity; change-triggered full digests; full verification bracketing persistent writes | query-path residual where fs-verity is unavailable (VR-4) |
| RK-14 | Caller-declared acting role (V-L5) unchanged | — | medium | gates bound to statement digests | unchanged boundary |
| RK-15 | Scope growth delays 4.1.6 compared with a bounded patch | high | medium | phased work packages; profiles may slip to a MINOR | the bounded patch is not an acceptable substitute (E1, E2, R1, R2b) |
| RK-16 | Every production install and update needs a human gate (OP-3 mode A), slowing automation | high | medium | the existing gate channel; mode B available to the owner with a clock trade-off | friction by design |
| RK-17 | Floor registration couples kernel changes to root ceremonies | medium | medium | floors change rarely; `draft-policy` shows exactly which keys changed | a ceremony per floor-raising release |
| RK-18 | Consumers on legacy kernels become read-only until they update | certain | medium | clear doctor remediation; update path works offline from a bundle | intended: legacy releases are REJECTED |
| RK-19 | Platform primitives (openat2, RENAME_EXCHANGE, reparse-point checks) differ across OSes | medium | medium | `SecureDir` abstraction with per-platform fallbacks under the journal; `TRUST_PLATFORM_UNSUPPORTED` elsewhere | reduced platform coverage for the production profile |
| RK-20 | Rewiring every file mutation through GovernedFs may cause regressions | high | medium | interception conformance across all commands; prior harnesses | regression risk handled by verification |
| RK-21 | Pre-RoT binaries can still damage a RoT-1 project by explicit operator action (LC-1) | medium | low | fail-closed detection and reinstall remedy; protocol lists unsupported binaries | availability only |
| RK-22 | Mis-issued TPS or TSS (wrong floor, omitted revocation) | low | high | `draft-policy` diff and `publish` admissibility checks before signing; regression detection by verifiers; correcting higher versions | operational error window |
| RK-23 | Per-machine lineage confirmation (OP-6 mode a) adds onboarding friction | medium | low | pin files for CI; one confirmation per machine | friction by design |
| RK-24 | Owner-chosen OP-3 mode B introduces clock trust | depends on OP-3 | medium | default mode A; clock rollback heuristic | RS-2 |
