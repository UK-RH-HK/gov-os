# W1-50, the freeze half: acceptance tests for three KPI lines (DEC-402, DEC-399)

Ticket `DAEO-xnbx` (W1-50), profile FULL, branch `w1/W1-50-freeze`. Written before implementation by the Independent
Test Designer (MR-3). This file covers only the three KPI lines the owner added on 2026-10-05. The ticket's other lines
(containment by commit trailers) are in `README.md` of this folder, by another designer, on another branch.

Files of this half: `w1_50_freeze_support.py`, `test_w1_50_freeze_marker.py`, `test_w1_50_freeze_guard_reading.py`,
`test_w1_50_freeze_launcher.py`, `test_w1_50_freeze_fixture_settings.py`, and this file. A second batch, from the
findings of a review (DEC-136), added `test_w1_50_freeze_records_file.py`, `test_w1_50_freeze_near_spellings.py`,
`test_w1_50_freeze_pause_links.py` and `test_w1_50_freeze_live_pause.py`: see "The second batch" below.

A third batch brought the cases to DEC-404 and repaired the second live case: see "The third batch" below.

A fourth batch added two cases on `gov pause --rollback` and the flag: see "The fourth batch" below.

A fifth batch, on 2026-10-06, covers KPI success lines 3 to 7 (DEC-409, DEC-407): who lifts a freeze. It added
`w1_50_freeze_lift.py`, `test_w1_50_freeze_lift_ancestry.py`, `test_w1_50_freeze_lift_terminal.py`,
`test_w1_50_freeze_lift_guard_rule.py` and `test_w1_50_freeze_flag_comparison.py`: see "The fifth batch" below.

