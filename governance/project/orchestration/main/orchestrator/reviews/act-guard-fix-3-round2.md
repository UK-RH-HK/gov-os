# Review of ACT-GUARD-FIX-3, round 2 (independent, read-only; the last round, DEC-1010)

Reviewer: fresh session. Judged against ADR-0001's threat model and governance/project/briefs/JUDGEMENT.md. Two questions asked of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"

Result: round 1's blocking findings (F2, F3) and the conditional F4 are fixed. F1 (the flaky order) is fixed. I found no finding that is in scope, ordinary work yes, and fails open or loses work. Three findings are recorded as non-blocking (one fails open on a narrow construction, one is a rule-5 residual of the old F2 class, one is a new class of fail-closed false refusals), plus Wave 3 rows.

## 1. What I read and ran

Read: JUDGEMENT.md; the round-1 review and the moderator's triage; ACT-GUARD-FIX-3.md (all, with the "Round 2" section); the Judgement, variants(), python_writes() argv/environ and inline_python parts of bash_writes.py; the hook's use of the module. I did not re-read the 1,555-line diff.

Checked and ran (all writes in my own `mktemp -d`; nothing in the repo):
- Hashes: bash_writes.py df7be57c6bdd, pretooluse.py b7e96a89d092, test file b6f8216c97bc, diff 73e20a522a85 match the package. `git apply --check` of the diff on today's hook (blob e937a0fc4494) succeeds, and applying it in a temp repo gives exactly bash_writes.py df7be57c6bdd and pretooluse.py b7e96a89d092. `guard4_check.py` against today's hook ends PASS.
- `test_guard_fix_3.py`: **270 passed** on each of 3 runs, and 270 passed under PYTHONHASHSEED 0, 1, 7, 42, 99, 12345 (about 32 s each).
- F1 directly: the five chained-variable auditor commands (`T=/tmp/a; H=$T/p; mkdir -p $H && touch $H/x` and four deeper chains), each run 12 times through the real hook (`-E`, so the seed is random per process): 60 of 60 allow.
- Round-1 probe scripts probe/p5/p6/p7/p8 re-run against the round-2 hook (my copy of run.py), diffed against the engineer's saved round-1 outputs: every round-1 F3 repro (rules 1 and 5: `cp`, `touch`, `sed -i`, `mv`, `git checkout/rm/restore` with continuations, `echo a > \<nl>file`) now denies; every F2 repro (`chmod +x; ./s.sh`, `cd /tmp && bash s.sh`, loop variable, `uv run`, `runpy`, `exec`) now denies; the F4 repros (`Path.glob().write_text`, `unlink`, `os.walk` + `remove`, `listdir` + `remove`, `chdir`, `mkdtemp(dir=)`, the `-c` computed-path forms) now deny. The rule 2 and 3 outputs (p5) are unchanged (the same 9 allows as round 1, all documented: Python reading `.env`, quoted-heredoc data).
- About 290 commands of my own (a rule-1 matrix of F2/F3/F4 variants and ordinary false-positive controls, argv/environ/continuation probes, rule-5 controls), each run through the round-2 hook and, where it mattered, today's hook (`.claude/hooks/pretooluse.py`).
- The 61-row logged corpus (reviewer's corp.py), seeds 0 and 3: refused rows are exactly [39, 46], the package's 2 of 61 (3.3 %). The package's claim is reproduced. I did not re-run the 4,893-command history or the 7-of-61 (11.5 %) measurement; I accepted them as stated, and they are plausible given the structure.

## 2. Status of round 1's findings

- **F1 (hash-seed-dependent verdict): fixed.** Variables expand in source order. Tests deterministic across seeds and runs; direct repro deterministic.
- **F2 (script written by a heredoc, run by an idiom the module did not read; blocking): fixed for rule 1.** About 70 run idioms tried (bash/sh/zsh/dash/source/`.`, `./`, after `cd` or in a subshell or `pushd`, `chmod 755`/`a+x`, variable and loop-variable runs, `bash < f`, `cat f | bash`, `xargs`, `find -exec`, `env`/`timeout`/`nohup`/`sudo`/`exec`, `-c` strings, `$(…)`, relative name with `cat > s.sh`, unquoted and `<<-` heredocs, `tee`, a pipe straight into `bash`, bodies using `$1`, `$@`, env-passed variables, bodies with `cd tests/acceptance`, Python bodies with `sys.argv`, `uv run`, `pytest`, `python3 -m pytest`, `python3 - < f`). All deny. Misses: `python3 -m s` (module name; after `cd /tmp` or with PYTHONPATH), a contrived form. Rule-5 residual: see F2 below.
- **F3 (backslash-newline; blocking): fixed.** About 30 continuation shapes tried (arguments, redirect targets, doubled continuations, inside the path word, inside `python3 -c`, in a loop, in a pipe, with a heredoc, with `git`, `install`, `ln`). All deny, for rule 1 and rule 5. Continuations in single quotes and `$'…'` are kept (shape correct). A comment ending in a backslash stays allowed (see Wave 3 rows; the same as today).
- **F4 (inline Python through derived names; conditionally in): fixed, and the condition holds** (corpus stays at 2 of 61). About 100 forms tried; all the round-1 repros and the close variants (aliases `import … as`, `from … import … as`, `pathlib` joins and `/`, `shutil.*`, `os.*`, `fileinput(inplace)`, `sqlite3`, `json.dump(open(…))`, `logging.FileHandler`, f-strings, `%`, `.format`, `Path.cwd().joinpath`, `os.getcwd()+`, `perl -pi -e`, `node -e`, `ruby -e`, a lone `open` alias) deny. The one miss: `os.open(…, dir_fd=…)` after an `os.open` of the folder (deliberate).
- **F5, F6, F7:** Wave 3 rows as ruled (unchanged; see the rows below).

## 3. Findings (round 2)

### F1 An unresolvable shell variable handed to inline Python as `sys.argv` is read as empty, so the write is not refused
- Repro (engineer; the same command is allowed today, so no regression):
  - `for f in tests/acceptance/a tests/acceptance/b; do python3 -c "import sys;open(sys.argv[1],'w')" $f; done`
  - `ls tests/acceptance/*.py | while read f; do python3 -c "import sys;open(sys.argv[1],'w')" "$f"; done`
  - `F=$(ls tests/acceptance/*.py | head -1); python3 -c "import sys;open(sys.argv[1],'w')" "$F"`
  - `read f < <(ls tests/acceptance/*.py); python3 -c "import sys;open(sys.argv[1],'w')" "$f"`
  - Also `echo tests/acceptance/ >/dev/null; python3 -c "import sys;open(sys.argv[1],'w')" "$X"`.
- Expected: refused (the command names the tests with a slash; the write target is a word the guard cannot work out; the package says an unresolvable target refuses when the command names the tests). Actual: allow. By contrast `f=tests/acceptance/a; … $f`, `… tests/acceptance/*.py`, and `$(date)` as the argument all deny. Cause (from reading `inline_python` and `python_writes`): the argv words are expanded once with `self.expand(w)` under the base environment, so a variable the guard dropped (loop variable, `read`, `$(…)`) is treated as an empty string, not as unknown. The per-variant expansion used for the code text is not used for argv.
- Ordinary work: no, because it needs a shell loop or pipeline whose variable is handed to `python3 -c` as an argument; the common bulk-edit forms (a `sed -i` loop, Python looping over the folder itself, a loop with the path in the word) all deny, and the same command passes today. (Borderline: a moderator may rule otherwise; it is a hole in a feature round 2 added.)
- Consequence: fails open
- Scope: in. Severity: low. Row for Wave 3 (fix: a dropped variable in an argv word is `None`, as `$(…)` already is).

### F2 Rule 5: a script written by a heredoc and run by a relative name after `cd` is not read (regression against today)
- Repro (independent-auditor): `cat > /tmp/s.sh <<'EOF'` / `touch src/x` / `EOF` then `chmod +x /tmp/s.sh; cd /tmp; ./s.sh`, or `cd /tmp && bash s.sh`. Allowed by round 2, denied by today's hook (by accident, as it reads the heredoc body as shell). The same commands naming `tests/acceptance/` are refused for rule 1 (F2 of round 1 is closed there); `bash /tmp/s.sh`, `chmod +x /tmp/s.sh && /tmp/s.sh`, loop and variable runs, `source`, `sh`, `| bash` all deny for rule 5.
- Expected: refused for a reviewer or auditor (the script writes `src/x`, not their record). Actual: allowed.
- Ordinary work: no, because an auditor would have to write a script whose body edits project source (not their record) in the same command and run it by a relative name after a `cd`; an auditor's probe scripts write under `$TMPDIR`, which passes.
- Consequence: fails open
- Scope: in (rule 5 uses the module). Severity: low. Wave 3 row (extend the "may run" rule that rule 1 uses to rule 5).

### F3 New false refusals: a data heredoc given to a program that is not on the readers' list, in a command naming the tests
- Repro (engineer; each is allowed by today's hook and refused by round 2): `git commit -F - <<'EOF'` / `fix tests/acceptance/f wording` / `EOF`; `git commit -F- …`; `git tag -F - v1 <<'EOF' …`; `gh pr create --body-file - <<'EOF' … tests/acceptance/f …`; `gov checkpoint write --stdin <<'EOF' …`; also `sed 's/a/b/' <<EOF`, `awk … <<EOF`, `sqlite3 db <<EOF`, `read -r x <<EOF`. The usual commit idiom `git commit -m "$(cat <<'EOF' … EOF)"` and `tee`, `cat`, `diff -`, `jq`, `ssh`, `python3 -m gov.cli … <<EOF` pass.
- Cause (by design, section 3): a body given to any other reader is "code the guard cannot read", refused when it names the tests. Round 1's pattern was not this broad for `git commit -F -`.
- Ordinary work: yes, because leads and the CTO write commit and PR messages that name test paths, and some use `-F -` or `--body-file -`.
- Consequence: other (fails closed; a retry with `-m "$(cat <<…)"` or `-F file` passes; no work lost)
- Scope: in. Severity: low. Not blocking (fails closed). The logged corpus is still 2 of 61, so the KPI line holds; recommended as a small add to the readers' list (`git commit/tag -F -`, `gh … --body-file -`, `gov … --stdin`, `sed`/`awk` with literal scripts) when the module is next touched.

## 4. Wave 3 rows (all out of scope or deliberate; none blocks)

Each: Ordinary work: no (or unchanged from today and ruled out of scope, F5/F6 class); Consequence: fails open; Scope: out.
- R1. Shell writers not read, unchanged from today (F5 class): combined sed flags `sed -Ei s/a/b/ f` and `sed -ni p f` (the separate `-E -i` form is read), `git stash -- path`, `git clean -fd path`, `git format-patch -o`, `xargs`/`find -exec` writers, `stdbuf`/`flock`/`setsid` prefixes, `chmod`.
- R2. A `# comment \` + newline + write is joined into the comment (bash does not continue a comment). Same result as today; a deliberate form.
- R3. `export W=tests/acceptance` (or `W=…; export W`) handed to `python3 -c` through `os.environ`: unresolvable and, with no slash, not refused (F6 class). `os.chdir` after `cd tests`; `os.environ['PWD']` after `cd`. Deliberate constructions.
- R4. A Python heredoc, or `echo`/`printf`, that writes a shell script the same command then runs, in a command naming the tests (the package's stated regression; see section 5).
- R5. `python3 -m s` run of a module the command just wrote (after `cd` or with PYTHONPATH); `os.open(..., dir_fd=)`.
- R6. `function f { … }; f`, `alias`, `trap`, `coproc`, `select … do`, and `$'\x61cceptance'` forms are not read (unchanged from round 1's p7 output).

## 5. The stated remaining regression

I tried to find the case where today refuses and round 2 allows: a Python heredoc (or `echo`/`printf`) that writes a shell script naming the tests, run in the same command (forms with `touch`, `echo hi > …`, `cat > … <<X`, an apostrophe in the text, a `gen.py` run). I could not reproduce a refusal by today's hook on any of the forms I tried (today allowed all of them), so I found no regression against today in this class; the package says today refuses some "by accident" (when the Python text is mis-read as shell), which my forms do not trigger. Either way, this is a deliberately-built two-step (code that writes a script that writes the test folder, in one command); an honest agent that wants to write a test file does not go through it, and refusing every run of a file the command wrote was measured at 11.5 % of the logged corpus (over the owner's 10 % line, and the ordinary "edit a tool, then run it" would be refused). The row is correctly a Wave 3 row, not a blocker: Ordinary work: no; Consequence: fails open; Scope: in (named in the package). I could not re-verify the 11.5 % figure (the script was not run), but the logic is sound.

## 6. The three KPI lines

- **no-fail-open: pass.** F2 and F3 of round 1 are closed and I tried about 290 variants. The remaining open items (F1 argv with a dropped variable, F2 rule-5 relative run) fail open but are not ordinary work (and not regressions against today in F1), so they are Wave 3 rows by the judgement rules.
- **fails-closed-on-unknown: pass.** Unreadable scans fall back to today's rule; unresolvable targets refuse when the command or code names the tests (any spelling for code); a module error exits 2. The one place an unknown is read as known is F1 (a dropped variable in argv).
- **false-positives-reduced: pass.** 31 of 61 to 2 of 61 (3.3 %), reproduced on seeds 0 and 3. F3 records one new class of false refusals (data heredocs to unlisted programs), which the corpus does not contain.

```verdict
{"kpis": [{"kpi": "no-fail-open", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "fails-closed-on-unknown", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "false-positives-reduced", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
