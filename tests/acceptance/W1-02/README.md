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

### W1-45 (DEC-156): orchestrator write scope

Reason: **owner correction, DEC-156**. The orchestrator may write anywhere in the repository except
`tests/acceptance/**`; the guard enforces only that exclusion. Revised by the Independent Test Designer in the
W1-45 test design batch (DEC-106). No test for another role was changed; no test was weakened.

| Test | Change | Reason |
|---|---|---|
| `test_w1_02_allow_list.py` `OTHER_ROLES`: `orchestrator-neighbour-file`, `orchestrator-source`, `orchestrator-root-file` | Expected result changed from denied (False) to allowed (True) | DEC-156: the orchestrator is not confined to its ticket's `allowed_paths` |
| `test_w1_02_allow_list.py` `MISMATCHED`: `orchestrator-on-engineer-ticket`, `orchestrator-on-product-spec-ticket` | Removed | DEC-156: the orchestrator writes regardless of the active ticket's role |
| `test_w1_02_subagent.py` `ROLE_DENIES`: `orchestrator-in-engineer-session-on-the-engineer-s-ticket` | Moved to `ROLE_ALLOWS` | DEC-156: the orchestrator subagent may write source regardless of ticket |

## Revision of 2026-10-08: reads of the settings file and the held-out file (DEC-508, DEC-525)

W1-02 is reopened for one change ordered by the owner: **the guard refuses any agent tool call that reads the Claude
Code settings file of the project (`.claude/settings.json`) or the project's held-out file, for every role, the
orchestrator included**, and a small helper lists the registered hooks so that no session needs to open the settings
file. The cases were written before any code for the change. The change is stricter-only.

**The two files are never this repository's.** Every case builds a temporary project with a stand-in settings file
(a stand-in deny line, stand-in hooks, stand-in permission, environment and sandbox entries) and a stand-in held-out
file that lists a stand-in directory (`w1_02_protected_support.make_guarded`). **The held-out file's path is not
spelled anywhere in this suite:** it is imported from the guard's own module (`gov.guard.heldout.CONFIG_REL`, with
`CONFIG_KEY`). That import is the one thing these cases take from the package directly; `CONFIG_REL` and `CONFIG_KEY`
must keep their names. Every decision is asked of the hook, run as a process, as in the rest of the suite.

### Run and red count

```sh
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-02/test_w1_02_protected_reads.py \
  tests/acceptance/W1-02/test_w1_02_protected_reads_open.py tests/acceptance/W1-02/test_w1_02_hook_listing.py \
  -q -p no:cacheprovider -rs
```

Red run on `w1/W1-02` at `a0bd166b`, against the guard as built: **202 failed, 164 passed** (366 cases, 22 test
functions, about 30 s). The whole of `tests/acceptance/W1-02`: 202 failed, 693 passed (895 cases); the 529 earlier
cases are all green, the latency case included.

| File | Cases | Red | Reason |
|---|---|---|---|
| `test_w1_02_protected_reads.py` | 190 | 190 | The guard allows the read: every one of the 190 calls comes back `decision=allow`, exit code 0 |
| `test_w1_02_protected_reads_open.py` | 164 | 0 | What must keep working: green today, and it stays green |
| `test_w1_02_hook_listing.py` | 12 | 12 | The command does not exist (`No module named gov.guard.hooks`) |

### What the guard refused before the change

Found by running the hook on the stand-in project, for the eleven actors below and the 48 forms of
`test_w1_02_protected_reads.py`:

- **The settings file:** no read is refused, for any role, through any tool. Read, Grep, Glob and every shell form
  (`cat`, `head`, `grep`, `jq`, an input redirect, `git diff`, `git show HEAD:<file>`, an interpreter with a script on
  the command line) are allowed for a session with no role, an unknown role, each known role, a role subagent and a
  subagent that is not a role.
- **The held-out file:** the same: no read is refused, for anyone. The rule as built (DEC-162, DEC-215) hides the
  paths the file *lists*, not the file; reading the file that holds them was an accepted residual.
- **A copy with the file as its source** is decided as a write at its destination only: allowed when the role may
  write the destination (scratch for every known role), denied otherwise. The source is not looked at.
- **Writes** to either file are decided by the allow-list, as before.

So nothing of line 1 was held; every refusal case is red.

### The owner's lines → tests

Actors ("every role"): no role, an unknown role (`developer`), `orchestrator`, `engineer`, `product-spec`,
`independent-test-designer`, `independent-auditor`, `research`, `ticket-lead`, an `engineer` subagent of the
orchestrator, a `general-purpose` subagent of the engineer.

