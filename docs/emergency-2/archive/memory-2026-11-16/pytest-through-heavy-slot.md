---
name: pytest-through-heavy-slot
description: "every pytest (lead's and workers') runs through heavy_slot.sh; pass the form into every worker brief"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f1129d1a-f14c-4971-9201-90141545cc51
  modified: 2026-11-12T06:05:41.915Z
---

Every pytest run, the lead's own and every worker's, goes through the heavy-slot gate:
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <the pytest command>`,
one folder per run, TMPDIR outside the repository, PYTHONUSERBASE=/home/usain/.local, `-p no:cacheprovider -o tmp_path_retention_policy=failed`.
Never kill a run already in progress to switch it to the new form.

**Why:** the CTO's order of 2026-11-12, after incident T1 0556: a pytest run outside a slot that goes past 5 minutes holds back every other lead's start.

**How to apply:** use this form for every pytest command you run yourself, and put it in the rules of every worker brief (test designer, engineer, reviewer). Related: [[check-before-ready-line]].

**2026-11-16 05:50 (W2-81 reopen, as lead):** outside the sandbox `$TMPDIR` is empty; I set TMPDIR to the tree's .gov-runtime/scratch/tmp and W2-81's hermetic guard refused all 300 cases (InsideThisRepository). The lead's own TMPDIR is a /tmp/<name> folder (outside every repo); only workers use "$TMPDIR".

**11-16:** `gov accept` spawns the whole acceptance pytest, so it is a heavy step too: W2-88's lead ran `gov accept W2-88` outside a slot for 20+ min (incident 2026-11-16-0953-outside-slot) because my brief named only pytest. In every standing paragraph, name `gov accept`, `lead_verify` and the scoped run explicitly as heavy steps run through heavy_slot.sh.
