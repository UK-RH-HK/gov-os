"""The decision checker (CAP-51.a, CAP-01.b, CAP-21.a, CAP-34.d): findings over the decisions, gates and tickets.

It only reads, and only frontmatter and git (DEC-329): every file is read from
``HEAD`` as the store reads it, never from the working tree, and no git command
it runs writes. An empty list passes; the check does not fail open.

- A decision file is a Markdown file whose frontmatter has ``type: decision`` or
  an ``id`` of the ``decision_id`` grammar; it need not be a record of the store.
  Supersession is one edge from the successor, read from ``supersedes`` and from
  ``superseded_by`` (DEC-277).
- The owner's approval fact is the ``Role: owner`` trailer on the commit that
  last set the decision ``ACTIVE`` (DEC-360), read from the final trailer block;
  a commit made before 2026-10-03 is read from the whole message (DEC-182). A
  commit that also carries another role is no approval.
- A gate authorises a record that cites it in ``approval`` only when it is a
  decision package, its ``status`` is ``ACCEPTED`` and both carry the same
  ``cit`` (DEC-331). A ticket that is not closed and is named in the
  ``constrains`` of a dead package fails (DEC-330).
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path

from gov.cli.errors import GovError
from gov.store.loader import TRAILER_RULE_DATE, _frontmatter, _git, _ids, _markdown
from gov.tasks.tickets import TICKETS_REL

DECISION_ID = re.compile(r"(ADR|DEC)-[0-9]{3,}")  # the kernel's decision_id grammar (common.schema.json)
GATE_TYPE = "decision-package"
GATE_DEAD = ("DECLINED", "REVOKED", "STALE")  # DEC-328

_ROLE = re.compile(r"^Role:[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_LOG_FORMAT = "--format=%x1e%H%x1f%cs%x1f%(trailers:key=Role,unfold)%x1f%B%x1f"


def _finding(code: str, ids, paths, message: str) -> dict:
    return {"code": code, "ids": list(ids), "paths": sorted(set(paths)), "message": message}


def _status(text: str | None):
    """The frontmatter ``status`` of a file's text; None when there is no file, no frontmatter or no reading it."""
    try:
        front = _frontmatter(text) if text is not None else None
    except ValueError:
        return None
    return front.get("status") if isinstance(front, dict) else None


def _read(root: Path) -> list[tuple[str, dict]]:
    """``(path, frontmatter)`` of every Markdown file of ``HEAD``; an empty map where it has none that can be read."""
    files = []
    for path, text in _markdown(root):
        try:
            front = _frontmatter(text)
        except ValueError:
            front = None
        files.append((path, front if isinstance(front, dict) else {}))
    return files


def _hazards(decisions: list[tuple[str, str, dict]]) -> list[dict]:
    """Duplicate and overlapping ids, ACTIVE while superseded, and supersession cycles."""
    found, paths, edges = [], {}, set()
    for path, record_id, front in decisions:
        paths.setdefault(record_id, []).append(path)
        edges.update((record_id, target) for target in _ids(front.get("supersedes")))
        edges.update((successor, record_id) for successor in _ids(front.get("superseded_by")))
    for record_id, files in paths.items():
        if len(files) > 1:
            found.append(_finding("DUPLICATE_ID", [record_id], files, f"{record_id} is the id of {len(files)} files"))
    for index, (path, record_id, _) in enumerate(decisions):
        for other_path, other_id, _ in decisions[index + 1:]:
            if (record_id != other_id and DECISION_ID.fullmatch(record_id) and DECISION_ID.fullmatch(other_id)
                    and record_id.partition("-")[2] == other_id.partition("-")[2]
                    and posixpath.dirname(path) != posixpath.dirname(other_path)):
                found.append(_finding("OVERLAPPING_ID", sorted((record_id, other_id)), (path, other_path),
                                      f"{record_id} and {other_id} have one number in two directories"))
    superseded = {target for source, target in edges if source != target}
    for path, record_id, front in decisions:
        if front.get("status") == "ACTIVE" and record_id in superseded:
            found.append(_finding("ACTIVE_SUPERSEDED", [record_id], [path],
                                  f"{record_id} is ACTIVE and a supersession names it as superseded"))
    after: dict[str, set] = {}
    for source, target in edges:
        after.setdefault(source, set()).add(target)

    def reach(start: str) -> set:
        seen, todo = set(), [start]
        while todo:
            for following in after.get(todo.pop(), ()):
                if following not in seen:
                    seen.add(following)
                    todo.append(following)
        return seen

    reached = {node: reach(node) for node in after}
    cycles = {frozenset(member for member in reached[node] if node in reached.get(member, ()))
              for node in after if node in reached[node]}
    for cycle in cycles:
        members = sorted(cycle)
        files = [path for member in members for path in paths.get(member, [])]
        found.append(_finding("SUPERSESSION_CYCLE", members, files,
                              f"the supersessions of {', '.join(members)} form a cycle"))
    return found


