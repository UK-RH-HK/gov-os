"""Planted roots for the memory audit's unit tests (Interface section 9): a repository with two commits, a sets root
with its own path map, a runs dir, a pool, a store with a fingerprints row and a gov link into a pin folder, all
under pytest's ``tmp_path``. The real sets root and run folders are never named."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SRC = str(Path(__file__).resolve().parents[3] / "src")
AUDIT = "memory-audit-20261111"
UNIQUE = {"question": "zephyrquokka", "gold": "xylophonemarmot", "path": "docs/plan/fjordnarwhal.md",
          "heading": "## Heading of the quillbadger"}

CATS = [c for c, q in [("decision", 6), ("contract", 4), ("plan", 4), ("ticket", 4), ("exact-string", 4),
                       ("callers", 4), ("code-paraphrase", 3), ("kernel-template", 3), ("multi-file", 3),
                       ("failure-memory", 3), ("history", 1), ("nonexistent-id", 1)] for _ in range(q)]
# Five domains, eight each; the code files spread over four subsystems
FILES = ["docs/DECISION_REGISTER.md", ".tickets/T-1.md", "docs/plan/plan.md", "docs/contract/contract.md",
         "src/gov/retrieval/a.py", "docs/DECISION_REGISTER.md", ".tickets/T-1.md", "docs/plan/plan.md",
         "docs/contract/contract.md", "src/gov/guard/b.py"]

SETS_MAP = """\
version: 1
# the sets root's own map
evaluation_sets:
  # memory-verdict-2, the verdict set
  memory-verdict-2:
    visible: []
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
  # a comment after the last entry
# a comment between the blocks
other_key:
  x: 1
"""

REPO_MAP = """\
namespaces:
  evaluation-sources:
    paths:
      - "docs/research/memory-measure-audit/**"
  evaluation-fixtures:
    paths:
      - "fixtures/evaluation/**"
evaluation_sets:
  memory-verdict-2:
    visible: ["docs/assessment/visible.md"]
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [engineer]
"""


def run(*args, cwd=None, env=None):
    return subprocess.run(list(args), cwd=cwd, env=env, capture_output=True, text=True, check=True)


def git_env(home: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    return env


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def file_text(path: str) -> str:
    lines = [f"# {path}"] + [f"## H{i:02d} of {Path(path).stem}\nline {i}" for i in range(1, 41)]
    if path == UNIQUE["path"]:
        lines.append(UNIQUE["heading"])
    return "\n".join(lines) + "\n"


@pytest.fixture(scope="session")
def repo(tmp_path_factory):
    """A repository with two commits; the second is the audit commit."""
    base = tmp_path_factory.mktemp("memaudit-repo")
    home = base / "home"
    home.mkdir()
    r = base / "repo"
    env = git_env(home)
    run("git", "init", "-q", "-b", "main", str(r), env=env)
    _write(r / "README.md", "planted\n")
    run("git", "add", "-A", cwd=r, env=env)
    run("git", "commit", "-q", "-m", "earlier", cwd=r, env=env)
    for path in {*FILES, UNIQUE["path"], "src/gov/close/c.py"}:
        _write(r / path, file_text(path))
    _write(r / "docs/research/memory-measure-audit/q.md", file_text("docs/research/memory-measure-audit/q.md"))
    _write(r / "docs/known.md", "the id KNOWN-77 lives here\n")
    _write(r / "governance/project/retrieval.yaml", "pool:\n  meaning_uncut: true\n  route_depth: 60\n")
    _write(r / "governance/project/path-map.yaml", REPO_MAP)
    _write(r / "governance/project/indep-walls/tree-exclude.txt", "# excluded\nfixtures/evaluation\ndocs/research/*\n")
    run("git", "add", "-A", cwd=r, env=env)
    run("git", "commit", "-q", "-m", "audit", cwd=r, env=env)
    earlier = run("git", "rev-parse", "HEAD~1", cwd=r, env=env).stdout.strip()
    head = run("git", "rev-parse", "HEAD", cwd=r, env=env).stdout.strip()
    # a second repository whose retrieval.yaml has the pool off
    off = base / "repo-off"
    run("git", "clone", "-q", str(r), str(off), env=env)
    _write(off / "governance/project/retrieval.yaml", "pool:\n  meaning_uncut: false\n")
    run("git", "commit", "-q", "-am", "pool off", cwd=off, env=env)
    off_head = run("git", "rev-parse", "HEAD", cwd=off, env=env).stdout.strip()
    return {"path": r, "head": head, "earlier": earlier, "off": off, "off_head": off_head, "home": home,
            "env": env}


def question(i: int, commit: str) -> dict:
    """Question ``q<i>`` (1-based), in the writer brief's form, its first source by FILES."""
    path = FILES[(i - 1) % len(FILES)]
    q = {"id": f"q{i:02d}", "question": f"What does part {i} say about the planted file?",
         "gold_answer": f"It says line {i}.", "sources": [{"path": path, "heading": f"## H{i:02d} of {Path(path).stem}",
                                                           "lines": [2 * i, 2 * i + 1]}],
         "commit": commit, "category": CATS[i - 1], "drawn": "none"}
    if q["category"] == "nonexistent-id":
        q["question"] = "Which ticket is ZZQ-4242 about?"
    return q


