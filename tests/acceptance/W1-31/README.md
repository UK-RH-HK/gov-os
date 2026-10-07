# W1-31 acceptance tests — governance share counter

Ticket `DAEO-6mk8`, profile STANDARD (DEC-221): each KPI line's success and failure and the key edge cases.
Written by the Independent Test Designer (MR-3, DEC-069). First written before implementation; brought to
DEC-491 and DEC-495 after the first engineer commit (the rewrites are listed at the end).

Run: `PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH" env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-31 -q -p no:cacheprovider -rs`

63 cases: 27 in `test_w1_31_share_counter.py`, 36 in `test_w1_31_measured_and_estimated.py`.
Support: `w1_31_support.py`, `conftest.py`.

**A result is measured or it is refused (DEC-449, DEC-454).** No case accepts a share, a count, a cost or a
field that is 0, empty, a default or present when its source was absent, unreadable or of a form the specimen
does not show.

## What this ticket delivers, and what the cases test

The ticket builds the counter and what it returns for a ticket. Its `allowed_paths` are `src/gov/telemetry/**`
and `tests/unit/telemetry/**`; `src/gov/close/` is outside it. The cases test that every figure the KPI lines
name is in what the counter returns, in a form a close record can carry. The share reaches the close record
through a W1-30 follow-up after W1-31 is merged; until then the orchestrator runs `gov telemetry` beside each
close (DEC-495). No case needs `src/gov/close/` to change.

## The interface the cases assume

`gov telemetry <ticket> [--json] [--ticket-session <session id>]...`

- A read command (`src/gov/telemetry/command.py`, by the convention in `src/gov/cli/main.py`). It writes
  nothing in the project (`test_the_counter_writes_nothing`).
- **The session logs** are the harness's local logs. The command and ccusage take the folder from
  `CLAUDE_CONFIG_DIR` (the folder that holds `projects/`); without it, the harness's default under `HOME`. The
  cases always set both to temporary folders. **The counter reads the logs of the named sessions itself**
  (DEC-495) for three sources and to check ccusage's figures.
- **ccusage** is found on `PATH` and run with its built-in prices (`--offline`). The sessions' tokens and cost
  are ccusage's.
- **The ticket's sessions** are named by the caller, one `--ticket-session` each (DEC-491). A session that was
  not named is never counted.
- **Counts only, never content.** No text of a log (packet, hook text, hook command, command line, tool
  result, prompt, answer) is in anything the command prints, with or without `--json`, on success, at exit
  code 3 or in a refusal.
- **No verdict.** Nothing printed says whether a budget is met, and no threshold is in it. The 15 % verdict is
  the owner's at the Wave 1 exit (DEC-495).
- **Exit codes.**
  - 0: every part of the share (measured, estimated, their sum) is a number, and `not_measured` is empty.
    It says nothing about the other fields: a learning metric or a P1 field may still say `"not measured"`.
  - 3 (declared in `EXIT_CODES`): the record is returned (`ok: true`) and at least one of the three share
    figures is `"not measured"`.
  - 1 with `ok: false`: a refusal. Pinned: an unknown ticket; ccusage absent; a log of another Claude Code
    version than 2.1.288, with the version named in the error.
  - Where the sessions' tokens could not be measured (no session named, a named session without a log, no log
    folder, a ccusage that fails or answers with something else, **ccusage's figures differing from the log's
    own assistant lines**), the cases accept a refusal, or the record at exit code 3 in which the three
    share figures, `tokens_in`, `tokens_out`, `cache_read_tokens`, `cache_creation_tokens` and `cost` all say
    `"not measured"`. Never exit code 0, never a number.
- **"not measured"** is the exact string `gov close` writes for a field it did not measure.

The record (`result` of the envelope) is plain data that survives the YAML frontmatter of a close record:

