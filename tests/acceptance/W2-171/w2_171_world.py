"""W2-171's planted world: a sets root, a repository, a store, a pinned fake ``gov``, a fake ``claude``, a set of 40.

Everything is planted under pytest's ``tmp_path`` (under ``TMPDIR``). Nothing here opens the true home's
``gov-os-eval`` or ``gov-os-runs`` (the tool is given a planted ``HOME`` and this tree's own ``src/`` first on its
``PYTHONPATH``). The tool is driven only as its callers drive it: ``python3 -m gov.memaudit <subcommand> --sets-root
<root> --audit <A> ...`` as a child process. ``gov.memaudit``'s new modules are never imported at collection.

The set and its repository are W2-170's (its acceptance world, copied here and trimmed: one variant only), so that the
real ``preflight`` and ``void`` of W2-170 prepare the state ``measure`` starts from (``measure`` itself calls
``declare``, Interface 1). Added here: the control set ``memory-retrieval`` (40 questions, gold files ``docs/ctl/``),
the three planted executables (``bin/gov``, ``bin/claude`` and a second pin), the state folder both fakes read through
``W171_STATE``, a pool, and the planting of ranks and verdicts (``plant``).

Item 12 fixes the order of a measure's searches (the probe, the control, the attempt); the faults here are keyed by the
question's text and its n-th asking, never by a call's number, so that a different order of unrelated calls changes
nothing.
"""

from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
import os
import pwd
import shutil
import site
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]          # tests/acceptance/W2-171 -> the repository root of this file
SRC = TREE / "src"              # the code under test
TRUE_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir)
AUDIT = "memory-audit-20261111"
EARLIER = "memory-audit-20261101"
PIN = "pin-0123456789ab"
OTHER_PIN = "pin-ffffffffffff"
SEED = 424242
PROBE = "what decides a close"
NONEXISTENT = "q40"
SPECIAL = "q07"
QWORD, GWORD, PWORD, HWORD, AWORD = "yarrowplinth", "quibbletonmarsh", "glimmerquaxt", "fennelwrisk", "marlowbrindle"
UNIQUE = (QWORD, GWORD, PWORD, AWORD)
CATEGORIES = ("decision", "contract", "plan", "ticket", "exact-string", "callers", "code-paraphrase",
              "kernel-template", "multi-file", "failure-memory", "history", "nonexistent-id")
EXIT = {"ok": 0, "refused": 1, "stopped": 2, "used": 3, "usage": 4}

LAYOUT = (["decision"] * 6 + ["contract"] * 4 + ["plan"] * 4 + ["ticket"] * 4 + ["exact-string"] * 4
          + ["callers"] * 4 + ["code-paraphrase"] * 3 + ["kernel-template"] * 3 + ["multi-file"] * 3
          + ["failure-memory"] * 3 + ["history"] + ["nonexistent-id"])
assert len(LAYOUT) == 40
CATEGORY_OF = {f"q{n:02d}": c for n, c in enumerate(LAYOUT, 1)}
KEYWORD_QID = "q19"


