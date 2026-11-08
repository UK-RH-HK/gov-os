# ACT-GUARD-SETS-1: the guard refuses the hidden sets outside the repository to the measured roles (DEC-1082 (3))

- **For:** the owner, to decide the four points in §5, then the owner's operator (a guard change: P-ACT-SPLIT).
- **By:** the CTO, 2026-11-06. A read-only design, built and rehearsed in a clone by an engineer, reviewed by the CTO.
- **Nothing live is changed** until the operator runs §3.
- **Rebuilt 2026-11-08 under DEC-1097 (2).** `apply.sh check` had stopped: the path map moved (W2-61h's
  `evaluation_families`, `cc8139a1c8f4` → `6d79946fdbbd`); the live hook had not (`e406653ef6c9`), and the new pin's
  guard code is byte for byte the old pin's. The rebuild adds the glob `runs/fresh-80/**` (the fresh 80's reader run and
  kept outputs, FRESH-80-1 §2 item 7) and deletes W2-84's hidden-half test cases with the ACT (DEC-1061 (4)). Rehearsed
  again end to end: 0 failures (§4). The 11-06 build is kept in `drafts/sets-root-guard/build-2026-11-06/`.
- **The line rule, 2026-11-08 (readiness review 5 F1; the CTO's option A, within DEC-1097 (2)/(3)).** A path the shell
  builds at run time passed the judge (`D=~/gov-os-eval; cat $D/runs/fresh-80/rows/q01.json`, `cd "$D"`, `grep -r`,
  `find`, `ls` with `$D`). The candidate hook now refuses, to the six refused roles, a Bash line that names the sets
  root and also names a hidden folder, or builds a path after it (§1 (2)). Rehearsed again end to end: 0 failures (§4).

## 1. The gap, and the fix
- **The gap:** the guard (`.claude/hooks/pretooluse.py`) builds its hidden-path checks only for the repository and
  its worktrees, so it never judges a path under the sets root `~/gov-os-eval`, for any role. The health check of
  11-06 showed it: an engineer's Read of `~/gov-os-eval/.../hidden/h01.yaml` was allowed.
- **The fix, two files, no pin change:**
  1. **A new block in the path map**, `sets_root_hidden`, read from the main tree's copy only, so a branch cannot
     weaken it. It names:
     - the root `~/gov-os-eval`;
     - the hidden globs: `memory-retrieval/hidden/**`, `memory-verdict/**`, `memory-verdict-2/**`,
       **`transcripts/**`** and **`runs/fresh-80/**`** (DEC-1097 (2): the 80's questions, gold answers, answers and kept
       outputs); every other folder under `runs/` stays open;
     - **the refused roles: orchestrator, engineer, research, product-spec, independent-test-designer and
       independent-auditor.**
  2. **The hook:**
     - those globs are refused under the sets root and in every tree, for reads and for the writes the guard can
       resolve;
     - one narrow override, so a listing that cannot reach the sets root is not refused for it (a `git diff | xargs`
       pipeline, the fresh-80 README's `proc.sh wait $(cat …/measure.pid)`);
     - **the line rule** (readiness review 5 F1): for the six refused roles, a Bash line that names the sets root (its
       real path, `~/…`, `$HOME/…`, an assignment's value included) is refused when it also (a) names a hidden folder as
       a path (`runs/fresh-80`, `memory-verdict-2`, …, whole names with a `/` beside them; the bare set name and
       `~/gov-os-runs/fresh-80` do not match), or its name as a quoted string; or (b) holds a command substitution, a
       `cd`/`-C`/`chdir` to the root, or, from the root's word on, a shell variable (`$!` and an unassigned `$HOME`
       aside), a glob or brace, or a `cd`. A plain `--sets-root ~/gov-os-eval` with variables only before it stays
       allowed: every command of `drafts/fresh80/README.md` is a case (A1–A23).
  3. **W2-84's hidden-half cases deleted** (DEC-1061 (4), DEC-1097 (2)): the six files under `tests/acceptance/W2-84/`
     listed in `tests/optin-lifted-guard.txt` under "Decision 4", and `tests/unit/guard/test_w2_84_trees.py` (all 13
     of its functions, 34 cases, test the old rule); their list lines go with them. Nothing else names them.
- **Not affected:**
  - **The measure:** its command names only the root, and its own code reads the files. `_measured` stays False for
    the orchestrator, checked.
  - **The fresh-80 scripts:** the CTO runs them with only `--sets-root ~/gov-os-eval` on the line; they derive
    `memory-verdict-2` and `runs/fresh-80` in their own code (the judge reads a command's words and inline code, never a
    script file's text). That line is allowed; one naming `runs/fresh-80/...` or `memory-verdict-2/...`, or carrying
    the root in a variable, a substitution, a glob or a `cd`, is refused, checked (F16–F23, V1–V25, A1–A23).
  - **Your writer, checker and operator:** they run outside the guard. A writer-like headless session read a
    planted hidden file, checked.
- **Two corrections to the CTO's first defaults, for you to approve (§5 (1)):**
  - **Six roles, not three.** The verdict sets also measure product-spec, the test designer and the auditor. With
    only three listed, those three could still read `memory-verdict-2/retired/` (old copies of the questions) and
    `XCHECK.md`.
  - **`transcripts/**` too.** It holds the writer's transcript of the hidden questions (ACT-D8). `runs/**` stays
    open: the CTO's results go there, with no question text.

## 2. The files (drafts, scratch; checked by hash before they apply; rebuilt 2026-11-08)
| File (`.gov-runtime/scratch/orchestrator/drafts/sets-root-guard/`) | sha256 (first 12) |
|---|---|
| `pretooluse.candidate.py`: the live hook (`e406653ef6c9`) plus the change and the line rule, nothing else | `bd545af83198` |
| `pretooluse.diff` (232 lines) | `b948e7ac831d` |
| `path-map.patch`: the map `6d79946fdbbd` → `a9d8b97267c4` | `8deead873070` |
| `optin-lifted-guard.patch`: the list `98f3b69a8ed9` → `868b6e1c8464` (W2-84's lines out) | `676014ab259d` |
| `guard4_check.candidate.py`: the 70 existing cases unchanged, 527 sets cases (11-06's 194, six of them now deny; F, V and A) | `ff5321041613` |
| `apply.sh`: `check`, `apply`, `undo` of the three files and the seven deletions, with backups and sha256s | `472bc1c1d226` |

The seven files `apply.sh` deletes, each checked by hash first: `tests/acceptance/W2-84/test_w2_84_code_under_test.py`
(`5c30ab77becb`), `test_w2_84_every_tree.py` (`0c6b02904b89`), `test_w2_84_fails_closed.py` (`ef6c3dcb0f3e`),
`test_w2_84_git_store.py` (`789d7f768267`), `test_w2_84_links.py` (`e268aba3aadd`), `test_w2_84_unchanged.py`
(`54ffe7787356`), and `tests/unit/guard/test_w2_84_trees.py` (`ac2dbd7398a6`).

`apply.sh check` and `apply` stop unless every file still hashes as built (`check` passed on the main tree at 11-08,
07:14, at `91cf43d98`). **If any of them changes before you apply (for example D-9's edits to
the map), the CTO rebuilds and re-runs the rehearsal first.**

## 3. The operator's steps (main tree, about 1 minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/drafts/sets-root-guard
bash $G/apply.sh check     # every file hashes as built (exit 0)
bash $G/apply.sh apply     # backups, then the hook, the map and the list, and the seven files deleted; sha256 before and after
git add .claude/hooks/pretooluse.py governance/project/path-map.yaml tests/optin-lifted-guard.txt
git rm -q -- tests/acceptance/W2-84/test_w2_84_code_under_test.py tests/acceptance/W2-84/test_w2_84_every_tree.py \
  tests/acceptance/W2-84/test_w2_84_fails_closed.py tests/acceptance/W2-84/test_w2_84_git_store.py \
  tests/acceptance/W2-84/test_w2_84_links.py tests/acceptance/W2-84/test_w2_84_unchanged.py \
  tests/unit/guard/test_w2_84_trees.py
git diff --cached --name-status    # expect 3 M and 7 D, nothing else
git commit -m "ACT-GUARD-SETS-1: the guard refuses the hidden sets outside the repository to the measured roles, the fresh 80's run folder included; W2-84's hidden-half cases deleted" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1082, DEC-1097, DEC-1061" --trailer "Role: owner"
```
`apply` prints the same `git add` and `git rm` lines at its end. **Then the CTO:** copies `guard4_check.candidate.py`
over `tools/guard4_check.py` and runs it on the live tree with no `SETS_PLANTED`. Expected: **453 run, PASS** (the 370
L cases of the rehearsal plus the 83 L cases that name `~` or `$HOME`, which run when the root is `~/gov-os-eval`); then
the live worktrees with measured roles get the merge the same day (DEC-1097 (2)). **Undo:** `bash $G/apply.sh undo`
restores the three files and the seven deleted files byte for byte (rehearsed), then a commit.

## 4. The rehearsal (DEC-1057): `REHEARSAL.md` and `rehearsal.log`, one clean run, 2026-11-08 07:04–07:13, 0 failures
Earlier runs are kept: 11-06's (194, 250 and 203 cases; 25 allow→deny) in `build-2026-11-06/`, and the rebuild's first
clean run without the line rule (01:19–01:29: 365, 409 and 310 cases; 9 allow→deny) in `REHEARSAL.md`. The run with the
line rule, in a `--no-hardlinks` clone at `91cf43d985c6` with a planted sets root (14 dummy files, the 80's run folder
included):

| Step | Result |
|---|---|
| R2 (HOME substituted, the block applied, the sets cases only) | **527 run, 0 failed** |
| R1 (the block's root planted; the 70 old cases and the sets cases) | **501 run, 0 failed** |
| The live-tree subset | **370 run, 0 failed** |
| The override switched off | exactly the 8 cases it exists for fail: X1, X2 (engineer, CTO) and A7, the README's `proc.sh wait $(cat …)` (CTO, lead) |
| `test_guard_fix_4.py`, `test_g14.py` (scoped pytest) | 467 passed; 151 passed, 1 skipped: the same before and after |
| W2-84's deletions | 7 of 7 gone; nothing left names them (`git grep`); `test_optin_lifted.py` 16 passed before and after (every list entry exists); collection 363 fewer (329 + 34), no error |
| The operator's staging lines | 10 files staged: 3 M, 7 D (then unstaged; no commit in the rehearsal) |
| The measure check | `_measured` False for the orchestrator in every set, True for the engineer (the control) |
| `apply.sh undo` | the three files and the seven back byte for byte, modes kept; `git diff` clean |
| The live hook, map, list, the seven, the settings, the real sets root | **unchanged** (hashed before and after; the sets root's entry only, never its contents) |

The writer-like session (11-06: no guard runs there) was not repeated: nothing it showed depends on the change.

**The replay:** the last 48 hours of tool calls (9,429 unique) through the hook before and after.
- **No change:** 9,396 allowed and 9 denied, before and after. None named `runs/fresh-80` (the 80 has not run).
- **24 go from allowed to refused:**
  - **6 are meant** (the hidden rule): `stat` of a hidden file, `repin_gold.py` on hidden folders (4), a `find` of
    `memory-verdict-2` by a product-spec session.
  - **6 are false (the hidden rule), all probes or edits about this ACT:** three names-only checks of `runs`,
    `transcripts` or `fixtures/evaluation/memory-retrieval/hidden` in the repository, where no such folder exists
    (the globs hold in every tree, as designed; two by the rebuilder, one by readiness reviewer 5), and three
    heredoc bodies of the rebuilder's that quote the globs as text.
  - **12 are the line rule's, and none reads a hidden file:** reads of *open* `runs/` outputs (`w4-e0`,
    `score-once-replay`, a trial) with a variable holding the path or `python3 -c` code with `[`, `{` or a glob (6:
    engineer subagents 4, the CTO 2); two `python3 - <<'EOF'` bodies that name the root (engineer subagents, one a
    ticket edit); names-only `find … -name "REANCHOR-LOG*"` and `ls -d <root>/*/` (3); and an auditor's `find` with
    a variable (1). This is option A's price: such lines must name only open paths with no
    variable, glob or substitution after the root, or run as a script with `--sets-root`.

## 5. For your decision
1. **The two corrections:** six refused roles, and `transcripts/**` (§1). Recommended: yes.
2. **When to apply.** Re-pin window 4 re-pins the hidden sets' gold with `repin_gold.py`, and the leak check runs
   on hidden folders, both today from the CTO's session. Once applied, those calls are refused.
   - **(a) Recommended:** apply right after re-pin window 4. Before that, the CTO changes its hidden-set tools to
     take the sets root as an argument and open the files in their own code, printing ids and counts only, as the
     measure does. That is its own lane, with no guard change. The ACT is then applied with no break.
   - **(b)** Apply now, and the gold re-pin and the leak check move to your operator.
3. **Diagnostics on spent sets.** After this change, no session the guard judges can read a set's questions, the
   auditor included. A diagnostic like DEC-1074 (2)'s auditor read of the spent 60 then runs outside the guard (your
   checker or operator), or under an exception you name. Recommended: outside the guard; no exception in the code.
4. **Worktrees:** each runs its own copy of the hook, so a worktree gets the change when `w2/integrate` is next merged
   into it. Live worktrees with measured roles get that merge as part of the ACT. Recommended: yes, by the CTO, the
   same day.

**For the CTO, from the rebuild (2026-11-08):**
7. **The line rule's cost** (§4): 12 lines in 48 hours by the CTO's sessions would now be refused, all on open
   folders. Each has a form that passes (a script taking `--sets-root`, or a literal path with no variable, glob or
   substitution after the root).
5. **W2-84's three leftovers** (`tests/acceptance/W2-84/README.md`, its KPI map, `conftest.py` and `w2_84_support.py`):
   not cases, so not in the deletion; they serve only the deleted cases. Delete them in the same commit (three lines in
   `apply.sh`'s list, a re-hash and a short re-run), or leave them.
6. **The fresh-80 scripts:** only `--sets-root` on the line; `memory-verdict-2`, `runs/fresh-80`, the kept folder and
   the `USED` check derived and done in their own code; every count the CTO reads printed by them.

**What it costs:**
- every hook call runs one git call to find the main tree, about 80 ms;
- a malformed block refuses every call (fail closed, as designed);
- the product's own guard (`reads.parts()`) is a later W2-42a line (D9-FATES).

**Basis:** question 2 (the hidden halves refused to every measured role, wherever they lie) and question 4 (the
measure and your writer, checker and operator unaffected).
