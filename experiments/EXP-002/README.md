# EXP-002, hook-limit round (ticket DAEO-6ox0, W2-40)

What does Claude Code do with a hook that runs past its configured time limit: is the call allowed, denied or
failed, how long does it take, is the hook's process ended or left running? `run_hook_limit.py` measures one
case per call. The record is `hook-limit-record.md` (a skeleton until the results are in).

Note: `EXP-002` is also the id DEC-164 gives to the Wave 2 sandbox experiment of DEC-160; this folder holds only
the hook-limit round (DEC-827: one experiments folder per research ticket).

## What it does

For one case and one run it makes `<base>/<case>-<run>/` (a throwaway project, outside every git repository: the
script refuses a `--base` that has a `.git` at or above it), writes its `.claude/settings.json` (one hook, nothing
else), empties `hook.log` and `ran.txt`, and starts one `claude -p` session in that folder. The session is asked
for exactly one bash command: `touch <project>/ran.txt`. It then writes one JSON line to
`<out>/<case>-<run>.json` and to stdout.

- The session's environment has every `CLAUDE*` and `GOV_*` variable removed (as W1-46's fixture does, DEC-784).
  The count removed is shown by `--dry-run` as `env_variables_removed`; the names and values are never printed or kept.
- The command is `claude -p <prompt> --model <model> --output-format stream-json --verbose
  [--setting-sources project] --allowedTools Bash` (the earlier run's form, `docs/research/EXP-hook-time-limit.md`).
  `--setting-sources` is used if `claude --help` names it (checked at run time; no session). In 2.1.322 it does.
  Managed settings (`/etc/claude-code/`) and anything else not a "setting source" are not switched off by it.
- The session runs in its own process group. The script prints `pid <n>` at once and writes
  `<out>/<case>-<run>.pid`, so a hung session can be ended by that pid (or its process group, `-<n>`) with
  `tools/proc.sh`. The pid file is removed when the session has ended. After the per-session wall limit (the hook's
  sleep + 60 s) the script ends the group (SIGTERM, then SIGKILL) and records `"session": "timed out"`.
- The script keeps only the extracted fields below, never the raw stream, the environment or a key.
  `stderr_head` is the first 300 characters of the session's stderr (to show an authentication failure).
- It writes nothing outside `--base` and `--out`, reads no settings file but the one it wrote, and starts no
  process but `claude` (and `claude --help`).

## Flags

| Flag | Meaning |
|---|---|
| `--case <id>` | one case per call (below) |
| `--run a\|b` | the run; the five mandatory cases are run twice, `a` and `b` |
| `--base <dir>` | where the throwaway projects go (made if absent; outside every git repository) |
| `--out <dir>` | where `<case>-<run>.json` and `.pid` go (made if absent) |
| `--model <id>` | the model id of the session (required; the earlier run used `claude-haiku-4-5-20251001`) |
| `--claude <path>` | the claude program (default `/home/usain/.local/bin/claude`) |
| `--dry-run` | print the plan (settings, hook command, argv, wall limit) and start no session; creates nothing |
| `--hook-events` | off by default: also pass `--include-hook-events` and keep, per hook lifecycle event, a whitelist of fields (`subtype`, `hook_event`, `hook_name`, `outcome`, `exit_code`, `timeout`, `stdout`, `stderr`, each cut at 200 characters) and the event's key names. The event's shape is **not known** from 2.1.322's help text; the key names show it. Not part of the lead's contract: use it for one extra run if wanted. |

One project folder per case **and run** (`<case>-<run>`), so that a hook process left running by run `a` can never
write into run `b`'s log. The folder's `hook.log` and `ran.txt` are emptied before each session.

## Cases

| Case | Event | Limit (`timeout`) | The hook sleeps | The hook would exit | Runs |
|---|---|---|---|---|---|
| `pre-control-5` | PreToolUse | 5 s | 0 (refuses at once) | 2 | a, b (mandatory) |
| `pre-allow-5` | PreToolUse | 5 s | 25 s | 0 | a, b (mandatory) |
| `pre-deny-5` | PreToolUse | 5 s | 25 s | 2 | a, b (mandatory) |
| `pre-allow-60` | PreToolUse | **60 s** (the repository's own value) | 90 s | 0 | a, b (mandatory) |
| `pre-deny-60` | PreToolUse | 60 s | 90 s | 2 | a, b (mandatory); the case that matters: a refusal that comes after the limit |
| `pre-nolimit` | PreToolUse | none (no `timeout` key) | 130 s | 0 | once (optional): is the harness's default limit below or above 130 s |
| `post-5` | PostToolUse | 5 s | 25 s | 0 | once (optional) |
| `stop-5` | Stop | 5 s | 25 s | 0 | once (optional) |

The hook is a shell command. Before anything else it appends `started <epoch seconds with fractions>` to
`<project>/hook.log`; then, once a second for its sleep time, `tick <epoch>`; then `finished <epoch>`; for exit 2
it writes `refused by the experiment hook` to stderr; then it exits with its code. PreToolUse and PostToolUse
entries carry `"matcher": "Bash"`; the Stop entry has no matcher.

Wall limit of a session: the hook's sleep + 60 s (60 s, 85 s, 150 s, 190 s).

## The JSON line, field by field

| Field | Meaning |
|---|---|
| `case`, `run` | the case and run |
| `harness_version`, `model` | from the session's init message (`claude_code_version`, `model`); `model_requested` is what `--model` asked for |
| `hook_event`, `limit`, `hook_sleep_s`, `would_exit` | the case's configuration (`limit` is a number of seconds or `"none"`) |
| `call_ran_after_hook_start_s` | the mtime of `ran.txt` less the hook's first `started` time, in seconds; `"not run"` if `ran.txt` is absent. For PostToolUse and Stop it is negative or small by construction (the call runs first). |
| `session_wall_s` | seconds from the start of the `claude` process to its exit (not to the closing of its pipes) |
| `session_end_after_hook_start_s` | the session's end less the hook's first `started`: how long after the hook began the session ended (the wait for the hook, for a Stop case) |
| `hook_starts` | number of `started` lines (more than 1: the hook ran again, for instance after a retry by the model; the offsets below are then ambiguous) |
| `hook_finished` | `finished` is in the log |
| `finished_offset_s` | the `finished` time less `started`; null if not finished |
| `ticks`, `last_tick_offset_s` | number of ticks, and the last tick's time less `started` (null: none). Ticks that stop near the limit show the hook's process was ended there; ticks that go to the end show it was left running. |
| `hook_process` | derived: `never started`, `ran to its end` (it was **not** ended by the harness, though the session may have moved on long before: compare with `session_end_after_hook_start_s`) or `ended before finishing` |
| `ran_txt_exists` | whether the command ran (the hook did not stop it) |
| `tool_uses`, `tool_results` | the model's `tool_use` blocks and the `tool_result` blocks seen |
| `tool_is_error`, `tool_text_head` | the first tool result's `is_error` and first 300 characters of its text |
| `result_head`, `result_subtype`, `result_is_error` | the session's final result message (first 300 characters of the text) |
| `system_subtypes` | counts of the stream's other `system` messages by `subtype` (a message naming the timeout would show here) |
| `session` | `completed` or `timed out` (the wall limit was reached and the group ended) |
| `exit_code`, `pipes_open_10s_after_exit` | the session's exit code (negative: a signal); whether a process still held its stdout or stderr 10 s after the exit (a left-running hook that inherited them) |
| `session_id`, `project`, `start_epoch`, `pid` | the session id (init message), the throwaway project, the epoch time just before the start, the session's pid |
| `setting_sources_flag`, `hook_events_flag` | whether `--setting-sources project` and `--include-hook-events` were used |
| `stderr_head` | first 300 characters of the session's stderr |
| `hook_events` | only with `--hook-events` |

Before the script reads `hook.log` it waits until `started` + the hook's sleep + 3 s has passed (or `finished` is
in the log), so a hook process the harness left running has had time to write `finished`. A hook that never
started in the log reads `never started` (no wait).

## How to repeat it (run outside the sandbox: it needs the model API and the login)

Pick a `--base` outside every git repository and an `--out`; one command per case and run, for example:

    python3 experiments/EXP-002/run_hook_limit.py --case pre-deny-60 --run a --base /tmp/exp002-base --out /tmp/exp002-out --model <model id>

Order: the five mandatory cases, runs `a` then `b`; then the three optional cases once. Start with `--dry-run` for
a case to read its plan. A hung session: stop it by the pid the script printed, never by a name match. The throwaway
projects and the session transcripts the harness keeps under its own home are not touched by the script; remove
the projects under `--base` when done.

What was checked without a model: `--dry-run` for all eight cases; the run path (pid file, log wait, mtime
arithmetic, the JSON line, the wall time at the process's exit) against a stub standing in for `claude` that
leaves a hook running. What is **not** checked: the real stream's field names beyond those the earlier script
(`exp-hook-timeout.py`) read (`claude_code_version`, `tool_result.is_error`, `result`); `model`, `session_id`, and
the `tool_use` blocks are read by the same stream-json shape and are null or 0 if the real stream differs.
