# W2-42a acceptance tests: the product's guard reads what a Bash command writes, replayed on every logged refusal

Ticket `DAEO-03ub` (W2-42a), profile FULL. Written by an independent test designer before implementation (MR-3),
from the ticket's 11 success and 2 failure KPI lines, DEC-1040 item 2, DEC-1028 item 4, DEC-958, DEC-953 item 2,
the package `P1-GUARD-PARSER-W2` and ACT-GUARD-FIX-3 §7, against the base `w2/integrate` at `a58ba344`. The
engineer's worktree and branch were not read (DEC-820 (c)).

Run from the tree under test (through the gate, DEC-1038 (4)):

```
cd <tree> && TMPDIR=/tmp/gov-os-emg-<name> PYTHONPATH=<tree>/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-42a -q -n auto -o tmp_path_retention_policy=failed -p no:cacheprovider
```

452 cases in four files. The replay and the planted cases run the hook once each (about 1 to 3 s a call: the
hook lists every worktree for rules 2 and 5), so run with `-n auto`.

## What judges what

- **The write parser:** `gov.guard.decide._extract_bash_write_targets(command, cwd)`, as `gov.guard` exposes it
  today (the ticket names it): a list of real paths, `/<guard-unresolvable>` among them for a write it cannot
  resolve, or `None` for no write. The cases run in a `tmp_path` of their own, with none of the session's variables
  and none of the command's own variables set, so a target is resolved only from the command's text.
- **The read judge:** `gov.guard.reads.policy_refusal("Bash", …)` (which runs `_set_aside` and
  `_Judge.tool`/`command`), for a research session in a project of the case's own whose evaluation set measures
  research and whose hidden part holds a file, so the listing rule ("the call reads files whose names another
  command gives at run time …", DEC-820 (d)) is live, as for the sessions it refused. `HOME` is the case's own.
- **The hook:** the reviewed `drafts/act-guard-fix-3/pretooluse.py` with `bash_writes.py` beside it, copied to
  `fixtures/hook/` (SHA-256 first 12: `b7e96a89d092`, `df7be57c6bdd`; the same as the live `.claude/hooks/` on
  2026-11-02), run as `python3 fixtures/hook/pretooluse.py` with `PYTHONPATH=<tree>/src`: the five-rule hook as it
  runs once this tree is pinned (re-pin window 2). Event JSON on stdin (`tool_name`, `tool_input`, `cwd`,
  `agent_type`); `GOV_ROLE`, `CLAUDE_PROJECT_DIR` and `TMPDIR` in its environment. No output and exit 0 is allow;
  a JSON `permissionDecision` is the answer; exit 2 (an error) is a refusal by no rule, which no case accepts.

## The fixtures

- **`fixtures/refusals.json`** (built by `tools/build_refusals.py` from the CTO's `log/guard-refusals.jsonl`, 80
  lines on 2026-11-02 at 20:22): for each line with a tool-use id, the full tool input from the `tool_use` block of
  that id in the line's transcript; the tool; the cwd (the transcript entry's); the project folder (the worktree the
  cwd lies in, else the main tree); the session's role (a main session: the role of its launch folder
  `gov-launch-<role>-<id>` when its own scratchpad lies in one, else `orchestrator`, as the CTO and the leads run;
  a subagent: its parent's role so found, and its type from its `.meta.json` as `agent_type`); the launch folder as
  `TMPDIR`; the verdict; the rule that refused it.
  - **Recovered: 76** (74 judged false, 2 judged true: line 74, a hidden-part read; line 77, a reviewer's Write).
  - **Left out: 4**, lines 51 to 54: summary rows with no tool-use id (each summarises a later row of the same
    session, ACT-GUARD-FIX-3 §2: lines 55, 56, 59, 60, which are replayed).
  - **Secrets:** gitleaks (`gitleaks dir <file> --no-banner --redact`) found none in either fixture; nothing was
    replaced. (`planted.json` was scanned before its `base_caught` booleans were added.)
- **`fixtures/planted.json`** (built by `tools/build_planted.py` from the reviewed `test_guard_fix_3.py`,
  `b6f8216c97bc`): 155 cases the hook must refuse: ACT-GUARD-FIX-3's 137 planted writes and unknown forms (rule 1,
  acceptance folder; rule 5, outside a reviewer's record; its one key-read case, rule 3, left out), its logged pattern
  left refused by design (row 46), and guard4_check.py's 17 planted writes of rules 1 and 5. Row 39's pattern (an
  unmatched glob in `/tmp`) is left out: KPI line 4 makes it pass. The main tree's path is written `{ROOT}` and
  replaced by the tree under test. `base_caught`: whether the base's parser catches each Bash case (computed on
  `a58ba344`, for failure line 1).

