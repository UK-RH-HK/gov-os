---
id: CAP-52
type: capability
status: PROPOSED
state_class: DERIVED
title: Model-agnostic adapters (provider, IDE, CLI)
depends_on:
- CONTRACT-v4
---

# CAP-52: Model-agnostic adapters (provider, IDE, CLI)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can use Claude Code or an AGENTS.md-reading harness with the same rules, generated from one source.
- **Acceptance:** `rulesync generate` produces CLAUDE.md, AGENTS.md and `.claude/`; CI fails when a generated file differs from its source; the Claude Code adapter carries every hook and deny rule.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-52.a, CAP-52.b
