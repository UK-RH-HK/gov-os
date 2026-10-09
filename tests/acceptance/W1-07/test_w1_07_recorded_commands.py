"""The four commands recorded in the command list beside the twelve (DEC-542, DEC-546; DEC-569).

DEC-542: "``ci``, ``launch``, ``telemetry`` and ``lock`` are recorded in the command list, each with one
test-designer line." The lines are in ``w1_07_support.py`` (``RECORDED_GOV_COMMANDS``,
``RECORDED_MODULE_COMMANDS``); each command has one case here.

What "recorded" means for each (README, section "The four commands of DEC-542"):

- ``ci``, ``launch`` and ``telemetry`` are ``gov`` commands as found: ``gov --help`` names each, and each
  answers its own ``--help``. No case runs one of them: ``launch`` starts a session and ``ci`` runs gates.
- ``lock`` is recorded as what it is today, the module command ``python3 -m gov.lock`` (the template's Copier
  task, DEC-499). Recording it adds no command: ``gov lock`` stays a usage error and ``gov --help`` does not
  offer it.

The command set as a whole (the twelve and these three, and nothing more) is held in W1-32's suite. What the
check on the command list reports for the four is held in W1-26's suite.

The cases are green: they hold what is found, so that the list and the command line cannot part unseen.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest

import w1_07_support as support

LOCK_TIMEOUT_S = 60.0


def _offered(run):
    """The command names ``gov --help`` offers: argparse's ``{a,b}`` list, or the indented first words."""
    found = re.search(r"\{([a-z,-]+)\}", run.stdout)
    if found:
        return set(found.group(1).split(","))
    listed = run.stdout.split("positional arguments:", 1)[-1].split("\noptions:", 1)[0]
    return set(re.findall(r"^    ([a-z][a-z-]*)(?:\s|$)", listed, re.MULTILINE))


def test_the_recorded_commands_are_four_and_none_is_one_of_the_twelve():
    recorded = support.RECORDED_GOV_COMMANDS + support.RECORDED_MODULE_COMMANDS
    assert sorted(recorded) == ["ci", "launch", "lock", "telemetry"], recorded
    assert not set(recorded) & set(support.RESERVED_COMMANDS), "a recorded command is one of the twelve"


@pytest.mark.parametrize("name", support.RECORDED_GOV_COMMANDS)
def test_a_recorded_gov_command_is_offered_and_answers_its_help(gov, name):
    """One case for each of ``ci``, ``launch`` and ``telemetry``."""
    listed = gov("--help")
    assert listed.returncode == 0, listed.describe()
    assert name in _offered(listed), f"gov --help does not offer the recorded command {name}\n{listed.describe()}"
    run = gov(name, "--help")
    assert run.returncode == 0, f"gov {name} --help does not end with exit code 0\n{run.describe()}"
    assert name in run.stdout, f"the help of gov {name} does not name the command\n{run.describe()}"


def test_lock_is_recorded_as_the_module_command_and_is_no_gov_command(gov, project, sandbox):
    """The one case of ``lock``. In a folder that is no installed project the module command runs, says that
    the lock was not written and writes nothing; ``gov`` has no command of that name."""
    listed = gov("--help")
    assert listed.returncode == 0, listed.describe()
    assert "lock" not in _offered(listed), f"gov --help offers a command lock\n{listed.describe()}"
    asked = gov("lock", "--json")
    assert asked.returncode == 2, f"gov lock is not a usage error: a command was added\n{asked.describe()}"

    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(project / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    done = subprocess.run([sys.executable, "-m", "gov.lock"], cwd=str(sandbox.elsewhere), env=env,
                          capture_output=True, text=True, timeout=LOCK_TIMEOUT_S, stdin=subprocess.DEVNULL)
    said = f"exit code {done.returncode}\nstdout: {done.stdout}\nstderr: {done.stderr}"
    assert "No module named" not in done.stderr, f"python3 -m gov.lock is no command\n{said}"
    assert done.returncode == 1 and "framework.lock" in done.stderr, \
        f"python3 -m gov.lock did not refuse a folder that is no installed project\n{said}"
    assert not list(sandbox.elsewhere.iterdir()), f"python3 -m gov.lock wrote into the folder\n{said}"
