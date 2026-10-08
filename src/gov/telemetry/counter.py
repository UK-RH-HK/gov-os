"""The governance share of a ticket (W1-31; DEC-086, DEC-106, DEC-170, DEC-491, DEC-495, DEC-501, DEC-502,
DEC-507).

``measure(root, ticket, sessions)`` returns the record ``gov telemetry`` prints, and writes nothing.

A figure is measured or it says "not measured" (DEC-449, DEC-454): nothing here turns "could not read" into a
number. The tokens of the sessions are ccusage's, held against the assistant lines of each session's own log
and of its sub-agents' logs; when they cannot be measured for every named session the counter refuses. Five
sources are measured (three from the session logs, ``gov.telemetry.sessionlog``; two from the ticket's record
folders) and two are a static estimate on a line of their own, which stands on the role each session is named
with (DEC-507). The counter gives counts and states no opinion of them.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from gov.checkpoint.record import CHECKPOINTS_REL, NAME, SCRATCH_CHECKPOINTS_REL, TICKET_ID
from gov.cli.errors import GovError
from gov.context import _tokens
from gov.tasks.tickets import TICKETS_REL, frontmatter
from gov.telemetry import sessionlog

NOT_MEASURED = "not measured"  # the word ``gov close`` writes for a field it did not measure
SOURCES = (*sessionlog.LOG_SOURCES, "checkpoint_records", "close_records")  # DEC-495: the measured ones
ESTIMATED = ("instruction_files", "mcp_definitions")
PROFILES = ("LITE", "STANDARD", "FULL")
# The record's name of each figure, and ccusage's; in the order of ``sessionlog.USAGE``.
FIGURES = {"tokens_in": "inputTokens", "tokens_out": "outputTokens", "cache_creation_tokens": "cacheCreationTokens",
           "cache_read_tokens": "cacheReadTokens"}
# No source is decided for these; the sandbox's tokens among them, until W1-42 records its measurement (DEC-501).
UNDECIDED = ("role", "skill_versions", "tool_versions", "packet_id", "retrieval_queries", "retrieval_hits",
             "files_written", "tests", "retries", "handoffs", "decisions", "owner_interventions",
             "provider", "files_read", "sandbox_system_prompt_tokens")
HARNESS, API_DURATION = "Claude Code", "harness_api_duration_ms"
# What the counter cannot count, said in every record (DEC-501). No entry makes a figure "not measured".
KNOWN_GAPS = (
    # DEC-502: the output is inside the line of the compaction command's own output. It is not read.
    ("precompact_hook_output", "the output of a PreCompact hook is in no hook line of the log: nothing is counted "
                               "for it"),
    ("gov_run_indirectly", "a gov command inside bash -c, eval, backticks or a wrapper script is not seen: its "
                           "result is not counted"),
    # DEC-507 leaves them undecided: this entry and the estimate's method are where the record says so.
    ("subagent_instruction_files", "the instruction files a sub-agent of a named session was given are not part "
                                   "of the estimate: they are not counted"),
)
ROOT_FILES, ROLE_FILES_REL = ("CLAUDE.md", "AGENTS.md"), ".claude/agents"
ROLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")  # a role is the plain name of its file, never a path
# DEC-507: this text and ``_estimate`` say all the estimate is.
METHOD = ("A static estimate, not read from a session log. instruction_files: for each session named for the "
          f"ticket, the tokens (4 characters a token, rounded up) of the file of its role, {ROLE_FILES_REL}/<role>.md, "
          f"and of {' and '.join(ROOT_FILES)} at the project's root where they exist, summed over the sessions; "
          "the caller names each session's role, and the instruction files of a sub-agent are not counted. "
          "mcp_definitions: 0 by decision, with its reason beside it; no file is read for it.")
MCP_REASON = "the Governance OS defines no MCP server (DEC-507): whatever the project defines is not governance text"
DISPUTES_NAME = "kpi-disputes.txt"
DISPUTE = re.compile(r"(DEC-\d+):\s*\S.*")
REASON_NOT_RECORDED = "reason not recorded"


def _total(values):
    """The sum of ``values``, or "not measured" when any of them is."""
    values = list(values)
    return NOT_MEASURED if NOT_MEASURED in values else sum(values)


def share(tokens, denominator):
    """``tokens / denominator`` as a fraction of 1, or "not measured"."""
    return NOT_MEASURED if NOT_MEASURED in (tokens, denominator) or denominator <= 0 else tokens / denominator


def _text(path: Path):
    """The text of ``path``; None when it is not there, False when it is there and cannot be read."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return False if os.path.lexists(path) else None
    except (OSError, UnicodeDecodeError):
        return False


