"""W1-46 -- the research session's write fence inside the repository: the generated ``Edit`` deny list.

KPI success 4 [CAP-61.c]: "the launcher generates at launch an Edit deny rule for
every other path of the repository, from its top-level entries and the siblings
along the path to the folder; the deny list is computed at launch, from the
paths that exist then, with two exceptions: .git/, so that the session can
commit its evidence record, and an entry whose name contains *, ? or [, which
the sandbox skips on Linux (EXP-001 §1); a path created after launch outside the
experiment folder is not in the list and is covered by the guard's per-ticket
allow-list ... the generated list leaves out exactly the named exceptions".
KPI failure 4: "A research session ... writes to a path that existed at launch
outside its experiment folder".

The experiment folder is the research ticket's ``allowed_paths``
(``experiments/spikes/exp-901/**``): two levels of siblings lie along the path
to it. The rules are read by what they cover, not by their spelling: a rule on
a directory holds for everything under it.

No session is started.
"""

from __future__ import annotations

import os

import pytest

import w1_46_support as support

GLOB_NAMED = ("odd[1].txt", "what?.txt", "star*.txt", "experiments/spikes/exp-[0-9]")
FOLDER = support.EXPERIMENT_REL


def _a_file_under(project, rel):
    """``rel`` itself when it is a file; otherwise the first file under it, or the directory."""
    path = project / rel
    if not path.is_dir():
        return rel
    for folder, dirs, files in os.walk(path):
        dirs.sort()
        if files:
            return os.path.relpath(os.path.join(folder, sorted(files)[0]), project)
    return rel


def _other_paths(project):
    """Every entry that exists at launch beside the path to the experiment folder, without the named exceptions.

    ``.gov-runtime`` is left to its own rule (DEC-180), which excepts
    ``scratch/``; see ``test_w1_46_role_settings.py``.
    """
    found, here = [], ""
    for part in FOLDER.split("/"):
        for name in sorted(os.listdir(project / here)):
            if name == part or support.has_glob_character(name) or (here == "" and name in (".git", ".gov-runtime")):
                continue
            found.append(os.path.join(here, name))
        here = os.path.join(here, part)
    return found


def test_every_other_path_that_exists_at_launch_is_denied(launch, project, sandbox):
    """Top-level entries and the siblings along the path, files and directories alike."""
    others = _other_paths(project)
    assert {"src", "README.md", ".tickets", "experiments/notes.md", "experiments/archive",
            "experiments/spikes/exp-900"} <= set(others), "the fixture project lost its other paths"
    result = launch(support.RESEARCH)
    open_paths = [rel for rel in others
                  if not (support.edit_denied(result, rel, project, sandbox)
                          and support.edit_denied(result, _a_file_under(project, rel), project, sandbox))]
    assert open_paths == [], f"the generated deny list leaves these paths open to a research session: {open_paths}"


def test_the_experiment_folder_stays_writable(launch, project, sandbox):
    result = launch(support.RESEARCH)
    closed = [rel for rel in (f"{FOLDER}/README.md", f"{FOLDER}/.venv/bin/python", f"{FOLDER}/results/run-1.json")
              if support.edit_denied(result, rel, project, sandbox)]
    assert closed == [], f"the generated deny list covers the experiment folder itself: {closed}"


def test_git_is_left_out_of_the_list(launch, project, sandbox):
    """ ".git/, so that the session can commit its evidence record"."""
    result = launch(support.RESEARCH)
    closed = [rel for rel in (".git", ".git/index", ".git/objects/ab/cdef", ".git/COMMIT_EDITMSG")
              if support.edit_denied(result, rel, project, sandbox)]
    assert closed == [], f"the generated deny list covers {closed}"


def test_an_entry_with_a_glob_character_in_its_name_is_left_out_of_the_list(launch, project, sandbox):
    """ "An entry whose name contains *, ? or [, which the sandbox skips on Linux": no rule is built from one.

    The entries exist at launch, at the top level and beside the experiment
    folder. Their neighbours are still denied.
    """
    for rel in GLOB_NAMED:
        support.write(project, f"{rel}/inside.txt" if rel.endswith("]") else rel, "glob-named\n")
    support.check_support.commit_all(project, "entries with glob characters in their names")
    result = launch(support.RESEARCH)
    specs = support.deny_rules(result.settings(), "Edit")
    named = [name for name in (os.path.basename(rel) for rel in GLOB_NAMED) if any(name in spec for spec in specs)]
    assert named == [], f"the generated deny list has a rule built from {named}"
    assert support.edit_denied(result, "README.md", project, sandbox), "the list no longer covers README.md"
    assert support.edit_denied(result, "experiments/spikes/exp-900/data.txt", project, sandbox), (
        "the list no longer covers the sibling experiment"
    )


def test_a_path_that_does_not_exist_at_launch_is_not_in_the_list(launch, project, sandbox):
    """ "Computed at launch, from the paths that exist then": a later path is the guard's and the containment check's."""
    result = launch(support.RESEARCH)
    listed = [rel for rel in ("created-after-launch/new.txt", "created-after-launch.txt",
                              "experiments/spikes/exp-902/new.txt")
              if support.edit_denied(result, rel, project, sandbox)]
    assert listed == [], f"the deny list covers paths that do not exist at launch: {listed}"


def test_a_path_that_exists_at_the_next_launch_is_in_that_launchs_list(launch, project, sandbox):
    """The list is computed at each launch, not kept from an earlier one or from a committed file."""
    before = launch(support.RESEARCH)
    assert not support.edit_denied(before, "created-after-launch/new.txt", project, sandbox)
    support.write(project, "created-after-launch/new.txt", "x\n")
    support.write(project, "experiments/spikes/exp-902/new.txt", "x\n")
    after = launch(support.RESEARCH)
    open_paths = [rel for rel in ("created-after-launch/new.txt", "experiments/spikes/exp-902/new.txt")
                  if not support.edit_denied(after, rel, project, sandbox)]
    assert open_paths == [], f"paths that exist at the second launch are not in its deny list: {open_paths}"


@pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
def test_the_other_roles_are_not_fenced_out_of_their_tickets_paths(launch, project, sandbox, role):
    """The generated fence is the research role's; another role's settings do not deny its own ticket's paths."""
    result = launch(role)
    assert not support.edit_denied(result, support.OWN_PATH[role], project, sandbox), (
        f"the built settings deny a launched {role} a path of its own ticket: {support.OWN_PATH[role]}"
    )


# --------------------------------------------------------------------------
# A path created after launch: the guard's per-ticket allow-list
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_the_guard_refuses_a_research_write_to_a_new_path_outside_the_folder(guard, project, tool):
    """KPI success 4, failure 5: "refused by the guard". Holds before implementation: the role is unknown to it."""
    for rel in ("created-after-launch/new.txt", "experiments/spikes/exp-902/new.txt"):
        result = guard(tool, support.w47.write_input(tool, project / rel), support.RESEARCH)
        support.w47.assert_stopped(result, f"{tool} to the new path {rel} by research")


def test_the_guard_refuses_a_research_bash_write_to_a_new_path_outside_the_folder(guard, project):
    for command in ("mkdir created-after-launch", "echo x > created-after-launch.txt",
                    "cp README.md experiments/spikes/exp-902.txt"):
        result = guard("Bash", support.w47.bash_input(command), support.RESEARCH)
        support.w47.assert_stopped(result, f"`{command}` by research")
