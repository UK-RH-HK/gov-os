# Original requirements baseline

## Reconstruction rule

This baseline is reconstructed only from the three original governing documents. The stage-control panel is used as workflow/prompt evidence, not as proof of original product intent. Contract v3 is compared separately as the current owner target.

## Original product intent

The original product is a model-agnostic, persistent software-engineering operating system. Its source of truth is governed repository state, not an agent conversation. Its defining architecture is broader than security:

- constitutional governance and deterministic precedence;
- repository contract and path map;
- Development Knowledge Fabric with structured, graph, lexical, semantic, code, temporal, episodic, failure, working and capability memory;
- role/authority organization, skills and tools;
- natural-language control mapped to deterministic operations;
- feature/capability readiness and dynamic task DAG;
- research, experiments, CIT-P/CIT-E, independent verification, checkpoints, telemetry and learning;
- canonical Governance OS releases consumed by separate product repositories;
- staged brownfield adoption and independently verified memory/audit.

The system was intended to be a practical engineering operating system, not primarily a high-assurance software-supply-chain product.

## Original security and release requirements

| ID | Original requirement | Source | Security meaning |
|---|---|---|---|
| OB-01 | Higher-precedence authority cannot be silently overridden by retrieval or inference | Framework §§2, 21 | Deterministic authority |
| OB-02 | Sensitive/secret/customer material is isolated and excluded from generic memory/export | Framework §§16, 72; Release Protocol §§14, 17 | Confidentiality boundary |
| OB-03 | Least authority for roles and tools; privileged/destructive actions gated | Framework §§23, 30, 32, 47–53 | Authorization and human control |
| OB-04 | Framework/kernel and project overlay are separate | Framework §80; Release Protocol §4 | Prevent project config from silently becoming framework authority |
| OB-05 | Released kernels are immutable, semantically versioned and carry manifest/file hashes | Framework §75D; Release Protocol §8 | Integrity, identity and reproducibility metadata |
| OB-06 | Release candidates receive independent verification beyond unit tests | Framework §75C; Release Protocol §§6–7 | Independent evidence |
| OB-07 | `gov init`, `gov adopt`, `gov update` preserve overlay/state, verify outcomes and support rollback | Framework §§78–82; Release Protocol §§9–12 | Safe lifecycle transitions |
| OB-08 | Derived memory/index state is rebuildable and not authoritative | Framework §§10–19, 81 | Recovery and source-of-truth separation |
| OB-09 | Governance evidence becomes stale when relevant inputs change | Framework §64 | Evidence currency |
| OB-10 | Brownfield migration is path-first, independently reviewed and verified | Framework §79; both protocols | Safe adoption |
| OB-11 | Upstream export is allowlisted, sanitized and fail-closed | Framework §§75E–75G; Release Protocol §§13–17 | Outbound security |
| OB-12 | A healthy repository has no unresolved critical audit finding and supports clean-machine reconstruction | Framework §76; Adoption Protocol §20 | Health and recovery |

## What the original documents did not require

They did not prescribe:

- digital signatures for release metadata;
- Ed25519, DSSE, JCS, TUF or transparency logs;
- three offline root keys or 2-of-3 root authority;
- delegated registration keys or purpose-specific threshold matrices;
- a separate compiled first-install admitter;
- two first-contact sources that must match;
- a 24-hour mutable trust-state freshness ceiling;
- local admission/account high-water stores;
- 2-of-3 independent binary reproducers;
- compiler diverse-double-compilation or independent bootstrap chains;
- two independent build-environment supplier classes;
- a complete selector/establishing-party decision register;
- CP-1, C0–C3 operation classes or a custom constitutional-surface calculus.

The original `release_hash`, file hashes and `framework.lock` are integrity/identity mechanisms. They do not by themselves imply a cryptographic authenticity PKI. Contract v3 correctly labels authentic root of trust as **POST-VERIFICATION HARDENING**.

## Current contract deltas

Contract v3 keeps the baseline and adds three distinct layers:

1. **Post-verification hardening**: A2 authentic root of trust and F4 plugin trust boundary.
2. **Execution refinements**: O5 G0–G6 health scheduling, V qualification oracle and W artifact flow/consumption integrity.
3. **Lifecycle expansion**: capability evidence freshness and the same contract at build, qualification, release, init/adopt/update, post-adoption and periodic health.

These are current owner-approved requirements. They must be honored going forward, but must not be cited as proof that the 2026-09-12 original baseline always required CP-1.

## Original acceptance boundary

A fair Phase-1 baseline would have accepted a release candidate when:

- the original capability architecture was materially implemented;
- critical/high defects in the stated implementation were resolved;
- immutable release identity and install/update integrity worked;
- independent held-out tests passed sufficiently for candidate acceptance;
- remaining qualification, platform certification and product adoption occurred in later gates.

It would not require proof that every compiler, custodian, offline medium, build supplier and first-contact channel remained uncompromised under every combination. That is a separate assurance programme.
