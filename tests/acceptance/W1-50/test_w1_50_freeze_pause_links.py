"""W1-50, KPI line 1 (DEC-402), review findings on ``gov pause`` and links (DEC-136).

"A freeze flag set by gov pause carries a marker line."

**Red by design until ``gov pause`` is changed** (DEC-404). These cases do not
depend on the layout of the marker line: they ask only what is at the flag's
path after the command, and whether the guard then denies the next write.

- **A link at the flag's path before the pause** (to ``/dev/null``, to another
  file, to nothing). A pause is a real one: it succeeds and leaves, at the
  flag's path of the project, a regular file that is not a link and that the
  guard reads as a freeze. It never writes through the link: the link's target
  is unchanged, or not created.
- **``.gov-runtime`` itself is a symbolic link** (to a folder elsewhere, or to
  nothing). DEC-404, on package DP-F4 option (a): the command refuses with an
  error that names the link and writes nothing; the owner repairs the folder.
  So: an error in the command's envelope whose message names
  ``.gov-runtime``, no "paused", nothing new where the link points, no flag,
  and the link left as it was. The error's code is pinned by no decision and
  is not tested.
- **No temporary file stays beside the flag.** DEC-404: the flag is written
  by a temporary file and a rename. After a pause the only new name in
  ``.gov-runtime/`` is the flag's.
- **``gov pause --off`` with a directory at the flag's path**: a refusal in the
  command's envelope, and the tree stays frozen.

``gov pause`` is run as W1-28's suite runs it, on a temporary project only.
The readings and their sources are in ``w1_50_freeze_README.md``.
"""

from __future__ import annotations

import json
import os

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import (  # noqa: F401  fixtures
    freeze_interface, freeze_pause, freeze_project, freeze_sandbox)

pause_support = support.pause_support
OTHER_TEXT = b"another file, not a flag\n"


# --------------------------------------------------------------------------
# A link at the flag's path
# --------------------------------------------------------------------------

def _to_dev_null(sandbox):
    return "/dev/null", None


def _to_another_file(sandbox):
    target = sandbox.elsewhere / "another-file.txt"
    target.write_bytes(OTHER_TEXT)
    return target, OTHER_TEXT


def _to_nothing(sandbox):
    return sandbox.elsewhere / "no-such-file", None


LINKS = {
    "a-link-to-dev-null": _to_dev_null,
    "a-link-to-another-file": _to_another_file,
    "a-dangling-link": _to_nothing,
}


# --------------------------------------------------------------------------
# The runtime folder is a symbolic link
# --------------------------------------------------------------------------

@pytest.mark.parametrize("points_to", ("a-folder-elsewhere", "nothing"))
def test_pause_refuses_when_the_runtime_folder_is_a_link(freeze_project, freeze_sandbox, freeze_pause,
                                                         freeze_interface, points_to):
    """DEC-404 (DP-F4, option a): an error that names the link, and nothing written. The owner repairs the folder."""
    runtime = freeze_project / support.RUNTIME_REL
    assert not os.path.lexists(runtime), "the fixture project starts with a runtime folder"
    elsewhere = freeze_sandbox.elsewhere / "a-runtime-folder-elsewhere"
    if points_to == "a-folder-elsewhere":
        elsewhere.mkdir()
    runtime.symlink_to(elsewhere, target_is_directory=True)
    what = f"with {support.RUNTIME_REL} a symbolic link to {points_to}"

    run = freeze_pause()

    # Nothing is written, whatever the command then says.
    if points_to == "a-folder-elsewhere":
        written = sorted(os.listdir(elsewhere))
        assert written == [], f"{what}, gov pause wrote outside the project: {elsewhere} now holds {written}"
    else:
        assert not os.path.lexists(elsewhere), f"{what}, gov pause created the link's target, {elsewhere}"
    assert runtime.is_symlink() and os.readlink(runtime) == str(elsewhere), \
        f"{what}, gov pause did not leave the link as it was"
    assert not os.path.lexists(support.flag(freeze_project)), f"{what}, gov pause left something at {support.FLAG_REL}"
    # The refusal: an error of the command, in the envelope, that names the link. Its code is not pinned.
    error = pause_support.failed(run, freeze_interface)
    assert support.RUNTIME_REL in error["message"], \
        f"{what}, the refusal's message does not name the link {support.RUNTIME_REL}: {error}"
    result = run.envelope().get("result")
    assert not (isinstance(result, dict) and result.get("paused")), \
        f"{what}, gov pause ended with an error and reports paused: {result}"


# --------------------------------------------------------------------------
# No temporary file stays beside the flag
# --------------------------------------------------------------------------

def test_a_pause_leaves_no_other_name_beside_the_flag(freeze_project, freeze_sandbox, freeze_pause,
                                                      freeze_interface):
    """DEC-404: a temporary file and a rename. Over the sandbox's placeholder, the only name there is the flag's."""
    support.put_placeholder(freeze_project)
    runtime = freeze_project / support.RUNTIME_REL
    before = set(os.listdir(runtime))

    pause_support.succeeded(freeze_pause(), freeze_interface)

    new = sorted(set(os.listdir(runtime)) - before)
    assert new == [], f"after gov pause, {support.RUNTIME_REL}/ holds names it did not hold before: {new}"
    assert support.flag(freeze_project).is_file() and not support.flag(freeze_project).is_symlink(), \
        f"after gov pause, {support.FLAG_REL} is not a regular file"


# --------------------------------------------------------------------------
# Lifting a pause when a directory is at the flag's path
# --------------------------------------------------------------------------

