"""Support code for the W2-23 acceptance tests: adoption safety on a planted repository (standard library and PyYAML).

Everything a case touches is planted under pytest's ``tmp_path``: a git repository of its own with the programme's
own ``CLAUDE.md``, ``AGENTS.md`` and ``.claude/settings.json``, tracked and untracked files, a path map, and an empty
``HOME``. The tool is driven the way its callers drive it: ``python -m gov.cli.main <command> ...`` as a child process
whose ``PYTHONPATH`` is the ``src/`` of the repository this file stands in (never a hard-coded worktree path), so the
tree the suite is run from is the code under test (DEC-732). Nothing of the implementation is imported here: the new
modules (``gov.adopt.safety``, ``gov.adapters.command``) need not exist for the suite to be collected.

The interface the cases hold is the ticket's ``## Interface`` (items 1-7), quoted where used; see ``README.md``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import pwd
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
TEMPLATE = REPO_ROOT / "template"
GITLEAKS_TEMPLATE = TEMPLATE / ".gitleaks.toml"
HOOKS_SOURCE = TEMPLATE / ".rulesync" / "hooks.jsonc"          # the source rulesync generates the settings' hooks from
KERNEL_HOOKS = TEMPLATE / "governance" / "kernel" / "hooks"
COMMAND_TIMEOUT_S = 180

PATH_MAP_REL = "governance/project/path-map.yaml"
ADOPTION = "governance/adoption"
RECORD = {"A0": f"{ADOPTION}/A0-safety-baseline.md", "A1": f"{ADOPTION}/A1-inventory.md",
          "A3": f"{ADOPTION}/A3-target-path-map.md", "A6": f"{ADOPTION}/A6-controlled-migration.md",
          "A8": f"{ADOPTION}/A8-legacy-import-and-retirement.md"}
STAGES = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")
ROLLBACK_PREFIX = "refs/gov/adoption/rollback/"
ROLLBACK_REF = re.compile(r"^refs/gov/adoption/rollback/([^/]+)/batch-(\d+)$")   # Interface item 2
VERDICT_REL = "audit/adoption/a5-verdict.md"
ADOPTER, AUDITOR = "adopter-w2-23", "auditor-w2-23"

# --- the programme's own instruction files: each line is its own and found nowhere else ---------------------------
CLAUDE_LINES = ["# Harbour programme: instructions for Claude",
                "Programme rule C1: berths are numbered from the north quay.",
                "Programme rule C2: the indigo tariff applies to berth four only.",
                "- C3: never move the tide tables without the harbour master."]
AGENTS_LINES = ["# Harbour programme: instructions for agents",
                "Programme rule A1: every agent reads the plum checklist first.",
                "Programme rule A2: the saffron gateway is touched only under a ticket.",
                "- A3: a review cites the walnut checklist."]
PROGRAMME_SETTINGS = {
    "model": "harbour-programme-model",
    "permissions": {"allow": ["Bash(make harbour-test:*)", "Read(./docs/**)"], "deny": ["Read(./vault/keys/**)"]},
    "hooks": {
        "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "programme/bin/check-bash.sh"}]}],
        "Notification": [{"hooks": [{"type": "command", "command": "programme/bin/notify.sh"}]}],
    },
    "env": {"HARBOUR_PROGRAMME_FLAG": "1"},
    "statusLine": {"type": "command", "command": "programme/bin/status-line.sh"},
}


def lines_text(lines):
    return "\n\n".join(lines) + "\n"


INSTRUCTION_FILES = {"CLAUDE.md": lines_text(CLAUDE_LINES), "AGENTS.md": lines_text(AGENTS_LINES),
                     ".claude/settings.json": json.dumps(PROGRAMME_SETTINGS, indent=2) + "\n"}

# Every folder the planted project uses and every held target. ``vault/`` is held by no namespace, on purpose.
NAMESPACE_PATHS = (".gitignore", ".gitleaks.toml", "README.md", "AGENTS.md", "CLAUDE.md", ".claude/**", ".rulesync/**",
                   "governance/**", "docs/**", "lib/**", "scripts/**", "spec/**", "legacy/**", "audit/**",
                   "archive/**", "modules/**")
GITIGNORE = ".gov-runtime/\n__pycache__/\n*.pyc\nlocal/\n*.local\n"

GUIDE, GUIDE_TARGET = "docs/guide.md", "docs/handbook/guide.md"
NOTES, NOTES_TARGET = "docs/notes.txt", "archive/notes.txt"
DROPS = ("docs/drop-1.txt", "docs/drop-2.txt", "docs/drop-3.txt")   # one DELETE_FROM_ACTIVE_TREE batch each

# --- the user's own untracked material, made while a run is under way (by a planted commit hook) -------------------
USER_FILE, USER_BYTES = "drafts/user-draft.md", b"# Draft\n\nThe owner's own notes, written during the adoption.\n"
USER_DIR_FILE, USER_DIR_BYTES = "user-dir/sketch.txt", b"a sketch in an untracked directory\n"
USER_CLONE, USER_CLONE_FILE, USER_CLONE_BYTES = "user-clone", "user-clone/README", b"an untracked nested clone\n"
IGNORED_FILES = {"local/scratch.md": b"ignored, untracked: the owner's scratch\n",
                 "settings.local": b"ignored, untracked: a local setting\n"}


# --------------------------------------------------------------------------------------------------------------------
# The box: a planted HOME, TMPDIR and a folder outside the project
# --------------------------------------------------------------------------------------------------------------------

@dataclass
class Box:
    home: Path
    tmp: Path
    elsewhere: Path


def make_box(base):
    base = Path(base)
    box = Box(base / "home", base / "tmp", base / "elsewhere")
    for folder in (box.home, box.tmp, box.elsewhere):
        folder.mkdir(parents=True, exist_ok=True)
    return box


def _search_path():
    """The child's PATH: this interpreter's folder, the caller's PATH and the user's ``~/.local/bin`` (rulesync)."""
    folders = [str(Path(sys.executable).parent), *os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep),
               str(Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local" / "bin")]
    return os.pathsep.join(dict.fromkeys(folder for folder in folders if folder))


def environment(box, **extra):
    """Built from scratch: no GOV_ROLE, GOV_TICKET, GOV_STORE or GIT_* of the session; no model can be reached."""
    dead = "127.0.0.1:9"  # the discard port: nothing answers there
    env = {"PATH": _search_path(), "HOME": str(box.home), "TMPDIR": str(box.tmp), "LC_ALL": "C.UTF-8",
           "PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1",
           "OLLAMA_HOST": dead, "GOV_QUERY_OLLAMA_HOST": dead,
           "GOV_OLLAMA_BIN": str(box.elsewhere / "no-embedding-program" / "ollama"),
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "W2-23 tests", "GIT_AUTHOR_EMAIL": "w2-23@example.invalid",
           "GIT_COMMITTER_NAME": "W2-23 tests", "GIT_COMMITTER_EMAIL": "w2-23@example.invalid"}
    env.update({k: v for k, v in os.environ.items() if k == "GOV_REBUILD_LOCK"})
    env.update(extra)
    return env


# --------------------------------------------------------------------------------------------------------------------
# Running the tool and git
# --------------------------------------------------------------------------------------------------------------------

@dataclass
class Done:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        def cut(text):
            return text if len(text) <= 3000 else text[:1500] + "\n[...]\n" + text[-1500:]
        return (f"$ gov {' '.join(self.args)}\nexit {self.returncode}\n--- stdout\n{cut(self.stdout)}\n"
                f"--- stderr\n{cut(self.stderr)}")


def run_gov(root, box, *args, timeout=COMMAND_TIMEOUT_S, **extra_env):
    """``python -m gov.cli.main <args>`` in ``root``, with this repository's ``src`` first on PYTHONPATH."""
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(root),
                              env=environment(box, **extra_env), capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout} s") from None
    return Done(tuple(args), done.returncode, done.stdout, done.stderr)


