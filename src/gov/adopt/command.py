"""``gov adopt --lite`` as a command module (W1-41, DEC-090, DEC-517). The convention is in ``gov.cli.main``.

``gov adopt --lite --stage <A0|A1|A2|AS|A3|A4|A5|A6|A7|A8|A9|A10|MA> [--map <file>] [--verdict <path>]`` runs one stage
of the adoption of the project, which commits its evidence record under ``governance/adoption/`` and refuses without
the record of the stage before it. ``gov adopt`` without ``--lite`` stays reserved: the full transaction is Wave 3.

W2-192: ``AS`` is the spec audit (DEC-1200), after A2 and before A3: ``AS-spec-audit.md`` lists the specs, what is
built of each, the tickets, and each gap as a question to the owner; A3 refuses without it (``spec_audit``).

W2-88: ``MA --out <folder>`` is the memory assessment and the refactoring plan (files under ``<folder>`` outside the
project, none in it); A3 takes ``--assessment <folder>`` and cites that assessment; ``A9 --out <folder> [--decision
DEC-n]... [--questions <file>] [--budget-ms N]`` builds the memory fabric (A9 lite) after A8.

W2-174: ``--verify-list``, ``--verify-apply <answers-file>`` (with the global ``--session``) and ``--facts`` need no
``--lite``: the Verify pass of an adopted repository's tickets (``verify_pass``) and its facts file (``facts``).
"""

from __future__ import annotations

from pathlib import Path

ACT_PATHS = ("**",)  # A6 moves and A8 retires what the audited path map names, wherever it lies in the project
STAGES = ("A0", "A1", "A2", "AS", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "MA")
_parser = None  # the command's own parser, kept for the usage error of --lite without --stage


def add_arguments(parser) -> None:
    global _parser
    _parser = parser
    parser.add_argument("--lite", action="store_true", help="the Wave 1 adoption: one stage per call")
    parser.add_argument("--stage", choices=STAGES, help="the stage to run")
    parser.add_argument("--map", metavar="<file>", help="A3: the proposal, a YAML file outside the project")
    parser.add_argument("--verdict", metavar="<path>", help="A5: the auditor's committed verdict record")
    parser.add_argument("--out", metavar="<folder>", help="MA, A9: where the assessment, the plan and the audit's "
                                                          "records are written: a folder outside the project")
    parser.add_argument("--assessment", metavar="<folder>", help="A3: the folder holding memory-assessment.json for "
                                                                 "HEAD's commit (MA's --out); A3 cites it")
    parser.add_argument("--decision", action="append", metavar="DEC-n", help="A9: the owner's decision that names a "
                                                                             "setting that differs from the standard "
                                                                             "(DEC-n, or DEC-n:setting); repeatable")
    parser.add_argument("--questions", metavar="<file>", help="A9: the questions to run end to end (w2-88-questions/1)")
    parser.add_argument("--budget-ms", type=int, metavar="<N>", help="A9: the vector scan's budget in milliseconds "
                                                                      "(default: fabric.RETRIEVE_BUDGET_MS)")
    parser.add_argument("--verify-list", action="store_true", help="W2-174: the open tickets' KPI lines with no verify "
                                                                       "and the launch fields they lack")
    parser.add_argument("--verify-apply", metavar="<answers-file>", help="W2-174: append the answers file's Verify "
                                                                         "clauses and write its launch fields (needs --session)")
    parser.add_argument("--facts", action="store_true", help="W2-174: write governance/project/facts.yaml if absent")


def _steps(root: Path, args) -> dict:
    """W2-174: ``--verify-list``, ``--verify-apply <answers-file>`` (the Verify pass) and ``--facts`` (the facts file)."""
    import datetime

    chosen = [flag for flag, on in (("--verify-list", args.verify_list), ("--verify-apply", args.verify_apply),
                                    ("--facts", args.facts)) if on]
    if len(chosen) > 1 or args.lite:
        _parser.error(f"{chosen[0]} goes alone: not with " + (" or ".join(chosen[1:]) if len(chosen) > 1 else "--lite"))
    today = datetime.datetime.now(datetime.timezone.utc).date()
    if args.facts:
        from gov.adopt import facts
        return facts.write_default(root, today)
    from gov.adopt import verify_pass
    if args.verify_list:
        found = verify_pass.missing(root)
        return {"missing": found, "text": "\n".join(" ".join([item["ticket"], *item["labels"], *item["fields"]])
                                                   for item in found) or "none"}
    if not args.session:
        _parser.error("--verify-apply needs --session <id>: the marker line carries it")
    return {"changed": verify_pass.apply(root, args.verify_apply, args.session, today)}


def run(root: Path, args, config: dict) -> dict:
    if args.verify_list or args.verify_apply or args.facts:
        return _steps(Path(root).resolve(), args)
    if not args.lite:
        from gov.cli.errors import not_implemented
        raise not_implemented("adopt")
    if not args.stage:
        _parser.error("--lite needs --stage, one of " + ", ".join(STAGES))
    from gov.adopt import stages
    return stages.run(Path(root).resolve(), args, config)
