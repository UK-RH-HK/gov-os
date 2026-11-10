#!/usr/bin/env python3
"""The spend log in one unit, and the runaway brake (DAEO-sdxk, 2026-11-10; DEC-1089 (3), DEC-1091, DEC-1112 (3)).

    spend.py record --what <text> --kind <kind> [--ticket ID] [--wbs W2-n] [--role R] [--cost-usd N]
                    [--output-tokens N] [--cache-read-tokens N] [--cache-creation-tokens N] [--input-tokens N]
                    [--projection-usd N] [--note <text>] [--extra key=value ...]     one line, by hand or by a tool
    spend.py from-log <claude -p json log> --what ... --kind launched [--ticket --wbs --role --projection-usd --note]
                    one line from a session's own result (total_cost_usd and usage), as launch_worker.sh does
    spend.py add-helper --what <text> --role R --model M --effort E --class C0|C1|C2|C3 [--ticket ID] [--wbs W2-n]
                    [--promoted <reason>] [--cost-usd N] [--output-tokens N] [--cache-read-tokens N]
                    [--cache-creation-tokens N] [--input-tokens N] [--note <text>]
                    one line (kind "agent") for an in-session helper the CTO started with the Agent tool, in the
                    same schema as a launched worker (DEC-1120 (3)): the model, effort and class are all required
    spend.py check                       the brake: one inbox item per ticket past twice its projection
    spend.py clear <W2> [--projection-usd N] [--note <text>]     the CTO lifts a ticket's brake
    spend.py sum                         each ticket's cost, projection and brake state, one line each
    spend.py brief-budget <brief>        the brief's budget (front matter projection_usd/budget_usd, or "N USD" after
                                         "budget"/"projection"), or nothing
    spend.py normalise [--swap]          rewrite log/spend.jsonl with every line in the one schema (below): the new file
                                         beside it first (spend.jsonl.norm), every line checked, then with --swap the
                                         old one kept as spend.jsonl.orig-<date> and the new one moved in

The one schema (every line has exactly these keys; unknown values are null, never a mixed sum):
  at, what, kind, ticket, wbs, role, cost_usd (a number: the session's total_cost_usd), cost_source, input_tokens,
  output_tokens, cache_read_tokens, cache_creation_tokens (each only where the source says which kind), projection_usd,
  note, orig_tokens, orig_cost (an old line's free-text `tokens`/`cost`, kept as written), extra (every other key an
  old line had, as written).
RUBRIC-2 (DEC-1120 (3), 2026-11-10) adds four top-level keys, after `extra`: model (the model as named at the spawn),
class (C0 mechanical, C1 routine, C2 significant, C3 critical), tier (opus, sonnet, haiku, or other: derived from the
model's name), promoted (null, or the recorded reason for a promotion). A line written before them has the first 17
keys alone: it stays valid, and normal() gives it the four as null; a reader that ignores them is unaffected.
There is no `tokens` field: cached context is never summed into a token count (the 17,057,921 of 2026-11-09).

The brake (DEC-1091): per ticket (the `wbs`, the W2 id; lines without one, all lines before this tool, never count), the
cost since its first launch, or since the CTO's last clear, against twice its latest projection_usd. Past
it: one line kind "brake" in the log, the file log/brake/<W2>.json (launch_worker.sh refuses a new launch for that W2
while it exists), and one inbox item, dispatch/inbox/<stamp>-spend-brake.txt, with a `W2:` line (the dispatcher holds
that W2's starts while it is unread). Usage stays record-only: nothing goes to the owner, no push, no alarm (DEC-1089
(3)); the dead-man's watch never pushes on this item's staleness. A ticket with no projection is never braked.
ORCH (environment) moves the scratch root; SPEND moves the log alone.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ORCH = Path(os.environ.get("ORCH") or "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
SPEND = Path(os.environ.get("SPEND") or ORCH / "log/spend.jsonl")
BRAKES, INBOX = ORCH / "log/brake", ORCH / "dispatch/inbox"
KEYS = ("at", "what", "kind", "ticket", "wbs", "role", "cost_usd", "cost_source", "input_tokens", "output_tokens",
        "cache_read_tokens", "cache_creation_tokens", "projection_usd", "note", "orig_tokens", "orig_cost", "extra",
        "model", "class", "tier", "promoted")
BASE_KEYS = KEYS[:17]  # the keys of a line written before RUBRIC-2: still a normal line
CLASSES = ("C0", "C1", "C2", "C3")
USD = re.compile(r"(\d+(?:\.\d+)?)\s*USD|total_cost_usd\W{0,3}(\d+(?:\.\d+)?)")
OLD_TOKEN_KINDS = {"input": "input_tokens", "output": "output_tokens", "cache_read": "cache_read_tokens",
                   "cache_creation": "cache_creation_tokens"}


def num(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def tier_of(model):
    """opus, sonnet or haiku from the model's name (claude-sonnet-5-5, sonnet, ...); other for any other name."""
    low = str(model or "").lower()
    for t in ("opus", "sonnet", "haiku"):
        if t in low:
            return t
    return "other" if low else None


