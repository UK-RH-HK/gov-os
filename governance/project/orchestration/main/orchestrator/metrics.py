"""Read-only: ticket claim and close times from the history of .tickets on w1/integrate."""
import collections
import datetime
import re
import subprocess


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


files = [f for f in git("ls-files", ".tickets").split() if f.endswith(".md")]
rows = []
for f in files:
    text = open(f).read()
    wbs = re.search(r"^wbs_id: (\S+)", text, re.M)
    prof = re.search(r"^profile: (\S+)", text, re.M)
    if not wbs:
        continue
    claim = close = None
    log = git("log", "--reverse", "--format=%H %ct", "--", f).split("\n")
    for line in log:
        if not line.strip():
            continue
        h, t = line.split()
        s = re.search(r"^status: (\S+)", git("show", f"{h}:{f}"), re.M)
        s = s.group(1) if s else ""
        if s == "in_progress" and claim is None:
            claim = int(t)
        if s == "closed" and close is None:
            close = int(t)
    rows.append((wbs.group(1), prof.group(1) if prof else "?", claim, close))

d = lambda t: datetime.datetime.fromtimestamp(t).strftime("%m-%d %H:%M") if t else "-"
perday = collections.Counter()
byprof = collections.defaultdict(list)
for w, p, c, k in sorted(rows):
    if k:
        perday[datetime.datetime.fromtimestamp(k).strftime("%m-%d")] += 1
    if c and k:
        byprof[p].append((k - c) / 3600)
    print(w, p, d(c), d(k), f"{(k - c) / 3600:.1f}h" if c and k else "")
print("closed per day:", sorted(perday.items()))
for p, v in byprof.items():
    v.sort()
    print(p, "n", len(v), "mean h", round(sum(v) / len(v), 1), "median h", round(v[len(v) // 2], 1), "max", round(v[-1], 1))
