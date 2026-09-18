#!/usr/bin/env python3
"""A2 bullets 1, 2, 3, 5, 6 + cross-capability S3/S4/S5 <-> A2 (AC-16) on a PROVISIONED machine.

A throw-away administrator root (3 root keys, threshold 2) is provisioned from an admin directory outside every
project. Synthetic releases 4.1.5 (seq 10) and 4.1.6 (seq 20) are built with the product's own `gov release build`
from scratch copies of framework/, then signed by this harness (independent minter, lib/srr_mint.py).
Every privileged lifecycle ingress (init, adopt A6 batch 0, update --apply, kernel reinstall, update --rollback) is
driven through the real `gov` binary with: an authentic release, an unsigned release, a post-signing tampered payload,
an attacker-signed release, and a below-floor release. Metadata versions are issued from one monotonic counter so
each case reaches the check it is aimed at (and is not stopped earlier by replay protection).
Run: PROBE_TMP=<scratch> python3 A2-02-provisioned-ingress.py
"""
import os, sys, json, shutil, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *

sb = Sandbox("a2-prov")
R = [K("root-a"), K("root-b"), K("root-c")]
REL1, SNAP, TS, REC, ATT = K("release-1"), K("snapshot-1"), K("timestamp-1"), K("recovery-1"), K("attacker")
roles = {"root": (2, R), "release": (1, [REL1]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]), "recovery": (1, [REC])}
anchor = os.path.join(sb.admin, "root-1.json")
open(anchor, "w").write(envelope(root_doc(1, roles), R[:2]))
MV = [0]
def nv():
    MV[0] += 1
    return MV[0]

def sign(reldir, seq, rel_keys=(REL1,), snap_keys=(SNAP,), ts_keys=(TS,), mutate_doc=None, **kw):
    v = nv()
    d = release_doc(os.path.join(reldir, "kernel"), sequence=seq, version=v, **kw)
    if mutate_doc:
        mutate_doc(d)
    publish(os.path.join(reldir, "metadata"), d, list(rel_keys), list(snap_keys) or None, list(ts_keys) or None, snap_version=v, ts_version=v)
    return v

def build(name, version, seq, supported=None, migration=None):
    canon = canonical_copy(sb.path(name + "-canon"), version=version, supported_from=supported, extra_migration=migration)
    out = sb.gov("release", "build", "--version", version, "--canonical", canon, "--out", sb.path(name), quiet=True)
    assert out.get("ok"), out
    return sb.path(name, "releases", version)

def variant(src_reldir, name, seq, tamper=None, unsigned=False, **kw):
    """Copy a built release; sign it at a fresh metadata version; THEN apply `tamper` to the payload (post-signing)."""
    d = sb.path(name)
    shutil.copytree(src_reldir, d)
    if os.path.isdir(os.path.join(d, "metadata")):
        shutil.rmtree(os.path.join(d, "metadata"))
    if not unsigned:
        sign(d, seq, **kw)
    if tamper:
        tamper(os.path.join(d, "kernel"))
    return d, os.path.join(d, "kernel")

def edit(rel, old, new):
    def f(k):
        p = os.path.join(k, rel)
        t = open(p).read()
        assert old in t, (rel, old)
        open(p, "w").write(t.replace(old, new))
    return f

def nothing_installed(proj):
    return (not os.path.exists(os.path.join(proj, "governance", "kernel")) and
            not os.path.exists(os.path.join(proj, "governance", "framework.lock")) and
            not glob.glob(os.path.join(proj, "governance", "*.srr-new")))

def staging_left():
    st = os.path.join(sb.home, ".local/state/governance-os/machine/staging")
    return os.listdir(st) if os.path.isdir(st) else []

def init(src, name, **kw):
    p = sb.new_repo(name)
    o = sb.gov("init", "--source", src, "--name", name, "--alias", name + "-a", "--skip-index", cwd=p, **kw)
    return p, o

print("## [P0] provisioning the trust anchor from the administrator domain")
proj0 = sb.new_repo("p0")
inside = os.path.join(proj0, "root.json"); shutil.copy(anchor, inside)
sb.gov("trust", "provision", "--anchor", inside, cwd=proj0)                 # repository-sourced anchor
print("[P0] note: `trust provision` refuses any anchor under the current working directory; the administrator runs it from $HOME")
sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home)              # admin-sourced anchor
sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home)              # re-provision
sb.gov("trust", "status", env={"GOV_MACHINE_STATE_DIR": sb.path("elsewhere")})  # relocation after provisioning

