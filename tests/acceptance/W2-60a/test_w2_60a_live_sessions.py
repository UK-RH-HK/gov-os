"""W2-60a -- what only a launched session can show (``local_only``; routed to the nightly).

One real session is started through ``gov launch`` in a fixture project built
from scratch, once per test run, and every case below reads its log (the CLI's
``--output-format stream-json --verbose`` output) and its launch record:

- KPI success 1 [DEC-826 Q1]: "the role's text ... is in the session's context
  at its start, shown by a launched session's log": the fixture role file and
  the skill it names each carry a code word the session is asked for; the
  session answers with both without a tool call;
- KPI success 2 [DEC-832 item 1]: a skill the role names is in the session's
  context at its start (the second code word);
- KPI success 6 [DEC-826 Q5, lens E R6]: the session's start (the ``init``
  event) shows no connector, no ``mcp__`` tool, no user-level agent or skill
  and no model-side memory path; the project's own agent and skill are there,
  so the lists were read;
- KPI success 8: the record of the session is keyed by the id the session's
  own log gives;
- KPI success 2 and failure 1, round 2 (review 1, F1): the fixture project's
  command file ``.claude/commands/w260a-live/probe.md`` shows in the start as
  ``w260a-live:probe``, and every ``w260a-`` skill the start shows is in the
  record.

**Which home.** A session needs the caller's own sign-in, which lives in the
real home and which no test may read or copy (DEC-820 (a)). So the session runs
in the caller's real home, where (the lead measured, CLI 2.1.292) connectors
from claude.ai, user-level agents, user-level ``anthropic-skills:`` skills and
a model-side memory path show in a start without the launcher's switches. The
user-level agents and skills this case names are those the real home holds at
the time (the names of ``~/.claude/agents/*.md`` and ``~/.claude/skills/*``)
plus every ``anthropic-skills:`` skill; the CLI's own built-ins (P-W2-60a-1)
are not asserted on. The planted test home is the stand-in cases'
(``test_w2_60a_kept_out.py``).

**Cost and needs.** One headless session on ``claude-sonnet-5-5`` at the role's
own effort, high (its default line), with no ``--effort`` given (a launch's own
effort below the role's high is refused, DEC-1120 (3)), at most two turns and
no tool call. It needs the CLI at ``~/.local/bin/claude``,
``bwrap``, ``socat`` and the network to the model's API. The launcher makes the
session's run folder ``~/gov-os-runs/W2-60a-fixture`` in the real home, as
W2-58's live cases make theirs. A launched test designer cannot run it: the
ticket lead runs it from an unsandboxed session.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

# Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19, no launch takes a model the rubric does not give; the fixture engineer's
# default model was Opus and is Sonnet now, so the live session runs on Sonnet.
import w2_60a_support as s

pytestmark = pytest.mark.local_only

ROLE_CODE = "larch-meridian-sixty"
SKILL_CODE = "cobalt-tundra-sixty"
PACK = s.Skill("w260a-live-pack", "w260a-live-pack", "1.0.0")
LIVE_COMMAND = s.Command("w260a-live/probe.md", "1.0.0", title="W260A: Probe")
PROMPT = ("Answer from your instructions only and use no tool. Your instructions give a role code word and a skill "
          "code word. Reply with exactly those two code words, separated by one space, and nothing else.")
SESSION_TIMEOUT_S = 420.0
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET")
NOT_INHERITED_PREFIX = "CLAUDE"


@dataclass(frozen=True)
class Session:
    project: Path
    run: s.Run
    events: tuple
    record: dict | None

    @property
    def init(self):
        for event in self.events:
            if event.get("type") == "system" and event.get("subtype") == "init":
                return event
        return None

    @property
    def result(self):
        for event in reversed(self.events):
            if event.get("type") == "result":
                return event
        return None

    def describe(self):
        return f"{self.run.describe()[-2500:]}\nrecord: {json.dumps(self.record)[:800] if self.record else None}"


def _prerequisites():
    missing = [name for name in ("bwrap", "socat") if shutil.which(name) is None]
    if not (Path.home() / s.CLI_REL).is_file():
        missing.append("~/.local/bin/claude")
    if missing:
        pytest.fail(f"a launched session needs {missing} on this machine", pytrace=False)


def _events(stdout):
    found = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            found.append(event)
    return tuple(found)


@pytest.fixture(scope="module")
def session(tmp_path_factory):
    _prerequisites()
    sandbox = s.make_sandbox(tmp_path_factory.mktemp("w2-60a-live"))
    project = s.make_project(sandbox, skills=(*s.SKILLS, PACK),
                             extra={f"{s.COMMANDS_REL}/{LIVE_COMMAND.rel}": LIVE_COMMAND.text()})
    role = s.role_text(s.ENGINEER, skills=(PACK.folder,))
    s.write(s.role_path(project, s.ENGINEER), role + f"\nWhen asked for your role code word, it is {ROLE_CODE}.\n")
    s.write(project / s.SKILLS_REL / PACK.folder / "SKILL.md",
            PACK.text() + f"\nWhen asked for your skill code word, it is {SKILL_CODE}.\n")
    env = {key: value for key, value in os.environ.items()
           if key not in NOT_INHERITED and not key.startswith(NOT_INHERITED_PREFIX)}
    env.update({"PYTHONPATH": s.python_path(), "PYTHONPYCACHEPREFIX": str(sandbox.pycache)})
    argv = s.gov_argv("launch", s.ENGINEER, s.T.tk, "--", "-p", PROMPT, "--output-format", "stream-json",
                      "--verbose", "--model", s.SONNET, "--max-turns", "2")
    try:
        done = subprocess.run(argv, cwd=str(project), env=env, capture_output=True, text=True,
                              timeout=SESSION_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        pytest.fail(f"the launched session did not end within {SESSION_TIMEOUT_S:.0f} s", pytrace=False)
    run = s.Run(("gov", "launch", s.ENGINEER, s.T.tk), done.returncode, done.stdout, done.stderr)
    events = _events(done.stdout)
    record = None
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    if init and isinstance(init.get("session_id"), str):
        path = sandbox.records / f"{init['session_id']}.json"
        if path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
    found = Session(project, run, events, record)
    if found.init is None:
        pytest.fail(f"the launched session's log has no init event\n{found.describe()}", pytrace=False)
    return found


def _names(entries):
    names = []
    for entry in entries or []:
        if isinstance(entry, str):
            names.append(entry)
        elif isinstance(entry, dict) and isinstance(entry.get("name"), str):
            names.append(entry["name"])
    return names


def _user_level(folder, suffix=""):
    """The names of the real home's user-level agents (``*.md``) or skills (folders); names only, no content."""
    path = Path.home() / ".claude" / folder
    if not path.is_dir():
        return set()
    return {entry.name[:-len(suffix)] if suffix else entry.name for entry in path.iterdir()
            if (entry.name.endswith(suffix) if suffix else entry.is_dir())}


