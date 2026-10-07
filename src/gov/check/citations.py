"""core-decision-citations: a commit citing a decision its own tree does not record (DEC-463).

A decision is recorded as a decision file or as an entry of the register file the project names (DEC-473); the
commits judged are those after the base commit the project records (DEC-474). Both are optional keys of the
project's path map, read as the project holds it now (DEC-479)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import PROJECT_DIR, load_config
from gov.decisions.checker import DECISION_ID, _front, _git, _Objects, _once

VERSION = "1.1.0"

CITATION = re.compile(rf"\b(?:{DECISION_ID.pattern})\b")  # the kernel's decision_id grammar, as a whole word
REGISTER_KEY, BASE_KEY = "decision_register", "decision_citations_base"
# DEC-473: a level-3 heading at the start of a line, the id, a space, a colon or a dash, and the title
ENTRY = re.compile(r"### (DEC-[0-9]+)(?=[ :\-–—])[ \t:\-–—]*[^\s:\-–—]")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
COMMIT_ID = re.compile(r"[0-9a-fA-F]{4,64}")


def _configured(root: Path) -> tuple[str | None, str | None]:
    """The register file and the base commit the project's path map names; None for the one it does not name."""
    path_map = load_config(root).get("path-map.yaml", {})
    for key in (REGISTER_KEY, BASE_KEY):
        if key in path_map and not (isinstance(path_map[key], str) and path_map[key].strip()):
            raise GovError("CITATIONS_CONFIG_INVALID", f"{PROJECT_DIR}/path-map.yaml: key '{key}' must be a "
                           "string that is not empty (a commit id of digits alone is written in quotes)")
    return path_map.get(REGISTER_KEY), path_map.get(BASE_KEY)


def _after(root: Path, base: str) -> str:
    """The range of the commits after ``base``; a GovError where ``base`` is no commit that ``HEAD`` descends from."""
    if COMMIT_ID.fullmatch(base):
        try:
            commit = _git(root, "rev-parse", "--verify", "--quiet", base + "^{commit}").decode("ascii").strip()
            if commit.startswith(base.lower()):  # the id of the commit, not a branch or a tag named in hex digits
                _git(root, "merge-base", "--is-ancestor", commit, "HEAD")
                return f"{commit}..HEAD"
        except GovError:
            pass
    raise GovError("CITATIONS_BASE_UNKNOWN", f"the base commit {base!r} recorded under '{BASE_KEY}' is not one "
                   f"commit of {root} that HEAD descends from: no commit is judged")


def _commits(root: Path, base: str | None) -> list[tuple[str, str]]:
    """``(commit, message)`` of every commit judged: reachable from ``HEAD`` and, with a base, not from the base."""
    span = "HEAD" if base is None else _after(root, base)
    log = _git(root, "log", "-z", "--format=%H%n%B", span).decode("utf-8", "replace")
    commits = [tuple(entry.partition("\n")[::2]) for entry in log.split("\0") if entry]
    if not commits:  # no commit to judge is not a clean history
        raise GovError("CITATIONS_NOTHING_JUDGED", f"no commit after the base commit {base}: nothing is judged")
    return commits


def _entries(content: bytes) -> set[str] | None:
    """The ids a register file records by its entry headings outside fenced code blocks; None where it is not text."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if "\0" in text:
        return None
    recorded, fence = set(), None
    for line in text.split("\n"):
        mark, entry = FENCE.match(line), ENTRY.match(line)
        if fence is None:
            if mark:
                fence = mark.group(1)
            elif entry:
                recorded.add(entry.group(1))
        elif mark and mark.group(1).startswith(fence) and not line[mark.end():].strip():
            fence = None  # closed by a fence of the same mark, at least as long, with nothing after it
    return recorded


def _register(root: Path, objects: _Objects, commit: str, register: str | None) -> tuple[set[str], list[tuple]]:
    """The decision ids recorded in the tree of ``commit`` by its decision files and by the file ``register``, and
    ``(path, reason)`` of each Markdown file and of the named register that cannot be read there."""
    recorded, unreadable = set(), []
    absent = register is not None
    for entry in _git(root, "ls-tree", "-r", "-z", commit).decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        if not path or meta.split()[1] != "blob":
            continue
        mode, _, blob = meta.split()
        if path == register and mode.startswith("100"):  # a file, not a link to one
            entries = _once(objects, ("entries", blob), lambda: _entries(_content(objects, blob, commit, path)))
            absent = False
            if entries is None:
                unreadable.append((path, "the register is not a file of text"))
            else:
                recorded |= entries
        if not path.endswith(".md"):
            continue
        if blob not in objects.known:  # the id a file records, "" for none, None where it cannot be read
            try:
                front = _front(_content(objects, blob, commit, path).decode("utf-8", "replace"))
                objects.known[blob] = str(front["id"]) if "id" in front and (
                    front.get("type") == "decision" or DECISION_ID.fullmatch(str(front["id"]))) else ""
            except ValueError:
                objects.known[blob] = None
        if objects.known[blob] is None:
            unreadable.append((path, "the frontmatter cannot be read"))
        elif objects.known[blob]:
            recorded.add(objects.known[blob])
    if absent:
        unreadable.append((register, "the register is not a file of this tree"))
    return recorded, unreadable


def _content(objects: _Objects, blob: str, commit: str, path: str) -> bytes:
    """The bytes of ``blob``; a GovError where git names the object and the repository does not hold it."""
    content = objects.read(blob)
    if content is None:
        raise objects.unreadable(f"{commit}:{path}")
    return content[1]


def check(root: Path) -> list[dict]:
    root = Path(root)
    if _git(root, "rev-parse", "--show-prefix").strip() != b"":
        raise GovError("CITATIONS_NOT_A_REPOSITORY", f"{root} is not the root of a git repository")
    findings = []
    objects = _Objects(root)
    try:
        register, base = _configured(root)
        for commit, message in _commits(root, base):
            cited = sorted({match.group(0) for match in CITATION.finditer(message)})
            if not cited:
                continue
            recorded, unreadable = _register(root, objects, commit, register)
            if unreadable:  # the register of this commit is not known: its citations are not judged
                findings += [{"code": "REGISTER_UNREADABLE", "commit": commit, "path": path,
                              "message": f"{path} at {commit[:12]}: {reason}"}
                             for path, reason in unreadable]
                continue
            findings += [{"code": "DECISION_UNRECORDED", "commit": commit, "decision": decision,
                          "message": f"commit {commit[:12]} cites {decision}, which its tree does not record"}
                         for decision in cited if decision not in recorded]
    finally:
        objects.close()
    return findings


if __name__ == "__main__":
    import sys
    try:
        results = check(Path.cwd())
    except GovError as exc:
        print(json.dumps({"unmeasured": True, "reason": exc.message}))
        sys.exit(1)
    print(json.dumps({"findings": results}, indent=2))
    sys.exit(1 if results else 0)
