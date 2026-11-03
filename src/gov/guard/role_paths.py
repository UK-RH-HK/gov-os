"""Role separation from the path map, for what the product hands a caller (DEC-1065 (2), DEC-1052 G-14; W2-13 S5).

The path map's ``role_paths:`` section names, per role, the globs it may not read (``reads_denied``): the engineer
never reads its ticket's acceptance tests, the independent test designer never the engineer's new code. The guard's
hook (``.claude/hooks/role_reads.py``) refuses such reads; this module applies the same path checks to what a search
returns, so that ``gov retrieve`` and ``gov context``'s supplementary block never hand a role what the guard would
refuse it. It holds the hook's matching logic (``section``, the placeholders, ``expand``, ``Judge``, ``judges``), not
its reading of shell commands: a search names its paths itself.

The placeholders, as the hook fills them:
  {ticket_tests}  the session ticket's acceptance tests in every tree: tests/acceptance/<WBS>/**, and each file in
                  another ticket's tests/acceptance/<X>/ that a test designer's commit made for the ticket touched
                  (``linked_tests``; none for a coordination ticket);
  {ticket_impl}   the ticket's allowed_paths but tests/acceptance/ (less the shared test files), in the engineer's
                  tree ~/gov-os-worktrees/<WBS>; there only the files its branch changes against w2/integrate when
                  the searched tree is that tree, and in the designer's tests tree <WBS>-tests the files the
                  engineer's commits carried in. Every other tree holds integrated code: readable (DEC-963).

The caller (``caller``): the roles are ``GOV_ROLE`` and, beside it, a ``--role`` given to the command (a role given
can add its own filter, never lift the session's); the ticket is ``GOV_TICKET``. The section is read from the main
tree's path map (a branch cannot weaken it), the ticket from the searched tree's ``.tickets/``. No section, no role
the section names, or no rule the ticket fills: no filter (``caller`` gives None). A section or ticket that cannot be
read raises ``RolePathsError``: the search fails closed, as the hook does.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import tempfile

PATH_MAP_REL = "governance/project/path-map.yaml"
KEY = "role_paths"
ACCEPTANCE = "tests/acceptance"
WORKTREES = os.path.realpath(os.path.expanduser("~/gov-os-worktrees"))
RULE = f"{KEY}.<role>.reads_denied ({PATH_MAP_REL}, DEC-1065 (2))"
# the shared test files the designer needs for fixtures stay readable (the owner's (c3), 2026-11-03)
SHARED = ("conftest.py", "__init__.py", "*support*.py", "*helper*.py")
# one cache per session's scratch, apart from the hook's
LINK_CACHE = os.path.join(tempfile.gettempdir(), f"gov-os-role-paths-{os.getuid()}")


class RolePathsError(Exception):
    """The section or the session's ticket cannot be read: what a role may be handed cannot be worked out."""


def _git_env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


# -- the section ----------------------------------------------------------------------------------------------------

def section(tree) -> dict | None:
    """The ``role_paths:`` section of the path map at ``tree``, or None when it has none (no filter). A section that
    is not a mapping of roles to ``reads_denied`` lists of project-relative globs raises ``RolePathsError``."""
    try:
        with open(os.path.join(tree, PATH_MAP_REL), encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError):
        raise RolePathsError(f"{PATH_MAP_REL} cannot be read") from None
    block = _block(text)
    if block is None:
        return None
    import yaml
    try:
        doc = yaml.load(block, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader)) or {}
    except yaml.YAMLError:
        raise RolePathsError(f"{PATH_MAP_REL}: {KEY} cannot be read") from None
    found = doc.get(KEY) if isinstance(doc, dict) else None
    if found is None:
        raise RolePathsError(f"{PATH_MAP_REL}: {KEY} is empty")
    check(found)
    return found


def _block(text: str) -> str | None:
    """The ``role_paths:`` block's own lines (from its key to the next line at the margin), parsed alone, so that a
    YAML error elsewhere in the map does not stop every search; None with no such key; written twice, it raises."""
    lines = text.splitlines(keepends=True)
    at = [i for i, line in enumerate(lines) if re.match(r"role_paths\s*:", line)]
    if not at:
        return None
    if len(at) > 1:
        raise RolePathsError(f"{PATH_MAP_REL}: {KEY} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    return "".join(lines[at[0]:end])


def check(found) -> None:
    if not isinstance(found, dict):
        raise RolePathsError(f"{PATH_MAP_REL}: {KEY} is not a mapping of roles")
    for role, entry in found.items():
        globs = entry.get("reads_denied") if isinstance(entry, dict) else None
        if not isinstance(role, str) or not isinstance(globs, list) or \
                not all(isinstance(g, str) and g.strip() and not g.startswith("/") for g in globs):
            raise RolePathsError(f"{PATH_MAP_REL}: {KEY}.{role}: reads_denied is not a list of project-relative globs")


def main_tree(root) -> str:
    """The repository's main working tree (the folder of the common .git of the tree at ``root``), else ``root``."""
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             capture_output=True, text=True, timeout=5, env=_git_env()).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    if out and os.path.basename(out.rstrip("/")) == ".git":
        return os.path.realpath(os.path.dirname(out.rstrip("/")))
    return os.path.realpath(str(root))


