"""G-14 (DEC-1052, DAEO-sdxk): role separation from the path map, deterministically.

The path map's ``role_paths:`` section names, per role, the globs it may not read (``reads_denied``): the engineer
never reads the acceptance tests; the independent test designer never reads the engineer's new code (it reads the
integrated code, DEC-963). A call is refused when a path it reads, as the call names it, is at or under a denied glob:
simple path checks, no guessing at shell commands. Let through, as rules 1 and 5 since ACT-GUARD-FIX-4: a target the
guard cannot resolve (a variable it cannot expand, a folder it cannot place), a search from a folder above, a listing
of names only (ls, find without -exec, git log without a patch, --stat), names a command gets at run time
(xargs, $(...) words) and a command the scan cannot read. No ``role_paths:`` section is no check (today's behaviour).

W2-141 (DEC-1093 (2), DEC-1102): but for the engineer's own acceptance folder ({ticket_tests}'s tests/acceptance/<WBS>/,
in any tree), a search from a folder that holds it is refused unless the call keeps the folder out, and the refusal
says how: a Grep or Glob call (pretooluse.py routes Glob here too), and in Bash a recursive grep, rg, ag, ack, a find
whose action reads, or a listing (find, rg --files, ag -g, ack -f) whose names go to a reader (| xargs <reader>, a
while-read loop that reads, a reader's $(...) word). A file is taken in or kept out as the tool would (the block
between the W2-141 markers, the same as gov.guard.reads's); an empty folder, or one no file of which the call takes
in, is not reached; a start the guard cannot resolve keeps today's behaviour. Other tickets' tests and other roles are
unaffected.

The section is read from the main tree's path map (governance/project/path-map.yaml): a branch cannot weaken it.

A glob is in the path map's language (``*`` within a folder, ``**`` across folders), with these placeholders
({ticket_impl_code}: {ticket_impl} without docs/, an option not in the patch):
  {ticket_tests}       the session ticket's acceptance tests, in every tree (the owner, 2026-11-03): its own folder
                       tests/acceptance/<WBS>/**, and each file in another ticket's tests/acceptance/<X>/ that a
                       test designer's commit made for it touched (linked_tests: the commit's Task: trailer names the
                       ticket, or the commit is on the first-parent line of w2/<WBS>-tests since it left
                       w2/integrate); for a coordination ticket (class: coordination, W2-00) its own folder only
                       (ACT-G14b);
                       other tickets' tests stay readable;
  {ticket_impl}        the engineer's new work (the owner's (c3), 2026-11-03): each of the ticket's allowed_paths but
                       tests/acceptance/ (its code, docs and new unit tests), less the shared test files (any conftest.py,
                       __init__.py, *support*.py, *helper*.py), in the engineer's tree (~/gov-os-worktrees/<WBS>) and
                       as read from its branch (git show w2/<WBS>:<path>); in a designer's session that runs in the
                       engineer's own tree, only the files that branch changes against w2/integrate; in the
                       designer's tests tree (~/gov-os-worktrees/<WBS>-tests, forked from the ticket's head), the
                       files the engineer's commits carried into it (review F1). Every other tree (the main tree,
                       the W2-00-store trees) holds integrated code: readable.
A plain glob applies in every tree: this tree, its worktrees and run clones, and each folder under ~/gov-os-worktrees/.
Nothing is opened but the path map and the session's ticket file (and git's name list of a branch's changes, for
a designer in the engineer's own tree); no file is read for its contents.
"""
from __future__ import annotations

import os
import re

PATH_MAP_REL = "governance/project/path-map.yaml"
KEY = "role_paths"
ACCEPTANCE = "tests/acceptance"
WORKTREES = os.path.realpath(os.path.expanduser("~/gov-os-worktrees"))
MOST_GLOB = 2000  # the paths one word's glob may name that are judged; beyond, the word as written

# The readers: commands that print or copy a file's contents (cp: its sources); wc, ls, stat, md5sum print none.
PLAIN = frozenset("cat tac nl less more bat batcat head tail cmp diff colordiff od xxd hexdump strings base64 "
                  "uniq sort cut fold fmt paste column expand unexpand rev iconv".split())
PATTERN_FIRST = frozenset("grep egrep fgrep zgrep rg ag ack".split())
SCRIPT_FIRST = frozenset("sed awk gawk mawk nawk jq yq".split())
COPIES = frozenset(("cp",))
READERS = PLAIN | PATTERN_FIRST | SCRIPT_FIRST | COPIES
SHELLS = frozenset("sh bash dash zsh ksh".split())
# Options that take the next word as their value (the value is no path), per reader.
VALUED = {
    "head": "-n -c --lines --bytes", "tail": "-n -c --lines --bytes -s --sleep-interval --pid",
    "cut": "-d -f -c -b --delimiter --fields --characters --bytes --output-delimiter",
    "sort": "-k -t -o -S -T --key --field-separator --output --buffer-size --temporary-directory --parallel",
    "uniq": "-f -s -w --skip-fields --skip-chars --check-chars", "od": "-A -j -N -t -w",
    "xxd": "-s -l -c -g -o", "diff": "-U -C -L --label -x -X -I --unified --context", "nl": "-b -w -s -v -i -n -d",
    "bat": "-l -r -H --line-range --language --highlight-line --style --theme --tabs",
    "base64": "-w --wrap", "fold": "-w --width", "column": "-s -c -t -o",
    "grep": "-e -f -A -B -C -m -d -D --regexp --file --after-context --before-context --context --max-count",
    "rg": "-e -f -g -t -T -A -B -C -m -M -j -r -E --regexp --file --glob --iglob --type --type-not --max-depth "
          "--max-count --replace --encoding --after-context --before-context --context --threads",
    "sed": "-e -f -l --expression --file --line-length", "awk": "-f -F -v --file --field-separator --assign",
    "jq": "-f --from-file --indent -L", "cp": "-t -S --target-directory --suffix",
}
for _same, _as in (("egrep", "grep"), ("fgrep", "grep"), ("zgrep", "grep"), ("ag", "rg"), ("ack", "rg"),
                   ("batcat", "bat"), ("gawk", "awk"), ("mawk", "awk"), ("nawk", "awk"), ("yq", "jq")):
    VALUED[_same] = VALUED[_as]
VALUED = {k: frozenset(v.split()) for k, v in VALUED.items()}
SCRIPT_GIVEN = {"grep": ("-e", "-f", "--regexp", "--file"), "rg": ("-e", "-f", "--regexp", "--file"),
                "sed": ("-e", "-f", "--expression", "--file"), "awk": ("-f", "--file"), "jq": ("-f", "--from-file")}
FILE_VALUES = {"grep": ("-f", "--file"), "rg": ("-f", "--file"), "sed": ("-f", "--file"), "awk": ("-f", "--file"),
               "jq": ("-f", "--from-file"), "diff": ("-X",)}
JQ_TWO = frozenset("--arg --argjson --slurpfile --rawfile --args --jsonargs".split())  # name and value
GIT_SHOWS = frozenset("show diff blame annotate cat-file grep log whatchanged".split())
GIT_QUIET = frozenset("--stat --name-only --name-status --shortstat --numstat --summary --dirstat -s --no-patch "
                      "--raw --check --quiet --exit-code".split())
GIT_PATCH = frozenset("-p -u --patch -L --cc -c".split())
GIT_VALUED = frozenset("-n -S -G -O -L -U --author --committer --grep --since --until --skip --max-count --format "
                       "--pretty --date --diff-filter".split())
GIT_GREP_VALUED = frozenset("-e -f -A -B -C -m -O --max-depth --threads --context --after-context "
                            "--before-context --max-count --open-files-in-pager".split())
BRANCH = re.compile(r"(?:^|/)w2/([A-Za-z0-9][A-Za-z0-9._-]*?)(?:[~^@].*)?$")


class Unreadable(Exception):
    pass


# -- the section ----------------------------------------------------------------------------------------------------

_SECTION = {}


