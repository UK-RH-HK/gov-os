"""Protected parts, the session's ticket names and the evaluation sets, as the guard's read rules read them (W2-150).

Moved from ``gov.guard.reads`` unchanged (DEC-1039 (2), DEC-1109 (2)), so that memory's measure
(``gov.retrieval.measure``) and the role filter (``gov.util.role_paths``) read them without importing the guard;
``gov.guard.reads`` imports every name from here. ``_Glob`` is ``gov.guard.protected._Glob`` and ``load_yaml_unique``
is ``gov.guard.heldout.load_yaml_unique``, copied as they stand: those two files are outside W2-150's paths, and
re-importing them from here is their follow-up.

Nothing here carries a path in a message (DEC-820).
"""

from __future__ import annotations

import os
import re
import stat

from gov.util.patterns import _has_glob
from gov.util.tickets import _parse_frontmatter

PATH_MAP_REL = "governance/project/path-map.yaml"
SETS_KEY = "evaluation_sets"
# The most files of a protected part, and the most a glob word expands to,
# that the rule reads: beyond, no answer comes in bounded time (DEC-562).
_MOST_FILES = 10000
# The deepest folder a glob with ``**`` is matched against, below the path itself.
_MOST_DEPTH = 64
_WBS_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
HIDDEN_REFUSAL = ("the call reads the hidden part of an evaluation set that "
                  "measures this session, which is refused to it (DEC-820 (d), "
                  "DEC-845)")
_WALK_FAULT = "a hidden part's folder cannot be walked"
_LONG_PART = "a protected part holds more files than the guard reads in bounded time"
_TICKET_FAULT = "the session's ticket file cannot be read for its WBS id"


class PolicyError(Exception):
    """What a session is refused cannot be worked out: its calls are refused
    (fail closed).  The text is fixed: it carries nothing of a file."""


def load_yaml_unique(stream):
    """yaml.safe_load that refuses a mapping with a key written twice:
    a reader that kept the last value would drop the first without a word."""
    import yaml

    class Loader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            mapping = super().construct_mapping(node, deep=deep)
            if len(mapping) != len(node.value):
                raise yaml.constructor.ConstructorError(
                    None, None, "a key is written twice", node.start_mark)
            return mapping

    return yaml.load(stream, Loader=Loader)


class _Glob:
    """A glob as a matcher of whole paths: ``**`` crosses folders, ``*`` and
    ``?`` stay inside one name, ``{a,b}`` is either, ``[...]`` any one
    character.

    The places of the path the pattern has reached are the bits of one
    number, and no place is tried twice: a match costs the length of the
    pattern, whatever stars it holds (DEC-562)."""

    def __init__(self, pattern: str):
        self.pattern = pattern

    def match(self, path: str) -> bool:
        pattern, n = self.pattern, len(path)
        at: dict[str, int] = {}  # a character -> the places where the path has it
        for k, c in enumerate(path):
            at[c] = at.get(c, 0) | 1 << k
        slash = at.get("/", 0)
        every = (1 << n + 1) - 1
        inside = (every >> 1) & ~slash  # the places of a character that is no slash
        last = pattern.rfind("]")
        groups: list[tuple[int, int]] = []  # open braces: where each began, what its alternatives reached
        cur, i = 1, 0
        while i < len(pattern) and (cur or groups):
            c = pattern[i]
            i += 1
            if pattern.startswith("**/", i - 1):
                cur |= (every & -(cur & -cur) & slash) << 1
                i += 2
            elif c == "*" and pattern.startswith("*", i):
                cur = every & -(cur & -cur)  # every place from the first one on
                i += 1
            elif c == "*":
                # The carry of the sum runs from a place to the end of its name.
                cur |= ((cur & inside) + inside) ^ inside
            elif c == "?" or (c == "[" and last > i):
                if c == "[":
                    i = pattern.index("]", i + 1) + 1
                cur = (cur & inside) << 1
            elif c == "{":
                groups.append((cur, 0))
            elif c == "}" and groups:
                cur |= groups.pop()[1]
            elif c == "," and groups:
                start, reached = groups[-1]
                groups[-1] = (start, reached | cur)
                cur = start
            else:
                cur = (cur & at.get(c, 0)) << 1
        for _, reached in groups:
            cur |= reached
        return bool(cur >> n & 1)


# -- the parts -----------------------------------------------------------------

