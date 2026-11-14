# Brief: independent test designer, W2-42a (DAEO-03ub), the cases for R3 and the here-string fail-opens (DEC-1164 (18))

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer: you write
tests from the behaviour stated here (DEC-136); the engineer starts after you and you read no fix (none exists yet).
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head d3ba8e50b.
Your paths: tests/acceptance/W2-42a/** only. Add a NEW file tests/acceptance/W2-42a/test_w2_42a_here_string.py (and a
fixture file under tests/acceptance/W2-42a/fixtures/ if you like). Do not edit the existing test files or fixtures.
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1164 (18), W2-42a R3" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The product under test
The product guard `decide()` in `src/gov/guard/decide.py` reads a Bash call and refuses a write outside the role's
allowed paths. Call it exactly as tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py does: its `proj` fixture (an
in-progress engineer ticket DAEO-03ub allowing `src/**`, the session variables removed, HOME a fresh folder, the root
passed as a real-path string), its `decide`, `assert_allowed` and `assert_refused_naming_t` helpers. Copy what you
need or import `w2_42a_support`. T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may never write it);
A = `src/ok.py` (allowed).

## The behaviour to pin (the CTO's reopening of 2026-11-14 under DEC-1164 (18))
Bash takes a here-string `<<< word` anywhere in a simple command, like any redirect: the word after `<<<` is the
here-string's text (fed to the command's standard input), and the words after it are still that command's arguments.
So the rule: the word after `<<<` is the here-string's text, never the command's end; the words after it stay the
command's arguments, and their write targets are judged. The text given to `bash <<<` or `sh <<<` is a command and is
judged as one. Anything the guard still cannot read is refused (fail closed). Read-only forms stay free.

### R3: a write argument after a here-string is seen
Each with T (refused; the reason names T) and with A (allowed):
- `tee <<< "x" {w}`, `tee -a <<< "x" {w}`, `cp <<< x x.py {w}`
- `tee <<< "x" {w}; echo done` and `echo a && tee <<< "$v" {w}` (a here-string inside a list)
- `cat <<< "x" > {w}` (a redirect after a here-string; kept as a guard; it is refused for T today)

### The fallback's here-string forms
- `bash <<< 'touch {w}'`, `sh <<< 'touch {w}'` (the text is the shell's command) and `xargs touch <<< {w}` (xargs
  passes the text's words as the arguments of `touch`): refused for T, allowed for A. For T, assert the decision is
  deny and put the reason in the assertion message; do not require the reason to name T for these three.
- a here-string to a shell whose text the guard cannot know: `bash <<< "$X"` and `sh <<< "$(cat x.py)"` are refused
  (fail closed).
- a body-less heredoc after a `python3 -c` write: `python3 -c "open('{w}','w').write('x')"; cat <<EOF` and the same
  with `cat <<'EOF'` (the heredoc has no body and no end line): refused for T. Do not pin the A form (refusing it
  as unreadable is allowed).

### The read-only here-string forms stay free (guards)
Allowed: `grep -c b <<< "a"`, `wc -l <<< "$v"`, `tr a b <<< "x"`, `cat <<< "x"`, `read -r a b <<< "x y"`,
`grep x <<< tests/acceptance/X/zz.py` and `cat <<< tests/acceptance/X/zz.py` (the text names T but is data, not a
write), `bash <<< 'echo hi'` and `sh <<< 'ls src'` (a shell given a command that writes nothing).
If one of these is refused on your head, say so in your return and keep it out of the file (do not pin a form that is
refused today as a guard).

Check each form through real bash in `$TMPDIR` first (a scratch folder with `x.py`, `src/`, `tests/acceptance/X/`):
every write you name must be one bash performs, and each read-only form must write nothing. Name each test so it
states the behaviour (`test_r3_…`, `test_hstr_fallback_…`, `test_hstr_read_only_…`). No xfail marks.

## Red check (report it)
Run your file on your head (the unfixed parser). Expected, and say per group whether it held:
- RED (fail-open today: allow, want deny): the R3 T cases except `cat <<< "x" > T`; `bash <<<`, `sh <<<` and
  `xargs touch <<<` with T; `bash <<< "$X"` and `sh <<< "$(cat x.py)"`; the two body-less heredoc T cases.
- GREEN today (guards the fix must keep): every A case, `cat <<< "x" > T`, and every read-only form.
If a case expected red is green, or red for another reason, say so in your return. Run pytest only this way (one line,
TMPDIR is your sandbox's own `$TMPDIR`; make the folder first with `mkdir -p $TMPDIR/empty-home`):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_here_string.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Also run the whole folder once (same line, `tests/acceptance/W2-42a`, adding `-m "not local_only" -k "not real and not green_here and not time_limit"`)
and report its counts: nothing outside your new file may change. You may run any command through real bash in
`$TMPDIR` to confirm what bash writes; never write outside `$TMPDIR` and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts and the reason line of one R3 failure and one fallback failure; in `tests`: the case count per group
(R3, fallback, read-only) and which are red. A refusal twice for the same call by the guard, the sandbox or a hook:
stop and say so; never work around it. Search with Read and Grep only (no gov retrieve, no gov context in the
sandbox); search again once, in other words. Never open the evaluation sets' root or any hidden folder. No merge in
the sandbox. A resource gate's refusal is a wait.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer --budget 12000)

```json
