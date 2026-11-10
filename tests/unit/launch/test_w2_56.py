"""Builder tests for W2-56 (DAEO-wnnz): the launcher's cleaned environment, refused arguments, sandbox block,
placeholders, process group and temp-folder removal.

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
from gov.launch import environ, launcher, sandbox  # noqa: E402
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


@pytest.mark.parametrize("args", (["--dangerously-skip-permissions"], ["--permission-mode", "bypassPermissions"],
                                  ["--add-dir=/x"], ["--settings", "{}"], ["--bare"], ["--setting-sources", "user"]))
def test_the_refusals_of_today_still_refuse(args):
    with pytest.raises(GovError):
        launcher._check_cli_args(args)


# --- S8, S9, S11: the sandbox block -----------------------------------------------------------------------------------

def test_the_socket_and_the_log_are_the_services_own_under_home(tmp_path):
    assert sandbox.socket_path(tmp_path) == str(tmp_path / ".cache/gov-os/rerank.sock")
    assert sandbox.network([], tmp_path) == {"strictAllowlist": True, "allowedDomains": [],
                                             "allowUnixSockets": [str(tmp_path / ".cache/gov-os/rerank.sock")]}


def test_the_log_is_made_a_regular_file_of_the_users_own_and_put_on_the_write_list(tmp_path):
    block = sandbox.filesystem("/tmp/gov-launch-ab", "/home/x/gov-os-runs/W2-1", tmp_path)
    log = tmp_path / ".cache/gov-os/rerank.log"
    assert block == {"allowWrite": ["//tmp/gov-launch-ab", "//home/x/gov-os-runs/W2-1", f"/{log}"]}
    assert stat.S_ISREG(log.lstat().st_mode) and stat.S_IMODE(log.lstat().st_mode) == 0o600
    assert stat.S_IMODE((tmp_path / ".cache/gov-os").stat().st_mode) == 0o700


def test_a_log_that_is_a_link_is_left_off_and_its_target_untouched(tmp_path):
    (tmp_path / ".cache/gov-os").mkdir(parents=True)
    target = tmp_path / "target.txt"
    target.write_text("keep\n", encoding="utf-8")
    (tmp_path / ".cache/gov-os/rerank.log").symlink_to(target)
    assert sandbox.filesystem("/t", None, tmp_path) == {"allowWrite": ["//t"]}
    assert target.read_text(encoding="utf-8") == "keep\n"


def test_a_log_that_is_a_folder_is_left_off(tmp_path):
    (tmp_path / ".cache/gov-os/rerank.log").mkdir(parents=True)
    assert sandbox.filesystem("/t", None, tmp_path) == {"allowWrite": ["//t"]}


def test_a_socket_that_is_a_link_is_not_allowed(tmp_path):
    (tmp_path / ".cache/gov-os").mkdir(parents=True)
    (tmp_path / ".cache/gov-os/rerank.sock").symlink_to(tmp_path / "other.sock")
    assert sandbox.reranker_socket(tmp_path) == []


def test_a_cache_folder_that_is_a_link_allows_neither(tmp_path):
    (tmp_path / "elsewhere").mkdir()
    (tmp_path / ".cache").mkdir()
    (tmp_path / ".cache/gov-os").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    assert sandbox.reranker_socket(tmp_path) == [] and sandbox.reranker_log(tmp_path) == []
    assert list((tmp_path / "elsewhere").iterdir()) == []


def _built(home: Path) -> dict:
    return {"sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                        "network": sandbox.network([], home), "filesystem": sandbox.filesystem("/t", None, home)}}


def test_the_built_block_has_no_fault(tmp_path):
    assert sandbox.faults(_built(tmp_path), tmp_path) == []


def test_the_socket_written_with_two_slashes_is_the_same(tmp_path):
    settings = _built(tmp_path)
    settings["sandbox"]["network"]["allowUnixSockets"] = ["/" + sandbox.socket_path(tmp_path)]
    assert sandbox.faults(settings, tmp_path) == []


@pytest.mark.parametrize("change", (
    lambda b, s: b.update(enabled=False),
    lambda b, s: b.update(failIfUnavailable=False),
    lambda b, s: b.update(allowUnsandboxedCommands=True),
    lambda b, s: b["network"].update(strictAllowlist=False),
    lambda b, s: b.update(excludedCommands=["git"]),
    lambda b, s: b.update(enableWeakerNestedSandbox=True),
    lambda b, s: b["network"].update(allowAllUnixSockets=True),
    lambda b, s: b["network"].update(allowLocalBinding=True),
    lambda b, s: b["network"].update(httpProxyPort=8080),
    lambda b, s: b["network"].update(socksProxyPort=1080),
    lambda b, s: b["network"]["allowUnixSockets"].append("/run/other.sock"),
    lambda b, s: b["network"].update(allowUnixSockets=["/run/other.sock"]),
    lambda b, s: b["network"].update(allowUnixSockets=[s.replace("rerank.sock", "*.sock")]),
    lambda b, s: b["network"].update(allowUnixSockets=[os.path.dirname(s)]),
    lambda b, s: b["filesystem"].update(allowRead=["/"]),
), ids=("enabled", "fail-if-unavailable", "unsandboxed", "strict", "excluded", "weaker-nested", "all-sockets",
        "local-binding", "http-port", "socks-port", "second-socket", "other-socket", "socket-pattern",
        "socket-folder", "filesystem-key"))
def test_each_widening_is_a_fault(tmp_path, change):
    settings = _built(tmp_path)
    change(settings["sandbox"], sandbox.socket_path(tmp_path))
    assert sandbox.faults(settings, tmp_path)


def test_the_launchers_sandbox_faults_reads_the_socket_from_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert launcher.sandbox_faults(_built(tmp_path)) == []
    monkeypatch.setenv("HOME", str(tmp_path / "other"))
    assert launcher.sandbox_faults(_built(tmp_path))


# --- S4: the placeholders ---------------------------------------------------------------------------------------------

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                          env=git_env(root)).stdout


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "first")
    worktree = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", str(worktree))
    (worktree / ".gov-runtime/scratch").mkdir(parents=True)
    (worktree / ".gov-runtime/records").mkdir()
    return main, worktree


def test_no_placeholder_is_staged_in_any_worktree_and_an_ordinary_file_is(tmp_path):
    main, worktree = _repository(tmp_path)
    root = Path(os.path.realpath(worktree))
    deny = launcher._runtime_rules(root) + launcher._tree_rules(root, "engineer")
    sandbox.exclude_placeholders(root, deny)
    sandbox.exclude_placeholders(root, deny)  # a second launch adds nothing
    planted = [*sandbox.PLACEHOLDER_NAMES, *sandbox.PLACEHOLDER_PATHS,
               *(f".gov-runtime/{'scratch'[:i]}" for i in range(1, 7)), "tests/acceptance"]
    for rel in planted:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).touch()
    (root / "docs").mkdir()
    (root / "docs/gitconfig-notes.md").write_text("x\n", encoding="utf-8")
    (root / "new.txt").write_text("x\n", encoding="utf-8")
    for place in (root, main):  # the worktree, and another worktree of the same repository
        _git(place, "add", "-A")
    assert sorted(_git(root, "diff", "--cached", "--name-only").split()) == ["docs/gitconfig-notes.md", "new.txt"]
    exclude = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude").strip())
    text = exclude.read_text(encoding="utf-8")
    assert text.count(sandbox.EXCLUDE_MARK) == 1 and text.count("\n.bashrc\n") == 1


def test_a_folder_at_a_placeholder_name_is_still_added(tmp_path):
    _, worktree = _repository(tmp_path)
    root = Path(os.path.realpath(worktree))
    sandbox.exclude_placeholders(root, [])
    (root / ".claude/commands").mkdir(parents=True)
    (root / ".claude/commands/a.md").write_text("x\n", encoding="utf-8")
    (root / ".idea").mkdir()
    (root / ".idea/b.xml").write_text("x\n", encoding="utf-8")
    _git(root, "add", "-A")
    assert sorted(_git(root, "diff", "--cached", "--name-only").split()) == [".claude/commands/a.md", ".idea/b.xml"]


def test_a_root_outside_any_repository_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    sandbox.exclude_placeholders(tmp_path, [])
    assert list(tmp_path.iterdir()) == []


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
    assert settings["sandbox"]["network"]["allowUnixSockets"] == [sandbox.socket_path()]
    allow = settings["sandbox"]["filesystem"]["allowWrite"]
    assert allow[0] == f"/{env['TMPDIR']}" and allow[-1] == f"/{sandbox.log_path()}" and len(allow) <= 3
    assert all(entry.startswith(f"/{os.path.realpath(env['HOME'])}/gov-os-runs/") for entry in allow[1:-1])
    assert launcher.sandbox_faults(settings) == []


def test_a_cli_that_cannot_be_started_is_refused_and_leaves_no_folder(launched, tmp_path):
    (tmp_path / "home" / launcher.CLI_REL).chmod(0o644)
    with pytest.raises(GovError):
        launched()
    assert os.listdir(tmp_path / "temp") == []


# --- S7 (round 2, the CTO's item 4): no path under a .git folder in the settings the launcher builds ----------------

def _strings(value):
    """Every string of a settings value, keys and values, at any depth."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _under_a_git_folder(text: str) -> bool:
    return ".git" in text.replace("(", "/").replace(")", "/").split("/")


