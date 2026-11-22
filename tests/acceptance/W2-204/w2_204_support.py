"""W2-204's planted second repository ("Second Harbour"): its own domains, categories, quotas, subsystems (two by the
record key ``feature``, one by path), its own control set, a sets root, a pinned fake ``gov``, a fake ``claude``, a
rebuild stub and a transcripts folder. Everything lies under pytest's temporary folder; every child gets a planted
``HOME`` and this tree's ``src/`` first on ``PYTHONPATH``; no child ever sees ``MEMAUDIT_CONFIG`` unless a case
passes it (``World.run`` drops it from the child's environment; the folder's conftest from the test's).

W2-171's helpers are imported by path and never edited: its ``child_env``, ``git``, ``install_script``, ``snapshot``,
``Run``, the planted register, the fake ``gov`` and ``claude`` and the scenario's ``calls_for``.

The tool is driven only as an adopter drives it: ``python3 -m gov.cli.main memaudit <step>`` (``gov memaudit``) or
``python3 -m gov.memaudit <step>``, as child processes. ``gov.memaudit`` is never imported at collection.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SRC = TREE / "src"
ACCEPT = HERE.parent
sys.path.insert(0, str(ACCEPT / "W2-171"))  # W2-171's helpers: imported, never changed

import w2_171_scenario as S171  # noqa: E402
import w2_171_world as W171  # noqa: E402

GOV_OS_CONFIG = TREE / "governance" / "project" / "memory-audit.yaml"
CONFIG_REL = "governance/project/memory-audit.yaml"
MISSING_LINE = "MA-CONFIG-MISSING write governance/project/memory-audit.yaml"
ENTRIES = {"module": [sys.executable, "-m", "gov.memaudit"],
           "cli": [sys.executable, "-m", "gov.cli.main", "memaudit"]}
STEPS = ("preflight", "void", "declare", "measure", "judge", "brief", "check", "fresh")
PIN = "pin-0123456789ab"
TAG = "20261119"


def audits(tag: str = TAG) -> tuple[str, str]:
    """The visible and the hidden half's names of a tag ``YYYYMMDD[b-z]`` (S8)."""
    k = 0 if len(tag) == 8 else ord(tag[8]) - ord("a")
    return f"memory-audit-{tag[2:8]}{2 * k + 1:02d}", f"memory-audit-{tag[2:8]}{2 * k + 2:02d}"


VISIBLE, HIDDEN = audits()
HALVES = ((VISIBLE, "v"), (HIDDEN, "h"))

# -- the second repository's configuration ------------------------------------------------------------------------
REPOSITORY = "Second Harbour"
CATEGORIES = [
    ("decision", 6, "a decision of the harbour board or what replaced it"),
    ("harbour-task", 4, "a task record and what it asks for"),
    ("berth-spec", 4, "a berth specification and its rules"),
    ("tide-scenario", 3, "a scenario of a specification"),
    ("pilot-report", 3, "a pilot's report and its finding"),
    ("exact-string", 4, "an exact name, id or message, with its file"),
    ("callers", 4, "callers, callees and definitions"),
    ("code-paraphrase", 4, "a code fact asked in other words"),
    ("multi-file", 3, "an answer that needs two or more files"),
    ("failure-memory", 3, "a lesson of a failed mooring"),
    ("history", 1, "why or when something changed"),
    ("nonexistent-id", 1, "an id that exists nowhere"),
]
CATEGORY_NAMES = [name for name, _, _ in CATEGORIES]
DOMAINS = [("decisions", ["records/decisions.md"]), ("harbour-tasks", ["records/tasks/**"]),
           ("berth-specs", ["records/specs/**"]), ("pilot-reports", ["records/reports/**"]), ("code", ["app/**"])]
DOMAIN_NAMES = [name for name, _ in DOMAINS]
SUBSYSTEM_NAMES = ["capture-flow", "review-flow", "tide-engine"]
CONTROL_SET, CONTROL_N = "second-control", 24
EXCLUDED = "archive/**"
# the names of Gov OS's own tables that the second repository's file does not hold
GOV_OS_ONLY_CATEGORIES = ("contract", "plan", "ticket", "kernel-template")
GOV_OS_ONLY_DOMAINS = ("tickets", "plan", "contract")


