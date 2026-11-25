"""``python3 -m gov.memaudit preflight|void|declare|measure|judge|classes|pool|pool-import|run|due|baseline|status|figures``
(Interface section 1; S1-S8, F1; W2-172 adds the last five), and W2-187's ``standing declare|run|live``, ``maintain`` and ``push``.

A thin wrapper: each subcommand calls its module's entry point and prints, through ``say`` only, the lines it produces
(the W2-171 subcommands print as they go, a line at a time). Exit codes: 0 ok, 1 refused, 2 void or stopped (the owner
decides), 3 used, 4 usage (a flag or value refused, argparse's own error, a line ``say`` refused, or any unexpected error,
printed as the one line ``ERROR: <class>``).
"""

from __future__ import annotations

import argparse
import sys
import warnings

from gov.memaudit import EXIT
from gov.memaudit.common import UsageError
from gov.memaudit.config import ConfigError
from gov.memaudit.say import say


class _Parser(argparse.ArgumentParser):
    """argparse with its error turned into exit 4 (no text of the value printed) and its help printed by ``say``."""

    def error(self, message):
        raise UsageError("argparse")

    def _print_message(self, message, file=None):
        for line in (message or "").rstrip("\n").splitlines():
            say(line)


def _week(sp):
    sp.add_argument("--week", metavar="YYYY-Www", help="a standing set's ISO week: the step works on that week's folder")


def _common(sp):
    sp.add_argument("--sets-root", required=True, metavar="ROOT",
                    help="the sets root; every folder under it is derived from it and the audit's name")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the audit's name, memory-audit-<8 digits>")