def _checkpoints(root: Path, ticket: str):
    """The tokens of the ticket's checkpoint records, deliberate and automatic (DEC-444), or the reason they
    are not measured. A folder that is there and holds no record counts 0 (DEC-491)."""
    texts, folders = [], 0
    for rel in (CHECKPOINTS_REL, SCRATCH_CHECKPOINTS_REL):
        folder = root / rel / ticket
        try:
            texts += [_text(folder / name) for name in sorted(os.listdir(folder)) if NAME.fullmatch(name)]
            folders += 1
        except FileNotFoundError:
            continue
        except OSError:
            return "a checkpoint folder of the ticket cannot be listed"
    if not folders:
        return "the ticket has no checkpoint folder"
    if not all(isinstance(text, str) for text in texts):
        return "a checkpoint record of the ticket cannot be read"
    return sum(_tokens(text) for text in texts)


def _estimate(root: Path, roles: list, missing: dict) -> dict:
    """The line of the estimate (DEC-495, DEC-507): for each session, by its role in ``roles`` (None where the
    caller named none), the role's file and the root files that exist. One session without a figure leaves
    the ticket without one: no role is guessed and the other sessions' sum is not given."""
    read, reasons, counted = {}, [], 0
    for role in roles:
        if role is None or not ROLE.fullmatch(role):
            reasons.append("a session was named without its role" if role is None
                           else "a session's role is not the plain name of a role file")
            continue
        for rel in (f"{ROLE_FILES_REL}/{role}.md", *ROOT_FILES):
            text = read[rel] = read[rel] if rel in read else _text(root / rel)
            if isinstance(text, str):
                counted += _tokens(text)
            elif text is False:
                reasons.append(f"{rel} is there and cannot be read")
            elif rel not in ROOT_FILES:  # a root file that does not exist adds nothing; a role has its file
                reasons.append(f"{rel} is not there: the role has no file")
    if reasons:
        missing["instruction_files"] = list(dict.fromkeys(reasons))
    line = {"label": "estimated", "method": METHOD,
            "files": NOT_MEASURED if reasons else sorted(rel for rel, text in read.items() if isinstance(text, str)),
            "instruction_files": NOT_MEASURED if reasons else counted,
            "mcp_definitions": 0, "mcp_definitions_reason": MCP_REASON}  # DEC-507: 0, never without its reason
    line["total"] = _total(line[name] for name in ESTIMATED)
    return line


def _commits(root: Path, ticket: str):
    """The commits of HEAD's history with ``Task: <ticket>``, oldest first, each ``(id, trailers)``; None when
    the project's commits cannot be read."""
    try:
        done = subprocess.run(["git", "-C", str(root), "log", "HEAD", "--topo-order", "--reverse",
                               "--format=%x01%H%n%(trailers:only,unfold)"], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=60,
                              env={**os.environ, "GIT_CEILING_DIRECTORIES": str(root.parent)})
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    commits = []
    for entry in done.stdout.split("\x01")[1:]:
        commit, _, rest = entry.partition("\n")
        trailers: dict[str, list] = {}
        for line in rest.split("\n"):
            key, _, value = line.partition(":")
            if key.strip() and value.strip():
                trailers.setdefault(key.strip().lower(), []).append(value.strip())
        if ticket in trailers.get("task", []):
            commits.append((commit.strip(), trailers))
    return commits


