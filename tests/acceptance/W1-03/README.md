# W1-03 — Post-command containment check: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-8qvp` (W1-03), the Contract v4
item it cites (CAP-58.a) and the decisions that bind the check. Written before implementation, in two batches:

- batch 1 (commit `a389ebc`): the report to the agent, the restore of `tests/acceptance/**`, in-scope work left alone;
- batch 2 (this one, on `w1/integrate` at `01ff589`): the finding record (DEC-122), the nine I-06 forms (DEC-123), a
  tree that was already dirty before the call (DEC-124, DEC-126), and role subagents in a session with no role
  (DEC-125).

One effect of one form is not tested and is with the owner as KD-4; see [Not tested](#not-tested).

## Run

```sh
python3 -m pytest tests/acceptance/W1-03 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. Each test builds a small git project
in a temporary directory and makes whole Bash calls in it: the PreToolUse hook, the command for real, the PostToolUse
hook. Nothing in the repository is written. The run takes about 40 seconds once the hook exists.

Fifteen cases need a program that a machine may lack (`perl`, `ruby`, `node`, `curl`, `base64`, three cases each); a
case is skipped where its program is missing. All five are present on the owner's machine.

## KPI → tests → red reason today

Red run on `w1/integrate` at `01ff589`: **202 errors, 0 passed** (202 cases, 55 test functions). Every case errors in
the `hook` fixture with the same reason: **no file matches `template/governance/kernel/hooks/posttooluse*`** — the
containment hook does not exist. That is the red reason for every row below.

| KPI line or covers id | Test file | Test functions |
|---|---|---|
| **Success 1.** After every Bash call and at gov close, `git status --porcelain` is compared with `allowed_paths`; a change outside them is reported to the agent and recorded as a containment finding [CAP-58.a] — *the run at `gov close` is left to W1-30, see [Not tested](#not-tested)* | `test_w1_03_out_of_scope.py` | `test_a_change_outside_the_ticket_paths_is_reported` · `test_one_call_with_both_kinds_reports_only_the_outside_change` · `test_a_new_directory_is_judged_file_by_file` · `test_the_comparison_follows_the_active_ticket` · `test_each_ticket_role_is_compared_with_its_own_ticket` · `test_a_session_without_ticket_paths_has_every_change_reported` · `test_the_test_designer_is_reported_outside_acceptance_tests` · `test_a_failed_call_is_checked_too` · `test_inside_a_subagent_the_subagent_s_role_is_compared` · `test_nothing_is_reported_on_a_clean_tree` · `test_scratch_writes_are_not_reported` |
| | `test_w1_03_finding_record.py` | `test_an_out_of_scope_change_is_recorded_as_one_finding` · `test_the_findings_file_is_one_json_object_per_line` · `test_the_finding_names_every_out_of_scope_path_and_no_other` · `test_the_recorded_action_tells_what_happened_to_the_change` · `test_one_call_with_both_kinds_records_what_was_done_with_each` · `test_a_run_that_finds_nothing_records_nothing` · `test_earlier_lines_of_the_findings_file_stay` · `test_a_finding_inside_a_subagent_names_the_subagent_type` · `test_a_session_without_role_and_ticket_is_recorded_without_them` · `test_a_failed_call_is_recorded_too` · `test_the_findings_file_does_not_show_in_git_status` |
| | `test_w1_03_dirty_tree.py` | `test_an_out_of_scope_change_is_reported_once` · `test_only_the_new_change_is_reported_on_a_dirty_tree` · `test_without_a_before_snapshot_a_change_is_flagged_and_not_reverted` · `test_the_before_snapshot_leaves_no_trace_in_git_status` |
| | `test_w1_03_bash_forms.py` | `test_a_write_the_guard_cannot_see_is_reported` (24 forms) |
| | `test_w1_03_hook.py` | `test_the_check_works_from_what_the_call_left_behind` |
| **Success 2.** Changes under `tests/acceptance/**` by a non-test-designer role are restored from HEAD and the breach is recorded | `test_w1_03_test_independence.py` | `test_an_engineer_s_change_under_acceptance_tests_is_restored_from_head` · `test_every_session_but_the_test_designer_s_is_restored` · `test_inside_a_subagent_the_subagent_s_role_decides_the_restore` |
| | `test_w1_03_finding_record.py` | `test_a_breach_of_the_acceptance_tests_is_recorded_as_reverted` · `test_a_failed_call_is_recorded_too` |
| | `test_w1_03_dirty_tree.py` | `test_the_restore_takes_back_only_what_this_call_changed` |
| | `test_w1_03_bash_forms.py` | `test_an_unseen_write_to_an_acceptance_test_is_reported_and_restored` (10 forms) |
| | `test_w1_03_i06_forms.py` | `test_an_i06_form_into_the_acceptance_tests_is_restored_and_recorded` · `test_git_checkout_of_an_older_acceptance_test_is_restored_from_head` |
| **Success 3.** All nine Bash write forms from S0b2 I-06 are caught — *one effect of form 8 is not tested: KD-4* | `test_w1_03_i06_forms.py` | `test_an_i06_form_outside_the_ticket_paths_is_caught` · `test_an_i06_form_into_the_acceptance_tests_is_restored_and_recorded` · `test_an_i06_form_given_word_for_word_passes_neither_line_unseen` (13 cases each, forms 1 to 7 and 9) · `test_git_checkout_of_an_older_revision_outside_the_ticket_paths_is_caught` · `test_git_checkout_of_an_older_acceptance_test_is_restored_from_head` · `test_a_git_command_that_discards_another_role_s_uncommitted_work_is_caught` · `test_discarding_one_s_own_uncommitted_work_is_no_finding` (form 8) |
| **Failure 1.** Any out-of-scope change survives without a finding | every file | Every Success 1, 2 and 3 test: each one now requires the finding next to the report (`assert_caught`). Sharpest: `test_the_finding_names_every_out_of_scope_path_and_no_other` · `test_a_git_command_that_discards_another_role_s_uncommitted_work_is_caught` · `test_a_new_directory_is_judged_file_by_file` |
| **Failure 2.** A legitimate in-scope change is reverted | `test_w1_03_out_of_scope.py` | `test_a_change_inside_the_ticket_paths_is_left_alone` · `test_one_call_with_both_kinds_reports_only_the_outside_change` · `test_a_new_directory_is_judged_file_by_file` · `test_scratch_writes_are_not_reported` · `test_the_check_adds_nothing_to_git_status` |
| | `test_w1_03_test_independence.py` | `test_the_restore_leaves_the_engineer_s_own_work_alone` · `test_the_test_designer_s_changes_stay` · `test_the_test_designer_s_scope_does_not_depend_on_the_ticket_paths` |
| | `test_w1_03_dirty_tree.py` | `test_the_test_designer_s_uncommitted_tests_survive_another_role_s_call` · `test_the_caller_s_own_change_is_judged_and_the_earlier_work_is_not` · `test_an_engineer_s_uncommitted_work_is_not_reported_after_another_role_s_call` · `test_a_path_already_changed_before_the_call_is_never_put_back_to_head` · `test_without_a_before_snapshot_another_role_s_uncommitted_tests_are_not_restored` · `test_without_a_before_snapshot_an_in_scope_change_is_still_silent` · `test_the_snapshot_of_an_earlier_call_is_not_used_for_a_later_one` · `test_a_change_made_by_an_overlapping_call_is_not_reverted` |
| **CAP-58.a** default-deny allow-lists per role and ticket; checks derived, not enumerated | `test_w1_03_hook.py` and the Success 1 files | `test_containment_hook_ships_in_the_kernel_template` · the Success 1 and Failure 2 tests |

**Count.** KPI lines with tests: 5 of 5. Covers ids with tests: 1 of 1. Two clauses inside those lines have no test:
"at gov close" (Success 1, left to W1-30) and a `git reset --hard` or `git checkout` that moves `HEAD` (Success 3,
KD-4).

## Decisions the tests rely on

| Decision | What the tests take from it |
|---|---|
| DEC-122 | A finding is one JSON line in `.gov-runtime/findings.jsonl`, the guard's file, with `time`, `session_id`, `agent_type`, `role`, `ticket`, `tool`, `command`, `paths`, `action` (`reverted` or `flagged`) and `reason` |
| DEC-123 | The nine I-06 forms are tested by their effect inside the repository. A write outside it is not tested (accepted residual) |
| DEC-124 | Only the current call's changes are acted on. The before-snapshot is taken in PreToolUse and compared in PostToolUse. A path already changed before the call is never touched. Uncertain attribution: flag, no revert |
| DEC-126 | The before-snapshot is taken by the kernel's PreToolUse hook, the guard's. The tests run that hook before every call |
| DEC-125 | In a session with no declared role, a role subagent has no write either |
| DEC-107 | Role and active ticket come from `GOV_ROLE` and `GOV_TICKET`. Missing or unknown role: no paths |
| DEC-117 | Inside a role subagent (`agent_type` in the hook input), the subagent's role is the one compared |
| DEC-113 | A subagent whose type is not a role has no write: every change it leaves is reported, and an acceptance test it changed is restored |
| DEC-108 | The scratch set is `.gov-runtime/scratch/**` plus the temp directory; neither shows in `git status` |
| DEC-099, DEC-110, DEC-111, DEC-115 | Shell aliases and functions, the guard's timeout case and every Bash form the guard does not judge are left to this check |

The path rules are W1-02's: the test designer may change `tests/acceptance/**` and nothing else; every other role is
denied `tests/acceptance/**`, also when a ticket's `allowed_paths` name it; a role on a ticket whose `role:` names
another role has no ticket paths.

## How the tests drive the check

- **Entry points.** The files matching `template/governance/kernel/hooks/pretooluse*` and `posttooluse*`. If several
  files match one pattern, exactly one must be executable, and that one is run. An executable file is run directly;
  otherwise `.py` runs under `python3` and `.sh` under `bash`.
- **Where they run.** Every matching file is copied to `governance/kernel/hooks/` of the temporary project (ADR-0002 §5)
  and committed there. The hooks run from there.
- **The `gov` package.** `src/` of this repository is on `PYTHONPATH`.
- **The project** is named three ways: the process working directory, `cwd` in the stdin object, and
  `CLAUDE_PROJECT_DIR`.
- **One call** is three steps: the PreToolUse hook with the call on stdin; the command, run with `bash -c` in the
  project; the PostToolUse hook with the same call on stdin. Both hooks get the same `session_id` and `tool_use_id`,
  and every call has a `tool_use_id` of its own.
- **The call the hooks see.** The fixture command is saved as a script outside the project, and the call is
  `bash <script>`. The guard cannot judge such a call, so it lets it through and the before-snapshot exists, whatever
  the guard parses now or later (W1-02, W1-04). The tests fail with a clear message if the PreToolUse hook does not let
  this call through. Two tests pass the command to the hooks word for word instead:
  `test_an_i06_form_given_word_for_word_passes_neither_line_unseen` and
  `test_the_check_works_from_what_the_call_left_behind`.
- **Earlier work.** A dirty tree is made by running a command in the project with no hook, before the call under test.
- **No before-snapshot.** Four tests leave the PreToolUse hook out, as when it never ran or timed out.
- **Stdin** is the harness's object: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`,
  `tool_name` (`Bash`), `tool_input`, `tool_use_id`, and
  - for `PostToolUse`: `tool_response` with `stdout`, `stderr`, `interrupted`, `isImage`;
  - for `PostToolUseFailure`: `error`, `error_type`, `is_interrupt`, `is_timeout`. The harness sends this event when the
    call failed, timed out or was interrupted.
  - The subagent tests add `agent_id` and `agent_type` to all three events.
- **Environment.** Built from scratch: `PATH`, an empty temporary `HOME`, locale, `TMPDIR`, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX` and `CLAUDE_PROJECT_DIR`, plus `GOV_ROLE` and `GOV_TICKET` when the test declares them.
- **"Reported to the agent"** is what the installed harness (2.1.284) passes to the model from the two post events:
  - exit code 2: the hook's stderr;
  - exit code 0 with a JSON object on stdout: `reason` when `decision` is `block`, and
    `hookSpecificOutput.additionalContext`.
  - Plain stdout with exit code 0 reaches the transcript only, and any other exit code reaches the user only. Neither
    counts.
  - The report must name the path that is out of scope, as `git status --untracked-files=all` spells it. For a new
    directory it may name the directory or the files in it.
- **"Recorded"** is: the lines added to `.gov-runtime/findings.jsonl` between the start of the call and the end of the
  PostToolUse hook. Every added line must be a finding as DEC-122 defines it.
- **"Caught"** is reported and recorded.
- **"Nothing to report"** is exit code 0, no text for the agent, and no line added to the findings file.

## The fixture project

Tickets, all `in_progress`:

| Ticket | Role | `allowed_paths` |
|---|---|---|
| `DAEO-zz90` | engineer | `src/gov/guard/**` · `tests/unit/guard/**` · `template/governance/kernel/hooks/pretooluse*` · `pyproject.toml` |
| `DAEO-zz91` | orchestrator | `.claude/settings.json` · `governance/project/bootstrap.md` |
| `DAEO-zz92` | product-spec | `template/governance/kernel/roles/**` · `docs/spec/**` |
| `DAEO-zz93` | engineer | `src/app/**` · `tests/acceptance/**` |
| `DAEO-zz94` | independent-auditor | `docs/audit/**` |
| `DAEO-zz95` | engineer | `docs/**` |
| `DAEO-zz96` | engineer | `tools/guard/**` (the directory does not exist yet) |

`src/gov/guard/acceptance_link` is a committed symbolic link to `tests/acceptance`. `.gov-runtime/` and `__pycache__/`
are ignored by git.

## The finding record (DEC-122)

What the tests require of each line the check adds:

- It is one JSON object on one line, and the file ends with a newline. Earlier lines, the guard's included, stay as
  they are.
- It holds all ten fields. `tool` is `Bash`. `session_id` and `command` are the hook input's. `time` and `reason` are
  not empty. `action` is `reverted` or `flagged`.
- `paths` is a list of path names. The tests accept a path relative to the repository or absolute inside it. A new
  directory may be recorded as the directory or as the files in it.
- `role` and `ticket` are what the session declared in `GOV_ROLE` and `GOV_TICKET`, tested on a call outside any
  subagent; both are empty when the session declared none. `agent_type` is the subagent's type inside a subagent and
  empty outside one.
- **One out-of-scope path is recorded once.** A call with one such path adds one line. A call with several adds one
  line or more, and each path is in exactly one of them.
- **No in-scope path is recorded.** A run that finds nothing adds nothing.
- **`action` tells the truth.** A restored acceptance test is `reverted`. Outside `tests/acceptance/**`: `reverted`
  means the path is back at HEAD, `flagged` means the change is still there. Without certain attribution it is
  `flagged`.

## A tree that was already dirty (DEC-124)

- **Nothing of an earlier call is touched or reported again.** With the test designer's uncommitted tests in the tree
  (a changed test, a new staged test, a new directory git does not track), a later `git status` by the orchestrator,
  the engineer, the product-spec role, the auditor, a session with no role, or a subagent is silent and leaves every
  file as it was. The same holds for the engineer's uncommitted source after the orchestrator's call.
- **A change is reported once:** by the call that made it. Later calls that change nothing more are silent.
- **Only the new change is named** in the report and in `paths`.
- **The restore takes back only this call's changes.** "Restored from HEAD" on a dirty tree means: `tests/acceptance`
  is as it was before the call. The engineer's new file inside the test designer's new, untracked directory is removed
  and the designer's file next to it stays; this needs every untracked file compared by itself.

Readings of DEC-124 that the tests hold the check to. Each follows from the decision's text; the owner can overrule
any of them:

1. **No before-snapshot for the call means attribution is uncertain.** The PreToolUse hook did not run or timed out
   (DEC-110). Every out-of-scope change in the tree is reported and recorded as `flagged`, and none is reverted, an
   acceptance test included. An in-scope change is silent as always.
2. **A snapshot belongs to one call.** A later call without one does not fall back on an earlier call's.
3. **A path already changed before the call, and changed again by it, is never put back to HEAD.** The tests take no
   side on whether it is reported.
4. **Overlapping calls mean attribution is uncertain.** The orchestrator's call begins, a subagent's whole call runs,
   the first one ends: the first call's check does not undo the subagent's work. The tests take no side on what it
   reports.
5. **A path that was changed before the call and no longer is, was changed by the call.** This is the effect of
   `git reset --hard` and `git checkout -- .` (I-06 form 8). Outside the caller's paths it is reported and recorded;
   the tests take no side on `action`. Discarding one's own in-scope work is no finding.

## The nine I-06 forms (DEC-123)

The list is the I-06 row of `INTEGRATION_REPORT.md` in S0b2's output, the source the KPI names. It was outside the
repository; it is quoted here so the KPI can be checked from the repository alone: *"9 Bash forms cannot be reliably
detected: writes inside `$(…)`/backticks, `perl/ruby/node -e`, unknown binaries, process substitution,
`base64 -d | bash`, `$VAR` commands, aliases/functions, `git checkout/reset --hard`, and `curl -o`/`wget -O`
(partial)."*

| # | Form | Cases |
|---|---|---|
| 1 | writes inside `$(…)` or backticks | `: "$(printf … >> file)"` · the same in backticks |
| 2 | `perl -e`, `ruby -e`, `node -e` | one each |
| 3 | unknown binaries | an executable outside the project that appends to its argument |
| 4 | process substitution | `cat <(printf … >> file)` · `printf … > >(cat >> file)` |
| 5 | `base64 -d \| bash` | the write, encoded |
| 6 | `$VAR` commands | `c="tee -a file"; … \| $c` |
| 7 | aliases and functions | one each |
| 8 | `git checkout`, `git reset --hard` | `git checkout HEAD~1 -- file` · `git reset --hard` and `git checkout -- .` on a dirty tree |
| 9 | `curl -o`, `wget -O` | `curl -s -o file file://…` (no network) |

- Forms 1 to 7 and 9 are each run against `README.md` (reported and recorded), against an acceptance test (restored
  from HEAD, recorded as `reverted`), and once with the command given to both hooks word for word. In that last run
  the guard may stop the call (`deny` or `ask`); then nothing ran and the form is caught by the first line. Otherwise
  the command runs and the check must catch it.
- Form 8 writes nothing new. `git checkout <older revision> -- file` stages older content: caught like any change, and
  an acceptance test is put back to HEAD, index included. `git reset --hard` and `git checkout -- .` discard
  uncommitted work: see reading 5 above. The third effect, a moved `HEAD`, is KD-4.
- `wget -O` is not run: it needs a server. Its effect in the repository is the same file write as `curl -o`.

The test designer's own 24 forms from batch 1 stay, in `test_w1_03_bash_forms.py`: `python3 -c` · `python3 -` with a
here-document · `bash -c` · `sh -c` · `eval` · a target in a shell variable · a target from `$(…)` · a shell function ·
a shell alias · `cat > … <<EOF` · `dd of=` · `truncate` · `install` · `ln -s` · `find -delete` · `xargs rm` · `awk` ·
`sed` with the `w` command · `tar -x` · `git mv` · `git rm` · `git apply` · `shutil.copy` · `os.rename`. Ten of them
are also run against `tests/acceptance/**`.

## Choices the implementer should know

- **The check does not read the command.** It works from the tree the call left behind. A harmless command in the hook
  input and an out-of-scope change in the tree still give a report and a finding.
- **Path patterns** are read as W1-02 reads them: anchored at the repository root; `**` crosses directories; `*` stays
  inside one name.
- **A new directory is judged file by file.** `git status --porcelain` shows a new directory as one line. With the
  ticket path `tools/guard/**`, a new `tools/guard/a.py` is in scope although the line says `?? tools/`; a new
  `tools/other/b.py` next to it is reported and recorded, and neither the report nor the finding names `tools/guard`.
- **Staged changes count,** and so do renames: both ends of a rename are compared.
- **A name with a space** is reported and recorded in plain form (`docs/my notes.md`).
- **Sessions without ticket paths.** No role, an empty or unknown role, a role without a ticket, a ticket that does not
  exist, a role on another role's ticket, and a role subagent in a session with no or an unknown role: every change is
  reported.
- **Out-of-scope changes outside `tests/acceptance/**`.** The KPI asks for a report and a finding. Whether the check
  also undoes such a change is the implementer's choice; `action` must say which.
- **Restore from HEAD.** After the check on a clean tree, `tests/acceptance` equals HEAD: a changed or deleted file has
  its HEAD content, a file or directory HEAD does not hold is gone, and nothing under `tests/acceptance` stays staged.
  This holds for a deleted directory, the whole tree deleted, a file moved in or out, and a change made through
  `src/gov/guard/acceptance_link`.
- **The restore touches nothing else.** With an acceptance test and the engineer's own files changed in one call,
  `git status` afterwards shows exactly the engineer's own changes, staged ones still staged.
- **The test designer** keeps every change under `tests/acceptance/**`: changed, added and deleted files, on any
  ticket. A change elsewhere is reported.
- **Subagents.** A test-designer subagent in an engineer or orchestrator session keeps its acceptance tests. An
  engineer subagent in a test-designer session is restored. A test-designer subagent in a session with no role is
  restored (DEC-125).
- **Failed calls.** The same result is expected from the `PostToolUseFailure` input as from `PostToolUse`.
- **No trace in git.** Neither hook adds a line to `git status`. The snapshot and the findings file are under
  `.gov-runtime/`, which the fixture project ignores.
- **W1-02's suite must still pass** after the PreToolUse hook changes (DEC-126): `python3 -m pytest tests/acceptance/W1-02 -q`.

## Changes to the tests of batch 1

| What | Change | Why |
|---|---|---|
| All 115 cases | Each call now runs the PreToolUse hook first, and the command is saved as a script (`bash <script>`) | DEC-124, DEC-126. In batch 1 the PostToolUse hook ran alone |
| Every test that expected a report | Now also expects the finding (`assert_caught`); a restored acceptance test must be recorded as `reverted` | DEC-122 |
| Every test that expected silence | Now also expects no line added to the findings file | DEC-122 |
| `test_the_check_works_from_what_the_call_left_behind` | Runs the PreToolUse hook with `ls -la` first | DEC-124 |
| Two subagent tables | Four cases added: a role subagent in a session with no role, and with an unknown role | DEC-125, left open in batch 1 |

One expectation changed in kind: a PostToolUse run with no PreToolUse run before it was expected to restore an
acceptance test in batch 1. Under DEC-124 it flags and does not revert (reading 1).

**W1-05's tests need the same change.** `tests/acceptance/W1-05/test_w1_05_live_hooks.py` was written before DEC-124.
Its `test_the_containment_check_restores_an_acceptance_test` runs the PostToolUse hooks alone and expects a restore, so
it cannot pass together with `test_without_a_before_snapshot_a_change_is_flagged_and_not_reverted` here. W1-05 is
outside this batch; its tests have to run the registered PreToolUse hooks before the call, in a W1-05 revision batch.

## Not tested

With the owner (`~/gov-os-workbench/w1-tests/decision-packages/W1-03-kpi-disputes-round-2.md`):

- **KD-4.** A call that moves `HEAD`: `git reset --hard <revision>`, `git checkout <branch>`, and a call that commits
  its own change. Afterwards `git status --porcelain` is clean, so the comparison the KPI names sees nothing. For
  `git reset --hard` and `git checkout` this is a part of I-06 form 8 with no test.

Left open on purpose; the tests take no side:

- **"At gov close".** `gov close` is W1-30, and its KPI says it "runs the containment check". The run at close is left
  to W1-30's acceptance tests.
- **A write outside the repository** through an opaque form: accepted residual (DEC-123).
- **`role` of a finding inside a subagent:** the session's role or the subagent's. `agent_type` is tested.
- **The format of `time`,** and the wording of `reason`.
- **A snapshot that is never used** (the guard denied the call, or the call never ended): how long it is kept.
- **A ticket that is not `in_progress`** (DEC-114 and DEC-116 are decisions on the guard).
- **An ignored path** outside the ticket paths; git does not show it.
- **Unusable stdin, a missing `git`, a directory that is not a repository,** and the time the two hooks take. No KPI
  names them.