def parser() -> argparse.ArgumentParser:
    ap = _Parser(prog="python3 -m gov.memaudit",
                 description="The memory audit's set record and measure: the checks before any search, the drop and "
                             "void rule, the declaration and the use-once marker, the control and the attempts, the "
                             "judged reader run, the regression pool. Counts only.")
    sub = ap.add_subparsers(dest="command", required=True, metavar="SUBCOMMAND", parser_class=_Parser)
    pf = sub.add_parser("preflight", help="the ten checks of the set before any search",
                        description="The ten checks of the delivered set before any search; writes PREFLIGHT.json.")
    _common(pf)
    pf.add_argument("--repo", metavar="DIR", help="the git repository holding the commit (default: the top level)")
    pf.add_argument("--commit", required=True, metavar="REV", help="the audit commit")
    pf.add_argument("--runs-dir", metavar="DIR",
                    help="the launch script's folder holding indep/AUDITS.log and indep/SEEDS.log "
                         "(default: $GOV_INDEP_RUNS_DIR, else ~/gov-os-runs)")
    _week(pf)
    vd = sub.add_parser("void", help="the drop and void rule after the checker's last pass",
                        description="Moves every question the notes do not accept aside (never deleted), recomputes "
                                    "the scales on the kept ones and writes DROPS.json; exit 2 when the audit is void.")
    _common(vd)
    vd.add_argument("--repo", metavar="DIR", help="the git repository whose configuration and records are read "
                                                  "(default: the top level)")
    dc = sub.add_parser("declare", help="the set's map entry, DECLARATION.json, then USED",
                        description="The set's entry in the sets root's own path map, then DECLARATION.json, then "
                                    "USED, then the ledger lines; refuses while USED exists.")
    _common(dc)
    dc.add_argument("--repo", metavar="DIR", help="the git repository holding the commit (default: the top level)")
    dc.add_argument("--commit", required=True, metavar="REV", help="the audit commit")
    dc.add_argument("--store", metavar="FILE", help="the store to declare (default: <repo>/.gov-runtime/store.db)")
    dc.add_argument("--gov", metavar="PATH", help="the gov executable whose pin is declared (default: ~/.local/bin/gov)")
    dc.add_argument("--decision", metavar="DEC-N", help="the decision that allows a non-standard retrieval.yaml")
    _week(dc)

    ms = sub.add_parser("measure", help="the declaration, the control, the attempts and the retrieval figures",
                        description="declare, then the ready check, the control (the visible 40) and the attempts "
                                    "with the fault rule; the RETRIEVAL line. With --kept <n>: re-score attempt-<n>'s "
                                    "kept outputs, writing nothing. Exit 2: STOPPED <cause>, to the owner.")
    _common(ms)
    ms.add_argument("--repo", metavar="DIR", help="the git repository holding the commit (default: the top level)")
    ms.add_argument("--commit", metavar="REV", help="the audit commit (required unless --kept)")
    ms.add_argument("--store", metavar="FILE", help="the store measured (default: <repo>/.gov-runtime/store.db)")
    ms.add_argument("--gov", metavar="PATH", help="the gov executable (default: ~/.local/bin/gov)")
    ms.add_argument("--decision", metavar="DEC-N", help="the decision that allows a non-standard retrieval.yaml")
    ms.add_argument("--kept", type=int, metavar="N", help="re-score attempt-<N>'s kept outputs; nothing is written")
    _week(ms)
    jd = sub.add_parser("judge", help="the judged reader run, the verdict, the misses and FIGURES.json",
                        description="The reader answers each question from its searches, search again once; a named "
                                    "grader judges, a second grader's agreement beside it; writes misses.jsonl and "
                                    "FIGURES.json. --resume continues after a brake stop, with a raised --projection.")
    _common(jd)
    jd.add_argument("--repo", metavar="DIR", help="the git repository at the audit commit (default: the top level)")
    jd.add_argument("--gov", metavar="PATH", help="the gov executable (default: ~/.local/bin/gov)")
    jd.add_argument("--claude", metavar="EXE", help="the claude executable (default: ~/.local/bin/claude)")
    jd.add_argument("--projection", type=float, metavar="USD", help="the spend projected (default: 0.157 x n)")
    jd.add_argument("--resume", action="store_true", help="continue a run the brake stopped")
    _week(jd)
    cl = sub.add_parser("classes", help="the auditor's five class counts into FIGURES.json",
                        description="Reads miss-classes.json and adds the five class counts to FIGURES.json.")
    _common(cl)
    pl = sub.add_parser("pool", help="the regression pool's re-run, then the audit's questions join it",
                        description="Re-runs the pool through the retrieval measure only (the whole pool up to 400 "
                                    "questions, else a seeded draw of 400), names a regression, then adds the audit's "
                                    "questions to the pool.")
    _common(pl)
    pl.add_argument("--repo", metavar="DIR", help="the git repository at the audit commit (default: the top level)")
    pl.add_argument("--gov", metavar="PATH", help="the gov executable (default: ~/.local/bin/gov)")
    pl.add_argument("--seed", type=int, metavar="N", help="the draw's seed (default: from the audit and the pool)")
    pi = sub.add_parser("pool-import", help="the one-time import of the earlier sets into the pool",
                        description="Copies the 79 questions of the fresh 80 and the 138 of the earlier sets into the "
                                    "pool; run once by the CTO.")
    pi.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    pi.add_argument("--sets", nargs="+", metavar="NAME",
                    help="import exactly these sets' kept questions (default: the 79 and the 138, as before)")
    _driver(sub)
    _adopted(sub)
    return ap


