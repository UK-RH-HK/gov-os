"""Support code for the W2-201 acceptance tests (standard library and PyYAML only).

W2-201 (DAEO-k1us) puts audit 4's Table 3, with the owner's model changes (DEC-1212 (3), DEC-1214 K1), into the role
files and ``governance/project/criticality.yaml``; makes ``gov launch`` refuse a caller's other model unless
``governance/project/model-exceptions.yaml`` lists it; makes the helper hook ``.claude/hooks/agent_model.py`` let Opus
through only for C3 work and refuse a ``fork``; keeps the 5-minute prompt cache for launched workers; and refuses a
worker launch whose repository settings carry an inbox-waiter or idle-check wake-up hook.

The cases drive public interfaces only:

- **The role reader** ``gov.launch.role`` (``launch_default``, ``read_by_criticality``) on the real role files, each
  copy planted alone in a temporary tree at the place the reader reads (``template/governance/kernel/roles/``).
- **``gov.launch.criticality.ticket_criticality``** on the real ``governance/project/criticality.yaml``.
- **``gov launch``** on W2-60a's stand-in CLI, through W2-184's support module (imported as ``s``; W2-60a's as
  ``s.b``): a temporary HOME, an open resource gate, a fixture git project, the stand-in that records its arguments,
  environment and ``--settings``, and the launch record folder. Nothing of those modules is changed here.
- **The hook** as a subprocess, ``python3 -I .claude/hooks/agent_model.py`` (the command the repository's settings
  run), handed one PreToolUse event as JSON on its standard input, with ``CLAUDE_PROJECT_DIR`` naming a project folder
  planted in ``tmp_path`` (tickets, a criticality file, an exceptions file) and its working folder another, empty one.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-184"))
import w2_184_support as s  # noqa: E402

b = s.b
REPO_ROOT = b.REPO_ROOT

OPUS, SONNET, HAIKU = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"
CLASSES = ("C3", "C2", "C1", "C0")
ENGINEER, TEST_DESIGNER, AUDITOR = s.ENGINEER, s.TEST_DESIGNER, s.AUDITOR
RESEARCH, PRODUCT_SPEC = s.RESEARCH, s.PRODUCT_SPEC
QA = "qa-engineer"

CRITICALITY_REL = "governance/project/criticality.yaml"
EXCEPTIONS_REL = "governance/project/model-exceptions.yaml"
HOOK_REL = ".claude/hooks/agent_model.py"
HOOK = REPO_ROOT / HOOK_REL
ROLES_REL = "template/governance/kernel/roles"
COPY_FOLDERS = (".rulesync/subagents", "template/.rulesync/subagents", ".claude/agents")
LOCATIONS = (ROLES_REL,) + COPY_FOLDERS

# --------------------------------------------------------------------------
# S1 / R1: the table (audit 4 Table 3 as DEC-1225 (1) revises it)
# --------------------------------------------------------------------------
# Rewrite-Reason: DEC-1225: S1's TABLE gave Opus at C3 to engineer, independent-test-designer, independent-auditor and
# qa-engineer, Haiku at C0, and a `Launch by criticality` line for those four. DEC-1225 (1): Opus only for each app's
# CTO (orchestrator) and the senior engineer; every other role Sonnet, high, at every class and profile, so no table
# line (R1).

_H, _S = (OPUS, "high"), (SONNET, "high")
# role -> (Launch default (model, effort), {class: (model, effort)} or None for no table line)
TABLE = {
    "orchestrator": (_H, None),
    "senior-engineer": (_H, None),
    "ticket-lead": ((SONNET, "medium"), None),   # Rewrite-Reason: F14 (fixes-015a): a ticket lead runs medium
    "engineer": (_S, None),
    "independent-test-designer": (_S, None),
    "independent-auditor": (_S, None),
    "qa-engineer": (_S, None),
    "product-spec": (_S, None),
    "research": (_S, None),
}
# What the Opus and Haiku model ids may name in the role files and criticality.yaml (R1's scan)
OPUS_ROLES = ("orchestrator", "senior-engineer")


def plant_role_copy(tmp, location, role):
    """A tree holding only ``<location>/<role>.md`` of this repository, written where the role reader reads a role
    file (``template/governance/kernel/roles/<role>.md``). Returns the tree."""
    source = REPO_ROOT / location / f"{role}.md"
    assert source.is_file(), f"{location}/{role}.md does not exist in this repository"
    tree = Path(tmp) / "tree"
    b.write(tree / ROLES_REL / f"{role}.md", source.read_text(encoding="utf-8"))
    return tree


# --------------------------------------------------------------------------
# Tickets as front-matter maps, for ticket_criticality and the hook
# --------------------------------------------------------------------------

def front_matter(allowed, profile="STANDARD", kind="implementation", tk="DAEO-k1t0"):
    return {"id": tk, "status": "in_progress", "type": "task", "class": kind, "role": ENGINEER,
            "allowed_paths": list(allowed), "profile": profile}


def ticket_file_text(data):
    return "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n# a W2-201 fixture ticket\n"


def real_criticality(allowed, profile="STANDARD"):
    """``ticket_criticality`` on this repository's own ``governance/project/criticality.yaml``."""
    from gov.launch import criticality
    return criticality.ticket_criticality(REPO_ROOT, front_matter(allowed, profile))


