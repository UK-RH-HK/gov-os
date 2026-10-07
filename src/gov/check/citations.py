"""core-decision-citations: a commit citing a decision its own tree does not record (DEC-463)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from gov.cli.errors import GovError
from gov.decisions.checker import DECISION_ID, _front, _git, _Objects

VERSION = "1.0.0"

CITATION = re.compile(rf"\b(?:{DECISION_ID.pattern})\b")  # the kernel's decision_id grammar, as a whole word


def _commits(root: Path) -> list[tuple[str, str]]:
    """``(commit, message)`` of every commit reachable from ``HEAD``."""
    log = _git(root, "log", "-z", "--format=%H%n%B", "HEAD").decode("utf-8", "replace")
    return [tuple(entry.partition("\n")[::2]) for entry in log.split("\0") if entry]


def _register(root: Path, objects: _Objects, commit: str) -> tuple[set[str], list[str]]:
    """The decision ids recorded in the tree of ``commit``, and its Markdown files that cannot be read."""
    recorded, unreadable = set(), []
    for entry in _git(root, "ls-tree", "-r", "-z", commit).decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        if not path.endswith(".md") or meta.split()[1] != "blob":
            continue
        blob = meta.split()[2]
        if blob not in objects.known:  # the id a file records, "" for none, None where it cannot be read
            content = objects.read(blob)
            if content is None:
                raise objects.unreadable(f"{commit}:{path}")
            try:
                front = _front(content[1].decode("utf-8", "replace"))
                objects.known[blob] = str(front["id"]) if "id" in front and (
                    front.get("type") == "decision" or DECISION_ID.fullmatch(str(front["id"]))) else ""
            except ValueError:
                objects.known[blob] = None
        if objects.known[blob] is None:
            unreadable.append(path)
        elif objects.known[blob]:
            recorded.add(objects.known[blob])
    return recorded, unreadable


def check(root: Path) -> list[dict]:
    root = Path(root)
    if _git(root, "rev-parse", "--show-prefix").strip() != b"":
        raise GovError("CITATIONS_NOT_A_REPOSITORY", f"{root} is not the root of a git repository")
    findings = []
    objects = _Objects(root)
    try:
        for commit, message in _commits(root):
            cited = sorted({match.group(0) for match in CITATION.finditer(message)})
            if not cited:
                continue
            recorded, unreadable = _register(root, objects, commit)
            if unreadable:  # the register of this commit is not known: its citations are not judged
                findings += [{"code": "REGISTER_UNREADABLE", "commit": commit, "path": path,
                              "message": f"{path} at {commit[:12]}: the frontmatter cannot be read"}
                             for path in unreadable]
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
