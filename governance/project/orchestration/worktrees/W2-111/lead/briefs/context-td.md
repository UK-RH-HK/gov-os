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
  "supplementary": [
    {
      "id": "45eacaa97e4464672544c2ad",
      "path": "governance/project/orchestration/packages/CAPACITY-1.md",
      "text": "### D2. P-LATENCY-1: the 11 hook-latency cases\n1. **Context:** W1-02's, W1-05's and W2-57's p95-under-100-ms cases; no ticket owns them (not W2-90b).\n2. **What happened:** traced 3 rounds with and without W2-106: red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30; they pass alone.\n3. **Why it matters:** they redden closes and the nightly whatever the change; DEC-968 allows no accepted reds.\n4. **Options:** (a) a fresh test designer revises them to time the hook's own work (its CPU time, or against a quiet reference beside each run), at the same 100 ms, lowering nothing (DEC-906: under the owner's named decision); (b) run them only in the nightly.\n5. **Recommendation:** (a), filed after W2-90b (W1-05's file shared). Under DEC-974 the ticket is itself a P1: this decision is that P1.\n6. **Blocks:** nothing directly; each close names them meanwhile.\n\n",
      "tokens": 219
    },
    {
      "id": "cd1946d017a297faecfd7d3b",
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "text": "- W2-157 (`DAEO-ozyt`, P2, engineer, open \u00b7 after the lift): The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills in\n- W2-171 (`DAEO-k1e2`, P2, engineer, open \u00b7 after the lift): The memory audit's measure: the control, the retrieval figures, the judged reader run, the fault rule, the mis\n**Batch 7**\n- W2-15a (`DAEO-rd0g`, P1, research, open): EXP-003, pass 1: the baseline\n- W2-60a (`DAEO-cv58`, P1, engineer, in progress): The role, its skills and its model and effort loaded at launch; the launch record\n- W2-111 (`DAEO-qvff`, P1, independent-test-designer, open): The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the\n- W2-113 (`DAEO-g29a`, P1, engineer, open): An adopted product's CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestr\n- W2-115 (`DAEO-emq1`, P1, engineer, open): gov close, the smart close: scoped runs only, a close refused only by a red its own change caused, the culprit\n",
      "tokens": 262
    }
  ],
  "supplementary_query": "The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the hook, not the machine's load (P-LATENCY-1)\nEach of the 11 hook-latency cases (W1-02's `test_decision_p95_is_under_100_ms` in its parameters, W1-05's `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57's `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook's own work: the CPU time (user and system) of the hook's process and its children over each call, or the call's wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook's process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]\nUnder load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded), each case's verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded): the 11 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]\nThey still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]\nWhat each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]\nThe 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 11 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.\nA case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.\nA case whose verdict still changes with the machine's load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.",
  "further_batch": [
    {
      "id": "DEC-977",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md"
    },
    {
      "id": "048dfadd052cb433da9ae7e2",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
    },
    {
      "id": "173131775859f5b6d7c3ce8b",
      "path": "governance/project/orchestration/packages/ACT-G14.md"
    },
    {
      "id": "60e1b1719924a4f125a40752",
      "path": "governance/project/orchestration/packages/ACT-G14.md"
    },
    {
      "id": "c8a0f02fc870f14b80da56c7",
      "path": "tests/acceptance/W1-28/README.md"
    },
    {
      "id": "f0c9e31ce3259c2a1a497100",
      "path": "tests/acceptance/W1-28/test_w1_28_fixture_copies.py"
    },
    {
      "id": "1649edcfe3cf19451d5b3711",
      "path": "tests/unit/hooks/test_live_hook.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "45eacaa97e4464672544c2ad",
          "path": "governance/project/orchestration/packages/CAPACITY-1.md"
        },
        {
          "id": "cd1946d017a297faecfd7d3b",
          "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md"
        },
        {
          "id": "DEC-977",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "048dfadd052cb433da9ae7e2",
          "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
        },
        {
          "id": "173131775859f5b6d7c3ce8b",
          "path": "governance/project/orchestration/packages/ACT-G14.md"
        },
        {
          "id": "60e1b1719924a4f125a40752",
          "path": "governance/project/orchestration/packages/ACT-G14.md"
        },
        {
          "id": "c8a0f02fc870f14b80da56c7",
          "path": "tests/acceptance/W1-28/README.md"
        },
        {
          "id": "f0c9e31ce3259c2a1a497100",
          "path": "tests/acceptance/W1-28/test_w1_28_fixture_copies.py"
        },
        {
          "id": "1649edcfe3cf19451d5b3711",
          "path": "tests/unit/hooks/test_live_hook.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "048dfadd052cb433da9ae7e2",
      "reason": "budget exceeded"
    },
    {
      "id": "1649edcfe3cf19451d5b3711",
      "reason": "budget exceeded"
    },
    {
      "id": "173131775859f5b6d7c3ce8b",
      "reason": "budget exceeded"
    },
    {
      "id": "60e1b1719924a4f125a40752",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-977",
      "reason": "budget exceeded"
    },
    {
      "id": "WAVE-2-WBS",
      "reason": "budget exceeded"
    },
    {
      "id": "c8a0f02fc870f14b80da56c7",
      "reason": "budget exceeded"
    },
    {
      "id": "f0c9e31ce3259c2a1a497100",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 5837,
  "budget": {
    "limit": 6000,
    "used": 5837
  },
  "left_out": {
    "count": 2,
    "superseded": [
      "DEC-045",
      "DEC-875"
    ],
    "done": []
  },
  "hash": "253aee49aeccd3131cdcb320f36d44052399ad7630c4d161bc3d24701dad7823"
}
