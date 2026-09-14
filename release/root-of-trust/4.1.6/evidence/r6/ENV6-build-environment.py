#!/usr/bin/env python3
"""ENV6-build-environment — evidence probe for R-BENV-1..R-BENV-5 (revision-6 rules),
AR-0015 (architect run, RoT-1 revision 6).

Follows reviewer B's probe RV5-B-A08-build-image-selects-bytes.py (AR-0012, review
r5) for build/image construction, Rust flags (--remap-path-prefix, opt-level=2,
codegen-units=1, debuginfo=0, strip=symbols, --build-id=none), and inject.o
constructor.  Extends it to model the full environment registration, environment-
reproduction, ceremony, and binary-reproduction protocol with Ed25519-signed
supplier checksums under OP-16 (a) and (b).

Scenarios E0-E9 exercise every R-ENV rule and both OP-16 modes.

Executed read-only against the local Rust toolchain and system C compiler.
All scratch work under env6/work/.  Output: JSON on stdout.
"""

import hashlib, json, os, stat, subprocess, sys
sys.dont_write_bytecode = True

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# ═══════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════
BASE = os.environ["ENV6_SCRATCH"]                      # scratch root (never the repository)
ACCOUNT_HOME = os.environ.get("ENV6_ACCOUNT_HOME", os.path.expanduser("~"))   # read-only use of the Rust toolchain
TOOLCHAIN = os.environ.get("ENV6_TOOLCHAIN", ACCOUNT_HOME + "/.rustup/toolchains/stable-x86_64-unknown-linux-gnu")
RUSTC = TOOLCHAIN + "/bin/rustc"
W = BASE + "/work"
for _d in (W, W + "/home", W + "/tmp"):
    os.makedirs(_d, exist_ok=True)

