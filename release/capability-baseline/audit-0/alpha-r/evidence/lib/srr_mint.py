"""P2-AR-0013 (alpha-r) independent Signed Release Root metadata minter + gov driver.

Independent of the product's own test material (tests/certification/srr_material.rs): written from the wire format
in runtime/src/srr/metadata.rs (envelope {"signed": <exact bytes>, "signatures": [{keyid, sig}]}, ed25519,
keyid = sha256(raw public key), strict verification) using Python `cryptography`.

This is AUDIT HARNESS code, not product code. It signs synthetic metadata with deterministic throw-away keys so the
real `gov` binary can be driven through provisioned-machine lifecycle ingress paths.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV", os.path.join(REPO, "target", "release", "gov"))
PRODUCT = "agentic-engineering-os"
FAR = "2099-01-01T00:00:00Z"
PAST = "2001-01-01T00:00:00Z"


# ------------------------------------------------------------------------------------------------ keys / envelopes
class Key:
    def __init__(self, name):
        seed = hashlib.sha256(("alpha-r-audit-key:" + name).encode()).digest()
        self.name = name
        self.sk = Ed25519PrivateKey.from_private_bytes(seed)
        raw = self.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.public = raw.hex()
        self.keyid = hashlib.sha256(raw).hexdigest()

    def sign(self, b):
        return self.sk.sign(b).hex()

    def entry(self):
        return {"keytype": "ed25519", "scheme": "ed25519", "keyval": {"public": self.public}}


def K(name):
    return Key(name)


def envelope(signed, keys):
    sb = json.dumps(signed, separators=(",", ":"), ensure_ascii=False)
    sigs = [{"keyid": k.keyid, "sig": k.sign(sb.encode())} for k in keys]
    return '{"signed":' + sb + ',"signatures":' + json.dumps(sigs, separators=(",", ":")) + "}"


def root_doc(version, roles, expires=FAR, product=PRODUCT):
    """roles: {role_name: (threshold, [Key,...])}"""
    keys = {}
    rmap = {}
    for rn, (thr, ks) in roles.items():
        for k in ks:
            keys[k.keyid] = k.entry()
        rmap[rn] = {"keyids": [k.keyid for k in ks], "threshold": thr}
    return {"_type": "root", "spec_version": "srr/1", "product": product, "version": version, "expires": expires,
            "keys": keys, "roles": rmap}


# ------------------------------------------------------------------------------------------------ payload measurement
def canonical_json(v):
    return json.dumps(v, separators=(",", ":"), ensure_ascii=False, sort_keys=True)


def sha256_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def stage_files(candidate):
    """Replicates kernel::stage_payload's selection (KERNEL.yaml payload_dirs, migrations/tools may sit beside)."""
    meta = yaml.safe_load(open(os.path.join(candidate, "KERNEL.yaml")))
    files = {}
    for d in meta.get("payload_dirs", []):
        src = os.path.join(candidate, d)
        if not os.path.exists(src) and d in ("migrations", "tools"):
            alt = os.path.join(os.path.dirname(candidate), d)
            if os.path.exists(alt):
                src = alt
        if not os.path.exists(src):
            continue
        for dp, dn, fn in os.walk(src):
            for f in fn:
                ab = os.path.join(dp, f)
                rel = os.path.join(d, os.path.relpath(ab, src)).replace(os.sep, "/")
                if rel == "KERNEL_MANIFEST.json":
                    continue
                files[rel] = hashlib.sha256(open(ab, "rb").read()).hexdigest()
    files["KERNEL.yaml"] = hashlib.sha256(open(os.path.join(candidate, "KERNEL.yaml"), "rb").read()).hexdigest()
    payload_hash = sha256_text(canonical_json(files))
    ver = meta.get("version")
    ver = ver if isinstance(ver, str) else json.dumps(ver)
    fw = meta.get("framework", PRODUCT)
    kmh = sha256_text(canonical_json({"framework": fw, "version": ver, "files": files, "payload_hash": payload_hash}))
    return {"files": files, "payload_hash": payload_hash, "kernel_manifest_hash": kmh, "version": ver}


