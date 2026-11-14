Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: engineer, W2-42a (DAEO-03ub), a here-string read as data must not hide a command it feeds (DEC-1164 (18), R3 F1, second batch)

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh engineer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head 98eff3c84.
Your paths: src/gov/guard/bash_writes.py and src/gov/guard/decide.py (the fix); tests/unit/guard/test_w2_42a* for unit
cases of what you change; one short paragraph in docs/changes/W2-42a-evidence.md. Nothing else changes. Never
tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The decided scope (the CTO's answer to the narrow check's F1, DEC-1164 (18): F1 (a))
The R3 round made a here-string whose text the shell expands (`"$v"`, `"$(…)"`) fail closed for any reader not on a
short data list, which refuses everyday read-only idioms. The rule to build:
1. `read`, `mapfile` and `readarray` take a here-string as data, whatever its text. Their own writes, if any (e.g. a
   redirect), are judged as usual.
2. A loop's here-string (`while read -r f; do …; done <<< "$(…)"`) is data for the loop; the loop body's commands are
   judged by their own words.
3. Data readers that never run their input (`sed`, `awk` without `system(`/`>`/`|`, `bc`, `grep`, `wc`, `cut`, `tr`,
   `sort`) take an expanded text as data. A reader whose script writes (an `awk` script with `>` or `system(`, `sed`
   with `w`/`-i`) is judged on that script, as today.
4. `bash`, `sh`, `zsh`, `dash`, `xargs`, `source`, `eval` and any reader not named above keep R3's fail-closed rule for
   an unknown text.
5. Nothing that R3's cases refuse becomes allowed; a `$(…)` inside a here-string's text still runs, so its writes are
   still judged. Fail closed: no form that gave a target, the unresolvable target or a refusal on 98eff3c84 gives
   neither after your change, except the read-only forms above. DEC-409's rule is unchanged (no agent Bash call holds
   the lift form of `gov pause` (--off)); its existing cases stay green (grep tests/ for `lift_refusal` and `DEC-409`).
