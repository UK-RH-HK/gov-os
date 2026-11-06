"""W2-134's planted worlds (DAEO-m4rq; DEC-1085 (2), DEC-1084, DEC-820 (d)).

Everything is planted under pytest's ``tmp_path``: a measured root that is a git repository with two commits, a
sets root that is a plain folder (as ``~/gov-os-eval`` is: in no git work tree) holding the path map and the set
``planted``'s question files, and a stand-in ``gov`` that answers ``retrieve`` with chosen evidence. No store, no
model, no network; never this repository's sets, ``~/gov-os-eval`` or ``~/gov-os-runs``. The measure is run as a
command, ``python3 -m gov.retrieval.measure``, from this tree's ``src`` (the runner's own ``PYTHONPATH`` when it has
one, DEC-732).

The question form is the measure's (``question``, ``gold_answer``, ``sources``; a source is ``path`` with
``heading``, ``lines: [first, last]`` and ``commit``; the question may carry its own ``commit``). An evidence item
matches a source when its path equals the source's and its lines overlap the source's span (W2-61's rule).

Commit 1 and commit 2 of the measured root:

- ``docs/moved.md``: the cited block (lines 5-7 at commit 1) moves down by 10 inserted lines (15-17 at commit 2);
  the old lines 5-7 then hold inserted notes;
- ``docs/contract/CONTRACT.md``: the cited block (5-6) moves down by 6 lines (11-12); the capability page
  ``docs/contract/capabilities/CAP-7.md`` holds its text (a family member, W2-61h S7);
- ``docs/steady.md``: the cited block (3-4) stays; lines are appended below it;
- ``docs/zqxw134hidden/gone.md``: the cited block (73-77) is deleted; the file is still 85 lines long, so the stated
  lines still lie in it and hold other text.

The *steady* second commit (S4) moves nothing cited: it only appends lines at the ends of files and adds a file.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SET = "planted"
TIMEOUT_S = 60.0
MARK = "zqxw134hidden"          # every word of the S3 label, its path and its block holds it

MOVED = "docs/moved.md"
STEADY = "docs/steady.md"
GONE = f"docs/{MARK}/gone.md"
CONTRACT = "docs/contract/CONTRACT.md"
CAP7 = "docs/contract/capabilities/CAP-7.md"
OTHER = "docs/other.md"

FAMILIES = {"contract": [CONTRACT, "docs/contract/capabilities/*.md"]}

MOVED_C1 = [
    "# Moved",
    "",
    "The packet rules.",
    "",
    "The ceiling for a packet is six thousand tokens.",    # 5
    "Every packet is checked against the ceiling.",        # 6
    "A packet above the ceiling is split in two.",         # 7
    "",
    "## Tail",
    "The end of the moved file.",
]
MOVED_OLD, MOVED_NEW = (5, 7), (15, 17)

CONTRACT_C1 = [
    "# The Contract",
    "",
    "## CAP-7 Writes",
    "",
    "The guard refuses every write",                       # 5
    "outside the allowed paths of the ticket.",            # 6
    "",
    "## CAP-8 Reads",
    "",
    "Reads are open.",
]
CONTRACT_OLD, CONTRACT_NEW = (5, 6), (11, 12)
CAP7_TEXT = ["# CAP-7 Writes", "", "The guard refuses every write outside the allowed paths of the ticket."]

STEADY_C1 = [
    "# Steady",
    "",
    "The archive is kept read-only.",                      # 3
    "Its copy is kept beside it.",                         # 4
    "",
    "## End",
    "The end.",
]
STEADY_SPAN = (3, 4)

GONE_SPAN = (73, 77)
GONE_C1 = ([f"Filler line {n}." for n in range(1, 73)]
           + [f"{MARK} block line {k}: the retention is ninety days." for k in range(1, 6)]
           + [f"Filler line {n}." for n in range(78, 91)])
OTHER_TEXT = [f"Unrelated line {n}." for n in range(1, 9)]


def files_c1() -> dict[str, list[str]]:
    return {MOVED: MOVED_C1, CONTRACT: CONTRACT_C1, CAP7: CAP7_TEXT, STEADY: STEADY_C1, GONE: GONE_C1,
            OTHER: OTHER_TEXT}


def files_c2_moving() -> dict[str, list[str]]:
    files = files_c1()
    files[MOVED] = MOVED_C1[:3] + [f"Inserted note {n}." for n in range(1, 11)] + MOVED_C1[3:]
    files[CONTRACT] = CONTRACT_C1[:2] + [f"Preamble line {n}." for n in range(1, 7)] + CONTRACT_C1[2:]
    files[STEADY] = STEADY_C1 + [f"Appended line {n}." for n in range(1, 4)]
    files[GONE] = GONE_C1[:72] + GONE_C1[77:]
    return files


def files_c2_steady() -> dict[str, list[str]]:
    files = {rel: lines + [f"Appended line {n}." for n in range(1, 4)] for rel, lines in files_c1().items()}
    files["docs/new.md"] = ["# New", "", "A file added in the second commit."]
    return files


def path_map(families: dict | None = FAMILIES) -> str:
    doc = {"evaluation_sets": {SET: {"visible": ["docs/sets/planted.md"],
                                     "hidden": [f"fixtures/evaluation/{SET}/hidden/**"],
                                     "measures": {"roles": ["engineer"]}}}}
    if families is not None:
        doc["evaluation_families"] = families
    return yaml.safe_dump(doc, sort_keys=False)


GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
           "GIT_AUTHOR_NAME": "W2-134 acceptance", "GIT_AUTHOR_EMAIL": "w2-134@example.invalid",
           "GIT_COMMITTER_NAME": "W2-134 acceptance", "GIT_COMMITTER_EMAIL": "w2-134@example.invalid"}


def git(root: Path, *args: str, when: str = "2026-01-01T00:00:00+00:00") -> str:
    env = {**os.environ, **GIT_ENV, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    done = subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                           "-c", "advice.detachedHead=false", *args],
                          capture_output=True, text=True, timeout=TIMEOUT_S, env=env)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


STAND_IN = """\
#!{python}
# A stand-in gov: answers `retrieve` from responses.json beside it, page by page (by --continue); keeps each answer
# as a run's kept outputs are kept; in trip mode records every call and answers none.
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
conf = json.loads((HERE / "responses.json").read_text())
argv = sys.argv[1:]
with open(HERE / "calls.log", "a") as log:
    log.write(json.dumps(argv) + "\\n")
