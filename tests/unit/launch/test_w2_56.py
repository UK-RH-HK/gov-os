"""Builder tests for W2-56 (DAEO-wnnz): the launcher's cleaned environment, refused arguments, process group and
temp-folder removal. The sandbox module's own block and placeholders were retired with it (EMERGENCY-2 6.1).

Regression evidence only (DEC-136). Every place is a temporary folder under a stand-in HOME; the CLI is a stand-in
script; no reranker, model or real sandbox is started.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import environ, launcher  # noqa: E402
from gov.util.gitenv import git_env  # noqa: E402


def _open_gate(home: Path, monkeypatch) -> None:
    """An open resource gate under this HOME (as tests/unit/launch/test_runs.py plants it)."""
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


def _plant_templates(root: Path) -> None:
    """Every role's template copy a session starts with (W2-153 S1, DEC-1112 (3)): any content will do."""
    for stem in set(launcher.ROLE_TEMPLATES.values()):
        path = root / launcher.TEMPLATES_REL / f"{stem}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {stem}\n", encoding="utf-8")


def _plant_role_files(root: Path, roles=("engineer",)) -> None:
    """W2-60a (DAEO-cv58; P-3, DEC-1156 (7)): a worker launch refuses a project without its role's role file (version
    and default line); these projects are in the adopted layout (no ``template/``): ``governance/kernel/roles/``."""
    for role in roles:
        path = root / "governance" / "kernel" / "roles" / f"{role}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {role} role (W2-56 fixture)\n\n- **Version:** 1.0.0\n"
                        "- **Launch default:** model claude-opus-5-5, effort high\n", encoding="utf-8")


# --- S5: the cleaned environment -------------------------------------------------------------------------------------

PARENT = {"PATH": "/a:/b", "HOME": "/home/x", "LANG": "C.UTF-8", "LC_ALL": "C", "USER": "x", "LOGNAME": "x",
          "TMPDIR": "/tmp/parent", "PYTHONPATH": "/src", "GOV_DEV_TIERS": "1", "GOV_ROLE": "orchestrator",
          "CLAUDE_CODE_SESSION_ID": "s", "CLAUDE_CODE_MESSAGING_SOCKET": "/s", "CLAUDE_CODE_MESSAGING_TOKEN": "t",
          "CLAUDE_EFFORT": "high", "CLAUDECODE": "1", "W2_56_UNRELATED": "u", "ANTHROPIC_API_KEY": "k",
          "CLAUDE_CODE_OAUTH_TOKEN": "o"}
OWN = {"GOV_ROLE": "engineer", "GOV_TICKET": "T-1", "TMPDIR": "/tmp/gov-launch-ab", "CLAUDE_CODE_TMPDIR": "/tmp/gov-launch-ab"}


def test_the_settings_env_holds_the_kept_variables_and_the_launchers_own_alone():
    assert environ.settings_env(PARENT, OWN) == {
        "PATH": "/a:/b", "HOME": "/home/x", "LANG": "C.UTF-8", "LC_ALL": "C", "USER": "x", "LOGNAME": "x", **OWN}


