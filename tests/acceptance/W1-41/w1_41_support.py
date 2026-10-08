"""Support code for the W1-41 acceptance tests (standard library, PyYAML, and W1-07's support).

W1-41 builds the adoption tool, ``gov adopt --lite``. It adopts nothing: every
case runs the tool on a project the case builds itself, file by file, in a
temporary folder, as a git repository of its own. ``run_adopt`` refuses to run
the tool on this repository, on a folder inside it, or on a worktree of it.

- **No copy of this repository.** The project is written from the texts in
  this file. Its path map is written here from the kernel's schema
  (``template/governance/kernel/schemas/path-map.schema.json``); nothing under
  ``governance/project/`` of this repository is read, listed or copied.
- **The code under test** is this worktree's ``gov`` package, reached through
  the launcher W1-07's support writes (``[project.scripts] gov``), with
  ``src/`` on the child's ``PYTHONPATH``. The suite itself needs none.
- **The environment is built from scratch:** ``PATH``, an empty temporary
  ``HOME``, ``TMPDIR``, a git identity (the tool commits its records and its
  batches). The session's ``GOV_ROLE`` and ``GOV_TICKET`` are not passed on.
- **No model, no network.** The A5 verdict is a record the case writes and
  commits as the Independent Auditor would (``Role: independent-auditor``).
- **Refs** (backup ref, rollback points, archive ref) are created by the tool
  in the temporary project only.

The interface the cases hold is in ``README.md`` ("The interface").
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_W1_07_DIR = str(Path(__file__).resolve().parents[1] / "W1-07")
if _W1_07_DIR not in sys.path:
    sys.path.insert(0, _W1_07_DIR)

import w1_07_support as base  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]

git = base.git
make_sandbox = base.make_sandbox
snapshot = base.snapshot
snapshot_difference = base.snapshot_difference
git_state = base.git_state
porcelain = base.porcelain

# --- what the sources fix -------------------------------------------------
STAGES = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")       # DEC-090: Wave 1 delivers these eight
ACTIONS = ("KEEP", "MOVE", "RENAME", "SPLIT", "MERGE", "EXTRACT", "RETIRE", "DELETE_FROM_ACTIVE_TREE")  # CAP-06.b
DESTRUCTIVE = ("MOVE", "RENAME", "SPLIT", "MERGE", "EXTRACT", "RETIRE", "DELETE_FROM_ACTIVE_TREE")
AUDITOR_ROLE = "independent-auditor"                            # CAP-44.c, DEC-090; the kernel role file's name
RECORD_ID_RE = re.compile(r"^[A-Z]{1,6}-[A-Za-z0-9._-]+$")      # common.schema.json, record_id
PATH_MAP_REL = "governance/project/path-map.yaml"               # DEC-185: where gov reads a project's path map
RULESYNC_REL = ".rulesync"                                      # ADR-0002 section 5; the ticket's third success line
CODE_INDEX_TOOL = "codebase-memory-mcp"                         # W1-16: the code graph's tool
NOT_BUILT_CODES = ("NOT_IMPLEMENTED", "COMMAND_MODULE_INVALID")
REFUSAL_EXIT_CODES = (1, 3, 4)                                  # API-0002: every non-zero code but the usage error
COMMAND_TIMEOUT_S = 180.0
ADOPTER_SESSION = "adopter-001"
AUDITOR_SESSION = "auditor-001"
DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()

# --- the legacy project ----------------------------------------------------
# Each legacy text holds a phrase found nowhere else in the project: what the import must carry into .rulesync/.
CURSORRULES_PHRASE = "answer about the heron ledger in short lines"
WINDSURF_PHRASE = "never touch the saffron gateway without a ticket"
MDC_STYLE_PHRASE = "use the cedar naming scheme"
MDC_REVIEW_PHRASE = "every review cites the walnut checklist"
ROLE_REVIEWER_PHRASE = "the reviewer reads the plum checklist"
ROLE_BUILDER_PHRASE = "the builder follows the maple procedure"
MCP_SERVER, MCP_COMMAND = "ledger", "ledger-mcp"
MEMORY_PHRASE = "the tangerine quorum rule"

AGENTS_MD = (
    "# Agents\n\nLegacy instructions of the harbour project.\n\n"
    f"## Role: reviewer\n\n{ROLE_REVIEWER_PHRASE.capitalize()}.\n\n"
    f"## Role: builder\n\n{ROLE_BUILDER_PHRASE.capitalize()}.\n"
)
CURSORRULES = f"{CURSORRULES_PHRASE.capitalize()}.\n"
WINDSURFRULES = f"{WINDSURF_PHRASE.capitalize()}.\n"
MDC_STYLE = f"---\ndescription: style\nglobs: '**/*.py'\nalwaysApply: false\n---\n{MDC_STYLE_PHRASE.capitalize()}.\n"
MDC_REVIEW = f"---\ndescription: review\nalwaysApply: true\n---\n{MDC_REVIEW_PHRASE.capitalize()}.\n"
MCP_TOOLS = json.dumps({"mcpServers": {MCP_SERVER: {"command": MCP_COMMAND, "args": ["--stdio"]}}}, indent=2) + "\n"

RULE_FILES = {                       # the five kinds the ticket's third success line names
    "AGENTS.md": AGENTS_MD,
    ".cursorrules": CURSORRULES,
    ".windsurfrules": WINDSURFRULES,
    ".cursor/rules/style.mdc": MDC_STYLE,
    ".cursor/rules/review.mdc": MDC_REVIEW,
    ".mcp/tools.json": MCP_TOOLS,
}
# kind of legacy file -> (its files, what must be found under .rulesync/ afterwards)
RULE_KINDS = {
    "agents-md-roles": (("AGENTS.md",), (ROLE_REVIEWER_PHRASE, ROLE_BUILDER_PHRASE)),
    "cursorrules": ((".cursorrules",), (CURSORRULES_PHRASE,)),
    "windsurfrules": ((".windsurfrules",), (WINDSURF_PHRASE,)),
    "cursor-mdc": ((".cursor/rules/style.mdc", ".cursor/rules/review.mdc"), (MDC_STYLE_PHRASE, MDC_REVIEW_PHRASE)),
    "mcp-tools": ((".mcp/tools.json",), (MCP_SERVER, MCP_COMMAND)),
}

MEMORY_FILES = ("legacy/memory/decisions/leg-001.md", "legacy/memory/decisions/leg-002.md",
                "legacy/memory/index.md")
MEMORY_DECISION_IDS = ("LEG-001", "LEG-002")
CHAT_DB = "legacy/chat/history.db"
EXTRACTION_REL = "spec/research/ext-0001.md"
EXTRACTION_ID = "EXT-0001"

GUIDE, GUIDE_TARGET = "docs/guide.md", "docs/handbook/guide.md"
NOTES, NOTES_TARGET = "docs/notes.txt", "archive/notes.txt"
UTIL, UTIL_TARGET = "lib/util.py", "modules/util.py"
UTIL_IMPORTER = "scripts/run.py"
MOVED_RECORD, MOVED_RECORD_TARGET, MOVED_RECORD_ID = "notes/dec-300.md", "spec/decisions/dec-300.md", "DEC-300"
CITING_RECORD, CITING_RECORD_ID = "spec/decisions/dec-301.md", "DEC-301"
RECORD_CONSUMER = "scripts/run.py"
NATIVE_FILE, NATIVE_TARGET = "src/app/core.py", "modules/core.py"
UNKNOWN = "vault/ledger.bin"         # a tracked path no namespace of the project's path map holds
VERDICT_REL = "audit/adoption/a5-verdict.md"

_SYSTEMS = (
    "constitution-and-policies", "knowledge-fabric", "repository-contract", "agent-organisation", "skills",
    "tools-and-capabilities", "command-surface", "model-adapters", "orchestration-and-handoffs",
    "specification-and-planning", "research-and-experiments", "task-system", "product-delivery",
    "verification-and-governance-tests", "change-impact-control", "checkpoint-and-recovery",
    "observability-and-cost", "organisational-learning", "independent-audit", "security-and-permissions",
    "budget-governance", "emergency-stop-and-rollback",
)
_HARD = ("security", "authority", "test", "change", "human_gate", "tool")
_SOFT = ("memory", "context", "checkpoint", "model_routing", "budget", "learning", "archive")
# Every folder the project uses, and every target a case moves to. ``vault/`` is left out on purpose.
NAMESPACE_PATHS = (
    ".gitignore", ".gitleaks.toml", "README.md", "pyproject.toml", "AGENTS.md", "CLAUDE.md", ".cursorrules",
    ".windsurfrules", ".cursor/**", ".mcp/**", ".rulesync/**", "governance/**", "src/**", "lib/**", "scripts/**", "docs/**",
    "notes/**", "spec/**", "legacy/**", "audit/**", "archive/**", "modules/**", "locked/**",
)


def path_map(patterns=NAMESPACE_PATHS, code_intelligence=True):
    """A path map valid against the kernel's schema, written from that schema."""
    capability = {"enabled": True, "languages": ["python"]} if code_intelligence else {"enabled": False}
    return {
        "state_class": "AUTHORITATIVE",
        "namespaces": {"harbour": {
            "paths": list(patterns), "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["orchestrator", "engineer", "independent-auditor"],
            "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "not embedded",
            "provenance": "written by the W1-41 tests", "deletion_rebuild": "authoritative; restored from git only",
        }},
        "capabilities": {"code_intelligence": capability, "research_corpus": {"enabled": False}},
        "policies": {**{key: "hard-block" for key in _HARD}, **{key: "warning" for key in _SOFT}},
        "systems": {name: {"status": "absent", "reason": "a legacy project before adoption"} for name in _SYSTEMS},
    }


