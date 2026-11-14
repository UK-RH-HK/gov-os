"""W2-61h's form tests: shared constants and readers (DAEO-h2k3; DEC-1055 (4), DEC-1052 G-3, DEC-820 (d), DEC-1069).

The new memory questions: ``q21.yaml`` to ``q24.yaml`` in this tree's visible folder (the first 28's draw), and the
hidden 40 (DEC-1069 (4): W2-61h's 24 and the operator's 16) in the hidden folder of the sets root outside every
worktree, named by ``GOV_EVAL_SETS_ROOT`` (absent: every hidden case skips). The question form is
``src/gov/retrieval/measure.py``'s docstring and loader: ``question``, ``gold_answer`` and ``sources`` required; a
source is a map with ``path`` and optionally ``heading``, ``lines: [first, last]`` and ``commit``, or a list of such
maps (alternatives). Comments (a ``# volatile:`` line, RUBRIC.md R11) are no part of the form.

Nothing here prints a hidden question, answer, category or gold path: the readers return faults as short words, and
the hidden cases name a file by its file name only (S5, DEC-820 (d)).
"""

from __future__ import annotations

import hashlib
import os
import pwd
import re
import subprocess
import warnings
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SET = "memory-retrieval"
PATH_MAP_REL = "governance/project/path-map.yaml"
VISIBLE = REPO_ROOT / "fixtures/evaluation" / SET / "visible"
HIDDEN_REL = f"fixtures/evaluation/{SET}/hidden"
NEW_VISIBLE = ("q21.yaml", "q22.yaml", "q23.yaml", "q24.yaml")
LENS_B = tuple(f"q{n:02d}.yaml" for n in range(1, 21))
# The hidden half as DEC-1069 (4) sets it, W2-61h's 24 (h01-h24) and the operator's 16 (h25-h40), less h10: DEC-1171 (2)
# retired h10 (moved to retired-hidden/ by the owner's operator), so the half holds 39 until the walled writer's
# replacement question lands and brings it back to 40 (revise this count then).
HIDDEN_COUNT = 39
SETS_ROOT_VAR = "GOV_EVAL_SETS_ROOT"
TICKET = "DAEO-h2k3"
TIMEOUT_S = 60.0

# S3's spread of the first 28 new questions, by the category labels the writer's draw used (recorded in the README).
# "A plan, ticket or path-map fact" takes any of its three labels. It still judges q21-q24, the draw's visible share.
SPREAD = {
    "decision": 5, "exact-string": 4, "callers": 4, "code-paraphrase": 3, "kernel-template": 3,
    "multi-file": 3, "history": 2, "failure-memory": 2, "plan-ticket-path-map": 1, "nonexistent-id": 1,
}
LABELS = {**{name: name for name in SPREAD if name != "plan-ticket-path-map"},
          "plan": "plan-ticket-path-map", "ticket": "plan-ticket-path-map", "path-map": "plan-ticket-path-map"}

# DEC-1069 (5): S3's quotas amended to fit R5, for a 40-question half (RUBRIC.md, version 2, R5 item 6's table):
# each `category` value and its "at least"; the twelve sum to 40. Less h10's retired place (R5_RETIRED below) the
# half's minimums sum to 39, as HIDDEN_COUNT does; the floors S3 applies are lower still by the accepted shortfall
# (R5_SHORT below).
R5_QUOTAS = {
    "decision": 6, "contract": 4, "plan": 4, "ticket": 4, "exact-string": 4, "callers": 4, "code-paraphrase": 3,
    "kernel-template": 3, "multi-file": 3, "failure-memory": 3, "history": 1, "nonexistent-id": 1,
}
# The owner's accepted shortfall (DEC-1069; the operator's note on ACT-HNEW-1): the hidden 40 end one short in these
# three categories. No other category may fall short, and none of these by more than one.
R5_SHORT = {"decision": 1, "callers": 1, "code-paraphrase": 1}
# DEC-1171 (2), the owner's option (b) (DEC-1175, to be recorded): h10 is retired from the hidden half, and its R5
# category is callers (given by the owner's operator from h10's retirement reason line). The callers floor drops by
# one more with the count: it is two short of R5's minimum (R5_SHORT's one and this one). Floors: callers 4 - 1 - 1
# = 2, decision 6 - 1 = 5, code-paraphrase 3 - 1 = 2, every other category at its full minimum (the floors sum to
# 40 - 3 - 1 = 36, within the half's 39 files).
R5_RETIRED = {"callers": 1}


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


