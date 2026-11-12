"""Builder tests for a product's CTO-only install rule (W2-110, DEC-957, DEC-971 item 4).

Regression evidence only (DEC-136): each line of the lead's specification, success and failure, through the
kernel hook in a temporary git project and through ``cto_install`` itself.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard import install  # noqa: E402
from gov.guard.install import coordination_ticket, cto_install  # noqa: E402

HOOK_DIR = REPO / "template" / "governance" / "kernel" / "hooks"
ROSTER = "governance/project/roster.yaml"
FOLDER = "experiments/exp-1"
NO_KEY = object()


def _ticket(tid, wbs, role, allowed="src/**"):
    return (f"---\nid: {tid}\nstatus: in_progress\nwbs_id: {wbs}\ntitle: t\nrole: {role}\n"
            f"allowed_paths:\n- {allowed}\nprofile: FULL\n---\n# T\n")


def _git(project, *args):
    subprocess.run(["git", "-C", str(project), "-c", "user.name=test", "-c", "user.email=t@x",
                    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                   capture_output=True, text=True, check=True)


def _project(tmp_path, key="W9-00", roster_text=None):
    """A project with the coordination ticket C-00 (W9-00), a lead's ticket T-01 (W9-01), an engineer's T-02
    (W9-02) and a research ticket R-01 (W9-03); the roster's key is *key* (NO_KEY: none; None: no roster)."""
    project = tmp_path / "project"
    tickets = project / ".tickets"
    tickets.mkdir(parents=True)
    (tickets / "C-00.md").write_text(_ticket("C-00", "W9-00", "orchestrator", "**"), encoding="utf-8")
    (tickets / "T-01.md").write_text(_ticket("T-01", "W9-01", "orchestrator"), encoding="utf-8")
    (tickets / "T-02.md").write_text(_ticket("T-02", "W9-02", "engineer"), encoding="utf-8")
    (tickets / "R-01.md").write_text(_ticket("R-01", "W9-03", "research", f"{FOLDER}/**"), encoding="utf-8")
    (project / FOLDER).mkdir(parents=True)
    (project / FOLDER / "README.md").write_text("x\n", encoding="utf-8")
    (project / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n", encoding="utf-8")
    hooks = project / "governance" / "kernel" / "hooks"
    hooks.mkdir(parents=True)
    for src in HOOK_DIR.glob("pretooluse*"):
        shutil.copy2(src, hooks / src.name)
    if roster_text is None and key is not None:
        roster_text = "roles: {}\n" if key is NO_KEY else f"coordination_ticket: {key}\nroles: {{}}\n"
    if roster_text is not None:
        (project / ROSTER).parent.mkdir(parents=True, exist_ok=True)
        (project / ROSTER).write_text(roster_text, encoding="utf-8")
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "init")
    return project


def _hook(project, tmp_path, command="pip install requests", role=None, ticket=None, subagent=None, cwd=None,
          older_gov=False):
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tmp").mkdir(exist_ok=True)
    pythonpath = str(REPO / "src")
    if older_gov:
        # A pinned gov older than the hook: its install module has no CTO rule.
        shim = tmp_path / "older-gov"
        shim.mkdir(exist_ok=True)
        (shim / "sitecustomize.py").write_text("import gov.guard.install as m\ndel m.cto_install\n", encoding="utf-8")
        pythonpath = f"{shim}{os.pathsep}{pythonpath}"
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8",
           "LC_ALL": "C.UTF-8", "TMPDIR": str(tmp_path / "tmp"), "PYTHONPATH": pythonpath,
           "PYTHONPYCACHEPREFIX": str(tmp_path / "pycache"), "CLAUDE_PROJECT_DIR": str(project)}
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    data = {"session_id": "s", "cwd": str(cwd or project), "hook_event_name": "PreToolUse", "tool_name": "Bash",
            "tool_input": {"command": command, "description": "t"}, "tool_use_id": "toolu_w2_110"}
    if subagent is not None:
        data["agent_id"] = "agent-1"
        data["agent_type"] = subagent
    proc = subprocess.run([sys.executable, str(project / "governance/kernel/hooks/pretooluse.py")],
                          input=json.dumps(data), capture_output=True, text=True, cwd=str(project), env=env,
                          timeout=30, check=False)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout.strip() or "{}").get("hookSpecificOutput", {})
    return out.get("permissionDecision", "allow"), out.get("permissionDecisionReason", "")


