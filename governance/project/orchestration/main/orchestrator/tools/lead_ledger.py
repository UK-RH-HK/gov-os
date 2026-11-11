#!/usr/bin/env python3
"""The lead ledger (the owner's order, chat 2026-11-11 ~18:45): one ledger of every lead run, built from the records
that exist, read-only on everything except its own output (log/lead-ledger.jsonl, rebuilt whole on each call).

Per run: start and end; each phase (tests, build, review, verify, land) and each worker's time; the waiting and what
for (a launch refusal, a brake, a PACKAGES return, a review round, a merge conflict the return names, the CTO's notes,
else "unattributed": a cause is never guessed); the memory peak and which source gave it; the cost (the lead's own
total_cost_usd plus its workers'); the time against an estimate (the CTO's log/lead-estimates.json, then BATCH-PREP's
section 2 table) and a FLAG past 1.5 times that estimate, running or finished, with the reason taken from the waits.

Sources (all read-only; every time is UTC):
  dispatch/dispatch.log, dispatch/started.txt     starts ("started <W2> (<ticket>) <brief> -> <log> (launcher exit N)"),
                                                  "would start", "return:", "started but never ran", gate/stagger lines
  log/<log>.json                                  the lead's return (status: line, total_cost_usd, duration_ms, turns);
                                                  json raw_decode, the last object that holds a result
  log/<W2>-<yyyymmdd>-<hhmm>-launch.txt           launch refusals (LAUNCH_NO_TEMPLATE, gate shut, empty brief ...)
  <worktrees>/<W2>[-tests]/.gov-runtime/scratch/lead/log/   launch_worker.sh's <name>.pid/.exit/.summary/.json and the
                                                  lead's own steps (accept, rebuild, reds-alone, verify/ ...), CHECKPOINT.md
  log/spend.jsonl                                 workers' cost, their end time (minute), brake and brake-clear rows
  log/brake/                                      brake files (current) and brake/cleared/
  log/lead-hour-watch.jsonl, log/lead-mem.jsonl, log/lead-mem-watch.jsonl   the memory samples
  log/lead-ledger-notes.jsonl                     the CTO's free-text waits: {"at","W2","run","wait","minutes","note"}
  log/lead-estimates.json                         {"<W2>:<run>": {"hours": x | [lo, hi], "usd": y | null, "source": "..."}}
  drafts/batch-prep/BATCH-PREP.md                 section 2's table: the hours and cost columns, for runs after its date

Phases by name: td-*/designer = tests; eng-*/en-* = build; rev-*/review-*/rv-*/probe-* = review; verify/ (the folder),
accept*, rebuild*, reds-alone, scoped*, select*, collect*, parallel*, serial*, check*, govcheck*, trailers*, keywords* =
verify; merge*/land* = land; anything else = other.

Usage: lead_ledger.py [--md] [--since <iso>|all] [--root <orchestrator dir>] [--wt <worktrees dir>] [--out <jsonl>]
                      [--now <iso>] [--est-basis hi|mid|lo] [--no-write]
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
WT = "/home/usain/gov-os-worktrees"
FLAG_RATIO = 1.5
GAP_MIN = 5.0          # a gap between workers shorter than this is not listed
MIN_WAIT_MIN = 1.0     # an admission wait ("would start" to "started") shorter than this is not listed
FILE_EXTS = ("json", "pid", "exit", "summary", "start", "err", "out", "log", "txt", "xml", "disk", "args", "entries", "diff")
WORKER_KINDS = ("launched", "worker", "launched worker")
PHASE_RULES = (
    ("tests", r"^(td|designer|tests?-design|test-designer)(?![a-z])"),
    ("build", r"^(eng|en|engineer)(?![a-z])"),
    ("review", r"^(rev|review|rv|probe|audit)(?![a-z])"),
    ("land", r"^(merge|land)"),
    ("verify", r"^(verify|accept|reds|rebuild|scoped|select|collect|parallel|serial|check|govcheck|trailers|keywords|sigign)"),
)


# ------------------------------------------------------------------ small helpers
def utc_from_ts(ts):
    return datetime.fromtimestamp(ts, timezone.utc).replace(tzinfo=None)


def mtime(path):
    try:
        return utc_from_ts(os.stat(path).st_mtime)
    except OSError:
        return None


def size(path):
    try:
        return os.stat(path).st_size
    except OSError:
        return -1


def parse_t(s):
    """A naive UTC datetime from '2026-11-11 18:08:07', '2026-11-11T18:08', '...+00:00' or 'Sun Nov  1 19:19:56 GMT 2026'."""
    if s is None:
        return None
    s = str(s).strip()
    m = re.match(r"^(\d{4})-(\d\d)-(\d\d)(?:[T ](\d\d):(\d\d)(?::(\d\d))?)?(?![\d:])", s)
    if m:
        y, mo, d, h, mi, se = (int(x) if x else 0 for x in m.groups())
        return datetime(y, mo, d, h, mi, se)
    try:
        return datetime.strptime(" ".join(s.split()), "%a %b %d %H:%M:%S GMT %Y")
    except ValueError:
        return None


def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def minutes(a, b):
    return round((b - a).total_seconds() / 60.0, 1)


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def read_jsonl(path, since_str=None):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if since_str:
                    m = re.search(r'"(?:at|t)": "(\d{4}-\d\d-\d\d[ T]\d\d:\d\d)', line)
                    if m and m.group(1).replace("T", " ") < since_str:
                        continue
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return out


def load_result(path):
    """The last JSON object in a log that holds a result (some logs hold two objects or trailing text); None if none."""
    text = read_text(path)
    if not text.strip():
        return None
    dec, objs, i, rx = json.JSONDecoder(), [], 0, re.compile(r"[\{\[]")
    while True:
        m = rx.search(text, i)
        if not m:
            break
        try:
            obj, end = dec.raw_decode(text, m.start())
        except ValueError:
            if objs:
                break
            i = m.start() + 1
            continue
        objs.append(obj)
        i = end
    flat = []
    for o in objs:
        if isinstance(o, list):
            flat.extend(x for x in o if isinstance(x, dict))
        elif isinstance(o, dict):
            flat.append(o)
    res = [o for o in flat if o.get("type") == "result" or "total_cost_usd" in o or "result" in o]
    return (res or flat or [None])[-1]


def status_line(result_text):
    m = re.search(r"(?im)^[\s*_>#-]*status[\s*_]*:[\s*_]*([A-Za-z_]+)", result_text or "")
    return m.group(1).upper() if m else None


def union_minutes(ivs):
    tot, cs, ce = 0.0, None, None
    for s, e in sorted(ivs):
        if ce is None or s > ce:
            if ce is not None:
                tot += (ce - cs).total_seconds()
            cs, ce = s, e
        else:
            ce = max(ce, e)
    if ce is not None:
        tot += (ce - cs).total_seconds()
    return round(tot / 60.0, 1)


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return True


def phase_of(base, sub=""):
    if sub == "verify":
        return "verify"
    name = base.lower()
    for ph, rx in PHASE_RULES:
        if re.match(rx, name):
            return ph
    return "other"


# ------------------------------------------------------------------ the ledger
class Ledger:
    def __init__(self, root=ROOT, wt=WT, now=None, since=None, est_basis="hi", alive=pid_alive):
        self.root, self.wt, self.alive, self.est_basis = root, wt, alive, est_basis
        self.now = now or datetime.now(timezone.utc).replace(tzinfo=None)
        self.since = since or datetime(self.now.year, self.now.month, self.now.day)
        self.log = os.path.join(root, "log")
        self.disp = os.path.join(root, "dispatch")
        self._items = {}
        self._mem = None

    # --- dispatcher records
    def parse_dispatch(self):
        starts, would, returns, never, gates = [], {}, {}, [], []
        rx_start = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) started (\S+) \((\S+)\) (\S+) -> (\S+) \(launcher exit (\d+)\)")
        rx_would = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) would start (\S+) \((\S+)\) (\S+) -> (\S+)")
        rx_ret = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) return: (\S+) -> (\S+)")
        rx_never = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) started but never ran: (\S+) (\S+)")
        rx_gate = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (.*\b(?:gate|stagger)\b.*)", re.I)
        for line in read_text(os.path.join(self.disp, "dispatch.log")).splitlines():
            m = rx_start.match(line)
            if m:
                t = parse_t(m.group(1))
                w = would.get((m.group(2), m.group(5)))
                starts.append({"W2": m.group(2), "ticket": m.group(3), "brief": m.group(4), "log": m.group(5),
                               "start": t, "launcher_exit": int(m.group(6)), "source": "dispatch.log",
                               "would_start": w if w and timedelta(0) <= t - w <= timedelta(minutes=10) else None})
                continue
            m = rx_would.match(line)
            if m:
                would[(m.group(2), m.group(5))] = parse_t(m.group(1))
                continue
            m = rx_ret.match(line)
            if m:
                returns.setdefault(m.group(2), []).append(parse_t(m.group(1)))
                continue
            m = rx_never.match(line)
            if m:
                never.append((parse_t(m.group(1)), m.group(2), m.group(3)))
                continue
            m = rx_gate.match(line)
            if m and "guard refusals" not in line and "embedding server" not in line and "gpu " not in line[:30]:
                gates.append((parse_t(m.group(1)), m.group(2)))
        for line in read_text(os.path.join(self.disp, "started.txt")).splitlines():
            f = line.split()
            if len(f) < 5:
                continue
            t = parse_t(f[0] + " " + f[1])
            if t is None:
                continue
            if any(s["log"] == f[4] and abs((s["start"] - t).total_seconds()) < 180 for s in starts):
                continue
            starts.append({"W2": f[2], "ticket": None, "brief": f[3], "log": f[4], "start": t, "launcher_exit": None,
                           "source": "started.txt", "would_start": None})
        # return logs no start record names (chained launches before the dispatcher): start from the log's duration
        known = {s["log"] for s in starts}
        for p in glob.glob(os.path.join(self.log, "*-A5-*.json")):
            name = os.path.basename(p)
            if name in known or size(p) <= 0:
                continue
            mt = mtime(p)
            if mt is None or mt < self.since:
                continue
            res = load_result(p) or {}
            dur = res.get("duration_ms")
            st = mt - timedelta(milliseconds=dur) if isinstance(dur, (int, float)) else mt
            starts.append({"W2": name.split("-A5-")[0], "ticket": None, "brief": None, "log": name, "start": st,
                           "launcher_exit": None, "source": "return log only", "would_start": None})
        starts.sort(key=lambda s: s["start"])
        return starts, returns, never, gates

    def status_leads(self):
        try:
            with open(os.path.join(self.disp, "status.json")) as f:
                d = json.load(f)
            t = parse_t(d.get("time"))
            return set(d.get("leads") or []), t
        except (OSError, ValueError):
            return set(), None

    def launch_file(self, w2, start):
        for dm in (0, 1, -1):
            t = start + timedelta(minutes=dm)
            p = os.path.join(self.log, f"{w2}-{t:%Y%m%d-%H%M}-launch.txt")
            if os.path.exists(p):
                return p, read_text(p)
        return None, ""

    @staticmethod
    def refusal(text):
        for rx, why in ((r"LAUNCH_NO_TEMPLATE", "LAUNCH_NO_TEMPLATE: role template missing"),
                        (r"(?i)disk gate is shut|gate is shut|gate shut", "gate shut"),
                        (r"Input must be provided", "empty brief (Input must be provided)"),
                        (r"(?i)runaway brake", "runaway brake"),
                        (r"REFUSED", "REFUSED"),
                        (r"(?m)^Error: ", None)):
            m = re.search(rx, text)
            if m:
                if why:
                    return why
                return re.search(r"(?m)^Error: .*", text).group(0)[:90]
        return None

    # --- the runs
    def build(self):
        starts, returns, never, gates = self.parse_dispatch()
        leads, status_time = self.status_leads()
        by_w2 = {}
        for s in starts:
            by_w2.setdefault(s["W2"], []).append(s)
        latest_for_log = {}
        for s in starts:
            latest_for_log[s["log"]] = s
        runs = [s for s in starts if s["start"] >= self.since]
        spend = read_jsonl(os.path.join(self.log, "spend.jsonl"), (self.since - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
        self.spend = spend
        used_spend = set()
        for r in runs:
            w2 = r["W2"]
            r["run"] = re.sub(r"^" + re.escape(w2) + r"-A5-", "", r["log"][:-5] if r["log"].endswith(".json") else r["log"])
            later = [x for x in by_w2[w2] if x["start"] > r["start"]]
            r["next_start"] = later[0]["start"] if later else None
            lp, ltext = self.launch_file(w2, r["start"])
            r["launch_file"] = lp
            r["refusal"] = self.refusal(ltext)
            jp = os.path.join(self.log, r["log"])
            has_json = latest_for_log.get(r["log"]) is r and size(jp) > 0
            res = load_result(jp) if has_json else None
            r["lead"] = {}
            r["result_text"] = ""
            r["end"] = None
            r["status"] = None
            r["running_source"] = None
            if res and ("result" in res or "total_cost_usd" in res):
                rt = res.get("result") if isinstance(res.get("result"), str) else ""
                r["result_text"] = rt
                r["lead"] = {"cost_usd": res.get("total_cost_usd"), "duration_ms": res.get("duration_ms"),
                             "num_turns": res.get("num_turns")}
                st = status_line(rt)
                if res.get("is_error"):
                    st = "ERROR" + (f" ({st})" if st else "")
                r["status"] = st or "NO_STATUS"
                r["end"] = mtime(jp)
            elif r["refusal"]:
                r["status"], r["end"] = "REFUSED", r["start"]
            elif any(n[1] == w2 and n[2] == r["log"] and n[0] >= r["start"] for n in never) or \
                    (not has_json and latest_for_log.get(r["log"]) is not r):
                r["status"], r["end"] = "NEVER_RAN", r["start"]
            else:
                fresh = status_time is not None and abs((self.now - status_time).total_seconds()) < 15 * 60
                if fresh and w2 in leads:
                    r["status"], r["running_source"] = "RUNNING", "dispatch/status.json"
                elif not fresh and (self.now - r["start"]) < timedelta(hours=12) and not returns.get(r["log"]):
                    r["status"], r["running_source"] = "RUNNING", "no return record (status.json stale)"
                else:
                    r["status"], r["end"] = "NO_RETURN", r["start"]
            r["running"] = r["status"] == "RUNNING"
        # items (workers and steps) per W2, assigned to the one run whose window holds them
        for w2 in sorted({r["W2"] for r in runs}):
            self.assign_items(w2, [r for r in runs if r["W2"] == w2], used_spend)
        notes = read_jsonl(os.path.join(self.log, "lead-ledger-notes.jsonl"))
        brakes = self.brake_intervals(spend)
        for r in runs:
            self.finish_run(r, gates, notes, brakes, runs)
        self.chains(runs)
        return runs, notes

    # --- workers and steps of one W2
    def scan_items(self, w2):
        if w2 in self._items:
            return self._items[w2]
        items = []
        for d in (w2, w2 + "-tests"):
            logdir = os.path.join(self.wt, d, ".gov-runtime", "scratch", "lead", "log")
            if not os.path.isdir(logdir):
                continue
            folders = [("", logdir)] + [(n, os.path.join(logdir, n)) for n in sorted(os.listdir(logdir))
                                        if os.path.isdir(os.path.join(logdir, n))]
            for sub, folder in folders:
                groups = {}
                for fn in os.listdir(folder):
                    m = re.match(r"^(.+)\.([a-z]+)$", fn)
                    if not m or m.group(2) not in FILE_EXTS or ".tripwire" in m.group(1):
                        continue
                    groups.setdefault(m.group(1), {})[m.group(2)] = os.path.join(folder, fn)
                for base, fs in groups.items():
                    if not any(k in fs for k in ("pid", "exit", "summary")):
                        continue
                    items.append(self.make_item(d, sub, base, fs))
        self._items[w2] = items
        return items

    def make_item(self, tree, sub, base, fs):
        it = {"name": (sub + "/" if sub else "") + base, "base": base, "tree": tree, "phase": phase_of(base, sub),
              "worker": "pid" in fs and "json" in fs, "approx": None, "source": "worktree log"}
        t_exit = mtime(fs["exit"]) if "exit" in fs else None
        t_json = mtime(fs["json"]) if "json" in fs and size(fs["json"]) > 0 else None
        start = None
        if "start" in fs:
            start = parse_t(read_text(fs["start"])) or mtime(fs["start"])
        for k in ("disk", "err", "pid"):
            if start is None and k in fs:
                start = mtime(fs[k])
        res = load_result(fs["json"]) if "json" in fs and size(fs["json"]) > 0 else None
        cost = dur = turns = None
        if isinstance(res, dict) and "total_cost_usd" in res:
            cost, dur, turns = res.get("total_cost_usd"), res.get("duration_ms"), res.get("num_turns")
        end = t_exit or t_json
        it["exit_code"] = None
        if "exit" in fs:
            txt = read_text(fs["exit"]).strip()
            it["exit_code"] = int(txt) if txt.isdigit() else txt[:20] or None
        running = False
        if end is None and "pid" in fs:
            pid_txt = read_text(fs["pid"]).strip()
            pid = int(pid_txt) if pid_txt.isdigit() else None
            if pid and self.alive(pid) and (mtime(fs["pid"]) is None or self.now - mtime(fs["pid"]) < timedelta(hours=12)):
                running = True
            else:
                end = max([t for t in (mtime(p) for p in fs.values()) if t] or [None])
        it.update({"start": start, "end": end, "running": running, "cost_usd": cost, "duration_ms": dur, "turns": turns,
                   "_base_json": base + ".json", "_spend": None})
        if dur and end and (start is None or abs((end - start).total_seconds() - dur / 1000.0) > 120):
            it["start"], it["approx"] = end - timedelta(milliseconds=dur), "start from duration_ms"
        return it

    def assign_items(self, w2, runs, used_spend):
        items = self.scan_items(w2)
        rows = [x for x in self.spend if x.get("wbs") == w2 and x.get("kind") in WORKER_KINDS]
        # reconcile each file item with its spend row (cost when the json is missing; the end when the files were copied)
        for it in items:
            best = None
            end = it["end"]
            for i, x in enumerate(rows):
                if i in used_spend or id(x) in used_spend:
                    continue
                if os.path.basename((x.get("extra") or {}).get("log") or "") != it["_base_json"]:
                    continue
                at = parse_t(x.get("at"))
                if at is None:
                    continue
                ref = end or it["start"] or self.now
                d = abs((ref - at).total_seconds())
                if d < 30 * 60 and (best is None or d < best[0]):
                    best = (d, x, at)
            if best:
                _, x, at = best
                used_spend.add(id(x))
                it["_spend"] = x
                if it["cost_usd"] is None:
                    it["cost_usd"] = x.get("cost_usd")
                if it["turns"] is None:
                    it["turns"] = (x.get("extra") or {}).get("num_turns")
                if end is not None and not (at - timedelta(seconds=5) <= end <= at + timedelta(seconds=150)):
                    new_end = at + timedelta(seconds=30)
                    it["end"] = new_end
                    it["approx"] = "end from spend.jsonl (the files' times do not fit)"
                    if it["duration_ms"]:
                        it["start"] = new_end - timedelta(milliseconds=it["duration_ms"])
        for x in rows:
            if id(x) in used_spend:
                continue
            at = parse_t(x.get("at"))
            if at is None:
                continue
            nm = os.path.basename((x.get("extra") or {}).get("log") or x.get("what") or "worker")
            nm = nm[:-5] if nm.endswith(".json") else nm
            used_spend.add(id(x))
            items.append({"name": nm, "base": nm, "tree": None, "phase": phase_of(nm), "worker": True,
                          "approx": "spend.jsonl only (no log in the worktrees)", "source": "spend.jsonl", "start": None,
                          "end": at + timedelta(seconds=30), "running": False, "cost_usd": x.get("cost_usd"),
                          "duration_ms": None, "turns": (x.get("extra") or {}).get("num_turns"), "exit_code": None,
                          "_base_json": nm + ".json", "_spend": x})
        for r in runs:
            r["items"] = []
        real = [r for r in runs if r["status"] not in ("REFUSED", "NEVER_RAN", "NO_RETURN")]
        for it in items:
            ie = it["end"] or self.now
            isx = it["start"] or ie
            if it["start"] is None and it["end"] is None:
                continue
            cands = []
            for r in real:
                re_ = r["end"] or self.now
                if ie >= r["start"] - timedelta(seconds=60) and isx <= re_ + timedelta(seconds=150):
                    cands.append(r)
            if cands:
                max(cands, key=lambda r: r["start"])["items"].append(it)

    # --- brakes
    def brake_intervals(self, spend):
        out = []
        rows = sorted([x for x in spend if x.get("kind") in ("brake", "brake-clear") and x.get("wbs")], key=lambda x: x.get("at") or "")
        open_ = {}
        cleared = []
        for p in glob.glob(os.path.join(self.log, "brake", "cleared", "*.json")):
            m = re.match(r"^(.+)-(\d{8})-(\d{6})\.json$", os.path.basename(p))
            if m:
                cleared.append((m.group(1), datetime.strptime(m.group(2) + m.group(3), "%Y%m%d%H%M%S"), p))
        for x in rows:
            w2, at = x["wbs"], parse_t(x.get("at"))
            if x["kind"] == "brake":
                open_[w2] = (at, x.get("what") or "runaway brake")
            elif w2 in open_:
                bs, what = open_.pop(w2)
                be = at
                for cw, ct, _ in cleared:
                    if cw == w2 and abs((ct - at).total_seconds()) < 300:
                        be = ct
                out.append({"W2": w2, "from": bs, "to": be, "cause": f"runaway brake ({what}), cleared by the CTO"})
        for w2, (bs, what) in open_.items():
            p = os.path.join(self.log, "brake", w2 + ".json")
            if os.path.exists(p):
                out.append({"W2": w2, "from": bs, "to": self.now, "cause": f"runaway brake ({what}), still on"})
        for p in glob.glob(os.path.join(self.log, "brake", "*.json")):
            w2 = os.path.basename(p)[:-5]
            if any(o["W2"] == w2 and o["to"] == self.now for o in out):
                continue
            try:
                d = json.load(open(p))
            except (OSError, ValueError):
                d = {}
            bs = parse_t(d.get("at")) or mtime(p)
            out.append({"W2": w2, "from": bs, "to": self.now,
                        "cause": f"brake file ({str(d.get('brake') or d.get('why') or 'no reason in the file')[:60]}), still on"})
        return out

    # --- one run's waits, phases, memory, cost
    def finish_run(self, r, gates, notes, brakes, runs):
        w2, now = r["W2"], self.now
        end_eff = r["end"] or now
        items = sorted(r["items"], key=lambda i: (i["start"] or i["end"] or now))
        waits = []
        # launch refusal, never ran, before-start admission
        if r["status"] in ("REFUSED", "NEVER_RAN", "NO_RETURN"):
            to = r["next_start"] or now
            cause = r["refusal"] or {"NEVER_RAN": "started but never ran (no process, no return)",
                                     "NO_RETURN": "no return and no process"}[r["status"]]
            waits.append({"kind": "launch refusal" if r["refusal"] else "launch lost", "cause": cause,
                          "minutes": minutes(r["start"], to), "from": fmt(r["start"]), "to": fmt(to) if r["next_start"] else None,
                          "open": r["next_start"] is None, "source": os.path.basename(r["launch_file"] or "dispatch.log")})
        if r.get("would_start") and minutes(r["would_start"], r["start"]) >= MIN_WAIT_MIN:
            waits.append({"kind": "admission", "cause": "the dispatcher's 'would start' to 'started' (gate or stagger)",
                          "minutes": minutes(r["would_start"], r["start"]), "from": fmt(r["would_start"]), "to": fmt(r["start"]),
                          "open": False, "source": "dispatch.log"})
        for t, line in gates:
            if w2 in line and r["start"] - timedelta(minutes=30) <= t <= r["start"]:
                waits.append({"kind": "gate/stagger line", "cause": line[:100], "minutes": minutes(t, r["start"]),
                              "from": fmt(t), "to": fmt(r["start"]), "open": False, "source": "dispatch.log"})
        # a return that leaves the work with the CTO or the owner
        if r["status"] and r["status"].split()[0] not in ("DONE", "RUNNING", "REFUSED", "NEVER_RAN", "NO_RETURN", "NO_STATUS") and r["end"]:
            to = r["next_start"] or now
            waits.append({"kind": "waiting on the CTO or the owner", "cause": f"{r['status']} return",
                          "minutes": minutes(r["end"], to), "from": fmt(r["end"]), "to": fmt(to) if r["next_start"] else None,
                          "open": r["next_start"] is None, "source": "return log status"})
        # brakes
        for b in brakes:
            if b["W2"] != w2:
                continue
            lo, hi = max(b["from"], r["start"]), min(b["to"], end_eff)
            if hi > lo:
                waits.append({"kind": "brake", "cause": b["cause"], "minutes": minutes(lo, hi), "from": fmt(lo), "to": fmt(hi),
                              "open": b["to"] == now, "source": "spend.jsonl / log/brake"})
        # review rounds, gaps
        ivs = []
        for it in items:
            if it["worker"] and it["phase"] == "review":
                mnt = minutes(it["start"], it["end"] or now) if it["start"] else None
                waits.append({"kind": "review round", "cause": it["name"], "minutes": mnt, "from": fmt(it["start"]),
                              "to": fmt(it["end"]), "open": it["running"], "source": "worker log"})
            if it["start"]:
                ivs.append((it["start"], it["end"] or now))
        ivs.sort()
        reach = None
        for s, e in ivs:
            if reach is not None and (s - reach).total_seconds() / 60.0 >= GAP_MIN:
                waits.append({"kind": "gap between workers", "cause": "unattributed", "minutes": minutes(reach, s),
                              "from": fmt(reach), "to": fmt(s), "open": False, "source": "worker log times"})
            reach = e if reach is None else max(reach, e)
        # a merge conflict the return names (minutes are not recorded)
        txt = r["result_text"] or ""
        if any(not m.group(1) for m in re.finditer(r"(?i)\b(no\s+|without\s+|0\s+)?merge conflicts?\b", txt)):
            waits.append({"kind": "merge conflict", "cause": "named in the return (the minutes are not recorded)",
                          "minutes": None, "from": None, "to": None, "open": False, "source": "return text"})
        # the CTO's notes
        for n in notes:
            if n.get("W2") != w2:
                continue
            at = parse_t(n.get("at"))
            match = (n.get("run") and n["run"] in (r["run"], r["log"])) or \
                    (not n.get("run") and at and r["start"] - timedelta(hours=1) <= at <= end_eff + timedelta(hours=1))
            if match:
                waits.append({"kind": str(n.get("wait") or "note"), "cause": str(n.get("note") or "")[:100] or "CTO note",
                              "minutes": n.get("minutes"), "from": n.get("at"), "to": None, "open": False,
                              "source": "CTO note"})
        r["waits"] = waits
        # phases
        phases = {}
        for ph in ("tests", "build", "review", "verify", "land", "other"):
            iv = [(i["start"], i["end"] or now) for i in items if i["phase"] == ph and i["start"]]
            if iv:
                phases[ph] = union_minutes(iv)
        r["phases"] = phases
        r["rev_rounds"] = sum(1 for i in items if i["worker"] and i["phase"] == "review")
        # cost
        lead_cost = r["lead"].get("cost_usd")
        wk = [i["cost_usd"] for i in items if i["worker"] and isinstance(i.get("cost_usd"), (int, float))]
        workers_cost = round(sum(wk), 4) if wk else 0.0
        r["cost"] = {"lead_usd": lead_cost, "workers_usd": workers_cost,
                     "total_usd": round((lead_cost or 0) + workers_cost, 4) if (lead_cost is not None or wk) else None,
                     "complete": lead_cost is not None}
        r["mem"] = ({"peak_mb": None, "source": None, "by_source": {}} if r["status"] in ("REFUSED", "NEVER_RAN", "NO_RETURN")
                    else self.mem_peak(r, end_eff))
        # the lead's checkpoint, for the last run of the W2 only
        r["checkpoint"] = None
        if r["running"] or r["next_start"] is None:
            cp = read_text(os.path.join(self.wt, w2, ".gov-runtime", "scratch", "lead", "CHECKPOINT.md"))
            st = re.search(r"(?m)^STATE:\s*(.*)$", cp)
            if st:
                wo = re.search(r"WAITING ON:\s*([^|\n]*)", st.group(1))
                r["checkpoint"] = {"state": st.group(1)[:200], "waiting_on": wo.group(1).strip() if wo else None}

    # --- memory
    def mem_sources(self):
        if self._mem is None:
            s = (self.since - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            hw = [(parse_t(x.get("at")), x.get("leads_mb") or {}) for x in read_jsonl(os.path.join(self.log, "lead-hour-watch.jsonl"), s)]
            lm = [(parse_t(x.get("t")), {k: v / 1024.0 for k, v in (x.get("leads_kb") or {}).items()})
                  for x in read_jsonl(os.path.join(self.log, "lead-mem.jsonl"), s)]
            mw = [(parse_t(x.get("at")), {k: (v.get("mb") if isinstance(v, dict) else v) for k, v in (x.get("leads") or {}).items()})
                  for x in read_jsonl(os.path.join(self.log, "lead-mem-watch.jsonl"), s)]
            self._mem = {"lead-hour-watch": hw, "lead-mem": lm, "lead-mem-watch": mw}
        return self._mem

    def mem_peak(self, r, end_eff):
        lo, hi = r["start"] - timedelta(seconds=60), end_eff + timedelta(seconds=60)
        by = {}
        for src, rows in self.mem_sources().items():
            key = r.get("ticket") if src == "lead-mem" else r["W2"]
            if not key:
                continue
            best, at, n = None, None, 0
            for t, d in rows:
                if t is None or not (lo <= t <= hi) or key not in d or d[key] is None:
                    continue
                n += 1
                if best is None or d[key] > best:
                    best, at = d[key], t
            if best is not None:
                by[src] = {"mb": int(round(best)), "at": fmt(at), "samples": n}
        if not by:
            return {"peak_mb": None, "source": None, "by_source": {}}
        src = max(by, key=lambda k: by[k]["mb"])
        return {"peak_mb": by[src]["mb"], "source": src, "by_source": by}

    # --- estimates and flags
    def load_estimates(self):
        ests = {}
        try:
            d = json.load(open(os.path.join(self.log, "lead-estimates.json")))
        except (OSError, ValueError):
            d = {}
        for k, v in d.items():
            if k.startswith("_") or not isinstance(v, dict):
                continue
            ests[k] = {"hours": v.get("hours"), "usd": v.get("usd"), "source": v.get("source") or "lead-estimates.json",
                       "by": v.get("by") or "CTO"}
        bp = {}
        path = os.path.join(self.root, "drafts", "batch-prep", "BATCH-PREP.md")
        text = read_text(path)
        m = re.search(r"Written (\d{4}-\d\d-\d\d) \(about (\d\d:\d\d)", text)
        bp_time = parse_t(f"{m.group(1)} {m.group(2)}") if m else mtime(path)
        sec = text.split("## 2.", 1)[1].split("\n## 3.", 1)[0] if "## 2." in text else ""
        for line in sec.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            km = re.match(r"(W[12]-[0-9]+[A-Za-z]?)\b", cells[0]) if cells else None
            if not km or len(cells) < 5:
                continue
            cost = cells[-1]
            h = re.search(r"(\d+(?:\.\d+)?)(?:\s*(?:-|–|to)\s*(\d+(?:\.\d+)?))?\s*h\b", cost)
            u = re.search(r"\$(\d+(?:\.\d+)?)(?:\s*(?:-|–|to)\s*\$?(\d+(?:\.\d+)?))?", cost)
            if not h:
                continue
            bp[km.group(1)] = {"hours": [float(h.group(1)), float(h.group(2) or h.group(1))],
                               "usd": [float(u.group(1)), float(u.group(2) or u.group(1))] if u else None,
                               "source": "BATCH-PREP §2 table", "by": "BATCH-PREP"}
        return ests, bp, bp_time

    @staticmethod
    def rng(v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return [float(v), float(v)]
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return [float(v[0]), float(v[1])]
        if isinstance(v, str):
            m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*$", v)
            if m:
                return [float(m.group(1)), float(m.group(2))]
            try:
                return [float(v), float(v)]
            except ValueError:
                return None
        return None

    def est_for(self, r, ests, bp, bp_time):
        run, w2 = r["run"], r["W2"]
        cands = [f"{w2}:{run}", f"{w2}:{re.sub(r'[0-9]+$', '', run)}"]
        tok = run.split("-")[-1]
        cands += [f"{w2}:{tok}", f"{w2}:{re.sub(r'[0-9]+$', '', tok)}"]
        for c in cands:
            if c in ests and self.rng(ests[c]["hours"]):
                e = ests[c]
                return {"key": c, "hours": self.rng(e["hours"]), "usd": self.rng(e["usd"]), "source": e["source"], "by": e["by"]}
        if w2 in bp and bp_time and r["start"] >= bp_time:
            e = bp[w2]
            return {"key": "BATCH-PREP:" + w2, "hours": e["hours"], "usd": e["usd"], "source": e["source"], "by": e["by"]}
        return None

    def basis(self, rg):
        return {"hi": rg[1], "lo": rg[0], "mid": (rg[0] + rg[1]) / 2.0}[self.est_basis]

    def chains(self, runs):
        ests, bp, bp_time = self.load_estimates()
        for r in runs:
            r["estimate"] = None
            r["flag"] = False
            r["flag_reason"] = None
            r["chain"] = None
        for w2 in sorted({r["W2"] for r in runs}):
            rs = sorted([r for r in runs if r["W2"] == w2], key=lambda r: r["start"])
            chains = []
            for r in rs:
                e = self.est_for(r, ests, bp, bp_time)
                if chains and e and chains[-1][0] == e["key"]:
                    chains[-1][2].append(r)
                else:
                    chains.append((e["key"] if e else None, e, [r]))
            for key, e, members in chains:
                for m in members:
                    m["chain"] = {"key": key, "runs": [x["run"] for x in members]} if key else None
                if not e:
                    continue
                last = members[-1]
                start = members[0]["start"]
                end = last["end"] if (last["end"] and not last["running"] and last["status"] not in ("REFUSED", "NEVER_RAN", "NO_RETURN")) else self.now
                elapsed_h = (end - start).total_seconds() / 3600.0
                active_h = sum(((x["end"] or self.now) - x["start"]).total_seconds() for x in members
                               if x["status"] not in ("REFUSED", "NEVER_RAN", "NO_RETURN")) / 3600.0
                est_h = self.basis(e["hours"])
                cost_total = sum((x["cost"]["total_usd"] or 0) for x in members)
                est = {"key": e["key"], "hours_lo": e["hours"][0], "hours_hi": e["hours"][1], "basis": self.est_basis,
                       "usd": e["usd"], "source": e["source"], "by": e["by"], "chain_runs": [x["run"] for x in members],
                       "chain_start": fmt(start), "elapsed_h": round(elapsed_h, 2), "active_h": round(active_h, 2),
                       "ratio_elapsed": round(elapsed_h / est_h, 2) if est_h else None,
                       "ratio_active": round(active_h / est_h, 2) if est_h else None,
                       "chain_cost_usd": round(cost_total, 2),
                       "ratio_cost": round(cost_total / self.basis(e["usd"]), 2) if e["usd"] and self.basis(e["usd"]) else None}
                last["estimate"] = est
                over_e = est["ratio_elapsed"] is not None and est["ratio_elapsed"] > FLAG_RATIO
                over_a = est["ratio_active"] is not None and est["ratio_active"] > FLAG_RATIO
                if over_e or over_a:
                    last["flag"] = True
                    last["flag_reason"] = self.reason(members, est, over_e, over_a, start, end)

    @staticmethod
    def hours_txt(h):
        return f"{h:.1f} h"

    def reason(self, members, est, over_e, over_a, start, end):
        est_txt = f"{est['hours_lo']:g}" + (f"-{est['hours_hi']:g}" if est["hours_hi"] != est["hours_lo"] else "") + " h"
        head = (f"elapsed {est['elapsed_h']:.1f} h = {est['ratio_elapsed']:.1f}x of the {est_txt} estimate "
                f"({est['by']}, {est['basis']} end); active {est['active_h']:.1f} h = {est['ratio_active']:.1f}x")
        ws = []
        for m in members:
            for w in m["waits"]:
                if w["minutes"] is None:
                    ws.append((0, f"{w['kind']}: {w['cause']} (minutes not recorded)"))
                elif w["kind"] != "review round":
                    ws.append((w["minutes"], f"{w['minutes']:.0f} min {w['kind']}: {w['cause']}" + (" (still open)" if w["open"] else "")))
        ws.sort(key=lambda x: -x[0])
        explained = sum(m for m, _ in ws)
        total_min = est["elapsed_h"] * 60 - est["active_h"] * 60
        txt = head + (". Waits: " + "; ".join(t for _, t in ws[:4]) if ws else ". No wait is recorded")
        if not ws and over_a:
            txt += ": the time is the run's own working time"
        gap = total_min - explained
        if gap > max(10.0, 0.2 * total_min):
            txt += f". Unattributed: {gap:.0f} min of the {total_min:.0f} min not in a run"
        if not over_e and over_a:
            txt += ". Over on active time"
        return txt

    # --- output
    def rows(self, runs):
        out = []
        for r in sorted(runs, key=lambda r: r["start"]):
            items = []
            for i in sorted(r["items"], key=lambda i: (i["start"] or i["end"] or self.now)):
                items.append({"name": i["name"], "phase": i["phase"], "worker": i["worker"], "start": fmt(i["start"]),
                              "end": fmt(i["end"]), "running": i["running"],
                              "minutes": minutes(i["start"], i["end"] or self.now) if i["start"] else None,
                              "cost_usd": i.get("cost_usd"), "turns": i.get("turns"), "exit": i.get("exit_code"),
                              "note": i.get("approx"), "source": i["source"]})
            end_m = minutes(r["start"], r["end"] or self.now)
            out.append({
                "W2": r["W2"], "run": r["run"], "ticket": r["ticket"], "log": r["log"], "brief": r["brief"],
                "start": fmt(r["start"]), "end": fmt(r["end"]) if not r["running"] else None, "running": r["running"],
                "status": r["status"], "launcher_exit": r["launcher_exit"], "refusal": r["refusal"],
                "wall_minutes": end_m, "lead": r["lead"], "workers": items, "phases_min": r["phases"],
                "rev_rounds": r["rev_rounds"], "waits": r["waits"], "mem": r["mem"], "cost": r["cost"],
                "estimate": r["estimate"], "chain": r["chain"], "flag": r["flag"], "flag_reason": r["flag_reason"],
                "checkpoint": r["checkpoint"], "running_source": r["running_source"], "start_source": r["source"],
                "built_at": fmt(self.now)})
        return out


# ------------------------------------------------------------------ the digest table
def short_t(s, now):
    if not s:
        return "-"
    return s[11:16] if s[:10] == fmt(now)[:10] else s[5:16]


def md(rows, now):
    def waits_txt(r):
        agg = {}
        for w in r["waits"]:
            if w["kind"] == "review round":
                continue
            k = (w["kind"], w["cause"])
            a = agg.setdefault(k, [0.0, False, False])
            if w["minutes"] is None:
                a[1] = True
            else:
                a[0] += w["minutes"]
            a[2] = a[2] or w["open"]
        parts = [f"{k[0]} {('%.0f' % a[0]) if not a[1] or a[0] else '?'}{'+' if a[2] else ''} min ({k[1][:44]})" for k, a in agg.items()]
        rv = [w for w in r["waits"] if w["kind"] == "review round"]
        if rv:
            parts.append(f"review rounds {len(rv)} ({sum(w['minutes'] or 0 for w in rv):.0f} min)")
        return "; ".join(parts) or "none recorded"

    def cost_txt(r):
        c = r["cost"]
        if c["total_usd"] is None:
            return "-"
        s = f"{c['total_usd']:.2f}"
        if c["workers_usd"]:
            s += f" (L {c['lead_usd'] or 0:.2f} + W {c['workers_usd']:.2f})"
        return s + ("" if c["complete"] else " so far")

    def est_txt(r):
        e = r["estimate"]
        if not e:
            return "-"
        rg = f"{e['hours_lo']:g}" + (f"-{e['hours_hi']:g}" if e["hours_hi"] != e["hours_lo"] else "")
        s = f"{e['elapsed_h']:.1f} h of {rg} h = {e['ratio_elapsed']:.2f}x"
        if len(e["chain_runs"]) > 1 or abs(e["elapsed_h"] - e["active_h"]) > 0.05:
            s += f" (active {e['active_h']:.1f} h = {e['ratio_active']:.2f}x)"
        return s + (" [CTO est.]" if e["by"] == "CTO" else " [BATCH-PREP]")

    def mem_txt(r):
        m = r["mem"]
        return f"{m['peak_mb']} {{{m['source'].replace('lead-hour-watch', 'hw').replace('lead-mem-watch', 'mw').replace('lead-mem', 'lm')}}}" if m["peak_mb"] is not None else "no sample"

    lines = ["| W2 | run | start | end | status | phases (min) | waits (min, cause) | peak MB | cost USD | time vs estimate | FLAG |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        ph = ", ".join(f"{k} {v:g}" for k, v in r["phases_min"].items()) or "-"
        end = "running" if r["running"] else short_t(r["end"], now)
        lines.append(f"| {r['W2']} | {r['run']} | {short_t(r['start'], now)} | {end} | {r['status']} | {ph} | {waits_txt(r)} | "
                     f"{mem_txt(r)} | {cost_txt(r)} | {est_txt(r)} | {'FLAG' if r['flag'] else ''} |")
    flags = [r for r in rows if r["flag"]]
    lines.append("")
    if flags:
        lines.append(f"FLAGS (past {FLAG_RATIO:g}x of the estimate):")
        for r in flags:
            lines.append(f"- {r['W2']} {r['run']}: {r['flag_reason']}")
    else:
        lines.append(f"FLAGS: none past {FLAG_RATIO:g}x of the estimate.")
    nt = [r for r in rows if any(w["open"] and w["kind"].startswith("waiting") for w in r["waits"])]
    for r in nt:
        w = [w for w in r["waits"] if w["open"] and w["kind"].startswith("waiting")][0]
        lines.append(f"- open: {r['W2']} {r['run']} returned {r['status']} at {short_t(r['end'], now)}; waiting on the CTO or the owner {w['minutes']:.0f} min so far")
    lines.append("")
    lines.append("Phases by worker name: td-* = tests; eng-* = build; rev-*/probe-* = review; verify/, accept, rebuild, reds-alone, "
                 "scoped = verify; merge*/land* = land. Phase minutes are wall time (parallel workers once). Times UTC; "
                 "a worker's end can be off by a minute (spend.jsonl is in minutes); a lead's own step with no start file has no minutes. Peak MB {hw} lead-hour-watch (per worktree), "
                 "{lm} lead-mem (per ticket's process tree), {mw} lead-mem-watch. Waits: '+' = still open; a cause is "
                 "'unattributed' when no record names it; a review round is the lead waiting on its reviewer.")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The lead ledger: one row per lead run, rebuilt whole on each call.")
    ap.add_argument("--md", action="store_true", help="print the compact table for the digest")
    ap.add_argument("--since", default=None, help="an ISO time, or 'all' (default: the start of today, UTC)")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--wt", default=WT)
    ap.add_argument("--out", default=None, help="the jsonl (default: <root>/log/lead-ledger.jsonl)")
    ap.add_argument("--now", default=None, help="the clock, ISO (tests)")
    ap.add_argument("--est-basis", choices=("hi", "mid", "lo"), default="hi", help="which end of an estimate range the ratio uses")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    now = parse_t(a.now) if a.now else None
    since = datetime(2000, 1, 1) if a.since == "all" else (parse_t(a.since) if a.since else None)
    if a.since and since is None:
        print("lead_ledger: not a time: " + a.since, file=sys.stderr)
        return 2
    led = Ledger(a.root, a.wt, now=now, since=since, est_basis=a.est_basis)
    runs, _ = led.build()
    rows = led.rows(runs)
    out = a.out or os.path.join(a.root, "log", "lead-ledger.jsonl")
    if not a.no_write:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        tmp = out + ".tmp"
        with open(tmp, "w") as f:
            for r in rows:
                f.write(json.dumps(r, default=str) + "\n")
        os.replace(tmp, out)
    if a.md:
        print(md(rows, led.now))
    else:
        print(f"lead_ledger: {len(rows)} runs since {fmt(led.since)}, {sum(1 for r in rows if r['flag'])} flagged"
              + ("" if a.no_write else f"; wrote {out}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
