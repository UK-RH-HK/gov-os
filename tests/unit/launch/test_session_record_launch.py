"""W2-60b through ``launcher.launch``: the session record at the start and after every ending (S1, S5, F3), the
launchable roles read from the role files (S7, S8, F1), one writer per worktree (S10, S12), ``--tests-worktree``'s
behaviour (S10) and ``qa-engineer`` as a known role of the guard (S9).

No CLI and no process is started: ``subprocess.Popen`` is replaced by a stand-in, as in ``test_w1_32.py``."""

from __future__ import annotations

import json
import os
import re
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "unit" / "telemetry"))

from gov.cli.errors import GovError  # noqa: E402
from gov.guard import decide  # noqa: E402
from gov.launch import launcher, session_record as sr  # noqa: E402
from test_sessionlog_w2_60b import SECRET, Log  # noqa: E402

ROLES_REL = Path("template/governance/kernel/roles")
REAL_POPEN = subprocess.Popen  # taken before the fixture puts the stand-in in its place
TICKET, SPEC_TICKET = "TST-a001", "TST-a002"
WORKER = ("- **Version:** 1.0.0\n- **Launch default:** model claude-opus-5-5, effort high\n")


def _role(project, role, extra=""):
    path = project / ROLES_REL / f"{role}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {role}\n\n{WORKER}{extra}", encoding="utf-8")
    template = project / launcher.TEMPLATES_REL / f"{launcher.ROLE_TEMPLATES.get(role, 'role-' + role)}.md"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(f"# {role}\n", encoding="utf-8")
    return path


def _ticket(project, tid, role):
    folder = project / ".tickets"
    folder.mkdir(exist_ok=True)
    (folder / f"{tid}.md").write_text(f"---\nid: {tid}\nstatus: in_progress\nrole: {role}\nclass: implementation\n"
                                      f"allowed_paths:\n- src/app/**\n---\n# {tid}\n", encoding="utf-8")


def _open_gate(home, monkeypatch):
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


class Session:
    """In place of ``subprocess.Popen``: ``plan(session)`` runs in ``wait``; it plants the session's log first."""
    made: list = []
    plan = staticmethod(lambda session: 0)
    log = None
    seen: list = []

    def __init__(self, argv, cwd, env, **options):
        self.argv, self.returncode, self.calls = argv, None, []
        self.session_id = argv[argv.index("--session-id") + 1]
        Session.made.append(self)
        if Session.log is not None:
            Session.log.session = self.session_id
            for line in Session.log.lines:
                line["sessionId"] = self.session_id
            Session.log.write(Path(os.environ["CLAUDE_CONFIG_DIR"]))

    def wait(self):
        if self.returncode is None:
            self.returncode = Session.plan(self)
        return self.returncode

    def poll(self):
        return self.returncode

    def terminate(self):
        self.calls.append("terminate")
        self.returncode = -signal.SIGTERM

    def kill(self):
        self.returncode = -signal.SIGKILL


@pytest.fixture
def project(tmp_path, monkeypatch):
    home, temp, project = tmp_path / "home", tmp_path / "temp", tmp_path / "project"
    for folder in (home / ".local" / "bin", temp, project):
        folder.mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "config"))
    _open_gate(home, monkeypatch)
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    monkeypatch.setattr(launcher, "END_WAIT_S", 1)
    for role in ("engineer", "product-spec", "research"):
        _role(project, role, "- **Authority level:** worker, with no approval authority.\n")
    for role in ("independent-test-designer", "independent-auditor"):
        _role(project, role, "- **Authority level:** worker, independent of the builders.\n")
    _ticket(project, TICKET, "engineer")
    _ticket(project, SPEC_TICKET, "product-spec")
    Session.made, Session.plan, Session.log = [], staticmethod(lambda session: 0), None
    before = {number: signal.getsignal(number) for number in (*launcher.END_SIGNALS, signal.SIGALRM)}
    yield Path(os.path.realpath(project))
    for number, handler in before.items():
        signal.signal(number, handler if handler is not None else signal.SIG_DFL)


