"""Support code for the W1-31 acceptance tests (the governance share counter, ``gov telemetry``).

How the cases run (README, "The interface the cases assume"):

- **Through the command line only**: ``gov telemetry <ticket> --json`` through W1-07's console-script stand-in,
  its API-0002 envelope and its exit code. Nothing of ``src/gov/telemetry/`` is imported.
- **Every project is a temporary git repository built from scratch** (a ticket file, commits, checkpoint
  records). Nothing of this repository is copied; the code under test is this worktree's ``src/``.
- **No case reads the session logs of this machine**, and no case reads a specimen. Each case writes its own
  session logs, in the specimens' forms and with its own texts, in a temporary folder and gives that folder to
  the command, and to ccusage, as ``CLAUDE_CONFIG_DIR``; ``HOME`` is a temporary folder too, so that a counter
  which ignored the variable would still find no real log.
- **Deterministic, no network**: ccusage runs with its built-in prices (``--offline``).
"""

from __future__ import annotations

import json
import os
import pwd
import shutil
import site
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_W1_07 = str(_HERE.parent / "W1-07")
if _W1_07 not in sys.path:
    sys.path.insert(0, _W1_07)

import w1_07_support as cli_support  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
COMMAND = "telemetry"
NOT_MEASURED = "not measured"          # the word ``gov close`` already writes for a field it did not measure
ESTIMATED = "estimated"                # DEC-495: the label of the static estimate
REASON_NOT_RECORDED = "reason not recorded"   # DEC-491: a rewrite whose commit carries no Rewrite-Reason trailer
EXIT_OK, EXIT_GOV_ERROR, EXIT_USAGE, EXIT_NOT_MEASURED = 0, 1, 2, 3

TICKET, OTHER_TICKET = "PROJ-aaaa", "PROJ-bbbb"
WBS = "T-01"
MODEL = "claude-opus-5-5"
OTHER_MODEL = "claude-haiku-4-5-20251001"
VERSION = "2.1.288"                    # the Claude Code version of the first three specimens
VERSION_4 = "2.1.292"                  # the fourth specimen's (DEC-649, DEC-655)
LATER_VERSION = "2.1.296"              # a later one: no version is pinned (DEC-655)
SESSION_A = "11111111-1111-4111-8111-111111111111"
SESSION_B = "22222222-2222-4222-8222-222222222222"
SESSION_OTHER = "33333333-3333-4333-8333-333333333333"
SESSION_NOWHERE = "99999999-9999-4999-8999-999999999999"


def named(session, role):
    """A session of the ticket named with its role (DEC-507): the value of one ``--ticket-session``."""
    return f"{session}={role}"

# DEC-086 names seven sources of governance text. DEC-495: five are measured (three from the session logs, two
# from the ticket's record folders) and two are a static estimate on a line of their own.
LOG_SOURCES = ("sessionstart_packet", "hook_output", "gov_output")
RECORD_SOURCES = ("checkpoint_records", "close_records")
SOURCES = (*LOG_SOURCES, *RECORD_SOURCES)                    # ``governance_tokens``: the measured ones
ESTIMATED_SOURCES = ("instruction_files", "mcp_definitions")  # ``estimated_governance_tokens``
MCP_REASON = "mcp_definitions_reason"  # DEC-507: the 0 of the MCP definitions is never without its reason
ESTIMATE_KEYS = ("label", "method", "files", *ESTIMATED_SOURCES, MCP_REASON, "total")
NO_MCP_SERVER = "no MCP server"        # what that reason says: the Governance OS defines no MCP server
# DEC-507: the estimate stands, per session, on the file of the session's role and on these two where they exist.
ROLE_FILES_REL = ".claude/agents"
ROOT_INSTRUCTION_FILES = ("CLAUDE.md", "AGENTS.md")
ROLE_A, ROLE_B = "engineer", "independent-test-designer"
SHARE_PARTS = ("measured", "estimated", "total")
# Ticket KPI, second success line: the Contract v3 P1 fields, as the result names them.
P1_FIELDS = ("sessions", "model", "role", "ticket", "skill_versions", "tool_versions", "packet_id",
             "retrieval_queries", "retrieval_hits", "tokens_in", "tokens_out", "cost", "files_written", "tests",
             "retries", "handoffs", "decisions", "owner_interventions")
# Third success line: taken from the harness session log.
LOG_FIELDS = ("agent", "provider", "latency", "files_read")
# A bare temporary project holds no trace of these: nothing may be invented for them.
NO_TRACE_FIELDS = ("retrieval_queries", "retrieval_hits", "retries", "handoffs", "owner_interventions")
LEARNING_METRICS = ("kpi_disputes", "acceptance_tests_rewritten", "governance_share")
SANDBOX_LINE = "sandbox_system_prompt_tokens"
DISPUTES_NAME = "kpi-disputes.txt"     # docs/close/<ticket>/kpi-disputes.txt (DEC-501)
# DEC-501: what the record says beside its counts. None of these is an entry of ``not_measured``.
NOTES = "counting_notes"                       # a map with exactly the two counts below
LARGER_READING = "larger_reading_hook_texts"   # hook texts counted although they may not have reached the model
COUNTED_WHOLE = "gov_results_counted_whole"    # results of commands in which ``gov`` did not run alone
KNOWN_GAPS = "known_gaps"                      # a list of {"name", "reason"}: what the counter cannot count
PRECOMPACT_GAP = "precompact_hook_output"
API_DURATION = "harness_api_duration_ms"       # the one key of ``latency``, and a key of each session's entry
HARNESS = "Claude Code"                        # ``agent``: {"harness", "version"}

# The registered place of ccusage (governance/project/tool-registry.yaml: Node v22.23.3).
CCUSAGE_REL = ".nvm/versions/node/v22.23.3/bin"
SYSTEM_PATH = "/usr/bin:/bin"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "A Worker", "GIT_AUTHOR_EMAIL": "worker@example.invalid",
    "GIT_COMMITTER_NAME": "A Worker", "GIT_COMMITTER_EMAIL": "worker@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-07T09:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-07T09:00:00+00:00",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
}
CO_AUTHOR = "Claude Opus 5.5 <noreply@anthropic.com>"


# --------------------------------------------------------------------------
# ccusage
# --------------------------------------------------------------------------

def ccusage_dir():
    """The folder that holds the registered ccusage, or None where this machine has none."""
    home = Path(pwd.getpwuid(os.getuid()).pw_dir)  # the real home, whatever HOME says
    registered = home / CCUSAGE_REL
    if (registered / "ccusage").is_file():
        return registered
    found = shutil.which("ccusage")
    return Path(found).parent if found else None


