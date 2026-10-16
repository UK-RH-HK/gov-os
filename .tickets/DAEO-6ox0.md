---
id: DAEO-6ox0
status: open
deps: [DAEO-g0ip, DAEO-1ahb]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: research
external-ref: W2-40
tags: [wave-2, research, full]
wbs_id: W2-40
title: 'EXP-002: the untested sandbox cases and the harness''s hook limits'
class: research
state_class: AUTHORITATIVE
role: research
depends_on:
- DAEO-g0ip
- DAEO-1ahb
allowed_paths:
- docs/research/EXP-002/**
- experiments/EXP-002/**
kpis:
  success:
  - 'Each of these is measured: the sandbox cases: denyWrite on a path that does not exist yet; symlink and hard-link tricks; the seccomp filter; bypassPermissions; subagents inside a sandboxed worker session;
    excludedCommands [CAP-61.f, DEC-160, W2-M336, W2-M337, W2-M350, W2-L316]'
  - 'Each of these is measured: file tools, hooks and MCP servers outside the sandbox [W2-M334, W2-M335]'
  - 'Each of these is measured: the harness''s behaviour at a hook''s time limit, so that the guard''s deadline sits below it [W2-H052, W2-M347, W2-L328]'
  - 'Each of these is measured: live auto-compaction and the PreCompact output [W2-M338, W2-M344].'
  failure: []
profile: FULL
sources:
- CAP-61.f
- DEC-160
est_loc: 60
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
track: C
closes:
- CAP-61.f
- W2-H052
list_rows:
- W2-H052
- W2-I001
- W2-I036
- W2-I037
- W2-L025
- W2-L316
- W2-L328
- W2-M005
- W2-M087
- W2-M234
- W2-M334
- W2-M335
- W2-M336
- W2-M337
- W2-M338
- W2-M344
- W2-M345
- W2-M347
- W2-M350
---
# W2-40 EXP-002: the untested sandbox cases and the harness's hook limits

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-40), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `docs/research/EXP-002/**`, `experiments/EXP-002/**`.
- **KPIs:** each of these is measured:
  - the sandbox cases: `denyWrite` on a path that does not exist yet; symlink and hard-link tricks; the seccomp filter; `bypassPermissions`; subagents inside a sandboxed worker session; `excludedCommands` [CAP-61.f, DEC-160, W2-M336, W2-M337, W2-M350, W2-L316];
  - file tools, hooks and MCP servers outside the sandbox [W2-M334, W2-M335];
  - the harness's behaviour at a hook's time limit, so that the guard's deadline sits below it [W2-H052, W2-M347, W2-L328];
  - live auto-compaction and the PreCompact output [W2-M338, W2-M344].
