"""The READY rule (CAP-31.c, CAP-31.d, CAP-34.e): which tickets may be started, and what holds the others.

Tickets are read from the working tree, records from the store. The rule is a
gate and does not fail open: a ticket whose file cannot be read is not READY,
and no ticket is READY while the store cannot be read.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from gov import records
from gov.cli.errors import GovError
from gov.tasks.claims import CLAIMS_REL
from gov.tasks.tickets import TICKETS_REL, frontmatter


def _list(value) -> list:
    return value if isinstance(value, list) else [] if value is None else [value]


def _queue(root: Path) -> tuple[list[str], dict[str, list[str]]]:
    root = Path(root)
    tickets = {path.stem: frontmatter(path) or {} for path in sorted((root / TICKETS_REL).glob("*.md"))}
    try:
        status = {record["id"]: record["status"] for record in records.records(root)}
        superseded = {edge["target"] for edge in records.edges(root, type="SUPERSEDES")}
        packages = {record["id"] for record in records.records(root, type="decision-package", status="PROPOSED")}
        waiting = {edge["target"] for edge in records.edges(root, type="CONSTRAINS") if edge["source"] in packages}
        store_read = True
    except (GovError, sqlite3.Error):
        status, superseded, waiting, store_read = {}, set(), set(), False
    ready, blocked = [], {}
    for ticket, front in tickets.items():
        if front.get("status") == "closed":
            continue
        tests = front.get("acceptance_tests")
        folder = tests.get("path") if isinstance(tests, dict) else None
        inputs = [str(item) for item in _list(front.get("inputs"))]
        holds = {
            "DEPENDENCY_OPEN": any(tickets.get(str(dep), {}).get("status") != "closed"
                                   for dep in _list(front.get("deps"))),
            "CLAIMED": front.get("status") == "in_progress" or os.path.lexists(root / CLAIMS_REL / ticket),
            "NO_ACCEPTANCE_TESTS": not (root / str(folder or f"tests/acceptance/{front.get('wbs_id') or ticket}")
                                        ).is_dir(),
            "SPEC_NOT_CLOSED": front.get("specification") is not None
                               and status.get(str(front["specification"])) != "CLOSED",
            "INPUT_ABSENT": any(item not in status for item in inputs),
            "INPUT_SUPERSEDED": any(item in superseded for item in inputs),
            "DECISION_OPEN": ticket in waiting,
        }
        reasons = [reason for reason, held in holds.items() if held]
        if front.get("status") == "open" and not reasons and store_read:
            ready.append(ticket)
        else:
            blocked[ticket] = reasons
    return ready, blocked


def ready(root: Path) -> list[str]:
    """The ids of the tickets that are READY: open, and held by nothing."""
    return _queue(root)[0]


def blocked(root: Path) -> dict[str, list[str]]:
    """``ticket id -> reason codes`` of every ticket that is neither closed nor READY."""
    return _queue(root)[1]