def bar(n: int) -> dict:
    return {"need_right": -(-85 * n // 100), "max_wrong": 5 * n // 100, "target_right": -(-95 * n // 100)}


# -- the repository's files (W2-170's) ---------------------------------------------------------------------------
def _qfile(n: int, category: str) -> str:
    return {
        "contract": f"docs/contract/c{n}.md" if n != 7 else f"docs/contract/{PWORD}.md",
        "plan": f"docs/plan/p{n}.md",
        "ticket": f".tickets/T-{n}.md",
        "exact-string": f"src/gov/retrieval/r{n}.py",
        "callers": f"src/gov/guard/g{n}.py",
        "code-paraphrase": f"src/gov/close/k{n}.py",
        "kernel-template": f"template/governance/kernel/roles/role{n}.md",
        "multi-file": f"src/gov/checkpoint/m{n}.py",
        "failure-memory": f"docs/lessons/L-{n}.md",
    }.get(category, "docs/DECISION_REGISTER.md")


SPARE_RETRIEVAL = [f"src/gov/retrieval/x{k}.py" for k in range(1, 11)]
SPARE_HOOKS = [f"template/governance/kernel/hooks/h{k}.py" for k in range(1, 8)] + [".claude/hooks/hk1.py"]
SPARE_LESSON = "docs/lessons/L-90.md"
SPARE_CHARTER = "docs/charter/ch1.md"
EVAL_SOURCES = {"evaluation-sources": "docs/research/evalsrc/report.md",
                "evaluation-fixtures": "fixtures/memory-quality/events.yaml",
                "evaluation-set-visible": "docs/assessment/old-visible.md"}
LATE_FILE = "docs/plan/late.md"
CHANGED = {"docs/DECISION_REGISTER.md", f"docs/contract/{PWORD}.md", "docs/contract/c8.md", "docs/plan/p11.md",
           "docs/plan/p12.md", ".tickets/T-15.md", ".tickets/T-16.md", "src/gov/retrieval/r19.py",
           "src/gov/retrieval/r20.py", "src/gov/guard/g23.py", "src/gov/guard/g24.py", "src/gov/close/k27.py",
           "template/governance/kernel/roles/role30.md", "src/gov/checkpoint/m33.py", "docs/lessons/L-36.md",
           SPARE_LESSON, *SPARE_RETRIEVAL[:5], *SPARE_HOOKS[:3]}


def heading_of(path: str) -> str:
    stem = Path(path).stem
    if path == f"docs/contract/{PWORD}.md":
        return f"## The {HWORD} clause"
    if path.endswith(".py"):
        return f"def rule_{stem.replace('-', '_')}():"
    return f"## Section {stem}"


def file_text(path: str) -> str:
    stem = Path(path).stem
    if path.endswith(".py"):
        body = [f"# planted module {stem}", "", heading_of(path)]
        body += [f"    # text line {i} of {stem}" for i in range(4, 20)] + ["    return None"]
    else:
        body = [f"# Planted file {stem}", "", heading_of(path)] + [f"Text line {i} of {stem}." for i in range(4, 21)]
    return "\n".join(body) + "\n"


REGISTER_DECISIONS = [101, 102, 103, 104, 105, 106, 120, 12, 999]


def register_text() -> tuple[str, dict[int, int]]:
    lines = ["# Decision register", "", "Next free id: DEC-200", ""]
    at = {}
    for k in REGISTER_DECISIONS:
        at[k] = len(lines) + 1
        lines.append(f"### DEC-{k} — the rule of item {k}")
        lines += [f"Body of the rule of item {k}, line {j}." for j in range(1, 5)]
        lines.append("")
    return "\n".join(lines) + "\n", at


REGISTER, REGISTER_AT = register_text()
TREE_EXCLUDE = ("# planted walls' exclusions (the launch script's form)\n"
                "fixtures/evaluation/**\n"
                "docs/research/evalsrc/**\n"
                "governance/project/indep-walls/**\n"
                ".gov-runtime/**\n")
REPO_MAP = """# The planted repository's path map: the two evaluation namespaces
version: 1
namespaces:
  governance:
    paths:
      - "docs/**"
      - ".tickets/**"
    embedding_policy: embedded
  code:
    paths:
      - "src/**"
      - "template/**"
    embedding_policy: embedded
  evaluation-sources:
    paths:
      - "docs/research/evalsrc/**"
    embedding_policy: not embedded
    lexical_policy: not indexed
  evaluation-fixtures:
    paths:
      - "fixtures/evaluation/**"
      - "fixtures/memory-quality/**"
    embedding_policy: not embedded
    lexical_policy: not indexed
evaluation_sets:
  old-set:
    visible: ["docs/assessment/old-visible.md"]
    hidden: ["fixtures/evaluation/old-set/hidden/**"]
    measures:
      roles: [engineer, research]
"""
ROLES = ["engineer", "research", "product-spec", "independent-test-designer", "independent-auditor"]
SETS_MAP = f"""# The sets root's own path map (planted for W2-171's acceptance tests).
version: 1
evaluation_sets:
  # memory-verdict-2, the verdict set of 80, in its shape
  memory-verdict-2:
    visible: []
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [{', '.join(ROLES)}]
  # the standing control set (the visible 40)
  memory-retrieval:
    visible: ["fixtures/evaluation/memory-retrieval/visible/**"]
    hidden: ["fixtures/evaluation/memory-retrieval/hidden/**"]
    measures:
      roles: [{', '.join(ROLES)}]
  # an earlier audit's set, among comments
  {EARLIER}:
    visible: []
    hidden: ["fixtures/evaluation/{EARLIER}/hidden/**"]
    measures:
      roles: [{', '.join(ROLES)}]
  # the last comment inside the block

# a comment between the blocks
evaluation_families:
  kernel: ["template/governance/kernel/**"]
"""
CONTROL_N = 40
CONTROL_FILES = [f"docs/ctl/c{k:02d}.md" for k in range(1, CONTROL_N + 1)]


def repo_files() -> dict[str, str]:
    files = {"docs/DECISION_REGISTER.md": REGISTER}
    for n, category in enumerate(LAYOUT, 1):
        path = _qfile(n, category)
        if path != "docs/DECISION_REGISTER.md":
            files[path] = file_text(path)
    for path in [*SPARE_RETRIEVAL, *SPARE_HOOKS, SPARE_LESSON, SPARE_CHARTER, "docs/plan/p90.md", *CONTROL_FILES]:
        files[path] = file_text(path)
    for path in EVAL_SOURCES.values():
        files[path] = "first line of an evaluation document\nsecond line\nthird line\n"
    files["fixtures/evaluation/old-set/hidden/a.yaml"] = "question: an old hidden question\n"
    files["governance/project/path-map.yaml"] = REPO_MAP
    files["governance/project/indep-walls/tree-exclude.txt"] = TREE_EXCLUDE
    files[".claude/settings.json"] = '{"planted": true}\n'
    files[".claude/hooks/pretooluse.py"] = "# planted guard hook\n"
    files["governance/project/retrieval.yaml"] = "# planted retrieval settings\npool:\n  meaning_uncut: true\n"
    return files


# -- git ------------------------------------------------------------------------------------------------------------
def git_env(home: Path, date: str = "2026-11-01T00:00:00+00:00") -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="Planted", GIT_COMMITTER_NAME="Planted",
               GIT_AUTHOR_EMAIL="planted@example.invalid", GIT_COMMITTER_EMAIL="planted@example.invalid",
               GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    return env


def git(repo: Path, *args: str, home: Path, date: str = "2026-11-01T00:00:00+00:00"):
    done = subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args], capture_output=True,
                          text=True, env=git_env(home, date), timeout=60)
    if done.returncode != 0:
        raise AssertionError(f"planting failed: git {' '.join(args)}: {done.stderr}")
    return done.stdout


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def excluded_by(globs):
    def excluded(rel):
        parts = rel.split("/")
        for i in range(1, len(parts) + 1):
            p = "/".join(parts[:i])
            forms = (p, p + "/") if i < len(parts) else (p,)
            if any(fnmatch.fnmatchcase(f, g) for f in forms for g in globs):
                return True
        return False
    return excluded


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path) -> str:
    return sha_bytes(Path(path).read_bytes())


