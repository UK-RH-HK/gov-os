"""The decision checker (CAP-51.a, CAP-01.b, CAP-21.a, CAP-34.d): findings over the decisions, gates and tickets.

It only reads, and only frontmatter and git (DEC-329): every file is read from
``HEAD`` as the store reads it, never from the working tree, and no git command
it runs writes or fetches. An empty list passes; the check does not fail open.

- It checks the repository at ``root``: git runs without the caller's ``GIT_*``
  variables (``GIT_DIR`` is set in a hook). An object git names and the
  repository does not hold is a ``GovError``, never "no such file".

- A decision file is a Markdown file whose frontmatter has ``type: decision`` or
  an ``id`` of the ``decision_id`` grammar; it need not be a record of the store.
  Supersession is one edge from the successor, read from ``supersedes`` and from
  ``superseded_by`` (DEC-277).
- The owner's approval fact is the ``Role: owner`` trailer on the commit that
  last set the decision ``ACTIVE`` (DEC-360), read from the final trailer block;
  a commit made before 2026-10-03 is read from the whole message (DEC-182). A
  commit that also carries another role is no approval. That commit is found
  by ancestry from ``HEAD``, not by date, and the decision is followed by its
  ``id``: a commit that only moves the file sets nothing. A merge that keeps
  one parent's decision sets nothing only where what each other parent holds
  is the earlier word: the commits that set the kept decision descend from it.
  Otherwise the merge is the commit that set it (a demotion undone, DEC-360;
  two sides that disagree, which no decision settles, fail closed).
- A gate authorises a file that cites it in ``approval`` only when it is a
  decision package, its ``status`` is ``ACCEPTED`` and both carry the same
  ``cit`` (DEC-331); the citing file need not have an ``id``. A ticket that is
  not closed and is named in the ``constrains`` of a dead package fails
  (DEC-330).
- Frontmatter that is not closed, is not valid YAML or writes a key twice
  cannot be read: the file is a finding, whatever kind of file it is.
"""

from __future__ import annotations

import os
import posixpath
import re
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.store.loader import TRAILER_RULE_DATE, _frontmatter, _ids
from gov.tasks.tickets import TICKETS_REL

DECISION_ID = re.compile(r"(ADR|DEC)-[0-9]{3,}")  # the kernel's decision_id grammar (common.schema.json)
GATE_TYPE = "decision-package"
GATE_DEAD = ("DECLINED", "REVOKED", "STALE")  # DEC-328

