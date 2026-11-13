---
id: DAEO-qyt2
wbs_id: W2-185
external-ref: W2-185
title: "Adopted projects get the context watch: the template wires context_watch.py, portability's lift exemption per hook, W1-38's fixture with seven hooks (W2-182's E gap)"
type: task
class: implementation
role: engineer
profile: STANDARD
status: open
state_class: AUTHORITATIVE
priority: 2
created: 2026-11-13
deps: [DAEO-5y8d]
allowed_paths:
- template/.rulesync/hooks.jsonc
- src/gov/adapters/portability.py
- tests/unit/adapters/test_w2_185_*.py
- tests/acceptance/W1-38/w1_38_support.py  # the fixture copies the seven kernel hooks; a test designer's revision (DEC-1156 (7))
- docs/probes/DAEO-qyt2/**  # the probe record
reads:
- .tickets/DAEO-5y8d.md
- .rulesync/hooks.jsonc
- template/governance/kernel/hooks/**
- tests/acceptance/W2-23/test_w2_23_space.py
- tests/acceptance/W2-05/test_w2_05_hooks_source.py
- tests/unit/gitenv/test_program_env.py
needs: []
waits_on: []
kpis:
  success:
  - 'S1: the template''s hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in postToolUse (matcher Bash, timeout 10), in the root `.rulesync/hooks.jsonc`''s form with the adopted path `governance/kernel/hooks/` [DEC-1163 (6) E (a), DEC-1167] Verify: W2-23 S6 (`tests/acceptance/W2-23/test_w2_23_space.py`) passes, the settings'' hook lines reaching the seven kernel hooks; a planted eighth hook with no wiring fails it'
  - 'S2: portability''s hooks comparison exempts the template''s `posttooluse.py` entry (DEC-971 item 3''s lift, per hook) rather than the whole postToolUse event, so the root''s and the template''s postToolUse compare on what both carry [DEC-971 item 3, DEC-805, DEC-1167] Verify: `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` and `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` pass with S1''s line; unit cases in `tests/unit/adapters/test_w2_185_*.py` for the exemption'
  - 'S3: W1-38''s adopted-project fixture copies the seven kernel hooks (`w1_38_support.py` HOOK_SCRIPTS), so its generated settings name only scripts it copied [DEC-1167, DEC-1156 (7)] Verify: `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` and `test_w1_38_hooks_any_folder.py`''s ordinary-call case pass with S1''s line; the fixture with six hooks fails them'
  failure:
  - 'F1: a hook that really drifts between the root and the template (another matcher or another event than the exempt `posttooluse.py` entry) is still a finding. Verify: a planted extra matcher on the root''s postToolUse, and a planted template hook in another event, each give a hooks finding'
non_goals:
- 'not the root''s own hooks (`.rulesync/hooks.jsonc`, `.claude/`): no change to what this repository''s sessions run'
- 'not W2-182''s other lines (B, C, R, D, F), which landed with W2-182'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1167, DEC-1163, DEC-971, DEC-805, DEC-1156]
acceptance_tests: {path: tests/acceptance/W2-185/}
---

# W2-185 Adopted projects get the context watch (W2-182's E gap)

The owner's P-W2-182-E-1 (1) (DEC-1167): W2-182 lands without E; this ticket carries it as one piece. E's template line
alone turned four cases red (W2-182 run 3, `log/W2-182-A5-run3.json`): portability's per-event lift exemption (DEC-971
item 3) let the root's and template's postToolUse match only by coincidence, and W1-38's fixture copies six hooks. A test
designer writes W2-185's cases and revises W1-38's fixture; an engineer builds S1 and S2; a STANDARD review; the land.