def _rewrites(commits: list) -> list:
    """The test designer's commits after the ticket's first engineer commit, each with its reason (DEC-491)."""
    roles = [trailers.get("role", []) for _commit, trailers in commits]
    began = next((at for at, role in enumerate(roles) if "engineer" in role), len(commits))
    return [{"commit": commit, "reason": "; ".join(trailers.get("rewrite-reason", [])) or REASON_NOT_RECORDED}
            for commit, trailers in commits[began + 1:] if "independent-test-designer" in trailers.get("role", [])]


def _disputes(root: Path, ticket: str):
    """The decisions of the ticket's disputes record, one a line (DEC-501); "not measured"
    without the record, when it cannot be read, and when a line names no decision."""
    text = _text(root / "docs" / "close" / ticket / DISPUTES_NAME)
    found = [DISPUTE.fullmatch(line) for line in text.splitlines()] if isinstance(text, str) else [None]
    return [{"decision": line.group(1)} for line in found] if all(found) else NOT_MEASURED


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
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
        rows = None
    if not isinstance(rows, list):
        raise GovError("SESSIONS_NOT_MEASURED", "ccusage gave no report of the sessions: nothing was measured", {})
    return rows


def _session(rows: list, session: str, log: dict) -> dict:
    """What ccusage measured for ``session``. An absent row is not a session of zero tokens, and a row is not
    proof (ccusage passes over a line it cannot parse): its four figures must be those of the assistant lines
    of the session's own log and of its sub-agents' logs, each message once. It refuses otherwise."""
    found = [row for row in rows if isinstance(row, dict) and row.get("sessionId") == session]
    if len(found) != 1 or any(type(found[0].get(key)) is not int or found[0][key] < 0 for key in FIGURES.values()):
        raise GovError("SESSIONS_NOT_MEASURED",
                       f"ccusage has no single row with the figures of session {session}: it was not measured",
                       {"session": session, "rows": len(found)})
    row = found[0]
    if tuple(row[key] for key in FIGURES.values()) != log["usage"]:
        raise GovError("SESSIONS_NOT_MEASURED", f"ccusage's figures of session {session} are not those of the "
                       "lines of its log and of its sub-agents' logs: it was not measured", {"session": session})
    cost, priced = row.get("totalCost"), row.get("modelBreakdowns")
    # A cost is measured only when ccusage had a price for every model of the session.
    costed = (type(cost) in (int, float) and isinstance(priced, list) and priced
              and all(isinstance(each, dict) and not each.get("missingPricing") for each in priced))
    return {"session": session, "model": log["models"] or NOT_MEASURED,
            **{name: row[key] for name, key in FIGURES.items()}, "cost": cost if costed else NOT_MEASURED,
            API_DURATION: NOT_MEASURED if log["duration"] is None else log["duration"]}  # DEC-501: no wall clock


