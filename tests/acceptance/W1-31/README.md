# W1-31 acceptance tests — governance share counter

Ticket `DAEO-6mk8`, profile STANDARD (DEC-221): each KPI line's success and failure and the key edge cases.
Written by the Independent Test Designer (MR-3, DEC-069). First written before implementation; brought to
DEC-491 and DEC-495, and then to DEC-501, after the first engineer commit (the rewrites are listed at the end).

Run: `PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH" env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-31 -q -p no:cacheprovider -rs`

82 cases: 27 in `test_w1_31_share_counter.py`, 36 in `test_w1_31_measured_and_estimated.py`, 19 in
`test_w1_31_second_specimen.py`. Support: `w1_31_support.py`, `conftest.py`.

**A result is measured or it is refused (DEC-449, DEC-454).** No case accepts a share, a count, a cost or a
field that is 0, empty, a default or present when its source was absent, unreadable or of a form neither
specimen shows.

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
  (DEC-495) for three sources and to check ccusage's figures: the session's own file and **the files of its
  sub-agents** (DEC-501), which are under the session's folder beside it.
- **ccusage** is found on `PATH` and run with its built-in prices (`--offline`). The sessions' tokens and cost
  are ccusage's; its row of a session holds the messages of the session's sub-agents.
- **The ticket's sessions** are named by the caller, one `--ticket-session` each (DEC-491). A session that was
  not named is never counted, and neither is a sub-agent's file of such a session.
- **Counts only, never content.** No text of a log (packet, hook text, hook command, command line, tool
  result, prompt, answer, summary, a sub-agent's line) is in anything the command prints, with or without
  `--json`, on success, at exit code 3 or in a refusal.
- **No verdict.** Nothing printed says whether a budget is met, and no threshold is in it. The 15 % verdict is
  the owner's at the Wave 1 exit (DEC-495).
- **Exit codes.**
  - 0: every part of the share (measured, estimated, their sum) is a number, and `not_measured` is empty.
    It says nothing about the other fields: a learning metric, a P1 field or the latency may still say
    `"not measured"`. **`counting_notes` and `known_gaps` (below) are not entries of `not_measured` and do
    not keep the exit code from 0** (`test_the_precompact_gap_is_named_and_is_no_entry_of_not_measured`,
    `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes`).
  - 3 (declared in `EXIT_CODES`): the record is returned (`ok: true`) and at least one of the three share
    figures is `"not measured"`.
  - 1 with `ok: false`: a refusal. Pinned: an unknown ticket; ccusage absent; a log of another Claude Code
    version than 2.1.288, with the version named in the error.
  - Where the sessions' tokens could not be measured (no session named, a named session without a log, no log
    folder, a ccusage that fails or answers with something else, **ccusage's figures differing from the own
    assistant lines of the session's file and of its sub-agents' files**), the cases accept a refusal, or the
    record at exit code 3 in which the three share figures, `tokens_in`, `tokens_out`, `cache_read_tokens`,
    `cache_creation_tokens` and `cost` all say `"not measured"`. Never exit code 0, never a number.
- **"not measured"** is the exact string `gov close` writes for a field it did not measure.

The record (`result` of the envelope) is plain data that survives the YAML frontmatter of a close record.
**New or changed with DEC-501:** `counting_notes`, `known_gaps`, `latency`, `agent`, and
`harness_api_duration_ms` in each entry of `sessions`.

