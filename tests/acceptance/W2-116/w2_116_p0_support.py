"""Support code for the phase-0 fix P0-1 of W2-116 (DAEO-f58b): the refresh retried and checked.

Public interfaces only: ``gov rebuild --integration <branch> --when-due`` (the cron tick, its stdout and stderr appended
to a log file the test owns, as a cron line ``>> log 2>&1`` does), ``gov status`` (text and ``--json``, the part
``integration_store``), ``gov retrieve`` and ``gov brief``. A failed refresh is planted by pointing the build's embedder
at an address where nothing listens (``w2_116_support.closed_host``); no real embedder runs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import w2_116_s2_support as s2
import w2_116_support as support
from w2_116_s2_support import DAY1, at

W2_197 = Path(__file__).resolve().parents[1] / "W2-197"
BEHIND_SENTENCE = "store behind HEAD"


def broken(env):
    """The environment with the build's embedder gone: a refresh built under it fails (``REBUILD_FAILED``)."""
    return {**env, "OLLAMA_HOST": support.closed_host()}


class Cron:
    """The tick as a cron line runs it: ``gov rebuild --integration <branch> --when-due``, output appended to ``log``."""

    def __init__(self, box, project, env):
        self.box, self.project, self.env = box, project, env
        self.log = box.base / "cron.log"

    def tick(self, now, env=None):
        run = support.gov(self.project, s2.now_env(env or self.env, now), "rebuild", support.INTEGRATION,
                          support.BRANCH, "--when-due")
        with open(self.log, "a", encoding="utf-8") as handle:
            handle.write(run.stdout + run.stderr)
        return run

    def text(self):
        return self.log.read_text(encoding="utf-8") if self.log.is_file() else ""


def built_store(box, env, project):
    """A store built at the branch's head with a refresh recorded at 18:05 (so no time makes the next tick due)."""
    s2.plant_config(box, project)    # latest 10:00, second 18:00
    s2.first_refresh(box, env, project, at(DAY1, "18:05"))
    return support.head(project)


def commits_between(project, old, new):
    return int(support.git(project, "rev-list", "--count", f"{old}..{new}").strip())


def status_run(project, env, *extra):
    return support.gov(project, env, "status", *extra)


def part_of(run):
    """``result.integration_store`` of ``gov status --json``, whatever the exit code (a red status may exit non-zero)."""
    value = run.result.get("integration_store")
    assert isinstance(value, dict), f"no integration_store part in the status\n{run.describe(800)}"
    return value


def red_flag(run):
    """The JSON's ``red`` key: at the top of the result, else at the top of the envelope."""
    for holder in (run.result, run.envelope()):
        if "red" in holder:
            return holder["red"]
    raise AssertionError(f"`gov status --json` has no top-level `red` key\n{run.describe(800)}")


def sentence(n):
    return f"{BEHIND_SENTENCE} by {n} commit(s)"


def one_line_each(text, *needles):
    return [needle for needle in needles if needle not in text]


# --- a repository for gov brief: the kernel templates, the facts file, one READY ticket ------------------------------------

def brief_ready(project):
    """The project made ready for ``gov brief`` (W2-197's BriefRepo: this tree's templates and facts file and the READY
    ticket DAEO-fx01), committed. Never changes a file this module did not add."""
    if str(W2_197) not in sys.path:
        sys.path.insert(0, str(W2_197))
    import w2_197_support as b197

    b197.BriefRepo(Path(project))
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "P0-1: the brief's templates, facts and READY ticket")
    return b197


def brief(project, env, b197):
    """``gov brief engineer <ticket> --store <project>``: stdout (the brief) and stderr (its warnings) joined."""
    run = support.gov(project, env, "brief", "engineer", b197.TICKET_ID, "--store", str(project),
                      timeout=support.WAIT_S)
    return run, run.stdout + "\n" + run.stderr
