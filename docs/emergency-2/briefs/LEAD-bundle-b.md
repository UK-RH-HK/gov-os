# Lead brief: bundle-b, the three held branches that conflict (W2-207 runtime, eval-roots, kit-head) merged onto batch A for release 0.1.8

You are a lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies** (read your bundle whole, never cut a `gov retrieve` result, list your retrieves, one trailer
paragraph with no blank line before `Co-Authored-By`, never open a sets root). Decide, never ask (I-10). Use `systematic-debugging`.

## Why
The owner (2026-11-25, after EXAMIN's fresh 80 failed at 86.8 %): the 0.1.8 bundle with D3 comes next. The CTO split it: batch A
(`e2/d1-verdict`, `e2/escalation-slice`, `e2/d3-stale-route`, `e2/usage-per-repo`, `e2/models-by-role`) merges with no conflict
and is branch `e2/bundle-a`. The other three conflict with batch A and with each other; you merge them onto `e2/bundle-a`, so
0.1.8 can carry all eight. Measured by the CTO (`git merge-tree`):
- `e2/w2-207-runtime` (it contains `e2/w2-207-pre-retire`; merge only `runtime`) x `e2/usage-per-repo`: `.tickets/DAEO-rt4s.md`,
  `tests/acceptance/W2-207/README.md`, `tests/acceptance/W2-207/conftest.py`.
- `e2/eval-roots` x `e2/models-by-role`: `src/gov/adapters/merge.py`, `template/.rulesync/hooks.jsonc`,
  `tests/acceptance/W1-38/w1_38_support.py`, `tests/acceptance/W2-17/test_w2_17_fix_hook_once.py`,
  `tests/acceptance/W2-23/test_w2_23_space.py`, `tests/unit/hooks/test_w2_106_template_hook_lines.py`;
  x `e2/usage-per-repo`: `src/gov/adopt/fabric.py`, `tests/acceptance/W2-88/test_w2_88_p1_shipped_bytes.py`,
  `tests/unit/adopt/test_w2_88_shipped.py`; x `e2/d3-stale-route`: `src/gov/doctor/command.py`.
- `e2/kit-head` x `e2/eval-roots`, `e2/models-by-role`, `e2/w2-207-runtime`: `.rulesync/permissions.jsonc`; x `e2/models-by-role`
  also `.tickets/DAEO-kt8e.md`, `tests/acceptance/W2-208/README.md`. **KH-3 against the interim deny lines** (`e8e277a74`, the two
  sets roots, DEC-1249 (2)): the interim deny lines **stay** in the merged `.rulesync/permissions.jsonc` and in the settings it
  generates; they go only after eval-roots' two root moves, which wait for each repository CTO's yes (not yours).

## What
Branch `e2/bundle-b` from `e2/bundle-a`, worktree `/home/usain/gov-os-worktrees/E2-bundle-b`. Merge, in this order,
`e2/w2-207-runtime`, `e2/eval-roots`, `e2/kit-head`, each with `git merge --no-ff`. For each conflict:
- **Code, configuration, tickets, `tests/unit/`:** keep both sides' intent (each branch's KPI lines must still hold); the engineer
  helper decides the resolution and says why in its notes.
- **Anything under `tests/acceptance/` (DEC-253; I-12, I-15):** the merge whose resolution touches `tests/acceptance/` is made by the
  independent test designer helper and carries `Role: independent-test-designer` **alone** (the landing's check,
  `src/gov/queue/checks.py:test_authors`, reads a two-parent merge by its `--remerge-diff` and refuses any other role). Where the same
  merge also has code conflicts, the engineer writes those resolved files first and the test designer commits them unchanged in the
  merge, its message saying `Code resolution: engineer (<files>)`. The engineer never edits `tests/acceptance/`.
- A test that cannot hold both branches' KPI lines at once: the test designer says which line wins and why, citing the decision.

## Where
Your worktree only. Code areas: the conflicted files above and what a resolution needs; nothing else. Others work meanwhile in
`src/gov/release/`, `src/gov/memaudit/brief.py`, `src/gov/memaudit/writercheck.py` and `tests/acceptance/serial-only.txt`: do not
edit those. Never merge into `w2/integrate`; the CTO lands `e2/bundle-b`.

