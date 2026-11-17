---
name: lead-verify-load-reddens-timing
description: "lead_verify's own parallel run (load 10-20) reddens CPU-time hook-timing cases; re-run them alone once at quiet behind a bounded load gate, and name them load-sensitive"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6542ebab-e51e-4053-b0fc-fc69c444d361
  modified: 2026-11-15T21:49:39.842Z
---

W2-111 r5 (2026-11-15): `gov accept` passed 111/0 at load 1.5-5, but lead_verify's parallel run (8,797 tests, load 10-20) failed 5 live-hook timing cases (after 106-174 ms; before 130-170, quiet ~75): W2-111's CPU-time-less-reference method still inflates ~1.5-1.8x when siblings are busy. Re-run alone once at load < 6 (a bounded 60-min gate script, wait_for on its exit file): 5/5 pass (57.7-78.8 ms).

**Why:** the run rules allow one alone re-run of a load-sensitive case; re-running under the same load wastes the one try, and retrying into green is forbidden.
**How to apply:** for timing reds in lead_verify, first check skip_known.json, then one alone re-run behind a load gate (`.gov-runtime/scratch/lead/r5/rerun5.sh` pattern); report the verify as RED with the triage, and raise the nightly risk to the CTO (DEC-968: no accepted reds). Related: [[load-tests-outside-critical-windows]], [[pytest-through-heavy-slot]].
