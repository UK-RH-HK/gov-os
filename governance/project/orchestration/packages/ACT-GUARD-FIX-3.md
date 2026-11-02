# ACT-GUARD-FIX-3 / P1: rules 1 and 5 read what a Bash command writes, not the words it holds (DEC-958)

For the owner. DEC-958's trigger has been met all week: 61 false refusals are logged, 81 minutes lost, and leads, auditors and the CTO hit them daily. You asked for a fix now: false positives under 10 % on the logged corpus, with no true write into the acceptance folder missed.

**Round 2.** The independent review failed round 1 on F2, F3 and F4. This version fixes F1–F4 as the moderator ruled (section "Round 2"), with every figure re-measured; F5–F7 are Wave 3 rows. Round 1 is kept unchanged beside this folder (`act-guard-fix-3-round1/`).

## 1. Context
- **The hook.** `.claude/hooks/pretooluse.py`, the five-rule hook (DEC-953 item 2). Rule 1 lets only the independent test designer write `tests/acceptance/**` (MR-3). Rule 5 limits reviewers and auditors to their own records. For Bash, both rules use the product's write parser, `gov.guard.decide._extract_bash_write_targets`, imported from the pinned judge (`pin-5c401220`, identical to `src/gov/guard/decide.py:431`).
- **Rule 1 refuses a Bash command** (lines 173–183) when:
  - the parser returns a write it cannot resolve **and** the command's text holds `tests/acceptance/` anywhere; or
  - a part of the command holds inline code (`python3 -c`, `perl -e`) **and** names the tests (`inline_writes_acceptance`, line 42).
- **ACT-GUARD-FIX-1** (`c3392f46`) let read-only commands pass. **ACT-GUARD-FIX-2** (`ffc60703`) judged inline code one part at a time.

## 2. What is refused today, and why
**The corpus.** `log/guard-refusals.jsonl` has 61 rows.
- The 57 rows with a `verdict` are false positives.
- The 4 rows with a `judgement` (rows 50–53) also read "false positive (known pattern)", so **the corpus holds no true positive.**
- Rows 50–53 carry no tool_use id. They are summaries of rows 54, 55, 58 and 59: the same session, the same pattern, minutes apart. Each is measured as its twin.

**Rebuilding the commands.** Each command was rebuilt in full from its transcript, using the `tool_use` id in the row's `key`. It was then run through a copy of today's hook as Claude Code runs it:
- event JSON on stdin, the pinned interpreter, `-E`;
- the session's role and `TMPDIR` from its launch folder (`gov-launch-<role>-<id>`);
- otherwise orchestrator, for the CTO and the leads.

**Today's hook still refuses 31 of the 61 (50.8 %):**

| Rule | Logged | Still refused today | Why |
|---|---|---|---|
| 1 (acceptance tests) | 48 | 18 | Heredoc bodies parsed as shell (rows 23, 40, 42, 45, 54, 55, 58, 59). Inline or heredoc Python that only **reads** a test, or puts its folder on `sys.path` (31, 33, 44, 49, 57). Nested quotes in `"$( … '…' … )"` (40). An unquoted Python heredoc the shell rewrites (46). |
| 5 (reviewers) | 11 | 11 | The command's own variables (`B=/tmp/…; mkdir $B/r`, rows 34, 35, 36, 41, 43, 47, 56). A literal loop's words (48). Nested quotes (37). Heredoc lines read as redirects (38). An unmatched glob (39). |
| 3 (secrets) | 1 | 1 | A probe written by a heredoc whose **text** names `.env` (32). |
| 2 (listing) | 1 | 1 | `sed -n "${n},$((n+6))p" docs/DECISION_REGISTER.md`: arithmetic `$((…))` read as a command substitution (60). |

The other 30 rule-1 rows already pass: FIX-1 and FIX-2 fixed them, and the sessions started before the fix reached their trees.

**The root cause.** The parser reads one shell line, and it does not know:
- **heredocs.** It reads the body as commands: an apostrophe makes the line unreadable, and a `>` in the text becomes a redirect;
- **the command's own variables, and literal loop words;**
- **substitutions inside double quotes;**
- **shell keywords and prefixes.** It takes `do`, `then` and `timeout 60` for the command's name.