# --------------------------------------------------------------------------
# The hook
# --------------------------------------------------------------------------

# A fixture rubric in the form gov.launch.criticality reads: C3 src/critical, C2 the rest of src, C1 docs, FULL >= C2.
HOOK_RUBRIC = {
    "version": 1, "default": "C2", "opus": OPUS,
    "rules": [{"class": "C3", "paths": ["src/critical/*"]}, {"class": "C2", "paths": ["src/*"]},
              {"class": "C1", "paths": ["docs/*"]}, {"class": "C2", "profile": "FULL"}],
}
DECIDED = "DEC-1214 K1 (W2-201 fixture)"
FOUR = (TEST_DESIGNER, ENGINEER, AUDITOR, QA)
C3_ENTRIES = [{"subagent_type": role, "model": "opus", "decided": DECIDED, "class": "C3"} for role in FOUR]

# The fixture tickets: id -> (allowed_paths, profile, the ``class`` key (the ticket's kind), the class by the rubric)
TICKETS = {
    "DAEO-c3c3": (["src/critical/core/**"], "STANDARD", "implementation", "C3"),
    "DAEO-c2c2": (["src/product/app/**"], "STANDARD", "implementation", "C2"),
    "DAEO-c1c1": (["docs/guides/**"], "STANDARD", "implementation", "C1"),
    "DAEO-c2k3": (["src/product/app/**"], "STANDARD", "C3", "C2"),          # its class key says C3: never read
    "DAEO-mixd": (["docs/guides/**", "src/critical/core/x.py"], "STANDARD", "implementation", "C3"),
    "DAEO-fdoc": (["docs/guides/**"], "FULL", "implementation", "C2"),
}
C3_TICKET, C2_TICKET = "DAEO-c3c3", "DAEO-c2c2"


@dataclass(frozen=True)
class HookRun:
    code: int
    stdout: str
    stderr: str
    event: str

    def describe(self):
        return (f"event: {self.event[:600]}\nexit code: {self.code}\nstdout: {self.stdout[-1500:]!r}\n"
                f"stderr: {self.stderr[-1500:]!r}")


def hook_project(base, *, rubric="fixture", exceptions="fixture", tickets="fixture"):
    """A project folder for the hook. ``rubric`` / ``exceptions``: ``"fixture"`` (HOOK_RUBRIC, C3_ENTRIES), ``"real"``
    (this repository's file, its bytes), None (no file), a dict or list (dumped as YAML) or a str (written as is).
    ``tickets``: ``"fixture"`` (TICKETS), None (no ``.tickets`` folder) or ``{id: text}``."""
    project = Path(base) / "hook-project"
    project.mkdir(parents=True, exist_ok=True)
    for rel, value, fixture in ((CRITICALITY_REL, rubric, HOOK_RUBRIC),
                                (EXCEPTIONS_REL, exceptions, {"exceptions": C3_ENTRIES})):
        if value is None:
            continue
        if value == "fixture":
            value = fixture
        if value == "real":
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        elif isinstance(value, (dict, list)):
            text = yaml.safe_dump(value, sort_keys=False)
        else:
            text = value
        b.write(project / rel, text)
    if tickets == "fixture":
        tickets = {tk: ticket_file_text(front_matter(allowed, profile, kind, tk))
                   for tk, (allowed, profile, kind, _) in TICKETS.items()}
    if tickets is not None:
        (project / ".tickets").mkdir(parents=True, exist_ok=True)
        for tk, text in tickets.items():
            b.write(project / ".tickets" / f"{tk}.md", text)
    return project


def prompt(*task_ids, body="Implement the change the brief names; return the commit."):
    """A spawn prompt with one line ``Task: <id>`` per id given."""
    return "\n".join([body, "", *[f"Task: {tk}" for tk in task_ids], "", "Read the ticket first."])


NO_MODEL = object()


def spawn(kind=ENGINEER, model=NO_MODEL, tasks=(C3_TICKET,), tool="Agent", text=None):
    """A PreToolUse event for an Agent (or Task) spawn; ``model=NO_MODEL`` leaves the key out."""
    tool_input = {"description": "a W2-201 fixture helper", "prompt": text if text is not None else prompt(*tasks)}
    if kind is not None:
        tool_input["subagent_type"] = kind
    if model is not NO_MODEL:
        tool_input["model"] = model
    return {"session_id": "00000000-0000-4000-8000-000000000201", "hook_event_name": "PreToolUse",
            "tool_name": tool, "tool_input": tool_input}