def ccusage_sessions(logs, home):
    """What ccusage itself prints for the temporary log folder ``logs``: ``{session id: its row}``."""
    folder = ccusage_dir()
    assert folder is not None, "ccusage is not on this machine"
    done = subprocess.run(
        [str(folder / "ccusage"), "claude", "session", "--json", "--offline"],
        env={"PATH": f"{folder}:{SYSTEM_PATH}", "HOME": str(home), "CLAUDE_CONFIG_DIR": str(logs)},
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert done.returncode == 0, f"ccusage failed on the fixture's logs: {done.stderr}"
    return {row["sessionId"]: row for row in json.loads(done.stdout)["sessions"]}


# --------------------------------------------------------------------------
# Session logs, in the specimen's form (README, "The session logs the cases write")
# --------------------------------------------------------------------------

def tokens(text):
    """W1-24's counter (``gov.context``), which W1-29's cap uses too: 4 characters a token, rounded up."""
    return -(-len(text) // 4)


def pad(text):
    """``text`` filled to a whole number of 4-character tokens, so that a count is the same whether a counter
    rounds per text or over all of them."""
    return text + "." * (-len(text) % 4)


def gov_command(args, *, installed=True, src="/work/project/src"):
    """How ``gov`` is run through the Bash tool: the console script of an installed project (``gov <args>``,
    ``[project.scripts]`` of the packaging file), or the specimen's form, which this project uses."""
    return f"gov {args}" if installed else f"PYTHONPATH={src} python3 -m gov.cli.main {args}"


# The second specimen's hooks are one script, the event named by its argument. "MARK-": never printed.
HOOK_COMMAND_2 = "python3 /work/project/hooks/hook.py --MARK-CIVET"
# The harness's own two texts around a compaction the user asked for, as the second specimen holds them.
COMPACT_CAVEAT = ("<local-command-caveat>The command below was run directly in Claude Code, not sent to you as a "
                  "request, and its output goes straight to the user. It's recorded here as context for later "
                  "messages.</local-command-caveat>")
COMPACT_COMMAND = ("<command-name>/compact</command-name>\n            <command-message>compact</command-message>\n"
                   "            <command-args></command-args>")


def blocked_text(text, *, tool="Bash", command=f"{HOOK_COMMAND_2} PreToolUse"):
    """The result of a call a PreToolUse hook blocked, as the second specimen holds it: the harness's prefix
    (it names the hook's command), the hook's text and a line end; a whole number of 4-character tokens."""
    head = f"PreToolUse:{tool} hook error: [{command}]: {text}"
    return head + "." * (-(len(head) + 1) % 4) + "\n"


def failing_text(text):
    """The ``stderr`` of the line of a hook that failed without blocking: the harness's prefix and the text."""
    return pad(f"Failed with non-blocking status code: {text}")


def error_text(text, code=2):
    """The result of a command that ended with another exit code: marked as an error, the code first."""
    return pad(f"Exit code {code}\n{text}")


# The third specimen's hooks are one script too, the case named by its argument.
HOOK_COMMAND_3 = "python3 /work/project/hooks/hook.py --MARK-GENET"


def plain_text(text):
    """The plain output of a SessionStart hook, as its run line carries it: the line's ``content`` holds the
    text and its ``stdout`` the text and a line end. One character short of a whole number of 4-character
    tokens, so that the text with and without its line end is the same count."""
    return text + "." * ((3 - len(text)) % 4)


def hook_denial_text(reason, *, tool="Bash"):
    """The result of a call a PreToolUse hook denied by its answer, as the third specimen holds it: the
    harness's prefix and the hook's reason; no hook command in brackets and no line end (the result of a
    call a hook blocked has both)."""
    return pad(f"PreToolUse:{tool} hook error: {reason}")


def rule_denial_text(command, *, tool="Bash"):
    """The result of a call a permission rule denied, as the third specimen holds it: the harness's own
    sentence, which names the tool and the command. It is no hook's and no ``gov`` output."""
    return f"Permission to use {tool} with command {command} has been denied."


def feedback_errors(text, event="Stop"):
    """What a blocking Stop or SubagentStop hook left, as the ``system`` line after it holds it in
    ``hookErrors``: the hook's command in brackets, the hook's text and a line end."""
    head = f"Stop hook feedback:\n[{HOOK_COMMAND_3} {event}]: {text}"
    return (head + "." * (-(len(head) + 1) % 4) + "\n")[len("Stop hook feedback:\n"):]


def feedback_text(text, event="Stop"):
    """The line of feedback a blocking Stop or SubagentStop hook gives the session: the harness's heading
    (the same words for both events), then ``feedback_errors``. A whole number of 4-character tokens."""
    return "Stop hook feedback:\n" + feedback_errors(text, event)


# The fourth specimen's hooks are the kernel's scripts, one per event, called from the project's folder.
HOOK_COMMAND_4 = "python3 \"$CLAUDE_PROJECT_DIR/governance/kernel/hooks/{}\" --MARK-HYRAX"


def _step(name, tool_input, content, use_result, *, wire=None, error=None, denial=None):
    """One tool call of a message with several (``Log.turn``): the tool, its input, the text of its result
    and what the result line carries as ``toolUseResult``. ``error``: None, the result block has no
    ``is_error`` (the fourth specimen's Read, Grep, Write and Edit results); False, it says
    ``is_error: false`` (Bash); True, the result is marked as an error and ``toolUseResult`` is a text."""
    return {"name": name, "input": tool_input, "content": content, "use_result": use_result, "wire": wire,
            "error": error, "denial": denial}


def bash_step(command, output, *, committed=None):
    """A command through the Bash tool. ``committed``: the harness noted a commit the command made, beside
    the output (the fourth specimen's last command)."""
    use_result = {"stdout": output, "stderr": "", "interrupted": False, "isImage": False,
                  "noOutputExpected": False}
    if committed:
        use_result["gitOperation"] = {"commit": {"sha": committed, "kind": "committed", "branch": "main"}}
    return _step("Bash", {"command": command, "description": "run the command"}, output, use_result, error=False)


def denied_step(command, content):
    """A command a PreToolUse hook denied by its answer (``hook_denial_text``), in the third specimen's
    form, which the fourth shows again."""
    return _step("Bash", {"command": command, "description": "run the command"}, content, None, error=True,
                 denial="permission-rule")


def read_step(path, text):
    """The Read tool: the result's text is the file with line numbers; no ``is_error``."""
    rows = text.splitlines()
    numbered = "\n".join(f"{number}\t{row}" for number, row in enumerate(rows, 1))
    return _step("Read", {"file_path": path}, numbered, {"type": "text", "file": {
        "filePath": path, "content": text, "numLines": len(rows), "startLine": 1, "totalLines": len(rows)}})


def grep_step(pattern, found):
    """The Grep tool: the result's text is what was found; no ``is_error``."""
    return _step("Grep", {"pattern": pattern, "path": "src", "glob": "*.py", "output_mode": "content"}, found,
                 {"mode": "content", "numFiles": 0, "filenames": [], "content": found,
                  "numLines": found.count("\n") + 1, "totalLines": found.count("\n") + 1})


def write_step(path, text):
    """The Write tool: the result's text is the harness's own sentence; no ``is_error``."""
    return _step("Write", {"file_path": path, "content": text}, f"File created successfully at: {path}",
                 {"type": "create", "filePath": path, "content": text, "structuredPatch": [],
                  "originalFile": None, "userModified": False})


def edit_step(path, old, new, original):
    """The Edit tool: the input as logged has ``replace_all``, the input as sent has not; the result's
    text is the harness's own sentence; no ``is_error``."""
    sent = {"file_path": path, "old_string": old, "new_string": new}
    return _step("Edit", {"replace_all": False, **sent},
                 f"The file {path} has been updated successfully.",
                 {"filePath": path, "oldString": old, "newString": new, "originalFile": original,
                  "structuredPatch": [{"oldStart": 1, "oldLines": 1, "newStart": 1, "newLines": 1,
                                       "lines": [f"-{old}", f"+{new}"]}],
                  "userModified": False, "replaceAll": False}, wire=sent)


def shortened_text(full, folder, session, *, mark="b5u4ggt"):
    """The result of a command whose output was too long, as the third specimen's result line holds it: the
    harness's words, the path of the file in the session's ``tool-results`` folder that holds the full
    text, and a preview of the first 2,000 characters. Returns ``(content, file name)``; the file's name is
    as long as makes the content a whole number of 4-character tokens."""
    for extra in range(4):
        name = f"{mark}{'k' * (2 + extra)}.txt"
        content = ("<persisted-output>\n"
                   f"Output too large ({round(len(full) / 1024)}KB). Full output saved to: "
                   f"{Path(folder) / session / 'tool-results' / name}\n\n"
                   f"Preview (first 2KB):\n{full[:2000]}\n...\n</persisted-output>")
        if len(content) % 4 == 0:
            return content, name
    raise AssertionError("no file name makes the shortened result a whole number of tokens")


class Log:
    """The log of one session, line by line as Claude Code 2.1.288 wrote the specimen.

    A message of the model takes two ``assistant`` lines (one per content block), and each carries the whole
    ``usage`` of the message under the same message id and request id. A hook's run is an ``attachment`` line
    of type ``hook_success``; what it added to the context is the next ``attachment`` line, of type
    ``hook_additional_context``, with the hook event and the texts as ``content``. A command is a ``tool_use``
    of the Bash tool, and its output the ``tool_result`` with the same id in the next ``user`` line. The last
    line is ``cost-state``, whose sums are larger than the assistant lines' (as the specimen's are).
    """

    failing_first = False   # the session's own lines: the failing hook's line comes after the added context
    use_result = True       # the session's own tool-result lines carry ``toolUseResult``
    effort = None           # the fourth specimen: the session's own assistant lines carry an effort and a model
    totals_model = None     # the fourth specimen: its totals line names a model no assistant line carries
    unfinished = None       # no specimen: text after the last line, cut off before its end

    def __init__(self, session, *, cwd="/work/project", model=MODEL, version=VERSION):
        self.session, self.cwd, self.model, self.version = session, cwd, model, version
        self.lines, self.messages, self.spaced = [], [], set()
        self._count, self._last = 0, None
        self.tag, self._block = session[:8], "0000"   # what this log's message, request and tool ids carry
        self.subagents, self.slug = [], None
        self.tool_results = {}     # what the session's ``tool-results`` folder holds: {file name: full text}
        self.api_duration = 5000   # ``totalAPIDuration`` of the totals line at the end; None: no such line

    # -- line by line -------------------------------------------------------

    def _uuid(self):
        self._count += 1
        return f"{self.session[:8]}-{self._block}-4000-8000-{self._count:012d}"

    def _stamp(self):
        return f"2026-10-07T10:{self._count // 60:02d}:{self._count % 60:02d}.000Z"

    def add(self, head, *, sidechain=False, **tail):
        """One full line: ``head``, then the fields every full line of the specimen ends with."""
        uuid = self._uuid()
        line = {"parentUuid": self._last, "isSidechain": sidechain, **head, "uuid": uuid,
                "timestamp": self._stamp(), **tail, "userType": "external", "entrypoint": "claude-vscode",
                "cwd": self.cwd, "sessionId": self.session, "version": self.version, "gitBranch": "main"}
        if self.version is None:
            del line["version"]
        if self.slug:
            line["slug"] = self.slug
        self.lines.append(line)
        self._last = uuid
        return line

    def bare(self, kind, **fields):
        """A line the counter has no use for (the specimen holds many): its type and the session."""
        self.lines.append({"type": kind, "sessionId": self.session, **fields})

    # -- hooks --------------------------------------------------------------

    def hook(self, event, texts, *, name=None, tool_use_id=None, exit_code=0, run_type="hook_success",
             context=True, content=None, command="python3 governance/kernel/hooks/hook.py"):
        """A hook's run and, with ``context``, what it added: ``texts`` (a list of texts, or one text)."""
        texts = [texts] if isinstance(texts, str) else list(texts)
        name = name or event
        stdout = json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                                    "additionalContext": "\n".join(texts)}}) + "\n"
        self.add({"attachment": {"type": run_type, "hookName": name, "toolUseID": tool_use_id or self._uuid(),
                                 "hookEvent": event, "content": "", "stdout": stdout, "stderr": "",
                                 "exitCode": exit_code, "command": command, "durationMs": 20},
                  "type": "attachment"})
        if context:
            shown = name.split(":")[0] if event == "SessionStart" else name
            rendered = "".join(f"<system-reminder>\n{shown} hook additional context: {text}\n</system-reminder>"
                               for text in texts)
            self.add({"attachment": {"type": "hook_additional_context",
                                     "content": texts if content is None else content,
                                     "hookName": shown, "toolUseID": tool_use_id or event, "hookEvent": event},
                      "type": "attachment"}, rendered=[{"content": rendered}], renderedRole="system")
        return self

    def session_start(self, texts, **how):
        return self.hook("SessionStart", texts, name="SessionStart:startup", **how)

    def prompt(self, text="work"):
        self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": text}}, permissionMode="acceptEdits")
        return self

    # -- the model's messages ----------------------------------------------

    def _message(self, usage, block, stop, *, model=None, sidechain=False, preface=None, thinking=True,
                 first_output=None, wire=None, more=(), wires=None, after=None):
        """The lines of one message, one per content block: ``thinking`` (unless ``thinking`` is false), a
        text ``preface`` when given, then ``block``. Each carries the message's whole usage; with
        ``first_output`` the first line carries an earlier, smaller usage instead (that many output tokens
        and no stop reason), as the first message of the second specimen's sub-agent does. ``wire`` is the
        tool input as the model sent it, where the harness logged another ``input`` (a leading ``cd``).
        The fourth specimen: ``more`` are further blocks of the same message, after ``block``; ``wires``
        gives the input as sent for each tool-use id; ``after(block, line)`` is called when a block's line
        is written, before the next block's (a call's result line comes before the next call's line)."""
        fresh_in, out, created, read = usage
        number = len(self.messages) + 1
        model = model or self.model
        self.messages.append((model, usage))
        early = {"input_tokens": fresh_in, "cache_creation_input_tokens": created, "cache_read_input_tokens": read,
                 "cache_creation": {"ephemeral_5m_input_tokens": created, "ephemeral_1h_input_tokens": 0},
                 "output_tokens": first_output, "service_tier": "standard", "inference_geo": "not_available"}
        full = {"input_tokens": fresh_in, "cache_creation_input_tokens": created,
                "cache_read_input_tokens": read, "output_tokens": out,
                "output_tokens_details": {"thinking_tokens": 0},
                "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0},
                "service_tier": "standard",
                "cache_creation": {"ephemeral_1h_input_tokens": created, "ephemeral_5m_input_tokens": 0},
                "inference_geo": "not_available",
                "iterations": [{"input_tokens": fresh_in, "output_tokens": out, "cache_read_input_tokens": read,
                                "cache_creation_input_tokens": created,
                                "cache_creation": {"ephemeral_5m_input_tokens": 0,
                                                   "ephemeral_1h_input_tokens": created}, "type": "message"}],
                "speed": "standard", "fallback_credit": None}
        made = []
        blocks = ([{"type": "thinking", "thinking": "", "signature": "c2lnbmF0dXJl"}] if thinking else []) \
            + ([{"type": "text", "text": preface}] if preface is not None else []) + [block, *more]
        tail = {"perTurnEffort": None} if self.effort is None else {
            "advisorModel": model, "effort": self.effort, "perTurnEffort": self.effort}
        for index, content in enumerate(blocks):
            partial = first_output is not None and index == 0 and len(blocks) > 1
            message = {"model": model, "id": f"msg_{self.tag}_{number:03d}", "type": "message",
                       "role": "assistant", "content": [content], "container": None,
                       "stop_reason": None if partial else stop,
                       "stop_sequence": None, "stop_details": None, "usage": early if partial else full,
                       "input_transformations": [], "diagnostics": None, "context_management": None}
            head = {"message": message}
            if content["type"] == "thinking":
                head["thinkingDurationMs"] = 900
            elif content["type"] == "tool_use":
                head["wireToolInputs"] = {content["id"]: (wires or {}).get(content["id"]) or wire
                                          or content["input"]}
                if wire:
                    head["wireIngestContext"] = {content["id"]: {"cwd": self.cwd}}
            made.append(self.add({**head, "apiBlockIndex": index,
                                  "requestId": f"req_{self.tag}_{number:03d}", "type": "assistant"},
                                 sidechain=sidechain, **tail))
            if after:
                after(content, made[-1])
        return made[-1]

    def say(self, usage, text="done", **how):
        """A message that ends the turn: a thinking line and a text line, each with the message's usage."""
        self._message(usage, {"type": "text", "text": text}, "end_turn", **how)
        return self

    def tool(self, name, tool_input, output, usage=(10, 20, 0, 0), *, result=True, result_content=None,
             sidechain=False, **how):
        """A tool call and its result: a thinking line and a ``tool_use`` line, then the ``user`` line with the
        ``tool_result`` of the same id. Returns the tool-use id."""
        tool_id = f"toolu_{self.tag}{len(self.messages) + 1:03d}"
        called = self._message(usage, {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input,
                                       "caller": {"type": "direct"}}, "tool_use", sidechain=sidechain, **how)
        if result:
            self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                      "message": {"role": "user", "content": [
                          {"tool_use_id": tool_id, "type": "tool_result",
                           "content": output if result_content is None else result_content, "is_error": False}]}},
                     sidechain=sidechain,
                     toolUseResult={"stdout": output, "stderr": "", "interrupted": False, "isImage": False,
                                    "noOutputExpected": False},
                     sourceToolAssistantUUID=called["uuid"])
        return tool_id

    def bash(self, command, output, usage=(10, 20, 0, 0), *, hook=None, **how):
        """A command through the Bash tool and its output; with ``hook``, the PostToolUse hook's run after it
        and the text it added."""
        tool_id = self.tool("Bash", {"command": command, "description": "run the command"}, output, usage, **how)
        if hook is not None:
            self.hook("PostToolUse", hook, name="PostToolUse:Bash", tool_use_id=tool_id)
        return self

    # -- the forms the second specimen adds (README, "The session logs the cases write") ------------------

    def run_only(self, event, text="", *, name=None, tool_use_id=None, command=HOOK_COMMAND_2):
        """A hook's successful run after which no added-context line follows: it added nothing. ``text`` is
        the hook's plain output, which the run line itself carries as ``content`` and ``stdout`` (the
        specimen's Stop and SubagentStop runs do). Returns the run's id."""
        run_id = tool_use_id or self._uuid()
        self.add({"attachment": {"type": "hook_success", "hookName": name or event, "toolUseID": run_id,
                                 "hookEvent": event, "content": text, "stdout": text + "\n" if text else "",
                                 "stderr": "", "exitCode": 0, "command": f"{command} {event}", "durationMs": 17},
                  "type": "attachment"})
        return run_id

    def stop_summary(self, run_id=None, *, added=(), errors=(), prevented=False, command=f"{HOOK_COMMAND_2} Stop",
                     has_output=True):
        """The ``system`` line after the Stop hooks ran. After a run that succeeded it names the run and its
        duration and holds no error; after a hook that blocked (the third specimen) it holds the hook's
        command and text in ``hookErrors``, no duration, and an id of its own. ``added`` and ``prevented``
        are what no specimen's line carries. The fourth specimen: after a Stop hook that printed nothing
        the line says ``hasOutput: false`` and no run line comes before it (``quiet_stop``)."""
        info = {"command": command} if errors else {"command": command, "durationMs": 17}
        self.add({"type": "system", "subtype": "stop_hook_summary", "hookCount": 1, "hookInfos": [info],
                  "hookErrors": list(errors), "hookAdditionalContext": list(added),
                  "preventedContinuation": prevented, "stopReason": "", "hasOutput": has_output,
                  "level": "suggestion"},
                 toolUseID=run_id or self._uuid())
        return self

    def stop(self, text, *, added=()):
        """A Stop hook's run and the ``system`` line that follows it. ``added`` is what that line would carry
        as added context: the specimen's carries none."""
        return self.stop_summary(self.run_only("Stop", text), added=added)

    # -- the forms the third specimen adds (README, "The session logs the cases write") -------------------

    summary_after = True    # the session's own file: a ``system`` line follows the feedback of a blocking hook

    def start_plain(self, text):
        """A SessionStart hook that prints plain text: its run line carries the text as ``content`` and, with
        a line end, as ``stdout``, and what the harness rendered of it; no added-context line follows.
        Returns the run's id, which the specimen's second SessionStart hook shares."""
        run_id = self._uuid()
        self.add({"attachment": {"type": "hook_success", "hookName": "SessionStart:startup", "toolUseID": run_id,
                                 "hookEvent": "SessionStart", "content": text, "stdout": text + "\n", "stderr": "",
                                 "exitCode": 0, "command": f"{HOOK_COMMAND_3} SessionStartPlain", "durationMs": 56},
                  "type": "attachment"},
                 rendered=[{"content": "<system-reminder>\nSessionStart:startup hook success: "
                                       f"{text}\n</system-reminder>"}], renderedRole="system")
        return run_id

    def start_failing(self, stderr, run_id=None):
        """A SessionStart hook that fails: the line of a failing hook (``failing_text``) with that event."""
        return self.failing("SessionStart", stderr, name="SessionStart:startup", tool_use_id=run_id or self._uuid())

    def denied(self, command, content, usage=(10, 20, 0, 0)):
        """A command that was denied: by a PreToolUse hook's answer (``hook_denial_text``) or by a permission
        rule (``rule_denial_text``). The two result lines differ in their text and in nothing else: both are
        marked as an error and both carry ``toolDenialKind: "permission-rule"``, as the result of a call a
        hook blocked does. No hook line is written and none follows."""
        return self.blocked(command, content, usage)

    def feedback(self, content, *, summary=None, prevented=False):
        """A Stop or SubagentStop hook that blocks: the ``user`` line of feedback given to the session
        (``feedback_text``), marked ``isMeta``. In the session's own file a ``system`` line follows, which
        holds the same text, less the heading, in ``hookErrors``; in a sub-agent's file none follows. No
        hook line is written for the run."""
        self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": content}, "isMeta": True})
        if self.summary_after if summary is None else summary:
            self.stop_summary(errors=[content[len("Stop hook feedback:\n"):]], prevented=prevented,
                              command=f"{HOOK_COMMAND_3} Stop")
        return self

    def folder(self, logs):
        """The folder of this session's project among the logs: its own file is in it, and so is the folder
        named after the session, which holds ``subagents`` and ``tool-results``."""
        return Path(logs) / "projects" / self.cwd.replace("/", "-")

    def long_call(self, command, full, logs, usage=(10, 20, 0, 0), **how):
        """A command whose output ``full`` was too long: the result line holds the shortened form
        (``shortened_text``), and the session's ``tool-results`` folder a file with the full text. Returns
        the result line's text, which is what reached the session."""
        content, name = shortened_text(full, self.folder(logs), self.session,
                                       mark=f"b{len(self.tool_results)}u4ggt")
        self.tool_results[name] = full + "\n"
        self.call(command, content, usage, kept=(full, str(self.folder(logs) / self.session / "tool-results" / name)),
                  **how)
        return content

    # -- the forms the fourth specimen adds (README, "The session logs the cases write") ------------------

    def at(self, version):
        """This log and its sub-agents' as another Claude Code version wrote them: every line that carries
        a version carries ``version`` (DEC-655: no version is pinned)."""
        for log in (self, *self.subagents):
            log.version = version
            for line in log.lines:
                if "version" in line:
                    line["version"] = version
        return self

    def brief(self, text):
        """The prompt of a launched worker session, as the fourth specimen holds it: one text, given
        through the SDK."""
        self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": text}}, permissionMode="acceptEdits",
                 promptSource="sdk", turnOrigin="sdk", turnPosition={"promptIndex": 0, "turnIndex": 1})
        return self

    def mark(self, *kinds, full=False):
        """Attachment lines that are no hook's, as the specimens hold them: reduced to the attachment's
        type, with the session and nothing else (no ``version``). What else the harness's line holds, the
        specimens do not show; with ``full`` the line also ends with the fields every full line ends with
        (a ``version`` among them), as a hook's attachment line does."""
        for kind in kinds:
            if full:
                self.add({"attachment": {"type": kind}, "type": "attachment"})
            else:
                self.lines.append({"type": "attachment", "sessionId": self.session, "attachment": {"type": kind}})
        return self

    def marks(self):
        """The three lines the harness writes between turns (the specimens hold them by their type)."""
        for kind in ("last-prompt", "ai-title", "atis-latch"):
            self.bare(kind)
        return self

    def file_history(self, count=1):
        """``file-history-delta`` lines, which only the fourth specimen shows: by their type, without a
        session id (``file-history-snapshot`` is held the same way)."""
        for _ in range(count):
            self.bare("file-history-delta", sessionId=None)
        return self

    def turn(self, usage, steps, *, thinking=True, preface=None):
        """One message of the model with several tool calls, as the fourth specimen shows it: a line per
        content block (``thinking`` unless it is false, a text ``preface`` when given, then one
        ``tool_use`` line per entry of ``steps``), all with the message's id and whole usage; **each
        call's result line comes right after that call's line**, before the next call's. ``steps`` are
        made by ``bash_step``, ``read_step``, ``grep_step``, ``write_step``, ``edit_step`` and
        ``denied_step``."""
        number = len(self.messages) + 1
        by_id = {f"toolu_{self.tag}{number:03d}{'abcdefghijklm'[index]}": each for index, each in enumerate(steps)}
        blocks = [{"type": "tool_use", "id": tool_id, "name": each["name"], "input": each["input"],
                   "caller": {"type": "direct"}} for tool_id, each in by_id.items()]

        def after(block, line):
            each = by_id.get(block.get("id"))
            if each is None:
                return
            if each["error"]:
                result = {"type": "tool_result", "content": each["content"], "is_error": True,
                          "tool_use_id": block["id"]}
                tail = {"toolUseResult": "Error: " + each["content"]}
            else:
                result = {"tool_use_id": block["id"], "type": "tool_result", "content": each["content"]}
                if each["error"] is False:
                    result["is_error"] = False
                tail = {"toolUseResult": each["use_result"]}
            if each["denial"]:
                tail["toolDenialKind"] = each["denial"]
            self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                      "message": {"role": "user", "content": [result]}}, **tail,
                     sourceToolAssistantUUID=line["uuid"])

        self._message(usage, blocks[0], "tool_use", thinking=thinking, preface=preface, more=blocks[1:],
                      wires={tool_id: each["wire"] for tool_id, each in by_id.items() if each["wire"]},
                      after=after)
        return self

    def quiet_stop(self, command=None):
        """A Stop hook that printed nothing, as the fourth specimen shows it: no run line, only the
        ``system`` line, which names the hook's command and its duration and says ``hasOutput: false``."""
        return self.stop_summary(command=command or HOOK_COMMAND_4.format("stop.py"), has_output=False)

    def failing(self, event, stderr, *, name, tool_use_id, **other):
        """The line of a hook that failed without blocking: an attachment of a type of its own, whose
        ``stderr`` is the harness's prefix and the hook's text (``failing_text``)."""
        self.add({"attachment": {"type": "hook_non_blocking_error", "hookName": name, "toolUseID": tool_use_id,
                                 "hookEvent": event, "stderr": stderr, "stdout": "", "exitCode": 1,
                                 "command": f"{HOOK_COMMAND_2} {event}Fail", "durationMs": 19, **other},
                  "type": "attachment"})
        return self

    def result(self, tool_id, called, content, *, error=False, denial=None, kept=None):
        """The ``user`` line with the result of the call ``tool_id``. A result marked as an error has its
        block's keys in another order and ``toolUseResult`` as a text; a call a hook blocked carries
        ``toolDenialKind`` too. A sub-agent's result line carries no ``toolUseResult``. ``kept`` is
        ``(full text, path)`` of an output the harness kept in a file: ``toolUseResult`` then holds the first
        30,000 characters of the full text, the file's path and its size."""
        if error:
            block = {"type": "tool_result", "content": content, "is_error": True, "tool_use_id": tool_id}
            tail = {"toolUseResult": "Error: " + content}
        else:
            block = {"tool_use_id": tool_id, "type": "tool_result", "content": content, "is_error": False}
            tail = {"toolUseResult": {"stdout": kept[0][:30000] if kept else content, "stderr": "",
                                      "interrupted": False, "isImage": False, "noOutputExpected": False}}
            if kept:
                tail["toolUseResult"].update(persistedOutputPath=kept[1], persistedOutputSize=len(kept[0]) + 1)
        if not self.use_result:
            tail = {}
        if denial:
            tail["toolDenialKind"] = denial
        self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": [block]}}, **tail, sourceToolAssistantUUID=called["uuid"])

    def _call(self, name, tool_input, usage, **how):
        tool_id = f"toolu_{self.tag}{len(self.messages) + 1:03d}"
        called = self._message(usage, {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input,
                                       "caller": {"type": "direct"}}, "tool_use", **how)
        return tool_id, called

    def call(self, command, output, usage=(10, 20, 0, 0), *, pre=None, post=None, fails=None, error=False,
             wire=None, failure=None, kept=None, **how):
        """A command through the Bash tool as the second specimen shows it: the call; with ``pre`` the
        PreToolUse hook's run and the text it added; the result (``error``: marked as an error); then, with
        ``post``, the PostToolUse hook's run and the text it added, and with ``fails`` the line of a second
        PostToolUse hook that failed (``fails`` is its ``stderr``). ``wire`` is the command as the model sent
        it where the harness logged ``command`` without its leading ``cd``. The third specimen: with
        ``failure``, the run of the hook of the event after a failed tool call and the text it added;
        ``kept``, see ``result``."""
        tool_input = {"command": command, "description": "run the command"}
        tool_id, called = self._call("Bash", tool_input, usage,
                                     wire={**tool_input, "command": wire} if wire else None, **how)
        if pre is not None:
            self.hook("PreToolUse", pre, name="PreToolUse:Bash", tool_use_id=tool_id,
                      command=f"{HOOK_COMMAND_2} PreToolUse")
        self.result(tool_id, called, output, error=error, kept=kept)
        if failure is not None:
            self.hook("PostToolUseFailure", failure, name="PostToolUseFailure:Bash", tool_use_id=tool_id,
                      command=f"{HOOK_COMMAND_3} PostToolUseFailure")
        after = []
        if post is not None:
            after.append(lambda: self.hook("PostToolUse", post, name="PostToolUse:Bash", tool_use_id=tool_id,
                                           command=f"{HOOK_COMMAND_2} PostToolUse"))
        if fails is not None:
            after.append(lambda: self.failing("PostToolUse", fails, name="PostToolUse:Bash", tool_use_id=tool_id))
        for step in (reversed(after) if self.failing_first else after):
            step()
        return self

    def blocked(self, command, content, usage=(10, 20, 0, 0)):
        """A command a PreToolUse hook blocked. No hook line is written: the hook's text is the call's result
        (``blocked_text``), marked as an error, on a line that carries ``toolDenialKind``."""
        tool_id, called = self._call("Bash", {"command": command, "description": "run the command"}, usage)
        self.result(tool_id, called, content, error=True, denial="permission-rule")
        return self

    def subagent(self, agent, *, model=OTHER_MODEL):
        """The log of a sub-agent of this session: a file of its own (``SubLog``), written with this one."""
        return SubLog(self, agent, model)

    def launch(self, sub, usage=(10, 20, 0, 0), *, prompt="MARK-TENREC run the one command", answer="launched"):
        """The Agent tool call that started ``sub``: its result is a list of texts and carries no error mark."""
        tool_id, called = self._call("Agent", {"description": "run the one command", "prompt": prompt}, usage)
        sub.tool_use_id = tool_id
        self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": [{"tool_use_id": tool_id, "type": "tool_result",
                                                           "content": [{"type": "text", "text": answer}]}]}},
                 toolUseResult={"isAsync": True, "status": "async_launched", "agentId": sub.agent,
                                "description": "run the one command", "resolvedModel": sub.model,
                                "prompt": prompt, "canReadOutputFile": True},
                 sourceToolAssistantUUID=called["uuid"])
        return self

    def notice(self, text):
        """The ``user`` line by which the harness tells the session that its sub-agent has finished."""
        self.add({"promptId": f"notice-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": text}}, permissionMode="acceptEdits",
                 origin={"kind": "task-notification", "producer": "session-task"}, promptSource="system",
                 turnOrigin="task_notification")
        return self

    def totals(self, api_duration):
        """A totals line (``cost-state``) here, in the middle of the log: the specimen has one before its
        compaction and one at the end."""
        self.lines.append(self._totals(api_duration))
        return self

    def compact(self, summary, precompact, packet, *, api_duration):
        """A compaction as the second specimen shows it: a totals line, the boundary (a ``system`` line), the
        summary, the three ``user`` lines of the local command (the last holds the PreCompact hook's plain
        output inside the command's own output), then SessionStart's run and the packet it gave again."""
        self.totals(api_duration).bare("mode")
        logical, self._last, self.slug = self._last, None, "quiet-fixture-slug"
        self.add({"logicalParentUuid": logical, "type": "system", "subtype": "compact_boundary",
                  "content": "Conversation compacted", "isMeta": False, "level": "info",
                  "compactMetadata": {"trigger": "manual", "preTokens": 36000, "durationMs": 14000,
                                      "postTokens": 4000, "cumulativeDroppedTokens": 32000}})
        said = {"promptId": f"compact-{self.session[:8]}", "type": "user"}
        self.add({**said, "message": {"role": "user", "content": summary}, "isVisibleInTranscriptOnly": True,
                  "isCompactSummary": True})
        self.add({**said, "message": {"role": "user", "content": COMPACT_CAVEAT}, "isMeta": True})
        self.add({**said, "message": {"role": "user", "content": COMPACT_COMMAND}})
        self.add({**said, "message": {"role": "user", "content": (
            "<local-command-stdout>Compacted (ctrl+o to see full summary)\n"
            f"PreCompact [{HOOK_COMMAND_2} PreCompact] completed successfully: {precompact}</local-command-stdout>")}})
        return self.hook("SessionStart", packet, name="SessionStart:compact",
                         command=f"{HOOK_COMMAND_2} SessionStart")

    # -- what the log holds, as a case counts it itself ---------------------

    def usage(self, subagents=False):
        """``(input, output, cache creation, cache read)`` summed once per message, each with the usage of
        its last line; with ``subagents``, the messages of the sub-agents' files too."""
        logs = (self, *self.subagents) if subagents else (self,)
        return tuple(sum(each[1][index] for log in logs for each in log.messages) for index in range(4))

    def _totals(self, api_duration):
        """A ``cost-state`` line: the usage summed per model, the sub-agents' models among them, larger than
        the assistant lines' (as the specimens' are), and three durations that differ."""
        usage = {}
        for log in (self, *self.subagents):
            for model, (fresh_in, out, created, read) in log.messages:
                sums = usage.setdefault(model, {"inputTokens": 900, "outputTokens": 15, "thinkingTokens": 0,
                                                "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0,
                                                "webSearchRequests": 0, "costUSD": 0.01})
                sums["inputTokens"] += fresh_in
                sums["outputTokens"] += out
                sums["cacheReadInputTokens"] += read
                sums["cacheCreationInputTokens"] += created
        if self.totals_model:
            usage = {self.totals_model: {"inputTokens": 2992, "outputTokens": 19, "thinkingTokens": 0,
                                         "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0,
                                         "webSearchRequests": 0, "costUSD": 0.003}, **usage}
        return {"type": "cost-state", "sessionId": self.session, "totalCostUSD": 0.01 * len(usage),
                "totalAPIDuration": api_duration, "totalAPIDurationWithoutRetries": api_duration - 31,
                "totalToolDuration": 100, "totalLinesAdded": 0, "totalLinesRemoved": 0,
                "totalDuration": api_duration - 1988, "startTime": 1791398922006, "modelUsage": usage,
                "hasUnknownModelCost": False}

    def _dump(self, path, lines, skipped):
        """Compact JSON, as the harness writes it. A line whose number (from 0, among ``self.lines``, which
        begin after ``skipped`` lines of the file) is in ``self.spaced`` is written with a space after its
        colons and commas: ccusage 20.0.26 passes over such a line silently."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(
            (json.dumps(line) if number - skipped in self.spaced else json.dumps(line, separators=(",", ":")))
            + "\n" for number, line in enumerate(lines)), encoding="utf-8")
        return path

    def write(self, logs):
        """Write ``<logs>/projects/<cwd with - for />/<session id>.jsonl`` and return the file; the files of
        the session's sub-agents are written under ``<session id>/subagents/`` beside it. The last line is
        a totals line, unless ``self.api_duration`` is None."""
        lines = [{"type": "queue-operation", "sessionId": self.session}, *self.lines,
                 {"type": "last-prompt", "sessionId": self.session}]
        if self.api_duration is not None:
            lines.append(self._totals(self.api_duration))
        folder = self.folder(logs)
        for sub in self.subagents:
            sub.write_beside(folder)
        for name, text in self.tool_results.items():
            kept = folder / self.session / "tool-results" / name
            kept.parent.mkdir(parents=True, exist_ok=True)
            kept.write_text(text, encoding="utf-8")
        path = self._dump(folder / f"{self.session}.jsonl", lines, 1)
        if self.unfinished is not None:   # a last line the harness did not finish: no line end, no whole object
            with path.open("a", encoding="utf-8") as handle:
                handle.write(self.unfinished)
        return path


class SubLog(Log):
    """The log of one sub-agent, as the second specimen shows it: a file of its own,
    ``<session id>/subagents/agent-<agent id>.jsonl`` beside the session's ``<session id>.jsonl``, with a
    ``.meta.json`` next to it. Its lines carry the session's id, ``isSidechain: true`` and ``agentId``; its
    tool-result line has no ``toolUseResult``; after a command the failing hook's line comes before the other
    hook's run and added context; it holds no totals line."""

    failing_first, use_result = True, False
    summary_after = False   # the third specimen: no ``system`` line follows the feedback in a sub-agent's file

    def __init__(self, parent, agent, model):
        super().__init__(parent.session, cwd=parent.cwd, model=model, version=parent.version)
        self.agent, self.tag, self.tool_use_id = agent, f"{parent.session[:8]}{agent}", None
        self._block = f"{len(parent.subagents) + 1:04d}"
        parent.subagents.append(self)

    def add(self, head, *, sidechain=True, **tail):
        if head.get("type") == "assistant":
            tail = {"attributionAgent": "general-purpose", "effort": "high", **tail}
        return super().add({"agentId": self.agent, **head}, sidechain=True, **tail)

    def task(self, text="MARK-TENREC run the one command"):
        """The first line: what the session asked of the sub-agent."""
        self.add({"promptId": f"prompt-{self.session[:8]}", "type": "user",
                  "message": {"role": "user", "content": text}})
        return self

    def write_beside(self, folder):
        path = Path(folder) / self.session / "subagents" / f"agent-{self.agent}.jsonl"
        self._dump(path, self.lines, 0)
        path.with_suffix(".meta.json").write_text(json.dumps(
            {"agentType": "general-purpose", "description": "run the one command", "toolUseId": self.tool_use_id,
             "spawnDepth": 1, "requestShape": "background", "requestNonInteractive": True},
            separators=(",", ":")), encoding="utf-8")
        return path