rel15 = build("r15", "4.1.5", 10)
print("\n## [P1] authentic release 4.1.5 (seq 10) -> gov init")
a15, k15 = variant(rel15, "a15", 10)
p1, o = init(k15, "p1", quiet=True)
ra = o["result"]["release_authenticity"]
print("[P1] ok =", o["ok"], "| authenticity =", ra["authenticity"], "| posture =", ra["posture"], "| currency =", ra["currency"],
      "| sequence =", ra["sequence"], "| channel =", ra["channel"], "| migrations_authorised =", ra["migrations_authorised"])
print("[P1] installed payload == signed payload:", stage_files(os.path.join(p1, "governance", "kernel"))["payload_hash"] == stage_files(k15)["payload_hash"])
print("[P1] protected floors after install:", json.dumps(o["result"]["protected_state"]["floors"]["release_high_water"]),
      json.dumps(o["result"]["protected_state"]["floors"]["metadata_high_water"]))

WEAKEN = edit("policies/SECURITY_POLICY.yaml", "never_index_classes: [secret, restricted]", "never_index_classes: []")
print("\n## [P2] pre-install tampering after signing: SECURITY_POLICY never_index_classes emptied")
_, kt = variant(rel15, "t15", 10, tamper=WEAKEN)
p2, o = init(kt, "p2")
print("[P2] refused =", not o["ok"], "| code =", err(o), "| nothing installed =", nothing_installed(p2), "| machine staging left =", staging_left())

print("\n## [P3] unauthorised extra payload file / signed payload file missing")
_, kx = variant(rel15, "x15", 10, tamper=lambda k: open(os.path.join(k, "policies", "EXTRA.yaml"), "w").write("x: 1\n"))
p3, o = init(kx, "p3")
_, km = variant(rel15, "m15", 10, tamper=lambda k: os.remove(os.path.join(k, "skills", sorted(os.listdir(os.path.join(k, "skills")))[0])))
p3b, o = init(km, "p3b")

print("\n## [P4] modified migration: payload migration edited; metadata re-signed over the NEW file bytes but binding the OLD migration identity")
orig_ids = migration_identities(os.path.join(rel15, "kernel"))
def mig_edit(k):
    open(os.path.join(k, "migrations", "M-4.1.4-4.1.5.yaml"), "a").write("  - {op: note, text: \"injected\"}\n")
d4 = sb.path("g15"); shutil.copytree(rel15, d4); mig_edit(os.path.join(d4, "kernel"))
sign(d4, 10, migrations=orig_ids)
p4, o = init(os.path.join(d4, "kernel"), "p4")
print("[P4b] unauthorised migration: the payload carries a migration file the metadata does not name")
d4b = sb.path("h15"); shutil.copytree(rel15, d4b)
y = open(os.path.join(d4b, "kernel", "migrations", "M-4.1.4-4.1.5.yaml")).read().replace("id: M-4.1.4-4.1.5", "id: M-9.9.9-9.9.10")
open(os.path.join(d4b, "kernel", "migrations", "M-9.9.9-9.9.10.yaml"), "w").write(y)
sign(d4b, 10, migrations=orig_ids)
p4b, o = init(os.path.join(d4b, "kernel"), "p4b")

print("\n## [P5] wrong key: release role signed by a key the root does not delegate (snapshot/timestamp genuine)")
_, katt = variant(rel15, "att15", 10, rel_keys=(ATT,))
p5, o = init(katt, "p5")
print("[P5b] no snapshot/timestamp at all, release signed by the attacker")
_, katt2 = variant(rel15, "att15b", 10, rel_keys=(ATT,), snap_keys=(), ts_keys=())
p5b, o = init(katt2, "p5b")
print("[P5c] genuine release key, forged payload digest")
_, kfd = variant(rel15, "fd15", 10, mutate_doc=lambda d: d["payload"].__setitem__("payload_hash", "0" * 64))
p5c, o = init(kfd, "p5c")
print("[P5d] root-role key (not a release key) signs release.json")
_, krk = variant(rel15, "rk15", 10, rel_keys=(R[0],))
p5d, o = init(krk, "p5d")

