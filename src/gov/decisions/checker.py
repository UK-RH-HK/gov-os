"""The decision checker (CAP-51.a, CAP-01.b, CAP-21.a, CAP-34.d): findings over the decisions, gates and tickets.

It only reads, and only frontmatter and git (DEC-329): every file is read from
``HEAD`` as the store reads it, never from the working tree, and no git command
it runs writes or fetches. An empty list passes; the check does not fail open.

- It checks the repository at ``root``: git runs without the caller's ``GIT_*``
  variables (``GIT_DIR`` is set in a hook) and with replace refs off
  (DEC-387). An object git names and the repository does not hold is a
  ``GovError``, never "no such file".

- A decision file is a Markdown file whose frontmatter has ``type: decision`` or
  an ``id`` of the ``decision_id`` grammar; it need not be a record of the store.
  Supersession is one edge from the successor, read from ``supersedes`` and from
  ``superseded_by`` (DEC-277).
- The owner's approval fact is the ``Role: owner`` trailer on the commit that
  last set the decision ``ACTIVE`` (DEC-360), read from the final trailer block;
  a commit made before 2026-10-03 is read from the whole message (DEC-182). A
  commit that also carries another role is no approval. That commit is found
  by ancestry from ``HEAD``, not by date, and the decision is followed by its
  ``id``: a commit that only moves the file sets nothing.
- A merge is read only through ``read_merge``, the helper shared with
  containment (DEC-398, DEC-418). A merge that holds the file every parent
  holds sets nothing. Otherwise it sets nothing only where a parent brought
  the file, a parent holds the decision ``ACTIVE``, no other parent changed
  its id, status or presence since the one merge base of the two, and the
  commits that set it in every parent that holds it ``ACTIVE`` carry the
  fact. In every other case the merge is the change and its own trailer the
  fact: also with several merge bases or none, where the helper brings
  nothing. A merge the helper cannot read approves nothing.
- A gate authorises a file that cites it in ``approval`` only when it is a
  decision package, its ``status`` is ``ACCEPTED`` and both carry the same
  ``cit`` (DEC-331); the citing file need not have an ``id``. A ticket that is
  not closed and is named in the ``constrains`` of a dead package fails
  (DEC-330).
- Frontmatter that is not closed, is not valid YAML or writes a key twice
  cannot be read: the file is a finding, whatever kind of file it is. So is a
  head that looks like frontmatter and that the store does not read as such
  (DEC-387), and a file with ``type: decision`` and no ``id``.
"""

from __future__ import annotations

import os
import posixpath
import re
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.guard.containment_merge import read_merge
from gov.store.loader import TRAILER_RULE_DATE, _frontmatter, _ids
from gov.tasks.tickets import TICKETS_REL

DECISION_ID = re.compile(r"(ADR|DEC)-[0-9]{3,}")  # the kernel's decision_id grammar (common.schema.json)
GATE_TYPE = "decision-package"
GATE_DEAD = ("DECLINED", "REVOKED", "STALE")  # DEC-328

