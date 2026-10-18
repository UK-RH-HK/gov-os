"""The impact of a stated change over the record graph and the code graph (W2-37; CAP-33.b, CAP-33.g, DEC-167).

``assess(root, changes, config)`` takes record ids, symbol names or one plain-language question ("What's the impact of
X?") and returns the impact assessment: the affected specifications, decisions, tickets, tests and code, each with
the graph it came from, the radius and the depth it implies (``gov.closure.depth_of_radius``), the gaps, and the
change-impact proposal (CIT-P) as frontmatter. The two graphs are joined by id (G-16): a record's edge to no record is
looked up as a symbol of the code index, and a symbol reaches the records whose edges name it. ``compare(root, rel)``
checks a change-execution record (CIT-E) against the CIT-P it names.

It only reads. It builds neither the store nor the code index, and a graph that is missing, stale or unreadable is
said, and the report is then never complete. The readings still with the owner are in ``gov.impact.readings``.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.impact import readings
from gov.impact.readings import CODE, KINDS, OK, RECORD

CITP_TYPE, CITE_TYPE = "change-impact-proposal", "change-execution-record"
DEPTH_LIMIT, UNRESOLVED, NO_KIND = "DEPTH_LIMIT_REACHED", "UNRESOLVED", "NO_KIND"  # the first two as gov closure's
_QUESTION = re.compile(r"\s*what(?:'s|’s|\s+is)\s+the\s+impact\s+of\s+[`'\"]?([^\s`'\"?]+)[`'\"]?\s*\??\s*",
                       re.IGNORECASE)
_NAME = re.compile(r"[A-Za-z_][\w.:/#-]*")  # a record id or a symbol name

__all__ = ["assess", "compare"]


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "--no-optional-locks", "-C", str(root), "-c", "core.quotePath=false", *args],
                          capture_output=True, text=True).stdout


def _front(text: str) -> dict | None:
    import yaml

    lines = text.split("\n")
    ends = [number for number, line in enumerate(lines) if line.rstrip() == "---"]
    if len(ends) < 2 or ends[0] != 0:
        return None
    try:
        found = yaml.safe_load("\n".join(lines[1:ends[1]]))
    except yaml.YAMLError:
        return None
    return found if isinstance(found, dict) else None


class _Records:
    """The record graph of the store, read once; ``state`` is OK only when the store holds ``HEAD``."""

    def __init__(self, root: Path):
        from gov import records

        try:
            self.by_id = {record["id"]: record for record in records.records(root)}
            edges, stored = records.edges(root), {entry["commit"] for entry in records.commits(root)}
        except GovError as error:
            raise GovError("IMPACT_RECORD_GRAPH_MISSING", f"the record graph cannot be read: {error.message}; "
                           "gov impact never loads the store", {"graph": RECORD}) from None
        except sqlite3.Error as error:
            raise GovError("IMPACT_RECORD_GRAPH_UNREADABLE", f"the record graph cannot be read: the store is "
                           f"unreadable ({error})", {"graph": RECORD}) from None
        self.near, self.named_by = {}, {}
        for edge in edges:
            self.near.setdefault(edge["source"], set()).add(edge["target"])
            self.near.setdefault(edge["target"], set()).add(edge["source"])
            if edge["source"] != edge["target"]:
                self.named_by.setdefault(edge["target"], set()).add(edge["source"])
        self.testers = {edge["source"] for edge in edges if edge["type"] == "TESTS"}
        head = _git(root, "rev-parse", "HEAD").strip()
        self.state = OK if head and head in stored else \
            f"stale: HEAD {head[:12] or '(none)'} is not among the store's commits; gov impact never loads it again"


class _Code:
    """The code graph of the code index, read once if it was built; ``usable`` when it was read, even stale."""

    def __init__(self, root: Path):
        from gov import codeintel

        self.root, self.dead, self.paths = root, set(), {}
        staged = codeintel.home(root).parent / "files"
        if not staged.is_dir():
            self.state = "missing: no code index was built here; gov impact never builds it"
            return
        try:
            self.dead = {entry["name"] for entry in codeintel.dead_code(root)}
        except (RuntimeError, OSError, LookupError, ValueError, TypeError) as error:
            self.state = f"unavailable: the code index cannot be read ({error})"
            return
        self.state = _staleness(root, staged) or OK

    @property
    def usable(self) -> bool:
        return self.state == OK or self.state.startswith("stale")

    def defined(self, name: str) -> list[str]:
        from gov import codeintel

        if self.usable and name not in self.paths:
            self.paths[name] = sorted({entry["path"] for entry in codeintel.definitions(self.root, name)})
        return self.paths.get(name, [])

    def near(self, name: str) -> set:
        from gov import codeintel

        return {entry["name"] for entry in codeintel.callers(self.root, name) + codeintel.callees(self.root, name)}


def _staleness(root: Path, staged: Path) -> str | None:
    """Why the code index is not the working tree's: a file it copied changed or went, or a file came after it."""
    listed = [rel for rel in _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")
              if rel]
    copies = {path.relative_to(staged).as_posix(): path for path in staged.rglob("*") if path.is_file()}
    since = min((path.stat().st_mtime for path in copies.values()), default=staged.stat().st_mtime)
    for rel in sorted(set(listed) | set(copies)):
        path = root / rel
        if rel in copies:
            changed = not path.is_file() or path.read_bytes() != copies[rel].read_bytes()
        else:
            changed = path.is_file() and path.stat().st_mtime > since
        if changed:
            return f"stale: {rel} changed after the code index was built; gov impact never builds it again"
    return None


