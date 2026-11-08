"""The block that ends every report to the owner (owner, standing, DEC-948). Prints five lines, readable on a phone:
Progress, Leads, Closes, Toward EXAMIN's copy, OWNER_ACTION. Live from .tickets/, the running leads, the lead queue's
spec and log, the gate and the close-queue logs; the hand-kept facts (merged-not-closed, held, the next closes, the
EXAMIN line, owner actions) from log/report-state.json, which the orchestrator updates at each merge, hold and close.
With --mark, records now as the last report (refusals are counted since it) and writes the block to
log/status-latest.txt (DEC-1087 (6), SEVEN-ANSWERS §6 (d)). The sixth line, the emergency plan, comes from
report-state.json's "emergency" (DEC-1087 (6)). With --countdown, prints the countdown that opens every report instead
(DEC-878, prompt §8): the progress line, the keystones line (done / in progress / ahead, of nine, from the tickets'
keystone-N tags), then report-state.json's "countdown" steps, each with its estimate."""
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
keystones = {}  # "keystone-N" -> the statuses of its tickets
for path in glob.glob(ROOT + "/.tickets/*.md"):
    head = open(path, encoding="utf-8").read().split("\n---", 1)[0]
    w = re.search(r"^wbs_id: (W2-\S+)$", head, re.M)
    s = re.search(r"^status: (\S+)$", head, re.M)
    if w and s:
        tickets[w.group(1)] = (os.path.basename(path)[:-3], s.group(1))
        tags = re.search(r"^tags: \[(.*)\]$", head, re.M)
        for k in re.findall(r"keystone-\d+", tags.group(1) if tags else ""):
            keystones.setdefault(k, []).append(s.group(1))
by_id = {tid: w2 for w2, (tid, _) in tickets.items()}
# DEC-1097 (15): a keystone with a list in the plan is computed from that list, not from tags (report-state.json's
# "keystone_lists": W2 ids, or "done: <DEC>" for a keystone done by decision); the rest still from keystone-N tags
for k, lst in st.get("keystone_lists", {}).items():
    if isinstance(lst, str):
        keystones[k] = ["closed"]
    else:
        keystones[k] = [tickets[w][1] if w in tickets else "open" for w in lst]

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
    queued = [l.split()[0] for l in open(O + "/log/" + st["chain_spec"]) if l.strip() and not l.lstrip().startswith("#") and l.split()[0] not in started]
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

lines = []
progress = "- Progress: %d closed / %d merged-not-closed / %d built-and-held / %d in flight / %d not started, of %d." % (
    len(closed), len(mnc), len(held), len(flight), len(notstarted), total)
if "--countdown" in sys.argv:
    # a keystone is done when all its tickets are closed (its owner acts are the countdown's to name), in progress when
    # one has started, ahead when none has (DEC-878)
    done = [k for k, ss in keystones.items() if all(x == "closed" for x in ss)]
    going = [k for k, ss in keystones.items() if k not in done and any(x != "open" for x in ss)]
    ahead = [k for k in keystones if k not in done and k not in going]
    key = lambda k: int(k.split("-")[1])
    print("Countdown (DEC-878):")
    print(progress)
    untagged = [str(n) for n in range(1, 10) if "keystone-%d" % n not in keystones]
    print("- Keystones: %d done / %d in progress / %d ahead, of nine (%s%s)." % (
        len(done), len(going), len(ahead), "; ".join(
            "%s: %s" % (label, ", ".join(sorted((k.split("-")[1] for k in ks), key=int)) or "none")
            for label, ks in (("done", done), ("in progress", going), ("ahead", ahead))),
        "; no ticket tagged: " + ", ".join(untagged) if untagged else ""))
    for i, step in enumerate(st.get("countdown", []), 1):
        print("%d. %s" % (i, step))
    sys.exit(0)
lines.append(progress)
lines.append("- Leads: %d running (%s); queued next: %s; the gate: %s." % (
    len(running), ", ".join(running) or "none", ", ".join(queued[:4]) or "none", gate_short))
lines.append("- Closes: %s; next: %s; refused since the last report: %s." % (
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


lines.append("- Memory chain: " + "; ".join(w + " " + mstate(w) for w in MEMORY) + ".")
lines.append("- Toward EXAMIN's copy: " + st["examin"] + ".")
if st.get("emergency"):
    lines.append("- Emergency plan: " + st["emergency"] + ".")
lines.append("- OWNER_ACTION: " + st["owner_action"])
print("\n".join(lines))
if "--mark" in sys.argv:
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    st["last_report"] = now
    json.dump(st, open(STATE, "w"), indent=2)
    with open(O + "/log/status-latest.txt", "w") as f:
        f.write("Status at %s (the last report's block)\n%s\n" % (now, "\n".join(lines)))