Rule 1 then falls back on whether the text names the tests. That passes nothing the parser cannot read, and refuses briefs, reads and edits elsewhere.

## 3. The change
A new module, `.claude/hooks/bash_writes.py`, sits beside the hook. Rules 1 and 5 read a Bash command through it, and it hands the product's parser only shell text:
- **Heredocs.** Each body is cut out and judged by what reads it:
  - data for `cat`, `tee`, `grep` and similar: no write. An unquoted body's `$(…)` is judged as a command;
  - Python for `python3 -`: its own writes;
  - shell for `bash`/`sh`: judged as a command;
  - any other reader: code the guard cannot read;
  - a body written to a file that a later word of the same command may run (`bash name` after a `cd`, `./name`, `chmod +x` and the path, a loop variable, `xargs`, a pipe into `bash`, `runpy`, `uv run`, …): judged as that file's code. A run the guard cannot read, or a run word that does not expand, refuses when the body names the tests (round 2, F2).
- **Line continuations.** A backslash-newline is removed before the text is read, as the shell does (round 2, F3).
- **The command's own variables.** A variable set once at the top level, before any use, is expanded, in source order (round 2, F1). A literal `for` loop is judged once per word. A variable bound any other way (`read`, `if`, a pipeline, `source`, `eval`) is unresolvable.
- **Substitutions, `sh -c` and `eval`.** `$(…)`, backticks, `<(…)`, `>(…)`, `sh -c '…'` and `eval` are each judged as a command of their own. Keywords and prefixes (`do`, `then`, `!`, `{`, `timeout`, `env -i`, `nohup`) are separated off, so `do touch X` is read as `touch X`.
- **Inline Python** (`-c`, and heredocs) is read for its own writes:
  - `open` in a write mode; the path, `os` and `shutil` writes; `sqlite3`, `tarfile` and `zipfile` writes;
  - the commands it runs (a literal `subprocess` or `os.system` command is judged as Bash);
  - straight-line names are resolved (`p='x'; open(p,'w')`), and so are `sys.argv[k]` (the command's words) and `os.environ[...]` (the session's value, when neither the command nor the code sets it).
  - A write whose target it cannot work out is unresolvable. So is `exec`/`eval`, code the shell rewrites with something it cannot resolve, and an unknown function handed a path that names the tests.
  - For code, "names the tests" counts any spelling: `tests/acceptance` with or without the slash, `'tests', 'acceptance'` as pieces, `%`, a glob (round 2, F4).
- **Writes the product's parser does not read** (rule 1 only): `git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync`. `git apply`, `git am`, `git stash apply|pop` and `patch` write the files their patch names: they are unknown targets.
- **The decision.** Rule 1 refuses when:
  - a target **names or lands in** the acceptance folder; or
  - a target cannot be worked out **and** the command, or its code, names the tests.
  
  Rule 5 judges the shell's own writes, as before.
- **The read rules** (2 and 3) see the command without the bodies of data heredocs, and with `$((…))` written as `0`.
- **Fail closed:**
  - anything the scan cannot read for certain (unbalanced quotes, an unterminated heredoc, `<<` in arithmetic) is judged by today's rule, read on both spellings of a continued line (round 2);
  - an error in the module refuses (exit 2), as any error in the hook does.
- **Size:**
  - the hook: 71 lines added, 8 changed;
  - the module: new, about 1,430 lines with its comments; about 320 of them read Python.
  - The full change is in `ACT-GUARD-FIX-3.diff`.

## 4. Measured, before and after
**The 61 logged refusals** (full commands from their transcripts):

| Rule | Logged | Refused today | Refused with the fix |
|---|---|---|---|
| 1 | 48 | 18 | **1** (row 46) |
| 5 | 11 | 11 | **1** (row 39) |
| 3 | 1 | 1 | **0** |
| 2 (listing) | 1 | 1 | **0** |
| **All** | **61** | **31 (50.8 %)** | **2 (3.3 %)** |

The two left refused are left by design:
- **Row 46.** An unquoted Python heredoc whose text the shell rewrites with `$(echo "$out" | sed …)`, in a command that names the tests. The guard cannot know what Python will run, so it fails closed.
- **Row 39.** `rm -f chain-*.json` in `/tmp`, with no file matching. The product's parser calls an unmatched glob unresolvable. That is the product's fix (section 7).

