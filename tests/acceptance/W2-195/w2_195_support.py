"""Shared helpers of the W2-195 acceptance tests (README).

Every case builds what it needs under ``tmp_path`` and drives the public interfaces the lead's interface statement names
(DEC-1157): ``python3 -m gov.cli.main brief ...`` as a child process, ``gov.launch.role.read_role(root, role)`` in a child
process (``read_role_child.py``), ``python3 -m gov.cli.main adapters generate``, ``copier copy`` and a wheel built from
HEAD. The skill's text is this folder's own copy (``data/judging-work.kernel.SKILL.md``, the approved 0fc1c502 with its
``description`` value quoted: sha256 ``3fd8864b...``), so the brief and launch fixtures never depend on the kernel file
existing in this tree. Nothing here reads the ticket's implementation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import site
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src"
KERNEL = REPO / "template/governance/kernel"
FACTS = REPO / "governance/project/facts.yaml"
DATA = HERE / "data"
SKILL_DATA = DATA / "judging-work.kernel.SKILL.md"
READ_ROLE_CHILD = HERE / "read_role_child.py"

SKILL = "judging-work"
KERNEL_SKILL_REL = "template/governance/kernel/skills/judging-work/SKILL.md"     # a tree with template/ (Gov OS, the kit's source)
ADOPTED_SKILL_REL = "governance/kernel/skills/judging-work/SKILL.md"             # a tree with no template/ (a kit or adopted tree)
MIRROR_REL = "template/.rulesync/skills/judging-work/SKILL.md"
PRELOADED_REL = ".claude/skills/judging-work/SKILL.md"
KERNEL_SHA256 = "3fd8864b4b095b01b8748da01acd6a5a0dbd1295aa28ee7e97007dc21d48bf4d"
KERNEL_SIZE = 3683
SECTIONS_SHA256 = "36f94490027fdaaddb32105e651621a7a83af7d82fdb36a31a8263df79ec7ac3"   # sections 1 to 3 of 1.0.0
VERSION = "1.0.0"
OTHER_VERSION = "1.0.1"
START, END = "## 1. The threat model\n", "## 4. Doing it\n"

TICKET_ID = "DAEO-jw01"
TICKET_W2 = "W2-951"
NEW_SINCE = "2026-11-10"
CREATED = "2026-11-11T08:00:00Z"
TIMEOUT = 120

# The judging briefs (interface item 2): the brief's arguments after ``brief``.
JUDGING_BRIEFS = {
    "independent-auditor": ("independent-auditor", TICKET_ID),
    "qa-engineer": ("qa-engineer", TICKET_ID),
    "lead-review": ("lead", TICKET_ID, "--run", "review"),
}
NON_JUDGING_BRIEFS = {
    "engineer": ("engineer", TICKET_ID),
    "independent-test-designer": ("independent-test-designer", TICKET_ID),
}
JUDGING_LAUNCH_ROLES = ("independent-auditor", "qa-engineer")          # interface item 4: the reviewer and probe launch as the auditor
PRELOADING_ROLES = ("independent-auditor", "qa-engineer", "orchestrator", "ticket-lead")   # S1's role files


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


# --- the skill's text -----------------------------------------------------------------------------------------------

def kernel_text() -> str:
    """The approved skill as the kernel installs it (this folder's copy, checked against its sha256)."""
    data = SKILL_DATA.read_bytes()
    assert sha256(data) == KERNEL_SHA256, f"the plant: {SKILL_DATA.name} is not the approved kernel bytes (sha256 {sha256(data)})"
    return data.decode("utf-8")


def sections(text: str) -> str:
    """Sections 1 to 3: the bytes from the start of the line ``## 1. The threat model`` up to, not including, the line
    ``## 4. Doing it`` (the lead's statement)."""
    start = text.index("\n" + START) + 1
    end = text.index("\n" + END, start) + 1
    return text[start:end]


def variant(text: str, version: str = OTHER_VERSION, word: bool = True) -> str:
    """The skill with another version (top-level and ``metadata.version``) and, when ``word``, one word of section 2
    changed ("every finding" -> "each finding"): what a brief must follow if it reads the installed file."""
    out = text.replace(f'version: "{VERSION}"', f'version: "{version}"')
    assert out.count(f'version: "{version}"') == 2, "the plant: the skill's two version fields were not both changed"
    if word:
        assert out.count("Ask of every finding, word for word:") == 1, "the plant: section 2's line is not in the skill"
        out = out.replace("Ask of every finding, word for word:", "Ask of each finding, word for word:")
    return out


def front_matter(text: str) -> dict:
    lines = text.split("\n")
    assert lines[0].strip() == "---", "no front matter"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    data = yaml.safe_load("\n".join(lines[1:end]))
    return data if isinstance(data, dict) else {}


def body(text: str) -> str:
    """The text after the front matter, its leading blank lines dropped (rulesync drops the one after ``---``)."""
    lines = text.split("\n")
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    return "\n".join(lines[end + 1:]).lstrip("\n")


def version_of(text: str) -> str | None:
    """A skill's version as ``gov.launch.role`` reads it: top-level ``version``, else ``metadata.version``."""
    front = front_matter(text)
    value = front.get("version")
    if not value and isinstance(front.get("metadata"), dict):
        value = front["metadata"].get("version")
    return str(value) if value else None


def preloaded(text: str, version: str | None = None) -> str:
    """The preloaded copy as ``gov adapters generate`` (rulesync) writes it from the kernel text: the front matter
    rewritten to ``name``, ``description`` and ``metadata.version`` only (no top-level ``version``), the blank line
    after it dropped, the body otherwise byte for byte (observed on this tree's generated skills)."""
    front = front_matter(text)
    version = version or version_of(text)
    head = (f"---\nname: {front['name']}\ndescription: {json.dumps(front['description'])}\n"
            f"metadata:\n  version: {version}\n---\n")
    return head + body(text)


# --- child processes ------------------------------------------------------------------------------------------------

def search_path() -> str:
    """The child's PATH: this interpreter's folder, the caller's PATH and the user base's ``bin`` (rulesync, copier)."""
    folders = [str(Path(sys.executable).parent), *os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep),
               str(Path(site.getuserbase()) / "bin")]
    return os.pathsep.join(dict.fromkeys(folder for folder in folders if folder))