def _stated(values: list[str]) -> list[str]:
    """The ids and names of the stated change; a question gives the one it names (KPI 3)."""
    ids, malformed = [], []
    for value in values:
        asked = _QUESTION.fullmatch(value)
        item = asked.group(1) if asked else value.strip()
        if not _NAME.fullmatch(item):
            malformed.append(value)
        elif item not in ids:
            ids.append(item)
    if malformed:
        raise GovError("IMPACT_CHANGE_MALFORMED", f"{', '.join(map(repr, malformed))}: neither a record id, a symbol "
                       "name nor a question \"What's the impact of X?\"", {"malformed": malformed})
    if not ids:
        raise GovError("IMPACT_NO_CHANGE", "no stated change: give a record id, a symbol name or a question")
    return ids


def _walk(graph: _Records, code: _Code, start: list[str], depth: int) -> tuple[dict, dict]:
    """``id -> graph`` of what is at most ``depth`` hops from ``start`` over both graphs, and ``id -> gap reason``."""
    seen, gaps, front = {}, {}, set(start)
    for _ in range(depth + 1):
        named = set()
        for item in sorted(front):
            if item in graph.by_id:
                seen[item] = RECORD
                named |= graph.near.get(item, set())
            elif code.defined(item):  # G-16: a name no record holds is a symbol of the code index, or a gap
                seen[item] = CODE
                named |= code.near(item) | graph.near.get(item, set())
            else:
                gaps[item] = UNRESOLVED if code.usable else "CODE_GRAPH_" + code.state.split(":")[0].upper()
        front = named - seen.keys() - gaps.keys()
    gaps.update(dict.fromkeys(front, DEPTH_LIMIT))
    return seen, gaps


def _grouped(graph: _Records, code: _Code, seen: dict, start: list[str], gaps: dict) -> dict:
    affected = {kind: [] for kind in KINDS}
    for item, where in sorted(seen.items()):
        if item in start:
            continue
        kind = readings.record_kind(graph.by_id[item], graph.testers) if where == RECORD \
            else readings.symbol_kind(code.defined(item))
        if kind is None:
            gaps[item] = NO_KIND
        else:
            affected[kind].append({"id": item, "graph": where})
    return affected


