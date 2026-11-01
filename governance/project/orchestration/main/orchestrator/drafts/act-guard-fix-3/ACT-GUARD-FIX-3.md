# ACT-GUARD-FIX-3 / P1: rules 1 and 5 read what a Bash command writes, not the words it holds (DEC-958)

For the owner. DEC-958's trigger has been met all week: 61 false refusals are logged, 81 minutes lost, and leads, auditors and the CTO hit them daily. You asked for a fix now: false positives under 10 % on the logged corpus, with no true write into the acceptance folder missed.

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
  - a body written to a file that the same command then runs: judged as that file's code.
- **The command's own variables.** A variable set once at the top level, before any use, is expanded. A literal `for` loop is judged once per word. A variable bound any other way (`read`, `if`, a pipeline, `source`, `eval`) is unresolvable.
- **Substitutions, `sh -c` and `eval`.** `$(…)`, backticks, `<(…)`, `>(…)`, `sh -c '…'` and `eval` are each judged as a command of their own. Keywords and prefixes (`do`, `then`, `!`, `{`, `timeout`, `env -i`, `nohup`) are separated off, so `do touch X` is read as `touch X`.
- **Inline Python** (`-c`, and heredocs) is read for its own writes:
  - `open` in a write mode; the path, `os` and `shutil` writes; `sqlite3`, `tarfile` and `zipfile` writes;
  - the commands it runs (a literal `subprocess` or `os.system` command is judged as Bash);
  - straight-line names are resolved (`p='x'; open(p,'w')`).
  - A write whose target it cannot work out is unresolvable. So is `exec`/`eval`, code the shell rewrites with something it cannot resolve, and an unknown function handed a path that names the tests.
- **Writes the product's parser does not read** (rule 1 only): `git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync`. `git apply`, `git am`, `git stash apply|pop` and `patch` write the files their patch names: they are unknown targets.
- **The decision.** Rule 1 refuses when:
  - a target **names or lands in** the acceptance folder; or
  - a target cannot be worked out **and** the command, or its code, names the tests.
  
  Rule 5 judges the shell's own writes, as before.
- **The read rules** (2 and 3) see the command without the bodies of data heredocs, and with `$((…))` written as `0`.
- **Fail closed:**
  - anything the scan cannot read for certain (unbalanced quotes, an unterminated heredoc, `<<` in arithmetic) is judged by today's rule, unchanged;
  - an error in the module refuses (exit 2), as any error in the hook does.
- **Size:**
  - the hook: 51 lines added, 8 changed;
  - the module: new, about 1,200 lines with its comments; about 280 of them read Python.
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

**Planted cases (169).** These are guard4_check.py's 54, plus 115 new ones written for this package (`test_guard_fix_3.py`). The new set has two kinds:
- 87 real writes into the tests that must be refused: heredocs, inline Python, variables, loops, substitutions, `sh -c`, `git checkout`/`restore`/`rm`, patch appliers, and keywords and prefixes;
- 28 patterns of the logged false refusals that must pass.

| | Today's hook | With the fix |
|---|---|---|
| guard4's 29 writes to refuse | 0 missed | 0 missed |
| guard4's 24 calls to pass (and 1 "ask") | 0 wrong | 0 wrong |
| New: 87 writes to refuse | **40 missed** | **0 missed** |
| New: 28 calls to pass | **11 refused** | **0 refused** |

guard4_check.py, run on the candidate, ends `PASS`. The test file gives 198 passed (197 passed and 1 skipped without the private corpus).

**The command history (differential).** Every Bash command in this week's transcripts was run through both hooks: each command that names the acceptance tests (judged as an orchestrator, rule 1), and every command of an auditor session (rule 5). **4,873** commands in all, on the final code.
- **Refused today, passed with the fix: 67.** Each was read by hand. None writes into the acceptance folder or outside a reviewer's records: they read the tests, run them, or write scratch, `/tmp`, records or tickets. One real write did turn up on the way (`git apply -R` of a test's diff, #146). Today's hook refused it only because a `$P` was unresolvable. The fix now refuses patch appliers (planted).
- **Passed today, refused with the fix: 9.** 6 of them are **real writes into the acceptance tests that today's hook misses**: test designers' Python heredocs writing test files, and `git rm` of a test, judged as a non-designer. 3 are fail-closed refusals: a Python write whose target the guard cannot work out (`open(f"briefs/{w2}…", "w")` in a loop), in a command that names the tests.

