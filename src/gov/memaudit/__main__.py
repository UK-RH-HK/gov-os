"""``python3 -m gov.memaudit preflight|void|declare`` (Interface section 1; S6, S5, F1).

A thin wrapper: each subcommand calls its module's entry point and prints, through ``say`` only, the lines of the
counts it returns. Exit codes: 0 ok, 1 refused, 2 void, 3 used, 4 usage (a flag or value refused, argparse's own
error, a line ``say`` refused, or any unexpected error, printed as the one line ``ERROR: <class>``).
"""

from __future__ import annotations

import argparse
import sys
import warnings

from gov.memaudit import EXIT
from gov.memaudit.common import UsageError
from gov.memaudit.say import say


class _Parser(argparse.ArgumentParser):
    """argparse with its error turned into exit 4 (no text of the value printed) and its help printed by ``say``."""

    def error(self, message):
        raise UsageError("argparse")

    def _print_message(self, message, file=None):
        for line in (message or "").rstrip("\n").splitlines():
            say(line)


def _common(sp):
    sp.add_argument("--sets-root", required=True, metavar="ROOT",
                    help="the sets root; every folder under it is derived from it and the audit's name")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the audit's name, memory-audit-<8 digits>")


def parser() -> argparse.ArgumentParser:
    ap = _Parser(prog="python3 -m gov.memaudit",
                 description="The memory audit's set record: the checks before any search, the drop and void rule, "
                             "the declaration and the use-once marker. Counts only.")
    sub = ap.add_subparsers(dest="command", required=True, metavar="SUBCOMMAND", parser_class=_Parser)
    pf = sub.add_parser("preflight", help="the ten checks of the set before any search",
                        description="The ten checks of the delivered set before any search; writes PREFLIGHT.json.")
    _common(pf)
    pf.add_argument("--repo", metavar="DIR", help="the git repository holding the commit (default: the top level)")
    pf.add_argument("--commit", required=True, metavar="REV", help="the audit commit")
    pf.add_argument("--runs-dir", metavar="DIR",
                    help="the launch script's folder holding indep/AUDITS.log and indep/SEEDS.log "
                         "(default: $GOV_INDEP_RUNS_DIR, else ~/gov-os-runs)")
    vd = sub.add_parser("void", help="the drop and void rule after the checker's last pass",
                        description="Moves every question the notes do not accept aside (never deleted), recomputes "
                                    "the scales on the kept ones and writes DROPS.json; exit 2 when the audit is void.")
    _common(vd)
    dc = sub.add_parser("declare", help="the set's map entry, DECLARATION.json, then USED",
                        description="The set's entry in the sets root's own path map, then DECLARATION.json, then "
                                    "USED, then the ledger lines; refuses while USED exists.")
    _common(dc)
    dc.add_argument("--repo", metavar="DIR", help="the git repository holding the commit (default: the top level)")
    dc.add_argument("--commit", required=True, metavar="REV", help="the audit commit")
    dc.add_argument("--store", metavar="FILE", help="the store to declare (default: <repo>/.gov-runtime/store.db)")
    dc.add_argument("--gov", metavar="PATH", help="the gov executable whose pin is declared (default: ~/.local/bin/gov)")
    dc.add_argument("--decision", metavar="DEC-N", help="the decision that allows a non-standard retrieval.yaml")
    return ap


def _run(args) -> tuple[str, list[str]]:
    if args.command == "preflight":
        from gov.memaudit import preflight
        word, counts = preflight.run(args.sets_root, args.audit, commit=args.commit, repo=args.repo,
                                     runs_dir=args.runs_dir)
        return word, preflight.lines(word, counts)
    if args.command == "void":
        from gov.memaudit import drops
        word, counts = drops.apply(args.sets_root, args.audit)
        return word, drops.lines(word, counts)
    from gov.memaudit import declare
    word, counts = declare.declare(args.sets_root, args.audit, commit=args.commit, repo=args.repo, store=args.store,
                                   gov=args.gov, decision=args.decision)
    return word, declare.lines(word, counts)


def main(argv=None) -> int:
    warnings.simplefilter("ignore")
    root = None
    try:
        args = parser().parse_args(argv)
        root = args.sets_root
        word, out = _run(args)
        for line in out:
            say(line, root)  # a refused line ends the process with exit 4
        return EXIT[word]
    except SystemExit as e:  # --help: argparse's own exit 0; a line say refused: 4
        return 0 if e.code == 0 else EXIT["usage"]
    except BaseException as e:  # noqa: BLE001: one line, the class only; no traceback, no text (F1)
        say(f"ERROR: {type(e).__name__}", root, err=True)
        return EXIT["usage"]


if __name__ == "__main__":
    sys.exit(main())