def normal(d):
    """One line in the schema. Idempotent: a normal line comes back unchanged (one of 17 keys gets the four
    RUBRIC-2 keys as null; a tier is derived from a model that has none)."""
    if set(d) in (set(KEYS), set(BASE_KEYS)):
        out = {k: d.get(k) for k in KEYS}
        if out["model"] and not out["tier"]:
            out["tier"] = tier_of(out["model"])
        if out["cost_usd"] is None and isinstance(out["orig_cost"], str) and USD.search(out["orig_cost"]):
            m = USD.search(out["orig_cost"])  # a cost an earlier pass missed (review finding 6)
            out["cost_usd"] = float(m.group(1) or m.group(2))
            out["cost_source"] = out["cost_source"] or "the line's cost text"
        return out
    out = dict.fromkeys(KEYS)
    out["extra"] = {}
    for k, v in d.items():
        if k in KEYS and k not in ("orig_tokens", "orig_cost", "extra"):
            out[k] = v
        elif k == "tokens":
            out["orig_tokens"] = v
            if isinstance(v, dict):  # the source names each kind: keep each in its own field
                for old, new in OLD_TOKEN_KINDS.items():
                    if num(v.get(old)) is not None:
                        out[new] = v[old]
        elif k == "cost":
            out["orig_cost"] = v
        elif k == "extra" and isinstance(v, dict):
            out["extra"].update(v)
        else:
            out["extra"][k] = v
    if out["cost_usd"] is not None and num(out["cost_usd"]) is None:
        out["extra"]["cost_usd_as_written"] = out["cost_usd"]
        out["cost_usd"] = None
    if out["cost_usd"] is None and isinstance(out["orig_cost"], str):
        m = USD.search(out["orig_cost"])
        if m:
            out["cost_usd"] = float(m.group(1) or m.group(2))
            out["cost_source"] = out["cost_source"] or "the line's cost text"
    elif out["cost_usd"] is None and num(out["orig_cost"]) is not None:
        out["cost_usd"], out["cost_source"] = num(out["orig_cost"]), out["cost_source"] or "the line's cost number"
    if out["projection_usd"] is not None and num(out["projection_usd"]) is None:
        out["extra"]["projection_as_written"] = out["projection_usd"]
        out["projection_usd"] = None
    out["extra"] = out["extra"] or None
    if out["model"] and not out["tier"]:
        out["tier"] = tier_of(out["model"])
    return out


def load(path=None):
    lines = []
    p = Path(path or SPEND)
    if p.is_file():
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if raw.strip():
                try:
                    lines.append(normal(json.loads(raw)))
                except ValueError:
                    lines.append(normal({"kind": "unreadable", "note": raw[:300]}))
    return lines