| Key | Value |
|---|---|
| `ticket`, `profile` | the ticket id; the profile its ticket file declares, `"not measured"` when it declares none (no STANDARD default) |
| `governance_tokens` | the **measured** sources: a map with exactly `sessionstart_packet`, `hook_output`, `gov_output`, `checkpoint_records`, `close_records` and `total`; each a count or `"not measured"`; `total` is their sum, `"not measured"` when any of them is |
| `estimated_governance_tokens` | the **estimate**, a line of its own: a map with exactly `label` (the string `"estimated"`), `method` (a text that says how it was formed), `files` (the project files it stands on, relative paths; `CLAUDE.md` is among them), `instruction_files`, `mcp_definitions` and `total` (their sum); each of the three a count or `"not measured"` |
| `governance_share` | a map with exactly `measured`, `estimated`, `total`: `governance_tokens.total`, `estimated_governance_tokens.total` and their sum, each over `tokens_in + cache_creation_tokens + tokens_out`, as a fraction of 1; each a number or `"not measured"` (`total` is `"not measured"` when either part is) |
| `not_measured` | a list, one entry per source of the seven that was not measured: `{"name": <source>, "reason": <text>}`; the reason is not empty and holds no log text; empty at exit code 0 |
| `tokens_in`, `tokens_out`, `cache_read_tokens`, `cache_creation_tokens`, `cost` | ccusage's figures summed over the ticket's sessions. Cache creation is in the denominator and shown apart; cache reads are in no share figure |
| `sessions` | one entry per session: `session`, `model`, `tokens_in`, `tokens_out`, `cache_read_tokens`, `cost` |
| `model` | a map with exactly `session_logs` (the models of the named sessions' assistant lines) and `commits` (one entry per commit of the ticket, `commit` and `model`: its `Co-Authored-By` line as read, `"not measured"` without one; the whole list is `"not measured"` when the commits cannot be read) |
| `role`, `skill_versions`, `tool_versions`, `packet_id`, `retrieval_queries`, `retrieval_hits`, `files_written`, `tests`, `retries`, `handoffs`, `decisions`, `owner_interventions` | the other P1 fields: a measured value or `"not measured"`, never null or empty text |
| `agent`, `provider`, `latency`, `files_read` | `provider` and `files_read` are `"not measured"` (the specimen shows no source); `agent` and `latency`: a value or `"not measured"` (AD-3) |
| `learning_metrics` | a map with exactly `kpi_disputes`, `acceptance_tests_rewritten`, `governance_share` (the same map as the record's) |
| `sandbox_system_prompt_tokens` | a line of its own, in no share figure; `"not measured"` until a measurement is recorded (AD-4); never the constant 3,250 |

**Learning metrics.**

- `acceptance_tests_rewritten`: a list, one entry per commit with `Task: <ticket>` and
  `Role: independent-test-designer` that comes after the ticket's first engineer commit (`Role: engineer`,
  same `Task:`) in the history of the project the counter runs in: `{"commit": <id, 7 characters or more>,
  "reason": <the value of its Rewrite-Reason: trailer>}`. A rewrite without the trailer has the reason
  `"reason not recorded"`. The commits were read and hold none: `[]`. The commits cannot be read:
  `"not measured"` (the record is still given).
- `kpi_disputes`: a list, one entry per line of the ticket's disputes record, in its order, each with
  `decision` (the id of the decision that settled it). The record is there and empty: `[]`. No record, a
  record that cannot be read, a line that names no decision: `"not measured"`. **Place and form are
  proposed, awaiting confirmation (PR-1).**

**Records.** `checkpoint_records`: the ticket's checkpoints, deliberate (`docs/checkpoints/<ticket>/`) and
automatic (`.gov-runtime/scratch/checkpoints/<ticket>/`). At least one of the two folders is there: the count
of what they hold, 0 when they hold no record. Neither is there: `"not measured"`. A record that is there and
cannot be read: `"not measured"`. `close_records`: `docs/close/<ticket>/CL-<ticket>.md`; before it exists
`"not measured"` (it is counted by a measure after the close), also when the folder holds something else.

**Token counter.** Session tokens are ccusage's. Governance text is counted with the counter of W1-24
(`gov.context`: 4 characters a token, rounded up). Every text the fixtures count is a whole number of
4-character tokens long, so rounding per text or over all of them gives the same count.

**Which P1 fields `gov close` measures itself**, and which the counter's record is therefore not widened for:
the commits' roles and models (`commits`), `skill_versions`, `tests_run` and `tests_produced`,
`decisions_applied`, `requirements_implemented`, `packet_hash` and `inputs`, the files written (`outputs`).
In the counter's record the P1 fields of those names may say `"not measured"`; no case asks for more.

## The session logs the cases write

`<CLAUDE_CONFIG_DIR>/projects/<working directory with "-" for "/">/<session id>.jsonl`, compact JSON, one
object a line. **The form is the specimen's and nothing else**: a reduced copy of the log of one short headless
session of Claude Code 2.1.288 in a throwaway project (one SessionStart hook, one PostToolUse hook, one `gov`
command through the Bash tool). The suite does not read the specimen when it runs: `support.Log` writes the
lines with the cases' own texts. No real session log was read.

- **A hook's run** is an `attachment` line whose `attachment` has `type: hook_success`, `hookName`
  (`SessionStart:startup`, `PostToolUse:Bash`), `toolUseID`, `hookEvent`, `content: ""`, `stdout` (the hook's
  own JSON, which repeats the text), `stderr`, `exitCode: 0`, `command`, `durationMs`.
- **What it added to the context** is the next `attachment` line: `type: hook_additional_context`, `content`
  (a list of texts), `hookName`, `toolUseID`, `hookEvent`; the line also has `rendered` and `renderedRole`.
  The SessionStart packet is the `content` of the lines with `hookEvent: SessionStart`; hook output is the
  `content` of the lines of the other event the specimen shows, `PostToolUse`.
- **A message of the model takes two `assistant` lines**, one per content block (`thinking`, then `tool_use`
  or `text`), with the same `message.id` and `requestId`, and **each carries the whole `usage` of the
  message**. A sum over lines counts every message twice; ccusage counts each message once (17 input and 407
  output for the specimen's two messages, which are its four lines' 9, 9, 8, 8 and 219, 219, 188, 188).
- **A command** is an assistant `tool_use` with `name: Bash` and `input.command`; its output is the
  `tool_result` with the same `tool_use_id` in the next `user` line (`content` a text, `is_error: false`),
  which also carries `toolUseResult.stdout` with the same text.
- **Every full line** carries `sessionId`, `cwd`, `version` (`2.1.288`), `isSidechain: false`, `uuid`,
  `parentUuid`, `timestamp`. Other lines (`queue-operation`, `last-prompt`, `cost-state`) carry their type.
- **The last line is `cost-state`**, with the usage summed per model. In the specimen its sums are not the
  assistant lines': input 964 against 17, output 422 against 407, cost 0.0306274 against ccusage's 0.0296054;
  cache reads (54,674), cache creation (11,043) and thinking tokens (284) agree. The fixtures' `cost-state`
  line differs from their assistant lines in the same way, and the cases expect numbers for such a log:
  the specimen itself is one. No case compares anything with `cost-state` (AD-5).

Established with ccusage 20.0.26 on hand-written logs in a temporary folder: it reads the form above and
counts each message once; it names the folder variable in its own error; a folder without `projects/` is exit
code 1; a folder without logs gives totals of zero and exit code 0; `--id` with an unknown session prints
`null` and exit code 0; **a line written with a space after its colons is passed over silently, and the
session's row is printed without it** (the specimen copy, which is written that way, gives no session at
all). Zero or a row from ccusage is therefore not proof of what was measured.