def child_env(scratch: Path, extra: dict | None = None) -> dict:
    """This tree's ``src`` first, an empty ``HOME``, no bytecode written, dead proxies, no ``GOV_``/``PYTEST_`` variable."""
    home = scratch / "empty-home"
    home.mkdir(parents=True, exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "GOV_"))}
    env.setdefault("PYTHONUSERBASE", site.getuserbase())
    dead = "http://127.0.0.1:9"
    env.update({"PYTHONPATH": str(SRC), "HOME": str(home), "PYTHONDONTWRITEBYTECODE": "1", "PATH": search_path(),
                "http_proxy": dead, "https_proxy": dead, "HTTP_PROXY": dead, "HTTPS_PROXY": dead,
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
    if extra:
        env.update(extra)
    return env


def describe(done: subprocess.CompletedProcess) -> str:
    return f"exit {done.returncode}\n--- stdout ---\n{done.stdout[-2500:]}\n--- stderr ---\n{done.stderr[-2500:]}"


# --- a project for gov brief ----------------------------------------------------------------------------------------

def ready_ticket(ticket_id: str = TICKET_ID, w2: str = TICKET_W2) -> str:
    """A ticket that is READY on every count of ``gov brief``'s ready check, in tk's form."""
    front = {
        "id": ticket_id, "status": "in_progress", "deps": [], "links": [],
        "type": "task", "priority": 1, "assignee": "engineer", "external-ref": w2, "tags": ["fixture"], "wbs_id": w2,
        "title": "Judge the widget", "class": "tool", "state_class": "AUTHORITATIVE", "role": "engineer",
        "depends_on": [], "allowed_paths": ["src/widget/**", "tests/unit/widget/**"], "reads": ["src/widget/**"],
        "needs": [], "waits_on": [],
        "kpis": {"success": [{"line": "S1 The widget prints its name [DEC-1].", "verify": "a unit test reads its name"}],
                 "failure": [{"line": "F1 The widget prints nothing.", "verify": "the unit test of S1 fails"}]},
        "non_goals": ["No graphical interface."], "done_when": ["DOD-1"], "profile": "FULL", "sources": ["DEC-1"],
        "est_loc": 120, "acceptance_tests": {"path": f"tests/acceptance/{w2}/"},
    }
    lines = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=1000).rstrip("\n").split("\n")
    lines.insert(3, f"created: {CREATED}")
    return "---\n" + "\n".join(lines) + f"\n---\n# {w2} Judge the widget\n\nThe widget is judged by its reviewers.\n"


class BriefProject:
    """A project ``gov brief`` reads: this tree's kernel templates and facts file (``ready.new_since`` set), one READY
    ticket, and the skill: the kernel file (``template/governance/kernel/skills/judging-work/SKILL.md``, or
    ``governance/kernel/...`` in the adopted layout) and the preloaded copy (``.claude/skills/judging-work/SKILL.md``)."""

    def __init__(self, root: Path, adopted: bool = False, kernel: str | None = None, copy: str | None = None):
        self.root, self.adopted = root, adopted
        prefix = "" if adopted else "template/"
        templates = root / f"{prefix}governance/kernel/templates"
        templates.mkdir(parents=True)
        for path in sorted((KERNEL / "templates").iterdir()):
            if path.is_file():
                shutil.copyfile(path, templates / path.name)
        facts = yaml.safe_load(FACTS.read_text(encoding="utf-8"))
        facts["ready"] = {"new_since": NEW_SINCE}
        self.write("governance/project/facts.yaml", yaml.safe_dump(facts, sort_keys=False, allow_unicode=True, width=1000))
        self.write(f".tickets/{TICKET_ID}.md", ready_ticket())
        self.kernel_rel = ADOPTED_SKILL_REL if adopted else KERNEL_SKILL_REL
        text = kernel_text()
        self.set_kernel(text if kernel is None else kernel)
        self.set_copy(preloaded(text) if copy is None else copy)

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def set_kernel(self, text: str) -> None:
        self.write(self.kernel_rel, text)

    def set_copy(self, text: str) -> None:
        self.write(PRELOADED_REL, text)

    def remove(self, rel: str) -> None:
        (self.root / rel).unlink()

    def brief(self, *args: str, json_out: bool = True) -> subprocess.CompletedProcess:
        argv = [sys.executable, "-B", "-m", "gov.cli.main", "brief", *args, "--root", str(self.root)]
        if json_out:
            argv.append("--json")
        return subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT, cwd=str(self.root.parent),
                              env=child_env(self.root.parent), stdin=subprocess.DEVNULL)


