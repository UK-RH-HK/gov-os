"""The status files (S5): ``status.json`` and ``status.txt``, written whole (a temporary file and a rename) every pass.

A pass that fails writes ``PASS FAILED <time>: <reason>`` as the first line of ``status.txt`` and ``"ok": false`` with
the reason in ``status.json``, replacing the file whole: no stale file looks current. ``read`` is what ``gov dispatch
status`` prints, and it says when the last pass is older than three minutes (``STALE_AFTER_S``).
"""

from __future__ import annotations

import json

from gov.dispatch import state as states

STALE_AFTER_S = 180


def failed(reason: str, when: str) -> dict:
    return {"ok": False, "time": when, "outcome": "failed", "reason": reason}


def write(state: states.State, data: dict) -> None:
    state.dir.mkdir(parents=True, exist_ok=True)
    state.write_whole(state.file("status.json"), json.dumps(data, indent=2, sort_keys=False) + "\n")
    state.write_whole(state.file("status.txt"), render(data))


def _figures(value) -> str:
    return "unknown" if value is None else str(value)


def render(data: dict) -> str:
    if not data.get("ok"):
        return f"PASS FAILED {data['time']}: {data.get('reason', 'unknown')}\n"
    out = [f"dispatch pass {data['time']}: {data['outcome']}"
           + (f" (exit {data['exit_code']})" if data.get("exit_code") else "")]
    if data["outcome"] == "OFF":
        return out[0] + " (an OFF file is present: no pass ran)\n"
    running = data["running"]
    out.append(f"running ({len(running)}): " + (", ".join(f"{r['ticket']} pid {r['pid']}" for r in running) or "none"))
    load, memory, gate = data["load"], data["memory"], data["gate"]
    out.append(f"load: 1m {_figures(load['load_1m'])}, 15m {_figures(load['load_15m'])}, busy cores "
               f"{_figures(load['busy_cores'])} of {_figures(load['nproc'])}")
    out.append(f"memory: available {_figures(memory['available_bytes'])}, floor {_figures(memory['floor_bytes'])}, "
               f"working size {_figures(memory['working_size_bytes'])}")
    out.append("gate: open" if gate["open"] else "gate: SHUT: " + "; ".join(gate["reasons"]))
    out.append(f"disk: {gate['disk']}")
    slots = data["slots"]
    out.append(f"slots: {len(slots['held'])} held of {_figures(slots['total'])}")
    peaks = data["peaks"]
    out.append(f"peaks (computed {peaks['computed']}):")
    for kind, peak in sorted(peaks["kinds"].items()):
        out.append(f"  {kind}: cpu {peak['cpu']:g}, memory {peak['mem_bytes']}, date {peak['date']}"
                   f" ({peak['source']})")
    ahead = data["peaks_ahead"]
    out.append(f"peaks ahead: memory {ahead['memory_bytes']}, cpu {ahead['cpu']:g}, jobs {len(ahead['jobs'])}")
    out.append(f"queue ({len(data['queue'])}): " + (", ".join(data["queue"]) or "empty"))
    if data.get("land"):
        out.append(f"land: {data['land']}")
    if data.get("land_hold") and data.get("land") != data["land_hold"]:
        out.append(f"land: {data['land_hold']}")
    out += [f"land: {note}" for note in data.get("land_notes", [])]
    steps = data.get("heavy_steps", [])
    if steps:
        out.append(f"heavy steps ({len(steps)}): " + ", ".join(
            f"{s['kind']} pid {s['pid']} " + (f"slot {s['slot']}" if s["slot"] is not None else "no slot")
            for s in steps))
    inbox = data["inbox"]
    out.append(f"inbox ({len(inbox)} unread): " + (", ".join(f"{i['name']} ({i['W2']}, {i['status']})" for i in inbox)
                                                  or "empty"))
    hold = data["nightly_hold"]
    if hold:
        out.append(f"nightly hold (landings only): {hold['from']} to {hold['until']}")
    started = data["started"]
    out.append("started: " + (f"{started['W2']} as {started['log']}" if started else "none"))
    out.append(f"skipped ({len(data['skipped'])}):")
    out += [f"  {s['W2'] or s['line']}: {s['reason']}" for s in data["skipped"]]
    if data.get("findings"):
        out.append("findings:")
        out += [f"  {f}" for f in data["findings"]]
    if data["problems"]:
        out.append("problems:")
        out += [f"  {p}" for p in data["problems"]]
    return "\n".join(out) + "\n"


def read(state: states.State, now) -> dict | None:
    """The last status with ``age_s`` and ``stale``, or None when no pass has written one."""
    try:
        data = json.loads(state.file("status.json").read_text(encoding="utf-8"))
        written = states.parse_time(data["time"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if written is None:
        return None
    age = max(0.0, (now - written).total_seconds())
    return {**data, "age_s": round(age), "stale": age > STALE_AFTER_S}