def migration_identities(candidate):
    mdir = os.path.join(candidate, "migrations")
    if not os.path.isdir(mdir):
        mdir = os.path.join(os.path.dirname(candidate), "migrations")
    out = []
    if os.path.isdir(mdir):
        for f in sorted(os.listdir(mdir)):
            if f.endswith(".yaml"):
                m = yaml.safe_load(open(os.path.join(mdir, f)))
                if isinstance(m, dict) and "id" in m:
                    out.append({"id": m["id"], "from_version": str(m.get("from_version", "")),
                                "to_version": str(m.get("to_version", "")), "sha256": sha256_text(canonical_json(m))})
    return out


def release_doc(candidate, release_version=None, sequence=1, version=1, channel="stable", expires=FAR,
                minimum_secure_release="", minimum_secure_sequence=0, platforms=("any",), repository="private/agentic-engineering-os",
                migrations=None, product=PRODUCT, evidence=None, drop_file=None, extra_file=None):
    st = stage_files(candidate)
    files = {p: {"sha256": h} for p, h in st["files"].items()}
    if drop_file:
        files.pop(drop_file, None)
    if extra_file:
        files[extra_file[0]] = {"sha256": extra_file[1]}
    d = {"_type": "release", "spec_version": "srr/1", "product": product, "repository": repository, "channel": channel,
         "release_version": release_version or st["version"], "sequence": sequence, "version": version, "expires": expires,
         "platforms": list(platforms), "minimum_secure_release": minimum_secure_release,
         "minimum_secure_sequence": minimum_secure_sequence,
         "payload": {"payload_hash": st["payload_hash"], "kernel_manifest_hash": st["kernel_manifest_hash"], "files": files},
         "migrations": migration_identities(candidate) if migrations is None else migrations}
    if evidence is not None:
        d["evidence"] = evidence
    return d


def publish(meta_dir, rel_signed, release_keys, snap_keys=None, ts_keys=None, snap_version=1, ts_version=1,
            snap_expires=FAR, ts_expires=FAR):
    """Write release.json (+ snapshot.json + timestamp.json when keys are given) into meta_dir."""
    os.makedirs(meta_dir, exist_ok=True)
    rel = envelope(rel_signed, release_keys)
    open(os.path.join(meta_dir, "release.json"), "w").write(rel)
    for f in ("snapshot.json", "timestamp.json"):
        p = os.path.join(meta_dir, f)
        if os.path.exists(p):
            os.remove(p)
    if snap_keys:
        snap = {"_type": "snapshot", "spec_version": "srr/1", "version": snap_version, "expires": snap_expires,
                "meta": {"release.json": {"version": rel_signed["version"], "sha256": hashlib.sha256(rel.encode()).hexdigest()}}}
        s = envelope(snap, snap_keys)
        open(os.path.join(meta_dir, "snapshot.json"), "w").write(s)
        if ts_keys:
            ts = {"_type": "timestamp", "spec_version": "srr/1", "version": ts_version, "expires": ts_expires,
                  "meta": {"snapshot.json": {"version": snap_version, "sha256": hashlib.sha256(s.encode()).hexdigest()}}}
            open(os.path.join(meta_dir, "timestamp.json"), "w").write(envelope(ts, ts_keys))


def break_glass_doc(machine_id, rel_stage, nonce, reason="audit probe", expires=FAR, issued="2026-09-18T00:00:00Z",
                    product=PRODUCT):
    return {"_type": "break-glass", "spec_version": "srr/1", "product": product, "machine_id": machine_id, "nonce": nonce,
            "reason": reason, "issued": issued, "expires": expires,
            "recovery_release": {"payload_hash": rel_stage["payload_hash"], "kernel_manifest_hash": rel_stage["kernel_manifest_hash"],
                                 "release_version": rel_stage["version"]}}


