"""W2-170's planted world: a sets root, a repository with three commits, a launch log, a store and a pinned ``gov``.

Everything is planted under pytest's ``tmp_path`` (under ``TMPDIR``), as the ticket's Interface section 9 lists it.
Nothing here opens the true home's ``gov-os-eval`` or ``gov-os-runs`` (F3): every child process gets a planted
``HOME`` and this tree's own ``src/`` first on its ``PYTHONPATH`` (DEC-732), taken from this file's repository root.

The tool is driven only as its callers drive it: ``python3 -m gov.memaudit preflight|void|declare --sets-root <root>
--audit <A> ...`` as a child process. ``gov.memaudit`` is never imported at collection time, so the suite runs red
by failing, never by erroring at collection.

The repository's commits:

- ``base``: every source file, the path map with the two evaluation namespaces and an ``evaluation_sets`` entry, the
  walls' ``tree-exclude.txt``, ``retrieval.yaml`` (per variant), ``.claude/`` files (to show they stay unwritten);
- ``audit`` (the audit commit): the files of ``CHANGED`` each gain a line at their end (headings do not move);
- ``later``: ``docs/plan/late.md`` added, naming ``DEC-777``, so that "at the commit" is told from "in the tree".

The working tree stands at ``later``: sources, ``retrieval.yaml`` and the path map must be read from the commit.
"""

from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
import os
import pwd
import re
import shutil
import site
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]          # tests/acceptance/W2-170 -> the repository root of this file
SRC = TREE / "src"              # the code under test (DEC-732)
TRUE_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir)   # from the password database, immune to HOME
TRUE_SETS = TRUE_HOME / "gov-os-eval"
TRUE_RUNS = TRUE_HOME / "gov-os-runs"

AUDIT = "memory-audit-20261111"
EARLIER = "memory-audit-20261101"
PIN = "pin-0123456789ab"
SEED = 424242
ROLES = ("engineer", "research", "product-spec", "independent-test-designer", "independent-auditor")
CODES = ("PF-COUNT", "PF-FORM", "PF-COMMIT", "PF-QUOTA", "PF-SPREAD", "PF-DRAWN", "PF-SOURCE", "PF-EVALNS",
         "PF-DUPPOOL", "PF-IDEXISTS")
QUOTAS = {"decision": 6, "contract": 4, "plan": 4, "ticket": 4, "exact-string": 4, "callers": 4,
          "code-paraphrase": 3, "kernel-template": 3, "multi-file": 3, "failure-memory": 3, "history": 1,
          "nonexistent-id": 1}
FINAL_OK = "PRE-FLIGHT: every check as expected"
FINAL_NOT = "PRE-FLIGHT: NOT as expected: stop, fix before any search"
ROUNDING = ("need_right = ceil(85 n / 100); max_wrong = floor(5 n / 100); target_right = ceil(95 n / 100); "
            "integer arithmetic")
REFUSED_LINE = "REFUSED: a line that names a sets-root folder was not printed"
DECLARATION_KEYS = ("audit", "audit_commit", "store_commit", "store_sha256", "gov_pin", "retrieval_yaml_sha256",
                    "set_digest", "n", "settings", "nonstandard", "decision", "ok", "bar", "rounding", "declared_at")
DROPS_KEYS = ("kept", "dropped", "by_code", "domains", "subsystems", "subsystem_over", "void", "set_digest",
              "notes_round")

# S5's words: each lives in one place of the special question only, and must reach no output (F1).
QWORD, GWORD, PWORD, HWORD = "yarrowplinth", "quibbletonmarsh", "glimmerquaxt", "fennelwrisk"
UNIQUE = (QWORD, GWORD, PWORD, HWORD)
EWORD = "snorkelvantry"         # the text of a malformed YAML file, which a YAML error would quote
SPECIAL = "q07"