def record_text(record_id, kind, status, body="A record of the harbour project.", **keys):
    front = {"id": record_id, "type": kind, "status": status, "state_class": keys.pop("state_class", "AUTHORITATIVE"),
             **keys}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\n{body}\n"


def chat_database_bytes(destination):
    """A raw chat database stand-in: a small SQLite file. The tool is never asked to understand it."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(destination)
    try:
        connection.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, author TEXT, body TEXT)")
        connection.executemany("INSERT INTO messages (author, body) VALUES (?, ?)", [
            ("owner", "The quay crane is serviced on the first Monday."),
            ("agent", "Noted: the indigo tariff applies to berth four only."),
        ])
        connection.commit()
    finally:
        connection.close()
    return destination.read_bytes()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def base_files():
    """Path -> text of the legacy project every case starts from (the chat database is written apart)."""
    files = {
        ".gitignore": ".gov-runtime/\n__pycache__/\n*.pyc\n",
        ".gitleaks.toml": 'title = "Minimal gitleaks configuration"\n\n[extend]\nuseDefault = true\n',
        PATH_MAP_REL: yaml.safe_dump(path_map(), sort_keys=False),
        "README.md": "# Harbour\n\nA legacy project, built by the W1-41 tests.\n",
        # A healthy native package layout (CAP-44.j): a src layout declared in pyproject.toml.
        "pyproject.toml": ('[build-system]\nrequires = ["setuptools>=68"]\nbuild-backend = "setuptools.build_meta"\n\n'
                           '[project]\nname = "app"\nversion = "0.1.0"\n\n'
                           '[tool.setuptools.packages.find]\nwhere = ["src"]\n'),
        "src/app/__init__.py": '"""The harbour application."""\n',
        NATIVE_FILE: "def compute(berths):\n    return berths * 2\n",
        # A loose module outside the package, and the script that imports it.
        "lib/__init__.py": '"""Loose helpers."""\n',
        UTIL: "def helper():\n    return 41\n",
        UTIL_IMPORTER: "from lib.util import helper\n\n\ndef main():\n    return helper()\n",
        GUIDE: "# Guide\n\nHow the harbour is run.\n",
        NOTES: "Tide tables are kept by the harbour master.\n",
        MOVED_RECORD: record_text(MOVED_RECORD_ID, "decision", "ACTIVE", "Berths are numbered from the north.",
                                  consumers=[RECORD_CONSUMER]),
        CITING_RECORD: record_text(CITING_RECORD_ID, "decision", "ACTIVE", "Berth four takes the indigo tariff.",
                                   depends_on=[MOVED_RECORD_ID]),
        f"{RULESYNC_REL}/rules/overview.md": "---\nroot: true\ntargets:\n  - '*'\n---\n# Harbour\n\nFollow the kernel.\n",
        "legacy/memory/decisions/leg-001.md": record_text(
            "LEG-001", "decision", "ACTIVE", f"{MEMORY_PHRASE.capitalize()} holds for every vote."),
        "legacy/memory/decisions/leg-002.md": record_text(
            "LEG-002", "decision", "ACTIVE", "The slate ballot is counted twice."),
        "legacy/memory/index.md": "# Legacy memory\n\n- LEG-001\n- LEG-002\n",
    }
    files.update(RULE_FILES)
    return files


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def commit(project, message, *trailers):
    """Commit everything; ``trailers`` are given to ``git commit --trailer`` (DEC-182). Returns the commit."""
    git(project, "add", "-A")
    args = ["commit", "-q", "--allow-empty", "-m", message]
    for trailer in trailers:
        args += ["--trailer", trailer]
    git(project, *args)
    return head(project)


def head(project):
    return git(project, "rev-parse", "HEAD").strip()


def build_project(destination, extraction=True, without=(), extra=None, patterns=NAMESPACE_PATHS,
                  path_map_file=True, code_intelligence=True):
    """The legacy project, committed, as a git repository of its own. Returns its root.

    ``without`` names files left out, ``extra`` maps further paths to their content, ``extraction`` adds the record
    that holds what was extracted from the chat database, citing it by path and content hash.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    files = base_files()
    files[PATH_MAP_REL] = yaml.safe_dump(path_map(patterns, code_intelligence), sort_keys=False)
    if not path_map_file:
        del files[PATH_MAP_REL]
    for rel, text in files.items():
        if rel not in without:
            write(destination, rel, text)
    if CHAT_DB not in without:
        data = chat_database_bytes(destination / CHAT_DB)
        if extraction:
            write(destination, EXTRACTION_REL, extraction_record(data))
    for rel, text in (extra or {}).items():
        write(destination, rel, text)
    git(destination, "init", "-q", "-b", "main")
    commit(destination, "the legacy project")
    return destination