**True positives in the 61:** none, so none is missed.

**Planted cases (233).** These are guard4_check.py's 54, round 1's 115 and round 2's 64 (`test_guard_fix_3.py`; work/planted_extra.json holds the 179 of this package):
- round 1: 87 real writes into the tests that must be refused (heredocs, inline Python, variables, loops, substitutions, `sh -c`, `git checkout`/`restore`/`rm`, patch appliers, keywords and prefixes), and 28 patterns of the logged false refusals that must pass;
- round 2: every repro of the review's F1–F4, as 51 writes to refuse (among them the F2 and F3 repros, now planted writes) and 13 calls to pass.

| | Today's hook | Round 1 | Round 2 (this package) |
|---|---|---|---|
| guard4's 29 writes to refuse | 0 missed | 0 missed | 0 missed |
| guard4's 24 calls to pass (and 1 "ask") | 0 wrong | 0 wrong | 0 wrong |
| Round 1's 87 writes to refuse | **40 missed** | 0 missed | 0 missed |
| Round 1's 28 calls to pass | **11 refused** | 0 refused | 0 refused |
| Round 2's 51 writes to refuse (F1–F4 repros) | **35 missed** | **46 missed** | **0 missed** |
| Round 2's 13 calls to pass | **3 refused** | **3 refused** (one by hash seed, F1) | 0 refused |

guard4_check.py, run on the candidate, ends `PASS`. The test file gives **270 passed** (269 passed and 1 skipped without the private corpus); the same on three runs and under PYTHONHASHSEED 0, 1, 42 and 12345, in parallel and serially.