def config_doc(**over) -> dict:
    """The second repository's ``memory-audit.yaml`` as a mapping (``over`` replaces top-level keys)."""
    doc = {
        "version": 1, "repository": REPOSITORY, "half_size": 40,
        "categories": [{"name": n, "count": c, "about": a} for n, c, a in CATEGORIES],
        "domains": [{"name": n, "paths": list(p)} for n, p in DOMAINS],
        "subsystems": [{"name": "capture-flow", "record_key": "feature", "values": ["F01"]},
                       {"name": "review-flow", "record_key": "feature", "values": ["F02"]},
                       {"name": "tide-engine", "paths": ["app/engine/**"]}],
        "spread": {"domain_min": 4, "subsystem_max": 10},
        "exclude": [EXCLUDED],
        "control": {"set": CONTROL_SET, "part": "visible", "size": CONTROL_N, "baseline": "first", "spread": 2},
    }
    doc.update(copy.deepcopy(over))
    return doc


def config_text(doc: dict | None = None) -> str:
    return yaml.safe_dump(doc if doc is not None else config_doc(), sort_keys=False, allow_unicode=True)


# -- the planted words: each lives in one question, gold answer, answer or note only (F3) ----------------------------
_ABC = "abcdefghijklmnopqrstuvwxyz"
QWORD, GWORD, AWORD, NWORD = "quorblat", "gildenfrum", "brindlewex", "snarkelwump"


def _letters(n: int) -> str:
    return _ABC[n // 26] + _ABC[n % 26]


def qword(half: str, n: int) -> str:
    return f"{QWORD}{half}{_letters(n)}"


def gword(half: str, n: int) -> str:
    return f"{GWORD}{half}{_letters(n)}"


def planted_words(half: str | None = None) -> tuple[str, ...]:
    """The stems of every planted word (of one half when given): none may reach a line or a file outside the set, the
    audit's run folder and a brief's own folder."""
    if half is None:
        return (QWORD, GWORD, AWORD, NWORD)
    return (f"{QWORD}{half}", f"{GWORD}{half}", f"{AWORD}{half}", f"{NWORD}{half}")


# -- the repository's files ----------------------------------------------------------------------------------------
FEATURES = {"records/tasks/T-07.md": "F01", "records/tasks/T-08.md": "F01", "records/tasks/T-09.md": "F02",
            "records/tasks/T-10.md": "F02", "records/specs/S-11.md": "F01", "records/specs/S-12.md": "F01",
            "records/specs/S-13.md": "F02", "records/specs/S-14.md": "F02",
            "records/reports/R-18.md": "F09"}  # F09 is in no subsystem row: it counts none
SPARE_F01 = [f"records/tasks/T-9{k}.md" for k in range(1, 8)]   # seven more records of feature F01
SPARE_CODE = [f"app/core/x{k}.py" for k in range(1, 5)]
FEATURES.update({path: "F01" for path in SPARE_F01})
CONTROL_FILES = [f"records/ctl/c{k:02d}.md" for k in range(1, CONTROL_N + 1)]
REGISTER_REL = "records/decisions.md"
LATE_FILE = "records/late.md"
CHANGED = ("records/tasks/T-07.md", "app/engine/e21.py", "archive/old.md")
LAYOUT = [c for c, count, _ in CATEGORIES for _ in range(count)]
assert len(LAYOUT) == 40


def qfile(n: int, category: str) -> str:
    return {
        "harbour-task": f"records/tasks/T-{n:02d}.md", "berth-spec": f"records/specs/S-{n:02d}.md",
        "tide-scenario": f"records/specs/scn-{n:02d}.md", "pilot-report": f"records/reports/R-{n:02d}.md",
        "exact-string": f"app/engine/e{n:02d}.py", "callers": f"app/ui/u{n:02d}.py",
        "code-paraphrase": f"app/core/k{n:02d}.py", "multi-file": f"app/core/m{n:02d}.py",
        "failure-memory": f"records/reports/L-{n:02d}.md",
    }.get(category, REGISTER_REL)


def file_text(path: str) -> str:
    """A code file as W2-171 plants it (its heading on line 3); a record with its front matter when it has a
    feature (its heading then on line 6)."""
    if path.endswith(".py"):
        return W171.file_text(path)
    stem = Path(path).stem
    front = ["---", f"feature: {FEATURES[path]}", "---"] if path in FEATURES else []
    body = [f"# Planted record {stem}", "", f"## Section {stem}"] + [f"Text line {i} of {stem}." for i in range(4, 21)]
    return "\n".join(front + body) + "\n"


def source(path: str) -> dict:
    at = 6 if path in FEATURES else 3
    heading = W171.heading_of(path) if path.endswith(".py") else f"## Section {Path(path).stem}"
    return {"path": path, "heading": heading, "lines": [at, at + 5]}


REPO_MAP = """# The planted second repository's path map: the two evaluation namespaces
version: 1
namespaces:
  governance:
    paths:
      - "records/**"
    embedding_policy: embedded
  code:
    paths:
      - "app/**"
    embedding_policy: embedded
  evaluation-sources:
    paths:
      - "archive/evalsrc/**"
    embedding_policy: not embedded
    lexical_policy: not indexed
  evaluation-fixtures:
    paths:
      - "fixtures/evaluation/**"
    embedding_policy: not embedded
    lexical_policy: not indexed
"""
SETS_MAP = f"""# The sets root's own path map (planted for W2-204's acceptance tests).
version: 1
evaluation_sets:
  # the second repository's control set
  {CONTROL_SET}:
    visible: ["fixtures/evaluation/{CONTROL_SET}/visible/**"]
    hidden: ["fixtures/evaluation/{CONTROL_SET}/hidden/**"]
    measures:
      roles: [{', '.join(W171.ROLES)}]
  # the last comment inside the block

# a comment between the blocks
evaluation_families:
  kernel: ["template/governance/kernel/**"]
"""


def repo_files() -> dict[str, str]:
    files = {REGISTER_REL: W171.REGISTER, CONFIG_REL: config_text(),
             "governance/project/path-map.yaml": REPO_MAP,
             "governance/project/retrieval.yaml": "# planted retrieval settings\npool:\n  meaning_uncut: true\n",
             ".gitignore": ".gov-runtime/\n",
             "archive/old.md": "# An archived page\n\nIt is never a question's source.\n",
             "archive/evalsrc/report.md": "first line of an evaluation document\nsecond line\n"}
    for n, category in enumerate(LAYOUT, 1):
        path = qfile(n, category)
        if path != REGISTER_REL:
            files[path] = file_text(path)
    for path in [*SPARE_F01, *SPARE_CODE]:
        files[path] = file_text(path)
    for path in CONTROL_FILES:
        files[path] = W171.file_text(path)
    return files


def control_text(k: int) -> str:
    return f"Control question {k:02d} about the harbour ledger."


def control_doc(k: int) -> dict:
    return {"id": f"c{k:02d}", "question": control_text(k), "gold_answer": f"The control answer {k}.",
            "sources": [{"path": CONTROL_FILES[k - 1]}], "category": "berth-spec"}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path) -> str:
    return sha_bytes(Path(path).read_bytes())


