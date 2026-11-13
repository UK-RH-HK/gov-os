"""F2: a refusal the launcher makes today no longer refuses (the refusals other than the CLI arguments').

Each case changes one thing in a fresh fixture project and launches a worker: the launch exits non-zero with
``LAUNCH_REFUSED``, starts no session and leaves no temp folder. The premise case launches the unchanged project.

Left for after the experiment (DEC-1099 (1)): the two refusals about the sandbox block itself (a repository
settings file carrying a ``sandbox`` key, DEC-233; built settings that are not strict, ``sandbox_faults``),
since set-up A may launch with no sandbox block.
"""

from __future__ import annotations

import json

import pytest

import w2_56_support as s

RESEARCH_OUTSIDE = s.Ticket("DAEO-zw62", s.RESEARCH, "W2-83", ("docs/outside/**",))
RESEARCH_TWO = s.Ticket("DAEO-zw63", s.RESEARCH, "W2-84", ("experiments/spikes/one/**", "experiments/spikes/two/**"))

# (id, the project's changed files, the role, the ticket id)
CASES = (
    ("unknown-ticket", {}, s.ENGINEER, "DAEO-none"),
    ("ticket-not-in-progress", {}, s.ENGINEER, s.CLOSED.tk),
    ("ticket-of-another-role", {}, s.ENGINEER, s.SPEC.tk),
    ("not-a-worker-role", {}, "janitor", s.T.tk),
    ("settings-disable-all-hooks", {".claude/settings.json": s.settings_text(disableAllHooks=True)},
     s.ENGINEER, s.T.tk),
    ("settings-bypass-mode", {".claude/settings.json": s.settings_text(
        permissions={"defaultMode": "bypassPermissions"})}, s.ENGINEER, s.T.tk),
    ("settings-additional-directories", {".claude/settings.json": s.settings_text(
        permissions={"additionalDirectories": ["/tmp"]})}, s.ENGINEER, s.T.tk),
    ("settings-guard-not-wired", {".claude/settings.json": json.dumps({"hooks": {}}) + "\n"}, s.ENGINEER, s.T.tk),
    ("local-settings-unreadable", {".claude/settings.local.json": "{not json\n"}, s.ENGINEER, s.T.tk),
    ("local-settings-bypass-mode", {".claude/settings.local.json": json.dumps(
        {"permissions": {"defaultMode": "bypassPermissions"}}) + "\n"}, s.ENGINEER, s.T.tk),
    ("held-out-not-a-list", {"governance/project/held-out.yaml": "held_out_paths: not-a-list\n"},
     s.ENGINEER, s.T.tk),
    ("held-out-relative-entry", {"governance/project/held-out.yaml": "held_out_paths:\n  - relative/path\n"},
     s.ENGINEER, s.T.tk),
    ("evaluation-set-malformed", {"governance/project/path-map.yaml": (
        "namespaces: {}\nevaluation_sets:\n  m:\n    visible: [a]\n    measures: {roles: [research]}\n")},
     s.AUDITOR, s.T.tk),
    ("integration-store-relative", {"governance/project/rebuild.yaml": "integration_store: relative/store\n"},
     s.ENGINEER, s.T.tk),
    ("research-allowlist-missing", {s.ALLOWLIST_REL: None}, s.RESEARCH, s.EXPERIMENT.tk),
    ("research-allowlist-malformed", {s.ALLOWLIST_REL: "hosts: [\"not a host\"]\n"}, s.RESEARCH, s.EXPERIMENT.tk),
    ("research-folder-outside-experiments", {f".tickets/{RESEARCH_OUTSIDE.tk}.md": s.ticket_text(RESEARCH_OUTSIDE)},
     s.RESEARCH, RESEARCH_OUTSIDE.tk),
    ("research-two-folders", {f".tickets/{RESEARCH_TWO.tk}.md": s.ticket_text(RESEARCH_TWO)},
     s.RESEARCH, RESEARCH_TWO.tk),
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
