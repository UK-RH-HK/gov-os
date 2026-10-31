---
id: DAEO-nqa2
status: open
deps: [DAEO-zpdj, DAEO-0mtg]
links: [DAEO-8lmb]
created: 2026-10-31T13:15:13Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-90b
tags: [wave-2, test-revision, guard, lite]
wbs_id: W2-90b
title: 'W2-90''s next round: the cases still tied to this repository''s live wiring move to the kernel''s wiring now that the template''s install block is removed and its hook lines pinned (W2-105, W2-106)'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on:
- DAEO-zpdj
- DAEO-0mtg
allowed_paths:
- tests/acceptance/W1-05/test_w1_05_live_hooks.py
- tests/acceptance/W1-05/conftest.py
- tests/acceptance/W1-46/test_w1_46_research_installs.py
- tests/acceptance/W1-46/test_w1_46_live_sessions.py
- tests/acceptance/W1-46/conftest.py
- tests/acceptance/W2-59/test_w2_59_hook_lines.py
- tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py
- tests/acceptance/W2-65/test_w2_65_hook_lines.py
- tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py
- tests/acceptance/W1-33/w1_33_support.py
- tests/acceptance/W1-47/w1_47_support.py
- tests/acceptance/W1-50/test_w1_50_freeze_launcher.py
- tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py
- tests/acceptance/W2-54/w2_54_support.py
- tests/acceptance/W2-90/w2_90_kernel_wiring.py
- tests/acceptance/W2-90/README.md
- tests/acceptance/W2-90b/**
kpis:
  success:
  - 'W2-90''s seven named reds (W1-05''s two orchestrator-asks cases, W1-46''s research npm-install case, four W2-59 cases) judge the kernel''s wiring and pass on the head with W2-105 and W2-106 merged [DEC-965 item 1, DEC-966]'
  - 'The 14 parametrized ids ACT 1 removed without a red (W2-59''s 10 post-tool ids, W2-65''s 4) and W2-59''s empty-parameter skip are back, on the template''s post-tool lines [DEC-965 item 4]'
  - 'W1-33''s four guard-and-launcher cases and W1-05''s two setup errors (their fixture repositories lack the five-rule hook file since ACT 1) judge the kernel''s wiring and pass; W2-54''s sandboxed-worker case''s cause is confirmed and, if it is the same, fixed the same way [DEC-970, DEC-953 item 2]'
  - 'The stand-in homes of the harnesses (W1-47''s installed environment, W1-46''s live sessions, W1-50''s freeze launcher) use the editable install''s gov, so with the hook lines pinned they judge the worktree''s code, not the installed copy [DEC-970, W2-106''s P2]'
  - 'Nothing is lowered: no case deleted, skipped, xfailed or weakened; every revised file''s commit carries Rewrite-Reason: DEC-953 item 2; a README under the ticket''s folder maps every case [DEC-906, MR-3]'
  failure:
  - 'A revised case still reads this repository''s live settings, or is red with W2-105 and W2-106 merged.'
  - 'A case deleted, skipped, xfailed or its verdict weakened.'
profile: LITE
sources:
- DEC-965
- DEC-970
- DEC-966
- DEC-953
- DEC-906
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-90b/
  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suites (DEC-892)
track: A
list_rows: []
---
# W2-90b W2-90's next round

Card: DEC-965 item 4 and DEC-970, filed by PLAN-GROWTH-1 §2 gap 1 (W2-90, `DAEO-8lmb`, is closed). It starts when W2-105 (the template's install block removed) and W2-106 (its hook lines pinned) have merged, so the seven cases P1-A and P1-B held can move to the kernel's wiring.