def set_digest(folder: Path, *, skip_prefix: str | None = None) -> str:
    """``LC_ALL=C sha256sum *.yaml | sha256sum`` over the flat ``*.yaml`` of ``folder`` (those not named
    ``<skip_prefix>*`` when given): W2-170's rule."""
    names = sorted((p.name for p in Path(folder).glob("*.yaml")
                    if p.is_file() and not (skip_prefix and p.name.startswith(skip_prefix))),
                   key=lambda s: s.encode())
    return sha_bytes("".join(f"{sha_file(Path(folder) / n)}  {n}\n" for n in names).encode())


# -- the planted executables -----------------------------------------------------------------------------------------
def install_script(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"#!{sys.executable} -S\n" + source.read_text(encoding="utf-8"), encoding="utf-8")
    dest.chmod(0o755)


def seeds_line(**over) -> dict:
    line = {"time": "2026-11-10T01:00:00Z", "kind": "writer", "run": "writer-1", "commit": "0" * 40,
            "seed": SEED, "seed_sha256": sha_bytes(f"{SEED}\n".encode()), "set": AUDIT, "round": 1, "dry": False}
    line.update(over)
    return line


def write_launch_log(folder: Path, base_commit: str, audit_commit: str) -> None:
    indep = folder / "indep"
    indep.mkdir(parents=True, exist_ok=True)
    (indep / "AUDITS.log").write_text(json.dumps(
        {"time": "2026-11-02T00:00:00Z", "commit": base_commit, "run": "auditor-1", "audit": EARLIER}) + "\n",
        encoding="utf-8")
    seeds = [seeds_line(commit=audit_commit),
             seeds_line(commit=audit_commit, round=2, seed=7, seed_sha256=sha_bytes(b"7\n"), run="writer-2"),
             seeds_line(commit=audit_commit, kind="checker", seed=8, seed_sha256=sha_bytes(b"8\n")),
             seeds_line(commit=audit_commit, dry=True, seed=9, seed_sha256=sha_bytes(b"9\n")),
             seeds_line(commit=base_commit, set=EARLIER, seed=10, seed_sha256=sha_bytes(b"10\n"))]
    (indep / "SEEDS.log").write_text("".join(json.dumps(s) + "\n" for s in seeds), encoding="utf-8")