def _records(project):
    folder = project / ".gov-runtime" / "sessions"
    return sorted(folder.glob("*.json")) if folder.is_dir() else []


def _record(project):
    paths = _records(project)
    assert len(paths) == 1, paths
    return json.loads(paths[0].read_text(encoding="utf-8"))


# -- the record at the start and after every ending (S1, S5, F3) --------------------------------------------------

def test_a_record_exists_while_the_session_runs_with_no_end(project):
    seen = []
    Session.plan = staticmethod(lambda session: seen.append(_record(project)) or 0)
    assert launcher.launch(project, "engineer", TICKET, []) == 0
    assert seen[0]["ended_at"] is None and seen[0]["session_id"] == Session.made[0].session_id
    assert seen[0]["role"]["value"] == "engineer" and seen[0]["ticket"]["value"] == TICKET
    assert seen[0]["worktree"] == str(project) and seen[0]["pid"] == os.getpid()


@pytest.mark.parametrize("code", (0, 4))
def test_an_ended_session_leaves_one_whole_record_keyed_by_its_id(project, code):
    Session.log = Log().user().assistant().compaction().api_error(429).cost(1.5)
    Session.plan = staticmethod(lambda session: code)
    assert launcher.launch(project, "engineer", TICKET, []) == code
    record = _record(project)
    assert _records(project)[0].stem == Session.made[0].session_id == record["session_id"]
    assert record["exit_code"] == code and record["ended_at"] is not None
    assert record["task_class"]["value"] == "implementation" and record["compactions"]["value"] == 1
    assert len(record["rate_limit_events"]["value"]) == 1 and record["cost_usd"]["value"] == 1.5
    assert SECRET not in _records(project)[0].read_text(encoding="utf-8")


def _caller_handles(number) -> None:
    """The caller's own disposition of ``number``: a handler, not SIG_IGN. A job a non-interactive shell starts with
    ``&`` inherits SIGINT ignored, and the launcher keeps a signal its caller ignores ignored (W2-56), so a case that
    needs DEC-392's ending sets the caller's handler itself (the fixture gives the original back), as test_w1_32 does."""
    signal.signal(number, signal.default_int_handler if number == signal.SIGINT else (lambda *_: None))


@pytest.mark.parametrize("number", launcher.END_SIGNALS, ids=lambda number: signal.Signals(number).name)
def test_a_signalled_session_leaves_its_record_with_the_interrupt_exit(project, number):
    _caller_handles(number)
    Session.plan = staticmethod(lambda session: signal.raise_signal(number) or 0)  # a real wait() gives an int
    assert launcher.launch(project, "engineer", TICKET, []) == launcher.INTERRUPT_EXIT
    record = _record(project)
    assert record["exit_code"] == launcher.INTERRUPT_EXIT and record["ended_at"] is not None


@pytest.mark.parametrize("number", launcher.END_SIGNALS, ids=lambda number: signal.Signals(number).name)
def test_a_signal_the_caller_ignores_stays_ignored_and_the_session_s_own_code_is_returned(project, number):
    """The lead's loaded run at 2d1e751d4 (launch returned None, not 130): it ran with SIGINT ignored (a ``&`` job of a
    non-interactive shell), so the signal never reached the launcher, and the stand-in returned raise_signal's None.
    The launcher returns the session's own code, an int, and records it; the caller's SIG_IGN is given back."""
    signal.signal(number, signal.SIG_IGN)
    Session.plan = staticmethod(lambda session: signal.raise_signal(number) or 7)
    code = launcher.launch(project, "engineer", TICKET, [])
    assert type(code) is int and code == 7
    assert _record(project)["exit_code"] == 7 and signal.getsignal(number) is signal.SIG_IGN


