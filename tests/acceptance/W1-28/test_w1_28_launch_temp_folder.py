"""KPI success 5 (DEC-386): the launcher removes its per-session temp folder.

"gov launch removes its per-session temp folder when the session ends."

``gov launch`` gives each session a temp folder of its own (DEC-159) and, as
W1-46 left it, leaves the folder behind. DEC-386 has it removed. What "when
the session ends" covers, as the ticket's brief settles it:

- **A normal end, and an end with a non-zero exit code.** The folder is
  removed after the CLI returns, with everything the session left in it. The
  launcher's exit code stays the session's (DEC-332).
- **An interrupt of the launcher** while its session runs. The launcher is
  started in a process group of its own, the stand-in session reports that it
  runs and waits, and the test sends ``SIGINT``: to the group (launcher and
  session, as Ctrl-C in a terminal does) and to the launcher alone
  (``kill -INT``). Nothing is timed: the test waits for the session's report
  and then for the launcher to end.
- **The folder goes whole.** A link inside it that points outside is removed
  as a link: what it points to stays, with its content.
- **Nothing else goes.** The directory the folders are made in keeps every
  other entry, a folder of another session among them.
- **A launch that starts no session leaves no folder**: a refusal, and a CLI
  that cannot be started.

Not tested (README, residuals): a launcher that is killed outright (SIGKILL,
power loss) cannot remove anything; SIGTERM, the exit code after an
interrupt, and a folder whose removal fails are not decided.
"""

from __future__ import annotations

import os

import pytest

import w1_28_launch_support as support

w46 = support.w46

LEFT = {
    "claude-1000/session/scratchpad/notes.txt": "notes\n",
    "claude-1000/session/tasks/1.json": "{}\n",
    ".hidden/cache.bin": "cache\n",
    "top-level.txt": "left at the top\n",
}


def _listing(sandbox):
    return sorted(os.listdir(sandbox.tmpdir))


# --------------------------------------------------------------------------
# The session ends
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.LAUNCHED_ROLES)
def test_the_temp_folder_is_removed_when_the_session_ends(launch, cli, role):
    support.plan(cli, files=LEFT)
    result = launch(role)
    assert result.run.returncode == 0, f"gov launch {role} did not end with the session's exit code 0\n{result.describe()}"
    support.assert_removed(support.temp_folder(result), f"after the {role} session ended")


@pytest.mark.parametrize("code", (1, 7))
def test_the_temp_folder_is_removed_when_the_session_ends_with_an_error(launch, cli, code):
    """DEC-332: the launcher's exit code is the session's, before and after the removal."""
    support.plan(cli, files=LEFT, exit_code=code)
    result = launch(support.ENGINEER)
    folder = support.temp_folder(result)
    assert result.run.returncode == code, (
        f"the session ended with exit code {code} and gov launch with {result.run.returncode}\n{result.describe()}"
    )
    support.assert_removed(folder, f"after a session that ended with exit code {code}")


def test_a_session_that_left_nothing_has_its_folder_removed_too(launch, cli):
    support.plan(cli)
    result = launch(support.RESEARCH)
    support.assert_removed(support.temp_folder(result), "after a session that wrote nothing")


def test_each_session_has_its_own_folder_and_each_is_removed(launch, cli):
    support.plan(cli, files=LEFT)
    first, second = support.temp_folder(launch(support.ENGINEER)), support.temp_folder(launch(support.ENGINEER))
    assert first != second, f"two sessions were given the same temp folder: {first}"
    for folder in (first, second):
        support.assert_removed(folder, "after two sessions in a row")


# --------------------------------------------------------------------------
# Whole, and nothing else
# --------------------------------------------------------------------------

def test_a_link_in_the_folder_is_removed_and_what_it_points_to_stays(launch, cli, sandbox, launch_project):
    """A link to a file and a link to a directory, outside the folder. The removal does not follow them."""
    outside_file = sandbox.elsewhere / "outside.txt"
    outside_file.write_text("outside the temp folder\n", encoding="utf-8")
    outside_dir = sandbox.elsewhere / "outside-directory"
    (outside_dir / "deep").mkdir(parents=True)
    (outside_dir / "deep" / "kept.txt").write_text("kept\n", encoding="utf-8")
    in_project = launch_project / "docs" / "notes.md"
    notes = in_project.read_text(encoding="utf-8")
    before = support.entries(outside_dir)
    support.plan(cli, files=LEFT, links={"link-to-file": outside_file, "sub/link-to-directory": outside_dir,
                                         "link-to-project-file": in_project, "link-to-project": launch_project})
    result = launch(support.ENGINEER)
    support.assert_removed(support.temp_folder(result), "after a session that left links")
    assert outside_file.read_text(encoding="utf-8") == "outside the temp folder\n", \
        "the removal changed a file a link in the temp folder pointed to"
    assert support.entries(outside_dir) == before, \
        f"the removal went through a link into {outside_dir}: {support.entries(outside_dir)} is left of {before}"
    assert (outside_dir / "deep" / "kept.txt").read_text(encoding="utf-8") == "kept\n"
    assert in_project.read_text(encoding="utf-8") == notes, "the removal changed a project file through a link"
    assert w46.check_support.porcelain(launch_project, "docs", "src") == "", \
        "the removal changed the project through a link"


