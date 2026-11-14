# Brief: independent test designer, W2-42a (DAEO-03ub), a here-string read as data must not hide a command it feeds (DEC-1164 (18), R3 F1, second batch)

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer: you write
tests from the behaviour stated here (DEC-136); you read no fix.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head 885b0d0f6.
Your paths: tests/acceptance/W2-42a/** only. Add a NEW file tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py and
update tests/acceptance/W2-42a/README.md (its map) in the SAME commit. Do not edit the other test files or fixtures.
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1164 (18), W2-42a R3 F1" --trailer "Implements: DEC-1028, DEC-958" -- tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py tests/acceptance/W2-42a/README.md`

## The product under test
The product guard `decide()` in `src/gov/guard/decide.py` reads a Bash call and refuses a write outside the role's
allowed paths; a write it cannot resolve becomes the target `/<guard-unresolvable>` and is refused (fail closed). Call
it exactly as tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py does (its `proj` fixture and helpers; copy what you
need). T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may never write it); A = `src/ok.py` (allowed).

## The decided rule (the CTO's F1 (a), DEC-1164 (18)), already pinned in test_w2_42a_here_string_ro.py
`read`, `mapfile` and `readarray` take a here-string as data, whatever its text; a loop's here-string
(`while read -r f; do …; done <<< "…"`) is data for the loop and the loop body's commands are judged by their own
words; their own writes are judged as usual. `bash`, `sh`, `zsh`, `dash`, `xargs`, `source`, `eval` and any reader not
named keep the fail-closed rule for a text the guard cannot know. **Nothing the guard refused before this rule becomes
allowed when real bash would write T.**

## The behaviour to pin (the lead's finding at 885b0d0f6; each writes T in real bash and is allowed at 885b0d0f6)
Taking the here-string as data is only safe while that data is not run. Two ways bash runs it:
1. **A command word taken from a variable the here-string fed.** When `read` (alone or as a loop's condition) binds a
   variable from a here-string, and a later word of the call uses that variable as a command's name (`$f`, `${f}`,
   `"$f" x`, `$a $b`, or after a prefix such as `env`, `command`, `time`), the guard cannot know the command: the call
   is refused (the unresolvable target), whatever the here-string's text. Forms:
   `while read -r f; do $f; done <<< 'touch {w}'`, `while read -r a b; do $a $b; done <<< 'touch {w}'`,
   `read -r a b <<< 'touch {w}'; $a $b`, `read -r a b <<< "$v"; $a $b`, `read -r a <<< "$v"; $a`,
   `while read -r l; do ${l}; done <<< "$v"`, `while read -r f; do "$f" x; done <<< "$v"`,
   `while read -r f; do env $f; done <<< "$v"`, `while read -r f; do command $f; done <<< "$v"`,
   `while read -r f; do time $f; done <<< "$v"`.
   Pin each with T and with A as refused (assert deny; do not require the reason to name a target).
2. **`mapfile`/`readarray` with a callback.** `-C <callback>` (also joined, `-tC <callback>`) makes bash run the
   callback as a command for each quantum of lines (`-c <n>`). The callback is a command: a literal callback is judged
   as that command (`mapfile -C 'touch {w}' -c 1 L <<< "$v"`, `readarray -tC 'touch {w}' -c1 L <<< "$v"`: T refused;
   for these the reason need not name T), and a callback the guard cannot know (`mapfile -C cb L <<< "$v"` where `cb`
   is a function or command it cannot read, `mapfile -t -C "$cb" L <<< "$v"`) is refused. Do not pin the A forms of the
   callback cases (refusing them as unreadable is allowed).

### Guards that must stay allowed (green at 885b0d0f6; keep them)
`while read -r f; do echo "$f"; done <<< "$v"`, `read -r a b <<< "$v"; echo "$a" "$b"`,
`while read -r f; do printf '%s\n' "$f"; done <<< "$(git status --porcelain)"`, `mapfile -t L <<< "$(ls)"`,
`readarray -t L <<< "$v"; echo "${L[0]}"`, `while read -r f; do grep -c x "$f"; done <<< "$(ls)"` (a variable used as
an argument of a command that writes nothing is not a command name), and `while read -r f; do cp "$f" src/; done <<<
"$(ls)"` is NOT a guard (cp to a folder named by its words: leave it out). Check each guard is allowed at your head; if
one is not, say so and leave it out.

Check each form through real bash in `$TMPDIR` first (a scratch folder with `x.py`, `src/`, `tests/acceptance/X/`, a
git repo if needed): each form in 1 and 2 with a literal `touch T` text or callback must write T in real bash (for the
`"$v"` forms, set `v='touch T'` in your bash check). Name tests so they state the behaviour
(`test_hsro2_read_var_command_…`, `test_hsro2_callback_…`, `test_hsro2_guard_…`). No xfail marks.

## The README map (same commit)
Add the new file as td-8 did for test_w2_42a_here_string_ro.py: a file-list entry (td-9, 2026-11-14, R3 F1 second
batch), each test function under the KPI line it proves by full `file.py::test_name` (the refused forms under F1 and F2,
as td-8 placed its fail-closed cases; the guards under S1), and a round-table row with the groups, counts and
"Red on 885b0d0f6: N failed, M passed". Check the map reads (`mkdir -p $TMPDIR/empty-home` first):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src python3 -c "import pathlib; from gov.accept import runner; print({k: len(v) for k, v in runner.parse_map(pathlib.Path('tests/acceptance/W2-42a/README.md').read_text()).items()})"`
(never run gov accept itself in the sandbox).

## Red check (report it)
Run your file at your head 885b0d0f6. Expected: RED = every form in 1 (T and A) and the literal and unknown callback
forms in 2; GREEN = the guards. Say per group whether it held. Run pytest only this way (one line):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Also run the whole folder once (same line, `tests/acceptance/W2-42a`, adding `-n auto -m "not local_only" -k "not real and not green_here and not time_limit"`)
and report its counts: nothing outside your new file may change (the folder is green at 885b0d0f6). The heavy slot may
queue: that is a wait. Anything longer than one line goes in a script file under `$TMPDIR`, run with bash or python3
(a unique heredoc delimiter if you write one). Never write outside `$TMPDIR` and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts, one failure's reason line per group, and the map reader's output line; in `tests`: the case count per
group and which are red. A refusal twice for the same call by the guard, the sandbox or a hook: stop and say so; never
work around it. Search with Read and Grep only (no gov retrieve, no gov context in the sandbox); search again once, in
other words. Never open the evaluation sets' root or any hidden folder. No merge in the sandbox. A resource gate's
refusal is a wait.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer --budget 12000)

```json