The whole half now: 245 cases, 243 run without a session and 2 are live. Run on 2026-10-06 before the fifth batch's
implementation: 106 red and 137 green. The red cases are 104 of the fifth batch's 132 and the 2 earlier cases of this
half that lift a freeze (revised, see the fifth batch). The fourth batch's 2 cases are green since `gov pause
--rollback` sets the flag again. The table below is the third batch's, run with `gov pause` unchanged (16 red and 93
green; every red case waited for `gov pause`); those 16 are green now.

| File | Cases | Red now | Green now |
|---|---|---|---|
| `test_w1_50_freeze_marker.py` | 11 | 10 | 1 |
| `test_w1_50_freeze_guard_reading.py` | 33 | 0 | 33 |
| `test_w1_50_freeze_launcher.py` | 16 and 1 live | 0 | 16 |
| `test_w1_50_freeze_fixture_settings.py` | 10 | 0 | 10 |
| `test_w1_50_freeze_records_file.py` | 10 | 0 | 10 |
| `test_w1_50_freeze_near_spellings.py` | 22 | 0 | 22 |
| `test_w1_50_freeze_pause_links.py` | 7 | 6 | 1 |
| `test_w1_50_freeze_live_pause.py` | 1 live | not run here | |
| **All** | **109 and 2 live** | **16** | **93** |

## How the tests run

- **Every test builds its own temporary project.** Nothing creates, writes or removes `.gov-runtime/freeze` of this
  worktree, and `gov pause` is never run on it.
- **The guard** is asked as W1-02's suite asks it: the kernel's PreToolUse hook as a process, one JSON object on
  stdin, in W1-02's fixture project. Both readers of the flag sit behind that one command.
- **`gov pause`** is run as W1-28's suite runs it: the command line with `--json`, this worktree's `src/`, a temporary
  project as `--root`.
- **`gov launch`** is read as W1-46's suite reads it: the `--settings` value a stand-in CLI is started with.
- **The whole-tree fixtures** are run on a synthetic source repository with a settings file made up in the test.
  This repository's own settings file and held-out file are never opened.
- Run: `python3 -m pytest tests/acceptance/W1-50 -q -p no:cacheprovider -m "not local_only"`. About 25 s for this
  half now that the four named-pipe cases of the second batch are green. The `local_only` mark is not registered for this folder (its `conftest.py` is the other half's), so pytest
  prints one "unknown mark" warning; the selection works.
- **Two live cases** (`local_only`) each start a real engineer session through `gov launch`. A launched test
  designer cannot run them (the sandbox refuses the API host): the ticket lead runs them, with `-m local_only`.

## The three KPI lines

70 cases when the first batch was written: 69 run without a session, 1 is live. Before implementation 30 were red
and 39 green. The table is that batch's; the counts of today are in the table at the top.

| KPI line | File | Cases | Red before implementation, and why |
|---|---|---|---|
| **1.** "A freeze flag set by gov pause carries a marker line" | `test_w1_50_freeze_marker.py` | 11 | 10 red: `gov pause` leaves an empty file, so the first line is not the marker line. Green: a refused caller writes no flag. |
| **1.** "the guard treats an empty file, or one without the marker, at the flag's path as no freeze" | `test_w1_50_freeze_guard_reading.py`: `test_what_is_not_a_marked_flag_does_not_freeze` (5), `test_a_marked_flag_and_what_the_guard_cannot_read_freeze` (13), `test_a_freeze_ends_when_the_marker_goes` (1), `test_the_install_rule_reads_the_flag_as_the_guard_does` (5) | 24 | 7 red: the guard and the install rule freeze on anything that exists at the path (`os.path.exists`). 1 more red: a dangling link is not read as frozen today. Green: nothing at the path, and the 12 shapes that already freeze by existing. |
| **1.** "and records its presence" | same file: `test_an_unmarked_presence_is_recorded` (4), `..._is_a_record_and_not_a_finding`, `..._recorded_once_for_each_call`, `test_nothing_is_recorded_when_nothing_is_at_the_path`, the two `test_a_records_file_that_cannot_be_written_...` | 9 | 7 red: the call is denied as frozen, so nothing is recorded. Green: nothing at the path leaves no record; an unwritable records file does not lift a real freeze. |
| **2.** "gov launch does not deny the freeze flag's path when the flag does not exist at launch" | `test_w1_50_freeze_launcher.py`: the built settings (9) | 9 | 5 red: `_runtime_rules` always adds the flag's name, so a literal `Edit` rule names it. Green: a marked flag at launch keeps its rule; the patterns still cover the path; the other by-name rules are unchanged. |
| **2.** "so a launched session leaves no placeholder there" | same file: `test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path` (live) | 1 | Not run here. Expected red: a placeholder is seen at the path while the session's Bash runs. |
| **2.** what the guard still holds without the literal rule | same file: `test_the_guard_denies_a_worker_s_write_to_the_flag_s_path` (6) | 6 | Green today and must stay green: two worker roles, three states of the path, Write, Edit and eleven Bash forms each. |
| **3.** "Every test fixture that copies the whole tree strips the held-out deny line from the copied settings file" | `test_w1_50_freeze_fixture_settings.py` | 10 | Green now: test code about test code, with the two fixtures revised in this batch. |

Success and failure of each line:

- **Line 1.** Success: the marker after each way of pausing; an unmarked presence does not freeze and is recorded.
  Failure: a refused caller writes no marker; a marked flag still freezes in every spelling; an unwritable records
  file neither blocks an unfrozen call nor lifts a freeze; a pause over a placeholder is a real pause.
- **Line 2.** Success: no literal rule when nothing is at the path. Failure: a real flag at launch loses its rule; the
  file tools lose the pattern; another name loses its rule.
- **Line 3.** Success: both fixtures strip the rules, in the working tree and in the commit. Failure: a copy that
  keeps them is caught; the rest of the file is changed; a file with nothing to strip is rewritten.

## The readings pinned, with their sources

### The marker

| Point | Reading | Source |
|---|---|---|
| The word | `FROZEN` | DEC-402: "(for example `FROZEN`, with who and when)". The owner's own example is taken. |
| Who | `owner` when `GOV_ROLE` is unset, `orchestrator` otherwise | DEC-365; DEC-378 uses the same two names for the `Role:` trailer |
| When | UTC, `YYYY-MM-DDTHH:MM:SSZ`; the form is tested, never the value | the form the project's records use: `src/gov/guard/containment.py:432` |
| The first line `gov pause` writes | `FROZEN <who> <when>`, single spaces | DEC-404 (on package DP-F3, option a). The three parts are DEC-402's. |
| Which commands write it | plain pause, `--cancel-agents`, `--rollback` (also when the rollback fails) | DEC-368, DEC-378 |
| A pause over an unmarked file | it becomes a real, marked flag | DEC-402: only a marked flag freezes; W1-28: a successful pause freezes |
| A second pause | succeeds, the first line is still a marker line; whether it is rewritten is not pinned | W1-28 `test_pause_on_a_paused_project_succeeds_and_stays_paused` |
| `--off` | as W1-28 holds it; not tested again here | DEC-365 |

### What the guard does with each shape at the flag's path

The rule behind the table: **frozen when a marker line is found, or when something is at the path that the guard
cannot read as a file; no freeze otherwise.** "Stricter where the guard cannot tell" is DEC-179 (a guard that fails open
is a defect) and the brief's rule; the two shapes the sandbox itself makes must not freeze (the observation of
2026-10-05; `bootstrap.md`, "Observations from launched worker sessions").

| Shape | Reading | Recorded | Source |
|---|---|---|---|
| nothing at the path | no freeze | no | DEC-109 |
| an empty regular file (0444: the placeholder seen outside the sandbox) | no freeze | yes | DEC-402 |
| text without the marker | no freeze | yes | DEC-402 |
| the marker line, alone or followed by anything | frozen | | DEC-402; W1-02: what follows is not read |
| the marker line after other lines | frozen | | stricter: the file carries a marker line |
| a symbolic link to a marked file | frozen | | read through the link |
| a symbolic link to an unmarked file | no freeze | yes | DEC-402: read through the link, it is a file without the marker. The guard can tell. |
| a character device (a link to `/dev/null` in the test) | no freeze | yes | what a session sees inside the sandbox; it reads as empty |
| a directory | frozen | | cannot be read as a file; as today |
| a dangling symbolic link | frozen | | something is there and cannot be read. **A change:** today it is no freeze. |
| a file the guard may not open (mode 000, non-empty) | frozen | | cannot be read; as today |
| a byte-order mark before the marker; CRLF line ends; another letter case; blank lines before it; trailing spaces; a very large file with the marker first | frozen | | the stricter reading of a near spelling |

Not pinned: an empty file the guard may not open; a FIFO or a socket at the path (see "Notes for the engineer"). The
word `FROZEN` inside a line that starts with another word was not pinned by the first batch; the second batch pins it
as frozen (below).

### The record

| Point | Reading | Source |
|---|---|---|
| Where | `.gov-runtime/records.jsonl` | DEC-177: a record of something permitted goes there, and "`findings.jsonl` and its action list are unchanged". DEC-402 calls it an observation, not a finding. |
| Fields | DEC-122's ten (`time`, `session_id`, `agent_type`, `role`, `ticket`, `tool`, `command`, `paths`, `action`, `reason`), with `action: "recorded"` and `paths: [".gov-runtime/freeze"]` | DEC-177 |
| How often | one line for each call that is let through with an unmarked presence; nothing is remembered between calls | DEC-177: "one JSON line per call" |
| For which calls | pinned for a file-tool write; not pinned for a read or for a Bash call that writes nothing | |
| Never blocks | a records file that cannot be written leaves an unfrozen call allowed (exit code 0, no denial) and a frozen call denied | DEC-402 ("observation"); DEC-179 |

### Every reader reads it the same way

Searched under `src/gov/` and `template/governance/kernel/hooks/`. There are two readers, both inside the ticket's
paths, both tested through the hook command:

- `decide` in `src/gov/guard/decide.py` (line 573);
- the hook's second reading for an install, `template/governance/kernel/hooks/pretooluse.py` (line 238).

`gov pause` writes and removes the flag and never reads it. The launcher lists the names under `.gov-runtime/`; it does
not read the flag as a freeze. There is no `gov status`, and `gov checkpoint` does not read the flag. No reader lies
outside the ticket's paths, so there is no package on this point.

### The launcher

| Point | Reading | Source |
|---|---|---|
| Nothing at the path at launch | no literal `Edit` rule names the flag | DEC-402, KPI line 2 |
| A marked flag at launch | it has a literal rule, as every name that exists at launch | DEC-311 |
| The pattern rules | unchanged: they cover the flag's path for the file tools | DEC-180 |
| `s`, `sc`, `scr`, `scra`, `scrat`, `scratc`, and the names at launch | unchanged | DEC-402 names the flag alone |
| An empty or unmarked file at the path at launch | it has a literal rule, as every name that exists at launch | DEC-404 (on package DP-F1, option a); DEC-311 |

### The held-out deny line (DEC-399)

A `Read` deny rule with an absolute path, `Read(//...)`, spaces ignored: the form `w1_46_support.make_project` and
`w1_47_support.make_wired_copy` leave out. The same code is now in `copy_working_tree` of W1-05 and of W1-07. "Every
fixture that copies the whole tree" is read from the sources by W1-28's check
(`w1_28_copy_check.whole_tree_copiers`); today it finds exactly those two.

## The second batch: behaviours a review found (DEC-136)

Eight described behaviours, turned into tests from the decisions. 38 cases: 37 run without a session, 1 is live.
The counts and the "red now" column below are that batch's, before the hook and the guard were changed; behaviours 1
to 5 are green now, and the runtime-folder case of behaviour 6 was replaced in the third batch. Run on 2026-10-05 with the guard's reading, the record and the launcher's rule built and `gov pause` unchanged: 32 red,
5 green. The first batch's cases are as they were (the 10 marker cases red by design, the other 59 green). No earlier
suite's case is contradicted, so none is revised.

| # | Behaviour | File and test | Cases | Red now, and why | Whose |
|---|---|---|---|---|---|
| 1 | The records file is a symbolic link | `test_w1_50_freeze_records_file.py`: `test_nothing_is_written_through_a_records_file_that_is_a_link` | 3 | 3 red: the hook appends through the link (into a test file of the project, into a file outside it) and creates a missing target outside the project | hook, now |
| 2 | The records file is a named pipe | same file: `test_a_named_pipe_as_records_file_does_not_hold_the_hook` | 4 | 4 red: the hook gives no answer within 10 s for any of the four calls | hook, now |
| 3 | A call a later rule denies is recorded | same file: `test_a_denied_call_is_not_recorded` | 3 | 2 red: the `sudo` call and the worker's install are in `records.jsonl` as "recorded". Green: a write outside the ticket's paths, denied by the guard's decision, leaves no line | hook, now |
| 4 | Near spellings of the marker | `test_w1_50_freeze_near_spellings.py`: `test_a_near_spelling_of_the_marker_freezes` (17), `test_a_file_that_does_not_carry_the_word_is_no_freeze_in_any_encoding` (2) | 19 | 17 red: each form reads as no freeze. Green: the two files without the word | guard, now |
| 5 | `.gov-runtime` is not a folder | same file: `test_a_project_without_a_runtime_folder_is_not_frozen`, `test_a_regular_file_where_the_runtime_folder_should_be_is_no_freeze`, `test_a_dangling_link_where_the_runtime_folder_should_be_freezes` | 3 | 1 red: a dangling link reads as nothing at the path. Green: no runtime folder; a regular file in its place | guard, now |
| 6 | `gov pause` and links | `test_w1_50_freeze_pause_links.py`: `test_pause_over_a_link_at_the_flag_s_path_is_a_real_pause` (3), `test_pause_writes_nothing_through_a_runtime_folder_that_is_a_link` (1) | 4 | 4 red: "paused" with the link still at the path and nothing frozen; the dangling link's target created; the flag written in the folder outside the project | `gov pause`, later |
| 7 | `gov pause --off` over a directory | same file: `test_lifting_a_pause_over_a_directory_is_refused_in_the_envelope` | 1 | 1 red: an unhandled `IsADirectoryError`, no envelope | `gov pause`, later |
| 8 | A flag put over the placeholder during a command stays | `test_w1_50_freeze_live_pause.py`: `test_a_flag_put_over_the_placeholder_during_a_command_stays` (live) | 1 | Not run here | the lead runs it |

The time limit of behaviour 2 is the test's own: the hook's process is killed after 10 s, so a run cannot hang. While
those four cases are red they add about 40 s to a run.

### The readings pinned by the second batch

| Point | Reading | Source |
|---|---|---|
| A records file that is a symbolic link | Nothing is written through it, whatever it points to; a missing target is not created; the call is allowed as without the link. Whether the link is left, and whether the observation is kept elsewhere, is not pinned. | DEC-176, DEC-311 (the guard denies every role a write outside its paths; the hook itself runs outside the sandbox and must not be the way round that); "never blocks", first batch |
| A named pipe as records file | The hook answers within the test's limit with the decision it gives without the pipe: `sudo` denied, a worker's install denied, a harmless command and a write inside the ticket's paths allowed. The pipe is still a pipe afterwards. | DEC-179: a hook that hangs is let through by the harness when its time limit ends, so a hang fails open; DEC-402: the record is an observation |
| A denied call | Not in `records.jsonl`. Pinned for a call denied by the sudo rule, by the install rule and by the guard's own decision. | DEC-171 and DEC-177: a record is "a change the orchestrator makes", a call that happened; the first batch's "one line for each call that is let through". A line `action: "recorded"` for a `sudo` command says to its reader that the command ran. The guard's own denials already leave no line. |
| An install that is answered "ask" | Not pinned: the owner may still refuse it. Today it is recorded. | no source |
| The marker line in UTF-16 or UTF-32, with or without a byte-order mark; a doubled UTF-8 byte-order mark | frozen | DEC-179 and the first batch's reading of a byte-order mark: the file carries the word and the guard cannot tell that it is not a marker line. A flag written by hand on another system (a Windows shell writes UTF-16) must freeze. |
| A NUL, a no-break space or a zero-width space before the word; a NUL right after it | frozen | the same: a person reading the file sees a marker line |
| `FROZEN:`, `FROZEN,`, `FROZEN.`, `"FROZEN"`, `# FROZEN`, `state: FROZEN`, `FROZEN_BY` | frozen | the same. This pins what the first batch left open: the word inside a line that starts with another word. What follows the word is not read (W1-02; first batch). |
| The rule behind the three rows above | **A file at the flag's path that carries the word, in any letter case and in any of these encodings, freezes.** The plainest rule that passes: take the NUL bytes out of what was read and look for the word. | DEC-179 |
| A file that does not carry the word, in any encoding (other text in UTF-16; a byte-order mark alone) | no freeze | DEC-402: "an empty file, or one without that marker" |
| The word inside a longer word or after a negation (`unfrozen`, `not frozen`) | Not tested. The rule above freezes them; an implementation that tells them apart is not contradicted by a test. | none; nothing the system writes puts such text at the path |
| No `.gov-runtime` at all | no freeze | DEC-109; as today, must stay |
| A regular file where `.gov-runtime` should be (empty, 0444) | no freeze; the call is allowed and the file is left as it is | The guard can tell: no flag can be at the path. And the sandbox puts its placeholder at the first missing part of a denied path, so this shape can be the sandbox's own in a project that has no runtime folder (not verified here). What the sandbox produces must not freeze. |
| A dangling symbolic link where `.gov-runtime` should be | frozen; the link is left, its target is not created | DEC-179, and the first batch's reading of a dangling link at the flag's path: the folder that would hold the flag cannot be reached, so the guard cannot tell. The sandbox does not make this shape. |
| `gov pause` over a link at the flag's path (to `/dev/null`, to another file, to nothing) | The pause succeeds and leaves a regular file that is not a link; the guard then denies the next write; the link's target is unchanged or not created. | The first batch's "a pause over an unmarked file becomes a real, marked flag" (DEC-402; W1-28: a successful pause freezes): a link to `/dev/null` or to an unmarked file is an unmarked presence. A refusal is not accepted here: replacing a name the command owns is always possible, and a planted link must not block the emergency stop (DEC-179). |
| `gov pause` when `.gov-runtime` is a symbolic link (to a folder elsewhere, or to nothing) | The command refuses: an error in the envelope whose message names `.gov-runtime`, and no "paused". Nothing is written: nothing new in the folder elsewhere, a missing target not created, no flag, the link left as it was. The error code is not pinned. | DEC-404 (on package DP-F4, option a). The second batch pinned only what held under both answers; the third batch brought the case to the decided one. |
| `gov pause --off` with a directory at the flag's path | An error in the command's envelope (not a usage error) that names `.gov-runtime/freeze`; the directory stays and the tree stays frozen. The error code is not pinned. | API-0002 (every command answers in the envelope); DEC-365; the guard reads a directory as a freeze (first batch) |
| A flag put over the sandbox's placeholder during a command | It is still there, with its content, at every moment after it was put: while the command runs, when it has ended, when the session has ended. | DEC-402; "a pause set at any moment stays set" (the brief) |

### The live case of the second batch

`test_a_flag_put_over_the_placeholder_during_a_command_stays` is marked `local_only` as the first batch's live case is,
and needs the same things (`bwrap`, `socat`, the CLI, the API). It starts one engineer session through `gov launch` in
a temporary project that holds a marked flag, so the session's settings name the flag's path. A thread of the test
plays the owner from outside the sandbox:

1. when the launcher's temp folder appears (the settings are built by then; the test gives the launcher a `TMPDIR` of
   its own so that no other launch is mistaken for it), it removes the flag;
