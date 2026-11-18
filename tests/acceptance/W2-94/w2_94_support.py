"""Support code for the W2-94 acceptance tests (standard library and PyYAML only).

W2-94 is EXAMIN's question set (DEC-957, DEC-954, DEC-828 items 3 and 4, DEC-820, DEC-845). The set itself is written by a
walled writer and is never read by the pair that builds the check (ticket DAEO-g87r, S1 to S5, F1 to F3). These tests
cover its **form only**: every case runs on a stand-in that this module plants under pytest's ``tmp_path``, with made-up
text about made-up files. Nothing under ``~/gov-os-eval``, ``~/gov-os-runs``, any ``hidden`` folder of a real tree or any
``fixtures/evaluation/examin/`` folder of this tree is opened, and no real question or answer is written anywhere.

**The program under test** is ``fixtures/evaluation/examin/check_gold.py``, run as a process:
``python3 check_gold.py --sets-root <root> --copy <launch clone> [--set examin]``. ``W2_94_CHECK_GOLD`` names another
file to run in its place (the planted-break runs in the README).

**The planted sets root**: ``<root>/fixtures/evaluation/examin/{hidden, hidden/visible, visible}`` with ``qNN.yaml``,
``DRAW.txt`` and ``.release-visible.record`` in the forms of the approved writer brief (sections 5 to 7) and of the
owner's release step (``release_visible.sh``). ``build`` makes a good set of any count from 9 to 21: pairs of questions
of the first categories, drawn by the brief's rule, plus one extra question when the count is odd.

**The planted copy** (the CTO's launch clone): a temporary git repository whose first commit holds the made-up files the
questions cite, and whose second, the scaffold commit, adds ``governance/project/indep-walls/COPY-HEAD.txt`` naming the
first. Planted beside the good files: a file that exists only in the scaffold commit, one that exists only in the working
tree, one whose text changed in the scaffold commit, a binary file, and a scaffold-named path that the first commit also
holds.

**Planted words** begin with ``zqxw94``: one in every planted question, answer, heading and source path, so an output can
be searched for them.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_REL = "fixtures/evaluation/examin/check_gold.py"
SCRIPT = Path(os.environ.get("W2_94_CHECK_GOLD") or REPO_ROOT / SCRIPT_REL)
CLOSE_RECORD = Path(os.environ.get("W2_94_CLOSE_RECORD")
                    or REPO_ROOT / "governance/project/orchestration/closes/W2-61-DAEO-iw1f.md")
TIMEOUT_S = 120.0

SET = "examin"
SET_REL = f"fixtures/evaluation/{SET}"
WORD = "zqxw94"
CATEGORIES = ("code-location", "code-paraphrase", "callers", "exact-string", "config-build-test", "governance-rule",
              "spec-or-decision", "multi-file", "history-or-lesson", "nonexistent")
REQUIRED = ("id", "question", "gold_answer", "sources", "commit", "category", "drawn")
COPY_HEAD_REL = "governance/project/indep-walls/COPY-HEAD.txt"
SCAFFOLD_MAP = "governance/project/path-map.yaml"
SCAFFOLD_NOTE = "governance/project/indep-walls/zqxw94scaffold.md"

GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(directory, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_ENV)
    done = subprocess.run(["git", "-C", str(directory), "-c", "user.name=W2-94 acceptance",
                           "-c", "user.email=w2-94@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=TIMEOUT_S, env=env)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# The planted copy
# --------------------------------------------------------------------------

def source_lines(i):
    """The planted source file of question ``i``: the heading is line 3, the answer is on lines 4 and 5."""
    return [
        f"# Zqxw94 document {i:02d}",
        "",
        f"## {WORD}heading{i:02d}",
        f"The routine {WORD}func{i:02d}_run reads the {WORD}conf{i:02d} value.",
        f"It returns {WORD}ans{i:02d} to its caller.",
        "",
        f"## Other {WORD} part",
        "Unrelated filler about the weather and nothing else.",
    ]


def source_path(i):
    return f"docs/{WORD}src{i:02d}.md"


OTHER = f"docs/{WORD}other.md"                  # a made-up file that holds no planted answer
CHANGED = f"docs/{WORD}changed.md"              # 3 lines at the copy's commit, 10 lines (and a token) after it
CHANGED_LATE_TOKEN = f"{WORD}late_token"
SCAFFOLD_ONLY = f"docs/{WORD}scaffoldonly.md"   # exists only in the scaffold commit
WORKTREE_ONLY = f"docs/{WORD}worktree.md"       # exists only in the copy's working tree, untracked
BINARY = f"docs/{WORD}blob.bin"
def ghost(i):
    """The asked name of the planted nonexistent question number ``i``: it exists nowhere in the copy."""
    return f"{WORD}ghost{i:02d}_fn"


GHOST_HOLDER = f"src/{WORD}/ghost_holder.py"    # a file that would hold the name if it existed
LOCATOR = f"src/{WORD}/real_module.py"          # a real file a nonexistent question may point at


def copy_files():
    files = {source_path(i): "\n".join(source_lines(i)) + "\n" for i in range(1, 25)}
    files[OTHER] = "\n".join(f"Filler line {n} of nothing in particular." for n in range(1, 9)) + "\n"
    files[CHANGED] = "alpha\nbeta\ngamma\n"
    files[BINARY] = b"\x00\x01\x02 binary \xff\xfe\x00"
    files[GHOST_HOLDER] = "def holder():\n    return 1\n\n\ndef other_holder():\n    return 2\n"
    files[LOCATOR] = "def real_function():\n    return 3\n"
    files[SCAFFOLD_MAP] = "# a stand-in path map that the copy's own commit holds\n" + "\n".join(f"# {n}" for n in range(8)) + "\n"
    files["README.md"] = "# The stand-in copy\n"
    return files


def scaffold_files(copy_head):
    return {
        COPY_HEAD_REL: copy_head + "\n" if copy_head else None,
        SCAFFOLD_NOTE: "\n".join(f"scaffold line {n} {WORD}scaffoldword" for n in range(1, 9)) + "\n",
        SCAFFOLD_ONLY: "\n".join(source_lines(5)) + "\n",
        CHANGED: "\n".join(["alpha", "beta", "gamma"] + [f"later line {n}" for n in range(4, 10)]
                           + [f"the {CHANGED_LATE_TOKEN} is only here"]) + "\n",
    }


def make_copy(path, copy_head="auto", extra_copy=None, extra_worktree=None):
    """The launch clone: one commit of the made-up files, then one scaffold commit. Returns (path, commit).
    ``copy_head``: ``"auto"`` (the first commit's id), ``None`` (no COPY-HEAD.txt), or the exact text to write."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    for rel, text in {**copy_files(), **(extra_copy or {})}.items():
        write(path / rel, text)
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "the copy's commit")
    commit = git(path, "rev-parse", "HEAD").strip()
    for rel, text in scaffold_files(commit if copy_head == "auto" else copy_head).items():
        if text is not None:
            write(path / rel, text)
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "the scaffold commit")
    write(path / WORKTREE_ONLY, "\n".join(source_lines(5)) + "\n")
    for rel, text in (extra_worktree or {}).items():
        write(path / rel, text)
    return path, commit


