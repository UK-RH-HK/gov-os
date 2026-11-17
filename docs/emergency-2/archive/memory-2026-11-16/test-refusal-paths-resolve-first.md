---
name: test-refusal-paths-resolve-first
description: before using a crafted path to test a "refuses a live path" rule, resolve it (realpath -m) and see where it lands; a miscounted ../ ran a whole rehearsal elsewhere (11-16)
metadata:
  type: feedback
---

On 2026-11-16 07:47 I tested rehearse_rel.sh's new "refuse a scratch dir inside the main tree" rule with `$D/../../../../../home/usain/Dynamic-Agentic-Engineering-OS/x`. I miscounted the `../`: it resolved to `/tmp/home/usain/Dynamic-Agentic-Engineering-OS/x`, a scratch path, so the rule rightly let it through and a full rehearsal (1.5 GB, scratch only, live UNCHANGED) ran there. I removed it.

**Why:** a test meant to prove a refusal can instead run the guarded thing, and with a live-looking path that could be dangerous.

**How to apply:** run `realpath -m <path>` first and check it names what the test intends, or use a symlink or `<live>/../<live>/x` form whose target is certain. Prefer testing refusal rules on the check block alone. Related: [[no-rehearsal-against-live]], [[mirror-copy-skips-live-refresh-tmp]].
