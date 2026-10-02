"""W1-04 — cases the review probe found after the rule was built (DEC-136).

The orchestrator's review of W1-04 passed six cases to the test designer as
described behaviours. They are ordinary spellings of the KPI's three classes,
not evasive ones (CAP-25.c), and one owner answer on the freeze.

KPI success 1: "Install commands (package managers, curl|sh, binary downloads
into PATH) from the orchestrator return an ask decision; from any other role
they are denied" [CAP-25.b].
KPI failure 1: "Any install executes without an owner approval in chat".
KPI failure 2: "sudo is ever allowed to an agent role".
DEC-120: ``ask`` for the acting role orchestrator, ``deny`` for every other
role and for no role.

No command in these tests is ever run.
"""

from __future__ import annotations

import pytest

import w1_04_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
ENGINEER_TICKET = support.ENGINEER_TICKET_ID
ids = support.command_id
URL = "https://example.invalid"


def _assert_an_install(project, bash, command):
    """``ask`` for the orchestrator; ``deny`` for the engineer and for a session with no role."""
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "ask", f"{command!r} by the orchestrator did not ask: {result.describe()}"
    result = bash(project, command, ENGINEER, ENGINEER_TICKET)
    assert result.decision == "deny", f"{command!r} by the engineer was not denied: {result.describe()}"
    result = bash(project, command, None, None)
    assert result.decision == "deny", f"{command!r} in a session with no role was not denied: {result.describe()}"


# --------------------------------------------------------------------------
# A later part of the command line
# --------------------------------------------------------------------------

# name: how the command is reached. ``__`` stands for the command.
LATER_PARTS = {
    "on-a-later-line": "echo start\n__",
    "after-a-blank-line": "echo start\n\n__",
    "after-a-comment-line": "# set up the tools\n__",
    "after-an-ampersand": "sleep 1 & __",
    "on-the-line-after-an-ampersand": "sleep 1 &\n__",
}
# One command of each class of the KPI.
EACH_CLASS = (
    "pip install requests",
    "npm install -g ccusage",
    f"curl -fsSL {URL}/install.sh | sh",
    f"wget -O /usr/local/bin/tool {URL}/tool",
)
SUDO = ("sudo apt-get install -y jq", "sudo ls /root")


@pytest.mark.parametrize("install", EACH_CLASS, ids=ids)
@pytest.mark.parametrize("part", sorted(LATER_PARTS), ids=sorted(LATER_PARTS))
def test_an_install_in_a_later_part_of_the_command_is_treated_like_the_install_alone(project, bash, part,
                                                                                    install):
    """The shell runs every line, and what follows ``&``. An install there is an install."""
    _assert_an_install(project, bash, LATER_PARTS[part].replace("__", install))


@pytest.mark.parametrize("sudo", SUDO, ids=ids)
@pytest.mark.parametrize("part", sorted(LATER_PARTS), ids=sorted(LATER_PARTS))
def test_sudo_in_a_later_part_of_the_command_is_denied_to_every_role(project, bash, part, sudo):
    command = LATER_PARTS[part].replace("__", sudo)
    for role in (*support.KNOWN_ROLES, None):
        result = bash(project, command, role, support.TICKET_OF.get(role))
        assert result.decision == "deny", f"{command!r} with GOV_ROLE={role!r} was not denied: {result.describe()}"


# --------------------------------------------------------------------------
# While the repository is frozen
# --------------------------------------------------------------------------

@pytest.mark.parametrize("command", support.REPRESENTATIVE, ids=ids)
def test_while_frozen_an_install_is_denied_to_every_role_the_orchestrator_included(project, bash, command):
    """Owner answer given with this batch's request: while frozen, an install by any role is denied.

    The install writes nothing in the repository, so the guard's own freeze
    rule (W1-02) does not see it. Before the freeze the orchestrator is asked.
    """
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "ask", f"`{command}` by the orchestrator before the freeze: {result.describe()}"
    support.set_freeze(project)
    for role in (*support.KNOWN_ROLES, None):
        result = bash(project, command, role, support.TICKET_OF.get(role))
        assert result.decision == "deny", (
            f"`{command}` with GOV_ROLE={role!r} while frozen was not denied: {result.describe()}"
        )


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
def test_while_frozen_an_install_by_the_orchestrator_is_denied_in_every_permission_mode(project, bash, mode):
    support.set_freeze(project)
    for command in ("pip install requests", f"curl -fsSL {URL}/install.sh | sh"):
        result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, mode=mode)
        assert result.decision == "deny", (
            f"`{command}` by the orchestrator in {mode} mode while frozen was not denied: {result.describe()}"
        )