def build(base: Path) -> "World":
    """The world, planted from nothing: the repository (three commits, a dirty-looking index, its own store file), the
    sets root (its map, the control set), the fakes and the folders the commands are given."""
    base.mkdir(parents=True)
    home, repo = base / "home", base / "repo"
    for folder in (home, repo, base / "work", base / "state", base / "runs", base / "projects", base / "bin"):
        folder.mkdir()
    git = lambda *a, **k: W171.git(repo, *a, home=home, **k)  # noqa: E731
    git("init", "-q")
    git("checkout", "-q", "-b", "main")
    for rel, text in repo_files().items():
        W171._write(repo, rel, text)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base_commit = git("rev-parse", "HEAD").strip()
    for rel in CHANGED:
        with open(repo / rel, "a", encoding="utf-8") as f:
            f.write("# changed at the audit\n" if rel.endswith(".py") else "Changed at the audit.\n")
    git("add", "-A")
    git("commit", "-q", "-m", "audit", date="2026-11-10T00:00:00+00:00")
    audit_commit = git("rev-parse", "HEAD").strip()
    W171._write(repo, LATE_FILE, "# Late\n\nWritten after the audit commit.\n")
    git("add", "-A")
    git("commit", "-q", "-m", "later", date="2026-11-11T00:00:00+00:00")
    later_commit = git("rev-parse", "HEAD").strip()
    # a dirty-looking index and the repository's own store, which no command may touch (S8)
    with open(repo / LATE_FILE, "a", encoding="utf-8") as f:
        f.write("An uncommitted line.\n")
    W171._write(repo, "notes/staged.txt", "staged, never committed\n")
    git("add", "notes/staged.txt")
    W171._write(repo, ".gov-runtime/store.db", "the repository's own store: not the snapshot's\n")

    W171.install_script(W171.HERE / "fake_gov.py", base / "pins" / PIN / "gov")
    os.symlink(f"../pins/{PIN}/gov", base / "bin" / "gov")
    W171.install_script(W171.HERE / "fake_claude.py", base / "bin" / "claude")

    sets = base / "sets"
    W171._write(sets, "governance/project/path-map.yaml", SETS_MAP)
    control = sets / "fixtures" / "evaluation" / CONTROL_SET
    (control / "visible").mkdir(parents=True)
    (control / "hidden").mkdir()
    for k in range(1, CONTROL_N + 1):
        (control / "visible" / f"c{k:02d}.yaml").write_text(yaml.safe_dump(control_doc(k), sort_keys=False),
                                                           encoding="utf-8")
    (base / "world.json").write_text(json.dumps({"base_commit": base_commit, "audit_commit": audit_commit,
                                                 "later_commit": later_commit}), encoding="utf-8")
    return World(base)