def brief_text(done: subprocess.CompletedProcess) -> str:
    """The brief of a ``--json`` run that must succeed: exit 0, an ok envelope, ``result.brief`` a non-empty string."""
    assert done.returncode == 0, f"gov brief did not succeed: {describe(done)}"
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"--json printed no JSON envelope: {describe(done)}") from None
    assert data.get("ok") is True, f"the envelope is not ok: {data}"
    text = (data.get("result") or {}).get("brief")
    assert isinstance(text, str) and text.strip(), f"result.brief is empty: {data}"
    return text


def refused_code(done: subprocess.CompletedProcess) -> str:
    """The error code of a ``--json`` refusal (non-zero exit, ``ok: false``), with no brief in the envelope."""
    assert done.returncode != 0, f"gov brief did not refuse (exit 0): it printed a brief\n{describe(done)}"
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"--json printed no JSON envelope (the refusal is not gov's): {describe(done)}") from None
    assert data.get("ok") is False, f"the envelope is not a refusal: {data}"
    assert not (data.get("result") or {}).get("brief"), f"a refusal's envelope carries a brief: {data}"
    return str((data.get("error") or {}).get("code"))


def version_lines(brief: str, version: str) -> list[str]:
    """The brief's lines that hold both ``judging-work`` and ``version <v>`` (interface item 2)."""
    return [line for line in brief.split("\n") if SKILL in line and f"version {version}" in line]


# --- a root for read_role -------------------------------------------------------------------------------------------

SKILLS_LINE = re.compile(r"^- \*\*Skills:\*\* (.+)$", re.M)


def skills_named(role_text: str) -> list[str]:
    """The names on a role file's ``- **Skills:**`` line (empty when it has none)."""
    found = SKILLS_LINE.findall(role_text)
    assert len(found) <= 1, f"the role file holds {len(found)} Skills lines"
    return [name.strip() for name in found[0].split(",")] if found else []


def with_skills(role_text: str, names: list[str]) -> str:
    """The role file with its ``- **Skills:**`` line naming ``names`` (added after the Version line if it had none)."""
    line = f"- **Skills:** {', '.join(names)}"
    if SKILLS_LINE.search(role_text):
        return SKILLS_LINE.sub(lambda _m: line, role_text, count=1)
    return re.sub(r"^(- \*\*Version:\*\* .+)$", lambda m: m.group(1) + "\n" + line, role_text, count=1, flags=re.M)


class LaunchRoot:
    """A root ``read_role`` reads: ``template/governance/kernel/roles/<role>.md`` (this tree's role file, its Skills line
    as the case sets it), the kernel skill file, and under ``.claude/skills/`` a copy of every skill the line names
    (the kernel's own folder for each other skill; the preloaded form of the skill for ``judging-work``)."""

    def __init__(self, root: Path, role: str, names: list[str] | None = None, copy: str | None = None,
                 with_copy: bool = True):
        self.root, self.role = root, role
        text = (KERNEL / "roles" / f"{role}.md").read_text(encoding="utf-8")
        named = skills_named(text) if names is None else names
        self.write(f"template/governance/kernel/roles/{role}.md", text if names is None else with_skills(text, names))
        self.write(KERNEL_SKILL_REL, kernel_text())
        for name in named:
            if name == SKILL:
                continue
            source = KERNEL / "skills" / name
            assert (source / "SKILL.md").is_file(), f"the plant: the kernel has no skill {name} for {role}'s Skills line"
            shutil.copytree(source, root / ".claude/skills" / name)
        if with_copy:
            self.write(PRELOADED_REL, preloaded(kernel_text()) if copy is None else copy)

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def read_role(self) -> dict:
        """``gov.launch.role.read_role(root, role)`` in a child: ``{ok: true, skills}`` or ``{ok: false, code, message}``."""
        done = subprocess.run([sys.executable, "-B", str(READ_ROLE_CHILD), str(self.root), self.role],
                              capture_output=True, text=True, timeout=TIMEOUT, cwd=str(self.root.parent),
                              env=child_env(self.root.parent), stdin=subprocess.DEVNULL)
        lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
        assert lines, f"the read_role child printed no answer: {describe(done)}"
        return json.loads(lines[-1])