## Green
1. `gov accept` for W2-207, W2-204 and W2-208 (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main accept <W> --root <worktree>`).
2. Exactly the impact-selected suites for the three merges, as one list: from the worktree, `PYTHONPATH=<worktree>/src python3 -m
   gov.cli.main queue DAEO-rt4s=e2/w2-207-runtime DAEO-ma4q=e2/eval-roots DAEO-3ef2=e2/kit-head --onto e2/bundle-a --select`
   (SEL-4: one list for the merged tree; if it refuses a pair `CANDIDATE_NOT_ISOLATED`, that is the conflict you resolved: instead
   select for `e2/bundle-b` itself against `e2/bundle-a`, and say which you used). Run exactly that list through the heavy slot,
   never a hand-picked set (DEC-1244 X-1).
3. Check by code: every merge's `git log -1 --remerge-diff --format= --name-only <merge> -- tests/acceptance` is empty or the merge's
   only `Role` is `independent-test-designer`; every non-merge commit touching `tests/acceptance/` is the test designer's.
A red that is the merge's: fix it (the same failure three times: stop, find the root cause, say it, Q-7). A red that is red on
`e2/bundle-a` too: note it, don't fix it. A case that passes alone but fails in the run (W2-112, W2-13, W1-19, W2-184): note it as
I-30/I-32, don't re-run it a second time.

## Return
Branch and head; each conflict and its resolution (file, which side, why); the selected run's summary and its list's count; the
remerge check's output; reds not yours; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: c1e81afd3e75 (/home/usain/Dynamic-Agentic-Engineering-OS), store behind HEAD, head 117c532de04f, 14 stale path(s)
{
  "store": {
    "commit": "c1e81afd3e7560e7a8f769bb51de083b07d72158",
    "head": "117c532de04f3dbe524fc82a30f32bb8458c2888",
    "stale": [
      ".claude/agents/orchestrator.md",
      ".claude/templates/role-cto.md",
      ".rulesync/subagents/orchestrator.md",
      "docs/DECISION_REGISTER.md",
      "docs/checkpoints/DAEO-sdxk/CP-DAEO-sdxk-3337.md",
      "docs/emergency-2/CTO-HANDOVER.md",
      "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "docs/emergency-2/briefs/PRODUCT-CTO-HANDOVER-METHOD.md",
      "docs/emergency-2/integration/FINDINGS.md",
      "governance/project/orchestration/tools/start_cto.sh",
      "src/gov/_shipped/template/governance/kernel/templates/role-cto.md",
      "template/.rulesync/subagents/orchestrator.md",
      "template/governance/kernel/roles/orchestrator.md",
      "template/governance/kernel/templates/role-cto.md"
    ],
    "root": "/home/usain/Dynamic-Agentic-Engineering-OS"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-rt4s",
      "sha256": "e374a76a3bdd3d11606581f8a63d5f9d581409b8ae19e33277bd8bec0d1a6d69",
      "path": ".tickets/DAEO-rt4s.md",
      "start_line": 1,
      "end_line": 51,
      "text": "---\nid: DAEO-rt4s\nstatus: open\ndeps: [DAEO-rt3s]\nlinks: [DAEO-5rgj, DAEO-rt2s, DAEO-rt3s]\ncreated: 2026-11-19T03:40:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-207\ntags: [dispatch, run-time-tool, cut-over, emergency-2]\nwbs_id: W2-207\ntitle: \"The run-time tool, slice 4: the cut-over: the cron line moves to the product's pass, the product slot replaces the scratch heavy_slot.sh, RT-5's relaunch and D8's spend brake switched on, ready work started from `gov plan --ready` through `gov launch` (RT-1 across tickets), the CTO's dispatcher and the scratch watchers retired (RT-7)\"\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: [DAEO-rt3s]\nwaits_on: []\ncloses:\n- CAP-23.b\n- CAP-64.a\nallowed_paths:\n- src/gov/dispatch/**\n- src/gov/resources/**\n- src/gov/launch/launcher.py\n- template/governance/kernel/hooks/stop.py\n- governance/project/orchestration/tools/**\n- .claude/settings.json\n- tests/unit/dispatch/test_w2_tbd*\n- tests/unit/resources/**\nest_loc: 500\nkpis:\n  success:\n  - 'RT-1 Ready work starts itself: the pass takes the ready tickets from `gov plan --ready`, and for each with a free admission starts its lead through `gov launch` with a `ready_at` record; a ticket whose lead is running, or whose start is held by the gate, the spend brake or a claim, is not started twice. Verify: a fixture project with three ready tickets and a limit of two leads: two leads start (a stub CLI) within one pass each, the third waits and starts when one ends; the log holds `ready_at` and `started_at` per ticket and `gov dispatch waits` reports each ready-to-start gap. [EMERGENCY-2 6.3 RT-1; audit 3 D2, D9; W2-205 non-goal]'\n  - 'RT-5 The relaunch is on: the config key `relaunch` of `~/.gov-os/runtime/config.json` is true in the shipped default, the leads the cut-over starts are started by `gov launch` (so they are in the registry with a session id), and a lead that dies is resumed once at its checkpoint''s next step. Verify: W2-205''s relaunch cases with the default config. [audit 3 D5; CTO ruling 4 of slice 3]'\n  - 'D8 The spend brake is called from the pass: a ticket past twice its projection has its next launch held and gets one message to its launcher. Verify: a planted launch record past 2x its projection: the pass starts nothing for the ticket and sends one wake message. [audit 3 D8; W2-156]'\n  - 'RT-3, RT-7 The product slot replaces the scratch `heavy_slot.sh`: `heavy_slot.sh` in the repository becomes a one-line call of `gov resources slot` (or the product''s `gov.resources.slots.run`), its sizes come from the detected machine (`heavy_slots` in the gate file only when the owner pins one), and `heavy_slots.conf` and the `REFERENCE` fallback are gone; one cron line runs the pass; `ps` shows one watcher process. Verify: the slot run through the wrapper on two simulated profiles gives different slot and worker counts; no `SLOTS=` or `WORKERS=` constant remains; the crontab lists one run-time line.'\n  - 'RT-6 The retirements of audit 3 are done: the CTO''s dispatcher (`dispatcher.py`, `balancer.py`, `run_tick.sh`, `launch_now.sh`, `loop.sh`) after its items are ported, the two dead-man copies, the sentinel check, `waiter_guard.sh`, `stop_idle_check.py`, `stop_waiter_check.py`, the jobs queue, `usage_watch.sh` and the `gate_check` comparison line; this repository''s own `.claude/settings.json` registers the template''s one Stop hook (W2-205) in their place. Verify: a grep of the tree and of the settings for each retired name finds nothing outside history; a Stop at the end of a turn with an unread wake message blocks once (W2-205).'\n  failure:\n  - 'F1 The cut-over loses nothing: the stall check and the CTO-stall push (DEC-1214 T1, T2; DEC-1216 (5)) run in the pass before the dispatcher''s cron line is removed, the unread items of the old inbox are carried into the per-session inbox, and the old line is removed only after one pass of the new one has run. Verify: a planted silent CTO transcript: one stall message and one push from the new pass; the old inbox''s unread items are in `cto`''s inbox after the cut-over step.'\nnon_goals:\n- 'Anything the owner decides: the 99 % plan push and the decision pushes stay the CTO''s own'\n- 'A new design: audit 3 and EMERGENCY-2 6.3 are the design'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [EMERGENCY-2 6.3, A-5, docs/emergency-2/audits/03-run-time-tool.md, DEC-1214, DEC-1216, DAEO-rt3s]\nacceptance_tests:\n  path: tests/acceptance/W2-207/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n",
      "chunk_id": "812e4b8dc74302df99b2fdc1",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-rt4s",
      "sha256": "61c1723b1eb620f0cf0cd652e4a97c8e28f6b038402e5d6051bd69e8907591f5",
      "path": ".tickets/DAEO-rt4s.md",
      "start_line": 52,
      "end_line": 62,
      "text": "# W2-207: the run-time tool, slice 4: the cut-over\n\nWritten 2026-11-19 by the slice 3 lead at the end of W2-205 (the night's brief: \"if time remains, write slice 4's ticket and stop\"). Not built, `wbs_id` is `W2-207` until the CTO gives the next free W2 number; the test paths are renumbered then.\n\n**What is already there.** Slices 1 to 3 built the product's pieces and left everything live untouched: `gov msg` and the watch pass (slice 1), the load admission, the runtime log and the product slot (slice 2), the end events, the Stop check, the relaunch (off by default) and the per-address messages (slice 3, W2-205). This slice switches the live machine over, in the order F1 requires, and is the owner's/CTO's cut-over: nothing here is run by a worker without the CTO's go.\n\n**Order of the cut-over (for the CTO).** (1) Port what the dispatcher does that the pass does not (the CTO-stall push, inbox items as `gov msg send`, the ready-list start) and run both for one day. (2) Register the template's Stop hook in `.claude/settings.json`, retire `stop_idle_check.py` and `stop_waiter_check.py`. (3) Replace the scratch `heavy_slot.sh` by the product slot. (4) Replace the cron line; remove the old one after one clean pass. (5) The retirements. (6) Turn `relaunch` on.\n\n**Largest part and a split option.** RT-1 across tickets (the first KPI line) is the biggest item (the rest of audit 3 D2 and D9); if it runs long, split it into its own ticket ahead of the cut-over, which then carries RT-3, RT-5, RT-6, RT-7, D8 and F1.\n\n**Open questions for the owner (one line each).** (a) When the cut-over runs (recommended: a day, not a night, so that the CTO watches the first passes). (b) Whether `relaunch` ships on (recommended: yes after one day of the new pass).\n",
      "chunk_id": "9a163f632af2e8bc525a6ca3",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "4ceb0c262b03fbad718d2a7b",
      "sha256": "6ce94970d093ec4b275facedcf6021951292615a67919e1f37cab33f3c4195eb",
      "path": "docs/emergency-2/briefs/LEAD-d1-land.md",
      "start_line": 8,
      "end_line": 12,
      "text": "## What\n1. Bring `e2/d1-verdict` up to `w2/integrate` so that **no merge commit changes anything under `tests/acceptance/`** and every acceptance change is a commit by the independent test designer (`Role: independent-test-designer`). Choose the order that achieves it (for example: the test designer first commits, on the branch, the W2-81 README and test as they must read once W2-210 is built, taking `w2/integrate`'s other changes to those two files; then the merge resolves with no acceptance content of its own). Read `tests/acceptance/W1-01/test_w1_01_integration_merges.py` for the exact rule before you choose.\n2. The test designer owns every edit under `tests/acceptance/` (W2-81 and W2-210); the engineer touches none (DEC-1243 (2)).\n3. Check `tests/acceptance/W1-35/` alone on the merged branch: in the CTO's one-process run of the selection it failed to import (`cannot import name 'CHECKS_DIR' from 'conftest'` resolving to `tests/unit/dispatch/conftest.py`). Say whether it is red on `w2/integrate` too when run alone and when run with `tests/unit/dispatch/`, and if it is a clash of two `conftest` modules in one run, name it as a finding (do not fix it here).\n\n",
      "chunk_id": "4ceb0c262b03fbad718d2a7b",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "34c73b385b1ddd9684e0fa91",
      "sha256": "840916db325e38b4404456df9a3ea8e9a3f73067a594d0afd59dcd3fbe7caeaf",
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "start_line": 132,
      "end_line": 132,
      "text": "- **Merges.** Every merge anyone makes, into `w2/integrate` or of `w2/integrate` into a ticket branch, carries a `Task:` trailer, is never made with `-s ours`, is never resolved by dropping the ticket's side of a conflict, and never removes or reverts what git's own merge of its parents keeps (DEC-750, DEC-754). A conflict you cannot resolve keeping the ticket's side is returned as PACKAGES. **A merge whose conflict in an acceptance file a test designer resolved carries `Role: independent-test-designer`** (owner, standing, DEC-1031 item 3), never `Role: orchestrator`: W1-01's DEC-253 rule judges a merge's own changes by its role.\n",
      "chunk_id": "34c73b385b1ddd9684e0fa91",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "124ee735903c02d24aba6808",
      "sha256": "251ffa45b348ffe19b2181377eb0a0681fa72c20c6daca9a7912d665ca7cebe8",
      "path": "governance/project/orchestration/packages/P-W2-66-M1-R2.md",
      "start_line": 36,
      "end_line": 51,
      "text": "## 4. Options (DEC-105)\n\n**M1:**\n- **(a) Revise W1-01's merge rule, by a fresh test designer, named in W2-66's ticket body (as DEC-903 did for W1-39).** A merge's acceptance file may also equal git's own merge of its parents (`merge-tree --write-tree`), provided every brought commit is still a test designer's or listed. What it could let through: a semantically wrong but clean auto-merge of two designers' edits, which no one typed. Every conflict resolution and hand edit stays red. Cost: about 1 hour plus the full run, in W2-66's resume. W2-65's branch is red on those two cases until it merges after W2-66, as a known red named in its brief.\n- **(b) Let `acceptance_exemptions` list merges too,** and you list `03f470a5` and `4ef3293a`. It needs the same test revision, plus an owner commit for every future such merge.\n- **(c) Re-make both branches** by re-applying their commits. About 4 hours each, and a history rewrite (never rebase).\n- **(d) Put both cases on `accepted_reds`.** Not recommended: the list only shrinks, and it would hide real offences.\n\n**R2:**\n- **(a) Your exception to DEC-413, as DEC-909 did for W2-69: one more round and a third, last review,** sharing M1's resume.\n  - P1: a selected target missing at the head widens the run to the full regression and is named.\n  - P2: W1-28's coupling reaches every file its scan reads, or falls away if P-IS-15 retires the check first.\n  - A test-design batch, about 30 lines from an engineer, a full verification. About 3 to 4 hours.\n- **(b) Defer:** P1 to W2-68's entry criteria, P2 to P-IS-15. You accept the review's findings in DEC-790's form, and W2-66 closes with the nightly as the backstop.\n- **(c) Re-baseline:** both become Wave 3 rows, covered by the nightly.\n\n",
      "chunk_id": "124ee735903c02d24aba6808",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ye2a",
      "sha256": "0c6271ee003e3f191d024a95ee31a31c37b0aea9e25facd6aceaef60e1ec1147",
      "path": ".tickets/DAEO-ye2a.md",
      "start_line": 1,
      "end_line": 48,
      "text": "---\nid: DAEO-ye2a\nstatus: closed\ndeps: []\nlinks: []\ncreated: 2026-10-24T20:37:07Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-72\ntags: [wave-2, guard, containment, full]\nwbs_id: W2-72\ntitle: 'Containment''s merge rule matches DEC-912: a merge-back file equal to git''s own merge is no change'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/guard/containment.py\n- src/gov/guard/containment_merge.py\n- tests/unit/guard/test_w2_72_*.py\nkpis:\n  success:\n  - 'Under tests/acceptance/, a path both parents of a merge commit changed against their merge base is not the merge commit''s own change when the merge holds exactly git''s own merge of that file (the blob git merge-tree --write-tree <first parent> <other parent> writes for it, with no conflict on that file): containment''s live post-command check neither restores, refuses nor flags it, and judge_commits (the close''s containment gate) returns no finding for it [DEC-918 item 1, DEC-912]'\n  - 'Any file that differs from git''s own merge is still caught as before: a hand edit of a clean merge, a conflict resolution in the file, a file git reports as conflicted, an octopus merge, and a merge whose parents have several merge bases or none stay the merge commit''s own change; a merge-tree run that cannot run gives no allowance (fails closed) [DEC-918 item 1, DEC-410]'\n  - 'Nothing else changes: ticket files keep DEC-421''s and DEC-572''s rule, every other path keeps read_merge''s rule, and the approval check''s reading of merges is unchanged [DEC-918 item 4]'\n  - 'The two merge-backs judge clean: judge_commits returns no finding for 03f470a5 and for 4ef3293a (W2-66''s and W2-65''s), read in this repository''s objects [DEC-918 item 3]'\n  - 'W1-50''s merge cases that read a clean merge of a both-changed acceptance file as the merge''s own are revised by the test designer with Rewrite-Reason: DEC-918, and no other expectation is lowered [DEC-918 item 4, DEC-866]'\n  failure:\n  - A file that differs from git's own merge passes, in the live check or at the close.\n  - A merge-back file equal to git's own merge is restored, refused or flagged.\n  - A ticket file's rule, or any other path's, changes.\nprofile: FULL\nsources:\n- DEC-918\n- DEC-912\n- DEC-410\n- DEC-421\n- DEC-572\n- DEC-453\nest_loc: 50\nacceptance_tests:\n  path: tests/acceptance/W2-72/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\nlist_rows:\n- W2-L437\n---\n",
      "chunk_id": "b49058189bde7a0637cb0adb",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "dd35f86f7295c0225ef5c014",
      "sha256": "417db124ff079a4f68cf35c6f9a29a4bc0df3d98f77db562a4c97b671aa2ae5a",
      "path": "docs/emergency-2/briefs/LEAD-w2-207-runtime.md",
      "start_line": 51,
      "end_line": 56,
      "text": "## The flow and green\nWrite MA-1 to MA-6 into the ticket's KPIs (the CTO approves them by this brief), each with its verify and a failure\nline. Test designer (Sonnet) writes the acceptance tests, red on the base; engineer (Sonnet) to `gov accept W2-207`\ngreen. Return: branch and head; each KPI line with its tests; the cut-over steps as an ordered runbook for the CTO\n(exact commands, the check after each, the rollback of each), with F1's order; reds not yours; the trial figures.\nIf RT-1 across tickets runs long, split it as the ticket's own note allows and say so.\n",
      "chunk_id": "dd35f86f7295c0225ef5c014",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-uzme",
      "sha256": "c7663e9d62878ea0c1e41be8e918e276f3ceacc4090b689dff22169aa1bb6f35",
      "path": ".tickets/DAEO-uzme.md",
      "start_line": 33,
      "end_line": 35,
      "text": "  - 'W1-01''s integration-merge case (test_the_integration_merges_of_this_repository_pass) reads the same list through merge_offences: a merge that brings a listed commit''s changes passes; one that brings an unlisted commit without the test designer''s role stays red; Rewrite-Reason: DEC-906 [DEC-908 item 3]'\n  - 'W1-01''s merge rule (merge_offences, read by the history and integration-merges cases) also passes a merge commit whose every changed file under tests/acceptance/ equals git''s own merge of its parents (git merge-tree --write-tree), when every brought commit that touches the folder is a test designer''s or listed in acceptance_exemptions; a file that differs from git''s own merge (a hand edit, a conflict resolution) stays a refusal. Fixtures: a clean merge of two test designers'' edits of one file passes; the same merge with one line hand-edited stays red; a merge that resolves a conflict in the file stays red; a clean merge that brings an unlisted commit without the role stays red. Rewrite-Reason: DEC-912 [DEC-912 item 1, DEC-750, DEC-754]'\n  failure:\n",
      "chunk_id": "ed014fe39b5b70f4d0ea0712",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ye2a",
      "sha256": "c00d7bb9eea72c3c263d8823034fc849bf08cd75ce1849042bc964ec38dc1cef",
      "path": ".tickets/DAEO-ye2a.md",
      "start_line": 55,
      "end_line": 56,
      "text": "- **The test designer's files** (MR-3: named here, not in the engineer's paths): `tests/acceptance/W2-72/**`, and W1-50's merge cases that read a clean merge of a both-changed acceptance file as the merge's own (`tests/acceptance/W1-50/test_w1_50_acceptance_test_changed_on_both_sides.py`, `test_w1_50_merge_that_takes_each_side_s_change.py`, `w1_50_own_change_support.py`, and any other W1-50 case the change turns red for that reason alone), with `Rewrite-Reason: DEC-918`.\n- **Not changed:** the approval check (`src/gov/decisions/checker.py`), ticket files' rule (DEC-421, DEC-572), W1-01's rule (DEC-912).\n",
      "chunk_id": "7df38e81d53a881d1a89b762",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e0d041b338e96f1381078a58",
      "sha256": "88daeef6512731b21c657f7f4012fbe65ea56c919ac87ef554fba1237af23b19",
      "path": "governance/project/orchestration/packages/P-W2-66-M1-R2.md",
      "start_line": 5,
      "end_line": 11,
      "text": "## 1. Context\n\n- **DEC-899 item 2:** W2-07 merged first (`2a9d1a11`); W2-66 then merged `w2/integrate` back, keeping both sides, re-verified, and got a fresh FULL review on the merged head.\n- **W1-01's merge rule (DEC-253, `merge_offences`):** a merge without the test designer's role passes only if each acceptance file it changes equals one parent's copy, and every brought commit touching `tests/acceptance/` is a test designer's or on `acceptance_exemptions` (DEC-906, which lists non-merge commits only).\n- **DEC-413:** two reviews per ticket; DEC-909 made one exception, for W2-69.\n- **DEC-906 item 1:** a change under `tests/acceptance/` is made only by a test designer, under the owner's named decision.\n\n",
      "chunk_id": "e0d041b338e96f1381078a58",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4d3b1da998a6482725bf6904",
      "sha256": "c65fc8c234ec5b0deb8ac5ac17c194d109b39be8ad0f6308774e1dccc9fe4a4d",
      "path": "docs/emergency-2/briefs/LEAD-w2-207-runtime.md",
      "start_line": 1,
      "end_line": 14,
      "text": "# Lead brief: W2-207, the run-time tool's slice 4, built and green on its branch (the live cut-over is the CTO's, by day, after 0.1.5)\n\nRead `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `w2-207-runtime`; worktree\n`/home/usain/gov-os-worktrees/E2-w2-207-runtime`, branch `e2/w2-207-runtime` from `w2/integrate`. **Do not merge, and\ndo not touch the live machine:** no crontab edit, no change to `~/.gov-os/`, no change to the scratch tools under\n`.gov-runtime/scratch/orchestrator/tools/` or `governance/project/orchestration/tools/dispatch/`, no hook registered in\nthe main tree's settings. Everything is built and proved on the branch, against planted machines and scratch homes; the\nCTO runs the cut-over steps by day after release 0.1.5. Built and green by tomorrow, 2026-11-23. Every helper Sonnet.\n\n**The ticket:** W2-207, `.tickets/DAEO-rt4s.md` (read it whole: KPI lines RT-1, RT-3, RT-5, RT-6, RT-7, D8, F1 and its\norder of the cut-over). EMERGENCY-2 \u00a76.3 (RT-1 to RT-8). Audit 3 of 2026-11-17 and slices 1 to 3 (W2-205 and earlier)\nbuilt the pieces; read `docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md` \u00a76 fix 19 (the scratch dispatcher, two\nwatchers, slots from constants).\n\n",
      "chunk_id": "4d3b1da998a6482725bf6904",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-rt3s",
      "sha256": "5f2a72df0e7167b42f6af43787b1996ab037d00cf20a91afdbddab2980c3af4f",
      "path": ".tickets/DAEO-rt3s.md",
      "start_line": 75,
      "end_line": 76,
      "text": "**Closed at the land, 2026-11-19 03:47 (the CTO; EMERGENCY-2 4.3 step 5):** merged as decf9b8f1 (branch `e2/rt-slice3` at eed9cefa7). On the merged tree, through the slot with workers: `tests/unit/dispatch` 192 passed; `tests/unit/msg`, `launch`, `checkpoint`, `hooks` and `tests/acceptance/W2-205`, `W2-121c`, `W2-05`, `W1-29`, `W2-199`: 1,479 passed, 9 skipped; `gov accept W2-205`: 38 passed, 0 failed. Live from the merge in this repository: the Stop check (the root's Stop hook runs the template's file); not switched: the cron line, the scratch dispatcher, the scratch slot, the relaunch (off). Owed as a follow-up line: after a compaction the resumed session's next step is the fixed \"Resume after compaction\", not the step it had. Slice 4 (the cut-over) is W2-207 (DAEO-rt4s): by day, the relaunch on after one day of the new pass (the CTO's call).\n\n",
      "chunk_id": "d681e36a38f8ddc70fe31e50",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "373ca62bd0ddbe66166e8b59",
      "sha256": "9e94dd334551ba4695bf1cd56a58cb79ae1f3eeed674c60a55d861982990edfd",
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "start_line": 14,
      "end_line": 17,
      "text": "- `usage` added to the recorded command list (`RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`, with its test); the CTO approves that by this brief.\n\nThe test designer writes UR-5 to UR-7's acceptance cases in `tests/acceptance/W2-207/` (its README rows), red on the branch's head; the engineer builds. Never read a real transcript in a test.\n\n",
      "chunk_id": "373ca62bd0ddbe66166e8b59",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-uzme",
      "sha256": "43e0ebcf5c49d7f86ec6b238ed14029c5beb1a9062ba987a0ac55e7ab601b9ad",
      "path": ".tickets/DAEO-uzme.md",
      "start_line": 34,
      "end_line": 51,
      "text": "  - 'W1-01''s merge rule (merge_offences, read by the history and integration-merges cases) also passes a merge commit whose every changed file under tests/acceptance/ equals git''s own merge of its parents (git merge-tree --write-tree), when every brought commit that touches the folder is a test designer''s or listed in acceptance_exemptions; a file that differs from git''s own merge (a hand edit, a conflict resolution) stays a refusal. Fixtures: a clean merge of two test designers'' edits of one file passes; the same merge with one line hand-edited stays red; a merge that resolves a conflict in the file stays red; a clean merge that brings an unlisted commit without the role stays red. Rewrite-Reason: DEC-912 [DEC-912 item 1, DEC-750, DEC-754]'\n  failure:\n  - A retired case whose suites no longer run in the close; any other test changed; W1-01's case accepting a commit the list does not name by its full sha.\nprofile: LITE\nsources:\n- DEC-889\n- DEC-892\n- DEC-899\n- DEC-906\n- DEC-908\n- DEC-912\nest_loc: 20\nacceptance_tests:\n  path: tests/acceptance/W1-05/\n  author: independent-test-designer (MR-3); a retirement by the owner's decision\ntrack: A\nlist_rows: []\n---\n",
      "chunk_id": "99074f785e67c0e6cc5a33f5",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "2e1b73daeb138677d1580958",
      "sha256": "c27155064555dbc4f148a56b1ebe7deeef37255f0c526e9a347a9a1f7c6eb4b0",
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "start_line": 21,
      "end_line": 23,
      "text": "## Green\n`gov accept W2-207` and exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-rt4s=e2/usage-per-repo --onto w2/integrate --select`), both through the heavy slot (DEC-1244 X-1). I-21 is fixed on `w2/integrate` (after the merge it should be green); I-22's two W1-35 import errors are not yours. Check the acceptance trailers (LEAD-COMMON).\n\n",
      "chunk_id": "2e1b73daeb138677d1580958",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "1cb62c1c84ed2907751ee88c",
      "sha256": "f39266c4e6b05eb00104658f8a463c0712397e2e9c7a4c2c5fe5df75855f121f",
      "path": "docs/emergency-2/briefs/LEAD-w2-207-gate.md",
      "start_line": 5,
      "end_line": 7,
      "text": "## Why\nW2-207 (`.tickets/DAEO-rt4s.md`, open) is built and green on two held branches: `e2/w2-207-runtime` (worktree `/home/usain/gov-os-worktrees/E2-w2-207-runtime`) and `e2/w2-207-pre-retire`, each about 207 commits behind `w2/integrate`. Its brief, with KPI lines MA-1 to MA-6, is `docs/emergency-2/briefs/LEAD-w2-207-runtime.md` (read it whole; MA-6 is new, DEC-1247). Since it was built, the owner decided (DEC-1246 (3)(a), read it in `docs/DECISION_REGISTER.md`): three repositories now run at once on this machine (Gov OS, EXAMIN at `/home/usain/gov-os-runs/W2-27/examin`, ASMO OS at `/home/usain/ASMO-OS-V1`), so the dispatcher and load balancer become **one machine-wide gate over every repository's sessions, leads, test slots and GPU work**: work waits for a slot instead of starting; capacity read, never assumed. It ships in 0.1.6; the CTO does the live cut-over by the runbook after you return.\n\n",
      "chunk_id": "1cb62c1c84ed2907751ee88c",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-weh2",
      "sha256": "080e45d028472035ffc3ba0015f198703aa17004ce04456ab007b9771336b705",
      "path": ".tickets/DAEO-weh2.md",
      "start_line": 46,
      "end_line": 53,
      "text": "# W2-180 W2-170's F5 case on other branches\n\nW2-171 run 2 (PKG-W2-171-F5-1, 2026-11-12 07:06): its verify is red on W2-170's F5 case, which diffs any branch against its\nmerge-base with w2/integrate and checks the result against W2-170's allowed_paths. W2-171 rightly changes `src/gov/memaudit/`\nfiles W2-170's paths do not list, so the case is red on W2-171's branch, and the merge queue's candidate merge of W2-171 would\nbe red too, attributed to W2-171's batch: the land refused. The CTO's ruling: (a) a branch-scoped red for W2-171's review now,\nand this ticket (b), which must land before W2-171's land. Class C1. A test revision with a Rewrite-Reason (DEC-866).\n\n",
      "chunk_id": "ee01148f72f839027c559243",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "89fb6c9167543b0fc6f82938",
      "sha256": "ea3513f961ed83bf99fa1e6263525715c0b454041f6fb23fcaf94e9045edbe54",
      "path": "docs/emergency-2/briefs/LEAD-w2-207-gate.md",
      "start_line": 1,
      "end_line": 4,
      "text": "# Lead brief: W2-207, one machine-wide gate (DEC-1246 (3)(a), DEC-1247)\n\nYou are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Where this brief leaves a choice, make it inside W2-207 and say what you chose in your return.\n\n",
      "chunk_id": "89fb6c9167543b0fc6f82938",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-rt3s",
      "sha256": "408674e4a2c6e51107a660091a22090f905f7e8c470d54dfeadeb556b6944ce1",
      "path": ".tickets/DAEO-rt3s.md",
      "start_line": 43,
      "end_line": 46,
      "text": "  - 'F1 A relaunch never loops and never loses work: a session that dies every time is relaunched at most once per ticket and boot, the checkpoint is not rewritten by the relaunch, and a pass killed between the relaunch and its log line does not relaunch again (the relaunch id `relaunch:<ticket>:<boot>:<pid>:<start_ticks>` is claimed in a file before the launch, so the pass is idempotent). Verify: a pass killed after the launch and before the log write, then a second pass: one launch in all. [audit 3 D5]'\n  - 'F2 The stall check, the push and the live tick are untouched, and nothing live is switched: the stall check in the pass (`check_stall`) and its push behave as W2-121c tests them, the cron line, the scratch dispatcher and `heavy_slot.sh` and this repository''s own `.claude/settings.json` are not edited (DEC-1214 T1, T2; DEC-1216 (5)). Verify: `tests/acceptance/W2-121c` stays green and `git diff` of the branch touches none of those paths.'\nnon_goals:\n- 'Dispatching tickets from `gov plan --ready` through `gov launch` with a `ready_at` record, and RT-1 across tickets and leads (the rest of audit 3 D2, D9), RT-8 beyond what slice 1 built'\n",
      "chunk_id": "eb7e2c1222da9db6ec778d10",
      "routes": [
        "closure"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 13,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "812e4b8dc74302df99b2fdc1",
      "parent_id": "b6a354cb3098955c1ea65892",
      "path": ".tickets/DAEO-rt4s.md",
      "start_line": 1,
      "end_line": 51
    },
    {
      "chunk_id": "9a163f632af2e8bc525a6ca3",
      "parent_id": "52c57a605ce1eee6e753eba0",
      "path": ".tickets/DAEO-rt4s.md",
      "start_line": 52,
      "end_line": 62
    },
    {
      "chunk_id": "124ee735903c02d24aba6808",
      "parent_id": "6f28233ed29c6cbc4fe5b51d",
      "path": "governance/project/orchestration/packages/P-W2-66-M1-R2.md",
      "start_line": 36,
      "end_line": 51
    },
    {
      "chunk_id": "b49058189bde7a0637cb0adb",
      "parent_id": "ed530ed9ab71fa41e5fd1381",
      "path": ".tickets/DAEO-ye2a.md",
      "start_line": 1,
      "end_line": 48
    },
    {
      "chunk_id": "4d3b1da998a6482725bf6904",
      "parent_id": "57dc9aac4dab0a97c0843a64",
      "path": "docs/emergency-2/briefs/LEAD-w2-207-runtime.md",
      "start_line": 1,
      "end_line": 14
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-rt2s",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "chunk_id": "d44274c8f2c9b3c93f789e86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "08fe150397a9b08de7a49765",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "7c95e42768e3d803f8cd6adb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "093303391ca85b930e0dc06e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-23.b.md",
      "chunk_id": "bbc1697ecf1d3e06ba7e5e27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "61f543ba02e258921b923884",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "624da5d421a5f5bb779a2762",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-64.a.md",
      "chunk_id": "aaf1e2593366e88f08cc0670",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-23.b.md",
      "chunk_id": "588f33fa90cb627c8e5f268f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-64.a.md",
      "chunk_id": "d33d3703fef597b26b9028e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "78adf033849ed24590dedeff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "4b7fccb17d42ef622a6f0da2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "50637a722ed693f6f970d9a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "54bc702aab87b1d1b62a6cc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "0485a75ba6ba5e39f1d47cf1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "0861017eda9a6a48091031c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "f6d61b909ea183ab3e46aa45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "20dcdf3cbb3490e372746026",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "7e80fed16c9c213abff25502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "82e16dc12ffb38c9cc660072",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "5541d890921fe0c794b45a4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-64.b.md",
      "chunk_id": "8b55a7e42c975223275b68d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-64.b.md",
      "chunk_id": "44fa1ba2154cfc4b151765f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-per-repo.md",
      "chunk_id": "7f6975524a27c5f4a0b35697",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-L437-A.md",
      "chunk_id": "0e5afa648cb8a7bba6b3be76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "6e71cb5074622db89a4c0e1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-64.e.md",
      "chunk_id": "8a1179431dbf244db02e83ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-64.e.md",
      "chunk_id": "d7cedd4f62ea9b0065881e8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "chunk_id": "fd3a4434d74fff79f3e43c9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "8e603a9f2626bb18463a7101",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-w2-207-gate.md",
      "chunk_id": "9719ce7111d0d97c35e70cfb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ye2a.md",
      "chunk_id": "3ff747182abea3a6b295a5ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "eb422e10d043e8e8a5436b99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "54457cf8a3890c699f205b93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-66-M1-R2.md",
      "chunk_id": "e78b1ccc8b57f323e83d122e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "160795d84828f0e98e018e95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "54f4ce5adf8418ff200d7724",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2e69abb8f8e8a3b0dbde00b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "2256a1e9fd83e3270b8f2421",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "5d172f2edea9fdd428941cae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-vhad.md",
      "chunk_id": "64d445352c6e8292d6693f07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "bdf18aef68c633db5e63b510",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ad0910aded1a2955d8c0fcb9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "7955bd57e436df8a68344ab5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "ad0ddb0547f9a4cab17ca46b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "630df801022885cd686c79b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-weh2.md",
      "chunk_id": "b691f22a6200da486e52bba4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "d6fb23196707388dfcdb0c66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "452bdeb91ad3eae6572ee9e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-78-PARK.md",
      "chunk_id": "693ad401f730b152ff4e6af3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "252128166f21411217490a2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "272af19c2c6c975dffc67e4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sg6x.md",
      "chunk_id": "6d78ba08097401d62c650dd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "93d290fb980c8f1ad3018529",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d1-land.md",
      "chunk_id": "cb0a9af5aff134de4fe24a3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "60c0bd160d9f3b2c6b649a71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "4aed1ad7f1c1edc5cd108293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/containment/commits.py",
      "chunk_id": "63e3a748e7f1b9c2c8c04bcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "69185c0ae83c249485a5be8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RECORD-REDS.md",
      "chunk_id": "4aad1b134ce30d016cfb3e29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "6f0b6de56eeb6f86db0be9c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ywb5.md",
      "chunk_id": "56193b713c55f1e045b0b638",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "204b93061ecee222c5408a85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uzme.md",
      "chunk_id": "864ecd59903dcde46eaf3077",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "0df90bc09baac233e9e477a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7rr2.md",
      "chunk_id": "c85119b9046e636ef343b865",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "716a954bf5da8aebfdbc610e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/containment/commits.py",
      "chunk_id": "1c47ad4b05ade30954b5f0f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "f274e565bf8f8d5450db1eec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md",
      "chunk_id": "0e5eec909dc65185067e5808",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "b866b1c7a01c212d7d9dd8a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "43d374d3a0f27e03713333aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "325a78af15812cb1e07d21c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "7ea32fca999eb9749aff2ab1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "6ec79d072021398ac67e15b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "0929db46a49fce5bc068c250",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "7df86f1694ded9c44e621acc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ywb5.md",
      "chunk_id": "44e9a896b2ce8cbbcc9a3d3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b3d192c18e29d8cecc7034d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-91-evidence.md",
      "chunk_id": "0cd2fd83b7cef54d9f45b604",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "ba7ad3e34209e8b8cb43ad00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md",
      "chunk_id": "01a6e52198d360065f62e9e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "904263f6486ac037752b80db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "ab6490b5e0c3962e7777fc3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "f69e1adf431dd56387a2543a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "3eb2ff5ae171c0f6b953f51f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "27873de422a22897e3df2987",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-66-M1-R2.md",
      "chunk_id": "b6aa13df9e0c7d37ee56b7e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "22773e524fb237a672953390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-weh2.md",
      "chunk_id": "7704f21acedb6f5f0b929521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "fe4f3e7fa9433db38a9cf248",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "a62953bc903517b189944ac8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "4d68bef02018f1e19c45e54e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.1/manifest.json",
      "chunk_id": "03b3fcb050595834b4e6f52d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "717d35471d57c15e6e60242c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ad62157c91d2f190151d038f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "9289ec3aed7973f1adcf59fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "9484657cab84065bb23cc8a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "647c32a2ef48f7687a64caf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7oxm.md",
      "chunk_id": "482c9854d8920dc25ee6da81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-ti-cuts.md",
      "chunk_id": "4a7a12243d1125dcb9ecc1cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0cd2.md",
      "chunk_id": "cfd4e53f7f3ac86a16de72f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "8694b2ba986f1f9594b478ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ye2a.md",
      "chunk_id": "10fba612828af66b23b8fdcd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ff6fbdb63b14a9be55c93082",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "chunk_id": "6b6f2b35e939424c2a7da6c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "c366d10eae340b4e13b00a98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md",
      "chunk_id": "65a1c99e8b09e1e344a21380",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-phase0-reds.md",
      "chunk_id": "1ddf81803247d01b5403f00f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "chunk_id": "1bdf34e79998b29014faae96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "5f22e6d5701d0d88478fb8cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "56dd88abd02bb587bcc316d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "d165c06d890a582e394750f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "2b082024e626fc3e364740c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-23.c.md",
      "chunk_id": "02028897b5279485866293db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "9f799ec5a4f4a4d5098aac44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-78-PARK.md",
      "chunk_id": "2777021fe35198262038368c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "a88d46811209675266d2dc08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "chunk_id": "058e1a05266e1928fc63269a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-23.c.md",
      "chunk_id": "36d61b0ec00ffb7ebd7af795",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "ca4c3652b3ded0a415941e41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l78m.md",
      "chunk_id": "99be1ef9696db5412215f25d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "ee05079da2fb760132fb52ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wq2b.md",
      "chunk_id": "aac604c674c8cbbd99e01b46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "f3216439d8d6d6677378636e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-66-M1-R2.md",
      "chunk_id": "fd512eb46d2a157fea3b0620",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b4898209e71f3043c4dc2634",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-07-DR2.md",
      "chunk_id": "fb73b5fcace1132201a24916",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "67461ac2db571d2708e9ac4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-w2-81-e2e.md",
      "chunk_id": "9c8d17777b98b60d7e722b23",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "e32fa261c7d8c2595e336c38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "5cd20fad861d782757800c68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "766b609e55d0c0824feb1026",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "7a418fa18fb64c653eb2a4de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "7adcc3c32c22b673362bdce3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-R1.md",
      "chunk_id": "206680e1e258761b48fab1fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "0fd14b052e30de863a224c1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "1d09fa99e0aec08125cc1e35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "d49c45ff620c0101bd7f2a4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "a2ce080cc61e6f91a2cf7a70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "7b122360266b83570b646c80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6y0x.md",
      "chunk_id": "d985a95113b9f4679230e808",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "3917edb38b8c0ac6c5532293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "c3aaa61f7776e4ce714a2119",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "2bcdd73a8d07d69087d9f0c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A3-target-path-map.md",
      "chunk_id": "f7660a226803cdf0ad574134",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "cbcba0cedb99e85575e5b7bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "dfe431d9cd4f1db0cce98c1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "ca9988b377946dc81de04c84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A1-inventory.md",
      "chunk_id": "abc1cf8aed0f5248c176a432",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "f6a55c68d7803d1b14202ad7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-2.md",
      "chunk_id": "19defab900420441f79a60bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "fb358e1c5e3bacb61b25f2c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "1f9b315d00be9c4172f6245b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "4417a14220fd6a34f0d6b355",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.1/manifest.json",
      "chunk_id": "efc1fd2786451d9030a2241f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "22b780b1274fb883ac885f82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wq2b.md",
      "chunk_id": "ffa92a21b3ab2c1af19cba15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "eb85334372343af873b12025",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "71e1265e8b4f23187d495cf4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-phase0-memory.md",
      "chunk_id": "75a23213506da2e798e40dee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0cd2.md",
      "chunk_id": "72e9584a460f96b3b3218af2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "ae02a78287148d71db59f621",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "bb82f321c622726043eadeee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-91-evidence.md",
      "chunk_id": "c52ed48350278370479f4fdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "8ad696cc2b9ae613bcd48a3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-uzme.md",
      "chunk_id": "8a2bbb739bf703638da02d7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "eb6200d2fc3275a42cec3917",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-W2-60a-P5.md",
      "chunk_id": "5683e798a3434def5d2270b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "856069318a11c7bf69867c45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-27-CIT-E.md",
      "chunk_id": "0c94917b2cd07d80a00471e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "fb5a6746efd7045a065866fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f02470db08d0d2c05c101827",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "59ffb5f6a481404ec700018a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-65-M1.md",
      "chunk_id": "fedd8eb080622a9e77196e2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "3f0521e85bffc04663a6d326",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "21838dc27ae0e3c3d73288fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "1d5129a937414644b68b11e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "c6da1032993011b5af1860dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "bb44a5b0a5bb338b68e0d461",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "e854055689abe37eb0b03894",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "3ac0cf9f55988caa7d980931",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-INVENTORY-2026-11-19.md",
      "chunk_id": "a21c81065247d8d538042d47",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "9f348566aca99266eacf2f5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "8efa8c70e8b2e7b1cd081fcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "a1369156084a82117ff0f1ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b2718424875daec77f36554d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "a8f9b2223c1a119b4511d2f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "9a91b1c1728374221f9e6568",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "0c2963d25c3bd54f72a47e3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "69fa41850853e23fb0ff92ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "234d9d663fce2e9ed43fdf22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "de826240703334cf14488cf2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "2e61fc3c222ce79c25257750",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "35d75fb0243f41e28563f87d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "f53872190ee70350ce2a26f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "7f2a7eae59b59590398730da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "bb78f646bba3225f004739d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "b3dfd1f27a4d26d157b1a001",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "63a68009136d9dfdcdf97525",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "63a3ae63ac781ab7481e85e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "a79bf869c0e257bb7b8f0eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "9883ec5a63f37e7d3560fa2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "98b71825d36a379ffd140ac6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "f1c05ad8c38741b366b64ace",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/integration-plan-decisions-2026-11-24.html",
      "chunk_id": "349efb59d4ea3c438739eac0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/golden-workflow-decisions.html",
      "chunk_id": "0b7c621c078e504eb4d6ccc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-w2-207-runtime.md",
      "chunk_id": "6bb039e65bd650b2609ed7fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "50299b59b86ffc69bc0516f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "d759bbe642359debf53e8fa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "71fa8a1d1cfbb49155912335",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "975f8e076948ebe4c3587bd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "782b947b64a7438dcfd36d3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "89b209b3cf4ca61cc421960e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "0ebed2b21e7aa5a3446694eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "c1993353a4eaf47cfe088754",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-by-role.md",
      "chunk_id": "6e48d9709caa00cba11b0799",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "9784c979e98ef6d2dba87f3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "231bf54ee313283a324e7234",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "1ed49a2bb6e827021893c1f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "013aea19af229d7674a7dd90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "chunk_id": "90d818b717dec7b9a873d1c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "a351c40fb4e2abc9aa151b0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "47fb3c55799e9aab3ad1e469",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-w2-207-runtime.md",
      "chunk_id": "ba700332785e13c71879201f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4ab56cb82ae415b0536ba6e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "f6a385f58a57a665d3cb1150",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-56-CIT-E.md",
      "chunk_id": "71232127f531d8a635be2311",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "d20f45b45b0529ec971be1aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "chunk_id": "08d42091b111fc23b0e08cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "75db42d06ad486e9ae249288",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "8b8bb0151646cfec1df28284",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "chunk_id": "2c83280e4d4a813e65abdb2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-w2-207-runtime.md",
      "chunk_id": "3fddfdcccefe9bf7ecf843d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "062e91d943e7e0add824d349",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-by-role.md",
      "chunk_id": "76fca833c069cbe72ce34b9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "e6ce15149eeb1652a143fad5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "7cf6fd22f849a1cbf50fa2c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "48cf8035678911c359ce86ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "7ef7065015b76c1d37fc4266",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "85d39a5f5a6ab5e561f2f0cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "b62919e3e91dd56e83d837f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-per-repo.md",
      "chunk_id": "80ab77adc03f7f2266a40100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-escalation-slice.md",
      "chunk_id": "731edfc23c680ace4931ece9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "8506e6222c9a08bd0929f75a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "375802c532157ade9343aa1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "121a6addbcc8dd53a5dd6ff3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-escalation-slice.md",
      "chunk_id": "46c04760f5a6533c6d284a44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "fc8c92043a2e0d063730df43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "d3bc5fcb6f63a9c9ee5aaa6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "04d1ed000724aad9a0193732",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "chunk_id": "4333cbf65c220627e8f5c8e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "521b56c8695d9acde5e29163",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-per-repo.md",
      "chunk_id": "32000bd5a659c190a2c1e82b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "30b1b98c21de008b6af5359f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/w2_53_support.py",
      "chunk_id": "e14a9072c474a383de445f9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-72/w2_72_support.py",
      "chunk_id": "ec7dc5c3b27f4876b3dc7862",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-01/test_w1_01_integration_merges.py",
      "chunk_id": "84b979b2817b2847f5597d02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run3-narrow.md",
      "chunk_id": "a62d07d950c2753504d416e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-01/w2_01_support.py",
      "chunk_id": "d174d231748f6fd1da203c96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-01/README.md",
      "chunk_id": "25544f611e6b0d0f2e18f32f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-202/conftest.py",
      "chunk_id": "e334325a4c8d47d31ada0af9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-50/w1_50_support.py",
      "chunk_id": "7c02e0db47b842a155b65bf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-157/test_w2_157_nothing_else.py",
      "chunk_id": "2244b17209b5a995ae20b422",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/README.md",
      "chunk_id": "7f06edc4b291b37ea7a47c13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-72/w2_72_support.py",
      "chunk_id": "9c4cf802ef44941e05f1307f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-01/test_w2_01_merge_form.py",
      "chunk_id": "5546be174814c344ad249298",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/README.md",
      "chunk_id": "d011bac0972cb6c804ae948b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-01/README.md",
      "chunk_id": "3f2159653aab7e0601f9a100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-202/conftest.py",
      "chunk_id": "9646af18548c2565966bcc12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-158/test_w2_158_nothing_else.py",
      "chunk_id": "41bd66c872a50602b9e431f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-01/README.md",
      "chunk_id": "e833857c48931c617c208114",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/w2_53_support.py",
      "chunk_id": "55a0dffb732886f9f8fe5d9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-173/README.md",
      "chunk_id": "7a268c061ccb97edb072db08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-72/w2_72_support.py",
      "chunk_id": "aa3a313622b182af12330dc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-72/w2_72_support.py",
      "chunk_id": "6613ed7156a4e36fc1f3005d",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "closure": {
      "available": true,
      "reason": null,
      "followed": {
        "records": [
          "CAP-23.b",
          "CAP-64.a",
          "DEC-1214",
          "DEC-1216",
          "DEC-1236",
          "DEC-1225",
          "DEC-1222",
          "DEC-1219",
          "DEC-1215",
          "DEC-1218",
          "CAP-64.b",
          "CAP-64.e"
        ],
        "left": 2
      },
      "changed_by": {
        "DEC-1214": [
          "DEC-1236",
          "DEC-1225",
          "DEC-1222",
          "DEC-1219",
          "DEC-1215"
        ],
        "DEC-1215": [
          "DEC-1218"
        ],
        "DEC-1216": [
          "DEC-1218"
        ],
        "DEC-1218": [
          "DEC-1220"
        ],
        "DEC-1222": [
          "DEC-1225",
          "DEC-1223"
        ],
        "DEC-1225": [
          "DEC-1236"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5885
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLXJ0M3MubWQiLDQzLDQ2LCJlYjdlMmMxMjIyZGE5ZGI2ZWM3NzhkMTAiXSxbIi50aWNrZXRzL0RBRU8tcnQzcy5tZCIsNzUsNzYsImQ2ODFlMzZhMzhmOGRkYzcwZmUzMWU1MCJdLFsiLnRpY2tldHMvREFFTy1ydDRzLm1kIiwxLDM0LCI1MTI4MTlkNmMwNTMzMTQwMjllZjFjNjAiXSxbIi50aWNrZXRzL0RBRU8tdXptZS5tZCIsMzMsMzUsImVkMDE0ZmUzOWI1YjcwZjRkMGVhMDcxMiJdLFsiLnRpY2tldHMvREFFTy11em1lLm1kIiwzNCw1MSwiOTkwNzRmNzg1ZTY3YzBlNmNjNWEzM2Y1Il0sWyIudGlja2V0cy9EQUVPLXdlaDIubWQiLDQ2LDUzLCJlZTAxMTQ4ZjcyZjgzOTAyN2M1NTkyNDMiXSxbIi50aWNrZXRzL0RBRU8teWUyYS5tZCIsNTUsNTYsIjdkZjM4ZTgxZDUzYTg4MWQxYTg5Yjc2MiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1kMS1sYW5kLm1kIiw4LDEyLCI0Y2ViMGMyNjJiMDNmYmFkNzE4ZDJhN2IiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtdXNhZ2UtZml4Lm1kIiwxNCwxNywiMzczY2E2MmJkMGRkYmU2NjE2NmU4YjU5Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELXVzYWdlLWZpeC5tZCIsMjEsMjMsIjJlMWI3M2RhZWIxMzg2NzdkMTU4MDk1OCJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC13Mi0yMDctZ2F0ZS5tZCIsMSw0LCI4OWZiNmM5MTY3NTQzYjBmYzZmODI5MzgiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtdzItMjA3LWdhdGUubWQiLDUsNywiMWNiNjJjMWM4NGVkMjkwNzc1MWVlODhjIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELXcyLTIwNy1ydW50aW1lLm1kIiw1MSw1NiwiZGQzNWY4NmY3Mjk1YzAyMjVlZjVjMDE0Il0sWyJnb3Zlcm5hbmNlL3Byb2plY3QvYnJpZWZzL0xFQUQtdzItY29tbW9uLm1kIiwxMzIsMTMyLCIzNGM3M2IzODViMWRkZDk2ODRlMGZhOTEiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtVzItNjYtTTEtUjIubWQiLDUsMTEsImUwZDA0MWIzMzhlOTZmMTM4MTA3OGE1OCJdXSwiZiI6Ii9ob21lL3VzYWluL0R5bmFtaWMtQWdlbnRpYy1FbmdpbmVlcmluZy1PUyIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiNjFlYTI4YmM0ZDBmMjBhMSIsIm8iOlsyNSwyOSw1LDM5LDMsMjEsMzQsMTMsMjQsNCwzMywyLDE4LDM4LDEsMjAsMCw5LDE3LDM1LDI4LDYsMTAsNywzMiwxMiwyMywzNywzMSwzNiwxNiwxMSwxNCw4LDE1LDMwLDE5LDIyLDI2LDI3XX0sInEiOiJtZXJnaW5nIGhlbGQgYnJhbmNoZXMgd2l0aCBjb25mbGljdHMgaW4gdGVzdHMvYWNjZXB0YW5jZTogd2hvIHJlc29sdmVzLCByZW1lcmdlLWRpZmYgYXV0aG9yc2hpcCBjaGVjaywgVzItMjA3IHJ1bnRpbWUgYW5kIGV2YWwtcm9vdHMgYW5kIGtpdC1oZWFkIGNvbmZsaWN0cywgaW50ZXJpbSBkZW55IGxpbmVzIGZvciBzZXRzIHJvb3RzIiwiciI6MCwicyI6ImMxZTgxYWZkM2U3NTYwZTdhOGY3NjliYjUxZGUwODNiMDdkNzIxNTgiLCJ0IjpudWxsLCJ4IjpbIjUyYzU3YTYwNWNlMWVlZTZlNzUzZWJhMCIsIjU3ZGM5YWFjNGRhYjBhOTdjMDg0M2E2NCIsIjZmMjgyMzNlZDI5YzZjYmM0ZmU1YjUxZCIsImI2YTM1NGNiMzA5ODk1NWMxZWE2NTg5MiIsImVkNTMwZWQ5YWI3MWZhNDFlNWZkMTM4MSJdfQ==",
  "routing": {
    "code": [],
    "named": [
      "812e4b8dc74302df99b2fdc1",
      "9a163f632af2e8bc525a6ca3"
    ],
    "phrasings": [
      "merging held branches with conflicts in tests/acceptance: who resolves, remerge-diff authorship check, W2-207 runtime and eval-roots and kit-head conflicts, interim deny lines for sets roots",
      "merging held branches conflicts tests/acceptance resolves remerge-diff authorship check W2-207 runtime eval-roots kit-head conflicts interim deny lines sets roots",
      "merging held branches with conflicts in tests/acceptance: who resolves, remerge-diff authorship check, W2-207 runtime and eval-roots and kit-head conflicts, interim deny lines for sets roots DAEO-rt4s"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "512819d6c053314029ef1c60",
        "path": ".tickets/DAEO-rt4s.md",
        "start_line": 1,
        "end_line": 34
      }
    ]
  }
}