def _adopted(sub):
    """W2-204: the steps an adopted repository's CTO runs (Interface I3 to I5)."""
    ck = sub.add_parser("check", help="the repository's memory-audit configuration: ok, or its first fault",
                        description="Reads governance/project/memory-audit.yaml (the file MEMAUDIT_CONFIG names, "
                                    "else the commit's, else the working tree's) and prints its counts or its first fault.")
    ck.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    ck.add_argument("--commit", metavar="REV", help="the commit whose file and tracked paths are read (default: the "
                                                    "working tree's file, HEAD's tracked paths)")
    ck.add_argument("--sets-root", metavar="ROOT", help=argparse.SUPPRESS)
    from gov.memaudit import brief, deliver, fresh, writercheck, writerrun
    brief.add_arguments(sub.add_parser("brief", help="a writer's or checker's brief, filled from the configuration",
                                       description=brief.DESCRIPTION))
    deliver.add_arguments(sub.add_parser("deliver", help="take a writer's set or a checker's notes into the sets root",
                                         description=deliver.DESCRIPTION))
    writercheck.add_arguments(sub.add_parser("writer-check", help="the Stop hook of a writer's session",
                                             description=writercheck.DESCRIPTION))
    writerrun.add_arguments(sub.add_parser("writer-run", help="a writer's session run with its check in the loop",
                                           description=writerrun.DESCRIPTION))
    fresh.add_arguments(sub.add_parser("fresh", help="a whole fresh pair of halves on a pinned snapshot it builds",
                                       description=fresh.DESCRIPTION))


def _check(args, emit) -> str:
    from gov.memaudit import config
    from gov.memaudit.common import resolve_commit, toplevel
    from pathlib import Path
    repo = Path(args.repo) if args.repo else toplevel()
    if args.commit:
        cfg = config.load(repo, resolve_commit(repo, args.commit))
    else:
        cfg = config.load(repo, tree=resolve_commit(repo, "HEAD"))
    emit(f"CONFIG ok half {cfg.half_size} categories {len(cfg.categories)} domains {len(cfg.domains)} "
         f"subsystems {len(cfg.subsystems)} control {cfg.control.set if cfg.control else 'none'}")
    return "ok"


def _driver(sub):
    """W2-172: the cycle and its schedule (Interface item 1)."""
    def base(name, help_text, repo=True):
        sp = sub.add_parser(name, help=help_text, description=help_text)
        sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root (never opened by the driver)")
        if repo:
            sp.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
        return sp

    rn = base("run", "one audit through the launch script, in order; counts only")
    rn.add_argument("--store-link", metavar="PATH", help="the integration store's link (default: rebuild.yaml's)")
    rn.add_argument("--launch", metavar="FILE", help="the launch script (default: <repo>/governance/project/"
                                                     "orchestration/tools/indep_launch.py)")
    rn.add_argument("--gov", metavar="EXE", help="passed on to measure, judge and pool")
    rn.add_argument("--claude", metavar="EXE", help="passed on to judge")
    rn.add_argument("--gate-cmd", metavar="CMD", help="the gate's check, split into words; exit 0 is open (default: none)")
    rn.add_argument("--force", action="store_true", help="the owner's word: lifts the 5-day refusal only")
    du = base("due", "whether an audit is due now, its mode and the reason")
    du.add_argument("--store-link", metavar="PATH", help="the integration store's link (default: rebuild.yaml's)")
    du.add_argument("--fresh", action="store_true", help="the fresh set's cadence (with a live standing set)")
    bl = base("baseline", "the first line of the audits' log: the commit the first audit's changes start from")
    bl.add_argument("--commit", required=True, metavar="REV", help="the baseline commit")
    stt = base("status", "audited, or not audited and the next due date, for a retrieval change since a commit")
    stt.add_argument("--since", metavar="REV", help="the commit to look from (required without --repair)")
    stt.add_argument("--store-link", metavar="PATH", help="the integration store's link (default: rebuild.yaml's)")
    stt.add_argument("--repair", action="store_true", help="whether a memory repair is open: exit 1 while it is")
    stt.add_argument("--residual", metavar="DEC-N", help="with --repair: the owner's decision that closes it")
    fg = base("figures", "one JSON line of an audit's figures, numbers and fixed words only", repo=False)
    fg.add_argument("--audit", required=True, metavar="NAME", help="the audit's name, memory-audit-<8 digits>")
    _week(fg)
    mt = base("maintain", "the weekly maintenance pass: six counts, never a gate")
    mt.add_argument("--store-link", metavar="PATH", help="the integration store's link (default: rebuild.yaml's)")
    mt.add_argument("--gov", metavar="EXE", help="the gov executable (default: ~/.local/bin/gov)")
    from gov.memaudit import push
    push.add_arguments(sub.add_parser("push", help="the weekly secret scan, then the push on a clean scan",
                                      description="The weekly secret scan and push (W2-187 I13): one line."))
    sg = sub.add_parser("standing", help="the standing question set: declare, run, live",
                        description="The repository's standing set of questions: judged once a week, counts only.")
    ss = sg.add_subparsers(dest="standing_command", required=True, metavar="SUBCOMMAND", parser_class=_Parser)
    sd = ss.add_parser("declare", help="record one standing set for the repository")
    sd.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sd.add_argument("--set", required=True, dest="set_name", metavar="NAME", help="the set's name")
    sd.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sd.add_argument("--runs-dir", metavar="DIR", help="the launch script's folder (default: $GOV_INDEP_RUNS_DIR, "
                                                       "else ~/gov-os-runs)")
    sd.add_argument("--replaces", metavar="NAME", help="the live set a thin one replaces")
    sr = ss.add_parser("run", help="one judged run of the live standing set, once a week")
    sr.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sr.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sr.add_argument("--store-link", metavar="PATH", help="the integration store's link (default: rebuild.yaml's)")
    sr.add_argument("--gov", metavar="EXE", help="passed on to measure and judge")
    sr.add_argument("--claude", metavar="EXE", help="passed on to judge")
    sr.add_argument("--gate-cmd", metavar="CMD", help="the gate's check, split into words; exit 0 is open")
    sl = ss.add_parser("live", help="the repository's key and its live standing set; writes nothing")
    sl.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sl.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")