def test_nothing_else_in_the_temp_directory_is_removed(launch, cli, sandbox):
    """The folder of another session that still runs, and a file of somebody else's, stay."""
    other = sandbox.tmpdir / f"gov-launch-{support.ENGINEER}-of-another-session"
    (other / "work").mkdir(parents=True)
    (other / "work" / "running.txt").write_text("another session's\n", encoding="utf-8")
    (sandbox.tmpdir / "somebody-elses.txt").write_text("not the launcher's\n", encoding="utf-8")
    before, inside = _listing(sandbox), support.entries(other)
    support.plan(cli, files=LEFT)
    result = launch(support.ENGINEER)
    folder = support.temp_folder(result)
    assert folder != other
    support.assert_removed(folder, "after the session ended")
    assert _listing(sandbox) == before, (
        f"the launch changed its temp directory beyond its own folder: {before} before, {_listing(sandbox)} after"
    )
    assert support.entries(other) == inside, "the launch removed files of another session's folder"


# --------------------------------------------------------------------------
# The launcher is interrupted
# --------------------------------------------------------------------------

@pytest.mark.parametrize("target", ("group", "launcher"))
def test_the_temp_folder_is_removed_when_the_launcher_is_interrupted(launch_project, sandbox, cli, target):
    """SIGINT while the session runs. The launcher's exit code after an interrupt is not decided, and not asserted."""
    before = _listing(sandbox)
    folder, _ = support.interrupted_launch(launch_project, sandbox, cli, support.ENGINEER, support.ENGINEER_TICKET,
                                           target)
    support.assert_removed(folder, f"after SIGINT to the {target}")
    assert _listing(sandbox) == before, f"after SIGINT the temp directory holds {_listing(sandbox)}, not {before}"


# --------------------------------------------------------------------------
# No session, no folder
# --------------------------------------------------------------------------

def _unknown_ticket(launch, project):
    return launch(support.ENGINEER, "DAEO-zz00")


def _closed_ticket(launch, project):
    return launch(support.ENGINEER, w46.write_ticket(project, "DAEO-zz98", support.ENGINEER, status="closed"))


def _bypass(launch, project):
    return launch(support.ENGINEER, None, "--dangerously-skip-permissions")


def _unwired(launch, project):
    w46.rewrite_settings(project, lambda data: data.pop("hooks", None))
    return launch(support.ENGINEER)


def _not_a_role(launch, project):
    return launch("no-such-role")


REFUSALS = {"unknown-ticket": _unknown_ticket, "closed-ticket": _closed_ticket, "bypass-flag": _bypass,
            "unwired-guard": _unwired, "not-a-role": _not_a_role}


@pytest.mark.parametrize("name", sorted(REFUSALS))
def test_a_refused_launch_leaves_no_temp_folder(launch, launch_project, cli, sandbox, name):
    """The control first: a session of this project runs and its folder goes. Then the refusal adds nothing."""
    support.plan(cli, files=LEFT)
    support.assert_removed(support.temp_folder(launch(support.ENGINEER)), "after the session ended")
    before = _listing(sandbox)
    result = REFUSALS[name](launch, launch_project)
    assert result.run.returncode != 0 and not result.sessions, f"gov launch did not refuse\n{result.describe()}"
    assert _listing(sandbox) == before, (
        f"a refused launch left something in the temp directory: {sorted(set(_listing(sandbox)) - set(before))}"
    )


def test_a_cli_that_cannot_be_started_leaves_no_temp_folder(launch, cli, sandbox):
    """The file is at ``~/.local/bin/claude`` and cannot be executed: no session starts, so no folder stays."""
    cli.path.chmod(0o644)
    before = _listing(sandbox)
    result = launch(support.ENGINEER)
    assert result.run.returncode != 0, f"gov launch ended with exit code 0 and started nothing\n{result.describe()}"
    assert not result.sessions and not result.bare, f"a CLI was started\n{result.describe()}"
    assert _listing(sandbox) == before, (
        f"a launch that started no session left a temp folder: {sorted(set(_listing(sandbox)) - set(before))}"
    )