2. when something appears at the path again (the sandbox's placeholder, while the session's one Bash command of
   about 15 s runs), it renames a new marked flag over it;
3. from then on it notes every change of what is at the path, with the time and whether the command had ended.

**Repaired in the third batch.** The lead's first run failed after 7 s: the session answered DONE without running
the probe, because its one Bash call was answered "Sandbox is required but failed to initialize: Failed to create
bridge sockets after 5 attempts". The test's `TMPDIR` was a folder under pytest's temporary directory; the launcher
makes the session's temp folder under it and the sandbox makes Unix sockets under that, whose path is limited to
about 107 bytes. This is the likely cause and is not verified here. Now the launcher's `TMPDIR` is a folder the test
makes with `tempfile.mkdtemp` directly under `/tmp` (`/tmp/w150-<8 characters>`, 18 bytes, checked against a limit
of 20) and removes when it ends. The session's temp folder is then 47 bytes long, shorter than that of a launched
test designer (51 bytes), whose sandbox starts on this machine. The session is started with
`--output-format stream-json --verbose`, and every failure of the "observed nothing" kind shows the session's exit
code, its tool calls, what the harness answered to each and its final answer.

The case fails without a verdict on the behaviour when it did not observe it (no session, the probe did not end, no
placeholder appeared, or the placeholder appeared only after the command). It never passes and is never skipped in
those cases. When the flag did not stay, the failure
message says what was at the path at each change (gone, emptied, replaced by what), whether during or after the
command, and what was there when the session had ended. **It is not known what the sandbox's clean-up does: a red
result is a decision package, not a defect of the ticket's code.**

## The third batch: DEC-404, and the second live case repaired

DEC-404 decided four of the five packages. The cases were read against it; none contradicted it. One case was brought
to the decided answer and three were added. No earlier suite's case is revised in this batch.

| What | File and test | Cases | Now, and why |
|---|---|---|---|
| DP-F4 (a): `gov pause` refuses when `.gov-runtime` is a symbolic link. It replaces `test_pause_writes_nothing_through_a_runtime_folder_that_is_a_link` (1 case, which allowed both answers of the package) | `test_w1_50_freeze_pause_links.py`: `test_pause_refuses_when_the_runtime_folder_is_a_link` (a folder elsewhere; nothing) | 2 | 2 red. A folder elsewhere: the command says "paused" and writes the flag in that folder. Nothing: an unhandled `FileExistsError`, no envelope. |
| "A temporary file and a rename": no temporary file stays beside the flag | same file: `test_a_pause_leaves_no_other_name_beside_the_flag` (a pause over the placeholder) | 1 | Green: it pins something that holds today (`touch` leaves no other name) and must still hold once the write is a temporary file and a rename. |
| DP-F1 (a): an unmarked file at the flag's path at launch is denied by name | `test_w1_50_freeze_launcher.py`: `test_an_unmarked_file_at_the_path_at_launch_has_a_literal_rule_too` | 1 | Green: the launcher as built names every name that exists at launch. |
| The second live case observes something or fails | `test_w1_50_freeze_live_pause.py` | 1 live | Not run here: see "The live case of the second batch". |

