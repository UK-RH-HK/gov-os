#!/usr/bin/env python3
"""A2 qualification challenge "interrupted install" / R1 item 6 re-established on this candidate: crash windows of the
install transaction (runtime/src/srr/staging.rs) are reproduced on disk exactly as a crash would leave them, then
`gov trust recover-transactions` (and the replay at the top of every admission) is run.
W1 crash after journal "prepare" (half-built <dest>.srr-new, dest intact)
W2 crash inside the two-rename window: dest renamed aside, .srr-new complete, dest missing
W3 crash inside the window, .srr-new lost: dest missing, .srr-old present
W4 crash after "committed": dest complete, .srr-old left behind
In every window the outcome must be exactly one complete installation and no floor advance.
Run: PROBE_TMP=<scratch> python3 A2-07-interrupted-install.py
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *

sb = Sandbox("a2-crash")
p = sb.new_repo("p", {"README.md": "# p\n"})
sb.gov("init", "--name", "p", "--alias", "pa", "--skip-index", cwd=p, quiet=True)
gov = os.path.join(p, "governance"); dest = os.path.join(gov, "kernel")
jdir = os.path.join(sb.home, ".local/state/governance-os/machine/journal"); os.makedirs(jdir, exist_ok=True)
floors0 = sb.gov("trust", "status", quiet=True)["result"]["floors"]
def journal(tid, phase):
    json.dump({"id": tid, "phase": phase, "dest": dest, "new_path": dest + ".srr-new", "old_path": dest + ".srr-old", "staging": "", "payload_hash": "x", "version": "4.1.5"}, open(os.path.join(jdir, tid + ".json"), "w"))
def state(label):
    kv = sb.gov("kernel", "verify", cwd=p, quiet=True)
    print(f"[{label}] dest exists={os.path.isdir(dest)} .srr-new={os.path.isdir(dest + '.srr-new')} .srr-old={os.path.isdir(dest + '.srr-old')} kernel verify ok={(kv.get('result') or {}).get('ok')}")
def recover(label):
    o = sb.gov("trust", "recover-transactions", quiet=True)
    print(f"[{label}] recover-transactions ->", json.dumps(o.get("result") or o.get("error"))[:400])

print("## [W1] crash after 'prepare': half-built .srr-new beside an intact dest")
os.makedirs(dest + ".srr-new/policies", exist_ok=True); open(dest + ".srr-new/policies/partial.yaml", "w").write("x: 1\n")
journal("t-w1", "prepare"); state("W1-before"); recover("W1"); state("W1-after")
print("\n## [W2] crash between the two renames: dest moved aside, .srr-new complete")
shutil.copytree(dest, dest + ".srr-new"); os.rename(dest, dest + ".srr-old")
journal("t-w2", "swap"); state("W2-before"); recover("W2"); state("W2-after")
shutil.rmtree(dest + ".srr-old", ignore_errors=True)
print("\n## [W3] crash between the renames, .srr-new lost: only .srr-old survives")
os.rename(dest, dest + ".srr-old")
journal("t-w3", "swap"); state("W3-before"); recover("W3"); state("W3-after")
print("\n## [W4] crash after 'committed': the superseded tree was not yet removed")
shutil.copytree(dest, dest + ".srr-old")
journal("t-w4", "committed"); state("W4-before")
print("[W4] replay also runs at the top of every admission: `gov kernel reinstall` (embedded payload)")
o = sb.gov("kernel", "reinstall", cwd=p, quiet=True); print("[W4] reinstall ->", "ok" if o["ok"] else f"REFUSED {err(o)}", "| notes =", [n[:90] for n in ((o.get("result") or {}).get("release_authenticity") or {}).get("notes", [])][:2])
state("W4-after")
floors1 = sb.gov("trust", "status", quiet=True)["result"]["floors"]
print("\n[W] floors unchanged by any replay:", floors0["release_high_water"] == floors1["release_high_water"] and floors0["metadata_high_water"] == floors1["metadata_high_water"], floors1["release_high_water"])
print("[W] journal dir left empty:", os.listdir(jdir))
print("\nDONE")
