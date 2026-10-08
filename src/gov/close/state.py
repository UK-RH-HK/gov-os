"""The state of a ticket's refused closes (A6; DEC-487, DEC-490): the counter, the escalation, and what an
owner's decision must be to lift one.

The state cannot be reset by its absence or by a value that is no count: such a file is named and the close
ends there, uncounted. Every file is written beside its place and renamed, so it is whole or as it was.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from gov.cli.errors import GovError
from gov.close.repo import git

ESCALATION_AT = 3
EXIT_BLOCKED = 4
ESCALATION_OPTIONS = [
    "fix_differently", "narrow", "split", "defer", "delete", "continue",
]
ESCALATION_REASON = "three consecutive non-converging iterations"
# Where a decision record is looked for, in the commit being closed.
DECISION_FOLDERS = ("docs/", "governance/decisions/")


def write_whole(path: Path, content: str | bytes) -> None:
    """Write ``content`` beside ``path`` and rename it there: ``path`` is whole or as it was (``OSError``)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    beside = path.with_name(f".{path.name}.{os.getpid()}.part")
    try:
        with open(beside, "wb") as handle:
            handle.write(content.encode("utf-8") if isinstance(content, str) else content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(beside, path)
    finally:
        beside.unlink(missing_ok=True)


def count_path(root: Path, ticket: str) -> Path:
    return Path(root) / ".gov-runtime" / "iterations" / f"{ticket}.json"


def escalation_path(root: Path, ticket: str) -> Path:
    return Path(root) / ".gov-runtime" / "escalations" / f"{ticket}.json"


def _named(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def blocked(message: str, state: dict, **details) -> GovError:
    """The answer of a close under an escalation: nothing runs (exit code 4)."""
    return GovError("ESCALATION_BLOCKED", message,
                     {"outcomes": state.get("outcomes", [])[-1:], "reason": ESCALATION_REASON,
                      "options": ESCALATION_OPTIONS, **details},
                     exit_code=EXIT_BLOCKED)


def read_escalation(root: Path, ticket: str) -> dict | None:
    """The ticket's escalation file; ``None`` without one. ``ESCALATION_CORRUPT`` names a file that cannot
    be read or has another shape."""
    path = escalation_path(root, ticket)
    if not os.path.lexists(path):
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise GovError("ESCALATION_CORRUPT",
                        f"the escalation file {_named(root, path)} cannot be read or parsed: {e}",
                        {"ticket": ticket, "file": _named(root, path)})
    if not isinstance(data, dict) or not isinstance(data.get("decisions_used", []), list):
        raise GovError("ESCALATION_CORRUPT",
                        f"the escalation file {_named(root, path)} has another shape",
                        {"ticket": ticket, "file": _named(root, path)})
    return data


def read_count(root: Path, ticket: str) -> dict:
    """The ticket's counter; a count of zero without a file and without an escalation in force.

    ``ITERATION_CORRUPT`` names a counter that cannot be read or whose count is not a whole number from
    zero up. An escalation in force whose counter is missing blocks (DEC-487).
    """
    root = Path(root)
    path = count_path(root, ticket)
    named = _named(root, path)
    if not os.path.lexists(path):
        escalation = read_escalation(root, ticket)
        if escalation is not None and not escalation.get("lifted_by"):
            raise blocked(f"an escalation of {ticket} is in force and its counter {named} is missing: "
                          "the escalation is not reset by the counter's absence",
                          escalation, counter=named)
        return {"count": 0, "last_failures": [], "outcomes": []}

    def corrupt(why: str):
        return GovError("ITERATION_CORRUPT", f"the iteration counter {named} {why}",
                         {"ticket": ticket, "file": named})

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise corrupt(f"cannot be read or parsed: {e}")
    if not isinstance(data, dict) or not isinstance(data.setdefault("outcomes", []), list) \
            or not isinstance(data.get("decisions", []), list):
        raise corrupt("has another shape")
    if type(data.get("count")) is not int or data["count"] < 0:
        raise corrupt(f"holds no count from zero up: {data.get('count')!r}")
    return data


def write_count(root: Path, ticket: str, data: dict) -> None:
    try:
        write_whole(count_path(root, ticket), json.dumps(data))
    except OSError as e:
        raise GovError("ITERATION_UNWRITABLE",
                        f"iteration count file cannot be written: {e}",
                        {"ticket": ticket})


def write_escalation(root: Path, ticket: str, data: dict, **details) -> None:
    try:
        write_whole(escalation_path(root, ticket), json.dumps(data))
    except OSError as e:
        raise GovError("ESCALATION_UNWRITABLE",
                        f"the escalation package cannot be written: {e}",
                        {"ticket": ticket, **details})


def decisions_used(state: dict, escalation: dict | None) -> list[str]:
    """The decisions that have lifted an escalation of the ticket, as the counter and the escalation hold them."""
    used = list(state.get("decisions", [])) + list((escalation or {}).get("decisions_used", []))
    if state.get("decision"):
        used.append(state["decision"])
    return sorted({str(item) for item in used})


def lift_escalation(root: Path, ticket: str, dec_id: str, state: dict) -> dict:
    """Lift the ticket's escalation by the owner's decision ``dec_id`` and return the new counter.

    The decision lifts it only if it is a decision record of the commit being closed, active, with no finding
    of W1-11's checker about it (the owner's approval fact among them), recorded after the escalation began,
    and not used for an escalation of this ticket before (DEC-487). Any other decision lifts nothing: the
    close stays blocked. The working tree is the commit when this is asked (``run`` refuses before).
    """
    from gov.decisions import check as check_decisions
    from gov.tasks.tickets import frontmatter

    root = Path(root)
    escalation = read_escalation(root, ticket)

    def lifts_nothing(why: str):
        return blocked(f"the escalation of {ticket} stays in force: decision {dec_id} {why}",
                       state, decision=dec_id)

    used = decisions_used(state, escalation)
    if dec_id in used:
        raise lifts_nothing("has lifted an escalation of this ticket before")

    held = [path for path in git(root, "ls-tree", "-r", "-z", "--name-only", "HEAD").split("\0")
            if path.startswith(DECISION_FOLDERS) and path.rsplit("/", 1)[-1] == f"{dec_id}.md"]
    if len(held) != 1:
        raise lifts_nothing("is not one committed decision record" if held else
                            "is no committed record under " + " or ".join(DECISION_FOLDERS))
    front = frontmatter(root / held[0])
    if front is None:
        raise lifts_nothing("has no readable frontmatter")
    if front.get("type") != "decision" or str(front.get("id", "")) != dec_id:
        raise lifts_nothing("is not a decision record of that id")
    if str(front.get("status", "")) != "ACTIVE":
        raise lifts_nothing(f"is not in force (status: {front.get('status')})")
    about = sorted({str(f.get("code")) for f in check_decisions(root)
                    if dec_id in f.get("ids", []) or held[0] in f.get("paths", [])})
    if about:
        raise lifts_nothing(f"is not confirmed as the owner's and in force ({', '.join(about)})")

    began = state.get("escalated_at") or (escalation or {}).get("escalated_at")
    if not began:
        raise lifts_nothing("cannot be shown to be later than the escalation: the commit at which the "
                            "escalation began is not recorded")
    if git(root, "merge-base", "--is-ancestor", str(began), "HEAD", ok=(0, 1), code=True):
        raise lifts_nothing(f"cannot be shown to be later than the escalation: {str(began)[:12]}, where the "
                            "escalation began, is not in the history of the commit being closed")
    if git(root, "ls-tree", "-z", "--name-only", str(began), "--", held[0]).strip("\0"):
        raise lifts_nothing("was recorded before the escalation began")

    lifted = {"count": 0, "last_failures": [], "outcomes": [],
              "decision": dec_id, "decisions": sorted({*used, dec_id})}
    write_count(root, ticket, lifted)
    if escalation is not None:
        write_escalation(root, ticket, {**escalation, "lifted_by": dec_id,
                                        "decisions_used": lifted["decisions"]})
    return lifted
