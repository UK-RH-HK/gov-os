# W2-111 (DAEO-qvff): the guard's two costs, the PATH lookup per session and the trees judged per call (brief eng-1, from the ticket lead)

You are a fresh engineer for ticket **DAEO-qvff (W2-111)**, profile FULL, class C3 (the guard's path: the kernel gate
and the owner's approval of the kernel bytes apply at the land). Use your skills `test-driven-development`,
`security` and `systematic-debugging`. You change the guard's code so a call's own work stays within the 100 ms bound
with many worktrees and on Bash calls, and **no decision changes**.

## Why
The owner reopened W2-111 on 2026-11-14 (DEC-1184 (3), Q-SCAN-2 (a)). The CTO's measure (W2-111's method: the CPU time
of the hook process and its children, less a reference hook timed beside it, p95 under 100 ms): a Bash call with a role
set takes 103-167 ms, and every call grows with the registered worktrees: about 59 ms to list 248 trees (`_trees` /
`_worktrees`, `src/gov/guard/reads.py:304-358`), 47 ms judging each tree's protected part (`parts`,
`src/gov/guard/reads.py:361-391`: one `_Part` per tree; `_Part.__init__` and `gov/util/parts.py:118` glob per tree),
and 52 ms for the Bash install check (`has_install`, `src/gov/guard/install.py:143-147`: `os.path.realpath` of every
`PATH` entry on every call, before it knows whether the command downloads anything). The CTO's evidence, read-only:
`/home/usain/gov-os-runs/W2-111/q-scan-2/` (`prof.txt`, `measure.py`, `breakdown.py`, `result-run*.json`); the profile
there is the **live** hook's, which has the same shape as the product guard's.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-111 |
| branch | w2/W2-111 (at d54654eab) |
| the only paths you write | src/gov/guard/install.py, src/gov/guard/reads.py, tests/unit/guard/test_w2_111* |
| the ticket (read-only) | /home/usain/gov-os-worktrees/W2-111/.tickets/DAEO-qvff.md |

Never read `tests/acceptance/W2-111/` or `/home/usain/gov-os-worktrees/W2-111-tests` (the test designer's work on this
ticket, DEC-820); the guard refuses it too. Other tickets' acceptance suites are open to read and run. **Never edit**
`.claude/` (the live hook `.claude/hooks/pretooluse.py` is a control path; it takes your change later by the CTO's
live-hook ACT), the path map, or any acceptance file. The register by id only (`docs/DECISION_REGISTER.md`, grep
`### DEC-1184`).

## The interface (binds you; the CTO at claim, DEC-1157 (3))
- `has_install(command)` keeps its signature and its answers; the PATH lookup is cached in the process for the session,
  keyed by the PATH value (a changed PATH is read again).
- `_trees(root)` keeps its return form; the caller passes the call's target paths so that only trees holding a target
  are judged; **a target that lies in no tree is judged as today**.
A KPI you cannot meet inside this interface or inside your three paths comes back in `unresolved` as a question with
options (cost, recommendation), never as a wider change. If the caller that must pass the targets lies outside
`reads.py`, stop and say so.

## The lines you build to (the ticket's, word for word)
- **success-5**: A Bash call is decided within the 100 ms bound at p95 by the hook's own work (the CPU time of the hook's
  process and its children, W2-111's method), for a plain command, a pipe and a redirect, with a role set.
- **success-6**: A call is decided within the bound with 150 or more worktrees registered (Read, Write and Bash calls with
  a role set, on a planted repository).
- **success-7**: The install check reads PATH once per session, not on every call; a changed PATH is read again. Verify:
  a unit case counts PATH lookups over 20 calls of one session (one lookup), then changes PATH (one more); `has_install`'s
  answers are the same as before for the same commands. — **this unit case is yours** (`tests/unit/guard/test_w2_111_install.py`
  or similar). Use commands that do need the PATH set (a `curl -o`/`wget -O` download), so the count means something.
  Making the lookup lazy (only when a download target is found) as well as cached is inside the interface, if the
  answers stay the same.
- **success-8**: A call is judged only against the trees its target lies in, and every decision is the same as before.
  Verify: the guard's rule suites pass unchanged, and the same corpus of calls (W2-42a's parser corpus and the five rules'
  cases) gives the same allow or refuse decision before and after, with the per-tree judge called only for trees holding
  the call's targets. — **your unit cases** (`tests/unit/guard/test_w2_111_trees.py` or similar): the per-tree judge
  called only for trees holding the call's targets (count it), and the decisions the same.
