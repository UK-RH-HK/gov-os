#!/usr/bin/env python3
"""P2-AR-0041 (round-3 integration) — R3-WS5-11 reproduction attempt: does the `memory_retrieval_regression` family,
executed inside its health sandbox (`isolated_in_sandbox: true`), get nothing back from the symbol route?

Integration evidence only (Contract v3 O3). For two projects — a minimal one (README + src/lib.rs) and the product's
greenfield fixture — on a private unprovisioned machine (HOME/XDG_* under env SCRATCH; bootstrap install of the binary's
embedded payload), it: installs, commits, rebuilds memory, lists the generated held-out set by category, then runs the
family through the scheduler with `--no-cache` (so it EXECUTES in the sandbox, never served from a cache) and prints the
family detail, every symbol query's result and every failing query. Env: GOV (binary), SCRATCH (private dir), WT (tree,
for the greenfield fixture).
"""
import json, os, shutil, subprocess, sys
import yaml

GOV, SCR, WT = os.environ["GOV"], os.environ["SCRATCH"], os.environ["WT"]
os.makedirs(SCR, exist_ok=True)
env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
env.update({"HOME": os.path.join(SCR, "home"), "XDG_STATE_HOME": os.path.join(SCR, "state"),
            "XDG_CACHE_HOME": os.path.join(SCR, "cache"), "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
            "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
os.makedirs(env["HOME"], exist_ok=True)


def git(proj, *a):
    return subprocess.run(["git", *a], cwd=proj, env=env, capture_output=True, text=True)


def g(proj, *a):
    r = subprocess.run([GOV, "--json", "--root", proj, "--session", "S-ws511", "--role", "orchestrator", *a], cwd=proj,
                       env=env, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "raw": (r.stdout + r.stderr)[-600:]}


def project(tag):
    proj = os.path.join(SCR, tag)
    if tag == "greenfield":
        shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), proj)
    else:
        os.makedirs(os.path.join(proj, "src"))
        open(os.path.join(proj, "README.md"), "w").write("# retrieval probe\n")
        open(os.path.join(proj, "src", "lib.rs"), "w").write(
            "pub fn total_cents(a: i64, b: i64) -> i64 { a + b }\n\npub struct Ledger { pub lines: Vec<i64> }\n")
    git(proj, "init", "-q"); git(proj, "add", "-A"); git(proj, "commit", "-qm", "baseline")
    d = g(proj, "init", "--name", tag, "--alias", f"r-{tag}")
    assert d.get("ok"), d
    git(proj, "add", "-A"); git(proj, "commit", "-qm", "installed")
    assert g(proj, "rebuild-memory").get("ok")
    return proj


for tag in ("minimal", "greenfield"):
    proj = project(tag)
    held = yaml.safe_load(open(os.path.join(proj, "governance/tests/memory/heldout.yaml")))
    qs = held.get("queries", [])
    cats = {}
    for q in qs:
        cats[q.get("category")] = cats.get(q.get("category"), 0) + 1
    print(f"== {tag}: held-out queries by category {json.dumps(cats, sort_keys=True)}; pending {sum(1 for q in qs if q.get('pending'))}")
    r = g(proj, "health", "run", "--check", "memory_retrieval_regression", "--no-cache", "--no-persist")
    fam = ((r.get("result") or {}).get("families") or {}).get("memory_retrieval_regression") or {}
    det = fam.get("detail") or {}
    print(f"   run ok={r.get('ok')} status={fam.get('status')} cached_from={fam.get('cached_from')} findings={fam.get('findings')}")
    print(f"   detail: isolated_in_sandbox={det.get('isolated_in_sandbox')} status={det.get('status')} recall_at_k={det.get('recall_at_k')} "
          f"mrr={det.get('mrr')} queries={det.get('queries')} pending={det.get('pending')} failed={det.get('failed')}")
    sym = [q["id"] for q in qs if q.get("category") == "symbol"]
    print(f"   symbol queries: {sym}; any failing: {[x for x in det.get('failed') or [] if x in sym]}")
    for fr in det.get("failed_results") or []:
        print("   FAILED", json.dumps(fr)[:400])
    print(f"RESULT {tag} R3-WS5-11 {'REPRODUCED' if [x for x in det.get('failed') or [] if x in sym] else 'NOT_REPRODUCED'} "
          f"(executed in sandbox: {fam.get('status') == 'executed' and det.get('isolated_in_sandbox') is True})")