def test_a_launched_session_has_its_role_text_and_named_skill_at_its_start(session):
    result = session.result
    assert result is not None, f"the session's log has no result event\n{session.describe()}"
    answer = str(result.get("result", ""))
    assert ROLE_CODE in answer, f"the session did not have its role file's text at its start: {answer!r}"
    assert SKILL_CODE in answer, f"the session did not have the skill its role names at its start: {answer!r}"


def test_the_launch_record_is_keyed_by_the_id_the_session_s_log_gives(session):
    assert session.record is not None, (
        f"no launch record named by the session's own id {session.init.get('session_id')}\n{session.describe()}")
    assert session.record.get("session_id") == session.init.get("session_id")
    assert (session.record.get("model") == s.SONNET
            and session.record.get("effort") == s.DEFAULTS[s.ENGINEER][1]), (
        f"the record's model and effort are not this launch's: {session.record.get('model')}, "
        f"{session.record.get('effort')}")
    assert session.init.get("model", "").startswith(s.SONNET), f"the session ran on {session.init.get('model')!r}"


def test_a_launched_session_starts_with_no_connector(session):
    servers = session.init.get("mcp_servers") or []
    tools = [tool for tool in _names(session.init.get("tools")) if tool.startswith("mcp__")]
    assert not servers, f"the session's start shows connectors: {servers}"
    assert not tools, f"the session's start shows connector tools: {tools[:10]}"


def test_a_launched_session_starts_with_no_user_level_agent_or_skill(session):
    agents, skills = _names(session.init.get("agents")), _names(session.init.get("skills"))
    assert s.ENGINEER in agents, f"the project's own agents are not in the start, so it cannot be judged: {agents}"
    assert PACK.name in skills, f"the project's own skills are not in the start, so it cannot be judged: {skills}"
    user_agents = sorted(_user_level("agents", ".md") & set(agents))
    assert not user_agents, f"the session's start shows user-level agents: {user_agents}"
    user_skills = sorted(name for name in skills
                         if name.startswith("anthropic-skills:") or name in _user_level("skills"))
    assert not user_skills, f"the session's start shows user-level skills: {user_skills}"


def test_a_launched_session_starts_with_no_model_side_memory(session):
    assert not session.init.get("memory_paths"), (
        f"the session's start shows model-side memory: {session.init.get('memory_paths')}")


def test_every_project_skill_in_the_session_s_start_is_in_its_record(session):
    """Round 2 (review 1, F1): the project's command file is a skill the session can load, and its record names it,
    as does every other ``w260a-`` skill (the fixture's own) the start shows."""
    loaded = set(_names(session.init.get("skills"))) | set(_names(session.init.get("slash_commands")))
    assert LIVE_COMMAND.recorded_name in loaded, (
        f"the session's start does not show the command file {LIVE_COMMAND.rel} as {LIVE_COMMAND.recorded_name}, "
        f"so it cannot be judged: {sorted(loaded)}")
    assert session.record is not None, f"no launch record\n{session.describe()}"
    recorded = {entry.get("name"): entry for entry in session.record.get("skills") or [] if isinstance(entry, dict)}
    unrecorded = sorted(name for name in loaded if name.startswith("w260a-") and name not in recorded)
    assert not unrecorded, f"the session's start shows project skills its record does not name: {unrecorded}"
    entry = recorded[LIVE_COMMAND.recorded_name]
    assert (entry.get("version"), entry.get("named")) == ("1.0.0", False), f"the command's entry: {entry!r}"
