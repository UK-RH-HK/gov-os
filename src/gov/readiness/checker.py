"""The readiness checker (CAP-30.a, CAP-30.b, CAP-53.a) and the closing of a specification (CAP-47.d).

A specification is the record in the frontmatter of ``openspec/changes/<change>/proposal.md``, with its
``readiness.yaml`` beside it (DEC-350). Both are read from the working tree. The rows and the capability-type
table come from the project's own ``feature-readiness`` schema; the ten mandatory rows are DEC-085's and are held
here, because that schema does not carry them.

The checker is a gate and does not fail open: the verdict comes from the rows, never from the record's status
(DEC-348), and whatever cannot be read or is not declared makes the record invalid. The output has no time in it
and a fixed order: rows in row order, specifications by id.
"""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import GovError

CHANGES_REL = "openspec/changes"
SCHEMA_REL = "openspec/schemas/feature-readiness/schema.yaml"
MANDATORY = (1, 2, 4, 5, 6, 9, 16, 23, 24, 25)  # DEC-085
PROFILES = ("LITE", "STANDARD", "FULL")
SATISFIED = ("PRESENT", "N/A_WITH_REASON")
STATES = (*SATISFIED, "MISSING", "PROVISIONAL", "BLOCKED")
UNLINKED = "UNLINKED"  # DEC-089
NOT_CLOSED, INVALID, NOT_FOUND = "SPEC_NOT_CLOSED", "READINESS_INVALID", "SPECIFICATION_NOT_FOUND"
EXIT_OPEN = 3
AUDIT_ROLE, AUDIT_CLASS = "independent-auditor", "audit"


def _yaml(path: Path):
    """The YAML document of ``path``; None when it cannot be read."""
    import yaml

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError):
        return None


def _text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def _invalid(specification: str, message: str, rows=()) -> GovError:
    return GovError(INVALID, f"{specification}: {message}",
                    {"specification": specification, "closed": False, "invalid": list(rows)})


def specifications(root: Path) -> list[tuple[str, Path, dict]]:
    """``(id, record path, frontmatter)`` of every specification record, by id."""
    from gov.tasks.tickets import frontmatter

    found = []
    for path in sorted((Path(root) / CHANGES_REL).glob("*/proposal.md")):
        front = frontmatter(path) or {}
        if front.get("type") == "specification" and _text(front.get("id")):
            found.append((front["id"], path, front))
    return sorted(found, key=lambda entry: (entry[0], str(entry[1])))


def of_ticket(root: Path, ticket: str) -> str:
    """The id of the specification the ticket names in its ``specification`` key (DEC-307)."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    front = frontmatter(Path(root) / TICKETS_REL / f"{ticket}.md")
    if front is None:
        raise GovError("TICKET_NOT_FOUND", f"{ticket}: no such ticket", {"ticket": ticket})
    if not _text(front.get("specification")):
        raise GovError(NOT_FOUND, f"{ticket} names no specification", {"ticket": ticket})
    return front["specification"]


def _fault(cells: list) -> str | None:
    """Why the cell of one row is invalid; None when it is a valid cell."""
    if len(cells) != 1:
        return "the row is repeated" if cells else "the row is absent"
    state, evidence = cells[0].get("state"), cells[0].get("evidence")
    if not isinstance(state, str) or state not in STATES:
        return f"the state is not one of {', '.join(STATES)}"
    if state == "N/A_WITH_REASON" and not _text(cells[0].get("reason")):
        return "N/A_WITH_REASON has no reason"
    if state == "PRESENT" and not (isinstance(evidence, list) and any(_text(item) for item in evidence)):
        return "PRESENT cites no evidence"
    return None


def judge(root: Path, specification: str, path: Path, front: dict) -> dict:
    """The report of one specification record; ``READINESS_INVALID`` when the record cannot be judged."""
    schema = _yaml(Path(root) / SCHEMA_REL)
    try:
        keys = {row["n"]: str(row["key"]) for row in schema["dimensions"]}
        extra = {name: set(rows) for name, rows in schema["capability_types"]["extra_rows_for_standard"].items()}
        numbers = sorted(keys)
    except (TypeError, KeyError, AttributeError):
        raise _invalid(specification, f"{SCHEMA_REL} cannot be read") from None
    if not set(MANDATORY) <= set(keys):
        raise _invalid(specification, f"{SCHEMA_REL} lacks a mandatory row")
    profile, spine, types = front.get("profile"), front.get("spine"), front.get("capability_types")
    types = [] if types is None else types
    if not isinstance(profile, str) or profile not in PROFILES or not isinstance(spine, bool) \
            or not isinstance(types, list) or not all(isinstance(name, str) and name in extra for name in types):
        raise _invalid(specification, f"the record declares profile ({', '.join(PROFILES)}), spine (true or false) "
                                      "and capability_types (types of the schema's table)")
    applied = "FULL" if spine else profile  # a spine always closes at FULL (DEC-085)
    if applied == "STANDARD" and not types:
        raise _invalid(specification, "a STANDARD specification declares at least one capability type")
    required = set(keys) if applied == "FULL" else set(MANDATORY).union(
        *(extra[name] for name in types if applied == "STANDARD"))
    record = _yaml(path.with_name("readiness.yaml"))
    rows = record.get("rows") if isinstance(record, dict) else None
    if not isinstance(rows, list):
        raise _invalid(specification, "readiness.yaml cannot be read, or has no rows")
    invalid, open_rows = [], []
    for n in numbers:
        cells = [row for row in rows if isinstance(row, dict) and row.get("n") == n]
        fault = _fault(cells)
        if fault is not None:
            invalid.append({"n": n, "key": keys[n], "reason": fault})
        elif n in required and cells[0]["state"] not in SATISFIED:
            open_rows.append({"n": n, "key": keys[n], "state": cells[0]["state"],
                              "gap_ticket": _text(cells[0].get("gap_ticket")) or UNLINKED})
    if invalid:
        named = ", ".join(f"{row['key']} ({row['reason']})" for row in invalid)
        raise _invalid(specification, f"{len(invalid)} invalid rows: {named}", invalid)
    return {"specification": specification, "profile": applied, "closed": not open_rows, "open": open_rows}


def _verdict(root: Path, specification: str, path: Path, front: dict) -> dict:
    """The report when no required row is open; ``SPEC_NOT_CLOSED`` with the report otherwise."""
    report = judge(root, specification, path, front)
    if not report["closed"]:
        named = ", ".join(f"{row['key']} ({row['gap_ticket']})" for row in report["open"])
        raise GovError(NOT_CLOSED, f"{specification}: {len(report['open'])} required rows open at "
                                   f"{report['profile']}: {named}", report, exit_code=EXIT_OPEN)
    return report


def _find(root: Path, specification: str) -> tuple[Path, dict]:
    found = [entry[1:] for entry in specifications(root) if entry[0] == specification]
    if len(found) != 1:
        raise GovError(NOT_FOUND, f"{specification}: {len(found)} specification records under {CHANGES_REL}/",
                       {"specification": specification})
    return found[0]


def check(root: Path, specification: str) -> dict:
    """The report of the specification; a ``GovError`` when it does not pass."""
    return _verdict(root, specification, *_find(root, specification))


def check_all(root: Path) -> dict:
    """Every specification's report; a ``GovError`` when one of them does not pass, an invalid record first."""
    answers, errors = [], []
    for specification, path, front in specifications(root):
        try:
            answers.append(_verdict(root, specification, path, front))
        except GovError as error:
            answers.append(error.details)
            errors.append(error)
    if errors:
        invalid = any(error.code == INVALID for error in errors)
        raise GovError(INVALID if invalid else NOT_CLOSED, "; ".join(error.message for error in errors),
                       {"closed": False, "specifications": answers}, exit_code=1 if invalid else EXIT_OPEN)
    return {"closed": True, "specifications": answers}