def measure(root: Path, ticket: str, sessions: list[str]) -> dict:
    """The telemetry record of ``ticket``, with ``sessions`` as its sessions (the caller names them, DEC-491);
    the logs of a named session's sub-agents are read with it (DEC-501).

    Each entry of ``sessions`` is a text in the form ``--ticket-session`` takes: ``"<session id>"``, or
    ``"<session id>=<role>"`` to name the session's role (DEC-507). ``<role>`` is the plain name of the role's
    file, ``.claude/agents/<role>.md`` under ``root`` (``"engineer"``; no path, no ``.md``). No role is read
    from a log or guessed: where an entry names none, names one that is no plain name or one without its
    file, the record is still returned and its estimate of the instruction files, the estimated share and
    the sum of the shares say "not measured". An entry given twice counts once.

    Reads, from the environment, ``CLAUDE_CONFIG_DIR`` (the folder that holds the session logs' ``projects/``;
    without it ``HOME``'s ``.claude``) and ``PATH`` (ccusage, git). Raises ``GovError`` for an unknown ticket,
    when no session is named, when one session is named with two roles, and when the tokens of a named
    session could not be measured; writes nothing."""
    root = Path(root).resolve()
    front = frontmatter(root / TICKETS_REL / f"{ticket}.md") if TICKET_ID.fullmatch(ticket) else None
    if front is None:
        raise GovError("TICKET_UNKNOWN", f"{ticket} is not a ticket of this project", {"ticket": ticket})
    roles: dict = {}
    for session, named, role in (entry.partition("=") for entry in sessions):
        if roles.setdefault(session, role if named else None) != (role if named else None):
            raise GovError("TICKET_SESSION_ROLE", "a session of the ticket is named with two roles "
                           "(--ticket-session): nothing was measured", {"ticket": ticket})
    sessions = list(roles)
    if not sessions:
        raise GovError("TICKET_SESSION_MISSING", "no session of the ticket is named (--ticket-session): "
                       "the sessions' tokens were not measured", {"ticket": ticket})
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path(os.environ.get("HOME") or Path.home()) / ".claude")
    logs = [sessionlog.read(sessionlog.find(config, session), session) for session in sessions]
    rows = _ccusage_rows()
    entries = [_session(rows, session, log) for session, log in zip(sessions, logs)]
    figures = {name: sum(entry[name] for entry in entries) for name in FIGURES}
    for entry in entries:
        del entry["cache_creation_tokens"]  # shown for the ticket, not per session
        role = roles[entry["session"]]  # DEC-507: as the caller named it, never read or guessed
        entry["role"] = role if role is not None and ROLE.fullmatch(role) else NOT_MEASURED

    missing: dict[str, list] = {}
    for log in logs:
        for name, reasons in log["missing"].items():
            missing[name] = list(dict.fromkeys(missing.get(name, []) + reasons))
    counted = {name: sum(log["counts"][name] for log in logs) for name in sessionlog.LOG_SOURCES}
    checkpoints, closed = _checkpoints(root, ticket), _text(root / "docs" / "close" / ticket / f"CL-{ticket}.md")
    counted["checkpoint_records"] = checkpoints
    if isinstance(checkpoints, str):
        missing["checkpoint_records"] = [checkpoints]
    counted["close_records"] = _tokens(closed) if isinstance(closed, str) else None
    if not isinstance(closed, str):
        missing["close_records"] = ["the ticket has no close record yet: it is counted by a measure after the close"
                                    if closed is None else "the ticket's close record cannot be read"]
    estimate = _estimate(root, list(roles.values()), missing)
    counted = {name: NOT_MEASURED if name in missing else counted[name] for name in SOURCES}
    counted["total"] = _total(counted.values())

    denominator = figures["tokens_in"] + figures["cache_creation_tokens"] + figures["tokens_out"]  # DEC-495
    shares = {"measured": share(counted["total"], denominator), "estimated": share(estimate["total"], denominator),
              "total": share(_total((counted["total"], estimate["total"])), denominator)}
    commits = _commits(root, ticket)
    profile = str(front.get("profile")).upper()
    return {
        "ticket": ticket,
        "profile": profile if profile in PROFILES else NOT_MEASURED,
        "governance_tokens": counted,
        "estimated_governance_tokens": estimate,
        "governance_share": shares,
        "not_measured": [{"name": name, "reason": "; ".join(missing[name])}
                         for name in (*SOURCES, *ESTIMATED) if name in missing],
        "counting_notes": {name: sum(log["notes"][name] for log in logs) for name in sessionlog.NOTES},
        "known_gaps": [{"name": name, "reason": reason} for name, reason in KNOWN_GAPS],
        **figures,
        "cost": _total(entry["cost"] for entry in entries),
        "sessions": entries,
        "model": {"session_logs": list(dict.fromkeys(model for log in logs for model in log["models"])) or NOT_MEASURED,
                  "commits": NOT_MEASURED if commits is None else [
                      {"commit": commit, "model": "; ".join(trailers.get("co-authored-by", [])) or NOT_MEASURED}
                      for commit, trailers in commits]},
        **dict.fromkeys(UNDECIDED, NOT_MEASURED),
        "latency": {API_DURATION: _total(entry[API_DURATION] for entry in entries)},
        "agent": {"harness": HARNESS,  # every log read is of this version, or the counter refused
                  "version": sessionlog.VERSION if all(log["versioned"] for log in logs) else NOT_MEASURED},
        "learning_metrics": {"kpi_disputes": _disputes(root, ticket),
                             "acceptance_tests_rewritten": NOT_MEASURED if commits is None else _rewrites(commits),
                             "governance_share": dict(shares)},
    }
