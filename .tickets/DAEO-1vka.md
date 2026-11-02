---
id: DAEO-1vka
status: open
deps: [DAEO-clon]
links: [DAEO-clon, DAEO-wnnz, DAEO-cv58]
created: 2026-11-02T13:50:25Z
type: task
priority: 0
assignee: engineer
external-ref: W2-127
tags: [wave-2, implementation, launch, sandbox, full]
wbs_id: W2-127
title: 'The shared reranker reachable from the launch sandbox: its one socket path allowed, nothing else (P-W2-112-T2 (a), DEC-1035)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-clon
allowed_paths:
- src/gov/launch/launcher.py
- tests/unit/launch/test_w2_127*
- docs/changes/W2-127-evidence.md
kpis:
  success:
  - 'A session started by `gov launch` (sandboxed) can connect to the shared reranker service''s socket (W2-112: one path in the user''s own folder, mode 0600) and gets its answers: the sandbox block allows that one Unix socket path and no other; the path comes from the same setting the service uses, never a pattern wider than it [DEC-1035, P-W2-112-T2 (a)]'
  - 'Nothing else in the sandbox widens: no other Unix socket, no network port, `allowUnsandboxedCommands` false and `strictAllowlist` as today; `sandbox_faults` still refuses any other change; a planted sandboxed session that opens another Unix socket is refused [DEC-1035]'
  - 'Measured, in docs/changes/W2-127-evidence.md: a sandboxed worker''s search reranked by the shared service (not the fallback), and its time against the fallback''s [DEC-1035]'
  failure:
  - 'A sandboxed session that can open any Unix socket or port beyond the reranker''s one path (containment widened).'
  - 'A sandboxed search that still falls back while the service runs.'
profile: FULL
sources:
- DEC-1035
- DEC-1034
- DEC-1033
- DEC-799
est_loc: 40
acceptance_tests:
  path: tests/acceptance/W2-127/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-127 The shared reranker reachable from the launch sandbox

The owner's DEC-1035 (P-W2-112-T2 (a)): the `gov launch` sandbox refuses `socket(AF_UNIX)`, so sandboxed sessions,
many of the agents that search memory among them, can never reach W2-112's shared reranker and always fall back (a
GPU slot or unranked, named). Until this lands, that fallback stands (option (c)). This ticket allows the service's one
socket path in the sandbox block that `src/gov/launch/launcher.py` builds, and nothing else. It runs right after
W2-112 lands, before EXAMIN's copy. W2-56 and W2-60a (built, held) also hold `launcher.py`: keep the change small;
the merge order settles any overlap. FULL: the sandbox is containment.