## The KPI map (read by `gov close`)

S1 to S11 are the ticket's success lines in order, F1 and F2 its failure lines.

| KPI | Tests |
|---|---|
| S1 | `test_w2_42a_parser.py::test_kpi1_a_data_body_for_cat_is_no_write_and_its_quotes_do_not_break_the_reading`, `test_w2_42a_parser.py::test_kpi1_a_data_body_for_tee_is_no_write`, `test_w2_42a_parser.py::test_kpi1_a_data_body_for_grep_is_no_write`, `test_w2_42a_parser.py::test_kpi1_a_quoted_data_body_s_substitution_is_text`, `test_w2_42a_parser.py::test_kpi1_an_unquoted_data_body_s_substitution_is_judged`, `test_w2_42a_parser.py::test_kpi1_a_shell_body_is_judged_as_commands` |
| S2 | `test_w2_42a_parser.py::test_kpi2_a_variable_set_once_at_the_top_before_use_is_expanded`, `test_w2_42a_parser.py::test_kpi2_a_variable_built_from_one_set_before_it_is_expanded`, `test_w2_42a_parser.py::test_kpi2_a_literal_for_loop_s_words_are_judged_one_by_one`, `test_w2_42a_parser.py::test_kpi2_any_other_binding_is_unresolvable` |
| S3 | `test_w2_42a_parser.py::test_kpi3_a_substitution_in_quotes_sh_c_and_eval_are_judged_as_commands`, `test_w2_42a_parser.py::test_kpi3_shell_keywords_are_not_the_command_s_name`, `test_w2_42a_parser.py::test_kpi3_prefixes_are_not_the_command_s_name` |
| S4 | `test_w2_42a_parser.py::test_kpi4_an_unmatched_glob_is_its_literal_path`, `test_w2_42a_parser.py::test_kpi4_an_unmatched_glob_after_a_cd_is_its_literal_path`, `test_w2_42a_parser.py::test_kpi4_a_matched_glob_is_still_its_matches` |
| S5 | `test_w2_42a_parser.py::test_kpi5_the_named_writers_write_their_paths`, `test_w2_42a_parser.py::test_kpi5_git_mv_writes_both_paths`, `test_w2_42a_parser.py::test_kpi5_rsync_writes_into_its_destination`, `test_w2_42a_parser.py::test_kpi5_patch_appliers_write_unresolvable_targets` |
| S6 | `test_w2_42a_read_judge.py::test_kpi6_arithmetic_is_no_command_substitution`, `test_w2_42a_read_judge.py::test_kpi6_a_data_body_naming_a_secret_is_no_read`, `test_w2_42a_read_judge.py::test_kpi6_a_data_body_for_tee_naming_a_key_is_no_read`, `test_w2_42a_read_judge.py::test_kpi6_a_data_body_holding_a_listing_loop_is_no_listing`, `test_w2_42a_read_judge.py::test_kpi6_a_shell_body_is_still_read`, `test_w2_42a_read_judge.py::test_kpi6_an_unquoted_data_body_s_substitution_is_still_read`, `test_w2_42a_read_judge.py::test_kpi6_a_substitution_inside_arithmetic_is_still_read`, `test_w2_42a_read_judge.py::test_kpi6_a_plain_secret_read_is_still_refused` |
| S7 | `test_w2_42a_parser.py::test_kpi7_a_continued_word_is_one_word`, `test_w2_42a_parser.py::test_kpi7_a_continued_command_writes_its_target`, `test_w2_42a_parser.py::test_kpi7_a_continued_copy_writes_its_destination_and_nothing_with_a_newline`, `test_w2_42a_parser.py::test_kpi7_a_backslash_newline_inside_single_quotes_is_kept`, `test_w2_42a_read_judge.py::test_kpi7_a_secret_named_across_a_continued_line_is_refused`, `test_w2_42a_read_judge.py::test_kpi7_a_hidden_file_named_across_a_continued_line_is_refused` |
| S8 | `test_w2_42a_parser.py::test_kpi8_a_script_written_then_run_by_bash_is_judged_as_its_code`, `test_w2_42a_parser.py::test_kpi8_a_script_written_after_a_cd_then_run_by_its_path_is_judged`, `test_w2_42a_parser.py::test_kpi8_a_python_file_written_then_run_is_its_code_or_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_the_parser_cannot_read_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_by_a_word_that_does_not_expand_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_written_file_that_is_only_read_is_judged_as_data` |
| S9 | `test_w2_42a_measured.py::test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_measured.py::test_kpi9_the_measures_are_stated_in_the_evidence_file` |
| S10 | `test_w2_42a_read_judge.py::test_kpi10_a_loop_over_seq_reading_a_literal_file_is_judged_by_that_file`, `test_w2_42a_read_judge.py::test_kpi10_a_substitution_that_yields_no_file_name_leaves_the_literal_files`, `test_w2_42a_read_judge.py::test_kpi10_a_python_heredoc_naming_its_files_literally_is_judged_by_them`, `test_w2_42a_read_judge.py::test_kpi10_a_data_heredoc_appended_to_a_record_is_judged_by_its_file`, `test_w2_42a_read_judge.py::test_kpi10_names_given_at_run_time_are_still_judged_as_a_listing`, `test_w2_42a_read_judge.py::test_kpi10_a_literal_hidden_file_is_still_refused` |
| S11 | `test_w2_42a_replay.py::test_kpi11_each_logged_refusal_replayed`, `test_w2_42a_replay.py::test_kpi11_the_replay_holds_every_recoverable_line`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |
| F1 | `test_w2_42a_measured.py::test_failure1_no_write_the_base_parser_catches_is_missed`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |
| F2 | `test_w2_42a_parser.py::test_failure2_an_unparseable_or_unknown_form_is_unresolvable`, `test_w2_42a_parser.py::test_failure2_a_form_read_uncertainly_keeps_its_write`, `test_w2_42a_read_judge.py::test_failure2_an_unparseable_command_naming_a_secret_is_refused`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |

