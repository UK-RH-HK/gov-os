"""S4 and F3: the shared disk.

S4: the gate also reads the shared disk: it shuts below a floor of free space and of free inodes (100 GiB and
10,000,000, set in the gate's one configuration file); gov launch refuses to start a session while it is shut, naming
the reading (``test_w2_20_launch.py``), and the reading is one function gov close can call before a close
[DEC-898 item 1]. F3 (failure): a launch or a close that starts with the disk below either floor; a gate that reads
disk space but not inodes.

The function (README, "The disk reading for gov close"): ``gov.resources.check_disk(env=None)`` returns
``{"open", "reasons", "free_bytes", "free_inodes"}``; ``env`` (default ``os.environ``) gives ``HOME`` (the
configuration file) and ``GOV_RESOURCES_DISK`` (the planted reading).
"""

from __future__ import annotations

import importlib

import pytest

import w2_20_support as support
from w2_20_support import GIB


def _check_disk(machine):
    resources = importlib.import_module("gov.resources")  # in the test's call: a failure, not a collection error
    return resources.check_disk(env=machine.env())


@pytest.mark.parametrize("free_bytes, free_inodes, broken", [
    (100 * GIB, 10_000_000, set()),
    (100 * GIB - 1, 50_000_000, {"disk"}),
    (500 * GIB, 9_999_999, {"inodes"}),
    (1 * GIB, 10, {"disk", "inodes"}),
], ids=["both at their floors opens", "space below its floor", "inodes below their floor [F3]", "both below"])
def test_s4_the_disk_reading_is_one_function_gov_close_can_call(machine, free_bytes, free_inodes, broken):
    machine.set_readings(free_bytes=free_bytes, free_inodes=free_inodes)

    answer = _check_disk(machine)
    assert isinstance(answer, dict) and isinstance(answer.get("open"), bool), answer
    assert answer.get("free_bytes") == free_bytes and answer.get("free_inodes") == free_inodes, answer
    assert answer["open"] is (not broken), answer
    named = {r.get("condition"): r for r in answer.get("reasons", [])}
    assert set(named) == broken, answer
    if "disk" in named:
        assert (named["disk"]["reading"], named["disk"]["threshold"]) == (free_bytes, 100 * GIB), named
    if "inodes" in named:
        assert (named["inodes"]["reading"], named["inodes"]["threshold"]) == (free_inodes, 10_000_000), named


def test_s4_the_floors_are_the_configuration_files(machine):
    """F5 as well: the floors come from the file, not from the code (200 GiB and 20,000,000 here)."""
    machine.open_config(disk_floor_bytes=200 * GIB, inode_floor=20_000_000)
    machine.set_readings(free_bytes=150 * GIB, free_inodes=15_000_000)

    answer = _check_disk(machine)
    named = {r.get("condition"): r for r in answer.get("reasons", [])}
    assert answer.get("open") is False and set(named) == {"disk", "inodes"}, answer
    assert named["disk"]["threshold"] == 200 * GIB and named["inodes"]["threshold"] == 20_000_000, named


def test_s4_an_unreadable_disk_is_shut_for_a_close_too(machine):
    """F5: a reading that cannot be taken is never treated as met."""
    answer = importlib.import_module("gov.resources").check_disk(
        env=machine.env(GOV_RESOURCES_DISK=str(machine.base / "no-such-disk.json")))
    assert answer.get("open") is False and answer.get("reasons"), answer


def test_f3_a_start_check_refuses_while_the_disk_is_below_either_floor(machine, repo):
    machine.set_readings(free_inodes=1_000)
    refused = support.refusal_of(*machine.check(repo))
    reasons = support.reasons_by_condition(refused)
    assert set(reasons) == {"inodes"}, reasons
    assert refused.get("disk", {}).get("free_inodes") == 1_000, f"the refusal does not carry the disk reading: {refused}"
