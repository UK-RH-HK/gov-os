"""W1-47 -- the time limit of the guard's hook entries in the kernel template's settings (DEC-580).

DEC-580: "The kernel template's settings carry ``"timeout": 60`` on every guard
hook entry, so that every adopted project gets it." Why: a hook that passes its
time limit lets the call through (``docs/research/EXP-hook-time-limit.md``), and
the guard's own deadline of 20 seconds has to end before the harness's limit.

The cases read ``template/governance/kernel/settings.json`` as the file it is
and walk every hook entry it registers, under every event. Nothing is run. What
the words are taken to mean is stated in ``w1_47_hook_time_limit.py`` and in the
README's section "The guard hooks' time limit".

The rest of the file (which events, which matchers, which commands) is held by
the cases that were here before: ``test_w1_47_kernel_template.py``, the template
cases of ``test_w1_47_failed_commands.py`` and of
``test_w1_47_settings_rules.py``. This file adds nothing about it.
"""

from __future__ import annotations

import copy

import pytest

import w1_47_hook_time_limit as limit
import w1_47_support as support

TEMPLATE_HOOKS_REL = f"{support.TEMPLATE_KERNEL_REL}/hooks"
GUARD_EVENTS = ("PreToolUse", "PostToolUse", "PostToolUseFailure")


@pytest.fixture(scope="module")
def programs():
    """The file names of the kernel template's hook programs."""
    return limit.program_names(support.REPO_ROOT / TEMPLATE_HOOKS_REL)


# --------------------------------------------------------------------------
# The file
# --------------------------------------------------------------------------

def test_every_guard_hook_entry_of_the_template_carries_the_time_limit(template_settings, programs):
    """DEC-580: ``"timeout": 60`` on every guard hook entry, whatever the event and the matcher group."""
    found = limit.faults(template_settings, programs)
    assert not found, (
        f"{support.TEMPLATE_SETTINGS_REL}: a guard hook entry without `\"{limit.LIMIT_KEY}\": {limit.LIMIT_S}` "
        f"(DEC-580):\n  " + "\n  ".join(found)
    )


@pytest.mark.parametrize("event", GUARD_EVENTS)
def test_the_walk_finds_the_template_s_guard_hook_entry_under_each_event(template_settings, programs, event):
    """The case above is not empty-handed: the entries the earlier cases hold are entries the walk judges."""
    found = [where for where, _group, _entry in limit.guard_entries(template_settings, programs)
             if where.startswith(f"{event}[")]
    assert found, (
        f"{support.TEMPLATE_SETTINGS_REL}: the walk finds no guard hook entry under {event}, so the time limit "
        f"would be held for nothing there"
    )


# --------------------------------------------------------------------------
# What the walk judges: the template's own registration with one thing changed, in memory
# --------------------------------------------------------------------------

def _conforming(template_settings, programs):
    """The template's settings as an object in which every guard hook entry carries the limit."""
    settings = copy.deepcopy(template_settings)
    for _where, _group, entry in limit.guard_entries(settings, programs):
        entry[limit.LIMIT_KEY] = limit.LIMIT_S
    return settings


def _first(settings, programs):
    _where, group, entry = limit.guard_entries(settings, programs)[0]
    return group, entry


def _without(settings, programs):
    del _first(settings, programs)[1][limit.LIMIT_KEY]


def _as_a_string(settings, programs):
    _first(settings, programs)[1][limit.LIMIT_KEY] = str(limit.LIMIT_S)


def _another_number(settings, programs):
    _first(settings, programs)[1][limit.LIMIT_KEY] = 30


def _zero(settings, programs):
    _first(settings, programs)[1][limit.LIMIT_KEY] = 0


def _on_the_matcher_group_only(settings, programs):
    group, entry = _first(settings, programs)
    del entry[limit.LIMIT_KEY]
    group[limit.LIMIT_KEY] = limit.LIMIT_S


def _a_second_entry_in_the_same_group(settings, programs):
    group, entry = _first(settings, programs)
    group["hooks"].append({"type": "command", "command": entry["command"]})


def _a_second_matcher_group_under_the_same_event(settings, programs):
    _group, entry = _first(settings, programs)
    event = next(iter(settings["hooks"]))
    settings["hooks"][event].append({"matcher": "Bash",
                                     "hooks": [{"type": "command", "command": entry["command"]}]})


def _an_entry_under_an_event_added_later(settings, programs):
    program = sorted(programs)[-1]
    settings["hooks"]["EventAddedAfterThisTicket"] = [
        {"hooks": [{"type": "command",
                    "command": f'python3 "${support.PROJECT_DIR_VARIABLE}/{limit.KERNEL_HOOKS_REL}/{program}"'}]}
    ]


WITHOUT_THE_LIMIT = {
    "no-limit": _without,
    "the-limit-as-a-string": _as_a_string,
    "another-number": _another_number,
    "zero": _zero,
    "on-the-matcher-group-only": _on_the_matcher_group_only,
    "a-second-entry-in-the-same-group": _a_second_entry_in_the_same_group,
    "a-second-matcher-group-under-the-same-event": _a_second_matcher_group_under_the_same_event,
    "an-entry-under-an-event-added-later": _an_entry_under_an_event_added_later,
}


@pytest.mark.parametrize("change", sorted(WITHOUT_THE_LIMIT))
def test_one_guard_hook_entry_without_the_number_is_found(template_settings, programs, change):
    """One entry that does not carry the number 60 itself is found, and no other entry is blamed for it."""
    settings = _conforming(template_settings, programs)
    assert limit.faults(settings, programs) == [], "the template's registration with the limit on every entry is faulted"
    WITHOUT_THE_LIMIT[change](settings, programs)
    found = limit.faults(settings, programs)
    assert len(found) == 1, f"{change}: one guard hook entry does not carry the limit, and the walk reports {found}"


def test_a_hook_entry_that_runs_no_kernel_hook_is_left_as_it_is(template_settings, programs):
    """DEC-580 speaks of the guard's entries: a project's or a later release's other hook needs no limit, or its own."""
    settings = _conforming(template_settings, programs)
    settings["hooks"]["Notification"] = [
        {"hooks": [{"type": "command", "command": "sh scripts/notify.sh"},
                   {"type": "command", "command": "sh scripts/log.sh", limit.LIMIT_KEY: 5}]}
    ]
    assert limit.faults(settings, programs) == [], "a hook entry that runs no kernel hook program was held to the limit"