class Plant:
    def __init__(self, tmp: Path, repo: dict):
        self.tmp, self.repo = tmp, repo
        self.root = tmp / "sets"
        self.hidden = self.root / "fixtures/evaluation" / AUDIT / "hidden"
        self.set_dir = self.hidden.parent
        self.run_dir = self.root / "runs" / AUDIT
        self.runs = tmp / "runsdir"
        self.home = tmp / "home"
        self.home.mkdir()
        _write(self.root / "governance/project/path-map.yaml", SETS_MAP)
        self.hidden.mkdir(parents=True)
        (self.root / "fixtures/evaluation/memory-pool/hidden").mkdir(parents=True)
        (self.runs / "indep").mkdir(parents=True)
        self.questions = {}
        for i in range(1, 41):
            self.put(question(i, repo["head"]))
        self.selection(changed=[], sample=[])
        self.store = tmp / "store.db"
        self.make_store(repo["head"])
        pin = tmp / "share/pin-0123456789ab/bin"
        pin.mkdir(parents=True)
        (pin / "gov").write_text("#!/bin/sh\n")
        (tmp / "bin").mkdir()
        self.gov = tmp / "bin/gov"
        self.gov.symlink_to(pin / "gov")

    def put(self, q: dict, name: str | None = None) -> None:
        self.questions[q["id"]] = q
        (self.hidden / (name or f"{q['id']}.yaml")).write_text(yaml.safe_dump(q, sort_keys=False), encoding="utf-8")

    def selection(self, **lists) -> None:
        (self.set_dir / "selection.json").write_text(json.dumps(lists), encoding="utf-8")

    def make_store(self, head: str) -> None:
        if self.store.exists():
            self.store.unlink()
        conn = sqlite3.connect(self.store)
        conn.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
        conn.execute("INSERT INTO fingerprints VALUES (?, 'c', 'r', 'rebuild')", (head,))
        conn.commit()
        conn.close()

    def notes(self, verdicts: dict | None = None, rnd: int = 2, text: str | None = None) -> None:
        verdicts = verdicts or {}
        if text is None:
            rows = []
            for qid in sorted(self.questions):
                v = verdicts.get(qid, "accept")
                if v is None:
                    continue
                codes = "-" if v == "accept" else "R6-SPAN-MISSES"
                rows.append(f"{qid} | {v} | {codes} | also: none | the anchor is as stated")
            text = "# Cross-check notes\n## Questions\n" + "\n".join(rows) + "\n## The set\ndomains: code 8\n"
        (self.set_dir / f"XCHECK-r{rnd}.md").write_text(text, encoding="utf-8")

    def env(self) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "GOV_INDEP_RUNS_DIR"}
        env.update(HOME=str(self.home), PYTHONPATH=SRC, GOV_ROLE="orchestrator")
        return env

    def cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, "-m", "gov.memaudit", *args], capture_output=True, text=True,
                              env=self.env(), cwd=cwd or self.tmp)

    def preflight_args(self, commit=None):
        return ["preflight", "--sets-root", str(self.root), "--audit", AUDIT, "--repo", str(self.repo["path"]),
                "--commit", commit or self.repo["head"], "--runs-dir", str(self.runs)]

    def declare_args(self, repo=None, commit=None, *extra):
        return ["declare", "--sets-root", str(self.root), "--audit", AUDIT, "--repo", str(repo or self.repo["path"]),
                "--commit", commit or self.repo["head"], "--store", str(self.store), "--gov", str(self.gov), *extra]

    def void_args(self):
        return ["void", "--sets-root", str(self.root), "--audit", AUDIT]


@pytest.fixture
def plant(tmp_path, repo, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("GOV_INDEP_RUNS_DIR", raising=False)
    return Plant(tmp_path, repo)
