# W1-31 acceptance tests — governance share counter

Ticket `DAEO-6mk8`, profile STANDARD (DEC-221): each KPI line's success and failure and the key edge cases.
Written before implementation by the Independent Test Designer (MR-3, DEC-069).

Run: `env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-31 -q -p no:cacheprovider -rs`

29 cases in `test_w1_31_share_counter.py`. Support: `w1_31_support.py`, `conftest.py`.

## What this ticket delivers, and what the cases test

The ticket builds the counter and what it returns for a ticket. Its `allowed_paths` are `src/gov/telemetry/**`
and `tests/unit/telemetry/**`; `src/gov/close/` is outside it. Four KPI lines say "the close record carries".
The cases test that every figure those lines name is in what the counter returns, in a form a close record can
carry. No case needs `src/gov/close/` to change. What has to change there is the first point under
"Awaiting decision".

## The interface the cases assume

`gov telemetry <ticket> --json [--ticket-session <session id>]...`

- A command module, `src/gov/telemetry/command.py`, by the convention in `src/gov/cli/main.py`. `telemetry` is
  not a reserved name, so no shared list of another suite changes. It is a read command: it writes nothing in
  the project (`test_the_counter_writes_nothing`).
- **The session logs** are the harness's local logs, read by ccusage (DEC-086). The command and ccusage take
  the folder from the environment variable `CLAUDE_CONFIG_DIR` (the folder that holds `projects/`), which the
  harness and ccusage both read; without it, the harness's default under `HOME`. The cases always set both to
  temporary folders.
- **ccusage** is found on `PATH` and run with its built-in prices (`--offline`), so the cost is deterministic.
- **The ticket's sessions** are named by the caller, one `--ticket-session` each. Nothing recorded on this
  machine ties a session to a ticket (see P-2), and the counter never takes a session that was not named.
- **Exit codes.** 0: the share is a number. 3 (declared in `EXIT_CODES`): the record is returned (`ok: true`)
  and the share is `"not measured"`. 1 with `ok: false`: a refusal (an unknown ticket; ccusage absent).
  Where the tokens of the sessions could not be measured (no session named, a named session without a log,
  no log folder, a ccusage that fails or answers with something else), the cases accept either a refusal or
  the record at exit code 3 in which the share, the tokens in and out, the cache reads and the cost all say
  `"not measured"`. They never accept exit code 0 or a number.
- **"not measured"** is the exact string `gov close` writes today for a field it did not measure.

The record (`result` of the envelope) is plain data (maps, lists, strings, numbers) that survives the YAML
frontmatter of a close record:

| Key | Value |
|---|---|
| `ticket`, `profile` | the ticket id; the profile its ticket file declares |
| `governance_tokens` | a map with exactly `instruction_files`, `sessionstart_packet`, `hook_output`, `gov_output`, `mcp_definitions`, `checkpoint_records`, `close_records` and `total`; each a count or `"not measured"`; `total` is their sum, or `"not measured"` when any of them is |
| `governance_share` | `total / (tokens_in + tokens_out)` as a fraction of 1, or `"not measured"` |
| `not_measured` | the list of the sources (by the names above) that were not measured; empty at exit code 0 |
| `tokens_in`, `tokens_out`, `cache_read_tokens`, `cache_creation_tokens`, `cost` | ccusage's figures summed over the ticket's sessions |
| `sessions` | one entry per session: `session`, `model`, `tokens_in`, `tokens_out`, `cache_read_tokens`, `cost` |
| `model`, `role`, `skill_versions`, `tool_versions`, `packet_id`, `retrieval_queries`, `retrieval_hits`, `files_written`, `tests`, `retries`, `handoffs`, `decisions`, `owner_interventions` | the other P1 fields: a measured value or `"not measured"`, never null or empty text |
| `agent`, `provider`, `latency`, `files_read` | from the session log: a measured value or `"not measured"` |
| `learning_metrics` | a map with exactly `kpi_disputes`, `acceptance_tests_rewritten`, `governance_share` |
| `sandbox_system_prompt_tokens` | a line of its own, outside `governance_tokens` |

**Token counter.** Session tokens are ccusage's. Governance text is counted with the counter of W1-24
(`gov.context`: 4 characters a token, rounded up), which W1-29's 2,500-token cap uses too. The fixtures' records
are a whole number of 4-character tokens long, so rounding per record or over all of them gives the same count.

## The session logs the cases write

`<CLAUDE_CONFIG_DIR>/projects/<working directory with "-" for "/">/<session id>.jsonl`, one JSON object a line:
one `user` line, then one `assistant` line per turn carrying `sessionId`, `cwd`, `version` (2.1.288, the
pinned Claude Code), `timestamp`, `requestId`, and `message` with `id`, `model` and `usage`
(`input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`).

How it was established: by running the registered ccusage 20.0.26 (`ccusage claude session --json --offline`)
against hand-written logs in a temporary folder, with `HOME` and `CLAUDE_CONFIG_DIR` both temporary. No real
session log was read. Observed:

