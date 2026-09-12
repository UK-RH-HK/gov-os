# Governance OS (agentic-engineering-os) — canonical source repository

The upstream, model-agnostic implementation of the **Dynamic Agentic Software Engineering Operating Framework v4.1**
as real software: an immutable kernel payload, a Rust deterministic core and `gov` CLI, a language-neutral capability
plugin protocol, declarative framework migrations, synthetic certification fixtures and an implementer test harness.
Product repositories in any language consume released kernels through `gov init` / `gov adopt` / `gov update`.

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
