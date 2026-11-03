"""W2-61h's form tests: shared constants and readers (DAEO-h2k3; DEC-1055 (4), DEC-1052 G-3, DEC-820 (d)).

The 28 new memory questions: ``q21.yaml`` to ``q24.yaml`` in this tree's visible folder, and 24 in the hidden folder
of the sets root outside every worktree, named by ``GOV_EVAL_SETS_ROOT`` (absent: every hidden case skips). The
question form is ``src/gov/retrieval/measure.py``'s docstring: ``question``, ``gold_answer`` and ``sources``
required; a source is a map with ``path`` and optionally ``heading``, ``lines: [first, last]`` and ``commit``, or a
list of such maps (alternatives).

Nothing here prints a hidden question, answer, category or gold path: the readers return faults as short words, and
the hidden cases name a file by its file name only (S5, DEC-820 (d)).
"""

from __future__ import annotations

import hashlib
import os
import pwd
import re
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SET = "memory-retrieval"
PATH_MAP_REL = "governance/project/path-map.yaml"
VISIBLE = REPO_ROOT / "fixtures/evaluation" / SET / "visible"
HIDDEN_REL = f"fixtures/evaluation/{SET}/hidden"
NEW_VISIBLE = ("q21.yaml", "q22.yaml", "q23.yaml", "q24.yaml")
LENS_B = tuple(f"q{n:02d}.yaml" for n in range(1, 21))
HIDDEN_COUNT = 24
SETS_ROOT_VAR = "GOV_EVAL_SETS_ROOT"
TICKET = "DAEO-h2k3"
TIMEOUT_S = 60.0

# S3's spread of the 28 new questions, by the category labels the writer's draw used (recorded in the README).
# "A plan, ticket or path-map fact" takes any of its three labels.
SPREAD = {
    "decision": 5, "exact-string": 4, "callers": 4, "code-paraphrase": 3, "kernel-template": 3,
    "multi-file": 3, "history": 2, "failure-memory": 2, "plan-ticket-path-map": 1, "nonexistent-id": 1,
}
LABELS = {**{name: name for name in SPREAD if name != "plan-ticket-path-map"},
          "plan": "plan-ticket-path-map", "ticket": "plan-ticket-path-map", "path-map": "plan-ticket-path-map"}


def real_home() -> Path:
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def path_map_entry() -> dict:
    return yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))["evaluation_sets"][SET]


def measured_roles() -> list[str]:
    return list((path_map_entry().get("measures") or {}).get("roles") or [])


def load(path: Path):
    """A question file as a map, or None (never raises; the caller names the file only)."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - a YAML error quotes the file; it is swallowed here
        return None
    return data if isinstance(data, dict) else None


def entries(data: dict):
    """The sources as a list of entries, each a list of alternative maps; None when malformed."""
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        return None
    out = []
    for entry in sources:
        alternatives = entry if isinstance(entry, list) else [entry]
        if not alternatives or not all(isinstance(a, dict) and isinstance(a.get("path"), str) and a["path"].strip()
                                       for a in alternatives):
            return None
        out.append(alternatives)
    return out


def form_faults(data) -> list[str]:
    """The question form's faults, as fixed words only."""
    if data is None:
        return ["not a YAML map"]
    faults = []
    if not (isinstance(data.get("question"), str) and data["question"].strip()):
        faults.append("no question")
    if not (isinstance(data.get("gold_answer"), str) and data["gold_answer"].strip()):
        faults.append("no gold_answer")
    if entries(data) is None:
        faults.append("sources is not a non-empty list of maps with a path")
    if "category" in data and data["category"] not in LABELS:
        faults.append("a category outside S3's ten")
    if "category" not in data:
        faults.append("no category")
    return faults


def cat_file(specs: list[str]) -> dict[str, bytes | None]:
    """``git cat-file --batch`` over ``<rev>:<path>`` specs: each spec's bytes, or None when it is no blob."""
    if not specs:
        return {}
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "cat-file", "--batch"],
                          input=("\n".join(specs) + "\n").encode(), capture_output=True, timeout=TIMEOUT_S)
    out, at, found = done.stdout, 0, {}
    for spec in specs:
        end = out.index(b"\n", at)
        line = out[at:end]
        at = end + 1
        if line.endswith((b" missing", b" ambiguous")):
            found[spec] = None
            continue
        _, kind, size = line.split()
        if kind == b"blob":
            found[spec] = out[at:at + int(size)]
        else:                       # a tree or another object: no file
            found[spec] = None
        at += int(size) + 1
    return found


_HEADING = re.compile(r"(#{1,6})\s")


