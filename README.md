# Governance OS (agentic-engineering-os) — canonical source repository

The upstream, model-agnostic implementation of the **Dynamic Agentic Software Engineering Operating Framework v4.1**
as real software: an immutable kernel payload, a Rust deterministic core and `gov` CLI, a language-neutral capability
plugin protocol, declarative framework migrations, synthetic certification fixtures and an implementer test harness.
Product repositories in any language consume released kernels through `gov init` / `gov adopt` / `gov update`.

## Governance OS — Start Here / Authority Map

Use these sources in authority order:

1. **Original product-intent sources** (historical intent):
   [Operating Framework v4.1.2](./DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md),
   [Release, Distribution, Adoption and Upstream Learning Protocol v1.2](./GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md), and
   [Adoption, Migration and Independent Audit Protocol v3.0](./GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md).
2. **Current product-owner capability contract:**
   [Governance OS Capability Acceptance Contract v3](./Governance_OS_Capability_Acceptance_Contract_v3.md).
   This root file is the product-owner-supplied normative capability source. Generated or machine-readable
   representations may be executable views, but they do not replace the owner source unless an explicit
   owner-approved decision changes that rule.
3. **Active owner decisions and directives:** [`./spec/decisions/`](./spec/decisions/).
4. **Accepted architecture records:** [`./spec/architecture/`](./spec/architecture/).
5. **Frozen lifecycle-gate contracts**, as referenced by the active decisions and architecture.
6. **Exact candidate/evidence state and durable orchestration state:** [`./release/orchestration/`](./release/orchestration/).
7. **Current operator control panel:**
   [Governance OS Interactive Stage Control Panel V8.2](./release/orchestration/control-panel/Governance_OS_Interactive_Stage_Control_Panel_FINAL_AUDITED_v8_2.html)
   — `NON_NORMATIVE_OPERATOR_UI`, SHA-256 `6fecfb6b2be86031137433a1cf7e960eeb9ca0c23b4890b2eb54c0546158269c`.
   It is a runbook/orchestration interface and never overrides the sources above. V8.1
   ([`…_v8_1.html`](./release/orchestration/control-panel/Governance_OS_Interactive_Stage_Control_Panel_FINAL_AUDITED_v8_1.html))
   is retained unchanged as **historical Phase-1 operator evidence only** and is **not** a current operator interface.

A new persistent Opus phase-orchestrator session should open that exact V8.2 HTML and use its
**V8.2 — Self-locating durable autonomous Phase Orchestrator** launcher. The launcher determines the active phase
from committed Git/orchestration evidence, then uses the matching phase prompts internally. The product owner should
not need to relay routine reviewer/builder prompts between agents. Each completed phase stops at its acceptance token;
the next outer session uses the same universal launcher again.

| Governing documents | |
|---|---|
| Operating framework v4.1.2 | [DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md](DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md) |
| Release, distribution, adoption & upstream learning v1.2 | [GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md](GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md) |
| Adoption, migration & independent audit v3.0 | [GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md](GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md) |
| Architecture decision (Rust-first core, polyglot capabilities) | [spec/decisions/D-0002.yaml](spec/decisions/D-0002.yaml), [spec/architecture/ARCH-0001.yaml](spec/architecture/ARCH-0001.yaml) |

## Layout
```text
framework/      kernel payload (constitution, policies, schemas, skills, adapters, roles, taxonomy, commands, overlay templates)
migrations/     declarative framework-version migrations        tools/        tool + MCP registries (part of the payload)
runtime/        Rust library: the deterministic core             cli/          Rust binary `gov`
capabilities/   polyglot plugins (gov-capability/1)             fixtures/     seven synthetic certification projects
tests/          certification harness (Rust integration tests)  release/      release manifests, notes, evidence
spec/           this repository's own governed records           docs/         architecture, commands, fixtures, evidence
lessons/inbox/  upstream lesson packets                          change-proposals/  framework change proposals
```

## Build and use
```bash
cargo build --release                 # produces target/release/gov (no Python/Node required to run the core)
bin/gov version                       # shim: builds on first use
bin/gov init --name my-project --alias proj-x --intent "..."      # greenfield
bin/gov adopt baseline && bin/gov adopt inventory && ...          # brownfield, stages A0–A11
bin/gov doctor && bin/gov status && bin/gov continue              # daily operation
cargo test                            # unit + certification suite (implementer evidence)
```
Optional Python capability plugins: `capabilities/python` (`python3 -m govos_capabilities.code_intel_python_ast`).

## Documentation
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/COMMANDS.md](docs/COMMANDS.md) · [docs/FIXTURES.md](docs/FIXTURES.md) ·
[docs/RELEASE.md](docs/RELEASE.md) · [docs/EVIDENCE.md](docs/EVIDENCE.md) · [capabilities/PROTOCOL.md](capabilities/PROTOCOL.md)

## Certification status
`release/CERTIFICATION_STATUS.md`: releases 4.1.2, 4.1.3 and 4.1.4 were **REJECTED** by independent verification
(`release/verification/4.1.2/`, `.../4.1.3/`, `.../4.1.4/`); repair candidate **4.1.5** (branch
`release/4.1.5-rc1`) is **READY_FOR_INDEPENDENT_REVERIFICATION** (`release/repair/4.1.5/REPAIR_REPORT.md`). The implementer does not certify its own release (protocol §6). An
independent verifier runs the fixtures, the suite and the held-out harness from a fresh context and records the verdict
in the release manifest.