class _Part:
    """One protected part of a project: project-relative globs in the path
    map's language (``*`` stays in one folder, ``**`` crosses folders); a
    path at or under one is in the part."""

    def __init__(self, root: str, globs: list[str], reason: str,
                 files: list[str] | None = None, base: str | None = None):
        self.root, self.globs, self.reason, self.base = root, globs, reason, base
        # A literal path, or a literal folder and ``/**``, is matched by its
        # words; another glob against the path and its folders, each of the
        # glob's depth when it has one (no ``**``, no braces).
        self.lead: list[str] = []
        self.rx: list[tuple[_Glob, int | None]] = []
        for g in globs:
            head = g[:-3] if g.endswith("/**") else g
            if not any(_has_glob(p) for p in head.split("/")):
                self.lead.append(head.rstrip("/"))
                continue
            for one in ([g, head] if head != g else [g]):
                free = "**" in one or "{" in one
                self.rx.append((_Glob(one), None if free else one.count("/") + 1))
        self._files = files
        # A hidden part fails closed on a folder it cannot walk, and is walked
        # only for a start at, in or above its tree (W2-84); (c)'s as before.
        self.strict = reason == HIDDEN_REFUSAL
        self.literals = [os.path.join(root, *g.split("/")[:next(
            (i for i, p in enumerate(g.split("/")) if _has_glob(p)), None)]) for g in globs]

    def rel(self, path: str) -> str | None:
        return path[len(self.root) + 1:] if path.startswith(self.root + "/") else None

    def inside(self, path: str) -> bool:
        return self.match(self.rel(path))

    def match(self, rel: str | None) -> bool:
        """Whether a path relative to the tree is at or under a glob."""
        if not rel:
            return False
        if any(rel == p or rel.startswith(p + "/") for p in self.lead):
            return True
        parts = rel.split("/")
        for rx, depth in self.rx:
            depths = ([depth] if depth else
                      [*range(1, min(len(parts), _MOST_DEPTH) + 1), len(parts)])
            if any(k <= len(parts) and rx.match("/".join(parts[:k])) for k in depths):
                return True
        return False

    def under(self, path: str) -> bool:
        """Whether *path* is at or above one of the globs' literal folders."""
        return any(_related(path, lit) and len(path) <= len(lit) for lit in self.literals)

    def held(self) -> bool:
        return bool(self.files)

    @property
    def files(self) -> list[str]:
        """The part's files that exist, as real paths."""
        if self._files is None:
            found: set[str] = set()
            for g in self.globs:
                parts = g.split("/")
                n = next((i for i, p in enumerate(parts) if _has_glob(p)), len(parts))
                start = os.path.join(self.root, *parts[:n])
                for folder, dirs, names in _walk(start, self.strict):
                    dirs[:] = [d for d in dirs if d != ".git"]
                    found |= {f for f in (os.path.join(folder, n) for n in names)
                              if self.inside(f)}
                    if len(found) > _MOST_FILES:
                        raise PolicyError(_LONG_PART)
            self._files = sorted(found)
        return self._files

    def below(self, folder: str | None) -> list[str]:
        if not folder or (self.strict and not _related(folder, self.root)):
            return []
        return [f for f in self.files if folder == "/" or f.startswith(folder + "/")]


def _related(a: str, b: str) -> bool:
    """Whether one of two real paths is at or under the other."""
    return a == "/" or a == b or a.startswith(b + "/") or b.startswith(a.rstrip("/") + "/")


def _walk_fault(err: OSError) -> None:
    if not isinstance(err, (FileNotFoundError, NotADirectoryError)):
        raise PolicyError(_WALK_FAULT)


def _walk(start: str, strict: bool):
    """The folders below *start* (or *start* alone, a file).  Strict, a
    folder that cannot be walked or stat'ed but for its absence refuses
    (W2-84); else as ``os.walk``, which passes over it."""
    try:
        kind = ("dir" if stat.S_ISDIR(os.stat(start).st_mode) else "file") if strict else (
            "dir" if os.path.isdir(start) else os.path.lexists(start) and "file")
    except (FileNotFoundError, NotADirectoryError):
        kind = os.path.islink(start) and "file"
    except OSError:
        raise PolicyError(_WALK_FAULT) from None
    if kind == "dir":
        return os.walk(start, onerror=_walk_fault if strict else None)
    return [(os.path.dirname(start), [], [os.path.basename(start)])] if kind else []


# -- the session's ticket --------------------------------------------------------

def _read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        raise PolicyError(_TICKET_FAULT) from None


