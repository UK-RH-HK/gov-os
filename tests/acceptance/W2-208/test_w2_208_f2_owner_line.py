"""F2: an update whose regeneration would drop an owner's own deny line fails at the step ``settings``, naming the line,
and rolls back: HEAD and every file as before, the lock still naming A (Q-UPD; DEC-1217 (6))."""

from __future__ import annotations

import json

import w2_208_support as support


def test_f2_an_update_that_loses_the_owners_deny_line_fails_naming_it_and_rolls_back(losing_013):
    done = losing_013["run"]
    assert done.returncode != 0, (
        f"`gov update {support.B}` exited 0 although its regeneration lost the owner's {support.OWNER_DENY}\n"
        f"{done.describe()}")
    error = done.error()
    details = error.get("details") or {}
    told = str(error.get("message", "")) + " " + json.dumps(details)
    assert support.OWNER_DENY in told, f"the failure does not name the lost line {support.OWNER_DENY}\n{done.describe()}"
    assert "settings" in told.lower(), f"the failure does not name the step `settings`\n{done.describe()}"
    assert details.get("rolled_back") is True and "roll" in str(error.get("message", "")).lower(), (
        f"the failure does not say it rolled back\n{done.describe()}")
    changed = support.w217.tree_difference(losing_013["before"], losing_013["after"])
    assert not changed, f"HEAD or files are not as before the failed update: {changed[:20]}"
    assert losing_013["lock"] == support.A1, f"the lock names {losing_013['lock']}, not {support.A1}, after the rollback"
