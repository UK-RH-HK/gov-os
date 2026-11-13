{
  "ticket": "DAEO-qvff",
  "ticket_text": "---\nid: DAEO-qvff\nstatus: in_progress\ndeps: [DAEO-nqa2]\nlinks: []\ncreated: 2026-10-31T21:53:25Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W2-111\ntags: [wave-2, test-revision, guard, lite, capacity]\nwbs_id: W2-111\ntitle: 'The hook-latency cases time the hook''s own work: W1-02''s, W1-05''s and W2-57''s p95-under-100-ms cases judge the hook, not the machine''s load (P-LATENCY-1)'\nclass: test-revision\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\ndepends_on:\n- DAEO-nqa2\nallowed_paths:\n- tests/acceptance/W1-02/test_w1_02_guard_hook.py\n- tests/acceptance/W1-02/README.md\n- tests/acceptance/W1-05/test_w1_05_live_hooks.py\n- tests/acceptance/W1-05/README.md\n- tests/acceptance/W2-57/test_w2_57_designer_read_p95.py\n- tests/acceptance/W2-57/README.md\nkpis:\n  success:\n  - 'Each of the 11 hook-latency cases (W1-02''s `test_decision_p95_is_under_100_ms` in its parameters, W1-05''s `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57''s `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook''s own work: the CPU time (user and system) of the hook''s process and its children over each call, or the call''s wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook''s process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]'\n  - 'Under load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded), each case''s verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded): the 11 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]'\n  - 'They still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]'\n  - 'What each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]'\n  failure:\n  - 'The 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 11 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.'\n  - 'A case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.'\n  - 'A case whose verdict still changes with the machine''s load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.'\nprofile: LITE\nsources:\n- DEC-979\n- DEC-906\n- DEC-968\n- DEC-958\nest_loc: 120\nacceptance_tests:\n  path: tests/acceptance/W2-111/\n  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suites and the planted slow hook (DEC-892)\ntrack: B\nlist_rows: []\n---\n# W2-111 The hook-latency cases time the hook's own work\n\nThe owner's D2 (a) on CAPACITY-1 (DEC-979, P-LATENCY-1): a fresh independent test designer revises the 11 hook-latency cases so they judge the hook, not the machine's load, at the same 100 ms, lowering nothing (DEC-906: the owner's named decision).\n\n- **Why:** on 2026-10-31 the 11 cases were red under load whatever the change: traced 3 rounds with and without W2-106, red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30, with run times of 34 to 152 s; they pass alone on a quiet machine. They refused a batch of four (15:19) and redden the nightly. DEC-968 allows no accepted reds.\n- **After W2-90b** (`DAEO-nqa2`): it holds `tests/acceptance/W1-05/test_w1_05_live_hooks.py` too.\n- **Not here:** the hook itself (a slow hook is a product ticket); the five-rule guard's decisions.\n\n**D9-FATES (DEC-1083, DEC-1084):** Stays open as a LITE test revision outside K9 (DEC-1084 (1)). Its 7 lines are not met: `6008a41f` touches only the READMEs of W1-02, W1-05 and W2-57, and there is no `tests/acceptance/W2-111/`, no `Rewrite-Reason: DEC-979` and no CPU-time or load code (audit 1).\n",
  "authority": [
    {
      "id": "DEC-979",
      "sha256": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "reason": "declared in sources",
      "tokens": 1123
    },
    {
      "id": "DEC-906",
      "sha256": "8a6c3222edc6be70c1ab302e119cb8306ef9e20fca42bf0971819da7c6f323cb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "8a6c3222edc6be70c1ab302e119cb8306ef9e20fca42bf0971819da7c6f323cb",
      "reason": "declared in sources",
      "tokens": 970
    },
    {
      "id": "DEC-968",
      "sha256": "c985a186c50b5746a7d6f6efdd8aa382514c301118e5ddbb0db88d0f236371b7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c985a186c50b5746a7d6f6efdd8aa382514c301118e5ddbb0db88d0f236371b7",
      "reason": "declared in sources",
      "tokens": 897
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DAEO-nqa2",
      "sha256": "16afd58897731fd8894908fbcde9f1d3fbc1561b19bc22911361b28a431b7c06",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "16afd58897731fd8894908fbcde9f1d3fbc1561b19bc22911361b28a431b7c06",
      "reason": "declared in sources",
      "tokens": 432
    }
  ],
  "mandatory": [
    {
      "id": "DEC-979",
      "sha256": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "reason": "declared in sources",
      "tokens": 1123
    },
    {
      "id": "DEC-906",
      "sha256": "8a6c3222edc6be70c1ab302e119cb8306ef9e20fca42bf0971819da7c6f323cb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "8a6c3222edc6be70c1ab302e119cb8306ef9e20fca42bf0971819da7c6f323cb",
      "reason": "declared in sources",
      "tokens": 970
    },
    {
      "id": "DEC-968",
      "sha256": "c985a186c50b5746a7d6f6efdd8aa382514c301118e5ddbb0db88d0f236371b7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c985a186c50b5746a7d6f6efdd8aa382514c301118e5ddbb0db88d0f236371b7",
      "reason": "declared in sources",
      "tokens": 897
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DAEO-nqa2",
      "sha256": "16afd58897731fd8894908fbcde9f1d3fbc1561b19bc22911361b28a431b7c06",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "16afd58897731fd8894908fbcde9f1d3fbc1561b19bc22911361b28a431b7c06",
      "reason": "declared in sources",
      "tokens": 432
    }
  ],
  "supplementary": [],
  "supplementary_query": "The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the hook, not the machine's load (P-LATENCY-1)\nEach of the 11 hook-latency cases (W1-02's `test_decision_p95_is_under_100_ms` in its parameters, W1-05's `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57's `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook's own work: the CPU time (user and system) of the hook's process and its children over each call, or the call's wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook's process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]\nUnder load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded), each case's verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded): the 11 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]\nThey still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]\nWhat each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]\nThe 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 11 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.\nA case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.\nA case whose verdict still changes with the machine's load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 5356,
  "budget": {
    "limit": 6000,
    "used": 5356
  },
  "hash": "d2fde12c44800b09f57daf03a8ff80f5979906fe443e3bd836d136062de93fcc"
}