def extraction_record(database_bytes, record_id=EXTRACTION_ID):
    """A record of knowledge extracted from the chat database: it cites the database by path and content hash."""
    return record_text(record_id, "extraction", "ACTIVE", "Berth four alone takes the indigo tariff.",
                       state_class="EVIDENCE", extracted_from={"path": CHAT_DB, "sha256": sha256(database_bytes)})


# --------------------------------------------------------------------------
# Proposals: what the caller gives stage A3
# --------------------------------------------------------------------------

def entry(path, action, target=None, batch=None, **more):
    made = {"path": path, "action": action}
    if target is not None:
        made["targets" if isinstance(target, (list, tuple)) else "target"] = (
            list(target) if isinstance(target, (list, tuple)) else target)
    if batch is not None:
        made["batch"] = batch
    made.update(more)
    return made


def rule_entries():
    return [entry(rel, "RETIRE", kind="rule-file") for rel in RULE_FILES]


def memory_entries():
    return [entry(rel, "RETIRE", kind="memory-store") for rel in MEMORY_FILES]


def chat_entry():
    return entry(CHAT_DB, "RETIRE", kind="chat-database")


def legacy_proposal():
    """Everything legacy is retired; nothing is moved (so no artefact needs the code graph)."""
    return rule_entries() + memory_entries() + [chat_entry()]