# -- section 4's two tables, as the expectations are computed (the first source path decides) ---------------------
DOMAIN_TABLE = (
    ("decisions", ("docs/DECISION_REGISTER.md",)),
    ("tickets", (".tickets/**",)),
    ("plan", ("docs/plan/**",)),
    ("contract", ("docs/contract/**", "docs/charter/**")),
    ("code", ("src/**", "template/governance/kernel/hooks/**", ".claude/hooks/**")),
)
SUBSYSTEM_TABLE = (
    ("retrieval", ("src/gov/retrieval/**", "src/gov/retrieve/**", "src/gov/context/**", "src/gov/store/**",
                   "src/gov/codeintel/**", "governance/project/retrieval.yaml")),
    ("guard", ("src/gov/guard/**", "src/gov/hooks/**", "template/governance/kernel/hooks/**", ".claude/hooks/**")),
    ("close", ("src/gov/close/**", "src/gov/closure/**", "src/gov/accept/**", "src/gov/check/**",
               "src/gov/readiness/**", "src/gov/ci/**", "docs/close/**")),
    ("checkpoint", ("src/gov/checkpoint/**", "src/gov/pause/**", "docs/checkpoints/**")),
    ("rebuild", ("src/gov/rebuild/**", "src/gov/secrets/**", "src/gov/doctor/**")),
    ("launch", ("src/gov/launch/**", "src/gov/brief/**", "template/governance/kernel/launch/**",
                "governance/project/orchestration/tools/indep_launch.py", "governance/project/indep-walls/**")),
    ("release", ("src/gov/release/**", "src/gov/adopt/**", "src/gov/adapters/**", "docs/releases/**")),
)
DOMAINS = tuple(name for name, _ in DOMAIN_TABLE)
SUBSYSTEMS = tuple(name for name, _ in SUBSYSTEM_TABLE)


def _hit(path: str, pattern: str) -> bool:
    return path.startswith(pattern[:-2]) if pattern.endswith("/**") else path == pattern


def _row(path: str, table) -> str:
    return next((name for name, patterns in table if any(_hit(path, p) for p in patterns)), "none")


def domain_of(path: str) -> str:
    return _row(path, DOMAIN_TABLE)


def subsystem_of(path: str) -> str:
    return _row(path, SUBSYSTEM_TABLE)


