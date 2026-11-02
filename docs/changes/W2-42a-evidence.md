# W2-42a evidence: the product's guard reads what a Bash command writes (DEC-1028 item 4, DEC-1040 item 2)

Engineer's record for `DAEO-03ub`. Base `a58ba344`. The CTO merged the acceptance tests at `5cca6398`. Their
results, the second round of fixes and the new log rows are in "Round 2" at the end.

## The change
- **`src/gov/guard/bash_writes.py` (new).** ACT-GUARD-FIX-3's reviewed module (`.claude/hooks/bash_writes.py`,
  sha256 `df7be57c6bdd`), ported whole, with these changes for the product:
  - `Judgement.targets()`: what the product enforces. It is the shell's own writes (`shell`), plus `writes`, plus
    `unread`:
    - `writes` are the writes the line parser does not read (KPI 5): `git checkout`/`restore`/`rm`/`mv` on
      paths, `dd of=`, `truncate`, `sort -o` and `rsync`, and a sentinel for `git apply`, `git am` and `patch`.
    - `unread` is a sentinel for each run of a heredoc's script that the parser cannot read (KPI 8).
  - `git checkout <rev>` without `--`: the first word is not taken for a path when git reads it as a revision
    (`git rev-parse --verify`). When git cannot tell, it is taken for a path (fail closed).
  - The product does not count `git stash apply|pop` among the KPI-5 writes. The hook's own `findings` still
    count it.
  - An unquoted heredoc body's `$(…)` is judged as a command whoever reads the body (not only a data reader).
    An unquoted `bash`/`sh` body is judged as commands (KPI 1).
  - A heredoc read by an unknown program (`flock … bash`, `make -f -`, `docker exec`, …) may run as shell:
    - its body is judged as commands, as the line parser read it before;
    - a body the scan cannot read is unresolvable;
    - programs that only take their input as data (git, tk, gh, yq and some text filters) write nothing by it.
  - The bound check on its marks: the hook hands the parser its own parser text, which holds the hook's
    `__gov_sub_N__` and `__gov_heredoc_N__` marks.
  - `read_view` for the read judge (below).
  - The Python, perl and node reading (`python_writes`, `findings`) is kept unchanged, so the hook can call this
    module in place of its own copy (a later ACT). The product does not enforce it: Python code stays opaque to
    the product, as `python3 -c` and `python3 x.py` always were.
- **`src/gov/guard/decide.py`.**
  - The line parser is now `_line_write_targets`. It has one change, KPI 4: an unmatched glob is the literal word.
    The exceptions: the command holds `shopt`, `GLOBIGNORE` or `set -f`/`-o`, or the pattern holds `**`. In those
    cases it stays unresolvable.
  - `_extract_bash_write_targets` reads the command through `bash_writes.judge` and returns `targets()`.
  - What the scan cannot read for certain is read by the line parser, on both spellings of a continued line, as
    before.
- **`src/gov/guard/reads.py`.**
  - `_set_aside` does not take `$((…))` for a substitution (bash's own rule: the `(` after `$(` closes just
    before the last `)`). What it holds is set aside on its own.
  - The Bash read view (`bash_writes.read_view`):
    - `$((…))` is written as 0;
    - a data heredoc's body is cut, unless a later command may run the file it is written to;
    - a program's code in a heredoc (`python3 -`, an unknown reader) is cut, and each of its words is judged as a
      path, as a `python3 -c` string is;
    - a shell's body is kept;
    - an unquoted body's substitutions are commands of their own.
  - The listing rule:
    - A `for` loop's list counts only when its variable is named anywhere else in the command, which includes
      after the loop. It also counts when the command may read a variable by another name (`${!`, `eval`,
      `declare`, `local`, `export`, `source`).
    - `seq` with numeric words and `nproc` are placed listings: numbers in the folder they run in. They refuse
      when a protected file there starts with a digit.
  - The per-command write check uses the line parser, as before.

## The replay: every logged refusal through the five-rule hook (KPI 11)
The method:
- The full calls were rebuilt from their transcripts by `tool_use` id: 76 of 80 rows. Rows 50–53 carry no id, so
  each is measured as its twin (54, 55, 58, 59), as in ACT-GUARD-FIX-3.
- Each call was run through `.claude/hooks/pretooluse.py` as Claude Code runs it: event JSON on stdin, the pinned
  interpreter (`pin-a7182f6c`), and the session's role, agent type and `TMPDIR`.