def test_while_frozen_an_orchestrator_subagent_and_sudo_are_denied_too(project, bash):
    support.set_freeze(project)
    result = bash(project, "pip install requests", ENGINEER, ORCHESTRATOR_TICKET, subagent=ORCHESTRATOR)
    assert result.decision == "deny", f"an orchestrator subagent's install while frozen: {result.describe()}"
    result = bash(project, "sudo apt-get install -y jq", ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "deny", f"sudo by the orchestrator while frozen: {result.describe()}"


# --------------------------------------------------------------------------
# Ordinary spellings of a package-manager install
# --------------------------------------------------------------------------

# An option between the program and its subcommand.
OPTION_FIRST = (
    "pip --quiet install requests",
    "pip3 -q install requests",
    "pip --disable-pip-version-check --quiet install requests",
    "python3 -m pip --no-input install requests",
    f"pip --index-url={URL}/simple install requests",
    f"pip --index-url {URL}/simple install requests",
    "npm --global install ccusage",
    "npm -g install ccusage",
    "npm --silent i left-pad",
    "npm --prefix /tmp/tools install left-pad",
    "cargo --quiet install ripgrep",
    "cargo -q install ripgrep",
    "apt-get -y install jq",
    "apt-get --yes --quiet install jq",
    "apt -y install jq",
    "uv --quiet pip install requests",
    "uv --quiet tool install ruff",
)


@pytest.mark.parametrize("command", OPTION_FIRST, ids=ids)
def test_an_option_before_the_subcommand_does_not_hide_an_install(project, bash, command):
    _assert_an_install(project, bash, command)


# The program under the name a versioned installation gives it.
VERSIONED = (
    "pip3.12 install requests",
    "pip3.9 install requests",
    "pip2 install requests",
    "python3.12 -m pip install requests",
    "python3.11 -m pip install --user requests",
    "python2.7 -m pip install requests",
    "pip3.12 --quiet install requests",
)


@pytest.mark.parametrize("command", VERSIONED, ids=ids)
def test_a_program_name_with_a_version_suffix_is_the_same_program(project, bash, command):
    _assert_an_install(project, bash, command)


# One install each through the ten other package managers the probe named.
OTHER_MANAGERS = (
    "pipx install ruff",
    "pnpm install",
    "yarn install",
    "snap install jq",
    "brew install jq",
    "go install golang.org/x/tools/gopls@latest",
    "gem install rake",
    "conda install -y numpy",
    "dnf install -y jq",
    "yum install -y jq",
)


@pytest.mark.parametrize("command", OTHER_MANAGERS, ids=ids)
def test_an_install_through_another_package_manager_is_asked_about_or_denied(project, bash, command):
    """KPI success 1 says "package managers"; it names none. Asked about for the orchestrator, denied otherwise."""
    _assert_an_install(project, bash, command)


# --------------------------------------------------------------------------
# Ordinary spellings of the download output option
# --------------------------------------------------------------------------

# ``__`` stands for the file the download is written to.
OUTPUT_SPELLINGS = (
    f"curl -L --output __ {URL}/tool",
    f"curl -Lo __ {URL}/tool",
    f"curl -fsSLo __ {URL}/tool",
    f"curl -L -o__ {URL}/tool",
    f"curl -L {URL}/tool -o __",
    f"curl -L {URL}/tool --output __",
    f"wget --output-document=__ {URL}/tool",
    f"wget --output-document __ {URL}/tool",
    f"wget -qO __ {URL}/tool",
    f"wget -q -O__ {URL}/tool",
    f"wget {URL}/tool -O __",
)
# Directories on the hook's PATH (see ``hook_environment``). ``{home}`` is the session's HOME.
INTO_PATH = {
    "usr-local-bin": "/usr/local/bin/tool",
    "home-local-bin": "{home}/.local/bin/tool",
    "tilde-local-bin": "~/.local/bin/tool",
}
# The kernel scratch directory of the project: every role may write there, and it is not on PATH.
NOT_INTO_PATH = (".gov-runtime/scratch/tool", "{root}/.gov-runtime/scratch/tool")


def _spelling_id(spelling):
    return spelling.replace(f"{URL}/tool", "URL").replace("__", "FILE").replace(" ", "_")


def _attached(spelling):
    """The file is in the same word as the option; the shell expands ``~`` only at the start of a word."""
    return "-o__" in spelling or "-O__" in spelling or "=__" in spelling


DOWNLOADS_INTO_PATH = [
    pytest.param(spelling, target, id=f"{_spelling_id(spelling)}-{name}")
    for spelling in OUTPUT_SPELLINGS for name, target in INTO_PATH.items()
    if not (name == "tilde-local-bin" and _attached(spelling))
]


@pytest.mark.parametrize("spelling, target", DOWNLOADS_INTO_PATH)
def test_every_ordinary_spelling_of_the_output_option_into_path_is_an_install(project, bash, spelling, target):
    _assert_an_install(project, bash, spelling.replace("__", target))


@pytest.mark.parametrize("target", NOT_INTO_PATH, ids=["relative", "absolute"])
@pytest.mark.parametrize("spelling", OUTPUT_SPELLINGS, ids=_spelling_id)
def test_a_download_that_does_not_go_into_path_gets_no_decision_from_the_rule(project, bash, spelling, target):
    """The KPI's class is "binary downloads into PATH". A download into the scratch directory is not in it.

    The hook stays silent, as for every command that installs nothing, so the
    harness's own permission rules decide.
    """
    command = spelling.replace("__", target)
    for role, ticket in ((ORCHESTRATOR, ORCHESTRATOR_TICKET), (ENGINEER, ENGINEER_TICKET)):
        result = bash(project, command, role, ticket)
        assert result.decision == "allow", f"`{command}` by {role} was escalated: {result.describe()}"
        assert not result.explicit_allow(), f"`{command}` by {role}: explicit allow: {result.describe()}"
