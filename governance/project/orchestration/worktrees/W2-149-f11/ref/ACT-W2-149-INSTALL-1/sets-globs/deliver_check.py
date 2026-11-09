"""ACT-SETS-GLOBS-1: the launch script still delivers into the new hidden globs, and the guard then refuses what it
delivered (end to end, planted).

  python3 deliver_check.py <clone> <work folder> <hook> before|after

The W2-149 acceptance harness (<clone>/tests/acceptance/W2-149/w2_149_support.py) plants a world under <work folder>:
a planted repository whose path map carries the clone's own sets_root_hidden block (so the launch script's stage 15
counts the hidden part by the globs under test), a planted HOME with its sets root, and a stub claude that plays a good
session. The real launch script (<clone>/governance/project/orchestration/tools/indep_launch.py) then runs a writer
(a new set: fixtures/evaluation/memory-verdict-4/hidden/), a checker (memory-verdict-3/XCHECK-r1.md) and an auditor
(runs/audit-1/miss-classes.json, beside the audit's planted runs/audit-1/misses.jsonl, which the auditor's wall is
seeded from). Each must be delivered. Then <hook> (the clone's, with CLAUDE_PROJECT_DIR=<clone>
and HOME the planted one, so its block's ~/gov-os-eval is the world's sets root) judges, for the CTO, a lead and an
engineer: a Read and a Bash cat of each delivered file and a Grep of each destination folder (deny after, allow
before), and the launch script's own line (allow, both). Prints one line per check and a last line PASS or FAIL.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

clone, work, hook, expect = os.path.realpath(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, f"{clone}/tests/acceptance/W2-149")
import w2_149_support as support  # noqa: E402

PY = os.environ.get("GOV_PIN_PY") or open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
text = open(f"{clone}/governance/project/path-map.yaml", encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, line in enumerate(text) if line.startswith("sets_root_hidden:")][0]
end = next(j for j in range(at + 1, len(text)) if text[j][:1] not in ("", " ", "\t", "#", "\n", "\r"))
block = "".join(line for line in text[at:end] if not line.startswith("#"))
assert re.search(r'^  root: "~/gov-os-eval"$', block, re.M), "the clone's block root must be ~/gov-os-eval here"
support.PATH_MAP = "# Planted path map (ACT-SETS-GLOBS-1 deliver check): the clone's sets_root_hidden block\n" + block
print("the planted repository's block:", " ".join(block.split())[:400])

work.mkdir(parents=True, exist_ok=False)
repo = support.build_repo(work / "repo")
w = support.World(work / "w", repo, base=work)
w.plant()
ok = True


def check(label, good, more=""):
    global ok
    ok &= bool(good)
    print(("ok   " if good else "FAIL ") + label + (f" | {more}" if more and not good else ""))


dest = {"writer": w.sr / "fixtures/evaluation/memory-verdict-4/hidden",
        "checker": w.sr / "fixtures/evaluation/memory-verdict-3/XCHECK-r1.md",
        "auditor": w.sr / "runs/audit-1/miss-classes.json"}
for kind in ("writer", "checker", "auditor"):
    run = w.deliver(kind)
    line = run.line or {}
    check(f"deliver {kind}: status {line.get('status')}, code {line.get('code')}, delivered "
          f"{(line.get('delivered') or {}).get('files')} file(s) to {(line.get('delivered') or {}).get('to')}",
          run.code == 0 and line.get("status") == "delivered", run.why())
    check(f"deliver {kind}: the destination exists ({dest[kind].relative_to(w.sr)})", dest[kind].exists())
misses = w.sr / "runs/audit-1/misses.jsonl"  # the auditor's input: hidden too (ACT-SETS-GLOBS-1)
check("the audit's misses.jsonl is still there after the auditor's run", misses.is_file())
files = sorted(str(p) for p in dest["writer"].rglob("*") if p.is_file()) + [str(dest["checker"]), str(dest["auditor"]),
                                                                          str(misses)]
print(f"delivered files under the planted sets root: {len(files)}")


def decide(role, tool, tin):
    role, _, ticket = role.partition("@")
    event = {"tool_name": tool, "tool_input": tin, "cwd": clone, "session_id": "sets-globs-deliver", "agent_type": None}
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_ROLE", "GOV_TICKET")}
    env.update(HOME=str(w.home), GOV_ROLE=role, GOV_TICKET=ticket or "W2-00", CLAUDE_PROJECT_DIR=clone)
    p = subprocess.run([PY, "-E", hook], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=60)
    if p.returncode == 2:
        return "deny"
    if p.stdout.strip():
        return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]
    return "allow"


want_hidden = "deny" if expect == "after" else "allow"
for role in ("orchestrator", "orchestrator@DAEO-0uhh", "engineer"):
    for f in files:
        rel = os.path.relpath(f, w.sr)
        check(f"{role} Read <SR>/{rel}: want {want_hidden}", decide(role, "Read", {"file_path": f}) == want_hidden)
        check(f"{role} Bash cat <SR>/{rel}: want {want_hidden}",
              decide(role, "Bash", {"command": f"cat {f}"}) == want_hidden)
    for d in (dest["writer"], dest["checker"].parent, dest["auditor"].parent):
        check(f"{role} Grep <SR>/{d.relative_to(w.sr)}: want {want_hidden}",
              decide(role, "Grep", {"pattern": "x", "path": str(d)}) == want_hidden)
    line = (f"python3 {clone}/governance/project/orchestration/tools/indep_launch.py --sets-root {w.sr} --kind checker "
            f"--set memory-verdict-3 --round 2 --commit {w.sha('B')}")
    check(f"{role} the launch script's own line: want allow", decide(role, "Bash", {"command": line}) == "allow")
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