def default_pool(audit_commit: str) -> dict[str, dict]:
    return {
        f"{EARLIER}-q01.yaml": {"id": "q01", "question": "An earlier question about a plan section.",
                                "gold_answer": "An earlier answer.", "commit": audit_commit,
                                "sources": [{"path": "docs/plan/p13.md", "heading": heading_of("docs/plan/p13.md"),
                                             "lines": [3, 9]}], "category": "plan", "drawn": "sample"},
        f"{EARLIER}-q02.yaml": {"id": "q02", "question": "An earlier question about an early rule.",
                                "gold_answer": "An earlier answer.", "commit": audit_commit,
                                "sources": [{"path": "docs/DECISION_REGISTER.md",
                                             "heading": "### DEC-12 — the rule of item 12",
                                             "lines": [REGISTER_AT[12], REGISTER_AT[12] + 2]}],
                                "category": "decision", "drawn": "sample"},
    }


def control_doc(k: int) -> dict:
    return {"id": f"c{k:02d}", "question": control_text(k), "gold_answer": f"The control answer {k}.",
            "sources": [{"path": f"docs/ctl/c{k:02d}.md"}], "category": "plan"}


def control_text(k: int) -> str:
    return f"Control question {k:02d} about the standing set."


# -- the template world ------------------------------------------------------------------------------------------------
def build(base: Path) -> None:
    base.mkdir(parents=True)
    home = base / "home"
    home.mkdir()
    (base / "work").mkdir()
    repo = base / "repo"
    repo.mkdir()
    git(repo, "init", "-q", home=home)
    git(repo, "checkout", "-q", "-b", "main", home=home)
    for rel, text in repo_files().items():
        _write(repo, rel, text)
    git(repo, "add", "-A", home=home)
    git(repo, "commit", "-q", "-m", "base", home=home)
    base_commit = git(repo, "rev-parse", "HEAD", home=home).strip()
    for rel in sorted(CHANGED):
        with open(repo / rel, "a", encoding="utf-8") as f:
            f.write("### DEC-130 — added at the audit\n" if rel == "docs/DECISION_REGISTER.md"
                    else "Changed at the audit.\n" if not rel.endswith(".py") else "# changed at the audit\n")
    git(repo, "add", "-A", home=home)
    git(repo, "commit", "-q", "-m", "audit", home=home, date="2026-11-10T00:00:00+00:00")
    audit_commit = git(repo, "rev-parse", "HEAD", home=home).strip()
    _write(repo, LATE_FILE, "# Late\n\nDEC-777 is named only after the audit commit.\n")
    git(repo, "add", "-A", home=home)
    git(repo, "commit", "-q", "-m", "later", home=home, date="2026-11-11T00:00:00+00:00")
    later_commit = git(repo, "rev-parse", "HEAD", home=home).strip()
    tracked = [p for p in git(repo, "ls-tree", "-r", "--name-only", "-z", audit_commit, home=home).split("\0") if p]
    excluded = excluded_by([x.strip() for x in TREE_EXCLUDE.splitlines() if x.strip() and not x.startswith("#")])
    diff = [p for p in git(repo, "diff", "--name-only", "--no-renames", "-z", base_commit, audit_commit,
                           home=home).split("\0") if p]
    changed = sorted({p for p in diff if p in tracked and not excluded(p)})
    sample = [p for p in tracked if not excluded(p) and p not in changed]
    assert len(sample) <= 300, "the planted repository must keep the sample whole"

    connection = sqlite3.connect(base / "store.db")
    connection.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
    connection.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (audit_commit, "c0de", "rec0", "rebuild"))
    connection.commit()
    connection.close()

    for folder in (PIN, OTHER_PIN, "plain"):
        install_script(HERE / "fake_gov.py", base / "pins" / folder / "gov")
    (base / "bin").mkdir()
    os.symlink(f"../pins/{PIN}/gov", base / "bin" / "gov")
    os.symlink("../pins/plain/gov", base / "bin" / "gov-unpinned")
    os.symlink(f"../pins/{OTHER_PIN}/gov", base / "bin" / "gov-other")
    install_script(HERE / "fake_claude.py", base / "bin" / "claude")
    (base / "state").mkdir()
    write_launch_log(base / "launch-log", base_commit, audit_commit)

    sets = base / "sets"
    _write(sets, "governance/project/path-map.yaml", SETS_MAP)
    pool = sets / "fixtures" / "evaluation" / "memory-pool" / "hidden"
    pool.mkdir(parents=True)
    for name, doc in default_pool(audit_commit).items():
        (pool / name).write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    control = sets / "fixtures" / "evaluation" / "memory-retrieval"
    (control / "visible").mkdir(parents=True)
    (control / "hidden").mkdir(parents=True)
    for k in range(1, CONTROL_N + 1):
        (control / "visible" / f"c{k:02d}.yaml").write_text(
            yaml.safe_dump(control_doc(k), sort_keys=False), encoding="utf-8")
    (base / "world.json").write_text(json.dumps({
        "base_commit": base_commit, "audit_commit": audit_commit, "later_commit": later_commit,
        "changed": changed, "sample": sample}, indent=1), encoding="utf-8")


