"""What the counter reads from the harness's session log of one session (W1-31, DEC-495, DEC-501, DEC-502).

The forms are those of the three specimens, written by Claude Code 2.1.288, and nothing else: a log of another
version is refused, and whatever a log holds that no specimen shows makes the source it concerns
"not measured", with the reason named. A sub-agent's file belongs to the session (DEC-501). **Counts only,
never content**: no text of a log line reaches a count's reason or a refusal, the Claude Code version excepted.
"""

from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path

from gov.cli.errors import GovError
from gov.context import _tokens

VERSION = "2.1.288"
LOG_SOURCES = PACKET, HOOKS, GOV = ("sessionstart_packet", "hook_output", "gov_output")
# DEC-501: what was counted although it over-counts. Counts of texts, beside the counts of tokens.
NOTES = LARGER, WHOLE = ("larger_reading_hook_texts", "gov_results_counted_whole")
LINE_TYPES = frozenset({"queue-operation", "attachment", "user", "assistant", "file-history-snapshot", "atis-latch",
                        "last-prompt", "ai-title", "cost-state", "system", "mode"})
FULL = ("attachment", "user", "assistant", "system")  # the lines that carry the version and the side-chain mark
SYSTEM = ("stop_hook_summary", "compact_boundary")
# The specimens' attachment lines that are no hook's: passed over.
ATTACHMENTS = frozenset({"environment", "model", "deferred_tools_delta", "agent_listing_delta", "skill_listing",
                         "total_tokens_reminder", "session_context", "date", "credential_org",
                         "remote_session_change", "prompt_snapshot", "mcp_instructions_delta",
                         "deferred_tools_record"})
HOOK_LINES = ("hook_success", "hook_additional_context", "hook_non_blocking_error")
# How the result of a call begins that a PreToolUse hook blocked or denied by its answer (DEC-501, DEC-502).
HOOK_DENIAL = re.compile(r"PreToolUse:\w+ hook error: ")
# The result of a call a permission rule denied: nothing is counted for it (DEC-502). Not decided (package E):
# the specimen shows the sentence for Bash only, so a rule's denial of another tool is "not measured".
RULE_DENIAL = re.compile(r"Permission to use Bash with command .* has been denied\.", re.DOTALL)
FEEDBACK = "Stop hook feedback:\n"  # the heading of the feedback line of a blocking Stop or SubagentStop hook
CAVEAT = "<local-command-caveat>"   # the specimens' other line the harness writes as a user's (``isMeta``)
USAGE = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*")
# DEC-502: beside its sub-agents' logs a session's folder may hold the full texts of its over-long results,
# which are passed over by name: a result is counted as logged. Anything else was read by nobody.
SUBAGENTS, SESSION_FOLDER = "subagents", frozenset({"subagents", "tool-results"})
SUBAGENT_FILE = re.compile(r"agent-[A-Za-z0-9]+\.(jsonl|meta\.json)")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)
OPERATORS = frozenset("();<>|&")
MODULE = ["-m", "gov.cli.main"]
# DEC-502: programs that run another program. ``gov`` behind one of them is "not measured".
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


def subagent_files(path: Path, session: str) -> list:
    """The logs of the session's sub-agents (DEC-501): ``<session id>/subagents/agent-<agent id>.jsonl`` beside
    the session's own file ``path``, each with its ``.meta.json``. None where the session has no folder; refuses
    a folder that cannot be listed or holds anything else than these and ``tool-results`` (DEC-502), which
    nobody read."""
    folder = path.with_suffix("")
    if not os.path.lexists(folder):
        return []
    try:
        held = os.listdir(folder)
        names = sorted(os.listdir(folder / SUBAGENTS)) if SUBAGENTS in held else []
    except OSError:
        held, names = [], None
    if names is None or not SESSION_FOLDER.issuperset(held) or not all(SUBAGENT_FILE.fullmatch(name)
                                                                       for name in names):
        raise GovError("SESSION_LOG_FORM", f"the folder of session {session} holds something else than its "
                       f"sub-agents' logs as Claude Code {VERSION} keeps them: the session was not measured",
                       {"session": session})
    return [folder / SUBAGENTS / name for name in names if name.endswith(".jsonl")]


