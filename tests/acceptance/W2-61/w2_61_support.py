"""Support code for the W2-61 acceptance tests (standard library and PyYAML only).

W2-61 is the standing 20-question measure of memory retrieval (DEC-828 items 3 and 4, DEC-833, DEC-860,
DEC-820 (d)). The tests drive public interfaces only:

- **the measure**, ``python3 -m gov.retrieval.measure <set> [options]``, run as a process with this worktree's
  ``src`` on its ``PYTHONPATH`` (DEC-732: the runner's own ``PYTHONPATH`` when it has one, else the ``src``
  folder of the worktree that holds this file);
- **the guard**, the kernel's PreToolUse hook (``template/governance/kernel/hooks/pretooluse.py``), copied as one
  file into the temporary project and run as the harness runs it (W2-58's way);
- **the files the ticket writes**: ``fixtures/evaluation/memory-retrieval/visible/*.yaml`` and
  ``docs/research/W2-61-baseline.md``, read as files, with lens B's report (``docs/assessment/2026-10/
  B-memory-retrieval.md``) and this repository's path map as the references.

**Nothing hidden is ever read.** The real hidden half (``fixtures/evaluation/memory-retrieval/hidden/**``) is never
opened, listed or depended on. Every hidden part here is a planted one, built at test time in a temporary
repository under pytest's ``tmp_path``, and its planted words begin with ``zqxw61hidden``.

**The planted retrieval.** A ``python3 -m venv --without-pip`` environment in the test's folder holds a planted
``gov`` package; the planted executable ``bin/gov`` names that environment's interpreter on its first line, as the
installed ``gov`` does. It answers ``--version`` and ``retrieve`` with canned bundles in the real ``--json``
envelope (per question, and per continuation token), and logs each call's arguments, its working folder, and
whether ``PYTHONPATH`` or ``GOV_TICKET`` reached it. No real store, no embedder, no network.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
MEASURE = "gov.retrieval.measure"
GUARD_SOURCE = REPO_ROOT / "template/governance/kernel/hooks/pretooluse.py"
GUARD_REL = "governance/kernel/hooks/pretooluse.py"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
PATH_MAP_REL = "governance/project/path-map.yaml"
HELD_OUT_LIST_REL = "governance/project/held-out.yaml"
SETTINGS_REL = ".claude/settings.json"
TIMEOUT_S = 60.0

# The real files W2-61 writes, and their references (read as files; never the hidden half).
REAL_VISIBLE = REPO_ROOT / "fixtures/evaluation/memory-retrieval/visible"
REAL_SET = "memory-retrieval"
BASELINE = REPO_ROOT / "docs/research/W2-61-baseline.md"
LENS_B = REPO_ROOT / "docs/assessment/2026-10/B-memory-retrieval.md"
LENS_B_REL = "docs/assessment/2026-10/B-memory-retrieval.md"
REAL_PATH_MAP = REPO_ROOT / PATH_MAP_REL

# --------------------------------------------------------------------------
# Planted words: only these tests write them, so an output can be searched for them
# --------------------------------------------------------------------------

HIDDEN_QUESTION = "zqxw61hiddenquestiontext"     # in every planted hidden question
HIDDEN_ANSWER = "zqxw61hiddengoldanswer"         # every planted hidden gold answer
HIDDEN_SOURCE_DIR = "docs/zqxw61hiddensrc"       # the folder of the hidden questions' governing source
HIDDEN_SOURCE = f"{HIDDEN_SOURCE_DIR}/governing.md"
HIDDEN_HEADING = "## zqxw61hiddenheading"
HIDDEN_ITEM_PATH = "docs/zqxw61hiddenitem.md"    # a retrieved item of a hidden question that is no source
HIDDEN_ITEM_TEXT = "zqxw61hiddenitemtext"
HIDDEN_FAILURE = "zqxw61hiddenfailuremessage"   # the planted gov's error message on a hidden question
HIDDEN_UNKNOWN = "zqxw61hiddenunknownfield"      # an unknown field's value in a hidden question
HIDDEN_WORDS = ("zqxw61hidden", HIDDEN_QUESTION, HIDDEN_ANSWER, HIDDEN_SOURCE_DIR, "zqxw61hiddenheading",
                HIDDEN_ITEM_PATH, HIDDEN_ITEM_TEXT, HIDDEN_FAILURE, HIDDEN_UNKNOWN)
ANSWER_WORD = "zqxw61quotedanswer"               # what the quoting files (report, fixture, test) hold
GATE_ANSWER = "four gigabytes free"              # v03's gold answer, quoted verbatim by the quoting files
UNKNOWN_WORD = "zqxw61unknownfieldvalue"         # an unknown field's value

PLANTED_VERSION = "gov 9.61.0-planted (commit 61a61a61a61a)"

# --------------------------------------------------------------------------
# The planted sets
# --------------------------------------------------------------------------

SET = "planted-memory"
SECOND = "planted-second"
UNCOVERED = "planted-uncovered"
REPORT = "docs/assessment/planted-report.md"     # the visible part planted-memory declares (as lens B's report)
SECOND_REPORT = "docs/second/report.md"
FIXTURE_QUOTE = "fixtures/evaluation/notes/quote.md"
TEST_QUOTE = "tests/unit/test_quotes.py"
DECISIONS = "docs/governing/decisions.md"
ARCHIVE_CODE = "src/app/archive.py"
MEASURED_ROLES = ("engineer", "research")
MEASURED_TICKET = "DAEO-zz61"                    # measured by its ticket id
MEASURED_WBS_TICKET = "DAEO-zz65"                # measured by its WBS id (W2-195)
MEASURED_WBS = "W2-195"
OTHER_TICKET = "DAEO-zz60"                       # measured by nothing


def evaluation_block():
    return {
        SET: {
            "visible": [REPORT],
            "hidden": [f"fixtures/evaluation/{SET}/hidden/**"],
            "measures": {"roles": list(MEASURED_ROLES), "tickets": [MEASURED_TICKET, MEASURED_WBS]},
        },
        SECOND: {
            "visible": [SECOND_REPORT],
            "hidden": [f"fixtures/evaluation/{SECOND}/hidden/**"],
            "measures": {"tickets": ["DAEO-zz62"]},
        },
        UNCOVERED: {
            "visible": [],
            "hidden": ["elsewhere/hidden/**"],
            "measures": {"roles": ["research"]},
        },
    }


def path_map_text(block=None):
    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    document["evaluation_sets"] = evaluation_block() if block is None else block
    return yaml.safe_dump(document, sort_keys=False)


def ticket_text(tk, wbs, role="engineer"):
    return "\n".join([
        "---", f"id: {tk}", "status: in_progress", "deps: []", "links: []", "created: 2026-10-29T08:00:00Z",
        "type: task", "priority: 1", f"assignee: {role}", f"external-ref: {wbs}", "tags: [wave-2]",
        f"wbs_id: {wbs}", "title: W2-61 fixture ticket", "class: implementation", f"role: {role}",
        "depends_on: []", "allowed_paths:", "- src/app/**", "kpis:", "  success:", "  - fixture",
        "  failure:", "  - fixture", "profile: STANDARD", "acceptance_tests:", f"  path: tests/acceptance/{wbs}/",
        "---", f"# {wbs} fixture ticket", "",
    ])


TICKETS = {MEASURED_TICKET: "W2-191", OTHER_TICKET: "W2-190", MEASURED_WBS_TICKET: MEASURED_WBS,
           "DAEO-zz62": "W2-192", "DAEO-zz63": "W2-193", "DAEO-zz64": "W2-194"}

# The governing documents. Line numbers are found by ``World.span``, never hard-coded in a test.
DECISIONS_LINES = [
    "# Planted decisions",
    "",
    "The decisions of the planted project.",
    "",
    "## DEC-1 The packet ceiling",
    "The packet ceiling is six thousand tokens.",
    "It holds for every packet.",
    "",
    "## DEC-2 The archive",
    "The archive is kept read-only.",
    "",
    "### DEC-2.1 The archive's copy",
    "The copy is kept beside the archive.",
    "",
    "## DEC-3 The gate",
    "The gate needs four gigabytes free.",
    "",
    "## DEC-4 The resume",
    "A session resumes from its last checkpoint.",
    "",
    "## DEC-5 The audit lines",
    "Every finding carries two lines.",
    "",
]
ARCHIVE_LINES = ["def archive(path):", "    return path  # read-only", ""]


def base_files():
    files = {
        "README.md": "# W2-61 planted project\n",
        ".gitignore": "__pycache__/\n",
        DECISIONS: "\n".join(DECISIONS_LINES) + "\n",
        ARCHIVE_CODE: "\n".join(ARCHIVE_LINES) + "\n",
        REPORT: f"# Planted report\n\nThe gate needs {GATE_ANSWER}: {ANSWER_WORD}.\n",
        SECOND_REPORT: "# Second report\n",
        FIXTURE_QUOTE: f"The gate needs {GATE_ANSWER}: {ANSWER_WORD}.\n",
        TEST_QUOTE: f"def test_gate():\n    assert 'The gate needs {GATE_ANSWER}: {ANSWER_WORD}'\n",
        HIDDEN_SOURCE: f"# Hidden governing\n\n{HIDDEN_HEADING}\nThe answer is {HIDDEN_ANSWER}.\n\n## Other\nx\n",
        HIDDEN_ITEM_PATH: f"{HIDDEN_ITEM_TEXT} {HIDDEN_ANSWER}\n",
        PATH_MAP_REL: path_map_text(),
        SETTINGS_REL: json.dumps({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
            {"type": "command", "command": f'python3 "$CLAUDE_PROJECT_DIR"/{GUARD_REL}'}]}]}}, indent=2) + "\n",
    }
    for n in range(1, 13):
        files[f"docs/noise/n{n:02d}.md"] = f"# Noise {n}\n\nNothing of use, part {n}.\n"
    for tk, wbs in TICKETS.items():
        files[f".tickets/{tk}.md"] = ticket_text(tk, wbs)
    return files


# --------------------------------------------------------------------------
# The planted gov
# --------------------------------------------------------------------------

PLANTED_PACKAGE = r'''"""The planted gov of the W2-61 acceptance tests: canned retrieve bundles, every call logged."""
import hashlib, json, os, sys

VERSION = @VERSION@
TAKES = {"--ticket": "ticket", "--radius": "radius", "--batch-size": "batch_size",
         "--bundle-budget": "bundle_budget", "--continue": "continue"}


def _token(query, n):
    return "tok-%d-%s" % (n, hashlib.sha256(query.encode()).hexdigest()[:8])


def _fail(code, message, status=1):
    print(json.dumps({"ok": False, "command": "retrieve", "result": {}, "session": None,
                      "error": {"code": code, "message": message, "details": {}}}))
    print("gov retrieve: %s: %s" % (code, message), file=sys.stderr)
    return status


def main(answers_path, log_path):
    args = sys.argv[1:]
    entry = {"argv": args, "cwd": os.getcwd(), "pythonpath": "PYTHONPATH" in os.environ,
             "gov_ticket": "GOV_TICKET" in os.environ}
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
    if args == ["--version"]:
        print(VERSION)
        return 0
    if not args or args[0] != "retrieve":
        print("planted gov: only retrieve and --version are planted", file=sys.stderr)
        return 2
    opts, positional, rest, i = {"ids": [], "json": False}, [], args[1:], 0
    while i < len(rest):
        word = rest[i]
        name, eq, value = word.partition("=")
        if word == "--json":
            opts["json"] = True
        elif word == "--id" or name == "--id":
            if eq:
                opts["ids"].append(value)
            else:
                opts["ids"].append(rest[i + 1])
                i += 1
        elif word in TAKES or name in TAKES:
            if eq:
                opts[TAKES[name]] = value
            else:
                opts[TAKES[word]] = rest[i + 1]
                i += 1
        elif word.startswith("--"):
            print("planted gov: unknown option " + word, file=sys.stderr)
            return 2
        else:
            positional.append(word)
        i += 1
    if len(positional) != 1:
        print("planted gov: one query expected", file=sys.stderr)
        return 2
    query = positional[0]
    with open(answers_path, encoding="utf-8") as handle:
        answers = json.load(handle)
    answer = answers.get(query)
    if answer is None:
        return _fail("STORE_MISSING", "no canned answer for this query")
    if answer.get("fail"):
        return _fail("STORE_MISSING", answer["fail"])
    bundles = answer["bundles"]
    index = 0
    if opts.get("continue") is not None:
        valid = {_token(query, n): n for n in range(1, len(bundles))}
        if opts["continue"] not in valid:
            return _fail("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle")
        index = valid[opts["continue"]]
    evidence = bundles[index]
    token = _token(query, index + 1) if index + 1 < len(bundles) else None
    used = sum(-(-len(item["text"]) // 4) for item in evidence)
    limit = int(opts.get("bundle_budget") or 6000)
    result = {"stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS" if token else "SATURATED",
              "evidence": evidence, "batches": [{"size": len(evidence)}],
              "merge": {"candidates": len(evidence), "duplicates": 0, "dropped": [], "reranked": False},
              "expansions": [], "gaps": [], "facets": {"lexical": {"available": True, "reason": None},
                                                       "semantic": {"available": True, "reason": None}},
              "budget": {"bundle": {"limit": limit, "used": used}, "rounds": {"limit": 1, "used": 0}},
              "continuation": token}
    if opts["json"]:
        print(json.dumps({"ok": True, "command": "retrieve", "result": result, "session": None}))
    else:
        print(json.dumps(result, indent=2))
    return 0
'''

PLANTED_EXECUTABLE = "#!@PYTHON@\nimport sys\nimport gov\nsys.exit(gov.main(@ANSWERS@, @LOG@))\n"


def token(query, n):
    """The planted gov's continuation token for the ``n``-th bundle (1-based after the first) of ``query``."""
    return "tok-%d-%s" % (n, hashlib.sha256(query.encode()).hexdigest()[:8])


