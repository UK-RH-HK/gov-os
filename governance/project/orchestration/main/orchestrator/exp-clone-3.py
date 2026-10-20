"""Step 3: gov adopt --lite A0 to A2 in the clone, gov doctor, a rebuild, and gov check with the secrets check timed."""
import json
import os
import subprocess
import time

BASE = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/45f2a529-6746-474d-b738-e1df6781c663/scratchpad/dev-tier-exp"
CLONE = os.path.join(BASE, "b dev clone")
GOV = "/home/usain/.local/bin/gov"
ENV = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_ROLE", "GOV_TICKET")}
ENV["GOV_DEV_TIERS"] = "/home/usain/gov-os-workbench/synthetic"


def gov(*args, show=6):
    start = time.time()
    done = subprocess.run([GOV, *args], cwd=CLONE, capture_output=True, text=True, env=ENV)
    wall = round(time.time() - start, 1)
    print("$ gov", " ".join(args), "->", done.returncode, f"({wall} s)")
    text = done.stdout.strip() or done.stderr.strip()
    try:
        out = json.loads(done.stdout)
    except ValueError:
        out = None
    if out is None:
        for line in text.splitlines()[-show:]:
            print("   ", line[:220])
    else:
        err = out.get("error") or {}
        print("    ok:", out.get("ok"), "|", (err.get("code") or ""), (err.get("message") or "")[:260])
    return out, done


for stage in ("A0", "A1", "A2"):
    out, done = gov("adopt", "--lite", "--stage", stage, "--json", "--role", "orchestrator")
    if out and out.get("ok"):
        print("    result keys:", list((out.get("result") or {}).keys())[:10])
    print("    git status:", subprocess.run(["git", "status", "--short"], cwd=CLONE, capture_output=True,
                                            text=True).stdout.strip().splitlines()[:6])
gov("doctor", "--json")
gov("rebuild", "--no-embeddings", "--json")
print("load:", open("/proc/loadavg").read().split()[:3])
size = subprocess.run(["du", "-sm", os.path.join(CLONE, ".gov-runtime")], capture_output=True, text=True).stdout.split()[:1]
count = sum(len(files) for _, _, files in os.walk(os.path.join(CLONE, ".gov-runtime")))
print("runtime folder MiB:", size, "files:", count)
start = time.time()
done = subprocess.run(["python3", "-m", "gov.secrets"], cwd=CLONE, capture_output=True, text=True, env=ENV)
print("python3 -m gov.secrets ->", done.returncode, round(time.time() - start, 1), "s; output lines",
      len(done.stdout.splitlines()), "|", done.stderr.strip()[-200:])
for line in done.stdout.splitlines()[:8]:
    print("   ", line[:200])
out, done = gov("check", "--json")
checks = {}


def walk(o):
    if isinstance(o, dict):
        if "id" in o and "status" in o:
            checks[o["id"]] = (o["status"], [(f.get("message") or f.get("code") or "")[:120] for f in (o.get("findings") or [])][:2])
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(out)
for name, (status, findings) in sorted(checks.items()):
    print(f"    {status:6} {name} {findings if status != 'GREEN' else ''}")
