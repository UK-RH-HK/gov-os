"""KPI success 1 [CAP-05.a] and both failure lines; "a plain pause writes no record" of KPI success 3 [CAP-05.d].

"gov pause sets the freeze flag; gov pause --off clears it." Failure: "The flag
lives outside the repository runtime directory".

The flag is the file ``.gov-runtime/freeze`` of the project (DEC-109).

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. The cases that asked the guard
whether a write is denied while paused are deleted with the guard; the flag cases stay.

Every pause and every ``--off`` here is the owner's: a call with no
``GOV_ROLE`` (DEC-365).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w1_28_support as support

cli_support = support.cli_support


def test_pause_sets_the_flag_in_the_runtime_directory(project, pause, interface):
    assert not support.is_paused(project), "the fixture project starts frozen"
    support.succeeded(pause(), interface)
    flag = support.flag(project)
    assert flag.is_file() and not flag.is_symlink(), f"gov pause did not create the file {support.FREEZE_FLAG_REL}"


def test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else(project, sandbox, pause,
                                                                                 interface):
    """Failure 2. The command runs from another directory: the flag follows ``--root``, not the caller.

    A plain pause writes nothing but the flag and the freeze mirror (DEC-429): the ticket files are compared
    too (DEC-367).
    """
    skip = (".git", support.RUNTIME_REL)
    before = {"project": cli_support.snapshot(project, skip=skip),
              "home": cli_support.snapshot(sandbox.home, skip=()),
              "elsewhere": cli_support.snapshot(sandbox.elsewhere, skip=())}
    run = pause(cwd=sandbox.elsewhere)
    support.succeeded(run, interface)

    flag = support.flag(project)
    assert flag.is_file(), f"the flag is not {support.FREEZE_FLAG_REL} of the project\n{run.describe()}"
    runtime = os.path.realpath(Path(project) / support.RUNTIME_REL)
    assert os.path.realpath(flag) == os.path.join(runtime, "freeze"), \
        f"the flag resolves outside the project's runtime directory: {os.path.realpath(flag)}"
    after = {"project": cli_support.snapshot(project, skip=skip),
             "home": cli_support.snapshot(sandbox.home, skip=()),
             "elsewhere": cli_support.snapshot(sandbox.elsewhere, skip=())}
    for place in ("project", "elsewhere"):
        changed = cli_support.snapshot_difference(before[place], after[place])
        assert not changed, f"gov pause wrote outside {support.RUNTIME_REL}/ ({place}): {changed}\n{run.describe()}"
    # DEC-429: gov pause writes a freeze mirror under ~/.local/state/gov-os/<key>/freeze.
    home_changed = cli_support.snapshot_difference(before["home"], after["home"])
    non_mirror = [d for d in home_changed if not cli_support.is_freeze_mirror_entry(d)]
    assert not non_mirror, \
        f"gov pause wrote to home outside .local/state/gov-os/: {non_mirror}\n{run.describe()}"
    assert any("/freeze" in d for d in home_changed), \
        f"gov pause did not create the freeze mirror (DEC-429)\n{run.describe()}"


def test_the_flag_is_not_seen_by_git(paused):
    """The runtime directory is derived state, ignored by git: a pause adds no flag to ``git status``."""
    assert support.FREEZE_FLAG_REL not in support.porcelain(paused), support.porcelain(paused)
    assert support.RUNTIME_REL + "/" not in support.porcelain(paused), support.porcelain(paused)


def test_a_plain_pause_writes_no_record(project, pause, interface, claims):
    """DEC-367: no commit and no change to a ticket file, even with claims held. The claims stay held."""
    before, tickets = support.head(project), support.ticket_files(project)
    support.succeeded(pause(), interface)
    assert support.head(project) == before, "a plain gov pause made a commit"
    assert support.ticket_files(project) == tickets, "a plain gov pause changed a ticket file"
    assert support.porcelain(project) == "", f"a plain gov pause left changes:\n{support.porcelain(project)}"
    assert support.locks(project) == sorted(claims), "a plain gov pause released a claim"