# -- 1, 2: the CTO is asked; the key by id or by WBS id, the session's ticket by either --------------------------

@pytest.mark.parametrize("key, ticket", [("C-00", "C-00"), ("W9-00", "C-00"), ("C-00", "W9-00"),
                                         ("W9-00", "W9-00"), ("'W9-00'", "C-00")])
def test_the_cto_is_asked(tmp_path, key, ticket):
    project = _project(tmp_path, key=key)
    decision, reason = _hook(project, tmp_path, role="orchestrator", ticket=ticket)
    assert decision == "ask"
    assert "owner approval" in reason and "tool registry record required" in reason


def test_an_orchestrator_subagent_in_the_ctos_session_is_asked(tmp_path):
    project = _project(tmp_path)
    assert _hook(project, tmp_path, role="orchestrator", ticket="C-00", subagent="orchestrator")[0] == "ask"


def test_the_ctos_ask_takes_the_before_snapshot(tmp_path):
    project = _project(tmp_path)
    assert _hook(project, tmp_path, role="orchestrator", ticket="C-00")[0] == "ask"
    assert any("toolu_w2_110" in p.name for p in (project / ".gov-runtime").rglob("*"))


# -- 3: every other session is refused and told to escalate --------------------------------------------------------

@pytest.mark.parametrize("role, ticket, subagent", [
    ("orchestrator", "T-01", None),            # a lead
    ("orchestrator", "W9-01", None),           # a lead, by WBS id
    ("orchestrator", None, None),              # an orchestrator with no ticket
    ("orchestrator", "", None),
    ("orchestrator", "NOPE", None),            # a ticket that does not exist
    ("engineer", "T-02", None),
    ("engineer", "C-00", None),                # another role on the coordination ticket
    ("product-spec", "C-00", None),
    ("independent-test-designer", "C-00", None),
    ("research", "R-01", None),                # research outside its experiment folder
    (None, "C-00", None),                      # no role
    ("", "C-00", None),
    ("orchestrator", "C-00", "engineer"),      # another role's subagent in the CTO's session
    ("orchestrator", "C-00", "general-purpose"),
    ("orchestrator", "T-01", "orchestrator"),  # an orchestrator subagent in a lead's session
    ("engineer", "C-00", "orchestrator"),      # an orchestrator subagent in a session that is not the CTO's
])
def test_every_other_session_is_refused_and_escalates(tmp_path, role, ticket, subagent):
    project = _project(tmp_path)
    decision, reason = _hook(project, tmp_path, role=role, ticket=ticket, subagent=subagent)
    assert decision == "deny"
    assert "P1 escalation to the CTO" in reason


# -- 4: fail closed ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("key, roster_text", [
    (None, None),                                       # no roster.yaml
    (NO_KEY, None),                                     # no key
    ("''", None),                                       # an empty value
    ("'   '", None),
    ("[C-00]", None),                                   # not text
    ("42", None),
    ("null", None),
    ("{id: C-00}", None),
    ("W9-77", None),                                    # names no ticket
    ("../C-00", None),
    (None, "coordination_ticket: [C-00\n"),             # cannot be parsed
    (None, "- coordination_ticket: C-00\n"),            # not a mapping
    (None, "roles:\n  coordination_ticket: C-00\n"),    # not top-level
    (None, ""),                                         # empty file
])
def test_no_usable_key_refuses_every_session_the_ctos_included(tmp_path, key, roster_text):
    project = _project(tmp_path, key=key, roster_text=roster_text)
    for role, ticket in (("orchestrator", "C-00"), ("orchestrator", "T-01"), ("engineer", "T-02")):
        decision, reason = _hook(project, tmp_path, role=role, ticket=ticket)
        assert decision == "deny"
        assert ROSTER in reason and "coordination_ticket" in reason and "Set the top-level key" in reason


def test_an_unreadable_roster_refuses(tmp_path):
    project = _project(tmp_path, key=None)
    (project / ROSTER).mkdir(parents=True)  # a folder where the file should be
    decision, reason = _hook(project, tmp_path, role="orchestrator", ticket="C-00")
    assert decision == "deny" and ROSTER in reason


def test_a_roster_that_is_not_utf8_refuses(tmp_path):
    project = _project(tmp_path, key=None)
    (project / ROSTER).parent.mkdir(parents=True)
    (project / ROSTER).write_bytes(b"coordination_ticket: C-00\n\xff\xfe\n")
    decision, reason = _hook(project, tmp_path, role="orchestrator", ticket="C-00")
    assert decision == "deny" and ROSTER in reason


