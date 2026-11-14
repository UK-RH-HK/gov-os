"""ACT-GUARD-FIX-6's decision diff, step 2: the 48-hour call set through the live hook and the after copy.

  python3 -B -I diff_calls.py <calls.jsonl> <prefilter before> <prefilter after> <before hooks> <after hooks> <out.jsonl>
         [--sample N] [--workers W]

Every Bash call whose in-process judgement differs (prefilter.py), every Bash call that names git, and N others at
random (seed 6) are judged by both hooks as the call's role (a call of unknown role: orchestrator), as an engineer
(rule 1) and as an auditor (rule 5); each non-Bash call (up to --sample, seed 6) as its own role. The project is the main
tree, or the worktree the call's cwd is in. One JSON row per judgement."""
import argparse
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairs  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("calls")
ap.add_argument("pb")
ap.add_argument("pa")
ap.add_argument("before")
ap.add_argument("after")
ap.add_argument("out")
ap.add_argument("--sample", type=int, default=400)
ap.add_argument("--workers", type=int, default=6)
args = ap.parse_args()
MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
WT = os.path.realpath(os.path.expanduser("~/gov-os-worktrees"))
KNOWN = ("orchestrator", "product-spec", "engineer", "independent-test-designer", "independent-auditor", "research")
rng = random.Random(6)
pb = {json.loads(l)["id"]: json.loads(l) for l in open(args.pb)}
pa = {json.loads(l)["id"]: json.loads(l) for l in open(args.pa)}
differ = {i for i in pb if any(pb[i][k] != pa[i][k] for k in ("writes", "made", "rm", "read", "view"))}
calls = []
for line in open(args.calls):
    try:
        c = json.loads(line)
    except ValueError:
        continue
    if c.get("event"):
        calls.append(c)
bash = [c for c in calls if c["event"]["tool_name"] == "Bash" and isinstance(c["event"]["tool_input"].get("command"), str)]
other = [c for c in calls if c["event"]["tool_name"] != "Bash"]
GIT = re.compile(r"(?<![\w./-])git(?![\w-])")
chosen = [c for c in bash if c["id"] in differ or GIT.search(c["event"]["tool_input"]["command"])]
rest = [c for c in bash if c not in chosen]
chosen_ids = {c["id"] for c in chosen}
sample = rng.sample(rest, min(args.sample, len(rest)))
osample = rng.sample(other, min(args.sample, len(other)))
print(f"bash calls {len(bash)}: differ in process {len(differ)}, name git {sum(1 for c in chosen if c['id'] not in differ)}, "
      f"random others {len(sample)}; non-bash sample {len(osample)}", flush=True)


def item(c, role, tag):
    ev = c["event"]
    cwd = ev.get("cwd") or MAIN
    m = re.match(re.escape(WT) + r"/[^/]+", cwd)
    return {"id": f"{c['id']}|{tag}", "tool": ev["tool_name"], "input": ev["tool_input"], "cwd": cwd, "role": role,
            "ticket": c.get("ticket") or "DAEO-sdxk", "project": m.group(0) if m else MAIN,
            "agent_type": ev.get("agent_type")}


items = []
for c in chosen + sample:
    own = c.get("role") if c.get("role") in KNOWN else "orchestrator"
    roles = dict.fromkeys([own, "engineer", "independent-auditor"])
    for r in roles:
        items.append(item(c, r, r[:3] + ("*" if r == own else "")))
for c in osample:
    own = c.get("role") if c.get("role") in KNOWN else "orchestrator"
    items.append(item(c, own, own[:3] + "*"))
print(f"judgements: {len(items)}", flush=True)
rows = pairs.run(items, args.before, args.after, workers=args.workers)
with open(args.out, "w") as handle:
    for r in rows:
        handle.write(json.dumps(r) + "\n")
import collections  # noqa: E402
print(collections.Counter(pairs.classify(r) for r in rows))
