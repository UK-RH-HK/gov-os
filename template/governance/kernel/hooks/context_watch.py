#!/usr/bin/env python3
"""
PostToolUse hook (W2-176, DEC-1140 (1)(b), DEC-445): a once-per-session reminder near the window's end.

Reads only the transcript's last 256 KiB, takes the last main-session assistant line's usage (input plus cache
tokens) and divides it by the model's window. At 85 % or more, and once per session (a state file under
.gov-runtime/scratch/context_watch/), it adds context telling the session to write its handover now and to begin
its compaction summary with the read-first line. A handover aid only: it sets no threshold, stops nothing and
never decides on the tool call (DEC-838, DEC-901's precedent).

Any error: nothing printed. Always exits 0.
"""

from __future__ import annotations

import json
import os
import re
import sys

TAIL_BYTES = 256 * 1024
SHARE = 0.85
DEFAULT_LIMIT = 200_000
CONTEXT_LIMITS = {  # tokens; a "[1m]" or date suffix matches its base (code.claude.com/docs/en/model-config)
    "claude-opus-5-5": 1_000_000,
    "claude-sonnet-5-5": 1_000_000,
    "claude-haiku-5-5": 1_000_000,
    "claude-fable-5-2": 1_000_000,
}
STATE_REL = ".gov-runtime/scratch/context_watch"


def limit(model: str) -> int:
    base = re.sub(r"(\[1m\]|-\d{8})$", "", model)
    return CONTEXT_LIMITS.get(model) or CONTEXT_LIMITS.get(base) or DEFAULT_LIMIT


def last_usage(path: str) -> tuple[int, str] | None:
    """(tokens in context, model) of the last main-session assistant line in the tail, or None."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - TAIL_BYTES))
        tail = f.read(TAIL_BYTES)
    for raw in reversed(tail.splitlines()):
        if b'"assistant"' not in raw or b'"usage"' not in raw:
            continue
        try:
            line = json.loads(raw)
        except ValueError:
            continue  # the first line of the tail, or a last line still being written
        if not isinstance(line, dict) or line.get("type") != "assistant" or line.get("isSidechain") is True:
            continue
        message = line.get("message") or {}
        usage = message.get("usage") or {}
        keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
        if not all(isinstance(usage.get(key, 0), int) for key in keys):
            return None
        return sum(usage.get(key, 0) for key in keys), str(message.get("model") or "")
    return None


def text(project_root: str) -> str:
    def at(rel: str) -> str:
        return os.path.join(project_root, rel)

    role = os.environ.get("GOV_ROLE", "")
    if role == "orchestrator" and not os.path.isfile(at(".git")):
        files = (f"the RESUME HERE section of {at('.gov-runtime/scratch/orchestrator/CHECKPOINT.md')}, "
                 f"{at('governance/project/orchestration/packages/DECIDED-NOT-DONE.md')} and "
                 f"{at('log/report-state.json')}")
        first = f"{at('.gov-runtime/scratch/orchestrator/CHECKPOINT.md')}, its RESUME HERE section"
    elif role == "orchestrator":
        files = f"your CHECKPOINT, {at('.gov-runtime/scratch/lead/CHECKPOINT.md')}"
        first = f"{at('.gov-runtime/scratch/lead/CHECKPOINT.md')}, its RESUME HERE section"
    else:
        files = f"your record (gov checkpoint), under {at('.gov-runtime/scratch/checkpoints/' + os.environ.get('GOV_TICKET', ''))}"
        first = "your brief and your record"
    return (f"Context watch: this session has used 85 % or more of its context window. Write your checkpoint now "
            f"and update every file that needs it: {files}. Begin your compaction summary with the line "
            f'"READ FIRST: {first}, before any other work." This is a handover aid, not a stop and not an early '
            f"compaction: carry on with your work once the handover is written.")


def main() -> None:
    try:
        event = json.loads(sys.stdin.read() or "null")
        if not isinstance(event, dict) or event.get("hook_event_name") != "PostToolUse":
            return
        found = last_usage(str(event["transcript_path"]))
        if not found or found[0] < SHARE * limit(found[1]):
            return
        project_root = os.environ.get("CLAUDE_PROJECT_DIR") or str(event["cwd"])
        if not os.path.isabs(project_root):
            return  # a null or relative cwd would put the state file outside the project
        state = os.path.join(project_root, STATE_REL)
        os.makedirs(state, exist_ok=True)
        name = re.sub(r"[^A-Za-z0-9_-]", "_", str(event["session_id"]))[:128] or "_"
        os.close(os.open(os.path.join(state, name), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644))
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse", "additionalContext": text(project_root)}}))
    except Exception:
        return  # already reminded, or any error: say nothing


if __name__ == "__main__":
    main()
    sys.exit(0)
