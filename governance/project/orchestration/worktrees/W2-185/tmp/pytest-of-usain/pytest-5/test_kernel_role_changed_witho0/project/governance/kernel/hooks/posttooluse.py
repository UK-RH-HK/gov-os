#!/usr/bin/env python3
"""
PostToolUse / PostToolUseFailure containment hook (W1-03).

After every Bash call, compares the repository state with the
before-snapshot taken by the PreToolUse hook (DEC-126) and:

- reports out-of-scope changes to the agent (KPI success 1);
- restores acceptance tests changed by a non-test-designer from
  HEAD (KPI success 2);
- records findings as JSON lines in .gov-runtime/findings.jsonl
  (DEC-122).

Exit codes:
- 0 with JSON on stdout  -> hookSpecificOutput.additionalContext
  reaches the agent
- 0 with no stdout       -> nothing reaches the agent (silent)
- 2 with stderr          -> stderr reaches the agent (internal error)
"""

from __future__ import annotations

import json
import os
import select
import sys
import time

STDIN_DEADLINE_S = 3.0
FINDINGS_REL = ".gov-runtime/findings.jsonl"


def _append_finding(project_root: str, finding: dict) -> None:
    try:
        path = os.path.join(project_root, FINDINGS_REL)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(finding, separators=(",", ":")) + "\n")
    except Exception:
        pass


def _fail(project_root: str, reason: str,
          session_id: str = "", tool_name: str = "",
          agent_type: str = "", role: str = "", ticket: str = "",
          command: str = "") -> None:
    """Record a DEC-122 finding for the hook's own failure, report
    through stderr (exit 2) so the agent sees the message."""
    _append_finding(project_root, {
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": session_id,
        "agent_type": agent_type,
        "role": role,
        "ticket": ticket,
        "tool": tool_name or "Bash",
        "command": command,
        "paths": [],
        "action": "flagged",
        "reason": reason,
    })
    sys.stderr.write(reason + "\n")
    sys.exit(2)


def _read_stdin_with_deadline(deadline_s: float) -> str:
    deadline = time.monotonic() + deadline_s
    chunks: list[str] = []
    fd = sys.stdin.fileno()
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return ""
        ready = select.select([fd], [], [], min(remaining, 0.5))
        if ready[0]:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk.decode("utf-8", errors="replace"))
        elif chunks:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
    return "".join(chunks)


def _report(text: str, event: str) -> None:
    """Exit 0 with additionalContext shown to the agent."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }
    sys.stdout.write(json.dumps(output))
    sys.exit(0)


def _silent() -> None:
    sys.exit(0)


def main() -> None:
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    role = os.environ.get("GOV_ROLE", "")
    ticket = os.environ.get("GOV_TICKET", "")

    try:
        raw = _read_stdin_with_deadline(STDIN_DEADLINE_S)
    except Exception as exc:
        _fail(project_root, f"containment: failed to read stdin: {exc}",
              role=role, ticket=ticket)

    if not raw or not raw.strip():
        _fail(project_root, "containment: stdin was empty",
              role=role, ticket=ticket)

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        _fail(project_root, f"containment: stdin is not valid JSON: {exc}",
              role=role, ticket=ticket)

    if not isinstance(data, dict):
        _fail(project_root, "containment: stdin is not a JSON object",
              role=role, ticket=ticket)

    tool_name = data.get("tool_name")
    if not tool_name or not isinstance(tool_name, str):
        _silent()

    # Only process Bash calls.
    if tool_name != "Bash":
        _silent()

    event = data.get("hook_event_name", "PostToolUse")
    if event not in ("PostToolUse", "PostToolUseFailure"):
        _silent()

    # Repair 8: no tool_use_id -> run check as a call without a
    # snapshot (flag only, never revert).
    tool_use_id = data.get("tool_use_id", "")

    session_id = data.get("session_id", "")
    command = ""
    ti = data.get("tool_input")
    if isinstance(ti, dict):
        command = ti.get("command", "")

    subagent_type = data.get("agent_type")

    try:
        from gov.guard.containment import check_containment
    except Exception as exc:
        _fail(project_root,
              f"containment: cannot import check logic: {exc}",
              session_id=session_id, tool_name=tool_name,
              agent_type=subagent_type or "", role=role,
              ticket=ticket, command=command)

    try:
        report = check_containment(
            project_root=project_root,
            role=role or None,
            ticket_id=ticket or None,
            subagent_type=subagent_type,
            session_id=session_id,
            agent_type=subagent_type,
            command=command,
            tool_use_id=tool_use_id,
        )
    except Exception as exc:
        _fail(project_root, f"containment: check failed: {exc}",
              session_id=session_id, tool_name=tool_name,
              agent_type=subagent_type or "", role=role,
              ticket=ticket, command=command)

    if report:
        _report(report, event)
    else:
        _silent()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        role = os.environ.get("GOV_ROLE", "")
        ticket = os.environ.get("GOV_TICKET", "")
        _fail(project_root, f"containment: uncaught: {exc}",
              role=role, ticket=ticket)
