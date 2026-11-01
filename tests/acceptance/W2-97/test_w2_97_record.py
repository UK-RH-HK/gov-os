"""KPI 5 (DEC-959 item 1): each advance writes the record the close cites: records/<new head, 12 hex>.json with the
head, the base, the tickets, the selection, the counts and the time; the landed files point at it."""

from __future__ import annotations

import json
from pathlib import Path

import w2_97_support as S


def test_each_advance_writes_the_record_the_close_cites(q):
    q.plant()
    t1 = q.ticket(901, {"app/c.txt": "ok\n", "tests/test_c.py": S.reads_ok("c")})
    t2 = q.ticket(902, {"app/d.txt": "ok\n", "tests/test_d.py": S.reads_ok("d")})
    h1 = q.code_moves_on()
    q.configure_select(targets={t1.name: ["tests/test_c.py"], t2.name: ["tests/test_d.py"]},
                       core_changed=["src/gov/stand_in_core.py"], unplaced=["misc/stand_in_unplaced.txt"])
    q.submit(t1, t2)

    done = q.run()
    assert done.returncode == 0, S.said(done)
    head = q.head()
    record = q.record(head)

    assert record["head"] == head and record["base"] == h1, (record["head"], record["base"])
    rows = record["tickets"].values() if isinstance(record["tickets"], dict) else record["tickets"]
    rows = {r["ticket"]: r for r in rows}
    assert sorted(rows) == [t1.name, t2.name], f"the record's tickets: {sorted(rows)}"
    for t in (t1, t2):
        landed = q.entry("landed", t.name)
        assert (rows[t.name]["task"], rows[t.name]["commit"], rows[t.name]["merge"]) == \
            (t.task, t.commit, landed["merge"]), rows[t.name]
        assert q.record_path(landed).resolve() == (q.queue / "records" / f"{head[:12]}.json").resolve(), \
            f"{t.name}'s landed file does not point at the advance's record: {landed['record']}"
    assert record["skipped"] is None, f"a run that ran records a skip: {record['skipped']}"
    selection = json.dumps(record["selection"])
    for named in ("tests/test_c.py", "tests/test_d.py", "src/gov/stand_in_core.py", "misc/stand_in_unplaced.txt"):
        assert named in selection, f"the record's selection does not name {named}: {selection}"
    assert {k: record["counts"][k] for k in ("tests", "failures", "errors", "skipped")} == \
        {"tests": 2, "failures": 0, "errors": 0, "skipped": 0}, f"the record's counts: {record['counts']}"
    assert record["flaky"] == [] and record["unowned"] == [] and record["ejected"] == [], record
    assert Path(record["log"]).is_absolute() and Path(record["log"]).is_dir(), f"the record's log: {record['log']}"
    assert record["started"] and record["finished"], "the record does not give the run's times"
    S.assert_main_unmoved(q)
