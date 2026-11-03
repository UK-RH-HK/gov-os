"""ACT-GUARD-FIX-3's planted cases (guard4's 54, its CASES, CORPUS_PATTERNS and KNOWN_GAPS) through today's hook and
the ACT-GUARD-FIX-4 candidate: every case whose answer differs from its fix-3 want, with both hooks' reasons.
Usage: planted4.py [--json out.json]"""
import importlib.util
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hookrun import run  # noqa: E402

D4 = os.path.dirname(HERE)
D3 = os.path.join(os.path.dirname(D4), "act-guard-fix-3")
spec = importlib.util.spec_from_file_location("fix3", os.path.join(D3, "test_guard_fix_3.py"))
fix3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix3)
cases = fix3.ALL + fix3.KNOWN_GAPS


def one(c):
    name, role, tool, tin, want = c[:5]
    agent = None
    if "subagent" in name:
        agent = "engineer" if "engineer subagent" in name else "general-purpose"
    role, _, ticket = role.partition("@")
    g4 = run(os.path.join(D4, "pretooluse.py"), role, tool, tin, cwd=fix3.ROOT, root=fix3.ROOT, agent=agent,
             ticket=ticket or "DAEO-sdxk")
    g3 = run(os.path.join(D3, "pretooluse.py"), role, tool, tin, cwd=fix3.ROOT, root=fix3.ROOT, agent=agent,
             ticket=ticket or "DAEO-sdxk")
    return {"name": name, "role": role, "want3": want, "fix3": g3[0], "fix4": g4[0], "why3": g3[1], "why4": g4[1],
            "tin": tin}


with ThreadPoolExecutor(6) as ex:
    out = list(ex.map(one, cases))
print(len(out), "cases;", sum(o["fix3"] == o["want3"] or (o["want3"] == "deny" and o["fix3"].startswith("deny"))
                              for o in out), "as fix-3 wants under fix-3")
diff = [o for o in out if o["fix4"] != o["fix3"]]
print(len(diff), "differ between fix-3 and fix-4:")
for o in diff:
    print(f"  [{o['fix3']}->{o['fix4']}] {o['role'][:10]} {o['name']} | 3: {o['why3'][:60]} | 4: {o['why4'][:80]}")
if "--json" in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