def need_domain(n: int) -> int:
    return -(-4 * n // 40)


def most_subsystem(n: int) -> int:
    return 10 * n // 40


def bar(n: int) -> dict:
    return {"need_right": -(-85 * n // 100), "max_wrong": 5 * n // 100, "target_right": -(-95 * n // 100)}


# -- the repository's files --------------------------------------------------------------------------------------
def _qfile(n: int, category: str) -> str:
    """The governing source file of question ``n`` (decisions, the history and the nonexistent id cite the register)."""
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


LAYOUT = (["decision"] * 6 + ["contract"] * 4 + ["plan"] * 4 + ["ticket"] * 4 + ["exact-string"] * 4
          + ["callers"] * 4 + ["code-paraphrase"] * 3 + ["kernel-template"] * 3 + ["multi-file"] * 3
          + ["failure-memory"] * 3 + ["history"] + ["nonexistent-id"])
assert len(LAYOUT) == 40

# Spare files the variants re-point first sources to.
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
    """The heading line (line 3) of a planted per-question or spare file."""
    stem = Path(path).stem
    if path == f"docs/contract/{PWORD}.md":
        return f"## The {HWORD} clause"
    if path.endswith(".py"):
        return f"def rule_{stem.replace('-', '_')}():"
    return f"## Section {stem}"


def file_text(path: str) -> str:
    """20 lines: a title, a blank, the heading on line 3, then plain lines."""
    stem = Path(path).stem
    if path.endswith(".py"):
        body = [f"# planted module {stem}", "", heading_of(path)]
        body += [f"    # text line {i} of {stem}" for i in range(4, 20)] + ["    return None"]
    else:
        body = [f"# Planted file {stem}", "", heading_of(path)] + [f"Text line {i} of {stem}." for i in range(4, 21)]
    return "\n".join(body) + "\n"


REGISTER_DECISIONS = [101, 102, 103, 104, 105, 106, 120, 12, 999]


def register_text() -> tuple[str, dict[int, int]]:
    """The planted register and the line number of each decision's heading."""
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

REPO_MAP = """# The planted repository's path map (W2-170's acceptance tests): the two evaluation namespaces
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
# The repository's own evaluation sets
evaluation_sets:
  old-set:
    visible: ["docs/assessment/old-visible.md"]
    hidden: ["fixtures/evaluation/old-set/hidden/**"]
    measures:
      roles: [engineer, research]
"""

BAD_REPO_MAP = f"namespaces: [{EWORD} unclosed\n  evaluation-sources: {{paths: [\n"

RETRIEVAL = {
    "standard": "# planted retrieval settings\npool:\n  meaning_uncut: true\n",
    "pool_off": "# planted retrieval settings\npool:\n  meaning_uncut: false\n",
    "retrieval_list": "- not\n- a mapping\n",
    "no_retrieval": None,
    "bad_repo_map": "pool:\n  meaning_uncut: true\n",
}

SETS_MAP = f"""# The sets root's own path map (planted for W2-170's acceptance tests).
# Only its evaluation_sets block is read by the measure; every other byte must be kept.
version: 1
evaluation_sets:
  # memory-verdict-2, the verdict set of 80, in its shape
  memory-verdict-2:
    visible: []
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
  # an earlier audit's set, among comments
  {EARLIER}:
    visible: []
    hidden: ["fixtures/evaluation/{EARLIER}/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
  # the last comment inside the block

# a comment between the blocks
evaluation_families:
  kernel: ["template/governance/kernel/**"]
"""


def repo_files(variant: str) -> dict[str, str]:
    files = {"docs/DECISION_REGISTER.md": REGISTER}
    for n, category in enumerate(LAYOUT, 1):
        path = _qfile(n, category)
        if path != "docs/DECISION_REGISTER.md":
            files[path] = file_text(path)
    for path in [*SPARE_RETRIEVAL, *SPARE_HOOKS, SPARE_LESSON, SPARE_CHARTER, "docs/plan/p90.md"]:
        files[path] = file_text(path)
    for path in EVAL_SOURCES.values():
        files[path] = "first line of an evaluation document\nsecond line\nthird line\n"
    files["fixtures/evaluation/old-set/hidden/a.yaml"] = "question: an old hidden question\n"
    files["governance/project/path-map.yaml"] = BAD_REPO_MAP if variant == "bad_repo_map" else REPO_MAP
    files["governance/project/indep-walls/tree-exclude.txt"] = TREE_EXCLUDE
    files[".claude/settings.json"] = '{"planted": true}\n'
    files[".claude/hooks/pretooluse.py"] = "# planted guard hook\n"
    if RETRIEVAL[variant] is not None:
        files["governance/project/retrieval.yaml"] = RETRIEVAL[variant]
    return files


# -- git ------------------------------------------------------------------------------------------------------------
def git_env(home: Path, date: str = "2026-11-01T00:00:00+00:00") -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="Planted", GIT_COMMITTER_NAME="Planted",
               GIT_AUTHOR_EMAIL="planted@example.invalid", GIT_COMMITTER_EMAIL="planted@example.invalid",
               GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    return env


def git(repo: Path, *args: str, home: Path, date: str = "2026-11-01T00:00:00+00:00", text: bool = True):
    done = subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args], capture_output=True,
                          text=text, env=git_env(home, date), timeout=60)
    if done.returncode != 0:
        raise AssertionError(f"planting failed: git {' '.join(args)}: {done.stderr}")
    return done.stdout


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def excluded_by(globs):
    """The launch script's rule (stage B4): a path, or one of its parent folders, matching a glob (fnmatchcase)."""
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


def sha_file(path: Path) -> str:
    return sha_bytes(Path(path).read_bytes())


# -- the template world (built once per session and variant, copied per test) --------------------------------------
def build(base: Path, variant: str = "standard") -> None:
    base.mkdir(parents=True)
    home = base / "home"
    home.mkdir()
    (base / "work").mkdir()
    repo = base / "repo"
    repo.mkdir()
    git(repo, "init", "-q", home=home)
    git(repo, "checkout", "-q", "-b", "main", home=home)
    for rel, text in repo_files(variant).items():
        _write(repo, rel, text)
    git(repo, "add", "-A", home=home)
    git(repo, "commit", "-q", "-m", "base", home=home, date="2026-11-01T00:00:00+00:00")
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

    # the store, its fingerprints row's head the audit commit
    connection = sqlite3.connect(base / "store.db")
    connection.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
    connection.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (audit_commit, "c0de", "rec0", "rebuild"))
    connection.commit()
    connection.close()

    # the pinned gov and an unpinned one, each reached through a relative link
    for folder in (PIN, "plain"):
        exe = base / "pins" / folder / "gov"
        exe.parent.mkdir(parents=True)
        exe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        exe.chmod(0o755)
    (base / "bin").mkdir()
    os.symlink(f"../pins/{PIN}/gov", base / "bin" / "gov")
    os.symlink("../pins/plain/gov", base / "bin" / "gov-unpinned")

    # the launch script's folder (GOV_INDEP_RUNS_DIR): AUDITS.log and SEEDS.log
    write_launch_log(base / "launch-log", base_commit, audit_commit)

    # the sets root: its own path map and the regression pool
    sets = base / "sets"
    _write(sets, "governance/project/path-map.yaml", SETS_MAP)
    pool = sets / "fixtures" / "evaluation" / "memory-pool" / "hidden"
    pool.mkdir(parents=True)
    for name, doc in default_pool(audit_commit).items():
        (pool / name).write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    (base / "world.json").write_text(json.dumps({
        "variant": variant, "base_commit": base_commit, "audit_commit": audit_commit,
        "later_commit": later_commit, "changed": changed, "sample": sample}, indent=1), encoding="utf-8")


