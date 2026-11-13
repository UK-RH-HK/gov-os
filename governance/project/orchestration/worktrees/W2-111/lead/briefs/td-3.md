# Brief: independent test designer, W2-111 (ticket DAEO-qvff), run 3 (one README edit)

You are a fresh independent test designer (MR-3). One ticket: DAEO-qvff (W2-111), profile LITE, class C1, a test revision under the owner's named decision (DEC-979 item 1 D2 (a), P-LATENCY-1; DEC-906). Headless: only your last message is read.

## Objective (narrow: README text only)
Round 2 (commit `a5bf1c0131b8` on `w2/W2-111-tests`) revised the 15 hook-latency cases to "form B": the round's CPU p95 of the hook and its children, minus the median CPU time of a stub reference hook timed beside each call, at the same 100 ms. Each of the three READMEs already says that this leaves out about 15-21 ms of start-up cost ("**This lowers what is judged by that much**").

The owner has since decided this: **DEC-1163 (3)** (ACCEPTED, 2026-11-13): "P-W2-111-MEASURE-1 (a): W2-111's cases judge the round's CPU p95 of the hook and its children minus the median CPU of a stub hook timed beside each call, at the same 100 ms (form B, a5bf1c0131b8); the start-up cost left out (~16-21 ms) is accepted under DEC-906." Read it in /home/usain/gov-os-worktrees/W2-111-tests/docs/DECISION_REGISTER.md (grep `DEC-1163`).

Your one task: in each of the three READMEs' W2-111 sections, add the decision's id **DEC-1163 (3)** where the README names the measure and where it says the start-up cost is left out. A short clause is enough, for example at the end of the "**What it measures.**" paragraph: "The measure is the owner's decision DEC-1163 (3) (P-W2-111-MEASURE-1 (a))." and after "**This lowers what is judged by that much**": "(accepted by the owner under DEC-906: DEC-1163 (3))". Choose the exact words; keep them short and factual.

**Change nothing else.** No test file is edited. No figure, no other section, no other wording changes. Your diff must be only those added words in the three READMEs.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-111-tests |
| branch | w2/W2-111-tests (at a5bf1c013; commit here; never merge, never push) |
| the three files you edit | tests/acceptance/W1-02/README.md (section at about line 2692), tests/acceptance/W1-05/README.md (about line 245), tests/acceptance/W2-57/README.md (about line 328) |
| allowed paths (the ticket's) | tests/acceptance/W1-02/test_w1_02_guard_hook.py, tests/acceptance/W1-02/README.md, tests/acceptance/W1-05/test_w1_05_live_hooks.py, tests/acceptance/W1-05/README.md, tests/acceptance/W2-57/test_w2_57_designer_read_p95.py, tests/acceptance/W2-57/README.md |
| ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qvff.md |

Edit with the Edit tool and absolute paths.

## Verify (put the output in your return)
1. `git -C /home/usain/gov-os-worktrees/W2-111-tests diff --stat` names only the three READMEs.
2. `git -C /home/usain/gov-os-worktrees/W2-111-tests diff` shows only added words (no removed or changed figures). Lines that you re-wrapped are fine if the only change is the added words.
3. `grep -n 'DEC-1163' tests/acceptance/W1-02/README.md tests/acceptance/W1-05/README.md tests/acceptance/W2-57/README.md` finds the id in each.
No pytest is needed for this edit (no test file changes). If you choose to run one anyway, it goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with a TMPDIR outside the repository and outside ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Commit (your paths only, on w2/W2-111-tests)
```
git -C /home/usain/gov-os-worktrees/W2-111-tests commit -m "W2-111: the READMEs name the owner's decision on the measure, DEC-1163 (3)" --trailer "Task: DAEO-qvff" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-979, DEC-906, DEC-968" --trailer "Rewrite-Reason: DEC-979" -- tests/acceptance/W1-02/README.md tests/acceptance/W1-05/README.md tests/acceptance/W2-57/README.md
```
Every trailer as shown. `Task:` is DAEO-qvff, never W2-111. DEC-1163 is not in the ticket's `sources:`, so it is not in `Implements:`; name it in your return's `discoveries`. Never `Role: owner` or `Decided-by:`.

## Rules
- Reads are open (the whole repository, history). Refused: secrets and keys; the held-out qualification material's contents; the hidden half of any evaluation set; never open the evaluation sets' root or any hidden or memory-verdict folder.
- No `gov retrieve`, no `gov context` (you are in the sandbox): search with the Read and Grep tools, and search again once in other words if the first does not answer.
- No merge, no push, no install. Write only the three READMEs.
- **A refusal is reported, never worked around** (DEC-1142 (9)). If the guard, the sandbox or a hook refuses an action, do not try the same thing in another form (no `cat` for a refused `cp`, no Bash write for a refused Write or Edit). Refused twice for the same action: stop and say so in your return. Run 2's designer worked around two refusals; that is not allowed.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
task: / status: (DONE or BLOCKED) / work_completed: / files_changed: / evidence: (the diff stat, the grep, the added words per file) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: `commits: <hash12> <subject> | trailers` per commit, and `guard_refusals: none | - <time> | <command form> | <the reason given> | true or false-positive`.

## Context bundle (gov context DAEO-qvff --role independent-test-designer, for reference)
```json
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
```