# ── test rustc with scratch HOME ────────────────────────────────
RUSTC_HOME_DEV = False
try:
    _r = subprocess.run(
        [RUSTC, "--version"],
        env={"PATH": "/usr/bin:/bin", "HOME": W + "/home",
             "TMPDIR": W + "/tmp", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=30)
    if _r.returncode != 0:
        RUSTC_HOME_DEV = True
except Exception:
    RUSTC_HOME_DEV = True


def cenv(**kw):
    """Clean child environment (env -i equivalent)."""
    e = {"PATH": "/usr/bin:/bin",
         "HOME": ACCOUNT_HOME if RUSTC_HOME_DEV else W + "/home",
         "TMPDIR": W + "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}
    e.update(kw)
    return {k: v for k, v in e.items() if not k.startswith("GOV_")}


# ═══════════════════════════════════════════════════════════════════
# Crypto helpers (Ed25519 via cryptography)
# ═══════════════════════════════════════════════════════════════════
def derive_key(label):
    """Deterministic Ed25519 keypair from label (SHA-256 seed), same as B probes."""
    seed = hashlib.sha256(label.encode()).digest()
    sk = Ed25519PrivateKey.from_private_bytes(seed)
    return sk, sk.public_key()


def ed_sign(sk, data):
    return sk.sign(data)


def ed_verify(pk, sig, data):
    try:
        pk.verify(sig, data)
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════
# Hash helpers
# ═══════════════════════════════════════════════════════════════════
def H(data):
    return hashlib.sha256(data).hexdigest()


def Hfile(p):
    return H(open(p, "rb").read())


# ═══════════════════════════════════════════════════════════════════
# Toolchain snapshot (before)
# ═══════════════════════════════════════════════════════════════════
_tc_files = [RUSTC] + sorted(
    os.path.join(TOOLCHAIN, "lib", f)
    for f in os.listdir(TOOLCHAIN + "/lib")
    if f.startswith("librustc_driver"))
tc_before = {os.path.basename(p): Hfile(p) for p in _tc_files}

# ═══════════════════════════════════════════════════════════════════
# Keys
# ═══════════════════════════════════════════════════════════════════
distA_sk, distA_pk = derive_key("distA")
distB_sk, distB_pk = derive_key("distB")
er1_sk, _ = derive_key("env-reproducer-1")
er2_sk, _ = derive_key("env-reproducer-2")

RELEASE_ID = "gov-os-4.1.6-rc1"
SRC = 'fn main() {\n    println!("gov: genuine behaviour");\n}\n'
INJECT_C = ('#include <unistd.h>\n'
            '__attribute__((constructor)) static void rv5b_inject(void)'
            ' { write(1, "INJECTED-BY-BUILD-IMAGE\\n", 24); }\n')

# ═══════════════════════════════════════════════════════════════════
# Compile inject.o once
# ═══════════════════════════════════════════════════════════════════
open(W + "/inject.c", "w").write(INJECT_C)
subprocess.run(["/usr/bin/cc", "-c", "-O2", "-fno-ident",
                "-o", W + "/inject.o", W + "/inject.c"],
               env=cenv(), check=True, capture_output=True)
INJECT_O = open(W + "/inject.o", "rb").read()

# ═══════════════════════════════════════════════════════════════════
# Component byte sets
# ═══════════════════════════════════════════════════════════════════


def _clean_cc(sid):
    return ("#!/bin/sh\n# supplier %s\nexec /usr/bin/cc \"$@\"\n" % sid).encode()


def _evil_cc(sid):
    return ("#!/bin/sh\n# supplier %s\n"
            "exec /usr/bin/cc \"$@\" \"${0%%/*}/../lib/inject.o\"\n" % sid).encode()


def _supplier_file(sid):
    return ("%s\n" % sid).encode()


def _add_sha(comps):
    for c in comps.values():
        c["sha256"] = H(c["bytes"])
    return comps


dA_clean = _add_sha({
    "bin/cc":         {"bytes": _clean_cc("distA"), "mode": 0o755},
    "share/SUPPLIER": {"bytes": _supplier_file("distA"), "mode": 0o644},
})
dA_evil = _add_sha({
    "bin/cc":         {"bytes": _evil_cc("distA"), "mode": 0o755},
    "lib/inject.o":   {"bytes": INJECT_O, "mode": 0o644},
    "share/SUPPLIER": {"bytes": _supplier_file("distA"), "mode": 0o644},
})
dB_clean = _add_sha({
    "bin/cc":         {"bytes": _clean_cc("distB"), "mode": 0o755},
    "share/SUPPLIER": {"bytes": _supplier_file("distB"), "mode": 0o644},
})
dB_evil = _add_sha({
    "bin/cc":         {"bytes": _evil_cc("distB"), "mode": 0o755},
    "lib/inject.o":   {"bytes": INJECT_O, "mode": 0o644},
    "share/SUPPLIER": {"bytes": _supplier_file("distB"), "mode": 0o644},
})

# ═══════════════════════════════════════════════════════════════════
# SHA256SUMS + signatures
# ═══════════════════════════════════════════════════════════════════


def _make_sums(comps):
    return "".join("%s  %s\n" % (comps[p]["sha256"], p)
                   for p in sorted(comps)).encode()


dA_honest_sums   = _make_sums(dA_clean)
dA_compr_sums    = _make_sums(dA_evil)
dB_honest_sums   = _make_sums(dB_clean)
dB_compr_sums    = _make_sums(dB_evil)

dA_honest_sig    = ed_sign(distA_sk, dA_honest_sums)
dA_compr_sig     = ed_sign(distA_sk, dA_compr_sums)
dB_honest_sig    = ed_sign(distB_sk, dB_honest_sums)
dB_compr_sig     = ed_sign(distB_sk, dB_compr_sums)

# ═══════════════════════════════════════════════════════════════════
# Image helpers
# ═══════════════════════════════════════════════════════════════════
_seq = [0]


def _td(prefix):
    _seq[0] += 1
    d = "%s/%s-%d" % (W, prefix, _seq[0])
    os.makedirs(d, exist_ok=True)
    return d


def _assemble(dest, comps):
    """Write component bytes into dest directory; return image_digest."""
    for p, c in comps.items():
        fp = os.path.join(dest, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb").write(c["bytes"])
        os.chmod(fp, c["mode"])
    return _img_digest(dest)


def _img_digest(d):
    """SHA-256 over sorted 'path\\tmode\\tsha256\\n' lines of the image tree."""
    lines = []
    for root, _, files in sorted(os.walk(d)):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, d)
            m = oct(stat.S_IMODE(os.stat(p).st_mode))
            lines.append("%s\t%s\t%s\n" % (rel, m, H(open(p, "rb").read())))
    lines.sort()
    return H("".join(lines).encode())


def _recipe_digest(comps):
    return H("".join("%s\t%s\n" % (p, oct(comps[p]["mode"]))
                     for p in sorted(comps)).encode())


def _mirror(comps):
    """Content-addressable mirror: sha256 -> bytes."""
    return {c["sha256"]: c["bytes"] for c in comps.values()}


# Pre-compute image digests
dA_clean_imgd = _assemble(_td("imgd"), dA_clean)
dA_evil_imgd  = _assemble(_td("imgd"), dA_evil)
dB_clean_imgd = _assemble(_td("imgd"), dB_clean)
dB_evil_imgd  = _assemble(_td("imgd"), dB_evil)

# ═══════════════════════════════════════════════════════════════════
# Manifest builder
# ═══════════════════════════════════════════════════════════════════


def mfst(env_id, sc, comps, imgd):
    return {
        "environment_id": env_id,
        "supplier_class": sc,
        "components": [{"path": p, "sha256": comps[p]["sha256"],
                        "mode": comps[p]["mode"]} for p in sorted(comps)],
        "recipe_digest": _recipe_digest(comps),
        "image_digest": imgd,
    }


# ═══════════════════════════════════════════════════════════════════
# Environment reproduction  (R-BENV-2)
# ═══════════════════════════════════════════════════════════════════


def env_repro(sk, m, mir, *, forced_digest=None):
    """
    Honest: fetch components from mirror by digest, assemble, compute
    image_digest, sign statement.
    Compromised (forced_digest set): sign a statement with that digest.
    """
    if forced_digest is not None:
        stmt = json.dumps({
            "release_id": RELEASE_ID,
            "environment_id": m["environment_id"],
            "supplier_class": m["supplier_class"],
            "recipe_digest": m["recipe_digest"],
            "image_digest": forced_digest,
        }, sort_keys=True).encode()
        return ("OK", {"image_digest": forced_digest,
                       "image_dir": None,
                       "signature": ed_sign(sk, stmt).hex()})

    fetched = {}
    for c in m["components"]:
        p, expected = c["path"], c["sha256"]
        if expected not in mir:
            return ("INPUT_DIGEST_MISMATCH",
                    {"path": p, "reason": "not in mirror"})
        blob = mir[expected]
        actual = H(blob)
        if actual != expected:
            return ("INPUT_DIGEST_MISMATCH",
                    {"path": p, "expected": expected[:16], "actual": actual[:16]})
        fetched[p] = {"bytes": blob, "sha256": expected, "mode": c["mode"]}

    dest = _td("erepro")
    imgd = _assemble(dest, fetched)
    stmt = json.dumps({
        "release_id": RELEASE_ID,
        "environment_id": m["environment_id"],
        "supplier_class": m["supplier_class"],
        "recipe_digest": m["recipe_digest"],
        "image_digest": imgd,
    }, sort_keys=True).encode()
    return ("OK", {"image_digest": imgd,
                   "image_dir": dest,
                   "signature": ed_sign(sk, stmt).hex()})


# ═══════════════════════════════════════════════════════════════════
# Ceremony  (R-BENV-1, R-BENV-2, R-BENV-3)
# ═══════════════════════════════════════════════════════════════════


def cer(m, supplier_pk, sums_bytes, sums_sig, env_repros):
    """
    R-BENV-1: each component sha256 in supplier's signed SHA256SUMS.
    R-BENV-2: >=2 environment reproductions by distinct keys agree on image_digest
             and that digest matches the proposed manifest.
    R-BENV-3: structural — no CI image record accepted.
    """
    # R-BENV-1
    if not ed_verify(supplier_pk, sums_sig, sums_bytes):
        return ("ENVIRONMENT_COMPONENT_UNVERIFIED",
                {"reason": "SHA256SUMS signature invalid"})
    listed = {line.split("  ")[0]
              for line in sums_bytes.decode().strip().split("\n")}
    for c in m["components"]:
        if c["sha256"] not in listed:
            return ("ENVIRONMENT_COMPONENT_UNVERIFIED",
                    {"path": c["path"], "sha256": c["sha256"][:16] + "..."})

    # R-BENV-2
    ok = [(s, r) for s, r in env_repros if s == "OK"]
    failed = [(s, r) for s, r in env_repros if s != "OK"]
    if len(ok) < 2:
        if failed:
            return (failed[0][0], failed[0][1])
        return ("ENVIRONMENT_NOT_REPRODUCED", {"valid": len(ok)})

    by_key = {r["signature"]: r["image_digest"] for _, r in ok}
    unique = set(by_key.values())
    if len(unique) > 1:
        return ("ENVIRONMENT_REPRODUCTION_CONFLICT",
                {"digests": sorted(unique)})
    established = unique.pop()
    if m["image_digest"] != established:
        return ("ENVIRONMENT_NOT_REPRODUCED",
                {"proposed": m["image_digest"][:16] + "...",
                 "established": established[:16] + "..."})
    return ("REGISTERED", {"image_digest": established})


# ═══════════════════════════════════════════════════════════════════
# Binary reproduction  (R-BENV-4)
# ═══════════════════════════════════════════════════════════════════


def bin_repro(label, comps, expected_imgd, mir):
    """Re-assemble image from pinned components, verify digest, build."""
    img = _td("brimg-%s" % label)
    for p, c in comps.items():
        sha = c["sha256"]
        if sha not in mir:
            return {"status": "INPUT_DIGEST_MISMATCH", "path": p,
                    "reason": "not in mirror"}
        blob = mir[sha]
        if H(blob) != sha:
            return {"status": "INPUT_DIGEST_MISMATCH", "path": p,
                    "reason": "digest mismatch after fetch"}
        fp = os.path.join(img, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb").write(blob)
        os.chmod(fp, c["mode"])
    actual = _img_digest(img)
    if actual != expected_imgd:
        return {"status": "INPUT_DIGEST_MISMATCH",
                "expected_image_digest": expected_imgd[:16] + "...",
                "actual_image_digest": actual[:16] + "..."}

    wd = _td("brwork-%s" % label)
    os.makedirs(wd + "/src", exist_ok=True)
    os.makedirs(wd + "/tmp", exist_ok=True)
    open(wd + "/src/main.rs", "w").write(SRC)
    out = wd + "/gov"

    env = cenv(PATH=img + "/bin:/usr/bin:/bin", TMPDIR=wd + "/tmp")
    cmd = [RUSTC, "--edition", "2021",
           "-C", "opt-level=2", "-C", "codegen-units=1",
           "-C", "debuginfo=0", "-C", "strip=symbols",
           "-C", "linker=" + img + "/bin/cc",
           "--remap-path-prefix", wd + "=/build",
           "--remap-path-prefix", img + "=/image",
           "-C", "link-arg=-Wl,--build-id=none",
           "-o", out, wd + "/src/main.rs"]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
    res = {"status": "OK" if r.returncode == 0 else "BUILD_FAILED",
           "rc": r.returncode, "stderr_tail": r.stderr[-300:]}
    if r.returncode == 0:
        bbin = open(out, "rb").read()
        run = subprocess.run([out], capture_output=True, text=True,
                             env={"PATH": "/usr/bin:/bin"}, timeout=10)
        res.update({
            "binary_digest": H(bbin),
            "stdout": run.stdout.strip(),
            "runs_injected_code": "INJECTED-BY-BUILD-IMAGE" in run.stdout,
            "contains_build_path": wd.encode() in bbin,
            "contains_image_path": img.encode() in bbin,
        })
    return res


# ═══════════════════════════════════════════════════════════════════
# OP-16 acceptance
# ═══════════════════════════════════════════════════════════════════


def op16a(repros):
    """OP-16 (a): quorum >= 2 one-signature reproductions naming same digest."""
    ok = [r for r in repros if r["status"] == "OK"]
    if len(ok) < 2:
        return ("INSUFFICIENT_REPRODUCTIONS", {})
    ds = set(r["binary_digest"] for r in ok)
    if len(ds) > 1:
        return ("REPRODUCTION_CONFLICT", {"digests": sorted(ds)})
    return ("ACCEPTED", {"binary_digest": ok[0]["binary_digest"]})


def op16b(items):
    """OP-16 (b): environments from >= 2 supplier_class, matching reproductions
    from >= 2 classes.
    items: [{"supplier_class": str, "repros": [result]}]
    """
    reg_cls = set(i["supplier_class"] for i in items)
    if len(reg_cls) < 2:
        return ("ENVIRONMENT_DIVERSITY_NOT_MET",
                {"registered_supplier_classes": sorted(reg_cls)})
    by_cls = {}
    for i in items:
        ok = [r for r in i["repros"] if r["status"] == "OK"]
        for r in ok:
            by_cls.setdefault(i["supplier_class"], set()).add(r["binary_digest"])
    if len(by_cls) < 2:
        return ("ENVIRONMENT_DIVERSITY_NOT_MET",
                {"classes_with_reproductions": sorted(by_cls)})
    all_d = set()
    for ds in by_cls.values():
        all_d.update(ds)
    if len(all_d) > 1:
        return ("REPRODUCTION_CONFLICT",
                {"digests_by_class": {k: sorted(v) for k, v in by_cls.items()}})
    return ("ACCEPTED", {"binary_digest": all_d.pop()})


# ═══════════════════════════════════════════════════════════════════
# Scenarios
# ═══════════════════════════════════════════════════════════════════
S = {}

# ── E0  honest, OP-16(a) ────────────────────────────────────────
m0 = mfst("distA-env", "distA", dA_clean, dA_clean_imgd)
mir0 = _mirror(dA_clean)
er0 = [env_repro(er1_sk, m0, mir0), env_repro(er2_sk, m0, mir0)]
c0 = cer(m0, distA_pk, dA_honest_sums, dA_honest_sig, er0)
br0_1 = bin_repro("E0-1", dA_clean, dA_clean_imgd, mir0)
br0_2 = bin_repro("E0-2", dA_clean, dA_clean_imgd, mir0)
a0 = op16a([br0_1, br0_2])
S["E0"] = {
    "description": "honest, OP-16(a)",
    "ceremony": c0[0],
    "binary_repro_1_digest": br0_1.get("binary_digest"),
    "binary_repro_2_digest": br0_2.get("binary_digest"),
    "binary_repro_1_stdout": br0_1.get("stdout"),
    "bit_identical": (br0_1.get("binary_digest") is not None
                      and br0_1["binary_digest"] == br0_2.get("binary_digest")),
    "genuine_only": br0_1.get("stdout", "") == "gov: genuine behaviour",
    "acceptance": a0[0],
    "code": a0[0],
    "binary_digest": a0[1].get("binary_digest"),
    "no_path_embedded": not any(r.get("contains_build_path") or r.get("contains_image_path")
                                for r in (br0_1, br0_2)),
}

# ── E1  pipeline-produced image ────────────────────────────────
m1 = mfst("distA-env", "distA", dA_clean, dA_evil_imgd)   # evil digest
mir1 = _mirror(dA_clean)
er1_res = [env_repro(er1_sk, m1, mir1), env_repro(er2_sk, m1, mir1)]
c1 = cer(m1, distA_pk, dA_honest_sums, dA_honest_sig, er1_res)
# side: demonstrate malicious image injection (as B-A08 did)
evil_mir1 = _mirror(dA_evil)
br1_evil = bin_repro("E1-evil", dA_evil, dA_evil_imgd, evil_mir1)
S["E1"] = {
    "description": "pipeline-produced image",
    "proposed_image_digest": dA_evil_imgd,
    "reproduced_image_digest": er1_res[0][1]["image_digest"] if er1_res[0][0] == "OK" else None,
    "ceremony": c1[0],
    "code": c1[0],
    "malicious_image_demo": {
        "binary_runs_injected": br1_evil.get("runs_injected_code"),
        "stdout": br1_evil.get("stdout"),
    },
    "rev5_would_accept": ("yes: rev 5 checks digest == CI-supplied image record; "
                          "no independent reproduction"),
}

# ── E2  component substitution ──────────────────────────────────
m2 = mfst("distA-env", "distA", dA_evil, dA_evil_imgd)
c2 = cer(m2, distA_pk, dA_honest_sums, dA_honest_sig, [])
S["E2"] = {
    "description": "component substitution",
    "ceremony": c2[0],
    "ceremony_detail": c2[1],
    "code": c2[0],
}

# ── E3  carrier substitution ───────────────────────────────────
mir3 = {}
for _p, _c in dA_clean.items():
    if _p == "bin/cc":
        mir3[_c["sha256"]] = dA_evil["bin/cc"]["bytes"]     # substitution
    else:
        mir3[_c["sha256"]] = _c["bytes"]
m3 = mfst("distA-env", "distA", dA_clean, dA_clean_imgd)
er3 = env_repro(er1_sk, m3, mir3)
br3 = bin_repro("E3-br", dA_clean, dA_clean_imgd, mir3)
S["E3"] = {
    "description": "carrier substitution",
    "env_repro_status": er3[0],
    "env_repro_detail": er3[1],
    "binary_repro_status": br3["status"],
    "code": er3[0],
}

# ── E4  distA compromised, OP-16(a) ────────────────────────────
m4 = mfst("distA-env", "distA", dA_evil, dA_evil_imgd)
mir4 = _mirror(dA_evil)
er4 = [env_repro(er1_sk, m4, mir4), env_repro(er2_sk, m4, mir4)]
c4 = cer(m4, distA_pk, dA_compr_sums, dA_compr_sig, er4)
br4_1 = bin_repro("E4-1", dA_evil, dA_evil_imgd, mir4)
br4_2 = bin_repro("E4-2", dA_evil, dA_evil_imgd, mir4)
a4 = op16a([br4_1, br4_2])
S["E4"] = {
    "description": "upstream supplier distA compromised, OP-16(a)",
    "residual": "E-a upstream environment supplier (TA-12')",
    "ceremony": c4[0],
    "binary_repro_1_runs_injected": br4_1.get("runs_injected_code"),
    "binary_repro_2_runs_injected": br4_2.get("runs_injected_code"),
    "bit_identical": (br4_1.get("binary_digest") is not None
                      and br4_1["binary_digest"] == br4_2.get("binary_digest")),
    "acceptance": a4[0],
    "code": a4[0],
    "binary_digest": a4[1].get("binary_digest"),
}

# ── E5  distA compromised + distB clean, OP-16(b) ──────────────
m5A = mfst("distA-env", "distA", dA_evil, dA_evil_imgd)
mir5A = _mirror(dA_evil)
er5A = [env_repro(er1_sk, m5A, mir5A), env_repro(er2_sk, m5A, mir5A)]
c5A = cer(m5A, distA_pk, dA_compr_sums, dA_compr_sig, er5A)

m5B = mfst("distB-env", "distB", dB_clean, dB_clean_imgd)
mir5B = _mirror(dB_clean)
er5B = [env_repro(er1_sk, m5B, mir5B), env_repro(er2_sk, m5B, mir5B)]
c5B = cer(m5B, distB_pk, dB_honest_sums, dB_honest_sig, er5B)

br5A = bin_repro("E5-A", dA_evil, dA_evil_imgd, mir5A)
br5B = bin_repro("E5-B", dB_clean, dB_clean_imgd, mir5B)
a5 = op16b([{"supplier_class": "distA", "repros": [br5A]},
            {"supplier_class": "distB", "repros": [br5B]}])
S["E5"] = {
    "description": "distA compromised, OP-16(b) with distB clean",
    "ceremony_distA": c5A[0],
    "ceremony_distB": c5B[0],
    "binary_A_digest": br5A.get("binary_digest"),
    "binary_B_digest": br5B.get("binary_digest"),
    "binary_A_runs_injected": br5A.get("runs_injected_code"),
    "binary_B_runs_injected": br5B.get("runs_injected_code"),
    "acceptance": a5[0],
    "code": a5[0],
}

# ── E6  both compromised, OP-16(b) ─────────────────────────────
m6A = mfst("distA-env", "distA", dA_evil, dA_evil_imgd)
mir6A = _mirror(dA_evil)
er6A = [env_repro(er1_sk, m6A, mir6A), env_repro(er2_sk, m6A, mir6A)]
c6A = cer(m6A, distA_pk, dA_compr_sums, dA_compr_sig, er6A)

m6B = mfst("distB-env", "distB", dB_evil, dB_evil_imgd)
mir6B = _mirror(dB_evil)
er6B = [env_repro(er1_sk, m6B, mir6B), env_repro(er2_sk, m6B, mir6B)]
c6B = cer(m6B, distB_pk, dB_compr_sums, dB_compr_sig, er6B)

br6A = bin_repro("E6-A", dA_evil, dA_evil_imgd, mir6A)
br6B = bin_repro("E6-B", dB_evil, dB_evil_imgd, mir6B)
a6 = op16b([{"supplier_class": "distA", "repros": [br6A]},
            {"supplier_class": "distB", "repros": [br6B]}])
S["E6"] = {
    "description": "both distA and distB compromised, OP-16(b)",
    "residual": "E-b every environment supplier used",
    "ceremony_distA": c6A[0],
    "ceremony_distB": c6B[0],
    "binary_A_digest": br6A.get("binary_digest"),
    "binary_B_digest": br6B.get("binary_digest"),
    "binary_A_runs_injected": br6A.get("runs_injected_code"),
    "binary_B_runs_injected": br6B.get("runs_injected_code"),
    "bit_identical": (br6A.get("binary_digest") is not None
                      and br6A["binary_digest"] == br6B.get("binary_digest")),
    "acceptance": a6[0],
    "code": a6[0],
    "binary_digest": a6[1].get("binary_digest") if a6[0] == "ACCEPTED" else None,
}

# ── E7  clean distA + clean distB, OP-16(b) ────────────────────
m7A = mfst("distA-env", "distA", dA_clean, dA_clean_imgd)
mir7A = _mirror(dA_clean)
er7A = [env_repro(er1_sk, m7A, mir7A), env_repro(er2_sk, m7A, mir7A)]
c7A = cer(m7A, distA_pk, dA_honest_sums, dA_honest_sig, er7A)

m7B = mfst("distB-env", "distB", dB_clean, dB_clean_imgd)
mir7B = _mirror(dB_clean)
er7B = [env_repro(er1_sk, m7B, mir7B), env_repro(er2_sk, m7B, mir7B)]
c7B = cer(m7B, distB_pk, dB_honest_sums, dB_honest_sig, er7B)

br7A = bin_repro("E7-A", dA_clean, dA_clean_imgd, mir7A)
br7B = bin_repro("E7-B", dB_clean, dB_clean_imgd, mir7B)
a7 = op16b([{"supplier_class": "distA", "repros": [br7A]},
            {"supplier_class": "distB", "repros": [br7B]}])
S["E7"] = {
    "description": "clean distA + clean distB, OP-16(b)",
    "ceremony_distA": c7A[0],
    "ceremony_distB": c7B[0],
    "binary_A_digest": br7A.get("binary_digest"),
    "binary_B_digest": br7B.get("binary_digest"),
    "binary_A_stdout": br7A.get("stdout"),
    "binary_B_stdout": br7B.get("stdout"),
    "bit_identical": (br7A.get("binary_digest") is not None
                      and br7A["binary_digest"] == br7B.get("binary_digest")),
    "acceptance": a7[0],
    "code": a7[0],
    "binary_digest": a7[1].get("binary_digest") if a7[0] == "ACCEPTED" else None,
    "no_path_embedded": not any(r.get("contains_build_path") or r.get("contains_image_path")
                                for r in (br7A, br7B)),
}

# ── E8  environment-reproducer process compromise ───────────────
# E8a: one honest, one compromised (signs malicious digest)
m8 = mfst("distA-env", "distA", dA_clean, dA_clean_imgd)
mir8 = _mirror(dA_clean)
er8a_1 = env_repro(er1_sk, m8, mir8)                          # honest
er8a_2 = env_repro(er2_sk, m8, mir8, forced_digest=dA_evil_imgd)  # compromised
c8a = cer(m8, distA_pk, dA_honest_sums, dA_honest_sig, [er8a_1, er8a_2])

# E8b: both compromised — manifest claims malicious digest
m8b = mfst("distA-env", "distA", dA_clean, dA_evil_imgd)
er8b_1 = env_repro(er1_sk, m8b, mir8, forced_digest=dA_evil_imgd)
er8b_2 = env_repro(er2_sk, m8b, mir8, forced_digest=dA_evil_imgd)
c8b = cer(m8b, distA_pk, dA_honest_sums, dA_honest_sig, [er8b_1, er8b_2])

S["E8"] = {
    "description": "environment-reproducer process compromise",
    "E8a": {
        "description": "one honest reproducer, one compromised",
        "honest_digest": er8a_1[1]["image_digest"][:16] + "...",
        "compromised_digest": er8a_2[1]["image_digest"][:16] + "...",
        "ceremony": c8a[0],
        "code": c8a[0],
    },
    "E8b": {
        "description": "both reproducers compromised",
        "residual": "environment reproducer quorum (TB-S1 class)",
        "ceremony": c8b[0],
        "code": c8b[0],
    },
}

# ── E9  OP-16(b) with only one supplier class ──────────────────
m9 = mfst("distA-env", "distA", dA_clean, dA_clean_imgd)
mir9 = _mirror(dA_clean)
er9 = [env_repro(er1_sk, m9, mir9), env_repro(er2_sk, m9, mir9)]
c9 = cer(m9, distA_pk, dA_honest_sums, dA_honest_sig, er9)
br9 = bin_repro("E9-A", dA_clean, dA_clean_imgd, mir9)
a9 = op16b([{"supplier_class": "distA", "repros": [br9]}])
S["E9"] = {
    "description": "OP-16(b) with only one supplier class",
    "ceremony": c9[0],
    "acceptance": a9[0],
    "code": a9[0],
}

# ═══════════════════════════════════════════════════════════════════
# Toolchain snapshot (after)
# ═══════════════════════════════════════════════════════════════════
tc_after = {os.path.basename(p): Hfile(p) for p in _tc_files}

# ═══════════════════════════════════════════════════════════════════
# Verdicts
# ═══════════════════════════════════════════════════════════════════
V = {
    "E0_code_ACCEPTED":                      S["E0"]["code"] == "ACCEPTED",
    "E0_bit_identical":                      S["E0"]["bit_identical"],
    "E0_genuine_only":                       S["E0"]["genuine_only"],
    "E1_code_ENVIRONMENT_NOT_REPRODUCED":    S["E1"]["code"] == "ENVIRONMENT_NOT_REPRODUCED",
    "E1_malicious_injection_demonstrated":   S["E1"]["malicious_image_demo"]["binary_runs_injected"] is True,
    "E2_code_ENVIRONMENT_COMPONENT_UNVERIFIED": S["E2"]["code"] == "ENVIRONMENT_COMPONENT_UNVERIFIED",
    "E3_code_INPUT_DIGEST_MISMATCH":         S["E3"]["code"] == "INPUT_DIGEST_MISMATCH",
    "E3_binary_repro_also_refuses":          S["E3"]["binary_repro_status"] == "INPUT_DIGEST_MISMATCH",
    "E4_code_ACCEPTED":                      S["E4"]["code"] == "ACCEPTED",
    "E4_malicious_injection":                S["E4"]["binary_repro_1_runs_injected"] is True,
    "E5_code_REPRODUCTION_CONFLICT":         S["E5"]["code"] == "REPRODUCTION_CONFLICT",
    "E6_code_ACCEPTED":                      S["E6"]["code"] == "ACCEPTED",
    "E6_malicious_injection":                S["E6"]["binary_A_runs_injected"] is True,
    "E6_bit_identical":                      S["E6"]["bit_identical"],
    "E7_code_ACCEPTED":                      S["E7"]["code"] == "ACCEPTED",
    "E7_bit_identical":                      S["E7"]["bit_identical"],
    "E8a_code_ENV_REPRODUCTION_CONFLICT":    S["E8"]["E8a"]["code"] == "ENVIRONMENT_REPRODUCTION_CONFLICT",
    "E8b_code_REGISTERED":                   S["E8"]["E8b"]["code"] == "REGISTERED",
    "E9_code_ENVIRONMENT_DIVERSITY_NOT_MET": S["E9"]["code"] == "ENVIRONMENT_DIVERSITY_NOT_MET",
    "toolchain_unchanged":                   tc_before == tc_after,
    "no_build_or_image_path_embedded":       (S["E0"]["no_path_embedded"]
                                              and S["E7"]["no_path_embedded"]),
}

# ═══════════════════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════════════════
rustc_ver = subprocess.run(
    [RUSTC, "--version"], capture_output=True, text=True,
    env=cenv()).stdout.strip()
cc_ver = subprocess.run(
    ["/usr/bin/cc", "--version"], capture_output=True, text=True,
    env=cenv()).stdout.splitlines()[0]

out = {
    "probe": "ENV6-build-environment (R-BENV-1..R-BENV-5, OP-16 a/b), AR-0015",
    "rustc": rustc_ver,
    "cc": cc_ver,
    "rustc_home_deviation": RUSTC_HOME_DEV,
    "source_sha256": H(SRC.encode()),
    "inject_o_sha256": H(INJECT_O),
    "image_digests": {
        "distA_clean": dA_clean_imgd,
        "distA_evil": dA_evil_imgd,
        "distB_clean": dB_clean_imgd,
        "distB_evil": dB_evil_imgd,
    },
    "toolchain_before": tc_before,
    "toolchain_after": tc_after,
    "scenarios": S,
    "verdicts": V,
}

txt = json.dumps(out, indent=1, sort_keys=True)
# sanitise paths
txt = txt.replace(BASE, "<scratch>")
txt = txt.replace(W, "<scratch>/work")
txt = txt.replace(ACCOUNT_HOME, "<home>")
import re
txt = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt)
print(txt)
