# ACT-OPERATOR-1: the rehearsal record (DEC-1057)

Two clean runs, 2026-11-09, from a fresh `env -i` shell, each in a `--no-hardlinks` clone of the main tree at its head
(`b7a373cf9`), with a worktree, a planted HOME (`~/gov-os-runs/OPERATOR1-rehearsal-<kind>/home`: the owner's operator
files planted in `gov-os-operator/`, a dummy sets root), a crontab stub seeded with the live table, and the clone's
`core.hooksPath` pointed at a safe copy of the git hook (its operator paths planted, its two live-path lines dropped).
`apply.sh` ran from the clone with `HOME` planted and the rehearsal's settings.

- **pre** (`rehearsal-pre.log`, 18:03–18:31 GMT): the clone's hook set to the pre-calllog hook `d5be03dbb48e`.
  **failures: 0.**
- **post** (`rehearsal-post.log`, 18:03–18:28 GMT): the clone's hook the post-calllog hook `a7981319f877` (live since
  the owner's operator applied ACT-GUARD-CALLLOG-1 at 18:13, `b7a373cf9`); every hook run logged into
  `$BASE/calls` (`GOV_GUARD_CALLS_DIR`). **failures: 0.**

| Step | pre | post |
|---|---|---|
| `test_guard_fix_4` before / after | 467 / 467 passed | 467 / 467 |
| `test_g14` before / after | 150 passed, 1 skipped, 1 failed / the same | the same |
| live hook, reads (W2 units) before / after | 85 / 85 passed | 85 / 85 |
| `guard4_check.py --settings <clone>` (root planted) | 501 run, 0 failed / 0 failed | the same |
| `walls_check.py repo <clone>` (HOME planted) | 331, 0 failed / 331, 0 failed | the same |
| rule 2d's cases (`op_cases.py`, HOME planted) before: the gap | 403: every R case allowed (243), A 144, L 16 | the same |
| rule 2d's cases after | 412, 0 failed: R 252 refused by 2d, A 144 and L 16 allowed | the same |
| W2-148 acceptance before / after | 169 / 169 passed | (pre only) |
| `tests/unit/operator` before / after | 184 / 202 passed (+18 new) | (pre only) |
| the merge queue's units before / after | 97 / 97 passed | (pre only) |
| `test_landing_select.sh` before / after | 49 ok / 54 ok (+5 new), 0 failures | (pre only) |
| `apply.sh` check, apply, a second apply, check | ready; applied; refused; already applied | the same |
| the operator's commit | 4 M, 2 A, trailers as the message | the same |
| replay, real calls of the last 48 hours | 7,898 unique: **0 changed** (7,861 allow, 37 deny) | 7,897: **0 changed** |
| the CTO's session (haiku, orchestrator on DAEO-sdxk, real) | 5 calls: Write and Bash into `install/` and Bash into `guard-calls` refused by 2d; the queue write and a Read of `install/brief.md` allowed; nothing written but the queue file | the same |
| the (a) ACT replayed (ACT-RERANK-GPU-SLOTS-1, its module at `d03ce368b`): queued, launched as the cron runs it (`python3 -I`, `env -i`, no config) | canary then the walled session (real `claude --restricted`, 19 s, about $0.02); G1–G9, recompute, apply, the check (count 1), after-check: **applied**, votes a/a/a, logged, pushed; the owner's undo line: **undone**, both files gone | (pre only) |
| a (b) ACT (SELECT-FIXES-1's kind: one record_only path) | no yes: **refused at G6**, HEAD unchanged; `yes ACT-SELECT-FIXES-1R 546f2e6c` planted, queued again: **applied**, committed with `Role: operator`, `Act:`, `Act-sha:`, `Class: b`, `Review:`, `Approved-by:` through the freeze gate; the freeze removed by its run; the owner's undo line: **undone** (an undo commit) | (pre only) |
| the commit path while a freeze holds | the CTO on the ACT's path: refused; on `.claude/settings.json`: refused; on another path: committed; the freeze gone: committed | (pre only) |
| the owner's operator files in the planted root | unchanged; entries `.claude CLAUDE.md acts hooks install log queue wall` | — |
| `apply.sh undo` | every part as before the ACT's commit; the git hook and the landing tool as live; the crontab as before; `queue/`'s record kept; **check: ready to apply again** | the same |
| live files (the hook and modules, the map, the settings, the git hook, the operator code, the landing tool, `~/.claude/settings.json`, `~/gov-os-operator` but its logs, the live crontab) | **unchanged** | **unchanged** |

Notes:
- `test_g14`'s one failure (`test_w2_91_tests_today`, a check of today's tree) fails at this head without the ACT, the
  same before and after.
- Earlier runs (`old-logs/`): run 1 found guard4's 5 failures (a thin planted sets root) and undo's false failure
  with `queue/` kept (review F1, F2): both fixed. Run 2 was stopped by its own guard when the live
  `~/.gov-os/guard-calls` appeared: the owner's operator had applied ACT-GUARD-CALLLOG-1 live at 18:13; the guard
  now applies only while the live hook is pre-calllog, and each kind sets its own hook in its clone.
- The CTO session's real calls ran with the real HOME (sign-in), so the clone's `write_refused` roots were set to the
  planted absolute paths for that step and set back after.