def test_a_worktree_sessions_settings_name_no_path_under_a_git_folder(tmp_path, monkeypatch):
    """Lens E F17: the CLI's sandbox binds each existing path its settings deny (``--ro-bind <path> <path>``), so a git
    lock file named there, or beside a git file the settings name, can vanish between the build and the mount. The
    launcher's own settings (deny rules, write list, socket, env) name no path in or under any ``.git`` folder, for a
    worktree that shares its repository's ``.git``; the git folder's own protections are the CLI's (CIT-E, S7)."""
    home, temp, main = tmp_path / "home", tmp_path / "temp", tmp_path / "main"
    for folder in (home / ".local/bin", temp, main):
        folder.mkdir(parents=True)
    git = git_env(main)
    subprocess.run(["git", "init", "-q", str(main)], check=True, env=git)
    (main / ".tickets").mkdir()
    (main / ".tickets/TST-a001.md").write_text(
        "---\nid: TST-a001\nwbs_id: W2-90\nstatus: in_progress\nrole: engineer\n---\n", encoding="utf-8")
    (main / ".gov-runtime/scratch").mkdir(parents=True)
    (main / ".gov-runtime/rebuild").mkdir()
    subprocess.run(["git", "-C", str(main), "add", ".tickets"], check=True, env=git)
    subprocess.run(["git", "-C", str(main), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "t"],
                   check=True, env=git)
    worktree = tmp_path / "W2-77"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", str(worktree)], check=True, env=git)
    (worktree / ".gov-runtime/scratch").mkdir(parents=True)
    _plant_templates(worktree)
    for lock in ("config.lock", "index.lock", "HEAD.lock"):  # a git command in another worktree holds its locks now
        (main / ".git" / lock).write_text("", encoding="utf-8")
    out = tmp_path / "out.json"
    cli = home / launcher.CLI_REL
    cli.write_text(CLI.format(python=sys.executable, out=str(out)), encoding="utf-8")
    cli.chmod(0o755)
    monkeypatch.setenv("HOME", str(home))
    _open_gate(home, monkeypatch)
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    for root in (main, worktree):
        for role in ("engineer", "independent-test-designer"):
            built = launcher.build_settings(Path(os.path.realpath(root)), role, "TST-a001")
            assert [text for text in _strings(built) if _under_a_git_folder(text)] == [], (root.name, role)
    assert launcher.launch(worktree, "engineer", "TST-a001", ["0"]) == 0
    seen = json.loads(out.read_text(encoding="utf-8"))["settings"]
    assert [text for text in _strings(seen) if _under_a_git_folder(text)] == []
    assert launcher.sandbox_faults(seen) == []