def test_an_error_inside_the_rule_refuses(tmp_path, monkeypatch):
    project = _project(tmp_path)

    def boom(*_):
        raise RuntimeError("boom")

    monkeypatch.setattr(install, "_ticket_file", boom)
    asks, reason = cto_install(str(project), "orchestrator", None, "C-00")
    assert asks is False and "P1 escalation" in reason


def test_coordination_ticket_names_the_file(tmp_path):
    project = _project(tmp_path, key="W9-00")
    assert coordination_ticket(str(project)) == (os.path.realpath(project / ".tickets/C-00.md"), "")


def test_cto_install_never_asks_without_the_key(tmp_path):
    project = _project(tmp_path, key=NO_KEY)
    asks, reason = cto_install(str(project), "orchestrator", None, "C-00")
    assert asks is False and "coordination_ticket" in reason


# -- 5: unchanged --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("role, ticket", [("orchestrator", "C-00"), ("orchestrator", "T-01"), ("engineer", "T-02")])
def test_sudo_is_refused_to_every_role(tmp_path, role, ticket):
    project = _project(tmp_path)
    decision, reason = _hook(project, tmp_path, command="sudo ls", role=role, ticket=ticket)
    assert decision == "deny" and "sudo" in reason


def test_a_frozen_project_refuses_the_ctos_install(tmp_path):
    project = _project(tmp_path)
    (project / ".gov-runtime").mkdir()
    (project / ".gov-runtime/freeze").write_text("FROZEN\n", encoding="utf-8")
    assert _hook(project, tmp_path, role="orchestrator", ticket="C-00")[0] == "deny"


@pytest.mark.parametrize("key", ["W9-00", NO_KEY, None])
def test_the_research_exception_stands_with_or_without_the_key(tmp_path, key):
    project = _project(tmp_path, key=key)
    decision, _ = _hook(project, tmp_path, command="uv sync", role="research", ticket="R-01",
                        cwd=project / FOLDER)
    assert decision == "allow"


@pytest.mark.parametrize("key", ["W9-00", NO_KEY, None])
def test_a_bash_call_that_is_not_an_install_is_unchanged(tmp_path, key):
    project = _project(tmp_path, key=key)
    assert _hook(project, tmp_path, command="ls", role="engineer", ticket="T-02")[0] == "allow"
    assert _hook(project, tmp_path, command="ls", role="orchestrator", ticket="T-01")[0] == "allow"


# -- the regression: a pinned gov older than the hook (no ``cto_install``) -----------------------------------------
# The hook once imported the CTO rule with the rest of the install rule, so under an older gov every Bash call ended
# with exit 2. Now only installs depend on it, and they are refused by a rule (fail closed).

def test_under_an_older_gov_a_bash_call_that_is_not_an_install_is_unchanged(tmp_path):
    project = _project(tmp_path)
    for role, ticket in (("engineer", "T-02"), ("orchestrator", "C-00"), ("research", "R-01")):
        assert _hook(project, tmp_path, command="ls", role=role, ticket=ticket, older_gov=True)[0] == "allow"


def test_under_an_older_gov_the_research_exception_stands(tmp_path):
    project = _project(tmp_path)
    decision, _ = _hook(project, tmp_path, command="uv sync", role="research", ticket="R-01", cwd=project / FOLDER,
                        older_gov=True)
    assert decision == "allow"


@pytest.mark.parametrize("role, ticket", [("orchestrator", "C-00"), ("orchestrator", "T-01"), ("engineer", "T-02"),
                                          ("research", "R-01")])
def test_under_an_older_gov_every_install_is_refused_by_a_rule_the_ctos_included(tmp_path, role, ticket):
    project = _project(tmp_path)
    decision, reason = _hook(project, tmp_path, role=role, ticket=ticket, older_gov=True)
    assert decision == "deny"
    assert "no CTO install rule" in reason and "P1 escalation to the CTO" in reason


def test_under_an_older_gov_sudo_is_still_refused(tmp_path):
    project = _project(tmp_path)
    decision, reason = _hook(project, tmp_path, command="sudo ls", role="engineer", ticket="T-02", older_gov=True)
    assert decision == "deny" and "sudo" in reason
