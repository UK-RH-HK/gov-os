"""W1-46 -- installs: let through for the research role inside its experiment folder, denied everywhere else.

KPI success 6 [CAP-25.e]: "In a launched research session an install command,
the uv forms of DEC-174 included (uv add, uv sync, uv run --with, uvx), is not
denied by the install rule and meets no settings ask rule, because the committed
.claude/settings.json carries none once W1-47 has removed them (DEC-172) ... the
acceptance test of the install runs with the repository's committed settings
loaded; install commands stay denied for engineer, independent test designer
and independent auditor, and the acceptance tests of W1-04 still pass".
KPI failure 6: "A launched research session's install inside its experiment
folder is stopped by a settings ask rule". Failure 7: "A role other than
research and the orchestrator gets an install command through".

DEC-219: the research role's exception is tested here, with the four ``uv``
forms of DEC-174 and the value options of DEC-216; the same commands stay denied
for engineer, independent test designer and independent auditor, and outside the
experiment folder.

Each command is text in the hook's input. None is run: nothing is installed and
no network is used. The decision is the one of the project's committed settings:
their deny and ask rules, then the PreToolUse commands they register.

"Inside its experiment folder" is read as: the session's working directory, as
the hook input gives it (``cwd``), is the experiment folder or below it. One
test covers a command that starts with ``cd <folder> &&`` from the repository
root; see DP-4 in the README for that reading.

The install that really runs, and the system-wide one that fails at the
sandbox's write fence, are in ``test_w1_46_live_sessions.py``.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47
RESEARCH = support.RESEARCH
FOLDER = support.EXPERIMENT_REL

# DEC-174: the four forms as the KPI names them.
UV_FORMS = {
    "uv-add": "uv add requests",
    "uv-sync": "uv sync",
    "uv-run-with": "uv run --with requests python script.py",
    "uvx": "uvx ruff check .",
}
# DEC-216: the four value options, and ``uv run -w``. Every value stays inside the folder.
VALUE_OPTIONS = {
    "directory-add": "uv --directory sub add requests",
    "project-sync": "uv --project sub sync",
    "cache-dir-sync": "uv --cache-dir .uv-cache sync",
    "config-file-add": "uv --config-file uv.toml add requests",
    "run-w": "uv run -w requests script.py",
}
# "An install command": the plain forms of W1-04, into a venv or local prefix of the folder.
OTHER_INSTALLS = {
    "uv-pip-install": "uv pip install requests",
    "venv-pip-install": ".venv/bin/pip install requests",
    "python-m-pip-install": ".venv/bin/python -m pip install requests",
    "npm-install": "npm install left-pad",
}
INSTALLS = {**UV_FORMS, **VALUE_OPTIONS, **OTHER_INSTALLS}
DEC_219_FORMS = {**UV_FORMS, **VALUE_OPTIONS}


@pytest.fixture()
def folder(project):
    return project / FOLDER


# --------------------------------------------------------------------------
# The research role, inside its experiment folder
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(INSTALLS))
def test_a_research_install_inside_the_experiment_folder_is_let_through(guard, folder, name):
    """Not denied by the install rule, and not asked: neither by the hook nor by a settings rule."""
    result = guard("Bash", w47.bash_input(INSTALLS[name]), RESEARCH, cwd=folder)
    w47.assert_allowed(result, f"`{INSTALLS[name]}` by research in its experiment folder")


@pytest.mark.parametrize("name", sorted(UV_FORMS))
def test_a_research_install_below_the_experiment_folder_is_let_through(guard, folder, name):
    (folder / "sub").mkdir()
    result = guard("Bash", w47.bash_input(UV_FORMS[name]), RESEARCH, cwd=folder / "sub")
    w47.assert_allowed(result, f"`{UV_FORMS[name]}` by research below its experiment folder")


def test_a_research_install_after_cd_into_the_experiment_folder_is_let_through(guard, project):
    """The reading of DP-4: ``cd <folder> && <install>`` from the repository root is inside the folder."""
    command = f"cd {FOLDER} && uv add requests"
    w47.assert_allowed(guard("Bash", w47.bash_input(command), RESEARCH, cwd=project), f"`{command}` by research")


@pytest.mark.parametrize("mode", w47.PERMISSION_MODES)
def test_no_permission_mode_turns_the_research_install_into_a_prompt(guard, folder, mode):
    """Failure 6. One form is enough: the mode is not part of the rule."""
    result = guard("Bash", w47.bash_input(UV_FORMS["uv-add"]), RESEARCH, cwd=folder, mode=mode)
    w47.assert_allowed(result, f"`uv add requests` by research in {mode} mode")


def test_the_committed_settings_carry_no_ask_rule_on_installs():
    """DEC-172: "meets no settings ask rule, because the committed .claude/settings.json carries none". Holds today."""
    asks = w47.permission_rules(w47.load_settings(), "ask")
    left = [rule for rule in asks if w47.is_withdrawn_install_rule(rule)]
    assert left == [], f".claude/settings.json still carries install or download ask rules: {left}"


def test_the_built_settings_carry_no_ask_rule_on_installs(launch):
    """The launcher does not bring back what DEC-172 withdrew: a later settings file cannot lift an ask rule."""
    built = launch(RESEARCH).settings()
    asks = [rule for rule in w47.permission_rules(built, "ask") if w47.bash_rule_prefix(rule) is not None]
    assert asks == [], f"the settings built for a research session carry Bash ask rules: {asks}"


# --------------------------------------------------------------------------
# The research role, outside its experiment folder
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", ("repository-root", "sibling-experiment", "source-tree"))
@pytest.mark.parametrize("name", sorted(DEC_219_FORMS))
def test_a_research_install_outside_the_experiment_folder_is_denied(guard, project, name, where):
    """DEC-219. Holds before implementation, for another reason: the guard does not know the role yet."""
    cwd = {"repository-root": project, "sibling-experiment": project / "experiments/spikes/exp-900",
           "source-tree": project / "src"}[where]
    result = guard("Bash", w47.bash_input(DEC_219_FORMS[name]), RESEARCH, cwd=cwd)
    w47.assert_denied_by_rule(result, f"`{DEC_219_FORMS[name]}` by research in {where}")


def test_a_research_install_on_another_roles_ticket_is_denied(guard, folder):
    """The exception belongs to the role on its own ticket: no experiment folder, no install."""
    result = guard("Bash", w47.bash_input(UV_FORMS["uv-add"]), RESEARCH, support.TICKET_OF[support.ENGINEER],
                   cwd=folder)
    w47.assert_denied_by_rule(result, "`uv add requests` by research on the engineer's ticket")


def test_sudo_stays_denied_to_the_research_role(guard, folder):
    """DEC-083: "sudo is denied to all agent roles". "No worker role installs system-wide" (DEC-157)."""
    for command in ("sudo apt-get install -y jq", "sudo pip install requests"):
        result = guard("Bash", w47.bash_input(command), RESEARCH, cwd=folder)
        w47.assert_denied_by_rule(result, f"`{command}` by research")


# --------------------------------------------------------------------------
# Every other worker role (failure 7)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
@pytest.mark.parametrize("name", sorted(DEC_219_FORMS))
def test_the_same_commands_stay_denied_for_the_other_worker_roles(guard, project, folder, name, role):
    """In the experiment folder and in the repository root. Holds before implementation; it must still hold after."""
    for cwd in (folder, project):
        result = guard("Bash", w47.bash_input(DEC_219_FORMS[name]), role, cwd=cwd)
        w47.assert_denied_by_rule(result, f"`{DEC_219_FORMS[name]}` by {role} in {cwd.name}")


@pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
def test_another_role_on_the_research_ticket_gets_no_install_through(guard, folder, role):
    """The exception is the research role's, not the research ticket's."""
    result = guard("Bash", w47.bash_input(UV_FORMS["uv-add"]), role, support.RESEARCH_TICKET, cwd=folder)
    w47.assert_denied_by_rule(result, f"`uv add requests` by {role} on the research ticket")