def _history(root: Path) -> dict[str, list[tuple[str, bool]]]:
    """``path -> (commit, whether it is the owner's approval)`` of the commits that changed it, newest first."""
    history: dict[str, list[tuple[str, bool]]] = {}
    log = _git(root, "-c", "core.quotePath=false", "log", "--name-only", _LOG_FORMAT, "HEAD")
    for entry in log.decode("utf-8", "replace").split("\x1e")[1:]:
        commit, date, final_block, message, names = entry.split("\x1f")
        roles = {role.strip() for role in _ROLE.findall(message if date < TRAILER_RULE_DATE else final_block)}
        for name in names.split("\n"):
            if name:
                history.setdefault(name, []).append((commit, roles == {"owner"}))
    return history


def _statuses(root: Path, path: str, commits: list[str]) -> list:
    """The frontmatter ``status`` of ``path`` at each commit."""
    out = _git(root, "cat-file", "--batch", stdin="".join(f"{commit}:{path}\n" for commit in commits).encode())
    statuses, position = [], 0
    for _ in commits:
        header_end = out.index(b"\n", position)
        header = out[position:header_end].split()
        if header[-1] == b"missing":
            statuses.append(None)
            position = header_end + 1
            continue
        size = int(header[-1])
        statuses.append(_status(out[header_end + 1:header_end + 1 + size].decode("utf-8", "replace")))
        position = header_end + size + 2
    return statuses


def _unapproved(root: Path, decisions: list[tuple[str, str, dict]]) -> list[dict]:
    """Every ACTIVE decision whose commit that last set it ACTIVE carries no owner approval fact (DEC-360)."""
    found, history = [], _history(root)
    for path, record_id, front in decisions:
        if front.get("status") != "ACTIVE":
            continue
        commits = history.get(path, [])
        statuses = _statuses(root, path, [commit for commit, _ in commits])
        setter = 0  # the oldest commit of the latest run of commits that leave the decision ACTIVE
        while statuses[setter:setter + 2] == ["ACTIVE", "ACTIVE"]:
            setter += 1
        if statuses[setter:setter + 1] != ["ACTIVE"] or not commits[setter][1]:
            found.append(_finding("ACTIVE_UNAPPROVED", [record_id], [path],
                                  f"{record_id} was set ACTIVE by a commit without the trailer `Role: owner`"))
    return found


def _gates(files: list[tuple[str, dict]]) -> list[dict]:
    """Records that cite a gate that does not authorise them, and open tickets that wait on a dead package."""
    found, by_id, tickets = [], {}, {}
    records = [(path, front) for path, front in files if "id" in front]
    for path, front in records:
        by_id.setdefault(str(front["id"]), []).append(front)
    for path, front in files:  # a ticket is known by its file name, as the READY rule knows it
        if posixpath.dirname(path) == TICKETS_REL:
            tickets[posixpath.basename(path)[:-len(".md")]] = (path, front.get("status"))
    for path, front in records:
        record_id, cit = str(front["id"]), front.get("cit")
        for cited in sorted(set(_ids(front.get("approval")))):
            gates = by_id.get(cited, [])
            if not gates or not all(gate.get("type") == GATE_TYPE and gate.get("status") == "ACCEPTED"
                                    and isinstance(cit, str) and cit and gate.get("cit") == cit for gate in gates):
                found.append(_finding("GATE_NOT_AUTHORISING", [record_id, cited], [path],
                                      f"{record_id} cites {cited}, which is no accepted gate of its CIT"))
        if front.get("type") == GATE_TYPE and front.get("status") in GATE_DEAD:
            for named in sorted(set(_ids(front.get("constrains")))):
                if named in tickets and tickets[named][1] != "closed":
                    found.append(_finding("TICKET_WAITS_ON_DEAD_GATE", [named, record_id], [tickets[named][0]],
                                          f"{named} is not closed and waits on {record_id}, which is "
                                          f"{front['status']}"))
    return found


def check(root: Path) -> list[dict]:
    """The findings on the project at ``root``, in a fixed order; an empty list passes."""
    root = Path(root)
    try:
        below = _git(root, "rev-parse", "--show-prefix").strip()
    except GovError:
        below = None
    if below != b"":  # a folder inside another project's repository is not that project
        raise GovError("DECISIONS_NOT_A_REPOSITORY", f"{root} is not the root of a git repository",
                       {"root": str(root)})
    files = _read(root)
    decisions = [(path, str(front["id"]), front) for path, front in files if "id" in front
                 and (front.get("type") == "decision" or DECISION_ID.fullmatch(str(front["id"])))]
    found = _hazards(decisions) + _unapproved(root, decisions) + _gates(files)
    return sorted(found, key=lambda finding: (finding["code"], finding["ids"], finding["paths"]))