def moves_proposal():
    """Three move batches. Batch 2 holds two moves, batch 3 a code file with an importer."""
    return [
        entry(GUIDE, "MOVE", GUIDE_TARGET, batch=1),
        entry(NOTES, "MOVE", NOTES_TARGET, batch=2),
        entry(MOVED_RECORD, "MOVE", MOVED_RECORD_TARGET, batch=2),
        entry(UTIL, "MOVE", UTIL_TARGET, batch=3),
    ]


def write_proposal(sandbox, entries, name="proposal.yaml"):
    """The proposal file, outside the project (the project's tree stays clean)."""
    path = Path(sandbox.elsewhere) / name
    path.write_text(yaml.safe_dump({"artefacts": list(entries)}, sort_keys=False), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Running the tool
# --------------------------------------------------------------------------

def _inside(path, folder):
    try:
        Path(path).resolve().relative_to(Path(folder).resolve())
        return True
    except ValueError:
        return False


def assert_own_project(project):
    """The tool is never run on this repository, a folder of it, or a worktree of it."""
    project = Path(project).resolve()
    assert not _inside(project, REPO_ROOT) and not _inside(REPO_ROOT, project), \
        f"gov adopt is never run on this repository or inside it: {project}"
    common = subprocess.run(["git", "-C", str(project), "rev-parse", "--git-common-dir"], capture_output=True,
                            text=True)
    if common.returncode == 0:
        own = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--git-common-dir"], capture_output=True,
                             text=True).stdout.strip()
        there = (project / common.stdout.strip()).resolve()
        assert there != (REPO_ROOT / own).resolve(), f"{project} is a worktree of this repository"


