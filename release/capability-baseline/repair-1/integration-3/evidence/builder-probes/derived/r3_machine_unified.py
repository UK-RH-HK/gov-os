"""LABELLED DERIVED COPY (P2-AR-0041, round-3 integration) of repair-1/r3-ws03/evidence/r3_machine.py (P2-AR-0034).
Changes, and only these (the integration unified P2-ADJ-0002 into one mechanism: WS-8's versioned
`t2-binding-authority` document and `gov trust bind`; WS-3's bundle and `trust t2-binding --provision` are gone):
  1. WT is computed from this copy's location (7 levels up instead of 5);
  2. `key_id_of` added; `authority_id_of(key)` names the probe owner's authority (`probe-owner-<6 hex of the key id>`)
     instead of deriving `t2a-...`;
  3. `bundle_text(key, signers, expires)` returns this helper's own pair {authority: <unified authority envelope with
     keys [{key_id, commitment, status: active}], version 1>, key_hex} instead of a `t2-binding-provisioning` bundle;
  4. `Machine.install_binding(text)` writes the authority and a `t2-binding-key` file into the administrator domain and
     runs `gov trust bind --authority <f> --key <f>` instead of `gov trust t2-binding --provision <bundle>`.
Everything else is byte-for-byte the original.

Original docstring follows.

P2-AR-0034 (WS-3, round 3) evidence helpers — TEST MATERIAL ONLY, builder regression evidence (Contract v3 O3).

Simulated machines for black-box probes (isolated HOME / XDG_STATE_HOME / XDG_CACHE_HOME, no GOV_* inherited), and the
product owner's side of P2-ADJ-0002 played with PUBLISHED seeds (never production keys):

* roots: the published-seed keys of tests/certification/srr_material.rs (root 0x11-0x13 at 2-of-3, release 0x21,
  snapshot 0x31, timestamp 0x41, recovery 0x51), the `human-gate` role delegated to seed 7 (the key hc_owner.py signs
  answers with) and, optionally, the `t2-binding` role delegated to seed 0x6b;
* the owner's T2 binding bundle: a published 32-byte binding key and its `t2-binding-authority` signed with seed 0x6b;
* another owner's root and bundle (other seeds) for the foreign-machine lines.

Release metadata is signed with the same published seeds through the alpha-r audit-of-record minter (read-only import;
no bytecode is written beside it). Derived in style from repair-1/r2-ws03/evidence/r2_machine.py (P2-AR-0024).
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
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))  # DERIVED: 1
HC = os.path.join(WT, "release/capability-baseline/repair-1/ws03/evidence/hc_owner.py")
sys.path.insert(0, os.path.join(WT, "release/capability-baseline/audit-0/alpha-r/evidence/lib"))
from srr_mint import publish, release_doc, stage_files  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402

PRODUCT = "agentic-engineering-os"
FAR = "2099-01-01T00:00:00Z"


class SeedKey:
    """A published-seed ed25519 key (srr_material.rs `key(seed)`). NOT A PRODUCTION KEY."""

    def __init__(self, seed):
        self.sk = Ed25519PrivateKey.from_private_bytes(bytes([seed]) * 32)
        raw = self.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.public = raw.hex()
        self.keyid = hashlib.sha256(raw).hexdigest()

    def signature(self, b):
        return self.sk.sign(b).hex()

    # the alpha-r minter (srr_mint.publish) calls keys through this name
    sign = signature

    def entry(self):
        return {"keytype": "ed25519", "scheme": "ed25519", "keyval": {"public": self.public}}


REL, SNAP, TS, REC = SeedKey(0x21), SeedKey(0x31), SeedKey(0x41), SeedKey(0x51)
OWNER_ROOT = [SeedKey(0x11), SeedKey(0x12), SeedKey(0x13)]
HUMAN = SeedKey(7)
T2_ROLE = SeedKey(0x6B)
BINDING_KEY = bytes([0x3C]) * 32
FOREIGN_ROOT = [SeedKey(0x81), SeedKey(0x82), SeedKey(0x83)]
FOREIGN_HUMAN = SeedKey(0x8A)
FOREIGN_T2 = SeedKey(0x8B)
FOREIGN_BINDING_KEY = bytes([0x5E]) * 32


def envelope(signed, keys):
    text = json.dumps(signed, separators=(",", ":"))
    sigs = [{"keyid": k.keyid, "sig": k.signature(text.encode())} for k in keys]
    return '{"signed":' + text + ',"signatures":' + json.dumps(sigs, separators=(",", ":")) + "}"


def root_text(version=1, root_keys=None, human=HUMAN, t2=(T2_ROLE,)):
    root_keys = root_keys or OWNER_ROOT
    keys, roles = {}, {}

    def role(name, ks, threshold=1):
        for k in ks:
            keys[k.keyid] = k.entry()
        roles[name] = {"keyids": [k.keyid for k in ks], "threshold": threshold}

    role("root", root_keys, 2)
    role("release", [REL])
    role("snapshot", [SNAP])
    role("timestamp", [TS])
    role("recovery", [REC])
    role("human-gate", [human])
    if t2:
        role("t2-binding", list(t2))
    signed = {"_type": "root", "spec_version": "srr/1", "product": PRODUCT, "version": version, "expires": FAR,
              "keys": keys, "roles": roles}
    return envelope(signed, root_keys[:2])


def key_id_of(key):  # DERIVED: 2
    return hashlib.sha256(b"t2-binding-key-id:" + key).hexdigest()[:16]


def authority_id_of(key):  # DERIVED: 2
    return "probe-owner-" + key_id_of(key)[:6]


def key_commitment_of(key):
    return hashlib.sha256(b"t2-binding-key-commitment:" + key).hexdigest()


def bundle_text(key=BINDING_KEY, signers=(T2_ROLE,), expires=FAR):  # DERIVED: 3
    signed = {"_type": "t2-binding-authority", "spec_version": "srr/1", "product": PRODUCT, "version": 1,
              "authority_id": authority_id_of(key), "expires": expires, "owner": "probe owner (published test seed)",
              "keys": [{"key_id": key_id_of(key), "commitment": key_commitment_of(key), "status": "active"}]}
    return json.dumps({"authority": envelope(signed, list(signers)), "key_hex": key.hex()})


PKG = {"why_now": "the next task depends on this choice", "current_state": "two options analysed, none chosen",
       "options": [{"id": "A", "description": "proceed as proposed"}, {"id": "B", "description": "do not proceed"}],
       "impact": "the dependent tasks are re-planned", "reversibility": "reversible: the change can be rolled back",
       "cost_rework": "one task of rework if reversed", "recommendation": "A", "confidence": 0.6, "impact_radius": "R3"}


class Machine:
    """One simulated machine with one project. `clone_of` makes this machine's project a Git clone of another's."""

    def __init__(self, gov, scratch, tag, fixture=None, clone_of=None, role="orchestrator"):
        self.gov = gov
        self.tag = tag
        self.base = tempfile.mkdtemp(prefix=tag + "-", dir=scratch)
        self.admin = os.path.join(self.base, "admin-domain")
        os.makedirs(self.admin)
        self.p = os.path.join(self.base, "proj")
        self.role = role
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
        self.env.update({"HOME": self.base + "/home", "XDG_STATE_HOME": self.base + "/state",
                         "XDG_CACHE_HOME": self.base + "/cache", "GIT_CONFIG_GLOBAL": "/dev/null",
                         "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
                         "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid",
                         "PYTHONDONTWRITEBYTECODE": "1"})
        os.makedirs(self.env["HOME"])
        if clone_of is not None:
            r = subprocess.run(["git", "clone", "-q", clone_of.p, self.p], env=self.env, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
        else:
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

    def pull(self, other):
        return self.git("pull", "-q", "--no-rebase", other.p, "HEAD")

    def g(self, *a, role=None, session=None):
        role = self.role if role is None else role
        session = session or ("S-" + self.tag)
        args = [self.gov, "--json", "--root", self.p, "--session", session] + (["--role", role] if role else []) + list(a)
        r = subprocess.run(args, capture_output=True, text=True, env=self.env, cwd=self.p)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"ok": False, "raw": (r.stdout + r.stderr)[-600:]}
        d["_exit"] = r.returncode
        return d

    def state_dir(self):
        return os.path.join(self.env["XDG_STATE_HOME"], "governance-os", "machine")

    def admin_file(self, name, text):
        f = os.path.join(self.admin, name)
        open(f, "w").write(text)
        return f

    # ---- administrator steps
    def provision(self, root=None):
        return self.g("trust", "provision", "--anchor", self.admin_file(f"root-{uuid.uuid4().hex[:6]}.json", root or root_text()))

    def install_binding(self, text=None):  # DERIVED: 4
        b = json.loads(text or bundle_text())
        n = uuid.uuid4().hex[:6]
        a = self.admin_file(f"authority-{n}.json", b["authority"])
        k = self.admin_file(f"key-{n}.json", json.dumps({"_type": "t2-binding-key", "key_hex": b["key_hex"]}))
        return self.g("trust", "bind", "--authority", a, "--key", k)

    def signed_release(self, kernel_src, sequence, meta_version=None):
        mv = meta_version or sequence
        d = os.path.join(self.base, f"rel-{sequence}-{uuid.uuid4().hex[:4]}")
        shutil.copytree(kernel_src, os.path.join(d, "kernel"))
        publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=sequence, version=mv),
                [REL], [SNAP], [TS], snap_version=mv, ts_version=mv)
        return os.path.join(d, "kernel")

    def reanchor(self):
        """Verify the kernel this project pins against a signed release of that exact payload (the installed copy)."""
        import yaml
        pin = yaml.safe_load(open(os.path.join(self.p, "governance/framework.lock")))["release_hash"]
        src = os.path.join(self.p, "governance/kernel")
        assert stage_files(src)["payload_hash"] == pin, "installed kernel does not measure to the pin"
        stage = os.path.join(self.base, f"kernel-copy-{uuid.uuid4().hex[:4]}")
        shutil.copytree(src, stage)
        r = self.g("kernel", "reinstall", "--source", self.signed_release(stage, 1), role="orchestrator")
        assert r.get("ok"), r
        return r

    # ---- owner-side human answers (TEST MATERIAL, published seed 7)
    def answer(self, gid, inst, sha, opt, nonce=None):
        f = os.path.join(self.admin, f"ans-{gid}-{opt}-{uuid.uuid4().hex[:6]}.json")
        a = [sys.executable, HC, "answer", f, gid, inst, sha, opt] + (["--nonce", nonce] if nonce else [])
        subprocess.run(a, check=True, capture_output=True, env=self.env)
        return f

    def owner_decide(self, gid, opt="A"):
        r = self.g("gate", "present", gid)
        if not r.get("ok"):
            return r
        pr = r["result"]["gate"]
        return self.g("decide", gid, "--option", opt, "--answer-file", self.answer(gid, pr["gate_instance"], pr["package_sha256"], opt))

    def gate(self, gid, question, extra=None):
        fields = dict(PKG)
        fields.update(extra or {})
        fields["id"] = gid
        return self.g("gate", "create", "--question", question, "--fields", json.dumps(fields))

    def t2(self, gid):
        r = self.g("gate", "show", gid)
        return (r.get("result") or {}).get("t2") or {"binding": None, "error": (r.get("error") or {}).get("code")}

    def binding_counts(self):
        r = self.g("audit", "--no-persist", "--family", "os_binding_integrity")
        body = r.get("result") or ((r.get("error") or {}).get("details")) or {}
        fam = (body.get("families") or {}).get("os_binding_integrity") or {}
        return (fam.get("detail") or {}).get("unverified_by_binding"), fam


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