def span_of(lines: list[str], source: dict):
    """The measure's rule (measure.py's docstring): a heading found is the first line equal to it (trailing
    whitespace removed) and governs; a ``#`` heading spans to the line before the next heading of the same or a
    higher level, any other heading as many lines as ``lines`` state. Not found, the stated lines, which must lie in
    the file. A path alone is the whole file. Returns (first, last, by) with by 'heading', 'lines' or 'path'; None
    when nothing resolves."""
    stated = source.get("lines")
    if stated is not None and not (isinstance(stated, list) and len(stated) == 2
                                   and all(isinstance(n, int) for n in stated) and 1 <= stated[0] <= stated[1]):
        return None
    heading = source.get("heading")
    if heading is not None:
        at = next((i for i, line in enumerate(lines) if line.rstrip() == str(heading).rstrip()), None)
        if at is not None:
            mark = _HEADING.match(lines[at])
            if not mark:
                return at + 1, at + (stated[1] - stated[0] + 1 if stated else 1), "heading"
            level = len(mark.group(1))
            end = next((j for j in range(at + 1, len(lines))
                        if (m := _HEADING.match(lines[j])) and len(m.group(1)) <= level), len(lines))
            return at + 1, end, "heading"
    if stated is None:
        return (1, max(len(lines), 1), "path") if heading is None else None
    if stated[1] > len(lines):
        return None
    return stated[0], stated[1], "lines"


def span_text(data: dict, rev: str = "HEAD") -> list[list[str]]:
    """Each entry's resolved text at ``rev``, one string per alternative ('' when it does not resolve)."""
    out = []
    for alts in entries(data) or []:
        blobs = cat_file([f"{rev}:{a['path'].removeprefix('./')}" for a in alts])
        texts = []
        for a in alts:
            blob = blobs.get(f"{rev}:{a['path'].removeprefix('./')}")
            lines = blob.decode("utf-8", "replace").splitlines() if blob is not None else []
            span = span_of(lines, a) if blob is not None else None
            texts.append("\n".join(lines[span[0] - 1:span[1]]) if span else "")
        out.append(texts)
    return out


def source_faults(data: dict, rev: str = "HEAD") -> list[tuple[int, str]]:
    """Every gold source of a question checked at ``rev`` (S4, F3): the path is a file there; a heading is a line of
    it or the stated lines are a span of it; a source cited by lines alone (or by a heading no longer found) holds,
    at ``rev``, the same lines as at the question's own ``commit`` (the source's, else the file's), when one is
    named. Returns (entry number, fault words); the words never quote the file or the question."""
    items = [(n, a) for n, alts in enumerate(entries(data) or [], 1) for a in alts]
    commit = data.get("commit")
    specs = [f"{rev}:{a['path'].removeprefix('./')}" for _, a in items]
    then = [f"{a.get('commit') or commit}:{a['path'].removeprefix('./')}" for _, a in items
            if (a.get("commit") or commit)]
    blobs = cat_file(sorted(set(specs + then)))
    faults = []
    for n, alt in items:
        rel = alt["path"].removeprefix("./")
        if rel.startswith("fixtures/evaluation/"):
            faults.append((n, "a source in the evaluation files"))
            continue
        now = blobs.get(f"{rev}:{rel}")
        if now is None:
            faults.append((n, f"the path is not a file at {rev}"))
            continue
        lines = now.decode("utf-8", "replace").splitlines()
        span = span_of(lines, alt)
        if span is None:
            faults.append((n, f"neither its heading nor its lines resolve at {rev}"))
            continue
        old_rev = alt.get("commit") or commit
        if span[2] == "lines" and old_rev:
            old = blobs.get(f"{old_rev}:{rel}")
            if old is None:
                faults.append((n, "the question's commit does not hold the path"))
                continue
            old_lines = old.decode("utf-8", "replace").splitlines()
            if old_lines[span[0] - 1:span[1]] != lines[span[0] - 1:span[1]]:
                faults.append((n, f"its cited lines at {rev} differ from the question's commit"))
    return faults


def commit_exists(rev: str) -> bool:
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "cat-file", "-e", f"{rev}^{{commit}}"],
                          capture_output=True, timeout=TIMEOUT_S)
    return done.returncode == 0


def normalised(text) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def missing_objects(git_dir: Path, ids: list[str]) -> int | None:
    """How many of ``ids`` the repository at ``git_dir`` does not hold (None when it cannot be asked)."""
    try:
        done = subprocess.run(["git", "-C", str(git_dir), "cat-file", "--batch-check"],
                              input=("\n".join(ids) + "\n").encode(), capture_output=True, timeout=TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    return sum(line.endswith(b" missing") for line in done.stdout.splitlines())


def worktrees() -> list[Path]:
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "worktree", "list", "--porcelain"], capture_output=True,
                          text=True, timeout=TIMEOUT_S)
    return [Path(line[len("worktree "):]) for line in done.stdout.splitlines() if line.startswith("worktree ")]


def trailers(rev: str) -> dict[str, list[str]]:
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "log", "-1", "--format=%(trailers:only,unfold)", rev],
                          capture_output=True, text=True, timeout=TIMEOUT_S)
    found: dict[str, list[str]] = {}
    for line in done.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            found.setdefault(key.strip().lower(), []).append(value.strip())
    return found


def commits_touching(rels: list[str]) -> list[str]:
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "log", "--no-merges", "--format=%H", "HEAD", "--", *rels],
                          capture_output=True, text=True, timeout=TIMEOUT_S)
    return done.stdout.split()