**The command history (differential).** Every Bash command in the transcripts since 30 October was run through three hooks (today's, round 1's, round 2's): each command that names the acceptance tests (judged as an orchestrator, rule 1), and every command of an auditor session (rule 5). **4,893** commands, on the final code; the full run took 6.5 minutes, so no sample was needed.
- **Refused today, passed with round 2: 67.** Round 2 passes nothing round 1 refused (0), so these are round 1's hand-read set, rerun: none writes into the acceptance folder or outside a reviewer's records. The 23 that hold a line naming the tests beside a write operation were read again: scratch and `/tmp` writes, reads of a test (`awk`, `ast.parse`), register appends, and probes whose command strings name the tests (this session's own refused edits among them).
- **Passed today, refused with round 2: 13.** Round 1's 9 (6 real writes into the tests that today's hook misses; 3 fail-closed Python writes in a loop, in commands naming the tests), and 4 new.
- **Passed by round 1, refused by round 2: 6** (4 of them passed today too). 5 are auditors' probe scripts, written by a heredoc and run by `python3` in the same command, that build a stand-in project under `$TMPDIR` with its own `tests/acceptance` folder and write into it through a loop variable (`for d in (proj, told): d.mkdir(...)`). Round 2 reads such a script as code (F2) and refuses a write it cannot place when the code names the tests (F4). 1 is an orchestrator's guard probe whose Python runs commands naming the tests through `subprocess` with a computed command. All 6 fail closed; the fix for the auditor is to write the probe in one call and run it in the next (a script file run alone is opaque, as since FIX-1).

**Robustness:**
- bash_writes raised nothing on any of the 4,893 history commands, or on any planted case;
- 6 of them it could not read for certain, and those were judged by today's rule;
- none took over 2 s; the largest planted shapes (a 130 KB heredoc, 400 chained variables, a 3,000-line Python heredoc) take 0.7 s, 1.2 s and 4.3 s (the hook's deadline is 20 s).

## Round 2: the review's findings and how each was handled
The independent review (`reviews/act-guard-fix-3.md`) failed round 1 on F2, F3 and F4; the moderator's triage is binding.
- **F1 (variable order; the test was flaky).** `variants()` walked a set, so `T=/tmp/a; H=$T/p` dropped `H` under some hash seeds. Variables are now expanded in source order. A module test runs `variants()` under 12 seeds and requires one answer; the reviewer's repro gives the same targets under 24 seeds (round 1 gave 6 different answers).
- **F2 (blocks; a regression).** A data heredoc's body written to a file is judged whenever a later word of the command may run it: `bash`/`sh`/`source` by name (after a `cd` too), `./name`, the path after `chmod +x`, `python3`, `-m runpy`, `pytest`, `bash < file`, a pipe into `xargs` or a shell, a `-c` string or a `$(…)` naming it, any program not on a list of readers (`cat`, `wc`, `chmod`, `cp`, `git`, …), and a copy of the file. A shell body read for certain is judged as shell, and a target that names the tests refuses wherever the script runs; a Python body is read as Python (with its `sys.argv`). Every other run, a run whose word does not expand (`bash $f` in a loop, `$S`), and a file with no `#!` line run by its name, is code the guard cannot read: refused under rule 1 when the body names the tests; under rule 5 the body is read as shell, as today's hook does. The review's four repros and 15 more are planted, with 4 calls that must pass.
- **F3 (blocks).** Backslash-newline is removed before the text is read (outside single quotes, as the shell does); a command the scan cannot read is judged by today's rule on both spellings. The review's repros (rules 1 and 5) are planted.
- **F4 (conditional; included).** Code (Python, perl or node, a script body) that names the tests in any spelling and writes through a path the guard cannot work out (a glob, `listdir`, `walk`, `chdir`, a computed path) is refused. The logged corpus stays at **2 of 61 (3.3 %)**, the same rows (39, 46), under the 10 % line, so F4 is in. To keep honest code passing, `sys.argv[k]` and `os.environ[...]` (the session's value, when neither the command nor the code sets it) are now resolved. Three of the review's F4 repros are F5's class and stay as today (below).
- **F5, F6, F7: Wave 3 rows** (moderator), unchanged by this package:
  - **F5.** Shell writers the module does not read: `find -delete`/`-exec rm`, `xargs rm`, `tar -x -C`, `unzip -d`, `curl -o`, `wget -O`, formatters (`black`, `ruff format`, `ruff check --fix`), `pytest --junitxml=`, `awk` and `sed` `w`, `git log --output=`, `git stash pop`/`git apply`/`patch` without the tests named, wholesale `git checkout -- .`/`restore .`/`reset --hard`/`clean`; and rule 5 reads fewer of them than rule 1. The same class through Python's `subprocess` with a literal command (`black`, `tar -C`, `git stash`) is pinned by three "known gap" tests.
  - **F6.** An unresolvable shell write refuses only when the text holds `tests/acceptance/` with its slash (`read T <<< tests/acceptance; touch $T/f`). Code now counts any spelling (F4); the shell rule is as today.
  - **F7.** `git rm -n`/`--dry-run` and `rsync -n`/`--dry-run` into the tests are refused (accepted by the moderator as new false refusals).
  - **New row (found in round 2).** A script written by `echo`/`printf` or by Python (not a heredoc), then run in the same command, is not read; today's hook refuses the Python-written case only by accident (it reads the Python as shell). Refusing every run of a file the command wrote, when the command names the tests, was measured: **7 of 61 (11.5 %)**, over the 10 % line (it refuses the ordinary "edit a tool, then run it"), so it was left out.

## 5. The risk
**What it could miss that today's hook catches.** Searched with the review's probe scripts (rerun on round 2) and the history:
- every planted case and every history command that today's hook refuses for a real write is still refused;
- the review's F2 regression is closed; the one left is the new row above (a Python heredoc writing a shell script that the command then runs, in a command naming the tests), refused today only by accident.

**Where it is unsure, it fails closed:**
- a command it cannot read for certain gets today's judgement;
- a target it cannot work out refuses when the command names the tests (code: in any spelling);
- a script written and run by a form it cannot read refuses when the script names the tests;
- a `cd` to an unknown folder makes relative targets unresolvable;
- a module error refuses.

**Left open, as today** (Wave 3 hardening rows):
- a script file the command runs that it did not write by a heredoc in the same command (`python3 tools/x.py`): opaque, as since FIX-1;
- F5's shell writers, F6's slash, and the new row above;
- wholesale git moves: `git checkout <branch>`, `merge`, `pull`, `rebase`;
- `perl`, `node` or `ruby` code that does not name the tests;
- a variable the command itself sets and hands to Python through the environment (`export D=…; python3 -c "…os.environ['D']…"`) is unresolvable, and refuses only when the command or code names the tests;
- rule 3 does not read Python code: a Python heredoc that reads `.env` passes today and after.

**Rule 5:**
- **Tighter.** It now also sees writes in `sh -c`, `"$(…)"`, `do`/`then` commands, `timeout`-prefixed commands, shell heredocs, line-continued commands, and scripts written by a heredoc and run by any idiom.
- **Not tighter on Python.** It does not read a Python heredoc's body as shell. Rule 5 never read Python: `python3 -c` and script files always passed it.

**New code on the guard's path.** The module is about 1,430 lines. Its behaviour is pinned by 270 tests and the 4,893-command history. Round 2 goes to the independent review (the last round, DEC-1010).

## 6. The undo
`git revert <the commit>`. This puts both files back as they are today.
- **Never delete `bash_writes.py` alone.** The hook would then fail closed on every Bash call by every role.
- **Running sessions:**
  - a session in the main tree reads the hook file at each call;
  - a lead's worktree gets the fix when `w2/integrate` is merged into it, as with FIX-2.

## 7. The files
**Your operator changes, in the main tree:**
- `.claude/hooks/pretooluse.py` (modified);
- `.claude/hooks/bash_writes.py` (new).

**The checks:**
- `test_guard_fix_3.py`, to be copied beside guard4_check.py in `.gov-runtime/scratch/orchestrator/tools/`;
- guard4_check.py, unchanged.

**Their hashes (SHA-256, first 12):** `bash_writes.py` df7be57c6bdd; `pretooluse.py` b7e96a89d092; `test_guard_fix_3.py` b6f8216c97bc; `ACT-GUARD-FIX-3.diff` 73e20a522a85. The diff is made against today's `.claude/hooks/pretooluse.py` (git blob e937a0fc4494, unchanged since ACT-GUARD-FIX-2) and applies to it to give exactly these two files.

**The product's half (DEC-1003): through a ticket, not this ACT.**
- **The template hook needs no change.** The product's hook, `template/governance/kernel/hooks/pretooluse.py`, has no rule-1 text heuristic. It calls `gov.guard.decide.decide` and `gov.guard.reads.policy_refusal`, which use the same parser. It refuses **any** unresolvable Bash write, for every role. So the product half belongs in:
  - `src/gov/guard/decide.py`: `_extract_bash_write_targets`;
  - `src/gov/guard/reads.py`: `_set_aside`, and `_Judge.tool`/`command`.
- **Measured** on the 61 commands: the product's parser cannot resolve the writes of **22**. With this package's shell-level reading it is **1** (row 39's glob).
- **The ticket.** The fitting open product ticket is **W2-42** (`DAEO-fau3`, "Guard: missing role, links, late paths, atomic saves"; paths `src/gov/guard/**`, `tests/unit/guard/**`; deferred to Wave 3).
- **Proposed KPI lines for W2-42** (for your approval, as SMART-WORK packages are). Each is written so the parser's result can be checked:
  1. A heredoc's body is not read as shell. A body that cat, tee or grep takes as data is no write; its unquoted `$(…)` is judged; a `bash`/`sh` body is judged as commands.
  2. A variable the command sets once at its top level, before any use, is expanded. A literal `for` loop's words are judged one by one. Any other binding is unresolvable.
  3. `$(…)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands. Shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command's name.
  4. An unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable.
  5. `git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes. `git apply`, `git am` and `patch` are writes to unresolvable targets.
  6. The read judge does not take `$((…))` for a command substitution, nor a data heredoc's body for commands.
  7. A backslash-newline outside single quotes is removed before the command is read.
  8. A data heredoc's body written to a file that a later word of the command may run is judged as that file's code; a run the parser cannot read is unresolvable.
- **The pin.** The five-rule hook works on today's pin (`pin-5c401220`): the module hands the parser text with heredocs already cut. When W2-42 lands and the pin is rebuilt, `bash_writes.py` stays correct and can be slimmed in a later ACT.

## The independent review (DEC-1010: two rounds, READY computed)
- **Round 1** (a different model, Sonnet): FAIL. F2 (a heredoc-written script run by `./name`, after `cd`, or in a loop: a regression), F3 (backslash continuation), F4 (inline Python writing through a computed path); F1 a flaky test. The CTO's triage: F1 to F3 fixed, F4 only if false refusals stayed under 10 % (they did); F5 to F7 Wave 3 rows. Record: the CTO's scratch `reviews/act-guard-fix-3.md`.
- **Round 2** (Sonnet, the last round): **PASS, no blocking finding; READY computed by `tools/verdict.py`: true.** Every round-1 repro and about 100 close variants now refuse; the diff applies to today's hook and gives exactly the two staged files; 270 tests pass on 3 runs and under 6 hash seeds; the corpus refuses rows 39 and 46 only. Record: `reviews/act-guard-fix-3-round2.md`.
- **Round 2's low findings, all Wave 3 rows:** an unresolvable shell variable passed as `sys.argv` to `python3 -c` is read as empty (today's hook allows it too; ordinary work no); rule 5 does not read a heredoc script run by a relative name after `cd` (ordinary work no); new false refusals, failing closed, for `git commit -F - <<EOF`, `gh pr create --body-file -`, `gov checkpoint write --stdin` and `sed`/`awk` heredocs whose text names the tests (ordinary work yes, consequence other: a refusal, not a miss). The reviewer could not reproduce the residual regression named in section 4 and judges it a deliberate two-step.

## 8. Options
- **(a) Apply the whole fix (recommended).**
  - 31 → 2 of the 61 refused (3.3 %).
  - 0 of 167 planted writes missed (today: 75; round 1: 46).
  - It also closes real gaps of today's hook: Python heredocs writing tests, `cd` into the tests, `sh -c`, `"$(…)"`, `git checkout`/`restore`/`rm`, patch appliers, keyword and prefix forms, line continuations, and Python writes through a glob, `listdir`, `walk` or `chdir`.
  - Cost: 6 history commands round 1 passed are refused (auditors' probe scripts building a stand-in `tests/acceptance` under `$TMPDIR`; section 4).
  - About 1,500 lines in two files.
- **(b) Apply only the narrowest part: the shell-level reading, without the Python reading.** Python code that names the tests is refused as today.
  - Measured in round 1: **15 of 61 refused (24.6 %), above your 10 % line.**
  - Planted: 6 writes missed, every one also missed today (no new miss).
  - About 300 fewer lines. It leaves the commonest false refusal (Python that reads a test) in place.
- **(c) Defer.**
  - 31 of the 61 patterns keep being refused: about 1 to 4 minutes each, 81 minutes logged so far.
  - The 75 planted writes today's hook misses stay missed.

## 9. Recommendation
**(a), confidence medium-high.**
- **High on the measurements:** the corpus, the 233 planted cases and the 4,893-command history.
- **Medium on the size of new code** on the guard's path. Hence the independent review (round 2, the last) before applying.
- **Classification:** ordinary work, yes (every lead, auditor and the CTO). Consequence: other. Today it fails closed, and costs time and brief gaps; the fix also closes misses.

## The commands (your operator, in the main tree)
The orchestrator first copies the staged files from this session's scratch into `governance/project/orchestration/packages/`: `ACT-GUARD-FIX-3.md`, `ACT-GUARD-FIX-3.diff` and `test_guard_fix_3.py`.
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short -- .claude/
git apply governance/project/orchestration/packages/ACT-GUARD-FIX-3.diff
cp governance/project/orchestration/packages/test_guard_fix_3.py .gov-runtime/scratch/orchestrator/tools/
python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py
python3 -m pytest -q -p no:cacheprovider .gov-runtime/scratch/orchestrator/tools/test_guard_fix_3.py
git add .claude/hooks/pretooluse.py .claude/hooks/bash_writes.py
git commit -m "ACT-GUARD-FIX-3: rules 1 and 5 read what a Bash command writes (heredocs, own variables, inline Python; DEC-958)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-958, DEC-953" --trailer "Role: owner"
```
- `git status --short -- .claude/` must show nothing before `git apply`.
- `guard4_check.py` must end with `PASS` (54 cases).
- The test file must end with `269 passed, 1 skipped`. The skipped test replays the private corpus; it runs only with `GUARD_FIX3_CORPUS` set.
- Stop at the first line that differs, and tell the orchestrator.
- **Undo:** `git revert <the commit>`. Both files go back together.
