"""S9: the re-measure.

gov resources records samples of each live session's process-tree memory, noting whether a verification run holds
the configured lock, and from them writes the verification peak (largest sample) and the working size (largest
outside verification) with the date into the configuration file, showing old and new side by side
[DEC-947 items 2 and 3, DEC-950 item 2].

Interface (README, "The re-measure"): ``gov resources --sample`` takes one sample of every live session (result
``samples``: ``[{"pid", "tree_memory_bytes", "verification"}]``); ``gov resources --remeasure`` writes both figures
(result ``{"old": {...}, "new": {...}}`` with the two keys). A verification run holds an exclusive ``flock`` on the
file the configuration's ``verification_lock`` names.
"""

from __future__ import annotations

import datetime

import w2_20_support as support
from w2_20_support import GIB, MIB


def test_s9_samples_note_the_verification_lock_and_the_remeasure_writes_both_figures_with_the_date(machine, repo):
    """Session A holds 64 MiB throughout. Session B is small, then takes the verification lock and holds 192 MiB
    more. Sampled once before and once during: the working size is about A's 64 MiB (largest outside verification),
    the verification peak about B's 192 MiB (largest sample)."""
    machine.open_config(verification_peak_bytes=support.dated(9 * GIB, date=support.days_ago(30), source="old"),
                        working_size_bytes=support.dated(5 * GIB, date=support.days_ago(30), source="old"))
    a = machine.live_process(memory_mib=64)
    b, start_verification = machine.verification_session(memory_mib=0, more_mib=192)
    machine.register(repo, a.pid, ticket="DAEO-smpa")
    machine.register(repo, b.pid, ticket="DAEO-smpb")

    code, envelope, out, err = machine.gov(repo, "--sample")
    samples = support.reading_of(code, envelope, out, err).get("samples")
    assert isinstance(samples, list) and {int(s["pid"]) for s in samples} >= {a.pid, b.pid}, samples
    assert not any(s.get("verification") for s in samples), f"no verification runs yet: {samples}"

    start_verification()
    code, envelope, out, err = machine.gov(repo, "--sample")
    samples = support.reading_of(code, envelope, out, err).get("samples")
    by_pid = {int(s["pid"]): s for s in samples}
    assert by_pid[b.pid].get("verification") is True, f"the lock held is not noted: {samples}"
    assert by_pid[b.pid]["tree_memory_bytes"] >= 192 * MIB, by_pid[b.pid]

    code, envelope, out, err = machine.gov(repo, "--remeasure")
    result = support.reading_of(code, envelope, out, err)
    old, new = result.get("old"), result.get("new")
    assert isinstance(old, dict) and isinstance(new, dict), f"old and new are not shown side by side: {result}"
    assert old.get("verification_peak_bytes") == 9 * GIB and old.get("working_size_bytes") == 5 * GIB, old
    assert new.get("verification_peak_bytes", 0) >= 192 * MIB, new
    assert 64 * MIB <= new.get("working_size_bytes", 0) < 192 * MIB, (
        f"the working size is not the largest sample outside verification: {new}")

    written = machine.read_config()
    dates = {datetime.date.today().isoformat(), datetime.datetime.now(datetime.timezone.utc).date().isoformat()}
    for key in support.MEASURED_KEYS:
        assert written[key]["value"] == new[key], (key, written[key], new)
        assert written[key]["date"] in dates, f"{key} is not dated today: {written[key]}"
        assert written[key].get("source"), written[key]
    assert written["memory_floor_bytes"]["value"] == 3 * GIB, "the re-measure changed a value it does not measure"