### How "runs `gov`" is told

From `pyproject.toml` (`[project.scripts] gov = "gov.cli.main:main"`: an installed project calls `gov`) and
from the specimen (this project calls `PYTHONPATH=<src> python3 -m gov.cli.main`; there is no
`gov/__main__.py`). A Bash command runs `gov` when it is one simple command whose first word, after leading
`NAME=value` assignments, is `gov`, or is `python3` followed by `-m gov.cli.main`. Pinned as counted: both
forms. Pinned as not `gov` output: a command that only names `gov` (`echo gov status`, `cat src/gov/...`,
`git commit -m 'gov close ...'`, `python3 -m pytest tests/unit/gov`, `grep -rn gov docs`, `tk show gov-0001`,
`python3 -m gov_tools.report`) and a tool that is not Bash. **A compound command** (`&&`, `|`, `;`) that runs
`gov` beside another command has one result for all of it, which cannot be told apart: `gov_output` is
`"not measured"` (the specimen shows one simple command). Not pinned: AD-2.

## What the counter does not measure, by name

Each is `"not measured"` (or a refusal), never a number, and the reason is named without content:

| What | Case |
|---|---|
| A hook that fails or blocks (`exitCode` not 0; a hook run of another `type`) | `test_a_form_the_specimen_does_not_show_is_not_measured` (`hook_output`, `sessionstart_packet`) |
| Context added under a hook event the specimen does not show (the reason names the event) | same case |
| Added context in another form (`content` not a list of texts) | same case |
| A `gov` command in a sub-agent's lines (`isSidechain: true`) | same case (`gov_output`) |
| A `gov` command without its `tool_result`; a result whose `content` is not a text | same case |
| `gov` inside a compound command | same case |
| A log of another Claude Code version | `test_a_log_of_another_claude_code_version_is_refused_by_its_version` |
| ccusage's figures against the log's assistant lines | `test_ccusage_figures_that_differ_from_the_logs_give_no_figure`, `test_a_line_ccusage_passes_over_gives_no_figure` |
| The instruction files' estimate without a readable `CLAUDE.md` | `test_the_estimate_is_not_measured_without_its_instruction_file` |
| Checkpoints of a ticket without a checkpoint folder; an unreadable record; the close record before the close | `test_an_empty_checkpoint_folder_counts_zero_and_an_absent_one_is_not_measured`, `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3`, `test_the_close_record_is_not_measured_before_the_close` |
| KPI disputes without a readable record; rewrites and commit models without readable commits | `test_kpi_disputes_are_not_measured_without_a_readable_record`, `test_commits_that_cannot_be_read_are_not_measured` |
| The profile of a ticket that declares none | `test_a_ticket_without_a_profile_is_not_measured_for_the_profile` |
| `provider`, `files_read`; the sandbox's added system-prompt tokens | `test_provider_and_files_read_have_no_source_in_the_specimen`, `test_sandbox_tokens_are_a_line_apart_and_never_assumed` |

