"""The governance share of a ticket (W1-31; DEC-086, DEC-106, DEC-170).

``measure(root, ticket, sessions)`` returns the record ``gov telemetry`` prints, and writes nothing.

A figure is measured or it says "not measured" (DEC-449, DEC-454): nothing here turns "could not read" into a
number. The tokens of the sessions are ccusage's, and when they cannot be measured for every named session
the counter refuses. A field whose source nobody has decided says "not measured": the five governance
sources without a recorded trace per ticket, a ticket without a checkpoint or close record, the P1 and
session-log fields, the sandbox's tokens, and two of the three learning metrics.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from gov.checkpoint.record import CHECKPOINTS_REL, NAME, SCRATCH_CHECKPOINTS_REL, TICKET_ID
from gov.cli.errors import GovError
from gov.context import _tokens
from gov.tasks.tickets import TICKETS_REL, frontmatter

NOT_MEASURED = "not measured"  # the word ``gov close`` writes for a field it did not measure
SOURCES = ("instruction_files", "sessionstart_packet", "hook_output", "gov_output", "mcp_definitions",
           "checkpoint_records", "close_records")  # DEC-086
PROFILES = ("LITE", "STANDARD", "FULL")
# The record's name of each figure, and ccusage's.
FIGURES = {"tokens_in": "inputTokens", "tokens_out": "outputTokens", "cache_read_tokens": "cacheReadTokens",
           "cache_creation_tokens": "cacheCreationTokens"}
UNDECIDED = ("model", "role", "skill_versions", "tool_versions", "packet_id", "retrieval_queries", "retrieval_hits",
             "files_written", "tests", "retries", "handoffs", "decisions", "owner_interventions",
             "agent", "provider", "latency", "files_read", "sandbox_system_prompt_tokens")


def _total(values):
    """The sum of ``values``, or "not measured" when any of them is."""
    values = list(values)
    return NOT_MEASURED if NOT_MEASURED in values else sum(values)


def share(total, tokens_in, tokens_out):
    """``total / (tokens_in + tokens_out)`` as a fraction of 1 (DEC-086), or "not measured"."""
    if NOT_MEASURED in (total, tokens_in, tokens_out) or tokens_in + tokens_out <= 0:
        return NOT_MEASURED
    return total / (tokens_in + tokens_out)


def _records(paths):
    """The tokens of the records ``paths``. "not measured" when one cannot be read, and when there is none:
    whether a ticket without a record counts 0 is not decided."""
    if paths == NOT_MEASURED or not paths:
        return NOT_MEASURED
    try:
        return sum(_tokens(path.read_text(encoding="utf-8")) for path in paths)
    except (OSError, UnicodeDecodeError):
        return NOT_MEASURED


def _checkpoints(root: Path, ticket: str):
    """The ticket's checkpoint records, deliberate and automatic (DEC-444); "not measured" for a folder that
    is there and cannot be listed."""
    paths = []
    for rel in (CHECKPOINTS_REL, SCRATCH_CHECKPOINTS_REL):
        folder = root / rel / ticket
        try:
            paths += [folder / name for name in sorted(os.listdir(folder)) if NAME.fullmatch(name)]
        except FileNotFoundError:
            continue
        except OSError:
            return NOT_MEASURED
    return paths


def _ccusage_rows() -> list:
    """ccusage's row of every session in the harness's logs (``CLAUDE_CONFIG_DIR``, or its default under
    ``HOME``), with its built-in prices. Refuses without ccusage and without its report."""
    program = shutil.which("ccusage")
    if program is None:
        raise GovError("CCUSAGE_ABSENT", "ccusage is not on PATH: the sessions' tokens were not measured", {})
    try:
        done = subprocess.run([program, "claude", "session", "--json", "--offline"], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=60)
        rows = json.loads(done.stdout)["sessions"] if done.returncode == 0 else None
        detail = done.stderr.strip()[-500:]
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as error:
        rows, detail = None, str(error)
    if not isinstance(rows, list):
        raise GovError("SESSIONS_NOT_MEASURED", "ccusage gave no report of the sessions: nothing was measured",
                       {"ccusage": detail})
    return rows


def _session(rows: list, session: str) -> dict:
    """What ccusage measured for ``session``. An absent row is not a session of zero tokens: it refuses."""
    found = [row for row in rows if isinstance(row, dict) and row.get("sessionId") == session]
    if len(found) != 1 or any(type(found[0].get(key)) is not int or found[0][key] < 0 for key in FIGURES.values()):
        raise GovError("SESSIONS_NOT_MEASURED",
                       f"ccusage has no single row with the figures of session {session}: it was not measured",
                       {"session": session, "rows": len(found)})
    row = found[0]
    models, cost, priced = row.get("modelsUsed"), row.get("totalCost"), row.get("modelBreakdowns")
    # A cost is measured only when ccusage had a price for every model of the session.
    costed = (type(cost) in (int, float) and isinstance(priced, list) and priced
              and all(isinstance(each, dict) and not each.get("missingPricing") for each in priced))
    named = isinstance(models, list) and models and all(isinstance(model, str) and model for model in models)
    return {"session": session, "model": models if named else NOT_MEASURED,
            **{name: row[key] for name, key in FIGURES.items()}, "cost": cost if costed else NOT_MEASURED}


def measure(root: Path, ticket: str, sessions: list[str]) -> dict:
    """The telemetry record of ``ticket``, with ``sessions`` as its sessions (the caller names them: nothing
    recorded ties a session to a ticket). Raises GovError when the sessions' tokens could not be measured."""
    root = Path(root)
    front = frontmatter(root / TICKETS_REL / f"{ticket}.md") if TICKET_ID.fullmatch(ticket) else None
    if front is None:
        raise GovError("TICKET_UNKNOWN", f"{ticket} is not a ticket of this project", {"ticket": ticket})
    sessions = list(dict.fromkeys(sessions))
    if not sessions:
        raise GovError("TICKET_SESSION_MISSING", "no session of the ticket is named (--ticket-session): "
                       "the sessions' tokens were not measured", {"ticket": ticket})
    rows = _ccusage_rows()
    entries = [_session(rows, session) for session in sessions]
    creation = sum(entry.pop("cache_creation_tokens") for entry in entries)
    figures = {name: sum(entry[name] for entry in entries) for name in ("tokens_in", "tokens_out", "cache_read_tokens")}

    counted = dict.fromkeys(SOURCES, NOT_MEASURED)
    counted["checkpoint_records"] = _records(_checkpoints(root, ticket))
    counted["close_records"] = _records([root / "docs" / "close" / ticket / f"CL-{ticket}.md"])
    counted["total"] = _total(counted[name] for name in SOURCES)
    fraction = share(counted["total"], figures["tokens_in"], figures["tokens_out"])
    profile = str(front.get("profile")).upper()
    return {
        "ticket": ticket,
        "profile": profile if profile in PROFILES else NOT_MEASURED,
        "governance_tokens": counted,
        "governance_share": fraction,
        "not_measured": [name for name in SOURCES if counted[name] == NOT_MEASURED],
        **figures,
        "cache_creation_tokens": creation,
        "cost": _total(entry["cost"] for entry in entries),
        "sessions": entries,
        **dict.fromkeys(UNDECIDED, NOT_MEASURED),
        "learning_metrics": {"kpi_disputes": NOT_MEASURED, "acceptance_tests_rewritten": NOT_MEASURED,
                             "governance_share": fraction},
    }
