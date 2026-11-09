# ACT-SETS-GLOBS-1: the rehearsal record (DEC-1057)

`rehearsal.log` beside this file is the clean run (run 4): every step in order, from a fresh `env -i` shell,
21:48–22:04 GMT 2026-11-09, **0 failures**. Nothing live was changed.

## Setup
- A `--no-hardlinks` clone of the main tree at its head, with a worktree. The clone's `core.hooksPath` pointed at an
  empty folder, so no live git hook ran.
- A planted HOME with a dummy sets root: the earlier rehearsals' layout plus the launch script's three destinations
  (`memory-verdict-4/hidden/`, `memory-verdict-4/XCHECK-r1.md`, `runs/audit-sg/miss-classes.json`, and their open
  neighbours). Every file holds a `DUMMY MARK-OUTSIDE-nn` line.
- Every hook run logged into `$BASE/calls` (`GOV_GUARD_CALLS_DIR`): 28,651 lines. The live call log got 0 lines
  from the rehearsal's checks.
- The real sets root was never opened. Only its own stat line was taken, before and after.

## The clean run
| Step | Result |
|---|---|
| `narrow_check.py`: `Narrow` against the judge's `_Part` | file lists equal on 135 trees, the planted root and a synthetic tree (links, `.git`, deep and look-alike names), live and map globs. `match` equal on 3,730 paths × 135 parts. Map globs: walk 768 → 19 ms, match 11,366 → 37 ms |
| `sets_globs_check.py`, before (the gap; HOME planted) | **473 run, 0 failed**: every N and L case allowed before |
| The candidate map with the live hook (why the hook changes) | 40 of 473 answers wrong. **34 O cases refused** (Bash lines naming the root and an open file: `runs/e0/counts.txt`, `ls <root>/runs`, a set's `visible/`, `README.md`, `XCHECK.md`, `misses.jsonl`). 6 L cases (`--file zz/hidden/q01.yaml` with the root) allowed |
| `walls_check.py repo <clone>`, before / after | 331 run, 0 failed / 331 run, 0 failed |
| `guard4_check.py --settings <clone>` (root planted), before / after | 501 run, 0 failed / 501 run, 0 failed |
| Suites before / after | `test_guard_fix_4` 467 / 467 passed; `test_g14` 150 passed, 1 skipped, 1 failed / the same (`test_w2_91_tests_today`, a check of today's tree that fails at this head without the ACT); live hook and reads 85 / 85 |
| W2-149's suites (unit and acceptance, root `~`), before / after | 128 passed, 3 skipped (live) / the same |
| `deliver_check.py` before | the real launch script delivered a writer (a new set's `hidden/`), a checker (`XCHECK-r1.md`) and an auditor (`runs/audit-1/miss-classes.json`): 5 files. The hook before: **every one open** to the CTO, a lead and an engineer (48 checks) |
| `apply.sh` check, apply, a second apply, check | ready (size: 7 → 10 hidden files, 1 ms); applied; refused; already applied. The applied map loads (`load_config`, `check_sets`); 10 globs, 6 roles |
| `deliver_check.py` after | the same three deliveries under the **applied** map (stage 15 counts by the new globs): delivered. The hook after: each file refused to Read, Bash `cat` and Grep, the launch script's own line allowed (48 checks, 0 failed) |
| `sets_globs_check.py`, after (HOME planted; the clone and its worktree) | **473 run, 0 failed** |
| Replay, 48 hours (2026-11-07T21:48:09 .. 11-09T21:48:09 UTC), 11,885 unique calls | before → after **0 changed** (11,808 allow, 77 deny); 65 calls name the new globs, none changed |
| Latency, 20 rounds × 6 calls, real HOME (135 trees) | median 133.3 → 136.4 ms per call (noise). `git grep -l x HEAD -- '*.yaml' '*.json'` 604 → 212 ms |
| The operator's commit (in the clone) | exactly `M .claude/hooks/pretooluse.py`, `M governance/project/path-map.yaml`; trailers `Task: DAEO-sdxk`, `Implements: DEC-1101, DEC-1112`, `Role: owner` |
| `apply.sh undo` | the hook and the map byte for byte as before the ACT's commit; check: ready to apply again |
| Live files: the hook and its two modules, the map, `held-out.yaml`, the settings, `indep_launch.py`, the walls' template, `guard4_check.py`, `walls_check.py`, `~/.claude/settings.json`, `~/gov-os-operator` but `log/` and `queue/`, the real sets root's entry | **unchanged** |

`apply.sh check` on the live main tree (head `260e70bd1`, with `--sets-root` set to the planted root, so only the
hashes are live): "check: ready to apply".

## What the earlier runs found (`old-logs/`, fixed before the clean run)
1. **Run 1 to 2 (map plus key change only):** the W2-149 harness refused a world under `~/gov-os-runs` ("a real
   location"), so the deliver check now runs under `/tmp`. W2-149's guard-line cases need the block's root as
   `~/gov-os-eval`, so they now run in the deliver phase. The replay changed **one call**: a CTO subagent's
   `git grep … HEAD -- '*.yaml'` went allow → deny on the guard's 20-second deadline. The cause was the judge's walk
   from `fixtures/evaluation` and `runs` in 135 trees, about 0.8 s on each call that asks whether a part holds files.
   **Fix:** `Narrow`, the pruned walk.
2. **Run 3 (with `Narrow`'s walk):** the same call again. Latency showed `git grep … HEAD` at **11.7 s**. A revision's
   listing asks each of the 135 tree parts whether each name matches, and the new globs are pattern matches, not
   prefixes. **Fix:** `Narrow.match`, the judge's own answer kept per path across parts with the same globs, behind
   an exact prefix filter. Run 3's compare result was also hidden behind `tee`; the step now reads the compare's own
   exit code.

## Limits
- The size check meets the real sets root for the first time at the operator's `check` (counts and ms only).
- The L, S and O cases name paths that do not exist. The R cases need the planted root. On the live tree after the
  ACT, the CTO runs `sets_globs_check.py <main tree>` with the real HOME (its non-R cases).