def write_session(logs, session_id, turns, *, cwd="/work/project", model=MODEL):
    """Write the log of a session without hooks and without commands: one prompt, then one message of the
    model per entry of ``turns``, each ``(input, output, cache_creation, cache_read)``. Returns the file."""
    log = Log(session_id, cwd=cwd, model=model).prompt()
    for usage in turns:
        log.say(usage)
    return log.write(logs)


# --------------------------------------------------------------------------
# A temporary project, built from scratch
# --------------------------------------------------------------------------

def git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          env={"PATH": os.environ.get("PATH", SYSTEM_PATH), "HOME": str(root), **GIT_ENV})
    assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr}"
    return done.stdout


def ticket_text(ticket, profile="STANDARD"):
    lines = ["---", f"id: {ticket}", "status: in_progress", "deps: []", "links: []",
             "created: 2026-10-01T00:00:00Z", "type: task", "priority: 2", "assignee: engineer",
             f"external-ref: {WBS}", f"wbs_id: {WBS}", "title: A fixture ticket", "class: implementation",
             "state_class: AUTHORITATIVE", "role: engineer", "allowed_paths:", "- src/example/**",
             "kpis:", "  success:", "  - it works", "  failure:", "  - it does not"]
    if profile is not None:
        lines.append(f"profile: {profile}")
    return "\n".join(lines + ["---", "# A fixture ticket", ""])