def test_the_session_env_adds_the_sign_in_variables_and_nothing_else():
    env = environ.session_env(PARENT, OWN)
    assert set(env) - set(environ.settings_env(PARENT, OWN)) == {"ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"}
    assert env["GOV_ROLE"] == "engineer" and env["TMPDIR"] == "/tmp/gov-launch-ab"
    for name in ("PYTHONPATH", "GOV_DEV_TIERS", "CLAUDECODE", "CLAUDE_EFFORT", "CLAUDE_CODE_SESSION_ID",
                 "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "W2_56_UNRELATED"):
        assert name not in env, name


# --- S6, F2: the refused arguments ------------------------------------------------------------------------------------

@pytest.mark.parametrize("flag", launcher.GUARD_FLAGS)
@pytest.mark.parametrize("form", ("alone", "spaced", "equals", "later"))
def test_each_guard_argument_is_refused_in_every_form_and_named(flag, form):
    args = {"alone": [flag], "spaced": [flag, "x"], "equals": [f"{flag}=x"], "later": ["-p", "hi", flag, "x"]}[form]
    with pytest.raises(GovError) as refused:
        launcher._check_cli_args(args)
    assert refused.value.code == "LAUNCH_REFUSED" and flag in refused.value.message


@pytest.mark.parametrize("flag", launcher.GUARD_FLAGS)
def test_a_prompt_that_names_a_guard_argument_among_other_words_starts(flag):
    launcher._check_cli_args(["-p", f"never pass {flag} to anything", "--model", "haiku"])


# Emergency 2 (0.1.2): the bypass, --add-dir and --bare no longer refuse.
@pytest.mark.parametrize("args", (["--settings", "{}"], ["--setting-sources", "user"]))
def test_the_refusals_of_today_still_refuse(args):
    with pytest.raises(GovError):
        launcher._check_cli_args(args)


# --- S15: the temp folder goes whole ----------------------------------------------------------------------------------

def test_a_folder_with_unwritable_folders_a_fifo_and_a_link_is_removed_and_the_target_kept(tmp_path):
    folder, target = tmp_path / "gov-launch-ab", tmp_path / "outside.txt"
    target.write_text("keep\n", encoding="utf-8")
    (folder / "cache/mod").mkdir(parents=True)
    (folder / "cache/mod/a.py").write_text("x\n", encoding="utf-8")
    (folder / "cache/mod").chmod(0o500)
    (folder / "cache").chmod(0o500)
    (folder / "closed").mkdir()
    (folder / "closed").chmod(0o000)
    os.mkfifo(folder / "fifo")
    (folder / "link").symlink_to(target)
    (folder / "dirlink").symlink_to(tmp_path, target_is_directory=True)
    launcher._remove(str(folder))
    assert not os.path.lexists(folder) and target.read_text(encoding="utf-8") == "keep\n"
    assert tmp_path.is_dir() and target.exists()  # the folder a link named is not removed


# --- S12: the ending reaches the group --------------------------------------------------------------------------------

GROUP = textwrap.dedent("""\
    import signal, subprocess, sys, time
    child = subprocess.Popen([sys.executable, "-c",
        "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); open(%r, 'w').write('up'); time.sleep(60)"])
    signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
    time.sleep(60)
""")


def _wait_for(path: Path, seconds: float = 10.0) -> None:
    deadline = time.monotonic() + seconds
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert path.exists()


def test_the_session_leads_its_own_group_and_the_kill_after_the_wait_reaches_a_grandchild(tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "END_WAIT_S", 1)
    up = tmp_path / "up"
    session = launcher._start([sys.executable, "-c", GROUP % str(up)], tmp_path, dict(os.environ), None)
    try:
        _wait_for(up)
        assert os.getpgid(session.pid) == session.pid != os.getpgrp()
        state = {"session": session, "asked": True, "deadline": time.monotonic() + launcher.END_WAIT_S}
        launcher._signal_session(session, signal.SIGTERM)
        session.wait(10)
        assert launcher._group_alive(session)  # the grandchild ignores SIGTERM
        started = time.monotonic()
        launcher._end_group(state)
        assert not launcher._group_alive(session) and time.monotonic() - started < launcher.END_WAIT_S + 5
    finally:
        if launcher._group_alive(session):
            os.killpg(session.pid, signal.SIGKILL)
        session.wait()


def test_what_a_session_that_ended_by_itself_left_in_its_group_is_ended(tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "END_WAIT_S", 1)
    up = tmp_path / "up"
    script = GROUP.replace('signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))\ntime.sleep(60)\n',
                           f'while not os.path.exists({str(up)!r}): time.sleep(0.02)\nsys.exit(3)\n')
    script = "import os\n" + script
    assert "sys.exit(3)" in script
    session = launcher._start([sys.executable, "-c", script % str(up)], tmp_path, dict(os.environ), None)
    try:
        assert session.wait(10) == 3
        _wait_for(up)
        launcher._end_group({"session": session, "asked": False, "deadline": None})
        assert not launcher._group_alive(session)
    finally:
        if launcher._group_alive(session):
            os.killpg(session.pid, signal.SIGKILL)


# --- The whole launch with a stand-in CLI -----------------------------------------------------------------------------

CLI = textwrap.dedent("""\
    #!{python}
    import json, os, sys
    settings = json.loads(sys.argv[sys.argv.index("--settings") + 1])
    os.makedirs(os.path.join(os.environ["TMPDIR"], "cache", "mod"))
    os.chmod(os.path.join(os.environ["TMPDIR"], "cache"), 0o500)
    with open({out!r}, "w") as out:
        json.dump({{"env": dict(os.environ), "settings": settings, "pgid": os.getpgrp(), "pid": os.getpid()}}, out)
    args = sys.argv[:-2] if sys.argv[-2:-1] == ["--append-system-prompt-file"] else sys.argv  # W2-153's appended pair
    sys.exit(int(args[-1]))
""")


@pytest.fixture
def launched(tmp_path, monkeypatch):
    home, temp, project = tmp_path / "home", tmp_path / "temp", tmp_path / "project"
    for folder in (home / ".local/bin", temp, project / ".tickets"):
        folder.mkdir(parents=True)
    out = tmp_path / "out.json"
    cli = home / launcher.CLI_REL
    cli.write_text(CLI.format(python=sys.executable, out=str(out)), encoding="utf-8")
    cli.chmod(0o755)
    (project / ".tickets/TST-a001.md").write_text(
        "---\nid: TST-a001\nwbs_id: W2-90\nstatus: in_progress\nrole: engineer\n---\n", encoding="utf-8")
    _plant_templates(project)
    _plant_role_files(project)
    monkeypatch.setenv("HOME", str(home))
    _open_gate(home, monkeypatch)
    for name, value in (("GOV_DEV_TIERS", "1"), ("PYTHONPATH", "/x"), ("CLAUDE_CODE_SESSION_ID", "s"),
                        ("W2_56_UNRELATED", "u")):
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)

    def _launch(code=0, args=()):
        found = launcher.launch(project, "engineer", "TST-a001", [*args, str(code)])
        return found, json.loads(out.read_text(encoding="utf-8")), temp

    return _launch


