"""W1-48 — every Node 22 install command of the registry carries the PATH prefix (DEC-207).

DEC-202: "The ccusage commands carry the prefix
``PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH``, because npm's script runs the
first ``node`` on ``PATH``. … Every future Node 22 install uses the prefix."

DEC-207: "W1-48's test designer adds a check that every Node 22 install command
in the registry carries the prefix ``PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH``."

The registry's commands spell the home directory ``$HOME``; ``~`` and
``${HOME}`` are the same directory and are accepted.

These cases hold before W1-48's implementation: the registry W1-06 committed
already carries the prefix on its openspec and ccusage commands. They are here
to keep it so, for those entries and for every later one.
"""

from __future__ import annotations

import pytest

import w1_48_support as support

PREFIXED = "PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH "


def _node_22_commands(registry):
    """``(tool, which command, the command)`` for every install and uninstall command that is a Node 22 command."""
    return [(support.norm_name(entry.get("name", "")), key, str(entry.get(key, "")))
            for entry in support.entries(registry) for key in ("install", "uninstall")
            if support.is_node_22_command(str(entry.get(key, "")))]


def test_every_node_22_command_of_the_registry_carries_the_path_prefix(registry):
    wrong = [f"{tool}.{key}: {command!r}" for tool, key, command in _node_22_commands(registry)
             if not support.carries_node_22_prefix(command)]
    assert wrong == [], (
        "Node 22 commands of the registry without the prefix PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH "
        f"before the package manager (DEC-202, DEC-207): {wrong}"
    )


@pytest.mark.parametrize("tool", ["openspec", "ccusage"])
def test_the_check_sees_the_node_22_commands_the_registry_has(registry, tool):
    """The two npm packages W1-06 recorded are found as Node 22 commands, install and uninstall: the check is not empty."""
    seen = {key for name, key, _ in _node_22_commands(registry) if name == tool}
    assert seen == {"install", "uninstall"}, (
        f"the check takes {sorted(seen) or 'no command'} of the {tool} entry for a Node 22 command; "
        "both its commands run npm"
    )


@pytest.mark.parametrize("command", [
    "npm install -g ccusage@20.0.26",
    "$HOME/.nvm/versions/node/v22.23.3/bin/npm install -g ccusage@20.0.26",
    "~/.nvm/versions/node/v22.23.3/bin/npm uninstall -g ccusage",
    "cd /tmp && npx some-tool@1.0.0",
    "PATH=$HOME/.nvm/versions/node/v18.20.8/bin:$PATH npm install -g x@1",
    "PATH=$HOME/.nvm/versions/node/v22.23.3/bin npm install -g x@1",
    "npm install -g x@1 && PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH npm ls -g",
    "MYPATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH npm install -g x@1",
])
def test_the_check_refuses_a_node_22_command_without_the_prefix(command):
    assert support.is_node_22_command(command), f"not taken for a Node 22 command: {command!r}"
    assert not support.carries_node_22_prefix(command), f"passes as prefixed: {command!r}"


@pytest.mark.parametrize("command", [
    PREFIXED + "npm install -g @fission-ai/openspec@1.13.2",
    PREFIXED + "$HOME/.nvm/versions/node/v22.23.3/bin/npm uninstall -g ccusage",
    "PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH npm install -g x@1",
    "PATH=${HOME}/.nvm/versions/node/v22.23.3/bin:${PATH} npx x@1",
    'PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH" npm install -g x@1',
])
def test_the_check_accepts_a_node_22_command_with_the_prefix(command):
    assert support.is_node_22_command(command), f"not taken for a Node 22 command: {command!r}"
    assert support.carries_node_22_prefix(command), f"refused although prefixed: {command!r}"


@pytest.mark.parametrize("command", [
    "bash -c '. ~/.nvm/nvm.sh && nvm install 22.23.3'",
    "uv tool install copier==9.18.2",
    "sudo apt-get install bubblewrap=0.9.0-1ubuntu0.3",
    "claude install 2.1.288",
    "rm -f ~/.local/bin/claude",
])
def test_the_check_leaves_other_commands_alone(command):
    """Installing Node itself (nvm), uv, apt and Claude Code's native installer are not Node 22 installs."""
    assert not support.is_node_22_command(command), f"taken for a Node 22 command: {command!r}"
