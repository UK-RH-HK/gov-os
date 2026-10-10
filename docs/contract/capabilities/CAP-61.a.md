---
id: CAP-61.a
type: capability
status: PROPOSED
state_class: DERIVED
title: 'The launcher refuses to start a worker session unless the sandbox is on, strict and fail-closed: enabled, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, network `strictAllowlist`; the configuration is passed through `--settings`, never read from the repository, whose settings carry no sandbox block; the launcher sets no `excludedCommands`'
depends_on:
- CAP-61
---

# CAP-61.a: The launcher refuses to start a worker session unless the sandbox is on, strict and fail-closed: enabled, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, network `strictAllowlist`; the configuration is passed through `--settings`, never read from the repository, whose settings carry no sandbox block; the launcher sets no `excludedCommands`

A covers item of CAP-61 (Worker session launcher and OS sandbox). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** The launcher refuses to start a worker session unless the sandbox is on, strict and fail-closed: enabled, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, network `strictAllowlist`; the configuration is passed through `--settings`, never read from the repository, whose settings carry no sandbox block; the launcher sets no `excludedCommands`
- **Wave:** W1
