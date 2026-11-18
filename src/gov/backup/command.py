"""``gov backup [--dest <dir>] [--name <name>] [--keep <n>] [--days <n>]`` as a command module (W2-198 S1, S2, F1).

One git bundle of every ref of the repository of ``--root`` (any of its worktrees), verified, in ``<dest>`` as
``<name>-<YYYYMMDDTHHMMSSZ>.bundle``; then the retention (the newest ``--keep``, the newest of each of the last
``--days`` UTC days). ``<dest>`` is ``$GOV_BACKUP_ROOT/<name>/`` (default ``~/.gov-os/backups/<name>/``); the clock is
``GOV_BACKUP_NOW`` when set. It prints its own output (one line, or the envelope under ``--json``) and ends with 0, or
1 with ``BACKUP_FAILED``, ``BACKUP_VERIFY_FAILED`` or ``BACKUP_DEST_INSIDE`` on stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HELP = "one verified git bundle of every ref, outside the tree, with a retention (keep N and one a day)"
CLASS = "act"
ACT_PATHS = ()  # it writes outside the project only
CHILD_EXIT_CODE = True
EXIT_CODES = {}


def _count(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number") from None
    if value < 0:
        raise argparse.ArgumentTypeError(f"{text!r} is below 0")
    return value


def add_arguments(parser) -> None:
    parser.add_argument("--dest", metavar="<dir>", help="the folder itself (default $GOV_BACKUP_ROOT/<name>/)")
    parser.add_argument("--name", metavar="<name>", help="the bundle's name (default the main worktree's folder name)")
    parser.add_argument("--keep", type=_count, default=48, metavar="<n>", help="the newest bundles kept (default 48)")
    parser.add_argument("--days", type=_count, default=30, metavar="<n>",
                        help="the days of the last one bundle each is kept (default 30)")


def run(root: Path, args, config: dict) -> int:
    from gov.backup.bundle import BackupError, run_backup

    try:
        result = run_backup(Path(root), args.dest, args.name, args.keep, args.days)
    except BackupError as error:
        if args.json:
            envelope = {"ok": False, "command": "backup", "result": {}, "session": args.session,
                        "error": {"code": error.code, "message": error.message, "details": {}}}
            print(json.dumps(envelope))
        else:
            print(f"gov backup: {error.code}: {error.message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"ok": True, "command": "backup", "result": result, "session": args.session}))
    else:
        print(f"{result['file']}: {result['refs']} refs, verified, kept {result['kept']}, "
              f"removed {len(result['removed'])}")
    return 0
