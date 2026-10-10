---
id: CAP-58.f
type: capability
status: PROPOSED
state_class: DERIVED
title: The containment check runs on `PostToolUseFailure` as well as `PostToolUse`, because a failed command may have written files before failing; a call refused by a deny rule reaches no hook
depends_on:
- CAP-58
---

# CAP-58.f: The containment check runs on `PostToolUseFailure` as well as `PostToolUse`, because a failed command may have written files before failing; a call refused by a deny rule reaches no hook

A covers item of CAP-58 (Path guards as default-deny allow-lists). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** The containment check runs on `PostToolUseFailure` as well as `PostToolUse`, because a failed command may have written files before failing; a call refused by a deny rule reaches no hook
- **Wave:** W1