# --------------------------------------------------------------------------
# The planted set
# --------------------------------------------------------------------------

def good_question(qid, i, category, commit, **changes):
    """One well-formed planted question (number ``i`` names its source file)."""
    if category == "nonexistent":
        data = {"id": qid, "question": f"Where is `{ghost(i)}` defined?", "gold_answer": "None: no such name exists.",
                "sources": [{"path": GHOST_HOLDER, "lines": [1, 6]}], "commit": commit, "category": category,
                "drawn": "none"}
    else:
        data = {"id": qid, "question": f"How does {WORD}qword{i:02d} work in the {WORD} project?",
                "gold_answer": f"The routine `{WORD}func{i:02d}_run` returns {WORD}ans{i:02d}.",
                "sources": [{"path": source_path(i), "heading": f"## {WORD}heading{i:02d}", "lines": [3, 5]}],
                "commit": commit, "category": category, "drawn": "sample"}
    data.update(changes)
    return data


def draw_value(seed, k):
    return seed + k


def draw_halves(k, seed):
    """The brief's rule: an even SEED+k sends q<2k-1> to the visible half, an odd one q<2k>."""
    first, second = f"q{2 * k - 1:02d}", f"q{2 * k:02d}"
    return (first, second) if draw_value(seed, k) % 2 == 0 else (second, first)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


