---
name: sandbox-codegraph-adopt-reds
description: "inside gov launch's sandbox the code graph fails (ADOPT_CODE_GRAPH_UNREADABLE, CODEGRAPH_RUNTIME_PATH_TOO_LONG): adopt move cases go red there; the lead confirms them outside"
metadata:
  node_type: memory
  type: project
  originSessionId: 49208027-8299-4c46-8aee-ab4fd6685c60
  modified: 2026-11-16T08:24:51.787Z
---

A launched worker's run of the adopt suites (W2-88 `test_w2_88_f1_codegraph.py`, W1-41 path_map/unknown/verdict, W2-23 rollback/setup/unheld) goes red in the sandbox: `codebase-memory-mcp index_repository failed` / `CODEGRAPH_RUNTIME_PATH_TOO_LONG`. On the same head, outside the sandbox (lead_verify), all were green (W2-190, 2026-11-16: W2-88 537, W1-41 100, W2-23 33 passed).

**Why:** the code-graph tool cannot index from inside the sandbox; not a product fault.
**How to apply:** in an adopt engineer's brief, say these cases are confirmed by the lead's lead_verify, not in the sandbox, so the worker doesn't spend 15+ min baselining them; never count them as the ticket's reds. See [[lead-verify-load-reddens-timing]].
