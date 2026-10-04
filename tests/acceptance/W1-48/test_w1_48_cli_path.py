"""W1-48 — DEC-211: registry commands carry the absolute path of the CLI; a bare ``claude`` is refused.

DEC-211 (the owner's answer on DP-2): "Registry commands carry the absolute
path (``$HOME/.local/bin/claude``), and a test refuses a bare ``claude``."

DEC-205: a second ``claude`` is on ``PATH`` (a Windows-side npm install), so
"every headless worker is started with the absolute path ``~/.local/bin/claude``,
never a bare ``claude``". Whoever repeats a recorded command on a changed
``PATH`` must not start that copy either.

The check reads the ``install`` and ``uninstall`` commands of every entry of
the registry. It looks at command words only: the program a command runs.
``claude`` as an argument, as part of a package name or of another path is
left alone. The check itself is tested on fixed sample commands.
"""

from __future__ import annotations

import pytest

import w1_48_support as support

COMMAND_KEYS = ("install", "uninstall")


def test_no_registry_command_runs_a_bare_claude(registry):
    refused = [f"{support.norm_name(entry.get('name', ''))}.{key}: {word}"
               for entry in support.entries(registry) for key in COMMAND_KEYS
               for word in support.refused_claude_words(support.field(entry, key))]
    assert refused == [], (
        f"{support.REGISTRY_REL} holds commands that run `claude` otherwise than by its absolute path "
        f"$HOME/.local/bin/claude (DEC-211): {refused}"
    )


def test_the_claude_code_install_command_runs_no_bare_claude(registry):
    """The command DEC-203 records is ``claude install 2.1.288``; the registry spells the path (DEC-211)."""
    entry = support.one(registry, support.CLAUDE_CODE)
    for key in COMMAND_KEYS:
        refused = support.refused_claude_words(support.field(entry, key))
        assert refused == [], f"the Claude Code entry's {key} command runs {refused}, not $HOME/.local/bin/claude"


# --------------------------------------------------------------------------
# The check itself, on fixed sample commands
# --------------------------------------------------------------------------

REFUSED = [
    "claude install 2.1.288",
    "claude update",
    "  claude install 2.1.288",
    "cd /tmp && claude install 2.1.288",
    "true; claude install 2.1.288",
    "test -x ~/.local/bin/claude || claude install 2.1.288",
    "echo 2.1.288 | claude install",
    "PATH=$HOME/.local/bin:$PATH claude install 2.1.288",
    "env PATH=/usr/bin claude install 2.1.288",
    "sudo claude install 2.1.288",
    "bash -c 'claude install 2.1.288'",
    "bash -lc \"claude install 2.1.288\"",
    "echo $(claude --version)",
    "$HOME/.local/bin/claude install 2.1.288 && claude --version",
    # another copy, or a path that is not absolute
    "/mnt/c/Users/someone/AppData/Roaming/npm/claude install 2.1.288",
    "/usr/local/bin/claude install 2.1.288",
    "./claude install 2.1.288",
    ".local/bin/claude install 2.1.288",
    "claude.exe install 2.1.288",
]

ACCEPTED = [
    "$HOME/.local/bin/claude install 2.1.288",
    "${HOME}/.local/bin/claude install 2.1.288",
    "~/.local/bin/claude install 2.1.288",
    "/home/someone/.local/bin/claude install 2.1.288",
    "\"$HOME/.local/bin/claude\" install 2.1.288",
    "cd /tmp && $HOME/.local/bin/claude install 2.1.288",
    "PATH=/usr/bin:/bin $HOME/.local/bin/claude install 2.1.288",
    "bash -c '$HOME/.local/bin/claude install 2.1.288'",
]

LEFT_ALONE = [
    # `claude` is not the program that runs
    "ln -sfn $HOME/.local/share/claude/versions/2.1.284 $HOME/.local/bin/claude && rm -f "
    "$HOME/.local/share/claude/versions/2.1.288",
    "rm -f ~/.local/bin/claude",
    "npm install -g @anthropic-ai/claude-code@2.1.288",
    "curl -fsSL https://claude.ai/install.sh | bash -s 2.1.288",
    "code --install-extension anthropic.claude-code",
    "rm -rf ~/.claude",
    "sudo apt-get install bubblewrap=0.9.0-1ubuntu0.3",
    "uv tool install copier==9.18.2",
    "",
]


@pytest.mark.parametrize("command", REFUSED)
def test_the_check_refuses_a_claude_that_is_not_run_by_its_absolute_path(command):
    assert support.refused_claude_words(command), f"not refused, and it runs a `claude` found some other way: {command!r}"


@pytest.mark.parametrize("command", ACCEPTED)
def test_the_check_accepts_the_cli_run_by_its_absolute_path(command):
    assert support.refused_claude_words(command) == [], f"refused, and it runs ~/.local/bin/claude: {command!r}"
    assert any(support.CLI_PATH_WORD.fullmatch(word) for word in support.command_words(command)), (
        f"the check does not see the CLI as a command word of: {command!r}"
    )


@pytest.mark.parametrize("command", LEFT_ALONE)
def test_the_check_leaves_a_command_alone_that_runs_no_claude(command):
    assert support.refused_claude_words(command) == [], f"refused, and no `claude` runs in it: {command!r}"