@dataclass
class World:
    base: Path
    root: Path           # the sets root
    copy: Path
    home: Path
    commit: str
    seed: int
    count: int
    cats: dict = field(default_factory=dict)       # id -> category
    visible_ids: list = field(default_factory=list)
    hidden_ids: list = field(default_factory=list)

    @property
    def set_dir(self):
        return self.root / SET_REL

    @property
    def hidden_dir(self):
        return self.set_dir / "hidden"

    @property
    def dev_dir(self):
        return self.hidden_dir / "visible"

    @property
    def released_dir(self):
        return self.set_dir / "visible"

    @property
    def record(self):
        return self.set_dir / ".release-visible.record"

    @property
    def draw(self):
        return self.hidden_dir / "DRAW.txt"

    def qpath(self, qid):
        for folder in (self.hidden_dir, self.dev_dir):
            if (folder / f"{qid}.yaml").is_file():
                return folder / f"{qid}.yaml"
        raise AssertionError(f"no planted file for {qid}")

    def load(self, qid):
        return yaml.safe_load(self.qpath(qid).read_text(encoding="utf-8"))

    def save(self, qid, data):
        self.qpath(qid).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def edit(self, qid, change):
        data = self.load(qid)
        change(data)
        self.save(qid, data)

    def source(self, qid, **changes):
        """Change the first source of a question (a plain source mapping)."""
        self.edit(qid, lambda d: d["sources"][0].update(changes))

    def drop(self, qid, key):
        self.edit(qid, lambda d: d.pop(key))

    def move_half(self, qid):
        """Move a question's file to the other half (the draw text is left as it was)."""
        path = self.qpath(qid)
        target = (self.hidden_dir if path.parent == self.dev_dir else self.dev_dir) / path.name
        shutil.move(str(path), str(target))

    def draw_lines(self):
        return self.draw.read_text(encoding="utf-8").splitlines()

    def set_draw_lines(self, lines):
        self.draw.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def release(self):
        """The owner's release step: copy hidden/visible/ into visible/, and the record (name, sha256)."""
        self.released_dir.mkdir(parents=True, exist_ok=True)
        rows = []
        for path in sorted(self.dev_dir.glob("q*.yaml")):
            shutil.copy2(path, self.released_dir / path.name)
            rows.append(f"{path.name} {sha256_bytes(path.read_bytes())}")
        self.record.write_text("\n".join(rows) + "\n", encoding="utf-8")

    def rerelease(self):
        """The release step run again after the development half changed (a test-only helper: the real step refuses a
        second release): the same copy and record, rebuilt from the half as it now is."""
        shutil.rmtree(self.released_dir, ignore_errors=True)
        self.record.unlink(missing_ok=True)
        self.release()

    def snapshot(self):
        """Every file and folder under the base (the copy's git folder included): kind, size and mtime."""
        found = {}
        for path in sorted(self.base.rglob("*")):
            stat = path.lstat()
            found[str(path)] = (path.is_dir(), stat.st_size, stat.st_mtime_ns)
        return found


def build(tmp_path, count=20, seed=20260901, release=True, copy_head="auto", extra_copy=None, extra_worktree=None):
    """A good planted set of ``count`` questions (9 to 21: ``count // 2`` pairs of the first categories drawn by the
    brief's rule, and one extra code-location question in the measured half when the count is odd), its sets root, its
    copy, the draw and (``release``) the released development half."""
    base = Path(tmp_path).resolve()
    copy, commit = make_copy(base / "launch-clone", copy_head, extra_copy, extra_worktree)
    root, home = base / "sets-root", base / "home"
    home.mkdir(parents=True, exist_ok=True)
    world = World(base, root, copy, home, commit, seed, count)
    world.dev_dir.mkdir(parents=True)
    pairs = count // 2
    draw_rows = []
    for k in range(1, pairs + 1):
        category = CATEGORIES[k - 1]
        visible, hidden = draw_halves(k, seed)
        for qid, folder in ((visible, world.dev_dir), (hidden, world.hidden_dir)):
            i = int(qid[1:])
            write(folder / f"{qid}.yaml", yaml.safe_dump(good_question(qid, i, category, commit), sort_keys=False))
            world.cats[qid] = category
        world.visible_ids.append(visible)
        world.hidden_ids.append(hidden)
        value = draw_value(seed, k)
        draw_rows.append(f"{k} {category} SEED+{k}={value} {'even' if value % 2 == 0 else 'odd'} "
                         f"visible={visible} hidden={hidden}")
    if count % 2:
        qid = f"q{count:02d}"
        write(world.hidden_dir / f"{qid}.yaml",
              yaml.safe_dump(good_question(qid, count, CATEGORIES[0], commit), sort_keys=False))
        world.cats[qid] = CATEGORIES[0]
        world.hidden_ids.append(qid)
    write(world.draw, "\n".join(draw_rows) + "\n")
    if release:
        world.release()
    return world