def _audit_ticket(root: Path, specification: str, profile: str) -> str:
    """The audit ticket of the specification's closure (DEC-088): the one that exists, or a new one."""
    import subprocess

    import yaml

    from gov import tasks
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    for path in sorted((root / TICKETS_REL).glob("*.md")):
        front = frontmatter(path) or {}
        if front.get("class") == AUDIT_CLASS and front.get("audits") == specification:
            return path.stem
    title = f"Audit the closure of specification {specification}"
    try:
        ticket = tasks.create(root, title)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise GovError("AUDIT_TICKET_FAILED", f"{specification} is not closed: its audit ticket cannot be created "
                                              f"({type(exc).__name__})", {"specification": specification}) from None
    fields = {
        "assignee": AUDIT_ROLE, "title": title, "class": AUDIT_CLASS, "role": AUDIT_ROLE, "audits": specification,
        "allowed_paths": [f"docs/audit/{specification}/**"],
        "kpis": {"success": [f"A fresh Independent Auditor that authored none of the audited files audits the "
                             f"closure of specification {specification} and reports its findings, naming the "
                             f"milestone (MR-4)"],
                 "failure": ["The auditor authored any audited file"]},
        "profile": profile, "sources": ["DEC-088", "MR-4"],
    }
    path = root / TICKETS_REL / f"{ticket}.md"
    lines = [line for line in path.read_text(encoding="utf-8").split("\n") if not line.startswith("assignee:")]
    end = lines.index("---", 1)
    lines[end:end] = yaml.safe_dump(fields, sort_keys=False, width=1000).rstrip("\n").split("\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return ticket


def close(root: Path, specification: str) -> dict:
    """Close the specification: its audit ticket first (none for a LITE feature), then the status ``CLOSED``.

    Refuses with ``SPEC_NOT_CLOSED`` or ``READINESS_INVALID`` and writes nothing when the specification does not
    pass (DEC-349). It writes in the working tree and commits nothing.
    """
    root = Path(root)
    path, front = _find(root, specification)
    report = _verdict(root, specification, path, front)
    ticket = None if report["profile"] == "LITE" else _audit_ticket(root, specification, report["profile"])
    if front.get("status") != "CLOSED":
        lines = path.read_text(encoding="utf-8").split("\n")
        end = [line.rstrip() for line in lines].index("---", 1)
        index = next(i for i, line in enumerate(lines[:end]) if line.startswith("status:"))
        lines[index] = "status: CLOSED"
        path.write_text("\n".join(lines), encoding="utf-8")
    return {**report, "status": "CLOSED", "audit_ticket": ticket}
