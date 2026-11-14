{
  "ticket": "DAEO-5y8d",
  "ticket_text": "---\nid: DAEO-5y8d\nwbs_id: W2-182\nexternal-ref: W2-182\ntitle: The nightly's drift reds of 2026-11-13 fixed by test revision (W1-32's command list, W1-18 and W2-123's rebuild answer, W2-121 S1's race, W2-136 S10, W2-23 S6)\ntype: task\nclass: implementation\nrole: independent-test-designer\nprofile: LITE\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-13\ndeps: []\nallowed_paths:\n- tests/acceptance/W1-32/test_w1_32_command_set.py\n- tests/acceptance/W1-32/README.md\n- tests/acceptance/W1-18/test_w1_18_on_demand_start.py\n- tests/acceptance/W1-18/README.md\n- tests/acceptance/W2-123/test_w2_123_retry.py\n- tests/acceptance/W2-123/README.md\n- tests/acceptance/W2-121/test_s1_lock_off_status.py\n- tests/acceptance/W2-121/README.md\n- tests/acceptance/W2-136/test_w2_136_never_a_gate.py\n- tests/acceptance/W2-136/README.md\n- tests/acceptance/W2-23/test_w2_23_space.py\n- tests/acceptance/W2-23/README.md\n- tests/acceptance/W2-128/test_w2_128_rows.py  # row 8: the 'until W2-56' line deleted (DEC-1163 (1)), widened by the CTO (DEC-1157 (12))\n- tests/acceptance/W2-128/README.md\n- docs/probes/DAEO-5y8d/**  # the probe record\n- tests/acceptance/W2-182/**  # the revision's own folder: its README maps the revised case ids so gov accept W2-182 runs them (DEC-892; the W2-90 form); CTO, DEC-1157 (12)\n- template/.rulesync/hooks.jsonc  # E (a): the template's hooks source gains context_watch.py (a product-spec worker's line, not a test designer's)\nreads:\n- .gov-runtime/scratch/orchestrator/drafts/nightly-20261113-analysis.md\n- src/gov/check/commands.py\n- src/gov/rebuild/**\n- src/gov/session_watch/items.py\n- .rulesync/hooks.jsonc\n- template/governance/kernel/hooks/**\nneeds: []\nwaits_on: []\nkpis:\n  success:\n  - 'B: W1-32''s recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail'\n  - 'C: W1-18''s and W2-123''s cases expect REBUILD_FAILED where a rebuild''s asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try''s record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)'\n  - 'R: W2-121 S1 takes its second snapshot only after the fake launched job''s .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job''s late write [DEC-1163 (6)] Verify: the case passes 20 runs in a row under the nightly''s load (beside a busy loop of 20 workers); it still fails when a stand-in status writes a file'\n  - 'D: W2-136 S10''s scan allows `src/gov/session_watch` to call gov plan (W2-159''s S5: session-watch reads the dispatcher''s ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105] Verify: the case passes on w2/integrate; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it'\n  - 'E: the template''s hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` as the root `.rulesync/hooks.jsonc` does (ACT-CONTEXT-WATCH-1), and W2-23 S6 expects the seven kernel hooks [DEC-1163 (6) E (a)] Verify: W2-23 S6 passes on w2/integrate; a planted eighth hook script with no wiring fails it; `python3 -m gov.adapters.portability` exits 0 on the template'\n  - 'F: W2-128''s row 8 records that the line \"Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56\" is gone from both kernel templates (W2-56 closed; the owner''s DEC-1163 (1), b88a76172), so W2-128 and W2-152 S10 (which runs gov accept W2-128) are green [DEC-1163 (1), DEC-1156 (7)] Verify: tests/acceptance/W2-128/test_w2_128_rows.py passes on w2/integrate; the row-8 case fails when the line is planted back into template/governance/kernel/templates/role-lead.md'\n  failure:\n  - 'A revised case that no longer catches what it guards, or any case lowered, skipped or marked. Verify: each revised case fails on a planted break of what it guards (the S lines above); `git diff` adds no skip, xfail or flaky mark'\nnon_goals:\n- no product code changes (src/gov/**); the behaviours these cases record were decided and landed by W2-45, W2-121, W2-23, W2-159, W2-160, W2-124 and W2-176\n- 'not the 2 timing cases that pass alone under the nightly beside the leads (W2-112, W2-145 S4): environment, DEC-1159 (1)'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1163, DEC-1156, DEC-1150, DEC-1159, DEC-105, DEC-781]\nacceptance_tests: {path: tests/acceptance/W2-182/}\n---\n\n# W2-182 The nightly's drift reds of 2026-11-13\n\nThe owner's DEC-1163 (6), route (a): one small gap ticket for the five red-alone cases of the nightly of 2026-11-13 that\nare not the Node 18 PATH (fixed by 8f68e0c7c). Each records a behaviour the owner already decided and that has landed;\nevery ticket that broke them is closed. Analysis: `.gov-runtime/scratch/orchestrator/drafts/nightly-20261113-analysis.md`.\n\n- **B** (W1-32): `dispatch` (W2-121, merge 787b097ac), `adapters` (W2-23), `session-watch` (W2-159), `wait` (W2-160).\n- **C** (W1-18, W2-123): W2-124's \"a rebuild without its asked-for semantic store fails named\" (799b2b65f, merge a2f28ccf3).\n- **R** (W2-121 S1): a race in the test under load (passes alone).\n- **D** (W2-136 S10 against W2-159 S5): the owner's (a).\n- **E** (W2-23 S6): W2-176's 7th kernel hook (context_watch.py, hand merge 3430341c4) never reached `template/.rulesync/hooks.jsonc`; the owner's (a).\n\nA test designer revises the cases (`Rewrite-Reason: DEC-1163 (6)`); a product-spec worker adds the template's hook line; a narrow independent check; the land.\n",
  "authority": [
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
      "id": "DEC-1156",
      "sha256": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "reason": "declared in sources",
      "tokens": 1044
    },
    {
      "id": "DEC-1150",
      "sha256": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DEC-1159",
      "sha256": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "reason": "declared in sources",
      "tokens": 515
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-781",
      "sha256": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "reason": "declared in sources",
      "tokens": 446
    }
  ],
  "mandatory": [
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
      "id": "DEC-1156",
      "sha256": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "reason": "declared in sources",
      "tokens": 1044
    },
    {
      "id": "DEC-1150",
      "sha256": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DEC-1159",
      "sha256": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "reason": "declared in sources",
      "tokens": 515
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-781",
      "sha256": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "reason": "declared in sources",
      "tokens": 446
    }
  ],
  "supplementary": [
    {
      "id": "23a8e3a105e5bfdfc88def4c",
      "path": "tests/acceptance/W2-182/README.md",
      "text": "| Success 4 (D) | `tests/acceptance/W2-136/test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan` | W2-136 S10 allows `src/gov/session_watch` to call gov plan | a module outside `plan/`, `launch/` and `session_watch/` calling gov plan |\n| Success 5 (E) | `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` | W2-23 S6 expects the seven kernel hooks | a planted eighth hook script with no wiring |\n| Success 6 (F) | `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-lead]`, `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-cto]` | W2-128 row 8 records that the `until W2-56` line is gone from both kernel templates | the line planted back into `template/governance/kernel/templates/role-lead.md` (and the role-cto template) |\n",
      "tokens": 251
    },
    {
      "id": "8fe665132f0d17d8e6e32a00",
      "path": "governance/project/orchestration/closes/W2-88a-DAEO-pg6i.md",
      "text": "- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py\n- Traced against: 36fc597ca74fe6b6e51ad56ff3b70f8a94dcf5cf (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))\n- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition[], tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition, tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead], tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto]\n- Acceptance tests' authors (G-1, DEC-1050): 1 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner\n- Core changed (scoped, not full, DEC-968): none; unplaced: none\n- Review: not required (STANDARD)\n",
      "tokens": 297
    }
  ],
  "supplementary_query": "The nightly's drift reds of 2026-11-13 fixed by test revision (W1-32's command list, W1-18 and W2-123's rebuild answer, W2-121 S1's race, W2-136 S10, W2-23 S6)\nB: W1-32's recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail\nC: W1-18's and W2-123's cases expect REBUILD_FAILED where a rebuild's asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try's record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)\nR: W2-121 S1 takes its second snapshot only after the fake launched job's .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job's late write [DEC-1163 (6)] Verify: the case passes 20 runs in a row under the nightly's load (beside a busy loop of 20 workers); it still fails when a stand-in status writes a file\nD: W2-136 S10's scan allows `src/gov/session_watch` to call gov plan (W2-159's S5: session-watch reads the dispatcher's ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105] Verify: the case passes on w2/integrate; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it\nE: the template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` as the root `.rulesync/hooks.jsonc` does (ACT-CONTEXT-WATCH-1), and W2-23 S6 expects the seven kernel hooks [DEC-1163 (6) E (a)] Verify: W2-23 S6 passes on w2/integrate; a planted eighth hook script with no wiring fails it; `python3 -m gov.adapters.portability` exits 0 on the template\nF: W2-128's row 8 records that the line \"Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56\" is gone from both kernel templates (W2-56 closed; the owner's DEC-1163 (1), b88a76172), so W2-128 and W2-152 S10 (which runs gov accept W2-128) are green [DEC-1163 (1), DEC-1156 (7)] Verify: tests/acceptance/W2-128/test_w2_128_rows.py passes on w2/integrate; the row-8 case fails when the line is planted back into template/governance/kernel/templates/role-lead.md\nA revised case that no longer catches what it guards, or any case lowered, skipped or marked. Verify: each revised case fails on a planted break of what it guards (the S lines above); `git diff` adds no skip, xfail or flaky mark",
  "further_batch": [
    {
      "id": "34e2c5379f09063659e4b3e4",
      "path": "tests/acceptance/W2-128/README.md"
    },
    {
      "id": "90720c1df3de752c27f0a8f1",
      "path": "tests/acceptance/W2-128/README.md"
    },
    {
      "id": "a4690016d8b2e013712b506a",
      "path": "tests/acceptance/W2-128/README.md"
    },
    {
      "id": "bf89a1e2b7a2277a7776919c",
      "path": "tests/acceptance/W2-128/README.md"
    },
    {
      "id": "2302dafddaf32ad11357e7cd",
      "path": "tests/acceptance/W2-182/README.md"
    },
    {
      "id": "3e9245b2d9bfc2663b2c72e2",
      "path": "governance/project/orchestration/reviews/D10-commands-review.md"
    },
    {
      "id": "60b5e3ffbc5335f387e22a50",
      "path": "tests/acceptance/W1-32/README.md"
    },
    {
      "id": "4e4a6b7e2829be65a40ddd40",
      "path": "governance/project/orchestration/closes/W2-176-DAEO-ktiw.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "23a8e3a105e5bfdfc88def4c",
          "path": "tests/acceptance/W2-182/README.md"
        },
        {
          "id": "8fe665132f0d17d8e6e32a00",
          "path": "governance/project/orchestration/closes/W2-88a-DAEO-pg6i.md"
        },
        {
          "id": "34e2c5379f09063659e4b3e4",
          "path": "tests/acceptance/W2-128/README.md"
        },
        {
          "id": "90720c1df3de752c27f0a8f1",
          "path": "tests/acceptance/W2-128/README.md"
        },
        {
          "id": "a4690016d8b2e013712b506a",
          "path": "tests/acceptance/W2-128/README.md"
        },
        {
          "id": "bf89a1e2b7a2277a7776919c",
          "path": "tests/acceptance/W2-128/README.md"
        },
        {
          "id": "2302dafddaf32ad11357e7cd",
          "path": "tests/acceptance/W2-182/README.md"
        },
        {
          "id": "3e9245b2d9bfc2663b2c72e2",
          "path": "governance/project/orchestration/reviews/D10-commands-review.md"
        },
        {
          "id": "60b5e3ffbc5335f387e22a50",
          "path": "tests/acceptance/W1-32/README.md"
        },
        {
          "id": "4e4a6b7e2829be65a40ddd40",
          "path": "governance/project/orchestration/closes/W2-176-DAEO-ktiw.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "2302dafddaf32ad11357e7cd",
      "reason": "budget exceeded"
    },
    {
      "id": "34e2c5379f09063659e4b3e4",
      "reason": "budget exceeded"
    },
    {
      "id": "3e9245b2d9bfc2663b2c72e2",
      "reason": "budget exceeded"
    },
    {
      "id": "4e4a6b7e2829be65a40ddd40",
      "reason": "budget exceeded"
    },
    {
      "id": "60b5e3ffbc5335f387e22a50",
      "reason": "budget exceeded"
    },
    {
      "id": "90720c1df3de752c27f0a8f1",
      "reason": "budget exceeded"
    },
    {
      "id": "a4690016d8b2e013712b506a",
      "reason": "budget exceeded"
    },
    {
      "id": "bf89a1e2b7a2277a7776919c",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 5725,
  "budget": {
    "limit": 6000,
    "used": 5725
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-045",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "264e8c28f8989f8b376f807c04ee4ff4b33ed396db045aa60be392aae7ce54c1"
}
