#!/usr/bin/env python3
"""P2-AR-0041 (round-3 integration) — R3-WS5-10: measure the per-write work-generation/reconciliation cost and the
claim-time propagation/checkpoint cost of the integrated `gov`, and set them beside the Gate U SLOs.

Integration evidence only (Contract v3 O3). Drives `gov` (env GOV) against a disposable project (bootstrap
installation of the binary's embedded payload on a private unprovisioned machine: XDG_STATE_HOME/HOME under the
scratch directory, env SCRATCH), every invocation declaring its role. Prints one line per measurement:

  MEASURE <name> n=<n> median_ms=<m> p90_ms=<p> min_ms=<a> max_ms=<b>

Measured operations (wall time of one `gov` process each, release build):
  status            `gov status`                         read-only baseline (no generation)
  task_list         `gov task list`                      read-only baseline
  generate_dry      `gov task generate --dry-run`        the reconciliation alone (read path, writes nothing)
  task_create       `gov task create ...`                a governed write + the post-command generation
  task_claim        `gov task claim <id>`                claim: G0, detect_and_propagate, DAG, grant, baseline, boundaries
  task_release      `gov task release <id>`              a governed write + the post-command generation
"""
import json
import os
import shutil
import statistics
import subprocess
import sys
import time

GOV = os.environ["GOV"]
SCR = os.environ["SCRATCH"]
N = int(os.environ.get("N", "7"))
os.makedirs(SCR, exist_ok=True)
proj = os.path.join(SCR, "proj")
env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
env.update({"HOME": os.path.join(SCR, "home"), "XDG_STATE_HOME": os.path.join(SCR, "state"),
            "XDG_CACHE_HOME": os.path.join(SCR, "cache"), "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
            "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
os.makedirs(env["HOME"], exist_ok=True)
os.makedirs(os.path.join(proj, "src"), exist_ok=True)
open(os.path.join(proj, "README.md"), "w").write("# cost probe\n")
open(os.path.join(proj, "src", "lib.rs"), "w").write("pub fn total(a: i64, b: i64) -> i64 { a + b }\n")


def git(*a):
    return subprocess.run(["git", *a], cwd=proj, env=env, capture_output=True, text=True)


def g(*a, role="orchestrator", session="S-cost"):
    t0 = time.perf_counter()
    r = subprocess.run([GOV, "--json", "--root", proj, "--session", session, "--role", role, *a], cwd=proj, env=env,
                       capture_output=True, text=True)
    ms = (time.perf_counter() - t0) * 1000.0
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"ok": False, "raw": (r.stdout + r.stderr)[-400:]}
    return d, ms


git("init", "-q")
git("add", "-A")
git("commit", "-qm", "baseline")
d, _ = g("init", "--name", "cost", "--alias", "cost")
assert d.get("ok"), d
git("add", "-A")
git("commit", "-qm", "installed")
d, _ = g("rebuild-memory")
assert d.get("ok"), d


def report(name, samples):
    s = sorted(samples)
    p90 = s[min(len(s) - 1, int(round(0.9 * (len(s) - 1))))]
    print(f"MEASURE {name} n={len(s)} median_ms={statistics.median(s):.0f} p90_ms={p90:.0f} min_ms={s[0]:.0f} "
          f"max_ms={s[-1]:.0f}", flush=True)


print(f"# gov {GOV}", flush=True)
for name, args in [("status", ["status"]), ("task_list", ["task", "list"]),
                   ("generate_dry", ["task", "generate", "--dry-run"])]:
    report(name, [g(*args)[1] for _ in range(N)])

created, cms = [], []
for i in range(N):
    d, ms = g("task", "create", "--class", "documentation", "--objective", f"write note {i}", "--status", "READY",
              "--allowed", f"docs/n{i}/**")
    assert d.get("ok"), d
    created.append(d["result"]["id"])
    cms.append(ms)
report("task_create", cms)

claims, rels = [], []
for i, t in enumerate(created):
    d, ms = g("task", "claim", t, session=f"S-c{i}")
    claims.append(ms)
    if not d.get("ok"):
        print(f"# claim {t} refused: {(d.get('error') or {}).get('code')}: {(d.get('error') or {}).get('message', '')[:200]}", flush=True)
        continue
    d, ms2 = g("task", "release", t, session=f"S-c{i}")
    rels.append(ms2)
report("task_claim", claims)
if rels:
    report("task_release", rels)
d, _ = g("task", "list")
tasks = d.get("result") or []
gen = [t for t in tasks if (t.get("generated_from") or {}).get("source")]
print(f"# tasks={len(tasks)} generated={len(gen)}", flush=True)