- The judge it imports came from `src/` on `PYTHONPATH`, as the pin will hold it after re-pin window 2.
- The scripts are in the engineer's `TMPDIR` (`/tmp/gov-os-emg-w242a/work/`: `rebuild.py`, `replay.py`,
  `diag.py`, `measure_product.py`).

| | Base `a58ba344` | W2-42a |
|---|---|---|
| Logged false refusals now allowed | 68/78 | **73/78** |
| Logged true refusals still refused (rows 73, 76) | 2/2 | **2/2** |
| ACT-GUARD-FIX-3 planted writes refused (167) | 167 | **167 (0 missed)** |
| Planted calls as expected | 233/233 | 232/233 (below) |
| Seconds per hook call, mean / max (all 313 calls) | 0.18 / 1.41 | 0.13 / 0.64 |

The base ran under heavy load, so the times are only a guide. They do not show the hook getting slower.

**Which part refused each false refusal, and what happens to it now:**

| Row | Part that refused (base) | Now |
|---|---|---|
| 39 | product write parser (unmatched glob `rm -f chain-*.json` in `/tmp`) | allowed (KPI 4) |
| 74, 78 | product read judge (python3 heredoc editing a file by its literal path) | allowed (KPI 10) |
| 77 | product read judge (`for i in $(seq 1 16)` wait loop grepping one literal file) | allowed (KPI 10) |
| 79 | product read judge (`cat >>` heredoc whose text holds backticks, and the file then read by `tail`) | allowed (KPI 6, 10) |
| 64 | product write parser: `cd $TMPDIR \|\| cd $(ls -dt /tmp/tmp.* \| head -1)`, then `cat > probe.py` in a command naming the tests | **refused by design:** the folder is given at run time, so the target cannot be placed (fail closed) |
| 46, 71, 72 | **the hook's own `bash_writes.py`** (Python reading, ACT-GUARD-FIX-3 F4): 46 is an unquoted Python heredoc the shell rewrites; 71 is `sys.argv[1]` from `I=$(tk create …)`; 72 runs `exec_module` on a test-support module | **refused by design** in the hook's file (the owner's): each target is truly unknown, and the code names the tests. No change to the hook is proposed |
| 75 | the hook's rule 5 target check: a reviewer's `cat >` into `.gov-runtime/scratch/orchestrator/reviews/` | **a true refusal, logged as false by mistake:** the note "auto: the live hook now allows it" is wrong. It is the same write as row 76 (judged true), outside the reviewer's record paths |

So every false refusal that came from the product (the read judge and the write parser) passes, except row 64,
whose target is unknowable. Five rows stay refused, and none of them is a misreading: 64, 46, 71 and 72 are
fail-closed unknowns, and row 75 is a true refusal.

**The planted case that differs** is "fix3 python heredoc reading .env (gap as today)". It was expected to pass
as a known gap of rule 3; it is now refused. The read view judges the words of a Python heredoc as paths, as it
judges a `python3 -c` string. This closes a gap. It is not a new false refusal.

## The product's parser on the logged commands (KPI 9)
`measure_product.py` counts the logged commands that hold a write `_extract_bash_write_targets` cannot resolve.
`decide()` refuses those to every role.

| | Base | W2-42a |
|---|---|---|
| The 61 rows of ACT-GUARD-FIX-3 | 22 | **0** |
| All 79 Bash rows of the log | 31 | **1** (row 64: the `cd` above) |

## No fail-open (the failure lines)
- Every planted write of ACT-GUARD-FIX-3 is still refused through the hook (167 of 167).
- Unit file `tests/unit/guard/test_w2_42a_parser.py`:
  - Each write the line parser catches is still caught: `before − {sentinel} ⊆ after`. An unresolvable write
    stays unresolvable, unless it is now resolved to its place in the tests.
  - This covers the plain writers, redirects, `cd`, globs, variables, substitutions and backticks.
  - Unparseable forms (an unbalanced quote, an unclosed substitution) still refuse. So does `decide()`.
  - A heredoc the scan cannot read is read by the line parser, as before.
- Unit file `tests/unit/guard/test_w2_42a_reads.py`. These reads of a protected file stay refused:
  - a listing loop whose variable is used, after the loop too;
  - `eval`, `${!…}` and an assignment inside such a loop;
  - `seq -f`;
  - `$(( $(cat hidden) ))`;
  - a Python or shell heredoc that reads the hidden part or `.env`;
  - a heredoc-written script run by `bash`;
  - an unquoted body's `$(…)`;
  - `cat <<EOF | bash`;
  - an unknown reader's text naming the hidden file;
  - a numbered name in a folder with a numbered protected file.

## Tests
- `tests/unit/guard/test_w2_42a_parser.py` and `tests/unit/guard/test_w2_42a_reads.py`: 105 passed.
- The scoped set, the history differential and the acceptance tests: below, when run.

## Risks left (Wave 3 rows, as ACT-GUARD-FIX-3 §5 left them)
- **Glob options in a substitution.** A `shopt` in the outer command, with an unmatched glob inside a substitution
  that the hook judges alone, is read as the literal word. In the product's own path the whole command's options
  hold.
- **Python, perl and node code stays opaque to the product,** as before. A heredoc-written Python script run by
  `python3` is opaque too, like any Python script.
- **Rule 5 is tighter on real writes.** Through the product's parser, the hook's rule 5 now also sees the KPI-5
  writes of reviewers: `git apply`/`git am`/`patch` anywhere, and `git checkout -- f` in a tree. These are real
  writes. A reviewer applying a patch in a `/tmp` clone is now refused.
- **The loop-variable test is textual.** It errs to refusing: a standalone word equal to the variable's name
  anywhere in the command keeps the listing rule.

## Round 2 (after the acceptance tests merged at `5cca6398`; stopped by the owner's order, PARTIAL)

**The acceptance tests (results only).**
- First run: 443 passed, 9 failed. The failures:
  - failure line 1 on row 46's form: a Python heredoc the shell rewrites;
  - KPI 8: a Python file written, then run;
  - failure line 2: `eval`/`sh -c` of an unknown word, and an unbalanced string inside `sh -c`;
  - KPI 7: a secret or hidden name continued over a line;
  - KPI 10: a `wc` or `date` substitution.
- The fixes (`aac18cca`):
  - an unquoted Python heredoc the shell rewrites unpredictably is unresolvable;
  - a Python file the command writes and runs is judged as its code (its targets, or unresolvable);
  - an `sh -c`/`eval` word that does not expand, or a string the scan cannot read, is unresolvable;
  - the read judge also reads the command with each backslash-newline removed;
  - `wc` counts and `date +<digits>` are placed numeric listings.
- **Second run: 452 passed.**

**DEC-1044.** `tests/unit/guard/test_decide.py`'s three unmatched-glob cases were revised to the literal-path rule.
Each still checks that a write into a protected folder by that literal path is refused.

**Log rows 80–84** (written after the designer drew the fixtures), replayed through the hook:

| Row | Before | Now | Verdict |
|---|---|---|---|
| 80 | refused | refused | **true, logged false by mistake:** the command ran `ls` on the hidden half's folder by name |
| 81 | refused | refused | the hook's own `bash_writes.py` by design: a heredoc-written probe naming the tests, run by `python3`, with computed writes |
| 82 | refused | **allowed** | python3 heredoc |
| 83 | refused | **allowed** | `$(…)` in single-quoted arguments; the fix: single-quoted text is no substitution, and an apostrophe inside double quotes opens none |
| 84 (log line 85) | refused | **allowed** | the same fix |

**The scoped set.** `select_tests.py`, without `tests/unit/secrets_check` and the secret-filter cases (DEC-1045),
at `aac18cca`: 12582 passed, 10 failed, 7 skipped.
- **W1-02, the unmatched glob** (`test_a_target_the_guard_cannot_resolve_is_denied[glob-that-matches-nothing]`
  and its `-touch` case, and `test_a_glob_is_judged_by_what_it_expands_to`): these acceptance cases pin the old
  rule (DEC-115). KPI 4 reverses it, so they need a test designer's revision.
- **W2-05 `test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`:** `bash_writes.py` holds the
  literal `"git"`, and its revision check runs `git rev-parse` through `reads._git` (since round 2). It needs a row
  in `docs/research/AR-2-git-sweep.md`, which is outside the ticket's paths.
- **W1-02 `test_decision_p95_is_under_100_ms`** (2 cases): p95 was 101–143 ms on a loaded machine. It was not yet
  compared with the base: that run was stopped by the owner's order. Importing `bash_writes` adds about 5 ms.
- **Likely unrelated, not yet confirmed against the base:**
  - W1-46 npm install: the fixture repository has no `.claude/hooks/pretooluse.py`;
  - W2-50 secrets-scan scale: a gitleaks suite (DEC-1045);
  - W2-54 `green_here`: no store in this worktree;
  - containment `test_committed_rename_names_old_path`.
