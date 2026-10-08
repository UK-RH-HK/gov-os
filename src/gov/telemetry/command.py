"""``gov telemetry`` as a command module (W1-31, DEC-317). The convention is in ``gov.cli.main``.

``gov telemetry <ticket> [--ticket-session <session id>[=<role>]]...`` measures the ticket's governance tokens
and the tokens of the sessions the caller names, each with its role (DEC-507), and only reads. The counter is
``gov.telemetry.counter``.
"""

from __future__ import annotations

from pathlib import Path

CLASS = "read"
HELP = "measure a ticket's governance share (DEC-086); only reads"
ACT_PATHS = ()
EXIT_NOT_MEASURED = 3
EXIT_CODES = {EXIT_NOT_MEASURED: "the record is given and a part of the governance share is not measured"}


def add_arguments(parser) -> None:
    parser.add_argument("ticket", metavar="<ticket>", help="the ticket")
    parser.add_argument("--ticket-session", metavar="<session id>[=<role>]", action="append", default=[],
                        help="a session of the ticket, read from the harness's session logs, and its role, the "
                             "name of its file under .claude/agents (without one the estimate is not measured); "
                             "repeatable")


def run(root: Path, args, config: dict):
    from gov.telemetry.counter import NOT_MEASURED, measure

    record = measure(root, args.ticket, args.ticket_session)
    partial = record["not_measured"] or NOT_MEASURED in record["governance_share"].values()
    return (record, EXIT_NOT_MEASURED) if partial else record