# -- the questions -------------------------------------------------------------------------------------------------
def source(path: str, *, heading: str | None = "", lines=(3, 8)) -> dict:
    s = {"path": path}
    if heading is not None:
        s["heading"] = heading or heading_of(path)
    if lines is not None:
        s["lines"] = list(lines)
    return s


def clean_specs() -> list[dict]:
    """The clean 40 of W2-170: every category at its quota, every domain at 4 or more, no subsystem over 10."""
    specs = []
    decisions = iter([101, 102, 103, 104, 105, 106])
    for n, category in enumerate(LAYOUT, 1):
        qid = f"q{n:02d}"
        if category == "decision":
            k = next(decisions)
            src = {"path": "docs/DECISION_REGISTER.md", "heading": f"### DEC-{k} — the rule of item {k}",
                   "lines": [REGISTER_AT[k], REGISTER_AT[k] + 3]}
        elif category == "history":
            src = {"path": "docs/DECISION_REGISTER.md", "heading": "### DEC-120 — the rule of item 120",
                   "lines": [REGISTER_AT[120], REGISTER_AT[120] + 3]}
        elif category == "nonexistent-id":
            src = {"path": "docs/DECISION_REGISTER.md", "heading": "Next free id: DEC-200", "lines": [3, 3]}
        else:
            src = source(_qfile(n, category))
        spec = {"id": qid, "category": category, "sources": [src]}
        if category == "nonexistent-id":
            spec["question"] = "What does decision DEC-9999 decide?"
            spec["gold"] = "None: the register's next free id is below it."
        if n == 1:
            spec["extra"] = {"naive_answer": "the replaced record's answer"}
        if n == 19:
            spec["extra"] = {"keyword": True}
        specs.append(spec)
    return specs


