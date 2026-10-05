"""KPI success 2: "Pause state appears in gov status".

**These two cases follow decision package DP-1, option (b), and cannot pass
from this ticket's paths.** ``gov status`` is ``src/gov/cli/commands/status.py``
(W1-07), outside ``src/gov/pause/**``, and today its result is ``root`` and
``config_files``: nothing about the flag. The KPI line is tested as written,
on ``gov status --json``, so that the gap is red and visible; under option (a)
this file moves to W1-32's suite as it is.

The shape is not decided either. The cases ask the least: somewhere in
``result`` a key whose name contains ``pause`` holds the pause state, it
differs between a paused project and one that is not, and it returns to its
first value after ``gov pause --off``.
"""

from __future__ import annotations

import re

import w1_28_support as support


def _pause_state(project, sandbox, interface):
    """``{key path: value}`` of every key of ``gov status --json`` whose name contains "pause"."""
    run = support.gov(project, sandbox, "status", "--json")
    envelope = support.cli_support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True, run.describe()
    found = {}

    def walk(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                where = f"{path}.{key}" if path else key
                if re.search("pause", key, re.IGNORECASE):
                    found[where] = item
                else:
                    walk(item, where)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(envelope["result"], "")
    assert found, f"gov status --json reports no pause state: no key names it\n{run.describe()}"
    return found


def test_gov_status_shows_a_paused_project_as_paused(project, sandbox, pause, interface):
    before = _pause_state(project, sandbox, interface)
    support.succeeded(pause(), interface)
    after = _pause_state(project, sandbox, interface)
    assert after != before, f"gov status reports the same pause state before and after gov pause: {after}"


def test_gov_status_shows_the_pause_lifted(project, sandbox, pause, interface):
    before = _pause_state(project, sandbox, interface)
    support.succeeded(pause(), interface)
    support.succeeded(pause("--off"), interface)
    after = _pause_state(project, sandbox, interface)
    assert after == before, f"after gov pause --off, gov status still differs: {before} -> {after}"