**The second batch (the lead's finding at 885b0d0f6: each form writes T in real bash and is allowed there).** Taking a
here-string as data is safe only while that data is not run. (a) When `read` (alone or as a loop's condition) binds a
variable from a here-string and a later word of the call uses that variable as a command's name (`$f`, `${f}`,
`"$f" x`, `$a $b`, or after a prefix such as `env`, `command`, `time`), the guard cannot know the command: the
unresolvable target, whatever the text. A variable used only as an argument of a command that writes nothing stays
free. (b) `mapfile`/`readarray -C <callback>` (also joined, `-tC`) runs the callback as a command: a literal callback is
judged as that command; one the guard cannot know gives the unresolvable target.
Fix it in src/gov/guard/bash_writes.py (and decide.py only if needed). Nothing else changes.

## The failing output (and nothing else)
tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py on 98eff3c84: `17 failed, 6 passed in 0.28s`.

```
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused[loop-read-then-run-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused[loop-read-two-then-run-a-b]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused[read-two-then-run-a-b]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path[loop-read-then-run-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path[loop-read-two-then-run-a-b]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path[read-two-then-run-a-b]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[read-two-from-v-then-run-a-b]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[read-from-v-then-run-a]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[loop-run-braced-l]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[loop-run-quoted-f-with-an-argument]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[loop-env-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[loop-command-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[loop-time-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_literal_callback_that_writes_t_is_refused[mapfile-literal-callback]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_literal_callback_that_writes_t_is_refused[readarray-joined-tC-literal-callback]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused[mapfile-callback-a-function-the-guard-cannot-read]
FAILED tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused[mapfile-callback-from-a-variable]
```

One full failure block per test function:

```
_ test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused[loop-read-then-run-f] _

proj = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_read_var_command_a_0/proj'
template = "while read -r f; do $f; done <<< 'touch {w}'"

    @pytest.mark.parametrize("template", V_LITERAL_FORMS)
    def test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused(proj, template):
>       assert_refused(template.replace("{w}", T), proj)

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:123: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

command = "while read -r f; do $f; done <<< 'touch tests/acceptance/X/zz.py'"
root = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_read_var_command_a_0/proj'

    def assert_refused(command, root):
        """Refused, whatever the reason (the reason is in the message)."""
        got, why = decide(command, root)
>       assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"
E       AssertionError: want deny, got allow: 
E         --- the command ---
E         while read -r f; do $f; done <<< 'touch tests/acceptance/X/zz.py'
E       assert 'allow' == 'deny'
E         
E         - deny
E         + allow

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:116: AssertionError

_ test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path[loop-read-then-run-f] _

proj = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_read_var_command_a_3/proj'
template = "while read -r f; do $f; done <<< 'touch {w}'"

    @pytest.mark.parametrize("template", V_LITERAL_FORMS)
    def test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path(proj, template):
        # the guard cannot know the command the variable names, so it refuses whatever the text says
>       assert_refused(template.replace("{w}", A), proj)

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:129: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

command = "while read -r f; do $f; done <<< 'touch src/ok.py'"
root = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_read_var_command_a_3/proj'

    def assert_refused(command, root):
        """Refused, whatever the reason (the reason is in the message)."""
        got, why = decide(command, root)
>       assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"
E       AssertionError: want deny, got allow: 
E         --- the command ---
E         while read -r f; do $f; done <<< 'touch src/ok.py'
E       assert 'allow' == 'deny'
E         
E         - deny
E         + allow

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:116: AssertionError

_ test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused[read-two-from-v-then-run-a-b] _

proj = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_read_var_command_a_6/proj'
command = 'read -r a b <<< "$v"; $a $b'

    @pytest.mark.parametrize("command", V_UNKNOWN_FORMS)
    def test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused(proj, command):
>       assert_refused(command, proj)

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:134: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

command = 'read -r a b <<< "$v"; $a $b'
root = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_read_var_command_a_6/proj'

    def assert_refused(command, root):
        """Refused, whatever the reason (the reason is in the message)."""
        got, why = decide(command, root)
>       assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"
E       AssertionError: want deny, got allow: 
E         --- the command ---
E         read -r a b <<< "$v"; $a $b
E       assert 'allow' == 'deny'
E         
E         - deny
E         + allow

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:116: AssertionError

_ test_hsro2_callback_a_literal_callback_that_writes_t_is_refused[mapfile-literal-callback] _

proj = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_callback_a_literal_0/proj'
template = 'mapfile -C \'touch {w}\' -c 1 L <<< "$v"'

    @pytest.mark.parametrize("template", CB_LITERAL_FORMS)
    def test_hsro2_callback_a_literal_callback_that_writes_t_is_refused(proj, template):
>       assert_refused(template.replace("{w}", T), proj)

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:141: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

command = 'mapfile -C \'touch tests/acceptance/X/zz.py\' -c 1 L <<< "$v"'
root = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_callback_a_literal_0/proj'

    def assert_refused(command, root):
        """Refused, whatever the reason (the reason is in the message)."""
        got, why = decide(command, root)
>       assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"
E       AssertionError: want deny, got allow: 
E         --- the command ---
E         mapfile -C 'touch tests/acceptance/X/zz.py' -c 1 L <<< "$v"
E       assert 'allow' == 'deny'
E         
E         - deny
E         + allow

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:116: AssertionError

_ test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused[mapfile-callback-a-function-the-guard-cannot-read] _

proj = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_callback_a_callback0/proj'
command = 'mapfile -C cb L <<< "$v"'

    @pytest.mark.parametrize("command", CB_UNKNOWN_FORMS)
    def test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused(proj, command):
>       assert_refused(command, proj)

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:146: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

command = 'mapfile -C cb L <<< "$v"'
root = '/tmp/w242a-lead/tmp/pytest-of-usain/pytest-1/test_hsro2_callback_a_callback0/proj'

    def assert_refused(command, root):
        """Refused, whatever the reason (the reason is in the message)."""
        got, why = decide(command, root)
>       assert got == "deny", f"want deny, got {got}: {why}\n--- the command ---\n{command}"
E       AssertionError: want deny, got allow: 
E         --- the command ---
E         mapfile -C cb L <<< "$v"
E       assert 'allow' == 'deny'
E         
E         - deny
E         + allow

tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py:116: AssertionError
```

## Done when
- tests/acceptance/W2-42a passes whole (the 23 cases of test_w2_42a_here_string_ro_2.py, the 53 of test_w2_42a_here_string_ro.py and
  every other file there; no case green on 98eff3c84 turns red).
- tests/unit/guard and tests/unit/hooks pass, and DEC-409's lift cases wherever they live.
- One short paragraph in docs/changes/W2-42a-evidence.md naming the fix (DEC-1164 (18), R3 F1, second batch) and the counts (add to the F1 paragraph already there).

## How to run (every pytest through the heavy slot; TMPDIR is your sandbox's own $TMPDIR; /tmp is read-only)
    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"
(mkdir -p $TMPDIR/empty-home first.) The heavy slot may queue: that is a wait. Anything longer than one line goes in a
script file under $TMPDIR, run with bash or python3; use a unique heredoc delimiter if you write one. Literal paths as
write targets. Search with Read and Grep (no gov retrieve or gov context in the sandbox); search again once in
different words if the first does not answer. Never open the evaluation sets' root or any hidden folder; never print
a secret. If something is refused twice, stop and say so; never work around a refusal. No merge in the sandbox. A
resource gate's refusal is a wait.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (the pytest summary lines) / tests: / discoveries: /
risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers.

## The ticket's context packet (gov context DAEO-03ub --role engineer --budget 12000)

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
