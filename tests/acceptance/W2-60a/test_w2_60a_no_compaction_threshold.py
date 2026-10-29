"""W2-60a, KPI success 5 -- no launch sets a compaction threshold.

KPI success 5 [DEC-838 items 1 and 2]: "No launch sets a compaction threshold:
no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the
settings or the session's environment, one given after -- refused; the launch
record states the threshold as none". KPI failure 1: "A launch that starts
with ... a compaction threshold".

The routes (Behaviour 6): the launcher's line and settings carry none; after
``--``, ``--autocompact <v>`` and ``--autocompact=<v>`` are refused; the
repository's ``.claude/settings.json`` or ``.claude/settings.local.json`` whose
``env`` holds ``CLAUDE_CODE_AUTO_COMPACT_WINDOW`` refuses the launch (the CLI
would apply it). The test home's user settings set both a threshold variable
and an ``autoCompactWindow`` key: the line keeps the user settings out
(``--setting-sources project,local``, ``test_w2_60a_kept_out.py``).

Two cases go past the design's Behaviour 6 (README, "Beyond the design"):

- the process environment's copy (a parent's ``CLAUDE_CODE_AUTO_COMPACT_WINDOW``)
  is W2-56's cleaned environment; the case is green only once W2-56 has merged;
- the repository's settings key ``autoCompactWindow`` (W1-49's README names it
  as a route that sets the window) is not in the design: KPI failure 1's "a
  compaction threshold" covers it, so it is written, and its red is the
  lead's to decide (package P-TD-W2-60a-1).
"""

from __future__ import annotations

import pytest

import w2_60a_support as s

VARIABLE = "CLAUDE_CODE_AUTO_COMPACT_WINDOW"


def test_no_launch_sets_a_compaction_threshold(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert s.occurrences(result.args, "--autocompact") == 0, f"the line sets a compaction threshold: {result.args}"
    assert VARIABLE not in result.env_block(), f"the settings' env sets {VARIABLE}: {result.env_block()}"
    assert "autoCompactWindow" not in result.settings(), "the settings set autoCompactWindow"
    assert result.record().get("compaction_threshold") == "none", (
        f"the record does not state the threshold as none: {result.record().get('compaction_threshold')!r}")


@pytest.mark.parametrize("passed", (("--autocompact", "300000"), ("--autocompact=300000",)),
                         ids=("spaced", "joined"))
def test_a_compaction_threshold_after_the_double_dash_is_refused(launch, passed):
    s.assert_refused(launch(s.ENGINEER, None, "-p", "Do the work.", *passed),
                     "LAUNCH_REFUSED", "the CLI arguments carry", "--autocompact")


@pytest.mark.parametrize("rel", (s.SETTINGS_REL, s.LOCAL_SETTINGS_REL), ids=("committed", "local"))
def test_a_compaction_threshold_in_the_repository_s_settings_is_refused(project, launch, rel):
    s.rewrite_settings(project, lambda data: data.setdefault("env", {}).update({VARIABLE: "300000"}), rel)
    s.assert_refused(launch(s.ENGINEER), VARIABLE)


def test_a_compaction_threshold_in_the_caller_s_environment_does_not_reach_the_session(launch):
    """Green only once W2-56 has merged: the session's process environment is W2-56's cleaned one (B, two edges)."""
    result = launch(s.ENGINEER, extra_env={VARIABLE: "300000"})
    s.assert_launched(result)
    assert VARIABLE not in result.session()["env"], (
        f"the caller's {VARIABLE} reached the session's process environment (W2-56's cleaned environment)")


@pytest.mark.parametrize("rel", (s.SETTINGS_REL, s.LOCAL_SETTINGS_REL), ids=("committed", "local"))
def test_an_auto_compact_window_key_in_the_repository_s_settings_is_refused(project, launch, rel):
    """Beyond the design's Behaviour 6 (P-TD-W2-60a-1): the settings key sets the window as the variable does."""
    s.rewrite_settings(project, lambda data: data.update({"autoCompactWindow": 300000}), rel)
    s.assert_refused(launch(s.ENGINEER), "autoCompactWindow")
