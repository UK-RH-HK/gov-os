# W2-141 — the review of the staged hook rebuilt on ACT-SETS-GLOBS-1's hook (DAEO-xwro; one round, READY by verdict.py)

You are a fresh, read-only independent reviewer. **Narrow scope: one point.** DECIDED-NOT-DONE row 78 (the CTO's
delegated decision, DEC-1112 (3)): W2-141's staged guard change, `docs/changes/W2-141-hook/pretooluse.py`, was built on
an older live hook. It is now rebuilt on today's live hook `.claude/hooks/pretooluse.py` (sha256 `74f8dbea4761…`,
ACT-SETS-GLOBS-1, commit `9cce7430d`). The rebuild must keep **both** ACT-SETS-GLOBS-1's `sets_line_keys` and
`Narrow` (and every other live rule: 2b, 2c, 2d, the call log) **and** W2-141's search rule. W2-141 itself (the
`role_reads.py` copy, `src/gov/guard/reads.py`, its tests) was reviewed READY in its own rounds and merged (`b1e2c3b9`);
it is not re-opened, except where the new base changes what it does. The staged pair goes live only through the lift's
re-pin ACT, by the owner's operator; nothing live changes here. READY is computed by `verdict.py` from your block.

## What to review
- **The commit:** `beec1f2f8` on `w2/integrate`, in your worktree (`git show beec1f2f8`): `docs/changes/W2-141-hook/pretooluse.py`
  and its `README.md`. The old staged copy is `beec1f2f8~1:docs/changes/W2-141-hook/pretooluse.py`.
- **The hooks' history:** `git log --format='%h %s' -- .claude/hooks/pretooluse.py`. The old staged copy was made from
  `bd545af83198` (`15952bbfa`, ACT-GUARD-SETS-1), not from `97a84e770058` as the row first said; since then the live
  hook took ACT-INDEP-WALLS-1 (`147706ae4`), ACT-GUARD-CALLLOG-1 (`b7a373cf9`), ACT-OPERATOR-1 (`2a6462653`) and
  ACT-SETS-GLOBS-1 (`9cce7430d`). `role_reads.py`'s live file last changed in `e02d55e40` (`5407aade9417`).
- **ACT-SETS-GLOBS-1** (the package and its hook diff `97a84e770058` → `74f8dbea4761`): `ACT-SETS-GLOBS-1.md` and
  `pretooluse.diff` in `.gov-runtime/scratch/ref/W2-141-rebase/`.
- **The CTO's runs** (copied into your worktree under `.gov-runtime/scratch/ref/W2-141-rebase/`):
  - `unit.log`, `accept.log`: `tests/unit/guard/test_w2_141_search.py` (pins the staged copy's diff against the live
    hook) and `gov accept W2-141` (the declared way, the pinned judge), at the main tree with the rebuilt copy.
  - `rehearse.sh`, `rehearsal.log` and `out/`: a `--no-hardlinks` clone at `w2/integrate`'s head with a planted HOME
    and sets root; "before" is the live hook, "after" is the clone with the staged pair copied over `.claude/hooks/`.
    Steps: `sets_globs_check.py`, `walls_check.py repo`, `guard4_check.py --settings`, the guard suites
    (`test_guard_fix_4`, `test_g14`, `test_live_hook` + `test_reads`), latency, and a 48-hour replay of the real calls
    judged under DAEO-sdxk and again under DAEO-xwro (W2-141's own ticket, so its search rule is exercised).
    **Results:** unit 204 passed; `gov accept W2-141` 184 passed, 0 failed, 0 skipped. Rehearsal (`failures: 0`): `sets_globs_check.py` 573 run, 0 failed before and after; `walls_check.py repo` 331/0 before and after; `guard4_check.py --settings` 501/0 before and after; `test_guard_fix_4` 467/467 both; `test_live_hook` + `test_reads` 85/85 both; `test_g14` (the G-14 ACT's draft suite, `drafts/g14/test_g14.py`, copied as `test_g14.py`) before 1 failed (`test_w2_91_tests_today`, red at this head without any change, as in ACT-SETS-GLOBS-1's rehearsal), after 5 failed: that one plus four `test_near_misses_pass` engineer cases (a search from above: `grep -rn x tests/acceptance`, `Glob tests/acceptance/**`, `Grep` of the tree root, `grep -r foo tests/`) which the CTO reads as S1/S2's intended refusals (judge that). Replay, 48 h, 14,569 unique calls: under DAEO-sdxk 0 changed (14,483 allow, 86 deny); under DAEO-xwro 29 allow->deny (engineer Grep 23, Bash 6; every reason "the search can reach tests/acceptance/W2-141/"), 0 deny->allow (`out/compare-after-xwro.txt`). Latency median 147.3 -> 168.0 ms under a load of 13-16 on 20 CPUs. Live files unchanged; 0 lines in the live call log.

## Check (each a KPI line of your verdict block)
- **R1 the rebuild is exact:** the staged `pretooluse.py` equals the live `.claude/hooks/pretooluse.py` at `beec1f2f8`
  with one change, `"Glob"` added to G-14's tool list; and the old staged copy's only change against its own base
  `bd545af83198` (`git show 15952bbfa:.claude/hooks/pretooluse.py`) was that same word, so nothing of W2-141 is lost.
  Compute the hashes and diffs yourself.
- **R2 both changes hold together:** read the live hook's `main()` path for a Glob call: with `"Glob"` added, a Glob
  reaches `role_reads.refusal` after rule 2b (the judge with `Narrow`, the line rule's `sets_line_keys`), 2c and 2d.
  Does adding Glob to G-14 change anything for ACT-SETS-GLOBS-1's cases, or does `Narrow`, the call log or rules 2c/2d
  change what the staged `role_reads.py` receives (`seen`, `tree_roots`, `_expand_token`, the roles, the ticket)?
  Can any path now fail open, or deny a Glob it should allow, that the old base did not?
- **R3 the evidence is real and says what it claims:** the logs above are runs of these files; the before/after
  counts match; the replay's differences are only W2-141's intended refusals (an engineer's search, Grep, Glob or Bash,
  that can reach its own ticket's acceptance folder without excluding it), each named; anything else is a finding.
  Say where the rehearsal differs from what the operator's ACT will do.
- **R4 the README:** the table's "made from" hashes, the rebuild note and the rollback commit are right for the
  rebuilt pair; following its rollback restores the live files byte for byte.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns the rebuild above.

## Write and return
- **You write nothing** in any tree. You may run the tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<your worktree>/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local` so pytest is found),
  e.g. `tests/unit/guard/test_w2_141_search.py`, and run the staged hook on planted event JSON in your temporary folder.
  Never run anything against the real `~/gov-os-eval/`, `~/gov-os-runs/`, `~/.claude/` or a real `claude` session. No
  GPU, no network. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything under
  `~/gov-os-eval/` or any `hidden` folder.
- **Code questions:** read the code with grep and the Read tool, in small targeted reads (DEC-859).
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (task,
  status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), your answer to R1-R4, every finding with its two lines and
  scope (ids F1, F2, …), and at the end one fenced block opened with three backticks and the word `verdict`:
  `{"staged_pretooluse_sha256": "<the sha256 you computed>", "kpis": [{"kpi": "R1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "R4"]}`.
Refused twice for the same call: stop and say so; no third try.