# --------------------------------------------------------------------------
# Processes
# --------------------------------------------------------------------------

def python_path():
    """The measure's PYTHONPATH: the runner's own (DEC-732), else this worktree's src."""
    return os.environ.get("PYTHONPATH") or str(SRC)


def git(directory, *args):
    proc = subprocess.run(["git", "-C", str(directory), "-c", "user.name=W2-61 acceptance",
                           "-c", "user.email=w2-61@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=TIMEOUT_S,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    def describe(self):
        return (f"{' '.join(map(str, self.args))}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-3000:]}\n"
                f"stderr:\n{self.stderr[-3000:]}")

    def json(self):
        assert self.returncode == 0, f"the measure did not end with 0\n{self.describe()}"
        try:
            document = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"--json printed no single JSON document\n{self.describe()}") from None
        assert isinstance(document, dict), f"--json printed no JSON object\n{self.describe()}"
        return document


# --------------------------------------------------------------------------
# The world: a planted repository, a planted gov, a home and a temp folder
# --------------------------------------------------------------------------

@dataclass
class World:
    base: Path
    repo: Path
    home: Path
    tmp: Path
    planted: Path        # the planted gov's own files (its answers and its log): not the measure's writes
    venv: Path
    gov: Path
    package_file: Path
    answers: dict = field(default_factory=dict)

    @property
    def answers_file(self):
        return self.planted / "answers.json"

    @property
    def log_file(self):
        return self.planted / "calls.jsonl"

    # -- files -------------------------------------------------------------

    def write(self, rel, text, repo=None):
        return write((repo or self.repo) / rel, text)

    def question(self, name, data, bundles=None, fail=None, part="visible", set_name=SET, repo=None):
        """Write one question file and its canned answer: ``bundles`` is a list of evidence lists."""
        rel = f"fixtures/evaluation/{set_name}/{part}/{name}.yaml"
        self.write(rel, yaml.safe_dump(data, sort_keys=False), repo=repo)
        query = data.get("question") if isinstance(data, dict) else None
        if isinstance(query, str):
            self.answer(query, bundles, fail)
        return rel

    def answer(self, query, bundles=None, fail=None):
        self.answers[query] = {"fail": fail} if fail else {"bundles": bundles if bundles is not None else [[]]}

    def commit(self, repo=None, message="W2-61 fixture"):
        repo = repo or self.repo
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "--allow-empty", "-m", message)
        return git(repo, "rev-parse", "HEAD").strip()

    def head(self, repo=None):
        return git(repo or self.repo, "rev-parse", "HEAD").strip()

    # -- evidence ----------------------------------------------------------

    def lines(self, rel, repo=None):
        return ((repo or self.repo) / rel).read_text(encoding="utf-8").splitlines()

    def span(self, rel, heading, repo=None):
        """The span of a Markdown heading as the ticket's brief states it (to the line before the next heading of
        the same or a higher level). Used only to place the planted gov's items."""
        lines = self.lines(rel, repo)
        first = lines.index(heading) + 1
        level = len(heading) - len(heading.lstrip("#"))
        last = len(lines)
        for number in range(first + 1, len(lines) + 1):
            text = lines[number - 1]
            if re.match(r"#{1,6} ", text) and len(text) - len(text.lstrip("#")) <= level:
                last = number - 1
                break
        return first, last

    def item(self, rel, first=None, last=None, text=None, repo=None):
        """One evidence item in ``gov retrieve``'s form."""
        lines = self.lines(rel, repo) if ((repo or self.repo) / rel).is_file() else []
        first = 1 if first is None else first
        last = (len(lines) or 1) if last is None else last
        if text is None:
            text = "\n".join(lines[first - 1:last]) + "\n" if lines else f"{rel}\n"
        digest = hashlib.sha256(f"{rel}:{first}:{last}:{text}".encode()).hexdigest()
        return {"id": rel, "sha256": hashlib.sha256(text.encode()).hexdigest(), "path": rel, "start_line": first,
                "end_line": last, "text": text, "chunk_id": digest[:16], "routes": ["semantic"], "batch": 1}

    def section(self, rel, heading, repo=None):
        first, last = self.span(rel, heading, repo)
        return self.item(rel, first, last, repo=repo)

    def noise(self, n):
        return self.item(f"docs/noise/n{n:02d}.md")

    # -- runs --------------------------------------------------------------

    def environment(self, role="orchestrator", ticket=OTHER_TICKET, path_first=None):
        path = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
        if path_first is not None:
            path = f"{path_first}{os.pathsep}{path}"
        env = {
            "PATH": path, "HOME": str(self.home), "TMPDIR": str(self.tmp), "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8", "TZ": "UTC", "PYTHONPATH": python_path(), "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
        }
        if role is not None:
            env["GOV_ROLE"] = role
        if ticket is not None:
            env["GOV_TICKET"] = ticket
        return env

    def measure(self, *args, role="orchestrator", ticket=OTHER_TICKET, gov=True, root=True, cwd=None,
                path_first=None, timeout=TIMEOUT_S):
        """Run the measure: ``python3 -m gov.retrieval.measure <args>`` with this worktree's src."""
        write(self.answers_file, json.dumps(self.answers, indent=1))
        argv = [sys.executable, "-m", MEASURE, *map(str, args)]
        if root:
            argv += ["--root", str(self.repo)]
        if gov:
            argv += ["--gov", str(self.gov)]
        try:
            done = subprocess.run(argv, cwd=str(cwd or self.repo), env=self.environment(role, ticket, path_first),
                                  capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"the measure did not end within {timeout:.0f} s: {argv}") from None
        return Run(tuple(argv), done.returncode, done.stdout, done.stderr)

    def calls(self):
        """The planted gov's logged retrieve calls, in order."""
        if not self.log_file.is_file():
            return []
        entries = [json.loads(line) for line in self.log_file.read_text(encoding="utf-8").splitlines() if line]
        return [entry for entry in entries if entry["argv"][:1] == ["retrieve"]]

    def all_calls(self):
        if not self.log_file.is_file():
            return []
        return [json.loads(line) for line in self.log_file.read_text(encoding="utf-8").splitlines() if line]

    def clear_calls(self):
        if self.log_file.exists():
            self.log_file.unlink()

    # -- what the measure writes -------------------------------------------

    def snapshot(self):
        """Every file under the world's base folder (the repository, home, temp, out folders), with its state;
        the planted gov's own files, its environment and git's own folder (whose index names the committed
        planted paths, and which a ``git status`` may refresh) are left out."""
        found = {}
        for path in self.base.rglob("*"):
            if self.planted in path.parents or path == self.planted:
                continue
            if self.venv in path.parents:
                continue
            if ".git" in path.relative_to(self.base).parts:
                continue
            if path.is_file() and not path.is_symlink():
                stat = path.stat()
                found[path] = (stat.st_size, stat.st_mtime_ns)
        return found

    def written_since(self, before):
        after = self.snapshot()
        return sorted(path for path, state in after.items() if before.get(path) != state)


