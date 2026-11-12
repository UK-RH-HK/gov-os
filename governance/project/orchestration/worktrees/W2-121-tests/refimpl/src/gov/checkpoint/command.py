"""``gov checkpoint`` as a command module (W1-25, DEC-317). The convention is in ``gov.cli.main``.

- ``gov checkpoint --ticket <id> --trigger <trigger> --next <text> [--input <path>]...`` writes a checkpoint
  (DEC-279) under ``docs/checkpoints/<ticket>/`` (DEC-320).
- ``gov checkpoint --watch --ticket <id>`` judges the latest checkpoint and only reads (DEC-280, DEC-281).
- ``gov checkpoint --resume [--ticket <id>]`` gives the resume brief from the latest checkpoint alone; without
  ``--ticket``, of every ticket that has a checkpoint, which is the fresh-agent-reconstruction check (DEC-282).
"""

from __future__ import annotations

from pathlib import Path

ACT_PATHS = ("docs/checkpoints/**",)
EXIT_UNHEALTHY = 3
EXIT_CODES = {EXIT_UNHEALTHY: "the latest checkpoint is stale, or the ticket has none"}

TRIGGERS = ("ticket-transition", "compaction", "stop")  # DEC-280
# The watchdog's kernel defaults (DEC-321, DEC-281): 4 hours, 20 commits, 30 % of the context window.
MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT = 240, 20, 0.30


def add_arguments(parser) -> None:
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--watch", action="store_true", help="judge the latest checkpoint of --ticket; only reads")
    mode.add_argument("--resume", action="store_true", help="the resume brief from the latest checkpoint; only reads")
    parser.add_argument("--ticket", metavar="<id>", help="the ticket")
    parser.add_argument("--trigger", metavar="<trigger>", help=" or ".join(TRIGGERS))
    parser.add_argument("--next", metavar="<text>", help="the next step, for the session that resumes")
    parser.add_argument("--input", metavar="<path>", action="append", default=[],
                        help="an input file, recorded with its hash (the ticket file always is); repeatable")
    parser.add_argument("--max-age-minutes", metavar="<n>", type=float, default=MAX_AGE_MINUTES,
                        help=f"--watch: stale when older (default {MAX_AGE_MINUTES})")
    parser.add_argument("--max-commits", metavar="<n>", type=int, default=MAX_COMMITS,
                        help=f"--watch: stale after more commits on the branch (default {MAX_COMMITS})")
    parser.add_argument("--max-context", metavar="<fraction>", type=float, default=MAX_CONTEXT,
                        help=f"--watch: stale above this context utilisation (default {MAX_CONTEXT})")
    parser.add_argument("--context-utilisation", metavar="<fraction>", type=float,
                        help="--watch: the caller's context utilisation; without it, context is not judged")


def run(root: Path, args, config: dict) -> dict:
    from gov.checkpoint import record

    if args.watch:
        return record.watch(root, args.ticket, args.max_age_minutes, args.max_commits, args.max_context,
                            args.context_utilisation)
    if args.resume:
        return record.brief(root, args.ticket) if args.ticket else {"briefs": record.briefs(root)}
    return record.write(root, args.ticket, args.trigger, args.next, args.input)
