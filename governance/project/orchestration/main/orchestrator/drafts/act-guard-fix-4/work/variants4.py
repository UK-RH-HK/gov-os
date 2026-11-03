"""The three logged refusals whose recovered command differs between corpus4.json and W2-42a's fixture
(tests/acceptance/W2-42a/fixtures/refusals.json on w2/W2-42a, read by `git show`): each replayed in W2-42a's spelling
too, with the corpus row's role, cwd and TMPDIR. Usage: variants4.py <the fixture, as a file>"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hookrun import MAIN, run  # noqa: E402

H4 = os.path.join(os.path.dirname(HERE), "pretooluse.py")
H3 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "act-guard-fix-3", "pretooluse.py")
ROLE = {**{i: "orchestrator" for i in (61, 62, 63, 70, 71, 72)},
        **{i: "independent-auditor" for i in (64, 67, 68, 69, 75, 76)}}
corpus = json.load(open(os.path.join(HERE, "corpus4.json")))
bykey = {o.get("key"): o for o in corpus}
fixture = json.load(open(sys.argv[1]))["refusals"]
for r in fixture:
    o = bykey.get(r["key"])
    if not o or o.get("input") == r["input"]:
        continue
    role = (o.get("launch_role") if o.get("from") == "fix-3 corpus" else ROLE.get(o["i"], "engineer")) or "orchestrator"
    cwd = o.get("cwd") or MAIN
    m = re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd)
    tmpdir = o.get("tmpdir")
    if tmpdir is None and o.get("from") != "fix-3 corpus":
        t = re.search(r"/tmp/gov-launch-[a-z-]+-[a-z0-9]{8}", json.dumps(o.get("input")))
        tmpdir = t.group(0) if t else None
    kw = dict(cwd=cwd, root=m.group(1) if m else MAIN, agent=o.get("agent_type"), tmpdir=tmpdir)
    for label, tin in (("corpus", o["input"]), ("W2-42a", r["input"])):
        g3 = run(H3, role, r["tool"], tin, **kw)
        g4 = run(H4, role, r["tool"], tin, **kw)
        print(f"row {o['i']} {label:7} {role[:12]:12} today {g3[0]:5} fix-4 {g4[0]:5} | {g4[1][:100]}")