# -- the questions ---------------------------------------------------------------------------------------------------
def clean_specs() -> list[dict]:
    """The clean 40: every category at its quota; decisions 8, harbour-tasks 4, berth-specs 7, pilot-reports 6,
    code 15; capture-flow 4, review-flow 4, tide-engine 4, none 28."""
    at, decisions, specs = W171.REGISTER_AT, iter([101, 102, 103, 104, 105, 106]), []
    for n, category in enumerate(LAYOUT, 1):
        if category == "decision":
            k = next(decisions)
            src = {"path": REGISTER_REL, "heading": f"### DEC-{k} — the rule of item {k}", "lines": [at[k], at[k] + 3]}
        elif category == "history":
            src = {"path": REGISTER_REL, "heading": "### DEC-120 — the rule of item 120", "lines": [at[120], at[120] + 3]}
        elif category == "nonexistent-id":
            src = {"path": REGISTER_REL, "heading": "Next free id: DEC-200", "lines": [3, 3]}
        else:
            src = source(qfile(n, category))
        specs.append({"id": f"q{n:02d}", "category": category, "sources": [src]})
    return specs


def repointed(moves: dict[str, str]) -> list[dict]:
    """The clean 40 with the first source of each id in ``moves`` set to the given path."""
    specs = clean_specs()
    for spec in specs:
        if spec["id"] in moves:
            spec["sources"] = [source(moves[spec["id"]])]
    return specs


def thin_specs() -> list[dict]:
    """The three failure-memory questions cite code: pilot-reports 3, under its minimum of 4."""
    return repointed({"q36": SPARE_CODE[0], "q37": SPARE_CODE[1], "q38": SPARE_CODE[2]})


def heavy_specs() -> list[dict]:
    """Seven code questions cite records of feature F01: capture-flow 11, over its maximum of 10 (code keeps 8)."""
    return repointed({f"q{n}": SPARE_F01[n - 21] for n in range(21, 28)})


def first_path(doc: dict) -> str:
    entry = doc["sources"][0]
    return (entry[0] if isinstance(entry, list) else entry)["path"]


class Call:
    """One child process's result (a ``W171.Run``, or a record of one read back from a stage)."""

    def __init__(self, code: int, out: str, err: str, argv=()):
        self.code, self.out, self.err, self.argv = code, out, err, list(argv)

    @property
    def lines(self) -> list[str]:
        return [x for x in self.out.splitlines() if x.strip()]

    @property
    def text(self) -> str:
        return self.out + "\n" + self.err

    @property
    def last(self) -> str:
        return self.lines[-1] if self.lines else ""

    def record(self) -> dict:
        return {"code": self.code, "out": self.out, "err": self.err, "argv": self.argv}

    def __repr__(self):
        return f"<exit {self.code}; stdout {self.out[-2500:]!r}; stderr {self.err[-1200:]!r}>"


