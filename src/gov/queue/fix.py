"""A fix landed under a closed ticket, in the ticket's close record (W2-201 fix X6, DEC-1219 (5)).

A fix is recorded in its owning ticket, open or closed (EMERGENCY-2 4.2): ``gov queue`` lands a closed ticket's fix
with no second close, and appends to ``docs/close/<ticket>/CL-<ticket>.md`` one entry of its front-matter list
``fixes`` (``{line, branch, tip, tested, landed}``) and one body line ``- fix landed: <line> (<branch> @ <tip12>)``;
everything else of the record stays as it was. A ticket with no close record gets one in the close record's form
with its identity and ``fixes`` only, nothing else of a first close.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from gov.cli.errors import GovError

FIX_RECORD_FAILED = "FIX_RECORD_FAILED"


def record_rel(ticket: str) -> str:
    return f"docs/close/{ticket}/CL-{ticket}.md"


def _split(text: str) -> tuple[dict, str]:
    """``(front matter, body)`` of a close record; ``ValueError`` where its front matter cannot be read."""
    import yaml

    if not text.startswith("---\n"):
        raise ValueError("it does not start with a front matter")
    end = text.find("\n---\n", 3)
    if end < 0:
        raise ValueError("its front matter has no end")
    front = yaml.safe_load(text[4:end + 1])
    if not isinstance(front, dict):
        raise ValueError("its front matter is not a mapping")
    return front, text[end + len("\n---\n"):]


def append(root: Path, ticket: str, line: str, branch: str, tip: str, tested: str) -> str:
    """Append the fix to the ticket's close record under ``root`` (written whole); its root-relative path.
    ``FIX_RECORD_FAILED`` where the record there cannot be read or written: nothing lands."""
    import yaml

    from gov.close import state

    rel = record_rel(ticket)
    path = Path(root) / rel
    landed = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {"line": line, "branch": branch, "tip": tip, "tested": tested, "landed": landed}
    try:
        if path.exists():
            front, body = _split(path.read_text(encoding="utf-8"))
        else:
            front = {"id": f"CL-{ticket}", "type": "close", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
                     "task": ticket, "created": landed}
            body = f"\n# CL-{ticket} — Close record for {ticket}\n"
        fixes = front.get("fixes")
        if fixes is None:
            fixes = front["fixes"] = []
        if not isinstance(fixes, list):
            raise ValueError("its fixes key is not a list")
        fixes.append(entry)
        if body and not body.endswith("\n"):
            body += "\n"
        body += f"- fix landed: {line} ({branch} @ {tip[:12]})\n"
        state.write_whole(path, "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n" + body)
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as e:
        raise GovError(FIX_RECORD_FAILED, f"{ticket}: the fix cannot be written to its close record {rel} "
                       f"({type(e).__name__}: {' '.join(str(e).split())[:200]}); nothing lands",
                       {"ticket": ticket, "record": rel}, exit_code=3) from None
    return rel