def _front(text: str) -> tuple[str | None, str | None]:
    """A ticket file's WBS id and id; one that cannot be read for them
    refuses (fail closed)."""
    head = text.split("\n---", 1)[0][4:] if text.startswith("---\n") else None
    try:
        import yaml  # the C parser when there is one: the guard runs on every call
        ticket = (yaml.load(head, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
                  if head is not None else None)
    except Exception:
        ticket = None
    if not isinstance(ticket, dict):
        # Not YAML: the line reader the write rules use (a fixture's
        # allowed_paths may start with a *).  No front matter at all, refused.
        ticket = _parse_frontmatter(text)
        if ticket is None:
            raise PolicyError(_TICKET_FAULT)
    wbs, tid = ticket.get("wbs_id") or None, ticket.get("id") or None
    if wbs is not None and not (isinstance(wbs, str) and _WBS_RE.fullmatch(wbs)):
        raise PolicyError(_TICKET_FAULT)
    return wbs, tid if isinstance(tid, str) else None


def _ticket(root: str, ticket_id: str | None) -> tuple[set[str], str | None]:
    """The names the session's ticket goes by (the id it was given, its
    file's name, its id, its WBS id) and its WBS id.  A ticket is named by
    its file or, as the launcher and the write rules take it, by its WBS id
    (item 3); with no such ticket, the id alone and no WBS id."""
    if not ticket_id or "/" in ticket_id:
        return set(), None
    folder = os.path.join(root, ".tickets")
    path = os.path.join(folder, f"{ticket_id}.md")
    if os.path.lexists(path):
        wbs, tid = _front(_read_text(path))
        return {ticket_id, tid, wbs} - {None}, wbs
    try:
        names = sorted(os.listdir(folder))
    except FileNotFoundError:
        return {ticket_id}, None
    except OSError:
        raise PolicyError(_TICKET_FAULT) from None
    # A file that gives the WBS id a line of its own is read in full.
    line = re.compile(r"^wbs_id:[ \t]*['\"]?" + re.escape(ticket_id) + r"['\"]?[ \t]*$",
                      re.M)
    for name in names:
        if not name.endswith(".md"):
            continue
        text = _read_text(os.path.join(folder, name))
        if not line.search(text):
            continue
        wbs, tid = _front(text)
        if wbs == ticket_id:
            return {ticket_id, name[:-3], tid} - {None}, wbs
    return {ticket_id}, None


# -- the evaluation sets (DEC-845) ---------------------------------------------

def _paths_ok(value, need: bool) -> bool:
    return isinstance(value, list) and (bool(value) or not need) and all(
        isinstance(p, str) and p and not p.startswith("/") and "\0" not in p
        and ".." not in p.split("/") for p in value)


def _measures_ok(m) -> bool:
    return isinstance(m, dict) and all(
        isinstance(m.get(k, []), list) and all(isinstance(x, str) for x in m.get(k, []))
        for k in ("roles", "tickets")) and bool(m.get("roles") or m.get("tickets"))


def set_fault(entry) -> str | None:
    """Why one evaluation set is not of the stated shape, or ``None``."""
    if not isinstance(entry, dict):
        return "a set is not a map"
    if not _paths_ok(entry.get("visible", []), False):
        return "a set's visible part is not a list of project-relative paths"
    if not _paths_ok(entry.get("hidden"), True):
        return "a set's hidden part is not a non-empty list of project-relative paths"
    if not _measures_ok(entry.get("measures")):
        return "a set's measures name no role and no ticket"
    return None


def evaluation_sets(root: str) -> dict:
    """The path map's ``evaluation_sets`` block; ``{}`` when there is none.
    A path map that cannot be read, or a block that is not a map of sets,
    raises ``PolicyError`` (fail closed, as DEC-218 for the held-out list)."""
    path = os.path.join(root, PATH_MAP_REL)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError):
        raise PolicyError(f"{PATH_MAP_REL} cannot be read") from None
    if SETS_KEY not in text:
        return {}
    # The block alone is parsed when it is written once, as a key at the
    # start of a line, so that every call does not parse the whole map.
    lines = text.splitlines(keepends=True)
    at = [i for i, line in enumerate(lines) if line.startswith(SETS_KEY + ":")]
    if len(at) == 1:
        end = next((j for j in range(at[0] + 1, len(lines))
                    if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
        text = "".join(lines[at[0]:end])
    try:
        data = load_yaml_unique(text)
    except Exception:
        raise PolicyError(f"{PATH_MAP_REL} cannot be read") from None
    block = data.get(SETS_KEY, {}) if isinstance(data, dict) else None
    if not isinstance(block, dict):
        raise PolicyError(f"{PATH_MAP_REL}: {SETS_KEY} is not a map of sets")
    return block