What DEC-404 names and the cases already held, unchanged: the layout `FROZEN <who> <when>`, with who and when
(`assert_marker`, `MARKER_LINE`); `--cancel-agents` and `--rollback` leave a marked flag (`test_w1_50_freeze_marker.py`);
a pause never writes through a link at the flag's path and leaves a regular file
(`test_pause_over_a_link_at_the_flag_s_path_is_a_real_pause`); `--off` over a directory is a refusal in the envelope;
the guard's wider reading (`test_w1_50_freeze_near_spellings.py`, `test_w1_50_freeze_guard_reading.py`).

**No case for the read-back by the guard's own reader as a step of its own.** What can be seen of it from outside is
that the flag `gov pause` leaves is one the guard reads as a freeze, which
`test_the_flag_pause_writes_is_the_freeze_the_guard_reads` and the link cases ask. A read-back that fails cannot be
brought about through the command line without a fault put into the command, so it is the engineer's unit test.

## The fourth batch: `--rollback` ends frozen (DEC-136)

One behaviour a review found: `gov pause --rollback <ticket>` answers `paused: true` after its own reverts have taken
the flag away. The command sets the flag and reads it back once, before the reverts. The project ignores
`.gov-runtime/`, so git overwrites or removes the flag when a revert touches its path.

| History | Test, in `test_w1_50_freeze_rollback_flag.py` | Red now, and why |
|---|---|---|
| The ticket force-added `.gov-runtime/freeze` to git in one commit and removed it in a later one | `test_rollback_of_a_ticket_that_added_and_removed_the_flag_ends_frozen` | Exit 0, `paused: true`, both commits reverted, and nothing is at the flag's path. |
| The flag's path was tracked, empty, before the ticket; one commit of the ticket removed it | `test_rollback_of_a_ticket_that_removed_a_tracked_flag_ends_frozen` | Exit 0, `paused: true`, and the file at the path is the old empty one: no marker, no freeze. |

**Pinned, and nothing more:** when `--rollback` has ended, with success or with an error, the flag at the path is a
regular file whose first line is the marker line for the caller, and the guard denies the next write; a success says
`paused: true`. Sources: DEC-378 (the rollback freezes first and the flag stays whatever its result), DEC-402 and
DEC-404 (a real flag carries the marker; what `gov pause` leaves is read back as a freeze). Both repairs pass: the
flag set again after the last step, or a commit that touches the flag's path not reverted. So the cases do not ask
whether the command succeeds, which commits it reverts, what it records, or whether the tree is clean afterwards.

The second history takes the same path through the command as the first. It is kept because it ends differently: a
file is at the path, unmarked, so a repair that only looks for a missing flag would pass the first case and not this
one.

**`--cancel-agents` cannot end this way, so it has no case.** It makes no revert and no checkout: it removes claim
locks and commits each ticket file by its path alone, which writes nothing else in the working tree. Run once on the
first history, it ended with the marked flag and a denied write.

**Seen and not written (the batch allowed two cases): the error ending.** With the first history and an older commit
of the ticket that cannot be reverted, the command ends with `PAUSE_ROLLBACK_ABORTED` and nothing is at the flag's
path: the reverts before the conflict removed the flag, and the reset to the starting commit does not bring back an
ignored file. Run once as a throwaway case, not committed. It is the abort path of the command, which a repair made
only at the end of a successful rollback does not reach.

## The fifth batch: who lifts a freeze (DEC-409, DEC-407; KPI success lines 3 to 7)

Written on 2026-10-06, before implementation. 132 new cases, all run without a session: 104 red, 28 green. Every red
case fails on an assertion about behaviour or on the missing contract function; no file fails to collect.

| KPI line | Rule | File | Cases | Red now, and why |
|---|---|---|---|---|
| 3 | 1: no Claude Code session among the ancestors | `test_w1_50_freeze_lift_ancestry.py` | 29 | 23 red. 20: the contract function `gov.pause.command.lift` is missing (8 session shapes, 6 unreadable ancestries, 4 values of `GOV_ROLE`, 2 owner ancestries that lift). 3: the real command line, run by this suite under a session with pipes, lifts (`ok: true`, `paused: false`): plainly, with the session's own marks cleared from the environment, and with every switch name set. 6 green and must stay: `GOV_ROLE` empty or `owner` is refused today (as a role that is not the owner); no option is accepted beside the command's own; the help shows exactly the eight options; setting a freeze under a session works with `GOV_ROLE` unset and as orchestrator. |
| 4 | 2: a terminal and a one-time code | `test_w1_50_freeze_lift_terminal.py` | 12 | 12 red: the contract function is missing. |
| 5 | 3: the guard refuses the lift form | `test_w1_50_freeze_lift_guard_rule.py` | 77 | 59 red: the guard allows the command (a Bash call that writes nothing is allowed before the role is read): 48 spellings, 10 callers, 1 while frozen. 18 green and must stay: `sudo gov pause --off` is refused already by the sudo rule, and the 17 ordinary commands are allowed. |
| 6 | 4: the flag compared around every Bash call | `test_w1_50_freeze_flag_comparison.py` | 14 | 10 red: no finding names the flag and it is not put back (removed, 5 callers; emptied, 4 ways; removed in a call that failed). 4 green and must stay: still frozen with another line, set during the call, nothing before and after, a placeholder that goes. |
| 7 | setting stays open; unset `GOV_ROLE` is not the owner for the lift | `test_w1_50_freeze_lift_ancestry.py`: `test_setting_a_freeze_stays_open_under_a_session` (2), `test_gov_role_does_not_turn_a_session_into_the_owner` (4), counted in line 3 | | see line 3 |

Success and failure sides: the owner in person lifts (plain terminal, editor terminal; the shown code typed back);
every other caller, terminal and reply is refused and **nothing changes** (the flag's bytes, mode and kind; no new
name in the project). The rule leaves ordinary work alone; a freeze that still holds, or was set, is no finding.

### The contract: one internal function

`gov.pause.command.lift(root, ancestry=None, terminal=None) -> dict`

| Parameter | Meaning |
|---|---|
| `root` | the project |
| `ancestry` | `None`: the function reads the real chain from `/proc`. Otherwise a list of dicts, the calling process first and the system's first process last: `{"pid": int, "ppid": int, "comm": str, "exe": str or None, "cmdline": [words]}`. `exe` is `None` when it could not be read. |
| `terminal` | `None`: `(0, 1)`. Otherwise a pair of file descriptors `(input, output)`. The function calls `os.isatty` on both itself; it is never told that they are terminals. The code is written to `output` and one line is read from `input`. |
| returns | `{"paused": False}`, also when nothing was frozen |
| refuses | by raising `GovError`; the command gives it back in the API-0002 envelope |

Order: the ancestry, the terminal, the code, then the removal of the flag. The first three come first also when
nothing is frozen (DEC-409 speaks of the command, not of its effect).

**How the seam is closed.** `run()` calls `lift(root)` and nothing else: no parameter of the function is reachable
from the command line or from the environment. Tested: the command line refuses where this suite runs (under a
session, with pipes); nine made-up options (`--force`, `--yes`, `--no-tty`, `--ancestry`, ...) are usage errors; the
help shows `--help --off --cancel-agents --rollback --json --root --session --role` and no other; no environment
variable changes the answer (`GOV_ROLE` empty or `owner`; the session's marks such as `CLAUDECODE` cleared; a list of
switch names all set to 1). A test reaches the function only by importing it in a process of its own
(`w1_50_freeze_lift.drive`), with an environment built from scratch.