if argv[:1] == ["--version"]:
    print("stand-in 0")
    sys.exit(0)
if argv[:1] != ["retrieve"] or conf.get("trip"):
    sys.exit(3)
token = argv[argv.index("--continue") + 1] if "--continue" in argv else ""
question = next(a for a in argv[1:] if a in conf["answers"])
page = conf["answers"][question][token]
out = json.dumps({{"ok": True, "result": {{"evidence": page["evidence"], "continuation": page.get("next")}}}})
if conf.get("keep"):
    keep = Path(conf["keep"])
    n = int((keep / ".n").read_text() or 0) + 1
    (keep / ".n").write_text(str(n))
    (keep / f"{{n:05d}}.json").write_text(out + "\\n")
print(out)
"""


class World:
    """A measured root (git, commit 1 then commit 2), a sets root (a plain folder) and a stand-in ``gov``.

    ``in_tree`` puts the question files in the measured root (untracked, so they stay through checkouts) and no
    ``--sets-root`` is passed; otherwise they are in the sets root and ``--sets-root`` names it."""

    def __init__(self, base: Path, second: str = "moving", in_tree: bool = False, families: dict | None = FAMILIES):
        self.base = base
        self.root = base / "root"
        self.sets_root = self.root if in_tree else base / "sets"
        self.in_tree = in_tree
        self.bin = base / "bin"
        self.home = base / "home"
        for folder in (self.root, self.bin, self.home):
            folder.mkdir(parents=True, exist_ok=True)
        git(self.root, "init", "-q", "-b", "main")
        write_lines(self.root / "governance/project/path-map.yaml", path_map(families).splitlines())
        for rel, lines in files_c1().items():
            write_lines(self.root / rel, lines)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "W2-134 fixture: commit 1")
        self.c1 = git(self.root, "rev-parse", "HEAD").strip()
        for rel, lines in (files_c2_moving() if second == "moving" else files_c2_steady()).items():
            write_lines(self.root / rel, lines)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "W2-134 fixture: commit 2", when="2026-01-02T00:00:00+00:00")
        self.c2 = git(self.root, "rev-parse", "HEAD").strip()
        if not in_tree:
            write_lines(self.sets_root / "governance/project/path-map.yaml", path_map(families).splitlines())
            write_lines(self.sets_root / "README.md", ["# The planted sets root"])
        self.answers: dict = {}
        self.gov = self.bin / "gov"
        self.gov.write_text(STAND_IN.format(python=sys.executable), encoding="utf-8")
        self.gov.chmod(0o755)
        self.respond()

    # -- the measured commit ---------------------------------------------------------------------------------------

    def checkout(self, rev: str) -> None:
        git(self.root, "checkout", "-q", rev)
        assert git(self.root, "rev-parse", "HEAD").strip() == rev

    def commit(self, files: dict[str, list[str]], message: str = "W2-134 fixture: another commit") -> str:
        """Write ``files`` into the measured root and commit them on top of HEAD; returns the new commit."""
        for rel, lines in files.items():
            write_lines(self.root / rel, lines)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", message, when="2026-01-03T00:00:00+00:00")
        return git(self.root, "rev-parse", "HEAD").strip()

    def set_sets_families(self, families: dict | None) -> None:
        """Rewrite the sets root's path map only (the measured root's committed path map is left as it is)."""
        assert not self.in_tree
        write_lines(self.sets_root / "governance/project/path-map.yaml", path_map(families).splitlines())

    # -- evidence and questions ------------------------------------------------------------------------------------

    def item(self, rel: str, first: int, last: int, rev: str | None = None) -> dict:
        """An evidence item whose text is the file's own lines ``first`` to ``last`` at ``rev`` (commit 2 when
        none is named)."""
        lines = git(self.root, "show", f"{rev or self.c2}:{rel}").splitlines()
        text = "\n".join(lines[first - 1:last])
        return {"path": rel, "start_line": first, "end_line": last, "text": text,
                "sha256": hashlib.sha256(text.encode()).hexdigest()}

    def question(self, qid: str, sources: list, pages: list[list[dict]], part: str = "visible",
                 commit: str | None = None, text: str | None = None, answer: str = "planted") -> Path:
        """A question file and the pages the stand-in returns for it (each after the first by a continuation)."""
        text = text or f"Planted question {qid}?"
        doc = {"question": text, "gold_answer": answer, "sources": sources}
        if commit:
            doc["commit"] = commit
        path = self.sets_root / "fixtures/evaluation" / SET / part / f"{qid}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        self.answers[text] = {("" if n == 0 else f"c{n}"): {"evidence": page,
                                                              "next": f"c{n + 1}" if n + 1 < len(pages) else None}
                              for n, page in enumerate(pages)}
        self.respond()
        return path

    def respond(self, keep: Path | None = None, trip: bool = False) -> None:
        conf = {"answers": self.answers, "keep": str(keep) if keep else None, "trip": trip}
        (self.bin / "responses.json").write_text(json.dumps(conf), encoding="utf-8")

    def calls(self) -> list[list[str]]:
        log = self.bin / "calls.log"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []

    # -- the measure -----------------------------------------------------------------------------------------------

    def measure(self, *extra: str, part: str = "visible") -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k not in ("GOV_TICKET", "PYTHONPATH", "GOV_ROLE")}
        env.update({"PYTHONPATH": os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src"), "GOV_ROLE": "orchestrator",
                    "HOME": str(self.home), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                    "PYTHONDONTWRITEBYTECODE": "1"})
        argv = [sys.executable, "-m", "gov.retrieval.measure", SET, "--root", str(self.root), "--part", part,
                "--gov", str(self.gov)]
        if not self.in_tree:
            argv += ["--sets-root", str(self.sets_root)]
        return subprocess.run([*argv, *extra], cwd=self.root, env=env, capture_output=True, text=True,
                              timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)

    def run(self, *extra: str, part: str = "visible") -> tuple[dict, str, str]:
        """The measure's record (``--json``), its text, and both runs' stderr."""
        done = self.measure(*extra, "--json", part=part)
        assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
        doc = json.loads(done.stdout)
        text = self.measure(*extra, part=part)
        assert text.returncode == 0, f"the measure failed (exit {text.returncode}): {text.stderr[-2000:]}"
        return doc, text.stdout, done.stderr + "\n" + text.stderr

    # -- the sets root's state -------------------------------------------------------------------------------------

    def label_state(self) -> dict[str, str]:
        """Every path under the sets root (its label files, path map and any other file or folder) with its
        bytes' sha256 (``dir`` for a folder). For an in-tree world: the label folder and the path map only (git
        owns the rest of the measured root)."""
        if self.in_tree:
            roots = [self.root / "fixtures/evaluation", self.root / "governance/project"]
        else:
            roots = [self.sets_root]
        state = {}
        for top in roots:
            for path in [top, *sorted(top.rglob("*"))]:
                rel = str(path.relative_to(self.base))
                state[rel] = "dir" if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()
        return state


# ----------------------------------------------------------------------------------------------------------------------
# Reading the measure's output
# ----------------------------------------------------------------------------------------------------------------------

def by_id(doc: dict) -> dict:
    return {q["id"]: q for q in doc["questions"]}


def figures(q: dict) -> tuple:
    """(hit@5, first gold rank, in the bundle, full evidence, pieces found, pieces needed)."""
    return (q["hit_at_5"], q["first_gold_rank"], q["in_bundle"], q["full_evidence"], q["pieces_found"],
            q["pieces_needed"])


def line_of(text: str, qid: str, part: str = "visible") -> str:
    found = [line for line in text.splitlines() if line.startswith(f"{qid} ({part}): ")]
    assert found, f"no per-question line for {qid} in:\n{text}"
    return found[0]


def total_line(text: str) -> str:
    found = [line for line in text.splitlines() if line.startswith("total: ")]
    assert found, f"no total line in:\n{text}"
    return found[-1]


def first_line(text: str) -> str:
    lines = text.splitlines()
    assert lines, "the measure printed nothing"
    return lines[0]


def names_family_hit(line: str, member: str) -> bool:
    return "famil" in line.lower() and member in line


def names_entry(output: str, qid: str, entry: int) -> bool:
    """A line naming the question by its id and the source by its entry number ("entry 2")."""
    pattern = re.compile(rf"(?<![\w-]){re.escape(qid)}(?![\w-]).*\bentry {entry}\b")
    return any(pattern.search(line) for line in output.splitlines())