def seeds_line(**over) -> dict:
    line = {"time": "2026-11-10T01:00:00Z", "kind": "writer", "run": "writer-1", "commit": "0" * 40,
            "seed": SEED, "seed_sha256": sha_bytes(f"{SEED}\n".encode()), "set": AUDIT, "round": 1, "dry": False}
    line.update(over)
    return line


def write_launch_log(folder: Path, base_commit: str, audit_commit: str, *, seeds: list[dict] | None = None,
                     audits: bool = True) -> None:
    indep = folder / "indep"
    indep.mkdir(parents=True, exist_ok=True)
    if audits:
        (indep / "AUDITS.log").write_text(json.dumps(
            {"time": "2026-11-02T00:00:00Z", "commit": base_commit, "run": "auditor-1", "audit": EARLIER}) + "\n",
            encoding="utf-8")
    elif (indep / "AUDITS.log").exists():
        (indep / "AUDITS.log").unlink()
    if seeds is None:
        seeds = [seeds_line(commit=audit_commit),
                 seeds_line(commit=audit_commit, round=2, seed=7, seed_sha256=sha_bytes(b"7\n"), run="writer-2"),
                 seeds_line(commit=audit_commit, kind="checker", seed=8, seed_sha256=sha_bytes(b"8\n")),
                 seeds_line(commit=audit_commit, dry=True, seed=9, seed_sha256=sha_bytes(b"9\n")),
                 seeds_line(commit=base_commit, set=EARLIER, seed=10, seed_sha256=sha_bytes(b"10\n"))]
    (indep / "SEEDS.log").write_text("".join(json.dumps(s) + "\n" for s in seeds), encoding="utf-8")


