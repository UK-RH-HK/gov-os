#!/usr/bin/env python3
"""
PreToolUse default-deny guard hook (W1-02, W1-03).

Reads a JSON object from stdin, decides whether the tool call is allowed,
and either allows (exit 0, no deny on stdout) or denies (exit 0 with
permissionDecision: deny, or exit 2 on internal failure).

When the guard lets a Bash call through, takes a before-snapshot of
``git status`` and ``HEAD`` for the post-command containment check
(DEC-126).

Fail-closed: any internal error exits with code 2 and appends a finding
to .gov-runtime/findings.jsonl (DEC-110).
"""

from __future__ import annotations

import json
import os
import select
import stat
import sys
import time

STDIN_DEADLINE_S = 3.0
FINDINGS_REL = ".gov-runtime/findings.jsonl"
RECORDS_REL = ".gov-runtime/records.jsonl"


def _append_finding(project_root: str, finding: dict) -> None:
    try:
        path = os.path.join(project_root, FINDINGS_REL)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(finding, separators=(",", ":")) + "\n")
    except Exception:
        pass


def _record_unmarked_flag(project_root: str, data: dict, flag: str) -> None:
    """Record an unmarked presence at the freeze flag's path (DEC-402).

    One line in ``records.jsonl`` in DEC-177's form.  An observation:
    it must not block or fail the call.  The hook runs outside the
    sandbox, so the line goes only to a regular file in a real
    ``.gov-runtime/``: no link is followed and nothing is opened that
    could hold the hook (a named pipe).
    """
    try:
        path = os.path.join(project_root, RECORDS_REL)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.islink(os.path.dirname(path)):
            return
        record = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": data.get("session_id", ""),
            "agent_type": data.get("agent_type") or "",
            "role": os.environ.get("GOV_ROLE") or "",
            "ticket": os.environ.get("GOV_TICKET") or "",
            "tool": data.get("tool_name", ""),
            "command": data["tool_input"].get("command", ""),
            "paths": [flag],
            "action": "recorded",
            "reason": "something without the freeze marker is at the "
                      "freeze flag's path: no freeze",
        }
        line = json.dumps(record, separators=(",", ":")) + "\n"
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT
                     | os.O_NOFOLLOW | os.O_NONBLOCK, 0o666)
        try:
            if stat.S_ISREG(os.fstat(fd).st_mode):
                os.write(fd, line.encode("utf-8"))
        finally:
            os.close(fd)
    except Exception:
        pass


def _fail(project_root: str, kind: str, reason: str,
          session_id: str = "", tool_name: str = "") -> None:
    _append_finding(project_root, {
        "source": "guard",
        "kind": kind,
        "reason": reason,
        "session_id": session_id,
        "tool_name": tool_name,
    })
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


def _deny(reason: str = "") -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(output))
    sys.exit(0)


def _ask(reason: str = "") -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(output))
    sys.exit(0)


def _allow() -> None:
    sys.exit(0)


def _take_snapshot(project_root: str, data: dict, flag: str) -> None:
    """Take a before-snapshot for the containment check (DEC-126).

    *flag* is the one reading of the freeze flag (DEC-402): the
    snapshot remembers a freeze from it (DEC-407).

    Called when the guard lets a Bash call through.  Snapshot failure
    in a non-git directory does not block the call.  Any other failure
    is appended as a finding but also does not block the call.
    """
    tool_use_id = data.get("tool_use_id", "")
    if not tool_use_id:
        return
    try:
        from gov.guard.containment import take_snapshot
        take_snapshot(project_root, tool_use_id,
                      session_id=data.get("session_id", ""),
                      agent_id=data.get("agent_id", ""), flag=flag)
    except Exception as exc:
        # Snapshot failure must not go unnoticed (but does not block).
        _append_finding(project_root, {
            "source": "guard",
            "kind": "snapshot_error",
            "reason": f"before-snapshot failed: {exc}",
            "session_id": data.get("session_id", ""),
            "tool_name": data.get("tool_name", ""),
        })


def _note_tool_call(project_root: str, data: dict) -> None:
    """Clear pending snapshots of this actor (DEC-142, DEC-146).

    Called for every tool call the PreToolUse hook sees, before the
    guard decides.  A later tool call of the same actor proves any
    earlier call of that actor is over; its snapshot no longer blocks
    restoration for other actors.  Must not add latency or block a call.
    """
    try:
        from gov.guard.containment import clear_actor_snapshots
        session_id = data.get("session_id", "")
        agent_id = data.get("agent_id", "")
        clear_actor_snapshots(project_root, session_id, agent_id or "")
    except Exception:
        pass  # must not block any call