print("\n## [P6] a source directory that regenerates its own identity: consistent KERNEL_MANIFEST.json + manifest.json (CERTIFIED), NO signed metadata")
canon_s = canonical_copy(sb.path("self-canon"), mutate=lambda dd: open(os.path.join(dd, "framework/policies/SECURITY_POLICY.yaml"), "a").write("# self-identified\n"))
sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon_s, "--out", sb.path("self"), "--certification", "CERTIFIED", quiet=True)
kself = sb.path("self", "releases", "4.1.5", "kernel")
p6, o = init(kself, "p6")
print("[P6] refused =", not o["ok"], "| code =", err(o), "| nothing installed =", nothing_installed(p6))
print("[P6b] the embedded payload (no metadata) on the provisioned machine")
p6b = sb.new_repo("p6b"); o = sb.gov("init", "--name", "p6b", "--alias", "p6ba", "--skip-index", cwd=p6b)

print("\n## [P7] expiry / replay / downgrade / identity binding")
_, kexp = variant(rel15, "exp15", 10, expires=PAST)
p7, o = init(kexp, "p7")
_, khi = variant(rel15, "hi15", 10)
p7b, o = init(khi, "p7b", quiet=True)
print("[P7] authentic install at metadata version", MV[0], "(raises the metadata high-water): ok =", o["ok"])
p7c, o = init(k15, "p7c")   # a15 was signed at metadata version 1
print("[P7] replay of metadata version 1 (high-water now", MV[0], ") refused =", not o["ok"], "| code =", err(o))
_, kdown = variant(rel15, "down15", 5)
p7d, o = init(kdown, "p7d")
print("[P7] downgrade (sequence 5 < floor 10) refused =", not o["ok"], "| code =", err(o), "| details =", json.dumps((o.get("error") or {}).get("details"))[:400])
_, kwp = variant(rel15, "wp15", 11, product="some-other-product")
p7e, o = init(kwp, "p7e")
_, kch = variant(rel15, "ch15", 11)
p7f, o = init(kch, "p7f")
p7g = sb.new_repo("p7g"); o = sb.gov("init", "--source", kch, "--channel", "nightly", "--name", "p7g", "--alias", "p7ga", "--skip-index", cwd=p7g)
_, kpl = variant(rel15, "pl15", 11, platforms=("plan9-sparc",))
p7h, o = init(kpl, "p7h")

print("\n## [P8] ADOPT ingress (A0..A5 then A6 batch 0): unsigned / tampered / below-floor / authentic sources")
def adopt_to_a6(name, src):
    pa = sb.new_repo(name, {"README.md": "# legacy app\n", "src/app.py": "def main():\n    return 1\n", "tests/test_app.py": "from src.app import main\n\ndef test_main():\n    assert main() == 1\n"})
    for st in (["adopt", "baseline"], ["adopt", "inventory"], ["adopt", "classify"], ["adopt", "map"], ["adopt", "plan"], ["adopt", "test-design"]):
        sb.gov(*st, cwd=pa, session="planner-1", quiet=True)
    sb.gov("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-session", "reviewer-1", cwd=pa, session="reviewer-1", quiet=True)
    o = sb.gov("adopt", "migrate", "--batch", "0", "--source", src, cwd=pa, session="executor-1")
    return pa, o
pa1, o = adopt_to_a6("pa-unsigned", kself)
print("[P8] adopt unsigned refused =", not o["ok"], "| code =", err(o), "| nothing installed =", nothing_installed(pa1))
_, kt8 = variant(rel15, "t15b", 12, tamper=WEAKEN)
pa2, o = adopt_to_a6("pa-tampered", kt8)
print("[P8] adopt tampered refused =", not o["ok"], "| code =", err(o), "| nothing installed =", nothing_installed(pa2))
_, kd8 = variant(rel15, "d15b", 5)
pa3, o = adopt_to_a6("pa-below", kd8)
print("[P8] adopt below-floor refused =", not o["ok"], "| code =", err(o), "| nothing installed =", nothing_installed(pa3))
_, ka8 = variant(rel15, "a15b", 12)
pa4, o = adopt_to_a6("pa-auth", ka8)
if o.get("ok"):
    inst = o["result"]["batches"][0]["installed"]
    print("[P8] adopt authentic: ok | authenticity =", inst["release_authenticity"]["authenticity"], "| version =", inst["version"])