def default_pool(audit_commit: str) -> dict[str, dict]:
    """Two earlier questions whose gold-source sets equal no question of the clean set."""
    return {
        f"{EARLIER}-q01.yaml": {"id": "q01", "question": "An earlier question about a plan section.",
                                "gold_answer": "An earlier answer.", "commit": audit_commit,
                                "sources": [{"path": "docs/plan/p13.md", "heading": heading_of("docs/plan/p13.md"),
                                             "lines": [3, 9]}], "category": "plan", "drawn": "sample"},
        f"{EARLIER}-q02.yaml": {"id": "q02", "question": "An earlier question about an early rule.",
                                "gold_answer": "An earlier answer.", "commit": audit_commit,
                                "sources": [{"path": "docs/DECISION_REGISTER.md",
                                             "heading": f"### DEC-12 — the rule of item 12",
                                             "lines": [REGISTER_AT[12], REGISTER_AT[12] + 2]}],
                                "category": "decision", "drawn": "sample"},
    }


# -- the questions ----------------------------------------------------------------------------------------------
def source(path: str, *, heading: str | None = "", lines=(3, 8)) -> dict:
    s = {"path": path}
    if heading is not None:
        s["heading"] = heading or heading_of(path)
    if lines is not None:
        s["lines"] = list(lines)
    return s


def clean_specs() -> list[dict]:
    """The clean 40: every category at its quota, every domain at 4 or more, no subsystem over 10."""
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


def by_id(specs: list[dict], qid: str) -> dict:
    return next(s for s in specs if s["id"] == qid)


def without(specs: list[dict], *qids: str) -> list[dict]:
    return [s for s in specs if s["id"] not in qids]


def repoint(specs: list[dict], qid: str, path: str, *, keep_old: bool = False) -> list[dict]:
    """Give question ``qid`` a new first source (its old one kept as a second entry when asked)."""
    spec = by_id(specs, qid)
    old = spec["sources"]
    spec["sources"] = [source(path)] + (old if keep_old else [])
    return specs


def first_path(sources) -> str:
    entry = sources[0]
    alternative = entry[0] if isinstance(entry, list) else entry
    return alternative["path"]


def kept_counts(specs: list[dict]) -> tuple[dict, dict]:
    domains = {d: 0 for d in DOMAINS}
    subsystems = {s: 0 for s in SUBSYSTEMS}
    for spec in specs:
        p = first_path(spec["sources"])
        if domain_of(p) != "none":
            domains[domain_of(p)] += 1
        if subsystem_of(p) != "none":
            subsystems[subsystem_of(p)] += 1
    return domains, subsystems


def set_digest(hidden: Path) -> str:
    """The fresh 80's digest: ``LC_ALL=C sha256sum *.yaml | sha256sum`` over hidden/*.yaml (not dropped/)."""
    names = sorted((p.name for p in Path(hidden).glob("*.yaml") if p.is_file()), key=lambda s: s.encode())
    text = "".join(f"{sha_file(Path(hidden) / n)}  {n}\n" for n in names)
    return sha_bytes(text.encode())


# -- running the tool -----------------------------------------------------------------------------------------------
class Run:
    def __init__(self, argv, done):
        self.argv = [str(a) for a in argv]
        self.code, self.out, self.err = done.returncode, done.stdout, done.stderr

    @property
    def lines(self) -> list[str]:
        return [x for x in self.out.splitlines() if x.strip()]

    @property
    def last(self) -> str:
        return self.lines[-1] if self.lines else ""

    def __repr__(self):
        return f"<exit {self.code}; stdout {self.out[-1500:]!r}; stderr {self.err[-1500:]!r}>"


def child_env(home: Path, extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_INDEP_"))}
    rest = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p and Path(p) != SRC]
    env.update(HOME=str(home), PYTHONPATH=os.pathsep.join([str(SRC), *rest]), GIT_CONFIG_NOSYSTEM="1",
               PYTHONDONTWRITEBYTECODE="1")
    # the planted HOME must not change which packages a child imports: the test process's own user site stays
    env.setdefault("PYTHONUSERBASE", site.getuserbase())
    env.update(extra or {})
    return env


