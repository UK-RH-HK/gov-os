"""A planted samples.jsonl for ACT-P95-1's tests and rehearsal (no real session is read).

96 lines 300 s apart from 2026-11-11T08:00:00+00:00 (an 8 h day); each holds two session samples (a lead and an engineer),
and some lines also hold: a slot holder (kind rebuild, 12 GB: never a session), a session sample taken while a
verification run held the lock (15 GB: outside the population), and two malformed sizes (a bool and a string). Of the 192
session samples outside verification, 5 are outliers of 6 to 9.5 GB; the rest lie between 1.5 and 2.5 GB. So the
maximum is 9.5 GB and the p95 (nearest rank, the 183rd of 192) is a normal sample under 2.5 GB.

   python3 plant_samples.py <out file>
"""
import datetime
import json
import sys

START = datetime.datetime(2026, 11, 11, 8, 0, 0, tzinfo=datetime.timezone.utc)
OUTLIERS = {7: 6_000_000_000, 31: 7_200_000_000, 58: 9_500_000_000, 80: 8_100_000_000, 140: 6_600_000_000}


def lines(count: int = 96, step: int = 300) -> list[dict]:
    out, index = [], 0
    for i in range(count):
        taken = []
        for role, ticket in (("orchestrator", "DAEO-lead1"), ("engineer", "W2-99")):
            size = 1_500_000_000 + (index * 7919 % 1000) * 1_000_000
            taken.append({"pid": 4000 + (index % 2), "tree_memory_bytes": OUTLIERS.get(index, size),
                          "verification": False, "ticket": ticket, "role": role})
            index += 1
        if i % 12 == 5:
            taken.append({"pid": 4010, "tree_memory_bytes": 12_000_000_000, "verification": False,
                          "kind": "rebuild", "slot": 1})
        if i % 16 == 9:
            taken.append({"pid": 4011, "tree_memory_bytes": 15_000_000_000, "verification": True,
                          "ticket": "W2-98", "role": "engineer"})
        if i == 20:
            taken += [{"pid": 4012, "tree_memory_bytes": True, "verification": False, "role": "engineer"},
                      {"pid": 4013, "tree_memory_bytes": "9999999999", "verification": False, "role": "engineer"}]
        stamp = (START + datetime.timedelta(seconds=step * i)).isoformat(timespec="seconds")
        out.append({"time": stamp, "samples": taken})
    return out


def text(**kw) -> str:
    return "".join(json.dumps(line) + "\n" for line in lines(**kw))


if __name__ == "__main__":
    with open(sys.argv[1], "w", encoding="utf-8") as handle:
        handle.write(text())