def section(tree):
    """The ``role_paths:`` section of the path map at ``tree``, or None when it has none (no check). A section that
    is not a mapping of roles to ``reads_denied`` lists of globs raises (the hook fails closed)."""
    if tree in _SECTION:
        return _SECTION[tree]
    path = os.path.join(tree, PATH_MAP_REL)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        text = ""
    found = None
    block = _block(text)
    if block is not None:
        import yaml
        try:
            doc = yaml.load(block, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader)) or {}
        except yaml.YAMLError:
            raise ValueError(f"{PATH_MAP_REL}: {KEY} cannot be read") from None
        found = doc.get(KEY) if isinstance(doc, dict) else None
        if found is None:
            raise ValueError(f"{PATH_MAP_REL}: {KEY} is empty")
        check(found)
    _SECTION[tree] = found
    return found


def _block(text):
    """The ``role_paths:`` block's own lines (from its key to the next line that starts at the margin), parsed alone
    as reads.evaluation_sets() parses its block, so a YAML error elsewhere in the map (a merge's conflict markers)
    does not refuse every call; None with no such key. Written twice, it raises (the hook fails closed)."""
    lines = text.splitlines(keepends=True)
    at = [i for i, line in enumerate(lines) if re.match(r"role_paths\s*:", line)]
    if not at:
        return None
    if len(at) > 1:
        raise ValueError(f"{PATH_MAP_REL}: {KEY} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    return "".join(lines[at[0]:end])


def check(found):
    if not isinstance(found, dict):
        raise ValueError(f"{PATH_MAP_REL}: {KEY} is not a mapping of roles")
    for role, entry in found.items():
        globs = entry.get("reads_denied") if isinstance(entry, dict) else None
        if not isinstance(role, str) or not isinstance(globs, list) or \
                not all(isinstance(g, str) and g.strip() and not g.startswith("/") for g in globs):
            raise ValueError(f"{PATH_MAP_REL}: {KEY}.{role}: reads_denied is not a list of project-relative globs")


# -- the ticket -----------------------------------------------------------------------------------------------------

def ticket_front(root, ticket_id):
    """The session ticket's front matter (a dict) from ``root``'s .tickets/, found as gov.guard.reads._ticket finds
    it (its file, else the file whose wbs_id is the id); {} with no such ticket. A file that cannot be read raises."""
    from gov.guard import reads
    if not ticket_id or "/" in ticket_id:
        return {}
    folder = os.path.join(root, ".tickets")
    path = os.path.join(folder, f"{ticket_id}.md")
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
    head = text.split("\n---", 1)[0][4:] if text.startswith("---\n") else ""
    import yaml
    try:
        front = yaml.load(head, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    except Exception:
        front = None
    return front if isinstance(front, dict) else {}


class Denied:
    """One denied glob: its tree (None: every tree), the glob, the path map's entry it comes from; ``only``, for the
    session's own tree, a callable giving the files (relative) its branch changes: the only ones named there."""

    def __init__(self, tree, glob, entry, only=None, keep_shared=False):
        from gov.guard import reads
        self.tree, self.glob, self.entry, self.only, self.keep_shared = tree, glob, entry, only, keep_shared
        self._part = {}
        self._reads = reads

    def part(self, tree):
        if tree not in self._part:
            self._part[tree] = self._reads._Part(tree, [self.glob], "")
        return self._part[tree]

    def names(self, full):
        """Whether ``full`` (a real path) is named by this glob in its own tree."""
        if not self.part(self.tree).inside(full) or self.keep_shared and shared(full):
            return False
        if self.only is None:
            return True
        found = self.only()
        return found is not None and full[len(self.tree) + 1:] in found


class Linked:
    """{ticket_tests}'s files outside the ticket's own folder: relative paths, in every tree, worked out from git
    only when a read names another folder's acceptance tests (linked_tests)."""

    def __init__(self, main, names, wbs, entry, source=None):
        self.tree, self.glob, self.entry, self.only = None, "the ticket's cases revised in other folders", entry, None
        self.main, self.names, self.wbs, self._source = main, names, wbs, source
        self._files = False

    def files(self):
        if self._files is False:
            self._files = (self._source or linked_tests)(self.main, self.names, self.wbs)
        return self._files

    def names_rel(self, rel):
        if not rel.startswith(ACCEPTANCE + "/") or rel.startswith(f"{ACCEPTANCE}/{self.wbs}/"):
            return False
        found = self.files()
        return bool(found) and any(rel == f or rel.startswith(f + "/") for f in found)


# the session's own temporary folder (its TMPDIR, else /tmp): one cache per session's scratch
LINK_CACHE = os.path.join(__import__("tempfile").gettempdir(), f"gov-os-role-reads-{os.getuid()}")
_LINKS = {}


def linked_tests(main, names, wbs):
    """The files (relative) under another ticket's tests/acceptance/<X>/ that a test designer's commit made for the
    ticket touched, from the git history of the main tree's repository (every branch):
      (i)  a non-merge commit with Role: independent-test-designer whose Task: trailer names the ticket (its id or WBS
           id), the project's trailer rule (DEC-182);
      (ii) a non-merge test designer's commit on the first-parent line of w2/<WBS>-tests since it left w2/integrate
           (_fork: where its first-parent line meets w2/integrate's): a revision made in the ticket's tests tree under
           another Task: (W2-126's of W2-54, 0922aa76 and 816e86dd, carry W2-54's ticket).
    Worked out once per (ticket, the heads of w2/integrate, w2/<WBS> and w2/<WBS>-tests) and kept in LINK_CACHE.
    None when git cannot say: then only the ticket's own folder is judged, and a refusal says so."""
    import json
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def git(*args, ok=(0,)):
        r = subprocess.run(["git", "-C", main, *args], capture_output=True, text=True, timeout=10, env=env)
        if r.returncode not in ok:
            raise OSError("git")
        return r.stdout
    try:
        refs = ["w2/integrate", f"w2/{wbs}", f"w2/{wbs}-tests"]
        heads = [git("rev-parse", "--verify", "--quiet", r + "^{commit}", ok=(0, 1)).strip() or "-" for r in refs]
        # the key: the method (this module's own hash: a changed rule never reads an older list), the repository,
        # the ticket's names and the three heads (a new commit on any of them is a new list)
        key = "|".join([_method(), os.path.realpath(main), *sorted(n for n in names if n), *heads])
        if key in _LINKS:
            return _LINKS[key]
        import hashlib
        cached = os.path.join(LINK_CACHE, hashlib.sha256(key.encode()).hexdigest()[:24] + ".json")
        try:
            with open(cached, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("key") == key and isinstance(data.get("files"), list):
                _LINKS[key] = set(data["files"])
                return _LINKS[key]
        except (OSError, ValueError):
            pass
        fmt = "--format=@@%H%x1f%(trailers:key=Task,valueonly,separator=%x2C)%x1f%(trailers:key=Role,valueonly,separator=%x2C)"
        grep = [a for n in sorted(names) if n for a in ("--grep", n)]
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
    _LINKS[key] = found
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
    """Where ``branch`` left w2/integrate: the first commit on its first-parent line that is on w2/integrate's own
    first-parent line (the project merges with --no-ff, so a branch's own commits are never on that line). Read from
    the commit graph, not the reflog: ACT-D8 expired every reflog (2026-11-03). None when the lines never meet."""
    line = set(git("rev-list", "--first-parent", "w2/integrate").split())
    return next((c for c in git("rev-list", "--first-parent", branch).split() if c in line), None)


_METHOD = []


def _method():
    """This module's own sha256 (12 digits), read once per call of the hook: the link cache's method key."""
    if not _METHOD:
        import hashlib
        with open(os.path.abspath(__file__), "rb") as f:
            _METHOD.append(hashlib.sha256(f.read()).hexdigest()[:12])
    return _METHOD[0]


def _files_of(out, names, wbs, need_task):
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


_CHANGED = {}


def changed(tree):
    """The files (relative) the branch at ``tree`` changes against its merge base with w2/integrate, committed or
    not: the engineer's new code when a test designer works in the engineer's own tree. None when git cannot say:
    then nothing there is refused (what the guard cannot work out is let through)."""
    if tree in _CHANGED:
        return _CHANGED[tree]
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def git(*args):
        p = subprocess.run(["git", "-C", tree, *args], capture_output=True, text=True, timeout=5, env=env)
        if p.returncode:
            raise OSError("git")
        return p.stdout
    try:
        base = git("merge-base", "w2/integrate", "HEAD").strip()
        names = git("diff", "--name-only", "--no-renames", "-z", base).split("\0")  # the work tree against the base
        names += git("ls-files", "--others", "--exclude-standard", "-z").split("\0")  # new files not yet added
        found = {n for n in names if n}
    except (OSError, subprocess.SubprocessError):
        found = None
    _CHANGED[tree] = found
    return found


# (c3), the owner's decision (2026-11-03): the shared test files the designer needs for fixtures stay readable.
SHARED = ("conftest.py", "__init__.py", "*support*.py", "*helper*.py")


def shared(full):
    """A shared test file: any conftest.py, a package's __init__.py, a support or helper module."""
    import fnmatch
    name = os.path.basename(full)
    return any(fnmatch.fnmatchcase(name, g) for g in SHARED)


_ENGINEER_SIDE = {}


def engineer_side(tree, wbs):
    """The files (relative) the commits of the ticket's branch carried into the designer's tests tree ``tree``
    (~/gov-os-worktrees/<WBS>-tests, forked from the ticket branch's head): the names of the commits reachable from
    its fork point with w2/<WBS> but not from its merge base with w2/integrate. The designer's own commits after the
    fork are not among them. With no w2/<WBS> ref, every commit since the merge base. None when git cannot say (then
    nothing there is refused: what the guard cannot work out is let through)."""
    if tree in _ENGINEER_SIDE:
        return _ENGINEER_SIDE[tree]
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def git(*args, ok=(0,)):
        p = subprocess.run(["git", "-C", tree, *args], capture_output=True, text=True, timeout=5, env=env)
        if p.returncode not in ok:
            raise OSError("git")
        return p
    try:
        base = git("merge-base", "w2/integrate", "HEAD").stdout.strip()
        fork = "HEAD"
        if git("rev-parse", "--verify", "--quiet", f"refs/heads/w2/{wbs}", ok=(0, 1)).returncode == 0:
            fork = git("merge-base", f"w2/{wbs}", "HEAD").stdout.strip()
        names = git("log", "--format=", "--name-only", "--no-renames", "-z", f"{base}..{fork}").stdout
        found = {n.strip("\n") for n in names.split("\0") if n.strip("\n")}
    except (OSError, subprocess.SubprocessError):
        found = None
    _ENGINEER_SIDE[tree] = found
    return found


def expand(entries, wbs, allowed, root=None, changes=changed, mode="c3", docs=True, tests_changes=engineer_side,
           main=None, names=(), links=None):
    """The path map's entries for a role as Denied globs, the placeholders filled from the ticket (WBS id, its
    allowed_paths). A placeholder the ticket cannot fill names nothing.
    {ticket_impl} (``mode`` c3, the owner's decision): the ticket's allowed paths but tests/acceptance/, in the
    engineer's tree: its code, its documents and its new unit tests, less the shared test files (SHARED);
    {ticket_impl_code} the same without docs/ (not the default: a proposal to the CTO). The replay's
    comparisons: c1, the paths outside tests/ only; c2, every path under tests/ too, shared files included.
    In the session's own tree (``root``) the ticket's paths name only the files its branch changes
    (``changes(root)``): the rest there is the integrated code (DEC-963). In the designer's tests tree
    (<WBS>-tests) they name also the files the engineer's commits carried in (``tests_changes(root, wbs)``)."""
    out = []
    own = os.path.join(WORKTREES, wbs) if wbs else None
    real = os.path.realpath(root) if root else None
    only = (lambda: changes(own)) if own and real == os.path.realpath(own) else None
    # The designer's tests tree is forked from the ticket branch's head (the lead brief), so it can hold the
    # engineer's commits (review F1): there the ticket's paths name the files those commits carried in.
    tests_tree = real if own and real == os.path.realpath(own) + "-tests" else None
    for entry in entries:
        if "{ticket_tests}" in entry:
            if wbs:
                out.append(Denied(None, entry.replace("{ticket_tests}", f"{ACCEPTANCE}/{wbs}/**"), entry))
                if links is not False and (main or root):
                    out.append(Linked(main or root, set(names) | {wbs}, wbs, entry,
                                      links if callable(links) else None))
        elif "{ticket_impl}" in entry or "{ticket_impl_code}" in entry:
            no_docs = "{ticket_impl_code}" in entry or not docs
            for p in allowed if own else ():
                p = p.strip().lstrip("./") if isinstance(p, str) else ""
                if not p or p.startswith(ACCEPTANCE + "/") or p == ACCEPTANCE or (p.startswith("docs/") and no_docs):
                    continue
                if mode == "c1" and (p.startswith("tests/") or p == "tests"):
                    continue
                out.append(Denied(own, p, entry, only, keep_shared=(mode == "c3")))
                if tests_tree:
                    out.append(Denied(tests_tree, p, entry, lambda t=tests_tree: tests_changes(t, wbs),
                                      keep_shared=(mode == "c3")))
        else:
            out.append(Denied(None, entry, entry))
    return out


# -- judging a path -------------------------------------------------------------------------------------------------

class Judge:
    def __init__(self, role, denied, trees):
        self.role, self.denied, self._trees, self._all = role, denied, trees, None

    def trees(self):
        """Every tree a plain glob applies in: the hook's trees (this tree, its worktrees, run clones) and each folder
        under ~/gov-os-worktrees/ (a removed one too: a path's first folder there)."""
        if self._all is None:
            found = list(self._trees() if callable(self._trees) else self._trees)
            try:
                found += [os.path.join(WORKTREES, n) for n in sorted(os.listdir(WORKTREES))]
            except OSError:
                pass
            self._all = list(dict.fromkeys(os.path.realpath(t) for t in found))
        return self._all

    def hit(self, full, plain=False):
        """The Denied glob ``full`` (an absolute path) is at or under, or None; ``plain``: only the globs of every
        tree."""
        full = os.path.realpath(full)
        for d in self.denied:
            if d.tree is not None and plain:
                continue
            if isinstance(d, Linked):
                trees = [t for t in self.trees() if full.startswith(t + "/")]
                if full.startswith(WORKTREES + "/"):
                    trees.append(os.path.join(WORKTREES, full[len(WORKTREES) + 1:].split("/")[0]))
                if any(d.names_rel(full[len(t) + 1:]) for t in trees):
                    return d
                continue
            if d.tree is not None:
                if d.names(full):
                    return d
                continue
            else:
                trees = [t for t in self.trees() if full.startswith(t + "/")]
                if full.startswith(WORKTREES + "/"):
                    trees.append(os.path.join(WORKTREES, full[len(WORKTREES) + 1:].split("/")[0]))
            if any(d.part(t).inside(full) for t in trees):
                return d
        return None

    def reason(self, d):
        shown = d.entry if d.entry == d.glob else f"{d.entry} ({d.glob})"
        why = (f"the {self.role} does not read {shown}: role_paths.{self.role}.reads_denied "
               f"({PATH_MAP_REL}, DEC-1052 G-14)")
        link = next((x for x in self.denied if isinstance(x, Linked) and x.entry == d.entry), None)
        if link is not None and link.files() is None:  # on a refusal only: the link source read once
            why += ("; its cases revised in other folders could not be worked out from git, so only its own "
                    "folder is judged")
        return why


def judge_paths(judges, paths):
    """The first refusal for any of ``paths`` (absolute, or (absolute, plain only)) by any of ``judges``, or None."""
    for item in paths:
        full, plain = item if isinstance(item, tuple) else (item, False)
        for j in judges:
            d = j.hit(full, plain)
            if d:
                return j.reason(d), full, d
    return None


# -- what a call reads ----------------------------------------------------------------------------------------------

def _abs(word, cwd):
    """A word as an absolute path, or None when it does not resolve (a variable, a substitution, an unknown folder)."""
    if not word or word.startswith("-") and word != "-":
        return None
    if os.path.isabs(word):
        return os.path.normpath(word)
    return None if cwd is None else os.path.normpath(os.path.join(cwd, word))


def _globbed(full):
    """A path with glob characters: the paths it names that exist (bounded), else itself."""
    if not any(c in full for c in "*?["):
        return [full]
    import glob as _glob
    found = []
    for p in _glob.iglob(full, recursive=True):
        found.append(p)
        if len(found) >= MOST_GLOB:
            break
    return found or [full]


def _lead(pattern):
    """A glob pattern's literal folders before its first glob character ('' when there are none)."""
    parts = pattern.split("/")
    lead = []
    for p in parts[:-1]:
        if any(c in p for c in "*?[{"):
            break
        lead.append(p)
    return "/".join(lead)


def tool_reads(tool, tin, cwd):
    """The paths a read tool reads, absolute; Glob lists names only and reads none."""
    if tool == "Read":
        p = tin.get("file_path")
        return [_abs(os.path.expanduser(p), cwd)] if isinstance(p, str) and p else []
    if tool == "NotebookRead":
        p = tin.get("notebook_path")
        return [_abs(os.path.expanduser(p), cwd)] if isinstance(p, str) and p else []
    if tool == "Grep":
        p = tin.get("path")
        start = _abs(os.path.expanduser(p), cwd) if isinstance(p, str) and p else cwd
        if start is None:
            return []
        out = [start]
        g = tin.get("glob")
        if isinstance(g, str) and _lead(g):
            out.append(os.path.normpath(os.path.join(start, _lead(g))))
        return out
    return []


def glob_lists(tin, cwd):
    """What a Glob call lists (for the replay's count only): its folder and the pattern's literal lead."""
    p = tin.get("path")
    start = _abs(os.path.expanduser(p), cwd) if isinstance(p, str) and p else cwd
    pat = tin.get("pattern") if isinstance(tin.get("pattern"), str) else ""
    if start is None:
        return []
    return [os.path.normpath(os.path.join(start, _lead(pat)))] if _lead(pat) else [start]


class Bash:
    """The paths a Bash command reads, as its words name them: (absolute path, how) pairs. Each simple command is
    judged with the folder ``cd`` leaves it in and the variables the command sets itself at its top level."""

    def __init__(self, expand_token):
        self.expand_token = expand_token
        self.found = []  # (path, how, plain only: judged by the globs of every tree alone)
        # W2-141: (start, start as written, keep, how, cwd) of each search from a folder; a listing's waits in
        # _listed until a reader takes its names (| xargs <reader>, a while-read loop that reads).
        self.searches = []
        self._listed = []

    def word(self, w, env):
        """A word with $NAME/${NAME} the command set itself filled in, then the product's expansion; None when it
        does not resolve."""
        if "`" in w or "__gov_sub_" in w or "__gov_hdl_" in w:
            return None

        def fill(m):
            name = m.group(1) or m.group(2)
            return env[name] if name in env else m.group(0)
        w = re.sub(r"\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)", fill, w)
        return self.expand_token(w)

    def run(self, command, cwd, depth=0, into=False):
        """``into``: the command is a reader's $(...) word, so a listing in it gives names a reader opens."""
        import bash_writes as bw
        if depth > bw.MOST_DEPTH:
            return
        try:
            text, bodies = bw.heredocs(command)
            lifted, subs = bw.lift(text)
            cmds = bw.simples(bw.tokens(lifted))
        except bw.Unreadable:
            return
        env, stack, ecwd = {}, [], cwd
        outer, self._listed, piped = self._listed, [], False
        for k, (words, reds, sep) in enumerate(cmds):
            for marker in re.findall(r"__gov_sub_(\d+)__", " ".join(words + [r[1] for r in reds])):
                if int(marker) < len(subs):
                    self.run(subs[int(marker)], ecwd, depth + 1, into=_reads_names(words))
            if words and all(bw._ASSIGN.match(w) for w in words):
                for w in words:
                    name, value = bw._ASSIGN.match(w).groups()
                    exp = self.word(value, env)
                    if exp is None:
                        env.pop(name, None)
                    else:
                        env[name] = exp
            else:
                fed = piped or any(op == "<" for op, _t in reds)
                ecwd = self.simple(words, reds, ecwd, env, bodies, subs, depth, fed=fed, into=into)
            # W2-141: a listing's names that a reader takes are a search from where it starts.
            if (piped and _xargs_reads(words)) or (sep not in ("|", "|&") and _loop_reads(cmds, k)):
                self.searches += self._listed
            if sep not in ("|", "|&"):
                self._listed = []
            piped = sep in ("|", "|&")
            if "(" in sep:
                stack.append(ecwd)
            if ")" in sep and stack:
                ecwd = stack.pop()
        self._listed = outer

    def path(self, raw, ecwd, env, how):
        exp = self.word(raw, env)
        full = _abs(exp, ecwd) if exp is not None else None
        if full is not None:
            self.found += [(p, how, False) for p in _globbed(full)]

    def search(self, name, args, ecwd, env, fed, into):
        """W2-141: a recursive search's starts, each with what it keeps out (x_search); a listing's wait in
        _listed for a reader, unless it is a reader's $(...) word (``into``). An rg, ag or ack fed by a pipe or a
        redirect with no folder named searches what feeds it."""
        spec = x_search(name, args)
        if spec is None:
            return
        operands, keep, how, names = spec
        if not operands and fed and how in ("rg", "ag", "ack"):
            return
        found = []
        for w in operands or ["."]:
            exp = self.word(w, env)
            full = _abs(exp, ecwd) if exp is not None else None
            found += [(p, exp, keep, how, ecwd) for p in (_globbed(full) if full is not None else [None])]
        if names and not into:
            self._listed += found
        else:
            self.searches += found

    def simple(self, words, reds, ecwd, env, bodies, subs, depth, fed=False, into=False):
        """Judge one simple command; returns the folder after it (a cd moves it; None when unknown)."""
        import bash_writes as bw
        for op, target in reds:
            if op == "<":
                m = re.fullmatch(r"__gov_hdl_(\d+)__", target)
                if m:
                    continue
                self.path(target, ecwd, env, "<")
        words = bw.lead(words)
        if not words:
            return ecwd
        name, args = os.path.basename(words[0]), words[1:]
        self.search(name, args, ecwd, env, fed, into)
        if name in ("cd", "pushd"):
            if not args:
                return os.path.expanduser("~")
            exp = self.word(args[0], env) if not args[0].startswith("-") else None
            if exp is None or any(c in exp for c in "*?[]{}") or ecwd is None and not os.path.isabs(exp):
                return None
            return os.path.normpath(os.path.join(ecwd or "/", exp))
        if name in SHELLS:
            if "-c" in args or any(bw._short(a, "c") for a in args if a.startswith("-")):
                i = next(i for i, a in enumerate(args) if a == "-c" or bw._short(a, "c"))
                if i + 1 < len(args):
                    # a substitution lifted out of the string at this level goes back in (a quoted $(...))
                    self.run(re.sub(r"`__gov_sub_(\d+)__`", lambda m: "$(" + subs[int(m.group(1))] + ")"
                                    if int(m.group(1)) < len(subs) else m.group(0), args[i + 1]), ecwd, depth + 1)
            elif not [a for a in args if not a.startswith("-")]:
                for op, target in reds:
                    m = re.fullmatch(r"__gov_hdl_(\d+)__", target)
                    if m and op == "<":
                        self.run(bodies[int(m.group(1))]["text"], ecwd, depth + 1)
            return ecwd
        if name == "git":
            self.git(args, ecwd, env)
            return ecwd
        if name == "find":
            execs = [i for i, a in enumerate(args) if a in ("-exec", "-execdir", "-ok", "-okdir")]
            if any(i + 1 < len(args) and os.path.basename(args[i + 1]) in READERS for i in execs):
                for a in args:
                    if a.startswith("-") or a in ("(", "!", ")"):
                        break
                    self.path(a, ecwd, env, "find -exec")
            return ecwd
        if name in READERS:
            for raw in self.reader_args(name, args):
                self.path(raw, ecwd, env, name)
        return ecwd

    @staticmethod
    def reader_args(name, args):
        """A reader's path words: its operands, less a grep's pattern or a sed/awk/jq script given as the first
        operand, and a copy's destination; plus a pattern or script file given by -f."""
        valued = VALUED.get(name, frozenset())
        files, operands, given = [], [], False
        i, ended = 0, False
        while i < len(args):
            a = args[i]
            if ended or not a.startswith("-") or a == "-":
                operands.append(a)
            elif a == "--":
                ended = True
            elif name in ("jq", "yq") and a in JQ_TWO:
                if a in ("--slurpfile", "--rawfile") and i + 2 < len(args):
                    files.append(args[i + 2])
                if a in ("--args", "--jsonargs"):
                    break  # the rest are values
                i += 2
            else:
                if a.startswith("--") and "=" in a:
                    key, value = a.split("=", 1)
                elif a in valued:
                    key, value = a, (args[i + 1] if i + 1 < len(args) else None)
                    i += 1
                else:
                    key, value = a, None  # a flag (or a cluster of them)
                if key in SCRIPT_GIVEN.get(_base(name), ()):
                    given = True
                if key in FILE_VALUES.get(_base(name), ()) and value:
                    files.append(value)
            i += 1
        if name in PATTERN_FIRST or name in SCRIPT_FIRST:
            if not given and operands:
                operands = operands[1:]
        if name in COPIES:
            if not any(a in ("-t", "--target-directory") or a.startswith("--target-directory=") for a in args):
                operands = operands[:-1]
        return [o for o in operands if o != "-"] + files

    def git(self, args, ecwd, env):
        """git show/diff/blame/cat-file/grep/log -p: ``rev:path`` words, the words after ``--``, and words that are
        existing paths; each judged in the cwd's tree and, when a revision names the branch w2/<X>, in
        ~/gov-os-worktrees/<X> too. Names only (--stat, --name-only, log without a patch) read nothing."""
        i = 0
        while i < len(args) and args[i].startswith("-"):
            a = args[i]
            if a == "-C" and i + 1 < len(args):
                exp = self.word(args[i + 1], env)
                ecwd = None if exp is None or ecwd is None and not os.path.isabs(exp) else \
                    os.path.normpath(os.path.join(ecwd or "/", exp))
                i += 2
                continue
            i += 2 if a in ("-c", "--git-dir", "--work-tree", "--namespace") else 1
        if i >= len(args) or args[i] not in GIT_SHOWS:
            return
        sub, rest = args[i], args[i + 1:]
        opts = [a for a in rest if a.startswith("-")]
        if any(o in GIT_QUIET or o.split("=")[0] in GIT_QUIET for o in opts):
            if not any(":" in a and not a.startswith("-") for a in rest):
                return
        if sub in ("log", "whatchanged") and not any(o in GIT_PATCH or o.startswith("-L") for o in opts):
            return
        top = _toplevel(ecwd)
        before, after = rest, []
        if "--" in rest:
            k = rest.index("--")
            before, after = rest[:k], rest[k + 1:]
        words, skip = [], False
        for a in before:
            if skip:
                skip = False
                continue
            if a.startswith("-"):
                skip = a in (GIT_GREP_VALUED if sub == "grep" else GIT_VALUED)
                continue
            words.append(a)
        if sub == "grep" and not any(o in ("-e", "-f") for o in opts) and words:
            words = words[1:]  # the pattern
        # A revision that is HEAD-like (or none: the work tree, the index) reads this tree's own state; another (a
        # hash, w2/integrate, a tag) its version there, judged only by the globs of every tree (the acceptance tests
        # are tests at any revision; the integrated code is not the engineer's new code); w2/<X> also in
        # ~/gov-os-worktrees/<X>, the branch's own tree.
        branches, paths, revs = [], [], []
        for w in words:
            exp = self.word(w, env)
            if exp is None:
                continue
            if ":" in exp and not os.path.lexists(_abs(exp, ecwd) or ""):
                rev, rel = exp.split(":", 1)
                if rev.isdigit() and rel and ":" in rel:  # :0:path, the index
                    rev, rel = "", rel.split(":", 1)[1]
                if not rel:
                    continue
                if rel.startswith(("./", "../")):
                    full = _abs(rel, ecwd)
                    rel = os.path.relpath(full, top) if full and top else None
                if rel is None:
                    continue
                if top:
                    self.found.append((os.path.normpath(os.path.join(top, rel)), f"git {sub} rev:path",
                                       not _own_rev(rev)))
                for t in _branches(rev):
                    self.found.append((os.path.normpath(os.path.join(t, rel)), f"git {sub} rev:path", False))
            elif sub == "diff" and "--no-index" in opts or os.path.lexists(_abs(exp, ecwd) or ""):
                paths.append(exp)
            else:
                revs.append(exp)
                branches += _branches(exp)
        for w in after:
            exp = self.word(w, env)
            if exp is not None and not exp.startswith(":"):
                paths.append(exp)
        foreign = bool(revs) and not any(_own_rev(r) for r in revs) and "--no-index" not in opts
        for p in paths:
            full = _abs(p, ecwd)
            if full is None:
                continue
            self.found += [(q, f"git {sub}", foreign) for q in _globbed(full)]
            rel = os.path.relpath(full, top) if top and full.startswith(top + "/") else None
            for t in branches if rel else ():
                self.found.append((os.path.normpath(os.path.join(t, rel)), f"git {sub} --", False))


def _own_rev(rev):
    """A revision that reads the tree's own state: none (the index), HEAD or @ and their ancestors' forms."""
    return any(side in ("", "@") or re.match(r"(HEAD|@)([~^@].*)?$", side) for side in re.split(r"\.\.\.?", rev))


def _base(name):
    return {"egrep": "grep", "fgrep": "grep", "zgrep": "grep", "ag": "rg", "ack": "rg", "gawk": "awk",
            "mawk": "awk", "nawk": "awk", "yq": "jq"}.get(name, name)


def _branches(rev):
    """The engineer's trees the revision names: w2/<X> (in a range too) as ~/gov-os-worktrees/<X>."""
    out = []
    for side in re.split(r"\.\.\.?", rev or ""):
        m = BRANCH.search(side)
        if m:
            out.append(os.path.join(WORKTREES, m.group(1)))
    return out


def _toplevel(cwd):
    """The tree that holds ``cwd``: the nearest folder at or above it with a .git; None when unknown."""
    at = cwd
    while at and at != "/":
        if os.path.lexists(os.path.join(at, ".git")):
            return os.path.realpath(at)
        at = os.path.dirname(at)
    return None


def reads_of(tool, tin, cwd, expand_token):
    """(path, how, plain only) of each path a call reads, absolute; [] for a call that reads nothing the guard can
    name. Plain only: a version at another revision, judged by the globs of every tree alone."""
    return scan(tool, tin, cwd, expand_token)[0]


def scan(tool, tin, cwd, expand_token):
    """reads_of's paths, and the call's searches from a folder (W2-141): (start, start as written, keep, how,
    cwd)."""
    if tool == "Bash":
        cmd = tin.get("command")
        if not isinstance(cmd, str):
            return [], []
        b = Bash(expand_token)
        b.run(cmd, cwd)
        return b.found, b.searches
    return [(p, tool, False) for p in tool_reads(tool, tin, cwd) if p], tool_searches(tool, tin, cwd)


def tool_searches(tool, tin, cwd):
    """A Grep call's search from its path (its globs as rg's), a Glob call's listing from its path (its pattern)."""
    if tool not in ("Grep", "Glob"):
        return []
    p = tin.get("path")
    start = _abs(os.path.expanduser(p), cwd) if isinstance(p, str) and p else cwd
    if tool == "Grep":
        g = tin.get("glob") if isinstance(tin.get("glob"), str) else ""
        return [(start, start, _x_rg(x_grep_tool_globs(g)), "Grep", cwd)]
    pattern = tin.get("pattern") if isinstance(tin.get("pattern"), str) else ""
    if pattern.startswith("/"):
        start, pattern = "/", pattern.lstrip("/")
    return [(start, start, x_glob_tool(pattern), "Glob", cwd)] if pattern else []


def _reads_names(words):
    """A reader (or an xargs that runs one): the names its $(...) words give are files it opens."""
    import bash_writes as bw
    lead = bw.lead(words)
    return bool(lead) and (os.path.basename(lead[0]) in X_READERS or _xargs_reads(lead))


_XARGS_VALUED = frozenset("-a -d -E -I -L -n -P -s --arg-file --delimiter --max-args --max-procs --max-chars "
                          "--process-slot-var".split())


def _xargs_reads(words):
    """An xargs that runs a reader on the names fed to it."""
    import bash_writes as bw
    lead = bw.lead(words)
    if not lead or os.path.basename(lead[0]) != "xargs":
        return False
    i = 1
    while i < len(lead) and lead[i].startswith("-") and lead[i] != "-":
        i += 2 if lead[i] in _XARGS_VALUED else 1
    return i < len(lead) and os.path.basename(lead[i]) in X_READERS


def _loop_reads(cmds, k):
    """Command ``k`` starts a while (or until) read loop whose body, up to its done, runs a reader."""
    import bash_writes as bw
    words = cmds[k][0]
    if words[:1] not in (["while"], ["until"]) or "read" not in words:
        return False
    for body, _reds, _sep in cmds[k + 1:]:
        if body[:1] == ["done"]:
            return False
        lead = bw.lead(body)
        if lead and (os.path.basename(lead[0]) in X_READERS or _xargs_reads(lead)):
            return True
    return False


def _reaches(folder, start, word, keep, cwd):
    """Whether a search from ``start`` takes in a file of ``folder`` (real paths): one that starts in it does; else
    each file is put to ``keep``. A folder that cannot be walked whole, or holds more files than are judged, is
    reached (the guard fails closed here: the refusal says how to keep it out)."""
    if start == folder or start.startswith(folder + "/"):
        return True

    def fault(err):
        raise err
    n = 0
    try:
        for top, dirs, names in os.walk(folder, onerror=fault):
            dirs.sort()
            for name in sorted(names):
                n += 1
                if n > MOST_GLOB or keep(os.path.join(top, name), start, word, cwd):
                    return True
    except OSError:
        return True
    return False


def search_refusal(js, searches):
    """W2-141 (DEC-1093 (2)): why a search from a folder that holds the engineer's own acceptance folder (in any tree)
    takes it in, or None. The folder is {ticket_tests}'s own (tests/acceptance/<WBS>/); a start the guard cannot
    resolve is let through, as before."""
    owns = [(j, d.glob[len(ACCEPTANCE) + 1:-3]) for j in js for d in j.denied
            if isinstance(d, Denied) and d.tree is None and "{ticket_tests}" in d.entry]
    for start, word, keep, how, cwd in searches if owns else ():
        if start is None:
            continue
        start = os.path.realpath(start)
        here = os.path.realpath(cwd) if cwd else None
        above = start.rstrip("/") + "/"
        for j, wbs in owns:
            top = _toplevel(start)
            for tree in dict.fromkeys(list(j.trees()) + ([top] if top else [])):
                folder = os.path.join(tree, ACCEPTANCE, wbs)
                if not (folder.startswith(above) or folder == start or start.startswith(folder + "/")):
                    continue
                if os.path.isdir(folder) and _reaches(folder, start, word or start, keep, here):
                    return (f"the search can reach {ACCEPTANCE}/{wbs}/, the ticket's own acceptance tests, which the "
                            f"{j.role} does not read: role_paths.{j.role}.reads_denied ({PATH_MAP_REL}, DEC-1052 "
                            f"G-14, DEC-1093 (2)); " + X_HOW[how].format(w=wbs))
    return None


# -- W2-141: what a search keeps out (DEC-1093 (2), DEC-1102) ------------------------------------------------
# The same block as gov.guard.reads's (between the markers, byte for byte: a unit test compares them), kept here
# so that the hook does not need the pinned product to hold it.
# BEGIN W2-141 BLOCK

SEARCH_REFUSAL = ("the search can reach {folder}, the ticket's own acceptance tests, the "
                  "counterpart's work, which is refused to the ticket's engineer (DEC-820 "
                  "(c), DEC-1093 (2)): {how}")
X_HOW = {
    "Grep": ("exclude it with the glob !tests/acceptance/{w}/** (Grep's glob, from the "
             "session's folder; !**/{w}/** from any folder), or search a path that does "
             "not hold it"),
    "grep": ("exclude it with --exclude-dir={w} (grep matches a folder's base name, never "
             "a path), or search a folder that does not hold it"),
    "rg": ("exclude it with -g '!tests/acceptance/{w}/**' (from the session's folder; "
           "-g '!**/{w}/**' from any folder), or search a folder that does not hold it"),
    "ag": "exclude it with --ignore-dir={w}, or search a folder that does not hold it",
    "ack": "exclude it with --ignore-dir={w}, or search a folder that does not hold it",
    "find": ("exclude it with -name {w} -prune -o ... (or -not -path '*/{w}/*'), or "
             "start from a folder that does not hold it"),
    "Glob": ("Glob has no exclusion: give a path or a pattern that cannot reach it (src/, "
             "or a pattern under another folder)"),
}
_X_GREP_VALUED = frozenset(
    "-e -f -m -A -B -C -d -D --regexp --file --include --exclude --exclude-dir "
    "--exclude-from --max-count --context --after-context --before-context "
    "--directories --devices --label --binary-files --group-separator".split())
_X_RG_VALUED = frozenset(
    "-e -f -g -t -T -m -A -B -C -j -M -d -E -r --regexp --file --glob --iglob --type "
    "--type-not --type-add --type-clear --max-count --context --after-context "
    "--before-context --threads --max-columns --max-depth --maxdepth --encoding --sort "
    "--sortr --replace --ignore-file --pre --pre-glob --max-filesize "
    "--path-separator --context-separator --field-match-separator --engine".split())
_X_AG_VALUED = frozenset(
    "-A -B -C -G -g -m -p -W --after --before --context --file-search-regex --ignore "
    "--ignore-dir --max-count --depth --path-to-ignore --pager --workers "
    "--width".split())
_X_ACK_VALUED = frozenset(
    "-A -B -C -m -g --after-context --before-context --context --max-count "
    "--ignore-dir --ignore-directory --noignore-dir --noignore-directory --ignore-file "
    "--type --type-add --type-set --type-del --output --pager --match "
    "--files-from".split())
_X_PATTERN = frozenset({"-e", "-f", "--regexp", "--file"})
# The readers a find's action or an xargs runs: they print or copy what they open.
X_READERS = frozenset(
    "cat tac nl less more bat batcat head tail cmp diff colordiff od xxd hexdump "
    "strings base64 uniq sort cut fold fmt paste column expand unexpand rev iconv "
    "grep egrep fgrep zgrep rg ag ack sed awk gawk mawk nawk jq yq cp".split())
_X_FIND_PATHS = frozenset("-path -wholename -ipath -iwholename".split())
_X_FIND_NAMES = frozenset("-name -iname".split())
_X_FIND_OPENS = frozenset("-exec -execdir -ok -okdir".split())


def x_glob(pattern: str) -> "re.Pattern[str]":
    """A glob as a whole-path matcher: ``**`` crosses folders, ``*`` and
    ``?`` stay in one name, ``[...]`` one character, ``{a,b}`` either."""
    def part(p: str) -> str:
        out, i = [], 0
        while i < len(p):
            if p.startswith("**/", i):
                out.append("(?:.*/)?")
                i += 3
            elif p.startswith("**", i):
                out.append(".*")
                i += 2
            elif p[i] == "*":
                out.append("[^/]*")
                i += 1
            elif p[i] == "?":
                out.append("[^/]")
                i += 1
            elif p[i] == "[" and p.find("]", i + 2) > 0:
                j = p.find("]", i + 2)
                body = p[i + 1:j]
                body = "^" + body[1:] if body[:1] in "!^" else body
                out.append("[" + body.replace("\\", "\\\\") + "]")
                i = j + 1
            elif p[i] == "{" and p.find("}", i) > 0 and "," in p[i:p.find("}", i)]:
                j = p.find("}", i)
                out.append("(?:" + "|".join(part(a) for a in p[i + 1:j].split(",")) + ")")
                i = j + 1
            else:
                out.append(re.escape(p[i]))
                i += 1
        return "".join(out)
    return re.compile("(?s)" + part(pattern) + r"\Z")


def _x_parse(args: list[str], valued: frozenset):
    """(operands, [(option, value)], short flag letters): a value glued, after
    ``=``, or the next word; after ``--`` every word is an operand."""
    operands, options, letters = [], [], set()
    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == "--":
            operands += args[i:]
            break
        if not a.startswith("-") or a == "-":
            operands.append(a)
        elif a.startswith("--"):
            opt, eq, val = a.partition("=")
            if opt in valued and not eq and i < len(args):
                val, i = args[i], i + 1
            options.append((opt, val))
        else:
            for j in range(1, len(a)):
                opt = "-" + a[j]
                if opt in valued:
                    val = a[j + 1:]
                    if not val and i < len(args):
                        val, i = args[i], i + 1
                    options.append((opt, val))
                    break
                letters.add(a[j])
                options.append((opt, ""))
    return operands, options, letters


def _x_rel(f: str, start: str) -> list[str]:
    return f[len(start.rstrip("/")) + 1:].split("/")


def _x_depth(keep, depth):
    try:
        most = int(depth)
    except (TypeError, ValueError):
        return keep
    return lambda f, start, word, cwd: (len(_x_rel(f, start)) <= most
                                        and keep(f, start, word, cwd))


def _x_rg(globs: list[tuple[str, bool]]):
    """rg's -g/--iglob (and the Grep tool's globs): gitignore lines matched
    against the path from the session's folder; the last that matches wins; a
    folder kept out is not walked; with a positive glob, a file no glob
    matches is not searched."""
    rules = []
    for g, fold in globs:
        neg = g.startswith("!")
        body = g[1:] if neg else g
        body = body.lower() if fold else body
        only_dir = body.endswith("/")
        body = body.rstrip("/")
        if body.startswith("/"):
            body = body[1:]
        elif "/" not in body:
            body = "**/" + body
        if body:
            rules.append((x_glob(body), only_dir, neg, fold))
    white = any(not neg for _rx, _d, neg, _f in rules)

    def verdict(path: str, is_dir: bool):
        last = None
        for rx, only_dir, neg, fold in rules:
            if (is_dir or not only_dir) and rx.match(path.lower() if fold else path):
                last = neg
        return last

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        def view(p: str) -> str:
            if cwd and p.startswith(cwd.rstrip("/") + "/"):
                return p[len(cwd.rstrip("/")) + 1:]
            return p
        at = start.rstrip("/")
        for name in _x_rel(f, start)[:-1]:
            at += "/" + name
            if verdict(view(at), True) is True:
                return False
        found = verdict(view(f), False)
        return not (found is True or (found is None and white))
    return keep


def _x_grep(rules: list[tuple[str, str]]):
    """grep -r's --exclude-dir (a folder's base name), --include and
    --exclude (a file's base name: the last that matches wins; none, and the
    file is searched unless the first is --include)."""
    import fnmatch as fm
    dirs = [g.rstrip("/") for k, g in rules if k == "exclude-dir"]
    files = [(k, g) for k, g in rules if k in ("include", "exclude")]

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = _x_rel(f, start)
        if any(fm.fnmatchcase(d, g) for d in rel[:-1] for g in dirs):
            return False
        last = None
        for k, g in files:
            if fm.fnmatchcase(rel[-1], g):
                last = k
        return (not files or files[0][0] != "include") if last is None else last == "include"
    return keep


def _x_ag(pats: list[str]):
    """ag's --ignore and --ignore-dir: a name at any depth, or a path from
    where the search starts."""
    import fnmatch as fm

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = _x_rel(f, start)
        for p in pats:
            q = p.strip("/") or p
            if "/" in q:
                rx = x_glob(q)
                if any(rx.match("/".join(rel[:k])) for k in range(1, len(rel) + 1)):
                    return False
            elif any(fm.fnmatchcase(n, q) for n in rel):
                return False
        return True
    return keep


def _x_ack(rules: list[tuple[bool, str]]):
    """ack's --ignore-dir (NAME, is:NAME, match:REGEX), undone by a later
    --noignore-dir."""
    def gone(d: str) -> bool:
        out = False
        for add, spec in rules:
            if spec.startswith("match:"):
                try:
                    hit = bool(re.search(spec[6:], d))
                except re.error:
                    hit = False
            else:
                hit = (spec[3:] if spec.startswith("is:") else spec).rstrip("/") == d
            out = add if hit else out
        return out

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        return not any(gone(d) for d in _x_rel(f, start)[:-1])
    return keep


def _x_test(t: str, v: str, printed: str, name: str) -> bool:
    import fnmatch as fm
    s = printed if t in _X_FIND_PATHS else name
    if t.startswith("-i"):
        s, v = s.lower(), v.lower()
    return fm.fnmatchcase(s, v)


def _x_find(expr: list[str]):
    """find's expression: TEST -prune -o ... and ( TEST -o TEST ) -prune -o
    ... keep a folder out (not under -depth); with no -o after them, a
    negated -path or -name keeps a file out and a positive one must hold;
    -maxdepth bounds the depth."""
    pruned: list[tuple[str, str]] = []
    rest = list(expr)
    tests = _X_FIND_PATHS | _X_FIND_NAMES
    harmless = {"-type": "d", "-maxdepth": None, "-mindepth": None, "-xdev": "",
                "-mount": ""}
    while "-prune" in rest and "-depth" not in expr:
        k = rest.index("-prune")
        if rest[k + 1:k + 2] not in (["-o"], ["-or"]):
            break
        head = rest[:k]
        if head[-1:] == [")"] and "(" in head:
            m = len(head) - 1 - head[::-1].index("(")
            inner, pre, group = head[m + 1:-1], head[:m], []
            alts = [[]]
            for a in inner:
                if a in ("-o", "-or"):
                    alts.append([])
                else:
                    alts[-1].append(a)
            if not all(len(x) == 2 and x[0] in tests for x in alts):
                break
            group = [(x[0], x[1]) for x in alts]
        elif len(head) >= 2 and head[-2] in tests:
            group, pre = [(head[-2], head[-1])], head[:-2]
        else:
            break
        i, ok = 0, True
        while i < len(pre):  # only -type d and the global options before it
            a = pre[i]
            if a in ("-a", "-and"):
                i += 1
            elif a in harmless and harmless[a] == "":
                i += 1
            elif a in harmless and i + 1 < len(pre) and (harmless[a] is None
                                                         or pre[i + 1] == harmless[a]):
                i += 2
            else:
                ok = False
                break
        if not ok:
            break
        pruned += group
        rest = rest[k + 2:]
    negated: list[tuple[str, str]] = []
    positive: list[tuple[str, str]] | None = []
    if any(a in ("-o", "-or", ",") for a in rest):
        positive = None  # an alternative: no test on the file is trusted
    else:
        i = 0
        while i < len(rest):
            a = rest[i]
            if a in ("!", "-not") and i + 2 < len(rest) and rest[i + 1] in tests:
                negated.append((rest[i + 1], rest[i + 2]))
                i += 3
            elif a in tests and i + 1 < len(rest):
                positive.append((a, rest[i + 1]))
                i += 2
            else:
                i += 1
    depth = next((expr[k + 1] for k, a in enumerate(expr[:-1]) if a == "-maxdepth"), None)

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = _x_rel(f, start)
        base = word.rstrip("/")
        for k in range(1, len(rel) + 1):
            printed = base + "/" + "/".join(rel[:k])
            if any(_x_test(t, v, printed, rel[k - 1]) for t, v in pruned):
                return False
        printed = base + "/" + "/".join(rel)
        if any(_x_test(t, v, printed, rel[-1]) for t, v in negated):
            return False
        return positive is None or all(_x_test(t, v, printed, rel[-1]) for t, v in positive)
    return _x_depth(keep, depth)


def x_glob_tool(pattern: str):
    """The Glob tool's pattern, from its path (a pattern with no folder in it
    at any depth, as rg's --files reads it) or from the session's folder."""
    rx = x_glob(pattern.lstrip("/"))

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = "/".join(_x_rel(f, start))
        if rx.match(rel) or ("/" not in pattern and rx.match(os.path.basename(f))):
            return True
        return bool(cwd) and f.startswith(cwd.rstrip("/") + "/") and bool(
            rx.match(f[len(cwd.rstrip("/")) + 1:]))
    return keep


def x_grep_tool_globs(glob: str) -> list[tuple[str, bool]]:
    """The Grep tool's glob parameter as the globs it gives rg: split on
    whitespace, and on commas outside braces."""
    out: list[tuple[str, bool]] = []
    for g in (glob or "").split():
        out += [(g, False)] if "{" in g and "}" in g else [(p, False) for p in g.split(",") if p]
    return out


def x_search(name: str, args: list[str]):
    """A recursive search's (start operands, keep, how, names only), or None:
    keep(f, start, word, cwd) says whether it takes in the file ``f`` (real
    paths; ``word``: the start as written).  Names only: a listing (rg
    --files, ag -g, ack -f/-g, a find with no action that reads), a search
    only when its names go to a reader."""
    name = os.path.basename(name)
    if name in ("grep", "egrep", "fgrep", "zgrep"):
        operands, options, letters = _x_parse(args, _X_GREP_VALUED)
        if not (letters & {"r", "R"} or any(
                o in ("--recursive", "--dereference-recursive")
                or (o in ("-d", "--directories") and v == "recurse") for o, v in options)):
            return None
        if _X_PATTERN.isdisjoint(o for o, _ in options):
            operands = operands[1:]
        rules = [(o[2:], v) for o, v in options if o in ("--include", "--exclude", "--exclude-dir")]
        return ["." if p in ("*", "./*") else p for p in operands] or ["."], _x_grep(rules), "grep", False
    if name == "rg":
        operands, options, letters = _x_parse(args, _X_RG_VALUED)
        files = any(o == "--files" for o, _ in options)
        if not files and _X_PATTERN.isdisjoint(o for o, _ in options):
            operands = operands[1:]
        fold = any(o == "--glob-case-insensitive" for o, _ in options)
        globs = [(v, fold or o == "--iglob") for o, v in options if o in ("-g", "--glob", "--iglob")]
        depth = next((v for o, v in options if o in ("-d", "--max-depth", "--maxdepth")), None)
        return operands, _x_depth(_x_rg(globs), depth), "rg", files
    if name == "ag":
        operands, options, letters = _x_parse(args, _X_AG_VALUED)
        names = any(o == "-g" for o, _ in options) or "--list-file-types" in args
        if not names:
            operands = operands[1:]
        pats = [v for o, v in options if o in ("--ignore", "--ignore-dir")]
        depth = next((v for o, v in options if o == "--depth"), None)
        return operands, _x_depth(_x_ag(pats), depth), "ag", names
    if name == "ack":
        operands, options, letters = _x_parse(args, _X_ACK_VALUED)
        names = "f" in letters or any(o == "-g" for o, _ in options)
        if not names and not any(o == "--match" for o, _ in options):
            operands = operands[1:]
        rules = [(o.startswith("--ignore"), v) for o, v in options if o in (
            "--ignore-dir", "--ignore-directory", "--noignore-dir", "--noignore-directory")]
        return operands, _x_ack(rules), "ack", names
    if name == "find":
        i = 0
        while i < len(args) and args[i] in ("-H", "-L", "-P"):
            i += 1
        j = i
        while j < len(args) and not (args[j].startswith("-") or args[j] in ("!", "(", ")", ",")):
            j += 1
        expr = args[j:]
        reads = any(a in _X_FIND_OPENS and k + 1 < len(expr)
                    and os.path.basename(expr[k + 1]) in X_READERS for k, a in enumerate(expr))
        return args[i:j] or ["."], _x_find(expr), "find", not reads
    return None


def x_how(wbs: str, how: str) -> str:
    """The refusal of a search that can reach the folder, saying how to keep it out."""
    return SEARCH_REFUSAL.format(folder=f"tests/acceptance/{wbs}/",
                                 how=X_HOW[how].format(w=wbs))

# END W2-141 BLOCK


# -- the hook's entry -----------------------------------------------------------------------------------------------

def judges(sec, roles, root, ticket_id, trees, main=None):
    """A Judge per role the section names (the session's and the acting one); the ticket is read only when a
    role's globs need it."""
    from gov.guard import reads
    out, front, wbs, names = [], None, None, set()
    for role in roles:
        entry = sec.get(role) if role else None
        if not entry:
            continue
        globs = entry["reads_denied"]
        if any("{ticket_" in g for g in globs) and front is None:
            names, wbs = reads._ticket(root, ticket_id)
            front = ticket_front(root, ticket_id) if any("{ticket_impl" in g for g in globs) else {}
            if not wbs and isinstance(front.get("wbs_id"), str):
                wbs = front["wbs_id"]
        allowed = front.get("allowed_paths") if isinstance(front, dict) else None
        if isinstance(front, dict) and isinstance(front.get("id"), str):
            names = set(names) | {front["id"]}
        out.append(Judge(role, expand(globs, wbs, allowed if isinstance(allowed, list) else [], root, main=main,
                                      names=names, links=_links_unless_coordination(root, ticket_id, front)),
                         trees))
    return out


def coordination(front):
    """A coordination ticket (front matter ``class: coordination``, as W2-00): it has no acceptance tests of its own,
    and the work committed under it (the CTO's, the refactoring's) revises other tickets' tests for them."""
    return isinstance(front, dict) and str(front.get("class") or "").strip() == "coordination"


def _links_unless_coordination(root, ticket_id, front):
    """{ticket_tests}'s link source for the session's ticket: none for a coordination ticket (its own folder only;
    ACT-G14b, after D-4's cut tied 109 acceptance files to W2-00 through Task: DAEO-sdxk), linked_tests otherwise.
    The ticket's class is read only when the links are first wanted (an engineer's read of another ticket's
    acceptance folder); a ticket that cannot be read gives None (only the own folder, and the refusal says so)."""
    seen = []

    def links(main, names, wbs):
        if not seen:
            try:
                seen.append(front if front else ticket_front(root, ticket_id))
            except Exception:
                seen.append(None)
        if seen[0] is None:
            return None
        if coordination(seen[0]):
            return set()
        return linked_tests(main, names, wbs)
    return links


def refusal(main, root, tool, tin, cwd, roles, ticket_id, trees, expand_token):
    """Why the role's call is refused by the main tree's ``role_paths:``, or None."""
    sec = section(main)
    if not sec or not any(r in sec for r in roles if r):
        return None
    js = judges(sec, roles, root, ticket_id, trees, main)
    if not js:
        return None
    paths, searches = scan(tool, tin, cwd, expand_token)
    found = judge_paths(js, [(p, plain) for p, _how, plain in paths])
    return found[0] if found else search_refusal(js, searches)
