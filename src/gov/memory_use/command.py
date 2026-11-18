"""``gov memory-use [--since YYYY-MM-DD] [--json]`` (W2-197 S9): the memory-use log counted per day and role.

Prints one line per day and role, ``<day> <role> retrieves <n> briefs <n> refused <n>``; with ``--json``, gov's
envelope with ``result.rows`` (each ``{day, role, retrieves, briefs, refused}``), ``result.skipped`` (the lines that
are no record) and ``result.log``. The log is ``gov.memory_use``'s: ``GOV_MEMORY_LOG``, else the one in the main
worktree of ``--root`` (the working folder). ``SINCE_INVALID``: ``--since`` is not a day. It writes nothing.
"""

from __future__ import annotations

CLASS = "read"
HELP = "the memory-use log counted per day and role: retrieves, brief retrievals and refusals"
CHILD_EXIT_CODE = True  # the lines themselves, never gov's default rendering of a result


def add_arguments(parser) -> None:
    parser.add_argument("--since", metavar="<YYYY-MM-DD>", help="only the days from this one on")


def run(root, args, config):
    import datetime
    import json
    import re

    from gov import memory_use
    from gov.cli.errors import GovError

    since = args.since
    if since is not None:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", since):
                raise ValueError(since)
            datetime.date.fromisoformat(since)
        except ValueError:
            raise GovError("SINCE_INVALID", f"--since {since!r} is not a day (YYYY-MM-DD)", {"since": since}) from None
    records = memory_use.read(root=root, since=since)
    rows = [{"day": day, "role": role, **counts}
            for (day, role), counts in memory_use.per_role_day(records).items()]
    if args.json:
        result = {"rows": rows, "skipped": records.skipped, "log": records.path}
        print(json.dumps({"ok": True, "command": args.command, "result": result, "session": args.session}))
        return 0
    for row in rows:
        print(f"{row['day']} {row['role']} retrieves {row['retrieves']} briefs {row['briefs']} "
              f"refused {row['refused']}")
    return 0
