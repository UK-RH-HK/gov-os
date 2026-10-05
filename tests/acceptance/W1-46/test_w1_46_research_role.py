"""W1-46 -- the minimal research role: its role file, its roster entry, and the guard's decisions for it.

KPI success 5 [CAP-22.d]: "A minimal research role is in the Wave 1 roster: a
role file with purpose, allowed-path pattern, tools, model tier, authority level
and handoff format, plus its roster entry; a research or experiment session runs
as GOV_ROLE=research; the guard knows the role and holds its writes to its
ticket's allowed_paths (its experiment folder); its network grant comes from the
launcher's profile, the research allowlist of DEC-158, not from the guard
(DEC-163)".

KPI success 8 [CAP-58.d], the file-tool half: "a file-tool write outside it is
refused by the permission rules and the guard".

The guard is asked through the PreToolUse commands the committed settings
register, run through the shell as the harness runs them. No call is made.
"""

from __future__ import annotations

import re

import pytest
import yaml

import w1_46_support as support

w47 = support.w47
RESEARCH = support.RESEARCH
FOLDER = support.EXPERIMENT_REL

# The six parts the KPI names, as a role file would word them.
ROLE_FILE_PARTS = {
    "purpose": r"purpose",
    "allowed-path pattern": r"allowed[\s_-]*paths?",
    "tools": r"tools",
    "model tier": r"model[\s_-]*tier",
    "authority level": r"authority",
    "handoff format": r"hand[\s_-]?off",
}


# --------------------------------------------------------------------------
# The role file and the roster entry (committed files of this repository)
# --------------------------------------------------------------------------

def _role_files():
    files = [path for path in sorted(support.REPO_ROOT.glob(support.KERNEL_ROLE_GLOB)) if path.is_file()]
    agent = support.REPO_ROOT / support.AGENT_REL
    return files + ([agent] if agent.is_file() else [])


def test_the_research_role_has_a_role_file():
    assert _role_files(), f"there is no research role file ({support.KERNEL_ROLE_GLOB} or {support.AGENT_REL})"


def test_the_role_file_states_the_six_parts_the_kpi_names():
    files = _role_files()
    assert files, "there is no research role file"
    missing = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        missing[path.relative_to(support.REPO_ROOT).as_posix()] = [part for part, pattern in ROLE_FILE_PARTS.items()
                              if not re.search(pattern, text, re.IGNORECASE)]
    assert any(not parts for parts in missing.values()), f"no research role file states all six parts: {missing}"


def test_the_research_role_is_a_session_role_definition_like_the_others():
    """``.claude/agents/research.md`` with the frontmatter of the five existing definitions (W1-05)."""
    path = support.REPO_ROOT / support.AGENT_REL
    assert path.is_file(), f"{support.AGENT_REL} does not exist"
    meta = support.live_support.frontmatter(path.read_text(encoding="utf-8"))
    assert meta and meta.get("name") == RESEARCH, f"{support.AGENT_REL} does not declare name: research ({meta})"
    assert str(meta.get("description", "")).strip(), f"{support.AGENT_REL} has no description"


def _names_research(value):
    if isinstance(value, dict):
        return any(key == RESEARCH or _names_research(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_names_research(item) for item in value)
    return value == RESEARCH


def test_the_roster_has_an_entry_for_the_research_role():
    path = support.REPO_ROOT / support.ROSTER_REL
    assert path.is_file(), f"{support.ROSTER_REL} does not exist"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, (dict, list)) and _names_research(data), (
        f"{support.ROSTER_REL} has no entry whose key or value is the role name `research`"
    )


# --------------------------------------------------------------------------
# The guard knows the role and holds its writes to its ticket's allowed_paths
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_a_research_session_may_write_inside_its_experiment_folder(guard, project, tool):
    for rel in (f"{FOLDER}/notes.md", f"{FOLDER}/results/run-1.json"):
        result = guard(tool, w47.write_input(tool, project / rel), RESEARCH)
        w47.assert_allowed(result, f"{tool} to {rel} by research")