_ROLE = re.compile(r"^Role:[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_ROLE_FORMAT = "--format=%cs%n%(trailers:key=Role,unfold)%x00%B"  # no date and no trailer holds a NUL
_GIT = ("git", "-c", "protocol.allow=never")  # with GIT_NO_LAZY_FETCH: a partial clone is read as it is


def _environment() -> dict:
    """The caller's environment without its git variables, which may name another repository, and no fetching."""
    return {**{key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
            "GIT_NO_LAZY_FETCH": "1"}


def _git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run([*_GIT, "-C", str(root), *args], capture_output=True, check=True,
                              env=_environment()).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        reason = " ".join(getattr(exc, "stderr", b"").decode("utf-8", "replace").split()) or str(exc)
        raise GovError("DECISIONS_GIT_FAILED", f"git {args[0]} failed in {root}: {reason}",
                       {"root": str(root)}) from None


def _finding(code: str, ids, paths, message: str) -> dict:
    return {"code": code, "ids": list(ids), "paths": sorted(set(paths)), "message": message}


def _front(text: str) -> dict:
    """The frontmatter map of ``text``, empty when it has none; ValueError when it cannot be read.

    Read as the store reads it, and a key written twice cannot be read: YAML would keep the last in silence."""
    import yaml

    front = _frontmatter(text)
    if front is None:
        return {}
    lines = [line.rstrip() for line in text.split("\n")]
    node = yaml.compose("\n".join(lines[1:lines.index("---", 1)]))
    keys = [key.value for key, _ in node.value if isinstance(key, yaml.ScalarNode)] \
        if isinstance(node, yaml.MappingNode) else []
    if len(keys) != len(set(keys)):
        raise ValueError("the frontmatter writes a key twice")
    return front if isinstance(front, dict) else {}


def _read(root: Path, objects: _Objects) -> tuple[list[tuple[str, dict]], list[dict]]:
    """``(path, frontmatter)`` of every Markdown file of ``HEAD``, and a finding for each that cannot be read."""
    files, found = [], []
    for entry in _git(root, "ls-tree", "-r", "-z", "HEAD").decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        if not path.endswith(".md") or meta.split()[1] != "blob":
            continue
        blob = objects.read(meta.split()[2])
        if blob is None:
            raise objects.unreadable(f"HEAD:{path}")
        try:
            front = _front(blob[1].decode("utf-8", "replace"))
        except ValueError as exc:
            front = {}
            found.append(_finding("FRONTMATTER_UNREADABLE", [], [path], f"{path}: {exc}"))
        files.append((path, front))
    return files, found


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


class _Objects:
    """One ``git cat-file --batch`` process: the commits of the repository and the files of their trees."""

    def __init__(self, root: Path):
        self.root, self.fronts = root, {}
        self.process = subprocess.Popen([*_GIT, "-C", str(root), "cat-file", "--batch"], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=_environment())

    def close(self) -> None:
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.wait()

    def read(self, name: str) -> tuple[str, bytes] | None:
        """``(object id, content)`` of the object ``name``; None when the repository has none."""
        if "\n" in name:  # a name the batch cannot ask for
            return None
        try:
            self.process.stdin.write(name.encode("utf-8") + b"\n")
            self.process.stdin.flush()
            header = self.process.stdout.readline().split()
            if header[-1] == b"missing":
                return None
            return header[0].decode("ascii"), self.process.stdout.read(int(header[-1]) + 1)[:-1]
        except (OSError, ValueError, IndexError):
            raise GovError("DECISIONS_GIT_FAILED", f"git cat-file failed in {self.root} at {name!r}",
                           {"root": str(self.root)}) from None

    def unreadable(self, name: str) -> GovError:
        return GovError("DECISIONS_OBJECT_UNREADABLE", f"{name}: git names the object and {self.root} does not "
                        "hold it", {"root": str(self.root), "object": name})

    def parents(self, commit: str) -> list[str]:
        header = self.read(commit)[1].split(b"\n\n")[0]
        return [line.split()[1].decode("ascii") for line in header.split(b"\n") if line.startswith(b"parent ")]

    def names(self, commit: str, path: str) -> bool:
        """Whether the trees of ``commit`` name ``path``, read without the object they name it by."""
        tree = self.read(commit + "^{tree}")
        for part in path.encode("utf-8").split(b"/"):
            if tree is None:
                raise self.unreadable(f"{commit}:{path}")
            entries, content, width = {}, tree[1], len(tree[0]) // 2
            while content:  # an entry is its mode, a space, its name, a NUL and the object id in bytes
                name, _, rest = content.partition(b" ")[2].partition(b"\0")
                entries[name], content = rest[:width].hex(), rest[width:]
            if part not in entries:
                return False
            tree = self.read(entries[part])
        return True

    def file(self, commit: str, path: str) -> tuple:
        """``(blob, id, status)`` of ``path`` in ``commit``: no blob where it has no such file, no id and no
        status where the file has no frontmatter that can be read. A file whose object is absent is an error."""
        entry = self.read(f"{commit}:{path}")
        if entry is None:
            if self.names(commit, path):
                raise self.unreadable(f"{commit}:{path}")
            return None, None, None
        if entry[0] not in self.fronts:
            try:
                front = _front(entry[1].decode("utf-8", "replace"))
            except ValueError:
                front = {}
            self.fronts[entry[0]] = (str(front["id"]) if "id" in front else None, front.get("status"))
        return (entry[0], *self.fronts[entry[0]])


def _setters(root: Path, objects: _Objects, path: str, record_id: str) -> set[str]:
    """The commits that set ACTIVE the decision ``record_id`` that ``HEAD`` holds at ``path``.

    Walked by ancestry from ``HEAD``. A commit whose file is a parent's file sets nothing; one that writes the
    file sets nothing where a parent held the decision ACTIVE, at this path or in a Markdown file the commit
    removes (a move). The commits that set it are then those of the parents it continues, unless it has another
    parent whose word is not the earlier one (``_earlier``): then, as where it continues no parent, it set it."""
    start = (objects.read("HEAD")[0], path)
    if objects.file(*start)[0] is None:  # a path the batch cannot ask for
        return set()
    held, sets, todo = {}, {}, [start]
    while todo:  # a commit is settled after the parents it continues or is compared with
        at = commit, path = todo[-1]
        if at in sets:
            todo.pop()
            continue
        if at not in held:
            held[at] = _held(root, objects, commit, path, record_id)
        before, others = held[at]
        todo += [older for older in before + [(other, path) for other in others
                                              if objects.file(other, path)[1:] == (record_id, "ACTIVE")]
                 if older not in sets]
        if todo[-1] != at:
            continue
        found = set().union(*(sets[older] for older in before))
        if not found or not all(_earlier(root, objects, other, path, record_id, sets, found) for other in others):
            found = {commit}
        sets[at] = found
    return sets[start]


def _held(root: Path, objects: _Objects, commit: str, path: str, record_id: str) -> tuple[list, list]:
    """``(parent, path)`` wherever a parent of ``commit`` holds the decision its file continues, and the parents
    that hold none such."""
    blob, parents = objects.file(commit, path)[0], objects.parents(commit)
    before = [(parent, path) for parent in parents if objects.file(parent, path)[0] == blob]
    for parent in () if before else parents:
        olds = [path]
        if objects.file(parent, path)[1] != record_id:
            removed = _git(root, "diff-tree", "-r", "-z", "--no-renames", "--name-only", "--diff-filter=D",
                           parent, commit).decode("utf-8", "replace").split("\0")
            olds = [old for old in removed if old.endswith(".md")]
        before += [(parent, old) for old in olds if objects.file(parent, old)[1:] == (record_id, "ACTIVE")]
    return before, [parent for parent in parents if parent not in {kept for kept, _ in before}]


def _earlier(root: Path, objects: _Objects, other: str, path: str, record_id: str, sets: dict, found: set) -> bool:
    """Whether what ``other`` holds at ``path`` is the earlier word: every commit of ``found`` descends from it.

    Its word is the commits that set its own ACTIVE decision, or else the commits it descends from that hold the
    same id and status (or no file) without a break. A demotion made after the approval is no earlier word."""
    older = [set(_git(root, "rev-list", setter).decode("ascii").split()) for setter in sorted(found)]
    state = objects.file(other, path)[1:]
    if state == (record_id, "ACTIVE"):
        return all(sets[(other, path)] & ancestors for ancestors in older)
    seen, todo = set(), [other]
    while todo and older:
        commit = todo.pop()
        if commit in seen or objects.file(commit, path)[1:] != state:
            continue
        seen.add(commit)
        older = [ancestors for ancestors in older if commit not in ancestors]
        todo += reversed(objects.parents(commit))
    return not older


def _approves(root: Path, commit: str) -> bool:
    """Whether ``commit`` carries the owner's approval fact: `Role: owner`, and no other role."""
    shown = _git(root, "show", "-s", _ROLE_FORMAT, commit).decode("utf-8", "replace")
    head, _, message = shown.partition("\0")
    date, _, final_block = head.partition("\n")
    roles = {role.strip() for role in _ROLE.findall(message if date < TRAILER_RULE_DATE else final_block)}
    return roles == {"owner"}


def _unapproved(root: Path, objects: _Objects, decisions: list[tuple[str, str, dict]]) -> list[dict]:
    """Every ACTIVE decision that a commit without the owner's approval fact set ACTIVE (DEC-360)."""
    found = []
    for path, record_id, front in decisions:
        if front.get("status") != "ACTIVE":
            continue
        setters = _setters(root, objects, path, record_id)
        if not setters or not all(_approves(root, commit) for commit in sorted(setters)):
            found.append(_finding("ACTIVE_UNAPPROVED", [record_id], [path],
                                  f"{record_id} was set ACTIVE by a commit without the trailer `Role: owner`"))
    return found


def _gates(files: list[tuple[str, dict]]) -> list[dict]:
    """Files that cite a gate that does not authorise them, and open tickets that wait on a dead package."""
    found, by_id, tickets = [], {}, {}
    for path, front in files:
        if "id" in front:
            by_id.setdefault(str(front["id"]), []).append(front)
        if posixpath.dirname(path) == TICKETS_REL:  # a ticket is known by its file name, as the READY rule knows it
            tickets[posixpath.basename(path)[:-len(".md")]] = (path, front.get("status"))
    for path, front in files:  # a file that cites a gate is checked with or without an id of its own
        own, cit = [str(front["id"])] if "id" in front else [], front.get("cit")
        for cited in sorted(set(_ids(front.get("approval")))):
            gates = by_id.get(cited, [])
            if not gates or not all(gate.get("type") == GATE_TYPE and gate.get("status") == "ACCEPTED"
                                    and isinstance(cit, str) and cit and gate.get("cit") == cit for gate in gates):
                found.append(_finding("GATE_NOT_AUTHORISING", own + [cited], [path],
                                      f"{(own or [path])[0]} cites {cited}, which is no accepted gate of its CIT"))
        if not own:
            continue
        record_id = own[0]
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
    objects = _Objects(root)
    try:
        files, found = _read(root, objects)
        decisions = [(path, str(front["id"]), front) for path, front in files if "id" in front
                     and (front.get("type") == "decision" or DECISION_ID.fullmatch(str(front["id"])))]
        found += _hazards(decisions) + _unapproved(root, objects, decisions) + _gates(files)
    finally:
        objects.close()
    return sorted(found, key=lambda finding: (finding["code"], finding["ids"], finding["paths"]))
