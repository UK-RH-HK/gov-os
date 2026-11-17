---
name: cto-fixes-path-cases
description: "The CTO decides and routes (no owner wait) a path case judging any branch, and a test revision that only records a behaviour the owner already decided"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b2f0511f-891b-4874-8930-6d34ca5972ea
  modified: 2026-11-12T22:50:58.447Z
---

Two kinds of test fix no longer stop a lead to wait for the owner (DEC-1156 (7), 2026-11-12, standing):
- a path case that judges any branch instead of its own (fix: judged only when HEAD is `refs/heads/w2/<own W2>`, skipped elsewhere naming the branch or "detached HEAD", as W2-180 and P1-N did);
- an older case asserting a behaviour the owner has since decided (e.g. W2-159's `test_route.py` pinning the pre-DEC-1153 ACT_PATHS).

**Why:** these blocked W2-121b, W2-160 and W2-172 on 2026-11-12 (ejections and PACKAGES) for decisions already made.

**How to apply:** the CTO routes the revision to a test designer (widen the ticket that meets it by that one file, or land an existing fix ticket), runs a narrow independent check of it ([[narrow-check-after-review]]), lands it, and lists it for the owner's reading in the next digest. The CTO still never writes tests/acceptance/** itself. Other widenings and new tickets still need the owner ([[no-ticket-without-owner]]).
