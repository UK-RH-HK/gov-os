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

import datetime
import json

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


# P-3 (a), settled (DEC-1097 (8)): the engineer ships a dated, sourced configuration template,
# ``gov resources --init-config``, with this machine's values from the decisions, never overwriting an existing file;
# no default is read in its absence (S8, ``test_with_no_configuration_file_the_gate_is_shut_and_names_it``).
DECIDED = {
    "memory_floor_bytes": 3 * GIB,      # DEC-942 item 2
    "disk_floor_bytes": 100 * GIB,      # DEC-898 item 1 (S4's floor)
    "inode_floor": 10_000_000,          # DEC-898 item 1 (S4's floor)
}


def test_s8_init_config_writes_a_dated_sourced_template_with_this_machines_decided_values(machine, repo):
    """No file: ``--init-config`` writes ``$HOME/.gov-os/machine/gate.json`` with every gate value, each with a real
    date and a source; the decided floors and margin are the decisions'; and the gate then reads the file whole
    (no ``config`` reason)."""
    machine.config_file.unlink()
    code, envelope, out, err = machine.gov(repo, "--init-config")
    assert code == 0 and envelope is not None and envelope.get("ok") is True, (
        f"--init-config did not succeed: exit {code}\nstdout: {out}\nstderr: {err}")
    assert machine.config_file.is_file(), f"--init-config wrote no {machine.config_file}"

    written = json.loads(machine.config_file.read_text())
    for key in support.GATE_KEYS:
        entry = written.get(key)
        assert isinstance(entry, dict) and "value" in entry, f"the template has no {key} value: {entry}"
        try:
            datetime.date.fromisoformat(str(entry.get("date")))
        except ValueError:
            raise AssertionError(f"the template's {key} has no date: {entry}") from None
        assert isinstance(entry.get("source"), str) and entry["source"].strip(), f"{key} has no source: {entry}"
    for key, value in DECIDED.items():
        assert written[key]["value"] == value, f"the template's {key} is not the decision's {value}: {written[key]}"
    assert support.close_to(written["gpu_margin"]["value"], 0.10), written["gpu_margin"]  # DEC-950 item 2

    assert support.config_reasons(machine.read(repo)) == [], "the gate does not read the template whole"


# Round 7: the configuration format is frozen from 28fbcfebf (W2-20's head when ACT-GATE-CONFIG-2 writes the machine's
# file): no key renamed, added or given another meaning. The expected set is the README's "The configuration file"
# section as it stands, never W2-20's code. Each dated value is exactly {"value", "date", "source"}.
def _int(low):
    return lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= low


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0


FROZEN_DATED = {
    "memory_floor_bytes": _int(0),
    "verification_peak_bytes": _int(0),
    "working_size_bytes": _int(0),
    "rebuild_peak_bytes": _int(0),
    "disk_floor_bytes": _int(0),
    "inode_floor": _int(0),
    "verification_lock": lambda v: isinstance(v, str) and v.strip() != "",
    "gpu_margin": _number,
    "oom_floor_bytes": _int(0),
    "heavy_slots": _int(1),
    "gpu_shares": lambda v: isinstance(v, dict) and set(v) == {"embedder_mib", "reranker_mib"} and all(
        _int(0)(n) for n in v.values()),
}
FROZEN_OPTIONAL = {"thread_budget": _int(1)}  # "optional": the template may leave it out
FROZEN_SECTION = "embedding_servers"          # W2-123's section, not a dated value
SERVER_KEYS = {"cpus", "nice", "parallel", "probe_slow_s", "probe_hung_s", "date", "source"}


def _dated_ok(entry) -> bool:
    if not isinstance(entry, dict) or set(entry) != {"value", "date", "source"}:
        return False
    try:
        datetime.date.fromisoformat(str(entry["date"]))
    except ValueError:
        return False
    return isinstance(entry["source"], str) and entry["source"].strip() != ""