class World:
    """One test's copy of a template world."""

    def __init__(self, base: Path):
        self.base = Path(base)
        meta = json.loads((self.base / "world.json").read_text(encoding="utf-8"))
        self.variant = meta["variant"]
        self.base_commit, self.audit_commit, self.later_commit = (
            meta["base_commit"], meta["audit_commit"], meta["later_commit"])
        self.changed, self.sample = meta["changed"], meta["sample"]
        self.home = self.base / "home"
        self.repo = self.base / "repo"
        self.sets = self.base / "sets"
        self.launch = self.base / "launch-log"
        self.store = self.base / "store.db"
        self.gov = self.base / "bin" / "gov"
        self.gov_unpinned = self.base / "bin" / "gov-unpinned"
        self.work = self.base / "work"
        self.set_dir = self.sets / "fixtures" / "evaluation" / AUDIT
        self.hidden = self.set_dir / "hidden"
        self.dropped = self.hidden / "dropped"
        self.run_dir = self.sets / "runs" / AUDIT
        self.pool = self.sets / "fixtures" / "evaluation" / "memory-pool" / "hidden"
        self.sets_map = self.sets / "governance" / "project" / "path-map.yaml"
        self.specs: list[dict] = []

    # -- planting the set
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
        for key in spec.get("drop_keys", ()):
            doc.pop(key, None)
        return doc

    def write_set(self, specs: list[dict], *, selection=True) -> None:
        """Plant ``specs`` as ``hidden/q<nn>.yaml`` (a spec's ``raw`` is written as it stands); ``selection`` True
        plants the true lists as ``selection.json``, a dict plants that, False plants none."""
        if self.hidden.exists():
            shutil.rmtree(self.hidden)
        self.hidden.mkdir(parents=True)
        self.specs = copy.deepcopy(specs)
        for spec in specs:
            text = spec["raw"] if "raw" in spec else yaml.safe_dump(
                self.question_doc(spec), sort_keys=False, allow_unicode=True)
            (self.hidden / f"{spec['id']}.yaml").write_text(text, encoding="utf-8")
        target = self.set_dir / "selection.json"
        if selection is False:
            if target.exists():
                target.unlink()
        else:
            data = self.selection() if selection is True else selection
            target.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")

    def selection(self, **over) -> dict:
        data = {"commit": self.audit_commit, "last_audit": self.base_commit,
                "seed_sha256": sha_bytes(f"{SEED}\n".encode()), "changed": list(self.changed),
                "sample": list(self.sample)}
        data.update(over)
        return data

    def write_notes(self, round_no: int, verdicts: dict | None = None, *, missing=(), raw: dict | None = None,
                    questions_section: bool = True) -> None:
        """``XCHECK-r<round>.md`` in the checker brief's form: one line per question of ``hidden/`` in id order."""
        verdicts, raw = verdicts or {}, raw or {}
        ids = sorted(p.stem for p in self.hidden.glob("q*.yaml"))
        lines = ["# Cross-check notes"]
        if questions_section:
            lines.append("## Questions")
        for qid in ids:
            if qid in missing:
                continue
            if qid in raw:
                lines.append(raw[qid])
                continue
            verdict, codes = verdicts.get(qid, ("accept", "-"))
            lines.append(f"{qid} | {verdict} | {codes} | also: none | the anchor holds the deciding line.")
        lines += ["## The set", "domains: code 14, decisions 8, tickets 4, plan 4, contract 4, none 6",
                  "keyword: any 1, all 0", "set codes: none"]
        (self.set_dir / f"XCHECK-r{round_no}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # -- the flags
    def pf_flags(self, runs_dir=True) -> list[str]:
        flags = ["--sets-root", str(self.sets), "--audit", AUDIT, "--repo", str(self.repo),
                 "--commit", self.audit_commit]
        return flags + (["--runs-dir", str(self.launch)] if runs_dir else [])

    def void_flags(self) -> list[str]:
        return ["--sets-root", str(self.sets), "--audit", AUDIT]

    def dc_flags(self, *, store=None, gov=None, decision=None, commit=None) -> list[str]:
        flags = ["--sets-root", str(self.sets), "--audit", AUDIT, "--repo", str(self.repo),
                 "--commit", commit or self.audit_commit, "--store", str(store or self.store),
                 "--gov", str(gov or self.gov)]
        return flags + (["--decision", decision] if decision else [])

    # -- running
    def run(self, *args, env: dict | None = None, home: Path | None = None) -> Run:
        argv = [sys.executable, "-m", "gov.memaudit", *map(str, args)]
        done = subprocess.run(argv, cwd=self.work, env=child_env(home or self.home, env), capture_output=True,
                              text=True, timeout=120)
        return Run(argv, done)

    def preflight(self, *extra, runs_dir=True, **kw) -> Run:
        return self.run("preflight", *self.pf_flags(runs_dir), *extra, **kw)

    def void(self, *extra, **kw) -> Run:
        return self.run("void", *self.void_flags(), *extra, **kw)

    def declare(self, *extra, store=None, gov=None, decision=None, commit=None, **kw) -> Run:
        return self.run("declare", *self.dc_flags(store=store, gov=gov, decision=decision, commit=commit),
                        *extra, **kw)

    # -- reading what was written
    def json_of(self, name: str):
        return json.loads((self.run_dir / name).read_text(encoding="utf-8"))

    def ledger(self) -> list[dict]:
        path = self.run_dir / "ledger.jsonl"
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def git_status(self) -> str:
        done = subprocess.run(["git", "-C", str(self.repo), "status", "--porcelain", "--untracked-files=all"],
                              capture_output=True, text=True, env=git_env(self.home), timeout=60)
        assert done.returncode == 0, done.stderr
        return done.stdout

    def show(self, rel: str) -> bytes:
        done = subprocess.run(["git", "-C", str(self.repo), "show", f"{self.audit_commit}:{rel}"],
                              capture_output=True, env=git_env(self.home), timeout=60)
        assert done.returncode == 0
        return done.stdout

    def measure(self, kept: Path) -> subprocess.CompletedProcess:
        """``gov.retrieval.measure`` on the planted set's hidden part, as the orchestrator (no role it measures),
        with an empty folder of kept outputs, so that it never starts a retriever."""
        kept.mkdir(parents=True, exist_ok=True)
        env = child_env(self.home, {"GOV_ROLE": "orchestrator"})
        env.pop("GOV_TICKET", None)
        argv = [sys.executable, "-m", "gov.retrieval.measure", AUDIT, "--root", str(self.repo), "--sets-root",
                str(self.sets), "--part", "hidden", "--kept", str(kept), "--json"]
        return subprocess.run(argv, cwd=self.work, env=env, capture_output=True, text=True, timeout=120)


def snapshot(*roots: Path) -> dict:
    """Every file under the roots: its bytes' sha256 and its mtime in nanoseconds (a link: its target)."""
    found = {}
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        for folder, dirs, names in os.walk(root):
            dirs.sort()
            for name in sorted(names) + [d for d in dirs if os.path.islink(os.path.join(folder, d))]:
                path = Path(folder) / name
                if path.is_symlink():
                    found[str(path)] = ("link", os.readlink(path))
                else:
                    found[str(path)] = (sha_file(path), path.stat().st_mtime_ns)
            found.update({str(Path(folder) / d) + "/": ("dir",) for d in dirs})
    return found


def ids_in_text(text: str) -> list[str]:
    return sorted(set(re.findall(r"(?<![\w-])q\d{2}(?![\w-])", text)))


def pf_blocks(stdout: str) -> tuple[dict, list[str]]:
    """``preflight``'s lines by code: ``{code: {"word", "n", "text", "ids"}}`` and the codes in printed order. A
    code's text is its line and any lines after it up to the next code or the closing line."""
    blocks, order, current = {}, [], None
    for line in stdout.splitlines():
        m = re.match(r"^(PF-[A-Z]+) (ok|refused)\b ?(.*)$", line)
        if m:
            current = m.group(1)
            order.append(current)
            words = m.group(3).split()
            n = int(words[0]) if m.group(2) == "refused" and words and words[0].isdigit() else None
            blocks[current] = {"word": m.group(2), "n": n, "text": line}
        elif line.startswith("PRE-FLIGHT:"):
            current = None
        elif current:
            blocks[current]["text"] += "\n" + line
    for block in blocks.values():
        block["ids"] = ids_in_text(block["text"])
    return blocks, order


def find_key(data, pattern: str):
    """The values of every key matching ``pattern`` anywhere in a JSON document."""
    found = []
    if isinstance(data, dict):
        for k, v in data.items():
            if re.fullmatch(pattern, str(k)):
                found.append(v)
            found += find_key(v, pattern)
    elif isinstance(data, list):
        for v in data:
            found += find_key(v, pattern)
    return found


def at_or_under(path: str, folder: Path) -> bool:
    p, f = os.path.normpath(path), os.path.normpath(str(folder))
    return p == f or p.startswith(f + os.sep)


# -- S6: a planted repository for the close's scoped selection ------------------------------------------------------
def plant_select_repo(base: Path, map_text: str, home: Path) -> tuple[Path, str]:
    """A repository holding ``map_text`` as its test map, a stub for every target the map names (so that no target
    is unresolved), a planted ``tests/unit/memaudit/`` and, in a second commit, one change under
    ``src/gov/memaudit/``. Its green nightly record names the first commit, the base of the change."""
    repo = base / "select-repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", home=home)
    _write(repo, "governance/project/test-map.yaml", map_text)
    data = yaml.safe_load(map_text) or {}
    targets = list(data.get("record_reading") or []) + list(data.get("every_close") or [])
    for coupling in data.get("couplings") or []:
        targets += list(coupling.get("suites") or [])
    targets.append("tests/unit/memaudit/")
    stubs: dict[str, set] = {}
    for target in targets:
        path, _, case = target.partition("::")
        path = path.rstrip("/")
        if not path.endswith(".py"):
            path = f"{path}/test_stub.py"
            case = case or "test_stub"
        names = stubs.setdefault(path, set())
        if case:
            names.add(tuple(re.sub(r"\[.*\]$", "", n) for n in case.split("::")))
        else:
            names.add(("test_stub",))
    for path, names in stubs.items():
        tops: dict[str, set] = {}
        for name in names:
            tops.setdefault(name[0], set()).update(name[1:2])
        body = []
        for top, subs in sorted(tops.items()):
            if subs or top.startswith("Test"):
                body.append(f"class {top}:")
                body += [f"    def {s}(self):\n        pass" for s in sorted(subs)] or ["    pass"]
            else:
                body.append(f"def {top}():\n    pass")
        _write(repo, path, "\n\n".join(body) + "\n")
    _write(repo, "src/gov/memaudit/__init__.py", '"""planted"""\n')
    git(repo, "add", "-A", home=home)
    git(repo, "commit", "-q", "-m", "base", home=home)
    base_commit = git(repo, "rev-parse", "HEAD", home=home).strip()
    _write(repo, "src/gov/memaudit/core.py", "VALUE = 1\n")
    git(repo, "add", "-A", home=home)
    git(repo, "commit", "-q", "-m", "a change under src/gov/memaudit/", home=home,
        date="2026-11-02T00:00:00+00:00")
    _write(repo, "docs/close/nightly/2026-11-01.json", json.dumps({"verdict": "green", "head": base_commit}))
    return repo, base_commit