print("\n## [P9] UPDATE ingress 4.1.5 -> 4.1.6 (seq 20), KERNEL REINSTALL, ROLLBACK")
mig = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "synthetic audit release",
       "breaking": False, "human_gate": "none", "affected_indexes": [], "operations": [{"op": "note", "text": "audit"}], "rollback": "gov update --rollback"})
rel16 = build("r16", "4.1.6", 20, supported=["4.1.5"], migration=mig)
def approve_update(proj, src):
    o = sb.gov("update", "--apply", "--source", src, "--approve", cwd=proj)
    gid = None
    if not o["ok"] and err(o) == "HUMAN_GATE_REQUIRED":
        gid = o["error"]["details"]["gate"]
    elif o.get("ok") and not o["result"].get("applied") and o["result"].get("human_gate"):
        gid = o["result"]["human_gate"]
    if gid:
        sb.gov("gate", "present", gid, cwd=proj, quiet=True)
        sb.gov("decide", gid, "--option", "A", "--by", "human", cwd=proj, role="human", quiet=True)
        print(f"  (human gate {gid} presented and answered A by role=human)")
        return sb.gov("update", "--apply", "--source", src, "--approve", cwd=proj)
    return o
PU = pa4  # the adopted, authentically installed 4.1.5 project (floor 12)
_, k16u = variant(rel16, "u16", 20, unsigned=True)
o = approve_update(PU, k16u); print("[P9] update unsigned refused =", not o["ok"], "| code =", err(o))
print("[P9] lock still 4.1.5 after refused update:", "version: 4.1.5" in open(os.path.join(PU, "governance/framework.lock")).read())
_, k16t = variant(rel16, "t16", 20, tamper=edit("policies/TOOL_POLICY.yaml", "policy: TOOL_POLICY", "policy: TOOL_POLICY # tampered"))
o = approve_update(PU, k16t); print("[P9] update tampered refused =", not o["ok"], "| code =", err(o))
_, k16a = variant(rel16, "a16", 20)
o = approve_update(PU, k16a)
if o.get("ok") and o["result"].get("applied"):
    print("[P9] update authentic ok | authenticity =", o["result"]["details"]["release_authenticity"]["authenticity"], "| floors =", json.dumps(o["result"]["details"]["protected_state"]["floors"]["release_high_water"]))
print("[P9] kernel reinstall: unsigned source (a copy of the installed 4.1.6 bytes, metadata removed)")
o = sb.gov("kernel", "reinstall", "--source", k16u, cwd=PU)
print("[P9] kernel reinstall: tampered source (a copy of the authentic 4.1.6 release, metadata kept, one payload file edited)")
d9 = sb.path("t16b"); shutil.copytree(sb.path("a16"), d9)
edit("policies/TOOL_POLICY.yaml", "policy: TOOL_POLICY", "policy: TOOL_POLICY # tampered")(os.path.join(d9, "kernel"))
o = sb.gov("kernel", "reinstall", "--source", os.path.join(d9, "kernel"), cwd=PU)
print("[P9] kernel reinstall: authentic source")
o = sb.gov("kernel", "reinstall", "--source", k16a, cwd=PU)
print("[P9] kernel reinstall: authentic 4.1.5 (seq 12) onto a machine whose floor is 20 (below floor)")
_, k15r = variant(rel15, "r15r", 12)
o = sb.gov("kernel", "reinstall", "--source", k15r, cwd=PU)
print("[P9] same, with --break-glass requested but no owner-signed token in the protected inbox")
o = sb.gov("kernel", "reinstall", "--source", k15r, "--break-glass", cwd=PU)
print("[P9] update --rollback (4.1.6 -> the 4.1.5 snapshot taken before the update)")
o = sb.gov("update", "--rollback", cwd=PU)
print("[P9] environment variable claiming authority")
_, o = init(k16a, "px", env={"GOV_SKIP_VERIFY": "1"})
print("\n## [P10] final trust status")
ts = sb.gov("trust", "status", quiet=True)
print(json.dumps({k: ts["result"][k] for k in ("posture", "installed_release", "floors")}, indent=1)[:1500])
print("\nDONE")