def test_the_research_fence_names_no_git_folder(tmp_path):
    """The one launcher rule that lists a folder's entries leaves ``.git`` out at the top (it is the session's to commit
    through), so neither ``.git`` nor a lock file in it is named."""
    root = tmp_path / "repo"
    for rel in (".git", "experiments/x", "src"):
        (root / rel).mkdir(parents=True)
    (root / ".git" / "config.lock").write_text("", encoding="utf-8")
    rules = launcher._fence_rules(root, str(root / "experiments" / "x"))
    assert rules and not [rule for rule in rules if _under_a_git_folder(rule)]


def test_the_git_name_check_sees_each_form():
    for text in ("Edit(//r/.git/config.lock)", "/r/.git", "/r/.git/worktrees/W2-77/index.lock", "Edit(/r/.git/**)"):
        assert _under_a_git_folder(text), text
    for text in ("Edit(//r/.gitignore)", "/r/.github/x", "/tmp/gov-launch-ab", "Edit(//r/.gov-runtime/rebuild)"):
        assert not _under_a_git_folder(text), text


# --- S14 (round 2, P-3): the template's rulesync source keeps the one allow rule through a regeneration ---------------

TEMPLATE_SOURCE = REPO / "template" / ".rulesync" / "permissions.jsonc"
TEMPLATE_SETTINGS = REPO / "template" / "governance" / "kernel" / "settings.json"


def _jsonc(path: Path) -> dict:
    return json.loads("\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                                if not line.lstrip().startswith("//")))


def test_the_rulesync_source_allows_exactly_the_kernel_settings_allow_rule():
    source = _jsonc(TEMPLATE_SOURCE)["permission"]
    allowed = [f"Bash({key})" for key, value in source.get("bash", {}).items() if value == "allow"]
    allowed += [f"{tool.capitalize()}({key})" for tool, rules in source.items() if tool != "bash"
                for key, value in rules.items() if value == "allow"]
    assert allowed == json.loads(TEMPLATE_SETTINGS.read_text(encoding="utf-8"))["permissions"]["allow"] \
        == ["Bash(gov launch:*)"]


@pytest.mark.skipif(shutil.which("rulesync") is None, reason="rulesync is not on PATH")
def test_a_rulesync_regeneration_of_the_template_keeps_the_allow_rule(tmp_path):
    """The generation itself (the template's sources only read; the output in an empty folder)."""
    done = subprocess.run(["rulesync", "generate", "--targets", "claudecode", "--features", "permissions,hooks",
                           "--input-roots", str(TEMPLATE_SOURCE.parent)], cwd=tmp_path, capture_output=True,
                          text=True, timeout=120)
    assert done.returncode == 0, done.stderr[-1000:]
    generated = json.loads((tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8"))
    kernel = json.loads(TEMPLATE_SETTINGS.read_text(encoding="utf-8"))
    assert generated["permissions"]["allow"] == kernel["permissions"]["allow"] == ["Bash(gov launch:*)"]
    assert generated["hooks"]["PreToolUse"] == kernel["hooks"]["PreToolUse"]