- ccusage names the folder variable in its own error message; a folder without `projects/` is exit code 1.
- It prints per session `sessionId`, `projectPath`, `inputTokens`, `outputTokens`, `cacheCreationTokens`,
  `cacheReadTokens`, `totalCost`, `totalTokens` (which includes the cache reads), `modelsUsed`,
  `firstActivity`, `lastActivity`. It prints no agent, provider, latency or files read.
- **A folder without logs gives totals of zero and exit code 0. `--id` with an unknown session prints `null`
  and exit code 0. A line written with a space after its colons is passed over silently.** Zero from ccusage
  is therefore not proof that zero was measured; three cases stand on this.

What was not established: the fields of the harness's log beyond those ccusage reads (the form of hook
output, tool calls, tool results, sub-agent logs). It cannot be established here without reading real logs,
which no test and no worker does. The cases write none of them and assert nothing that depends on them (P-4).

## KPI lines and covers ids

| Line | Cases |
|---|---|
| Success 1: governance tokens per ticket, joined with ccusage fresh input+output [CAP-04.b] | `test_joins_ccusage_input_and_output_of_the_tickets_sessions`, `test_names_each_of_the_seven_sources_of_governance_tokens`, `test_counts_the_tickets_checkpoint_records`, `test_automatic_checkpoints_are_checkpoint_records`, `test_counts_the_tickets_close_record`, `test_share_is_the_governance_total_over_input_plus_output` |
| Success 2: the share and the P1 fields; cache reads reported separately | `test_record_names_every_p1_field_and_invents_none`, `test_sessions_carry_what_ccusage_measured_for_each`, `test_cost_is_ccusages`, `test_cache_reads_and_cache_creation_are_figures_of_their_own`, `test_record_is_plain_data_a_close_record_can_carry`, `test_the_counter_writes_nothing` |
| Success 3: agent, provider, latency, files read [CAP-40.a] | `test_record_names_agent_provider_latency_and_files_read` (with success 2's cases for the rest of CAP-40.a) |
| Success 4: the share per profile [CAP-53.c] | `test_record_names_the_tickets_profile_beside_the_share` (LITE, STANDARD, FULL) |
| Success 5: the three learning metrics [CAP-40.c] | `test_record_carries_the_three_learning_metrics` |
| Success 6: the sandbox's tokens, a separate line [CAP-40.d] | `test_sandbox_tokens_are_a_line_apart_and_never_assumed` |
| Failure 1: a ticket closes without a share figure | `test_share_is_the_governance_total_over_input_plus_output` (exit code 0 only with a number), `test_unreadable_checkpoint_record_gives_no_share`, `test_no_session_of_the_ticket_gives_no_figure`, `test_named_session_without_a_log_gives_no_figure`, `test_absent_log_folder_gives_no_figure`, `test_empty_log_folder_gives_no_figure`, `test_absent_ccusage_refuses`, `test_ccusage_that_cannot_be_read_gives_no_figure` (three forms) |
| Failure 2: cache reads are counted in the share | `test_cache_reads_change_neither_share_nor_tokens`, `test_cache_reads_and_cache_creation_are_figures_of_their_own` |
| The command exists | `test_the_counter_is_a_command_of_gov` |

For failure 1 the counter's part is this: it never ends with exit code 0 without a share that is a number.
That `gov close` refuses on it is outside this ticket (P-1).

## Expected red, and which failure is which

Today (no `src/gov/telemetry/`): **1 failed, 28 errors**.

- **The module is absent.** `test_the_counter_is_a_command_of_gov` fails with "gov telemetry is not built: no
  command module". The other 28 cases are errors at setup of the fixture `built`, with "gov telemetry is not
  built: there is no command module src/gov/telemetry/command.py".
- **Behaviour.** Once the command module exists, `built` passes and every failure is an assertion of the case
  itself. A case that needs ccusage is skipped, with its reason, on a machine without it.

## Awaiting decision (no case guesses these)

- **P-1** How the counter's figures reach the close record, and what refuses a close without a share.
- **P-2** How a session is attributed to a ticket. The cases take the sessions from the caller.
- **P-3** Whether cache creation belongs to "fresh input". The share cases use logs without cache creation.
- **P-4** What counts for the five sources without a recorded trace per ticket (instruction files, the
  SessionStart packet, hook output, `gov` output, governance MCP definitions), and the form of the harness
  log for agent, provider, latency and files read. The cases assert only that each is named with a count or
  `"not measured"`, and that the share is a number only when every source is. No case asserts a share that
  is a number for a full fixture.
- **P-5** How the sandbox's added system-prompt tokens are measured.
- **P-6** Where KPI disputes and rewritten acceptance tests, with their reasons, are read from.
- **P-7** Also open, without a case: a ticket without a `profile` (`gov close` reads it as STANDARD); an
  aggregate report across tickets by profile; whether a ticket with no checkpoint or close record counts 0
  for that source; the close record counting its own tokens; whether a session's model comes from the log
  (as the cases allow) or only from the commits' co-author lines (DEC-470).

The packages are in the designer's return message in full.