def form_faults(data, labels=LABELS, named: str = "S3's ten") -> list[str]:
    """The question form's faults, as fixed words only. ``labels`` are the category values allowed (S3's ten for
    q21-q24, R5's twelve for the hidden 40). Comments are no part of the form: a ``# volatile: ...`` line (R11) is
    ignored, as the measure's YAML loader ignores it."""
    if data is None:
        return ["not a YAML map"]
    faults = []
    if not (isinstance(data.get("question"), str) and data["question"].strip()):
        faults.append("no question")
    if not (isinstance(data.get("gold_answer"), str) and data["gold_answer"].strip()):
        faults.append("no gold_answer")
    if entries(data) is None:
        faults.append("sources is not a non-empty list of maps with a path")
    if "category" in data and data["category"] not in labels:
        faults.append(f"a category outside {named}")
    if "category" not in data:
        faults.append("no category")
    return faults


def commit_faults(data: dict) -> list[str]:
    """The commits a question names (R10 item 2): its own ``commit``, or one on every source alternative (the
    operator's form, ACT-HNEW-1); every commit named, the question's or a source's, a commit of this repository.
    Fixed words only."""
    alts = [a for alts in entries(data) or [] for a in alts]
    if not (data.get("commit") or (alts and all(a.get("commit") for a in alts))):
        return ["names no commit, neither its own nor one on every source"]
    named = {str(c) for c in [data.get("commit"), *(a.get("commit") for a in alts)] if c}
    return ["names a commit this repository does not hold"] if not all(commit_exists(c) for c in named) else []


def cat_file(specs: list[str], root: Path = REPO_ROOT) -> dict[str, bytes | None]:
    """``git cat-file --batch`` over ``<rev>:<path>`` specs in the repository at ``root`` (default this one): each
    spec's bytes, or None when it is no blob."""
    if not specs:
        return {}
    done = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"],
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


def own_commit(data: dict, alt: dict) -> str | None:
    """A source alternative's own commit (DEC-1178 (1)): its ``commit``, else the question's; None when neither."""
    return str(alt.get("commit") or data.get("commit") or "").strip() or None


def span_text_own(data: dict, root: Path = REPO_ROOT, rev: str = "HEAD") -> list[list[str]]:
    """Each entry's resolved text, one string per alternative ('' when it does not resolve), read at the source's own
    commit (``rev`` only for a source that names none): the span the designer's anchors are judged on (S4, F3)."""
    items = [(a, own_commit(data, a) or rev) for alts in entries(data) or [] for a in alts]
    blobs = cat_file([f"{at}:{a['path'].removeprefix('./')}" for a, at in items], root)
    out, i = [], 0
    for alts in entries(data) or []:
        texts = []
        for a in alts:
            at = items[i][1]
            i += 1
            blob = blobs.get(f"{at}:{a['path'].removeprefix('./')}")
            lines = blob.decode("utf-8", "replace").splitlines() if blob is not None else []
            span = span_of(lines, a) if blob is not None else None
            texts.append("\n".join(lines[span[0] - 1:span[1]]) if span else "")
        out.append(texts)
    return out


def _heading_found(lines: list[str], heading) -> bool:
    return any(line.rstrip() == str(heading).rstrip() for line in lines)


def _text_of(lines: list[str], source: dict) -> list[str]:
    """A cited span's text for comparison (DEC-1180 (1)): the lines ``span_of`` resolves, each with its trailing
    whitespace stripped, and the span's trailing blank lines dropped. Trailing whitespace is invisible to a reader and
    to the measure's own heading match (which strips it); a trailing blank line is a separator, not content, and a
    section moved to the end of a file loses it. Any other difference (a word, a line added or removed, a blank line
    inside) is a difference. No span: an empty text."""
    span = span_of(lines, source)
    text = [line.rstrip() for line in lines[span[0] - 1:span[1]]] if span else []
    while text and not text[-1]:
        text.pop()
    return text


