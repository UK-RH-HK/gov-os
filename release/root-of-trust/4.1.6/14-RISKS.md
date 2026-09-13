# Output 14 — Risks and trade-offs

| ID | Risk / trade-off | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|---|
| RK-01 | Key custody burden; threshold root loss forces re-bootstrap | low | high | 2-of-3 custodians, standby keys, ceremony records, re-attestation keeps payload digests stable | reconfirmation cost if it happens |
| RK-02 | Freeze attack: an offline machine never learns of a revocation | medium (air-gapped use) | medium | revocation floor in every binary and bundle; D032 metadata-age warning (OP-5); overlay may make freshness gating | accepted for G5 (offline verification) |
| RK-03 | Signing friction slows repair iterations | high | low | builder iterates on the test profile; owner signs only candidates handed to the verifier | one signing per candidate |
| RK-04 | Signature proves origin, not correctness; a malicious commit can be signed | low | high | sign-what-you-reproduced, independent verification, separate certification holder, revocation | insider collusion of builder and certifier |
| RK-05 | Parser/canonicalisation bugs in new crypto code | medium | high | minimal strict format, compiled-in schemas, cross-implementation vectors, fuzzing of DSSE/JCS parsers recommended, `verify_strict` semantics | implementation defects are testable, not architectural |
| RK-06 | Development flag misuse through social engineering or CI configuration | medium | medium | production floors stay on the embedded baseline for unsigned kernels; override gate; permanent labels; D030 HIGH | an operator who answers the gate accepts the risk explicitly |
| RK-07 | Legacy identity statement depends on correctly reproducing old payloads | low | medium | reproduce from recorded commits; cross-check with digests already recorded by independent verifiers | none if reproduction matches |
| RK-08 | Frozen harness behaviour changes | certain (HV-11 on production) | low | documented classification and signed re-proof (`12` §4) | verifier judgement |
| RK-09 | New dependency supply chain (Ed25519 crate) | low | high | pinned version, recorded review, algorithm abstraction for replacement | standard dependency risk |
| RK-10 | Trust files add repository noise and merge conflicts | medium | low | small files changed only by updates; conflicts resolve to one authenticated identity or fail closed | minor |
| RK-11 | The binary remains the TCB | — | high | artifact statements, independent bootstrap verification, upgrade verification by the previous binary | out of scope by definition |
| RK-12 | Signatures never expire | — | medium | lifecycle through revocation and certification withdrawal | intended (offline verification) |
| RK-13 | Large model digests slow plugin start | medium | low | size/mtime-gated full digests plus sampled checks (`10` §5) | small window between full checks |
| RK-14 | Caller-declared role (V-L5) unchanged | — | medium | human gates bound to statement digests | unchanged documented boundary |
| RK-15 | Scope growth delays 4.1.6 versus the bounded §12 patch | high | medium | phased work packages; profile install and fetch may slip to a MINOR release without weakening G1–G10 for kernels | the bounded patch alone is **not** an acceptable substitute (E1, E2) |