**How a session is recognised.** A process is a Claude Code session when one sign holds: its `comm` is `claude`; or
the last part of its `exe`, of the first word of its command line, or of the first word after it that is not an
option (the script an interpreter runs) is `claude`; or one of those three holds `claude/versions/<name>`; or one of
their path parts holds `claude-code` or is `@anthropic-ai`. One session anywhere in the chain refuses. Signs are read
by path parts of those three words, never as a loose search of the whole command line: a project folder named after
Claude in `--root` must not refuse the owner. Planted shapes: headless `-p` and the operator console as the lead saw
them, `gov launch`, a session several levels up, a session inside a session, the npm install, the version file run
by its own name (`comm` is then the version), and a process whose command line alone says it.

**What was seen from inside a launched session's sandbox (2026-10-06).** The sandbox has its own process-number
space. `/proc` lists process 1, process 2 and the command's own children. The chain is: the command, `bash` (process
2, `/usr/bin/bash`, `/bin/bash -c ...`), then process 1 with `comm` `3`, command line `/proc/self/fd/3 /bin/bash -c
...`, parent 0 and an `exe` that cannot be read. **No Claude process is visible.** So "no session among the
ancestors" is true there, and rule 1 holds only through "cannot be read".

**"Cannot be read" refuses, and means:** an empty chain; a last entry that is not process 1 with parent 0; an entry
whose parent is not the next entry; an entry without `comm` or with an empty command line; and a process 1 that is
not a system's first process. The last is this suite's choice and is not pinned by a decision: process 1 is accepted
when its `comm` is `init` or `systemd` (its `exe` cannot be read by a user on a plain host either, so `exe` cannot be
the test). The sandbox's own first process (`comm` `3`) and a shell as first process are planted and must refuse.

**Refusal reasons.** The message is tested by its words only: a session says `claude`; an unreadable ancestry says
one of `ancest`, `process`, `cannot be read`, `unreadable`, `not readable`; no terminal says `terminal` or `tty`; a wrong, empty or
ended reply says `code`. Error codes are pinned by no decision and are not tested, with one exception that already
stands: W1-28 holds `PAUSE_REFUSED` for a `GOV_ROLE` that is set, so a refusal for who the caller is should keep it.
`PAUSE_RUNTIME_LINKED`, `PAUSE_NOT_SET`, `PAUSE_NOT_LIFTED` and mode 0600 stay as built (DEC-412).

**The code.** `LIFT-` and four digits, from the system's random source: 12 runs in one process with Python's
`random` seeded to 0 before each must show more than one code. It is shown on the terminal only: it is not in the
result, not in the error, and in no file of the project. One attempt: after a wrong line, an empty line or the end of
input the function refuses at once, and a function that still waits after 10 s fails the case.

### Rule 3: the border

The **lift form** is a gov word (a word whose last part is `gov`, the module `gov.cli.main`, or the file
`gov/cli/main.py`) followed, among the words after it, by `pause` and `--off`.

Refused, for every role, a subagent, an unknown role and no role, frozen or not:

1. the form as words of a command that is run, whatever stands before it in that command (`env`, `env -u GOV_ROLE`,
   an assignment, `command`, `exec`, `nohup`, `setsid`, `time`, `timeout`, `python3 -m`, `PYTHONPATH=`) and wherever
   the command stands (after `&&`, `||`, `;`, a pipe or a newline, in a subshell, in a command substitution, in
   backticks, in a substitution inside a quoted word), with other options between or around the words;
2. the form anywhere in the text of a command or pipeline that starts a shell, an interpreter or a Claude Code
   session: `bash -c`, `sh -c`, `eval`, `python3 -c`, text piped or given as a here-string to `bash`, `sh` or
   `claude`, a prompt of `claude` (with or without `-p`, by name or by path), a prompt of `gov launch`.

Not refused: the form as one quoted word of a command that only reads or stores it (`grep`, `rg`, `git log --grep`,
a commit message, `echo` to a file or into `grep`); a file that holds it being read (`cat`, `git show`, `pytest` on
these suites); `gov pause`, `gov pause --json`, `--cancel-agents`, `--rollback`; another program with both words or
with its own `--off`; a session started without the words.

### Rule 4: the choices made on the open points

| Point | Reading | Why |
|---|---|---|
| "Removed or emptied" | the guard's reader said frozen before the call and does not say frozen after it | one reader for every question about the flag (first batch) |
| What follows | a finding whose `paths` hold `.gov-runtime/freeze`, with the caller's role and ticket and DEC-122's fields; and the flag put back: a regular file, mode 0600, the first line it had, no temporary name left, read as frozen by the guard | DEC-407 |
| Not pinned in the finding | its `action` word; a field for the tool call; whether the agent is told | no source |
| Still frozen with another line | no finding | the stricter reading would flag the orchestrator's own second `gov pause` |
| A freeze set during the call | no finding, and it stays | setting is open (DEC-409) |
| Nothing before, nothing after; a placeholder that goes | nothing | the sandbox's own shapes are not events |
| A call that failed | as a call that succeeded (PostToolUseFailure) | a failed command may have removed the flag |
| A call without a tool call id | no case | no snapshot is taken for it today, so nothing is remembered; unpinned |
| After the call the path holds a directory, a dangling link, or a link to a marked file | no case | it still freezes; whether it is "the same" is not pinned |
| Latency | no case added | W1-02 and W1-05 time the file tools and read-only calls, not the snapshot of a Bash call |

### Where an unset `GOV_ROLE` is read as the owner

| Place | What it does with an unset `GOV_ROLE` | Inside the ticket's paths |
|---|---|---|
| `src/gov/pause/command.py:133` | **the owner.** The only place. Behind it: setting (stays allowed, `<who>` is `owner`) and the lift (now the four rules) | yes |
| `src/gov/launch/launcher.py:140` | sets it for the session it starts; does not read it | |
| `template/governance/kernel/hooks/pretooluse.py:59`, `:240` | a field of the record; the role given to the guard, where no role is no known role and writes are denied | yes |
| `template/governance/kernel/hooks/posttooluse.py:104`, `:190` | passed to the containment check as no role | yes |
| `sessionstart.py:55`, `precompact.py:100` | act only when it is exactly `orchestrator` | no; no owner reading |
| `src/gov/guard/containment.py:756` | reads a commit's `Role: owner` trailer, not `GOV_ROLE` | yes |

No place other than `gov pause` reads an unset `GOV_ROLE` as the owner, so there is no package on this point. Cases:
`test_gov_role_does_not_turn_a_session_into_the_owner` and `test_setting_a_freeze_stays_open_under_a_session`.

### Earlier cases revised in this batch

Each is a rewrite after implementation in the sense of DEC-106. 9 functions, 13 cases, reason **owner decision,
DEC-409**: `gov pause --off` on the command line refuses under the session that runs the suites, so the lift is made
through the contract function as the owner in person (`w1_50_freeze_lift.lift_as_the_owner`: a plain terminal's
ancestry, a pseudo-terminal, the shown code typed back). All 13 are red until the function exists, then green.

