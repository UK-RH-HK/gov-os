"""The turn and the ``IDLE-REASON`` line, read from the session's transcript (JSON lines).

Only entry types, keys and the assistant's text items are read. A turn starts at the last ``user`` entry that is not a
tool result and not meta, or at any ``user`` entry that carries ``turnOrigin`` or ``wakeupSource`` (a scheduled wakeup is
meta and still starts a turn); its ``uuid`` (else its ``timestamp``) is the turn's key.
"""

from __future__ import annotations

import json
import os
import re

REASON_LINE = re.compile(r"^\s*IDLE-REASON:\s*(\S.*?)\s*$", re.M)
TAIL_BYTES = 8 * 1024 * 1024


def _starts_a_turn(entry: dict, content) -> bool:
    if entry.get("turnOrigin") or entry.get("wakeupSource"):
        return True
    return not entry.get("isMeta") and (isinstance(content, str) or (isinstance(content, list) and any(
        c.get("type") != "tool_result" for c in content if isinstance(c, dict))))


def read(data: dict) -> tuple[str | None, str | None]:
    """``(the turn's key or None, the text of this turn's IDLE-REASON line or None)`` for a Stop hook's input."""
    texts, turn = [], None
    path = data.get("transcript_path")
    if path and os.path.isfile(path):
        with open(path, "rb") as stream:
            size = stream.seek(0, 2)
            stream.seek(max(0, size - TAIL_BYTES))
            tail = stream.read().decode("utf-8", errors="replace").splitlines()
        for line in reversed(tail):
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            message = entry.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if entry.get("type") == "user" and _starts_a_turn(entry, content):
                turn = entry.get("uuid") or entry.get("timestamp")
                break
            if entry.get("type") == "assistant" and isinstance(content, list):
                texts += [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
    if isinstance(data.get("last_assistant_message"), str):
        texts.append(data["last_assistant_message"])
    for text in texts:
        found = REASON_LINE.search(text or "")
        if found:
            return turn, f"IDLE-REASON: {found.group(1)[:300]}"
    return turn, None
