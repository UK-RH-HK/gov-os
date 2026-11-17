---
name: read-the-rule-before-routing
description: read the governing code's own rule (docstring) before sending a route; I sent EXAMIN an accepted_reds route, then had to correct it (owner entry naming each test + Role: owner commit) minutes later (11-16)
metadata:
  type: feedback
---

On 11-16 at 15:4x I told EXAMIN's CTO to add `accepted_reds` entries in its own commit. The ratchet's docstring, which I read only after sending, counts an entry only when its decision is an ACCEPTED owner entry of the register naming each test, and every commit adding it carries `Role: owner`. I sent a correction at once.

**Why:** a wrong route to another CTO costs its run and a correction message, and an entry added the wrong way is itself a finding.

**How to apply:** before sending a product route to a CTO, open the deciding module's docstring or code (e.g. src/gov/close/ratchet.py) and check every condition it states. Related: [[wake-examin-cto-after-reply]].
