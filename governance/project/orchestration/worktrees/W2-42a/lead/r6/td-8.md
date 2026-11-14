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
{
  "ticket": "DAEO-03ub",
  "ticket_text": "---\nid: DAEO-03ub\nstatus: in_progress\ndeps: []\nlinks: [DAEO-fau3]\ncreated: 2026-11-02T10:58:34Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-42a\ntags: [wave-2, implementation, guard, full]\nwbs_id: W2-42a\ntitle: 'The product''s guard reads what a Bash command writes: ACT-GUARD-FIX-3''s eight parser lines in src/gov/guard, before EXAMIN''s copy (DEC-1028 item 4)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- docs/probes/DAEO-03ub/**  # the probe record (the resume after the emergency, DEC-1158; CTO)\n- src/gov/guard/decide.py\n- src/gov/guard/reads.py\n- src/gov/guard/bash_writes.py\n- tests/unit/guard/test_w2_42a*\n- docs/changes/W2-42a-evidence.md\n- tests/unit/guard/test_decide.py\nkpis:\n  success:\n  - 'A heredoc''s body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body''s `$(\u2026)` is text, an unquoted body''s `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body''s `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body''s `$(\u2026)`, fails them'\n  - 'A variable the command sets once at its top level, before any use, is expanded; a literal `for` loop''s words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them'\n  - '`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command''s name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command''s name gives no write and fails them'\n  - 'An unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both'\n  - '`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them'\n  - 'The read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc''s body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body''s `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them'\n  - 'A backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them'\n  - 'A data heredoc''s body written to a file that a later word of the command may run is judged as that file''s code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them'\n  - 'Measured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product''s parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer''s record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it'\n  - 'The read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them'\n  - 'Replayed against every refusal in the CTO''s `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it'\n  failure:\n  - 'Any write the parser misses that today''s parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write'\n  - 'An unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them'\nprofile: FULL\nsources:\n- DEC-1040\n- DEC-1028\n- DEC-1027\n- DEC-958\n- DEC-953\n- DEC-1044\nest_loc: 600\nacceptance_tests:\n  path: tests/acceptance/W2-42a/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows: []\n---\n# W2-42a The product's guard reads what a Bash command writes\n\nThe owner's DEC-1028 item 4 (P1-GUARD-PARSER-W2 (a)): ACT-GUARD-FIX-3 fixed this repository's five-rule hook\n(`.claude/hooks/bash_writes.py`, `e662684a`), but the product's guard, which every adopted repository runs, keeps the\nold parser (`_extract_bash_write_targets` in `src/gov/guard/decide.py`; `_set_aside` and `_Judge.tool`/`command` in\n`src/gov/guard/reads.py`) and refuses the writes of 22 of the 61 logged commands it cannot resolve. EXAMIN's agents\nwould meet those refusals. This ticket brings the eight parser lines (ACT-GUARD-FIX-3 \u00a77) into the product, before\nEXAMIN's copy. The engineer may port the reviewed `bash_writes.py` as its basis (a new `src/gov/guard/bash_writes.py`\nmodule); the test designer works from the KPIs and may take the package's planted cases and the logged corpus as\nfixtures (no secrets in them). W2-42 (`DAEO-fau3`) keeps its other rows in Wave 3. W2-09 and W2-10 hold\n`src/gov/guard/**`: start beside W2-09 only with the files split, or after it. Once it lands, the five-rule hook can\ncall the product's parser and `bash_writes.py` slims away (a later ACT).\n\n**Reopened 2026-11-13 by the CTO under DEC-1164 (18) (DEC-1174 (1), a P2 listed for the owner's reading).** A defect\ninside this ticket's scope: a Bash call whose heredoc body (to a shell) holds a comment with an apostrophe\n(`bash <<'EOF'` / `# it's fine` / `ls` / `EOF`) is refused whole, \"the command cannot be read\", although it writes\nnothing; the same body without the comment is allowed. It fails closed (the four F1 reversal calls of ACT-GUARD-FIX-5's\nround-2 review stay refused), but it refuses ordinary work, and the live hook is to copy this parser (DEC-1174 (1)).\nThe fix: comment text in a shell body is dropped before the body is tokenised (a `#` that starts a word, outside\nquotes, to the end of its line), so an apostrophe there is no unclosed quote; a body still unreadable after that stays\nrefused. A test designer adds the cases (the harmless forms allowed; the F1 reversal calls and a body that writes into\n`tests/acceptance/` after such a comment still refused), the engineer fixes `bash_writes.py`, then a narrow independent\ncheck of that change only.\n\n**Reopened 2026-11-14 by the CTO under DEC-1164 (18) (a P2 listed for the owner's reading): R3 and the fallback's here-string forms.** A defect inside this ticket's scope, found by its own apos-2 check: the line parser splits a command at `<<`/`<<<` (`decide.py` `_line_write_targets`), so a write argument after a here-string is missed (`tee <<< \"x\" T`, `tee -a <<< \"x\" T`): ordinary work yes, fails open. The same check named three older fail-opens in the unreadable fallback: `bash <<< 'touch T'`, `xargs touch <<< T`, and a body-less heredoc after a `python3 -c` write. The live hook is to copy this parser (DEC-1174 (1)), so they are fixed before that ACT. The fix: the word after `<<<` is the here-string's text (judged, as a `bash <<<`/`sh <<<` body is a command), never the command's end; the words after it stay the command's arguments; anything still unreadable fails closed. A test designer adds the cases, the engineer fixes `src/gov/guard/` within these paths, then a narrow independent check of that change only (DEC-1154).\n",
  "authority": [
    {
      "id": "DEC-1040",
      "sha256": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "reason": "declared in sources",
      "tokens": 551
    },
    {
      "id": "DEC-1028",
      "sha256": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "reason": "declared in sources",
      "tokens": 692
    },
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1044",
      "sha256": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "reason": "declared in sources",
      "tokens": 328
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1040",
      "sha256": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "reason": "declared in sources",
      "tokens": 551
    },
    {
      "id": "DEC-1028",
      "sha256": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "reason": "declared in sources",
      "tokens": 692
    },
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1044",
      "sha256": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "reason": "declared in sources",
      "tokens": 328
    }
  ],
  "supplementary": [],
  "supplementary_query": "The product's guard reads what a Bash command writes: ACT-GUARD-FIX-3's eight parser lines in src/gov/guard, before EXAMIN's copy (DEC-1028 item 4)\nA heredoc's body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body's `$(\u2026)` is text, an unquoted body's `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body's `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body's `$(\u2026)`, fails them\nA variable the command sets once at its top level, before any use, is expanded; a literal `for` loop's words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them\n`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command's name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command's name gives no write and fails them\nAn unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both\n`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them\nThe read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc's body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body's `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them\nA backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them\nA data heredoc's body written to a file that a later word of the command may run is judged as that file's code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them\nMeasured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product's parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer's record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it\nThe read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them\nReplayed against every refusal in the CTO's `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it\nAny write the parser misses that today's parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write\nAn unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 8371,
  "budget": {
    "limit": 12000,
    "used": 8371
  },
  "hash": "141f2126b20ca6f07255d22be529a159a87f9ead341b885efe7a7e12fbbff0ab"
}

```