# ------------------------------------------------------------------------------------------------ sandbox + driver
class Sandbox:
    """An isolated machine: HOME / XDG_* under a fresh scratch dir; no GOV_* inherited."""

    def __init__(self, name, base=None):
        base = base or os.environ.get("PROBE_TMP") or tempfile.gettempdir()
        self.dir = tempfile.mkdtemp(prefix=f"alpha-r-{name}-", dir=base)
        self.home = os.path.join(self.dir, "home")
        os.makedirs(self.home)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
        self.env.update({"HOME": self.home, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "probe",
                         "GIT_AUTHOR_EMAIL": "probe@example.invalid", "GIT_COMMITTER_NAME": "probe",
                         "GIT_COMMITTER_EMAIL": "probe@example.invalid"})
        self.admin = os.path.join(self.dir, "admin")  # administrator domain (outside every project)
        os.makedirs(self.admin)

    def path(self, *p):
        return os.path.join(self.dir, *p)

    def gov(self, *args, cwd=None, env=None, role=None, session=None, quiet=False):
        e = dict(self.env)
        if env:
            e.update(env)
        cmd = [GOV, "--json"]
        if role:
            cmd += ["--role", role]
        if session:
            cmd += ["--session", session]
        cmd += list(args)
        r = subprocess.run(cmd, cwd=cwd or self.dir, env=e, capture_output=True, text=True)
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"ok": False, "raw_stdout": r.stdout[-3000:], "raw_stderr": r.stderr[-3000:]}
        out["_exit"] = r.returncode
        if not quiet:
            show(args, out)
        return out

    def git(self, cwd, *args):
        r = subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()

    def new_repo(self, name, files=None):
        d = self.path(name)
        os.makedirs(d, exist_ok=True)
        for rel, txt in (files or {"README.md": "# probe project\n"}).items():
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(txt)
        self.git(d, "init", "-q", "-b", "main")
        self.git(d, "add", "-A")
        self.git(d, "commit", "-q", "-m", "baseline")
        return d


def err(out):
    e = out.get("error") or {}
    return e.get("code")


def show(args, out, keys=None):
    shown = " ".join(str(a) for a in args)
    if out.get("ok"):
        r = out.get("result")
        s = json.dumps(r, ensure_ascii=False)
        print(f"$ gov {shown}\n  -> ok (exit {out['_exit']}) {s[:600]}{'…' if len(s) > 600 else ''}")
    else:
        e = out.get("error") or {}
        print(f"$ gov {shown}\n  -> REFUSED (exit {out['_exit']}) code={e.get('code')} msg={str(e.get('message'))[:400]}")
        if "raw_stdout" in out:
            print("  raw:", out["raw_stdout"][-800:], out["raw_stderr"][-800:])


def canonical_copy(dest, version=None, supported_from=None, extra_migration=None, mutate=None):
    """Export framework/, migrations/, tools/ at HEAD into dest (a scratch 'canonical repository'), optionally
    re-versioned. Never touches the product tree."""
    os.makedirs(dest, exist_ok=True)
    tar = subprocess.run(["git", "archive", "--format=tar", "HEAD", "framework", "migrations", "tools"], cwd=REPO,
                         capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", dest], input=tar, check=True)
    ky = os.path.join(dest, "framework", "KERNEL.yaml")
    if version:
        t = open(ky).read()
        import re
        t = re.sub(r"^version: .*$", f"version: {version}", t, flags=re.M)
        t = re.sub(r"^cli_version: .*$", f"cli_version: {version}", t, flags=re.M)
        t = re.sub(r"^runtime_version: .*$", f"runtime_version: {version}", t, flags=re.M)
        if supported_from is not None:
            t = re.sub(r"^supported_from_versions: .*$", "supported_from_versions: " + json.dumps(supported_from), t, flags=re.M)
        open(ky, "w").write(t)
    if extra_migration:
        name, doc = extra_migration
        open(os.path.join(dest, "migrations", name), "w").write(yaml.safe_dump(doc, sort_keys=False))
    if mutate:
        mutate(dest)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest)
    subprocess.run(["git", "add", "-A"], cwd=dest)
    subprocess.run(["git", "-c", "user.name=probe", "-c", "user.email=probe@example.invalid", "commit", "-q", "-m", "canon"], cwd=dest)
    return dest
