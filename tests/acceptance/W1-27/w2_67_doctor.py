"""Reading ``gov doctor``'s structured result (W2-67's revisions of W1-27's weak cases, I4 F1).

Doctor prints every section on every run. A healthy run puts them in ``result``; an unhealthy one exits 3 with
``DOCTOR_UNHEALTHY`` and puts the same sections in ``error.details`` (``result`` is then ``{}``). A revised case
reads the value of the section it claims, wherever doctor put it, never a key name or a word of the output.
"""

from __future__ import annotations

import functools

import w1_27_support as support

LEVELS = ("MINIMAL", "INTERMEDIATE", "ADOPTED_HEALTHY")   # lowest first (CAP-54.a)


@functools.cache
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``, read from this worktree."""
    return support.base.load_interface(support.REPO_ROOT)


def sections(run):
    """The doctor sections of a run: ``result`` when healthy, else ``error.details``."""
    envelope = support.assert_envelope(run, interface(), command="doctor")
    if envelope.get("ok") is True:
        found = envelope.get("result")
    else:
        error = envelope.get("error") or {}
        assert error.get("code") == "DOCTOR_UNHEALTHY", f"doctor did not run its checks\n{run.describe()}"
        found = error.get("details")
    assert isinstance(found, dict) and found, f"doctor gave no sections\n{run.describe()}"
    return found


def section(run, name):
    """One section, which must be there and be measured (a dict with a status)."""
    found = sections(run).get(name)
    assert isinstance(found, dict) and "status" in found, f"doctor has no {name} section\n{run.describe()}"
    return found


def small_project(destination):
    """A small committed project of a case's own (a minimal path map), instead of a copy of the whole tree."""
    project = destination
    project.mkdir(parents=True)
    support.git(project, "init", "-q", "-b", "main")
    support.write_path_map(project, support.minimal_valid_path_map())   # commits
    return project


def doctor(project, sandbox):
    """``gov doctor --json`` in ``project``, with this worktree's code (DEC-732)."""
    return support.run_gov_with_code(support.REPO_ROOT, project, sandbox, "doctor", "--json")
