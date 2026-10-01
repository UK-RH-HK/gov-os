# W1-02 — PreToolUse default-deny guard: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-emkd` (W1-02), the Contract v4
items it cites (CAP-05, CAP-38.c, CAP-39.a, CAP-58.a, CAP-58.c) and the owner's answers of 2026-10-01 to KPI disputes
KD-1 to KD-5. Written before implementation.

**Revised on 2026-10-01, after the implementation at `7d9ab30`,** for two owner decisions: DEC-117 (amends DEC-107:
inside a role subagent, the subagent's role governs) and DEC-115 (the guard resolves a Bash write target before judging
it). W1-02 is reopened as a repair for both. The rewrites are listed under
[Rewrites after implementation](#rewrites-after-implementation).

## Run

```sh
python3 -m pytest tests/acceptance/W1-02 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. Each test builds a small git project
in a temporary directory, copies the hook into it and runs the hook as a process. Nothing in the repository is written.

## KPI → tests → red reason today

Red run on `w1/integrate` at `5d65ba7`: 450 errors, 0 passed (450 cases, 67 test functions). Every case errors in the
`hook` fixture with the same reason: **no file matches `template/governance/kernel/hooks/pretooluse*`** — the guard
does not exist. That was the red reason for every row below.

Red run of the revision on `w1/integrate` at `d6bb6d5`, against the guard of `7d9ab30`: 59 failed, 472 passed (531
cases, 76 test functions).

| Tests | Cases red | Red reason today |
|---|---|---|
| `test_w1_02_subagent.py` | 13 of 52 | The guard still applies the stricter of the session's role and the subagent's: a role subagent is denied a write its own role allows whenever the session's role would not allow it |
| `test_w1_02_target_resolution.py` | 46 of 46 | The guard reads `~`, `$NAME`, `$(…)` and a glob as ordinary file names, so it judges a path the shell never writes |

The 39 green cases of `test_w1_02_subagent.py` hold behaviour the repair must keep: a subagent that is not a role stays
read-only (28 cases, DEC-113), reads stay open (4), and 7 role-subagent cases on which the two rules agree.

| KPI line or covers id | Test file | Test functions |
|---|---|---|
| **Success 1.** Edit/Write/Bash writes are allowed only inside the active ticket `allowed_paths` plus the kernel scratch set, per role [CAP-39.a, CAP-58.a] | `test_w1_02_allow_list.py` | `test_engineer_can_write_inside_the_ticket_paths` · `test_engineer_cannot_write_outside_the_ticket_paths` · `test_engineer_notebook_edits_follow_the_same_list` · `test_each_ticket_role_gets_its_own_ticket_paths_only` · `test_the_list_follows_the_active_ticket` · `test_a_ticket_of_another_role_gives_no_paths` · `test_a_known_role_without_a_ticket_gets_no_ticket_paths` · `test_role_and_ticket_are_read_on_every_call` |
| | `test_w1_02_bash_writes.py` | `test_engineer_bash_write_inside_the_ticket_paths_is_allowed` · `test_engineer_bash_write_outside_the_ticket_paths_is_denied` · `test_engineer_bash_read_is_let_through` · `test_bash_decisions_change_nothing_on_disk` |
| | `test_w1_02_scratch.py` | `test_every_known_role_can_write_to_the_scratch_set` · `test_scratch_needs_no_ticket` · `test_bash_write_to_the_scratch_set_is_allowed` · `test_the_rest_of_the_runtime_directory_is_not_scratch` · `test_only_the_temp_directory_itself_is_scratch` · `test_scratch_is_closed_without_a_known_role` |
| | `test_w1_02_subagent.py` | `test_a_role_subagent_writes_what_its_own_role_allows` · `test_a_role_subagent_gets_nothing_from_the_session_s_role` · `test_a_role_subagent_s_bash_writes_follow_its_own_role` · `test_a_subagent_that_is_not_a_role_stays_read_only` · `test_a_subagent_can_still_read` |
| | `test_w1_02_target_resolution.py` | `test_a_target_that_expands_into_the_engineer_s_paths_is_allowed` · `test_tilde_follows_the_hook_s_own_home` · `test_a_glob_is_judged_by_what_it_expands_to` · `test_the_test_designer_s_targets_are_resolved_too` · `test_resolving_a_target_runs_nothing` |
| **Success 2.** The engineer role is denied every write under `tests/acceptance/**`; the independent-test-designer role is allowed only there [CAP-38.c] | `test_w1_02_test_independence.py` | `test_engineer_cannot_write_under_acceptance_tests` · `test_engineer_cannot_reach_acceptance_tests_indirectly` · `test_no_ticket_role_can_write_under_acceptance_tests` · `test_a_ticket_that_names_acceptance_tests_still_gives_no_access` · `test_test_designer_can_write_under_acceptance_tests` · `test_test_designer_cannot_write_anywhere_else` · `test_test_designer_scope_does_not_depend_on_the_ticket_paths` · `test_test_designer_bash_write_under_acceptance_tests_is_allowed` · `test_test_designer_bash_write_elsewhere_is_denied` · `test_auditor_cannot_write_into_another_role_s_work` · `test_auditor_can_still_read` |
| | `test_w1_02_bash_writes.py` | `test_engineer_bash_write_under_acceptance_tests_is_denied` |
| **Success 3a.** The freeze flag (gov pause) denies every write | `test_w1_02_freeze.py` | `test_freeze_denies_the_write_each_role_could_otherwise_make` · `test_the_flag_freezes_by_existing_whatever_it_contains` · `test_freeze_closes_the_scratch_set` · `test_freeze_denies_notebook_edits` · `test_freeze_denies_bash_writes` · `test_no_agent_role_can_lift_the_freeze` · `test_reads_stay_open_while_frozen` · `test_freeze_leaves_git_status_unchanged` |
| **Success 3b.** The guard reads ticket frontmatter directly | `test_w1_02_allow_list.py` | `test_allowed_paths_come_straight_from_the_ticket_file` · `test_guard_reads_this_repository_s_own_ticket` |
| **Success 3c.** Decision in < 100 ms p95 | `test_w1_02_guard_hook.py` | `test_decision_p95_is_under_100_ms` (five decisions) |
| **Success 4.** A session with no declared role, or an unknown role, is read-only: every write is denied [CAP-58.c] | `test_w1_02_role_less_session.py` | `test_role_less_session_cannot_edit_or_write` · `test_role_less_session_cannot_edit_a_notebook` · `test_role_less_session_cannot_write_through_bash` · `test_no_ticket_state_gives_a_role_less_session_write_access` · `test_a_ticket_alone_declares_no_role` · `test_role_less_session_can_still_read_with_file_tools` · `test_role_less_session_can_still_read_through_bash` · `test_deciding_leaves_the_working_tree_unchanged` |
| | `test_w1_02_unknown_role.py` | `test_unknown_role_cannot_edit_or_write` · `test_unknown_role_cannot_edit_a_notebook` · `test_unknown_role_cannot_write_through_bash` · `test_unknown_role_gets_nothing_from_any_ticket` · `test_unknown_role_can_still_read` |
| **Failure 1.** Any write outside `allowed_paths` is allowed | `test_w1_02_allow_list.py` | `test_engineer_cannot_write_outside_the_ticket_paths` · `test_engineer_cannot_write_outside_the_repository` · `test_engineer_cannot_rewrite_the_installed_guard` · `test_a_ticket_of_another_role_gives_no_paths` |
| | `test_w1_02_bash_writes.py` | `test_engineer_bash_write_outside_the_ticket_paths_is_denied` |
| | `test_w1_02_target_resolution.py` | `test_a_target_that_expands_out_of_the_engineer_s_paths_is_denied` · `test_a_target_the_guard_cannot_resolve_is_denied` · `test_a_glob_is_judged_by_what_it_expands_to` |
| **Failure 2.** Guard crash or timeout lets the call through without a recorded finding | `test_w1_02_guard_failure.py` | `test_unusable_input_is_denied_with_exit_code_2` · `test_unusable_input_leaves_one_finding` · `test_findings_are_appended_one_line_per_failure` · `test_a_failure_does_not_show_in_git_status` · `test_input_that_never_ends_is_denied_by_the_guard_s_own_deadline` · `test_a_ticket_file_the_guard_cannot_use_never_lets_a_write_through` |
| **Failure 3.** A session with no or an unknown role can write anywhere | `test_w1_02_role_less_session.py`, `test_w1_02_unknown_role.py`, `test_w1_02_scratch.py` | The Success 4 tests · `test_scratch_is_closed_without_a_known_role` |
| **CAP-39.a** G0 guard tier | `test_w1_02_guard_hook.py` | `test_guard_hook_ships_in_the_kernel_template` · `test_guard_decides_before_the_tool_runs` |
| **CAP-58.a** default-deny allow-lists per role and ticket | `test_w1_02_allow_list.py` and the other Success 1 files | The Success 1 and Failure 1 tests |
| **CAP-38.c** independent test authorship | `test_w1_02_test_independence.py` | The Success 2 tests |
| **CAP-58.c** no or unknown role has no write privilege | `test_w1_02_role_less_session.py`, `test_w1_02_unknown_role.py` | The Success 4 tests |

**Count.** KPI lines with tests: 7 of 7. Covers ids with tests: 4 of 4.

## Owner answers the tests rely on (2026-10-01)

| Id | Answer | Where tested |
|---|---|---|
| KD-1 | A session declares its role and active ticket through the environment variables `GOV_ROLE` and `GOV_TICKET`, read on every call. Missing or unknown means read-only. ~~If the hook input also identifies a subagent, the stricter of the two applies~~ (amended by DEC-117, below) | `test_w1_02_allow_list.py`, `test_w1_02_unknown_role.py` |
| KD-2 | The scratch set is `.gov-runtime/scratch/**` plus the directory returned by `tempfile.gettempdir()` | `test_w1_02_scratch.py` |
| KD-3 | Until `gov pause` exists, the freeze flag is the file `.gov-runtime/freeze` | `test_w1_02_freeze.py` |
| KD-4 | A failing guard denies with exit code 2 and appends one line to `.gov-runtime/findings.jsonl` | `test_w1_02_guard_failure.py` |
| KD-5 | The guard judges the plain Bash forms; all other forms stay with W1-03 | `test_w1_02_bash_writes.py` |
| DEC-117 | Inside a subagent with a defined role, that subagent's role governs its tool calls. The session's role governs the main thread only. There is no "stricter of the two" | `test_w1_02_subagent.py` |
| DEC-113 | A subagent whose type is not a defined role is read-only | `test_w1_02_subagent.py` |
| DEC-115 | Before judging a Bash write target, the guard expands `~`, `~user` and environment variables from the hook's own environment. A target it still cannot resolve (command substitution, an unset or unknown variable, a glob it cannot expand) is denied | `test_w1_02_target_resolution.py` |

The readings listed under KD-1 in the decision package were accepted with it:

1. Known roles: `orchestrator`, `product-spec`, `independent-test-designer`, `engineer`, `independent-auditor`. Any
   other value of `GOV_ROLE` is an unknown role.
2. A known role with no ticket, or naming a ticket file that does not exist, gets no ticket paths.
3. A role working on a ticket whose `role:` field names another role gets no ticket paths.
4. The test designer may write `tests/acceptance/**` and no other repository path. Every other role is denied
   `tests/acceptance/**`, also when a ticket's `allowed_paths` name it.
5. The independent auditor is read-only. DEC-112 has since allowed it the report path of its own ticket; see Not tested.
6. A change to `allowed_paths` in the ticket file changes the next decision.

## How the tests drive the guard

- **Entry point.** The file matching `template/governance/kernel/hooks/pretooluse*`. If several files match, exactly one
  must be executable, and that one is run. An executable file is run directly; otherwise `.py` runs under `python3` and
  `.sh` under `bash`.
- **Where it runs.** Every matching file is copied to `governance/kernel/hooks/` of the temporary project, where Copier
  puts it in a product repository (ADR-0002 §5). The hook runs from there.
- **The `gov` package.** `src/` of this repository is on `PYTHONPATH`. That stands in for the installed package.
- **The project** is named three ways, as the harness does: the process working directory, `cwd` in the stdin object,
  and `CLAUDE_PROJECT_DIR`.
- **Stdin** is the harness's PreToolUse object: `session_id`, `transcript_path`, `cwd`, `permission_mode`,
  `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`. File tools get absolute paths. The subagent tests add
  `agent_id` and `agent_type`.
- **Environment.** Built from scratch: `PATH`, an empty temporary `HOME`, locale, `TMPDIR`, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX` and `CLAUDE_PROJECT_DIR`, plus `GOV_ROLE` and `GOV_TICKET` when the test declares them. No
  variable of the calling session is passed on. The target-resolution tests add four variables of their own
  (`W1_02_GUARD_DIR`, `W1_02_UP`, `W1_02_ELSEWHERE`, `W1_02_ACCEPTANCE_DIR`) and, in one test, another `HOME`.
- **`TMPDIR`** points at a directory next to the project, so `tempfile.gettempdir()` returns that directory inside the
  hook and the project is not inside the scratch set.
- **`GOV_TICKET`** holds the ticket id, the file name under `.tickets/` without `.md` (`DAEO-zz90`).
- **Decision** (register DEC-025):
  - *denied* — exit code 2, or exit code 0 with `hookSpecificOutput.permissionDecision` = `deny` on stdout;
  - *allowed* — exit code 0 with no `deny` and no `ask`;
  - any other exit code is a hook error, which the harness lets through. It counts as neither, so it fails both kinds of
    test.
  - For a guard failure (KD-4) only exit code 2 passes.

## The fixture project

Tickets, all `in_progress`:

| Ticket | Role | `allowed_paths` |
|---|---|---|
| `DAEO-zz90` | engineer | `src/gov/guard/**` · `tests/unit/guard/**` · `template/governance/kernel/hooks/pretooluse*` · `pyproject.toml` |
| `DAEO-zz91` | orchestrator | `.claude/settings.json` · `governance/project/bootstrap.md` |
| `DAEO-zz92` | product-spec | `template/governance/kernel/roles/**` · `docs/spec/**` |
| `DAEO-zz95` | engineer | `docs/**` |

Two committed symbolic links sit inside the engineer's directory: `src/gov/guard/acceptance_link` → `tests/acceptance`
and `src/gov/guard/docs_link` → `docs`. `.gov-runtime/` is ignored by git and does not exist at the start.

## Choices the implementer should know

- **Path patterns** are read as the W1-01 commit check reads them (DEC-097): anchored at the repository root; `**`
  crosses directories; `*` stays inside one name. So `pyproject.toml` does not cover `docs/pyproject.toml`, and
  `hooks/pretooluse*` covers `hooks/pretooluse_guard.sh` but not `hooks/sub/pretooluse.py`.
- **Where a write lands decides,** not how the path is spelled. `..` segments and symbolic links are followed:
  `src/gov/guard/../../../README.md` and `src/gov/guard/acceptance_link/W1-90/test_fixture.py` are denied to the
  engineer.
- **Outside the repository** every write is denied unless it is in the scratch set: the home directory, a directory
  next to the project, `/etc`.
- **Self-protection follows from the list.** The ticket file, `.claude/settings.json`, `.git/config`, the installed
  hook, the freeze flag and the findings file are outside every allow-list in the fixture, so writes to them are denied.
- **A ticket is not a role declaration,** and `GOV_TICKET` without `GOV_ROLE` is read-only. `GOV_ROLE` set to an empty
  string or a blank counts as no role.
- **Write tools.** Edit, Write and NotebookEdit.
- **Bash writes** (KD-5): `>`, `>>`, `| tee`, `touch`, `rm`, `mv`, `cp`, `mkdir -p`, `sed -i`, with relative targets,
  after `cd <dir> &&`, and with absolute targets.
  - A command with several writes is denied when one of them is outside.
  - `mv` writes at both ends: moving a file out of, or into, a place the role may not write is denied.
  - `cp` writes at the destination only.
  - `rm -r src` is denied to an engineer whose paths are below `src/`.
- **Reads stay open** for every session: Read, Grep, Glob, and the Bash commands `ls -la`, `cat <file>` and
  `git status --porcelain`. A guard that denies everything fails.
- **Scratch** (KD-2): open to each of the five known roles, with or without a ticket; closed to no role and to an
  unknown role; closed to everyone while frozen. The rest of `.gov-runtime/` is not scratch.
- **Freeze** (KD-3): the flag freezes by existing. A flag file that contains `false`, `off`, `0` or `{"freeze": false}`
  still freezes. No agent role can write or remove the flag, frozen or not.
- **Target resolution** (DEC-115). The guard judges where the shell would write, not the text of the target.
  - *Expanded from the hook's own environment:* `~` (the hook's `HOME`), `~user`, `$NAME`, `${NAME}`, bare or inside
    double quotes, in a target and in the directory of a leading `cd`.
  - *Allowed after expansion:* `$CLAUDE_PROJECT_DIR/src/gov/guard/decide.py`, `$W1_02_GUARD_DIR/new_module.py`,
    `$TMPDIR/w1-02.log` (scratch), and `~/…` when `HOME` is the project or lies in the scratch directory.
  - *Denied after expansion,* though the unexpanded text looks like a path inside `src/gov/guard`:
    `cd src/gov/guard && echo changed > ~/notes.py`, the same with `$HOME`, `~root`, a variable that holds an outside
    directory or the acceptance-test directory, and `src/gov/guard/$W1_02_UP/README.md` where the variable holds
    `../../..`.
  - *Denied as unresolvable:* `$(…)` and backticks in a target, a variable that is not set in the hook's environment,
    a variable that only the command itself sets (`D=../../.. && echo changed > $D/README.md`, also with `export`),
    and a glob that matches nothing.
  - *Globs.* A glob that matches is judged by its matches: `rm src/gov/guard/*.py` is allowed, and
    `rm src/gov/guard/*/notes.md` is denied because it matches `docs/notes.md` through `docs_link`.
  - *Nothing is run.* The guard resolves by reading the command. A command substitution with a side effect leaves no
    file behind, and `HOME` and the outside directory stay empty.
- **Subagents** (DEC-117, DEC-113).
  - *A role subagent is judged as its own role* on the active ticket (`GOV_TICKET`), whatever `GOV_ROLE` says. An
    engineer subagent in an orchestrator, test-designer or auditor session may write the engineer ticket's paths. A
    test-designer subagent in an engineer or orchestrator session may write `tests/acceptance/**`.
  - *Nothing of the session's role carries in.* An engineer subagent in a test-designer session is denied
    `tests/acceptance/**`; a test-designer subagent in an engineer session is denied source; an engineer subagent on
    the orchestrator's ticket is denied that ticket's paths.
  - *A subagent that is not a role* (`general-purpose`, `Explore`, `Plan`, `claude`, and look-alikes such as
    `Engineer`, `engineer-helper`, `test-designer`) is denied every write, scratch included, through Edit, Write and
    Bash. It can still read.
- **Guard failure** (KD-4):
  - Unusable stdin (not JSON, empty, cut off, not an object, no `tool_name`, no `tool_input`, `tool_input` not an
    object) → exit code 2 and exactly one new line in `.gov-runtime/findings.jsonl`. Earlier lines stay as they are.
  - The line is one JSON object with `source` = `"guard"`, non-empty strings `kind` and `reason`, and the keys
    `session_id` and `tool_name`. When the input still gave the session and the tool, the finding holds their values.
  - A stdin that never ends → exit code 2 within 5 s, and a finding. The harness lets a call through when a hook times
    out, so the guard needs a deadline of its own.
  - A ticket file the guard cannot use (not YAML, no frontmatter, empty, not UTF-8, a directory, unreadable) → every
    write is denied. A finding is not required here, because a guard may treat such a file as "no ticket paths".
- **No trace in git.** After any decision or failure, `git status --porcelain` of the project is unchanged.
- **Latency.** The time measured is the wall-clock time of the hook process, start to exit, which is what the harness
  waits for. p95 over 40 calls after 3 warm-up calls; a round that misses 100 ms is repeated, up to three rounds. Five
  decisions are timed: no role, engineer allowed, engineer denied, test designer allowed, frozen.

## Rewrites after implementation

The implementation at `7d9ab30` passed all 450 cases of `43fdf41`. These tests were changed afterwards, on the owner's
decisions of 2026-10-01 (register v0.18). No other test was touched.

| Test | Change | Reason |
|---|---|---|
| `test_the_stricter_of_session_role_and_subagent_role_applies` (15 cases) | Replaced by `test_a_role_subagent_writes_what_its_own_role_allows` (10 cases) and `test_a_role_subagent_gets_nothing_from_the_session_s_role` (9 cases). Three expectations turned from denied to allowed: the engineer subagent on source in a test-designer session and in an auditor session, and the test-designer subagent on an acceptance test in an engineer session. Nine cases are kept as they were. Seven cases are new, among them the engineer and the test-designer subagent in an orchestrator session. Three cases were removed: a role subagent in a session with no role or an unknown role (KD-9 below) | Owner correction of DEC-107 |
| `test_a_subagent_cannot_widen_the_session_s_bash_writes` | Replaced by `test_a_role_subagent_s_bash_writes_follow_its_own_role`. The test-designer subagent's Bash write to an acceptance test in an engineer session is now allowed, and its write to source denied | Owner correction of DEC-107 |
| `test_a_subagent_can_still_read` | Kept; now also run for an engineer subagent and two non-role subagents, with a Bash read | Owner correction of DEC-107 |
| `test_a_subagent_that_is_not_a_role_stays_read_only` (28 cases) | Added. Green today: the guard already does this | Owner correction of DEC-107 (its last sentence keeps DEC-113) |
| `test_w1_02_target_resolution.py`, 7 test functions (46 cases) | Added. No earlier test changed its expectation: the plain forms of `test_w1_02_bash_writes.py` hold no `~`, variable, substitution or glob | New target-resolution rule |
| `w1_02_support.py`, `conftest.py` | `run_hook`, `call` and `bash` accept extra environment variables for the hook process | New target-resolution rule |

## Not tested

With the owner (`~/gov-os-workbench/w1-tests/decision-packages/W1-02-kpi-disputes.md`):

- **KD-9.** A role subagent in a session that declares no role or an unknown role. DEC-117 says the subagent's role
  governs; KPI success 4 says such a session is read-only and every write is denied. The three cases that took the
  second side were removed, and none takes the first.

Answered by the owner since `43fdf41`, and still without an acceptance test here. This revision was asked for DEC-115
and DEC-117 only:

- **DEC-112** (was KD-6). The auditor on its own ticket may write that ticket's report path.
- **DEC-114 and DEC-116** (were "left open"): `GOV_TICKET` accepts the ticket id and the W1 id; writes require
  `status: in_progress`; a test designer without a claimed ticket has no write, scratch included; a repository inside
  the temp directory gets no temp-directory allowance; `/dev/null` is the only device target that is not a write.

Left open on purpose; the tests take no side:

- a `~user` that names no user on the machine, and a target inside single quotes, where the shell expands nothing;
- brace expansion (`{a,b}`) in a target;
- Bash forms outside the plain list (KD-5), and a record of each ordinary refusal (no KPI asks for one).