@pytest.mark.parametrize("code", (0, 3))
def test_a_launch_passes_the_cleaned_env_and_removes_its_folder(launched, code):
    found, seen, temp = launched(code)
    assert found == code and os.listdir(temp) == []
    env, settings = seen["env"], seen["settings"]
    for name in ("GOV_DEV_TIERS", "PYTHONPATH", "CLAUDE_CODE_SESSION_ID", "W2_56_UNRELATED"):
        assert name not in env and name not in settings["env"], name
    assert env["TMPDIR"] == env["CLAUDE_CODE_TMPDIR"] == settings["env"]["TMPDIR"]
    assert Path(env["TMPDIR"]).parent == temp and Path(env["TMPDIR"]).name.startswith("gov-launch-")
    assert len(Path(env["TMPDIR"]).name) == len("gov-launch-") + 8
    assert env["PATH"] == os.environ["PATH"] and settings["env"]["GOV_ROLE"] == "engineer"
    assert seen["pgid"] == seen["pid"]


def test_a_cli_that_cannot_be_started_is_refused_and_leaves_no_folder(launched, tmp_path):
    (tmp_path / "home" / launcher.CLI_REL).chmod(0o644)
    with pytest.raises(GovError):
        launched()
    assert os.listdir(tmp_path / "temp") == []


# --- S14 (round 2, P-3): the template's rulesync source keeps the one allow rule through a regeneration ---------------
# Rewrite-Reason: DEC-1217 (6), W2-208 K1: the kit writes two deny lines only and no allow line; the source and the
# kernel settings allow nothing, and a regeneration of the template writes no allow rule.

TEMPLATE_SOURCE = REPO / "template" / ".rulesync" / "permissions.jsonc"
TEMPLATE_SETTINGS = REPO / "template" / "governance" / "kernel" / "settings.json"


def _jsonc(path: Path) -> dict:
    return json.loads("\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                                if not line.lstrip().startswith("//")))


def _kernel_allow() -> list:
    permissions = json.loads(TEMPLATE_SETTINGS.read_text(encoding="utf-8")).get("permissions") or {}
    return list(permissions.get("allow") or [])


def test_the_rulesync_source_allows_exactly_the_kernel_settings_allow_rule():
    """Rewrite-Reason: DEC-1217 (6), W2-208 K1: both allow nothing (it was ``["Bash(gov launch:*)"]``)."""
    source = _jsonc(TEMPLATE_SOURCE)["permission"]
    allowed = [f"Bash({key})" for key, value in source.get("bash", {}).items() if value == "allow"]
    allowed += [f"{tool.capitalize()}({key})" for tool, rules in source.items() if tool != "bash"
                for key, value in rules.items() if value == "allow"]
    assert allowed == _kernel_allow() == []


@pytest.mark.skipif(shutil.which("rulesync") is None, reason="rulesync is not on PATH")
def test_a_rulesync_regeneration_of_the_template_keeps_the_allow_rule(tmp_path):
    """The generation itself (the template's sources only read; the output in an empty folder).
    Rewrite-Reason: DEC-1217 (6), W2-208 K1: the regeneration writes no allow rule, as the kernel settings hold none."""
    done = subprocess.run(["rulesync", "generate", "--targets", "claudecode", "--features", "permissions,hooks",
                           "--input-roots", str(TEMPLATE_SOURCE.parent)], cwd=tmp_path, capture_output=True,
                          text=True, timeout=120)
    assert done.returncode == 0, done.stderr[-1000:]
    generated = json.loads((tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8"))
    kernel = json.loads(TEMPLATE_SETTINGS.read_text(encoding="utf-8"))
    assert list((generated.get("permissions") or {}).get("allow") or []) == _kernel_allow() == []
    # The guard's PreToolUse line left both with the guard (EMERGENCY-2 6.1, DAEO-gr7t).
    assert "PreToolUse" not in generated.get("hooks", {}) and "hooks" not in kernel
