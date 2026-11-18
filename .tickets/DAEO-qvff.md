---
id: DAEO-qvff
status: closed
deps: [DAEO-nqa2]
links: []
created: 2026-10-31T21:53:25Z
type: task
priority: 1
assignee: engineer
external-ref: W2-111
tags: [wave-2, test-revision, guard, full, capacity]
wbs_id: W2-111
title: 'The hook-latency cases time the hook''s own work: W1-02''s, W1-05''s and W2-57''s p95-under-100-ms cases judge the hook, not the machine''s load (P-LATENCY-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-nqa2
allowed_paths:
- src/gov/util/role_paths.py  # [added 2026-11-15, the owner's P-W2-111-YAML-REST (a): the guard's role_paths and front-matter reads through the checked loader]
- tests/acceptance/serial-only.txt  # [added 2026-11-15 by the CTO, DEC-1156 (7), P-W2-111-R5-ROWS (a): the ticket's own five timing files as 'serial: latency' entries, beside W1-02's, W1-05's and W2-57's]
- tests/acceptance/W1-02/test_w1_02_guard_hook.py
- tests/acceptance/W1-02/README.md
- tests/acceptance/W1-05/test_w1_05_live_hooks.py
- tests/acceptance/W1-05/README.md
- tests/acceptance/W2-57/test_w2_57_designer_read_p95.py
- tests/acceptance/W2-57/README.md
- tests/acceptance/W2-111/**
- src/gov/guard/install.py
- src/gov/guard/reads.py
- tests/unit/guard/test_w2_111*
- docs/probes/DAEO-qvff/**
- src/gov/guard/decide.py  # [added, DEC-1187: S9 the fixed import cut]
- src/gov/guard/heldout.py  # [added, DEC-1187]
- src/gov/util/parts.py  # [added, DEC-1187: the parsed-once loader]
- docs/changes/W2-111-live-hook/**  # [added, DEC-1187: S10 the live-hook diff for ACT-GUARD-FIX-7]
- tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py  # [added, the CTO's path case DEC-1156 (7): the two strict xfail marks made non-strict before ACT-GUARD-FIX-6 applies]
kpis:
  success:
  - 'Each of the 15 hook-latency cases (11 in DEC-979''s count; 15 node ids with their parameters, the CTO, DEC-1157 (12)) (W1-02''s `test_decision_p95_is_under_100_ms` in its parameters, W1-05''s `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57''s `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook''s own work: the CPU time (user and system) of the hook''s process and its children over each call, or the call''s wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook''s process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]'
  - 'Under load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded), each case''s verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded): the 15 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]'
  - 'They still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]'
  - 'What each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]'
  - 'A Bash call is decided within the 100 ms bound at p95 by the hook''s own work (the CPU time of the hook''s process and its children, W2-111''s method), for a plain command, a pipe and a redirect, with a role set Verify: the new Bash cases under `tests/acceptance/W2-111/` run against the product hook pass at the bound, quiet and at a load of about 20; before the change they fail (the measure of 2026-11-14 gave 103-167 ms; evidence `~/gov-os-runs/W2-111/q-scan-2/`). [DEC-1184 (3)]'
  - 'A call is decided within the bound with 150 or more worktrees registered Verify: a case that registers 150 or more planted worktrees on a planted repository and times Read, Write and Bash calls with a role set: p95 within 100 ms of the hook''s own work. [DEC-1184 (3)]'
  - 'The install check reads PATH once per session, not on every call; a changed PATH is read again Verify: a unit case counts PATH lookups over 20 calls of one session (one lookup), then changes PATH (one more); `has_install`''s answers are the same as before for the same commands. [DEC-1184 (3)]'
  - 'A call is judged only against the trees its target lies in, and every decision is the same as before Verify: the guard''s rule suites pass unchanged, and the same corpus of calls (W2-42a''s parser corpus and the five rules'' cases) gives the same allow or refuse decision before and after, with the per-tree judge called only for trees holding the call''s targets. [DEC-1184 (3)]'
  - 'S9 (DEC-1187; amended by the CTO 2026-11-15, P-W2-111-S9-BASE (a), then P-W2-111-S9-DROP (a), DEC-1157 (12)) The hook''s fixed cost is cut where it lies, in the live hook''s path (YAML through the pure-Python SafeLoader where libyaml''s CSafeLoader is installed, the tree roots, the evaluation sets'' globbing, the imports): the live hook copy is judged by DEC-1187 (1)''s own target (S10''s measure: the patched copy, paired against the applied ACT-GUARD-FIX-6 hook, every mapped W1-02, W1-05, W2-57 and Bash case within 100 ms at p95, quiet, by W2-111''s method, decisions unchanged), with the measured drop recorded [changed, P-W2-111-S9-DROP (a): the 30 ms drop came from the loaded 14-28 measure; quiet, the applied hook was already 52-83 ms and the rest of each call (interpreter, the pinned gov''s imports, compiling the script) lies outside .claude/hooks/]. In the product, decisions are unchanged and a call that needs neither the held-out nor the parts YAML parses neither. Verify: S10''s measure on the patched copy; the decision corpus (3,452 calls x 4 roles) gives the same decisions; a count case shows no YAML parse on a call that needs none. (The product hook''s cases already run 23-52 ms; its whole import cost is about 14 ms.) [DEC-1187 (1)]'
  - 'S10 (DEC-1187) The live hook''s changes are prepared for ACT-GUARD-FIX-7: the PATH-once and per-target-trees speed-ups and the import cut, as a diff of `.claude/hooks/` against the applied ACT-GUARD-FIX-6 bytes, with the functions and lines named. The CTO builds the ACT; the ticket never writes `.claude/`. Verify: the diff applies to a clean copy of the live hook, and in that copy every W1-02, W1-05, W2-57 and Bash case is within 100 ms at p95 by W2-111''s method (`~/gov-os-runs/W2-111/gf6-measure/measure.py`) on the live repository. [DEC-1187 (1)]'
  failure:
  - 'The 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 15 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.'
  - 'A case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.'
  - 'A case whose verdict still changes with the machine''s load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.'
  - 'A decision changed by the speed-up: a refusal turned into an allow, or an allow into a refusal. Verify: the decision corpus run before and after: no decision differs.'
  - 'A Bash or many-tree case that still passes a hook doing 150 ms of its own work. Verify: the planted 150 ms hook against each new case: none passes.'
profile: FULL
sources:
- DEC-1187
- DEC-979
- DEC-906
- DEC-968
- DEC-958
- DEC-1184
- DEC-1182
- DEC-1157
est_loc: 320
acceptance_tests:
  path: tests/acceptance/W2-111/  # the reopen's cases (DEC-1184 (3)); the earlier revision was judged on its revised suites (DEC-892): with W1-05's test_w1_05_live_hooks.py and W2-57's test_w2_57_designer_read_p95.py (the CTO, DEC-1157 (12), 2026-11-13)
  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suites and the planted slow hook (DEC-892)
track: B
list_rows: []
---
# W2-111 The hook-latency cases time the hook's own work

The owner's D2 (a) on CAPACITY-1 (DEC-979, P-LATENCY-1): a fresh independent test designer revises the 11 hook-latency cases so they judge the hook, not the machine's load, at the same 100 ms, lowering nothing (DEC-906: the owner's named decision).

- **Why:** on 2026-10-31 the 11 cases were red under load whatever the change: traced 3 rounds with and without W2-106, red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30, with run times of 34 to 152 s; they pass alone on a quiet machine. They refused a batch of four (15:19) and redden the nightly. DEC-968 allows no accepted reds.
- **After W2-90b** (`DAEO-nqa2`): it holds `tests/acceptance/W1-05/test_w1_05_live_hooks.py` too.
- **Not here:** the hook itself (a slow hook is a product ticket); the five-rule guard's decisions.

**D9-FATES (DEC-1083, DEC-1084):** Stays open as a LITE test revision outside K9 (DEC-1084 (1)). Its 7 lines are not met: `6008a41f` touches only the READMEs of W1-02, W1-05 and W2-57, and there is no `tests/acceptance/W2-111/`, no `Rewrite-Reason: DEC-979` and no CPU-time or load code (audit 1).

**Reopened 2026-11-14 by the owner (DEC-1184 (3), Q-SCAN-2 (a)), within the 100 ms bound's purpose.** The measure of 2026-11-14 (W2-111's method; `~/gov-os-runs/W2-111/q-scan-2/`): the 15 cases pass (87-97 ms best round, load 13-20), but a Bash call takes 103-167 ms, and every call grows with the worktree count (about 59 ms to list 248 trees, 47 ms for the per-tree judge, 52 ms for the Bash install check). The owner's decision changes the "Not here: the hook itself" line above for these two costs only. Order: an independent test designer writes the Bash and many-tree cases under `tests/acceptance/W2-111/` (proven red before the change on a planted repository); an engineer caches the install check's PATH lookup per session (`src/gov/guard/install.py`) and judges a call only against its targets' trees (`src/gov/guard/reads.py`); an independent review (FULL: the guard, fails-open risk); the kernel gate and the owner's approval of the kernel bytes at the land. The live hook (`.claude/hooks/pretooluse.py`, a control path) takes the same change by the planned live-hook ACT, with the owner's yes.

**Interface at claim (the CTO, DEC-1157 (3)):** `has_install(command)` keeps its signature and answers; the PATH lookup is cached in the process for the session (keyed by the PATH value). `_trees(root)` keeps its return form; the caller passes the call's target paths so that only trees holding a target are judged; a target that lies in no tree is judged as today. The new cases time the product guard's hook the way W1-02's and W1-05's cases run and measure it (W1-02's budget and method); the live hook's figures are measured in the live-hook ACT's rehearsal, not here.

**Path case 2026-11-15 (the CTO, DEC-1156 (7)):** ACT-GUARD-FIX-6 (the live hook to W2-42a's parser, DEC-1174 (1)) makes `tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py`'s two `xfail(strict=True)` cases (lines 119-126) XPASS, which fails strict. W2-111's test designer makes the two marks non-strict now (`strict=False`, reason naming ACT-GUARD-FIX-6), `Rewrite-Reason: DEC-1156 (7), DEC-1174 (1)`, no other change; the marks' removal after the apply is DECIDED-NOT-DONE's follow-up row. Listed for the owner's reading.

**Run r4 returned PACKAGES 2026-11-15 02:31 (the CTO's delegated P2s, listed for the owner's reading):** P-W2-111-MARGIN (a): land on a `gov accept` taken at a quiet moment in the CTO's load window (the one red, success-6 at 151 trees under load 25-40, passes alone at load 25: a load-sensitive timing red, never retried into green, no accepted red); (b) cutting the hook's fixed ~50 ms of imports and YAML (kernel files) goes to the owner as a follow-up decision. P-W2-111-RED-BEFORE (a)+(c): success-5's "before the change they fail" is accepted as shown at the CTO's load of about 20 (plain and pipe Bash cases fail before; quiet 56-59 ms and load 52 do not), and the wall-time and /mnt/c cost go to the live-hook ACT's rehearsal. Review round 1 PASS (PR-DAEO-qvff-r4.md). Next: run r4b in the load window after the re-pin (quiet after-change run, quiet `gov accept`, lead_verify at 75e709f68371, the side-by-side at load 50+), then DONE, land; W2-111 lands before ACT-GUARD-FIX-6 is queued (W2-42a's non-strict marks ride in it).

**Reopened 2026-11-15 by the owner (DEC-1187, P-W2-111-MARGIN (a)):** after ACT-GUARD-FIX-6 the live hook measured over 100 ms (Bash 112-208 ms, role-checked calls 127-153 ms; `~/gov-os-runs/W2-111/gf6-measure/`). S9 cuts the hook's fixed import and YAML cost in the product; S10 prepares the live hook's diff (the r4 speed-ups plus the cut) for the CTO's ACT-GUARD-FIX-7. The src part reaches the live hook through release 0.1.1's re-pin (DEC-1178 (3)(c)). FULL, class C3; the kernel gate and the owner's approval of any kernel bytes at the land.

**Interface for S9's count case (the CTO, 2026-11-15, DEC-1157 (3), on the r5 lead's measure at 0e2cdf33e):** observed in the product hook's process as W1-02 runs it, by the YAML files opened under `governance/` and the number of parses through yaml's public load API: (1) a call refused before the held-out check (for example `dangerouslyDisableSandbox` set) parses no YAML file; (2) a write or edit, of any role, parses no `path-map.yaml`; (3) every call parses each YAML file it opens at most once. `held-out.yaml` stays read on every call past decide()'s early refusals (DEC-218: a broken held-out.yaml stops every call). Decisions and reasons are unchanged (the corpus).

**Widened 2026-11-15 by the CTO (DEC-1156 (7), P-W2-111-R5-ROWS (a)):** `tests/acceptance/serial-only.txt`, so a test designer lists W2-111's five timing files as `serial: latency` (rv-3's F2: they red only inside lead_verify's parallel phase at load 10-20; alone and quiet 25/25 pass). rv-3's F1 (libyaml accepts tab and `? ` texts the pure SafeLoader refuses, so a malformed held-out.yaml no longer stops every call: fails open) is fixed in the same round by DEC-802 (engineer, product and live-hook diff, with a test-design batch giving it as a described behaviour), and F3's README line with it; then a narrow independent re-check at the new head (DEC-1154).

**Widened 2026-11-15 by the owner (P-W2-111-YAML-REST (a)):** `src/gov/util/role_paths.py`. The fast YAML loader's fail-open class (rv-3's F1) also sits in the guard's other reads: `role_paths.py:85`, `:165`, `parts.py:234` and the live hook's `role_reads.py:111`, `:171` (in the diff). All are routed through the checked loader, with a planted-tab case each, before the narrow re-check; ACT-GUARD-FIX-7 and release 0.1.1 carry it.

**Reopened 2026-11-16 by the CTO within purpose (DEC-1157 (12); DEC-1198 (6), DEC-1203 (b)): ACT-GUARD-FIX-7 follow-up 03.** ACT-GUARD-FIX-7 applies this ticket's live-hook diff to `.claude/hooks/`; after it, `tests/acceptance/W2-111/w2_111_live_hook.py`'s `_copy_hooks` would copy the already-patched tree and its 20 + 5 + 7 cases (DND 231) would judge the diff against the wrong bytes. An independent test designer applies the prepared patch (`.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-7-followups/03-w2-111-acceptance-before-from-git.patch`): the before copy is read from git at ACT-GUARD-FIX-6's commit `fa6135903`, not from the tree, so the cases judge the same bytes before and after the apply. No other change; no KPI changes; closed again after the merge. Listed for the owner's reading.


**Closed on its record 2026-11-18 by the CTO (EMERGENCY-2 6.1; the owner's audit 09 items):** the guard and the sandbox this ticket served are switched off and being retired (EMERGENCY-2 2.2, 6.1); nothing further is built under it, and any open reopen or follow-up of it is void.