## KPI lines, their cases and the expected red reasons

| KPI line | Cases (file: test) | Expected red reason on the base |
|---|---|---|
| S1 heredoc bodies | parser: `test_kpi1_*` (7) | the body is read as shell: an apostrophe makes the command unreadable (sentinel), a body's `touch` or `>` is taken as a write, a quoted body's `$(…)` as a command. Green on the base: the unquoted body's `$(…)` and the shell bodies (both already caught) |
| S2 own variables, literal loops | parser: `test_kpi2_*` (8) | `$W242A_B` is read from the environment only (sentinel); `do touch` is taken as the command `do` (no write), the loop over a substitution too (4 red). Green: the other four "any other binding" cases (already unresolvable) |
| S3 quotes, `sh -c`, `eval`, keywords, prefixes | parser: `test_kpi3_*` (14) | `echo "$(touch b)"`, `sh -c`, `eval`, `then rm`, `timeout 5 touch` give no write (the command's name is `echo`, `sh`, `then`, `timeout`) |
| S4 unmatched glob | parser: `test_kpi4_*` (3) | an unmatched glob is the sentinel. Green: the matched glob |
| S5 the writers it did not read | parser: `test_kpi5_*` (13) | `git checkout`/`restore`/`rm`/`mv`, `dd`, `truncate`, `sort -o`, `rsync`, `git apply`/`am`, `patch` give no write (all 13 red) |
| S6 read judge: `$((…))`, data bodies | read judge: `test_kpi6_*` (9) | `$((n+6))` is set aside as a substitution, so `sed` reads names given at run time (listing refusal); a data body's `cat .env` and `cat ~/.ssh/…` are secret reads (4 red). Green: the four kept refusals (a shell body, an unquoted body's `$(cat .env)`, `$(…)` inside `$((…))`, `cat .env`), and the data body holding a listing loop (the base places that listing) |
| S7 backslash-newline | parser: `test_kpi7_*` (4); read judge: `test_kpi7_*` (2) | the newline stays in the word: `accep\ntance`, `\n/…/f`, a `\n` operand of `cp`; `cat .e\␤nv` and the hidden file split over two lines are not seen (the base fails open) (5 red). Green: the single-quoted case |
| S8 a written body that is run | parser: `test_kpi8_*` (6) | a body the command only reads is taken as a write; a Python or ruby body run by its interpreter gives no target and no sentinel (3 red). Green: the shell script run by `bash` or `./s.sh`, and the run by `$S` (the body read as shell, or `$S`, catches it) |
| S9 measured | measured: `test_kpi9_*` (1 + 81 + 1) | the base leaves 22 of the 61 logged commands unresolvable (lines 24, 33, 35–38, 40–44, 46–49, 51, 52, 54–57, 60; more than 2); it misses 30 of the 81 planted shell writes (no target there, no sentinel); `docs/changes/W2-42a-evidence.md` does not exist (32 red; 51 planted shell writes green) |
| S10 literal paths are no listing | read judge: `test_kpi10_*` (11) | a `for` over `$(seq …)`, `$(wc -l < f)`, `$(nproc)`, `$(date …)` in a reading command, and a data heredoc appended to a record whose body holds `$(…)` text, are read as listings the guard cannot place (listing refusal; 5 red). Green: the five kept refusals, and the Python heredoc case (the base passes this shape; lines 75 and 79 of the replay are the shapes it refuses) |
| S11 replay and planted, through the hook | replay: `test_kpi11_*` (76 + 1 + 155) | see "The replay" (5 red) |
| F1 no write the base catches is missed | measured: `test_failure1_*` (53) | green by construction on the base (each is a case the base catches) |
| F2 unknown forms fail closed | parser: `test_failure2_*` (6); read judge: `test_failure2_*` (1); and the planted unknown forms in S9 and S11 | `eval "$X"`, `sh -c "$X"` and `bash -c` with unbalanced quotes give no write on the base (3 red); the unbalanced quotes, the unterminated heredoc, the shift in arithmetic and the unparseable secret read are green |