def path_without(commands, farm):
    """A ``PATH`` on which none of ``commands`` is found; everything else the folders offer stays."""
    kept, seen = [], set()
    folders = [str(Path(sys.executable).parent), *os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)]
    for number, folder in enumerate(folders):
        folder = Path(folder)
        try:
            resolved, names = folder.resolve(), sorted(os.listdir(folder))
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if not any(name in commands for name in names):
            kept.append(str(folder))
            continue
        links = Path(farm) / str(number)
        links.mkdir(parents=True, exist_ok=True)
        for name in names:
            if name not in commands and not (links / name).exists():
                os.symlink(folder / name, links / name)
        kept.append(str(links))
    return os.pathsep.join(kept)


def environment(sandbox, without=()):
    folders = [str(Path(sys.executable).parent), *os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)]
    path = path_without(tuple(without), Path(sandbox.elsewhere) / "path-without") if without \
        else os.pathsep.join(folders)
    return {
        "PATH": path,
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(REPO_ROOT / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-41 tests", "GIT_AUTHOR_EMAIL": "w1-41@example.invalid",
        "GIT_COMMITTER_NAME": "W1-41 tests", "GIT_COMMITTER_EMAIL": "w1-41@example.invalid",
    }


def run_gov(project, sandbox, *args, without=()):
    """``gov <args>`` with this worktree's code, in ``project`` (never this repository)."""
    assert_own_project(project)
    launcher = base.write_launcher(REPO_ROOT, sandbox)
    started = time.perf_counter()
    try:
        done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(project),
                              env=environment(sandbox, without), capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {COMMAND_TIMEOUT_S:.0f} s") from None
    return base.Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def not_built(run):
    """Whether the run says the command (or its module) is not there: the red reason before implementation."""
    try:
        error = json.loads(run.stdout).get("error") or {}
    except (ValueError, AttributeError):
        return False
    return error.get("code") in NOT_BUILT_CODES


def assert_refused(run, interface, *names, any_of=()):
    """The tool refused, for a reason of its own, and its answer names every one of ``names``
    (and at least one of ``any_of``). A usage error or "not built" is no refusal. Returns the error object."""
    assert not not_built(run), f"gov adopt --lite is not built: it answers that it is reserved\n{run.describe()}"
    envelope = base.assert_envelope(run, interface, command="adopt")
    assert envelope["ok"] is False, f"expected a refusal, but the tool reports success\n{run.describe()}"
    assert run.returncode in REFUSAL_EXIT_CODES, \
        f"a refusal ends with one of {REFUSAL_EXIT_CODES}, never 0 or the usage error\n{run.describe()}"
    said = json.dumps(envelope["error"])
    for name in names:
        assert name in said, f"the refusal does not name {name!r}\n{run.describe()}"
    if any_of:
        assert any(name in said for name in any_of), f"the refusal names none of {list(any_of)}\n{run.describe()}"
    return envelope["error"]


def frontmatter(text, where="the record"):
    """The frontmatter of a Markdown record as a dict; an assertion error where it cannot be read."""
    lines = text.split("\n")
    assert lines and lines[0].strip() == "---", f"{where} has no frontmatter"
    assert "---" in [line.strip() for line in lines[1:]], f"{where}: the frontmatter is not closed"
    end = [line.strip() for line in lines[1:]].index("---") + 1
    data = yaml.safe_load("\n".join(lines[1:end]))
    assert isinstance(data, dict), f"{where}: the frontmatter is not a mapping"
    return data


def with_frontmatter(text, front):
    """``text``, a Markdown record, with ``front`` as its frontmatter; what follows the frontmatter stays."""
    lines = text.split("\n")
    assert lines and lines[0].strip() == "---", "the record has no frontmatter"
    end = [line.strip() for line in lines[1:]].index("---") + 1
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "\n".join(lines[end:])


def replaced(value, swaps):
    """A copy of ``value`` in which every string, at any depth, holds each key of ``swaps`` as its value."""
    if isinstance(value, dict):
        return {key: replaced(item, swaps) for key, item in value.items()}
    if isinstance(value, list):
        return [replaced(item, swaps) for item in value]
    if isinstance(value, str):
        for old, new in swaps.items():
            value = value.replace(old, new)
    return value


def at_head(project, rel):
    """The bytes of ``rel`` at HEAD, None where HEAD has no such file."""
    done = subprocess.run(["git", "-C", str(project), "show", f"HEAD:{rel}"], capture_output=True)
    return done.stdout if done.returncode == 0 else None


def tree(project, rev="HEAD"):
    """Path -> blob id of every file of the commit ``rev``."""
    listed = {}
    for line in git(project, "ls-tree", "-r", "-z", rev).split("\0"):
        if line:
            meta, _, path = line.partition("\t")
            listed[path] = meta.split()[2]
    return listed


def resolve(project, name):
    """The commit ``name`` resolves to, None where it does not."""
    done = subprocess.run(["git", "-C", str(project), "rev-parse", "--verify", "--quiet", f"{name}^{{commit}}"],
                          capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


@dataclass
class Stage:
    name: str
    run: object
    result: dict
    record: str          # the evidence record's path, relative to the project
    front: dict          # its frontmatter


@dataclass
class Adoption:
    """One adoption of one temporary project: runs stages and keeps what each left."""
    project: Path
    sandbox: object
    interface: object
    session: str = ADOPTER_SESSION
    stages: dict = field(default_factory=dict)
    proposal: Path | None = None

    def run(self, stage, *extra, without=(), session=None):
        return run_gov(self.project, self.sandbox, "adopt", "--lite", "--stage", stage, *extra, "--json",
                       "--session", session or self.session, without=without)

    def ok(self, stage, *extra, without=()):
        """Run the stage; it must succeed and leave its evidence record, committed, in a clean tree."""
        run = self.run(stage, *extra, without=without)
        if not_built(run):
            raise AssertionError(f"gov adopt --lite is not built (stage {stage}): it answers that it is reserved\n"
                                 f"{run.describe()}")
        envelope = base.assert_envelope(run, self.interface, command="adopt")
        assert envelope["ok"] is True, f"stage {stage} did not succeed\n{run.describe()}"
        result = envelope["result"]
        assert result.get("stage") == stage, f"the result does not name the stage {stage}\n{run.describe()}"
        rel = result.get("record")
        assert isinstance(rel, str) and rel and not os.path.isabs(rel), \
            f"the result does not give the evidence record as a path inside the project\n{run.describe()}"
        path = self.project / rel
        assert path.is_file(), f"stage {stage}: the evidence record {rel} does not exist\n{run.describe()}"
        assert at_head(self.project, rel) == path.read_bytes(), \
            f"stage {stage}: the evidence record {rel} is not committed as it stands\n{run.describe()}"
        assert porcelain(self.project) == "", \
            f"stage {stage} left the tree dirty:\n{porcelain(self.project)}\n{run.describe()}"
        front = frontmatter(path.read_text(encoding="utf-8"), rel)
        assert isinstance(front.get("id"), str) and RECORD_ID_RE.match(front["id"]), \
            f"{rel}: the id is not a record id ({front.get('id')!r})"
        assert front.get("type") == "evidence", f"{rel}: type is not 'evidence'"
        assert front.get("state_class") == "EVIDENCE", f"{rel}: state_class is not EVIDENCE"
        assert isinstance(front.get("status"), str) and front["status"], f"{rel}: no status"
        assert front.get("stage") == stage, f"{rel}: the record does not name its stage {stage}"
        self.stages[stage] = Stage(stage, run, result, rel, front)
        return self.stages[stage]

    def map_argument(self, entries):
        self.proposal = write_proposal(self.sandbox, entries)
        return ("--map", str(self.proposal))

    def through(self, last, entries=(), verdict="pass"):
        """Every stage up to and including ``last``, each of which must succeed. The A5 verdict is the case's
        own record, committed as the Independent Auditor commits its report."""
        for stage in STAGES[:STAGES.index(last) + 1]:
            if stage == "A3":
                self.ok(stage, *self.map_argument(entries))
            elif stage == "A5":
                write_verdict(self.project, self.stages["A3"].record, verdict=verdict)
                self.ok(stage, "--verdict", VERDICT_REL)
            else:
                self.ok(stage)
        return self.stages[last]

    def map_entries(self):
        """Path -> entry of the A3 record."""
        return entries_by_path(self.stages["A3"].front, self.stages["A3"].record)


def entries_by_path(front, where):
    listed = front.get("artefacts")
    assert isinstance(listed, list) and listed, f"{where}: no list 'artefacts'"
    found = {}
    for item in listed:
        assert isinstance(item, dict) and isinstance(item.get("path"), str), f"{where}: an artefact without a path"
        assert item["path"] not in found, f"{where}: the artefact {item['path']} is listed twice"
        found[item["path"]] = item
    return found


# --------------------------------------------------------------------------
# The A5 verdict: a record, written and committed as the Independent Auditor does
# --------------------------------------------------------------------------

def map_hash(project, map_rel):
    """The content hash of the path map's record as it stands at HEAD."""
    data = at_head(project, map_rel)
    assert data is not None, f"{map_rel} is not committed"
    return sha256(data)


def verdict_text(project, map_rel, verdict="pass", session=AUDITOR_SESSION, **override):
    front = {
        "id": "AV-0001", "type": "adoption-verdict", "status": "ACTIVE", "state_class": "EVIDENCE", "stage": "A5",
        "verdict": verdict, "path_map": map_rel, "path_map_hash": map_hash(project, map_rel),
        "auditor_session": session,
    }
    for key, value in override.items():
        if value is None:
            front.pop(key, None)
        else:
            front[key] = value
    return ("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# AV-0001: review of the path map\n\n"
            "The Independent Auditor read the path map before any move.\n")


def write_verdict(project, map_rel, verdict="pass", role=AUDITOR_ROLE, session=AUDITOR_SESSION, text=None,
                  rel=VERDICT_REL, **override):
    """Write the verdict and commit it; ``role=None`` commits without a ``Role`` trailer."""
    write(project, rel, text if text is not None else verdict_text(project, map_rel, verdict, session, **override))
    trailers = ["Task: HARB-a5aa"] + ([f"Role: {role}"] if role else [])
    return commit(project, "A5: review of the path map", *trailers)


# --------------------------------------------------------------------------
# Measures
# --------------------------------------------------------------------------

def moved_nothing(project, baseline, origins):
    """No origin of ``origins`` left its place: each holds at HEAD and on disk what the baseline holds."""
    now = tree(project)
    problems = []
    for rel in origins:
        if now.get(rel) != baseline.get(rel):
            problems.append(f"{rel} changed or left HEAD")
        if not (Path(project) / rel).exists():
            problems.append(f"{rel} is gone from the working tree")
    return problems


def doctor_section(project, sandbox, name):
    """One section of ``gov doctor --json`` in the temporary project (from the result, or the error's details)."""
    run = run_gov(project, sandbox, "doctor", "--json")
    try:
        envelope = json.loads(run.stdout)
    except ValueError:
        raise AssertionError(f"gov doctor printed no envelope\n{run.describe()}") from None

    def find(value):
        if isinstance(value, dict):
            if isinstance(value.get(name), dict):
                return value[name]
            for item in value.values():
                found = find(item)
                if found is not None:
                    return found
        elif isinstance(value, list):
            for item in value:
                found = find(item)
                if found is not None:
                    return found
        return None

    section = find(envelope)
    assert section is not None, f"gov doctor reports no section {name!r}\n{run.describe()}"
    return section


def under_rulesync(project):
    """Path -> text of every file under ``.rulesync/`` at HEAD."""
    found = {}
    for rel in tree(project):
        if rel.startswith(RULESYNC_REL + "/"):
            found[rel] = (at_head(project, rel) or b"").decode("utf-8", "replace")
    return found


def phrase_under_rulesync(project, phrase):
    return [rel for rel, text in under_rulesync(project).items() if phrase.lower() in text.lower()]


def make_unreadable(path):
    """Take every permission from ``path``; returns a function that gives them back."""
    path = Path(path)
    mode = stat.S_IMODE(path.stat().st_mode)
    path.chmod(0)
    return lambda: path.chmod(mode)


def can_be_made_unreadable(tmp_path):
    """Whether this user is held by file permissions (root is not)."""
    probe = Path(tmp_path) / "permission-probe"
    probe.write_text("x", encoding="utf-8")
    restore = make_unreadable(probe)
    try:
        probe.read_text(encoding="utf-8")
        return False
    except PermissionError:
        return True
    finally:
        restore()


# --------------------------------------------------------------------------
# The context and the sources that live outside the repository (success line 9; DEC-511, DEC-520)
# --------------------------------------------------------------------------
# W1-24's support calls the context's function and its command, each in a new process, and loads a project's record
# store. Every project here is written file by file in the case's own temporary folder; its path map is the one
# this file writes from the kernel's schema.

_W1_24_DIR = str(Path(__file__).resolve().parents[1] / "W1-24")
if _W1_24_DIR not in sys.path:
    sys.path.insert(0, _W1_24_DIR)

import w1_24_support as context_base  # noqa: E402

EXTERNAL_REFERENCES_REL = "governance/project/external-references.yaml"
F_REFERENCES, F_ID, F_LOCATION, F_REASON = "references", "id", "location", "reason"     # the file's keys
K_EXTERNAL, X_READ = "external", "read"                                                 # the packet's addition
PACKET_KEYS = (context_base.K_TICKET, context_base.K_AUTHORITY, context_base.K_MANDATORY,
               context_base.K_SUPPLEMENTARY, context_base.K_DROPPED, context_base.K_HASH, context_base.K_TOKENS,
               context_base.K_BUDGET)                                                   # W1-24's README, the packet
RECORD_ONLY_KEYS = (context_base.M_SHA, context_base.M_AUTHORITY, context_base.M_LIFECYCLE,
                    context_base.M_CONSTRAINT, "text", "tokens", "path")
REGISTER_KEY, REGISTER_REL = "decision_register", "docs/decision-register.md"           # DEC-473

CHARTER_ID, CHARTER_REL = "CHARTER-H9", "docs/charter/charter.md"
ADR_ID, ADR_REL = "ADR-H9-A", "docs/adr/adr-a.md"
OLD_ADR_ID = "ADR-H9-OLD"
CONTEXT_PATTERNS = ("*", "docs/**", ".tickets/**", "governance/**")


def reference(reference_id, location="the owner's archive of source documents, outside this repository",
              reason="a planning source the owner keeps; it was never a record of this project", **more):
    """One entry of the external references file; a key given as None is left out."""
    made = {F_ID: reference_id, F_LOCATION: location, F_REASON: reason, **more}
    return {key: value for key, value in made.items() if value is not None}


def references_text(entries):
    return yaml.safe_dump({F_REFERENCES: list(entries)}, sort_keys=False)


def context_project(api, destination, tickets, references=None, text=None, register=None):
    """A project with a charter, a decision, a superseded decision and the tickets of ``tickets`` (id -> the ids it
    declares as sources), committed, with its record store loaded. ``references`` (entries) or ``text`` (the
    file's own text) writes the external references file; with neither the project has none. ``register`` is the
    text of a decision register the path map then names (DEC-473)."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    assert_own_project(destination)
    document = path_map(CONTEXT_PATTERNS, code_intelligence=False)
    if register is not None:
        document[REGISTER_KEY] = REGISTER_REL
        write(destination, REGISTER_REL, register)
    files = {
        ".gitignore": ".gov-runtime/\n",
        "README.md": "# Quay\n\nA project built by the W1-41 tests for the context.\n",
        PATH_MAP_REL: yaml.safe_dump(document, sort_keys=False),
        CHARTER_REL: context_base.record(CHARTER_ID, "charter", "ACTIVE", "Every berth has one harbour master."),
        ADR_REL: context_base.record(ADR_ID, "decision", "ACTIVE", "Berths are numbered from the north."),
        "docs/adr/adr-old.md": context_base.record(OLD_ADR_ID, "decision", "SUPERSEDED",
                                                   "Berths were numbered from the south.", superseded_by=ADR_ID),
    }
    for ticket, sources in tickets.items():
        files[f".tickets/{ticket}.md"] = context_base.ticket_file(ticket, sources=sources)
    for rel, content in files.items():
        write(destination, rel, content)
    context_base.git(destination, "init", "-q", "-b", "main")
    set_references(api, destination, references, text, message="the project")
    return destination


def set_references(api, project, references=None, text=None, message="the external references change"):
    """Write the external references file (or leave the project as it is), commit, and load the record store."""
    if text is None and references is not None:
        text = references_text(references)
    if text is not None:
        write(project, EXTERNAL_REFERENCES_REL, text)
    context_base.commit(project, message)
    loaded = api.build_store(project)
    assert not loaded.get("invalid"), f"the case's own project holds a record the store refuses: {loaded}"
    return project


def clone_tier(name, destination):
    """A clone of a dev tier in a temporary directory; None where this machine has no such tier."""
    tier = DEV_TIERS / name
    if not (tier / ".git").exists():
        return None
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    done = subprocess.run(["git", "clone", "-q", str(tier), str(destination)], capture_output=True, text=True)
    assert done.returncode == 0, f"the dev tier {name} could not be cloned:\n{done.stderr}"
    return destination
