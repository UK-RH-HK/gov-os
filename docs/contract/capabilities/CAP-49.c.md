---
id: CAP-49.c
type: capability
status: PROPOSED
state_class: DERIVED
title: 'The oracle is hidden from every session started in the repository root, the unsandboxed orchestrator included, by two layers: a `Read` deny rule with the oracle''s absolute path in the committed `.claude/settings.json`, and the guard denying any tool call whose input names the oracle path (Read, Grep, Glob, Bash); an opaque Bash read in the orchestrator''s own session is an accepted residual; the oracle path is held in `governance/project/held-out.yaml` and in the committed deny rule built from it; register entry DEC-067 names the directory historically; the guard and the launcher take the path from `held-out.yaml`, and no acceptance test names it'
depends_on:
- CAP-49
---

# CAP-49.c: The oracle is hidden from every session started in the repository root, the unsandboxed orchestrator included, by two layers: a `Read` deny rule with the oracle's absolute path in the committed `.claude/settings.json`, and the guard denying any tool call whose input names the oracle path (Read, Grep, Glob, Bash); an opaque Bash read in the orchestrator's own session is an accepted residual; the oracle path is held in `governance/project/held-out.yaml` and in the committed deny rule built from it; register entry DEC-067 names the directory historically; the guard and the launcher take the path from `held-out.yaml`, and no acceptance test names it

A covers item of CAP-49 (Qualification oracle (synthetic repos, fault injection, hidden tests)). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** The oracle is hidden from every session started in the repository root, the unsandboxed orchestrator included, by two layers: a `Read` deny rule with the oracle's absolute path in the committed `.claude/settings.json`, and the guard denying any tool call whose input names the oracle path (Read, Grep, Glob, Bash); an opaque Bash read in the orchestrator's own session is an accepted residual; the oracle path is held in `governance/project/held-out.yaml` and in the committed deny rule built from it; register entry DEC-067 names the directory historically; the guard and the launcher take the path from `held-out.yaml`, and no acceptance test names it
- **Wave:** W1
