---
id: DAEO-emkd
status: open
deps: [DAEO-dtv3]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-02
tags: [wave-1, implementation, full]
wbs_id: W1-02
title: PreToolUse default-deny guard
class: implementation
role: engineer
depends_on:
- W1-01
allowed_paths:
- src/gov/guard/**
- template/governance/kernel/hooks/pretooluse*
- tests/unit/guard/**
kpis:
  success:
  - Edit/Write/Bash writes are allowed only inside the active ticket allowed_paths plus the kernel scratch set, per role
  - The engineer role is denied every write under tests/acceptance/**; the independent-test-designer role is allowed only there
  - The freeze flag (gov pause) denies every write; the guard reads ticket frontmatter directly; decision in < 100 ms p95
  - 'A session with no declared role, or an unknown role, is read-only: every write is denied'
  failure:
  - Any write outside allowed_paths is allowed
  - Guard crash or timeout lets the call through without a recorded finding
  - A session with no or an unknown role can write anywhere
profile: FULL
sources:
- G-01
- S0a-G-10
- CAP-58
- CAP-05
- DEC-041
- DEC-069
- OWNER-DECISION-P2-0001 BC-P2-08
- MR-3
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W1-02/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-02 PreToolUse default-deny guard

Default-deny allow-list per role and per ticket (G-01), reading the ticket file frontmatter; honours the freeze flag.
