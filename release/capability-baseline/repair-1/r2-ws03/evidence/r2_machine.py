"""P2-AR-0024 (WS-3, round 2) evidence helpers — TEST MATERIAL ONLY, builder regression evidence (Contract v3 O3).

A simulated machine for probes: isolated HOME / XDG_STATE_HOME / XDG_CACHE_HOME, no GOV_* inherited. Provisioning uses a
throw-away Signed Release Root (hc_root.py: the published-seed keys of tests/certification/srr_material.rs plus the
test owner's `human-gate` key, seed 7, the key hc_owner.py signs answers with). Release metadata is signed with the
same published seeds through the alpha-r audit-of-record minter (read-only import; no bytecode is written beside it).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
HC = os.path.join(WT, "release/capability-baseline/repair-1/ws03/evidence/hc_owner.py")
sys.path.insert(0, os.path.join(WT, "release/capability-baseline/audit-0/alpha-r/evidence/lib"))
from srr_mint import publish, release_doc, stage_files  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402


class SeedKey:
    """A published-seed ed25519 key (srr_material.rs `key(seed)`). NOT A PRODUCTION KEY."""

    def __init__(self, seed):
        self.sk = Ed25519PrivateKey.from_private_bytes(bytes([seed]) * 32)
        raw = self.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.public = raw.hex()
        self.keyid = hashlib.sha256(raw).hexdigest()

    def sign(self, b):
        return self.sk.sign(b).hex()


REL, SNAP, TS, REC = SeedKey(0x21), SeedKey(0x31), SeedKey(0x41), SeedKey(0x51)

PKG = {"why_now": "the next task depends on this choice", "current_state": "two options analysed, none chosen",
       "options": [{"id": "A", "description": "proceed as proposed"}, {"id": "B", "description": "do not proceed"}],
       "impact": "the dependent tasks are re-planned", "reversibility": "reversible: the change can be rolled back",
       "cost_rework": "one task of rework if reversed", "recommendation": "A", "confidence": 0.6, "impact_radius": "R3"}


class Machine:
    def __init__(self, gov, scratch, tag, fixture=None, role="orchestrator"):
        self.gov = gov
        self.base = tempfile.mkdtemp(prefix=tag + "-", dir=scratch)
        self.p = os.path.join(self.base, "proj")
        self.role = role
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
        self.env.update({"HOME": self.base + "/home", "XDG_STATE_HOME": self.base + "/state",
                         "XDG_CACHE_HOME": self.base + "/cache", "GIT_CONFIG_GLOBAL": "/dev/null",
                         "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
                         "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid",
                         "PYTHONDONTWRITEBYTECODE": "1"})
        os.makedirs(self.env["HOME"])
        if fixture:
            shutil.copytree(os.path.join(WT, "fixtures", fixture, "project"), self.p)
        else:
            os.makedirs(self.p)
            open(os.path.join(self.p, "README.md"), "w").write("# probe\n")
        self.git("init", "-q")
        self.commit("baseline")

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.p, env=self.env, capture_output=True, text=True)

    def commit(self, m):
        self.git("add", "-A")
        self.git("commit", "-qm", m)

    def g(self, *a, role=None, session="S-probe"):
        role = self.role if role is None else role
        args = [self.gov, "--json", "--root", self.p, "--session", session] + (["--role", role] if role else []) + list(a)
        r = subprocess.run(args, capture_output=True, text=True, env=self.env, cwd=self.p)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"ok": False, "raw": (r.stdout + r.stderr)[-600:]}
        d["_exit"] = r.returncode
        return d

    def path(self, *p):
        return os.path.join(self.base, *p)

    # ---- trust material (administrator domain: outside the project)
    def root_file(self, human_gate=True):
        f = self.path(f"root-{uuid.uuid4().hex[:6]}.json")
        subprocess.run([sys.executable, os.path.join(HERE, "hc_root.py"), f] + ([] if human_gate else ["--no-human-gate"]),
                       check=True, capture_output=True, env=self.env)
        return f

    def provision(self, human_gate=True):
        return self.g("trust", "provision", "--anchor", self.root_file(human_gate))

    def signed_release(self, kernel_src, sequence, name=None, meta_version=None):
        """A signed release of `kernel_src`; metadata versions default to `sequence` (they must stay monotonic per
        machine, so a release published later for an older sequence passes a higher `meta_version`)."""
        mv = meta_version or sequence
        d = self.path(name or f"rel-{sequence}-{uuid.uuid4().hex[:4]}")
        shutil.copytree(kernel_src, os.path.join(d, "kernel"))
        publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=sequence, version=mv),
                [REL], [SNAP], [TS], snap_version=mv, ts_version=mv)
        return os.path.join(d, "kernel")

    def reanchor(self):
        """Re-verify the kernel installed while unprovisioned against a signed release of the payload the lock pins."""
        import yaml
        pin = yaml.safe_load(open(os.path.join(self.p, "governance/framework.lock")))["release_hash"]
        # the installed copy first: a canonical `framework/` directory is not a self-contained kernel source (its
        # payload also draws on the repository's migrations/ and tools/), so a copy of it measures differently
        cands = [os.path.join(self.p, "governance/kernel")] + \
                [os.path.join(WT, f"release/releases/{v}/kernel") for v in ("4.1.4", "4.1.5")]
        src = next(c for c in cands if os.path.isdir(c) and stage_files(c)["payload_hash"] == pin)
        r = self.g("kernel", "reinstall", "--source", self.signed_release(src, 1), role="orchestrator")
        assert r.get("ok"), r
        return r

    def human_channel(self):
        st = self.g("trust", "human-channel")
        if (st.get("result") or {}).get("available"):
            return st
        self.provision()
        if os.path.exists(os.path.join(self.p, "governance/framework.lock")):
            self.reanchor()
        return self.g("trust", "human-channel")

    # ---- owner-side documents (TEST MATERIAL, published seed)
    def answer(self, gid, inst, sha, opt, nonce=None):
        f = self.path(f"ans-{gid}-{opt}-{uuid.uuid4().hex[:6]}.json")
        a = [sys.executable, HC, "answer", f, gid, inst, sha, opt] + (["--nonce", nonce] if nonce else [])
        subprocess.run(a, check=True, capture_output=True, env=self.env)
        return f

    def anchor_doc(self):
        f = self.path("standalone-anchor.json")
        subprocess.run([sys.executable, HC, "anchor", f, "7"], check=True, capture_output=True, env=self.env)
        return f

    def owner_decide(self, gid, opt="A"):
        r = self.g("gate", "present", gid)
        if not r.get("ok"):
            return r
        pr = r["result"]["gate"]
        return self.g("decide", gid, "--option", opt, "--answer-file", self.answer(gid, pr["gate_instance"], pr["package_sha256"], opt))


def err(d):
    e = d.get("error") or {}
    return e.get("code")


RES = []


def check(cid, ok, statement, detail=None):
    RES.append((cid, bool(ok)))
    d = "" if detail is None else " -- " + (detail if isinstance(detail, str) else json.dumps(detail, default=str))[:700]
    print(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {statement}{d}", flush=True)


def summary(gov):
    f = [c for c, ok in RES if not ok]
    print(f"SUMMARY gov={gov} total={len(RES)} pass={len(RES) - len(f)} fail={len(f)} failed={f}", flush=True)
