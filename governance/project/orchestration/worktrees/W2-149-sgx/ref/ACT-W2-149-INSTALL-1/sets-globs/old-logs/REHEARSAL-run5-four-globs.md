# ACT-SETS-GLOBS-1: the rehearsal record (DEC-1057)

`rehearsal.log` beside this file is the clean run with the four globs (run 5): every step in order, from a fresh
`env -i` shell, 22:08–22:27 GMT 2026-11-09, **0 failures**. Nothing live was changed. Run 4, clean with the first three
globs, is kept in `old-logs/` (`rehearsal-run4-three-globs.log`, `REHEARSAL-run4-three-globs.md`).

## Setup
- A `--no-hardlinks` clone of the main tree at its head, with a worktree. The clone's `core.hooksPath` pointed at an
  empty folder, so no live git hook ran.
- A planted HOME with a dummy sets root: the earlier rehearsals' layout plus the launch script's four destinations
  (`memory-verdict-4/hidden/`, `memory-verdict-4/XCHECK-r1.md`, `runs/audit-sg/miss-classes.json`,
  `runs/audit-sg/misses.jsonl`) and their open neighbours. Every file holds a `DUMMY MARK-OUTSIDE-nn` line.
- Every hook run logged into `$BASE/calls` (`GOV_GUARD_CALLS_DIR`): 29,183 lines. The live call log got 0 lines
  from the rehearsal's checks.
- The real sets root was never opened. Only its own stat line was taken, before and after.

## The clean run (run 5)
| Step | Result |
|---|---|
| `narrow_check.py`: `Narrow` against the judge's `_Part` | file lists equal on 138 trees, the planted root and a synthetic tree (links, `.git`, deep and look-alike names), live and map globs. `match` equal on 3,733 paths × 138 parts. Map globs: walk 1,042 → 26 ms, match 16,072 → 44 ms |
| `sets_globs_check.py`, before (the gap; HOME planted) | **573 run, 0 failed**: every N and L case allowed before |
| The candidate map with the live hook (why the hook changes) | 42 of 573 answers wrong. **34 O cases refused** (a Bash line naming the root and an open file). 8 L cases allowed (`--file zz/hidden/q01.yaml`, `--name 'misses.jsonl'` with the root) |
| `walls_check.py repo <clone>`, before / after | 331 run, 0 failed / 331 run, 0 failed |
| `guard4_check.py --settings <clone>` (root planted), before / after | 501 run, 0 failed / 501 run, 0 failed |
| Suites before / after | `test_guard_fix_4` 467 / 467 passed; `test_g14` 150 passed, 1 skipped, 1 failed / the same (`test_w2_91_tests_today`, a check of today's tree that fails at this head without the ACT); live hook and reads 85 / 85 |
| W2-149's suites (unit and acceptance, root `~`), before / after | 128 passed, 3 skipped (live) / the same |
| `deliver_check.py` before | the real launch script delivered a writer (a new set's `hidden/`), a checker (`XCHECK-r1.md`) and an auditor (`runs/audit-1/miss-classes.json`, its wall seeded from `runs/audit-1/misses.jsonl`): 6 files with the misses. The hook before: **every one open** to the CTO, a lead and an engineer (55 checks) |
| `apply.sh` check, apply, a second apply, check | ready (size: 7 → 11 hidden files, 1 ms); applied; refused; already applied. The applied map loads (`load_config`, `check_sets`); 11 globs, 6 roles |
| `deliver_check.py` after | the same deliveries under the **applied** map (stage 15 counts by the new globs): delivered. The hook after: each of the 6 files refused to Read, Bash `cat` and Grep, the launch script's own line allowed (55 checks, 0 failed) |
| `sets_globs_check.py`, after (HOME planted; the clone and its worktree) | **573 run, 0 failed** |
| Replay, 48 hours (2026-11-07T22:08:11 .. 11-09T22:08:11 UTC), 11,995 unique calls | before → after **0 changed** (11,918 allow, 77 deny); 72 calls name the new globs, none changed |
| Latency, 20 rounds × 6 calls, real HOME (138 trees; the machine loaded) | median 167.2 → 151.9 ms per call (noise). `git grep -l x HEAD -- '*.yaml' '*.json'` 767 → 292 ms |
| The operator's commit (in the clone) | exactly `M .claude/hooks/pretooluse.py`, `M governance/project/path-map.yaml`; trailers `Task: DAEO-sdxk`, `Implements: DEC-1101, DEC-1112`, `Role: owner` |
| `apply.sh undo` | the hook and the map byte for byte as before the ACT's commit; check: ready to apply again |
| Live files: the hook and its two modules, the map, `held-out.yaml`, the settings, `indep_launch.py`, the walls' template, `guard4_check.py`, `walls_check.py`, `~/.claude/settings.json`, `~/gov-os-operator` but `log/` and `queue/`, the real sets root's entry | **unchanged** |

`apply.sh check` on the live main tree (head `27aaab381`, with `--sets-root` set to the planted root, so only the
hashes are live): "check: ready to apply".

## What the earlier runs found (`old-logs/`, fixed before the clean runs)
1. **Runs 1 to 2 (map plus key change only):**
   - The W2-149 harness refused a world under `~/gov-os-runs` ("a real location"), so the deliver check now runs
     under `/tmp`.
   - W2-149's guard-line cases need the block's root as `~/gov-os-eval`, so they now run in the deliver phase.
   - The replay changed **one call**: a CTO subagent's `git grep … HEAD -- '*.yaml'` went allow → deny on the 20-second
     deadline. The cause was the judge's walk from `fixtures/evaluation` and `runs` in 135 trees. **Fix:** `Narrow`'s
     pruned walk.
2. **Run 3 (with the walk):** the same call again. `git grep … HEAD` took **11.7 s**: a revision's listing asks each
   tree's part about each name, and the new globs are patterns, not prefixes. **Fix:** `Narrow.match`, the judge's own
   answer kept per path across parts with the same globs, behind an exact prefix filter. The compare's exit code had
   also been hidden by `tee`; the step now reads it directly.
3. **Run 4:** clean with the three globs (11,885 calls, 0 changed). Then the CTO added `runs/*/misses.jsonl`. Run 5 is
   the same steps with it: the cases were extended (misses moved from open to refused, open neighbours `report.md`,
   `misses.jsonl.bak` and deeper names added) and the deliver check now checks the auditor's input file.

## Limits
- The size check meets the real sets root for the first time at the operator's `check` (counts and ms only).
- The L, S and O cases name paths that do not exist; the R cases need the planted root. On the live tree after the
  ACT, the CTO runs `sets_globs_check.py <main tree>` with the real HOME (its non-R cases).
