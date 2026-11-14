"""``gov skilleval <skill> [--adopt]`` as a command module (W2-104, DEC-959 item 5, DEC-317).

An act command: it runs each of a skill's three scenarios on a fresh model session with only that skill
loaded, judges each against its pass line in a second session, and appends the verdicts to
``scenario-records.yaml`` beside the skill. With ``--adopt`` it marks the skill's entry in
``governance/project/skill-imports.yaml`` adopted, only with a licence record and three passes. The
convention is in ``gov.cli.main``; the harness is ``gov.skilleval.harness``.
"""

from __future__ import annotations

from pathlib import Path

HELP = "run a skill's three scenarios on fresh sessions and record the verdicts (--adopt: adopt an import)"
CLASS = "act"
ACT_PATHS = ("**/scenario-records.yaml", "governance/project/skill-imports.yaml")
EXIT_CODES = {
    3: "a scenario failed",
    4: "no scenario failed and one or more was not run",
    5: "the skill cannot be evaluated (SKILL.md, its version or three complete scenarios missing)",
    6: "adoption refused",
}


def add_arguments(parser) -> None:
    parser.usage = ("gov skilleval <skill> [--adopt] [--model <model>] [--effort <effort>] "
                    "[--timeout <seconds>] [--json] [--root <path>]")
    parser.add_argument("skill", metavar="<skill>", help="the skill's folder, relative to the project or absolute")
    parser.add_argument("--adopt", action="store_true",
                        help="mark the skill's import adopted, only with a licence record and three passes")
    parser.add_argument("--model", metavar="<model>", help="the model (default: the role default)")
    parser.add_argument("--effort", metavar="<effort>", help="the effort (default: the role default)")
    parser.add_argument("--timeout", type=float, default=900.0, metavar="<seconds>",
                        help="a model process past this many seconds is not run (default 900)")


def run(root: Path, args, config: dict):
    from gov.skilleval.harness import evaluate
    return evaluate(root, args.skill, adopt_import=args.adopt, model=args.model, effort=args.effort,
                    timeout=args.timeout)