def _in_place(root: Path, record: dict) -> list[dict]:
    """Edits of a closed specification that keep it closed: in a commit after it was closed, or in the working tree."""
    rel, found, before = record["path"], [], None
    for commit in _git(root, "log", "--reverse", "--format=%H", "--", rel).split():
        now = (_front(_git(root, "show", f"{commit}:{rel}")) or {}).get("status")
        if before == now == readings.CLOSED:
            found.append(commit)
        before = now
    path = root / rel
    if before == readings.CLOSED and _git(root, "status", "--porcelain", "--", rel).strip() and path.is_file() \
            and (_front(path.read_text(encoding="utf-8", errors="replace")) or {}).get("status") == readings.CLOSED:
        found.append("working tree")
    return [{"code": "CLOSED_SPEC_EDITED_IN_PLACE", "id": record["id"], "path": rel, "where": where,
             "message": f"{record['id']} is closed and was edited in place ({where}): a change to a closed "
                        "specification goes through a CIT-P and one of DEC-105's options"} for where in found]


def _options(closed: list[str], count: int) -> list[dict]:
    """DEC-105's three options for a change to a closed specification, each with its cost (CAP-33.e)."""
    names = ", ".join(closed)
    return [
        {"option": "apply now", "cost": f"{names} changes now, through this CIT-P and the owner's approval; the "
                                        f"{count} affected items are checked against the new text before they close"},
        {"option": "defer", "cost": f"the finding is recorded and work continues; the {count} affected items keep "
                                    f"building on {names} as it stands until the owner takes the finding up"},
        {"option": "re-baseline", "cost": f"{names} is reopened and re-planned from; the work it invalidates among "
                                          f"the {count} affected items is retired, and every version is kept"},
    ]


def assess(root: Path, values: list[str], config: dict, out: str | None = None) -> dict:
    """The impact assessment of the stated change, with its CIT-P; with ``out``, the CIT-P written there too."""
    from gov.closure import depth_of_radius

    root, ids = Path(root), _stated(values)
    graph, code = _Records(root), _Code(Path(root))
    unknown = [item for item in ids if item not in graph.by_id and not code.defined(item)]
    if unknown:
        looked = "" if code.usable else f", and the code graph cannot be asked ({code.state})"
        raise GovError("IMPACT_CHANGE_UNKNOWN", f"{', '.join(unknown)}: no record of the store and no symbol of the "
                       f"code index{looked}", {"unknown": unknown, "graphs": {RECORD: graph.state, CODE: code.state}})
    current = graph.state == OK
    change = []
    for item in ids:
        record = graph.by_id.get(item)
        named = bool(graph.named_by.get(item))
        dead, path = (True, record["path"]) if record else (item in code.dead, (code.defined(item) or [None])[0])
        change.append({"id": item, "graph": RECORD if record else CODE, "path": path,
                       "deletable": readings.deletable(named, dead, current and (record is not None or code.state == OK)),
                       "governance": readings.governance(config.get("path-map.yaml", {}).get("namespaces"), path)})
    near, near_gaps = _walk(graph, code, ids, 1)
    one_hop = {kind for kind, listed in _grouped(graph, code, near, ids, {}).items() if listed}
    if any(reason.startswith("CODE_GRAPH_") for reason in near_gaps.values()):
        one_hop.add("code")  # what the code graph could not say is never read as nothing
    number = readings.radius(all(entry["deletable"] for entry in change), one_hop)
    depth = depth_of_radius(number)
    seen, gaps = _walk(graph, code, ids, depth)
    affected = _grouped(graph, code, seen, ids, gaps)
    closed = [item for item in ids if item in graph.by_id and readings.closed_specification(graph.by_id[item])]
    record_id = "CITP-" + hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()[:8]
    if out is not None and re.fullmatch(r"[A-Z][A-Z0-9]*-[A-Za-z0-9._-]+", Path(out).stem):
        record_id = Path(out).stem
    proposal = {"id": record_id, "type": CITP_TYPE, "status": "PROPOSED", "state_class": "DERIVED",
                "title": f"The impact of changing {', '.join(ids)}", "change": ids, "radius": f"R{number}",
                "depth": depth, "affected": {kind: [entry["id"] for entry in affected[kind]] for kind in KINDS}}
    graphs = {RECORD: graph.state, CODE: code.state}
    result = {
        "change": change, "radius": f"R{number}", "depth": depth, "depth_source": readings.DEPTH_SOURCE,
        "affected": affected, "graphs": graphs, "complete": not gaps and all(state == OK for state in graphs.values()),
        "gaps": [{"id": item, "reason": gaps[item]} for item in sorted(gaps)], "proposal": proposal,
        "options": _options(closed, sum(map(len, affected.values()))) if closed else [],
        "findings": [finding for item in closed for finding in _in_place(root, graph.by_id[item])],
    }
    if out is not None:
        _write(root, out, proposal)
    return result