def first_path(sources) -> str:
    entry = sources[0]
    alternative = entry[0] if isinstance(entry, list) else entry
    return alternative["path"]


# -- running the tool -----------------------------------------------------------------------------------------------
class Run:
    def __init__(self, argv, done):
        self.argv = [str(a) for a in argv]
        self.code, self.out, self.err = done.returncode, done.stdout, done.stderr

    @property
    def lines(self) -> list[str]:
        return [x for x in self.out.splitlines() if x.strip()]

    @property
    def text(self) -> str:
        return self.out + "\n" + self.err

    def __repr__(self):
        return f"<exit {self.code}; stdout {self.out[-2500:]!r}; stderr {self.err[-1500:]!r}>"


def child_env(home: Path, extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_INDEP_", "GOV_", "W171_"))}
    rest = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p and Path(p) != SRC]
    env.update(HOME=str(home), PYTHONPATH=os.pathsep.join([str(SRC), *rest]), GIT_CONFIG_NOSYSTEM="1",
               PYTHONDONTWRITEBYTECODE="1")
    env.setdefault("PYTHONUSERBASE", site.getuserbase())
    env.update(extra or {})
    return env


class World:
    """One test's copy of the template world."""

    def __init__(self, base: Path):
        self.base = Path(base)
        meta = json.loads((self.base / "world.json").read_text(encoding="utf-8"))
        self.base_commit, self.audit_commit, self.later_commit = (
            meta["base_commit"], meta["audit_commit"], meta["later_commit"])
        self.changed, self.sample = meta["changed"], meta["sample"]
        self.home, self.repo, self.sets = self.base / "home", self.base / "repo", self.base / "sets"
        self.launch, self.store, self.work = self.base / "launch-log", self.base / "store.db", self.base / "work"
        self.gov, self.gov_unpinned = self.base / "bin" / "gov", self.base / "bin" / "gov-unpinned"
        self.gov_other, self.claude = self.base / "bin" / "gov-other", self.base / "bin" / "claude"
        self.state = self.base / "state"
        self.set_dir = self.sets / "fixtures" / "evaluation" / AUDIT
        self.hidden = self.set_dir / "hidden"
        self.run_dir = self.sets / "runs" / AUDIT
        self.pool = self.sets / "fixtures" / "evaluation" / "memory-pool" / "hidden"
        self.sets_map = self.sets / "governance" / "project" / "path-map.yaml"
        self.specs: list[dict] = []

    # -- planting the set (W2-170's)
    def drawn_of(self, spec: dict) -> str:
        if spec["category"] in ("history", "nonexistent-id"):
            return "none"
        return "changed" if first_path(spec["sources"]) in self.changed else "sample"

    def question_doc(self, spec: dict) -> dict:
        n = int(spec["id"][1:])
        if spec["id"] == SPECIAL:
            question, gold = f"Which {QWORD} rule does the contract set?", f"The {GWORD} rule applies."
        else:
            question = spec.get("question", f"Where is the rule of item {n} stated?")
            gold = spec.get("gold", f"It is stated in the planted file of item {n}.")
        doc = {"id": spec["id"], "question": question, "gold_answer": gold,
               "sources": copy.deepcopy(spec["sources"]), "commit": spec.get("commit", self.audit_commit),
               "category": spec["category"], "drawn": spec.get("drawn") or self.drawn_of(spec)}
        doc.update(copy.deepcopy(spec.get("extra", {})))
        return doc

    def write_set(self, specs: list[dict]) -> None:
        if self.hidden.exists():
            shutil.rmtree(self.hidden)
        self.hidden.mkdir(parents=True)
        self.specs = copy.deepcopy(specs)
        for spec in specs:
            (self.hidden / f"{spec['id']}.yaml").write_text(
                yaml.safe_dump(self.question_doc(spec), sort_keys=False, allow_unicode=True), encoding="utf-8")
        (self.set_dir / "selection.json").write_text(json.dumps({
            "commit": self.audit_commit, "last_audit": self.base_commit,
            "seed_sha256": sha_bytes(f"{SEED}\n".encode()), "changed": list(self.changed),
            "sample": list(self.sample)}, indent=1) + "\n", encoding="utf-8")

    def write_notes(self, round_no: int = 1, rejects=()) -> None:
        ids = sorted(p.stem for p in self.hidden.glob("q*.yaml"))
        lines = ["# Cross-check notes", "## Questions"]
        lines += [f"{qid} | reject | R1-WRONG | also: none | the anchor does not hold." if qid in rejects else
                  f"{qid} | accept | - | also: none | the anchor holds the deciding line." for qid in ids]
        lines += ["## The set", "domains: code 14, decisions 8, tickets 4, plan 4, contract 4, none 6",
                  "keyword: any 1, all 0", "set codes: none"]
        (self.set_dir / f"XCHECK-r{round_no}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def docs(self) -> dict[str, dict]:
        """Each question of the set as its YAML parses (the set's own files, read back)."""
        return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(self.hidden.glob("q*.yaml"))}

    # -- the flags
    def pf_flags(self) -> list[str]:
        return ["--sets-root", str(self.sets), "--audit", AUDIT, "--repo", str(self.repo),
                "--commit", self.audit_commit, "--runs-dir", str(self.launch)]

    def common(self) -> list[str]:
        return ["--sets-root", str(self.sets), "--audit", AUDIT]

    def measure_flags(self, *, gov=None, store=None, commit=None) -> list[str]:
        return [*self.common(), "--repo", str(self.repo), "--commit", commit or self.audit_commit,
                "--store", str(store or self.store), "--gov", str(gov or self.gov)]

    def judge_flags(self, *, gov=None) -> list[str]:
        return [*self.common(), "--repo", str(self.repo), "--gov", str(gov or self.gov),
                "--claude", str(self.claude)]

    def pool_flags(self, *, gov=None) -> list[str]:
        return [*self.common(), "--repo", str(self.repo), "--gov", str(gov or self.gov)]

    # -- running
    def env(self, extra: dict | None = None) -> dict:
        return {"W171_STATE": str(self.state), **(extra or {})}

    def run(self, *args, env: dict | None = None, home: Path | None = None) -> Run:
        argv = [sys.executable, "-m", "gov.memaudit", *map(str, args)]
        done = subprocess.run(argv, cwd=self.work, env=child_env(home or self.home, self.env(env)),
                              capture_output=True, text=True, timeout=400)
        return Run(argv, done)

    def preflight(self, *extra, **kw) -> Run:
        return self.run("preflight", *self.pf_flags(), *extra, **kw)

    def void(self, *extra, **kw) -> Run:
        return self.run("void", *self.common(), *extra, **kw)

    def declare(self, *extra, **kw) -> Run:
        return self.run("declare", *self.measure_flags(), *extra, **kw)

    def measure(self, *extra, **kw) -> Run:
        return self.run("measure", *self.measure_flags(), *extra, **kw)

    def measure_kept(self, n, *extra, **kw) -> Run:
        return self.run("measure", *self.measure_flags(), "--kept", str(n), *extra, **kw)

    def judge(self, *extra, gov=None, **kw) -> Run:
        return self.run("judge", *self.judge_flags(gov=gov), *extra, **kw)

    def classes(self, *extra, **kw) -> Run:
        return self.run("classes", *self.common(), *extra, **kw)

    def pool_run(self, *extra, gov=None, **kw) -> Run:
        return self.run("pool", *self.pool_flags(gov=gov), *extra, **kw)

    def pool_import(self, *extra, **kw) -> Run:
        return self.run("pool-import", "--sets-root", str(self.sets), *extra, **kw)

    def prepare(self, drops=()) -> None:
        """The set planted, pre-flighted and voided (W2-170's flow; ``drops`` the questions the checker rejects, at
        most three), ready for ``measure``."""
        self.write_set(clean_specs())
        run = self.preflight()
        assert run.code == 0, run
        self.write_notes(1, rejects=drops)
        run = self.void()
        assert run.code == 0, run

    # -- reading what was written
    def json_of(self, name: str):
        return json.loads((self.run_dir / name).read_text(encoding="utf-8"))

    def ledger(self) -> list[dict]:
        path = self.run_dir / "ledger.jsonl"
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def events(self, name: str, **where) -> list[dict]:
        return [e for e in self.ledger() if e.get("event") == name and all(e.get(k) == v for k, v in where.items())]

    def jsonl(self, name: str) -> list[dict]:
        path = self.state / name
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def gov_calls(self) -> list[dict]:
        return self.jsonl("gov_calls.jsonl")

    def claude_calls(self) -> list[dict]:
        return self.jsonl("claude_calls.jsonl")

    def attempt_dir(self, n: int) -> Path:
        return self.run_dir / f"attempt-{n}"

    def question_lines(self, folder: Path) -> list[tuple[str, str, bool, int | None, bool, bool]]:
        """``(id, part, hit5, first gold rank, in the bundle, full evidence)`` of a measure's text output."""
        import re
        found = []
        pattern = re.compile(r"^(\S+) \((\w+)\): hit@5 (yes|no) \(first gold rank (\d+|-)\), in the bundle (yes|no); "
                             r"full evidence (yes|no)")
        for line in (folder / "measure.txt").read_text(encoding="utf-8").splitlines():
            m = pattern.match(line)
            if m:
                found.append((m[1], m[2], m[3] == "yes", None if m[4] == "-" else int(m[4]), m[5] == "yes",
                              m[6] == "yes"))
        return found

    def git_status(self) -> str:
        done = subprocess.run(["git", "-C", str(self.repo), "status", "--porcelain", "--untracked-files=all"],
                              capture_output=True, text=True, env=git_env(self.home), timeout=60)
        assert done.returncode == 0, done.stderr
        return done.stdout

    # -- planting the fakes' plans
    def write_plans(self, gov_questions: dict, claude_questions: dict, *, cost=None, sleep=0, garbage="") -> None:
        self.state.mkdir(exist_ok=True)
        (self.state / "gov_plan.json").write_text(json.dumps(
            {"questions": gov_questions, "default": {"calls": [["d"] * 10]}}), encoding="utf-8")
        (self.state / "claude_plan.json").write_text(json.dumps(
            {"q": claude_questions, "cost": cost or {"reader": 0.10, "grader": 0.02, "check": 0.01}, "sleep": sleep,
             "garbage": garbage}), encoding="utf-8")

    def reset_state(self) -> None:
        shutil.rmtree(self.state, ignore_errors=True)
        self.state.mkdir()

    def plant_earlier(self, audit: str, *, control_hit5=None, pool=None) -> None:
        """An earlier audit's run folder holding a complete ``FIGURES.json`` (Interface 10), by which ``last`` of the
        control and the pool's last figures are read."""
        folder = self.sets / "runs" / audit
        folder.mkdir(parents=True, exist_ok=True)
        os.chmod(folder, 0o700)
        doc = {"audit": audit, "n": 40, "n_gold": 39, "bar": bar(40),
               "verdict": {"right": 36, "wrong": 1, "passes": True, "right_ok": True, "wrong_ok": True,
                           "target_ok": False, "interval_exact": [0.7, 0.96], "not_run": 0},
               "beside": {}, "misses": {},
               "control": {"hit5": control_hit5 if control_hit5 is not None else 34, "of": 40, "last": 34,
                           "last_audit": None},
               "pool": pool, "classes": None, "spend": {"usd": 5.0, "projection": 6.28, "brake": 12.56}}
        (folder / "FIGURES.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def snapshot(*roots: Path) -> dict:
    """Every file under the roots: its bytes' sha256 and its mtime in nanoseconds (a link: its target), and every
    folder."""
    found = {}
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        for folder, dirs, names in os.walk(root):
            dirs.sort()
            for name in sorted(names):
                path = Path(folder) / name
                if path.is_symlink():
                    found[str(path)] = ("link", os.readlink(path))
                else:
                    found[str(path)] = (sha_file(path), path.stat().st_mtime_ns)
            found.update({str(Path(folder) / d) + "/": ("dir",) for d in dirs})
    return found
