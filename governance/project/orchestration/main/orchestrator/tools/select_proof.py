"""DEC-953 item 4c: run select_tests.py on the running leads' worktrees and on the merged tickets to close, and
summarise scope, the suites chosen and why. Usage: python3 select_proof.py <out.json> W2-64 W2-76 ... --merged W2-71 ..."""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
TOOL = ROOT + "/.gov-runtime/scratch/orchestrator/tools/select_tests.py"


def ticket_of(w2):
    for path in glob.glob(ROOT + "/.tickets/*.md"):
        head = open(path, encoding="utf-8").read().split("\n---", 1)[0]
        if re.search(r"^wbs_id: " + re.escape(w2) + r"$", head, re.M):
            return os.path.basename(path)[:-3]
    return None


def merge_of(w2):
    out = subprocess.run(["git", "-C", ROOT, "log", "--merges", "--first-parent", "w2/integrate", "--format=%H %s",
                          "-400"], capture_output=True, text=True).stdout.splitlines()
    for line in out:
        sha, subj = line.split(" ", 1)
        if re.search(r"w2/" + re.escape(w2) + r"\b", subj):
            return sha
    return None


def run(tree, w2, tid, merge=None):
    cmd = ["python3", TOOL, tree, w2, tid] + (["--merge", merge] if merge else [])
    env = dict(os.environ, PYTHONPATH=tree + "/src")
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode:
        return {"w2": w2, "error": p.stderr[-800:]}
    d = json.loads(p.stdout)
    return {"w2": w2, "ticket": tid, "tree": tree, "merge": merge, "scope": d["scope"], "why_full": d["why_full"],
            "base": d["base"][:12], "changed": len(d["changed"]), "governance_left_out": len(d["governance_left_out"]),
            "selected": [(s["target"], sorted({w["reason"] for w in s["why"]})) for s in d["selected"]],
            "changed_paths": d["changed"][:40]}


def main():
    out = sys.argv[1]
    args = sys.argv[2:]
    split = args.index("--merged") if "--merged" in args else len(args)
    results = []
    for w2 in args[:split]:
        results.append(run("/home/usain/gov-os-worktrees/" + w2, w2, ticket_of(w2)))
    for w2 in args[split + 1:]:
        results.append(run(ROOT, w2, ticket_of(w2), merge_of(w2)))
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        if "error" in r:
            print(r["w2"], "ERROR", r["error"][-300:])
            continue
        print(f"{r['w2']}: {r['scope']} base {r['base']} merge {(r['merge'] or '')[:12]} changed {r['changed']} "
              f"governance left out {r['governance_left_out']}")
        for w in r["why_full"]:
            print("   why full:", json.dumps(w)[:300])
        for t, why in r["selected"]:
            print("   ", t, ",".join(why))


main()
