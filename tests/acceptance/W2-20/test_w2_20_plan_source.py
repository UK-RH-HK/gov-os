"""S21: W2-136's F2 entry criterion (DEC-1088 (5)(b), DEC-803; W2-136 F4).

Before leads are routed through gov launch, the plan check (src/gov/launch/plan_check.py) reads the current tickets
and the approved ready list from the main tree (or a named path the dispatcher keeps), never a lead worktree's own
copies, which can be stale; and a plan override is written to a launch log, not only to standard error (W2-136 F4).
Verify: unit tests with a planted main tree and a lead worktree whose tickets and ready list differ from it: the check
follows the main tree's, a lead its stale copy would admit is refused; a planted override: one line in the launch log
and the line on standard error [DEC-1088 (5)(b), DEC-803].

How: a planted main tree (a git repository with ``.tickets/`` and the approved ready list at W2-136's
``governance/project/orchestration/ready.txt``), and a lead worktree (``git worktree add``) made from it; then the
main tree moves on (one commit), so the worktree keeps yesterday's copies, as a lead's worktree does. The check is the
real ``gov.launch.plan_check.check_lead(root, ticket)`` with no ``ready=`` (it finds the list itself), called with
the lead worktree as ``root`` as the launcher calls it; the launcher's cases run the real ``launch`` with the real
plan check and W2-20's gate (open on planted readings), the session itself replaced by a stub.

The planted tickets (README, "S21"):

| Ticket (its planted WBS id in) | Lead worktree (stale) | Main tree (current) |
|---|---|---|
| ``PLN-f001`` (``STALE_ADMITS``) | in the ready list | taken out of the ready list |
| ``PLN-f002`` (``STALE_WAIT``) | in the list, no waits | in the list, ``depends_on: PLN-f003`` (open) |
| ``PLN-f004`` (``NEW_IN_MAIN``) | no such ticket, not in the list | a new ticket, in the list |
| ``PLN-f005`` (``OVERRIDDEN``) | ``plan_override:`` a planted decision id, not in the list | the same |
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

READY_REL = "governance/project/orchestration/ready.txt"   # W2-136's place for the approved ready list
NAMED_REL = "governance/project/orchestration/ready-dispatch.txt"
GIT_DATE = "2026-11-09T00:00:00+00:00"

STALE_ADMITS = ("PLN-f001", "W2-911")   # the stale list admits it; the main tree's does not
STALE_WAIT = ("PLN-f002", "W2-912")     # the stale ticket has no wait; the main tree's waits for PLN-f003
NEW_IN_MAIN = ("PLN-f004", "W2-914")    # only the main tree has it
OVERRIDDEN = ("PLN-f005", "W2-915")     # admitted by its plan_override in both trees


# --- the planted trees ---------------------------------------------------------------------------------------------

def _ticket(tid: str, wbs: str, *, status: str = "in_progress", depends_on=(), plan_override: str | None = None):
    deps = ", ".join(depends_on)
    lines = ["---\n", f"id: {tid}\n", f"status: {status}\n", f"deps: [{deps}]\n", "links: []\n",
             "created: 2026-11-09T00:00:00Z\n", "type: task\n", "priority: 1\n", "assignee: engineer\n",
             f"external-ref: {wbs}\n", "tags: [planted]\n", f"wbs_id: {wbs}\n",
             f"title: 'planted ticket {wbs}'\n", "class: implementation\n", "state_class: AUTHORITATIVE\n",
             "role: engineer\n"]
    lines.append("depends_on:\n" + "".join(f"- '{d}'\n" for d in depends_on) if depends_on else "depends_on: []\n")
    lines.append(f"allowed_paths:\n- 'src/{tid.lower()}/**'\n")
    lines += ["reads: []\n", "needs: []\n", "waits_on: []\n"]
    if plan_override:
        lines.append(f"plan_override: {plan_override}\n")
    lines += ["---\n", f"# {wbs} planted\n", "\n", "A planted ticket for the W2-20 acceptance tests (S21).\n"]
    return "".join(lines)


def _ready(*entries) -> str:
    out = ["# the approved ready list (planted for the W2-20 acceptance tests, S21)\n", "# batch 1\n"]
    out += [f"{wbs} {tid} {wbs}-A5-plan.md {wbs}-A5-plan.json\n" for tid, wbs in entries]
    return "".join(out)


def _git(root: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_DATE=GIT_DATE, GIT_COMMITTER_DATE=GIT_DATE, GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull)
    subprocess.run(["git", "-c", "user.name=planted", "-c", "user.email=planted@example.invalid",
                    "-c", "commit.gpgsign=false", *args], cwd=root, env=env, check=True, capture_output=True,
                   timeout=60)


def _write(root: Path, files: dict) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class Trees:
    def __init__(self, main: Path, lead: Path):
        self.main, self.lead = main, lead


@pytest.fixture
def trees(tmp_path) -> Trees:
    """The main tree and a lead worktree made from it before the main tree moved on (see the module's table)."""
    main, lead = tmp_path / "main", tmp_path / "lead-W2-911"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    dependency = _ticket("PLN-f003", "W2-913", status="open")
    _write(main, {
        "README.md": "planted main tree (W2-20 S21)\n",
        ".tickets/PLN-f001.md": _ticket(*STALE_ADMITS),
        ".tickets/PLN-f002.md": _ticket(*STALE_WAIT),
        ".tickets/PLN-f003.md": dependency,
        ".tickets/PLN-f005.md": _ticket(*OVERRIDDEN, plan_override="DEC-1234"),
        READY_REL: _ready(STALE_ADMITS, STALE_WAIT),
    })
    _git(main, "add", "-A")
    _git(main, "commit", "-q", "-m", "the plan as the lead's worktree was made")
    _git(main, "worktree", "add", "-q", "-b", "lead/W2-911", str(lead))

    # The main tree moves on: the list re-approved without PLN-f001 and with the new PLN-f004; PLN-f002 now waits.
    _write(main, {
        ".tickets/PLN-f002.md": _ticket(*STALE_WAIT, depends_on=("PLN-f003",)),
        ".tickets/PLN-f004.md": _ticket(*NEW_IN_MAIN),
        READY_REL: _ready(STALE_WAIT, NEW_IN_MAIN),
    })
    _git(main, "add", "-A")
    _git(main, "commit", "-q", "-m", "the plan today")

    assert (lead / ".git").is_file(), "the lead worktree is not a git worktree of the main tree"
    assert "PLN-f001" in (lead / READY_REL).read_text() and not (lead / ".tickets/PLN-f004.md").exists(), (
        "the lead worktree does not hold the stale copies")
    return Trees(main.resolve(), lead.resolve())


@pytest.fixture
def no_named_list(monkeypatch):
    for key in ("GOV_PLAN_READY", "GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(key, raising=False)


def _get(answer, key):
    return answer.get(key) if isinstance(answer, dict) else getattr(answer, key, None)


def _mentions(text: str, names) -> bool:
    return any(re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text or "") for name in names)


def _check(root: Path, tid: str):
    from gov.launch import plan_check
    return plan_check.check_lead(root, tid)


# --- the check, from the lead worktree -----------------------------------------------------------------------------

def test_s21_a_lead_its_stale_ready_list_would_admit_is_refused(trees, no_named_list):
    """PLN-f001 is in the worktree's copy of the list but no longer in the main tree's."""
    answer = _check(trees.lead, STALE_ADMITS[0])
    assert _get(answer, "admitted") is False, (
        f"the check followed the lead worktree's stale ready list and admitted {STALE_ADMITS[0]}: {answer}")
    assert _mentions(_get(answer, "reason"), STALE_ADMITS), answer


def test_s21_a_lead_its_stale_ticket_would_admit_is_refused_naming_the_current_wait(trees, no_named_list):
    """PLN-f002's copy in the worktree has no wait; the main tree's waits for PLN-f003, which is open."""
    answer = _check(trees.lead, STALE_WAIT[0])
    assert _get(answer, "admitted") is False, (
        f"the check followed the lead worktree's stale ticket and admitted {STALE_WAIT[0]}: {answer}")
    assert _mentions(_get(answer, "reason"), ("PLN-f003", "W2-913")), (
        f"the refusal does not name what the current ticket waits for: {answer}")


def test_s21_a_lead_the_main_tree_admits_is_admitted_from_the_lead_worktree(trees, no_named_list):
    """PLN-f004 exists only in the main tree, and only the main tree's list holds it."""
    answer = _check(trees.lead, NEW_IN_MAIN[0])
    assert _get(answer, "admitted") is True, (
        f"the check did not follow the main tree's tickets and list for {NEW_IN_MAIN[0]}: {answer}")


def test_s21_guard_from_the_main_tree_itself_the_check_reads_its_own_tickets_and_list(trees, no_named_list):
    """What W2-136 built, kept: the main tree as root refuses PLN-f001 and PLN-f002 and admits PLN-f004."""
    assert _get(_check(trees.main, STALE_ADMITS[0]), "admitted") is False
    assert _get(_check(trees.main, STALE_WAIT[0]), "admitted") is False
    assert _get(_check(trees.main, NEW_IN_MAIN[0]), "admitted") is True


# --- a named path the dispatcher keeps -----------------------------------------------------------------------------

@pytest.mark.parametrize("form", ["absolute", "relative to the main tree"])
def test_s21_a_named_ready_list_is_followed_from_the_lead_worktree(trees, tmp_path, monkeypatch, form):
    """``GOV_PLAN_READY`` names the list the dispatcher keeps. Absolute: that file (W2-136 already). Relative: read
    against the main tree, never the lead worktree *(choice)*. The named list holds PLN-f004 only; the main tree's
    usual list is emptied, so only the named one can admit it."""
    for key in ("GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(key, raising=False)
    _write(trees.main, {READY_REL: _ready()})
    if form == "absolute":
        named = tmp_path / "dispatcher" / "ready.txt"
        named.parent.mkdir()
        named.write_text(_ready(NEW_IN_MAIN), encoding="utf-8")
        monkeypatch.setenv("GOV_PLAN_READY", str(named))
    else:
        _write(trees.main, {NAMED_REL: _ready(NEW_IN_MAIN)})
        assert not (trees.lead / NAMED_REL).exists()
        monkeypatch.setenv("GOV_PLAN_READY", NAMED_REL)
    answer = _check(trees.lead, NEW_IN_MAIN[0])
    assert _get(answer, "admitted") is True, f"the named ready list ({form}) was not followed: {answer}"
    assert _get(_check(trees.lead, STALE_ADMITS[0]), "admitted") is False


# --- the launcher, with the real plan check ------------------------------------------------------------------------

@pytest.fixture
def launch_lead(machine, trees, monkeypatch):
    """``launch_lead(ticket)`` from the lead worktree -> exit code; ``.started`` lists the sessions the stub would
    start. The real launcher, the real plan check and W2-20's gate (planted readings, open); the repository's
    settings check and the session itself replaced."""
    from gov.launch import launcher

    for key, value in machine.env().items():
        monkeypatch.setenv(key, value)
    for key in ("GOV_PLAN_READY", "GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(key, raising=False)
    (machine.home / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    cli = machine.home / launcher.CLI_REL
    cli.write_text("")
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(machine.base))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)

    started = []
    real_popen = subprocess.Popen

    class Session:  # the CLI's stand-in: nothing starts
        returncode = 0

        def wait(self):
            return 0

        def poll(self):
            return 0

        def kill(self):
            pass

    def popen(argv, *args, **kwargs):
        if str(argv[0]) == str(cli):
            started.append(kwargs.get("env"))
            return Session()
        return real_popen(argv, *args, **kwargs)

    monkeypatch.setattr(launcher.subprocess, "Popen", popen)

    def _launch(tid):
        return launcher.launch(trees.lead, "orchestrator", tid, [])
    _launch.started = started
    return _launch


def test_s21_the_launcher_refuses_a_lead_its_stale_copies_would_admit(launch_lead):
    from gov.cli.errors import GovError

    with pytest.raises(GovError) as refused:
        launch_lead(STALE_ADMITS[0])
    assert refused.value.code == "LAUNCH_REFUSED", refused.value
    assert _mentions(refused.value.message, STALE_ADMITS), refused.value.message
    assert launch_lead.started == [], "a lead was started on the lead worktree's stale ready list"


def test_s21_the_launcher_starts_a_lead_the_main_tree_admits(launch_lead):
    assert launch_lead(NEW_IN_MAIN[0]) == 0
    assert len(launch_lead.started) == 1


def test_s21_a_plan_override_is_one_line_in_the_launch_log_and_the_line_on_standard_error(
        machine, launch_lead, capfd):
    """PLN-f005 is in no list and admitted by its ``plan_override`` (the planted decision id): the launch log
    (``$HOME/.gov-os/machine/launch.log``, P-1's log) gets one line naming the override, its decision and the
    ticket, and standard error keeps W2-136's line."""
    assert launch_lead(OVERRIDDEN[0]) == 0
    assert len(launch_lead.started) == 1

    assert machine.launch_log.exists(), f"no launch log at {machine.launch_log}: the override went to stderr only"
    lines = [line for line in machine.launch_log.read_text().splitlines() if "DEC-1234" in line]
    assert len(lines) == 1, f"not one launch-log line for the plan override:\n{machine.launch_log.read_text()}"
    assert "plan_override" in lines[0] and _mentions(lines[0], OVERRIDDEN), (
        f"the launch log's line does not name the plan override and the ticket: {lines[0]}")
    err = capfd.readouterr().err
    said = [line for line in err.splitlines() if "OVERRIDE" in line and "DEC-1234" in line]
    assert len(said) == 1, f"standard error does not carry the override's one line: {err}"