**Robustness:**
- bash_writes raised nothing on any of the 4,867 history commands, or on any planted case;
- 6 of them it could not read for certain, and those were judged by today's rule;
- none took over 2 s (the hook's deadline is 20 s).

**Three rows added to the log during this work** (61–63: the CTO's, and two of this package's own commands) are refused today and pass with the fix.

## 5. The risk
**What it could miss that today's hook catches.** Nothing found:
- every planted case and every history command that today's hook refuses for a real write is still refused;
- the one gap the history showed (`git apply`) is closed.

**Where it is unsure, it fails closed:**
- a command it cannot read for certain gets today's judgement;
- a target it cannot work out refuses when the command names the tests;
- a `cd` to an unknown folder makes relative targets unresolvable;
- a module error refuses.

**Left open, as today** (each needs a deliberate construction; Wave 3 hardening rows, as FIX-1 and FIX-2 left theirs):
- a script file the command runs (`python3 tools/x.py`). It is opaque, as since FIX-1. A script written by a heredoc in the same command and then run is now read;
- wholesale git moves: `git checkout <branch>`, `merge`, `pull`, `reset --hard`, `rebase`, and `stash` without apply or pop;
- `xargs`, `find -exec` or `parallel` running a write command;
- `perl`, `node` or `ruby` code that does not name the tests;
- a Python write through a library given a path built at run time that never appears as the tests' path;
- rule 3 does not read Python code: a Python heredoc that reads `.env` passes today and after.

**Rule 5:**
- **Tighter.** It now also sees writes in `sh -c`, `"$(…)"`, `do`/`then` commands, `timeout`-prefixed commands and shell heredocs.
- **Not tighter on Python.** It no longer reads a Python heredoc's body as shell. Rule 5 never read Python: `python3 -c` and script files always passed it.

**New code on the guard's path.** The module is about 1,200 lines. Its behaviour is pinned by 198 tests and the 4,867-command history. An independent review before applying is recommended (CAP-33).

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
- **The pin.** The five-rule hook works on today's pin (`pin-5c401220`): the module hands the parser text with heredocs already cut. When W2-42 lands and the pin is rebuilt, `bash_writes.py` stays correct and can be slimmed in a later ACT.

## 8. Options
- **(a) Apply the whole fix (recommended).**
  - 31 → 2 of the 61 refused (3.3 %).
  - 0 of 116 planted writes missed (today: 40).
  - It also closes real gaps of today's hook: Python heredocs writing tests, `cd` into the tests, `sh -c`, `"$(…)"`, `git checkout`/`restore`/`rm`, patch appliers, and keyword and prefix forms.
  - About 1,250 lines in two files.
- **(b) Apply only the narrowest part: the shell-level reading, without the Python reading.** Python code that names the tests is refused as today.
  - Measured: **15 of 61 refused (24.6 %), above your 10 % line.**
  - Planted: 6 writes missed, every one also missed today (no new miss).
  - About 300 fewer lines. It leaves the commonest false refusal (Python that reads a test) in place.
- **(c) Defer.**
  - 31 of the 61 patterns keep being refused: about 1 to 4 minutes each, 81 minutes logged so far.
  - The 40 planted writes today's hook misses stay missed.

## 9. Recommendation
**(a), confidence medium-high.**
- **High on the measurements:** the corpus, the 169 planted cases and the 4,867-command history.
- **Medium on the size of new code** on the guard's path. Hence the independent review before applying.
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
- The test file must end with `197 passed, 1 skipped`. The skipped test replays the private corpus; it runs only with `GUARD_FIX3_CORPUS` set.
- Stop at the first line that differs, and tell the orchestrator.
- **Undo:** `git revert <the commit>`. Both files go back together.