# --------------------------------------------------------------------------
# Running the program
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    @property
    def lines(self):
        return self.stdout.splitlines()

    def describe(self):
        return (f"{' '.join(map(str, self.args))}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-2000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")


def run_check(world, *, sets_root=None, copy=None, extra=(), script=None, drop=()):
    """Run the program on a planted world. ``sets_root`` and ``copy`` replace the world's own; ``drop`` names flags to
    leave out (``--sets-root``, ``--copy``)."""
    argv = [sys.executable, str(script or SCRIPT)]
    if "--sets-root" not in drop:
        argv += ["--sets-root", str(sets_root if sets_root is not None else world.root)]
    if "--copy" not in drop:
        argv += ["--copy", str(copy if copy is not None else world.copy)]
    argv += list(extra)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(world.home), LC_ALL="C.UTF-8", PYTHONDONTWRITEBYTECODE="1")
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT_S, env=env, cwd=str(world.base),
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the check did not end within {TIMEOUT_S:.0f} s: {argv}") from None
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr)


# --------------------------------------------------------------------------
# What every output must look like (counts and ids only)
# --------------------------------------------------------------------------

LINE_SHAPES = (
    re.compile(r"\d+ questions \(\d+ visible, \d+ hidden\); draw (ok|FAIL); release (ok|FAIL|pending)\Z"),
    re.compile(r"\d+ of \d+ hold\Z"),
    re.compile(r"FAIL (q\d\d|draw|release|set) [A-Z_]+( (q\d\d|k\d+))*\Z"),
    re.compile(r"REFUSED [A-Z_]+( q\d\d)?\Z"),
)


def shape_faults(run):
    """Lines of the output that are not one of the four counts-and-ids shapes, and anything on stderr."""
    faults = [line for line in run.lines if not any(shape.match(line) for shape in LINE_SHAPES)]
    if run.stderr.strip():
        faults.append("<stderr is not empty>")
    return faults


def planted_hits(run, world=None):
    """Planted words an output shows: the ``zqxw94`` prefix, a source path, a question or answer phrase."""
    needles = [WORD, "Zqxw94", "routine", "caller", "project work", "docs/", ".md", ".yaml", "gold_answer",
               "question:", str(world.base) if world else None]
    return [needle for needle in needles if needle and needle in run.output]


def codes(run):
    """The words of every FAIL line (without ``FAIL``: ``("q07", "SPAN_OUT_OF_FILE")``, ``("draw", "HALVES_UNBALANCED")``,
    ``("release", "VISIBLE_BYTES_DIFFER", "q03")``) and of every REFUSED line (``("REFUSED", "FIELD_MISSING", "q07")``)."""
    found = []
    for line in run.lines:
        words = tuple(line.split())
        if words[:1] == ("FAIL",):
            found.append(words[1:])
        elif words[:1] == ("REFUSED",):
            found.append(words)
    return found


def has(run, *prefix):
    """True when some FAIL or REFUSED line of the output begins with ``prefix`` (see ``codes``)."""
    return any(words[:len(prefix)] == tuple(prefix) for words in codes(run))


def question_failures(run):
    """The ids that have a FAIL line, each with its reason code: ``{"q07": "SPAN_OUT_OF_FILE"}``."""
    return {words[0]: words[1] for words in codes(run) if re.fullmatch(r"q\d\d", words[0])}


# --------------------------------------------------------------------------
# The guard (F1): the live hook, driven as W2-149's tests drive it
# --------------------------------------------------------------------------

