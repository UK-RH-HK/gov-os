# Brief: independent test designer, W2-42a (DAEO-03ub), read-only here-string forms with an expanded text (DEC-1164 (18), R3 F1)

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer: you write
tests from the behaviour stated here (DEC-136); the engineer starts after you and you read no fix (none exists yet).
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head 209ec8464.
Your paths: tests/acceptance/W2-42a/** only. Add a NEW file tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py and
update tests/acceptance/W2-42a/README.md (its map) in the SAME commit. Do not edit the other test files or fixtures.
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1164 (18), W2-42a R3 F1" --trailer "Implements: DEC-1028, DEC-958" -- tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py tests/acceptance/W2-42a/README.md`

## The product under test
The product guard `decide()` in `src/gov/guard/decide.py` reads a Bash call and refuses a write outside the role's
allowed paths; a write it cannot resolve becomes the target `/<guard-unresolvable>` and is refused (fail closed). Call
it exactly as tests/acceptance/W2-42a/test_w2_42a_here_string.py does: its `proj` fixture (an in-progress engineer
ticket DAEO-03ub allowing `src/**`, the session variables removed, HOME a fresh folder, the root passed as a real-path
string), its `decide`, `assert_allowed`, `assert_refused_naming_t` and `assert_refused` helpers. Copy what you need.
T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may never write it); A = `src/ok.py` (allowed).

## Why (the narrow check's F1, docs/probes/DAEO-03ub/PR-DAEO-03ub-r3.md lines 99 to 115)
The R3 round made a here-string whose text the shell expands (`"$v"`, `"$(…)"`) fail closed for any reader not on a
short data list. That refuses everyday read-only idioms: `read -r a <<< "$v"`, `while read -r f; do …; done <<<
"$(git status --porcelain)"`, `mapfile -t L <<< "$(ls)"`, `sed 's/a/b/' <<< "$v"`, `bc <<< "$x + 1"`. The CTO decided
(F1 (a), DEC-1164 (18)) the rule below, to be built before the land.

## The behaviour to pin (the decided rule)
1. `read`, `mapfile` and `readarray` take a here-string as data, whatever its text. Their own writes, if any (e.g. a
   redirect), are judged as usual.
2. A loop's here-string (`while read -r f; do …; done <<< "$(…)"`) is data for the loop; the loop body's commands are
   judged by their own words.
3. Data readers that never run their input (`sed`, `awk` without `system(`/`>`/`|` in its script, `bc`, `grep`, `wc`,
   `cut`, `tr`, `sort`) take an expanded text as data. A reader whose script writes (an `awk` script with `>` or
   `system(`, `sed` with `w` or `-i`) is judged on that script, as today.
4. `bash`, `sh`, `zsh`, `dash`, `xargs`, `source`, `eval` and any reader not named above keep R3's fail-closed rule for
   an unknown text.
5. Nothing that R3's cases refuse becomes allowed. A `$(…)` inside the here-string's text still runs, so its writes
   are still judged.

### Group RO: read-only forms allowed (each red today: refused as `/<guard-unresolvable>`)
`read -r a <<< "$v"`; `IFS=: read -r a b <<< "$line"`; `read -r a b <<< "$(git rev-parse HEAD HEAD)"`;
`v=$(git log -1); read -r a <<< "$v"`; `mapfile -t L <<< "$(ls)"`; `readarray -t L <<< "$v"`;
`while read -r f; do echo "$f"; done <<< "$(git status --porcelain)"`; `sed 's/a/b/' <<< "$v"`;
`awk '{print $1}' <<< "$line"`; `bc <<< "$x + 1"`. Add your own variants of the same rule if you like (e.g.
`read -ra arr <<< "$v"`, `until read …; do …; done <<< "$v"`, `while IFS= read -r l; do printf '%s\n' "$l"; done <<<
"$v"`), each checked red today. Guards already green today, keep them in the group as guards: `grep x <<< "$v"`,
`wc -l <<< "$(ls)"`, `cut -d: -f1 <<< "$v"`, `tr a b <<< "$v"`, `sort <<< "$v"`.

### Group RW: the same forms with a write (T refused, its reason naming T; A allowed)
`read -r a <<< "$v" > {w}`; `mapfile -t L <<< "$v"; touch {w}`; `while read -r f; do touch {w}; done <<< "$(ls)"`;
`while read -r f; do cp "$f" {w}; done <<< "$v"`; `sed 's/a/b/' <<< "$v" > {w}`; `sort -o {w} <<< "$v"`;
`read -r a <<< "$(touch {w})"`; `while read -r f; do echo "$f"; done <<< "$(touch {w})"`;
`sed 's/a/b/' <<< "$(touch {w})"`. Today each T form is refused naming T (green, keep as guards) and each A form but
`sort -o` is refused as `/<guard-unresolvable>` (red, wanted allowed).

### Group FC: R3's fail-closed forms stay refused (green today; guards)
Assert deny (do not require the reason to name a target): `bash <<< "$v"`, `sh <<< "$(cat x.py)"`, `zsh <<< "$v"`,
`dash <<< "$v"`, `xargs touch <<< "$v"`, `source /dev/stdin <<< "$v"`, `. /dev/stdin <<< "$v"`, `eval "$v"`,
`python3 <<< "$v"`, `perl <<< "$v"` (a reader not named), `awk '{print}' <<< "$(cat x)" | sh`,
`while read -r f; do bash -c "$f"; done <<< "$v"` (the loop body's own command cannot be read),
`while read -r f; do eval "$f"; done <<< "$v"`, and the writing scripts with T: `awk '{print > "tests/acceptance/X/zz.py"}' <<< "$v"`,
`awk '{system("touch tests/acceptance/X/zz.py")}' <<< "$v"`, `sed 'w tests/acceptance/X/zz.py' <<< "$v"`, `sed -i 's/a/b/' tests/acceptance/X/zz.py <<< "$v"`. Do not pin the A
forms of the writing `awk`/`sed` scripts (refusing them as unreadable is allowed).

Check each form through real bash in `$TMPDIR` first (a scratch folder with `x.py`, `src/`, `tests/acceptance/X/`, a
git repo if a form needs one): every write you name must be one bash performs, and each RO form must write no file.
If a form in RO is not refused today, keep it as a guard and say so; if a form in FC or a T form in RW is allowed
today, say so in your return and keep it out of the file. Name each test so it states the behaviour
(`test_hsro_read_only_…`, `test_hsro_write_…`, `test_hsro_fail_closed_…`). No xfail marks.

## The README map (same commit)
`gov accept W2-42a` reads the folder's README map to place each case under a KPI line. Add the new file as the R3
round did for `test_w2_42a_here_string.py` (read the README: its file list near line 127, the S1, F1 and F2 rows of the
KPI table near lines 145 to 157, and the round table near line 179): a file-list entry (td-8, 2026-11-14, R3 F1, the
read-only here-string forms with an expanded text); each test function under the KPI line it proves, by full
`file.py::test_name` (RO and the A forms where the README puts the read-only guards (S1); the T writes under F1; the
FC forms under F2); a round-table row with the groups, counts and the red line "Red on 209ec8464: N failed, M passed".
Then check the map reads (one line; `mkdir -p $TMPDIR/empty-home` first):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src python3 -c "import pathlib; from gov.accept import runner; print({k: len(v) for k, v in runner._read_map(pathlib.Path('tests/acceptance/W2-42a/README.md').read_text()).items()})"`
(if that function has another name, read src/gov/accept/runner.py near lines 66 to 210 for the map reader; never run
gov accept itself in the sandbox).

## Red check (report it)
Run your file on your head (the unfixed parser). Expected: RED = every RO form above but the five named guards, and
every A form of RW but `sort -o`; GREEN = the five RO guards, every T form of RW, `sort -o A`, every FC form. Say per
group whether it held; if a case expected red is green, or red for another reason, say so. Run pytest only this way
(one line, TMPDIR is your sandbox's own `$TMPDIR`):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Also run the whole folder once (same line, `tests/acceptance/W2-42a`, adding `-n auto -m "not local_only" -k "not real and not green_here and not time_limit"`)
and report its counts: nothing outside your new file may change. The heavy slot may queue: that is a wait. Anything
longer than one line goes in a script file under `$TMPDIR`, run with bash or python3 (a unique heredoc delimiter if
you write one). Never write outside `$TMPDIR` and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts, the reason line of one RO failure and one RW failure, and the map reader's output line; in `tests`: the
case count per group (RO, RW, FC) and which are red. A refusal twice for the same call by the guard, the sandbox or a
hook: stop and say so; never work around it. Search with Read and Grep only (no gov retrieve, no gov context in the
sandbox); search again once, in other words. Never open the evaluation sets' root or any hidden folder. No merge in
the sandbox. A resource gate's refusal is a wait.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer --budget 12000)

```json