def gov_command(command):
    """Whether a Bash command runs ``gov``: ``(runs, beside)``, or the reason, a text, where that cannot be told.
    It runs ``gov`` when one of its simple commands has, after ``NAME=value`` assignments, a command word
    whose last path component is ``gov``, or is ``python3 -m gov.cli.main ...`` (DEC-502); ``beside`` when it
    then holds another command, a pipe or a redirection, so that its one result is counted whole (DEC-501)."""
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
        if part[0].rsplit("/", 1)[-1] == "gov" or part[:3] == ["python3", *MODULE]:
            found = True
        # Not decided (package A): an interpreter word other than ``python3`` (another name, a path).
        elif part[1:3] == MODULE:
            return "gov as a module of an interpreter word other than python3, a form the specimens do not show"
        elif (any(part[at:at + 2] == MODULE for at in range(len(part)))
              or (part[0] in RUNNERS and any(word.rsplit("/", 1)[-1] == "gov" for word in part[1:]))):
            return "gov through another runner, a form the specimens do not show"
    return found, found and len(parts) > 1


def read(path: Path, session: str) -> dict:
    """The log ``path`` of ``session`` and the logs of its sub-agents: ``usage`` (fresh input, output, cache
    creation and cache reads of the assistant lines, each message once, with the figures of its last line),
    ``models`` (those lines' models), ``counts`` (the tokens of the three log sources), ``notes`` (how many
    texts were counted by the larger reading, how many ``gov`` results whole), ``missing`` (``{source:
    [reasons]}`` for a source that is not measured, whose count is then void), ``duration`` (``totalAPIDuration``
    of the last totals line of the session's own file; None without one) and ``versioned`` (whether a line
    named the version). Refuses a log it cannot read, of another version, or whose lines are of another form."""
    def refuse(what, code="SESSION_LOG_FORM"):
        raise GovError(code, f"the log of session {session} is not in the form of Claude Code {VERSION} "
                       f"({what}): the session was not measured", {"session": session})

    missing: dict[str, list] = {}

    def not_measured(sources, reason):
        for source in sources:
            if reason not in missing.setdefault(source, []):
                missing[source].append(reason)

    usage, models, counts, notes = {}, [], dict.fromkeys(LOG_SOURCES, 0), dict.fromkeys(NOTES, 0)
    duration, versioned = None, False
    start = set()  # what the SessionStart hook lines that follow one another gave: plain output, added context

    def hook(attachment):
        """Count a hook line: what it added goes to the packet for SessionStart, to hook output otherwise."""
        form, event, content = attachment.get("type"), attachment.get("hookEvent"), attachment.get("content")
        source = PACKET if event == "SessionStart" else HOOKS
        sources = (source,) if isinstance(event, str) else (PACKET, HOOKS)
        texts = [attachment.get("stderr"), attachment.get("stdout")]
        if not isinstance(event, str) or form not in HOOK_LINES:
            not_measured(sources, "an attachment line of a type the specimens do not show")
        elif form == "hook_success":  # DEC-501: a run added nothing; what it added is the next line
            if attachment.get("exitCode") != 0:
                not_measured(sources, "a hook run that did not end with exit code 0")
            elif source == PACKET and content != "":  # DEC-502: SessionStart's plain output is given to the session
                # Not decided (package D): ``content`` is counted, the field the specimen's line shows as what
                # was rendered to the session; its ``stdout`` is the same text and a line end.
                if isinstance(content, str) and attachment.get("stdout") == content + "\n":
                    counts[PACKET] += _tokens(content)
                    notes[LARGER] += 1
                    start.add("plain output")
                else:
                    not_measured(sources, "a SessionStart run whose output is in a form the specimens do not show")
        elif form == "hook_additional_context":
            if isinstance(content, list) and all(isinstance(text, str) for text in content):
                counts[source] += sum(_tokens(text) for text in content)
                start.update(["added context"] if source == PACKET else [])
            else:
                not_measured(sources, "context added by a hook in a form the specimens do not show")
        elif all(isinstance(text, str) for text in texts):  # DEC-501, DEC-502: the larger reading, SessionStart's too
            counts[HOOKS] += sum(_tokens(text) for text in texts)
            notes[LARGER] += 1
        else:
            not_measured((HOOKS,), "the line of a failing hook in a form the specimens do not show")
        # Not decided (package B): one start with plain output and with added context, which no specimen shows.
        if source == PACKET and len(start) == 2:
            not_measured((PACKET,), "SessionStart hooks that gave plain output and added context at one start, "
                         "which the specimens do not show")

    for file in (path, *subagent_files(path, session)):
        side = file != path
        where = "a sub-agent's file, line" if side else "line"
        try:
            lines = Path(file).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            refuse("a sub-agent's file cannot be read" if side else "it cannot be read", "SESSION_LOG_UNREADABLE")
        calls, results, denied, totals = [], {}, set(), None
        feedback = None  # the text of a blocking Stop hook's feedback line, which the next line repeats
        start.clear()
        for number, raw in enumerate(lines, 1):
            try:
                line = json.loads(raw)
            except ValueError:
                line = None
            if not isinstance(line, dict):
                refuse(f"{where} {number} is no JSON object")
            kind, attachment = line.get("type"), line.get("attachment")
            if not (kind == "attachment" and isinstance(attachment, dict)
                    and attachment.get("hookEvent") == "SessionStart"):
                start.clear()
            repeated, feedback = feedback, None
            if repeated is not None and (kind, line.get("subtype")) != ("system", SYSTEM[0]):
                not_measured((HOOKS,), "the feedback of a blocking Stop hook without the line the specimen shows "
                             "after it")
            passed_over = (kind == "attachment" and isinstance(attachment, dict)
                           and attachment.get("type") in ATTACHMENTS)
            full = kind in FULL and not passed_over
            if line.get("sessionId") not in (None, session):
                refuse(f"{where} {number} is of another session")
            if "version" in line or full:
                version = line.get("version")
                if version != VERSION:
                    named = version if isinstance(version, str) and re.fullmatch(r"\d+(\.\d+){1,3}", version) else None
                    refuse(f"{where} {number} is of version {named}" if named else f"{where} {number} names no version",
                           "SESSION_LOG_VERSION")
                versioned = True
            if full and line.get("isSidechain") is not side:  # the session's own lines are not, a sub-agent's are
                not_measured(LOG_SOURCES, "a line whose side-chain mark is not the one of its file")
            if kind not in LINE_TYPES:
                not_measured(LOG_SOURCES, "a log line of a type the specimens do not show")
            elif kind == "cost-state":
                totals = line.get("totalAPIDuration")
            elif kind == "system":
                if line.get("subtype") not in SYSTEM:
                    not_measured(LOG_SOURCES, "a system line of a kind the specimens do not show")
                # DEC-502: after a hook that blocked, the line repeats the feedback line's text, counted there.
                elif line.get("subtype") == SYSTEM[0] and not (
                        line.get("hookErrors") == ([] if repeated is None else [repeated])
                        and line.get("hookAdditionalContext") == [] and line.get("preventedContinuation") is False):
                    not_measured((HOOKS,), "a line after a Stop hook that carries added context, a refusal to stop, "
                                 "or an error that is not the text of a feedback line before it")
            elif kind == "attachment" and not passed_over:
                if not isinstance(attachment, dict):
                    refuse(f"{where} {number} has no attachment")
                hook(attachment)
            elif kind in ("user", "assistant"):
                message = line.get("message")
                content = message.get("content") if isinstance(message, dict) else None
                if kind == "user":
                    if not isinstance(content, (str, list)):
                        refuse(f"{where} {number} has no message content")
                    if isinstance(content, str):
                        # The specimens' text lines are prompts, notices, a summary and a local command's lines
                        # (the PreCompact gap), which carry no hook line's text, and the two forms below.
                        if content.startswith(FEEDBACK) and line.get("isMeta") is True:
                            # DEC-502: a Stop or SubagentStop hook blocked; its feedback is hook output, once.
                            counts[HOOKS] += _tokens(content)
                            notes[LARGER] += 1
                            feedback = None if side else content[len(FEEDBACK):]  # no line follows a sub-agent's
                        elif content.startswith(FEEDBACK) or (line.get("isMeta") and not content.startswith(CAVEAT)):
                            not_measured((HOOKS,), "a line the harness wrote for the session in a form the "
                                         "specimens do not show")
                        continue
                    for block in content:
                        if not isinstance(block, dict) or block.get("type") != "tool_result":
                            not_measured(LOG_SOURCES, "a user line with a block of a kind the specimens do not show")
                            continue
                        call, text = block.get("tool_use_id"), block.get("content")
                        call = call if isinstance(call, str) else None
                        if "toolDenialKind" not in line:
                            results.setdefault(call, []).append(block)
                            continue
                        # The call never ran. DEC-501, DEC-502: blocked by a hook or denied by its answer, the
                        # result is the hook's text; denied by a permission rule, it is nobody's and counts nothing.
                        denied.add(call)
                        known = (line["toolDenialKind"] == "permission-rule" and block.get("is_error") is True
                                 and isinstance(text, str))
                        if known and HOOK_DENIAL.match(text):
                            counts[HOOKS] += _tokens(text)
                            notes[LARGER] += 1
                        elif not (known and RULE_DENIAL.fullmatch(text)):
                            not_measured((HOOKS,), "a denied call whose result is in none of the forms the "
                                         "specimens show")
                    continue
                figures = message.get("usage") if isinstance(message, dict) else None
                if (not isinstance(content, list) or not isinstance(figures, dict)
                        or not isinstance(message.get("id"), str) or not isinstance(message.get("model"), str)
                        or any(type(figures.get(key)) is not int or figures[key] < 0 for key in USAGE)):
                    refuse(f"{where} {number} is no message of the model with its usage")
                # The lines of one message may differ (the specimen's sub-agent): the last line's, as ccusage takes.
                usage[(message["id"], str(line.get("requestId")))] = tuple(figures[key] for key in USAGE)
                if message["model"] not in models:
                    models.append(message["model"])
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Bash":
                        tool_input = block.get("input")
                        told = gov_command(tool_input.get("command") if isinstance(tool_input, dict) else None)
                        if isinstance(told, str):
                            not_measured((GOV,), told)
                        elif told[0]:
                            calls.append((block.get("id"), told[1]))
        for call, beside in calls:
            found = results.get(call, []) if isinstance(call, str) else []
            if isinstance(call, str) and call in denied:
                continue  # it never ran: its result is a hook's, counted above once, or a rule's, which counts nothing
            if len(found) != 1:
                not_measured((GOV,), "a gov command without its one result")
            elif not isinstance(found[0].get("content"), str) or type(found[0].get("is_error")) is not bool:
                not_measured((GOV,), "the result of a gov command in a form the specimens do not show")
            else:  # DEC-501: marked as an error or not; whole where gov did not run alone
                counts[GOV] += _tokens(found[0]["content"])
                notes[WHOLE] += beside
        if feedback is not None:
            not_measured((HOOKS,), "the feedback of a blocking Stop hook without the line the specimen shows after it")
        if not side and type(totals) is int and totals >= 0:
            duration = totals
    return {"usage": tuple(sum(each[at] for each in usage.values()) for at in range(len(USAGE))),
            "models": models, "counts": counts, "notes": notes, "missing": missing, "duration": duration,
            "versioned": versioned}