- **failure-4**: A decision changed by the speed-up: a refusal turned into an allow, or an allow into a refusal.

## Fails open: the thing the review checks first
"A tree holding a target" must include **every tree that lies below a target**, not only the tree a target lies in: a
search, listing or glob from a folder above the trees (`grep -r x /home/usain/gov-os-worktrees`, `find <parent>`, `ls
<parent>/*/…`, `cat <parent>/*/secret-ish`) reaches into every tree under it and must be judged against each of them, as
today. A target the guard cannot resolve (a variable, `$(…)`, an unresolvable glob, a relative path with no known cwd, a
symlink), a cwd change it cannot follow, or any error: judged against **all** trees, as today (fail closed). The runs
root's part (`_Runs`) and the own-ticket and changed-files parts are untouched. One sound shape, your choice: keep one
part per tree but make each tree's part lazy (its expensive set-up paid only when a path at, in, or above that tree is
checked), so nothing about which parts exist changes; or pass the resolved targets into `parts` and add a tree only when
a target is in or above it, with "unknown" meaning every tree. Say which, and why, in your return.

The 59 ms listing: profile the **product** hook first (how W1-02's cases run it: `tests/acceptance/W1-02/w1_02_support.py`)
on a repository with 150-250 worktrees, and say where the time is (the `git worktree list` process, `realpath`, the
glob, imports, the YAML loads). If the listing itself must get cheaper (reading the common directory's `worktrees/*/gitdir`
in place of the git process, say), it must give exactly `git worktree list --porcelain`'s set on every case you can
plant (a pruned or missing tree, a locked one, a detached one, a bare repository, a run clone per `_clone_trees`) and refuse
with the same fault where git would fail; otherwise leave the listing as it is and say what remains.

## Proving no decision changed (success-8, failure-4)
1. **Before you change anything**, write a corpus script under the sandbox's own `$TMPDIR` that runs every call of W2-42a's
   parser corpus (`tests/unit/guard/test_w2_42a_*.py`: the commands and their expected answers) and the five rules' cases
   (the guard's unit suites `tests/unit/guard/` and W1-02's acceptance suites: the calls they decide) through the product
   guard's decision function (`policy_refusal` in `reads.py`, and the decision entry the hook uses), with roles
   engineer, independent-test-designer, independent-auditor and none, on a planted repository with 150 or more trees and a
   planted hidden folder (the evaluation-sets keys of the path map; your planted repository only). Record each call's
   decision (allow, or refused with its reason) to a file under `$TMPDIR`. Record its size (calls, refusals).
2. After the change, run it again and diff: **no call differs**, reasons included. Put the counts and the diff's result in
   your return, and keep the script's corpus as a unit case in `tests/unit/guard/test_w2_111_*` where it can run without
   the real project (the before decisions as its expected answers, written from the before run).
3. The guard's rule suites pass unchanged: `tests/unit/guard/` whole, and W1-02's and W1-05's acceptance folders, before
   and after (counts in your return).

## Timing (what the test designer's cases will judge; you never read them)
Measure your own before/after with W1-02's method on the product hook: per call, the CPU time (user and system) of the hook
process and its children (`RUSAGE_CHILDREN`), less the median CPU time of a reference hook (a fresh interpreter that reads
the event and answers allow) timed beside it; nearest-rank p95 over 40 calls; bound 100 ms. Report before and after for:
Bash plain (`ls`), a pipe (`ls | wc -l`), a redirect (`echo x > <tree>/out.txt`), each with role engineer; and Read,
Write, Bash with 150+ planted trees; with the session's own inherited PATH (its entry count recorded) and the load
(`os.getloadavg()`) at each run. Never shorten PATH or the tree count to make a figure.

## Running tests
Every pytest through the heavy slot, `TMPDIR` the sandbox's own `$TMPDIR` (the empty home folder exists; do not create it):
`env HOME=/home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-111/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(a resource gate's refusal is a wait). A timing red that passes alone at a quiet moment is named as such, never retried
into green.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it). Commit in batches as you go.
```
git commit -m "W2-111 (DAEO-qvff): <what the batch does>" --trailer "Task: DAEO-qvff" --trailer "Role: engineer" --trailer "Implements: DEC-1184, DEC-979, DEC-906" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>
```

## Rules
- Write files with the Write and Edit tools and absolute paths. Anything longer than one line goes in a script under the
  sandbox's own `$TMPDIR`, never a new folder under `.gov-runtime/scratch/`.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- Never open the evaluation sets' root or any hidden or memory-verdict folder of the real project; never secrets.
- No merge, no push. No new ticket; a gap comes back in `unresolved` as a question with options.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: your commits (12-digit hash, subject); the shape you chose for the trees and why; the corpus run (calls,
refusals, before vs after: differences, which must be none); the suites' counts before and after; the timing table
(before / after per call kind: p95 less reference, reference median, raw CPU p95, load, PATH entries, tree count); and
**for the live-hook ACT**: the functions and line ranges in `src/gov/guard/install.py` and `src/gov/guard/reads.py`
that changed, and the matching functions in `.claude/hooks/pretooluse.py` (read-only; by name and line) that the ACT
must change the same way.

## The ticket's context packet (gov context DAEO-qvff --role engineer)
```json
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
    },
    {
      "id": "1129e803d25e1e7e645c0f1b",
      "path": "governance/project/orchestration/closes/W2-49-DAEO-ha8z.md",
      "text": "- Reds caused by the change: none; flaky candidates: tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_clean_store_is_decided_green, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check, tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here, tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched, tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer], tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95\n",
      "tokens": 433
    },
    {
      "id": "67e8b68792add67700151f81",
      "path": "governance/project/orchestration/closes/W2-67-DAEO-9nys.md",
      "text": "- Reds caused by the change: none; flaky candidates: tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_clean_store_is_decided_green, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check, tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here, tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched, tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer], tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95\n",
      "tokens": 433
    },
    {
      "id": "dcba5b618746edffd644189c",
      "path": "governance/project/orchestration/closes/W2-76-DAEO-tgk2.md",
      "text": "- Reds caused by the change: none; flaky candidates: tests/acceptance/W1-35/test_w1_35.py, tests/acceptance/W1-35/test_w1_35_orchestration.py, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_clean_store_is_decided_green, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it, tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check, tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here, tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched, tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role], tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer], tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95\n",
      "tokens": 433
    }
  ],
  "supplementary_query": "The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the hook, not the machine's load (P-LATENCY-1)\nEach of the 15 hook-latency cases (11 in DEC-979's count; 15 node ids with their parameters, the CTO, DEC-1157 (12)) (W1-02's `test_decision_p95_is_under_100_ms` in its parameters, W1-05's `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57's `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook's own work: the CPU time (user and system) of the hook's process and its children over each call, or the call's wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped Verify: a read of the 11 revised cases (collect-only on the three files names 11 ids) finds in each a CPU-time measure of the hook's process and its children, or a wall time compared with a quiet reference measured in the same run, with the bound still 100 ms at p95; `git diff` against the unrevised files shows no raised bound and no `skip`, `xfail` or removed id. [DEC-979 item 1 D2, DEC-906, DEC-968]\nUnder load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded), each case's verdict is the same at both, with the measured figures in each README Verify: each revised case is run on a quiet machine and at a load of about 20 and at 50 or more (the CTO's benchmark load, recorded): the 15 verdicts are the same at all three, and each README holds the measured figures. [DEC-979, DEC-968]\nThey still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads Verify: a planted hook that does 150 ms of its own work per call is put in place of the hook: each revised case fails at both loads. [DEC-906]\nWhat each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` Verify: each of the three READMEs states what its case measures and why wall time under load is not the measure, and its commit carries the trailer `Rewrite-Reason: DEC-979`: grep of the READMEs and `git log` finds both. [DEC-906]\nA Bash call is decided within the 100 ms bound at p95 by the hook's own work (the CPU time of the hook's process and its children, W2-111's method), for a plain command, a pipe and a redirect, with a role set Verify: the new Bash cases under `tests/acceptance/W2-111/` run against the product hook pass at the bound, quiet and at a load of about 20; before the change they fail (the measure of 2026-11-14 gave 103-167 ms; evidence `~/gov-os-runs/W2-111/q-scan-2/`). [DEC-1184 (3)]\nA call is decided within the bound with 150 or more worktrees registered Verify: a case that registers 150 or more planted worktrees on a planted repository and times Read, Write and Bash calls with a role set: p95 within 100 ms of the hook's own work. [DEC-1184 (3)]\nThe install check reads PATH once per session, not on every call; a changed PATH is read again Verify: a unit case counts PATH lookups over 20 calls of one session (one lookup), then changes PATH (one more); `has_install`'s answers are the same as before for the same commands. [DEC-1184 (3)]\nA call is judged only against the trees its target lies in, and every decision is the same as before Verify: the guard's rule suites pass unchanged, and the same corpus of calls (W2-42a's parser corpus and the five rules' cases) gives the same allow or refuse decision before and after, with the per-tree judge called only for trees holding the call's targets. [DEC-1184 (3)]\nThe 100 ms bound raised, a case removed, skipped or marked flaky. Verify: diff of the revised files against the unrevised: the bound is the same 100 ms, the 15 ids are all present, and grep for `skip`, `xfail` and `flaky` marks finds none added.\nA case that passes a hook doing more than 100 ms of its own work. Verify: the planted 150 ms hook run against each revised case: none passes.\nA case whose verdict still changes with the machine's load. Verify: each case run quiet and at load 20 and at 50 or more: no case changes its verdict between runs.\nA decision changed by the speed-up: a refusal turned into an allow, or an allow into a refusal. Verify: the decision corpus run before and after: no decision differs.\nA Bash or many-tree case that still passes a hook doing 150 ms of its own work. Verify: the planted 150 ms hook against each new case: none passes.",
  "further_batch": [
    {
      "id": "a9e493ebd2b6e5feaf5f6c9f",
      "path": "governance/project/orchestration/closes/W2-84-DAEO-m1u3.md"
    },
    {
      "id": "65b54f504c13ddf5a1d6b67e",
      "path": "governance/project/orchestration/closes/W2-95-DAEO-57hm.md"
    },
    {
      "id": "3286c682fdf76639d4230ce9",
      "path": "governance/project/orchestration/closes/W2-115-DAEO-emq1.md"
    },
    {
      "id": "d50daa7b5ff8c6114807a5db",
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md"
    },
    {
      "id": "9f4b1dffba160d8be54d1c89",
      "path": "governance/project/orchestration/packages/CAPACITY-1.md"
    },
    {
      "id": "8f22085ddc936454a3b27444",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md"
    },
    {
      "id": "377e6a0a2ed83fe410f01b69",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md"
    },
    {
      "id": "4ad05cc5a4d48a45e92f8411",
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md"
    },
    {
      "id": "DEC-757",
      "path": "docs/DECISION_REGISTER.md"
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
        }
      ],
      "limit": 10
    },
    {
      "items": [
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
          "id": "3286c682fdf76639d4230ce9",
          "path": "governance/project/orchestration/closes/W2-115-DAEO-emq1.md"
        },
        {
          "id": "d50daa7b5ff8c6114807a5db",
          "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md"
        },
        {
          "id": "9f4b1dffba160d8be54d1c89",
          "path": "governance/project/orchestration/packages/CAPACITY-1.md"
        },
        {
          "id": "8f22085ddc936454a3b27444",
          "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md"
        },
        {
          "id": "377e6a0a2ed83fe410f01b69",
          "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md"
        },
        {
          "id": "4ad05cc5a4d48a45e92f8411",
          "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md"
        },
        {
          "id": "DEC-757",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "3286c682fdf76639d4230ce9",
      "reason": "budget exceeded"
    },
    {
      "id": "377e6a0a2ed83fe410f01b69",
      "reason": "budget exceeded"
    },
    {
      "id": "4ad05cc5a4d48a45e92f8411",
      "reason": "budget exceeded"
    },
    {
      "id": "65b54f504c13ddf5a1d6b67e",
      "reason": "budget exceeded"
    },
    {
      "id": "8f22085ddc936454a3b27444",
      "reason": "budget exceeded"
    },
    {
      "id": "9f4b1dffba160d8be54d1c89",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-757",
      "reason": "budget exceeded"
    },
    {
      "id": "a9e493ebd2b6e5feaf5f6c9f",
      "reason": "budget exceeded"
    },
    {
      "id": "d50daa7b5ff8c6114807a5db",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-qvff): 6 paths, 117 chunks; 6 by role_paths.engineer.reads_denied {ticket_tests} (the ticket's cases revised in other folders) (DEC-1065 (2))"
    }
  ],
  "tokens": 19833,
  "budget": {
    "limit": 20000,
    "used": 19833
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
  "hash": "0529af535237eb0b5238ce0258d2786a134fe0db9510c2598a25f9809bf9078d"
}
```
