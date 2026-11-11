"""W2-153 builder tests: gov launch passes the role template as the appended system prompt, and refuses without it.

Regression evidence only (DEC-136). No CLI is started: a recording stand-in replaces ``subprocess.Popen``, under a
temporary HOME with an open resource gate. The dispatcher's lead form (launch_now.sh) is run with a stub ``claude``
on a copy whose absolute paths point into tmp_path.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import launcher

REPO = Path(__file__).resolve().parents[3]
LAUNCH_NOW = REPO / "governance/project/orchestration/tools/dispatch/launch_now.sh"
ALL_ROLES = (*launcher.WORKER_ROLES, *launcher.LEAD_ROLES)
STEMS = {"engineer": "role-engineer", "independent-test-designer": "role-test-designer",
         "independent-auditor": "role-reviewer", "product-spec": "role-product-spec", "research": "role-research",
         "lead": "role-lead", "orchestrator": "role-lead"}


def _open_gate(home: Path, monkeypatch) -> None:
    from gov.resources import config as gate_config
    folder = home / ".gov-os" / "machine"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "gate.json").write_text(json.dumps(gate_config.template(cpus=list(range(20)))), encoding="utf-8")
    (folder / "meminfo").write_text("MemAvailable: 67108864 kB\n", encoding="utf-8")
    (folder / "loadavg").write_text("0.1 0.1 0.1 1/1 1\n", encoding="utf-8")
    for name, value in (("GOV_RESOURCES_MEMINFO", folder / "meminfo"), ("GOV_RESOURCES_LOADAVG", folder / "loadavg"),
                        ("GOV_RESOURCES_NPROC", 20), ("GOV_RESOURCES_BUSY_CORES", 0),
                        ("GOV_RESOURCES_EMBEDDING_CPU", '{"shared": 0, "query": 0}'),
                        ("GOV_RESOURCES_EMBEDDING_CPU_NOW", '{"shared": 0, "query": 0}'),
                        ("GOV_RESOURCES_DISK", '{"free_bytes": 1000000000000000, "free_inodes": 1000000000}')):
        monkeypatch.setenv(name, str(value))


def _ticket(root: Path, role: str, allowed: list[str]) -> str:
    tid = f"T-{role}"
    front = {"id": tid, "wbs_id": f"W9-{role}", "status": "in_progress", "priority": 1, "role": role,
             "allowed_paths": allowed, "depends_on": [], "deps": [], "needs": []}
    (root / ".tickets").mkdir(parents=True, exist_ok=True)
    (root / ".tickets" / f"{tid}.md").write_text("---\n" + yaml.safe_dump(front) + "---\n", encoding="utf-8")
    return tid


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project with every role's ticket, every role template copy, a CLI stand-in and a recording Popen."""
    root = tmp_path / "project"
    for role in ALL_ROLES:
        allowed = ["experiments/w153/**"] if role == "research" else ["src/x/**"]
        _ticket(root, "engineer" if role in launcher.LEAD_ROLES else role, allowed)
    (root / "experiments/w153").mkdir(parents=True)
    (root / launcher.KERNEL_ALLOWLIST_REL).parent.mkdir(parents=True)
    (root / launcher.KERNEL_ALLOWLIST_REL).write_text("hosts: [pypi.org]\n", encoding="utf-8")
    (root / launcher.TEMPLATES_REL).mkdir(parents=True)
    for stem in set(STEMS.values()):
        (root / launcher.TEMPLATES_REL / f"{stem}.md").write_text(f"# {stem}\n", encoding="utf-8")
    for name in ("GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(name, raising=False)
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    _open_gate(home, monkeypatch)
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    monkeypatch.setattr(launcher, "check_lead", lambda root, tid: {"admitted": True, "reason": "", "override": None})
    started = []

    class Session:
        def __init__(self, argv, cwd, env):
            started.append(argv)

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    return root, started


def _launch(project, role: str, args: list[str]) -> list[str]:
    root, started = project
    tid = "T-engineer" if role in launcher.LEAD_ROLES else f"T-{role}"
    assert launcher.launch(root, role, tid, args) == 0
    [argv] = started
    return argv


def _template(project, role: str) -> str:
    return str(Path(os.path.realpath(project[0])) / ".claude" / "templates" / f"{STEMS[role]}.md")


def test_every_launched_role_has_a_template_in_the_map():
    assert launcher.ROLE_TEMPLATES == STEMS
    assert set(ALL_ROLES) == set(launcher.ROLE_TEMPLATES)


@pytest.mark.parametrize("role", ALL_ROLES)
def test_the_flag_comes_after_the_callers_arguments_by_absolute_path(project, role):
    args = ["-p", "go", "--model", "haiku"]
    argv = _launch(project, role, args)
    assert argv[-2:] == ["--append-system-prompt-file", _template(project, role)]
    assert os.path.isabs(argv[-1])
    assert argv[-2 - len(args):-2] == args


@pytest.mark.parametrize("role", ALL_ROLES)
def test_the_launch_is_otherwise_what_it_was(project, role):
    """F2: without the one added flag the argv is the CLI, its --settings and the caller's arguments, as before."""
    args = ["-p", "go"]
    argv = _launch(project, role, args)
    assert argv[0] == str(Path(os.environ["HOME"]) / launcher.CLI_REL)
    assert argv[1] == "--settings" and argv[3:-2] == args and len(argv) == 3 + len(args) + 2
    assert argv.count("--append-system-prompt-file") == 1


@pytest.mark.parametrize("role", ALL_ROLES)
def test_a_missing_template_refuses_naming_the_path_and_starts_nothing(project, role):
    path = _template(project, role)
    os.unlink(path)
    tid = "T-engineer" if role in launcher.LEAD_ROLES else f"T-{role}"
    with pytest.raises(GovError) as raised:
        launcher.launch(project[0], role, tid, [])
    assert raised.value.code == "LAUNCH_NO_TEMPLATE" and path in raised.value.message
    assert project[1] == []


def test_a_template_that_is_a_folder_refuses(project):
    path = Path(_template(project, "engineer"))
    path.unlink()
    path.mkdir()
    with pytest.raises(GovError) as raised:
        launcher.launch(project[0], "engineer", "T-engineer", [])
    assert raised.value.code == "LAUNCH_NO_TEMPLATE"


# -- the dispatcher's lead form ---------------------------------------------------------------------------------------

def _launch_now(tmp_path: Path, with_template: bool) -> tuple[subprocess.CompletedProcess, Path]:
    """launch_now.sh with its absolute paths moved into tmp_path: a stub claude that records its argv."""
    home, orch, trees = tmp_path / "home", tmp_path / "orch", tmp_path / "trees"
    (home / ".local/bin").mkdir(parents=True)
    record = tmp_path / "argv.txt"
    stub = home / ".local/bin/claude"
    stub.write_text(f'#!/bin/bash\nprintf "%s\\n" "$@" > "{record}"\n', encoding="utf-8")
    stub.chmod(0o755)
    for folder in ("tools", "briefs", "log"):
        (orch / folder).mkdir(parents=True)
    (orch / "tools/disk_gate.sh").write_text("exit 0\n", encoding="utf-8")
    (orch / "briefs/B.md").write_text("brief\n", encoding="utf-8")
    tree = trees / "W9-1"
    (tree / ".claude/templates").mkdir(parents=True)
    if with_template:
        (tree / ".claude/templates/role-lead.md").write_text("# lead\n", encoding="utf-8")
    text = LAUNCH_NOW.read_text(encoding="utf-8")
    text = text.replace("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator", str(orch))
    text = text.replace("/home/usain/gov-os-worktrees", str(trees)).replace("/home/usain/.local", str(home / ".local"))
    script = tmp_path / "launch_now.sh"
    script.write_text(text, encoding="utf-8")
    done = subprocess.run(["bash", str(script), "W9-1", "T-1", "B.md", "L.json"], capture_output=True, text=True,
                          timeout=30)
    return done, record


def test_the_dispatchers_lead_form_passes_the_lead_template(tmp_path):
    done, record = _launch_now(tmp_path, with_template=True)
    assert done.returncode == 0, done.stderr
    argv = record.read_text(encoding="utf-8").splitlines()
    template = str(tmp_path / "trees/W9-1/.claude/templates/role-lead.md")
    assert argv[-2:] == ["--append-system-prompt-file", template]


def test_the_dispatchers_lead_form_is_otherwise_the_same_command():
    """F2: removing the added flag line leaves the exec command as integrate's (the call form kept, D-4)."""
    lines = LAUNCH_NOW.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("exec /home/usain/.local/bin/claude "))
    command = [line for line in lines[start:start + 6] if "--append-system-prompt-file" not in line]
    assert command[:4] == [
        "exec /home/usain/.local/bin/claude -p --model claude-opus-5-5 --effort high --output-format json "
        "--permission-mode acceptEdits \\",
        '  --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \\',
        '  --settings "{\\"env\\":{\\"GOV_ROLE\\":\\"orchestrator\\",\\"GOV_TICKET\\":\\"$ID\\",'
        '\\"CLAUDE_CODE_SUBAGENT_MODEL\\":\\"claude-opus-5-5\\"}}" \\',
        '  < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"',
    ]


def test_the_dispatchers_lead_form_refuses_without_the_template(tmp_path):
    done, record = _launch_now(tmp_path, with_template=False)
    assert done.returncode != 0 and not record.exists()
    assert "LAUNCH_NO_TEMPLATE" in done.stderr
    assert str(tmp_path / "trees/W9-1/.claude/templates/role-lead.md") in done.stderr