GUARDED = ("preflight", "void", "declare", "measure", "judge", "classes", "pool")


def _standing(args, emit) -> str:
    sub = args.standing_command
    from gov.memaudit import standing
    if sub == "declare":
        word, counts = standing.declare(args.sets_root, args.set_name, repo=args.repo, runs_dir=args.runs_dir,
                                        replaces=args.replaces)
        for line in standing.lines(word, counts):
            emit(line)
        return word
    if sub == "run":
        from gov.memaudit import driver
        return driver.standing(args.sets_root, repo=args.repo, link=args.store_link, gov=args.gov, claude=args.claude,
                               gate_cmd=args.gate_cmd, emit=emit)
    from gov.memaudit import schedule
    state = schedule.state_of(args.repo)
    found = standing.live(state)
    emit(f"KEY {state.name}")
    emit(f"LIVE {found['set']}" if found else "LIVE none")
    return "ok" if found else "refused"


def _run(args, emit) -> str:
    cmd = args.command
    if cmd == "standing":
        return _standing(args, emit)
    if cmd == "check":
        return _check(args, emit)
    if cmd in ("brief", "deliver", "fresh", "writer-check", "writer-run"):
        import importlib
        return importlib.import_module(f"gov.memaudit.{cmd.replace('-', '')}").from_args(args, emit)
    from gov.memaudit import layout
    audit, week = getattr(args, "audit", None), getattr(args, "week", None)
    layout.check_week(week)
    if (cmd in GUARDED and not week and isinstance(audit, str) and layout.STANDING_RE.fullmatch(audit)
            and not (cmd == "measure" and args.kept is not None)):
        emit("MS-STANDING")  # a standing set is judged through ``standing run`` and its week folder only
        return "refused"
    if cmd == "preflight" and week:
        from gov.memaudit import preflight
        word, counts = preflight.standing(args.sets_root, args.audit, week=week, commit=args.commit, repo=args.repo)
        for line in preflight.standing_lines(word, counts):
            emit(line)
        return word
    if cmd == "preflight":
        from gov.memaudit import preflight
        word, counts = preflight.run(args.sets_root, args.audit, commit=args.commit, repo=args.repo,
                                     runs_dir=args.runs_dir)
        for line in preflight.lines(word, counts):
            emit(line)
        return word
    if cmd == "void":
        from gov.memaudit import drops
        word, counts = drops.apply(args.sets_root, args.audit, repo=args.repo)
        for line in drops.lines(word, counts):
            emit(line)
        return word
    if cmd == "declare":
        from gov.memaudit import declare
        word, counts = declare.declare(args.sets_root, args.audit, commit=args.commit, repo=args.repo,
                                       store=args.store, gov=args.gov, decision=args.decision, week=week)
        for line in declare.lines(word, counts):
            emit(line)
        return word
    if cmd == "measure":
        from gov.memaudit import measure
        if args.kept is not None:
            if args.kept < 1:
                raise UsageError("kept")
            return measure.rescore(args.sets_root, args.audit, args.kept, repo=args.repo, emit=emit, week=week)
        if not args.commit:
            raise UsageError("commit")
        return measure.run(args.sets_root, args.audit, commit=args.commit, repo=args.repo, store=args.store,
                           gov=args.gov, decision=args.decision, emit=emit, week=week)
    if cmd == "judge":
        from gov.memaudit import judge
        return judge.run(args.sets_root, args.audit, repo=args.repo, gov=args.gov, claude=args.claude,
                         projection=args.projection, resume=args.resume, emit=emit, week=week)
    if cmd == "classes":
        from gov.memaudit import classes
        return classes.run(args.sets_root, args.audit, emit=emit)
    if cmd == "pool":
        from gov.memaudit import pool
        return pool.run(args.sets_root, args.audit, repo=args.repo, gov=args.gov, seed=args.seed, emit=emit)
    if cmd == "run":
        from gov.memaudit import driver
        return driver.run(args.sets_root, repo=args.repo, link=args.store_link, launch=args.launch, gov=args.gov,
                          claude=args.claude, gate_cmd=args.gate_cmd, force=args.force, emit=emit)
    if cmd == "due":
        from gov.memaudit import schedule
        return schedule.due(args.sets_root, args.repo, args.store_link, emit, fresh=args.fresh)
    if cmd == "baseline":
        from gov.memaudit import schedule
        return schedule.baseline(args.sets_root, args.repo, args.commit, emit)
    if cmd == "status":
        from gov.memaudit import schedule, standing
        if args.repair:
            return standing.repair_status(args.sets_root, args.repo, args.residual, emit)
        if args.residual is not None or not args.since:
            raise UsageError("since")
        return schedule.status(args.sets_root, args.repo, args.since, args.store_link, emit)
    if cmd == "figures":
        from gov.memaudit import digest
        return digest.figures(args.sets_root, args.audit, emit, week)
    if cmd == "maintain":
        from gov.memaudit import maintain
        return maintain.run(args.sets_root, repo=args.repo, link=args.store_link, gov=args.gov, emit=emit)
    if cmd == "push":
        from gov.memaudit import push
        return push.from_args(args, emit)
    from gov.memaudit import pool
    return pool.importing(args.sets_root, emit=emit, sets=args.sets)


def main(argv=None) -> int:
    warnings.simplefilter("ignore")
    root = None
    try:
        args = parser().parse_args(argv)
        root = getattr(args, "sets_root", None)

        def emit(line):
            say(line, root)  # a refused line ends the process with exit 4

        return EXIT[_run(args, emit)]
    except SystemExit as e:  # --help: argparse's own exit 0; a line say refused: 4
        return 0 if e.code == 0 else EXIT["usage"]
    except ConfigError as e:  # the repository's configuration is absent or faulty: its one line, exit 1 (W2-204 I2)
        say(e.line, root)
        return EXIT["refused"]
    except BaseException as e:  # noqa: BLE001: one line, the class only; no traceback, no text (F1)
        say(f"ERROR: {type(e).__name__}", root, err=True)
        return EXIT["usage"]


if __name__ == "__main__":
    sys.exit(main())
