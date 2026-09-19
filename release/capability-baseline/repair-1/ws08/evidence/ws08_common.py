"""P2-AR-0020 (WS-8) supplementary probe helpers. BUILDER EVIDENCE (Contract v3 O3: regression, not acceptance).

Reuses, read-only, the independent ed25519 SRR minter written by the alpha-r audit of record
(release/capability-baseline/audit-0/alpha-r/evidence/lib/srr_mint.py); that file is not modified and no bytecode is
written beside it. The binary under test is $GOV (default: <worktree>/target/release/gov), so every probe can be run
against the base commit's binary as a negative control and against the repaired binary.

Every verdict line is `W <id> PASS|FAIL <statement> -- <detail>`; `O <id> <observation>` lines are observations the
probe does not grade (for example a behaviour that depends on another workstream's integration point).
"""
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "audit-0", "alpha-r", "evidence", "lib"))
from srr_mint import (GOV, K, REPO, Sandbox, break_glass_doc, canonical_copy, canonical_json, envelope, err,  # noqa
                      publish, release_doc, root_doc, sha256_text, stage_files)

REPO_ROOT = REPO

import yaml  # noqa: E402

RES = []


def w(xid, ok, statement, detail=""):
    RES.append((xid, bool(ok)))
    d = detail if isinstance(detail, str) else json.dumps(detail, default=str)
    print(f"W {xid} {'PASS' if ok else 'FAIL'} {statement} -- {d[:1500]}", flush=True)


def o(xid, text):
    print(f"O {xid} {text}", flush=True)


def summary():
    f = [i for i, ok in RES if not ok]
    print(f"SUMMARY gov={GOV} total={len(RES)} pass={len(RES) - len(f)} fail={len(f)} failed={f}", flush=True)


ROOT_KEYS = [K("root-a"), K("root-b"), K("root-c")]
REL, SNAP, TS, REC = K("release-1"), K("snapshot-1"), K("timestamp-1"), K("recovery-1")
ROLES = {"root": (2, ROOT_KEYS), "release": (1, [REL]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]),
         "recovery": (1, [REC])}


def provision(sb):
    anchor = os.path.join(sb.admin, "root-1.json")
    if not os.path.exists(anchor):
        open(anchor, "w").write(envelope(root_doc(1, ROLES), ROOT_KEYS[:2]))
    r = sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home, quiet=True)
    assert r.get("ok"), r
    return r


class Releases:
    """Builds releases from a scratch export of this worktree's HEAD framework and signs them with the probe keys."""

    def __init__(self, sb):
        self.sb = sb
        self.meta_version = 0

    def build(self, name, version="4.1.5", supported=None, migration=None, mutate=None, certification=None):
        canon = canonical_copy(self.sb.path(name + "-canon"), version=None if version == "4.1.5" else version,
                               supported_from=supported, extra_migration=migration, mutate=mutate)
        args = ["release", "build", "--version", version, "--canonical", canon, "--out", self.sb.path(name)]
        if certification:
            args += ["--certification", certification]
        r = self.sb.gov(*args, quiet=True)
        assert r.get("ok"), r
        return self.sb.path(name, "releases", version)

    def sign(self, reldir, sequence, evidence=None, minimum_secure_release="", minimum_secure_sequence=0):
        self.meta_version += 1
        v = self.meta_version
        publish(os.path.join(reldir, "metadata"),
                release_doc(os.path.join(reldir, "kernel"), sequence=sequence, version=v, evidence=evidence,
                            minimum_secure_release=minimum_secure_release,
                            minimum_secure_sequence=minimum_secure_sequence),
                [REL], [SNAP], [TS], snap_version=v, ts_version=v)
        return os.path.join(reldir, "kernel")


def mig(frm, to, ops=None):
    return (f"M-{frm}-{to}.yaml", {"id": f"M-{frm}-{to}", "from_version": frm, "to_version": to,
                                   "description": "synthetic probe release", "breaking": False, "human_gate": "none",
                                   "affected_indexes": [], "operations": ops or [{"op": "note", "text": "probe"}],
                                   "rollback": "gov update --rollback"})


def consistent_rewrite(proj, rel_file, old, new):
    """Rewrite one installed kernel file AND regenerate KERNEL_MANIFEST.json AND framework.lock to agree (what any
    actor with write access to governance/ can do with sha256 alone)."""
    kd = os.path.join(proj, "governance/kernel")
    fp = os.path.join(kd, rel_file)
    t = open(fp).read()
    assert old in t, (rel_file, old)
    open(fp, "w").write(t.replace(old, new))
    mm = json.load(open(os.path.join(kd, "KERNEL_MANIFEST.json")))
    sg = stage_files(kd)
    mm["files"] = sg["files"]
    mm["payload_hash"] = sg["payload_hash"]
    json.dump(mm, open(os.path.join(kd, "KERNEL_MANIFEST.json"), "w"), indent=2)
    lp = os.path.join(proj, "governance/framework.lock")
    lk = yaml.safe_load(open(lp))
    lk["release_hash"] = sg["payload_hash"]
    lk["kernel_manifest_hash"] = sha256_text(canonical_json({k: mm[k] for k in ("framework", "version", "files", "payload_hash")}))
    open(lp, "w").write(yaml.safe_dump(lk, sort_keys=False))
    return sg["payload_hash"]


def presented(out):
    return (out.get("release_trust") or {}).get("presented_as")


def lock(proj):
    return yaml.safe_load(open(os.path.join(proj, "governance/framework.lock")))


def gate_approve(sb, proj, gid):
    sb.gov("gate", "present", gid, cwd=proj, quiet=True)
    return sb.gov("decide", gid, "--option", "A", "--by", "product-owner", cwd=proj, quiet=True)


def apply_update_through_gate(sb, proj, src):
    """`gov update --apply` the ordinary way: the Human Decision Gate is raised, presented and answered, then applied."""
    first = sb.gov("update", "--apply", "--source", src, cwd=proj, quiet=True)
    if first.get("ok"):
        return first, None
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    if not gid:
        return first, None
    gate_approve(sb, proj, gid)
    return sb.gov("update", "--apply", "--source", src, "--approve", "--by", "product-owner", cwd=proj, quiet=True), gid


def copytree(a, b):
    shutil.copytree(a, b, symlinks=True)
