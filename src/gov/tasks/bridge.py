"""The proposal-to-ticket bridge (CAP-31.a, MR-2): the tasks of a closed specification become tickets.

A task is a checkbox line of ``openspec/changes/<change>/tasks.md``, ``- [ ] <number> <description>``, and its task
contract is the one map in the fenced ``yaml`` block indented two spaces under that line: ``role``, ``class``,
``profile``, ``allowed_paths``, ``kpis`` and, optionally, ``depends_on`` (task numbers of the file, or ids of
tickets that exist) and ``inputs``. The ticket carries them as the task wrote them, with ``specification``, the id
of the change's specification record (DEC-307, DEC-350), and ``task``, by which a second run finds it again.

The bridge is a gate and does not fail open: the specification is CLOSED and passes the readiness checker, and one
task that cannot become a ticket refuses the whole derivation. A refusal writes nothing. A task that has its ticket
keeps it, untouched. Tickets are written in the working tree and nothing is committed.
"""

from __future__ import annotations

import posixpath
import re
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.guard import decide as guard
from gov.readiness import checker
from gov.tasks import tickets

TASKS_INVALID, TASKS_NOT_FOUND, TICKET_FAILED = "TASKS_INVALID", "TASKS_NOT_FOUND", "TICKET_FAILED"
TEST_DESIGNER = "independent-test-designer"  # the one role that may hold tests/acceptance/** (MR-3)
PROBES = ("tests", "tests/acceptance", "tests/acceptance/x", "tests/acceptance/x/y")
TASK = re.compile(r"^- \[[ xX]\] (\S+) ?(.*)$")
FENCE = "  ```"


def _lines(value, least: int = 0) -> bool:
    """Whether ``value`` is a list of at least ``least`` non-empty strings."""
    return isinstance(value, list) and len(value) >= least \
        and all(isinstance(item, str) and item.strip() for item in value)


def _covers(pattern: str) -> bool:
    """Whether ``pattern``, read as the guard reads it, allows a path at or under ``tests/acceptance/``."""
    pattern = posixpath.normpath(pattern)
    return guard._is_under_acceptance(pattern.rstrip("*/ ")) \
        or any(guard._match_pattern(probe, pattern) for probe in PROBES)  # a folder covers what is under it


def _tasks(text: str) -> list[tuple[str, str, dict]]:
    """``(number, description, fields)`` of every task; no fields when its block is absent or is no YAML map."""
    import yaml

    found, lines = [], [line.rstrip() for line in text.split("\n")]
    for index, line in enumerate(lines):
        if not TASK.match(line):
            continue
        number, description = TASK.match(line).groups()
        rest = lines[index + 1:]
        block = rest[:next((i for i, after in enumerate(rest) if TASK.match(after) or after.startswith("#")),
                           len(rest))]
        try:
            start = block.index(FENCE + "yaml") + 1
            fields = yaml.safe_load("\n".join(inner[2:] for inner in block[start:block.index(FENCE, start)]))
        except (ValueError, yaml.YAMLError):
            fields = None
        found.append((number, description.strip(), fields if isinstance(fields, dict) else {}))
    return found


def _fault(fields: dict) -> str | None:
    """Why the fields of one task cannot be a ticket's; None when they can."""
    kpis, paths = fields.get("kpis"), fields.get("allowed_paths")
    if not all(isinstance(fields.get(key), str) and fields[key].strip() for key in ("role", "class")):
        return "role and class are required"
    if not isinstance(fields.get("profile"), str) or fields["profile"] not in checker.PROFILES:
        return f"the profile is not one of {', '.join(checker.PROFILES)}"
    if not _lines(paths, 1):
        return "allowed_paths is not a non-empty list of paths"
    if not (isinstance(kpis, dict) and _lines(kpis.get("success"), 1) and _lines(kpis.get("failure"))):
        return "kpis is not a map of success (at least one line) and failure (a list of lines)"
    if not all(_lines(fields.get(key, [])) for key in ("depends_on", "inputs")):
        return "depends_on and inputs are lists of strings (a task number is written in quotes)"
    if fields["role"] != TEST_DESIGNER and any(_covers(pattern) for pattern in paths):
        return f"allowed_paths covers {guard.ACCEPTANCE}/**, which only the {TEST_DESIGNER} may hold (MR-3)"
    return None


def _reaches_cycle(node: str, edges: dict, seen: dict) -> bool:
    """Whether a dependency cycle is reached from ``node``. ``seen`` holds the answers; an open node's is True."""
    if node not in seen:
        seen[node] = True
        seen[node] = any(_reaches_cycle(dep, edges, seen) for dep in edges.get(node, ()))
    return seen[node]