def test_an_unwritable_record_keeps_the_exit_code_with_one_stderr_line(project, capfd):
    (project / ".gov-runtime").mkdir(exist_ok=True)
    (project / ".gov-runtime" / "sessions").write_text("not a folder", encoding="utf-8")
    Session.plan = staticmethod(lambda session: 5)
    assert launcher.launch(project, "engineer", TICKET, []) == 5
    err = capfd.readouterr().err
    lines = [line for line in err.splitlines() if "session record" in line]
    assert len(lines) == 1 and f"{Session.made[0].session_id}.json" in lines[0]
    assert (project / ".gov-runtime" / "sessions").read_text() == "not a folder"


def test_a_session_that_cannot_start_leaves_no_session_record(project, monkeypatch):
    def refuse(*args, **kwargs):
        raise OSError("no")
    monkeypatch.setattr(launcher.subprocess, "Popen", refuse)
    with pytest.raises(GovError):
        launcher.launch(project, "engineer", TICKET, [])
    assert _records(project) == []


# -- the launchable roles read from the role files (S7, S8, F1) ----------------------------------------------------

def _assigned_names(source: str) -> set[str]:
    import ast
    names = set()
    for node in ast.walk(ast.parse(source)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] \
            if isinstance(node, (ast.AnnAssign, ast.AugAssign)) else []
        for target in targets:
            for leaf in ast.walk(target):
                if isinstance(leaf, ast.Name):
                    names.add(leaf.id)
    return names


def test_no_fixed_role_tuple_is_left_in_the_launcher():
    """F1: no assignment of WORKER_ROLES or OWN_TICKET_ROLES (annotated too) stays in launcher.py."""
    source = Path(launcher.__file__).read_text(encoding="utf-8")
    assert not {"WORKER_ROLES", "OWN_TICKET_ROLES"} & _assigned_names(source)
    assert not re.search(r"^\s*(WORKER_ROLES|OWN_TICKET_ROLES)\s*(:[^=]*)?=", source, re.M)


def test_worker_roles_is_still_served_for_w2_153_s_readers():
    """The template map's five worker entries, served by name (PEP 562) for W2-153's and W1-50's readers."""
    from gov.launch.launcher import WORKER_ROLES
    assert WORKER_ROLES == ("engineer", "independent-test-designer", "independent-auditor", "product-spec", "research")
    assert launcher.WORKER_ROLES == WORKER_ROLES and "ticket-lead" not in WORKER_ROLES
    with pytest.raises(AttributeError):
        launcher.NO_SUCH_NAME  # noqa: B018


def test_a_sixth_worker_role_file_launches_with_no_code_change(project):
    _role(project, "w260b-sixth", "- **Authority level:** worker, with no approval authority.\n")
    _ticket(project, "TST-a006", "w260b-sixth")
    assert launcher.launch(project, "w260b-sixth", "TST-a006", []) == 0
    argv = Session.made[0].argv
    assert argv[argv.index("--append-system-prompt-file") + 1].endswith("role-w260b-sixth.md")
    assert _record(project)["role"]["value"] == "w260b-sixth"


def test_the_kernel_s_qa_engineer_file_is_launchable_on_any_ticket(project):
    kernel = (REPO / ROLES_REL / "qa-engineer.md").read_bytes()
    (project / ROLES_REL / "qa-engineer.md").write_bytes(kernel)
    (project / launcher.TEMPLATES_REL / "role-qa-engineer.md").write_text("# qa\n", encoding="utf-8")
    assert launcher._role_kind(project, "qa-engineer") == {"rel": f"{ROLES_REL}/qa-engineer.md", "own_ticket": False}


@pytest.mark.parametrize("role", ("senior-engineer", "ticket-lead"))
def test_the_coordinators_kernel_files_are_not_launchable(project, role):
    (project / ROLES_REL / f"{role}.md").write_bytes((REPO / ROLES_REL / f"{role}.md").read_bytes())
    _ticket(project, "TST-a009", role)
    with pytest.raises(GovError) as raised:
        launcher.launch(project, role, "TST-a009", [])
    assert "not a worker role" in raised.value.message and role in raised.value.message


@pytest.mark.parametrize("role", ("engineer", "independent-test-designer", "independent-auditor", "research",
                                  "product-spec", "qa-engineer"))
