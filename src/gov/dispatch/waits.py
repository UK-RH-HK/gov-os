"""``gov dispatch waits``: how long each heavy job waited, and how much of it with room (RT-1; audit 3 D2, D9).

Read from the runtime log's events. A job's wait is its ``ready`` to its ``started`` (to now while it still waits: no
``started``, no ``ended`` and a live pid). Its **with-room** seconds are the intervals that follow a ``wait`` event whose
``room`` is true, or a ``ready`` that no ``wait`` follows at once (the run asked and was not held), until the next
event; a wait for lack of room (``room`` false: the load, the GPU) is never counted, so it is never a finding. A job that
is gone without starting (a dead pid, no ``ended``) is ``abandoned``, measured to its last event, and no finding.
"""

from __future__ import annotations

import datetime

from gov.resources import machine

OVER_S = 600.0
ENDING = ("started", "ended")


def epoch(text) -> float | None:
    try:
        when = datetime.datetime.fromisoformat(str(text).strip().replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
        return when.timestamp()
    except ValueError:
        return None


def analyse(log: list[dict], now: float, alive=machine.alive) -> list[dict]:
    """One row per job with a ``ready`` event, in the order the jobs asked: ``{job, kind, pid, state, reason, waited_s,
    with_room_s}``; ``state`` is ``started``, ``ended`` (never started), ``waiting`` or ``abandoned``."""
    jobs: dict[str, list[tuple[float, dict]]] = {}
    for item in log:
        job, when = item.get("job"), epoch(item.get("at"))
        if isinstance(job, str) and when is not None and isinstance(item.get("event"), str):
            jobs.setdefault(job, []).append((when, item))
    rows = []
    for job, seen in jobs.items():
        seen.sort(key=lambda pair: pair[0])
        names = [e["event"] for _, e in seen]
        if "ready" not in names:
            continue
        first = names.index("ready")
        asked = seen[first][0]
        pid = seen[first][1].get("pid")
        started = next((w for w, e in seen if e["event"] == "started"), None)
        finished = next((w for w, e in seen if e["event"] == "ended"), None)
        if started is not None:
            state, until = "started", started
        elif finished is not None:
            state, until = "ended", finished
        elif isinstance(pid, int) and alive(pid):
            state, until = "waiting", now
        else:
            state, until = "abandoned", seen[-1][0]
        with_room, reason = 0.0, None
        for index in range(first, len(seen)):
            at, item = seen[index]
            if at >= until or item["event"] in ENDING:
                break
            following = seen[index + 1][0] if index + 1 < len(seen) else until
            following = min(following, until)
            if item["event"] == "wait":
                reason = item.get("reason")
                if item.get("room") is True:
                    with_room += following - at
            elif item["event"] == "ready":
                after = seen[index + 1][1]["event"] if index + 1 < len(seen) else None
                if after != "wait":
                    with_room += following - at
            elif item["event"] == "admitted":
                with_room += following - at
        rows.append({"job": job, "kind": seen[first][1].get("kind"), "pid": pid, "state": state, "reason": reason,
                     "waited_s": round(max(0.0, until - asked), 3), "with_room_s": round(with_room, 3)})
    rows.sort(key=lambda row: jobs[row["job"]][0][0])
    return rows


def findings(rows: list[dict], over: float = OVER_S) -> list[dict]:
    """The jobs whose with-room wait passed ``over`` seconds (an abandoned job cannot be waiting: never one)."""
    return [row for row in rows if row["with_room_s"] > over and row["state"] != "abandoned"]


def render(rows: list[dict], found: list[dict], over: float) -> str:
    lines = [f"{row['job']}  {row['state']}  waited {row['waited_s']:.1f} s  with room {row['with_room_s']:.1f} s"
             for row in rows] or ["no heavy job has asked yet"]
    lines += [f"finding: {row['job']} waited with room past {over:g} s" for row in found]
    return "\n".join(lines) + "\n"
