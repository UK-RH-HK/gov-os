"""The tickets ``gov discover`` makes (W2-36): the discovery ticket, a gap ticket per open readiness row (CAP-30.c,
DEC-089, DEC-102, DEC-103) and the feature ticket of a spec that passes. Each is made with the project's vendored
``tk create`` (``gov.tasks.create``; ``tk`` on ``PATH`` when the project has none), then its front matter is written
whole: the lines tk wrote, ``deps`` from ``depends_on``, and the fields below."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.discover import draft
from gov.tasks.tickets import TICKETS_REL, TK_REL

BRIEF = "gov brief {role} {ticket}"
REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
RESEARCH_PARTS = "what was tested, how it was tested, the results with measured numbers, and the verdict"


def exists(root: Path, ticket) -> bool:
    return isinstance(ticket, str) and bool(REF.fullmatch(ticket)) and (Path(root) / TICKETS_REL / f"{ticket}.md").is_file()


def create(root: Path, title: str) -> str:
    """The id of a new ticket made by tk; ``DISCOVER_TICKET_FAILED`` when tk cannot make one."""
    from gov import tasks
    from gov.util.gitenv import git_env

    root = Path(root)
    try:
        if (root / TK_REL).is_file():
            return tasks.create(root, title)
        done = subprocess.run(["tk", "create", title], cwd=root, capture_output=True, text=True, check=True,
                              env={**git_env(root), "TICKETS_DIR": str(root / TICKETS_REL)})
        return done.stdout.strip().split("\n")[-1]
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise GovError("DISCOVER_TICKET_FAILED", f"tk cannot make a ticket ({type(error).__name__})", {}) from None


def write(root: Path, ticket: str, fields: dict, body: str) -> None:
    """The ticket file whole: tk's own lines (not its assignee or deps), ``deps`` as ``depends_on``, ``fields``, body."""
    path = Path(root) / TICKETS_REL / f"{ticket}.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    keep = [line for line in lines[1:lines.index("---", 1)] if not line.startswith(("assignee:", "deps:"))]
    deps = fields.get("depends_on") or []
    keep.insert(2, f"deps: [{', '.join(deps)}]")
    if "state_class: AUTHORITATIVE" not in keep:
        keep.append("state_class: AUTHORITATIVE")
    fields = {"assignee": fields["role"], **fields}
    dumped = yaml.safe_dump(fields, sort_keys=False, width=1000, allow_unicode=True).rstrip("\n")
    path.write_text("\n".join(["---", *keep, dumped, "---", body]) + "\n", encoding="utf-8")


def remove(root: Path, tickets: list[str]) -> None:
    for ticket in tickets:
        (Path(root) / TICKETS_REL / f"{ticket}.md").unlink(missing_ok=True)


def _kpi(line: str, verify: str) -> dict:
    return {"line": line, "verify": verify}


def discovery(change: str, words: str, profile: str, spec: str) -> tuple[str, dict, str]:
    """``(title, fields, body)`` of the discovery ticket: a product-spec session writes the spec and passes the check."""
    fields = {
        "title": f"Discover and write the spec: {words}", "class": "specification", "role": "product-spec",
        "discovers": change, "allowed_paths": [f"openspec/changes/{change}/**"],
        "kpis": {"success": [_kpi(f"The spec at {spec} ({words}) is written to the spec-writing form, its open "
                                  "questions answered or taken to the owner, every KPI with its failure line and verify",
                                  f"gov discover --check {change}")],
                 "failure": [_kpi("The spec passes the check with a question left unanswered that decides a KPI",
                                  f"gov discover --check {change}")]},
        "profile": profile, "reads": [], "needs": [], "waits_on": [],
        "non_goals": ["It does not close the specification (gov readiness close does)"]}
    body = (f"# Discover and write the spec: {words}\n\nWrite {spec} from the idea \"{words}\": fill every part, answer "
            f"or hand on each open question, then run `gov discover --check {change}`.")
    return fields["title"], fields, body


def gap(change: str, spec_id: str, row: dict, name: str, depends: list[str], profile: str) -> tuple[str, dict, str]:
    """``(title, fields, body)`` of the gap ticket of an open readiness row, its class and role by the row."""
    n, key = row["n"], row["key"]
    cls, role = draft.class_of(key)
    paths = [f"openspec/changes/{change}/**"] + ([f"docs/research/{change}/**"] if cls == "research" else [])
    success = [_kpi(f"The {key} row ({name}) of {spec_id} is PRESENT with evidence or N/A_WITH_REASON with a reason",
                    f"gov readiness --specification {spec_id} no longer lists {key} as open")]
    if cls == "research":  # DEC-102: the answer is an evidence record, its four parts
        record = f"docs/research/{change}/{key}.md"
        success.append(_kpi(f"The evidence record {record} holds four parts: {RESEARCH_PARTS}",
                            f"{record} exists, with its four parts: what was tested, how, the results with measured "
                            "numbers, and the verdict"))
    title = f"Settle readiness row {n} {key} ({name}) of {change}"
    fields = {
        "title": title, "class": cls, "role": role, "readiness_row": {"specification": spec_id, "n": n, "key": key},
        "allowed_paths": paths, "depends_on": depends,
        "kpis": {"success": success,
                 "failure": [_kpi(f"The {key} row is marked PRESENT with no evidence or N/A_WITH_REASON with no reason",
                                  f"gov readiness --specification {spec_id} no longer lists {key} as open")]},
        "profile": profile, "reads": [], "needs": [], "waits_on": []}
    return title, fields, (f"# {title}\n\nRow {n}, {key} ({name}), of {spec_id} is {row['state']}. Settle it for "
                           f"openspec/changes/{change}/spec.md and record it in readiness.yaml.")


def feature(change: str, spec_id: str, words: str, profile: str, paths: list[str], kpis: list, non_goals: list,
            ) -> tuple[str, dict, str]:
    """``(title, fields, body)`` of the feature ticket: a success and a failure line per K, each with the K's verify."""
    spec = f"openspec/changes/{change}/spec.md"
    success = [_kpi(f"{behaviour} [K{n}]", verify) for n, behaviour, _, verify in kpis]
    failure = [_kpi(f"Fails if: {fails} [K{n}]", verify) for n, _, fails, verify in kpis]
    fields = {
        "title": f"Implement: {words}", "class": "implementation", "role": "engineer", "specification": spec_id,
        "allowed_paths": paths, "kpis": {"success": success, "failure": failure}, "profile": profile,
        "non_goals": non_goals, "reads": [spec], "needs": [], "waits_on": []}
    return fields["title"], fields, f"# Implement: {words}\n\nBuild what {spec} specifies; its KPIs are the lines above."
