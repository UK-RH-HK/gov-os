# ACT-SETS-GLOBS-1: the rehearsal record (DEC-1057)

`rehearsal.log` beside this file is the clean run (run 6): the four globs and the listing-only walk. Every step ran in
order, from a fresh `env -i` shell, 22:34–22:51 GMT 2026-11-09, with **0 failures**. Nothing live was changed. Runs 4
and 5 (clean with three and four globs, the earlier pruned walk) are kept in `old-logs/`.

## Why run 6
The CTO's `apply.sh check` on the live tree (`328d40f5`, normal working load) stopped, as designed:
`size (live globs, 7): 4560 hidden files, walked in 9 ms; size (candidate globs, 11): 4560 hidden files, walked in
3179 ms; over the limit`. The check had timed the judge's own walk, a recursive walk of the real `runs/` and
`fixtures/`. The candidate hook's walk then still listed every run folder's entries. Run 6's hook (`74f8dbea4761`)
changes the walk:
- it lists only `fixtures/evaluation/*` and `runs/*`;
- it stats `hidden`, `miss-classes.json` and `misses.jsonl` directly;
- it walks only the matched `hidden/` folders, each once;
- listings are cached per hook run.

`apply.sh`'s size check now times the walk each hook really does: the judge's for the live globs and `Narrow` for the
candidate globs, each the median of 5.

## Setup
- A `--no-hardlinks` clone of the main tree at its head, with a worktree. The clone's `core.hooksPath` pointed at an
  empty folder.
- A planted HOME with a dummy sets root, holding the four destinations and their open neighbours.
- Every hook run logged into `$BASE/calls` (30,027 lines); the live call log got 0 lines.
- The real sets root was never opened; only its own stat line was taken.

## The clean run (run 6)
| Step | Result |
|---|---|
| `narrow_check.py` | `Narrow`'s file lists equal the judge's on 139 trees, the planted root and a synthetic tree (links to folders and to files, broken links, a run folder that is a link, a `hidden/` that is a link, `.git`, folders named like the files). `match` equal on 3,754 paths × 139 parts. Over the trees: 818 → 19 ms |
| `scale_check.py` (synthetic root: 138,962 files, 9,362 hidden; median of 10; load average 3.4 / 7.0 / 10.5) | the judge, live globs 13.2 ms; the judge, candidate globs 6,782 ms; **`Narrow`, candidate globs 30.1 ms**; the same files |
| `sets_globs_check.py` before / after | 573, 0 failed (the gap) / 573, 0 failed |
| The map alone with the live hook | 42 answers wrong (34 open forms refused, 8 line-rule forms allowed) |
| `walls_check.py repo` before / after | 331, 0 failed / 331, 0 failed |
| `guard4_check.py --settings` before / after | 501, 0 failed / 501, 0 failed |
| Suites before / after | `test_guard_fix_4` 467 / 467; `test_g14` 150 passed, 1 skipped, 1 failed / the same (fails at this head without the ACT); live hook, reads 85 / 85; W2-149 128 passed, 3 skipped / the same |
| `deliver_check.py` before / after | 6 files delivered (writer, checker, auditor, plus the auditor's `misses.jsonl`): open before; refused after, the script's own line allowed (55 / 55 checks) |
| `apply.sh` | check, apply, a second apply refused, check: already applied; the commit (two files, the trailers); undo byte for byte |
| Replay, 48 hours, 12,417 unique calls | **0 changed** (12,338 allow, 79 deny); 77 name the new globs |
| Latency per tool call, 20 rounds × 6 calls | median 128.0 → 137.3 ms (noise); `git grep … HEAD` 591 → 217 ms |
| Live files | **unchanged** |

`apply.sh check` on the live main tree (`cf23e9f8d`, the size check on the planted root): "check: ready to apply".
Against the synthetic scale root: live 9,050 files in 14 ms, `Narrow` 9,362 files in 31 ms (median of 5). It stops on
the count, because the synthetic root holds more than 8,000 hidden files; the real root holds 4,560.

## What the earlier runs found (`old-logs/`)
1. Runs 1–2: the harness's location rule, and the W2-149 guard-line cases' root. One replayed call was refused at the
   20-second deadline because of the judge's walk over 135 trees. Fix: the pruned walk.
2. Run 3: a revision's listing took 11.7 s on pattern matches across parts. Fix: the match kept per path behind a
   prefix filter. A masked compare exit code was also fixed.
3. Runs 4–5: clean with three, then four globs.
4. The live check: the 3.2 s walk on the real root. Fix: run 6's listing-only walk, and a size check that times the
   hook's own walk.

## Limits
The size check meets the real sets root at the operator's `check` (counts and timings only). The synthetic scale root
stands in for its timing.