# -- the ticket -----------------------------------------------------------------------------------------------------

def _ticket(root: str, ticket_id: str | None) -> tuple[set, str | None]:
    """The names the session's ticket goes by and its WBS id, as the guard reads them (gov.guard.reads._ticket)."""
    from gov.guard import reads
    try:
        return reads._ticket(root, ticket_id)
    except reads.PolicyError as error:
        raise RolePathsError(str(error)) from None


def ticket_front(root: str, ticket_id: str | None) -> dict:
    """The session ticket's front matter (its file, else the file whose wbs_id is the id); {} with no such ticket."""
    from gov.guard import reads
    if not ticket_id or "/" in ticket_id:
        return {}
    folder = os.path.join(root, ".tickets")
    path = os.path.join(folder, f"{ticket_id}.md")
    try:
        if not os.path.lexists(path):
            try:
                names = sorted(n for n in os.listdir(folder) if n.endswith(".md"))
            except FileNotFoundError:
                return {}
            line = re.compile(r"^wbs_id:[ \t]*['\"]?" + re.escape(ticket_id) + r"['\"]?[ \t]*$", re.M)
            path = next((os.path.join(folder, n) for n in names
                         if line.search(reads._read_text(os.path.join(folder, n)))), None)
            if path is None:
                return {}
        text = reads._read_text(path)
    except (OSError, reads.PolicyError):
        raise RolePathsError("the session's ticket file cannot be read") from None
    head = text.split("\n---", 1)[0][4:] if text.startswith("---\n") else ""
    import yaml
    try:
        front = yaml.load(head, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    except Exception:
        front = None
    return front if isinstance(front, dict) else {}


def coordination(front) -> bool:
    """A coordination ticket (``class: coordination``, as W2-00): it has no acceptance tests of its own."""
    return isinstance(front, dict) and str(front.get("class") or "").strip() == "coordination"


# -- what git says --------------------------------------------------------------------------------------------------

def linked_tests(main: str, names, wbs: str):
    """The files (relative) under another ticket's tests/acceptance/<X>/ that a test designer's commit made for the
    ticket touched: a non-merge commit with Role: independent-test-designer whose Task: trailer names the ticket, or
    one on the first-parent line of w2/<WBS>-tests since it left w2/integrate. Kept in LINK_CACHE per (method,
    repository, names, the three heads). None when git cannot say: then only the ticket's own folder is judged."""
    def git(*args, ok=(0,)):
        r = subprocess.run(["git", "-C", main, *args], capture_output=True, text=True, timeout=10, env=_git_env())
        if r.returncode not in ok:
            raise OSError("git")
        return r.stdout
    try:
        refs = ["w2/integrate", f"w2/{wbs}", f"w2/{wbs}-tests"]
        heads = [git("rev-parse", "--verify", "--quiet", r + "^{commit}", ok=(0, 1)).strip() or "-" for r in refs]
        key = "|".join([_method(), os.path.realpath(main), *sorted(n for n in names if n), *heads])
        cached = os.path.join(LINK_CACHE, hashlib.sha256(key.encode()).hexdigest()[:24] + ".json")
        try:
            with open(cached, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("key") == key and isinstance(data.get("files"), list):
                return set(data["files"])
        except (OSError, ValueError):
            pass
        fmt = ("--format=@@%H%x1f%(trailers:key=Task,valueonly,separator=%x2C)"
               "%x1f%(trailers:key=Role,valueonly,separator=%x2C)")
        grep = [a for n in sorted(n for n in names if n) for a in ("--grep", n)]
        out = git("log", "--all", "--no-merges", "-F", *grep, fmt, "--name-only", "--no-renames", "--",
                  ACCEPTANCE + "/") if grep else ""
        found = _files_of(out, names, wbs, need_task=True)
        if heads[2] != "-":
            fork = _fork(git, f"w2/{wbs}-tests")
            if fork:
                out = git("log", "--first-parent", "--no-merges", f"{fork}..w2/{wbs}-tests", fmt, "--name-only",
                          "--no-renames", "--", ACCEPTANCE + "/")
                found |= _files_of(out, names, wbs, need_task=False)
    except (OSError, subprocess.SubprocessError):
        return None
    try:
        os.makedirs(LINK_CACHE, mode=0o700, exist_ok=True)
        tmp = cached + f".{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"key": key, "files": sorted(found)}, f)
        os.replace(tmp, cached)
    except OSError:
        pass
    return found


def _fork(git, branch):
    """Where ``branch`` left w2/integrate: the first commit on its first-parent line on w2/integrate's own."""
    line = set(git("rev-list", "--first-parent", "w2/integrate").split())
    return next((c for c in git("rev-list", "--first-parent", branch).split() if c in line), None)


_METHOD: list = []


def _method() -> str:
    """This module's own sha256 (12 digits): the link cache's method key (a changed rule never reads an older list)."""
    if not _METHOD:
        with open(os.path.abspath(__file__), "rb") as f:
            _METHOD.append(hashlib.sha256(f.read()).hexdigest()[:12])
    return _METHOD[0]


def _files_of(out: str, names, wbs: str, need_task: bool) -> set:
    found, keep = set(), False
    for line in out.splitlines():
        if line.startswith("@@"):
            _h, task, role = (line[2:].split("\x1f") + ["", ""])[:3]
            tasks = {t.strip() for t in task.split(",")}
            keep = "independent-test-designer" in role and (not need_task or bool(tasks & set(names)))
        elif keep and line.strip():
            parts = line.strip().split("/")
            if len(parts) >= 4 and "/".join(parts[:2]) == ACCEPTANCE and parts[2] != wbs:
                found.add(line.strip())
    return found


def changed(tree: str):
    """The files (relative) the branch at ``tree`` changes against its merge base with w2/integrate, committed or
    not; None when git cannot say (then nothing there is filtered)."""
    def git(*args):
        p = subprocess.run(["git", "-C", tree, *args], capture_output=True, text=True, timeout=5, env=_git_env())
        if p.returncode:
            raise OSError("git")
        return p.stdout
    try:
        base = git("merge-base", "w2/integrate", "HEAD").strip()
        names = git("diff", "--name-only", "--no-renames", "-z", base).split("\0")
        names += git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
        return {n for n in names if n}
    except (OSError, subprocess.SubprocessError):
        return None


def engineer_side(tree: str, wbs: str):
    """The files (relative) the ticket branch's commits carried into the designer's tests tree ``tree``; None when
    git cannot say."""
    def git(*args, ok=(0,)):
        p = subprocess.run(["git", "-C", tree, *args], capture_output=True, text=True, timeout=5, env=_git_env())
        if p.returncode not in ok:
            raise OSError("git")
        return p
    try:
        base = git("merge-base", "w2/integrate", "HEAD").stdout.strip()
        fork = "HEAD"
        if git("rev-parse", "--verify", "--quiet", f"refs/heads/w2/{wbs}", ok=(0, 1)).returncode == 0:
            fork = git("merge-base", f"w2/{wbs}", "HEAD").stdout.strip()
        names = git("log", "--format=", "--name-only", "--no-renames", "-z", f"{base}..{fork}").stdout
        return {n.strip("\n") for n in names.split("\0") if n.strip("\n")}
    except (OSError, subprocess.SubprocessError):
        return None


def shared(full: str) -> bool:
    """A shared test file: any conftest.py, a package's __init__.py, a support or helper module."""
    name = os.path.basename(full)
    return any(fnmatch.fnmatchcase(name, g) for g in SHARED)


def _once(fn):
    """``fn`` called at most once (its answer kept)."""
    kept = []

    def call():
        if not kept:
            kept.append(fn())
        return kept[0]
    return call


# -- the denied globs -----------------------------------------------------------------------------------------------

class Denied:
    """One denied glob: its tree (None: every tree), the glob, the path map's entry it comes from; ``only``, a
    callable giving the files (relative) that alone are named in that tree (None from it: none are)."""

    def __init__(self, tree, glob, entry, only=None, keep_shared=False):
        from gov.guard import reads
        self.tree, self.glob, self.entry, self.only, self.keep_shared = tree, glob, entry, only, keep_shared
        self._reads, self._part = reads, {}

    def part(self, tree):
        if tree not in self._part:
            self._part[tree] = self._reads._Part(tree, [self.glob], "")
        return self._part[tree]

    def names(self, full: str) -> bool:
        """Whether ``full`` (a real path) is named by this glob in its own tree."""
        if not self.part(self.tree).inside(full) or self.keep_shared and shared(full):
            return False
        if self.only is None:
            return True
        found = self.only()
        return found is not None and full[len(self.tree) + 1:] in found


class Linked:
    """{ticket_tests}'s files outside the ticket's own folder, in every tree, worked out from git only when a path
    names another folder's acceptance tests."""

    def __init__(self, main, names, wbs, entry, source=None):
        self.tree, self.glob, self.entry, self.only = None, "the ticket's cases revised in other folders", entry, None
        self.wbs = wbs
        self.files = _once(lambda: (source or linked_tests)(main, names, wbs))

    def names_rel(self, rel: str) -> bool:
        if not rel.startswith(ACCEPTANCE + "/") or rel.startswith(f"{ACCEPTANCE}/{self.wbs}/"):
            return False
        found = self.files()
        return bool(found) and any(rel == f or rel.startswith(f + "/") for f in found)


def expand(entries, wbs, allowed, root=None, changes=None, tests_changes=None, main=None, names=(),
           links=None) -> list:
    """The path map's entries for a role as Denied globs, the placeholders filled from the ticket (its WBS id and
    allowed_paths); a placeholder the ticket cannot fill names nothing. ``root`` is the searched tree: when it is the
    engineer's own tree, the ticket's paths there name only the files its branch changes (``changes``); when it is
    the designer's tests tree, also the files the engineer's commits carried in (``tests_changes``)."""
    out, changes, tests_changes = [], changes or changed, tests_changes or engineer_side
    own = os.path.join(WORKTREES, wbs) if wbs else None
    real = os.path.realpath(root) if root else None
    only = _once(lambda: changes(own)) if own and real == os.path.realpath(own) else None
    tests_tree = real if own and real == os.path.realpath(own) + "-tests" else None
    carried = _once(lambda: tests_changes(tests_tree, wbs)) if tests_tree else None
    for entry in entries:
        if "{ticket_tests}" in entry:
            if wbs:
                out.append(Denied(None, entry.replace("{ticket_tests}", f"{ACCEPTANCE}/{wbs}/**"), entry))
                if links is not False and (main or root):
                    out.append(Linked(main or root, set(names) | {wbs}, wbs, entry,
                                      links if callable(links) else None))
        elif "{ticket_impl}" in entry or "{ticket_impl_code}" in entry:
            no_docs = "{ticket_impl_code}" in entry
            for p in allowed if own else ():
                p = p.strip().lstrip("./") if isinstance(p, str) else ""
                if not p or p.startswith(ACCEPTANCE + "/") or p == ACCEPTANCE or (p.startswith("docs/") and no_docs):
                    continue
                out.append(Denied(own, p, entry, only, keep_shared=True))
                if tests_tree:
                    out.append(Denied(tests_tree, p, entry, carried, keep_shared=True))
        elif "{ticket_" not in entry:
            out.append(Denied(None, entry, entry))
    return out


class Judge:
    """The denied globs of one role, judged against the trees a plain glob applies in."""

    def __init__(self, role, denied, trees):
        self.role, self.denied, self._trees, self._all = role, denied, trees, None

    def trees(self) -> list:
        """The given trees and each folder under ~/gov-os-worktrees/."""
        if self._all is None:
            found = list(self._trees() if callable(self._trees) else self._trees)
            try:
                found += [os.path.join(WORKTREES, n) for n in sorted(os.listdir(WORKTREES))]
            except OSError:
                pass
            self._all = list(dict.fromkeys(os.path.realpath(t) for t in found))
        return self._all

    def hit(self, full: str):
        """The Denied glob ``full`` (an absolute path) is at or under, or None."""
        full = os.path.realpath(full)
        trees = [t for t in self.trees() if full.startswith(t + "/")]
        if full.startswith(WORKTREES + "/"):
            trees.append(os.path.join(WORKTREES, full[len(WORKTREES) + 1:].split("/")[0]))
        for d in self.denied:
            if isinstance(d, Linked):
                if any(d.names_rel(full[len(t) + 1:]) for t in trees):
                    return d
            elif d.tree is not None:
                if d.names(full):
                    return d
            elif any(d.part(t).inside(full) for t in trees):
                return d
        return None


def judges(sec, roles, root, ticket_id, trees, main=None, links=None) -> list:
    """A Judge per role the section names; the ticket is read only when a role's globs need it."""
    out, front, wbs, names = [], None, None, set()
    for role in roles:
        entry = sec.get(role) if role else None
        if not entry:
            continue
        globs = entry["reads_denied"]
        if any("{ticket_" in g for g in globs) and front is None:
            names, wbs = _ticket(root, ticket_id)
            front = ticket_front(root, ticket_id) if any("{ticket_impl" in g for g in globs) else {}
            if not wbs and isinstance(front.get("wbs_id"), str):
                wbs = front["wbs_id"]
        allowed = front.get("allowed_paths") if isinstance(front, dict) else None
        if isinstance(front, dict) and isinstance(front.get("id"), str):
            names = set(names) | {front["id"]}
        source = links if links is not None else _links_unless_coordination(root, ticket_id, front)
        out.append(Judge(role, expand(globs, wbs, allowed if isinstance(allowed, list) else [], root, main=main,
                                      names=names, links=source), trees))
    return out


def _links_unless_coordination(root, ticket_id, front):
    """{ticket_tests}'s link source: none for a coordination ticket (its own folder only), linked_tests otherwise;
    a ticket that cannot be read gives None (only the own folder)."""
    def links(main, names, wbs):
        try:
            seen = front if front else ticket_front(root, ticket_id)
        except RolePathsError:
            return None
        return set() if coordination(seen) else linked_tests(main, names, wbs)
    return links


# -- the caller's filter --------------------------------------------------------------------------------------------

def roles_of(role=None) -> list:
    """The caller's roles: ``GOV_ROLE`` and, beside it, a role given (``--role``); empty ones left out."""
    return [r for r in dict.fromkeys(((os.environ.get("GOV_ROLE") or "").strip(), (role or "").strip())) if r]


class Filter:
    """What the caller's roles may not be handed, by path; ``denied(rel)`` gives the rule that withholds a
    project-relative path, and ``summary`` counts what was withheld, by rule (DEC-1065 (2): never silently)."""

    def __init__(self, root, roles, ticket, judges_):
        self.root, self.roles, self.ticket, self._judges = os.path.realpath(str(root)), roles, ticket, judges_
        self._seen: dict = {}
        self._counts: dict = {}

    def denied(self, rel: str):
        """(role, entry, glob) of the rule that withholds ``rel`` (a path relative to the searched tree), or None."""
        if rel not in self._seen:
            found = None
            full = os.path.join(self.root, rel)
            for j in self._judges:
                d = j.hit(full)
                if d is not None:
                    found = (j.role, d.entry, d.glob)
                    break
            self._seen[rel] = found
        return self._seen[rel]

    def keep(self, items) -> list:
        """``items`` (dicts with ``path`` and ``chunk_id``) without those whose path is withheld; each withheld one
        counted under its rule, a chunk once however many routes named it."""
        out = []
        for item in items:
            rule = self.denied(item["path"])
            if rule is None:
                out.append(item)
                continue
            paths, chunks = self._counts.setdefault(rule, (set(), set()))
            paths.add(item["path"])
            chunks.add(item.get("chunk_id") or item["path"])
        return out

    def summary(self) -> dict:
        """How many paths and chunks were withheld, by which rule (role, the path map's entry, the glob it filled)."""
        by = [{"role": role, "rule": entry, "glob": glob, "paths": len(paths), "chunks": len(chunks)}
              for (role, entry, glob), (paths, chunks) in sorted(self._counts.items())]
        return {"roles": list(self.roles), "ticket": self.ticket, "rule": RULE,
                "withheld": {"paths": len({p for paths, _c in self._counts.values() for p in paths}),
                             "chunks": len({c for _p, chunks in self._counts.values() for c in chunks})},
                "by": by}


def caller(root, role=None, ticket=None, main=None, links=None, also=()) -> Filter | None:
    """The filter for the caller (``GOV_ROLE`` and ``role``; ``ticket``, else ``GOV_TICKET``, and each ticket in
    ``also``, as a packet's own ticket: the union of their rules, which can only add) searching the tree at ``root``;
    None when the main tree's path map has no ``role_paths:`` section, names none of the roles, or no rule is
    filled. Raises ``RolePathsError`` when the section or a ticket cannot be read."""
    roles = roles_of(role)
    if not roles:
        return None
    root = os.path.realpath(str(root))
    main = main or main_tree(root)
    sec = section(main)
    if not sec or not any(r in sec for r in roles):
        return None
    if ticket is None:
        ticket = os.environ.get("GOV_TICKET") or None
    tickets = [t for t in dict.fromkeys([ticket, *also]) if t] or [None]  # review S5-F1: the packet's ticket too
    found = [j for t in tickets for j in judges(sec, roles, root, t, [root, main], main=main, links=links)]
    if not any(j.denied for j in found):
        return None
    return Filter(root, list(dict.fromkeys(j.role for j in found)), ", ".join(t for t in tickets if t) or None, found)
