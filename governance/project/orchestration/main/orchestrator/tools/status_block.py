"""The block that ends every report to the owner (owner, standing, DEC-948). Prints five lines, readable on a phone:
Progress, Leads, Closes, Toward EXAMIN's copy, OWNER_ACTION. Live from .tickets/, the running leads, the lead queue's
spec and log, the gate and the close-queue logs; the hand-kept facts (merged-not-closed, held, the next closes, the
EXAMIN line, owner actions) from log/report-state.json, which the orchestrator updates at each merge, hold and close.
With --mark, records now as the last report (refusals are counted since it)."""
import glob
import json
import os
import re
import subprocess
import sys
import time

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
O = ROOT + "/.gov-runtime/scratch/orchestrator"
STATE = O + "/log/report-state.json"
st = json.load(open(STATE))

tickets = {}
for path in glob.glob(ROOT + "/.tickets/*.md"):
    head = open(path, encoding="utf-8").read().split("\n---", 1)[0]
    w = re.search(r"^wbs_id: (W2-\S+)$", head, re.M)
    s = re.search(r"^status: (\S+)$", head, re.M)
    if w and s:
        tickets[w.group(1)] = (os.path.basename(path)[:-3], s.group(1))
by_id = {tid: w2 for w2, (tid, _) in tickets.items()}

running = []
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    try:
        cmd = open("/proc/" + pid + "/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        continue
    m = re.search(r'"GOV_ROLE":"orchestrator","GOV_TICKET":"(DAEO-[a-z0-9]+)"', cmd)
    if m and " -p " in cmd:
        running.append(by_id.get(m.group(1), m.group(1)))
running = sorted(set(running))

total = len(tickets)
closed = [w for w, (_, s) in tickets.items() if s == "closed"]
mnc = [w for w in st["merged_not_closed"] if tickets.get(w, ("", ""))[1] != "closed"]
held = [w for w in st["built_held"] if tickets.get(w, ("", ""))[1] != "closed" and w not in running and w not in mnc]
flight = [w for w, (_, s) in tickets.items() if s == "in_progress" and w not in mnc and w not in held]
notstarted = [w for w, (_, s) in tickets.items() if s == "open"]

started = set()
try:
    for line in open(O + "/log/" + st["chain_log"]):
        m = re.search(r" starting (W2-\S+) ", line)
        if m:
            started.add(m.group(1))
    queued = [l.split()[0] for l in open(O + "/log/" + st["chain_spec"]) if l.strip() and l.split()[0] not in started]
except OSError:
    queued = []
gate = subprocess.run(["python3", O + "/tools/gate_check.py"], capture_output=True, text=True).stdout.strip()
gate_short = "open"
if gate.startswith("SHUT"):
    parts = []
    m = re.search(r"load ([0-9.]+)/([0-9.]+) >= nproc (\d+)", gate)
    if m:
        parts.append("load %.0f, limit %s" % (float(m.group(1)), m.group(3)))
    m = re.search(r"have=(\d+)kB need=(\d+)kB", gate)
    if m and "memory:" in gate:
        parts.append("memory %.1f of %.1f GiB needed" % (int(m.group(1)) / 1048576, int(m.group(2)) / 1048576))
    gate_short = "shut on " + " and ".join(parts) if parts else "shut"

closing = os.path.exists(O + "/CLOSE-RUNNING")
since = time.strptime(st["last_report"], "%Y-%m-%d %H:%M:%S")
refused = []
for q in glob.glob(O + "/log/close-queue-*/queue.txt"):
    for line in open(q):
        if "CLOSE REFUSED" in line or "STOPPED" in line:
            try:
                if time.strptime(line[:19], "%Y-%m-%d %H:%M:%S") > since:
                    refused.append(line[20:].strip()[:80])
            except ValueError:
                pass

print("- Progress: %d closed / %d merged-not-closed / %d built-and-held / %d in flight / %d not started, of %d." % (
    len(closed), len(mnc), len(held), len(flight), len(notstarted), total))
print("- Leads: %d running (%s); queued next: %s; the gate: %s." % (
    len(running), ", ".join(running) or "none", ", ".join(queued[:4]) or "none", gate_short))
print("- Closes: %s; next: %s; refused since the last report: %s." % (
    "a close is running" if closing else "none running", st["closes_next"], "; ".join(refused) or "none"))
MEMORY = ["W2-61", "W2-61h", "W2-84", "W2-86", "W2-87", "W2-03", "W2-05", "W2-55", "W2-64", "W2-04", "W2-06", "W2-13",
          "W2-15a"]


def mstate(w):
    if w not in tickets:
        return st.get("memory_notes", {}).get(w, "no ticket")
    status = tickets[w][1]
    if status == "closed":
        return "closed"
    if st.get("memory_notes", {}).get(w):
        return st["memory_notes"][w]
    if w in st["merged_not_closed"]:
        return "merged, closing"
    if w in running:
        return "lead running"
    if w in st.get("parked", []):
        return "parked"
    if w in held:
        return "held"
    note = st.get("memory_notes", {}).get(w)
    if note:
        return note
    if w in queued:
        return "queued"
    return "claimed" if status == "in_progress" else "not started"


print("- Memory chain: " + "; ".join(w + " " + mstate(w) for w in MEMORY) + ".")
print("- Toward EXAMIN's copy: " + st["examin"] + ".")
print("- OWNER_ACTION: " + st["owner_action"])
if "--mark" in sys.argv:
    st["last_report"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(st, open(STATE, "w"), indent=2)