_ROLE = re.compile(r"^Role:[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_ROLE_FORMAT = "--format=%cs%n%(trailers:key=Role,unfold)%x00%B"  # no date and no trailer holds a NUL
_GIT = ("git", "--no-replace-objects", "-c", "protocol.allow=never")  # with GIT_NO_LAZY_FETCH: nothing is fetched
_HEAD = re.compile(r"---(\s.*)?")  # a first line that opens frontmatter for a reader, as `--- # c` does


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

    Read as the store reads it. A key written twice cannot be read (YAML would keep the last in silence), nor can
    a head that looks like frontmatter and that the store takes for none."""
    import yaml

    front = _frontmatter(text)
    if front is None:  # DEC-387: after a byte-order mark or blank lines, with CR line ends or in UTF-16
        head = text.lstrip("\ufeff\ufffd\0 \t\r\n")[:99].replace("\0", "").splitlines()[:1]
        if head and _HEAD.fullmatch(head[0].strip()):
            raise ValueError("the head looks like frontmatter and the store does not read it as frontmatter")
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
        self.root, self.fronts, self.known = root, {}, {}
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
        return _once(self, ("parents", commit), lambda: [
            line.split()[1].decode("ascii") for line in self.read(commit)[1].split(b"\n\n")[0].split(b"\n")
            if line.startswith(b"parent ")])

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
        return _once(self, (commit, path), lambda: self._file(commit, path))

    def _file(self, commit: str, path: str) -> tuple:
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


def _once(objects: _Objects, key: tuple, make):
    """What ``make`` gives, asked once in a check: one read or one git process serves every decision that needs it."""
    if key not in objects.known:
        objects.known[key] = make()
    return objects.known[key]


def _approved(root: Path, objects: _Objects, path: str, record_id: str) -> bool:
    """Whether the decision ``record_id`` that ``HEAD`` holds ACTIVE at ``path`` carries the owner's fact.

    Walked by ancestry from ``HEAD``. A commit that continues the ACTIVE decision of its parents (``_held``) is
    approved as they are; the commit that is the change is approved by its own trailer."""
    start = (objects.read("HEAD")[0], path)
    if objects.file(*start)[0] is None:  # a path the batch cannot ask for
        return False
    held, passes, todo = {}, {}, [start]
    while todo:  # a commit is settled after the parents it continues
        at = todo[-1]
        if at not in held:
            held[at] = _held(root, objects, *at, record_id)
        before, change = held[at]
        todo += [older for older in before if older not in passes]
        if todo[-1] != at:
            continue
        todo.pop()
        passes[at] = (bool(before) and all(passes[older] for older in before)
                      or change and _once(objects, ("fact", at[0]), lambda: _approves(root, at[0])))
    return passes[start]


def _removed(root: Path, objects: _Objects, older: str, newer: str) -> list[str]:
    """The Markdown files of ``older`` that ``newer`` does not hold, without rename detection."""
    return _once(objects, ("removed", older, newer), lambda: [
        old for old in _git(root, "diff-tree", "-r", "-z", "--no-renames", "--name-only", "--diff-filter=D",
                            older, newer).decode("utf-8", "replace").split("\0") if old.endswith(".md")])


def _state(objects: _Objects, commit: str, paths: list, record_id: str) -> tuple:
    """``(path, status)`` of the decision in ``commit``, looked for by its id at ``paths``; no path where none of
    them holds it."""
    for path in paths:
        if objects.file(commit, path)[1] == record_id:
            return path, objects.file(commit, path)[2]
    return None, None


def _held(root: Path, objects: _Objects, commit: str, path: str, record_id: str) -> tuple[list, bool]:
    """``(before, change)``: the ``(parent, path)`` whose ACTIVE decision the file of ``commit`` continues, and
    whether the commit may itself be the change that set it ACTIVE, with its own trailer as the fact.

    A commit with one parent continues it where the parent held the decision ACTIVE, at this path or in a
    Markdown file the commit removes (a move); otherwise it is the change."""
    parents = list(dict.fromkeys(objects.parents(commit)))
    if len(parents) > 1:
        return _merged(root, objects, commit, parents, path, record_id)
    before = [(parent, old) for parent in parents
              for old in ([path] if objects.file(parent, path)[1] == record_id
                          else _removed(root, objects, parent, commit))
              if objects.file(parent, old)[1:] == (record_id, "ACTIVE")]
    return before, not before


def _merged(root: Path, objects: _Objects, commit: str, parents: list, path: str, record_id: str) -> tuple[list, bool]:
    """``_held`` for a commit with several parents: the merge rule (DEC-398), read through ``read_merge``.

    The file every parent holds continues them all, and the merge is no change. A path the helper does not list
    as brought is the merge's own change: so is every path where the parents have several merge bases or none.
    For a brought path the decision is looked for by its id, in each parent at the paths the merge changed and in
    the one merge base also among the files the kept parent removed (DEC-418); the merge continues the parents
    that hold it ACTIVE only where every other parent holds it as the merge base does."""
    blob = objects.file(commit, path)[0]
    if all(objects.file(parent, path)[0] == blob for parent in parents):
        return [(parent, path) for parent in parents], False
    try:
        reading = _once(objects, ("merge", commit), lambda: read_merge(str(root), commit))
    except ValueError:  # MergeReadError, or a path that is no text: a merge that cannot be read approves nothing
        return [], False
    paths = [path] + [other for other in reading.own + reading.brought if other.endswith(".md")]
    held = {parent: _state(objects, parent, paths, record_id) for parent in parents}
    kept = next((parent for parent in parents if held[parent][1] == "ACTIVE"), None)
    if path not in reading.brought or kept is None:
        return [], True
    for parent in parents:
        if parent == kept:
            continue
        bases = _once(objects, ("bases", kept, parent), lambda: _git(
            root, "merge-base", "--all", kept, parent).decode("ascii").split())
        if len(bases) != 1:
            return [], True
        at, was = _state(objects, bases[0], paths, record_id)
        if at is None:
            at, was = _state(objects, bases[0], _removed(root, objects, bases[0], kept), record_id)
        held[parent] = _state(objects, parent, paths + [at or path], record_id)
        if (held[parent][0] is None, held[parent][1]) != (at is None, was):
            return [], True
    return [(parent, old) for parent, (old, status) in held.items() if status == "ACTIVE"], True


def _approves(root: Path, commit: str) -> bool:
    """Whether ``commit`` carries the owner's approval fact: `Role: owner`, and no other role."""
    shown = _git(root, "show", "-s", _ROLE_FORMAT, commit).decode("utf-8", "replace")
    head, _, message = shown.partition("\0")
    date, _, final_block = head.partition("\n")
    roles = {role.strip() for role in _ROLE.findall(message if date < TRAILER_RULE_DATE else final_block)}
    return roles == {"owner"}


def _unapproved(root: Path, objects: _Objects, decisions: list[tuple[str, str, dict]]) -> list[dict]:
    """Every ACTIVE decision that a commit without the owner's approval fact set ACTIVE (DEC-360)."""
    return [_finding("ACTIVE_UNAPPROVED", [record_id], [path],
                     f"{record_id} was set ACTIVE by a commit without the trailer `Role: owner`")
            for path, record_id, front in decisions
            if front.get("status") == "ACTIVE" and not _approved(root, objects, path, record_id)]


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
        found += [_finding("DECISION_WITHOUT_ID", [], [path], f"{path}: a decision without an id cannot be followed")
                  for path, front in files if front.get("type") == "decision" and "id" not in front]
        found += _hazards(decisions) + _unapproved(root, objects, decisions) + _gates(files)
    finally:
        objects.close()
    return sorted(found, key=lambda finding: (finding["code"], finding["ids"], finding["paths"]))
