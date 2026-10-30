---
id: DAEO-8lmb
status: open
deps: []
links: []
created: 2026-10-30T21:44:47Z
type: task
priority: 0
assignee: independent-test-designer
external-ref: W2-90
tags: [wave-2, test-revision, guard, lite]
wbs_id: W2-90
title: 'The 235 live-wiring tests judge the kernel''s wiring: after ACT 1, the cases that asserted this repository runs the full guard and its containment hooks are revised to assert the kernel''s template and a generated repository do, lowering nothing'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-05/test_w1_05_live_hooks.py
- tests/acceptance/W1-05/test_w1_05_role_subagents.py
- tests/acceptance/W1-28/test_w1_28_launch_product_spec.py
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py
- tests/acceptance/W1-46/test_w1_46_install_spellings.py
- tests/acceptance/W1-46/test_w1_46_links_and_cp_targets.py
- tests/acceptance/W1-46/test_w1_46_live_sessions.py
- tests/acceptance/W1-46/test_w1_46_options_after_the_destination.py
- tests/acceptance/W1-46/test_w1_46_research_installs.py
- tests/acceptance/W1-46/test_w1_46_research_role.py
- tests/acceptance/W1-46/test_w1_46_role_settings.py
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py
- tests/acceptance/W1-47/test_w1_47_failed_commands.py
- tests/acceptance/W1-49/test_w1_49_registration.py
- tests/acceptance/W1-50/test_w1_50_freeze_launcher.py
- tests/acceptance/W1-50/test_w1_50_freeze_live_pause.py
- tests/acceptance/W2-59/test_w2_59_hook_lines.py
- tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py
- tests/acceptance/W2-65/test_w2_65_hook_lines.py
- tests/acceptance/W1-05/conftest.py
- tests/acceptance/W1-46/conftest.py
- tests/acceptance/W2-90/**
kpis:
  success:
  - 'Each of the 235 cases red after ACT 1 (the list in the ticket body) passes on the integration head after ACT 1, and judges the kernel''s guard wiring (the template''s generated settings, or a repository generated from the template), not this repository''s live `.claude/settings.json` [DEC-957, DEC-953]'
  - 'No expectation on the product is lowered: every refusal, hook line and registration a revised case asserted of this repository it now asserts of the kernel''s wiring, with the same verdict; a case that cannot be moved is named in the README with its reason, never deleted or skipped [DEC-906, MR-3]'
  - 'Each revised file''s commit carries `Rewrite-Reason: DEC-953 item 2`, and `tests/acceptance/W2-90/README.md` maps every one of the 235 case ids to its revised case [DEC-906, DEC-957]'
  - 'The revised suites (the 19 files) are green on the head after ACT 1 and green on the base before it (`aafd45c1`), each in a scoped run of the corrected tests (DEC-954, P-W2-64-1 (a)) [DEC-954]'
  failure:
  - 'A revised case still reads this repository''s live settings or hooks and is red after ACT 1.'
  - 'A case deleted, skipped, marked xfail, or its asserted verdict weakened.'
  - 'A file outside the ticket''s paths changed, or code changed.'
profile: LITE
sources:
- DEC-957
- DEC-953
- DEC-954
- DEC-955
- DEC-906
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W2-90/
  author: independent-test-designer (MR-3); a test-revision ticket judged on its declared revised suites (DEC-892); the README maps the 235 ids
track: A
list_rows: []
---
# W2-90 The 235 live-wiring tests judge the kernel's wiring

Card: the owner's named decision under DEC-906, given in DEC-957 (ACT 1, option (a)); the first lead after ACT 1.

- **Why:** ACT 1 (`6c36c7b5`) switched this repository's own pre-tool hook from the kernel's full guard to the five-rule hook (`.claude/hooks/pretooluse.py`) and removed the containment hooks (PostToolUse, PostToolUseFailure), under DEC-953 item 2. The kernel's guard stays built and tested in `template/` and `src/gov/guard/`: nothing is deleted from the product. 235 cases in 19 files asserted that *this repository* runs the full guard and its containment hooks; they went red with ACT 1 and pass on the base (measured on a trial clone, each red re-run alone on both sides: `packages/ACT-1-GUARD.md` "Tests").
- **The 235, by suite:** W1-46 142 (the live guard's refusals: installs, links, `cp` and `mv` targets, role settings, the research role, scratch); W1-05 77 (live hooks and role subagents); W2-59 5 and W2-65 1 (the hook lines); W1-47 4 and W1-49 2 (the containment hooks registered); W1-28 2 and W1-50 2 (the launcher and freeze through the live settings). The full id list is in the lead's brief.
- **What the revision does:** each case asserts the same behaviour of the kernel's wiring: the settings the template generates (rulesync output from `template/`), or a repository generated from the template (copier, as other suites already do), with the kernel's hook running as the generated settings register it. The verdict each case expects stays as it is.
- **What it never does:** lower an expectation; delete, skip or xfail a case; change code, the template or the live settings; touch the product's own guard tests (they are green).
- **Paths:** the 19 files, two shared conftests if a fixture must move, and `tests/acceptance/W2-90/` (README). A helper needed in another file is a package.
- **Verification:** a scoped run of the 19 files on the head after ACT 1 and on `aafd45c1` before it; the nightly covers the rest. Closes test on the pre-ACT head (`CLOSE-HEAD`) until this lands.
- **Profile LITE:** a test revision under a named owner decision; no judge, gate or product code changes.