def _write(path: Path, fields: dict) -> None:
    """Put ``fields`` in the frontmatter of the ticket ``tk create`` wrote, in place of its assignee and deps."""
    import yaml

    lines = [line for line in path.read_text(encoding="utf-8").split("\n")
             if not line.startswith(("assignee:", "deps:"))]
    end = lines.index("---", 1)
    lines[end:end] = yaml.safe_dump(fields, sort_keys=False, width=1000).rstrip("\n").split("\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def derive(root: Path, change: str) -> dict:
    """Derive one ticket per task of the change ``openspec/changes/<change>``; the tickets of its tasks.

    Refuses with ``SPEC_NOT_CLOSED`` when the specification is not CLOSED or a required row is open, with
    ``TASKS_INVALID`` (``details["invalid"]`` names every faulty task) when a task cannot become a ticket, and
    with another ``GovError`` when the change, its specification record or its tasks cannot be read.
    """
    root = Path(root)
    found = [entry for entry in checker.specifications(root) if entry[1].parent.name == change]
    if len(found) != 1:
        raise GovError(checker.NOT_FOUND, f"{checker.CHANGES_REL}/{change}: no change with a specification record",
                       {"change": change})
    specification, record, front = found[0]
    if front.get("status") != "CLOSED":  # MR-2, DEC-307; rows that would pass do not close a specification
        raise GovError(checker.NOT_CLOSED, f"{specification}: the status is not CLOSED",
                       {"change": change, "specification": specification, "closed": False},
                       exit_code=checker.EXIT_OPEN)
    checker.check(root, specification)  # a status set by hand is not trusted (DEC-348)
    try:
        tasks = _tasks(record.with_name("tasks.md").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        tasks = []
    if not tasks:
        raise GovError(TASKS_NOT_FOUND, f"{checker.CHANGES_REL}/{change}/tasks.md cannot be read, or has no task",
                       {"change": change, "specification": specification})

    fronts = {path.stem: tickets.frontmatter(path) or {}
              for path in sorted((root / tickets.TICKETS_REL).glob("*.md"))}
    held = {str(front.get("task")): ticket for ticket, front in fronts.items()
            if front.get("specification") == specification}
    numbers = [number for number, _, _ in tasks]
    node = {number: held.get(number, number) for number in numbers}  # a task without a ticket is its number
    edges = {ticket: [str(dep) for dep in front.get("deps", [])] if isinstance(front.get("deps"), list) else []
             for ticket, front in fronts.items()}
    invalid = {}
    for number, description, fields in tasks:
        fault = _fault(fields)
        unknown = fault or [dep for dep in fields.get("depends_on", []) if dep not in node and dep not in fronts]
        if not re.fullmatch(r"\d+\.\d+", number) or numbers.count(number) > 1 or not description:
            invalid[number] = "the task has no number <group>.<n> of its own, or no description"
        elif fault:
            invalid[number] = fault
        elif unknown:
            invalid[number] = f"depends on {', '.join(unknown)}: no task of this file and no ticket"
        elif number not in held:
            edges[number] = [node.get(dep, dep) for dep in fields.get("depends_on", [])]
    seen = {}
    for number in numbers:
        if number not in invalid and _reaches_cycle(node[number], edges, seen):
            invalid[number] = "its dependencies lead to a cycle"
    if invalid:
        raise GovError(TASKS_INVALID, f"{change}: {len(invalid)} tasks cannot become tickets: "
                       + "; ".join(f"{number} ({reason})" for number, reason in invalid.items()),
                       {"change": change, "specification": specification,
                        "invalid": [{"task": number, "reason": reason} for number, reason in invalid.items()]})

    created = []
    try:
        for number, description, _ in tasks:
            if number not in held:
                held[number] = tickets.create(root, description)
                created.append(held[number])
        for number, description, fields in tasks:
            if held[number] in created:
                contract = {key: fields[key] for key in ("class", "role", "allowed_paths", "kpis", "profile", "inputs")
                            if key in fields}
                _write(root / tickets.TICKETS_REL / f"{held[number]}.md",
                       {"assignee": fields["role"], "title": description, **contract,
                        "specification": specification, "task": number,
                        "deps": [held.get(dep, dep) for dep in fields.get("depends_on", [])]})
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        for ticket in created:  # no partial set of tickets is left behind
            (root / tickets.TICKETS_REL / f"{ticket}.md").unlink(missing_ok=True)
        raise GovError(TICKET_FAILED, f"{change}: no ticket is derived: a ticket cannot be created "
                                      f"({type(exc).__name__})", {"change": change}) from None
    return {"change": change, "specification": specification,
            "tickets": [{"task": number, "ticket": held[number]} for number in numbers]}