| Suite | Test | Cases |
|---|---|---|
| W1-28 | `test_w1_28_freeze.py::test_the_next_write_by_each_role_is_denied_until_pause_is_lifted` | 5 |
| W1-28 | `test_w1_28_repeat.py::test_one_off_lifts_however_many_pauses` | 1 |
| W1-28 | `test_w1_28_repeat.py::test_off_on_a_project_that_is_not_paused_succeeds_and_changes_nothing` | 1 |
| W1-28 | `test_w1_28_repeat.py::test_off_twice_gives_the_same_result` | 1 |
| W1-28 | `test_w1_28_roles.py::test_the_owner_lifts_a_pause_the_orchestrator_set` | 1 |
| W1-28 | `test_w1_28_roles.py::test_the_owner_is_the_call_without_gov_role_whatever_the_session_that_runs_the_tests_has` | 1 |
| W1-28 | `test_w1_28_rollback.py::test_a_failed_rollback_keeps_a_freeze_that_was_already_set` | 1 |
| W1-50 | `test_w1_50_freeze_marker.py::test_a_second_pause_on_a_frozen_project_succeeds_and_keeps_a_marker` | 1 |
| W1-50 | `test_w1_50_freeze_pause_links.py::test_lifting_a_pause_over_a_directory_is_refused_in_the_envelope` (the refusal is now the function's `GovError`, which the command puts in the envelope) | 1 |

Added for them: `lift` in `w1_28_support.py` and the fixture `lift` in W1-28's `conftest.py`. W1-28's cases that
refuse a lift for a set role, and its help case, are unchanged and green.

One more, reason **owner decision: freeze marker** (DEC-402, DEC-407): W1-46's live case
`test_w1_46_live_sessions.py::test_a_bash_write_under_gov_runtime_fails_and_scratch_stays_writable`, one assertion.
It asked that nothing exists at the flag's path; it asks that no freeze exists there (what the guard's reader reads
as frozen). Live, not run here. W1-46's README does not state the old reading and is unchanged.

**Builder tests that lift, the engineer's to update** (`tests/unit/pause/test_pause.py`):
`test_the_flag_is_one_marker_line_and_a_lifted_pause_removes_it`,
`test_a_linked_runtime_folder_is_refused_and_nothing_is_written_or_removed[off]`,
`test_an_empty_gov_role_is_refused_and_sets_nothing[off]`.

### DP-F7 (open): the owner lifts while an agent's Bash call is running

- **Question.** When the owner lifts in person while a Bash call of any session is between its two hooks, does that
  call's flag comparison put the freeze back?
- **Why now.** Rule 4 as written compares before and after and cannot tell the owner's lift from an agent's removal.
  A long call (a test run) makes the overlap likely exactly when the owner lifts with sessions alive.
- **Options.** (a) Accept it: the freeze comes back with a finding; the owner lifts again when the sessions are idle.
  (b) `gov pause --off` leaves a lift record that the comparison honours. (c) Another rule.
- **Impact.** (a) A lift can seem not to work; the finding says why. (b) The record is a file an agent's opaque
  write can forge, which reopens what rule 4 closes, unless it sits where no session writes.
- **Reversibility.** Full for each: hook code.
- **Cost.** (a) one residual line in `bootstrap.md`. (b) new code in the command and the hook, and its tests.
- **Recommendation.** (a). **Confidence:** medium.
- **Does the implementation depend on it?** No. No case is written for the overlap; the 14 cases of rule 4 hold
  under (a) and (b).

Two choices of this batch are unpinned by a decision and are the lead's to confirm or return: the rule for process
1, and which error codes the new refusals carry.

### Residuals

Not held by the four rules, and not tested: the Write tool writing a script that is then run by name; a variable
that holds `--off`; an encoded command (base64); `xargs`; a renamed or copied `gov`; a process-number space an agent
makes itself with a first process dressed as `init`; an agent that reaches a real terminal of the owner. The flag
comparison acts after the call: between the removal and the PostToolUse hook the tree is not frozen.

## Earlier suites revised in the first batch

Each is a rewrite after implementation in the sense of DEC-106.

