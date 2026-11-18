"""``gov brief <role> <ticket> [--run <kind>] [--part <file>] [--repair <file>] [--store <dir>] [--root <repo>]
[--json]`` (W2-152, W2-197).

Prints the filled T-0 (``template/governance/kernel/templates/brief.md``) for the role, from the ticket file,
``governance/project/facts.yaml`` and the kernel templates; for a lead, the one run block of T-7 that ``--run``
names follows it. Without ``--json`` stdout is the brief alone, and the ready check's warnings and the size line go to
stderr, each ``gov brief: <CODE> <detail>``; with ``--json``, gov's envelope with ``result.brief``,
``result.warnings``, ``result.size``, ``result.budget`` and ``result.memory`` (W2-197 S1: the ticket's retrieval, as
``gov.brief.memory.public`` gives it). A store that is missing or cannot be read is the warning
``gov brief: MEMORY_UNAVAILABLE <detail>`` and the block's not-reached line, never a refusal (F1). A ticket that is
not READY, a placeholder left over, a KPI line without a verify or an "until <ticket>" line whose ticket is closed is
refused: ``GovError("BRIEF_NOT_READY")`` with ``details.findings`` (each ``{code, detail}``), nothing on stdout but
``--json``'s envelope. It writes one file only: the retrieval's line in the memory-use log (``gov.memory_use``, S8),
which never changes what is printed (F2). A brief that judges work (independent-auditor, qa-engineer, the lead's
``review`` run) carries sections 1 to 3 of the installed judging-work skill and names its version, or is refused
``BRIEF_JUDGING_RULE_MISSING`` (W2-195, ``gov.brief.judging``).
"""

from __future__ import annotations

from gov.brief import ROLE_TEMPLATES, RUN_KINDS

CLASS = "read"
HELP = "a filled brief from the ticket and the facts file, refused when the ticket is not READY"
CHILD_EXIT_CODE = True  # stdout is the brief itself, never gov's default rendering of a result


def add_arguments(parser) -> None:
    parser.add_argument("brief_role", metavar="<role>", choices=tuple(ROLE_TEMPLATES),
                        help="engineer, independent-test-designer, independent-auditor, qa-engineer, product-spec, "
                             "research or lead")
    parser.add_argument("ticket", metavar="<ticket>", help="a tk id (DAEO-...) or a W2 id, resolved in <root>/.tickets/")
    parser.add_argument("--run", metavar="<kind>", choices=RUN_KINDS, help="the lead's run: " + "|".join(RUN_KINDS))
    parser.add_argument("--part", metavar="<file>", help="what the lead knows: fills {LEAD_NOTE}")
    parser.add_argument("--repair", metavar="<file>", help="the repair input: fills {REPAIR}")
    parser.add_argument("--store", metavar="<dir>",
                        help="the store the ticket's retrieval answers from (default: GOV_STORE, facts.yaml's "
                             "paths.store_tree, the root)")


def _line(finding: dict) -> str:
    return f"gov brief: {finding['code']}" + (f" {finding['detail']}" if finding["detail"] else "")


def run(root, args, config):
    import json
    import os
    import sys
    from pathlib import Path

    from gov import memory_use
    from gov.brief import memory
    from gov.brief.build import build
    from gov.cli.errors import GovError

    spent = {}
    out = build(Path(root), args.brief_role, args.ticket, run=args.run, part=args.part, repair=args.repair,
                store=args.store, spent=spent)
    if out["memory"] is not None:  # S8: the brief's retrieval is logged; a log fault changes nothing (F2)
        session = args.session or os.environ.get("GOV_SESSION") or None
        memory_use.append(memory.record(out["memory"], args.brief_role, out["ticket"], session,
                                        spent.get("latency_ms", 0)), root)
    for warning in out["warnings"]:
        print(_line(warning), file=sys.stderr)
    print(f"gov brief: SIZE {out['size']} of {out['budget']} (budgets.brief, prose characters)", file=sys.stderr)
    if out["findings"]:
        for finding in out["findings"]:
            print(_line(finding), file=sys.stderr)
        listed = "; ".join(_line(finding)[len("gov brief: "):] for finding in out["findings"])
        raise GovError("BRIEF_NOT_READY", f"{out['ticket']} is not ready for a brief: {listed}",
                       {"ticket": out["ticket"], "findings": out["findings"]})
    if args.json:
        result = {"brief": out["brief"], "warnings": out["warnings"], "size": out["size"], "budget": out["budget"],
                  "memory": memory.public(out["memory"]) if out["memory"] is not None else None}
        print(json.dumps({"ok": True, "command": "brief", "result": result, "session": args.session}))
    else:
        sys.stdout.write(out["brief"])
    return 0