def run_hook(project, event, base=None):
    """``python3 -I <repo>/.claude/hooks/agent_model.py`` with ``event`` (a dict as JSON, or a str as is) on stdin,
    ``CLAUDE_PROJECT_DIR`` the project, the working folder an empty one beside it."""
    base = Path(base or Path(project).parent)
    elsewhere = base / "hook-cwd"
    elsewhere.mkdir(parents=True, exist_ok=True)
    text = event if isinstance(event, str) else json.dumps(event)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(base / "hook-home"), "LANG": "C.UTF-8",
           "CLAUDE_PROJECT_DIR": str(project)}
    done = subprocess.run([sys.executable, "-I", str(HOOK)], input=text, capture_output=True, text=True,
                          cwd=str(elsewhere), env=env, timeout=60)
    return HookRun(done.returncode, done.stdout, done.stderr, text)


def let_through(run):
    assert run.code == 0, f"the hook did not let the spawn through (exit 0)\n{run.describe()}"
    assert run.stdout.strip() == "", f"the hook let the spawn through but wrote to stdout\n{run.describe()}"


def refused(run, *words):
    """Exit 2 with the reason on stderr; every word in ``words`` in it (case-insensitive)."""
    assert run.code == 2, f"the hook did not refuse the spawn (exit 2)\n{run.describe()}"
    assert run.stderr.strip(), f"the hook refused with no reason on stderr\n{run.describe()}"
    missing = [word for word in words if word.lower() not in run.stderr.lower()]
    assert not missing, f"the hook's refusal does not name {missing}\n{run.describe()}"


# --------------------------------------------------------------------------
# Launches
# --------------------------------------------------------------------------

def write_exceptions(project, value):
    """``governance/project/model-exceptions.yaml`` in the fixture project: a dict or list as YAML, a str as is."""
    text = yaml.safe_dump(value, sort_keys=False) if isinstance(value, (dict, list)) else value
    return b.write(Path(project) / EXCEPTIONS_REL, text)


def fixture_skill_text(name):
    return (f"---\nname: {name}\nversion: \"1.0.0\"\ndescription: the W2-201 fixture copy of {name}.\n---\n\n"
            f"# {name}\n\nThe fixture method text.\n")


JUDGING_SRC = REPO_ROOT / "template/governance/kernel/skills/judging-work/SKILL.md"
JUDGING_RELS = ("template/governance/kernel/skills/judging-work/SKILL.md", ".claude/skills/judging-work/SKILL.md")


def plant_real_role(project, role):
    """This repository's kernel role file for ``role`` in the fixture project, with what its launch needs: each skill
    its ``Skills`` line names (a versioned fixture copy at ``.claude/skills/<name>/SKILL.md``; ``judging-work`` as the
    kernel's own bytes, kernel file and loaded copy, W2-195) and its template copy under the names a launcher looks for
    (any bytes, W2-153). Returns the role file's text."""
    text = (REPO_ROOT / ROLES_REL / f"{role}.md").read_text(encoding="utf-8")
    b.write(b.role_path(project, role), text)
    line = next((l for l in text.splitlines() if l.startswith("- **Skills:** ")), None)
    for name in (line[len("- **Skills:** "):].split(", ") if line else []):
        if name == "judging-work":
            for rel in JUDGING_RELS:
                b.write(Path(project) / rel, JUDGING_SRC.read_text(encoding="utf-8"))
        else:
            b.write(Path(project) / ".claude/skills" / name / "SKILL.md", fixture_skill_text(name))
    template = f"---\nname: role-{role}\n---\n# W2-201 fixture template for {role} {b.TEMPLATE_WORD}\n"
    for rel in (f".claude/templates/role-{role}.md", f".claude/templates/{role}.md"):
        if not (Path(project) / rel).exists():
            b.write(Path(project) / rel, template)
    return text


def quiet(result):
    assert result.run.stdout == "" and result.run.stderr == "", (
        f"a successful launch wrote to its stdout or stderr\n{result.describe()}")


def record_values(result, *keys):
    record = result.record()
    return {key: record.get(key, s.MISSING) for key in keys}


# --------------------------------------------------------------------------
# R3: Fable (DEC-1225 (3): no session runs Fable)
# --------------------------------------------------------------------------
# Rewrite-Reason: DEC-1225: S9 planted DEC-1215's substitution file (`governance/project/model-substitution.yaml`) in
# four states and judged Fable as Opus while it was active. The file and its readers are gone (R3), so the states are
# gone; what is kept is the two names Fable goes by, and `plant_substitution_file`, which plants a file in the old
# form to show that nothing reads it any more.

FABLE = "claude-fable-5-2"
FABLE_NAMES = ("fable", FABLE)
SUBSTITUTION_REL = "governance/project/model-substitution.yaml"


def plant_substitution_file(project):
    """DEC-1215's file in its old form, active until far in the future (Opus to Fable): R3 says no reader of it is left,
    so a launch or a spawn that names Fable is refused with it there as without it."""
    data = {"active": True, "from": OPUS, "to": FABLE, "effort": "high", "until": "2099-01-01T09:00:00+00:00",
            "decided": "DEC-1215 (W2-201 R3 fixture)"}
    b.write(Path(project) / SUBSTITUTION_REL, yaml.safe_dump(data, sort_keys=False))
    return Path(project)