| Suite | What changed | Reason | State now |
|---|---|---|---|
| W1-46 | `test_w1_46_runtime_and_ln.py`: `test_the_freeze_flag_has_a_literal_rule_also_when_it_does_not_exist_at_launch` (4 cases) became `test_the_freeze_flag_has_no_literal_rule_when_it_does_not_exist_at_launch`; it asserts the opposite | owner decision, DEC-402 | **4 red by design** until the launcher is changed; the other 40 cases of the file as they were |
| W1-02 | `w1_02_support.set_freeze` writes the marker line, then the content it is given; the module text of `test_w1_02_freeze.py` says so. `test_the_flag_freezes_by_existing_whatever_it_contains` (5) keeps its name and now shows that what follows the marker line is not read | owner decision, DEC-402 (it amends DEC-176, which had kept this test) | 529 green |
| W1-45 | no file changed: it uses W1-02's `set_freeze` | owner decision, DEC-402 | `test_w1_45_gov_runtime.py`: 17 green |
| W1-04 | `w1_04_support.set_freeze` writes the marker line | owner decision, DEC-402 | 336 green |
| W1-05 | `test_w1_05_live_hooks.py`: the two cases that wrote an empty flag write the marker line | owner decision, DEC-402 | green, see below |
| W1-47 | `test_w1_47_oracle_guard.py`: `test_a_read_of_the_oracle_path_is_denied_while_frozen` writes the marker line | owner decision, DEC-402 | 281 green |
| W1-28 | `conftest.py`: the check that this worktree is never paused reads an empty regular file at the worktree's flag path as nothing (it was "this worktree is frozen"). Read by its size, never opened | owner decision, DEC-402 | 149 green |
| W1-05, W1-07 (W1-25 uses W1-07's) | `copy_working_tree` strips the held-out deny rules from the copied settings file (`strip_held_out_rules`) | owner decision, DEC-399 | W1-07: 217 green; W1-25: 48 green; W1-05: 97 green, 2 latency cases red in the full run under load and green alone (DEC-372) |

Not changed, and stale in words only: the READMEs of W1-02, W1-28 and W1-46 still say the flag freezes by existing and
that the launcher names the flag when it does not exist.

**One earlier case was left for package DP-F2 and is revised in the fifth batch:** W1-46's live case
`test_a_bash_write_under_gov_runtime_fails_and_scratch_stays_writable` asserted that an interpreter one-liner in a
launched session cannot create `.gov-runtime/freeze`. Without the literal rule nothing stops that write. DEC-407
decided the package; the assertion now asks that the session's Bash made no *freeze*.

## Decision packages

DP-F1, DP-F3, DP-F4 and DP-F5 are decided by **DEC-404** (orchestrator, delegated under DEC-220, 2026-10-05). **DP-F2
is decided by the owner: DEC-407, and DEC-409 on who lifts.** DP-F1 to DP-F4 are kept below as they were
returned; DP-F5 was the lead's package and is not written out here. **DP-F7 is open**: it is written out in "The
fifth batch".

| Package | State | How it was decided |
|---|---|---|
| DP-F1 | decided, DEC-404 | Option (a): `gov launch` denies the flag's path by name whenever a file exists there at launch, marked or not (DEC-311). A placeholder renewed this way freezes nothing. |
| DP-F2 | decided, DEC-407 and DEC-409 | The flag's path has no literal rule when no flag exists at launch, and what held it is replaced: the flag is compared around every Bash call (a freeze that a call removed or emptied is a finding and is put back), and only the owner in person lifts (no Claude Code session among the ancestors, a terminal, a one-time code; the guard refuses the lift form). W1-46's live case is revised: what must not exist is a freeze the session's Bash made. The cases are the fifth batch's. |
| DP-F7 | **open** | An owner's lift while an agent's Bash call is running is undone by the flag comparison. See "The fifth batch". |
| DP-F3 | decided, DEC-404 | Option (a): the first line is `FROZEN <who> <when>` with single spaces; who is `owner` or `orchestrator`, when is UTC `YYYY-MM-DDTHH:MM:SSZ`. The guard's wider reading stays as built. |
| DP-F4 | decided, DEC-404 | Option (a): when `.gov-runtime` is a symbolic link, `gov pause` refuses with an error that names the link and writes nothing. The owner repairs the folder. |
| DP-F5 | decided, DEC-404 | Option (a): `tests/unit/install/**` is added to the ticket's `allowed_paths`, so the engineer updates the one builder test that sets an empty flag. No acceptance test follows from it. |

### DP-F1: an empty or unmarked file at the flag's path at launch

- **Question.** When `gov launch` finds a file at `.gov-runtime/freeze` that is not a marked flag, does it deny the
  path by name?
- **Why now.** KPI line 2 says "when the flag does not exist at launch". DEC-311 says every name that exists at
  launch has a literal rule. An unmarked file exists as a name and is not a flag.
- **Options.** (a) Deny it by name, as any name that exists (DEC-311 as written). (b) Deny it by name only when it
  is a marked flag.
- **Impact.** (a) The path stays protected in that session. If the file was a passing placeholder of another
  session, the new session's sandbox puts its own placeholder there for each of its commands; with the new guard
  reading that freezes nothing and adds one record line per call. (b) No placeholder is ever renewed; a file that is
  there for another reason is left open to that session's Bash.
- **Reversibility.** Full: a launcher rule, computed at each launch.
- **Cost.** (a) none: removing the flag's name from the fixed set leaves exactly this. (b) a few lines: the launcher
  reads the marker.
- **Recommendation.** (a). **Confidence:** medium.
- **Does the implementation depend on it?** No. The tests of line 2 hold under both; the minimal change gives (a).

### DP-F2: the flag's path inside a session launched while no flag existed

- **Question.** Is it accepted that a launched worker's opaque Bash write can create, rewrite or remove
  `.gov-runtime/freeze` when the flag did not exist at that session's launch?
- **Why now.** Only the literal rule held this, and KPI line 2 removes it. W1-46's KPI success 10 says such a write
  fails, and its live case asserts it for the flag.
- **What still holds the path.** The guard denies every role's Write, Edit and recognisable Bash write to it
  (redirection, `rm`, `mv`, `cp`, `touch`, `ln`), with or without a flag: tested here. The settings' patterns deny
  the file tools. **Nothing holds** a write the guard does not read as one (an interpreter one-liner, a script run
  by an interpreter, a wrapped command) in a session whose settings carry no literal rule.
- **Two cases.** A freeze set after the session was launched can be lifted by that session (only the owner may lift,
  DEC-365). A session can write a marked flag itself and freeze every session; the owner lifts it.
- **Options.** (a) Accept it as a residual in `bootstrap.md`, beside DEC-311's "a new name after launch", and revise
  W1-46's live assertion on the flag (reason: owner decision). (b) Have the containment check note the flag's state
  before a Bash call and raise a finding, and restore a removed flag, when a call that is not `gov pause` changed it.
  (c) Keep the literal rule and rely on the marker reading alone: KPI line 2 is then not built and the placeholder
  stays, recorded on every call.
- **Impact.** (a) An emergency control can be undone by a misbehaving worker, through forms the guard already does
  not judge inside that worker's own paths. (b) Closes it after the fact, for about 30 to 40 lines in the
  PostToolUse hook and its tests. (c) Undoes an owner decision.
- **Reversibility.** (a) and (c) full. (b) is new code.
- **Cost.** (a) one revised live assertion and a residual. (b) a ticket's worth of containment work. (c) none.
- **Recommendation.** (a) now; (b) only if the owner wants the freeze to hold against a worker that works around
  the guard. **Confidence:** medium. This lowers a protection, so it is the owner's.
- **Does the implementation depend on it?** No: line 2 is decided. The lead's live run of W1-46 will show that one
  case red until this is answered.

### DP-F3: the layout of the marker line

- **Question.** Is the flag's first line `FROZEN <who> <when>`, with single spaces?
- **Why now.** DEC-402 gives the word and the two parts as an example and no layout. The tests and the helpers of six
  suites need one.
- **Options.** (a) `FROZEN <who> <when>` on the first line. (b) `FROZEN` alone on the first line, who and when on
  the lines after it. (c) another wording, such as `FROZEN by <who> at <when>`.
- **Impact.** The guard's reading is the same under all three (the first word of a line). Only what `gov pause`
  writes and what `assert_marker` accepts differ.
- **Reversibility.** Full: one expression (`MARKER_LINE` in `w1_50_freeze_support.py`). The helpers of the earlier
  suites write a line that every option reads as marked.
- **Cost.** None for (a). A two-line change in the tests for (b) or (c).
- **Recommendation.** (a). **Confidence:** medium. The tests are written to (a).
- **Does the implementation depend on it?** Only the line `gov pause` writes. It can be built to (a) and changed in
  one place.

### DP-F4: `gov pause` when `.gov-runtime` is a symbolic link to a folder elsewhere

- **Question.** When `.gov-runtime` of the project is a symbolic link to a folder outside the project, does
  `gov pause` refuse, or does it replace the link by a real folder and set the flag there?
- **Why now.** Today the command says "paused" and writes the flag in the folder elsewhere. The review's expected
  result excludes writing through the link and leaves these two answers; no decision chooses between them.
- **Options.** (a) Refuse: an error of the command that names the link; nothing is written; the owner repairs the
  folder and pauses again. (b) Replace: remove the link, make a real `.gov-runtime`, write the flag; the pause
  succeeds.
- **Impact.** (a) The emergency stop does not work until the owner has repaired the folder; nothing is lost and the
  owner sees the abnormal state. (b) The stop works at once; the findings, records and snapshots in the folder
  elsewhere are no longer the project's (they stay where they are, unseen), and the command changes `.gov-runtime`
  itself, which is outside what it declares it acts on (`ACT_PATHS`: `.gov-runtime/freeze`, `.tickets/**`).
- **Reversibility.** (a) full. (b) the link can be put back by hand; what the hooks wrote into the new folder in the
  meantime must then be merged by hand.
- **Cost.** A few lines either way. One more test for the chosen answer.
- **Recommendation.** (a). **Confidence:** medium. A linked runtime folder is a state the owner should see, and the
  command should not rearrange the runtime folder on its own; against it, (a) lets a planted link delay a pause.
- **Does the implementation depend on it?** Only this one case of `gov pause`, which is not built yet. The test in
  place holds under both answers. Nothing of the guard or the hook depends on it.

## Notes for the engineer

- **Second batch, the hook.** The record is to be written only to a regular file inside a real `.gov-runtime/`: no
  following of a link, no blocking open (`O_NOFOLLOW`, `O_NONBLOCK`, then a check that what was opened is a regular
  file), and only once the call is known to be let through. `_append_finding` of the hook and `_write_records` and
  `_record_findings` of `containment.py` open their files the same way as the record did; no behaviour of this batch
  covers them, so no test does (reported to the lead as a gap).
- **Second batch, the guard.** One rule passes all near-spelling cases: the word, in any letter case, anywhere in
  what was read once the NUL bytes are taken out. A dangling link at `.gov-runtime` is the one new shape of "cannot
  tell"; a regular file there and no folder at all stay "nothing at the path".

- **Do not open what is not a regular file.** A FIFO at the path would block a plain `open`, and the harness lets a
  call through when a hook times out. A very large file should not be read whole.
- **`gov pause` over a placeholder.** The placeholder is mode 0444, so appending to it fails; the tests ask that the
  pause succeeds and leaves a marked flag.
- **The record is written by the hook**, which has the session and the tool; `decide` returns only a decision. Both
  readers need the same three-way answer: nothing, unmarked, frozen.
- **Unit tests** under `tests/unit/` that write an empty flag are the engineer's to update: `tests/unit/guard`,
  `tests/unit/pause`, `tests/unit/launch`, `tests/unit/install` mention the flag.

## A sixth case: the seam in ``lift()`` (reviewer finding, DEC-136)

A reviewer found that `gov.pause.command.lift` takes `ancestry` and `terminal` as public keyword arguments and uses
them as given. An agent can write a Python script that imports the function and calls it with a forged ancestry (no
Claude Code session, a readable chain to the system's first process) and a real pseudo-terminal pair, bypassing all
four rules of DEC-409 and lifting the freeze without being the owner in person.

| File | Test | Cases | Red now, and why |
|---|---|---|---|
| `test_w1_50_freeze_seam.py` | `test_an_agent_script_that_calls_lift_with_planted_parameters_does_not_lift` | 1 | 1 red: `lift()` accepts the planted `ancestry` and `terminal`, every rule passes, and the freeze is lifted. |

**What closes the seam.** `lift()` must either stop accepting `ancestry` and `terminal` as parameters (so the call
gets TypeError) or ignore them and read the real ancestry from `/proc` and the real terminal from `(0, 1)`. In either
case, the driver's subprocess — which has a Claude Code session among its real ancestors, or an unreadable chain — is
refused, and the freeze stays.

**Expected green after the fix:** the freeze flag is still present, the guard still denies, and no name under
`.gov-runtime/` has changed.

---

## Batch 7 — closing follow-up: KPIs 9, 10, 11

Three KPI lines from the ticket, added as a closing follow-up after the first five batches and the seam fix.

### KPI 9 — the freeze mirror (DEC-429)

`gov pause` writes the freeze to `.gov-runtime/freeze` and to a mirror outside the repository, under
`~/.local/state/gov-os/`, keyed by the repository; the guard treats the project as frozen if either exists.

| File | Test | Cases | Red now, and why |
|---|---|---|---|
| `test_w1_50_freeze_mirror.py` | `test_gov_pause_writes_both_flag_and_mirror_as_owner` | 1 | red: `gov pause` does not write the mirror (mirror code not built). |
| | `test_gov_pause_writes_both_flag_and_mirror_as_orchestrator` | 1 | red: same reason. |
| | `test_mirror_keyed_same_for_worktrees_of_the_same_repo` | 1 | red: no mirror written by `gov pause`. |
| | `test_mirror_keyed_differently_for_different_repos` | 1 | green: tests only the key derivation helper, which is in test code. |
| | `test_guard_frozen_when_only_mirror_exists` | 1 | red: `freeze_state()` does not read the mirror. |
| | `test_guard_frozen_when_only_flag_exists` | 1 | green: existing behaviour. |
| | `test_guard_frozen_when_both_exist` | 1 | green: frozen by the flag (existing behaviour). |
| | `test_not_frozen_when_neither_exists` | 1 | green: existing behaviour. |
| | `test_cancel_agents_writes_mirror` | 1 | red: no mirror written. |
| | `test_rollback_writes_mirror` | 1 | red: no mirror written. |
| | `test_mirror_failure_is_reported` | 1 | red: no mirror write attempted, so no failure to report. |
| | `test_mirror_content_is_the_same_marker_line_as_the_flag` | 1 | red: no mirror written. |
| | `test_guard_fails_closed_on_unreadable_mirror_folder` | 1 | red: the guard does not read the mirror folder. |

**13 tests** (9 red, 4 green).

### KPI 10 — flag restoration from the mirror (DEC-429)

A flag removed or emptied while the mirror remains is a finding; flag is restored. Lifting removes both. Sandbox
denies the mirror path. Projects frozen before this change (flag only, no mirror) stay frozen by the flag alone.

| File | Test | Cases | Red now, and why |
|---|---|---|---|
| `test_w1_50_freeze_mirror_restore.py` | `test_flag_removed_while_mirror_remains_is_a_finding` (×3 roles) | 3 | green: the snapshot-based `_compare_flag` detects the removal; the mirror is planted but not read. |
| | `test_flag_emptied_while_mirror_remains_is_a_finding` | 1 | green: snapshot detects the emptied flag. |
| | `test_flag_restored_from_mirror_content_not_snapshot` | 1 | red: no mirror-based detection exists in containment; the snapshot did not remember a freeze. |
| | `test_lift_removes_both_flag_and_mirror` | 1 | red: `gov pause` does not write a mirror (DEC-429, KPI 1), so the precondition fails. |
| | `test_after_lift_guard_reads_not_frozen` | 1 | green: lift succeeds and removes the flag; no mirror was written to persist. |
| | `test_sandbox_denies_mirror_path_for_engineer` | 1 | green: the mirror path is outside the project; the guard already denies writes outside the project root. |
| | `test_lift_refuses_when_mirror_cannot_be_removed` | 1 | red: the current lift has no mirror support and succeeds (DP-M3 option b, DEC-437). |
| | `test_old_project_flag_only_stays_frozen` | 1 | green: existing `freeze_state()` reads the flag. |
| | `test_old_project_flag_removed_during_call_is_still_found_via_snapshot` | 1 | green: `_compare_flag` via snapshot. |
| | `test_old_project_lift_works_without_mirror` | 1 | green: lift removes the flag; no mirror to fail on. |

**12 tests** (3 red, 9 green).

### KPI 11 — the ticket lead's own role (DEC-434, DEC-435)

A ticket lead runs under its own role (`ticket-lead`), may write only its checkpoint, scratch and merge-backs
judged by the three-way rule. Writes to source, tests, tickets, or documents are refused.

| File | Test | Cases | Red now, and why |
|---|---|---|---|
| `test_w1_50_ticket_lead_role.py` | `test_ticket_lead_in_known_roles` | 1 | red: `ticket-lead` not in `KNOWN_ROLES`. |
| | `test_ticket_lead_may_write_scratch` | 1 | red: denied as "not a known role" before scratch check. |
| | `test_ticket_lead_may_write_scratch_via_bash` | 1 | red: same. |
| | `test_ticket_lead_may_write_checkpoint` | 1 | red: not in `KNOWN_ROLES`, no `_get_allowed_paths` case. |
| | `test_ticket_lead_may_read` (×3 tools) | 3 | green: `READ_TOOLS` allowed before role check. |
| | `test_ticket_lead_may_run_read_only_bash` | 1 | green: no write targets → allow. |
| | `test_ticket_lead_denied_write_to` (×6 paths) | 6 | green (as deny): denied as "not a known role" now; after fix, denied by path rules — denial stays, reason changes. |
| | `test_ticket_lead_denied_bash_write_to_source` | 1 | green (as deny): same. |
| | `test_ticket_lead_not_in_worker_roles` | 1 | green: true now and must stay. |
| | `test_gov_launch_refuses_ticket_lead` | 1 | green: not in `WORKER_ROLES`; `assert_refused` confirms. |
| | `test_ticket_lead_cannot_set_freeze` | 1 | green: `gov pause` checks for orchestrator. |
| | `test_ticket_lead_stricter_than_orchestrator` | 1 | green (as deny): denied now. |

**19 tests** (4 red, 15 green).

### Decision packages

**DP-M1 — mirror key derivation.** Proposed: `sha256(os.path.realpath(git rev-parse --git-common-dir))` as hex.
This makes worktrees of the same clone share one mirror. Confidence: medium. The engineer may choose a different
derivation as long as it satisfies the two keying tests.

**DP-M2 — mirror content for an empty or unmarked flag.** The mirror holds the same marker line as the flag
(DEC-402). If the flag is empty or unmarked, the mirror may be absent or hold the empty/unmarked content; tests
do not mandate which. Confidence: medium.

**DP-M3 — lift fails to remove mirror.** Decided: **(b), the lift refuses and nothing changes** (DEC-437). The
flag stays, the project stays frozen, and the message names the mirror's path. The designer proposed option (a):
remove the flag anyway; the decision chose the stricter option.

**DP-M4 — XDG_STATE_HOME.** The mirror lives under `$XDG_STATE_HOME/gov-os/` when set, else `~/.local/state/gov-os/`.
Tests redirect via the sandbox's `HOME`. Confidence: medium.

**DP-L1 — role name.** `ticket-lead`, hyphenated, matching the ticket's `role: ticket-lead` field and DEC-236.
Confidence: high.

**DP-L2 — `_get_allowed_paths` for ticket-lead.** Decided: **(a), no allowed paths** (DEC-437). The function
returns `[]` for ticket-lead. Scratch access is via `_is_in_scratch`. The lead's checkpoint is under
`.gov-runtime/scratch/lead/CHECKPOINT.md` (inside scratch), not under `.gov-runtime/checkpoints/`. The
three-way merge-back rule is checked in `_judge_commit`, not in path patterns.

### Summary

| Batch | File | Tests | Red | Green |
|---|---|---|---|---|
| KPI 9 | `test_w1_50_freeze_mirror.py` | 13 | 9 | 4 |
| KPI 10 | `test_w1_50_freeze_mirror_restore.py` | 12 | 3 | 9 |
| KPI 11 | `test_w1_50_ticket_lead_role.py` | 19 | 4 | 15 |
| **Total** | | **44** | **16** | **28** |
