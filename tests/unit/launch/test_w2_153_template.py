"""W2-153 builder tests: gov launch passes the role template as the appended system prompt, and refuses without it.

Regression evidence only (DEC-136). No CLI is started: a recording stand-in replaces ``subprocess.Popen``, under a
temporary HOME with an open resource gate. The dispatcher's lead form (launch_now.sh) is run with a stub ``claude``
on a copy whose absolute paths point into tmp_path.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import launcher
from gov.launch.role import JUDGING_ROLES, SKILLS_REL

from .test_w2_195_preload import install_judging_skill

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


# W2-60a (DAEO-cv58; P-3, DEC-1156 (7)): a worker launch refuses a project without its role's role file (version line,
# default line). The worker roles' default model is the one the cases pass after ``--`` (a model not the role's is
# refused since W2-60a). Since W2-60a (P-4 (A)) a worker is handed ONE appended file, ``<TMPDIR>/role-<role>.md``: the
# role file's bytes, one blank line, then the role template's bytes.
ROLE_MODEL = "claude-opus-5-5"
ROLES_REL = Path("template/governance/kernel/roles")
appended: list[dict] = []  # per started session: its TMPDIR and the bytes of each appended file, read at its start


def _role_text(role: str) -> str:
    return (f"# {role} role (W2-153 fixture)\n\nThe marker zq153-role-{role}.\n\n- **Version:** 1.0.0\n"
            f"- **Launch default:** model {ROLE_MODEL}, effort high\n")


def _plant_role_files(root: Path) -> None:
    for role in launcher.WORKER_ROLES:
        path = root / ROLES_REL / f"{role}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_role_text(role), encoding="utf-8")
    install_judging_skill(root)  # a judging role launches with the judging-work skill (W2-195, DEC-1204 (5))


def _assert_one_appended_role_file(project, role: str, argv: list[str]) -> None:
    """A worker's one appended file: ``role-<role>.md`` in the session's temp folder, by absolute path, last on the
    line; it starts with the role file's bytes and ends with the role template's bytes; between them only blank, but
    for a judging role the judging-work skill's preloaded copy, the one skill its role file names (W2-195)."""
    root = Path(os.path.realpath(project[0]))
    [seen] = appended
    assert argv.count("--append-system-prompt-file") == 1, argv
    assert argv[-2] == "--append-system-prompt-file" and os.path.isabs(argv[-1]), argv
    assert Path(argv[-1]).name == f"role-{role}.md", argv[-1]
    assert seen["tmpdir"] and Path(argv[-1]).parent == Path(seen["tmpdir"]), (argv[-1], seen["tmpdir"])
    [data] = seen["files"]
    assert data is not None, f"the appended file {argv[-1]} could not be read when the session started"
    role_bytes = (root / ROLES_REL / f"{role}.md").read_bytes()
    template_bytes = (root / launcher.TEMPLATES_REL / f"{STEMS[role]}.md").read_bytes()
    assert data.startswith(role_bytes), f"{role}: the appended file does not start with the role file: {data!r}"
    assert data.endswith(template_bytes), f"{role}: the appended file does not end with the template: {data!r}"
    skill = (root / SKILLS_REL / "judging-work/SKILL.md").read_bytes() if role in JUDGING_ROLES else b""
    assert data[len(role_bytes):len(data) - len(template_bytes)].strip() == skill.strip(), data


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
    _plant_role_files(root)
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
    appended.clear()

    class Session:
        def __init__(self, argv, cwd, env):
            started.append(argv)
            # The appended file lives in the session's temp folder, which goes when the session ends: read it now.
            values = [argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == "--append-system-prompt-file"]
            appended.append({"tmpdir": env.get("TMPDIR"),
                             "files": [Path(value).read_bytes() if os.path.isfile(value) else None
                                       for value in values]})

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
    # DEC-1225 (R2): a lead's --model other than the launcher's own Sonnet is refused, so a lead passes its own
    args = ["-p", "go", "--model", ROLE_MODEL if role in launcher.WORKER_ROLES else launcher.LEAD_MODEL]
    argv = _launch(project, role, args)
    if role in launcher.WORKER_ROLES:
        _assert_one_appended_role_file(project, role, argv)
    else:
        assert argv[-2:] == ["--append-system-prompt-file", _template(project, role)]
    assert os.path.isabs(argv[-1])
    assert argv[-2 - len(args):-2] == args


@pytest.mark.parametrize("role", ALL_ROLES)
def test_the_launch_is_otherwise_what_it_was(project, role):
    """F2: without the one added flag the argv is the CLI, its --settings and the caller's arguments, as before."""
    args = ["-p", "go"]
    argv = _launch(project, role, args)
    assert argv[0] == str(Path(os.environ["HOME"]) / launcher.CLI_REL)
    assert argv[1] == "--settings" and argv[-2 - len(args):-2] == args
    assert argv.count("--append-system-prompt-file") == 1 and argv[-2] == "--append-system-prompt-file"
    # W2-60a (DAEO-cv58): a worker's line also carries the role's default model and effort, its session id and the
    # two switches that keep user-level context out; nothing else is added. A lead's line is as it was.
    between = _options(argv[3:-2 - len(args)])
    if role in launcher.WORKER_ROLES:
        # Emergency 2 (2.3): the launcher's own no-prompt mode, the caller naming none
        assert between.pop("--permission-mode", None) == "bypassPermissions", argv
        assert set(between) == {"--model", "--effort", "--session-id", "--strict-mcp-config", "--setting-sources"}, argv
        assert (between["--model"], between["--effort"]) == (ROLE_MODEL, "high"), argv
        assert between["--strict-mcp-config"] is None and between["--setting-sources"] == "project,local", argv
        assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", between["--session-id"])
    else:
        # Emergency 2 (2.3): a lead's too; DEC-1225 (R2): and the launcher adds the lead's model, Sonnet
        assert between == {"--permission-mode": "bypassPermissions", "--model": launcher.LEAD_MODEL}, argv