def checkpoint_text(ticket, number, filler=""):
    """A checkpoint record of ``ticket`` in the kernel's form, padded to a whole number of 4-character tokens,
    so that the count is the same whether a counter rounds per record or over all of them."""
    ident = f"CP-{ticket}-{number:04d}"
    text = ("---\n"
            f"id: {ident}\ntype: checkpoint\nstatus: ACTIVE\nstate_class: NARRATIVE\n"
            f"title: {ticket} at stop\ntask: {ticket}\ntask_status: in_progress\ntrigger: stop\n"
            "next_action: resume\ncreated: '2026-10-07T09:30:00Z'\n"
            f"inputs:\n- id: {ticket}\n  version: untracked\n  hash: sha256:{'0' * 64}\n"
            "---\n\n"
            f"# {ident}\n\n## Next action\n\nresume {filler}\n")
    return text + "\n" * (-len(text) % 4)


def close_text(ticket):
    text = f"---\nid: CL-{ticket}\ntype: close\nstatus: ACTIVE\ntask: {ticket}\n---\n\n# CL-{ticket}\n\n\n"
    return text + "\n" * (-len(text) % 4)


class Project:
    """A temporary git repository with one in-progress ticket and one engineer commit of that ticket."""

    def __init__(self, root, profile="STANDARD"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        git(self.root, "init", "-q", "-b", "main")
        self.write(".gitignore", ".gov-runtime/\n")
        self.write(f".tickets/{TICKET}.md", ticket_text(TICKET, profile))
        self.write(f".tickets/{OTHER_TICKET}.md", ticket_text(OTHER_TICKET))
        self.commit("tickets", "Role: orchestrator")
        self.write(f"tests/acceptance/{WBS}/test_it.py", "def test_it():\n    assert True\n")
        self.tests = self.commit("the acceptance tests", f"Task: {TICKET}", "Role: independent-test-designer",
                                 "Implements: CAP-00.a")   # before implementation began: never a rewrite
        self.write("src/example/a.py", "VALUE = 1\n")
        self.work = self.commit("the work", f"Task: {TICKET}", "Role: engineer", "Implements: CAP-00.a",
                                f"Co-Authored-By: {CO_AUTHOR}")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
        return path

    def commit(self, message, *trailers):
        """Commit everything with ``trailers`` and return the commit's full id."""
        git(self.root, "add", "-A")
        args = ["commit", "-q", "--no-gpg-sign", "--allow-empty", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        git(self.root, *args)
        return git(self.root, "rev-parse", "HEAD").strip()

    def add_checkpoint(self, number, ticket=TICKET, filler="", automatic=False):
        """Write a checkpoint record of ``ticket`` and return its number of tokens."""
        base = ".gov-runtime/scratch/checkpoints" if automatic else "docs/checkpoints"
        text = checkpoint_text(ticket, number, filler)
        self.write(f"{base}/{ticket}/CP-{ticket}-{number:04d}.md", text)
        return tokens(text)

    def add_close(self, ticket=TICKET):
        """Write the close record of ``ticket``, as after ``gov close``, and return its number of tokens."""
        self.write(f"docs/close/{ticket}/CL-{ticket}.md", close_text(ticket))
        return tokens(close_text(ticket))

    def add_role(self, role, more=""):
        """The file of ``role`` as rulesync generates it for Claude Code (W1-33): ``.claude/agents/<role>.md``,
        a whole number of 4-character tokens long. Returns its tokens."""
        text = pad(f"---\nname: {role}\ndescription: \"MARK-AARDVARK the {role} role of the fixture\"\n---\n\n"
                   f"# {role}\n\n- **Purpose:** MARK-AARDVARK do the work of the {role} role.\n" + more)
        self.write(f"{ROLE_FILES_REL}/{role}.md", text)
        return tokens(text)

    def add_instructions(self, more=""):
        """The instruction files rulesync generates for Claude Code and the others (W1-38), the files of two
        roles (W1-33), and a project MCP file that defines no server. Returns the tokens of ``CLAUDE.md``."""
        rule = pad("# Governance\n\nMARK-AARDVARK Work on one ticket. Stay inside its allowed paths.\n" + more)
        self.write("CLAUDE.md", rule)
        self.write("AGENTS.md", pad("Please also follow the rule below.\n\n" + rule))
        self.write(".mcp.json", '{"mcpServers": {}}\n')
        for role in (ROLE_A, ROLE_B):
            self.add_role(role, "It is the longer of the two files.\n" if role == ROLE_B else "")
        return tokens(rule)

    def file_tokens(self, rel):
        """The tokens of the project file ``rel`` as the case counts them itself; 0 for a file that is not
        there (DEC-507: ``CLAUDE.md`` and ``AGENTS.md`` count "where they exist")."""
        path = self.root / rel
        return tokens(path.read_text(encoding="utf-8")) if path.is_file() else 0

    def estimate(self, *roles):
        """What the case computes for ``instruction_files`` (DEC-507): for each session, named here by its
        role, the role's file under ``.claude/agents/`` plus ``CLAUDE.md`` and ``AGENTS.md`` where they
        exist; the ticket's figure is the sum over its sessions."""
        shared = sum(self.file_tokens(rel) for rel in ROOT_INSTRUCTION_FILES)
        return sum(self.file_tokens(f"{ROLE_FILES_REL}/{role}.md") + shared for role in roles)

    def estimate_files(self, *roles):
        """The project files that estimate stands on, each once: relative paths."""
        return sorted({f"{ROLE_FILES_REL}/{role}.md" for role in roles}
                      | {rel for rel in ROOT_INSTRUCTION_FILES if (self.root / rel).is_file()})

    def add_disputes(self, *lines, ticket=TICKET):
        """The record the orchestrator writes by hand at the merge (proposed place and form, README PR-1)."""
        return self.write(f"docs/close/{ticket}/{DISPUTES_NAME}", "".join(line + "\n" for line in lines))


# --------------------------------------------------------------------------
# The full fixture: every source measured or estimated
# --------------------------------------------------------------------------

# Every text a case writes into a log carries "MARK-": none of it may appear in anything the command prints.
MARK = "MARK-"
PACKET_A = pad("MARK-ZEBRA packet: ticket PROJ-aaaa is in progress; next action: resume the work")
PACKET_B = pad("MARK-OKAPI packet: ticket PROJ-aaaa; second session")
PACKET_OTHER = pad("MARK-IBIS packet of other work " + "x" * 400)
HOOK_1 = pad("MARK-LEMUR the guard recorded one write")
HOOK_2 = pad("MARK-TAPIR context is at 40 percent")
HOOK_3 = pad("MARK-MARMOT a checkpoint is due")
HOOK_OTHER = pad("MARK-HERON hook text of other work " + "y" * 400)
GOV_1 = pad("MARK-QUOKKA usage: gov status [-h] [--json]\n  the ticket is in progress")
GOV_2 = pad("MARK-NARWHAL {\"ok\": true, \"command\": \"check\", \"result\": {\"families\": 12}}")
GOV_3 = pad("MARK-AXOLOTL doctor: every tool is at its registered version")
GOV_OTHER = pad("MARK-PANGOLIN gov output of other work " + "z" * 400)
OTHER_OUT = "MARK-CASSOWARY total 4\ndrwxr-xr-x 2 worker worker 4096 src\n" * 20   # output of a command that is not gov
HOOK_COMMAND = "python3 governance/kernel/hooks/hook.py --MARK-OCELOT"


def full_logs():
    """The logs of the full fixture, not yet written: two sessions of the ticket and one of other work."""
    first = Log(SESSION_A).session_start(PACKET_A, command=HOOK_COMMAND).prompt("MARK-WOMBAT do the work")
    first.bash(gov_command("status --session MARK-KAKAPO"), GOV_1, (1000, 200, 3000, 50000), hook=HOOK_1)
    first.bash("ls -la src/gov  # MARK-DUGONG", OTHER_OUT, (100, 50, 0, 1000), hook=HOOK_2)
    first.bash(gov_command("check --json", installed=False), GOV_2, (500, 300, 0, 70000))
    first.say((40, 60, 0, 0), "MARK-GECKO done")
    second = Log(SESSION_B, model=OTHER_MODEL).session_start(PACKET_B).prompt()
    second.bash(gov_command("doctor"), GOV_3, (400, 100, 500, 0), hook=HOOK_3).say((30, 20, 0, 0))
    other = Log(SESSION_OTHER, cwd="/work/other").session_start(PACKET_OTHER).prompt()
    other.bash(gov_command("status"), GOV_OTHER, (9000, 900, 0, 0), hook=HOOK_OTHER).say((10, 10, 0, 0))
    return first, second, other


def full_fixture(project, logs, *, change=None):
    """A ticket of which every source can be measured or estimated: two sessions with a SessionStart packet,
    PostToolUse hook output and ``gov`` commands, one checkpoint record, the close record, the instruction
    files and a project MCP file that defines no server. ``change(first, second)`` may add to the two logs
    before they are written. Returns what the case computes itself: the count of each measured source, the
    tokens of ``CLAUDE.md``, and the sessions' ``(input, output, cache creation, cache read)``."""
    first, second, other = full_logs()
    if change:
        change(first, second)
    for log in (first, second, other):
        log.write(logs)
    counts = {"sessionstart_packet": tokens(PACKET_A) + tokens(PACKET_B),
              "hook_output": tokens(HOOK_1) + tokens(HOOK_2) + tokens(HOOK_3),
              "gov_output": tokens(GOV_1) + tokens(GOV_2) + tokens(GOV_3),
              "checkpoint_records": project.add_checkpoint(1), "close_records": project.add_close()}
    rule = project.add_instructions()
    project.commit("governance files", "Role: orchestrator")
    usage = tuple(a + b for a, b in zip(first.usage(), second.usage()))
    return {"counts": counts, "rule": rule, "usage": usage, "logs": (first, second, other),
            "estimate": project.estimate(ROLE_A, ROLE_B)}


# The two sessions of the fixtures' ticket, each named with its role (DEC-507). Named so, the estimate of the
# instruction files is ``expected["estimate"]``; named by their ids alone it is "not measured".
ROLED = (named(SESSION_A, ROLE_A), named(SESSION_B, ROLE_B))


# --------------------------------------------------------------------------
# The second fixture: every form the second specimen shows (DEC-501)
# --------------------------------------------------------------------------

PACKET_2 = pad("MARK-SAIGA packet: ticket PROJ-aaaa is in progress; resume at the third step")
PRE_1 = pad("MARK-BILBY the guard allows this command")
PRE_2 = pad("MARK-NUMBAT the guard allows this command, the second")
PRE_3 = pad("MARK-QUOLL the guard allows it")
PRE_4 = pad("MARK-POTOROO the guard allows the pipe")
POST_1 = pad("MARK-DINGO the guard recorded nothing written")
POST_2 = pad("MARK-BETTONG context is at 30 percent")
POST_4 = pad("MARK-KOWARI a checkpoint is due soon")
FAIL_1 = failing_text("MARK-CURLEW the second hook could not write its record")
FAIL_2 = failing_text("MARK-GALAH the second hook failed again")
FAIL_4 = failing_text("MARK-JABIRU the second hook failed a third time, at more length than before")
BLOCK_1 = blocked_text("MARK-BROLGA the guard refuses this command: outside the allowed paths")
GOV2_1 = pad("MARK-MULGARA usage: gov doctor [-h] [--json] [--root <path>]\n  --json  structured output")
GOV2_2 = pad("MARK-DUNNART the ticket is in progress; 3 commits")
GOV2_3 = error_text("MARK-ANTECHINUS usage: gov [-h] <command> ...\ngov: error: argument <command>: invalid choice")
GOV2_4 = pad("MARK-PLANIGALE usage: gov doctor [-h] [--json]\n   [--role <role>]")
SUB_PRE = pad("MARK-NINGAUI the guard allows the sub-agent's command")
SUB_POST = pad("MARK-KULTARR the guard recorded the sub-agent's command")
SUB_FAIL = failing_text("MARK-PHASCOGALE the second hook failed in the sub-agent")
SUB_GOV = pad("MARK-MONJON usage: gov doctor [-h] [--json] [--root <path>] [--session <id>]")
STOP_TEXT = "MARK-WALLAROO the stop hook's plain output, which adds nothing"
SUBSTOP_TEXT = "MARK-PADEMELON the sub-agent stop hook's plain output"
PRECOMPACT_TEXT = "MARK-BANDICOOT the pre-compaction hook's plain output " + "p" * 200
SUMMARY = "MARK-ECHIDNA This session is being continued from a previous conversation. " + "s" * 400
NOTICE = "<task-notification>\n<status>completed</status>\n<result>MARK-GLIDER done</result>\n</task-notification>"
AGENT_A, AGENT_OTHER = "a1b2c3d4e5f6a7b8c", "f9e8d7c6b5a4f3e2d"
API_DURATION_EARLIER, API_DURATION_A, API_DURATION_B = 27000, 41000, 6000


def second_logs():
    """The logs of the second fixture, not yet written.

    The first session is in the second specimen's forms, in its order: SessionStart's packet; a ``gov``
    command with PreToolUse context, PostToolUse context and a second PostToolUse hook that fails; the same
    for a command the model sent behind ``cd ... &&`` (logged without it); a ``gov`` command whose result is
    marked as an error (no PostToolUse line follows); one through a pipe with a redirection; a command a
    PreToolUse hook blocks; a sub-agent, whose file holds one ``gov`` command with its hook lines, a first
    message whose two lines differ in usage, a last message of one line and a SubagentStop run; two Stop
    runs; a compaction with the PreCompact hook's output in the local command's own output, and the packet
    given again; two totals lines. The second session is in the first specimen's forms. The third is other
    work and has a sub-agent too: nothing of it is the ticket's."""
    first = Log(SESSION_A)
    first.hook("SessionStart", PACKET_2, name="SessionStart:startup", command=f"{HOOK_COMMAND_2} SessionStart")
    first.prompt("MARK-WOMBAT do the six steps")
    first.call(gov_command("doctor --help", installed=False), GOV2_1, (1000, 250, 3000, 0),
               pre=PRE_1, post=POST_1, fails=FAIL_1, preface="MARK-GECKO I run the steps in order")
    first.call(gov_command("status --session MARK-KAKAPO"), GOV2_2, (100, 180, 400, 3000),
               pre=PRE_2, post=POST_2, fails=FAIL_2,
               wire="cd /work/project && " + gov_command("status --session MARK-KAKAPO"))
    first.call(gov_command("nosuchcommand --MARK-KEA", installed=False), GOV2_3, (100, 140, 400, 3400),
               pre=PRE_3, error=True)
    first.call(gov_command("doctor --help", installed=False) + " 2>&1 | head -3  # MARK-TAKAHE", GOV2_4,
               (100, 160, 300, 3800), pre=PRE_4, post=POST_4, fails=FAIL_4)
    first.blocked("echo MARK-DUGONG", BLOCK_1, (100, 120, 300, 4100))
    sub = first.subagent(AGENT_A)
    first.launch(sub, (80, 170, 200, 4400))
    sub.task().call(gov_command("doctor --help", installed=False), SUB_GOV, (30, 141, 2000, 0),
                    pre=SUB_PRE, post=SUB_POST, fails=SUB_FAIL, first_output=14)
    sub.say((30, 4, 300, 2000), "MARK-GECKO done", thinking=False).run_only("SubagentStop", SUBSTOP_TEXT)
    first.say((80, 440, 500, 4600), "MARK-GECKO five steps are done").stop(STOP_TEXT)
    first.notice(NOTICE).say((100, 140, 800, 5100), "MARK-GECKO done").stop(STOP_TEXT)
    first.compact(SUMMARY, PRECOMPACT_TEXT, PACKET_2, api_duration=API_DURATION_EARLIER)
    first.api_duration = API_DURATION_A
    second = Log(SESSION_B).session_start(PACKET_B).prompt()
    second.bash(gov_command("doctor"), GOV_3, (400, 100, 500, 0), hook=HOOK_3).say((30, 20, 0, 0))
    second.api_duration = API_DURATION_B
    other = Log(SESSION_OTHER, cwd="/work/other").session_start(PACKET_OTHER).prompt()
    other.bash(gov_command("status"), GOV_OTHER, (9000, 900, 0, 0), hook=HOOK_OTHER)
    stray = other.subagent(AGENT_OTHER)
    other.launch(stray)
    stray.task().call(gov_command("status"), GOV_OTHER, (7000, 700, 0, 0), pre=HOOK_OTHER, post=HOOK_OTHER,
                      fails=failing_text(HOOK_OTHER))
    stray.say((10, 10, 0, 0), thinking=False)
    other.say((10, 10, 0, 0))
    return first, second, other


def second_fixture(project, logs, *, change=None):
    """A ticket of which every source can be measured or estimated, with a session in the second specimen's
    forms. Returns what the case computes itself: ``counts`` (each measured source), ``notes`` (how many hook
    texts were counted by the larger reading: the blocking hook's and the four failing hooks'; how many
    ``gov`` results were counted whole: the pipe's), ``usage`` (the two sessions' and the sub-agent's
    messages, each once with the usage of its last line), ``latency`` and ``rule`` (the tokens of
    ``CLAUDE.md``)."""
    first, second, other = second_logs()
    if change:
        change(first, second)
    for log in (first, second, other):
        log.write(logs)
    hook_texts = (PRE_1, PRE_2, PRE_3, PRE_4, POST_1, POST_2, POST_4, FAIL_1, FAIL_2, FAIL_4, BLOCK_1,
                  SUB_PRE, SUB_POST, SUB_FAIL, HOOK_3)
    counts = {"sessionstart_packet": 2 * tokens(PACKET_2) + tokens(PACKET_B),
              "hook_output": sum(tokens(text) for text in hook_texts),
              "gov_output": sum(tokens(text) for text in (GOV2_1, GOV2_2, GOV2_3, GOV2_4, SUB_GOV, GOV_3)),
              "checkpoint_records": project.add_checkpoint(1), "close_records": project.add_close()}
    rule = project.add_instructions()
    project.commit("governance files", "Role: orchestrator")
    usage = tuple(a + b for a, b in zip(first.usage(subagents=True), second.usage()))
    return {"counts": counts, "rule": rule, "usage": usage, "logs": (first, second, other),
            "notes": {LARGER_READING: 5, COUNTED_WHOLE: 1},
            "latency": API_DURATION_A + API_DURATION_B, "estimate": project.estimate(ROLE_A, ROLE_B)}


# --------------------------------------------------------------------------
# The third fixture: every form the third specimen shows (DEC-502)
# --------------------------------------------------------------------------

PACKET_3 = plain_text("MARK-FOSSA packet printed as plain text: ticket PROJ-aaaa is in progress")
START_FAIL = failing_text("MARK-TAYRA the second SessionStart hook could not read its record")
FAIL_CONTEXT = pad("MARK-KINKAJOU the command failed: read its message before the next step")
GOV3_1 = pad("MARK-OLINGO usage: gov doctor [-h] [--json] [--root <path>]\n  --json  structured output")
GOV3_2 = error_text("MARK-COATI usage: gov [-h] <command> ...\ngov: error: argument <command>: invalid choice")
GOV3_LONG = "MARK-GRISON a line of the over-long gov output\n" * 2600        # about 120,000 characters
OTHER_LONG = "MARK-ZORILLA a line of another command's over-long output\n" * 2200
GOV3_PIPE = pad("MARK-RATEL usage: gov doctor [-h] [--json]\n   [--role <role>]")
HOOK_DENY = hook_denial_text("MARK-TAMANDUA the guard denies this command: outside the allowed paths")
STOP_FEEDBACK = feedback_text("MARK-CACOMISTLE the record is not written yet: write it, then stop")
SUB_FEEDBACK = feedback_text("MARK-BINTURONG the sub-agent has not answered in one word", "SubagentStop")
SUB_GOV3 = pad("MARK-LINSANG usage: gov doctor [-h] [--json] [--root <path>] [--session <id>]")
STOP_TEXT_3 = "MARK-SURICATE the stop hook's plain output after it let the session stop"
SUBSTOP_TEXT_3 = "MARK-KUSIMANSE the sub-agent stop hook's plain output"
GOV_PATH = "/work/project/.venv/bin/gov"   # ``gov`` called by a path, as the third specimen's sessions call it
RULE_DENIED = ("echo MARK-NYALA now", "gov close PROJ-aaaa --MARK-NYALA", f"{GOV_PATH} pause --MARK-NYALA")
API_DURATION_3 = 20000


def third_logs(logs):
    """The logs of the third fixture, not yet written; ``logs`` is the folder they will be written to (a
    shortened result names a file in it).

    The first session is in the third specimen's forms, in its order: a SessionStart hook that prints plain
    text and one that fails; ``gov`` called by a path; ``gov`` called by the interpreter after an
    assignment, its result marked as an error, with the run and the added context of the hook of the event
    after a failed tool call; a command that is not ``gov`` and a ``gov`` command by a path whose outputs
    were too long (a shortened result each, the full texts in ``tool-results``); ``gov`` by a path through
    a pipe; a call a PreToolUse hook denies by its answer; three calls a permission rule denies, two of
    which would run ``gov``; a sub-agent, whose file holds a first message of one line with its ``gov``
    call by a path, a blocking SubagentStop hook's feedback and a later successful run; a blocking Stop
    hook's feedback with its ``system`` line; two later Stop runs that succeed; a totals line. The second
    session is in the first specimen's forms. The third is other work in the same forms: nothing of it is
    the ticket's."""
    first = Log(SESSION_A)
    first.start_failing(START_FAIL, first.start_plain(PACKET_3))
    first.prompt("MARK-WOMBAT do the six steps")
    first.call(f"{GOV_PATH} doctor --help", GOV3_1, (900, 350, 3300, 0))
    first.call(gov_command("nosuchcommand --MARK-KEA", installed=False), GOV3_2, (80, 130, 500, 3300),
               error=True, failure=FAIL_CONTEXT)
    first.long_call("python3 -c \"print('MARK-DUGONG ' * 6000)\"", OTHER_LONG, logs, (80, 120, 300, 3800))
    shortened = first.long_call(f"{GOV_PATH} status --all --MARK-KAKAPO", GOV3_LONG, logs, (80, 110, 900, 4100))
    first.call(f"{GOV_PATH} doctor --help 2>&1 | head -3  # MARK-TAKAHE", GOV3_PIPE, (80, 100, 200, 5000))
    first.denied("echo MARK-DUGONG denied", HOOK_DENY, (80, 100, 900, 5200))
    for command in RULE_DENIED:
        first.denied(command, rule_denial_text(command), (80, 110, 200, 6100))
    sub = first.subagent(AGENT_A)
    first.launch(sub, (80, 160, 200, 6700))
    sub.task().call(f"{GOV_PATH} doctor --help", SUB_GOV3, (3, 92, 2000, 0), thinking=False)
    sub.say((1, 4, 300, 2000), "MARK-GECKO done", thinking=False).feedback(SUB_FEEDBACK)
    sub.say((2, 4, 60, 2300), "MARK-GECKO done", thinking=False).run_only(
        "SubagentStop", SUBSTOP_TEXT_3, command=HOOK_COMMAND_3)
    first.say((80, 110, 500, 6900), "MARK-GECKO five steps are done").feedback(STOP_FEEDBACK)
    first.say((90, 65, 170, 7400), "MARK-GECKO done").stop(STOP_TEXT_3)
    first.notice(NOTICE).say((100, 200, 440, 7600), "MARK-GECKO done").stop(STOP_TEXT_3)
    first.api_duration = API_DURATION_3
    second = Log(SESSION_B).session_start(PACKET_B).prompt()
    second.bash(gov_command("doctor"), GOV_3, (400, 100, 500, 0), hook=HOOK_3).say((30, 20, 0, 0))
    second.api_duration = API_DURATION_B
    other = Log(SESSION_OTHER, cwd="/work/other")
    other.start_failing(failing_text(HOOK_OTHER), other.start_plain(plain_text(PACKET_OTHER)))
    other.prompt().call(f"{GOV_PATH} status", GOV_OTHER, (9000, 900, 0, 0))
    other.long_call(f"{GOV_PATH} status --all", GOV_OTHER * 40, logs)
    other.denied("echo denied", hook_denial_text(HOOK_OTHER))
    stray = other.subagent(AGENT_OTHER)
    other.launch(stray)
    stray.task().call(f"{GOV_PATH} status", GOV_OTHER, (7000, 700, 0, 0), thinking=False)
    stray.say((10, 10, 0, 0), thinking=False).feedback(feedback_text(HOOK_OTHER, "SubagentStop"))
    stray.say((10, 10, 0, 0), thinking=False)
    other.say((10, 10, 0, 0)).feedback(feedback_text(HOOK_OTHER)).say((10, 10, 0, 0)).stop(STOP_TEXT_3)
    first.shortened = shortened
    return first, second, other


def third_fixture(project, logs, *, change=None):
    """A ticket of which every source can be measured or estimated, with a session in the third specimen's
    forms. Returns what the case computes itself: ``counts`` (each measured source; the over-long ``gov``
    output with the count of its shortened result line, ``shortened``, not of its full text), ``notes``
    (five hook texts by the larger reading: the plain SessionStart text, the failing SessionStart hook's,
    the hook's denial, the Stop and the SubagentStop feedback; one ``gov`` result counted whole: the
    pipe's), ``usage`` (the two sessions' and the sub-agent's messages), ``latency`` and ``estimate`` (the
    instruction files of the two sessions when they are named with their roles, ``ROLED``)."""
    first, second, other = third_logs(logs)
    if change:
        change(first, second)
    for log in (first, second, other):
        log.write(logs)
    hook_texts = (START_FAIL, FAIL_CONTEXT, HOOK_DENY, STOP_FEEDBACK, SUB_FEEDBACK, HOOK_3)
    gov_texts = (GOV3_1, GOV3_2, first.shortened, GOV3_PIPE, SUB_GOV3, GOV_3)
    counts = {"sessionstart_packet": tokens(PACKET_3) + tokens(PACKET_B),
              "hook_output": sum(tokens(text) for text in hook_texts),
              "gov_output": sum(tokens(text) for text in gov_texts),
              "checkpoint_records": project.add_checkpoint(1), "close_records": project.add_close()}
    project.add_instructions()
    project.commit("governance files", "Role: orchestrator")
    usage = tuple(a + b for a, b in zip(first.usage(subagents=True), second.usage()))
    return {"counts": counts, "usage": usage, "logs": (first, second, other), "shortened": first.shortened,
            "notes": {LARGER_READING: 5, COUNTED_WHOLE: 1}, "latency": API_DURATION_3 + API_DURATION_B,
            "estimate": project.estimate(ROLE_A, ROLE_B)}


# --------------------------------------------------------------------------
# The fourth fixture: every form the fourth specimen shows (DEC-655)
# --------------------------------------------------------------------------

PACKET_4 = pad("MARK-ADDAX PROJ-aaaa [P1][in_progress] - the fixture's ticket, as the kernel's hook gives it")
GOV4_1 = pad("MARK-ORIBI usage: gov readiness [-h] [--json] [--root <path>]\n4.2.0\nREADME.md\nsrc\nOK")
GOV4_2 = pad("MARK-KUDU {\"ok\": false, \"command\": \"readiness\", \"result\": {}}\ncontract\nkernel")
GOV4_3 = pad("MARK-GERENUK {\n    \"ok\": false,\n    \"command\": \"readiness\",\n    \"result\": {}\n}")
GOV4_4 = pad("MARK-DIKDIK {\"ok\": false, \"command\": \"readiness\"}\nexit=1\nChange is valid\nexit=0")
HOOK_DENY_4 = hook_denial_text("MARK-SITATUNGA the call reads a file that is refused to every role")
FILE_4 = "MARK-TOPI ---\nid: PROJ-aaaa\nstatus: in_progress\n---\n# the ticket, read with the Read tool\n"
FOUND_4 = "src/example/a.py:1:VALUE = 1  # MARK-BONTEBOK"
WRITTEN_4 = "MARK-NYALA # the record the session wrote\n\nrows:\n  - id: R-01\n    gap_ticket: null\n"
RETURN_4 = "MARK-GECKO # Return: the record is committed; nine rows are open"
ROOT_4 = "/work/project"
NODE_4 = "PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
# The attachment lines of the fourth specimen that are no hook's, by their type, in its order: those after
# SessionStart's two lines, those after the first prompt, and those between later turns.
ATTACHMENTS_4_START = ("sandbox_instructions", "environment", "model", "deferred_tools_delta",
                       "agent_listing_delta", "mcp_instructions_delta", "skill_listing")
ATTACHMENTS_4_PROMPT = ("instructions", "session_context", "date", "credential_org", "remote_session_change",
                        "prompt_snapshot")
ATTACHMENTS_4_LATER = ("environment", "silent_turn_reminder", "deferred_tools_record")
# The four ``gov`` commands of the fourth specimen: each behind a ``cd`` the harness kept, beside other
# commands; three of them through a pipe.
GOV4_COMMANDS = (
    f"cd {ROOT_4}; gov readiness --help 2>&1 | head -40; {NODE_4} openspec --version 2>&1 | head -5; ls; "
    "cd python && python3 -m unittest example.tests.test_a 2>&1 | tail -5",
    f"cd {ROOT_4}; gov readiness --specification MARK-KAKAPO --json 2>&1 | head -60; "
    f"ls governance governance/contract | head -40; {NODE_4} openspec new change --help 2>&1 | head -20",
    f"cd {ROOT_4}; gov readiness --specification MARK-KAKAPO --json 2>&1 | python3 -m json.tool",
    f"cd {ROOT_4}; gov readiness --specification MARK-KAKAPO --json; echo \"exit=$?\"; "
    f"{NODE_4} openspec validate a-change --strict; echo \"exit=$?\"")
# Its commands that do not run ``gov``: a list of commands, a loop behind a ``cd``, a program behind a
# ``cd`` and ``&&``, a commit whose message and trailers hold words of the governance.
OTHER4_COMMANDS = (
    "printenv GOV_ROLE GOV_TICKET; git rev-parse --show-toplevel --abbrev-ref HEAD",
    "git show --stat HEAD; ls -la src/gov src/gov/* 2>&1 | head -80",
    f"cd {ROOT_4}; for f in src/gov/a.py src/gov/cli/main.py docs/gov.md; do echo \"=== $f\"; cat -n $f; done",
    f"cd {ROOT_4}/python && python3 -B -c \"\nfrom example.a import *\nprint(VALUE, 'MARK-DUGONG gov status')\n\"",
    f"cd {ROOT_4}; git add docs && git status --short && git commit -m \"MARK-DUGONG the record of gov "
    "readiness\" --trailer \"Task: PROJ-aaaa\" --trailer \"Role: product-spec\" 2>&1 | tail -15; "
    "git log -1 --stat --format='%H%n%B'")
DENIED4_COMMAND = (f"cd {ROOT_4}; cat -n .github/workflows/ci.yml tests/ci.yaml; "
                   "grep -rn \"MARK-DUGONG\" . --exclude-dir=governance -l 2>/dev/null | head")
API_DURATION_4 = 330000


def fourth_session(session, *, cwd=ROOT_4, version=VERSION_4, packet=PACKET_4, results=None, denial=HOOK_DENY_4):
    """One session in the fourth specimen's forms, in its order, not yet written. ``results`` are the
    results of its four ``gov`` commands.

    SessionStart's run and the packet it added; the brief, one text given through the SDK; attachment lines
    that are no hook's, a ``file-history-snapshot`` line and the lines between turns, each by its type; a
    first message of one line, a command; a message of a ``thinking`` line and three calls (two Read, one
    Bash), each call's result line right after its call; a message of two calls without a ``thinking``
    line (a loop behind a ``cd`` the harness kept, a Read); a message with a Grep and a ``gov`` command
    behind a ``cd``, beside other commands and through a pipe; a message of a text line and a ``gov``
    command; a command a PreToolUse hook denies by its answer; ``file-history-delta`` lines; Write and
    Grep; a message of ``thinking``, a text, a Write and a ``gov`` command through a pipe; a message of
    three Edit calls (logged with a key the model did not send); a program behind ``cd`` and ``&&``; a
    Write, an Edit and the fourth ``gov`` command in one message; a commit, whose result line notes it; a
    last message of one text line; the ``system`` line of a Stop hook that printed nothing, with no run
    line; a totals line that names a model no assistant line carries. No PreToolUse and no PostToolUse
    line: the kernel's hooks printed nothing. No sub-agent. Every assistant line carries ``effort`` and
    ``advisorModel``."""
    results = results or (GOV4_1, GOV4_2, GOV4_3, GOV4_4)
    path = f"{cwd}/docs/record.yaml"
    log = Log(session, cwd=cwd, version=version)
    log.effort, log.totals_model = "high", OTHER_MODEL
    log.hook("SessionStart", packet, name="SessionStart:startup", command=HOOK_COMMAND_4.format("sessionstart.py"))
    log.brief("MARK-WOMBAT # Brief: a worker of the fixture\n\nDo the work of the ticket.")
    log.mark(*ATTACHMENTS_4_START).bare("file-history-snapshot", sessionId=None)
    log.bare("atis-latch")
    log.mark(*ATTACHMENTS_4_PROMPT).marks()
    log.turn((2, 125, 47000, 0), [bash_step(OTHER4_COMMANDS[0], OTHER_OUT)], thinking=False)
    log.mark("prompt_snapshot").marks()
    log.turn((2, 880, 230, 47000), [read_step(f"{cwd}/.tickets/{TICKET}.md", FILE_4),
                                    read_step(f"{cwd}/governance/kernel/skills/discovery/SKILL.md", FILE_4),
                                    bash_step(OTHER4_COMMANDS[1], OTHER_OUT)])
    log.marks()
    log.turn((2, 650, 6100, 47200), [bash_step(OTHER4_COMMANDS[2], OTHER_OUT),
                                     read_step(f"{cwd}/README.md", FILE_4)], thinking=False)
    log.marks()
    log.turn((2, 760, 14100, 53300), [grep_step("(?i)MARK-DUGONG|gov status", FOUND_4),
                                      bash_step(GOV4_COMMANDS[0], results[0])])
    log.mark("environment", "environment", "silent_turn_reminder").marks()
    log.turn((2, 400, 3900, 67400), [bash_step(GOV4_COMMANDS[1], results[1])], thinking=False,
             preface="MARK-GECKO the readiness command is there; I ask it about the record")
    log.marks()
    log.turn((2, 5900, 650, 71300), [denied_step(DENIED4_COMMAND, denial)])
    log.marks().file_history()
    log.turn((2, 2400, 4500, 71900), [write_step(path, WRITTEN_4), grep_step("MARK-DUGONG", FOUND_4)])
    log.mark("silent_turn_reminder").marks().file_history()
    log.turn((2, 3700, 2700, 76400), [write_step(f"{cwd}/docs/proposal.md", WRITTEN_4),
                                      bash_step(GOV4_COMMANDS[2], results[2])],
             preface="MARK-GECKO the record is written; I ask the command again")
    log.marks()
    log.turn((2, 2500, 4700, 79100), [edit_step(path, "gap_ticket: null", f"gap_ticket: MARK-{number}", WRITTEN_4)
                                      for number in range(3)])
    log.marks().mark("deferred_tools_record")
    log.turn((2, 1800, 3900, 83800), [bash_step(OTHER4_COMMANDS[3], OTHER_OUT)])
    log.mark("environment").file_history(4)
    log.turn((2, 11600, 2200, 87700), [write_step(f"{cwd}/docs/design.md", WRITTEN_4),
                                       edit_step(path, "id: R-01", "id: R-02", WRITTEN_4),
                                       bash_step(GOV4_COMMANDS[3], results[3])])
    log.marks().mark("environment", "deferred_tools_record")
    log.turn((2, 630, 13200, 89900), [bash_step(OTHER4_COMMANDS[4], OTHER_OUT, committed="11308f8")])
    log.say((2, 4000, 1500, 103100), RETURN_4, thinking=False).quiet_stop()
    log.api_duration = API_DURATION_4
    return log


def fourth_logs(version=VERSION_4):
    """The logs of the fourth fixture, not yet written, as Claude Code ``version`` wrote them. The first
    session is in the fourth specimen's forms (``fourth_session``). The second is in the first specimen's
    forms, at the same version. The third is other work in the fourth specimen's forms, written by yet
    another version: nothing of it is the ticket's, its version neither."""
    first = fourth_session(SESSION_A, version=version)
    second = Log(SESSION_B, version=version).session_start(PACKET_B).prompt()
    second.bash(gov_command("doctor"), GOV_3, (400, 100, 500, 0), hook=HOOK_3).say((30, 20, 0, 0))
    second.api_duration = API_DURATION_B
    other = fourth_session(SESSION_OTHER, cwd="/work/other", version="2.1.290", packet=PACKET_OTHER,
                           results=(GOV_OTHER,) * 4, denial=hook_denial_text(HOOK_OTHER))
    return first, second, other


def fourth_fixture(project, logs, *, version=VERSION_4, change=None):
    """A ticket of which every source can be measured or estimated, with a session in the fourth specimen's
    forms, written by Claude Code ``version``. Returns what the case computes itself: ``counts`` (each
    measured source: the packet of each session; the hook's denial and the second session's added context;
    the four ``gov`` results of the first session, each whole, and the second session's), ``notes`` (one
    hook text by the larger reading: the denial; four ``gov`` results counted whole), ``usage``,
    ``latency``, ``estimate`` (the two sessions named with their roles, ``ROLED``) and ``version``."""
    first, second, other = fourth_logs(version)
    if change:
        change(first, second)
    for log in (first, second, other):
        log.write(logs)
    counts = {"sessionstart_packet": tokens(PACKET_4) + tokens(PACKET_B),
              "hook_output": tokens(HOOK_DENY_4) + tokens(HOOK_3),
              "gov_output": sum(tokens(text) for text in (GOV4_1, GOV4_2, GOV4_3, GOV4_4, GOV_3)),
              "checkpoint_records": project.add_checkpoint(1), "close_records": project.add_close()}
    project.add_instructions()
    project.commit("governance files", "Role: orchestrator")
    usage = tuple(a + b for a, b in zip(first.usage(), second.usage()))
    return {"counts": counts, "usage": usage, "logs": (first, second, other), "version": version,
            "notes": {LARGER_READING: 1, COUNTED_WHOLE: 4}, "latency": API_DURATION_4 + API_DURATION_B,
            "estimate": project.estimate(ROLE_A, ROLE_B)}


def agent(result):
    """The record's ``agent``: a map with exactly the harness and the Claude Code version that was read
    (DEC-501, DEC-655)."""
    said = result.get("agent")
    assert isinstance(said, dict) and sorted(said) == ["harness", "version"], \
        f"agent is {said!r}: a map with exactly the harness and the version that was read"
    assert said["harness"] == HARNESS, said
    return said["version"]


# --------------------------------------------------------------------------
# Running the command
# --------------------------------------------------------------------------

def run_env(sandbox, logs, path):
    env = {"PATH": path, "HOME": str(sandbox.home), "TMPDIR": str(sandbox.tmpdir), "LC_ALL": "C.UTF-8",
           "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(sandbox.pycache), **GIT_ENV}
    if logs is not None:
        env["CLAUDE_CONFIG_DIR"] = str(logs)
    if site.ENABLE_USER_SITE:  # the installed packages of the interpreter running the suite (as W1-30 does)
        env["PYTHONUSERBASE"] = site.getuserbase()
    return env


def run_telemetry(project, sandbox, logs, *sessions, ticket=TICKET, path=None, as_json=True):
    """``gov telemetry <ticket> --json [--ticket-session <id>]...`` in the project, with ``logs`` as the
    session logs. ``path`` replaces ``PATH`` (the cases about an absent or failing ccusage give it)."""
    if path is None:
        folder = ccusage_dir()
        path = f"{folder}:{SYSTEM_PATH}" if folder else SYSTEM_PATH
    args = [COMMAND, ticket] + (["--json"] if as_json else [])
    for session in sessions:
        args += ["--ticket-session", session]
    launcher = cli_support.write_launcher(REPO_ROOT, sandbox)
    started = time.perf_counter()
    done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(getattr(project, "root", project)),
                          env=run_env(sandbox, logs, path), capture_output=True, text=True,
                          timeout=120, stdin=subprocess.DEVNULL)
    return cli_support.Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def fake_ccusage(sandbox, script):
    """Put ``script`` in place of ccusage and return the ``PATH`` that finds it first."""
    fake = sandbox.bin / "ccusage"
    fake.write_text(script, encoding="utf-8")
    fake.chmod(fake.stat().st_mode | 0o100)
    return f"{sandbox.bin}:{SYSTEM_PATH}"


# --------------------------------------------------------------------------
# Reading the answer
# --------------------------------------------------------------------------

def is_count(value):
    return type(value) is int and value >= 0


def is_number(value):
    return type(value) in (int, float) and value >= 0


def record(run):
    """The result of a run that answered with its record: exit code 0 (every part of the share is a number) or
    3 (a part is "not measured"), ``ok: true``."""
    envelope = run.envelope()
    assert run.returncode in (EXIT_OK, EXIT_NOT_MEASURED) and envelope.get("ok") is True, \
        f"gov telemetry gave no record\n{run.describe()}"
    assert envelope.get("command") == COMMAND, run.describe()
    result = envelope["result"]
    assert isinstance(result, dict) and result, f"the record is empty\n{run.describe()}"
    return result


def share(result, part):
    """One of the three share figures of the record, each named: ``measured``, ``estimated``, ``total``."""
    figures = result.get("governance_share")
    assert isinstance(figures, dict) and sorted(figures) == sorted(SHARE_PARTS), \
        f"governance_share is {figures!r}: it names its measured part, its estimated part and their sum"
    return figures[part]


def estimate(result):
    """The line of the static estimate (DEC-495), a map with its label, its method, its files, the two
    estimated sources and their sum."""
    line = result.get("estimated_governance_tokens")
    assert isinstance(line, dict) and sorted(line) == sorted(ESTIMATE_KEYS), \
        f"estimated_governance_tokens is {line!r}: the estimate is a line of its own with {ESTIMATE_KEYS}"
    return line


def models(result):
    """The record's ``model``: the session logs' and the commits', each named."""
    model = result.get("model")
    assert isinstance(model, dict) and sorted(model) == ["commits", "session_logs"], \
        f"model is {model!r}: it is reported from the session logs and from the commits, each named"
    return model


def reasons(result):
    """``not_measured`` of the record as ``{source: reason}``: one entry per source that was not measured,
    with the name of the source and the reason, a text that is not empty."""
    listed = result.get("not_measured")
    assert isinstance(listed, list), f"not_measured is {listed!r}"
    for entry in listed:
        assert isinstance(entry, dict) and isinstance(entry.get("name"), str) \
            and isinstance(entry.get("reason"), str) and entry["reason"].strip(), \
            f"an entry of not_measured names its source and its reason: {entry!r}"
    return {entry["name"]: entry["reason"] for entry in listed}


def notes(result):
    """The record's two counting notes (DEC-501): how many hook texts were counted by the larger reading, and
    how many ``gov`` results were counted whole. Counts, never content."""
    said = result.get(NOTES)
    assert isinstance(said, dict) and sorted(said) == sorted((LARGER_READING, COUNTED_WHOLE)), \
        f"{NOTES} is {said!r}: a map with exactly {LARGER_READING} and {COUNTED_WHOLE}"
    assert all(is_count(value) for value in said.values()), f"{NOTES} holds counts: {said!r}"
    return said


def gaps(result):
    """The record's known gaps as ``{name: reason}``: what the counter cannot count, each with a reason that
    is not empty. They are no entries of ``not_measured``."""
    listed = result.get(KNOWN_GAPS)
    assert isinstance(listed, list) and all(
        isinstance(entry, dict) and sorted(entry) == ["name", "reason"] and isinstance(entry["name"], str)
        and isinstance(entry["reason"], str) and entry["reason"].strip() for entry in listed), \
        f"{KNOWN_GAPS} is {listed!r}: a list of entries with a name and a reason"
    return {entry["name"]: entry["reason"] for entry in listed}


def latency(result):
    """The record's latency: a map with exactly the harness's summed API duration, in milliseconds."""
    said = result.get("latency")
    assert isinstance(said, dict) and list(said) == [API_DURATION], \
        f"latency is {said!r}: a map with exactly {API_DURATION}"
    return said[API_DURATION]


def refusal(run):
    """The run refused: exit code 1, ``ok: false``, a code, no record. Returns the error."""
    envelope = run.envelope()
    assert run.returncode == EXIT_GOV_ERROR and envelope.get("ok") is False, \
        f"gov telemetry must refuse here\n{run.describe()}"
    assert envelope.get("error", {}).get("code"), f"a refusal names its code\n{run.describe()}"
    assert not envelope.get("result"), f"a refusal carries no record\n{run.describe()}"
    return envelope["error"]


def assert_no_figure(run):
    """The run did not succeed and gave no share, token count or cost as a number."""
    assert run.returncode not in (EXIT_OK, EXIT_USAGE), \
        f"gov telemetry must not succeed here, and this is no usage error\n{run.describe()}"
    envelope = run.envelope()
    if envelope.get("ok") is False:
        return refusal(run)
    result = envelope["result"]
    assert run.returncode == EXIT_NOT_MEASURED, run.describe()
    for name in ("tokens_in", "tokens_out", "cache_read_tokens", "cache_creation_tokens", "cost"):
        assert result.get(name) == NOT_MEASURED, \
            f"{name} is {result.get(name)!r}: it was not measured and must say so\n{run.describe()}"
    for part in SHARE_PARTS:
        assert share(result, part) == NOT_MEASURED, \
            f"the {part} share is {share(result, part)!r}: there is no denominator\n{run.describe()}"
    assert result["learning_metrics"]["governance_share"] == result["governance_share"], run.describe()
    return result