class World:
    def __init__(self, base: Path):
        self.base = Path(base)
        meta = json.loads((self.base / "world.json").read_text(encoding="utf-8"))
        self.base_commit, self.audit_commit, self.later_commit = (
            meta["base_commit"], meta["audit_commit"], meta["later_commit"])
        self.home, self.repo, self.sets = self.base / "home", self.base / "repo", self.base / "sets"
        self.work, self.state, self.runs = self.base / "work", self.base / "state", self.base / "runs"
        self.projects, self.gov, self.claude = self.base / "projects", self.base / "bin" / "gov", self.base / "bin" / "claude"
        self.rebuild_log = self.state / "rebuild.jsonl"
        self.rebuild_cmd = f"{sys.executable} {HERE / 'rebuild_stub.py'} {self.rebuild_log}"
        self.fresh_dir = self.runs / "fresh" / TAG
        self.clone = self.fresh_dir / "repo"

    # -- where things are
    def set_dir(self, audit: str) -> Path:
        return self.sets / "fixtures" / "evaluation" / audit

    def hidden(self, audit: str) -> Path:
        return self.set_dir(audit) / "hidden"

    def run_dir(self, audit: str) -> Path:
        return self.sets / "runs" / audit

    # -- planting a half, as a delivery leaves it in the sets root
    def question_doc(self, half: str, spec: dict, commit: str | None = None) -> dict:
        n = int(spec["id"][1:])
        question = f"Which harbour rule mentions the {qword(half, n)} mooring?"
        if spec["category"] == "nonexistent-id":
            question = f"What does decision DEC-9999 decide for the {qword(half, n)} mooring?"
        doc = {"id": spec["id"], "question": question, "gold_answer": f"The {gword(half, n)} entry settles it.",
               "sources": copy.deepcopy(spec["sources"]), "commit": commit or self.audit_commit,
               "category": spec["category"], "drawn": spec.get("drawn", "none")}
        doc.update(copy.deepcopy(spec.get("extra", {})))
        return doc

    def write_half(self, audit: str, specs: list[dict], *, salt: str | None = None, folder: Path | None = None,
                   forbidden_default: bool = True) -> Path:
        """``specs`` as ``q<nn>.yaml`` in the half's ``hidden/`` (or in ``folder``); ``salt`` changes one file's bytes
        and nothing a check reads (a round 2 whose digest differs)."""
        half = dict(HALVES)[audit]
        folder = folder or self.hidden(audit)
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        for spec in specs:
            doc = self.question_doc(half, spec)
            if forbidden_default and spec is specs[0] and not any((x.get("extra") or {}).get("forbidden") for x in specs):
                doc["forbidden"] = ["docs/superseded-planted.md"]  # F15: declare refuses a set with no forbidden list
            if salt and spec["id"] == "q01":
                doc["naive_answer"] = f"the replaced answer {salt}"
            (folder / f"{spec['id']}.yaml").write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True),
                                                       encoding="utf-8")
        return folder

    def notes_text(self, audit: str, verdicts: dict | None = None, *, ids=None, questions: bool = True) -> str:
        """The checker brief's form: one line per question, each ``accept`` unless ``verdicts`` says otherwise."""
        half, verdicts = dict(HALVES)[audit], verdicts or {}
        ids = ids if ids is not None else sorted(p.stem for p in self.hidden(audit).glob("q*.yaml"))
        lines = ["# Cross-check notes"] + (["## Questions"] if questions else [])
        for qid in ids:
            verdict, codes = verdicts.get(qid, ("accept", "-"))
            lines.append(f"{qid} | {verdict} | {codes} | also: none | the anchor holds the {NWORD}{half} line.")
        lines += ["## The set", "domains: code 15, decisions 8, harbour-tasks 4, berth-specs 7, pilot-reports 6, none 0",
                  "keyword: any 0, all 0", "set codes: none"]
        return "\n".join(lines) + "\n"

    def write_notes(self, audit: str, round_no: int = 1, verdicts: dict | None = None) -> None:
        (self.set_dir(audit) / f"XCHECK-r{round_no}.md").write_text(self.notes_text(audit, verdicts), encoding="utf-8")

    def docs(self, audit: str) -> dict[str, dict]:
        return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(self.hidden(audit).glob("q*.yaml"))}

    # -- the fakes' plans
    def install_plans(self, *, control_hits: int = 17, wrong=()) -> None:
        """The fake gov ranks every question's gold first and ``control_hits`` of the control's 24; the fake reader
        answers every question right (the nonexistent id: not found), but the ``(audit, id)`` pairs of ``wrong``."""
        gov, claude = {W171.PROBE: {"calls": [["d"] * 10]}}, {}
        for k in range(1, CONTROL_N + 1):
            gov[control_text(k)] = {"gold": [[CONTROL_FILES[k - 1], 1, 3]],
                                    "calls": S171.calls_for(1 if k <= control_hits else None)}
        for audit, half in HALVES:
            for qid, doc in self.docs(audit).items():
                src = doc["sources"][0]
                gold = [src["path"], *src["lines"]]
                if doc["category"] == "nonexistent-id":
                    gov[doc["question"]] = {"fault": "unresolved"}
                    claude[doc["question"]] = {
                        "id": f"{half}-{qid}", "grader": ["not_found"], "check": ["not_found"],
                        "reader": [{"verdict": "not_found", "answer": "", "citations": [], "search": ""}]}
                    continue
                grade = "wrong" if (audit, qid) in wrong else "correct"
                gov[doc["question"]] = {"gold": [gold], "calls": S171.calls_for(1)}
                claude[doc["question"]] = {
                    "id": f"{half}-{qid}", "grader": [grade], "check": [grade],
                    "reader": [{"verdict": "answer", "answer": f"The {AWORD}{half} answer for {qid}.", "search": "",
                                "citations": [{"path": gold[0], "start_line": gold[1],
                                               "end_line": min(gold[2], gold[1] + 3)}]}]}
        (self.state / "gov_plan.json").write_text(json.dumps(
            {"questions": gov, "default": {"calls": [["d"] * 10]}}), encoding="utf-8")
        (self.state / "claude_plan.json").write_text(json.dumps(
            {"q": claude, "cost": {"reader": 0.10, "grader": 0.02, "check": 0.01}, "sleep": 0, "garbage": ""}),
            encoding="utf-8")

    # -- running
    def run(self, entry: str, *args, env: dict | None = None, cwd: Path | None = None) -> Call:
        argv = [*ENTRIES[entry], *map(str, args)]
        child = W171.child_env(self.home, {"W171_STATE": str(self.state)})
        child.pop("MEMAUDIT_CONFIG", None)  # a repository's own file, unless the case passes the trial form itself
        child.update(env or {})
        done = subprocess.run(argv, cwd=cwd or self.work, capture_output=True, text=True, timeout=900, env=child)
        return Call(done.returncode, done.stdout, done.stderr, argv)

    def common(self, audit: str) -> list[str]:
        return ["--sets-root", str(self.sets), "--audit", audit]

    def step_flags(self, step: str, audit: str = HIDDEN, *, repo=None, commit=None, out=None, tag: str = TAG,
                   runs=None) -> list[str]:
        """The flags of one step, as the ticket's Interface gives them."""
        repo, commit = str(repo or self.repo), commit or self.audit_commit
        store = ["--store", str(self.base / "step-store.db"), "--gov", str(self.gov)]
        return {
            "preflight": [*self.common(audit), "--repo", repo, "--commit", commit, "--runs-dir", str(self.runs)],
            "void": [*self.common(audit), "--repo", repo],
            "declare": [*self.common(audit), "--repo", repo, "--commit", commit, *store],
            "measure": [*self.common(audit), "--repo", repo, "--commit", commit, *store],
            "judge": [*self.common(audit), "--repo", repo, "--gov", str(self.gov), "--claude", str(self.claude)],
            "figures": ["--sets-root", str(self.sets), "--audit", audit],
            "brief": ["--kind", "writer", *self.common(audit), "--commit", commit, "--repo", repo,
                      "--out", str(out or self.base / "briefs" / f"{audit}-writer-1")],
            "check": ["--repo", repo, "--commit", commit],
            "fresh": ["--sets-root", str(self.sets), "--repo", repo, "--commit", commit, "--tag", tag,
                      "--runs-dir", str(runs or self.runs), "--rebuild-cmd", self.rebuild_cmd, "--gov", str(self.gov),
                      "--claude", str(self.claude), "--projects", str(self.projects)],
        }[step]

    def step(self, step: str, audit: str = HIDDEN, *extra, entry: str = "cli", env=None, **kw) -> Call:
        return self.run(entry, step, *self.step_flags(step, audit, **kw), *extra, env=env)

    def fresh(self, *extra, entry: str = "cli", env=None, **kw) -> Call:
        return self.step("fresh", HIDDEN, *extra, entry=entry, env=env, **kw)

    def brief(self, kind: str, audit: str, out: Path, *extra, round_no: int = 1, entry: str = "cli", repo=None,
              commit=None, env=None) -> Call:
        return self.run(entry, "brief", "--kind", kind, *self.common(audit), "--commit", commit or self.audit_commit,
                        "--repo", repo or self.repo, "--round", round_no, "--out", out, *extra, env=env)

    def deliver(self, kind: str, audit: str, source_dir: Path, *extra, round_no: int = 1, entry: str = "cli") -> Call:
        return self.run(entry, "deliver", "--kind", kind, *self.common(audit), "--repo", self.repo,
                        "--from", source_dir, "--round", round_no, *extra)

    def make_step_store(self) -> None:
        """A store whose fingerprints row names the audit commit: what the step commands declare (``--store``)."""
        path = self.base / "step-store.db"
        if path.exists():
            return
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
        connection.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (self.audit_commit, "c0de", "rec0", "rebuild"))
        connection.commit()
        connection.close()

    def prepare(self, audit: str = HIDDEN, specs=None, *, env=None, verdicts=None) -> None:
        """One half delivered, pre-flighted and voided by the step commands: ``measure`` starts here."""
        self.make_step_store()
        self.write_half(audit, specs or clean_specs(), forbidden_default=specs is None)
        run = self.step("preflight", audit, env=env)
        assert run.code == 0, ("the clean half's pre-flight did not pass", run)
        self.write_notes(audit, 1, verdicts)
        run = self.step("void", audit, env=env)
        assert run.code == 0, ("the clean half's void did not pass", run)

    # -- reading what was written
    def json_of(self, audit: str, name: str):
        return json.loads((self.run_dir(audit) / name).read_text(encoding="utf-8"))

    def ledger(self, audit: str) -> list[dict]:
        path = self.run_dir(audit) / "ledger.jsonl"
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def gov_calls(self) -> list[dict]:
        return self.jsonl(self.state / "gov_calls.jsonl")

    def claude_calls(self) -> list[dict]:
        return self.jsonl(self.state / "claude_calls.jsonl")

    def rebuilds(self) -> list[dict]:
        return self.jsonl(self.rebuild_log)

    def git_out(self, repo: Path, *args: str) -> subprocess.CompletedProcess:
        env = W171.git_env(self.home)
        env["GIT_OPTIONAL_LOCKS"] = "0"  # a status that never refreshes the index it is asked about
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, timeout=60)

    def git_status(self, repo: Path | None = None) -> str:
        done = self.git_out(repo or self.repo, "status", "--porcelain", "--untracked-files=all")
        assert done.returncode == 0, done.stderr
        return done.stdout

    def repo_state(self) -> dict:
        """What S8 says no command touches: the repository's status, head, index and store bytes, and its files."""
        tree = {k: v for k, v in W171.snapshot(self.repo).items() if "/.git/" not in k}
        return {"status": self.git_status(), "head": self.git_out(self.repo, "rev-parse", "HEAD").stdout.strip(),
                "index": sha_file(self.repo / ".git" / "index"), "store": sha_file(self.repo / ".gov-runtime/store.db"),
                "tree": sha_bytes(json.dumps(tree, sort_keys=True).encode())}

    def plant_transcript(self, session: str, text: str) -> Path:
        """One transcript of the planted projects folder, written now: a line of ``session`` holding ``text``."""
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        path = self.projects / "planted-project" / f"{session}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId": session, "timestamp": now, "type": "user", "text": text}) + "\n")
        return path


def files_holding(root: Path, words, *, skip=()) -> list[str]:
    """The files under ``root`` (those under a ``skip`` folder left out) whose bytes hold one of ``words``."""
    found, skip = [], [os.path.realpath(s) for s in skip]
    for folder, dirs, names in os.walk(root):
        real = os.path.realpath(folder)
        if any(real == s or real.startswith(s + os.sep) for s in skip):
            dirs[:] = []
            continue
        for name in names:
            path = Path(folder) / name
            if path.is_symlink() or not path.is_file():
                continue
            data = path.read_bytes()
            if any(w.encode() in data for w in words):
                found.append(str(path))
    return found


def find_key(data, key: str) -> list:
    """The values of every ``key`` anywhere in a JSON document."""
    found = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                found.append(v)
            found += find_key(v, key)
    elif isinstance(data, list):
        for v in data:
            found += find_key(v, key)
    return found