def _dated_by(entry: dict, section: dict) -> bool:
    """A server's date and source, on the server or on the whole section ("plus date and source")."""
    for holder in (entry, section):
        if "date" in holder or "source" in holder:
            try:
                datetime.date.fromisoformat(str(holder.get("date")))
            except ValueError:
                return False
            return isinstance(holder.get("source"), str) and holder["source"].strip() != ""
    return False


def test_s8_init_config_writes_exactly_the_frozen_configuration_format(machine, repo):
    """Under a planted HOME with no file, ``--init-config`` writes exactly the README's key set, nesting and value
    form, and nothing else: the eleven dated values, ``thread_budget`` only as a dated value when present, and
    ``embedding_servers`` as W2-123's section (``shared`` and ``query``, each ``cpus`` as a CPU list text and ``nice``
    from 0 to 19, optionally ``parallel`` and ``probe_*``, ``query`` optionally ``device`` ``gpu``/``cpu``, with a date
    and a source)."""
    machine.config_file.unlink()
    code, envelope, out, err = machine.gov(repo, "--init-config")
    assert code == 0 and envelope is not None and envelope.get("ok") is True, (
        f"--init-config did not succeed: exit {code}\nstdout: {out}\nstderr: {err}")
    written = json.loads(machine.config_file.read_text())
    assert isinstance(written, dict), f"the template is not a JSON object: {written!r}"

    allowed = set(FROZEN_DATED) | set(FROZEN_OPTIONAL) | {FROZEN_SECTION}
    required = set(FROZEN_DATED) | {FROZEN_SECTION}
    assert not set(written) - allowed, f"keys the README does not state: {sorted(set(written) - allowed)}"
    assert not required - set(written), f"keys the README states are missing: {sorted(required - set(written))}"

    for key, value_ok in {**FROZEN_DATED, **FROZEN_OPTIONAL}.items():
        if key not in written:
            continue
        entry = written[key]
        assert _dated_ok(entry), f"{key} is not exactly {{value, date, source}} with a real date: {entry}"
        assert value_ok(entry["value"]), f"{key}'s value is not of the README's form: {entry['value']!r}"

    section = written[FROZEN_SECTION]
    assert isinstance(section, dict), f"{FROZEN_SECTION} is not an object: {section!r}"
    assert {"shared", "query"} <= set(section) <= {"shared", "query", "date", "source"}, (
        f"{FROZEN_SECTION} holds other keys than shared, query, date and source: {sorted(section)}")
    for name in ("shared", "query"):
        entry = section[name]
        assert isinstance(entry, dict), f"{FROZEN_SECTION}.{name} is not an object: {entry!r}"
        keys = SERVER_KEYS | ({"device"} if name == "query" else set())
        assert not set(entry) - keys, f"{FROZEN_SECTION}.{name} holds keys the README does not state: {sorted(entry)}"
        assert isinstance(entry.get("cpus"), str) and entry["cpus"].strip(), (
            f"{FROZEN_SECTION}.{name}.cpus is not a CPU list text: {entry.get('cpus')!r}")
        assert _int(0)(entry.get("nice")) and entry["nice"] <= 19, (
            f"{FROZEN_SECTION}.{name}.nice is not an integer from 0 to 19: {entry.get('nice')!r}")
        assert _dated_by(entry, section), f"{FROZEN_SECTION}.{name} has no date and source: {entry}"
        if "device" in entry:
            assert entry["device"] in ("gpu", "cpu"), f"{FROZEN_SECTION}.query.device: {entry['device']!r}"


def test_s8_init_config_never_overwrites_an_existing_file(machine, repo):
    before = machine.config_file.read_bytes()
    code, envelope, out, err = machine.gov(repo, "--init-config")
    assert code != 0, f"--init-config over an existing file ended with exit 0\nstdout: {out}\nstderr: {err}"
    assert envelope is None or envelope.get("ok") is False, envelope
    assert machine.config_file.read_bytes() == before, "--init-config changed an existing configuration file"
    assert "gate.json" in out + err, f"the refusal does not name the file it keeps: {out}{err}"