def _note_write_tool(project_root: str) -> None:
    """Increment the sequence counter for a write-tool call (DEC-124).

    When a Write/Edit/NotebookEdit is allowed, the seq counter
    advances so that any running Bash call's check sees overlap and
    does not revert the write-tool's work.
    """
    try:
        from gov.guard.containment import mark_concurrent_write
        mark_concurrent_write(project_root)
    except Exception:
        pass  # must not add latency to write-tool calls


def main() -> None:
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    try:
        raw = _read_stdin_with_deadline(STDIN_DEADLINE_S)
    except Exception as exc:
        _fail(project_root, "stdin_error", f"failed to read stdin: {exc}")

    if not raw or not raw.strip():
        _fail(project_root, "empty_input", "stdin was empty")

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        _fail(project_root, "invalid_json", f"stdin is not valid JSON: {exc}")

    if not isinstance(data, dict):
        _fail(project_root, "invalid_input", "stdin is not a JSON object")

    # DEC-142, DEC-146: every tool call clears pending snapshots of the
    # same actor, proving any earlier call of that actor is over.
    _note_tool_call(project_root, data)

    tool_name = data.get("tool_name")
    if not tool_name or not isinstance(tool_name, str):
        session_id = data.get("session_id", "")
        _fail(project_root, "missing_field", "no tool_name in input",
              session_id=session_id, tool_name="")

    tool_input = data.get("tool_input")
    if tool_input is None or not isinstance(tool_input, dict):
        session_id = data.get("session_id", "")
        _fail(project_root, "missing_field", "no usable tool_input in input",
              session_id=session_id, tool_name=tool_name)

    try:
        from gov.guard.decide import decide, freeze_state, FREEZE_FLAG
    except Exception as exc:
        session_id = data.get("session_id", "")
        _fail(project_root, "import_error", f"cannot import guard logic: {exc}",
              session_id=session_id, tool_name=tool_name)

    role = os.environ.get("GOV_ROLE")
    ticket_id = os.environ.get("GOV_TICKET")
    cwd = data.get("cwd", project_root)
    subagent_type = data.get("agent_type")

    try:
        # DEC-402: the flag is read once, for the decision and for the
        # install rule.
        flag = freeze_state(project_root)
        decision, reason = decide(
            tool_name=tool_name,
            tool_input=tool_input,
            project_root=project_root,
            role=role,
            ticket_id=ticket_id,
            subagent_type=subagent_type,
            cwd=cwd,
            flag=flag,
        )
    except Exception as exc:
        session_id = data.get("session_id", "")
        _fail(project_root, "decide_error", f"decision failed: {exc}",
              session_id=session_id, tool_name=tool_name)

    def _record() -> None:
        # DEC-402: an unmarked presence is recorded for a call that may
        # write, once the call is known not to be denied.
        if flag == "unmarked":
            _record_unmarked_flag(project_root, data, FREEZE_FLAG)

    if decision == "deny":
        _deny(reason)
    else:
        if tool_name == "Bash":
            # Install rule (W1-04, DEC-120): after the guard allows a
            # Bash call, check for sudo and install commands.
            command = tool_input.get("command", "")
            try:
                from gov.guard.install import (
                    has_sudo, has_install, acting_role,
                    install_in_experiment_folder)
            except Exception as exc:
                session_id = data.get("session_id", "")
                _fail(project_root, "import_error",
                      f"cannot import install rule: {exc}",
                      session_id=session_id, tool_name=tool_name)
            if has_sudo(command):
                _deny("sudo is denied to all agent roles (DEC-083)")
            elif has_install(command):
                if flag == "frozen":
                    _deny("frozen: install denied")
                ar = acting_role(role, subagent_type)
                if ar == "orchestrator":
                    # The owner may approve; take the before-snapshot
                    # so containment can run if the command executes.
                    _record()
                    _take_snapshot(project_root, data, flag)
                    _ask(f"install command requires owner approval "
                         f"(tool registry record required): {command}")
                elif ar == "research" and install_in_experiment_folder(
                        command, cwd, project_root, ticket_id):
                    # DEC-163: the research role's one exception; the
                    # sandbox's write fence holds it to the folder.
                    _record()
                    _take_snapshot(project_root, data, flag)
                    _allow()
                else:
                    _deny(
                        f"install by role "
                        f"'{ar or 'none'}' denied: only the "
                        f"orchestrator may propose installs, and research "
                        f"may install inside its experiment folder")
            else:
                # Non-install Bash: take the before-snapshot (DEC-126)
                # and allow.
                _record()
                _take_snapshot(project_root, data, flag)
                _allow()
        elif tool_name in ("Write", "Edit", "NotebookEdit"):
            _record()
            _note_write_tool(project_root)
            _allow()
        else:
            _allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        _fail(project_root, "uncaught_error", f"uncaught: {exc}")