A session in the specimen's form that holds no hook and no command was read: its three log sources are 0
(`test_a_log_that_was_read_and_holds_none_counts_zero`).

## KPI lines and covers ids

| Line | Cases |
|---|---|
| Success 1: governance tokens per ticket, joined with ccusage fresh input+output [CAP-04.b] | `test_joins_ccusage_input_and_output_of_the_tickets_sessions`, `test_names_each_of_the_seven_sources_of_governance_tokens`, `test_sessionstart_packet_is_what_the_sessionstart_hooks_added`, `test_hook_output_is_what_the_other_hooks_added`, `test_gov_output_is_the_results_of_the_bash_calls_that_run_gov`, `test_a_command_that_only_names_gov_is_not_gov_output`, `test_a_log_that_was_read_and_holds_none_counts_zero`, `test_a_form_the_specimen_does_not_show_is_not_measured` (9), `test_a_log_of_another_claude_code_version_is_refused_by_its_version`, `test_the_counter_prints_counts_only_never_content`, `test_the_estimate_is_a_line_of_its_own_labelled_estimated`, `test_the_estimate_follows_the_instruction_file`, `test_the_estimate_is_not_measured_without_its_instruction_file` (2), `test_counts_the_tickets_checkpoint_records`, `test_automatic_checkpoints_are_checkpoint_records`, `test_an_empty_checkpoint_folder_counts_zero_and_an_absent_one_is_not_measured`, `test_counts_the_tickets_close_record`, `test_the_close_record_is_not_measured_before_the_close`, `test_the_three_share_figures_are_the_numbers_the_case_computes` |
| Success 2: the share and the P1 fields; cache reads reported separately | `test_the_three_share_figures_are_the_numbers_the_case_computes`, `test_record_names_every_p1_field_and_invents_none`, `test_sessions_carry_what_ccusage_measured_for_each`, `test_cost_is_ccusages`, `test_cache_reads_and_cache_creation_are_figures_of_their_own`, `test_the_model_is_reported_from_the_logs_and_from_the_commits`, `test_record_is_plain_data_a_close_record_can_carry`, `test_the_counter_writes_nothing`, `test_the_record_states_no_verdict_and_no_threshold` |
| Success 3: agent, provider, latency, files read [CAP-40.a] | `test_record_names_agent_provider_latency_and_files_read`, `test_provider_and_files_read_have_no_source_in_the_specimen` (with success 2's cases for the rest of CAP-40.a) |
| Success 4: the share per profile [CAP-53.c] | `test_record_names_the_tickets_profile_beside_the_share` (LITE, STANDARD, FULL), `test_a_ticket_without_a_profile_is_not_measured_for_the_profile` |
| Success 5: the three learning metrics; only the share has a threshold [CAP-40.c] | `test_record_carries_the_three_learning_metrics`, `test_rewrites_are_the_designers_commits_after_the_first_engineer_commit`, `test_commits_that_cannot_be_read_are_not_measured`, `test_kpi_disputes_are_read_from_the_orchestrators_record`, `test_kpi_disputes_are_not_measured_without_a_readable_record` (3), `test_the_record_states_no_verdict_and_no_threshold` |
| Success 6: the sandbox's tokens, a separate line [CAP-40.d] | `test_sandbox_tokens_are_a_line_apart_and_never_assumed` |
| Failure 1: a ticket closes without a share figure | `test_the_three_share_figures_are_the_numbers_the_case_computes` (exit code 0 only with three numbers), `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3`, `test_no_session_of_the_ticket_gives_no_figure`, `test_named_session_without_a_log_gives_no_figure`, `test_absent_log_folder_gives_no_figure`, `test_empty_log_folder_gives_no_figure`, `test_absent_ccusage_refuses`, `test_ccusage_that_cannot_be_read_gives_no_figure` (3), `test_ccusage_figures_that_differ_from_the_logs_give_no_figure`, `test_a_line_ccusage_passes_over_gives_no_figure` |
| Failure 2: cache reads are counted in the share | `test_cache_reads_change_neither_share_nor_tokens`, `test_cache_reads_and_cache_creation_are_figures_of_their_own`, `test_the_three_share_figures_are_the_numbers_the_case_computes` (the fixture has 121,000 cache reads; the denominator is input + cache creation + output) |
| The command exists | `test_the_counter_is_a_command_of_gov` |

For failure 1 the counter's part is this: it never ends with exit code 0 without three share figures that are
numbers. That `gov close` refuses on it is the W1-30 follow-up (DEC-495).

## Expected red against the counter as built (commit `c2e5aa8f`)

**33 failed, 30 passed.** Every failure is an assertion of the case about the record; none is a crash of a
case or of a fixture. The built counter says `"not measured"` for five of the seven sources, has one flat
`governance_tokens` map of seven sources and a single `governance_share`, lists `not_measured` as names
without reasons, and reads neither logs nor commits.

| Red | Why |
|---|---|
| `test_names_each_of_the_seven_sources_of_governance_tokens`, `test_sandbox_tokens_are_a_line_apart_and_never_assumed` | `governance_tokens` still holds the two estimated sources; there is no estimate's line |
| `test_sessionstart_packet_...`, `test_hook_output_...`, `test_gov_output_...`, `test_a_command_that_only_names_gov_...`, `test_a_log_that_was_read_and_holds_none_counts_zero` | the three log sources are `"not measured"`: the logs are not read |
| `test_a_form_the_specimen_does_not_show_is_not_measured` (9) | the source is not a count for logs in the specimen's form (the case's first assertion) |
| `test_a_log_of_another_claude_code_version_is_refused_by_its_version` | no refusal: the version is not read |
| `test_the_counter_prints_counts_only_never_content`, `test_the_record_states_no_verdict_and_no_threshold` | the full fixture does not end with exit code 0 (the built counter prints no content and no verdict) |
| `test_the_estimate_is_a_line_...`, `test_the_estimate_follows_...`, `test_the_estimate_is_not_measured_without_its_instruction_file` (2) | no `estimated_governance_tokens` |
| `test_the_three_share_figures_...`, `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3` | no measured counts; `governance_share` is one value, not three named figures |
| `test_ccusage_figures_that_differ_from_the_logs_give_no_figure`, `test_a_line_ccusage_passes_over_gives_no_figure` | ccusage's figures are taken as they come: `tokens_in` is a number |
| `test_rewrites_are_the_designers_commits_...`, `test_kpi_disputes_are_read_from_the_orchestrators_record` | both metrics are always `"not measured"` |
| `test_commits_that_cannot_be_read_are_not_measured`, `test_the_model_is_reported_from_the_logs_and_from_the_commits` | `model` is `"not measured"`, not the two places |
| `test_an_empty_checkpoint_folder_counts_zero_...`, `test_the_close_record_is_not_measured_before_the_close` | `not_measured` gives no reason; an empty folder is not 0 |