def _options(items: list[str]) -> dict:
    """``{option: value or None}`` of a run of options; a repeated option or a stray value fails."""
    found, index = {}, 0
    while index < len(items):
        name = items[index]
        assert name.startswith("--") and name not in found, f"not one run of distinct options: {items}"
        if name == "--strict-mcp-config":
            found[name], index = None, index + 1
        else:
            assert index + 1 < len(items), f"{name} without a value: {items}"
            found[name], index = items[index + 1], index + 2
    return found


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
    # DEC-1133 (3): the lead form checks the resource gate and registers the lead with gov; here the gate is open.
    gov = home / ".local/bin/gov"
    gov.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
    gov.chmod(0o755)
    for folder in ("tools", "briefs", "log"):
        (orch / folder).mkdir(parents=True)
    (orch / "tools/disk_gate.sh").write_text("exit 0\n", encoding="utf-8")
    (orch / "briefs/B.md").write_text("brief\n", encoding="utf-8")
    tree = trees / "W9-1"
    (tree / ".claude/templates").mkdir(parents=True)
    if with_template:
        (tree / ".claude/templates/role-lead.md").write_text("# lead\n", encoding="utf-8")
    # ACT-BOX-LAUNCH-1 (DEC-1207 (b)): the lead form starts the lead through the owner's pinned box when it names one;
    # a stub pinned box records its arguments and runs the command after "--" (a no-op for a form without the box).
    box = home / ".gov-os-owner/box"
    box.mkdir(parents=True)
    (home / ".gov-os-owner/heldout").mkdir()
    (home / ".gov-os-owner/heldout/MAP").write_text("", encoding="utf-8")
    boxed = tmp_path / "box-argv.txt"
    (box / "session_start.sh").write_text(
        f'#!/bin/bash\nprintf "%s\\n" "$@" > "{boxed}"\nwhile [ $# -gt 0 ] && [ "$1" != -- ]; do shift; done\nshift\n'
        'exec "$@"\n', encoding="utf-8")
    text = LAUNCH_NOW.read_text(encoding="utf-8")
    text = text.replace("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator", str(orch))
    text = text.replace("/home/usain/gov-os-worktrees", str(trees)).replace("/home/usain/.local", str(home / ".local"))
    text = text.replace("/home/usain/.gov-os-owner", str(home / ".gov-os-owner"))
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
    if "session_start.sh" in LAUNCH_NOW.read_text(encoding="utf-8"):  # ACT-BOX-LAUNCH-1: the lead runs in the box
        box = (tmp_path / "box-argv.txt").read_text(encoding="utf-8").splitlines()
        assert box[box.index("--scope") + 1] == "tree" and box[box.index("--ticket") + 1] == "T-1"
        assert box[box.index("--rw") + 1] == str(tmp_path / "trees/W9-1")


def test_the_dispatchers_lead_form_is_otherwise_the_same_command():
    """F2: removing the added flag line leaves the exec command as integrate's (the call form kept, D-4)."""
    lines = LAUNCH_NOW.read_text(encoding="utf-8").splitlines()
    # ACT-BOX-LAUNCH-1 (DEC-1207 (b), DEC-1205 (2)(iii)) puts the box's start before the CLI and the CLI's own line
    # after it, with full permission inside the box; without the box the CLI line is the exec itself, as at W2-153.
    start = next(i for i, line in enumerate(lines)
                 if line.startswith(("exec /home/usain/.local/bin/claude ", "  /home/usain/.local/bin/claude ")))
    boxed = lines[start].startswith("  ")
    if boxed:
        assert lines[start - 2].startswith('exec bash "$BOX/session_start.sh" ')
    head = lines[start].strip()
    lines = lines[:start] + [head if head.startswith("exec ") else "exec " + head] + lines[start + 1:]
    mode = "bypassPermissions"  # the owner's Emergency 2 (bb61d3d74, DEC-1209): every lead starts in the no-prompt mode
    # ACT-LEADS-ADD-DIR-1 (DEC-1161 (2)) added the lead's --add-dir line after W2-153; it is judged apart from this.
    command = [line for line in lines[start:start + 7]
               if "--append-system-prompt-file" not in line and not line.startswith("  --add-dir ")]
    assert command[:4] == [
        "exec /home/usain/.local/bin/claude -p --model claude-sonnet-5-5 --effort high --output-format json "
        f"--permission-mode {mode} \\",
        '  --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \\',
        '  --settings "{\\"env\\":{\\"GOV_ROLE\\":\\"orchestrator\\",\\"GOV_TICKET\\":\\"$ID\\",'
        '\\"CLAUDE_CODE_SUBAGENT_MODEL\\":\\"claude-sonnet-5-5\\"}}" \\',
        '  < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"',
    ]


def test_the_dispatchers_lead_form_refuses_without_the_template(tmp_path):
    done, record = _launch_now(tmp_path, with_template=False)
    assert done.returncode != 0 and not record.exists()
    assert "LAUNCH_NO_TEMPLATE" in done.stderr
    assert str(tmp_path / "trees/W9-1/.claude/templates/role-lead.md") in done.stderr