| Key | Value |
|---|---|
| `ticket`, `profile` | the ticket id; the profile its ticket file declares, `"not measured"` when it declares none (no STANDARD default) |
| `governance_tokens` | the **measured** sources: a map with exactly `sessionstart_packet`, `hook_output`, `gov_output`, `checkpoint_records`, `close_records` and `total`; each a count or `"not measured"`; `total` is their sum, `"not measured"` when any of them is |
| `estimated_governance_tokens` | the **estimate**, a line of its own: a map with exactly `label` (the string `"estimated"`), `method` (a text that says how it was formed), `files` (the project files it stands on, relative paths; `CLAUDE.md` is among them), `instruction_files`, `mcp_definitions` and `total` (their sum); each of the three a count or `"not measured"` |
| `governance_share` | a map with exactly `measured`, `estimated`, `total`: `governance_tokens.total`, `estimated_governance_tokens.total` and their sum, each over `tokens_in + cache_creation_tokens + tokens_out`, as a fraction of 1; each a number or `"not measured"` (`total` is `"not measured"` when either part is) |
| `not_measured` | a list, one entry per source of the seven that was not measured: `{"name": <source>, "reason": <text>}`; the reason is not empty and holds no log text; empty at exit code 0 |
| `counting_notes` | **DEC-501.** A map with exactly two counts (0 when there was none): `larger_reading_hook_texts`, how many hook texts were counted by the larger reading (each result of a call a hook blocked, each line of a hook that failed without blocking); `gov_results_counted_whole`, how many results of commands in which `gov` ran beside other commands, through a pipe or with a redirection were counted whole. Counts, never content. Not part of `not_measured` |
| `known_gaps` | **DEC-501.** A list of `{"name", "reason"}` (exactly these two keys; the reason a text that is not empty): what the counter cannot count. Always holds the entry named `precompact_hook_output`, whether or not a session was compacted. It may hold more. Not part of `not_measured`, and the name is not in it |
| `tokens_in`, `tokens_out`, `cache_read_tokens`, `cache_creation_tokens`, `cost` | ccusage's figures summed over the ticket's sessions, the messages of their sub-agents among them. Cache creation is in the denominator and shown apart; cache reads are in no share figure |
| `sessions` | one entry per session: `session`, `model`, `tokens_in`, `tokens_out`, `cache_read_tokens`, `cost`, and **`harness_api_duration_ms`**: `totalAPIDuration` of the **last** totals line of that session's log, `"not measured"` for a log without a totals line |
| `model` | a map with exactly `session_logs` (the models of the named sessions' assistant lines, their sub-agents' among them) and `commits` (one entry per commit of the ticket, `commit` and `model`: its `Co-Authored-By` line as read, `"not measured"` without one; the whole list is `"not measured"` when the commits cannot be read) |
| `role`, `skill_versions`, `tool_versions`, `packet_id`, `retrieval_queries`, `retrieval_hits`, `files_written`, `tests`, `retries`, `handoffs`, `decisions`, `owner_interventions` | the other P1 fields: a measured value or `"not measured"`, never null or empty text |
| `latency` | **DEC-501.** A map with exactly `harness_api_duration_ms`: the sum of the sessions' `harness_api_duration_ms`, in milliseconds; `"not measured"` when any named session has none (never 0, never the others' sum). The key names what it is: the harness's summed API duration, not a wall-clock time |
| `agent` | **DEC-501.** A map with exactly `harness` (the string `"Claude Code"`) and `version` (the `version` of the log's lines: `"2.1.288"`, the one version the counter accepts, so one value for any number of sessions) |
| `provider`, `files_read` | `"not measured"`: neither specimen shows a source |
| `learning_metrics` | a map with exactly `kpi_disputes`, `acceptance_tests_rewritten`, `governance_share` (the same map as the record's) |
| `sandbox_system_prompt_tokens` | a line of its own, in no share figure; `"not measured"` until a measurement is recorded (its place and form are W1-42's, DEC-501); never the constant 3,250 |

**Learning metrics.**

- `acceptance_tests_rewritten`: a list, one entry per commit with `Task: <ticket>` and
  `Role: independent-test-designer` that comes after the ticket's first engineer commit (`Role: engineer`,
  same `Task:`) in the history of the project the counter runs in: `{"commit": <id, 7 characters or more>,
  "reason": <the value of its Rewrite-Reason: trailer>}`. A rewrite without the trailer has the reason
  `"reason not recorded"`. The commits were read and hold none: `[]`. The commits cannot be read:
  `"not measured"` (the record is still given).
- `kpi_disputes`: a list, one entry per line of the ticket's disputes record, in its order, each with
  `decision` (the id of the decision that settled it). The record is there and empty: `[]`. No record, a
  record that cannot be read, a line that names no decision: `"not measured"`. **The record is
  `docs/close/<ticket>/kpi-disputes.txt` (decided, DEC-501):** written by hand by the orchestrator at the
  merge (for a FULL ticket before the probe), one line per dispute beginning with the decision that settled
  it (`DEC-<number>: <what was disputed>`), an empty file for none. Not Markdown, so the record store never
  loads it; nothing of this ticket's code writes it.

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

## What is counted, form by form (DEC-495, DEC-501)

| Form in the log | Counted as | Case |
|---|---|---|
| Added context (`hook_additional_context`) of `SessionStart`, **each time it is given**, after a compaction too | `sessionstart_packet`: the texts of `content` | `test_sessionstart_packet_is_what_the_sessionstart_hooks_added`, `test_the_sessionstart_packet_is_counted_each_time_it_is_given` |
| Added context of any other event (`PreToolUse`, `PostToolUse`; an event neither specimen shows when the line is in this form) | `hook_output`: the texts of `content` | `test_hook_output_is_what_the_other_hooks_added`, `test_added_context_of_any_other_event_is_hook_output` |
| A successful run (`hook_success`, exit code 0) of any event with no added-context line after it, whatever the run line carries (`Stop` and `SubagentStop` carry the hook's plain output as `content` and `stdout`), and the `system` line after a Stop run | 0; the source stays measured | `test_a_hook_run_without_added_context_counts_zero` |
| The result of a call a PreToolUse hook blocked (the `user` line carries `toolDenialKind`; its `tool_result` is marked as an error and holds the harness's prefix, the hook's command and the hook's text) | `hook_output`: **the whole result text**; one in `larger_reading_hook_texts`. Also when the blocked command runs `gov`: the command never ran, the result is the hook's, it is counted once and is not `gov_output` | `test_the_text_of_a_blocking_hook_is_hook_output_by_the_larger_reading`, `test_a_blocked_gov_command_is_counted_once_as_hook_output` |
| The line of a hook that failed without blocking (`hook_non_blocking_error`) | `hook_output`: **the whole `stderr` and `stdout` of the line** (the larger reading: whether it reaches the model is not shown); one in `larger_reading_hook_texts` | `test_the_text_of_a_failing_hook_is_hook_output_by_the_larger_reading` |
| The result of a Bash call whose command runs `gov`, alone | `gov_output`: the result text; a result marked as an error like any other | `test_gov_output_is_the_results_of_the_bash_calls_that_run_gov`, `test_a_gov_result_marked_as_an_error_is_counted` |
| The result of a Bash call in which `gov` runs beside other commands (`&&`, `;`), through a pipe or with a redirection | `gov_output`: the whole result (it over-counts); one in `gov_results_counted_whole` | `test_gov_beside_other_commands_is_counted_whole_and_the_record_says_so` (4) |
| The lines of a sub-agent's file of a named session | with that session, by the rows above; its messages are in the session's tokens | `test_a_subagents_lines_and_tokens_belong_to_the_named_session`, `test_a_subagent_of_a_session_that_was_not_named_is_never_counted` |
| The summary, the local command's three `user` lines after a compaction boundary (the last holds the PreCompact hook's output), prompts, answers, results of other commands | nothing | `test_the_sessionstart_packet_is_counted_each_time_it_is_given`, `test_a_command_that_only_names_gov_is_not_gov_output` |
| All of the above in one session | every count and the three share figures as numbers | `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes` |

## The session logs the cases write

`<CLAUDE_CONFIG_DIR>/projects/<working directory with "-" for "/">/<session id>.jsonl`, compact JSON, one
object a line; a sub-agent's lines in `<session id>/subagents/agent-<agent id>.jsonl` beside it, with
`agent-<agent id>.meta.json` next to that. **The forms are the two specimens' and nothing else**: reduced
copies of the logs of two short headless sessions of Claude Code 2.1.288 in throwaway projects. The suite
does not read a specimen when it runs: `support.Log` and `support.SubLog` write the lines with the cases' own
texts. No real session log was read.

Shown by **both** specimens (S1: one SessionStart hook, one PostToolUse hook, one `gov` command):

- **A hook's run** is an `attachment` line whose `attachment` has `type: hook_success`, `hookName`
  (`SessionStart:startup`, `PostToolUse:Bash`), `toolUseID`, `hookEvent`, `content: ""`, `stdout` (the hook's
  own JSON, which repeats the text), `stderr`, `exitCode: 0`, `command`, `durationMs`.
- **What it added to the context** is the next `attachment` line: `type: hook_additional_context`, `content`
  (a list of texts), `hookName`, `toolUseID`, `hookEvent`; the line also has `rendered` and `renderedRole`.
- **A message of the model takes one `assistant` line per content block** with the same `message.id` and
  `requestId`, and each carries the `usage` of the message. A sum over lines counts a message more than once;
  ccusage counts each message once.
- **A command** is an assistant `tool_use` with `name: Bash` and `input.command`; its output is the
  `tool_result` with the same `tool_use_id` in the next `user` line (`content` a text, `is_error: false`),
  which also carries `toolUseResult.stdout` with the same text.
- **Every full line** carries `sessionId`, `cwd`, `version` (`2.1.288`), `isSidechain`, `uuid`, `parentUuid`,
  `timestamp`. Other lines (`queue-operation`, `last-prompt`, `cost-state`) carry their type.
- **A totals line (`cost-state`)** holds the usage summed per model and `totalAPIDuration`,
  `totalAPIDurationWithoutRetries`, `totalDuration`. Its token sums are not the assistant lines' (S1: input
  964 against 17). No case compares tokens with a totals line (DEC-501: the harness's totals are not used
  for tokens).

Shown by the **second** specimen only (S2: hooks on six events, one that blocks, one that fails, four forms of
a `gov` command, one sub-agent, one compaction):

- **`PreToolUse`** run and added-context lines (`hookName: PreToolUse:Bash`, the tool call's id as
  `toolUseID`), between the call and its result. **`SessionStart` again** after the compaction
  (`hookName: SessionStart:compact` on the run line), followed by its added-context line.
- **A hook that blocks** leaves no attachment line. The call's `user` line holds a `tool_result` with
  `is_error: true` and the content `PreToolUse:Bash hook error: [<the hook's command>]: <the hook's text>\n`;
  the line carries `toolUseResult` as a text (`Error: ` and the same content) and `toolDenialKind:
  "permission-rule"`. No PostToolUse line follows.
- **A hook that fails without blocking** is an `attachment` of `type: hook_non_blocking_error` with
  `hookName`, `toolUseID`, `hookEvent`, `stderr` (`Failed with non-blocking status code: <the hook's text>`),
  `stdout: ""`, `exitCode: 1`, `command`, `durationMs`, and no `content`. In the session's file it comes after
  the other PostToolUse hook's run and added context; in the sub-agent's file before them.
- **`Stop` and `SubagentStop` runs**: `hook_success` whose `content` and `stdout` hold the hook's plain
  output, with no added-context line after them. A Stop run is followed by a `system` line, `subtype:
  stop_hook_summary`, with `hookCount`, `hookInfos`, `hookErrors: []`, `hookAdditionalContext: []`,
  `preventedContinuation: false`, `stopReason: ""`, `hasOutput: true`, `toolUseID` (the run's).
- **A result marked as an error**: `is_error: true`, the content beginning `Exit code 2\n`, `toolUseResult`
  a text; no PostToolUse line follows it. **A command through a pipe with a redirection**: `input.command`
  as written, one result.
- **A command the model sent behind `cd <the working directory> &&`**: `input.command` holds the command
  **without** the `cd`; the line's `wireToolInputs` holds it with the `cd`, and `wireIngestContext` the
  directory. The command the counter reads is `input.command`.
- **The Agent tool call**: its `tool_result` has a list of texts as `content` and no `is_error`. Later a
  `user` line whose content is one text (`<task-notification>…`) tells the session that the sub-agent ended.
- **The first message of the session has three lines** (`thinking`, `text`, `tool_use`).
- **The sub-agent's file**: every full line carries the session's `sessionId`, `isSidechain: true` and
  `agentId`; assistant lines also `attributionAgent` and `effort`, and a model of their own; its tool-result
  line has no `toolUseResult`; it holds no totals line. **The two lines of its first message carry
  different usage** (the first: an earlier figure, 14 output tokens, a usage map with fewer keys and
  `stop_reason: null`; the second: 141); its last message is one line. The `.meta.json` holds `agentType`,
  `description`, `toolUseId`, `spawnDepth`, `requestShape`, `requestNonInteractive`.
- **A compaction**: a totals line; a `mode` line; a `system` line, `subtype: compact_boundary`, with
  `parentUuid: null`, `logicalParentUuid` and `compactMetadata`; a `user` line with the summary
  (`isCompactSummary: true`); three `user` lines of the local command (`<local-command-caveat>`,
  `<command-name>/compact`, and `<local-command-stdout>Compacted …\nPreCompact [<the hook's command>]
  completed successfully: <the hook's plain output></local-command-stdout>`); then SessionStart's run and
  added context. Lines after the boundary carry `slug`. **So the PreCompact hook's output is in the log**,
  inside the local command's own output, in no hook line. DEC-501 says it left no line and that its output
  is a gap the record names; the cases pin no count for it (AD-7).
- **Two totals lines**, one before the compaction and one at the end (27,508 and 41,994 ms of
  `totalAPIDuration` in S2); both name the sub-agent's model in `modelUsage`.

Established with ccusage 20.0.26 on logs written by the fixtures, in temporary folders: it reads the forms
above and counts each message once; with a sub-agent's file in its place it prints **one row for the session
that holds the sub-agent's messages** (the row names both models), and without the file the session's own
messages only; for a message whose lines differ in usage its figure is the **later** line's (output 141, not
14); when that later line is passed over, the earlier one's. It names the folder variable in its own error; a
folder without `projects/` is exit code 1; a folder without logs gives totals of zero and exit code 0; `--id`
with an unknown session prints `null` and exit code 0; **a line written with a space after its colons is
passed over silently, in a sub-agent's file too, and the session's row is printed without it**. Zero or a row
from ccusage is therefore not proof of what was measured.

### How "runs `gov`" is told

From `pyproject.toml` (`[project.scripts] gov = "gov.cli.main:main"`: an installed project calls `gov`) and
from both specimens (this project calls `PYTHONPATH=<src> python3 -m gov.cli.main`; there is no
`gov/__main__.py`). The hook settings (`.rulesync/hooks.jsonc`, `template/.rulesync/hooks.jsonc`,
`template/governance/kernel/settings.json`) call the hook scripts with `python3`, never `gov`, and settle
nothing more. A Bash command runs `gov` when **one of its simple commands** has as its first word, after
leading `NAME=value` assignments, `gov`, or `python3` followed by `-m gov.cli.main`. The command is
`input.command`. Pinned as counted: both forms, alone; and beside other commands (`&&`, `;`), through a pipe
or with a redirection, where the whole result is counted and noted (DEC-501). Pinned as not `gov` output: a
command that only names `gov` (`echo gov status`, `cat src/gov/...`, `git commit -m 'gov close ...'`,
`python3 -m pytest tests/unit/gov`, `grep -rn gov docs`, `tk show gov-0001`, `python3 -m gov_tools.report`),
a tool that is not Bash, and a `gov` command a hook blocked (hook output). Not pinned: AD-2.

## What the counter does not measure, by name

Each is `"not measured"` (or a refusal), never a number, and the reason is named without content:

| What | Case |
|---|---|
| A successful run line with another exit code than 0 (`hook_success`, `exitCode` 2), of SessionStart or another event | `test_a_form_the_specimen_does_not_show_is_not_measured` (`hook_output`, `sessionstart_packet`) |
| A hook attachment of a type neither specimen shows (`hook_blocking_error`), in the session's file or in a sub-agent's | same case |
| Added context in another form (`content` not a list of texts) | same case |
| A failing hook's line in another form (`stderr` not a text) | same case |
| A line after a Stop run that carries added context (`hookAdditionalContext` not empty) | same case |
| A `gov` command without its `tool_result`; a result whose `content` is not a text | same case (`gov_output`) |
| A log of another Claude Code version | `test_a_log_of_another_claude_code_version_is_refused_by_its_version` |
| ccusage's figures against the assistant lines of the session's file and of its sub-agents' files | `test_ccusage_figures_that_differ_from_the_logs_give_no_figure`, `test_a_line_ccusage_passes_over_gives_no_figure`, `test_a_subagents_file_that_ccusage_reads_otherwise_gives_no_figure` |
| The latency of a session without a totals line | `test_a_session_without_a_totals_line_has_no_latency` |
| The instruction files' estimate without a readable `CLAUDE.md` | `test_the_estimate_is_not_measured_without_its_instruction_file` |
| Checkpoints of a ticket without a checkpoint folder; an unreadable record; the close record before the close | `test_an_empty_checkpoint_folder_counts_zero_and_an_absent_one_is_not_measured`, `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3`, `test_the_close_record_is_not_measured_before_the_close` |
| KPI disputes without a readable record; rewrites and commit models without readable commits | `test_kpi_disputes_are_not_measured_without_a_readable_record`, `test_commits_that_cannot_be_read_are_not_measured` |
| The profile of a ticket that declares none | `test_a_ticket_without_a_profile_is_not_measured_for_the_profile` |
| `provider`, `files_read`; the sandbox's added system-prompt tokens | `test_provider_and_files_read_have_no_source_in_the_specimen`, `test_sandbox_tokens_are_a_line_apart_and_never_assumed` |

A session in the specimens' forms that holds no hook and no command was read: its three log sources are 0
(`test_a_log_that_was_read_and_holds_none_counts_zero`).

**Known gaps and residuals of DEC-501** (none makes a share figure "not measured"):

- **The output of a PreCompact hook** is not counted: the record names it in `known_gaps`
  (`precompact_hook_output`). See AD-7 for what the specimen holds.
- **`gov` inside `bash -c`, `eval`, backticks, `$(...)` or a wrapper script** is not seen: no case counts
  it, and a counter that passes such a command over is not wrong by this suite. A named residual.
- **Results counted whole over-count** `gov_output`; **texts counted by the larger reading** may over-count
  `hook_output`. The record says how many (`counting_notes`).
- **The harness's own totals** hold calls the log does not show as assistant lines: the denominator is
  slightly low and the share slightly high. W1-42 reports the difference once.
- **Not seen in either specimen, and without a case:** a call denied by a permission rule that is no hook
  (the same `toolDenialKind`); a line with `isSidechain: true` in the session's own file; a sub-agent of a
  sub-agent; a `gov` command behind a leading `cd` that the harness did not take off.

## KPI lines and covers ids

| Line | Cases |
|---|---|
| Success 1: governance tokens per ticket, joined with ccusage fresh input+output [CAP-04.b] | `test_joins_ccusage_input_and_output_of_the_tickets_sessions`, `test_names_each_of_the_seven_sources_of_governance_tokens`, `test_sessionstart_packet_is_what_the_sessionstart_hooks_added`, `test_hook_output_is_what_the_other_hooks_added`, `test_gov_output_is_the_results_of_the_bash_calls_that_run_gov`, `test_a_command_that_only_names_gov_is_not_gov_output`, `test_a_log_that_was_read_and_holds_none_counts_zero`, `test_a_form_the_specimen_does_not_show_is_not_measured` (9), `test_a_log_of_another_claude_code_version_is_refused_by_its_version`, `test_the_counter_prints_counts_only_never_content`, `test_the_estimate_is_a_line_of_its_own_labelled_estimated`, `test_the_estimate_follows_the_instruction_file`, `test_the_estimate_is_not_measured_without_its_instruction_file` (2), `test_counts_the_tickets_checkpoint_records`, `test_automatic_checkpoints_are_checkpoint_records`, `test_an_empty_checkpoint_folder_counts_zero_and_an_absent_one_is_not_measured`, `test_counts_the_tickets_close_record`, `test_the_close_record_is_not_measured_before_the_close`, `test_the_three_share_figures_are_the_numbers_the_case_computes`; **DEC-501:** `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes`, `test_a_hook_run_without_added_context_counts_zero`, `test_the_sessionstart_packet_is_counted_each_time_it_is_given`, `test_added_context_of_any_other_event_is_hook_output`, `test_the_text_of_a_blocking_hook_is_hook_output_by_the_larger_reading`, `test_the_text_of_a_failing_hook_is_hook_output_by_the_larger_reading`, `test_a_blocked_gov_command_is_counted_once_as_hook_output`, `test_a_gov_result_marked_as_an_error_is_counted`, `test_gov_beside_other_commands_is_counted_whole_and_the_record_says_so` (4), `test_a_subagents_lines_and_tokens_belong_to_the_named_session`, `test_a_subagent_of_a_session_that_was_not_named_is_never_counted` |
| Success 2: the share and the P1 fields; cache reads reported separately | `test_the_three_share_figures_are_the_numbers_the_case_computes`, `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes`, `test_record_names_every_p1_field_and_invents_none`, `test_sessions_carry_what_ccusage_measured_for_each`, `test_cost_is_ccusages`, `test_cache_reads_and_cache_creation_are_figures_of_their_own`, `test_the_model_is_reported_from_the_logs_and_from_the_commits`, `test_a_subagents_lines_and_tokens_belong_to_the_named_session` (tokens and model), `test_record_is_plain_data_a_close_record_can_carry`, `test_the_counter_writes_nothing`, `test_the_record_states_no_verdict_and_no_threshold` |
| Success 3: agent, provider, latency, files read [CAP-40.a] | `test_record_names_agent_provider_latency_and_files_read`, `test_provider_and_files_read_have_no_source_in_the_specimen`, `test_latency_is_the_api_duration_of_each_sessions_last_totals_line`, `test_a_session_without_a_totals_line_has_no_latency`, `test_the_agent_is_the_harness_and_its_version` |
| Success 4: the share per profile [CAP-53.c] | `test_record_names_the_tickets_profile_beside_the_share` (LITE, STANDARD, FULL), `test_a_ticket_without_a_profile_is_not_measured_for_the_profile` |
| Success 5: the three learning metrics; only the share has a threshold [CAP-40.c] | `test_record_carries_the_three_learning_metrics`, `test_rewrites_are_the_designers_commits_after_the_first_engineer_commit`, `test_commits_that_cannot_be_read_are_not_measured`, `test_kpi_disputes_are_read_from_the_orchestrators_record`, `test_kpi_disputes_are_not_measured_without_a_readable_record` (3), `test_the_record_states_no_verdict_and_no_threshold` |
| Success 6: the sandbox's tokens, a separate line [CAP-40.d] | `test_sandbox_tokens_are_a_line_apart_and_never_assumed` |
| Failure 1: a ticket closes without a share figure | `test_the_three_share_figures_are_the_numbers_the_case_computes` and `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes` (exit code 0 only with three numbers), `test_the_precompact_gap_is_named_and_is_no_entry_of_not_measured` (the notes and the gap do not take the figure away), `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3`, `test_no_session_of_the_ticket_gives_no_figure`, `test_named_session_without_a_log_gives_no_figure`, `test_absent_log_folder_gives_no_figure`, `test_empty_log_folder_gives_no_figure`, `test_absent_ccusage_refuses`, `test_ccusage_that_cannot_be_read_gives_no_figure` (3), `test_ccusage_figures_that_differ_from_the_logs_give_no_figure`, `test_a_line_ccusage_passes_over_gives_no_figure`, `test_a_subagents_file_that_ccusage_reads_otherwise_gives_no_figure` |
| Failure 2: cache reads are counted in the share | `test_cache_reads_change_neither_share_nor_tokens`, `test_cache_reads_and_cache_creation_are_figures_of_their_own`, `test_the_three_share_figures_are_the_numbers_the_case_computes` (121,000 cache reads), `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes` (30,400 cache reads, the sub-agent's among them; the denominator is input + cache creation + output) |
| The command exists | `test_the_counter_is_a_command_of_gov` |

For failure 1 the counter's part is this: it never ends with exit code 0 without three share figures that are
numbers. That `gov close` refuses on it is the W1-30 follow-up (DEC-495).

## Expected red against the counter as built (commit `7e7234b7`)

**19 failed, 63 passed.** Every failure is an assertion of the case about the record or the exit code; none
is a crash of a case or of a fixture (where a case checks its fixture against ccusage, that check comes first
and passes). The built counter reads the first specimen's forms only: it does not read a sub-agent's file
(so ccusage's row, which holds the sub-agent's messages, is not its own lines' sum, and it refuses), takes a
`system` or `mode` line and every hook event but SessionStart and PostToolUse as "not measured", and has no
`counting_notes`, `known_gaps`, latency or agent.

| Red | Why, as run |
|---|---|
| `test_every_count_of_a_session_in_the_second_specimens_form_is_the_number_the_case_computes`, `test_a_subagents_lines_and_tokens_belong_to_the_named_session`, `test_a_subagent_of_a_session_that_was_not_named_is_never_counted`, `test_a_hook_run_without_added_context_counts_zero` | no record: the command refuses (`SESSIONS_NOT_MEASURED`) a session that has a sub-agent's file, whose messages it does not read |
| `test_latency_is_the_api_duration_of_each_sessions_last_totals_line`, `test_a_session_without_a_totals_line_has_no_latency`, `test_the_agent_is_the_harness_and_its_version`, `test_the_precompact_gap_is_named_and_is_no_entry_of_not_measured` | the same refusal first (their fixture has the sub-agent's file); once it is read they stand on `latency`, `agent`, `known_gaps` and `counting_notes`, which the built record does not have (`latency` and `agent` are `"not measured"`) |
| `test_the_counter_prints_counts_only_never_content` | the second fixture does not end with exit code 0 (the same refusal; the built counter prints no content) |
| `test_the_sessionstart_packet_is_counted_each_time_it_is_given` | the three log sources are "not measured": the compaction's `system` and `mode` lines are of a type the built counter does not know |
| `test_added_context_of_any_other_event_is_hook_output` | `hook_output` is "not measured" for PreToolUse and UserPromptSubmit |
| `test_the_text_of_a_blocking_hook_is_hook_output_by_the_larger_reading` | `hook_output` is 0: the blocked call's result is not counted |
| `test_the_text_of_a_failing_hook_is_hook_output_by_the_larger_reading` | `hook_output` is "not measured": a hook line of an unknown type |
| `test_a_blocked_gov_command_is_counted_once_as_hook_output`, `test_a_gov_result_marked_as_an_error_is_counted` | `gov_output` is "not measured": a result marked as an error |
| `test_gov_beside_other_commands_is_counted_whole_and_the_record_says_so` (4) | `gov_output` is "not measured": a compound command or a redirection |

**Green (63):** the 52 cases of the earlier suite that were not touched;
`test_kpi_disputes_are_read_from_the_orchestrators_record` (docstring only); the nine of
`test_a_form_the_specimen_does_not_show_is_not_measured` (six kept, two of them renamed, and three new: the
built counter says "not measured" or refuses for each, in two of the new ones for another reason than the one
a counter of DEC-501 will have: the Stop line's type, the sub-agent's file as such); and
`test_a_subagents_file_that_ccusage_reads_otherwise_gives_no_figure` (the built counter refuses every
session with a sub-agent's file; the case holds a counter of DEC-501 to the cross-check). A case that needs
ccusage is skipped, with its reason, on a machine without it.

## Decided since the last version (DEC-501)

- **AD-2 (in part), AD-6:** hook runs of every event and `gov` commands in every plain form, as above.
- **AD-3:** latency and agent, as above. **AD-4:** the sandbox measurement's record is W1-42's; only the
  `"not measured"` state has a case. **AD-5:** the harness's totals are not used for tokens.
- **PR-1:** the KPI disputes record is `docs/close/<ticket>/kpi-disputes.txt`, as the cases already pinned.

## Awaiting decision (no case guesses these)

- **AD-1 The estimate's formula.** Which files beyond `CLAUDE.md` it stands on (`AGENTS.md`, the role file
  of the session's role, skills), whether it counts once per ticket or once per session, and what the MCP
  part is: the Gov OS brings no MCP definition today (no MCP source under `.rulesync/` or the template, and
  rulesync is run without that feature). The cases hold the properties only: a line apart, labelled, names
  its method and files, at least the tokens of `CLAUDE.md`, follows the file, `"not measured"` without it.
  The full fixture holds a project MCP file that defines no server, for which the MCP part must be a count;
  which count, and what it is without such a file, is open. **With the owner (DEC-501).**
- **AD-2 `gov` by a path or through a runner.** `gov` by a path (`.venv/bin/gov`, `./gov`), through `uv run`
  or another runner, as a module of another interpreter (`python -m gov.cli.main`, `python3.12 -m …`). No
  source shows how an installed project's sessions call it beyond the console script's name. No case.
- **AD-7 The PreCompact hook's output is in the second specimen's log**, inside the `<local-command-stdout>`
  `user` line after the compaction boundary, with the hook's command (not in a hook line). DEC-501 says the
  hook left no line. The cases pin the decision as it stands (a named gap, no count) and count nothing for
  that line.
- **AD-8 A failing hook of the SessionStart event** (`hook_non_blocking_error` with `hookEvent:
  SessionStart`): hook output, as DEC-501's sentence says for every failing hook, or the packet. No case.

The packages are in the designer's return message in full.

## Rewrites after implementation began (commit trailer `Rewrite-Reason:`)

Brought to DEC-501 (this version):

| Case | What changed | Decision |
|---|---|---|
| `test_a_form_the_specimen_does_not_show_is_not_measured` | three variants removed, because the second specimen shows their form and it is now counted: `context added under another hook event` (added context of any event counts), `gov in a sub-agent's lines` (a sub-agent's lines belong to the session), `gov inside a compound command` (counted whole). Two variants renamed, their logs unchanged: `a hook that fails` is now `a successful run line with another exit code`, `a SessionStart hook that fails` is now `a SessionStart run line with another exit code` (a failing hook has a form of its own now). Three variants added: a failing hook's line in another form, a line after a Stop run that carries added context, a hook run of another type in a sub-agent's file. Docstring: "neither specimen" | DEC-501 |
| `test_the_counter_prints_counts_only_never_content` | its fixture is the second fixture (every form of the second specimen); its "not measured" run uses forms that are still unseen; a run in which ccusage disagrees with a sub-agent's file is added | DEC-501 |
| `test_kpi_disputes_are_read_from_the_orchestrators_record` | docstring only: the record's place is decided, no longer proposed | DEC-501 |
| every case that writes logs | unchanged text; the totals line the fixtures write has three durations that differ (5,000, 4,969 and 3,012 ms in place of 5,000, 5,000 and 5,200) | DEC-501 |

No case about the estimate was added, changed or removed.

Brought to DEC-491 and DEC-495 (the version before):

| Case | What changed | Decision |
|---|---|---|
| `test_names_each_of_the_seven_sources_of_governance_tokens` | five measured sources in `governance_tokens`, two on the estimate's line | DEC-495 |
| `test_share_is_the_governance_total_over_input_plus_output` | removed; replaced by `test_the_three_share_figures_are_the_numbers_the_case_computes` (three figures, cache creation in the denominator, numbers asserted) | DEC-495 |
| `test_unreadable_checkpoint_record_gives_no_share` | removed; replaced by `test_a_part_that_is_not_measured_gives_no_sum_and_exit_code_3` (three figures; `not_measured` with reasons) | DEC-495 |
| `test_sandbox_tokens_are_a_line_apart_and_never_assumed` | outside the estimate and the three share figures too; the constant 3,250 nowhere in the output | DEC-491, DEC-495 |
| `test_no_session_of_the_ticket_gives_no_figure`, `test_named_session_without_a_log_gives_no_figure`, `test_absent_log_folder_gives_no_figure`, `test_empty_log_folder_gives_no_figure`, `test_ccusage_that_cannot_be_read_gives_no_figure` | unchanged text; the shared `assert_no_figure` now asks for the three share figures and cache creation to say `"not measured"` | DEC-495 |
| every case that writes logs | unchanged text; the logs are now written in the specimen's form (two lines a message, a `cost-state` line) | DEC-495 |
| every case | unchanged text; the fixture project now has the designer's commit before the engineer's | DEC-491 |
