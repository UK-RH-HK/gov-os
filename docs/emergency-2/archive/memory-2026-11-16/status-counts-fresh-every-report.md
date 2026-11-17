---
name: status-counts-fresh-every-report
description: "run status_block.py fresh for EVERY report's status block; never copy counts or leads from an earlier report"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T16:37:39.795Z
---

On 11-16 my reports from 15:20 to 15:58 said "170 closed of 182" after W2-81's reopening (820cd6f61, 15:20) had made it 169. Reports after 16:22 said "of 184" after W2-195 (06cd7f869) had made it 185, and "in flight 6" and the leads list were stale too. The owner caught the jump and asked for every change and every new ticket's approving line (DEC-974).

**Why:** I copied the previous block's numbers forward between reports instead of re-running the counter.

**How to apply:** run `python3 .gov-runtime/scratch/orchestrator/tools/status_block.py` in the same response as every report and copy from its output only. When a count changes, name the ticket and the commit. Related: [[report-ends-with-status-block]], [[stamp-from-date-output]], [[status-block-names-new-tickets]].
