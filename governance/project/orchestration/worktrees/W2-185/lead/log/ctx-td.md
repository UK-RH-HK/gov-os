{
  "ticket": "DAEO-qyt2",
  "ticket_text": "---\nid: DAEO-qyt2\nwbs_id: W2-185\nexternal-ref: W2-185\ntitle: \"Adopted projects get the context watch: the template wires context_watch.py, portability's lift exemption per hook, W1-38's fixture with seven hooks (W2-182's E gap)\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: STANDARD\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 2\ncreated: 2026-11-13\ndeps: [DAEO-5y8d]\nallowed_paths:\n- template/.rulesync/hooks.jsonc\n- src/gov/adapters/portability.py\n- tests/unit/adapters/test_w2_185_*.py\n- tests/acceptance/W1-38/w1_38_support.py  # the fixture copies the seven kernel hooks; a test designer's revision (DEC-1156 (7))\n- docs/probes/DAEO-qyt2/**  # the probe record\nreads:\n- .tickets/DAEO-5y8d.md\n- .rulesync/hooks.jsonc\n- template/governance/kernel/hooks/**\n- tests/acceptance/W2-23/test_w2_23_space.py\n- tests/acceptance/W2-05/test_w2_05_hooks_source.py\n- tests/unit/gitenv/test_program_env.py\nneeds: []\nwaits_on: []\nkpis:\n  success:\n  - 'S1: the template''s hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in postToolUse (matcher Bash, timeout 10), in the root `.rulesync/hooks.jsonc`''s form with the adopted path `governance/kernel/hooks/` [DEC-1163 (6) E (a), DEC-1167] Verify: W2-23 S6 (`tests/acceptance/W2-23/test_w2_23_space.py`) passes, the settings'' hook lines reaching the seven kernel hooks; a planted eighth hook with no wiring fails it'\n  - 'S2: portability''s hooks comparison exempts the template''s `posttooluse.py` entry (DEC-971 item 3''s lift, per hook) rather than the whole postToolUse event, so the root''s and the template''s postToolUse compare on what both carry [DEC-971 item 3, DEC-805, DEC-1167] Verify: `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` and `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` pass with S1''s line; unit cases in `tests/unit/adapters/test_w2_185_*.py` for the exemption'\n  - 'S3: W1-38''s adopted-project fixture copies the seven kernel hooks (`w1_38_support.py` HOOK_SCRIPTS), so its generated settings name only scripts it copied [DEC-1167, DEC-1156 (7)] Verify: `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` and `test_w1_38_hooks_any_folder.py`''s ordinary-call case pass with S1''s line; the fixture with six hooks fails them'\n  failure:\n  - 'F1: a hook that really drifts between the root and the template (another matcher or another event than the exempt `posttooluse.py` entry) is still a finding. Verify: a planted extra matcher on the root''s postToolUse, and a planted template hook in another event, each give a hooks finding'\nnon_goals:\n- 'not the root''s own hooks (`.rulesync/hooks.jsonc`, `.claude/`): no change to what this repository''s sessions run'\n- 'not W2-182''s other lines (B, C, R, D, F), which landed with W2-182'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1167, DEC-1163, DEC-971, DEC-805, DEC-1156]\nacceptance_tests: {path: tests/acceptance/W2-185/}\n---\n\n# W2-185 Adopted projects get the context watch (W2-182's E gap)\n\nThe owner's P-W2-182-E-1 (1) (DEC-1167): W2-182 lands without E; this ticket carries it as one piece. E's template line\nalone turned four cases red (W2-182 run 3, `log/W2-182-A5-run3.json`): portability's per-event lift exemption (DEC-971\nitem 3) let the root's and template's postToolUse match only by coincidence, and W1-38's fixture copies six hooks. A test\ndesigner writes W2-185's cases and revises W1-38's fixture; an engineer builds S1 and S2; a STANDARD review; the land.\n",
  "authority": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1163",
      "sha256": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "reason": "declared in sources",
      "tokens": 1014
    },
    {
      "id": "DEC-971",
      "sha256": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "reason": "declared in sources",
      "tokens": 702
    },
    {
      "id": "DEC-805",
      "sha256": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "reason": "declared in sources",
      "tokens": 302
    },
    {
      "id": "DEC-1156",
      "sha256": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "reason": "declared in sources",
      "tokens": 1068
    },
    {
      "id": "DAEO-5y8d",
      "sha256": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "reason": "declared in sources",
      "tokens": 623
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1163",
      "sha256": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "reason": "declared in sources",
      "tokens": 1014
    },
    {
      "id": "DEC-971",
      "sha256": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "reason": "declared in sources",
      "tokens": 702
    },
    {
      "id": "DEC-805",
      "sha256": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "reason": "declared in sources",
      "tokens": 302
    },
    {
      "id": "DEC-1156",
      "sha256": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "reason": "declared in sources",
      "tokens": 1068
    },
    {
      "id": "DAEO-5y8d",
      "sha256": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "reason": "declared in sources",
      "tokens": 623
    }
  ],
  "supplementary": [
    {
      "id": "f6c2ee261b8a484c5fae1ed6",
      "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md",
      "text": "## The lead's verification on the same head (not a verdict; it stops the land)\n\n- `gov accept W2-182` on f0cb5284d: pass, 9 passed, 0 failed, every line pass.\n- The scoped run (`lead_verify.sh`, DEC-968, once): **RED, 5604 tests, 6 failed** in the parallel phase; the serial phase\n  was 2/0. Each red was run alone on the head and on its parent 80b19dc16 (without E's line), in clean copies:\n  - **Caused by E's line (green on the parent, red on the head), 4:**\n    - `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` (F-E1).\n    - `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`\n      (the same `HOOKS_MATCHER_DIFFERS`).\n    - `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`: W1-38's adopted-project\n      fixture copies six hook scripts (`w1_38_support.py:94` `HOOK_SCRIPTS`). The generated settings now name\n      `governance/kernel/hooks/context_watch.py`, which the fixture never copied.\n    - `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked`:\n",
      "tokens": 299
    },
    {
      "id": "4bb96b15a8f4398a317b3697",
      "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md",
      "text": "## Findings (the reviewer's, each with its two lines)\n\n- **F-E1.** After E's line, the repository-root hooks drift comparison (DEC-805, `src/gov/adapters/portability.py:350-359`)\n  reports `HOOKS_MATCHER_DIFFERS` on postToolUse: the root has `['Bash']`, the template `['Bash', 'Bash']`. The cause:\n  `posttooluse.py` was lifted from the root (DEC-971 item 3), and ACT-CONTEXT-WATCH-1 then gave the root a postToolUse of\n  its own. `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` goes from green on the\n  parent to red on the head.\n  Ordinary work: yes, because every unit-suite run and every nightly hits it, with no construction.\n  Consequence: other (a new red test; nothing passes that should not, and no work is lost).\n- **F-E2.** E's Verify says \"`python3 -m gov.adapters.portability` exits 0 on the template\". Inside `template/` it exits 1,\n  before and after, with the same nine findings (`RULESYNC_VERSION_UNKNOWN` and eight `TEMPLATE_COPY_MISSING`). Those\n  findings come from `template/` not being an adopted project. The line adds none there, but the literal clause is not met,\n  and at the root the line adds F-E1.\n",
      "tokens": 292
    },
    {
      "id": "d8e4f48d4acbe9ee080eafca",
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "text": "| `test_w1_38_rulesync.py::TestHandEditDetected::test_hand_edit_skill_file` | 1 | rulesync generate --check exits non-zero after the first generated SKILL.md is overwritten | KPI F2 |\n| `test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` | 1 | Every script path in the generated hook commands is a file of the project | KPI S2 |\n| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_kernel_role_changed_without_its_source` | 1 | Kernel engineer role changed alone: gov check RED/RED, findings name the source and nothing outside the pair | KPI S3; DEC-066, DEC-471 |\n| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_kernel_skill_changed_without_its_source` | 1 | Kernel planning skill changed alone: RED/RED, the source named | KPI S3; DEC-066, DEC-471 |\n| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_role_source_changed_without_its_kernel_role` | 1 | Role source changed and regenerated: RED/RED, the source named, nothing outside the pair | KPI S3; DEC-066, DEC-471 |\n",
      "tokens": 256
    },
    {
      "id": "22d25c91bf36b3b2e37ae70a",
      "path": "tests/acceptance/W1-38/README.md",
      "text": "Cases: 42 in the full run, 159 in `breadth`, 0 in `lifted`.\n\n| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |\n|---|---|---|\n| S1: rulesync 24.0.0 generates CLAUDE.md, AGENTS.md (<= 1.5k tokens) and .claude/ with hooks, deny rules, roles and skills; OpenSpec commands and ve... | `test_w1_38_rulesync.py::TestClaudeMdAndAgentsMd::test_claude_md_is_the_root_rule`, `test_w1_38_rulesync.py::TestClaudeMdAndAgentsMd::test_agents_md_token_limit`, `test_w1_38_rulesync.py::TestOpenSpecSkills::test_generated_skill_is_the_one_openspec_ships` (1 of 6) | designer |\n| S2: Hook-script stubs referenced by generated settings exist; rulesync generate --check is clean in CI | `test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`, `test_w1_38_rulesync.py::TestGenerateCheck::test_check_clean_after_generate` | the ticket's words |\n",
      "tokens": 219
    },
    {
      "id": "DAEO-0z8c",
      "path": ".tickets/DAEO-0z8c.md",
      "text": "# W2-05 The git environment of every check, hook and helper; the settings re-sort\n\n**DEC-971 item 3 (owner, 2026-10-31), package H (a), refined:** DEC-805's comparison of the template's hooks source with this repository's (`src/gov/adapters/portability.py`, the adapter-portability check, inside this ticket's `src/gov/**/*.py`) gets an exception covering **exactly the two hook events ACT 1 lifted** (`postToolUse` and `postToolUseFailure`), **named in the comparison**, and **ending when those events return** (with W2-08). A test designer revises the two cases (`test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`, `test_this_repository_s_two_hooks_sources_agree`) to the exception, lowering nothing else. R3-1 is W2-08's entry criterion (DEC-971 item 3).\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-05), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:**\n  - `src/gov/**/*.py`, limited to calls that start git. The sweep is the ticket's first deliverable and names each file before it is changed.\n",
      "tokens": 296
    },
    {
      "id": "584839ee7ec87387eaae3a62",
      "path": "tests/acceptance/W1-38/README.md",
      "text": "### Success 2 \u2014 Hook-script stubs referenced by generated settings exist; rulesync generate --check is clean in CI\n\n| Test | Measures | Red reason |\n|---|---|---|\n| `TestHookStubs::test_hook_stubs_exist` | every script path in a hook command of `.claude/settings.json` is a file of the project | green |\n| `TestGenerateCheck::test_check_clean_after_generate` | `rulesync generate --check` exits 0 after a fresh generation | green |\n\n",
      "tokens": 109
    },
    {
      "id": "607a9adc9f5b7ee63a9ef747",
      "path": "tests/acceptance/W2-57/README.md",
      "text": "| (b) W1-38's session fixture fails, never skips, on a timeout | `rulesync_bin` skips only when `RULESYNC_BIN` names no file; a rulesync that does not answer `--version` within 60 s fails every case that needs it, naming the timeout; the suite's `generate` waits 180 s (was 30 s), its check wait 180 s (was 60 s), and a timeout in any of them fails, naming it | the revised `tests/acceptance/W1-38/conftest.py` and `w1_38_support.py` (every `needs_rulesync` case of the suite) | shown by a run, not a case of this folder (a nested pytest run would put a 60 s wait into every close): with `RULESYNC_BIN` naming a stand-in whose `--version` answers after 70 s, `TestGenerateCheck::test_check_clean_after_generate` and `TestHookStubs::test_hook_stubs_exist` **errored** \"rulesync at \u2026 gave no answer to --version within 60 s: a timeout, not an absent tool (DEC-892 item 2)\", 0 skipped; with `RULESYNC_BIN` naming no file, skipped \"rulesync is not installed\". The old helper returned None on a timeout and the fixture skipped (I4's RS-any: 181 cases skipped, exit 0) |\n",
      "tokens": 267
    },
    {
      "id": "6b04d7b4c1576b8f453b6c45",
      "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md",
      "text": "## The reviewer's result, in short\n\n- **Point 1, the revert: PASS.** `git diff w2/integrate...HEAD -- template/` is empty. f299a5eb6 removes exactly the 6\n  lines f0cb5284d added. The ticket's own change is 14 files, all in `allowed_paths`, with no `template/` and no\n  `src/gov/**`. The four cases E's line had turned red (`test_program_env` two hooks sources, W2-05 hooks source, W1-38\n  hook stubs, W1-38 any folder) gave `4 passed` on a copy of HEAD.\n- **Point 2, the README: PASS.** The folder alone collects 8 and gives 8 passed. With a skip planted on W2-23 S6, Failure 1\n  goes red (`... carries ['skip']`, `test_w2_182_no_lowering.py:72`); with that row deleted from the README it goes red\n  on `6 >= 7`. A mixed run of W1-32 and the folder collects 53 = 52 + 1. The README's words agree with the ticket and the\n  map.\n\n",
      "tokens": 208
    },
    {
      "id": "243da4170a742521247aa3fb",
      "path": "tests/unit/gitenv/test_program_env.py",
      "text": "def test_this_repository_s_two_hooks_sources_agree():\n    root = Path(__file__).resolve().parents[3]\n    assert portability._hooks_findings(root) == []\n",
      "tokens": 38
    },
    {
      "id": "77e699f0865f719f3356fdae",
      "path": "tests/acceptance/W1-38/test_w1_38_rulesync.py",
      "text": "    def test_hook_stubs_exist(self, generated_project):\n        settings = support.load_settings(generated_project)\n        script_paths = support.extract_hook_script_paths(settings)\n        assert script_paths, (\n            \"no hook script paths found in .claude/settings.json; \"\n            \"hooks were not generated\"\n        )\n        missing = [p for p in script_paths\n                   if not (generated_project / p).is_file()]\n        assert not missing, (\n            f\"hook scripts in .claude/settings.json do not exist: {missing}\"\n        )\n",
      "tokens": 138
    },
    {
      "id": "037ea8a0a0dc861179c0e445",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "  that their base pair differs in two events is returned to the lead as a package (P-W2-05-DRIFT-BASE): green, but\n  `[an event whose matcher differs]` is green through the event `postToolUseFailure` being in the template's source\n  only, not through its matcher. DEC-970 decided it; the drift cases' base pair is now built from one source (see\n  \"P-W2-05-DRIFT-BASE\" below).\n- **`test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` is red, and stays red until the\n  orchestrator's decision (package H).** It compares this repository's two files byte for byte, and since ACT 1 they\n  differ in two events: `HOOKS_EVENT_DIFFERS` for `postToolUse` and `postToolUseFailure`, \"only in\n  template/.rulesync/hooks.jsonc\". That is a decision about the sources, not about the case, and the case is not\n  changed.\n\n| Case | At `f217353e59fa`, before | After |\n|---|---|---|\n| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the order of the hooks of an event]` | **red:** `KeyError: 'postToolUse'`, in the case's construction | **green** |\n",
      "tokens": 278
    },
    {
      "id": "19dbaf41321184a2929c646d",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "| **W2-M281**: adapter-portability goes red on a planted drift in the template's hooks source (`template/.rulesync/hooks.jsonc`, DEC-783 item 3), compared with the repository's by hook events and matchers, paths normalised (DEC-805) | `test_w2_05_hooks_source.py`: `test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event` with `[an event in the template's source only]`, `[an event in the repository's source only]`, `[an event whose matcher differs]`, `[a matcher in the repository's source only]`, `[a matcher in the template's source only]` (their base pair built from one source and checked green before the plant, DEC-970); `test_a_difference_that_is_not_drift_leaves_adapter_portability_green` with `[only the paths]`, `[only the order of the events]`, `[only the order of the hooks of an event]`, `[only the command wrapper]`; `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`; and DEC-971 item 3's exception for the two hook events ACT 1 lifted, 14 cases (see \"DEC-971 item 3\" below) |\n",
      "tokens": 268
    },
    {
      "id": "43e300004ba68670e4a1e50a",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "| `...[a matcher in the repository's source only]` | new | **red:** the same |\n| `...[a matcher in the template's source only]` | new | **red:** the same |\n| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the paths]`, `[only the order of the events]`, `[only the order of the hooks of an event]`, `[only the command wrapper]` | new | **green:** the check compares no hooks source today, so nothing in them can turn it red. These cases hold the comparison to come against an over-strict reading |\n| `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | new | **red, for the missing matcher:** the check is green over the two files (it does not compare them), then `template/.rulesync/hooks.jsonc`'s `sessionStart` matchers are `[None]`, not `[\"compact\\|clear\\|resume\"]`. After the comparison alone it would be red at its first step (a finding for `sessionStart`); after the matcher line alone, at its last (the drift not seen) |\n",
      "tokens": 260
    },
    {
      "id": "4941d022db1ba03722837922",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "| **DEC-971 item 3** (H (a) refined): DEC-805's comparison excepts exactly the two hook events ACT 1 lifted (`postToolUse`, `postToolUseFailure`), named in it, until they return with W2-08 | `test_w2_05_hooks_source.py`: point 1 `test_a_lifted_hook_event_in_the_template_s_source_only_leaves_adapter_portability_green` `[postToolUse]`, `[postToolUseFailure]`, `[both]`; point 2 `test_a_drift_beside_the_lifted_hook_events_still_turns_adapter_portability_red_naming_its_event` \u00d7 4; point 3 `test_a_lifted_hook_event_in_the_repository_s_source_only_still_turns_adapter_portability_red` `[postToolUse]`, `[postToolUseFailure]`, `[both]`; point 4 `test_a_lifted_hook_event_back_in_both_sources_is_compared_as_any_other` \u00d7 4; point 5 (the output form) in each of the 14; and `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` (unchanged). At `d1533bf30a10`: point 1's 3 and the over-this-repository case **red**, the other 10 **green** |\n\nNot written:\n\n- **W2-L109** (findings grouped by cause) and **W2-M231** (the check and the hand-run generator use the same\n  root) state no form these tests could hold them to. They are returned to the lead.\n- **W2-M012** is an owner act.\n",
      "tokens": 300
    },
    {
      "id": "a9d53869fba807fb5aac6a27",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "| `test_w2_05_hooks_source.py::test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event[an event in the template's source only]`, `[an event in the repository's source only]`, `[an event whose matcher differs]`, `[a matcher in the repository's source only]`, `[a matcher in the template's source only]` | green; with nothing planted, `[an event whose matcher differs]` still green and the other four red only at the naming step | green, the control green first; with nothing planted, all five red: \"stayed green\" |\n| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green` (4 cases) | green | green |\n| `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | **red:** two `HOOKS_EVENT_DIFFERS` findings (ACT 1) | **red, the same** (package H) |\n\nW2-05 whole, after the change, in a launched session: 48 cases, 40 passed and 8 failed. Of the 8:\n\n- the hooks-source case above (package H);\n- six that fail for a reason of the session, not their own:\n",
      "tokens": 273
    },
    {
      "id": "bc61f49b78d9c7b6433c03ef",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "| `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the order of the hooks of an event]` | **red:** `KeyError: 'postToolUse'`, in the case's construction | **green** |\n| `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` | **red:** two `HOOKS_EVENT_DIFFERS` findings (ACT 1) | **red, the same** (package H) |\n| the other 8 cases of the file | green | green |\n\n",
      "tokens": 117
    },
    {
      "id": "fbfe9300e41ee20ecffbbd77",
      "path": "tests/acceptance/W2-05/README.md",
      "text": "- **The mutation check, after the change.** With every plant made to do nothing, all five cases pass their control\n  and fail at their last step: \"adapter-portability stayed green on ... it did not see the drift\". Each case is now\n  red only because of its own plant.\n- **Unchanged:** the four not-drift cases, and `test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`.\n  The last is still red (two `HOOKS_EVENT_DIFFERS` findings, ACT 1). That is a decision about the sources, held by\n  the owner (package H), and the case stays as it is.\n\n| Case | At `0cfa8684f720`, before | After |\n|---|---|---|\n| `test_w2_05_hooks_source.py::test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event[an event in the template's source only]`, `[an event in the repository's source only]`, `[an event whose matcher differs]`, `[a matcher in the repository's source only]`, `[a matcher in the template's source only]` | green; with nothing planted, `[an event whose matcher differs]` still green and the other four red only at the naming step | green, the control green first; with nothing planted, all five red: \"stayed green\" |\n",
      "tokens": 297
    },
    {
      "id": "1fcd5a287d981350efe9d374",
      "path": "tests/acceptance/W1-38/README.md",
      "text": "## Covers mapping\n\n| Covers ID | Tests |\n|---|---|\n| CAP-52.a | `TestUnsourcedFile` (skill, command), `TestSettingsHandEdit`, `TestSkillGeneration`, `TestVendoredSkillRegistration`, `TestClaudeMdAndAgentsMd`, `TestOpenSpecCommands`, `TestOpenSpecSkills`, `TestRulesyncVersion`, `TestHookStubs`, `TestGenerateCheck`, `TestDeleteProtection`, `TestHandEditDetected` (CLAUDE.md, AGENTS.md, skill), `TestSourceChangeDetected`, `TestMissingFileDetected::test_missing_agents_md_fails_check` |\n| CAP-52.b | `TestUnsourcedFile` (role), `TestRoleToolsAgainstKernel::test_source_tools_are_the_kernel_role_s`, `TestRoleFieldAgreement`, `TestHandEditDetected::test_hand_edit_role_file` |\n| CAP-38.b | `TestSettingsAfterTheHeldOutStep`, `TestProjectWithoutAHeldOutFile`, `TestBrokenHeldOutFile`, `TestStepRepeated`, `TestHeldOutStepThroughGovCheck` (the round of DEC-635), `TestRoleToolsAgainstKernel` (the two changed-source cases), `TestRegisteredFamilyCheck`, `TestKernelAgainstAdapterSource`, `TestFindings`, `TestMissingFileDetected::test_portability_check_fails_on_missing_agents_md`, `TestToolAbsentOrHanging`, `TestRulesyncVersion::test_gov_check_is_red_when_the_version_cannot_be_read` |\n\n",
      "tokens": 296
    },
    {
      "id": "fafdc6a1060ca48a724b1bba",
      "path": "tests/acceptance/W1-38/test_w1_38_rulesync.py",
      "text": "\n\n# ===================================================================\n# KPI Success 2 \u2014 hook-script stubs exist\n# ===================================================================\n\nclass TestHookStubs:\n    \"\"\"Every command path in generated settings resolves to a file.\"\"\"\n\n    @needs_rulesync\n",
      "tokens": 75
    },
    {
      "id": "ADOPT-A1",
      "path": "governance/adoption/A1-inventory.md",
      "text": "  blob: 183055dd13628d0343030a1e8b8795e1eda404c0\n- path: tests/acceptance/W1-36/test_w1_36_skill_form.py\n  blob: 799a2a480fc673917e037ec664deb4b0bc7e577b\n- path: tests/acceptance/W1-36/w1_36_support.py\n  blob: ccf7f8ce6bbc7a7557f658612019f5d50ebfec9a\n- path: tests/acceptance/W1-37/README.md\n  blob: 0decda6b025b78d064e0a9eb34099cabdb8ef6e4\n- path: tests/acceptance/W1-37/conftest.py\n  blob: 1157a8c0699d2a31bb6e54348290fefb896e4bdb\n- path: tests/acceptance/W1-37/test_w1_37_skills.py\n  blob: 6c3a0e9e8e66898b95d169c39a11bf24b0654cec\n- path: tests/acceptance/W1-37/w1_37_support.py\n  blob: bdfc3c2c353c3d3357e5c040b00aeafda7c3291a\n- path: tests/acceptance/W1-38/README.md\n  blob: 6b89f5e52eb5f42494c0f7a4dd705273854cffdd\n- path: tests/acceptance/W1-38/conftest.py\n  blob: ee182da3280bbba8a78c8c18a6dcd2dad815de8e\n- path: tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py\n  blob: a7dd4d3b2d52eb4f234959bef58e3a90d797deb0\n- path: tests/acceptance/W1-38/test_w1_38_hooks_command_line.py\n  blob: 984867ac76b9296e5ebd861774ddcce79f8c4f76\n- path: tests/acceptance/W1-38/test_w1_38_hooks_source.py\n  blob: 547e66dbffa0540f33e750581f078248f8f246ed\n- path: tests/acceptance/W1-38/test_w1_38_rulesync.py\n",
      "tokens": 300
    },
    {
      "id": "ADOPT-A3",
      "path": "governance/adoption/A3-target-path-map.md",
      "text": "  action: KEEP\n- path: tests/acceptance/W1-36/test_w1_36_skill_form.py\n  action: KEEP\n- path: tests/acceptance/W1-36/w1_36_support.py\n  action: KEEP\n- path: tests/acceptance/W1-37/README.md\n  action: KEEP\n- path: tests/acceptance/W1-37/conftest.py\n  action: KEEP\n- path: tests/acceptance/W1-37/test_w1_37_skills.py\n  action: KEEP\n- path: tests/acceptance/W1-37/w1_37_support.py\n  action: KEEP\n- path: tests/acceptance/W1-38/README.md\n  action: KEEP\n- path: tests/acceptance/W1-38/conftest.py\n  action: KEEP\n- path: tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py\n  action: KEEP\n- path: tests/acceptance/W1-38/test_w1_38_hooks_command_line.py\n  action: KEEP\n- path: tests/acceptance/W1-38/test_w1_38_hooks_source.py\n  action: KEEP\n- path: tests/acceptance/W1-38/test_w1_38_rulesync.py\n  action: KEEP\n- path: tests/acceptance/W1-38/w1_38_hooks_support.py\n  action: KEEP\n- path: tests/acceptance/W1-38/w1_38_support.py\n  action: KEEP\n- path: tests/acceptance/W1-39/README.md\n  action: KEEP\n- path: tests/acceptance/W1-39/conftest.py\n  action: KEEP\n- path: tests/acceptance/W1-39/test_w1_39_copy.py\n  action: KEEP\n- path: tests/acceptance/W1-39/test_w1_39_drift.py\n  action: KEEP\n",
      "tokens": 296
    },
    {
      "id": "4da9d4d7c25af21bb4fe555e",
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "text": "| `test_w1_38_heldout_step.py::TestStepRepeated::test_whole_procedure_repeated_is_still_green` | 1 | generate, step, generate, step: settings byte-identical to the first pass and the check green | DEC-641 |\n| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_a_call_the_guard_refuses_from_the_root_is_refused_in_a_subfolder_too` | 1 | An out-of-scope write is refused by the guard's own answer (exit 0, deny) from root and src/app; file unchanged | DEC-603 |\n| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_a_change_left_out_of_scope_by_a_failed_command_is_reported_and_recorded` | 1 | From src/app, a failed command changing ../../README.md: allowed, failed-call commands exit 0, report and findings name \u2026 | DEC-603, DEC-596, DEC-607 |\n| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked` | 1 | An in-scope write from src/app is allowed, runs, its PostToolUse commands exit 0, no report, no finding | DEC-603 |\n",
      "tokens": 259
    },
    {
      "id": "f98fb96b0a3628f71824678f",
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "text": "| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked` | 1 | An in-scope write from src/app is allowed, runs, its PostToolUse commands exit 0, no report, no finding | DEC-603 |\n| `test_w1_38_hooks_any_folder.py::TestAProjectFolderWithASpace::test_the_registered_command_starts_from_a_subfolder` | 7 | The same from src/app of a project whose folder path holds spaces | DEC-603, DEC-608, DEC-609 |\n| `test_w1_38_hooks_any_folder.py::TestEveryEntryStartsFromAnyFolder::test_the_registered_command_starts_its_program` | 28 | Each generated command, run from root, subfolder, deep subfolder or outside, gives its program's own answer, never an \u2026 | DEC-603, DEC-607, DEC-608 |\n| `test_w1_38_hooks_any_folder.py::test_the_events_started_are_the_events_rulesync_generates_guard_entries_under` | 1 | Generated settings register guard entries under exactly the source's seven events | DEC-603, DEC-607 |\n| `test_w1_38_hooks_any_folder.py::test_the_source_holds_the_seven_entries_the_cases_start` | 1 | template/.rulesync/hooks.jsonc holds entries under exactly the seven events the cases start | DEC-603, DEC-607 |\n",
      "tokens": 293
    },
    {
      "id": "ADOPT-A2",
      "path": "governance/adoption/A2-classification.md",
      "text": "- path: tests/acceptance/W1-36/test_w1_36_audit_skill.py\n  namespace: root-files\n- path: tests/acceptance/W1-36/test_w1_36_check_declarations.py\n  namespace: root-files\n- path: tests/acceptance/W1-36/test_w1_36_check_integration.py\n  namespace: root-files\n- path: tests/acceptance/W1-36/test_w1_36_retrieval_skill.py\n  namespace: root-files\n- path: tests/acceptance/W1-36/test_w1_36_skill_form.py\n  namespace: root-files\n- path: tests/acceptance/W1-36/w1_36_support.py\n  namespace: root-files\n- path: tests/acceptance/W1-37/README.md\n  namespace: root-files\n- path: tests/acceptance/W1-37/conftest.py\n  namespace: root-files\n- path: tests/acceptance/W1-37/test_w1_37_skills.py\n  namespace: root-files\n- path: tests/acceptance/W1-37/w1_37_support.py\n  namespace: root-files\n- path: tests/acceptance/W1-38/README.md\n  namespace: root-files\n- path: tests/acceptance/W1-38/conftest.py\n  namespace: root-files\n- path: tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py\n  namespace: root-files\n- path: tests/acceptance/W1-38/test_w1_38_hooks_command_line.py\n  namespace: root-files\n- path: tests/acceptance/W1-38/test_w1_38_hooks_source.py\n  namespace: root-files\n",
      "tokens": 291
    },
    {
      "id": "7cead89b53cdb7f71aa0522d",
      "path": "tests/acceptance/W1-38/README.md",
      "text": "no refusal, the command then runs, and the check after it ends with 0; for the in-scope call it stays silent and\nnothing is recorded.\n\nChecked before the commit, in temporary projects only (a plug-in outside this tree gave each case's temporary\nproject a copy of the source in the decided form, and gave the cases that read the source as written the same\nobject; nothing under `template/` was touched): with the decided form **all 164 cases of the suite pass**, among\nthem all 19 of `test_w1_38_hooks_command_line.py`, all 40 of `test_w1_38_hooks_any_folder.py` and all 18 of\n`test_w1_38_hooks_source.py`. No existing case of this suite goes red with it.\n\n**Not held by the addition, and why.**\n- A project that holds `gov` only under its own `src`, with none installed for the user (shape B: this\n  repository on a fresh machine), is blocked at every call with the decided form. It fails closed; it is the\n  named residual of DEC-608, and no case is written for it.\n- That `gov` is installed for the user who runs a project's sessions is a precondition (DEC-608), stated in the\n  adoption notes and the exit package, not checked by a case.\n",
      "tokens": 286
    },
    {
      "id": "9ed4a4006471a440341f4fa6",
      "path": "tests/acceptance/W1-38/README.md",
      "text": "## The second run (DEC-603, DEC-607): every hook of the source starts from any folder\n\nTicket `DAEO-7nne` (W1-15, reopened for one short run). Cases in `test_w1_38_hooks_any_folder.py`, helpers in the\nlast part of `w1_38_hooks_support.py`. DEC-603: \"the seven command lines of the template's rulesync hooks source\n(`template/.rulesync/hooks.jsonc`) take the kernel template's form, with `$CLAUDE_PROJECT_DIR` in the path, so\nhooks start from any folder.\" Measured before it by the orchestrator (harness 2.1.288): the harness starts every\nhook in the session's current folder; after one `cd` a hook registered by a relative path cannot start.\n\n",
      "tokens": 161
    },
    {
      "id": "d93fbdb1697cee45aaf0deef",
      "path": "tests/acceptance/W1-38/README.md",
      "text": "# W1-38 Acceptance Tests \u2014 rulesync adapters and .claude ownership\n\nTicket: `DAEO-3ef2` \u00b7 Profile: STANDARD \u00b7 Covers: CAP-52.a, CAP-52.b, CAP-38.b\n\nRun: `env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-38 -q -p no:cacheprovider -rs`\n\n**87 cases in 20 classes.** Round 4 (2026-10-07), run after the engineer's commit `d2c2d6ff` (which had the 67\ncases of round 3b green): **76 green, 11 red, 0 skipped**. Round 4 added 20 cases in three classes\n(`TestUnsourcedFile`, `TestSettingsHandEdit`, `TestRoleToolsAgainstKernel`) and changed no other case. Its red\nreasons are in the section \"Round 4\" below; the \"Red reason\" columns of the older tables are those of round 3 and\n3b, kept as the record of what was red then.\n\n**The round of DEC-596 (2026-10-10, ticket `DAEO-7nne`, W1-15 reopened by DEC-600)** added 18 cases in\n`test_w1_38_hooks_source.py` and changed no other case: **105 cases; 96 green, 9 red, 0 skipped** as run before\nthe engineer's work. See the section \"The round of DEC-596\" below.\n\n**The second run on `DAEO-7nne` (2026-10-10, DEC-603, DEC-607)** added 40 cases in\n`test_w1_38_hooks_any_folder.py` and changed no other case: **145 cases; 114 green, 31 red, 0 skipped** as run\n",
      "tokens": 300
    }
  ],
  "supplementary_query": "Adopted projects get the context watch: the template wires context_watch.py, portability's lift exemption per hook, W1-38's fixture with seven hooks (W2-182's E gap)\nS1: the template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in postToolUse (matcher Bash, timeout 10), in the root `.rulesync/hooks.jsonc`'s form with the adopted path `governance/kernel/hooks/` [DEC-1163 (6) E (a), DEC-1167] Verify: W2-23 S6 (`tests/acceptance/W2-23/test_w2_23_space.py`) passes, the settings' hook lines reaching the seven kernel hooks; a planted eighth hook with no wiring fails it\nS2: portability's hooks comparison exempts the template's `posttooluse.py` entry (DEC-971 item 3's lift, per hook) rather than the whole postToolUse event, so the root's and the template's postToolUse compare on what both carry [DEC-971 item 3, DEC-805, DEC-1167] Verify: `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` and `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` pass with S1's line; unit cases in `tests/unit/adapters/test_w2_185_*.py` for the exemption\nS3: W1-38's adopted-project fixture copies the seven kernel hooks (`w1_38_support.py` HOOK_SCRIPTS), so its generated settings name only scripts it copied [DEC-1167, DEC-1156 (7)] Verify: `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` and `test_w1_38_hooks_any_folder.py`'s ordinary-call case pass with S1's line; the fixture with six hooks fails them\nF1: a hook that really drifts between the root and the template (another matcher or another event than the exempt `posttooluse.py` entry) is still a finding. Verify: a planted extra matcher on the root's postToolUse, and a planted template hook in another event, each give a hooks finding",
  "further_batch": [
    {
      "id": "c8148ef641f4c2964d39695a",
      "path": "tests/acceptance/W2-106/README.md"
    },
    {
      "id": "c50a1dbeb1162cbcdd02dd0c",
      "path": "tests/optin-lifted-breadth.txt"
    },
    {
      "id": "897848e229424c547c09266a",
      "path": "tests/acceptance/W2-05/README.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "f6c2ee261b8a484c5fae1ed6",
          "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md"
        },
        {
          "id": "4bb96b15a8f4398a317b3697",
          "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md"
        },
        {
          "id": "d8e4f48d4acbe9ee080eafca",
          "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
        },
        {
          "id": "22d25c91bf36b3b2e37ae70a",
          "path": "tests/acceptance/W1-38/README.md"
        },
        {
          "id": "DAEO-0z8c",
          "path": ".tickets/DAEO-0z8c.md"
        },
        {
          "id": "584839ee7ec87387eaae3a62",
          "path": "tests/acceptance/W1-38/README.md"
        },
        {
          "id": "607a9adc9f5b7ee63a9ef747",
          "path": "tests/acceptance/W2-57/README.md"
        },
        {
          "id": "6b04d7b4c1576b8f453b6c45",
          "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md"
        },
        {
          "id": "243da4170a742521247aa3fb",
          "path": "tests/unit/gitenv/test_program_env.py"
        },
        {
          "id": "77e699f0865f719f3356fdae",
          "path": "tests/acceptance/W1-38/test_w1_38_rulesync.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "037ea8a0a0dc861179c0e445",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "19dbaf41321184a2929c646d",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "43e300004ba68670e4a1e50a",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "4941d022db1ba03722837922",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "a9d53869fba807fb5aac6a27",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "bc61f49b78d9c7b6433c03ef",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "fbfe9300e41ee20ecffbbd77",
          "path": "tests/acceptance/W2-05/README.md"
        },
        {
          "id": "1fcd5a287d981350efe9d374",
          "path": "tests/acceptance/W1-38/README.md"
        },
        {
          "id": "fafdc6a1060ca48a724b1bba",
          "path": "tests/acceptance/W1-38/test_w1_38_rulesync.py"
        },
        {
          "id": "ADOPT-A1",
          "path": "governance/adoption/A1-inventory.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "ADOPT-A3",
          "path": "governance/adoption/A3-target-path-map.md"
        },
        {
          "id": "4da9d4d7c25af21bb4fe555e",
          "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
        },
        {
          "id": "f98fb96b0a3628f71824678f",
          "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
        },
        {
          "id": "ADOPT-A2",
          "path": "governance/adoption/A2-classification.md"
        },
        {
          "id": "7cead89b53cdb7f71aa0522d",
          "path": "tests/acceptance/W1-38/README.md"
        },
        {
          "id": "9ed4a4006471a440341f4fa6",
          "path": "tests/acceptance/W1-38/README.md"
        },
        {
          "id": "d93fbdb1697cee45aaf0deef",
          "path": "tests/acceptance/W1-38/README.md"
        },
        {
          "id": "c8148ef641f4c2964d39695a",
          "path": "tests/acceptance/W2-106/README.md"
        },
        {
          "id": "c50a1dbeb1162cbcdd02dd0c",
          "path": "tests/optin-lifted-breadth.txt"
        },
        {
          "id": "897848e229424c547c09266a",
          "path": "tests/acceptance/W2-05/README.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "897848e229424c547c09266a",
      "reason": "budget exceeded"
    },
    {
      "id": "c50a1dbeb1162cbcdd02dd0c",
      "reason": "budget exceeded"
    },
    {
      "id": "c8148ef641f4c2964d39695a",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-qyt2): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 11831,
  "budget": {
    "limit": 12000,
    "used": 11831
  },
  "hash": "01358c7901fffac137282eebafe5c38bd6a88dc83252b79c3a5561515b0f66be"
}