| Line | Test file | Test functions |
|---|---|---|
| **1.** The guard refuses any agent tool call that reads either file, for every role | `test_w1_02_protected_reads.py` | `test_a_read_of_a_protected_file_is_refused` (42 forms × 2 files, by the orchestrator) · `test_a_command_that_prints_the_settings_file_is_refused` (6; the DEC-525 incident is `interpreter-loading-the-settings-for-their-hooks`) · `test_the_search_behind_dec_508_is_refused` (the DEC-508 incident, by the test designer) · `test_a_read_of_a_protected_file_is_refused_for_every_role` (4 forms × 11 actors × 2 files) · `test_a_read_of_a_protected_file_is_refused_while_frozen` |
| **2.** What a guard reading a command line cannot see is not pretended | this README | [Residuals](#residuals); no case |
| **3a.** `git diff --stat` and `git status` naming the settings file | `test_w1_02_protected_reads_open.py` | `test_git_diff_stat_and_git_status_on_the_settings_file_stay_allowed` (6 forms × 4 actors) |
| **3b.** A write to the settings file where the role may write it today | `test_w1_02_protected_reads_open.py` | `test_a_write_to_the_settings_file_is_decided_as_today` (20 actors × Write, Edit) · `test_a_bash_write_to_the_settings_file_is_decided_as_today` (a redirect, a copy with the file as destination × 4 actors) |
| **3c.** The harness's own use of the settings file | this README | [What stands](#what-stands); no case can exist |
| **3d.** Ordinary work near the two files | `test_w1_02_protected_reads_open.py` | `test_another_file_of_the_same_folder_named_alone_stays_readable` (6 forms × 3 actors × 2 files) · `test_a_read_a_search_or_a_listing_that_takes_neither_file_in_stays_allowed` (14 forms × 3 actors) · `test_text_that_mentions_the_settings_file_is_not_a_read` (3) |
| **3e.** Every decision W1-02's and W1-50's suites hold today | the 529 earlier cases of this suite; W1-50's suite | unchanged, with one point returned as a package (DP-1) |
| **4.** A helper for hook listings | `test_w1_02_hook_listing.py` · `test_w1_02_protected_reads_open.py` | the 9 functions of the first file (12 cases) · `test_the_helper_s_command_is_allowed_for_every_role` (11 actors) |
| **5.** A refusal names the rule and the decision, not the file's content | `test_w1_02_protected_reads.py` | `test_a_refusal_names_the_decision_and_nothing_of_the_file` (5 forms × 2 files) |

### The forms held as refused

`{file}` is either stand-in file, `{folder}` the folder that holds it.

- **File tools.** Read of the file: absolute, relative, with a limit, through `..`, through a symbolic link. Grep in
  the file (absolute, relative, through the link). Grep over `{folder}` (absolute, relative, and with a glob for the
  file's extension). Glob in `{folder}` (`path` = the folder; a pattern `{folder}/*`; an absolute pattern). From the
  project root with a glob that takes the file in: Grep with `glob` = `*<extension>` or `{folder}/**`; Glob with
  `**/*<extension>` or `**/<name>`; Glob with the file's own path as the pattern.
- **Shell.** `cat` of the file: relative, absolute, double-quoted, single-quoted, `./`, through `..`, through
  `$CLAUDE_PROJECT_DIR` (a variable of the hook's environment), through a symbolic link, after `cd {folder} &&`, by
  a glob `{folder}/*`, beside another file. `head`; an input redirect (`wc -c < {file}`); the first command of a
  pipeline; after `&&`. `grep` in the file; `grep -rn` over `{folder}`; `ls -la {folder}`; `find {folder} -type f`.
  `cp` with the file as its source, into scratch (relative and absolute). An interpreter with a script on the command
  line that names the file, relative or absolute (`python3 -c "print(open('{file}').read())"`).
- **The settings file alone.** The incident form, `python3 -c "import json; print(json.load(open('…'))['hooks'])"`;
  `jq .hooks {file}`; `git diff {file}`; `git diff --stat -p {file}`; `git show HEAD:{file}`; and
  `git diff --stat {file} && cat {file}`.
- **A refusal is a decision of a rule:** exit code 0 with `permissionDecision: deny`. Exit code 2, the guard's report
  of its own failure (DEC-110), does not pass these cases.

### What a refusal says (line 5)

For five forms on each file the cases read the reason and everything else the hook wrote (standard output and
standard error):

- the reason holds `DEC-508` or `DEC-525`, and words beside the decision id (the rule);
- for the stand-in held-out file: the file's path (relative and absolute), its name and the directory it lists appear
  nowhere. Three of the forms are shell commands that name the file, so a refusal that echoes the command fails;
- for the stand-in settings file: no deny value, no allow or ask value, no environment name or value and no sandbox
  value appears. The settings file's own path may be named.

A failing case does not print the values either: it reports their positions in `Guarded.secrets`.

### What stands

- **Who may write the settings file** (found in `decide.py` and held by the 48 write cases, all green): an
  orchestrator session, on any ticket or none (DEC-156); any other role only on an in-progress ticket of its own
  role whose `allowed_paths` name the file (the engineer on `DAEO-zz96`; an engineer subagent on that ticket; an
  orchestrator subagent in another role's session on the orchestrator's ticket that names it). Everyone else is
  denied: a role on a ticket that does not name the file or belongs to another role, the test designer, the auditor,
  research and the ticket lead on a ticket that names it, a subagent that is not a role, no role, an unknown role.
  As the target of a shell write (`>`, the destination of `cp`) the file is a write and is decided the same way.
  The `Edit` deny rules for `.claude/**` in launched worker sessions (DEC-315) and rulesync's ownership of
  `.claude/` (W1-38) are not the guard's and are untouched.
- **The harness's own use of the settings file** is no tool call: the harness loads the file itself, and no
  PreToolUse input exists for that. The guard decides tool calls only, which every case here shows by its form (a
  hook input in, a decision out); the registered hooks keep running, as W1-05's suite holds.
- **`git diff --stat` and `git status`** naming the settings file, relative or absolute, with or without `--`.
- **Near the files:** another file of the same folder named alone (Read, Grep, Glob, `cat`, `grep`); a file and a
  folder below `.claude/`; a search over `src/`; from the root, a Grep with `glob` = `*.py` or `src/**` and a Glob
  for `**/*.py`; `ls -la` of the root; `cat README.md`.
- **A mention is not a read** in a file tool or a brief: a Grep pattern that holds the file's name, the content of
  a Write to another file, and the prompt of an `Agent` call may name `.claude/settings.json`.

### The helper

Settled from the sources:

- **Where it lives.** In the guard's package, on this ticket's paths: `src/gov/guard/hooks.py`, run as a module, the
  way `python3 -m gov.guard.heldout` already is. No new `gov` subcommand; W1-07's command set is not touched.
- **How the guard lets exactly that helper read the file.** The guard decides a tool call by its file targets, and
  the helper's command line names none: it takes no argument and finds the file from the project. So the guard needs
  no exception for it, and `test_the_helper_s_command_is_allowed_for_every_role` holds that the command stays an
  ordinary read-only command for all eleven actors. Any other command has to name the file to read it, and is refused.

The interface the cases require:

| | |
|---|---|
| Invocation | `python3 -m gov.guard.hooks`, no argument |
| Project | `CLAUDE_PROJECT_DIR`; without it, the working directory. The file read is that project's `.claude/settings.json` |
| Output | exit code 0; standard output is one JSON array, one object per registered hook command, in the file's order, each with exactly the keys `event`, `matcher`, `command` (strings). A matcher that is left out is `""`. Other keys of an entry (`type`, `timeout`) are left out |
| Redaction | every value of `permissions.deny` that appears inside a hook command is replaced by `[redacted]`; the rest of the command stays |
| Nothing else | no deny line, no permission entry, no environment entry, no sandbox entry, none of their keys |
| No hooks | no `hooks` key, an empty `hooks`, or `{}`: `[]`, exit code 0 |
| No settings file | exit code 1, nothing on standard output, one line on standard error that names `.claude/settings.json` |
| Not valid JSON | the same, and the line carries nothing of the file (a parser's message is not passed on) |
| Writes | nothing: `git status --porcelain` of the project is unchanged |

A throwaway helper of about 30 lines passed all 12 cases; it lived in the session's temporary folder only.

### Residuals

**What a guard that reads a command line cannot see** (no case; none is pretended):

1. A script file that opens either file, by a literal or a computed name: the guard reads the command, not the script.
2. A script on the command line that builds the name (joined parts, a variable, an encoding).
3. An interpreter or a shell fed by a pipe or by standard input.
4. A name that reaches the command at run time: command substitution, a variable the command itself sets, `xargs`,
   `find -exec`. The guard refuses such a target for a *write* today (DEC-115), and that stays; a read is not held.
5. A command that names no path and reads the tree or the history by itself: `git diff` and `git diff --stat -p`
   with no path, `git show <commit>`, `git log -p`, `git stash show -p`, `git grep`, `rg` with no path, an archive
   of the root.
6. A git object read by its id (`git cat-file -p <id>`).
7. A second name made earlier and outside the call: a hard link, or a copy, that already exists.
8. A program that reads the settings file by itself (a `claude` process started from the shell, `rulesync`).
9. A tool the guard does not know (an MCP file tool, a tool added later) with the file in one of its fields.

**Left open on purpose; the cases take no side:**

- an unrestricted recursive search from the project root, through any tool (package DP-1);
- a deny line's bare path inside a hook command, in the helper's output (package DP-2);
- a shell command that only mentions the settings file (a commit message, an `echo`), and git commands other than
  the two named ones that take the file as a path without printing it (`git add`, `git log --oneline --`): a guard
  that refuses them is stricter than ordered, a guard that allows them reads nothing; neither is held;
- `git diff --stat` and `git status` naming the held-out file (the order names the settings file only);
- Grep with a `type` filter; `~` and `$HOME` spellings; a look-alike sibling such as `.claude/settings.local.json`;
- who may write the held-out file (unchanged, and not restated here);
- the helper called with arguments.

### Second batch: more spellings of a read (`test_w1_02_protected_reads_forms.py`)

A review of the implementation found spellings of a read that no case held. The order is unchanged; each form is
visible in the hook input, reads one of the two files, and must be refused by a rule's decision (`deny`, exit code
0). Every form is asked on both stand-in files, by the orchestrator (the role with the widest scope).

```sh
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-02/test_w1_02_protected_reads_forms.py \
  -q -p no:cacheprovider -rs
```

Red run on `w1/W1-02` at `97fd99cc`, against the guard as built: **71 failed, 10 passed** (81 cases, 8 test
functions, about 15 s). Every red case has one reason: the guard allows the read (`decision=allow`, exit code 0). The
three earlier files of this revision: 366 passed.

`{file}` is either stand-in file, `{folder}` its folder, `{name}` its bare name, `{other}` another file's name.

| Form | Test function | Spellings | Cases | Red |
|---|---|---|---|---|
| **1.** A search whose glob is the file's own name | `test_a_search_whose_glob_names_the_file_is_refused` · `test_a_search_from_a_folder_above_with_the_bare_name_as_its_glob_is_refused` | Grep with `glob` = `{name}` from the root (`path` = the root; no `path`); Grep from the root with `glob` = `/{file}`; Grep with `glob` = `{name}` from the folder between the root and the held-out file's folder (the settings file's folder is directly under the root) | 7 | 7 |
| **2.** An input redirect in every spelling | `test_a_shell_spelling_of_a_read_is_refused` | `echo a;<{file} cat` · `(<{file} cat)` · `true&&<{file} cat` · `true\|<{file} cat` · `echo $(<{file})` · `echo "$(<{file})"` · `cat <>{file}` | 14 | 14 |
| **3.** Backticks | the same | ``echo `cat {file}` `` · ``echo "`cat {file}`"`` | 4 | 4 |
| **4.** A brace expansion | the same · `test_a_search_whose_glob_names_the_file_is_refused` · `test_a_listing_glob_with_braces_around_the_name_is_refused` | `cat {folder}/{{name},{other}}` and with the name last; Grep from the root with `glob` = `{{name},{other}}`; Glob with the pattern `{folder}/{{name},{other}}` | 8 | 8 |
| **5.** A substitution inside the two git forms | `test_a_shell_spelling_of_a_read_is_refused` | `git diff --stat "$(cat {file})"` · ``git diff --stat `cat {file}` `` · `git status "$(cat {file})"` · ``git status `cat {file}` `` · `git diff --stat <(cat {file})` · `cat <<< "$(cat {file})"` | 12 | 12 |
| **6.** Into the folder, then a search that names no path | the same · `test_a_search_with_no_path_in_a_session_that_stands_in_the_folder_is_refused` | `cd {folder} && grep -r VALUE` · `cd {folder} && rg VALUE` · `cd {folder}; grep -rn VALUE` · `cd {folder} && ls` · `grep -r VALUE` with the hook input's `cwd` = `{folder}` | 10 | 10 |
| **7.** `cd` with an option | `test_a_shell_spelling_of_a_read_is_refused` | `cd -P {folder} && cat {name}` · `cd -- {folder} && cat {name}` · `pushd {folder} && cat {name}` | 6 | 6 |
| **8.** The name glued to a prefix in one word | the same | `python3 -m pytest @{file}` · `gcc @{file}` · `grep -f{file} README.md` | 6 | 6 |
| Another role | `test_a_shell_spelling_of_a_read_is_refused_for_another_role` | `echo a;<{file} cat` and ``echo `cat {file}` `` by the engineer | 4 | 4 |

No listed form was refused before this batch. Spellings next to them that the guard already refuses, found by
running the hook, and given no case: `cat<{file}`, `cat 0<{file}`, `<{file} cat`, a loop fed by `< {file}`;
`echo $(cat {file})`, quoted or not, and `git status $(cat {file})` unquoted; `cat <(cat {file})`;
`cd {folder}; cat {name}`, `(cd {folder} && cat {name})`, `cd {folder} && cat *`, `cd {folder} && grep -r VALUE .`;
`cat`, `Read`, a Grep with no path and a Glob for `*` when the hook input's `cwd` is the folder; `?` and `[…]` globs
in a shell word and in a tool's glob; `--file={file}`, `dd if={file}`; `eval`, `bash -c`, `sh -c`, `source`;
`git diff --stat` with `-p`, `--patch`, `-u`, `-U3`, `--word-diff`, `git diff --patch-with-stat`, `git status -v`.

Forms beyond the eight that were asked for, each settled by the order's words (the call's expanded targets take the
file in, or the shell opens it): the redirect glued after `&&` and after `|`; braces in a Grep `glob` and in a Glob
pattern; a process substitution inside `git diff --stat` and a substitution inside a here-string; `cd {folder} && ls`
(the listing the earlier cases hold as `ls -la {folder}`); the search with no path when the session already stands
in the folder; `pushd`; a file glued to a short option (`-f{file}`).

**What keeps working** (10 cases, green before and after): `cd {folder} && cat {other}`, `wc -c < {folder}/{other}`
and `cat {folder}/{{other},w1-02-other.md}` beside each file
(`test_the_same_spelling_on_another_file_of_the_folder_stays_allowed`); a Grep from the root whose `glob` is
`{other}` (`test_a_search_from_the_root_whose_glob_is_another_file_s_name_stays_allowed`);
`git diff --stat "$(git rev-parse HEAD)"` and `git status "$(git rev-parse --show-toplevel)"`
(`test_git_diff_stat_and_git_status_with_a_substitution_that_reads_neither_file_stay_allowed`).

**Read with this batch:** residual 4 above is about a *name* that only exists at run time (the output of a
substitution used as a path). A substitution whose own command names the file (`$(cat {file})`, backticks,
`$(<{file})`) is visible in the command and is held as refused here.

**Added to the residual list** (what a guard that reads a command line cannot see):

10. An argument file or a response file (`@{other}`) whose content names either file.
11. A `cd` whose folder exists only at run time (a variable the command sets, a substitution's output, `cd -`,
    `CDPATH`), followed by a bare name or a search with no path.
12. A shell function or an alias defined in the command that hides the reading program or the change of folder.

**Not in this batch, with the owner; no case either way:** a search from the root with no glob or with a type filter
only, or from above the root (DP-1); a listing glob for everything from the root; a move, a hard link or an in-place
edit with a backup suffix that gives the file a second name; copies of the two files outside the project; a shell
command that only mentions the file; how far the helper redacts (DP-2).

No earlier case was changed and the support module is as it was. No decision package comes with this batch.

### Third batch (2026-10-09): the four points of DEC-548

DEC-548 decided four of the points the second batch left open: DP-2 (the helper also redacts a deny rule's absolute
path held bare in a hook command), DP-3 (a second name is a read), DP-4 (the same two files outside the session's
own project, and the user-level settings file), DP-5 (the refusals beyond the order stand as built). DP-1 (a search
from the root) is still with the owner: no case here takes a side on it and none of the cases that hold a root
search as allowed was touched.

Written before any code. Five test files and one support module (`w1_02_copies_support.py`), all new; 331 cases.

```
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-02/test_w1_02_hook_listing_paths.py \
  tests/acceptance/W1-02/test_w1_02_second_names.py tests/acceptance/W1-02/test_w1_02_copies.py \
  tests/acceptance/W1-02/test_w1_02_copies_open.py tests/acceptance/W1-02/test_w1_02_refusals_beyond_the_order.py \
  -q -p no:cacheprovider -rs
```

Red first, 2026-10-09: **198 failed, 133 passed** in about 30 s. The whole of `tests/acceptance/W1-02`, once:
198 failed, 1109 passed (1307 cases, 4 min 31 s); the 198 are these and no other, the latency case passed in the
whole run, nothing was skipped.

| File | Point | Cases | Red | Green | Why red today |
|---|---|---|---|---|---|
| `test_w1_02_hook_listing_paths.py` | DP-2 | 23 | 18 | 5 | the helper prints a deny rule's path when a hook command holds it without the rule around it |
| `test_w1_02_second_names.py` | DP-3 | 120 | 54 | 66 | a move, a rename, a hard link, a linking copy and `sed` in place with a backup suffix are decided as writes only: allowed for a role that may write the file (40 cases), denied by the allow-list and not by the rule for the others (14) |
| `test_w1_02_copies.py` | DP-4 | 126 | 126 | 0 | every read of a copy is allowed, and so is a symbolic link to one and a second name below `template/` by the orchestrator (114); a second name of a copy outside the project is denied by the allow-list only (12) |
| `test_w1_02_copies_open.py` | DP-4 | 30 | 0 | 30 | — (what keeps working) |
| `test_w1_02_refusals_beyond_the_order.py` | DP-5 | 32 | 0 | 32 | — (as built) |

Every red case fails on the decision itself: `decision=allow`, or a denial whose reason names none of DEC-508,
DEC-525, DEC-548 (the allow-list's), or a helper output that still carries the path. None fails on an import, a
fixture or a crash.

**The world of the cases** (`w1_02_copies_support.make_world`): one temporary session project with both stand-in
files (the fixture of the revision), and copies of them at the same project-relative path under other folders
`<P>`: a sibling checkout (a git repository of its own), a folder that is no repository, a git worktree of the
session project, `template/` below the project's root, and the `HOME` of the hook's environment (the settings file
only). The real home folder is never read: `~` and `$HOME` in a command are the stand-in. No file of this repository
is opened and the held-out file's path is imported, never typed.

**How "refused by the rule" is told from a denied write** (`assert_refused_by_the_rule`): `deny`, exit code 0, and
a reason that names one of DEC-508, DEC-525, DEC-548. The allow-list's denial of a write names no decision, so it
does not pass: DP-3 says "refused as a read, for every role". If the implementer words the refusal under another
recorded decision, that line of the support module is the one to discuss, not the cases.

#### The reading before the cases (DP-4: "if a suite reads such a copy through a tool call")

Read for hook calls that name either file, a copy of one, the user-level settings file, another checkout or a
worktree: `tests/unit/guard` and the acceptance suites W1-01, W1-03, W1-04, W1-05, W1-07, W1-28, W1-29, W1-38, W1-45,
W1-46, W1-47, W1-49 and W1-50. Found:

- Every hook call in another suite that names either file is in the session's own project and is a **write**:
  W1-05 `test_the_engineer_writes_only_inside_the_ticket_paths`; W1-47
  `test_an_edit_to_a_file_that_holds_the_path_is_not_denied_for_carrying_it`,
  `test_the_usual_role_rules_still_apply_to_the_two_files`, `test_the_exception_is_for_the_two_files_only`,
  `test_the_exception_does_not_open_the_path_itself` (held as denied); W1-46
  `test_a_file_tool_write_to_the_three_trees_is_refused_by_the_guard` and the research role's writes; the
  `echo changed >> …` and Write cases of W1-45 and W1-03. DP-3 leaves a plain write as it is: no conflict.
- No case reads a copy in a second project, a sibling or a parent folder; none names the main tree's file from a
  worktree; none reads the user-level settings file through a tool call. The `HOME` cases of W1-47 name a stand-in
  held-out folder below a stand-in home, not a settings folder.
- The root searches of W1-05, W1-50 and W1-47 are DP-1: untouched.
- The unit case `test_a_project_without_either_file_refuses_nothing` uses files that do not exist and a glob over
  everything: both are points on which this batch takes no side.

**No suite goes red by DP-4 as these cases hold it; nothing is returned by name.**

#### DP-2 → `test_w1_02_hook_listing_paths.py`

An absolute path in a deny rule is the argument that starts with two slashes (`Tool(//<abs>…)`), as the harness
writes one; its tail may be `/**`, `/` or nothing, a blank may follow the bracket, the tool may be any.

- `test_a_deny_rule_s_absolute_path_held_bare_in_a_hook_command_is_redacted` (6 spellings of the rule): the path
  alone in a hook command prints as `[redacted]`, the rest of the command unchanged.
- `test_the_path_with_the_rule_s_wildcard_part_or_inside_a_word_is_redacted` (5): with `/**` or `/` after it,
  quoted, after `=`, inside a longer word.
- `test_the_path_as_the_start_of_a_longer_path_is_redacted` (4): a file below the path; only "the deny path is
  gone" is asserted, not what becomes of the tail (residual 14).
- `test_every_place_a_command_holds_the_path_is_redacted`, `test_the_paths_of_several_deny_rules_are_all_redacted`,
  `test_a_path_that_starts_like_another_rule_s_path_is_redacted_whole` (1 each).
- Green before and after (5): `test_the_argument_of_a_deny_rule_that_is_no_absolute_path_is_not_blanked` (3: a
  Bash prefix rule, a relative `./` glob, a bare relative glob: ordinary words of a command stay),
  `test_a_hook_command_that_holds_no_deny_path_prints_unchanged`,
  `test_a_whole_deny_value_with_an_absolute_path_is_still_redacted_as_one` (as built).

A failure message never prints the path it looks for (positions only).

#### DP-3 → `test_w1_02_second_names.py`

- `test_a_second_name_for_a_protected_file_is_refused_as_a_read` (20 forms × 2 files, by the orchestrator, which may
  write both): move (relative, absolute, `-t`), rename in the folder, hard link (`ln`, absolute, `link`), symbolic
  link (`-s` absolute and relative, `--symbolic`), linking copy (`-l`, `--link`, `-al`, `-s`, `--symbolic-link`),
  in-place edit with a backup (`sed -i.bak`, `sed -i .bak`, `sed --in-place=.bak`, `perl -i.bak`, `perl -pi.bak`).
  26 red, 14 green.
- `test_a_second_name_is_refused_as_a_read_whether_or_not_the_role_may_write_the_file` (8 forms × 2 files × an
  engineer whose ticket names the file and one whose ticket does not): 24 red, 8 green.
- `test_the_refusal_of_a_second_name_names_the_rule_and_nothing_of_the_file` (4, red).
- Green before and after: `test_a_plain_write_to_a_protected_file_is_decided_as_today` (Write, Edit, `>`, the file
  as the destination of `cp` and of `mv`, `sed -i`, `sed --in-place` × 2 files × 3 actors = 42: allowed for the
  orchestrator and for the engineer whose ticket names the file, denied for the other engineer);
  `test_an_interpreter_in_place_with_no_backup_is_decided_as_today` (2: `perl -pi -e` is refused today for naming
  the file, and stays so).

#### DP-4 → `test_w1_02_copies.py` (refused) and `test_w1_02_copies_open.py` (keeps working)

Refused, all red today:

- `test_a_read_of_a_copy_in_another_checkout_is_refused` (24 forms × 2 files): Read by the absolute path, relative
  with the working folder in the copy's site, relative from the project, with `..`, through a symbolic link; Grep in
  the copy, over its folder, from `<P>` with a glob that matches and with the bare name; Glob in its folder, by name
  from `<P>`, by an absolute pattern over its folder; `cat` in the same five spellings and after `cd`; `<`; `cp`
  with the copy as source; an inline script; a listing, a recursive search and a shell glob over its folder.
- `test_a_search_for_the_file_s_name_from_a_folder_between_is_refused` (1).
- `test_a_read_of_a_copy_anywhere_else_or_in_a_worktree_is_refused` (4 forms × 2 sites × 2 files).
- `test_a_read_of_a_copy_below_the_project_s_root_is_refused` (7 forms × 2 files; `template/` as `<P>`).
- `test_a_read_of_the_user_level_settings_file_is_refused` (11: absolute, through a link, `~`, `$HOME`,
  `"${HOME}"`, `<`, `cp`, Grep and Glob over its folder, a listing of `~/<folder>`).
- `test_a_read_of_a_copy_is_refused_for_every_role` (the 11 actors of the revision);
  `test_a_read_of_the_user_level_settings_file_is_refused_for_every_role` (3).
- DP-3 on a copy: `test_a_second_name_for_a_copy_in_another_checkout_is_refused_as_a_read` (5 × 2),
  `…_below_the_project_s_root_…` (2 × 2), `test_a_second_name_for_the_user_level_settings_file_is_refused_as_a_read`
  (2).
- `test_the_refusal_for_a_copy_names_neither_the_copy_nor_its_folder` (6): no path of the copy, no folder of it, not
  `<P>`, no value of the file.

Every one names the copy, its folder, or a glob with a literal start at or below `<P>`: none needs the guard to walk
a tree.

Keeps working, green before and after:

- `test_another_file_of_a_copy_s_folder_named_alone_is_still_read` (10): Read and `cat` of a neighbour, in another
  checkout, below `template/`, beside the user-level settings file.
- `test_the_rest_of_a_copy_s_site_is_still_read` (7): a file at the root of another checkout, a source file and a
  source folder of it; a file and a folder **below** the folder that holds the user-level settings file (where the
  harness keeps its own records).
- `test_a_plain_write_to_a_copy_is_decided_as_today` (6) and
  `test_a_plain_write_to_the_user_level_settings_file_is_decided_as_today` (1): outside the project a write is
  denied for every role, below `template/` the allow-list decides.
- `test_git_status_and_diff_stat_stay_allowed_on_a_copy` (6).

No case, by the brief: a search from `<P>` with nothing that selects the file, or from a folder above `<P>` (DP-1's
question, on a copy); a path that ends in the file's project-relative path and names no existing file.

#### DP-5 → `test_w1_02_refusals_beyond_the_order.py` (all green today)

- `test_a_command_that_only_mentions_the_settings_file_s_path_is_refused` (3 forms × 2 actors): a commit message,
  an `echo`, an `echo` of a sentence.
- `test_a_folder_that_holds_either_file_is_refused_in_a_command_that_does_not_read` (4 × 2 files): `git add` of the
  folder (relative, absolute), `test -d`, `git log -- <folder>`.
- `test_a_folder_above_the_held_out_file_inside_the_project_is_refused_in_a_command_that_does_not_read` (2).
- `test_git_diff_stat_with_a_folder_option_is_refused` (2 × 2 files): `git -C <project>` and `git -C .`.
- Allowed: `test_git_status_and_diff_stat_with_no_other_option_stay_allowed` (5 × 2 files),
  `test_git_status_and_diff_stat_with_no_file_stay_allowed` (2).

#### What the guard already refused before this batch

Found by running the hook as a process on these calls (no file of this repository opened):

- DP-2: a whole deny value inside a hook command (as built). Not the bare path.
- DP-3: as reads, for every role: a symbolic link to either file (`ln -s`, `-sf`, `--symbolic`), `cp -s` and
  `cp --symbolic-link`, `perl -i.bak`, `perl -pi.bak`, `ruby -i.bak`, and `perl -pi -e` with no backup. As writes
  only: `mv` with the file as source, `ln`, `link`, `cp -l`, `cp --link`, `cp -al`, `sed -i.bak`,
  `sed --in-place=.bak` (allowed for a role that may write the file). A rename inside the folder and `sed -i .bak`
  (the suffix as a word of its own) were allowed for the orchestrator only.
- DP-4: nothing. Every read of a copy was allowed at all five sites, for every actor asked. A write to a copy
  outside the project was denied by the allow-list; `ln -s <copy>` was allowed.
- DP-5: all of it, as the decision says.

#### Added to the residual list

13. The helper (DP-2): a deny rule's path written in a project-relative spelling (one leading slash, `./`, a bare
    relative glob) and then held bare in a hook command: it prints, and a case holds that it does (DEC-553: redacting
    it would blank ordinary relative paths). *Amended by the fourth batch:* the spelling from the home folder (`~/`)
    is no residual any more; it is redacted as written and with the home folder in its place.
14. The helper (DP-2): the tail of a longer path that starts with a deny rule's path. The deny path is gone; whether
    the tail prints is not held.
15. A copy reached by a glob or a search whose start is above `<P>` (`**/<name>` from the folder that holds several
    checkouts, from the home folder, from `/`): telling needs a walk of the tree, or a refusal by pattern alone
    (package DP-6). The same search from `<P>` itself with no glob at all follows DP-1. *Amended by the fourth
    batch:* a glob of wildcards alone from `<P>` itself is no residual any more (DEC-553: refused as from the
    session's root); the start above `<P>` stays, with DP-1.
16. A path that ends in either file's project-relative path and names no existing file (a copy made later in the
    same command, a folder that exists only at run time). No case either way, by the brief.
17. A copy under another name or at another relative path (the file copied to `notes.txt`, a backup an editor left,
    an archive that holds it). DP-4 covers a path that ends in the file's project-relative path.
18. `git -C <another checkout>` with a path relative to that checkout, and a `cd` into `<P>` that exists only at
    run time, followed by the relative path (as residual 11, on a copy).
19. A second name made by a program the guard does not know as one (`rsync --link-dest`, `install`, `cp --reflink`,
    `git mv`, `tar`, an editor's own backup), or by a script (residuals 1 to 3).
20. An in-place option the guard cannot tell from a backup suffix without knowing the program's version
    (`sed -i .bak` is a suffix on BSD and a script on GNU); held here as a second name. Other programs' in-place
    options with a suffix (`ruby -i.bak` is refused today; `awk -i inplace -v inplace::suffix=`) are not held.
21. A user-level settings file that is not at `$HOME` of the hook's environment (a harness told by an environment
    variable to keep its folder elsewhere, another user's home).

Residuals 1 to 12 stand.

### Fourth batch (2026-10-09): the three points of DEC-553

DEC-553 decided three points the third batch returned: DP-6 (a glob made of wildcards alone from the folder a copy
lies under is refused as from the session's own root), DP-7 (the helper also redacts a deny path spelled from the
home folder, as written and with the home folder in its place), DP-8 (a move or a link of a folder that holds either
file or a copy is a second name and is refused as a read, for every role). DP-1 (a search from the root, and with it
a glob or a search from above `<P>`) is still with the owner: no case here takes a side on it, and none of the cases
that hold a root search as allowed was touched.

Written before any code. Three test files and one support module (`w1_02_folders_support.py`), all new; 383 cases.

```
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-02/test_w1_02_wildcard_globs.py \
  tests/acceptance/W1-02/test_w1_02_hook_listing_home_paths.py \
  tests/acceptance/W1-02/test_w1_02_holding_folders.py -q -p no:cacheprovider -rs
```

Red first, 2026-10-09, against the guard as built at `f0c352a5`: **235 failed, 148 passed** in about 45 s. The whole
of `tests/acceptance/W1-02`, once: 235 failed, 1455 passed (1690 cases, 4 min 27 s); the 235 are these and no other,
the latency case passed in the whole run, nothing was skipped.

| File | Point | Cases | Red | Green | Why red today |
|---|---|---|---|---|---|
| `test_w1_02_wildcard_globs.py` | DP-6 | 176 | 104 | 72 | the guard allows the glob from `<P>`: every one of the 104 calls comes back `decision=allow`, exit code 0 |
| `test_w1_02_hook_listing_home_paths.py` | DP-7 | 36 | 30 | 6 | the helper prints the deny path, as written and with the home folder in its place |
| `test_w1_02_holding_folders.py` | DP-8 | 171 | 101 | 70 | a move, a hard link and a hard-linking copy of a holding folder are decided as writes only: allowed for a role that may write the folder (57 cases), denied by the allow-list and not by the rule for the others and outside the project (44) |

Every red case fails on the decision itself (`decision=allow`, or a denial whose reason names none of DEC-508,
DEC-525, DEC-548, DEC-553) or on a helper output that still carries the path. None fails on an import, a fixture or
a crash.

**The world of the cases** (`w1_02_folders_support.make_world`) is the third batch's world with three things added:
a ticket of an engineer whose `allowed_paths` name every folder above either stand-in file, `template/` and `docs/`
(a role other than the orchestrator that may write those folders today); a package below `src/` of the sibling
checkout; a work folder below the stand-in home. The folders above the held-out file are computed from the guard's
constant: no path of it is typed, and a case's id names a folder by its level below `<P>` only. The DP-7 cases write
their stand-in settings files into one temporary project; the home folder is the `HOME` of the helper's environment,
an empty temporary folder.

**How "refused by the rule" is told** (`w1_02_folders_support.assert_refused_by_the_rule`): as in the third batch,
with DEC-553 accepted beside DEC-508, DEC-525 and DEC-548 in the reason. "Denied, and not by this rule"
(`assert_denied_but_not_by_the_rule`) is `deny`, exit code 0, and a reason that names none of the four.

#### DP-6 → `test_w1_02_wildcard_globs.py`

**What the guard refuses from the session's own root today** (found by running the hook on the stand-in project).
A glob of wildcards alone is refused when its pattern reaches the depth where one of the two files lies:

| Pattern | Glob tool | Grep tool (`glob`) | Shell word |
|---|---|---|---|
| `**`, `**/*`, `**/**`, `*/**`, `**/*/*` (everything) | refused | refused | refused |
| one star per level down to a file (`*/*` for the settings file; one level more for the held-out file) | refused | refused | refused |
| `*` (one level; neither file lies there) | allowed | **refused** (a glob with no slash is a name at any depth) | allowed |
| more levels than the deeper file has | allowed | allowed | allowed |

Through these tool forms: Glob with `path` = the root, with no `path` when the session stands in the root, and as
one pattern with the root in front; Grep with the glob and `path` = the root, with no `path`, and with a slash in
front of the glob; a shell word after `cat`, `grep`, `ls` and also after `echo` (any word of a command), absolute,
relative to the working folder, and after `cd`.

**From a copy's `<P>` today** every one of them is allowed, at every site, with one exception: a Grep glob over
everything with a slash in front (`/**`, `/**/*`) is refused from `<P>` already.

Refused from `<P>` (sibling checkout, `template/` below the session's root, the stand-in home), red unless said:

- `test_a_glob_over_everything_from_a_copy_s_folder_is_refused` (14 tool forms × 3 sites): `**/*` in Glob (absolute
  `path`, relative `path`, no `path` in a session that stands in `<P>`, absolute pattern, relative pattern), Grep
  (absolute `path`, relative `path`, no `path`), `cat` (absolute, relative, standing in `<P>`, after `cd`), `grep`,
  `ls -d`. The relative spellings go from the session's project to `<P>`.
- `test_a_glob_over_every_file_at_the_copy_s_depth_is_refused` (4 forms × 5 copies): one star per level of the copy.
- `test_the_other_globs_over_everything_are_refused` (6): `**` and `*/**`, from the sibling checkout.
- `test_a_search_whose_glob_is_a_single_star_is_refused` (3 Grep forms × 3 sites).
- `test_a_search_whose_glob_starts_with_a_slash_is_refused` (5 copies);
  `test_a_search_over_everything_with_a_slash_in_front_is_still_refused` (3, **green today**: refused before).
- `test_a_wildcard_only_glob_from_the_home_folder_as_a_shell_spells_it_is_refused` (4 forms × 2 patterns): `~/`,
  `$HOME/`, `ls -d ~/`, a bare `cd` and then the glob.
- `test_a_wildcard_only_glob_from_a_copy_s_folder_is_refused_for_every_role` (3 sites × an engineer, a session with
  no role, the test designer); the orchestrator asks every other case.
- `test_the_refusal_of_a_wildcard_only_glob_names_neither_the_copy_nor_its_folder` (5 copies): no path of the copy,
  no folder of it, not `<P>` (the command carries it), no value of the file.

Stays allowed, green before and after (72):

- `test_a_glob_over_everything_from_a_source_folder_of_the_project_stays_allowed` (the 14 tool forms from `src/`)
  and `test_a_glob_over_everything_from_a_folder_outside_under_which_no_copy_lies_stays_allowed` (7 forms × `src/`
  of the sibling checkout and the work folder below the stand-in home);
  `test_the_other_wildcard_only_globs_from_such_a_folder_stay_allowed` (`*/*` and `**` × 3 forms × the 3 folders).
- `test_a_glob_from_a_copy_s_folder_that_selects_other_files_stays_allowed` (5 forms × 3 sites): `**/*.py`,
  `**/README.md`, a Grep with `glob` = `*.py`, `cat <P>/**/*.py`, `ls <P>/src/*.py`.
- `test_a_single_star_stays_allowed_from_the_root_and_from_a_copy_s_folder` (2 forms × the root and the 3 sites).

**Allowed from the root today and so not refused from `<P>`** (no case makes `<P>` stricter than the root): a
single star in the Glob tool and in a shell word (held, above); a pattern with more levels than the copy has (no
case). No case either way, by the brief: a glob or a search that starts above `<P>`; a search from `<P>` or from the
root with no glob at all.

#### DP-7 → `test_w1_02_hook_listing_home_paths.py`

A deny path spelled from the home folder is the argument of a deny rule that starts with `~/`: `Tool(~/<path>…)`;
its tail may be `/**`, `/` or nothing, a blank may follow the bracket, the path may go below a folder, the tool may
be any. A hook command may hold it as written (`~/<path>`) or with the home folder in its place (`<home>/<path>`,
the home folder being the `HOME` of the helper's environment); both print as `[redacted]`.

- `test_a_deny_path_spelled_from_the_home_folder_is_redacted_as_written` (6 spellings of the rule) and
  `…_is_redacted_with_the_home_folder_in_its_place` (6): the path alone in a hook command, the rest unchanged.
- `test_both_spellings_in_one_command_are_redacted` (3): both in one command, in either order.
- `test_the_path_with_the_rule_s_wildcard_part_or_inside_a_word_is_redacted` (8): each spelling with `/**`, with
  `/`, in quotes, after `=`.
- `test_the_path_as_the_start_of_a_longer_path_is_redacted` (4): only "the deny path is gone" is asserted (residual
  14 covers the tail).
- `test_the_paths_of_several_deny_rules_of_both_kinds_are_all_redacted` (1): an absolute deny path (DEC-548), two
  from the home folder, a command pattern and a relative glob; a whole deny value and bare paths in one command.
- `test_a_home_path_that_starts_like_another_rule_s_path_is_redacted_whole` (1).
- `test_without_a_home_folder_the_helper_does_not_fail_and_redacts_the_path_as_written` (1): with no `HOME` in the
  helper's environment the case holds only exit code 0 and the as-written spelling; **no side is taken on the
  resolved spelling** (the command holds none).
- Green before and after (6): `test_a_project_relative_deny_path_held_bare_is_not_blanked` (3: one leading slash,
  `./`, a bare relative glob, each beside a deny rule from the home folder; the whole value is still redacted),
  `test_the_home_folder_alone_and_another_path_below_it_print_unchanged` (`~`, the home folder, `$HOME`, a path
  below the home that no deny rule carries, in both spellings),
  `test_a_hook_command_that_holds_no_deny_path_prints_unchanged`,
  `test_a_whole_deny_value_spelled_from_the_home_folder_is_still_redacted_as_one` (as built).

A failure message never prints the path it looks for (positions only). The 35 earlier cases of the helper are
untouched and green.

#### DP-8 → `test_w1_02_holding_folders.py`

A folder that holds a file or a copy is a folder strictly between `<P>` and the file. The settings file has one;
the held-out file lies below more than one, and each is asked.

- `test_a_second_name_for_a_folder_that_holds_a_protected_file_is_refused_as_a_read` (15 forms × 3 folders, by the
  orchestrator): move (relative, absolute, with a trailing slash, `-t`), rename beside itself, hard link (relative,
  absolute), symbolic link (`-s` absolute and relative, `--symbolic`), linking copy (`-rl`, `-al`, `-r --link`,
  `-rs`, `-R --symbolic-link`). 30 red, 15 green.
- `test_a_second_name_for_a_holding_folder_is_refused_whether_or_not_the_role_may_write_it` (4 forms × 3 folders ×
  the engineer whose ticket names the folders and the one whose ticket does not): 18 red, 6 green.
- A copy in a sibling checkout: `test_a_second_name_for_a_folder_that_holds_a_copy_in_another_checkout_is_refused_as_a_read`
  (6 forms × 3 folders, by the orchestrator; the relative spelling goes from the session's project into the other
  checkout: 12 red, 6 green) and `…_in_another_checkout_is_refused_for_a_role_that_writes_less` (4, red).
- A copy below the session's root: `…_below_the_project_s_root_is_refused_as_a_read` (4 forms × 3 folders, 12 red),
  `…_below_the_root_is_refused_whether_or_not_the_role_may_write_it` (8, red),
  `test_a_symbolic_second_name_for_a_folder_that_holds_a_copy_below_the_root_is_refused_as_a_read` (4, green).
- The user-level settings file's folder: `test_a_second_name_for_the_folder_that_holds_the_user_level_settings_file_is_refused_as_a_read`
  (7 forms with `~`, `$HOME`, `"${HOME}"`: 6 red, 1 green) and
  `test_a_second_name_for_that_folder_by_its_absolute_path_is_refused_for_every_role` (3 forms × 2 roles, red).
- `test_the_refusal_for_a_holding_folder_names_the_rule_and_no_path` (5, red): not the file, not the folder moved
  (the command carries it), not `<P>`, no value of the file.

Stays as it is, green before and after (38):

- `test_a_second_name_for_a_folder_that_holds_neither_file_stays_allowed_for_a_role_that_may_write_it` (9 forms on
  `docs/spec` × the orchestrator and the engineer whose ticket names `docs/`): move, hard link, linking copy,
  symbolic link, symbolic-linking copy, and a plain `cp -r`.
- `test_a_second_name_for_such_a_folder_by_a_role_that_may_not_write_it_is_decided_by_the_allow_list` (9): the six
  forms that write the folder are denied, and **not** by this rule; the three that only write scratch are allowed.
- `test_a_folder_that_holds_neither_file_as_the_destination_of_a_move_is_decided_as_today` (3 forms × 2 roles).
- `test_a_second_name_for_a_folder_outside_the_project_that_holds_no_copy_is_decided_as_today` (5): a symbolic link
  to and a plain copy of `src/` of the sibling checkout and of the work folder below the home are allowed; a move
  of either is the allow-list's denial.

No case either way, by the brief: a move or a link of `<P>` itself or of a folder above it (afterwards the file
lies at the same project-relative path under the new name, which the rule as built covers as a copy); an in-place
edit whose backup suffix is a word of its own without a dot; a move or copy with an option the guard's reading of
operands cannot read.

#### What the guard already refused before this batch

Found by running the hook and the helper as processes on stand-ins (no file of this repository opened):

- DP-6: from the session's root, the table above. From a copy's `<P>`: only a Grep glob over everything with a
  slash in front. A glob from `<P>` that names the file, its extension or its folder was refused already (third
  batch).
- DP-7: a whole deny value inside a hook command, whatever its spelling, and a bare absolute (two-slash) deny path.
  Nothing of a deny path spelled from the home folder, in either spelling.
- DP-8: as reads, for every role and at every site: a symbolic link to a holding folder (`ln -s`, `--symbolic`,
  `-sfn`), a recursive copy that makes symbolic links (`cp -rs`, `--symbolic-link`), and a plain recursive copy of
  it (`cp -r`: the folder is a read source). As writes only: `mv` in every form, `ln` (hard), `cp -rl`, `cp -al`,
  `cp -r --link`: allowed for the orchestrator and for an engineer whose ticket names the folder (in the project
  and below `template/`), denied by the allow-list for an engineer whose ticket does not and for a session with no
  role, and denied by the allow-list for every role in another checkout and below the home folder.

#### Changes to the residual list

Amended above: **13** (the spelling from the home folder is held; the project-relative one stays, and a case holds
that it prints) and **15** (the wildcard-only glob from `<P>` is held; the start above `<P>` stays, with DP-1).
Residuals 1 to 12, 14 and 16 to 21 stand. Added:

22. DP-6: a wildcard-only glob from `<P>` in a word of a command that is no reader (`echo <P>/**/*`): refused from
    the root today, so it follows; no case. Other spellings of "everything" (`**/**`, `**/*/*`, a pattern made by
    braces) are not held one by one.
23. DP-6: a `<P>` the guard cannot resolve from the command line (a `cd` into a folder that exists only at run time,
    as residual 11), and a copy that comes to lie under the start only later in the same command (residual 16).
24. DP-7: the home folder spelled in a hook command in another way than `~/` or its absolute path (`$HOME/…`,
    `${HOME}/…`, `~user/…`, a path through a symbolic link to the home folder). Not held either way.
25. DP-7: the resolved spelling when the helper's `HOME` is missing or is not the home folder the hooks run with
    (the helper started with another `HOME`). Without `HOME` only the as-written spelling is held.
26. DP-7: a deny rule whose path is the home folder itself (`~`, `~/**`): not held either way (the home folder
    alone is held as printing unchanged only when no rule carries it).
27. DP-8: a holding folder given a second name by a program the guard does not know as one (`git mv`, `rsync`,
    `tar`, `install`, `rename`, `cp --reflink`, a bind mount), or by a script (residual 19, on a folder).
28. DP-8: a holding folder reached by a glob in the command's word (`mv <P>/.c* …`) or through a symbolic link to
    it made earlier (residual 7). No case.
29. DP-8: a move or a link of `<P>` itself or of a folder above it: after it the copy lies at the same
    project-relative path under the new name and is covered as a copy; the command itself is not held either way.
30. DP-8, left by DEC-553: an in-place edit whose backup suffix is a word of its own without a dot; a move or copy
    with an option the guard's reading of operands cannot read.

#### Rewrites and cases outside this suite

No case of this suite was rewritten: none holds as allowed what DP-6, DP-7 or DP-8 now refuses or redacts (read:
the files of the three earlier batches and the 529 cases before them; the third batch took no side on a deny path
spelled from the home folder, on a wildcard-only glob from `<P>` or on a holding folder). No acceptance suite of
another ticket holds such a form either (searched: `tests/acceptance`).

Two cases of the engineer's unit suite hold such a form as allowed and go red with the change. They are not
acceptance cases and not this designer's to touch; they are returned by name (package DP-9):

- `tests/unit/guard/test_protected.py::test_what_is_beside_or_above_a_copy_is_let_through`: a Glob for `**/*` with
  `path` = a copy's `<P>` is held as let through (DP-6 refuses it).
- `tests/unit/guard/test_protected.py::test_the_listing_redacts_an_absolute_path_a_deny_rule_carries`: with the
  rule `Read(~/w/**)`, `~/w` in a hook command is held as printing unchanged (DP-7 redacts it).

### Rewrites

None. No earlier case was changed; `conftest.py` gained one fixture (`guarded`). The third batch (DEC-548) rewrote
none either: it added five test files and `w1_02_copies_support.py`, and changed no line of an earlier file but this
README. The fourth batch (DEC-553) rewrote none: it added three test files and `w1_02_folders_support.py`, and
changed no line of an earlier file but this README (residuals 13 and 15 amended, this section and the packages).

### Decision packages

**DP-1. An unrestricted recursive search from the project root.**
- Question: is a search from the project root with no glob that keeps both files out (Grep with `path` = the root
  or no `path`; `grep -r … .`, `find .`, `ls -R`; Glob `**/*`) refused?
- Why now: the order lists "a recursive search from the project root" among the forms to refuse, and it also says
  every decision W1-02's and W1-50's suites hold today stands. Four suites hold exactly that Grep as allowed:
  W1-02 `test_role_less_session_can_still_read_with_file_tools`, W1-50 `test_ticket_lead_may_read[Grep]`, W1-47
  `test_a_call_that_names_another_path_stays_allowed[…Grep]` (6 cases) and W1-05
  `test_a_read_only_tool_goes_through_the_hook_and_is_allowed` (Grep, 6 cases). Three of them are not this ticket's.
- Options: (a) refuse it; the four suites' cases are rewritten by their designers to search `src/` or to pass a
  glob, with `Rewrite-Reason` trailers. (b) keep it allowed and record it as a residual: either file's content can
  then come back from one root search. (c) refuse it, in a follow-up after this ticket, once the four rewrites are
  in.
- Impact: (a) and (c) change everyday work in every project that has the kernel: a search from the root needs a
  path or a glob, for every role. (b) leaves the held-out file readable by a listed tool, which is the incident
  class of DEC-508.
- Reversibility: high; a rule and about 14 cases.
- Cost: (a) one more rule in the guard, about 10 cases here, 14 cases rewritten in four suites; (b) none; (c) as
  (a), later.
- Recommendation: (a). Confidence: medium (the order's wording is clear; the cost in daily use is real).
- Held under both readings: a search over the folder that holds the file, a glob that takes the file in from any
  start, and a root search under a glob that matches neither file.

**DP-2. A deny line's bare path inside a hook command.**
- Question: the helper redacts a deny value (`Read(//…/**)`) that appears inside a hook command. Does it also
  redact the path that value carries when a hook command holds the path without the rule around it?
- Why now: the interface is fixed by these cases; the deny lines are where the held-out paths are written.
- Options: (a) the whole deny value only (held by the cases); (b) also the argument of each deny rule, with and
  without its trailing `/**`.
- Impact: (a) a hook command that names a held-out path would print it; the guard's own rule (DEC-215) would still
  refuse any call that then uses it. (b) a short common argument (`sudo:*`, `**/*.key`) could blank ordinary text
  of a command.
- Reversibility: high. Cost: (b) a few lines and two cases.
- Recommendation: (b) for arguments that are absolute paths only. Confidence: medium.
- Decided by DEC-548 as recommended; held by `test_w1_02_hook_listing_paths.py`.

**DP-6 (third batch). A copy reached by a glob or a search that starts above its site.**
- Question: DP-4 covers "any target whose path ends in either file's project-relative path". Is a glob or a search
  whose start is a folder above a copy's site `<P>` and outside the session's project (the folder that holds several
  checkouts, the home folder, `/`), with a pattern that could take a copy in (`**/<the file's name>`, `**/*<ext>`,
  a recursive `grep` or `find` with the name), refused?
- Why now: the cases for DP-4 are written before the code and fix what the engineer builds. The brief rules out any
  case that needs the guard to walk a tree, and the guard cannot know where copies lie without one.
- Options: (a) residual: the guard refuses a copy that is named, its folder, and a glob with a literal start at or
  below `<P>` (held by the cases); a wide search from above is left to the harness's own deny lines. (b) refuse by
  pattern alone: any glob or recursive search outside the project whose pattern can end in either file's name or
  project-relative path, wherever it starts. (c) walk the tree below the start, with a bound.
- Impact: (a) one search from the home folder can return the user-level settings file or a sibling checkout's
  held-out file: the incident class of DEC-508, one folder up. (b) refuses ordinary searches outside the project
  (`**/*.json` in another checkout), for every role. (c) costs time in a hook with a 100 ms budget, and a refusal
  then tells that a copy exists below the start.
- Reversibility: high (a rule and a few cases). Cost: (a) none; (b) one rule, about 10 cases; (c) a rule, a bound,
  a latency risk.
- Recommendation: (b) for a pattern that names the file's own name or its project-relative path; (a) for a pattern
  by extension only. Confidence: medium-low: it meets DP-1, which is with the owner, and should be answered with it.
- No case either way in this batch (residual 15).

**DP-7 (third batch). Other spellings of a deny rule's path in the helper.**
- Question: DEC-548 has the helper redact "an absolute path that a deny rule carries". A deny rule may also carry a
  path from the home folder (`Tool(~/…)`) or a project-relative one (one slash). Does the helper redact those when a
  hook command holds them bare, and in which spelling (as written, or resolved to the absolute path)?
- Why now: the cases fix the interface; the decision's word is "absolute", and the cases hold only the two-slash
  spelling as absolute.
- Options: (a) absolute (two slashes) only, as held. (b) also `~/…`, matched both as written and with the home
  folder in its place. (c) also project-relative, matched as written and resolved against the project.
- Impact: (a) a held-out path below the home folder, written with `~/` in a deny rule, prints if a hook command
  names it. (b) and (c) redact more; (c) can blank ordinary relative paths of a command (`src/**`).
- Reversibility: high. Cost: (b) a few lines and about four cases; (c) the same and a risk of blanking.
- Recommendation: (b), not (c). Confidence: medium.
- No case either way in this batch (residual 13).
- Decided by DEC-553 as recommended; held by `test_w1_02_hook_listing_home_paths.py`.

**DP-6, after DEC-553.** The wildcard-only glob from `<P>` itself is decided (refused as from the root) and held by
`test_w1_02_wildcard_globs.py`. The start above `<P>` is not: it is answered with DP-1 and stays residual 15.

**DP-9 (fourth batch). Two unit cases of the guard hold as allowed what DEC-553 refuses or redacts.**
- Question: `tests/unit/guard/test_protected.py::test_what_is_beside_or_above_a_copy_is_let_through` holds a Glob
  for `**/*` from a copy's `<P>` as let through, and `…::test_the_listing_redacts_an_absolute_path_a_deny_rule_carries`
  holds `~/w` as printing unchanged under the rule `Read(~/w/**)`. Who changes them, and how?
- Why now: both go red the moment DP-6 and DP-7 are built; they are on the ticket's own paths (`tests/unit/guard/**`).
- Options: (a) the engineer changes those two lines with the code (each moves from the "let through" list to the
  refused or redacted one), as the engineer's own unit cases; (b) the lines are removed; (c) the cases are kept and
  the change is narrowed to pass them.
- Impact: (a) none beyond the two lines; (b) loses the neighbours the same cases hold; (c) would undo DEC-553.
- Reversibility: high. Cost: two lines.
- Recommendation: (a). Confidence: high. Not this designer's to edit (unit cases are the engineer's).

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