def test_a_research_session_may_write_inside_its_experiment_folder_with_bash(guard, project):
    for command in (f"mkdir -p {FOLDER}/results", f"echo done > {FOLDER}/results/run-1.txt",
                    f"cp README.md {FOLDER}/copy.md"):
        w47.assert_allowed(guard("Bash", w47.bash_input(command), RESEARCH), f"`{command}` by research")


def test_a_research_session_may_use_scratch(guard, project):
    """Scratch is every known role's (W1-02). Red until the guard knows the role."""
    result = guard("Write", w47.write_input("Write", project / ".gov-runtime/scratch/research/notes.md"), RESEARCH)
    w47.assert_allowed(result, "a Write to .gov-runtime/scratch/ by research")


@pytest.mark.parametrize("tool", ("Write", "Edit"))
@pytest.mark.parametrize("rel", ("README.md", "src/gov/guard/decide.py", "experiments/spikes/exp-900/data.txt",
                                 "experiments/notes.md", "tests/acceptance/W1-90/test_fixture.py",
                                 ".tickets/DAEO-zz97.md", "governance/project/held-out.yaml"))
def test_a_research_write_outside_its_experiment_folder_is_denied(guard, project, tool, rel):
    """Holds before implementation, for another reason: the guard does not know the role yet."""
    w47.assert_stopped(guard(tool, w47.write_input(tool, project / rel), RESEARCH), f"{tool} to {rel} by research")


def test_a_research_bash_write_outside_its_experiment_folder_is_denied(guard, project):
    for command in ("echo x >> README.md", "rm experiments/notes.md", f"cp {FOLDER}/README.md src/gov/copied.md",
                    "touch experiments/spikes/exp-900/new.txt"):
        w47.assert_stopped(guard("Bash", w47.bash_input(command), RESEARCH), f"`{command}` by research")


def test_the_research_role_has_no_scope_on_another_roles_ticket(guard, project):
    """ "Its ticket's allowed_paths": a research session on an engineer's ticket gets neither scope."""
    for rel in (support.OWN_PATH[support.ENGINEER], f"{FOLDER}/notes.md"):
        result = guard("Write", w47.write_input("Write", project / rel), RESEARCH, support.TICKET_OF[support.ENGINEER])
        w47.assert_stopped(result, f"a Write to {rel} by research on the engineer's ticket")


@pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
def test_another_role_gains_nothing_from_the_research_ticket(guard, project, role):
    result = guard("Bash", w47.bash_input(f"echo x > {FOLDER}/notes.md"), role, support.RESEARCH_TICKET)
    if role == support.TEST_DESIGNER:
        return   # its scope is tests/acceptance/** whatever the ticket (W1-02)
    w47.assert_stopped(result, f"a Bash write into the experiment folder by {role} on the research ticket")


def test_the_guard_grants_the_research_role_no_network_and_asks_nothing_for_it(guard, project):
    """ "Its network grant comes from the launcher's profile ... not from the guard": the guard just lets the call by."""
    for command in ("curl -sI https://pypi.org/simple/", "git ls-remote https://github.com/astral-sh/uv"):
        result = guard("Bash", w47.bash_input(command), RESEARCH, cwd=project / FOLDER)
        w47.assert_allowed(result, f"`{command}` by research")


# --------------------------------------------------------------------------
# Success 8 [CAP-58.d]: a file-tool write outside the repository
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
@pytest.mark.parametrize("tool", ("Write", "Edit", "NotebookEdit"))
def test_a_file_tool_write_outside_the_repository_is_refused_by_the_guard(guard, sandbox, role, tool):
    """Holds before implementation for every role; it must still hold once the guard knows the research role."""
    for target in (sandbox.elsewhere / "outside.txt", sandbox.home / ".bashrc", "/etc/w1-46-outside"):
        w47.assert_stopped(guard(tool, w47.write_input(tool, target), role), f"{tool} to {target} by {role}")
