"""F2: a refusal the launcher makes today no longer refuses (the refusals other than the CLI arguments').

Each case changes one thing in a fresh fixture project and launches a worker: the launch exits non-zero with
``LAUNCH_REFUSED``, starts no session and leaves no temp folder. The premise case launches the unchanged project.

Emergency 2 (release 0.1.2, EMERGENCY-2 2.1-2.3): the refusals about the guard, the sandbox, the no-prompt mode,
added directories, the held-out file, the evaluation sets and the research fence are no longer made, and their cases
are retired.
"""

from __future__ import annotations

import json

import pytest

import w2_56_support as s

# (id, the project's changed files, the role, the ticket id)
CASES = (
    ("unknown-ticket", {}, s.ENGINEER, "DAEO-none"),
    ("ticket-not-in-progress", {}, s.ENGINEER, s.CLOSED.tk),
    ("ticket-of-another-role", {}, s.ENGINEER, s.SPEC.tk),
    ("not-a-worker-role", {}, "janitor", s.T.tk),
    ("local-settings-unreadable", {".claude/settings.local.json": "{not json\n"}, s.ENGINEER, s.T.tk),
    ("integration-store-relative", {"governance/project/rebuild.yaml": "integration_store: relative/store\n"},
     s.ENGINEER, s.T.tk),
)


def _project(tmp_path, changes):
    box = s.make_box(tmp_path)
    project = s.make_project(box)
    for rel, text in changes.items():  # after the commit: the launcher reads the working tree
        if text is None:
            (project / rel).unlink()
        else:
            s.write(project / rel, text)
    s.install_stand_in_cli(box)
    s.set_plan(box)
    return box


def _assert_refused(box, launch):
    assert launch.returncode != 0, f"the launch was not refused\n{launch.describe()}"
    assert not launch.calls, f"the refused launch started a session\n{launch.describe()}"
    assert "LAUNCH_REFUSED" in launch.output, f"the refusal does not say LAUNCH_REFUSED\n{launch.describe()}"
    left = [entry for entry in s.temp_folders(box) if entry.startswith(s.TEMP_PREFIX)]
    assert not left, f"the refused launch left temp folders {left}"


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_f2_premise_the_unchanged_project_starts_every_worker_role(tmp_path, role):
    box = _project(tmp_path, {})
    launch = s.run_launch(box, role, s.TICKET_OF[role].tk)
    assert launch.returncode == 0 and launch.started, f"the fixture project does not launch\n{launch.describe()}"


@pytest.mark.parametrize("case", CASES, ids=[case[0] for case in CASES])
def test_f2_todays_refusal_still_refuses(tmp_path, case):
    _, changes, role, ticket = case
    box = _project(tmp_path, changes)
    _assert_refused(box, s.run_launch(box, role, ticket))


def test_f2_a_missing_cli_still_refuses(tmp_path):
    box = _project(tmp_path, {})
    box.cli.unlink()
    _assert_refused(box, s.run_launch(box, s.ENGINEER, s.T.tk))


def test_f2_a_cli_that_cannot_be_started_still_refuses_and_leaves_no_temp_folder(tmp_path):
    box = _project(tmp_path, {})
    box.cli.chmod(0o644)
    _assert_refused(box, s.run_launch(box, s.ENGINEER, s.T.tk))
