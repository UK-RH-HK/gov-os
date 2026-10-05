# W1-50, the freeze half: acceptance tests for three KPI lines (DEC-402, DEC-399)

Ticket `DAEO-xnbx` (W1-50), profile FULL, branch `w1/W1-50-freeze`. Written before implementation by the Independent
Test Designer (MR-3). This file covers only the three KPI lines the owner added on 2026-10-05. The ticket's other lines
(containment by commit trailers) are in `README.md` of this folder, by another designer, on another branch.

Files of this half: `w1_50_freeze_support.py`, `test_w1_50_freeze_marker.py`, `test_w1_50_freeze_guard_reading.py`,
`test_w1_50_freeze_launcher.py`, `test_w1_50_freeze_fixture_settings.py`, and this file. A second batch, from the
findings of a review (DEC-136), added `test_w1_50_freeze_records_file.py`, `test_w1_50_freeze_near_spellings.py`,
`test_w1_50_freeze_pause_links.py` and `test_w1_50_freeze_live_pause.py`: see "The second batch" below.

The whole half now: 108 cases, 106 run without a session and 2 are live. With the guard's reading, the record and the
launcher's rule built and `gov pause` unchanged, 42 are red and 64 green.

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
- Run: `python3 -m pytest tests/acceptance/W1-50 -q -p no:cacheprovider -m "not local_only"`. About 65 s for this
  half while the four named-pipe cases of the second batch are red (10 s each), about 25 s once they are green. The `local_only` mark is not registered for this folder (its `conftest.py` is the other half's), so pytest
  prints one "unknown mark" warning; the selection works.
- **One live case** (`local_only`) starts a real engineer session through `gov launch`. A launched test designer
  cannot run it (the sandbox refuses the API host): the ticket lead runs it.

## The three KPI lines

70 cases: 69 run without a session, 1 is live. Before implementation 30 are red and 39 green.

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
| The first line `gov pause` writes | `FROZEN <who> <when>`, single spaces | The three parts are DEC-402's. **Their order and the separator are this designer's plainest arrangement, decided by no source**: see package DP-F3. |
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
| An empty or unmarked file at the path at launch | **open**: package DP-F1, no test | DEC-311 and DEC-402 point different ways |

### The held-out deny line (DEC-399)

A `Read` deny rule with an absolute path, `Read(//...)`, spaces ignored: the form `w1_46_support.make_project` and
`w1_47_support.make_wired_copy` leave out. The same code is now in `copy_working_tree` of W1-05 and of W1-07. "Every
fixture that copies the whole tree" is read from the sources by W1-28's check
(`w1_28_copy_check.whole_tree_copiers`); today it finds exactly those two.

## The second batch: behaviours a review found (DEC-136)

Eight described behaviours, turned into tests from the decisions. 38 cases: 37 run without a session, 1 is live.
Run on 2026-10-05 with the guard's reading, the record and the launcher's rule built and `gov pause` unchanged: 32 red,
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
| `gov pause` when `.gov-runtime` is a link to a folder elsewhere | Only what holds under both answers of package DP-F4: nothing is written in the folder elsewhere; "paused" only with a real folder, a regular flag and a guard that denies; otherwise an error of the command, with the link left. | the brief's expected result; DP-F4 |
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

The case fails without a verdict on the behaviour when it did not observe it (no session, the probe did not end, no
placeholder appeared, or the placeholder appeared only after the command). When the flag did not stay, the failure
message says what was at the path at each change (gone, emptied, replaced by what), whether during or after the
command, and what was there when the session had ended. **It is not known what the sandbox's clean-up does: a red
result is a decision package, not a defect of the ticket's code.**

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

**One earlier case will go red after the implementation and is not revised here:** W1-46's live case
`test_a_bash_write_under_gov_runtime_fails_and_scratch_stays_writable` asserts that an interpreter one-liner in a
launched session cannot create `.gov-runtime/freeze`. Without the literal rule nothing stops that write. It is package
DP-F2.

## Decision packages

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