**Green (30):** the 25 cases of the first suite that still hold (the command, the join with ccusage, the
checkpoint and close record counts, the P1 fields, sessions, cost, cache figures, plain data, writes nothing,
cache reads, the four log fields, the three profiles, the learning metrics' names, the six no-figure cases
with ccusage) and five new ones the built counter already satisfies:
`test_kpi_disputes_are_not_measured_without_a_readable_record` (3),
`test_a_ticket_without_a_profile_is_not_measured_for_the_profile`,
`test_provider_and_files_read_have_no_source_in_the_specimen`. A case that needs ccusage is skipped, with its
reason, on a machine without it.

## Proposed, awaiting confirmation

- **PR-1 The KPI disputes record.** `docs/close/<ticket>/kpi-disputes.txt`, written by hand by the
  orchestrator at the merge. One line per dispute: `DEC-<number>: <what was disputed>`. An empty file says
  "no dispute". Not Markdown, so the record store (which reads the `.md` files of `HEAD` and takes a record
  from frontmatter with an `id`) never loads it; `gov close` writes and reads only `CL-<ticket>.md` in that
  folder and creates the folder with `exist_ok`; the counter's close-record count reads only that one file.
  Nothing of this ticket's code writes it. Pinned by `test_kpi_disputes_are_read_from_the_orchestrators_record`
  and `test_kpi_disputes_are_not_measured_without_a_readable_record`.