def _write(root: Path, out: str, proposal: dict) -> None:
    """The CIT-P as a record file at ``out``: the one file gov impact writes, and never over another."""
    import yaml

    path = Path(out) if Path(out).is_absolute() else root / out
    if path.exists():
        raise GovError("IMPACT_OUT_EXISTS", f"{out}: a file is there already; gov impact writes no file over another",
                       {"out": str(out)})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml.safe_dump(proposal, sort_keys=False, allow_unicode=True)}---\n\n"
                    f"# {proposal['id']}: {proposal['title']}\n\nWritten by `gov impact`: radius {proposal['radius']}, "
                    f"depth {proposal['depth']}.\n", encoding="utf-8")


def _lists(value) -> dict | None:
    """``kind -> set of ids`` of an ``affected`` map; None when there is none."""
    if not isinstance(value, dict) or not value:
        return None
    return {str(kind): {str(item.get("id") if isinstance(item, dict) else item) for item in (ids or [])}
            for kind, ids in value.items() if isinstance(ids, (list, type(None)))}


def compare(root: Path, rel: str) -> dict:
    """The CIT-E at ``rel`` checked against the CIT-P it names: ``matches``, or every difference (KPI 2)."""
    root = Path(root)
    path = Path(rel) if Path(rel).is_absolute() else root / rel
    try:
        front = _front(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError):
        raise GovError("IMPACT_EXECUTION_MISSING", f"{rel}: no change-execution record can be read there",
                       {"path": str(rel)}) from None
    execution = str(front.get("id", rel))
    if front.get("type") != CITE_TYPE:
        raise GovError("IMPACT_NOT_AN_EXECUTION_RECORD", f"{rel} ({execution}) is no {CITE_TYPE}: its type is "
                       f"{front.get('type')!r}", {"path": str(rel)})
    named = front.get("proposal")
    if not isinstance(named, str) or not named:
        raise GovError("IMPACT_NO_PROPOSAL", f"{execution} names no proposal: its `proposal` key gives no CIT-P id",
                       {"execution": execution})
    record = _Records(root).by_id.get(named)
    if record is None or record["type"] != CITP_TYPE:
        what = "no record of the store" if record is None else f"a {record['type']}, no {CITP_TYPE}"
        raise GovError("IMPACT_PROPOSAL_UNKNOWN", f"{execution} names the proposal {named}, which is {what}",
                       {"execution": execution, "proposal": named})
    try:
        proposed = _lists((_front((root / record["path"]).read_text(encoding="utf-8")) or {}).get("affected"))
    except (OSError, UnicodeDecodeError):
        proposed = None
    done = _lists(front.get("affected"))
    for which, lists in ((execution, done), (named, proposed)):
        if lists is None:
            raise GovError("IMPACT_NOTHING_LISTED", f"{which} lists nothing under `affected`: the records cannot be "
                           "compared", {"execution": execution, "proposal": named})
    differences = [{"id": item, "kind": kind, "only_in": side}
                   for kind in sorted(set(proposed) | set(done))
                   for side, here, there in (("proposal", proposed, done), ("execution", done, proposed))
                   for item in sorted(here.get(kind, set()) - there.get(kind, set()))]
    return {"proposal": named, "execution": execution, "matches": not differences, "differences": differences}