def test_the_kernel_s_worker_files_are_launchable(role):
    kind = launcher._role_kind(REPO, role)
    assert kind["own_ticket"] is (role in ("engineer", "research", "product-spec"))


@pytest.mark.parametrize("role", ("orchestrator", "senior-engineer", "ticket-lead"))
def test_the_kernel_s_coordinator_files_are_refused(role):
    with pytest.raises(GovError) as raised:
        launcher._role_kind(REPO, role)
    assert "not a worker role" in raised.value.message and role in raised.value.message


def test_a_ticket_naming_a_role_with_no_role_file_is_refused_naming_the_role(project):
    _ticket(project, "TST-a007", "w260b-ghost")
    with pytest.raises(GovError) as raised:
        launcher.launch(project, "w260b-ghost", "TST-a007", [])
    assert raised.value.code == "LAUNCH_REFUSED" and "w260b-ghost" in raised.value.message
    assert Session.made == [] and _records(project) == []


def test_an_unreadable_role_file_refuses_naming_the_role(project):
    path = _role(project, "w260b-broken")
    path.write_bytes(b"\xff\xfe not utf-8")
    _ticket(project, "TST-a008", "w260b-broken")
    with pytest.raises(GovError) as raised:
        launcher.launch(project, "w260b-broken", "TST-a008", [])
    assert "w260b-broken" in raised.value.message and Session.made == []


def test_a_role_file_that_is_a_folder_refuses(project):
    (project / ROLES_REL / "w260b-folder.md").mkdir(parents=True)
    with pytest.raises(GovError):
        launcher._role_kind(project, "w260b-folder")


@pytest.mark.parametrize("role", ("../engineer", "Engineer", "", "a/b"))
def test_a_role_name_that_is_not_a_plain_name_is_refused(project, role):
    with pytest.raises(GovError) as raised:
        launcher.launch(project, role, TICKET, [])
    assert "not a worker role" in raised.value.message


def test_two_authority_lines_refuse(project):
    _role(project, "w260b-twice", "- **Authority level:** worker.\n- **Authority level:** coordinator.\n")
    with pytest.raises(GovError):
        launcher._role_kind(project, "w260b-twice")


def test_a_worker_role_without_independence_keeps_to_its_own_ticket(project):
    _role(project, "w260b-sixth", "- **Authority level:** worker, with no approval authority.\n")
    with pytest.raises(GovError) as raised:
        launcher.launch(project, "w260b-sixth", TICKET, [])
    assert "another role" in raised.value.message


def test_an_independent_role_launches_on_another_role_s_ticket(project):
    _role(project, "w260b-checker", "- **Authority level:** worker, independent of the builders.\n")
    assert launcher.launch(project, "w260b-checker", TICKET, []) == 0


def test_the_engineer_on_a_spec_ticket_is_refused_as_before(project):
    with pytest.raises(GovError) as raised:
        launcher.launch(project, "engineer", SPEC_TICKET, [])
    assert "another role" in raised.value.message


def test_the_plan_reads_a_sixth_role(project, capsys):
    _role(project, "w260b-sixth", "- **Authority level:** worker.\n")
    _ticket(project, "TST-a006", "w260b-sixth")
    assert launcher.plan(project, "w260b-sixth", "TST-a006") == 0
    assert capsys.readouterr().out.strip() == "model claude-opus-5-5, effort high"


# -- one writer per worktree (S10, S12) ----------------------------------------------------------------------------

def _plant_live(project, role="engineer", sid="33333333-3333-4333-8333-333333333333", started=None):
    folder = project / ".gov-runtime" / "sessions"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{sid}.json").write_text(json.dumps({
        "record": "gov-session", "format": 1, "session_id": sid, "worktree": str(project), "pid": os.getpid(),
        "started_at": started or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "ended_at": None,
        "exit_code": None, "role": {"value": role, "source": "launch record"}}), encoding="utf-8")
    return sid