def judge_sources(data: dict, root: Path = REPO_ROOT, rev: str = "HEAD") -> tuple[list[tuple[int, str]], list[int]]:
    """Every gold source of a question, judged at its own commit (DEC-1178 (1), DEC-1180 (1), (4); S4, F3). Returns
    ``(faults, changed)``: ``faults`` are ``(entry number, words)`` for a source that does not hold its answer where
    it was written (it is red); ``changed`` are the entry numbers whose cited block or section changed at ``rev``
    (listed, never red; each entry once, however many of its alternatives changed). The words never quote the file or
    the question.

    Red: the source is in the evaluation files; its path is not a file at its own commit (its ``commit``, else the
    question's); its heading or lines are no span there (``span_of``, the measure's rule). A source that names no
    commit at all is judged at ``rev`` instead, and cannot be listed.

    Listed, at ``rev``, for a source that holds its answer at its own commit: the path is no longer a file; or the
    heading is still a line of the file and the section it governs (``span_of`` at ``rev``: to the next heading of the
    same or a higher level, or the end of the file; a heading that is not a ``#`` heading spans the stated width) has
    different text from the section at its own commit (``_text_of``), wherever the section now sits (DEC-1180 (1),
    N2 (b)); or the heading is no longer a line of the file and no lines are stated; or, for lines (the heading absent
    or not cited), the block, the stated lines of the file at its own commit, is found nowhere at ``rev`` or more than
    once away from its stated lines. A block that moved unchanged (the same lines, or exactly one other place: the
    measure's and ``repin_gold.py``'s re-anchor) and a section that moved unchanged are no fault and are not listed.
    A source cited by a path alone is the whole file and is not listed while the file stands."""
    items = [(n, a) for n, alts in enumerate(entries(data) or [], 1) for a in alts]
    specs = [f"{rev}:{a['path'].removeprefix('./')}" for _, a in items]
    then = [f"{own_commit(data, a)}:{a['path'].removeprefix('./')}" for _, a in items if own_commit(data, a)]
    blobs = cat_file(sorted(set(specs + then)), root)
    faults, changed = [], []

    def list_entry(n: int) -> None:
        if n not in changed:            # an entry is listed once, however many of its alternatives changed (N1)
            changed.append(n)

    for n, alt in items:
        rel = alt["path"].removeprefix("./")
        if rel.startswith("fixtures/evaluation/"):
            faults.append((n, "a source in the evaluation files"))
            continue
        own = own_commit(data, alt)
        now = blobs.get(f"{rev}:{rel}")
        old = blobs.get(f"{own}:{rel}") if own else now
        where = "its own commit" if own else rev
        if old is None:
            faults.append((n, f"the path is not a file at {where}"))
            continue
        old_lines = old.decode("utf-8", "replace").splitlines()
        if span_of(old_lines, alt) is None:
            faults.append((n, f"neither its heading nor its lines resolve at {where}"))
            continue
        if not own:
            continue
        if now is None:
            list_entry(n)
            continue
        now_lines = now.decode("utf-8", "replace").splitlines()
        heading, stated = alt.get("heading"), alt.get("lines")
        if heading is not None and _heading_found(now_lines, heading):
            if _text_of(old_lines, alt) != _text_of(now_lines, alt):    # N2 (b): the section's text changed
                list_entry(n)
            continue
        if stated is None:
            if heading is not None:
                list_entry(n)
            continue
        first, last = stated
        if last > len(old_lines):
            list_entry(n)
            continue
        block = old_lines[first - 1:last]
        if now_lines[first - 1:last] == block:
            continue
        width = len(block)
        if sum(now_lines[i:i + width] == block for i in range(len(now_lines) - width + 1)) != 1:
            list_entry(n)
    return faults, changed


def judge_all(named: dict[str, dict], root: Path = REPO_ROOT) -> tuple[list[str], list[str]]:
    """``judge_sources`` over question files by name: ``(faults, changed)`` as lines naming the file and the entry
    number only: ``"<file>: source entry <n>: <words>"`` and ``"<file> entry <n>"``."""
    faults, changed = [], []
    for name, data in named.items():
        red, listed = judge_sources(data, root)
        faults += [f"{name}: source entry {n}: {why}" for n, why in red]
        changed += [f"{name} entry {n}" for n in listed]
    return faults, changed


class GoldBlockChanged(UserWarning):
    """The maintenance list (DEC-1178 (1), DEC-1180 (1)): gold blocks or sections that changed at HEAD, named by file
    and entry only."""


def notify_changed(changed: list[str]) -> None:
    """Show the list in the run's own output: a ``GoldBlockChanged`` warning, which pytest's default summary prints
    for a passing run (no flag, no file written). Nothing is shown when the list is empty. Under ``-W error`` the
    warning would raise, so the list is printed instead: the check never fails for it."""
    if not changed:
        return
    message = (f"W2-61h S4 maintenance list (DEC-1178 (1), DEC-1180 (1)): {len(changed)} cited block(s) or "
               f"section(s) changed at HEAD, for the walled writer: " + "; ".join(changed))
    try:
        warnings.warn(message, GoldBlockChanged, stacklevel=2)
    except GoldBlockChanged:
        print(message)


def commit_exists(rev: str, root: Path = REPO_ROOT) -> bool:
    done = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{rev}^{{commit}}"],
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
