"""S8 and F5: the one configuration file.

S8: all values in one configuration file (floor, verification peak, working size, disk and inode floors,
verification lock, GPU margin), each with its date and source; a value missing or malformed shuts the gate, naming
it; the reading names a measured figure older than seven days as due for re-measure [DEC-947 item 3, DEC-950 item 2].
F5 (failure): a value the gate uses not taken from the configuration file, or a reading that cannot be taken treated
as met.

The file is ``$HOME/.gov-os/machine/gate.json`` (the file W2-123's server start already reads, ``GATE_REL`` in
``gov.retrieval.ollama``); each gate value is ``{"value": ..., "date": "YYYY-MM-DD", "source": "..."}``
(README, "The configuration file"). A broken value is one reason ``{"condition": "config", ...}`` that names its key.
"""

from __future__ import annotations

import pytest

import w2_20_support as support
from w2_20_support import GIB


@pytest.mark.parametrize("key", support.GATE_KEYS)
def test_s8_a_value_missing_shuts_the_gate_naming_it(machine, repo, key):
    machine.open_config(**{key: None})

    reading = machine.read(repo)
    assert support.gate_of(reading)["open"] is False, f"{key} missing, and the gate opened: {reading}"
    config = support.config_reasons(reading)
    assert any(support.names_key(r, key) for r in config), f"no config reason names {key}: {reading['gate']}"
    assert any(support.names_key(r, key) for r in support.config_reasons(support.refusal_of(*machine.check(repo))))


MALFORMED = {
    "a word for a number": ("memory_floor_bytes", support.dated("three gibibytes")),
    "a negative size": ("working_size_bytes", support.dated(-1)),
    "no slot at all": ("heavy_slots", support.dated(0)),
    "a margin in words": ("gpu_margin", support.dated("ten percent")),
    "a lock that is no path": ("verification_lock", support.dated(42)),
    "a fraction of an inode": ("inode_floor", support.dated(1.5)),
    "shares that are no map": ("gpu_shares", support.dated([3000, 2000])),
    "a value without its date": ("disk_floor_bytes", {"value": 100 * GIB, "source": "DEC-898 item 1"}),
    "a value without its source": ("verification_peak_bytes", {"value": 4 * GIB, "date": support.today()}),
    "a date that is no date": ("oom_floor_bytes", {"value": GIB, "date": "last week", "source": "planted"}),
    "a bare value, no date or source": ("memory_floor_bytes", 3 * GIB),
}


@pytest.mark.parametrize("case", list(MALFORMED))
def test_s8_a_malformed_value_shuts_the_gate_naming_it(machine, repo, case):
    key, value = MALFORMED[case]
    values = machine.config_values()
    values[key] = value
    machine.write_config(values)

    reading = machine.read(repo)
    assert support.gate_of(reading)["open"] is False, f"{case} ({key}), and the gate opened: {reading}"
    assert any(support.names_key(r, key) for r in support.config_reasons(reading)), (
        f"no config reason names {key}: {reading['gate']}")


def test_s8_a_file_that_is_not_json_shuts_the_gate(machine, repo):
    machine.write_config("{ this is not JSON")
    reading = machine.read(repo)
    assert support.gate_of(reading)["open"] is False and support.config_reasons(reading), reading


@pytest.mark.parametrize("age, due", [(8, True), (7, False)], ids=["8 days old is due", "7 days old is not"])
def test_s8_a_measured_figure_older_than_seven_days_is_named_due_for_re_measure(machine, repo, age, due):
    """The working size measured ``age`` days ago, the verification peak today. Due is a notice: the gate stays
    open."""
    machine.open_config(working_size_bytes=support.dated(1 * GIB, date=support.days_ago(age), source="measured"))

    reading = machine.read(repo)
    listed = reading.get("due_for_remeasure")
    assert isinstance(listed, list), f"the reading has no due_for_remeasure list: {reading}"
    assert ("working_size_bytes" in listed) is due, listed
    assert "verification_peak_bytes" not in listed, listed
    assert support.gate_of(reading)["open"] is True, reading


def test_f5_the_values_in_force_are_the_files_and_follow_it(machine, repo):
    """Changing the floor and the working size in the file changes the memory need the gate reports."""
    machine.set_readings(available_bytes=4 * GIB)
    machine.open_config(memory_floor_bytes=5 * GIB, working_size_bytes=2 * GIB)
    first = support.reasons_by_condition(machine.read(repo))
    assert first["memory"]["threshold"] == 7 * GIB, first
    machine.open_config(memory_floor_bytes=2 * GIB, working_size_bytes=3 * GIB)
    second = support.reasons_by_condition(machine.read(repo))
    assert second["memory"]["threshold"] == 5 * GIB, second
