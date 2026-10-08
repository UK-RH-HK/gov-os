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

### Rewrites

None. No earlier case was changed; `conftest.py` gained one fixture (`guarded`).

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