def envelope(done):
    """The API-0002 envelope a ``--json`` run printed; None where it printed none."""
    for line in reversed(done.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except ValueError:
                return None
            return value if isinstance(value, dict) else None
    return None


def assert_no_crash(done):
    """A run that ends in a refusal is no crash: no traceback, an envelope that says why."""
    assert "Traceback (most recent call last)" not in done.stderr, \
        f"the run crashed (a Python traceback) instead of refusing or succeeding\n{done.describe()}"


def refusal(done, code=None):
    """The error object of a refusal (``ok: false``, a non-zero exit); ``code`` if given must be its code."""
    assert_no_crash(done)
    doc = envelope(done)
    assert doc is not None, f"the run printed no envelope\n{done.describe()}"
    assert doc.get("ok") is False and done.returncode != 0, f"expected a refusal\n{done.describe()}"
    error = doc.get("error") or {}
    if code is not None:
        assert error.get("code") == code, f"expected the refusal {code}, got {error.get('code')}\n{done.describe()}"
    return error


def succeeded(done):
    assert_no_crash(done)
    doc = envelope(done)
    assert done.returncode == 0 and doc is not None and doc.get("ok") is True, \
        f"expected the run to succeed\n{done.describe()}"
    return doc.get("result") or {}


def git(root, *args, box=None, check=True):
    env = environment(box) if box else {"PATH": _search_path(), "GIT_CONFIG_NOSYSTEM": "1",
                                        "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C.UTF-8",
                                        "GIT_AUTHOR_NAME": "W2-23 tests", "GIT_AUTHOR_EMAIL": "w2-23@example.invalid",
                                        "GIT_COMMITTER_NAME": "W2-23 tests",
                                        "GIT_COMMITTER_EMAIL": "w2-23@example.invalid", "HOME": str(root)}
    done = subprocess.run(["git", "-C", str(root), "-c", "core.quotePath=false", *args], capture_output=True,
                          env=env, stdin=subprocess.DEVNULL)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {root}: {done.stderr.decode('utf-8', 'replace')}")
    return done.stdout.decode("utf-8", "surrogateescape")


def head(root):
    return git(root, "rev-parse", "HEAD").strip()


def at_head(root, rel):
    done = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"], capture_output=True,
                          env={"PATH": _search_path(), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return done.stdout if done.returncode == 0 else None


def porcelain(root):
    return git(root, "status", "--porcelain", "--untracked-files=all")


def staged(root):
    return [line for line in git(root, "diff", "--cached", "--name-status", "--no-renames").splitlines() if line]


def changed_in(root, commit):
    return [line for line in git(root, "show", "--name-only", "--format=", commit).splitlines() if line]


def rollback_refs(root):
    return {line.split()[1]: line.split()[0]
            for line in git(root, "for-each-ref", "--format=%(objectname) %(refname)", ROLLBACK_PREFIX).splitlines()
            if line.strip()}


def commits_deleting(root, rel):
    return [line for line in git(root, "log", "--diff-filter=D", "--format=%H", "--", rel).splitlines() if line]


def commit_all(root, message, *trailers):
    git(root, "add", "-A")
    args = ["commit", "-q", "--allow-empty", "-m", message]
    for trailer in trailers:
        args += ["--trailer", trailer]
    git(root, *args)
    return head(root)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def frontmatter(text, where="the record"):
    lines = text.split("\n")
    assert lines and lines[0].strip() == "---", f"{where} has no frontmatter"
    end = [line.strip() for line in lines[1:]].index("---") + 1
    data = yaml.safe_load("\n".join(lines[1:end]))
    assert isinstance(data, dict), f"{where}: the frontmatter is not a mapping"
    return data


# --------------------------------------------------------------------------------------------------------------------
# The planted project
# --------------------------------------------------------------------------------------------------------------------

def namespace(patterns):
    return {"paths": list(patterns), "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["orchestrator", "engineer", "independent-auditor"],
            "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "embedded",
            "provenance": "written by the W2-23 tests", "deletion_rebuild": "authoritative; restored from git only"}


def path_map(patterns=NAMESPACE_PATHS, code_intelligence=False):
    """A path map in the kernel schema's shape (as W1-41's tests write it): one namespace, ``harbour``."""
    systems = ("constitution-and-policies", "knowledge-fabric", "repository-contract", "agent-organisation", "skills",
               "tools-and-capabilities", "command-surface", "model-adapters", "orchestration-and-handoffs",
               "specification-and-planning", "research-and-experiments", "task-system", "product-delivery",
               "verification-and-governance-tests", "change-impact-control", "checkpoint-and-recovery",
               "observability-and-cost", "organisational-learning", "independent-audit", "security-and-permissions",
               "budget-governance", "emergency-stop-and-rollback")
    capability = {"enabled": True, "languages": ["python"]} if code_intelligence else {"enabled": False}
    return {"state_class": "AUTHORITATIVE", "namespaces": {"harbour": namespace(patterns)},
            "capabilities": {"code_intelligence": capability, "research_corpus": {"enabled": False}},
            "policies": {**{key: "hard-block" for key in ("security", "authority", "test", "change", "human_gate",
                                                           "tool")},
                         **{key: "warning" for key in ("memory", "context", "checkpoint", "model_routing", "budget",
                                                       "learning", "archive")}},
            "systems": {name: {"status": "absent", "reason": "a legacy project before adoption"} for name in systems}}


def base_files(code_intelligence=False, patterns=NAMESPACE_PATHS):
    files = {
        ".gitignore": GITIGNORE,
        ".gitleaks.toml": GITLEAKS_TEMPLATE.read_text(encoding="utf-8"),
        PATH_MAP_REL: yaml.safe_dump(path_map(patterns, code_intelligence), sort_keys=False),
        "README.md": "# Harbour\n\nA programme's own repository, planted by the W2-23 tests.\n",
        GUIDE: "# Guide\n\nHow the harbour is run.\n",
        NOTES: "Tide tables are kept by the harbour master.\n",
        "lib/__init__.py": '"""Loose helpers."""\n',
        "lib/util.py": "def helper():\n    return 41\n",
        "scripts/run.py": "from lib.util import helper\n\n\ndef main():\n    return helper()\n",
        **{rel: f"Batch file {number}: removed from the active tree by batch {number}.\n"
           for number, rel in enumerate(DROPS, 1)},
        **INSTRUCTION_FILES,
    }
    return files


def write(root, rel, data):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")
    return path


def plant_project(root, extra=None, without=(), code_intelligence=False, patterns=NAMESPACE_PATHS, ignored=True):
    """The programme's repository, committed: tracked files, the instruction files, and (``ignored``) the owner's
    ignored untracked files. ``without`` leaves files out; ``extra`` adds or replaces files."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    files = base_files(code_intelligence, patterns)
    files.update(extra or {})
    for rel, text in files.items():
        if rel not in without:
            write(root, rel, text)
    git(root, "init", "-q", "-b", "main")
    commit_all(root, "the programme's repository")
    if ignored and ".gitignore" not in without and files.get(".gitignore") == GITIGNORE:
        for rel, data in IGNORED_FILES.items():
            write(root, rel, data)
    return root


# --------------------------------------------------------------------------------------------------------------------
# The adoption, stage by stage
# --------------------------------------------------------------------------------------------------------------------

def entry(path, action, target=None, batch=None, **more):
    made = {"path": path, "action": action}
    if target is not None:
        made["target"] = target
    if batch is not None:
        made["batch"] = batch
    made.update(more)
    return made


def drops_proposal():
    """Three batches, each one DELETE_FROM_ACTIVE_TREE: no move, so no code graph is needed."""
    return [entry(rel, "DELETE_FROM_ACTIVE_TREE", batch=number) for number, rel in enumerate(DROPS, 1)]


class Adoption:
    def __init__(self, root, box):
        self.root, self.box, self.results = Path(root), box, {}

    def run(self, stage, *extra):
        return run_gov(self.root, self.box, "adopt", "--lite", "--stage", stage, *extra, "--json",
                       "--session", ADOPTER)

    def ok(self, stage, *extra):
        done = self.run(stage, *extra)
        self.results[stage] = succeeded(done)
        return done

    def map_argument(self, entries, name="proposal.yaml"):
        path = self.box.elsewhere / name
        path.write_text(yaml.safe_dump({"artefacts": list(entries)}, sort_keys=False), encoding="utf-8")
        return ("--map", str(path))

    def write_verdict(self):
        """The A5 verdict, written and committed as the Independent Auditor commits its report."""
        map_rel = self.results["A3"].get("record") or RECORD["A3"]
        data = at_head(self.root, map_rel)
        assert data is not None, f"{map_rel} is not committed"
        front = {"id": "AV-0001", "type": "adoption-verdict", "status": "ACTIVE", "state_class": "EVIDENCE",
                 "stage": "A5", "verdict": "pass", "path_map": map_rel, "path_map_hash": sha256(data),
                 "auditor_session": AUDITOR}
        write(self.root, VERDICT_REL, "---\n" + yaml.safe_dump(front, sort_keys=False)
              + "---\n\n# AV-0001: review of the path map\n\nRead before any move.\n")
        git(self.root, "add", "--", VERDICT_REL)
        git(self.root, "commit", "-q", "-m", "A5: review of the path map", "--trailer", "Task: HARB-a5aa",
            "--trailer", "Role: independent-auditor")

    def through(self, last, entries=()):
        for stage in STAGES[:STAGES.index(last) + 1]:
            if stage == "A3":
                self.ok(stage, *self.map_argument(entries))
            elif stage == "A5":
                self.write_verdict()
                self.ok(stage, "--verdict", VERDICT_REL)
            else:
                self.ok(stage)


# --------------------------------------------------------------------------------------------------------------------
# Planted commit hooks: the failure, the kill, and the owner's files made while a run is under way
# --------------------------------------------------------------------------------------------------------------------

_HOOK = '''#!{python}
"""A pre-commit hook planted by the W2-23 tests (not the tool): rules by what the commit stages."""
import json, os, signal, subprocess, sys
RULES = json.loads({rules!r})
PLANTED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "w2-23-planted")
listed = subprocess.run(["git", "diff", "--cached", "--name-only", "--no-renames"], capture_output=True,
                        text=True).stdout.splitlines()
clean = {{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}}
for rule in RULES:
    if not any(name == want or name.startswith(want) for name in listed for want in rule["when"]):
        continue
    for rel in rule.get("clone", []):  # the clone first: a file of its own is written into it after
        if not os.path.isdir(os.path.join(rel, ".git")):
            subprocess.run(["git", "init", "-q", rel], env=clean, check=True)
        if os.path.isdir(os.path.join(rel, ".git")):  # the support reads this: a planting failure is not the tool's
            with open(PLANTED, "a") as handle:
                handle.write(rel + "\\n")
    for rel, text in rule.get("write", {{}}).items():
        if not os.path.exists(rel):
            os.makedirs(os.path.dirname(rel) or ".", exist_ok=True)
            with open(rel, "wb") as handle:
                handle.write(text.encode("latin-1"))
    if rule.get("kill"):
        with open("/proc/%d/stat" % os.getppid()) as handle:  # git's parent: the process that runs the stage
            runner = int(handle.read().rsplit(")", 1)[1].split()[1])
        with open(rule["kill"], "w") as handle:
            handle.write(str(runner))
        os.kill(runner, signal.SIGKILL)
    if rule.get("refuse"):
        sys.stderr.write("the planted pre-commit hook refuses this commit\\n")
        sys.exit(1)
sys.exit(0)
'''


def install_hook(root, rules):
    """``rules``: a list of {when: [path or prefix staged], write: {rel: bytes}, clone: [rel], kill: <file>,
    refuse: bool}; each rule whose ``when`` matches what the commit stages acts, in order."""
    plain = [{**rule, "write": {rel: data.decode("latin-1") for rel, data in rule.get("write", {}).items()}}
             for rule in rules]
    path = Path(root) / ".git" / "hooks" / "pre-commit"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_HOOK.format(python=sys.executable, rules=json.dumps(plain)), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def remove_hook(root):
    (Path(root) / ".git" / "hooks" / "pre-commit").unlink(missing_ok=True)


USER_MATERIAL = {USER_FILE: USER_BYTES, USER_DIR_FILE: USER_DIR_BYTES}


def user_material_rule(when):
    """At the commit staging ``when``: the owner writes a file, a file in a new directory, and a nested clone with a
    file of its own, none of them tracked (the tool never wrote them)."""
    return {"when": list(when), "write": {**USER_MATERIAL, USER_CLONE_FILE: USER_CLONE_BYTES},
            "clone": [USER_CLONE]}


def planted_clones(root):
    """The nested clones the planted hook made (each with its ``.git`` a directory right after ``git init``)."""
    path = Path(root) / ".git" / "hooks" / "w2-23-planted"
    return set(path.read_text(encoding="utf-8").split()) if path.is_file() else set()


def user_material_problems(root):
    assert USER_CLONE in planted_clones(root), \
        f"the planted clone was not made ({USER_CLONE}/.git was not a directory after the hook ran): the case's " \
        "planting failed, not the tool"
    problems = []
    for rel, data in {**USER_MATERIAL, USER_CLONE_FILE: USER_CLONE_BYTES}.items():
        path = Path(root) / rel
        if not path.is_file():
            problems.append(f"{rel} (untracked, the owner's) is gone")
        elif path.read_bytes() != data:
            problems.append(f"{rel} (untracked, the owner's) changed")
    if not (Path(root) / USER_CLONE / ".git").is_dir():
        problems.append(f"{USER_CLONE}/.git (the owner's nested clone) is gone")
    return problems


def listing(root, paths):
    """Path -> sha256 of its bytes (None where it is absent)."""
    return {rel: (sha256((Path(root) / rel).read_bytes()) if (Path(root) / rel).is_file() else None)
            for rel in paths}


def untracked_files(root):
    """Every untracked file, ignored ones included, outside the tool's own ``.gov-runtime/``."""
    out = git(root, "ls-files", "--others", "-z")
    return sorted(rel for rel in out.split("\0") if rel and not rel.startswith(".gov-runtime/"))


# --------------------------------------------------------------------------------------------------------------------
# S3: the dependency proof's citation forms (Interface item 6)
# --------------------------------------------------------------------------------------------------------------------

STORE = ("legacy/memory/decisions/leg-001.md", "legacy/memory/decisions/leg-002.md", "legacy/memory/index.md")
STORE_IDS = ("LEG-001", "LEG-002")


def record_text(record_id, kind, status, body, **keys):
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE", **keys}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\n{body}\n"


def store_files():
    return {STORE[0]: record_text("LEG-001", "decision", "ACTIVE", "The tangerine quorum rule holds for every vote."),
            STORE[1]: record_text("LEG-002", "decision", "ACTIVE", "The slate ballot is counted twice."),
            STORE[2]: "# Legacy memory\n\n- LEG-001\n- LEG-002\n"}


# form -> (the planted file, its text). Each file cites the store once, in that form alone.
LISTED_FORMS = {
    "word_or_dash_before": (".rulesync/rules/cite-dash-before.md",
                            "# Votes\n\nVotes follow rule-LEG-001 of the old store.\n"),
    "backslashes": (".rulesync/rules/cite-backslashes.md",
                    "# Votes\n\nSee legacy\\memory\\decisions\\leg-001.md for the quorum.\n"),
    "url_encoding": (".rulesync/rules/cite-url-encoded.md",
                     "# Votes\n\nSee legacy%2Fmemory%2Fdecisions%2Fleg-001.md for the quorum.\n"),
    "letter_case": (".rulesync/rules/cite-letter-case.md",
                    "# Votes\n\nSee Legacy/Memory/Decisions/Leg-001.md for the quorum.\n"),
    "split_across_lines": (".rulesync/rules/cite-split-lines.md",
                           "# Votes\n\nThe quorum is in legacy/memory/\ndecisions/leg-001.md as written.\n"),
    "store_folder_only": (".rulesync/rules/cite-folder.md",
                          "# Votes\n\nKeep reading the notes in legacy/memory/ before a vote.\n"),
    "glob": (".rulesync/rules/cite-glob.md", "# Votes\n\nThe vote rules are in legacy/memory/**/*.md.\n"),
    "dotdot_then_tail": (".rulesync/rules/cite-dotdot-tail.md",
                         "# Votes\n\nThe quorum: ../decisions/leg-001.md, as the store says.\n"),
    "id_in_record_prose": ("spec/decisions/dec-401.md",
                           record_text("DEC-401", "decision", "ACTIVE", "A vote follows LEG-001 as written.")),
}
# The unlisted form, the test designer's choice (Interface item 6): the store's path written in base64. No listed
# form covers it, so it must be the only planted citation the proof does not find.
UNLISTED_FORM = ("base64_of_path", ".rulesync/rules/cite-base64.md",
                 "# Votes\n\nThe store, encoded: " + base64.b64encode(STORE[0].encode()).decode() + "\n")


def citation_files():
    files = {rel: text for rel, text in LISTED_FORMS.values()}
    files[UNLISTED_FORM[1]] = UNLISTED_FORM[2]
    return files


def retire_store_proposal():
    return [entry(rel, "RETIRE", kind="memory-store") for rel in STORE]


def proof_said(error):
    """What the proof says it found: the refusal's message and its list of citers (never its list of what it read)."""
    details = error.get("details") or {}
    return (error.get("message") or "") + "\n" + json.dumps(details.get("citers", []))


# --------------------------------------------------------------------------------------------------------------------
# S2: adapter generation
# --------------------------------------------------------------------------------------------------------------------

BEGIN, END = "<!-- gov:generated begin -->", "<!-- gov:generated end -->"   # Interface item 5
RULE_PHRASE_1, RULE_PHRASE_2 = "The heron ledger rule is generated.", "The egret ledger rule is generated."
GENERATED_HOOK_MARK = "governance/kernel/hooks/pretooluse.py"   # the template hooks source's PreToolUse command
AUTO_COMPACT = re.compile(r"AUTO_?COMPACT", re.I)   # a key that must NOT appear in the merged env (DEC-838: no threshold)


def rulesync_sources(phrase):
    return {".rulesync/rules/overview.md": ('---\nroot: true\ntargets: ["claudecode", "agentsmd"]\n'
                                            f'description: "harbour"\n---\n\n# Harbour rules\n\n{phrase}\n'),
            ".rulesync/hooks.jsonc": HOOKS_SOURCE.read_text(encoding="utf-8"),
            ".rulesync/permissions.jsonc": (TEMPLATE / ".rulesync" / "permissions.jsonc").read_text(encoding="utf-8")}


def nonblank(lines):
    return [line for line in lines if line.strip()]


# --------------------------------------------------------------------------------------------------------------------
# S6: a path with a space
# --------------------------------------------------------------------------------------------------------------------

ERROR_PHRASES = ("No such file or directory", "not found", "can't open", "cannot access", "unexpected",
                 "Is a directory", "Not a directory", "invalid path", "Traceback", "unknown option")


def hooks_source():
    text = HOOKS_SOURCE.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except ValueError:  # JSONC: drop whole-line comments
        return json.loads("\n".join(line for line in text.splitlines() if not line.strip().startswith("//")))


def path_errors(space_out, plain_out, root):
    """Word-splitting or path errors in the output of the run under ``root`` (whose path holds a space) that the same
    run at a path without one does not print."""
    found = []
    text = space_out
    for whole in (str(root), "EXAMIN APP", "EXAMIN\\ APP", "EXAMIN%20APP", "EXAMIN\\u0020APP"):
        text = text.replace(whole, "<root>")
    for fragment in re.findall(r".{0,40}(?:\bEXAMIN\b|(?<![A-Za-z])APP\b).{0,40}", text):
        found.append(f"a fragment of the split path: {fragment!r}")
    for phrase in ERROR_PHRASES:
        if space_out.count(phrase) > plain_out.count(phrase):
            found.append(f"{phrase!r} printed only at the path with a space")
    return found


def kernel_hook_events():
    """(event as the harness names it, the settings' command line) for every hook of the template's source."""
    pascal = {"preToolUse": "PreToolUse", "postToolUse": "PostToolUse", "postToolUseFailure": "PostToolUseFailure",
              "sessionStart": "SessionStart", "stop": "Stop", "preCompact": "PreCompact",
              "subagentStop": "SubagentStop"}
    events = []
    for name, entries in hooks_source()["hooks"].items():
        for item in entries:
            events.append((pascal.get(name, name[:1].upper() + name[1:]), item["command"]))
    return events


def hook_event(event, root):
    base = {"session_id": "w2-23-session", "transcript_path": str(Path(root) / ".none.jsonl"), "cwd": str(root),
            "hook_event_name": event}
    if event == "PreToolUse":
        base.update(tool_name="Read", tool_input={"file_path": str(Path(root) / "README.md")})
    elif event in ("PostToolUse", "PostToolUseFailure"):
        base.update(tool_name="Bash", tool_input={"command": "true"},
                    tool_response={"stdout": "", "stderr": "", "interrupted": False})
        if event == "PostToolUseFailure":
            base["error"] = "exit status 1"
    elif event == "SessionStart":
        base["source"] = "compact"
    elif event in ("Stop", "SubagentStop"):
        base["stop_hook_active"] = False
    elif event == "PreCompact":
        base.update(trigger="manual", custom_instructions="")
    return base


_WRAPPER = '''#!/bin/sh
# The pinned gov's interpreter, as a planted HOME holds it: this repository's src is on its path even under -E.
[ "$1" = "-E" ] && shift
exec "{python}" -E -c 'import runpy, sys; sys.path.insert(0, sys.argv.pop(1)); sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name="__main__")' "{src}" "$@"
'''


def plant_pinned_gov(box):
    """``$HOME/.local/bin/gov`` whose first line names an interpreter, as the hooks' command lines read it."""
    wrapper = box.home / "gov-python"
    wrapper.write_text(_WRAPPER.format(python=sys.executable, src=str(SRC)), encoding="utf-8")
    wrapper.chmod(0o755)
    launcher = box.home / ".local" / "bin" / "gov"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(f"#!{wrapper}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n",
                        encoding="utf-8")
    launcher.chmod(0o755)


def plant_kernel_hooks(root):
    for source in sorted(KERNEL_HOOKS.glob("*.py")):
        target = Path(root) / "governance" / "kernel" / "hooks" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def run_hook(root, box, command, event):
    env = environment(box, CLAUDE_PROJECT_DIR=str(root))
    try:
        done = subprocess.run(["/bin/sh", "-c", command], cwd=str(root), env=env, capture_output=True, text=True,
                              input=json.dumps(hook_event(event, root)), timeout=90)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the {event} hook did not end within 90 s at {root}") from None
    return Done((event,), done.returncode, done.stdout, done.stderr)