def make_world(tmp_path, files=None, commit=True):
    """A planted repository with the planted sets' documents, and a planted gov in a pip-less venv."""
    base = Path(tmp_path).resolve()
    repo, home, tmp, planted = base / "repo", base / "home", base / "systmp", base / "planted"
    for folder in (repo, home, tmp, planted):
        folder.mkdir(parents=True, exist_ok=True)
    venv = base / "v"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True, capture_output=True,
                   timeout=TIMEOUT_S, env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    python = venv / "bin" / "python3"
    purelib = subprocess.run([str(python), "-I", "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                             check=True, capture_output=True, text=True, timeout=TIMEOUT_S).stdout.strip()
    package_file = write(Path(purelib) / "gov" / "__init__.py",
                         PLANTED_PACKAGE.replace("@VERSION@", repr(PLANTED_VERSION)))
    gov = base / "bin" / "gov"
    write(gov, PLANTED_EXECUTABLE.replace("@PYTHON@", str(python))
          .replace("@ANSWERS@", repr(str(planted / "answers.json"))).replace("@LOG@", repr(str(planted / "calls.jsonl"))))
    gov.chmod(0o755)
    world = World(base, repo, home, tmp, planted, venv, gov, package_file)
    held_out = base / "held-out-material"
    write(held_out / "answers.md", "stand-in held-out material\n")
    contents = base_files()
    contents[HELD_OUT_LIST_REL] = yaml.safe_dump({"held_out_paths": [str(held_out)]})
    contents.update(files or {})
    for rel, text in contents.items():
        world.write(rel, text)
    (repo / GUARD_REL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GUARD_SOURCE, repo / GUARD_REL)
    git(repo, "init", "-q", "-b", "main")
    if commit:
        world.commit(message="W2-61 fixture: the planted project")
    return world


def make_plain_repo(path, files):
    """A second repository from scratch (``--sets-root`` cases)."""
    path = Path(path).resolve()
    for rel, text in files.items():
        write(path / rel, text)
    git(path, "init", "-q", "-b", "main")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "W2-61 fixture: a second repository")
    return path


# --------------------------------------------------------------------------
# The standard scenario: four visible questions of planted-memory
# --------------------------------------------------------------------------

def standard_questions(world):
    """v01: the governing source at rank 2 (hit). v02: two pieces, the second only in the second batch (hit, full).
    v03: the report, a fixture and a test quote the answer at ranks 1-5, the governing source at rank 6 (no hit,
    in the bundle, full). v04: never retrieved (nothing). Totals: hit@5 2 of 4, full evidence 3 of 4."""
    dec = DECISIONS
    world.question("v01", {"question": "What is the packet ceiling?", "gold_answer": "six thousand tokens",
                           "sources": [{"path": dec, "heading": "## DEC-1 The packet ceiling"}]},
                   [[world.noise(1), world.section(dec, "## DEC-1 The packet ceiling"), world.noise(2)]])
    world.question("v02", {"question": "How is the archive kept?", "gold_answer": "read-only, by archive()",
                           "sources": [{"path": dec, "heading": "## DEC-2 The archive"}, {"path": ARCHIVE_CODE}]},
                   [[world.noise(1), world.noise(2), world.section(dec, "## DEC-2 The archive")],
                    [world.noise(3), world.item(ARCHIVE_CODE, 1, 2)]])
    world.question("v03", {"question": "What does the gate need?", "gold_answer": GATE_ANSWER,
                           "sources": [{"path": dec, "heading": "## DEC-3 The gate"}]},
                   [[world.item(REPORT), world.item(FIXTURE_QUOTE), world.item(TEST_QUOTE), world.noise(1),
                     world.noise(2), world.section(dec, "## DEC-3 The gate"), world.noise(3)]])
    world.question("v04", {"question": "How does a session resume?", "gold_answer": "from its last checkpoint",
                           "sources": [{"path": dec, "heading": "## DEC-4 The resume"}]},
                   [[world.noise(4), world.noise(5)]])


def hidden_questions(world, set_name=SET):
    """h01: hit at rank 2; h02: a miss. Every word of them is a planted hidden word."""
    world.question("h01", {"question": f"{HIDDEN_QUESTION} one?", "gold_answer": f"{HIDDEN_ANSWER} one",
                           "sources": [{"path": HIDDEN_SOURCE, "heading": HIDDEN_HEADING}],
                           "category": f"{HIDDEN_UNKNOWN} category", "explanation": HIDDEN_UNKNOWN},
                   [[world.item(HIDDEN_ITEM_PATH), world.section(HIDDEN_SOURCE, HIDDEN_HEADING)]],
                   part="hidden", set_name=set_name)
    world.question("h02", {"question": f"{HIDDEN_QUESTION} two?", "gold_answer": f"{HIDDEN_ANSWER} two",
                           "sources": [{"path": HIDDEN_SOURCE, "heading": HIDDEN_HEADING}]},
                   [[world.item(HIDDEN_ITEM_PATH)]], part="hidden", set_name=set_name)


# --------------------------------------------------------------------------
# Reading the measure's output
# --------------------------------------------------------------------------

def questions(document):
    found = document.get("questions")
    assert isinstance(found, list), f"the document has no list of questions: {sorted(document)}"
    return found


def question(document, qid):
    found = [q for q in questions(document) if isinstance(q, dict) and q.get("id") == qid]
    assert len(found) == 1, f"question {qid} is not given once: {[q.get('id') for q in questions(document)]}"
    return found[0]


def objects(value):
    """Every JSON object in a document, itself included."""
    if isinstance(value, dict):
        yield value
        for inner in value.values():
            yield from objects(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from objects(inner)


HIT_LABEL = re.compile(r"hit\s*(@|_at_|\sat\s)\s*5", re.I)
FULL_LABEL = re.compile(r"full[ _-]?evidence", re.I)


def lone_figures(text):
    """The text lines that give one figure without the other (DEC-833 item 3)."""
    return [line for line in text.splitlines()
            if bool(HIT_LABEL.search(line)) != bool(FULL_LABEL.search(line))]


def lone_objects(document):
    """The JSON objects that give one figure without the other."""
    return [sorted(o) for o in objects(document) if ("hit_at_5" in o) != ("full_evidence" in o)]


def options(argv):
    """A logged ``retrieve`` call's arguments: ``{"query": ..., "--batch-size": [...], "--id": [...], ...}``.
    Both ``--opt value`` and ``--opt=value`` are read; ``--json`` is counted under ``"--json"``."""
    found, rest, i = {"query": []}, list(argv[1:]), 0
    while i < len(rest):
        word = rest[i]
        name, eq, value = word.partition("=")
        if word == "--json":
            found.setdefault("--json", []).append(True)
        elif word.startswith("--") and eq:
            found.setdefault(name, []).append(value)
        elif word.startswith("--") and i + 1 < len(rest):
            found.setdefault(word, []).append(rest[i + 1])
            i += 1
        else:
            found["query"].append(word)
        i += 1
    return found


def records_in(folder):
    """The JSON files in a folder (the measure's ``--out`` records), parsed."""
    folder = Path(folder)
    if not folder.is_dir():
        return {}
    return {path: json.loads(path.read_text(encoding="utf-8")) for path in sorted(folder.rglob("*.json"))}


# --------------------------------------------------------------------------
# The guard (W2-58's way)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Call:
    tool: str
    input: dict
    label: str

    def __str__(self):
        return self.label


def read_call(path):
    return Call("Read", {"file_path": str(path)}, f"Read {path}")


def grep_call(path=None, pattern="zqxw61"):
    data = {"pattern": pattern, "output_mode": "content"}
    if path is not None:
        data["path"] = str(path)
    return Call("Grep", data, f"Grep {pattern!r} in {path}")


def glob_call(pattern, path=None):
    data = {"pattern": pattern}
    if path is not None:
        data["path"] = str(path)
    return Call("Glob", data, f"Glob {pattern!r} in {path}")


def bash_call(command):
    return Call("Bash", {"command": command, "description": "W2-61 acceptance call"}, f"Bash `{command}`")


def ask_guard(world, call, role, ticket):
    """The guard's decision (allow, ask, deny or error) on one call of a session of ``role`` on ``ticket``."""
    data = {"session_id": "w2-61-acceptance", "transcript_path": str(world.base / "transcript.jsonl"),
            "cwd": str(world.repo), "permission_mode": "default", "hook_event_name": "PreToolUse",
            "tool_name": call.tool, "tool_input": call.input, "tool_use_id": "toolu_w2_61_000001"}
    env = world.environment(role, ticket)
    env["CLAUDE_PROJECT_DIR"] = str(world.repo)
    try:
        proc = subprocess.run([sys.executable, str(world.repo / GUARD_REL)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=str(world.repo), env=env, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "error", "timed out"
    if proc.returncode == 2:
        return "deny", proc.stderr.strip()
    if proc.returncode != 0:
        return "error", proc.stderr.strip()
    try:
        data = json.loads(proc.stdout.strip() or "null")
    except ValueError:
        return "allow", ""
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    if isinstance(specific, dict) and specific.get("permissionDecision") in ("deny", "ask"):
        return specific["permissionDecision"], str(specific.get("permissionDecisionReason") or "")
    return "allow", ""


# --------------------------------------------------------------------------
# Lens B's Table 2 (the visible half's reference)
# --------------------------------------------------------------------------

def lens_b_commands():
    """``{"Q01": {"question": ..., "ticket": ..., "ids": [...], "radius": int}, ...}`` from Table 2's Command
    column of lens B's report, parsed here from the report itself."""
    import shlex

    found = {}
    for line in LENS_B.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\|\s*(Q\d\d)\s*\|[^|]*\|\s*`retrieve ([^`]*)`\s*\|", line)
        if not match:
            continue
        words = shlex.split(match.group(2))
        entry = {"question": None, "ticket": None, "ids": [], "radius": 0}
        i = 0
        while i < len(words):
            if words[i] == "--ticket":
                entry["ticket"] = words[i + 1]
                i += 2
            elif words[i] == "--id":
                entry["ids"].append(words[i + 1])
                i += 2
            elif words[i] == "--radius":
                entry["radius"] = int(words[i + 1])
                i += 2
            else:
                entry["question"] = words[i]
                i += 1
        found[match.group(1)] = entry
    return found
