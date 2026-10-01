# W1-03 — Post-command containment check: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-8qvp` (W1-03), the Contract v4
item it cites (CAP-58.a) and the decisions that already bind the check (DEC-099, DEC-107, DEC-108, DEC-110, DEC-113,
DEC-117). Written before implementation.

Three clauses of the KPIs are not tested yet. They wait for owner answers KD-1, KD-2 and KD-3; see
[Not tested](#not-tested).

## Run

```sh
python3 -m pytest tests/acceptance/W1-03 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. Each test builds a small git project
in a temporary directory, runs a real Bash command in it, and then runs the hook as a process, the way the harness does
after the call. Nothing in the repository is written.

## KPI → tests → red reason today

Red run on `w1/integrate` at `d6bb6d5`: 115 errors, 0 passed (115 cases, 23 test functions). Every case errors in the
`hook` fixture with the same reason: **no file matches `template/governance/kernel/hooks/posttooluse*`** — the
containment hook does not exist. That is the red reason for every row below.

| KPI line or covers id | Test file | Test functions |
|---|---|---|
| **Success 1.** After every Bash call and at gov close, `git status --porcelain` is compared with `allowed_paths`; a change outside them is reported to the agent and recorded as a containment finding [CAP-58.a] — *tested: after every Bash call, the comparison, the report. Not tested: the record (KD-1), the run at `gov close` (left to W1-30)* | `test_w1_03_out_of_scope.py` | `test_a_change_outside_the_ticket_paths_is_reported` · `test_one_call_with_both_kinds_reports_only_the_outside_change` · `test_a_new_directory_is_judged_file_by_file` · `test_the_comparison_follows_the_active_ticket` · `test_each_ticket_role_is_compared_with_its_own_ticket` · `test_a_session_without_ticket_paths_has_every_change_reported` · `test_the_test_designer_is_reported_outside_acceptance_tests` · `test_a_failed_call_is_checked_too` · `test_inside_a_subagent_the_subagent_s_role_is_compared` · `test_nothing_is_reported_on_a_clean_tree` · `test_scratch_writes_are_not_reported` |
| | `test_w1_03_bash_forms.py` | `test_a_write_the_guard_cannot_see_is_reported` (24 forms) |
| | `test_w1_03_hook.py` | `test_the_check_works_from_what_the_call_left_behind` |
| **Success 2.** Changes under `tests/acceptance/**` by a non-test-designer role are restored from HEAD and the breach is recorded — *tested: the restore and the report. Not tested: the record (KD-1)* | `test_w1_03_test_independence.py` | `test_an_engineer_s_change_under_acceptance_tests_is_restored_from_head` · `test_every_session_but_the_test_designer_s_is_restored` · `test_inside_a_subagent_the_subagent_s_role_decides_the_restore` |
| | `test_w1_03_bash_forms.py` | `test_an_unseen_write_to_an_acceptance_test_is_reported_and_restored` (10 forms) |
| **Success 3.** All nine Bash write forms from S0b2 I-06 are caught | — | *Not tested: the list is not in the repository (KD-2). The test designer's own 24 forms are under Success 1* |
| **Failure 1.** Any out-of-scope change survives without a finding — *tested as: without a report to the agent. The record is KD-1* | `test_w1_03_out_of_scope.py`, `test_w1_03_bash_forms.py` | The Success 1 tests |
| **Failure 2.** A legitimate in-scope change is reverted | `test_w1_03_out_of_scope.py` | `test_a_change_inside_the_ticket_paths_is_left_alone` · `test_one_call_with_both_kinds_reports_only_the_outside_change` · `test_a_new_directory_is_judged_file_by_file` · `test_scratch_writes_are_not_reported` · `test_the_check_adds_nothing_to_git_status` |
| | `test_w1_03_test_independence.py` | `test_the_restore_leaves_the_engineer_s_own_work_alone` · `test_the_test_designer_s_changes_stay` · `test_the_test_designer_s_scope_does_not_depend_on_the_ticket_paths` |
| **CAP-58.a** default-deny allow-lists per role and ticket; checks derived, not enumerated | `test_w1_03_hook.py` and the Success 1 files | `test_containment_hook_ships_in_the_kernel_template` · the Success 1 and Failure 2 tests |

**Count.** KPI lines with tests: 4 of 5 (Success 3 has none; Success 1, Success 2 and Failure 1 lack the record clause).
Covers ids with tests: 1 of 1.

## Decisions the tests rely on

| Decision | What the tests take from it |
|---|---|
| DEC-107 | Role and active ticket come from `GOV_ROLE` and `GOV_TICKET`. Missing or unknown role: no paths |
| DEC-117 | Inside a role subagent (`agent_type` in the hook input), the subagent's role is the one compared |
| DEC-113 | A subagent whose type is not a role has no write: every change it leaves is reported, and an acceptance test it changed is restored |
| DEC-108 | The scratch set is `.gov-runtime/scratch/**` plus the temp directory; neither shows in `git status` |
| DEC-099 | Shell aliases and functions are left to this check |
| DEC-110, DEC-111, DEC-115 | The guard's timeout case and every Bash form the guard does not judge are left to this check |

The path rules are W1-02's (accepted with its KD-1): the test designer may change `tests/acceptance/**` and nothing
else; every other role is denied `tests/acceptance/**`, also when a ticket's `allowed_paths` name it; a role on a ticket
whose `role:` names another role has no ticket paths.

## How the tests drive the check

- **Entry point.** The file matching `template/governance/kernel/hooks/posttooluse*`. If several files match, exactly
  one must be executable, and that one is run. An executable file is run directly; otherwise `.py` runs under `python3`
  and `.sh` under `bash`.
- **Where it runs.** Every matching file is copied to `governance/kernel/hooks/` of the temporary project (ADR-0002 §5)
  and committed there. The hook runs from there.
- **The `gov` package.** `src/` of this repository is on `PYTHONPATH`.
- **The project** is named three ways: the process working directory, `cwd` in the stdin object, and
  `CLAUDE_PROJECT_DIR`.
- **The Bash call.** The test runs the command with `bash -c` in the project, then starts the hook. The working tree is
  clean before every call.
- **Stdin** is the harness's object: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`,
  `tool_name` (`Bash`), `tool_input`, `tool_use_id`, and
  - for `PostToolUse`: `tool_response` with `stdout`, `stderr`, `interrupted`, `isImage`;
  - for `PostToolUseFailure`: `error`, `error_type`, `is_interrupt`, `is_timeout`. The harness sends this event when the
    call failed, timed out or was interrupted.
  - The subagent tests add `agent_id` and `agent_type`.
- **Environment.** Built from scratch: `PATH`, an empty temporary `HOME`, locale, `TMPDIR`, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX` and `CLAUDE_PROJECT_DIR`, plus `GOV_ROLE` and `GOV_TICKET` when the test declares them.
- **"Reported to the agent"** is what the installed harness (2.1.284) passes to the model from these two events:
  - exit code 2: the hook's stderr;
  - exit code 0 with a JSON object on stdout: `reason` when `decision` is `block`, and
    `hookSpecificOutput.additionalContext`.
  - Plain stdout with exit code 0 reaches the transcript only, and any other exit code reaches the user only. Neither
    counts.
  - The report must name the path that is out of scope, as `git status` spells it. For a new directory it may name the
    directory or the files in it.
- **"Nothing to report"** is exit code 0 and no text for the agent.

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

## Choices the implementer should know

- **The check does not read the command.** It works from the tree the call left behind. A harmless command in the hook
  input and an out-of-scope change in the tree still give a report.
- **Path patterns** are read as W1-02 reads them (DEC-097): anchored at the repository root; `**` crosses directories;
  `*` stays inside one name.
- **A new directory is judged file by file.** `git status --porcelain` shows a new directory as one line. With the
  ticket path `tools/guard/**`, a new `tools/guard/a.py` is in scope although the line says `?? tools/`; a new
  `tools/other/b.py` next to it is reported, and the report does not name `tools/guard`.
- **Staged changes count,** and so do renames: both ends of a rename are compared.
- **A name with a space** is reported in plain form (`docs/my notes.md`).
- **Sessions without ticket paths.** No role, an empty or unknown role, a role without a ticket, a ticket that does not
  exist, and a role on another role's ticket: every change is reported.
- **Out-of-scope changes outside `tests/acceptance/**`.** The KPI asks for a report and a finding. Whether the check
  also undoes such a change is the implementer's choice; the tests take no side.
- **Restore from HEAD.** After the check, `tests/acceptance` equals HEAD: a changed or deleted file has its HEAD
  content, a file or directory HEAD does not hold is gone, and nothing under `tests/acceptance` stays staged. This holds
  for a deleted directory, the whole tree deleted, a file moved in or out, and a change made through
  `src/gov/guard/acceptance_link`.
- **The restore touches nothing else.** With an acceptance test and the engineer's own files changed in one call,
  `git status` afterwards shows exactly the engineer's own changes, staged ones still staged.
- **The test designer** keeps every change under `tests/acceptance/**`: changed, added and deleted files, on any
  ticket. A change elsewhere is reported.
- **Subagents.** A test-designer subagent in an engineer or orchestrator session keeps its acceptance tests. An
  engineer subagent in a test-designer session is restored.
- **Failed calls.** The same result is expected from the `PostToolUseFailure` input as from `PostToolUse`.
- **Nothing to report.** `ls -la`, `cat`, `git status --porcelain`, `git log`, an in-scope change, and a write to
  either scratch location give exit code 0 and no text for the agent.
- **No trace in git.** The check adds no line to `git status`.

## The Bash forms tested

All land outside the engineer's paths, and none holds a plain `> file`, `touch`, `rm`, `mv`, `cp`, `mkdir` or `sed -i`
aimed at the path it changes:

`python3 -c` · `python3 -` with a here-document · `bash -c` · `sh -c` · `eval` · a target in a shell variable · a target
from `$(…)` · a shell function · a shell alias · `cat > … <<EOF` · `dd of=` · `truncate` · `install` · `ln -s` ·
`find -delete` · `xargs rm` · `awk` · `sed` with the `w` command · `tar -x` · `git mv` · `git rm` · `git apply` ·
`shutil.copy` · `os.rename`.

Ten of them are also run against `tests/acceptance/**`, where the file must be restored.

## Not tested

With the owner (`~/gov-os-workbench/w1-tests/decision-packages/W1-03-kpi-disputes.md`):

- **KD-1.** Where and how a containment finding is recorded. DEC-110 names `.gov-runtime/findings.jsonl` for the guard
  only. Until the answer, "recorded as a containment finding", "the breach is recorded" and "without a finding" are
  tested through the report to the agent.
- **KD-2.** The "nine Bash write forms from S0b2 I-06". The list is not in the repository.
- **KD-3.** A working tree that was already dirty before the call: whose change it is, and whether it is reported
  again after every call. Every test starts from a clean tree.

Left open on purpose; the tests take no side:

- **"At gov close".** `gov close` is W1-30, and its KPI says it "runs the containment check". The run at close is left
  to W1-30's acceptance tests.
- **A change that the call itself commits.** `git status --porcelain` is clean after `git commit`, so the comparison
  the KPI names cannot see it.
- **A ticket that is not `in_progress`** (DEC-114 and DEC-116 are decisions on the guard).
- **An ignored path** outside the ticket paths; git does not show it.
- **A role subagent in a session with no or an unknown role** (W1-02 KD-9).
- **Unusable stdin, a missing `git`, a directory that is not a repository,** and the time the check takes. No KPI
  names them.
