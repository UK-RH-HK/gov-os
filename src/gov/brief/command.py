"""``gov brief <role> <ticket> [--run <kind>] [--part <file>] [--repair <file>] [--root <repo>] [--json]`` (W2-152).

Prints the filled T-0 (``template/governance/kernel/templates/brief.md``) for the role, from the ticket file,
``governance/project/facts.yaml`` and the kernel templates; for a lead, the one run block of T-7 that ``--run``
names follows it. Without ``--json`` stdout is the brief alone, and the ready check's warnings and the size line go to
stderr, each ``gov brief: <CODE> <detail>``; with ``--json``, gov's envelope with ``result.brief``,
``result.warnings``, ``result.size`` and ``result.budget``. A ticket that is not READY, a placeholder left over, a KPI
line without a verify or an "until <ticket>" line whose ticket is closed is refused: ``GovError("BRIEF_NOT_READY")``
with ``details.findings`` (each ``{code, detail}``), nothing on stdout but ``--json``'s envelope. It writes no file.
"""

from __future__ import annotations

from gov.brief import ROLE_TEMPLATES, RUN_KINDS

CLASS = "read"
HELP = "a filled brief from the ticket and the facts file, refused when the ticket is not READY"
CHILD_EXIT_CODE = True  # stdout is the brief itself, never gov's default rendering of a result


def add_arguments(parser) -> None:
    parser.add_argument("brief_role", metavar="<role>", choices=tuple(ROLE_TEMPLATES),
                        help="engineer, independent-test-designer, independent-auditor, product-spec, research or lead")
    parser.add_argument("ticket", metavar="<ticket>", help="a tk id (DAEO-...) or a W2 id, resolved in <root>/.tickets/")
    parser.add_argument("--run", metavar="<kind>", choices=RUN_KINDS, help="the lead's run: " + "|".join(RUN_KINDS))
    parser.add_argument("--part", metavar="<file>", help="what the lead knows: fills {LEAD_NOTE}")
    parser.add_argument("--repair", metavar="<file>", help="the repair input: fills {REPAIR}")


def _line(finding: dict) -> str:
    return f"gov brief: {finding['code']}" + (f" {finding['detail']}" if finding["detail"] else "")


def run(root, args, config):
    import json
    import sys
    from pathlib import Path

    from gov.brief.build import build
    from gov.cli.errors import GovError

    out = build(Path(root), args.brief_role, args.ticket, run=args.run, part=args.part, repair=args.repair)
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
        result = {"brief": out["brief"], "warnings": out["warnings"], "size": out["size"], "budget": out["budget"]}
        print(json.dumps({"ok": True, "command": "brief", "result": result, "session": args.session}))
    else:
        sys.stdout.write(out["brief"])
    return 0