def test_a_live_writer_with_an_earlier_fixed_start_stamp_refuses_the_second_writer(project):
    """The interface's planted form: a fixed stamp earlier than the live process's start. Alive is live (no pid-reuse
    discount): the launch is refused, naming the session and the worktree, and nothing is started or recorded."""
    sid = _plant_live(project, started="2026-11-16T05:00:00Z")
    with pytest.raises(GovError) as raised:
        launcher.launch(project, "engineer", TICKET, [])
    assert sid in raised.value.message and str(project) in raised.value.message
    assert Session.made == [] and [p.stem for p in _records(project)] == [sid]


def test_a_second_writer_in_a_worktree_with_a_live_writer_is_refused(project):
    sid = _plant_live(project)
    with pytest.raises(GovError) as raised:
        launcher.launch(project, "engineer", TICKET, [])
    assert raised.value.code == "LAUNCH_REFUSED" and sid in raised.value.message
    assert str(project) in raised.value.message and Session.made == []
    assert not (project / ".gov-runtime" / "launches").exists()


def test_a_reviewer_starts_beside_a_live_writer(project):
    _plant_live(project)
    assert launcher.launch(project, "independent-auditor", TICKET, []) == 0


def test_a_live_reviewer_does_not_block_a_writer(project):
    _plant_live(project, role="qa-engineer")
    assert launcher.launch(project, "engineer", TICKET, []) == 0


def test_a_writer_s_own_ended_record_does_not_block_the_next_launch(project):
    assert launcher.launch(project, "engineer", TICKET, []) == 0
    assert launcher.launch(project, "engineer", TICKET, []) == 0
    assert len(_records(project)) == 2


# -- one writer per worktree under the start lock (review round 1, F1) ---------------------------------------------
#
# Two ``gov launch`` processes into one worktree. Each says "L" on the events pipe as it reaches the start lock (after
# every check made before the lock), so the test knows both have passed those checks before either can take it: with
# ``barrier`` each then waits for the test's go, so the two contend for the lock together; with ``held`` the test
# holds the machine-wide start lock itself (a third party, as in a fan-out) until both have said "L". The planted CLI
# says "S <session id>" when it starts and runs until the test closes the hold pipe. Every wait is on an event (a pipe
# or a process's end), none on a sleep, so load cannot change the outcome.

LAUNCHER = """
import os, sys
sys.path.insert(0, {src!r})
from gov.cli.errors import GovError
from gov.launch import gate, launcher
launcher._check_repository_settings = lambda *args: None
EVENTS, GO = {events!r}, {go}

def event(text):
    fd = os.open(EVENTS, os.O_WRONLY)
    os.write(fd, (text + "\\n").encode())
    os.close(fd)

class AtTheLock(gate.StartLock):
    def __init__(self, *args, **kwargs):
        event("L")
        if GO is not None:
            os.read(GO, 1)
        super().__init__(*args, **kwargs)

gate.StartLock = AtTheLock
try:
    code = launcher.launch({project!r}, {role!r}, {ticket!r}, [])
except GovError as error:
    sys.stderr.write(f"{{error.code}}: {{error.message}}\\n")
    event("E refused")
    sys.exit(1)
event(f"E {{code}}")
sys.exit(code)
"""

HOLDING_CLI = """
import os, select, sys
session = sys.argv[sys.argv.index("--session-id") + 1]
hold = os.open({hold!r}, os.O_RDONLY | os.O_NONBLOCK)  # opened before "S": the test's close always reaches it
fd = os.open({events!r}, os.O_WRONLY)
os.write(fd, f"S {{session}}\\n".encode())
os.close(fd)
select.select([hold], [], [], 120)  # until the test closes the hold pipe (its last writer): then exit 0
"""


