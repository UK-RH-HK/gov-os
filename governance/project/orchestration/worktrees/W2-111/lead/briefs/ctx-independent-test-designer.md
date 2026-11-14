{
  "ticket": "DAEO-qvff",
  "ticket_text": "---\nid: DAEO-qvff\nstatus: in_progress\ndeps: [DAEO-nqa2]\nlinks: []\ncreated: 2026-10-31T21:53:25Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-111\ntags: [wave-2, test-revision, guard, full, capacity]\nwbs_id: W2-111\ntitle: 'The hook-latency cases time the hook''s own work: W1-02''s, W1-05''s and W2-57''s p95-under-100-ms cases judge the hook, not the machine''s load (P-LATENCY-1)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-nqa2\nallowed_paths:\n- tests/acceptance/W1-02/test_w1_02_guard_hook.py\n- tests/acceptance/W1-02/README.md\n- tests/acceptance/W1-05/test_w1_05_live_hooks.py\n- tests/acceptance/W1-05/README.md\n- tests/acceptance/W2-57/test_w2_57_designer_read_p95.py\n- tests/acceptance/W2-57/README.md\n- tests/acceptance/W2-111/**\n- src/gov/guard/install.py\n- src/gov/guard/reads.py\n- tests/unit/guard/test_w2_111*\n- docs/probes/DAEO-qvff/**\nkpis:\n  success:\n  - 'Each of the 15 hook-latency cases (11 in DEC-979''s count; 15 node ids with their parameters, the CTO, DEC-1157 (12)) (W1-02''s `test_decision_p95_is_under_100_ms` in its parameters, W1-05''s `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57''s `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook''s own work: the CPU time (user and system) of the hook''s process and its children over each call, or the call''s wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook''s process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]'\n  - 'Under load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded), each case''s verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded): the 15 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]'\n  - 'They still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]'\n  - 'What each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]'\n  - 'A Bash call is decided within the 100 ms bound at p95 by the hook''s own work (the CPU time of the hook''s process and its children, W2-111''s method), for a plain command, a pipe and a redirect, with a role set Verify: the new Bash cases under `tests/acceptance/W2-111/` run against the product hook pass at the bound, quiet and at a load of about 20; before the change they fail (the measure of 2026-11-14 gave 103-167 ms; evidence `~/gov-os-runs/W2-111/q-scan-2/`). [DEC-1184 (3)]'\n  - 'A call is decided within the bound with 150 or more worktrees registered Verify: a case that registers 150 or more planted worktrees on a planted repository and times Read, Write and Bash calls with a role set: p95 within 100 ms of the hook''s own work. [DEC-1184 (3)]'\n  - 'The install check reads PATH once per session, not on every call; a changed PATH is read again Verify: a unit case counts PATH lookups over 20 calls of one session (one lookup), then changes PATH (one more); `has_install`''s answers are the same as before for the same commands. [DEC-1184 (3)]'\n  - 'A call is judged only against the trees its target lies in, and every decision is the same as before Verify: the guard''s rule suites pass unchanged, and the same corpus of calls (W2-42a''s parser corpus and the five rules'' cases) gives the same allow or refuse decision before and after, with the per-tree judge called only for trees holding the call''s targets. [DEC-1184 (3)]'\n  failure:\n  - 'The 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 15 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.'\n  - 'A case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.'\n  - 'A case whose verdict still changes with the machine''s load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.'\n  - 'A decision changed by the speed-up: a refusal turned into an allow, or an allow into a refusal. Verify: the decision corpus run before and after: no decision differs.'\n  - 'A Bash or many-tree case that still passes a hook doing 150 ms of its own work. Verify: the planted 150 ms hook against each new case: none passes.'\nprofile: FULL\nsources:\n- DEC-979\n- DEC-906\n- DEC-968\n- DEC-958\n- DEC-1184\n- DEC-1182\n- DEC-1157\nest_loc: 320\nacceptance_tests:\n  path: tests/acceptance/W2-111/  # the reopen's cases (DEC-1184 (3)); the earlier revision was judged on its revised suites (DEC-892): with W1-05's test_w1_05_live_hooks.py and W2-57's test_w2_57_designer_read_p95.py (the CTO, DEC-1157 (12), 2026-11-13)\n  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suites and the planted slow hook (DEC-892)\ntrack: B\nlist_rows: []\n---\n# W2-111 The hook-latency cases time the hook's own work\n\nThe owner's D2 (a) on CAPACITY-1 (DEC-979, P-LATENCY-1): a fresh independent test designer revises the 11 hook-latency cases so they judge the hook, not the machine's load, at the same 100 ms, lowering nothing (DEC-906: the owner's named decision).\n\n- **Why:** on 2026-10-31 the 11 cases were red under load whatever the change: traced 3 rounds with and without W2-106, red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30, with run times of 34 to 152 s; they pass alone on a quiet machine. They refused a batch of four (15:19) and redden the nightly. DEC-968 allows no accepted reds.\n- **After W2-90b** (`DAEO-nqa2`): it holds `tests/acceptance/W1-05/test_w1_05_live_hooks.py` too.\n- **Not here:** the hook itself (a slow hook is a product ticket); the five-rule guard's decisions.\n\n**D9-FATES (DEC-1083, DEC-1084):** Stays open as a LITE test revision outside K9 (DEC-1084 (1)). Its 7 lines are not met: `6008a41f` touches only the READMEs of W1-02, W1-05 and W2-57, and there is no `tests/acceptance/W2-111/`, no `Rewrite-Reason: DEC-979` and no CPU-time or load code (audit 1).\n\n**Reopened 2026-11-14 by the owner (DEC-1184 (3), Q-SCAN-2 (a)), within the 100 ms bound's purpose.** The measure of 2026-11-14 (W2-111's method; `~/gov-os-runs/W2-111/q-scan-2/`): the 15 cases pass (87-97 ms best round, load 13-20), but a Bash call takes 103-167 ms, and every call grows with the worktree count (about 59 ms to list 248 trees, 47 ms for the per-tree judge, 52 ms for the Bash install check). The owner's decision changes the \"Not here: the hook itself\" line above for these two costs only. Order: an independent test designer writes the Bash and many-tree cases under `tests/acceptance/W2-111/` (proven red before the change on a planted repository); an engineer caches the install check's PATH lookup per session (`src/gov/guard/install.py`) and judges a call only against its targets' trees (`src/gov/guard/reads.py`); an independent review (FULL: the guard, fails-open risk); the kernel gate and the owner's approval of the kernel bytes at the land. The live hook (`.claude/hooks/pretooluse.py`, a control path) takes the same change by the planned live-hook ACT, with the owner's yes.\n\n**Interface at claim (the CTO, DEC-1157 (3)):** `has_install(command)` keeps its signature and answers; the PATH lookup is cached in the process for the session (keyed by the PATH value). `_trees(root)` keeps its return form; the caller passes the call's target paths so that only trees holding a target are judged; a target that lies in no tree is judged as today. The new cases time the product guard's hook the way W1-02's and W1-05's cases run and measure it (W1-02's budget and method); the live hook's figures are measured in the live-hook ACT's rehearsal, not here.\n",
  "authority": [
    {
      "id": "DEC-979",
      "sha256": "a967a059989b08e0da632b6ac66e56855ac8baa6b962c3337f95abac04dbd8d5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a967a059989b08e0da632b6ac66e56855ac8baa6b962c3337f95abac04dbd8d5",
      "reason": "declared in sources",
      "tokens": 1153
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
      "id": "DEC-1184",
      "sha256": "e7b329b425f25f997350442fac7ae1f83594fa180c14e5667f0ba774207e6395",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e7b329b425f25f997350442fac7ae1f83594fa180c14e5667f0ba774207e6395",
      "reason": "declared in sources",
      "tokens": 7145
    },
    {
      "id": "DEC-1182",
      "sha256": "372519a2935de9d7cb00f7f50467f51d3f3be170b0a46d74c64981b9eee2e90e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "372519a2935de9d7cb00f7f50467f51d3f3be170b0a46d74c64981b9eee2e90e",
      "reason": "declared in sources",
      "tokens": 1206
    },
    {
      "id": "DEC-1157",
      "sha256": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "reason": "declared in sources",
      "tokens": 1274
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
      "sha256": "a967a059989b08e0da632b6ac66e56855ac8baa6b962c3337f95abac04dbd8d5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a967a059989b08e0da632b6ac66e56855ac8baa6b962c3337f95abac04dbd8d5",
      "reason": "declared in sources",
      "tokens": 1153
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
      "id": "DEC-1184",
      "sha256": "e7b329b425f25f997350442fac7ae1f83594fa180c14e5667f0ba774207e6395",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e7b329b425f25f997350442fac7ae1f83594fa180c14e5667f0ba774207e6395",
      "reason": "declared in sources",
      "tokens": 7145
    },
    {
      "id": "DEC-1182",
      "sha256": "372519a2935de9d7cb00f7f50467f51d3f3be170b0a46d74c64981b9eee2e90e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "372519a2935de9d7cb00f7f50467f51d3f3be170b0a46d74c64981b9eee2e90e",
      "reason": "declared in sources",
      "tokens": 1206
    },
    {
      "id": "DEC-1157",
      "sha256": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "reason": "declared in sources",
      "tokens": 1274
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
    },
    {
      "id": "2de7735178c00867b3f394fa",
      "path": "tests/acceptance/W2-57/README.md",
      "text": "## W2-111: the hook-latency case(s) judge the hook's own work against a reference hook timed beside them (DAEO-qvff; `Rewrite-Reason: DEC-979`)\n\n`Rewrite-Reason: DEC-979` (the owner's D2 (a) on CAPACITY-1, P-LATENCY-1; DEC-906, DEC-968). Revised twice by fresh\nindependent test designers (round 1 and round 2, 2026-11-13); the case ids, their parameters, the 100 ms bound at p95,\nthe 3 warm-up calls, the 40 samples, the nearest-rank p95 and the three-round repeat are the same as before the\nrevision; nothing is skipped, marked or removed.\n\n**What it measures.** `test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95` (one case): the CPU time of the hook and its children for a test designer's read on a branch with 120 changed files (the git that finds the files the branch changes, Policy 2 (c): `HookResult.cpu_seconds`), less the median CPU time of a reference hook called just before each of the 40 timed reads, in the same round. The bound is 100 ms at p95. The measure is the owner's decision DEC-1163 (3) (P-W2-111-MEASURE-1 (a)).\n\n",
      "tokens": 277
    },
    {
      "id": "9dad605f7b4e5675c5bf074d",
      "path": "tests/acceptance/W1-02/README.md",
      "text": "## W2-111: the hook-latency case(s) judge the hook's own work against a reference hook timed beside them (DAEO-qvff; `Rewrite-Reason: DEC-979`)\n\n`Rewrite-Reason: DEC-979` (the owner's D2 (a) on CAPACITY-1, P-LATENCY-1; DEC-906, DEC-968). Revised twice by fresh\nindependent test designers (round 1 and round 2, 2026-11-13); the case ids, their parameters, the 100 ms bound at p95,\nthe 3 warm-up calls, the 40 samples, the nearest-rank p95 and the three-round repeat are the same as before the\nrevision; nothing is skipped, marked or removed.\n\n**What it measures.** `test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` (5 parameters: `no-role-deny`, `engineer-allow-from-ticket-frontmatter`, `engineer-deny-outside-the-ticket`, `test-designer-allow`, `frozen-deny`): the CPU time of the guard's hook process and its children over one write decision (`HookResult.cpu_seconds`, filled by `run_hook_raw`: the `RUSAGE_CHILDREN` difference before and after the one synchronous call), less the median CPU time of a reference hook called just before each of the 40 timed calls, in the same round. The bound is 100 ms at p95. The measure is the owner's decision DEC-1163 (3) (P-W2-111-MEASURE-1 (a)).\n",
      "tokens": 300
    },
    {
      "id": "ed81553eafcdeb627c302b5b",
      "path": "tests/acceptance/W1-05/README.md",
      "text": "## W2-111: the hook-latency case(s) judge the hook's own work against a reference hook timed beside them (DAEO-qvff; `Rewrite-Reason: DEC-979`)\n\n`Rewrite-Reason: DEC-979` (the owner's D2 (a) on CAPACITY-1, P-LATENCY-1; DEC-906, DEC-968). Revised twice by fresh\nindependent test designers (round 1 and round 2, 2026-11-13); the case ids, their parameters, the 100 ms bound at p95,\nthe 3 warm-up calls, the 40 samples, the nearest-rank p95 and the three-round repeat are the same as before the\nrevision; nothing is skipped, marked or removed.\n\n",
      "tokens": 136
    },
    {
      "id": "DEC-977",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  2. **W2-108 goes back** (merged `789513df`, not closed) for a fresh independent test designer to put that one test's copy into DEC-385's form, lowering nothing (`Rewrite-Reason: DEC-385`); then W1-28's and W1-50's files and W2-108's own suite alone, and the merge. It is first in the lead queue after W2-107's close (memory's critical chain: W2-108, then W2-13).\n  3. **W2-106, W2-84, W2-76, W2-49 and W2-16** caused none of the reds; they re-close in the next batch with W2-67 and W2-95, right after W2-107's own close (DEC-975), and W2-108 joins a close once its fix is merged.\n  4. **Not this batch's (DEC-968, dealt with at once):** W1-05's two and W1-46's one install cases, W2-59's four hook-line cases and W1-33's four cases are W2-90b's; W1-35's two files pass alone (flaky candidates); the hook-latency cases pass alone (P-LATENCY-1, to the owner in CAPACITY-1).\n- **Where it goes (DEC-851):** this register; W2-108's resume brief; the close records of the five; the daily document.\n\n| Version | Date | Change |\n|---|---|---|\n",
      "tokens": 260
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-90c | A | **New (DEC-999, the owner's split of W2-90b).** The cases of W2-90b that need W2-105 or W2-110: W2-90's seven named reds and any case W2-90b names (`DAEO-fu3n`). | test-revision | independent-test-designer | LITE | W2-90b, W2-105, W2-110 | 60 | DEC-999, DEC-965, DEC-966 |\n| W2-111 | A | **New (DEC-979 item 1 D2, P-LATENCY-1).** The 11 hook-latency cases (W1-02, W1-05, W2-57, p95 under 100 ms) time the hook's own work, not the machine's load, at the same bound, lowering nothing (`DAEO-qvff`) | test-revision | independent-test-designer | LITE | W2-90b | 120 | DEC-979, DEC-906, DEC-968 |\n| W2-112 | A | **New (DEC-982, P-RERANKER-1 (a)).** One reranker serves every session: a shared, on-demand service on a local socket; each search falls back to a private reranker, else an unranked order marked `rerank: unavailable` (`DAEO-clon`) | implementation | engineer | FULL | W2-32 | 200 | DEC-982, DEC-979, DEC-374 |\n",
      "tokens": 233
    },
    {
      "id": "048dfadd052cb433da9ae7e2",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "text": "| 8 | **Verification wrong because of its environment: reds caused by load or flakiness, the wrong baseline, the machinery judging itself** (MAST FM-3.3; S24: pass^k reliability falls sharply over repeated runs) | S1, S24 | **Yes.** The 11 hook-latency cases fail under load and pass when quiet; they refused a batch (a 3.5 h redo) (`PKG/CAPACITY-1.md:46`). 17 of 24 close refusals came from the machinery itself (`PKG/AUDIT-GOV-FEATURES-1.md:8-13`). W2-81's runner READY self-test fails one seed in seven (REG:12507). | DEC-968: a close is refused only by a failure its own change caused. DEC-988 and DEC-989: a known baseline from the nightly. Re-runs alone, 3+3 interleaved. Heavy-job slots. P-LATENCY-1 is due after W2-90b. | The timing tests still run in scoped sets under load. No ticket states a repeat-pass (pass^k) requirement for tests that judge closes. | **KPI W2-115:** \"a test that refuses a close has passed k = 3 consecutive runs on the baseline; one that has not is quarantined and named, never a refusal\". Timing cases go to the nightly only (P-LATENCY-1 as planned). |\n\n",
      "tokens": 273
    },
    {
      "id": "47efaeb6a72d735ba1387df7",
      "path": "tests/acceptance/W1-02/test_w1_02_guard_hook.py",
      "text": "def test_decision_p95_is_under_100_ms(project, write, name):\n    \"\"\"The hook's own work, p95 under 100 ms: its CPU time over each call, less a reference hook timed beside it.\n\n    Rewrite-Reason: DEC-979 (W2-111, P-LATENCY-1; DEC-906). The case measured the wall time of the hook process;\n    under load a wall clock times the scheduler's queue, not the hook (2026-10-31: red 8, 0, 1 of the 11 latency\n    cases with W2-106 and 0, 0, 5 without, at loads of 15 to 30; green alone on a quiet machine). A CPU time alone\n    was not the measure either (round 1, 2026-11-13: it rises about 1.4 times when every CPU is busy, because a\n    busy sibling thread slows the same work; 3 of the 15 cases were red at load 20 and at 50). Each call is now\n    judged by the CPU time of the hook and of every process it waited for (``result.cpu_seconds``, from\n    ``RUSAGE_CHILDREN``), less the CPU time of a reference hook (a trivial hook: a fresh interpreter that reads the\n    event and answers) called just before it, in the same round and the same CPU share. The round's figure is the\n    nearest-rank p95 of the 40 calls' CPU times less the median of the 40 reference calls' CPU times. It leaves out\n",
      "tokens": 298
    },
    {
      "id": "341b51abdc893ab49c11b963",
      "path": "tests/acceptance/W1-05/test_w1_05_live_hooks.py",
      "text": "def test_a_call_waits_under_100_ms_p95_for_the_hook(kernel_live, kernel_switched_over, kernel_sandbox, name):\n    \"\"\"W1-02's budget, \"decision in < 100 ms p95\", through the wiring, for the read-only tools as well.\n\n    Rewrite-Reason: DEC-979 (W2-111, P-LATENCY-1; DEC-906). The case timed the wall clock of the call; under load a\n    wall clock times the scheduler's queue, not the hook (2026-10-31: red 8, 0, 1 of the 11 latency cases with W2-106\n    and 0, 0, 5 without, at loads of 15 to 30; green alone on a quiet machine). A CPU time alone was not the measure\n    either (round 1, 2026-11-13: it rises about 1.4 times when every CPU is busy, because a busy sibling thread slows\n    the same work; 3 of the 15 cases were red at load 20 and at 50). Each call is now judged by its CPU time: the\n    difference of ``RUSAGE_CHILDREN`` (user and system) before and after one call, which waits for every PreToolUse\n    command registered for the tool and what each waited for, so it is the sum of their work (stricter than the wall\n    time of commands that run side by side, never looser); less the CPU time of a reference hook (a trivial hook: a\n",
      "tokens": 287
    },
    {
      "id": "a5f14150be7e2fa7ed0d67f4",
      "path": "governance/project/orchestration/closes/W2-106-DAEO-0mtg.md",
      "text": "- Reds caused by the change: none; flaky candidates: tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_clean_store_is_decided_green, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check, tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here, tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched, tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer], tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95\n",
      "tokens": 433
    },
    {
      "id": "1ac6fe613cb99c8f4ad46be2",
      "path": "governance/project/orchestration/closes/W2-108-DAEO-zoex.md",
      "text": "- Reds caused by the change: none; flaky candidates: tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_clean_store_is_decided_green, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check, tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here, tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched, tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer], tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95\n",
      "tokens": 433
    },
    {
      "id": "d19be29c8745fe261090a9d5",
      "path": "governance/project/orchestration/closes/W2-16-DAEO-49o5.md",
      "text": "- Reds caused by the change: none; flaky candidates: tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_clean_store_is_decided_green, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check, tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here, tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched, tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer], tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95\n",
      "tokens": 433
    }
  ],
  "supplementary_query": "The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the hook, not the machine's load (P-LATENCY-1)\nEach of the 15 hook-latency cases (11 in DEC-979's count; 15 node ids with their parameters, the CTO, DEC-1157 (12)) (W1-02's `test_decision_p95_is_under_100_ms` in its parameters, W1-05's `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57's `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook's own work: the CPU time (user and system) of the hook's process and its children over each call, or the call's wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook's process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]\nUnder load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded), each case's verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded): the 15 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]\nThey still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]\nWhat each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]\nA Bash call is decided within the 100 ms bound at p95 by the hook's own work (the CPU time of the hook's process and its children, W2-111's method), for a plain command, a pipe and a redirect, with a role set Verify: the new Bash cases under `tests/acceptance/W2-111/` run against the product hook pass at the bound, quiet and at a load of about 20; before the change they fail (the measure of 2026-11-14 gave 103-167 ms; evidence `~/gov-os-runs/W2-111/q-scan-2/`). [DEC-1184 (3)]\nA call is decided within the bound with 150 or more worktrees registered Verify: a case that registers 150 or more planted worktrees on a planted repository and times Read, Write and Bash calls with a role set: p95 within 100 ms of the hook's own work. [DEC-1184 (3)]\nThe install check reads PATH once per session, not on every call; a changed PATH is read again Verify: a unit case counts PATH lookups over 20 calls of one session (one lookup), then changes PATH (one more); `has_install`'s answers are the same as before for the same commands. [DEC-1184 (3)]\nA call is judged only against the trees its target lies in, and every decision is the same as before Verify: the guard's rule suites pass unchanged, and the same corpus of calls (W2-42a's parser corpus and the five rules' cases) gives the same allow or refuse decision before and after, with the per-tree judge called only for trees holding the call's targets. [DEC-1184 (3)]\nThe 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 15 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.\nA case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.\nA case whose verdict still changes with the machine's load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.\nA decision changed by the speed-up: a refusal turned into an allow, or an allow into a refusal. Verify: the decision corpus run before and after: no decision differs.\nA Bash or many-tree case that still passes a hook doing 150 ms of its own work. Verify: the planted 150 ms hook against each new case: none passes.",
  "further_batch": [
    {
      "id": "1129e803d25e1e7e645c0f1b",
      "path": "governance/project/orchestration/closes/W2-49-DAEO-ha8z.md"
    },
    {
      "id": "67e8b68792add67700151f81",
      "path": "governance/project/orchestration/closes/W2-67-DAEO-9nys.md"
    },
    {
      "id": "dcba5b618746edffd644189c",
      "path": "governance/project/orchestration/closes/W2-76-DAEO-tgk2.md"
    },
    {
      "id": "a9e493ebd2b6e5feaf5f6c9f",
      "path": "governance/project/orchestration/closes/W2-84-DAEO-m1u3.md"
    },
    {
      "id": "65b54f504c13ddf5a1d6b67e",
      "path": "governance/project/orchestration/closes/W2-95-DAEO-57hm.md"
    },
    {
      "id": "09a7cb65bd434cb760d28db7",
      "path": "tests/acceptance/W2-57/README.md"
    },
    {
      "id": "a5c4f12fb567d95b325c99ee",
      "path": "tests/acceptance/W2-57/test_w2_57_designer_read_p95.py"
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
          "id": "2de7735178c00867b3f394fa",
          "path": "tests/acceptance/W2-57/README.md"
        },
        {
          "id": "9dad605f7b4e5675c5bf074d",
          "path": "tests/acceptance/W1-02/README.md"
        },
        {
          "id": "ed81553eafcdeb627c302b5b",
          "path": "tests/acceptance/W1-05/README.md"
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
          "id": "47efaeb6a72d735ba1387df7",
          "path": "tests/acceptance/W1-02/test_w1_02_guard_hook.py"
        },
        {
          "id": "341b51abdc893ab49c11b963",
          "path": "tests/acceptance/W1-05/test_w1_05_live_hooks.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "a5f14150be7e2fa7ed0d67f4",
          "path": "governance/project/orchestration/closes/W2-106-DAEO-0mtg.md"
        },
        {
          "id": "1ac6fe613cb99c8f4ad46be2",
          "path": "governance/project/orchestration/closes/W2-108-DAEO-zoex.md"
        },
        {
          "id": "d19be29c8745fe261090a9d5",
          "path": "governance/project/orchestration/closes/W2-16-DAEO-49o5.md"
        },
        {
          "id": "1129e803d25e1e7e645c0f1b",
          "path": "governance/project/orchestration/closes/W2-49-DAEO-ha8z.md"
        },
        {
          "id": "67e8b68792add67700151f81",
          "path": "governance/project/orchestration/closes/W2-67-DAEO-9nys.md"
        },
        {
          "id": "dcba5b618746edffd644189c",
          "path": "governance/project/orchestration/closes/W2-76-DAEO-tgk2.md"
        },
        {
          "id": "a9e493ebd2b6e5feaf5f6c9f",
          "path": "governance/project/orchestration/closes/W2-84-DAEO-m1u3.md"
        },
        {
          "id": "65b54f504c13ddf5a1d6b67e",
          "path": "governance/project/orchestration/closes/W2-95-DAEO-57hm.md"
        },
        {
          "id": "09a7cb65bd434cb760d28db7",
          "path": "tests/acceptance/W2-57/README.md"
        },
        {
          "id": "a5c4f12fb567d95b325c99ee",
          "path": "tests/acceptance/W2-57/test_w2_57_designer_read_p95.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "09a7cb65bd434cb760d28db7",
      "reason": "budget exceeded"
    },
    {
      "id": "1129e803d25e1e7e645c0f1b",
      "reason": "budget exceeded"
    },
    {
      "id": "65b54f504c13ddf5a1d6b67e",
      "reason": "budget exceeded"
    },
    {
      "id": "67e8b68792add67700151f81",
      "reason": "budget exceeded"
    },
    {
      "id": "a5c4f12fb567d95b325c99ee",
      "reason": "budget exceeded"
    },
    {
      "id": "a9e493ebd2b6e5feaf5f6c9f",
      "reason": "budget exceeded"
    },
    {
      "id": "dcba5b618746edffd644189c",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-qvff): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 19832,
  "budget": {
    "limit": 20000,
    "used": 19832
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
  "hash": "5529f7ae0352d9e00db6609becb540629f15c0ebc4778b47dcdf5e04863acfaf"
}