## Awaiting decision (no case guesses these)

- **AD-1 The estimate's formula.** Which files beyond `CLAUDE.md` it stands on (`AGENTS.md`, the role file
  of the session's role, skills), whether it counts once per ticket or once per session, and what the MCP
  part is: the Gov OS brings no MCP definition today (no MCP source under `.rulesync/` or the template, and
  rulesync is run without that feature). The cases hold the properties only: a line apart, labelled, names
  its method and files, at least the tokens of `CLAUDE.md`, follows the file, `"not measured"` without it.
  The full fixture holds a project MCP file that defines no server, for which the MCP part must be a count;
  which count, and what it is without such a file, is open.
- **AD-2 `gov` commands the specimen does not show.** A compound command in which every part runs `gov`; a
  `gov` command whose result has `is_error: true` (every refusal of `gov`); `gov` by a path
  (`.venv/bin/gov`), through `uv run`, with a redirection.
- **AD-3 `agent` and `latency`.** The specimen shows `entrypoint`, `userType` and `version` but nothing
  called an agent; for latency it shows `totalAPIDuration`, `totalAPIDurationWithoutRetries` and
  `totalDuration` on `cost-state`, `thinkingDurationMs` and timestamps. Which is meant is not settled.
- **AD-4 The sandbox measurement's record** (place and form). Only the `"not measured"` state has a case.
- **AD-5 `cost-state` against the assistant lines.** The specimen's two disagree on input, output and cost.
- **AD-6 A hook run of an event the specimen does not show that adds no context** (the template registers
  PreToolUse, Stop, PreCompact and SubagentStop hooks, so every real session has such lines).

The packages are in the designer's return message in full.

## Rewrites after implementation began (commit trailer `Rewrite-Reason:`)

| Case | What changed | Decision |
|---|---|---|
| `test_names_each_of_the_seven_sources_of_governance_tokens` | five measured sources in `governance_tokens`, two on the estimate's line | DEC-495 |
| `test_share_is_the_governance_total_over_input_plus_output` | removed; replaced by `test_the_three_share_figures_are_the_numbers_the_case_computes` (three figures, cache creation in the denominator, numbers asserted) | DEC-495 |
| `test_unreadable_checkpoint_record_gives_no_share` | removed; replaced by `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3` (three figures; `not_measured` with reasons) | DEC-495 |
| `test_sandbox_tokens_are_a_line_apart_and_never_assumed` | outside the estimate and the three share figures too; the constant 3,250 nowhere in the output | DEC-491, DEC-495 |
| `test_no_session_of_the_ticket_gives_no_figure`, `test_named_session_without_a_log_gives_no_figure`, `test_absent_log_folder_gives_no_figure`, `test_empty_log_folder_gives_no_figure`, `test_ccusage_that_cannot_be_read_gives_no_figure` | unchanged text; the shared `assert_no_figure` now asks for the three share figures and cache creation to say `"not measured"` | DEC-495 |
| every case that writes logs | unchanged text; the logs are now written in the specimen's form (two lines a message, a `cost-state` line) | DEC-495 |
| every case | unchanged text; the fixture project now has the designer's commit before the engineer's | DEC-491 |