def append(d):
    line = normal(d)
    SPEND.parent.mkdir(parents=True, exist_ok=True)
    with open(SPEND, "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
    return line


def inbox_item(name, body):
    INBOX.mkdir(parents=True, exist_ok=True)
    stamp, n = time.strftime("%Y%m%d-%H%M%S"), 1
    item = INBOX / f"{stamp}-{name}.txt"
    while True:
        try:
            with open(item, "x") as f:
                f.write(body)
            return item
        except FileExistsError:
            n += 1
            item = INBOX / f"{stamp}-{name}-{n}.txt"


def totals(lines):
    """{W2: {cost, projection, since, launches}}: the cost since the last clear, against the ticket's latest
    projection_usd (a relaunch of a budgeted brief does not raise it; a clear with --projection-usd sets it)."""
    t = {}
    for d in lines:
        w = d.get("wbs")
        if not w:
            continue
        e = t.setdefault(w, {"cost": 0.0, "projection": 0.0, "since": d["at"], "launches": 0})
        if d["kind"] == "brake-clear":
            e["cost"], e["since"] = 0.0, d["at"]
        if num(d.get("projection_usd")):
            e["projection"] = num(d["projection_usd"])
        if d["kind"] not in ("brake", "brake-clear") and num(d.get("cost_usd")) is not None:
            e["cost"] += num(d["cost_usd"])
        e["launches"] += d["kind"] == "launched"
    return t


def now_s():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def check():
    out = []
    for w, e in sorted(totals(load()).items()):
        brake = BRAKES / f"{w}.json"
        if e["projection"] <= 0 or e["cost"] <= 2 * e["projection"] or brake.exists():
            continue
        why = (f"{w} has spent {e['cost']:.2f} USD since {e['since']}, past twice its projection "
               f"({e['projection']:.2f} USD, brake at {2 * e['projection']:.2f})")
        BRAKES.mkdir(parents=True, exist_ok=True)
        try:  # created once: a check ending at the same moment finds it there (review finding 8)
            with open(brake, "x") as f:
                f.write(json.dumps({"wbs": w, "at": now_s(), "cost_usd": round(e["cost"], 4),
                                    "projection_usd": e["projection"], "why": why}) + "\n")
        except FileExistsError:
            continue
        append({"at": now_s(), "what": f"runaway brake on {w}", "kind": "brake", "wbs": w,
                "note": why + "; new launches stop until the CTO clears it (DEC-1091)"})
        item = inbox_item("spend-brake", (
            f"log: spend.jsonl\nW2: {w}\nBrake: runaway (DEC-1091)\nstatus: {why}\n\n"
            f"New launches for {w} stop (launch_worker.sh refuses while {brake} exists) until the CTO clears it:\n"
            f"  python3 {Path(__file__).resolve()} clear {w} [--projection-usd <more>] --note '<why>'\n"
            "Record only: never an alarm to the owner (DEC-1089 (3)).\n"))
        out.append(f"BRAKE {w}: {why}; {item}")
    print("\n".join(out) or "spend check: no ticket past twice its projection")
    return out


def clear(w, projection, note):
    brake = BRAKES / f"{w}.json"
    if not brake.exists():
        sys.exit(f"spend clear: no brake on {w}")
    (BRAKES / "cleared").mkdir(parents=True, exist_ok=True)
    os.replace(brake, BRAKES / "cleared" / f"{w}-{time.strftime('%Y%m%d-%H%M%S')}.json")
    append({"at": now_s(), "what": f"the CTO cleared the brake on {w}", "kind": "brake-clear", "wbs": w,
            "projection_usd": projection, "note": note})
    print(f"spend clear: {w} cleared; its cost counts afresh from now")


def from_log(log):
    """The last JSON object of a claude -p --output-format json log (launcher lines may come first)."""
    try:
        text = Path(log).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    for raw in reversed(text.splitlines()):
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                d = json.loads(raw)
            except ValueError:
                continue
            if isinstance(d, dict) and ("total_cost_usd" in d or d.get("type") == "result"):
                return d
    return {}


def brief_budget(path):
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"^(?:projection_usd|budget_usd)\s*:\s*(\d+(?:\.\d+)?)\s*$", text, re.M) or \
        re.search(r"(?i)\b(?:projection|budget)\b[^\n\d]{0,30}?\$?(\d+(?:\.\d+)?)\s*USD", text)
    v = float(m.group(1)) if m else None
    return v if v else None