class Events:
    """The events FIFO, read by the test. The test keeps a writer open itself, so the reader never sees an end
    between two writers."""

    def __init__(self, path: Path):
        os.mkfifo(path)
        self.path, self.lines, self.buffer = path, [], b""
        self.reader = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        self.keep = os.open(path, os.O_WRONLY)

    def count(self, head: str) -> int:
        return sum(1 for line in self.lines if line.split()[0] == head)

    def until(self, done, timeout: float = 120.0) -> None:
        deadline = time.monotonic() + timeout
        while not done(self):
            left = deadline - time.monotonic()
            assert left > 0, f"no such events within {timeout} s: {self.lines}"
            ready, _, _ = select.select([self.reader], [], [], left)
            if ready:
                try:
                    self.buffer += os.read(self.reader, 4096)
                except BlockingIOError:
                    continue
                *whole, self.buffer = self.buffer.split(b"\n")
                self.lines += [line.decode() for line in whole if line]

    def close(self) -> None:
        os.close(self.reader)
        os.close(self.keep)


def _race(project, tmp_path, roles, mode):
    """Two launches of ``roles`` into ``project``, started together; returns (events, the launchers, their stderr)."""
    from gov.launch import gate
    events, hold = Events(tmp_path / "events"), tmp_path / "hold"
    os.mkfifo(hold)
    holder = os.open(hold, os.O_RDWR)  # the CLIs' hold pipe's only writer
    cli = Path(os.environ["HOME"]) / launcher.CLI_REL
    cli.write_text(f"#!{sys.executable}\n" + HOLDING_CLI.format(hold=str(hold), events=str(events.path)),
                   encoding="utf-8")
    cli.chmod(0o755)
    lock = gate.StartLock() if mode == "held" else None
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    procs, gos, errs = [], [], []
    try:
        for index, role in enumerate(roles):
            read_go, write_go = os.pipe() if mode == "barrier" else (None, None)
            err = tmp_path / f"launcher-{index}.err"
            script = LAUNCHER.format(src=str(REPO / "src"), events=str(events.path), go=read_go,
                                     project=str(project), role=role, ticket=TICKET)
            with open(err, "wb") as handle:
                procs.append(REAL_POPEN([sys.executable, "-c", script], stdout=subprocess.DEVNULL,
                                              stderr=handle, env=env, pass_fds=(read_go,) if read_go else ()))
            if read_go is not None:
                os.close(read_go)
                gos.append(write_go)
            errs.append(err)
        events.until(lambda e: e.count("L") == 2)  # both are past every check made before the start lock
        for write_go in gos:
            os.write(write_go, b"g")
        if lock is not None:
            lock.release()
        writers = sum(1 for role in roles if role not in sr.REVIEWERS)
        events.until((lambda e: e.count("S") >= 1 and e.count("E") >= 1 or e.count("S") >= 2) if writers == 2
                     else (lambda e: e.count("S") >= 2))
    finally:
        os.close(holder)  # every started CLI ends now
        for write_go in gos:
            os.close(write_go)
        if lock is not None:
            lock.release()
        for proc in procs:
            proc.wait(timeout=120)
    events.until(lambda e: e.count("E") == 2)
    events.close()
    return events, procs, [err.read_text(encoding="utf-8") for err in errs]


@pytest.mark.parametrize("mode", ("barrier", "held"))
def test_two_writers_launched_together_start_one_cli_and_refuse_the_other_naming_it(project, tmp_path, mode):
    """F1: of two writing launches into one worktree, started together, or waiting together on a start lock a third
    party holds, exactly one starts its CLI. The other is refused (LAUNCH_REFUSED, non-zero exit, no CLI start, no
    session record of its own), naming the first's session id and the worktree."""
    events, procs, errs = _race(project, tmp_path, ("engineer", "engineer"), mode)
    starts = [line.split()[1] for line in events.lines if line.startswith("S ")]
    assert len(starts) == 1, (starts, errs)
    first = starts[0]
    codes = sorted(proc.returncode for proc in procs)
    assert codes == [0, 1], (codes, errs)
    refused = errs[[proc.returncode for proc in procs].index(1)]
    assert refused.startswith("LAUNCH_REFUSED: ") and first in refused and str(project) in refused
    assert [path.stem for path in _records(project)] == [first]
    assert [path.stem for path in (project / ".gov-runtime" / "launches").glob("*.json")] == [first]


