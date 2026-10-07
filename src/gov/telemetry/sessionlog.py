"""What the counter reads from the harness's session log of one session (W1-31, DEC-495).

The form is the one of the specimen, written by Claude Code 2.1.288, and nothing else: a log of another
version is refused, and whatever a log holds that the specimen does not show makes the source it concerns
"not measured", with the reason named. **Counts only, never content**: no text of a log line reaches a
count's reason or a refusal, the Claude Code version excepted.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

from gov.cli.errors import GovError
from gov.context import _tokens

VERSION = "2.1.288"
LOG_SOURCES = ("sessionstart_packet", "hook_output", "gov_output")
HOOK_SOURCES = {"SessionStart": "sessionstart_packet", "PostToolUse": "hook_output"}  # the specimen's two events
# The harness's other hook events: named in a reason, never measured (AD-6: with or without added context).
OTHER_EVENTS = ("PreToolUse", "UserPromptSubmit", "Stop", "SubagentStop", "PreCompact", "SessionEnd", "Notification")
LINE_TYPES = frozenset({"queue-operation", "attachment", "user", "assistant", "file-history-snapshot", "atis-latch",
                        "last-prompt", "ai-title", "cost-state"})
# The specimen's attachment lines that are no hook's: passed over.
ATTACHMENTS = frozenset({"environment", "model", "deferred_tools_delta", "agent_listing_delta", "skill_listing",
                         "total_tokens_reminder", "session_context", "date", "credential_org",
                         "remote_session_change", "prompt_snapshot", "mcp_instructions_delta",
                         "deferred_tools_record"})
USAGE = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)
OPERATORS = frozenset("();<>|&")
# AD-2: programs that run another program. ``gov`` behind one of them is "not measured", as is ``gov`` by a path.
RUNNERS = ("uv", "uvx", "pipx", "poetry", "hatch", "env", "exec", "command", "time", "timeout", "nohup", "sudo",
           "xargs")


def find(config: Path, session: str) -> Path:
    """The one log of ``session`` under ``<config>/projects/``. Refuses without exactly one."""
    found = []
    if SESSION_ID.fullmatch(session):
        try:
            found = [folder / f"{session}.jsonl" for folder in sorted((Path(config) / "projects").iterdir())
                     if (folder / f"{session}.jsonl").is_file()]
        except OSError:
            found = []
    if len(found) != 1:
        raise GovError("SESSION_LOG_MISSING", f"there is not exactly one session log of {session} in the harness's "
                       "log folder: the session was not measured", {"session": session, "logs": len(found)})
    return found[0]


def gov_command(command):
    """Whether a Bash command runs ``gov``: True for one simple command in one of the two known forms
    (``gov ...`` and the specimen's ``python3 -m gov.cli.main ...``, each after ``NAME=value`` assignments),
    False for a command that does not run it, and the reason, a text, where that cannot be told."""
    if not isinstance(command, str):
        return "a Bash call without a command text"
    lexer = shlex.shlex(command.strip().replace("\n", ";"), posix=True, punctuation_chars=True)
    lexer.whitespace_split, lexer.commenters = True, ""
    try:
        words = list(lexer)
    except ValueError:
        return "a Bash command whose words cannot be told apart"
    parts, found = [[]], False
    for word in words:
        if set(word) <= OPERATORS:
            parts.append([])
        else:
            parts[-1].append(word)
    for part in parts:
        while part and ASSIGNMENT.fullmatch(part[0]):
            part = part[1:]
        if not part:
            continue
        if part[0] == "gov" or part[:3] == ["python3", "-m", "gov.cli.main"]:
            found = True
        # AD-2, awaiting decision: by a path, as a module of another interpreter, through another runner.
        elif (("/" in part[0] and part[0].rsplit("/", 1)[-1] == "gov")
              or any(part[at:at + 2] == ["-m", "gov.cli.main"] for at in range(len(part)))
              or (part[0] in RUNNERS and any(word.rsplit("/", 1)[-1] == "gov" for word in part[1:]))):
            return "gov called by a path or through another runner, a form the specimen does not show"
    if found and len(parts) > 1:  # AD-2: also a compound command in which every part runs gov, and a redirection
        return "gov inside a compound command or with a redirection: its one result cannot be told apart"
    return found


def read(path: Path, session: str) -> dict:
    """The log ``path`` of ``session``: ``usage`` (fresh input, output, cache creation and cache reads of the
    assistant lines, each message once), ``models`` (those lines' models), ``counts`` (the tokens of the three
    log sources) and ``missing`` (``{source: [reasons]}`` for a source that is not measured, whose count is
    then void). Refuses a log it cannot read, of another version, or whose lines are of another form."""
    def refuse(what, code="SESSION_LOG_FORM"):
        raise GovError(code, f"the log of session {session} is not in the form of Claude Code {VERSION} "
                       f"({what}): the session was not measured", {"session": session})

    missing: dict[str, list] = {}

    def not_measured(sources, reason):
        for source in sources:
            if reason not in missing.setdefault(source, []):
                missing[source].append(reason)

    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        refuse("it cannot be read", "SESSION_LOG_UNREADABLE")
    usage, models, counts = {}, [], dict.fromkeys(LOG_SOURCES, 0)
    calls, results = [], {}
    for number, raw in enumerate(lines, 1):
        try:
            line = json.loads(raw)
        except ValueError:
            line = None
        if not isinstance(line, dict):
            refuse(f"line {number} is no JSON object")
        kind, attachment = line.get("type"), line.get("attachment")
        passed_over = kind == "attachment" and isinstance(attachment, dict) and attachment.get("type") in ATTACHMENTS
        if line.get("sessionId") not in (None, session):
            refuse(f"line {number} is of another session")
        if "version" in line or (kind in ("attachment", "user", "assistant") and not passed_over):
            version = line.get("version")
            if version != VERSION:
                named = version if isinstance(version, str) and re.fullmatch(r"\d+(\.\d+){1,3}", version) else None
                refuse(f"line {number} is of version {named}" if named else f"line {number} names no version",
                       "SESSION_LOG_VERSION")
        own = line.get("isSidechain") is False  # the session's own line, as every line of the specimen is
        if kind not in LINE_TYPES:
            not_measured(LOG_SOURCES, "a log line of a type the specimen does not show")
        elif kind == "attachment" and not passed_over:
            if not isinstance(attachment, dict):
                refuse(f"line {number} has no attachment")
            event = attachment.get("hookEvent")
            source = HOOK_SOURCES.get(event) if isinstance(event, str) else None
            sources = (source or "hook_output",) if isinstance(event, str) else LOG_SOURCES[:2]
            content = attachment.get("content")
            if source is None:  # AD-6: an event the specimen does not show, whether or not it added context
                not_measured(sources, f"a hook line of the event {event}, which the specimen does not show"
                             if event in OTHER_EVENTS else "an attachment line of a type the specimen does not show")
            elif not own:
                not_measured(sources, "a hook line of a sub-agent")
            elif attachment.get("type") == "hook_success":
                if attachment.get("exitCode") != 0:
                    not_measured(sources, "a hook run that did not end with exit code 0")
            elif attachment.get("type") != "hook_additional_context":
                not_measured(sources, "a hook run of a type the specimen does not show")
            elif isinstance(content, list) and all(isinstance(text, str) for text in content):
                counts[source] += sum(_tokens(text) for text in content)
            else:
                not_measured(sources, "context added by a hook in a form the specimen does not show")
        elif kind in ("user", "assistant"):
            message = line.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if kind == "user":
                if not isinstance(content, (str, list)):
                    refuse(f"line {number} has no message content")
                for block in content if isinstance(content, list) else ():
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        results.setdefault(block.get("tool_use_id"), []).append(
                            (block.get("content"), block.get("is_error"), own))
                continue
            figures = message.get("usage") if isinstance(message, dict) else None
            if (not isinstance(content, list) or not isinstance(figures, dict)
                    or not isinstance(message.get("id"), str) or not isinstance(message.get("model"), str)
                    or any(type(figures.get(key)) is not int or figures[key] < 0 for key in USAGE)):
                refuse(f"line {number} is no message of the model with its usage")
            usage.setdefault((message["id"], line.get("requestId")), tuple(figures[key] for key in USAGE))
            if message["model"] not in models:
                models.append(message["model"])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Bash":
                    tool_input = block.get("input")
                    runs = gov_command(tool_input.get("command") if isinstance(tool_input, dict) else None)
                    if runs is True and own:
                        calls.append(block.get("id"))
                    elif runs:
                        not_measured(("gov_output",), "a gov command in a sub-agent's lines" if runs is True else runs)
    for call in calls:
        found = results.get(call, []) if isinstance(call, str) else []
        if len(found) != 1:
            not_measured(("gov_output",), "a gov command without its one result")
        elif not isinstance(found[0][0], str) or not found[0][2]:
            not_measured(("gov_output",), "the result of a gov command in a form the specimen does not show")
        elif found[0][1] is not False:  # AD-2: a result marked as an error (every refusal of gov) awaits decision
            not_measured(("gov_output",), "a gov command whose result is marked as an error")
        else:
            counts["gov_output"] += _tokens(found[0][0])
    return {"usage": tuple(sum(each[at] for each in usage.values()) for at in range(len(USAGE))),
            "models": models, "counts": counts, "missing": missing}
