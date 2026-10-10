---
id: CAP-58.d
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Claim split by tool: in a launched worker session the OS sandbox stops a Bash write outside the repository without parsing the command; the file tools (Read, Edit, Write) run outside the sandbox and are held by the permission rules and the guard; `Edit(...)` and `Read(...)` deny rules bind both layers'
depends_on:
- CAP-58
---

# CAP-58.d: Claim split by tool: in a launched worker session the OS sandbox stops a Bash write outside the repository without parsing the command; the file tools (Read, Edit, Write) run outside the sandbox and are held by the permission rules and the guard; `Edit(...)` and `Read(...)` deny rules bind both layers

A covers item of CAP-58 (Path guards as default-deny allow-lists). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Claim split by tool: in a launched worker session the OS sandbox stops a Bash write outside the repository without parsing the command; the file tools (Read, Edit, Write) run outside the sandbox and are held by the permission rules and the guard; `Edit(...)` and `Read(...)` deny rules bind both layers
- **Wave:** W1