def test_a_reviewer_launched_together_with_a_writer_still_starts(project, tmp_path):
    events, procs, errs = _race(project, tmp_path, ("engineer", "independent-auditor"), "barrier")
    assert events.count("S") == 2 and [proc.returncode for proc in procs] == [0, 0], errs
    assert len(_records(project)) == 2


# -- --tests-worktree (S10) ----------------------------------------------------------------------------------------

def _repo(tmp_path):
    main = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "w2/T-1", str(main)], check=True)
    subprocess.run(["git", "-C", str(main), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)
    _ticket(main, TICKET, "engineer")
    return Path(os.path.realpath(main))


def test_tests_worktree_makes_the_tests_tree_on_its_own_branch_at_head(tmp_path, capsys):
    main = _repo(tmp_path)
    head = subprocess.run(["git", "-C", str(main), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    assert launcher.tests_worktree(main, "independent-test-designer", TICKET) == 0
    tests = Path(f"{main}-tests")
    assert capsys.readouterr().out.strip() == str(tests)
    branch = subprocess.run(["git", "-C", str(tests), "symbolic-ref", "--short", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    there = subprocess.run(["git", "-C", str(tests), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    assert branch == "w2/T-1-tests" and there == head


def test_tests_worktree_refuses_an_existing_path(tmp_path):
    main = _repo(tmp_path)
    Path(f"{main}-tests").mkdir()
    with pytest.raises(GovError) as raised:
        launcher.tests_worktree(main, "independent-test-designer", TICKET)
    assert f"{main}-tests" in raised.value.message


def test_tests_worktree_refuses_an_existing_branch(tmp_path):
    main = _repo(tmp_path)
    subprocess.run(["git", "-C", str(main), "branch", "w2/T-1-tests"], check=True)
    with pytest.raises(GovError) as raised:
        launcher.tests_worktree(main, "independent-test-designer", TICKET)
    assert "w2/T-1-tests" in raised.value.message and not Path(f"{main}-tests").exists()


def test_tests_worktree_is_the_test_designer_s_alone(tmp_path):
    main = _repo(tmp_path)
    with pytest.raises(GovError):
        launcher.tests_worktree(main, "engineer", TICKET)
    assert not Path(f"{main}-tests").exists()


# -- the guard (S9) ------------------------------------------------------------------------------------------------

def test_qa_engineer_is_a_known_role_of_the_guard_and_in_the_reviewer_set():
    assert "qa-engineer" in decide.KNOWN_ROLES and "qa-engineer" in sr.REVIEWERS


def test_a_qa_engineer_writes_only_its_ticket_s_report(tmp_path):
    folder = tmp_path / ".tickets"
    folder.mkdir()
    (folder / "TST-q001.md").write_text("---\nid: TST-q001\nstatus: in_progress\nrole: qa-engineer\nallowed_paths:\n"
                                        "- docs/qa/TST-q001.md\n---\n", encoding="utf-8")
    paths = decide._get_allowed_paths("qa-engineer", "TST-q001", str(tmp_path))
    assert decide._path_allowed(str(tmp_path / "docs/qa/TST-q001.md"), str(tmp_path), paths, "qa-engineer")
    assert not decide._path_allowed(str(tmp_path / "src/app/x.py"), str(tmp_path), paths, "qa-engineer")


def test_a_qa_engineer_on_another_role_s_ticket_writes_nothing(tmp_path):
    folder = tmp_path / ".tickets"
    folder.mkdir()
    (folder / "TST-q002.md").write_text("---\nid: TST-q002\nstatus: in_progress\nrole: engineer\nallowed_paths:\n"
                                        "- src/**\n---\n", encoding="utf-8")
    assert decide._get_allowed_paths("qa-engineer", "TST-q002", str(tmp_path)) == []


def test_a_role_the_guard_does_not_know_is_still_refused_every_write(tmp_path):
    assert not decide._path_allowed(str(tmp_path / "x"), str(tmp_path), ["**"], "w260b-sixth")