def normalise(swap, keep_as="orig"):
    stamp = time.strftime("%Y%m%d")
    for _ in range(5):  # a hand-written line appended meanwhile: start again
        before = SPEND.read_bytes()
        rows = []
        for raw in before.decode("utf-8", "replace").splitlines():
            if raw.strip():
                rows.append(normal(json.loads(raw)))  # an unreadable line stops it: nothing is swapped
        norm = SPEND.with_name(SPEND.name + ".norm")
        norm.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        back = [json.loads(x) for x in norm.read_text(encoding="utf-8").splitlines()]
        assert len(back) == len(rows) == len([x for x in before.decode().splitlines() if x.strip()])
        assert all(tuple(b) == KEYS for b in back), "a line without the schema's keys"
        assert all("tokens" not in b for b in back)
        if not swap:
            print(f"spend normalise: {len(back)} lines in {norm}, every one with the {len(KEYS)} keys")
            return norm
        if SPEND.read_bytes() != before:
            continue
        orig = SPEND.with_name(f"{SPEND.name}.{keep_as}-{stamp}")
        if orig.exists():
            sys.exit(f"spend normalise: {orig} exists already; nothing swapped")
        os.link(SPEND, orig)  # the old file kept as it was, then the new one moved in
        os.replace(norm, SPEND)
        print(f"spend normalise: {len(back)} lines swapped in; the old file kept as {orig}")
        return SPEND
    sys.exit("spend normalise: the log kept changing; nothing swapped")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("record", "from-log", "add-helper"):
        s = sub.add_parser(name)
        helper = name == "add-helper"  # an in-session helper: the model, effort and class are all required
        s.add_argument("--model", required=helper, help="the model as named at the spawn (DEC-1120 (3))")
        s.add_argument("--class", dest="klass", required=helper, choices=CLASSES, help="criticality class C0..C3")
        s.add_argument("--promoted", help="the recorded reason, when the spawn is a promotion")
        if helper:
            s.add_argument("--effort", required=True)
            s.add_argument("--role", required=True)
            s.add_argument("--what", required=True)
            for k in ("ticket", "wbs", "note"):
                s.add_argument("--" + k)
            s.add_argument("--cost-usd", type=float)
            s.add_argument("--projection-usd", type=float)
            for k in ("output-tokens", "cache-read-tokens", "cache-creation-tokens", "input-tokens"):
                s.add_argument("--" + k, type=int)
            s.add_argument("--extra", action="append", default=[], help="key=value, kept in extra")
            continue
        if name == "from-log":
            s.add_argument("log")
            s.add_argument("--exit")
            s.add_argument("--effort")
        s.add_argument("--what", required=True)
        s.add_argument("--kind", required=True)
        for k in ("ticket", "wbs", "role", "note"):
            s.add_argument("--" + k)
        for k in ("cost-usd", "projection-usd"):
            s.add_argument("--" + k, type=float)
        for k in ("output-tokens", "cache-read-tokens", "cache-creation-tokens", "input-tokens"):
            s.add_argument("--" + k, type=int)
        s.add_argument("--extra", action="append", default=[], help="key=value, kept in extra")
    sub.add_parser("check")
    s = sub.add_parser("clear")
    s.add_argument("wbs")
    s.add_argument("--projection-usd", type=float)
    s.add_argument("--note")
    sub.add_parser("sum")
    s = sub.add_parser("brief-budget")
    s.add_argument("brief")
    s = sub.add_parser("normalise")
    s.add_argument("--swap", action="store_true")
    s.add_argument("--keep-as", default="orig", help="the kept file's suffix word (orig, or pre-repair for a re-run)")
    a = ap.parse_args()
    if a.cmd in ("record", "from-log", "add-helper"):
        if a.cmd == "add-helper":
            a.kind = "agent"
        for what, v in (("--model", a.model), ("--promoted", a.promoted)):
            if v is not None and not v.strip():
                sys.exit(f"spend: {what} is empty")
        d = {"at": now_s(), "what": a.what, "kind": a.kind, "ticket": a.ticket, "wbs": a.wbs, "role": a.role,
             "cost_usd": a.cost_usd, "projection_usd": a.projection_usd, "note": a.note,
             "output_tokens": a.output_tokens, "cache_read_tokens": a.cache_read_tokens,
             "cache_creation_tokens": a.cache_creation_tokens, "input_tokens": a.input_tokens,
             "cost_source": "given" if a.cost_usd is not None else None,
             "model": a.model, "class": a.klass, "tier": tier_of(a.model), "promoted": a.promoted}
        extra = dict(x.split("=", 1) for x in a.extra if "=" in x)
        if a.cmd == "add-helper":
            extra["effort"] = a.effort
        if a.cmd == "from-log":
            r = from_log(a.log)
            u = r.get("usage") or {}
            d.update(cost_usd=num(r.get("total_cost_usd")), input_tokens=u.get("input_tokens"),
                     output_tokens=u.get("output_tokens"), cache_read_tokens=u.get("cache_read_input_tokens"),
                     cache_creation_tokens=u.get("cache_creation_input_tokens"),
                     cost_source="the session's total_cost_usd" if r.get("total_cost_usd") is not None
                     else "none in the log")
            extra.update({k: v for k, v in (("exit", a.exit), ("effort", a.effort), ("log", a.log),
                                            ("session_id", r.get("session_id")), ("num_turns", r.get("num_turns")),
                                            ("is_error", r.get("is_error")),
                                            ("api_error_status", r.get("api_error_status"))) if v is not None})
        d["extra"] = extra or None
        print(json.dumps(append(d)))
    elif a.cmd == "check":
        check()
    elif a.cmd == "clear":
        clear(a.wbs, a.projection_usd, a.note)
    elif a.cmd == "sum":
        for w, e in sorted(totals(load()).items()):
            state = "BRAKED" if (BRAKES / f"{w}.json").exists() else "ok"
            proj = f"{e['projection']:.2f}" if e["projection"] else "none (never braked)"
            print(f"{w}: {e['cost']:.2f} USD since {e['since']}; projection {proj}; {e['launches']} launch(es); {state}")
    elif a.cmd == "brief-budget":
        v = brief_budget(a.brief)
        print("" if v is None else f"{v:g}")
    elif a.cmd == "normalise":
        normalise(a.swap, a.keep_as)


if __name__ == "__main__":
    main()
