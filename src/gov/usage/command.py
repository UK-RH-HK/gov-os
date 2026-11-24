"""``gov usage daily [--date D] | show [--date D] [--days N]``: usage and context per repository, role and session
(W2-207, DEC-1246 (3)(c)). ``daily`` writes ``~/.gov-os/usage/<D>.json``; ``show`` prints and never writes. Dollars are
a list-price estimate (``governance/project/usage-prices.yaml``)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HELP = "usage and context per repository, role and session, daily (daily, show)"
CLASS = "act"
ACT_PATHS = ()
CHILD_EXIT_CODE = True


def add_arguments(parser) -> None:
    sub = parser.add_subparsers(dest="usage_command", metavar="<daily|show>", required=True)
    for name, text in (("daily", "write the day's record to ~/.gov-os/usage/<D>.json"),
                       ("show", "print the day (or N days) per repository; writes nothing")):
        each = sub.add_parser(name, help=text, allow_abbrev=False)
        each.add_argument("--root", metavar="<path>", default=argparse.SUPPRESS, help="the project")
        each.add_argument("--date", metavar="<D>", default=None, help="the UTC day, YYYY-MM-DD (default: today)")
        if name == "show":
            each.add_argument("--days", metavar="<N>", type=int, default=1, help="the last N days, one line per repository")


def run(root: Path, args, config: dict) -> int:
    from gov.usage import record

    try:
        day = record.parse_day(args.date)
        if args.usage_command == "daily":
            path, rec = record.write_daily(root, day)
            print(f"usage daily: {day} written to {path} ({len(rec['rows'])} rows, "
                  f"{rec['skipped_lines']} skipped lines; dollars are a list-price estimate)")
            return 0
        days = max(1, getattr(args, "days", 1) or 1)
        print("\n".join(record.show_lines(root, day, days)))
        return 0
    except record.UsageError as exc:
        print(f"gov usage: {exc}", file=sys.stderr)
        return 2
