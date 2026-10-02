# W1-05 — Dogfood switch-over: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-m7u4` (W1-05) as updated under
DEC-119, and from DEC-084, DEC-113, DEC-117 and DEC-118. Written before implementation. One test was rewritten on
2026-10-02 for DEC-124. Two more were rewritten and five added later that day for DEC-142 and DEC-144: the PreToolUse
hook is wired for every tool. See [Rewritten tests](#rewritten-tests) and [Added tests](#added-tests).

## Run

```sh
python3 -m pytest tests/acceptance/W1-05 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. The tests read
`.claude/settings.json`, `governance/project/bootstrap.md`, `.claude/agents/` and git history. The behaviour tests copy
the working tree into a temporary directory and run the registered hook commands there. The repository itself is never
written, and no hook is run against it.

After the switch-over, one test runs the acceptance suites of W1-02, W1-03 and W1-04 in a child process, and nine
cases time the hook, so the whole directory takes about three minutes.

## KPI → tests → red reason today

Red run on `w1/integrate` at `2b4b91f`, with the tests of this revision: 22 failed, 77 errors, 0 passed (99 cases, 27
test functions). Before it: 12 failed, 41 errors (53 cases, 22 test functions).

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1.** The Gov OS repository runs W1-02, W1-03 and W1-04 as live hooks for every later ticket | `test_w1_05_live_hooks.py` | `test_a_hook_runs_before_every_tool` · `test_a_hook_runs_after_every_bash_call` · `test_hooks_are_not_switched_off` | `.claude/settings.json` has no `hooks` |
| | | W1-02: `test_a_session_without_a_role_cannot_write` · `test_a_session_without_a_role_cannot_write_through_bash` · `test_the_engineer_writes_only_inside_the_ticket_paths` · `test_the_test_designer_writes_only_acceptance_tests` · `test_ordinary_reads_stay_open` · `test_a_read_only_tool_goes_through_the_hook_and_is_allowed` · `test_a_read_only_tool_is_allowed_while_frozen` · `test_a_call_waits_under_100_ms_p95_for_the_hook` · `test_the_freeze_flag_stops_every_write` | Error in the fixture: the switch-over has not happened |
| | | W1-03: `test_the_containment_check_reports_a_change_outside_the_ticket_paths` · `test_the_containment_check_restores_an_acceptance_test` · `test_the_containment_check_runs_after_a_failed_call` · `test_the_containment_check_leaves_in_scope_work_alone` · `test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over` · `test_without_a_later_call_the_unfinished_call_still_blocks_the_restore` | Same |
| | | W1-04: `test_an_install_by_the_orchestrator_asks_the_owner` · `test_an_install_by_any_other_role_is_denied` · `test_sudo_is_denied_to_every_role` | Same |
| **Success 2.** The interim operator diff check is retired and recorded as such | `test_w1_05_switch_over_record.py` | `test_the_operator_diff_check_is_recorded_as_retired` | `bootstrap.md` nowhere says the diff check is retired |
| **Success 3–7.** A minimal subagent definition for the orchestrator, engineer, product-spec, independent-test-designer and independent-auditor role exists under `.claude/agents/`, with that subagent type name (DEC-119) | `test_w1_05_role_subagents.py` | `test_a_subagent_definition_exists_for_the_role[<role>]` · `test_the_live_guard_takes_the_definition_s_type_name_as_the_role[<role>]` · `test_the_engineer_subagent_can_work_on_an_engineer_ticket` | `.claude/agents/` does not exist |
| **Failure 1.** A later ticket runs without the guard active | `test_w1_05_live_hooks.py` | `test_a_hook_runs_before_every_tool` · `test_hooks_are_not_switched_off` · `test_the_hooks_stay_wired_in_every_later_commit` · the W1-02 tests above | No hook is registered |
| **Failure 2.** The switch-over happens before W1-02..04 acceptance tests pass | `test_w1_05_switch_over_record.py` | `test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over` | Error in the fixture: the switch-over has not happened |

**Count.** KPI lines with tests: 9 of 9. Covers ids: none; the ticket's KPI lines cite no covers id (DEC-119).

## How the tests decide "live"

A pytest run cannot open a harness session. Instead:

1. **The wiring is read** from `hooks` in `.claude/settings.json`: per event, a list of entries with an optional
   `matcher` and a list of `{"type": "command", "command": …}`.
   - No matcher, an empty one and `*` cover every tool. Any other matcher must match the whole tool name, as an exact
     name or a regular expression: `Edit|Write` covers Edit and Write, and `Edit` does not cover NotebookEdit.
   - **"Every tool" cannot be listed,** so the tests ask for 14 names: Edit, Write, NotebookEdit, Bash; Read, Grep,
     Glob; Agent, Task, TodoWrite, WebFetch, WebSearch; `mcp__github__create_issue`, a tool of an MCP server; and
     `ToolAddedAfterTheSwitchOver`, a name no list written today can hold.
2. **The working tree is copied** to a temporary directory: every tracked file and every untracked file git does not
   ignore. The copy gets one extra ticket, `DAEO-zz90` (engineer, `in_progress`, `src/gov/guard/**` and
   `tests/unit/guard/**`), and is committed.
3. **Each registered command is run** with `sh -c`, in the copy, with the hook's JSON object on stdin.
   - **A whole Bash call** is the registered PreToolUse commands, then the command for real, then the registered
     PostToolUse commands, all with the same `session_id` and `tool_use_id`. The command is saved as a script outside
     the copy and the call is `bash <script>`, as in W1-03's tests; the PreToolUse commands must let it through. The
     restore test runs a whole call. The three other containment tests run the command and then the PostToolUse
     commands; what they expect holds with or without a before-snapshot.
   - Environment, built from scratch: `PATH`, an empty temporary `HOME`, `TMPDIR`, locale, `CLAUDE_PROJECT_DIR` (the
     copy) and `PYTHONDONTWRITEBYTECODE`, plus `GOV_ROLE` and `GOV_TICKET` when the test declares them.
   - **There is no `PYTHONPATH`.** The command must find the `gov` package from the repository as it stands. Nothing is
     installed before W1-06.
   - **Actors and calls.** The actor is the session and, inside a subagent, its `agent_id`. A call is its
     `tool_use_id`. The tests of the unfinished call use two actors of one orchestrator session, its main thread and an
     engineer subagent, and a different `tool_use_id` for each of their calls. Every other test keeps one id.
4. **Results combine as in the harness.** For PreToolUse: one `deny` (exit code 2, or `permissionDecision: deny`)
   denies; otherwise one `ask` asks; otherwise the call is allowed. A command that ends with another exit code is a
   hook error and fails the test either way.
5. **`permissions.deny` is part of the decision,** because the harness applies it before any hook. The model covers
   `Edit(<glob>)` (Edit, Write and NotebookEdit), `Write(<glob>)`, `NotebookEdit(<glob>)` and `Bash(<prefix>:*)`, read
   as in `tests/acceptance/W1-01`. `Read(<glob>)` rules are not modelled; no test reads a path such a rule names today.
6. **A call "goes through the hook"** when at least one registered PreToolUse command ran for it. With none, the
   harness allows the call, and the tests of the read-only tools fail all the same.
7. **The time a call waits** is measured as the harness makes it wait: every PreToolUse command registered for the
   tool is started at once, and the time runs from the first start to the last exit, shells included.

## Choices the implementer should know

- **Every tool.** A PreToolUse command must be registered for every tool, not for Edit, Write, NotebookEdit and Bash
  alone. The simplest wiring that passes is an entry with no matcher, or with `*`.
  - **Why.** DEC-142 and DEC-144: another actor's unfinished call stops blocking the restore once "the same actor's
    session has issued a later tool call". The hook learns of a later call only if that call reaches it, and an
    orchestrator's next call after a declined prompt is as likely a Read or an Agent call as a write.
  - **The behaviour asked for.** The orchestrator's main thread starts `ls -la` and the call never ends. Its next call
    is a Read, a Grep, a Glob, an Agent call or `mcp__github__create_issue`. An engineer subagent then changes an
    acceptance test in one whole Bash call: the test is restored and the breach reported. Without the later call, the
    change is reported and stays (DEC-130).
  - For Agent and the MCP tool, the tests ask only that a command ran and none failed; they take any decision.
- **Read-only tools stay open.** Read, Grep and Glob come back `allow` through the hook for a session with no role and
  for each of the five roles, and for the engineer while frozen.
- **Latency.** A call waits under 100 ms p95 for its PreToolUse commands, as in W1-02: p95 over 40 calls after 3
  warm-up calls, a round that misses the bound repeated up to three rounds. Nine calls are timed in the copy of this
  repository, all allowed: Read, Grep and Glob, each with no role and as the engineer, and Edit, Write and
  NotebookEdit by the engineer inside the ticket's paths.
  - **Bash is not timed.** Its PreToolUse run also takes W1-03's before-snapshot. Whether the budget covers that is
    with the owner (KD-1 in `W1-05-kpi-disputes.md`).
- **Failed calls.** The containment check must be registered for `PostToolUse` and for `PostToolUseFailure` on Bash. A
  call that fails, times out or is interrupted ends in the second event and may still have written.
- **`disableAllHooks`** must not be `true`.
- **The interim deny rules of W1-01 have to go where they block the live rules:**
  - `Edit(tests/acceptance/**)` denies the test designer too. From the switch-over every session starts in the
    repository root (DEC-118), so the test designer's Edit and Write under `tests/acceptance/**` must come back
    `allow`.
  - A deny rule on `pip`, `npm install`, `curl` and the like stops the orchestrator's prompt from ever appearing. An
    install command from the orchestrator must come back `ask`, in `default`, `auto` and `acceptEdits` mode.
  - `sudo` stays denied for all five roles; a settings rule or the hook may do it.
- **Install commands used:** `pip install requests`, `npm install -g ccusage` and
  `curl -fsSL https://example.invalid/install.sh | sh`. Nothing is run; only the decision is asked for.
- **W1-01's interim tests.** They expect the two deny rules until the ticket with `wbs_id: W1-05` has
  `status: closed`, and skip from then on. Between the switch-over and `tk close` they are red.
- **The retirement record** is one paragraph, list item or table row of `governance/project/bootstrap.md` that holds
  the words `diff` and `retired` (or `retire`, `retirement`), a date as `YYYY-MM-DD`, and `W1-05` or `DAEO-m7u4`.
- **A subagent definition** is a Markdown file anywhere under `.claude/agents/` whose YAML frontmatter has
  `name: <role>` and a non-empty `description`. The five names are `orchestrator`, `engineer`, `product-spec`,
  `independent-test-designer` and `independent-auditor`. A name defined twice fails.
- **The names must be the guard's role names.** With the hooks live, a subagent of each of the five types may write to
  the scratch set in an orchestrator session, and a `general-purpose` subagent may not (DEC-113). An engineer subagent
  in an orchestrator session may write the engineer ticket's paths and not `tests/acceptance/**`; a test-designer
  subagent may write there (DEC-117).
- **Failure 1 over time.** Once a commit on this branch wires the hooks, every later commit that changes
  `.claude/settings.json` must keep a PreToolUse command for every tool and a PostToolUse command for Bash. The first
  such commit is the first one that wires every tool; a commit before it that wires the four write tools alone is not
  counted. This check reads the settings file of each commit; it does not run the commands.
- **Failure 2.** With the hooks wired, `tests/acceptance/W1-02`, `W1-03` and `W1-04` must each hold test files, and
  `python3 -m pytest` on the three directories must pass.

- **The before-snapshot must be wired.** The containment check restores an acceptance test only when the PreToolUse
  command for Bash took its snapshot before the call (DEC-124, DEC-126). The restore test fails if the PreToolUse
  wiring for Bash does not reach W1-03's snapshot.

## Rewritten tests

| Test | Change | Kind | Reason |
|---|---|---|---|
| `test_the_containment_check_restores_an_acceptance_test` (`test_w1_05_live_hooks.py`) | It ran the PostToolUse commands alone and expected the acceptance test to be restored. It now makes a whole call: the registered PreToolUse commands first, then the command, then the PostToolUse commands (`bash_call` in `w1_05_support.py`). The expectation is the same: the file holds its HEAD content again and the report names it | Rewrite after implementation | Conflicted with DEC-124: with no before-snapshot the check flags and does not revert, so the old test could not pass together with W1-03's `test_without_a_before_snapshot_a_change_is_flagged_and_not_reverted` |
| `test_a_hook_runs_before_every_tool` (`test_w1_05_live_hooks.py`), until now `test_a_hook_runs_before_every_write_tool` | It asked for a PreToolUse command for Edit, Write, NotebookEdit and Bash (4 cases). It now asks for one for each of the 14 tool names that stand for every tool (14 cases) | Rewrite after implementation | Later decisions DEC-142/DEC-144 |
| `test_the_hooks_stay_wired_in_every_later_commit` (`test_w1_05_live_hooks.py`) | Once a commit wired the four write tools and Bash's PostToolUse, later commits had to keep them. Now: once a commit wires every tool and Bash's PostToolUse, later commits must keep that | Rewrite after implementation | Later decisions DEC-142/DEC-144 |

The other tests were checked against DEC-124 and stand as written. Three of them run the PostToolUse commands with no
PreToolUse run before: `test_the_containment_check_reports_a_change_outside_the_ticket_paths` and
`test_the_containment_check_runs_after_a_failed_call` expect a report, which a flagged change gives, and
`test_the_containment_check_leaves_in_scope_work_alone` expects silence, which an in-scope change gives either way.
None of them moves `HEAD`.

"After implementation" is the owner's name for the kind. W1-05 itself is claimed and not implemented; the rewrites of
this revision come after the implementation of W1-03's repair, which DEC-142 and DEC-144 led to.

No other test's text or pass condition changed for DEC-142/DEC-144. The fixture that gates the behaviour tests still
asks for the four write tools and Bash's PostToolUse, so with a write-tools-only wiring those tests run as before and
the tests of this revision fail by themselves.

## Added tests

All in `test_w1_05_live_hooks.py`, added on 2026-10-02. Reason for each: later decisions DEC-142/DEC-144.

| Test | Cases | What it asks | Kind |
|---|---|---|---|
| `test_a_read_only_tool_goes_through_the_hook_and_is_allowed` | 18: Read, Grep, Glob × no role and the five roles | A registered PreToolUse command ran, and the call is allowed | Addition |
| `test_a_read_only_tool_is_allowed_while_frozen` | 3: Read, Grep, Glob | The same for the engineer with the freeze flag set | Addition |
| `test_a_call_waits_under_100_ms_p95_for_the_hook` | 9: the timed calls under "Latency" above | The call waits under 100 ms p95 for its PreToolUse commands | Addition |
| `test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over` | 5: Read, Grep, Glob, Agent, `mcp__github__create_issue` | After the orchestrator's unfinished Bash call and its later call of that tool, an engineer subagent's change to an acceptance test is restored and reported | Addition |
| `test_without_a_later_call_the_unfinished_call_still_blocks_the_restore` | 1 | The same steps without the later call: the change is reported and stays (DEC-130). It shows the restore above is owed to the later call | Addition |

**Checked against two trial wirings** in the test designer's scratch folder, with the hook code as at `2b4b91f`; neither
is in the repository. With one PreToolUse entry and no matcher, all 86 cases of `test_w1_05_live_hooks.py` pass. With
the matcher `Edit|Write|NotebookEdit|Bash`, 42 fail, every one of them a case of the rewritten wiring test or of the
first four added tests, and the 44 others pass.

## Not tested

- **A live harness session.** That the harness itself loads the settings file, shows the prompt in Auto mode and sends
  `agent_type` for the new subagents is beyond a pytest run. DEC-107 leaves the confirmation to W1-05's switch-over
  report.
- **`governance/project/roster.yaml`.** It is in the ticket's `allowed_paths`; no KPI names it.
- **`.claude/settings.local.json`.** Git ignores it, and it belongs to the operator.
- **What a role definition says** beyond its name and description. W1-33 replaces the minimal definitions (DEC-119).