**The red run on the base** (`a58ba344`, through the gate, `-n auto`): **94 failed, 358 passed**, no errors, each
failure for the reason above: S1 4, S2 4, S3 14, S4 2, S5 13, S6 4, S7 5, S8 3, S9 32, S10 5, S11 5, F2 3.

## The replay (S11)

Parametrised by refusal: `line<NN>-<tool-use id>`. A line judged false must be allowed; a line judged true must be
refused with the hook's reason equal to the logged rule. On the base (`a58ba344`, this hook) 64 of the 74 false lines
already pass (ACT-GUARD-FIX-1 to -3 fixed them in the hook); the 10 still refused are:

| Line | Rule | Why the base refuses it | In W2-42a's reach? |
|---|---|---|---|
| 40 | rule 5, unreadable writes | `rm -f chain-*.json` matches nothing: the parser's sentinel (S4) | yes: **red, must pass** |
| 75 | listing | a Python heredoc's body read as shell (S10) | yes: **red, must pass** |
| 78 | listing | `for i in $(seq 1 16); do grep … <file>` (S10) | yes: **red, must pass** |
| 79 | listing | a Python heredoc's body read as shell (S10) | yes: **red, must pass** |
| 80 | listing | a data heredoc appended to a record, its body read as shell (S6, S10) | yes: **red, must pass** |
| 47 | rule 1 | the hook's own Python reading | no: **held** |
| 65 | rule 1 | a write in a folder known only at run time, in a command naming the tests | no (a fail-open): **held** |
| 72 | rule 1 | the hook's own Python reading (F4) | no: **held** |
| 73 | rule 1 | the hook's own Python reading (F4) | no: **held** |
| 76 | rule 5, record paths | a reviewer's write to `scratch/orchestrator/reviews/` | no (the rule, not a misreading): **held** |

The two true lines (74, 77) are refused on the base by their logged rules and must stay so. The 155 planted cases
are refused on the base by their write rules (ACT-GUARD-FIX-3 measured 0 missed) and must stay so.

### Held refusals (a decision package to the CTO)

The KPI line says each line judged false must now pass. Five cannot, within W2-42a's paths (`src/gov/guard/**`),
without failing open or changing a rule; the tests expect each still refused by its logged rule (`HELD` in
`test_w2_42a_replay.py`, one line each, so the CTO's decision is one edit):

- **47:** ACT-GUARD-FIX-3 left this pattern refused by design (its row 46): an unquoted Python heredoc the shell
  rewrites with `$(echo "$out" | sed …)`, in a command naming the tests. Judged by `bash_writes.py`'s Python reading,
  which `src/` does not reach.
- **65:** `cd $TMPDIR 2>/dev/null || cd $(ls -dt /tmp/tmp.* | head -1)`, then `cat > probe.py`, in a command whose
  heredoc data names the tests: the write's folder is known only at run time. Rule 1 refuses an unresolvable write
  when the command names the tests; letting it pass is a fail-open.
- **72, 73:** the hook's Python reading (ACT-GUARD-FIX-3 F4): an f-string path from `sys.argv` (72), a computed path
  while the code runs a module of the acceptance folder (73), in code naming the tests. The product's parser adds
  nothing to either; only a change to `bash_writes.py` (an owner ACT) could.
- **76:** the log's "false-positive" is the harvester's automatic verdict ("the live hook now allows it", judged as
  an engineer); the same reviewer's Write of the same file seconds later (line 77) is judged true. Rule 5 keeps a
  reviewer to `docs/probes/`, `docs/audit/`, `docs/assessment/`, its own scratch and `/tmp`.

## Notes

- The replay runs against this machine's trees: each refusal's cwd and project folder (worktrees under
  `~/gov-os-worktrees/`, the main tree). A tree removed later changes what rules 2 and 5 see; the fixture states
  each path.
- No case reads a secret, the held-out material or a hidden half: the read-judge cases name `.env`, a key path and a
  hidden file of their own stand-in project as words; the replay passes the logged commands to the hook, which runs
  none of them.
