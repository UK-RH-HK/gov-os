#!/usr/bin/env python3
"""A2 bullet 10 — release verification works offline after obtaining an authentic release envelope.

Every verification step below runs inside `unshare -rn` (a user+network namespace with only a DOWN loopback: no
route, no DNS). The authentic envelope (release dir + metadata/) is obtained beforehand; the trust anchor is
provisioned beforehand. Offline: init (authentic), tamper refusal, update, reinstall from this machine's protected
installed record with NO metadata, currency reporting, break-glass entry.
Run: PROBE_TMP=<scratch> python3 A2-06-offline-verification.py
"""
import os, sys, json, shutil, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *

sb = Sandbox("a2-offline")
A, B, C = K("root-a"), K("root-b"), K("root-c")
REL1, SNAP, TS, REC = K("release-1"), K("snapshot-1"), K("timestamp-1"), K("recovery-1")
roles = {"root": (2, [A, B, C]), "release": (1, [REL1]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]), "recovery": (1, [REC])}
anchor = os.path.join(sb.admin, "root-1.json"); open(anchor, "w").write(envelope(root_doc(1, roles), [A, B]))
sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home, quiet=True)
canon = canonical_copy(sb.path("canon"))
sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("rel"), quiet=True)
base = sb.path("rel", "releases", "4.1.5")
def signed(name, seq, v, ts_expires=FAR):
    d = sb.path(name); shutil.copytree(base, d)
    publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=v), [REL1], [SNAP], [TS], snap_version=v, ts_version=v, ts_expires=ts_expires)
    return os.path.join(d, "kernel")
k1 = signed("e1", 10, 1)
k2 = signed("e2", 11, 2, ts_expires=PAST)      # authentic, but its timestamp is stale
tamp = sb.path("e3"); shutil.copytree(sb.path("e2"), tamp)
open(os.path.join(tamp, "kernel", "policies", "TOOL_POLICY.yaml"), "a").write("# tampered\n")
bare = sb.path("bare"); shutil.copytree(sb.path("e2"), bare); shutil.rmtree(os.path.join(bare, "metadata"))

def off(*args, cwd=None):
    """gov inside a network-less namespace."""
    e = dict(sb.env)
    cmd = ["unshare", "-rn", GOV, "--json", *args]
    r = subprocess.run(cmd, cwd=cwd or sb.home, env=e, capture_output=True, text=True)
    try:
        out = json.loads(r.stdout)
    except Exception:
        out = {"ok": False, "raw_stdout": r.stdout[-1500:], "raw_stderr": r.stderr[-1500:]}
    out["_exit"] = r.returncode
    show(["[offline]"] + list(args), out)
    return out

print("## [O0] the namespace really has no network")
r = subprocess.run(["unshare", "-rn", "sh", "-c", "cat /proc/net/route; (getent hosts example.com || echo DNS-FAILED); (timeout 3 bash -c 'echo > /dev/tcp/1.1.1.1/443' 2>&1 || echo TCP-FAILED)"], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())

p = sb.new_repo("p1")
print("\n## [O1] offline init from the authentic envelope")
o = off("init", "--source", k1, "--name", "p1", "--alias", "p1a", "--skip-index", cwd=p)
if o.get("ok"):
    ra = o["result"]["release_authenticity"]; print("[O1] authenticity =", ra["authenticity"], "| currency =", ra["currency"])
print("\n## [O2] offline refusal of a tampered payload")
off("kernel", "reinstall", "--source", os.path.join(tamp, "kernel"), cwd=p)
print("\n## [O3] offline reinstall of an authentic release whose timestamp metadata is stale")
o = off("kernel", "reinstall", "--source", k2, cwd=p)
if o.get("ok"):
    ra = o["result"]["release_authenticity"]; print("[O3] authenticity =", ra["authenticity"], "| currency =", ra["currency"], "| notes =", [n[:90] for n in ra["notes"]])
print("\n## [O4] offline reinstall with NO metadata reachable (authenticity from this machine's protected installed record)")
o = off("kernel", "reinstall", "--source", os.path.join(bare, "kernel"), cwd=p)
if o.get("ok"):
    ra = o["result"]["release_authenticity"]; print("[O4] authenticity =", ra["authenticity"], "| currency =", ra["currency"], "| notes =", [n[:120] for n in ra["notes"]])
print("\n## [O5] offline trust status: currency / revocation honesty, network_required")
o = off("trust", "status")
if o.get("ok"):
    print("[O5] currency =", json.dumps(o["result"]["currency"])[:500]); print("[O5] break_glass.network_required =", o["result"]["break_glass"]["network_required"])
print("\nDONE")
