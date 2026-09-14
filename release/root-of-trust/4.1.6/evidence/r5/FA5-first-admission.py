#!/usr/bin/env python3
# AR-0011 (architect) correction: the install mutant is now evaluated on the INS1 shape (see install_from_buffer).
"""FA5 first-admission evidence (AR-0011, RoT-1 revision 5).

Patterns adapted from:
  specialist-a/evidence/E3-first-binary-acceptance.py SHA-256 243a472a49b90089ccc624d223144437f66e2833f27c1cfb1ee7d3a334c44087
  specialist-a/evidence/gov_accept_reference.py       SHA-256 56f101df8ac2055a8088220e5fb5f6f05350ddecfcb3c4821796efba87571b11
  specialist-b/evidence/F2-first-tcb-admission.py     SHA-256 4f052150205c391eac7cb26ba7e3d6a2fe241ae09e44a75ad4b2272bf8bb52f4
  specialist-b/evidence/F4-external-measurement.py    SHA-256 035d79ba57ed8b34cbbef7c077040dca049bbfa31ecc8520a15a3bce6ca35784

Environment: env -i PATH=/usr/bin:/bin HOME=<S>/home PYTHONDONTWRITEBYTECODE=1
Output: FA5-first-admission.json
"""
import base64, copy, hashlib, importlib.util, json, os, re, subprocess, sys, tempfile, time

sys.dont_write_bytecode = True
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("GA", os.path.join(HERE, "gov_admit_reference.py"))
GA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GA)

BASE_SCRATCH = os.environ.get("FA5_SCRATCH") or os.path.join(os.environ.get("TMPDIR", "/tmp"), "fa5-base")
os.makedirs(BASE_SCRATCH, exist_ok=True)
S = tempfile.mkdtemp(prefix="run-", dir=BASE_SCRATCH)
BINDIR = os.path.join(S, "binaries"); os.makedirs(BINDIR, exist_ok=True)
GOV = os.environ.get("GOV")
TARGET = "x86_64-linux"
ADMITTER_DIGEST = GA.sha256d(open(os.path.join(HERE, "gov_admit_reference.py"), "rb").read())

# ========== KEYS ==========
KEYS = {}
def key(label):
    if label not in KEYS:
        sk = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"rot1r5:" + label.encode()).digest())
        raw = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        KEYS[label] = (sk, raw, "ed25519:" + hashlib.sha256(raw).hexdigest())
    return KEYS[label]

kid = lambda l: key(l)[2]
pub64 = lambda l: base64.b64encode(key(l)[1]).decode()
pub_map = lambda ls: {kid(l): pub64(l) for l in ls}

def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

def sha256d(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()

def pae(pt, body):
    t = pt.encode()
    return b"DSSEv1 %d %s %d %s" % (len(t), t, len(body), body)

def fp(lineage, rv, rd, pv, pd, seq, sd):
    ep = {"lineage": lineage, "root_version": rv, "root_digest": rd,
          "policy_version": pv, "policy_digest": pd,
          "state_sequence": seq, "state_digest": sd}
    return "gov-state:%s:%d:%s" % (lineage[7:15], seq, hashlib.sha256(canon(ep)).hexdigest()[:32])

# ========== ENVELOPE ==========
TP = "application/vnd.rot1r5."
def envelope(suffix, payload, signers, bad_sig=False):
    body = canon(payload)
    pt = TP + suffix
    sigs = []
    for s in signers:
        sk, raw, k = key(s)
        sig = sk.sign(pae(pt, body))
        if bad_sig:
            sig = bytes([sig[0] ^ 1]) + sig[1:]
        sigs.append({"keyid": k, "sig": base64.b64encode(sig).decode()})
    return {"purpose": suffix.split("+")[0], "payload": payload, "digest": sha256d(body),
            "env": {"payloadType": pt, "payload": base64.b64encode(body).decode(), "signatures": sigs}}

def to_stmts(envs):
    out = []
    for e in envs:
        ev = e["env"]
        body = base64.b64decode(ev["payload"])
        pt = ev["payloadType"]
        p = GA.TYPE_PURPOSE.get(pt)
        if p is None:
            continue
        out.append({"type": pt, "purpose": p, "body": body, "payload": json.loads(body),
                    "digest": e["digest"], "sigs": ev["signatures"]})
    return out

# ========== SOURCE ==========
def src(tag):
    return {"build_profile_digest": sha256d(("profile-" + tag).encode()), "commit": "c-" + tag,
            "content_digest": sha256d(("tree-" + tag).encode())}
SRC7, SRC8 = src("R7"), src("R8")
INP7, INP8 = sha256d(b"inputs-R7"), sha256d(b"inputs-R8")
CAND7 = sha256d(canon({"kind": "candidate", "release_id": "R7", "source": SRC7}))
CAND8 = sha256d(canon({"kind": "candidate", "release_id": "R8", "source": SRC8}))

# ========== WORLD ==========
ALL_V1 = ["r1","r2","r3","ts1","p1","p2","p3","v1","v2","f1","g1","g2","g3"]
ALL_V2 = ALL_V1 + ["p4"]

# -- Grants (variant B: delegated registration keys)
G1B = {"root": {"keys": [kid(x) for x in ("r1","r2","r3")], "threshold": 2},
       "trust-policy": {"keys": [kid(x) for x in ("r1","r2","r3")], "threshold": 2},
       "trust-state": {"keys": [kid("ts1")], "threshold": 1},
       "reproducer": {"keys": [kid(x) for x in ("p1","p2","p3")], "threshold": 2},
       "verification-attestation": {"keys": [kid(x) for x in ("v1","v2")], "threshold": 1},
       "release-final": {"keys": [kid("f1")], "threshold": 1},
       "release-registration": {"keys": [kid(x) for x in ("g1","g2","g3")], "threshold": 2}}

G2B = copy.deepcopy(G1B)
G2B["reproducer"] = {"keys": [kid(x) for x in ("p1","p4")], "threshold": 2}

# Variant A: registration on root keys
G1A = copy.deepcopy(G1B)
G1A["release-registration"] = {"keys": [kid(x) for x in ("r1","r2","r3")], "threshold": 2}
G2A = copy.deepcopy(G2B)
G2A["release-registration"] = {"keys": [kid(x) for x in ("r1","r2","r3")], "threshold": 2}

# -- Roots
ROOT1 = envelope("root+json", {"version": 1, "previous_digest": None, "keys": pub_map(ALL_V1),
                                "grants": G1B, "revoked_keys": []}, ["r1","r2","r3"])
LINEAGE = ROOT1["digest"]
ROOT2 = envelope("root+json", {"version": 2, "previous_digest": LINEAGE, "keys": pub_map(ALL_V2),
                                "grants": G2B, "revoked_keys": [kid("p2"), kid("p3")]}, ["r1","r2"])
ROOT1A = envelope("root+json", {"version": 1, "previous_digest": None, "keys": pub_map(ALL_V1),
                                 "grants": G1A, "revoked_keys": []}, ["r1","r2","r3"])
ROOT2A = envelope("root+json", {"version": 2, "previous_digest": ROOT1A["digest"],
                                 "keys": pub_map(ALL_V2), "grants": G2A,
                                 "revoked_keys": [kid("p2"), kid("p3")]}, ["r1","r2"])

# -- Trust Policy
TPS1 = envelope("trust-policy+json",
    {"policy_version": 1,
     "registration": {"min_verification_records": 1, "reproduction_quorum": 2},
     "bootstrap": {"channel_quorum": 2, "image_record_max_validity_days": 30},
     "admitter_digests": [ADMITTER_DIGEST]}, ["r1","r2"])
TPS1_Q1 = envelope("trust-policy+json",
    {"policy_version": 1,
     "registration": {"min_verification_records": 1, "reproduction_quorum": 2},
     "bootstrap": {"channel_quorum": 1, "image_record_max_validity_days": 30},
     "admitter_digests": [ADMITTER_DIGEST]}, ["r1","r2"])
TPS1_MIN2 = envelope("trust-policy+json",
    {"policy_version": 1,
     "registration": {"min_verification_records": 2, "reproduction_quorum": 2},
     "bootstrap": {"channel_quorum": 2, "image_record_max_validity_days": 30},
     "admitter_digests": [ADMITTER_DIGEST]}, ["r1","r2"])

# -- Verification attestations
VA7 = envelope("verification-attestation+json",
    {"candidate_statement_digest": CAND7, "verdict": "ACCEPTED", "source": SRC7,
     "inputs_manifest_digest": INP7}, ["v1"])
VA7B = envelope("verification-attestation+json",
    {"candidate_statement_digest": CAND7, "verdict": "ACCEPTED", "source": SRC7,
     "inputs_manifest_digest": INP7}, ["v2"])
VA8 = envelope("verification-attestation+json",
    {"candidate_statement_digest": CAND8, "verdict": "ACCEPTED", "source": SRC8,
     "inputs_manifest_digest": INP8}, ["v1"])
VA8_REJ = envelope("verification-attestation+json",
    {"candidate_statement_digest": CAND8, "verdict": "REJECTED", "source": SRC8,
     "inputs_manifest_digest": INP8}, ["v1"])

# -- Release finals
FINAL7 = envelope("release-final+json",
    {"release_id": "R7", "sequence": 7, "promoted_from": CAND7, "source": SRC7,
     "kernel_tree_digest": sha256d(b"kernel-R7")}, ["f1"])
FINAL8 = envelope("release-final+json",
    {"release_id": "R8", "sequence": 8, "promoted_from": CAND8, "source": SRC8,
     "kernel_tree_digest": sha256d(b"kernel-R8")}, ["f1"])

# -- Release registrations (variant B: g1, g2)
REG7 = envelope("release-registration+json",
    {"release_id": "R7", "sequence": 7, "final_statement_digest": FINAL7["digest"],
     "candidate_statement_digest": CAND7, "source": SRC7, "inputs_manifest_digest": INP7,
     "targets": [TARGET], "verification_records": [VA7["digest"]], "units": {}}, ["g1","g2"])
REG8 = envelope("release-registration+json",
    {"release_id": "R8", "sequence": 8, "final_statement_digest": FINAL8["digest"],
     "candidate_statement_digest": CAND8, "source": SRC8, "inputs_manifest_digest": INP8,
     "targets": [TARGET], "verification_records": [VA8["digest"]], "units": {}}, ["g1","g2"])
# Variant A registrations
REG7A = envelope("release-registration+json",
    {"release_id": "R7", "sequence": 7, "final_statement_digest": FINAL7["digest"],
     "candidate_statement_digest": CAND7, "source": SRC7, "inputs_manifest_digest": INP7,
     "targets": [TARGET], "verification_records": [VA7["digest"]], "units": {}}, ["r1","r2"])
REG8A = envelope("release-registration+json",
    {"release_id": "R8", "sequence": 8, "final_statement_digest": FINAL8["digest"],
     "candidate_statement_digest": CAND8, "source": SRC8, "inputs_manifest_digest": INP8,
     "targets": [TARGET], "verification_records": [VA8["digest"]], "units": {}}, ["r1","r2"])

# -- TBMs and Binaries
def make_tbm(rv, pv, tss_seq, tss_dig, source, inp, build="release", lineage=None):
    return {"build": build, "inputs_manifest_digest": inp, "lineage": lineage or LINEAGE,
            "policy_version": pv, "root_version": rv, "source": source,
            "trust_state": {"digest": tss_dig, "sequence": tss_seq}}

def make_binary(name, tbm):
    tbm_json = canon(tbm).decode()
    body = "#!/bin/sh\n# GOV-TBM %s\n: > \"${GOV_MARKERS:-/nonexistent}/%s\"\n" % (tbm_json, name)
    bdata = body.encode()
    return bdata, sha256d(bdata)

# -- Trust state T1 (initial, empty)
T1 = envelope("trust-state+json",
    {"sequence": 1, "issued_at": "2026-01-01T00:00:00Z",
     "references": {"root": {"version": 1, "digest": LINEAGE},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": [], "registrations": [], "published_binaries": [], "revocations": []}, ["ts1"])

# B7 (genuine, later revoked)
TBM7 = make_tbm(1, 1, 1, T1["digest"], SRC7, INP7)
TBM7_D = sha256d(canon(TBM7))
B7_BYTES, B7_D = make_binary("B7", TBM7)

# B7x (malicious, produced by stolen keys)
TBM7x = make_tbm(1, 1, 1, T1["digest"], SRC7, INP7)
B7x_BYTES, B7x_D = make_binary("B7x", TBM7x)

# -- Reproductions for R7
def repro(rid, source, inp, target, bdig, tbm_d, signer, env_d="env1", signers=None):
    return envelope("binary-reproduction+json",
        {"release_id": rid, "source": source, "inputs_manifest_digest": inp, "target": target,
         "binary_digest": bdig, "tbm_digest": tbm_d, "environment_digest": env_d},
        signers or [signer])

RP7 = [repro("R7", SRC7, INP7, TARGET, B7_D, TBM7_D, k) for k in ("p1","p2","p3")]
# B7x reproductions: p1 (to make quorum check reachable), p2, p3 (stolen)
RP7x = [repro("R7", SRC7, INP7, TARGET, B7x_D, sha256d(canon(TBM7x)), k) for k in ("p1","p2","p3")]

# -- T5: publishes B7
T5 = envelope("trust-state+json",
    {"sequence": 5, "issued_at": "2026-03-01T00:00:00Z",
     "references": {"root": {"version": 1, "digest": LINEAGE},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": [{"sequence": 1, "digest": T1["digest"]}],
     "registrations": [REG7["digest"]], "published_binaries": [B7_D], "revocations": []}, ["ts1"])
FP5 = fp(LINEAGE, 1, LINEAGE, 1, TPS1["digest"], 5, T5["digest"])

# -- T6: B7x also published (compromised pipeline)
T6 = envelope("trust-state+json",
    {"sequence": 6, "issued_at": "2026-04-01T00:00:00Z",
     "references": {"root": {"version": 1, "digest": LINEAGE},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": [{"sequence": 1, "digest": T1["digest"]}, {"sequence": 5, "digest": T5["digest"]}],
     "registrations": [REG7["digest"]], "published_binaries": [B7_D, B7x_D],
     "revocations": []}, ["ts1"])

# -- T7: same as T6 but later
T7 = envelope("trust-state+json",
    {"sequence": 7, "issued_at": "2026-05-01T00:00:00Z",
     "references": {"root": {"version": 1, "digest": LINEAGE},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": [{"sequence": 1, "digest": T1["digest"]}, {"sequence": 5, "digest": T5["digest"]},
                      {"sequence": 6, "digest": T6["digest"]}],
     "registrations": [REG7["digest"]], "published_binaries": [B7_D, B7x_D],
     "revocations": []}, ["ts1"])

PRIOR9 = [{"sequence": 1, "digest": T1["digest"]}, {"sequence": 5, "digest": T5["digest"]},
           {"sequence": 6, "digest": T6["digest"]}, {"sequence": 7, "digest": T7["digest"]}]
REVS9 = sorted([B7_D, B7x_D])

# -- T9: remediation (root v2, revokes B7 and B7x). B8 is NOT yet published here.
T9 = envelope("trust-state+json",
    {"sequence": 9, "issued_at": "2026-08-01T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR9,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D]),
     "revocations": REVS9}, ["ts1"])

# B8 (genuine replacement) -- built under T9, no circularity
TBM8 = make_tbm(2, 1, 9, T9["digest"], SRC8, INP8)
TBM8_D = sha256d(canon(TBM8))
B8_BYTES, B8_D = make_binary("B8", TBM8)

# Reproductions for R8: p1, p4 (root v2 keys)
RP8 = [repro("R8", SRC8, INP8, TARGET, B8_D, TBM8_D, k) for k in ("p1","p4")]

# -- T10: publishes B8
PRIOR10 = PRIOR9 + [{"sequence": 9, "digest": T9["digest"]}]
T10 = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]),
     "revocations": REVS9}, ["ts1"])
FP10 = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, T10["digest"])

# -- T10 variant: B7x revocation removed (for FB2b variant)
T10_norev = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]),
     "revocations": sorted([B7_D])}, ["ts1"])
FP10_norev = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, T10_norev["digest"])

# T10 with channel_quorum 1
T10_Q1 = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1_Q1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]),
     "revocations": REVS9}, ["ts1"])
FP10_Q1 = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1_Q1["digest"], 10, T10_Q1["digest"])

# T10 with B8 NOT in published_binaries (for skip_published mutant detection)
T10_nopub = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D]),
     "revocations": REVS9}, ["ts1"])
FP10_nopub = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, T10_nopub["digest"])

# -- Malicious/variant roots for mutant detection --
# Root v2 with broken link (for skip_root_link)
root_v2_badlink = envelope("root+json",
    {"version": 2, "previous_digest": "sha256:" + "0"*64, "keys": pub_map(ALL_V2),
     "grants": G2B, "revoked_keys": [kid("p2"), kid("p3")]}, ["r1","r2"])
tss_badlink = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": root_v2_badlink["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]),
     "revocations": REVS9}, ["ts1"])
fp_badlink = fp(LINEAGE, 2, root_v2_badlink["digest"], 1, TPS1["digest"], 10, tss_badlink["digest"])

# Root v2 with KS-7 violation: revoked keys granted (for skip_ks7)
g_ks7 = copy.deepcopy(G2B)
g_ks7["reproducer"] = {"keys": [kid(x) for x in ("p1","p2","p3","p4")], "threshold": 2}
root_v2_ks7 = envelope("root+json",
    {"version": 2, "previous_digest": LINEAGE, "keys": pub_map(ALL_V2),
     "grants": g_ks7, "revoked_keys": [kid("p2"), kid("p3")]}, ["r1","r2"])
tss_ks7 = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": root_v2_ks7["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]),
     "revocations": REVS9}, ["ts1"])
fp_ks7 = fp(LINEAGE, 2, root_v2_ks7["digest"], 1, TPS1["digest"], 10, tss_ks7["digest"])

# Root v2 with FTC violation: reproducer key in verification-attestation (for skip_ftc)
g_ftc = copy.deepcopy(G2B)
g_ftc["verification-attestation"] = {"keys": [kid("v1"), kid("v2"), kid("p1")], "threshold": 1}
root_v2_ftc = envelope("root+json",
    {"version": 2, "previous_digest": LINEAGE, "keys": pub_map(ALL_V2),
     "grants": g_ftc, "revoked_keys": [kid("p2"), kid("p3")]}, ["r1","r2"])
tss_ftc = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": root_v2_ftc["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10,
     "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]),
     "revocations": REVS9}, ["ts1"])
fp_ftc = fp(LINEAGE, 2, root_v2_ftc["digest"], 1, TPS1["digest"], 10, tss_ftc["digest"])

# Reproductions with wrong tbm_digest (for skip_tbm mutant detection)
RP8_badtbm = [repro("R8", SRC8, INP8, TARGET, B8_D, "sha256:" + "a"*64, k) for k in ("p1","p4")]

# Planted binary
TBM_planted = make_tbm(2, 1, 9, T9["digest"], SRC8, INP8)
BPLANTED_BYTES, BPLANTED_D = make_binary("Bplanted", TBM_planted)

# B8 variants
B8_SELF = B8_BYTES  # identical self-built
B8_DIFF = B8_BYTES[:-2] + bytes([B8_BYTES[-2] ^ 1]) + B8_BYTES[-1:]
B8_DIFF_D = sha256d(B8_DIFF)

# B8x: malicious variant
TBM_B8x = make_tbm(2, 1, 9, T9["digest"], SRC8, INP8)
B8x_BYTES, B8x_D = make_binary("B8x", TBM_B8x)

# Write binaries to disk
for name, data in [("B7", B7_BYTES), ("B7x", B7x_BYTES), ("B8", B8_BYTES),
                    ("B8x", B8x_BYTES), ("Bplanted", BPLANTED_BYTES), ("B8-diff", B8_DIFF)]:
    p = os.path.join(BINDIR, name)
    with open(p, "wb") as f:
        f.write(data)
    os.chmod(p, 0o755)

# ========== STATEMENT BUNDLES ==========
FULL = [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8
FULL_Q1 = [ROOT1, ROOT2, TPS1_Q1, T1, T5, T6, T7, T9, T10_Q1, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8

# ========== RUN HELPER ==========
V = GA.Verifier(S)

def run(label, binary_bytes, fps, stmts_list, target=TARGET, flags=None, evaluator=ADMITTER_DIGEST):
    stmts = to_stmts(stmts_list)
    r = GA.accept(binary_bytes, fps, stmts, target, evaluator, flags=flags, verifier=V, workdir=S)
    return r

# ========== REV-4 CONTROL ==========
def r4_path_b(binary_d, stmts_list):
    """Rev-4 path (b): signatures + TSS reference, no fingerprint, no negatives."""
    for s in stmts_list:
        if s["purpose"] == "trust-state":
            if binary_d in s["payload"].get("published_binaries", []):
                return "PASS(signatures+TSS_reference_only)"
    return "FAIL(not_in_TSS)"

def r4_path_c(binary_path, markers_dir):
    """Rev-4 path (c): execute candidate and compare printed values."""
    os.makedirs(markers_dir, exist_ok=True)
    r = subprocess.run([binary_path, "version", "--trust"], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "GOV_MARKERS": markers_dir})
    marker = os.path.join(markers_dir, os.path.basename(binary_path))
    return {"executed": os.path.exists(marker), "output": r.stdout.strip()}

# ========== SCENARIOS ==========
out = {"probe": "FA5 first-admission evidence (AR-0011, revision 5)",
       "executor": "gov_admit_reference.py",
       "openssl": subprocess.run(["openssl","version"], capture_output=True, text=True).stdout.strip(),
       "lineage": LINEAGE, "fp_t10": FP10, "fp_t5": FP5}
scenarios = {}

def sc(sid, attack, expected, observed, holds, extras=None):
    r = {"attack": attack, "expected": expected,
         "observed": observed if isinstance(observed, str) else observed.get("result","?"),
         "holds": holds, "candidate_executed": False}
    if extras:
        r.update(extras)
    scenarios[sid] = r

# --- V00: honest first admission of B8
r00 = run("V00", B8_BYTES, [FP10, FP10], FULL)
sc("V00", "honest B8, two channels fp(t10)", "ACCEPTED", r00, r00["result"] == "ACCEPTED")
# V00 under channel_quorum 1
r00q1 = run("V00q1", B8_BYTES, [FP10_Q1], FULL_Q1)
sc("V00_Q1", "honest B8, one channel, quorum 1", "ACCEPTED", r00q1, r00q1["result"] == "ACCEPTED")
# V00 install
inst_dir = os.path.join(S, "install_v00", "bin")
os.makedirs(inst_dir, exist_ok=True)
inst_dest = os.path.join(inst_dir, "gov")
inst_r = GA.install_from_buffer(B8_BYTES, inst_dest, B8_D)
sc("V00_install", "install from buffer", "reread_equal", inst_r, inst_r["reread_equal"],
   extras={"location_protected": inst_r["location_protected"]})

# --- FB1a: revoked B7, only t7 served, operator types fp(t10)
STRIPPED_FB1 = [ROOT1, TPS1, T1, T5, T7, VA7, FINAL7, REG7] + RP7
r_fb1a = run("FB1a", B7_BYTES, [FP10, FP10], STRIPPED_FB1)
sc("FB1a", "revoked B7, t9/t10 withheld, fp(t10)", "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH",
   r_fb1a, r_fb1a["result"] != "ACCEPTED")
# FB1b: everything served
r_fb1b = run("FB1b", B7_BYTES, [FP10, FP10], FULL)
sc("FB1b", "revoked B7, everything served", "BINARY_REVOKED", r_fb1b, r_fb1b["result"] == "BINARY_REVOKED")
# FB1 rev-4 control
fb1_ctl = r4_path_b(B7_D, [s for s in to_stmts(STRIPPED_FB1) if s["purpose"] == "trust-state"])
sc("FB1_r4ctl", "rev-4 path(b) on FB1a bundle", "PASS", fb1_ctl, fb1_ctl.startswith("PASS"),
   extras={"label": "revision-4 control"})

# --- FB2a: remediated compromise, root v1 and t6
STRIPPED_FB2 = [ROOT1, TPS1, T1, T5, T6, VA7, FINAL7, REG7] + RP7x
r_fb2a = run("FB2a", B7x_BYTES, [FP10, FP10], STRIPPED_FB2)
sc("FB2a", "B7x, root v1 + t6, fp(t10)", "refused", r_fb2a, r_fb2a["result"] != "ACCEPTED")
# FB2b: everything served
r_fb2b = run("FB2b", B7x_BYTES, [FP10, FP10], FULL)
sc("FB2b", "B7x, everything served", "BINARY_REVOKED", r_fb2b, r_fb2b["result"] == "BINARY_REVOKED")
# FB2b variant: B7x revocation removed from T10, stolen keys still revoked in root v2
r_fb2bv = run("FB2bv", B7x_BYTES, [FP10_norev, FP10_norev],
              [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10_norev, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8)
sc("FB2b_variant", "B7x, revocation removed, stolen keys revoked in root v2",
   "REPRODUCTION_QUORUM_NOT_MET", r_fb2bv, r_fb2bv["result"] == "REPRODUCTION_QUORUM_NOT_MET",
   extras={"spec_note": "p1 also reproduces B7x so quorum check is reachable; without p1 result would be RELEASE_UNREGISTERED"})
# FB2c: root v2 withheld
r_fb2c = run("FB2c", B7x_BYTES, [FP10, FP10],
             [ROOT1, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8)
sc("FB2c", "B7x, root v2 withheld, t10 served", "refused", r_fb2c, r_fb2c["result"] != "ACCEPTED")
# FB2 rev-4 control
fb2_ctl = r4_path_b(B7x_D, [s for s in to_stmts(STRIPPED_FB2) if s["purpose"] == "trust-state"])
sc("FB2_r4ctl", "rev-4 path(b) on FB2a bundle", "PASS", fb2_ctl, fb2_ctl.startswith("PASS"),
   extras={"label": "revision-4 control"})

# --- FB3: moved tag / planted binary
r_fb3 = run("FB3", BPLANTED_BYTES, [FP10, FP10], FULL)
sc("FB3", "planted binary claiming genuine source", "refused", r_fb3, r_fb3["result"] != "ACCEPTED",
   extras={"candidate_executed": False})
# FB3 rev-4 path(c) control
fb3_markers = os.path.join(S, "fb3_markers")
fb3_ctl = r4_path_c(os.path.join(BINDIR, "Bplanted"), fb3_markers)
sc("FB3_r4ctl", "rev-4 path(c) executes candidate", "PASS+marker", fb3_ctl,
   fb3_ctl.get("executed", False), extras={"label": "revision-4 control", "candidate_executed": fb3_ctl.get("executed")})

# --- BUILD1: self-built binary
r_build1_same = run("BUILD1same", B8_SELF, [FP10, FP10], FULL)
sc("BUILD1_identical", "self-built identical to B8", "ACCEPTED", r_build1_same,
   r_build1_same["result"] == "ACCEPTED")
r_build1_diff = run("BUILD1diff", B8_DIFF, [FP10, FP10], FULL)
sc("BUILD1_different", "self-built one byte different", "refused", r_build1_diff,
   r_build1_diff["result"] != "ACCEPTED")

# --- PH4: Phase 4 legacy + self-evaluation
legacy_info = {}
if GOV:
    h = subprocess.run([GOV, "--help"], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home")})
    t = subprocess.run([GOV, "trust", "--help"], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home")})
    legacy_info = {"help_exit": h.returncode, "verify_artifact_in_help": "verify-artifact" in h.stdout,
                   "trust_help_exit": t.returncode}
r_ph4 = run("PH4", B8_BYTES, [FP10, FP10], FULL)
sc("PH4_accept", "gov-admit accepts B8", "ACCEPTED", r_ph4, r_ph4["result"] == "ACCEPTED",
   extras={"legacy": legacy_info})
r_ph4_self = run("PH4self", B8_BYTES, [FP10, FP10], FULL, evaluator=B8_D)
sc("PH4_self_eval", "evaluator_digest == candidate_digest", "SELF_EVALUATION_REFUSED",
   r_ph4_self, r_ph4_self["result"] == "SELF_EVALUATION_REFUSED")

# --- CI1: image admission
NOW_EPOCH = 1726272000  # 2024-09-14 approx
rec_ci = {"binary_digest": B8_D, "target": TARGET, "release_id": "R8", "lineage": LINEAGE,
          "state_fingerprint": FP10, "admitted_at": NOW_EPOCH, "admitter_digest": ADMITTER_DIGEST,
          "valid_until": NOW_EPOCH + 30 * 86400, "location_protected": True}
rec_dir_ci = os.path.join(S, "ci_records")
os.makedirs(rec_dir_ci, exist_ok=True)
vts_ci = os.path.join(rec_dir_ci, "vts-" + LINEAGE[:16])
os.makedirs(vts_ci, exist_ok=True)
with open(os.path.join(vts_ci, "admission-%s.json" % B8_D[:24]), "w") as f:
    json.dump(rec_ci, f)
b8_path = os.path.join(BINDIR, "B8")
r_ci_20 = GA.gov_run(b8_path, "C2", rec_dir_ci, NOW_EPOCH + 20 * 86400, [], "C0_C2")
r_ci_40 = GA.gov_run(b8_path, "C2", rec_dir_ci, NOW_EPOCH + 40 * 86400, [], "C0_C2")
r_ci_rev_c0only = GA.gov_run(b8_path, "C2", rec_dir_ci, NOW_EPOCH + 20 * 86400, [B8_D], "C0_only")
r_ci_rev_c0c2 = GA.gov_run(b8_path, "C2", rec_dir_ci, NOW_EPOCH + 20 * 86400, [B8_D], "C0_C2")
r_ci_rev_c3_c0only = GA.gov_run(b8_path, "C3", rec_dir_ci, NOW_EPOCH + 20 * 86400, [B8_D], "C0_only")
sc("CI1_20d", "image record, C2 at +20d", "ALLOWED", r_ci_20, r_ci_20["result"] == "ALLOWED")
sc("CI1_40d", "image record, C2 at +40d", "ADMISSION_RECORD_EXPIRED", r_ci_40,
   r_ci_40["result"] == "ADMISSION_RECORD_EXPIRED")
sc("CI1_rev_c0only", "B8 in negatives, scope C0_only, C2", "BINARY_REVOKED_SELF", r_ci_rev_c0only,
   r_ci_rev_c0only["result"] == "BINARY_REVOKED_SELF")
sc("CI1_rev_c0c2", "B8 in negatives, scope C0_C2, C2", "ALLOWED", r_ci_rev_c0c2,
   r_ci_rev_c0c2["result"] == "ALLOWED")
sc("CI1_rev_c3_c0only", "B8 in negatives, scope C0_only, C3", "BINARY_REVOKED_SELF", r_ci_rev_c3_c0only,
   r_ci_rev_c3_c0only["result"] == "BINARY_REVOKED_SELF")

# --- DA04: ceremonies on unadmitted binary (fresh directory!)
rec_dir_da = os.path.join(S, "da04_records")
os.makedirs(rec_dir_da, exist_ok=True)
for act in ("confirm-root", "confirm-state", "trust-gate-confirm"):
    r_da = GA.gov_run(b8_path, act, rec_dir_da, NOW_EPOCH, [], "C0_C2")
    sc("DA04_unadmitted_%s" % act, "unadmitted B8 %s" % act, "BINARY_NOT_ADMITTED", r_da,
       r_da["result"] == "BINARY_NOT_ADMITTED")
# After admission (same-uid, so not protected)
rec_da = {"binary_digest": B8_D, "target": TARGET, "release_id": "R8", "lineage": LINEAGE,
          "state_fingerprint": FP10, "admitted_at": NOW_EPOCH, "admitter_digest": ADMITTER_DIGEST,
          "valid_until": None, "location_protected": False}
vts_da = os.path.join(rec_dir_da, "vts-" + LINEAGE[:16])
os.makedirs(vts_da, exist_ok=True)
with open(os.path.join(vts_da, "admission-%s.json" % B8_D[:24]), "w") as f:
    json.dump(rec_da, f)
# C3 and ceremonies need protected location - same-uid = not protected -> TCB_WRITABLE
for act in ("confirm-root", "confirm-state", "trust-gate-confirm"):
    r_da2 = GA.gov_run(b8_path, act, rec_dir_da, NOW_EPOCH, [], "C0_C2")
    sc("DA04_admitted_%s" % act, "admitted B8 (same-uid) %s" % act,
       "TCB_WRITABLE_BY_GOVERNED_ACCOUNT", r_da2,
       r_da2["result"] == "TCB_WRITABLE_BY_GOVERNED_ACCOUNT")
# C2 allowed even without protection
r_da_c2 = GA.gov_run(b8_path, "C2", rec_dir_da, NOW_EPOCH, [], "C0_C2")
sc("DA04_admitted_C2", "admitted B8 C2 (no protection needed)", "ALLOWED", r_da_c2,
   r_da_c2["result"] == "ALLOWED")

# --- CH1: channel disagreement
r_ch1 = run("CH1", B8_BYTES, [FP10, FP5], FULL)
sc("CH1_disagree", "ch1=fp(t10), ch2=fp(t5)", "CHANNEL_DISAGREEMENT", r_ch1,
   r_ch1["result"] == "CHANNEL_DISAGREEMENT")

# --- CH2: attacker lineage
evil_root = envelope("root+json", {"version": 1, "previous_digest": None,
    "keys": pub_map(["r1","r2","r3","ts1","p1","p2","p3","v1","f1","g1","g2","g3"]),
    "grants": copy.deepcopy(G1B), "revoked_keys": []}, ["r1","r2","r3"])
r_ch2 = run("CH2", B8x_BYTES, [FP10, FP10], [evil_root, TPS1, T1])
sc("CH2", "attacker lineage, genuine fp(t10)", "refused", r_ch2, r_ch2["result"] != "ACCEPTED")

# --- ADM1: admitter substitution
def operator_compare_admitter(measured, tps_admitter_list, channel_digest):
    if measured not in tps_admitter_list or measured != channel_digest:
        return "ADMITTER_DIGEST_MISMATCH"
    return "OK"
adm_ok = operator_compare_admitter(ADMITTER_DIGEST, [ADMITTER_DIGEST], ADMITTER_DIGEST)
adm_bad = operator_compare_admitter("sha256:fake-admitter", [ADMITTER_DIGEST], ADMITTER_DIGEST)
sc("ADM1_ok", "genuine admitter", "OK", adm_ok, adm_ok == "OK")
sc("ADM1_bad", "substituted admitter", "ADMITTER_DIGEST_MISMATCH", adm_bad,
   adm_bad == "ADMITTER_DIGEST_MISMATCH")

# --- INS1: measure-then-swap
swap_path = os.path.join(S, "ins1", "target")
os.makedirs(os.path.dirname(swap_path), exist_ok=True)
with open(swap_path, "wb") as f:
    f.write(B8_BYTES)
measured_d = sha256d(open(swap_path, "rb").read())
with open(swap_path, "wb") as f:
    f.write(B8_DIFF)
inst_buf = os.path.join(S, "ins1", "installed_buffer")
r_ins1_buf = GA.install_from_buffer(B8_BYTES, inst_buf, B8_D, source_path=swap_path)
import shutil
inst_ctrl = os.path.join(S, "ins1", "installed_control")
shutil.copyfile(swap_path, inst_ctrl)
ctrl_d = sha256d(open(inst_ctrl, "rb").read())
sc("INS1_buffer", "install from measured buffer after disk swap", "digest matches measured",
   r_ins1_buf, r_ins1_buf["reread_equal"])
sc("INS1_control", "re-read path installs swapped bytes", "digest differs",
   {"result": ctrl_d != B8_D}, ctrl_d != B8_D,
   extras={"swapped_digest": ctrl_d, "original_digest": B8_D})

# --- INS2: same-uid location
inst_same = os.path.join(S, "ins2", "bin", "gov")
r_ins2 = GA.install_from_buffer(B8_BYTES, inst_same, B8_D)
sc("INS2_location", "same-uid install", "location_protected=false", r_ins2,
   not r_ins2["location_protected"])
# Gov_run C3 on same-uid location -> TCB_WRITABLE
rec_dir_ins2 = os.path.join(S, "ins2_records")
rec_ins2 = {"binary_digest": B8_D, "target": TARGET, "release_id": "R8", "lineage": LINEAGE,
            "state_fingerprint": FP10, "admitted_at": NOW_EPOCH, "admitter_digest": ADMITTER_DIGEST,
            "valid_until": None, "location_protected": False}
vts_ins2 = os.path.join(rec_dir_ins2, "vts-" + LINEAGE[:16])
os.makedirs(vts_ins2, exist_ok=True)
with open(os.path.join(vts_ins2, "admission-%s.json" % B8_D[:24]), "w") as f:
    json.dump(rec_ins2, f)
r_ins2_c3 = GA.gov_run(inst_same, "C3", rec_dir_ins2, NOW_EPOCH, [], "C0_C2")
r_ins2_c2 = GA.gov_run(inst_same, "C2", rec_dir_ins2, NOW_EPOCH, [], "C0_C2")
sc("INS2_C3", "C3 on same-uid location", "TCB_WRITABLE_BY_GOVERNED_ACCOUNT", r_ins2_c3,
   r_ins2_c3["result"] == "TCB_WRITABLE_BY_GOVERNED_ACCOUNT")
sc("INS2_C2", "C2 on same-uid location", "ALLOWED", r_ins2_c2, r_ins2_c2["result"] == "ALLOWED")
# Test protection predicate on /usr/bin/env (owned by root)
prot_usr, _ = GA.tcb_location_protected("/usr/bin/env")
sc("INS2_protected_example", "/usr/bin/env protection", "protected=true", {"result": prot_usr}, prot_usr)

# --- VTS1: pre-existing VTS moved aside
vts_dir_pre = os.path.join(S, "vts1_records")
vts_pre = os.path.join(vts_dir_pre, "vts-" + LINEAGE[:16])
os.makedirs(vts_pre, exist_ok=True)
with open(os.path.join(vts_pre, "forged_anchor.json"), "w") as f:
    json.dump({"forged": True}, f)
rec_vts1 = {"binary_digest": B8_D, "target": TARGET, "release_id": "R8", "lineage": LINEAGE,
            "state_fingerprint": FP10, "admitted_at": NOW_EPOCH, "admitter_digest": ADMITTER_DIGEST,
            "valid_until": None, "location_protected": False}
rp_vts1, new_vts, moved = GA.write_admission_record(rec_vts1, vts_dir_pre, LINEAGE)
sc("VTS1", "pre-existing VTS moved aside", "moved and forged anchor not in new store",
   {"result": moved is not None and not os.path.exists(os.path.join(new_vts, "forged_anchor.json"))},
   moved is not None and not os.path.exists(os.path.join(new_vts, "forged_anchor.json")),
   extras={"moved_to": moved})

# --- K1: one stolen key reproduction conflict
conflict_rep = repro("R8", SRC8, INP8, TARGET, B8x_D, TBM8_D, "p1", env_d="forged")
r_k1 = run("K1", B8_BYTES, [FP10, FP10], FULL + [conflict_rep])
sc("K1", "one stolen key reproduces B8x for R8 (conflict)", "REPRODUCTION_CONFLICT", r_k1,
   r_k1["result"] == "REPRODUCTION_CONFLICT")
r_k1x = run("K1x", B8x_BYTES, [FP10, FP10], FULL + [conflict_rep])
sc("K1_B8x", "B8x with one reproduction", "refused", r_k1x, r_k1x["result"] != "ACCEPTED")

# --- K2: two stolen keys + stolen trust-state key
t11x = envelope("trust-state+json", {"sequence": 11, "issued_at": "2026-09-14T00:00:00Z",
    "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                   "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
    "prior_states": PRIOR10 + [{"sequence": 10, "digest": T10["digest"]}],
    "registrations": [REG7["digest"], REG8["digest"]],
    "published_binaries": sorted([B7_D, B7x_D, B8_D, B8x_D]), "revocations": REVS9}, ["ts1"])
FP11x = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 11, t11x["digest"])
forged_rp8x = [repro("R8", SRC8, INP8, TARGET, B8x_D, sha256d(canon(TBM_B8x)), k, env_d="forged") for k in ("p1","p4")]
stmts_k2 = [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, t11x, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + forged_rp8x
# K2a: operator types genuine fp(t10)
r_k2a = run("K2a", B8x_BYTES, [FP10, FP10], stmts_k2)
sc("K2a", "stolen keys+ts, genuine fp(t10), honest reps withheld", "refused", r_k2a,
   r_k2a["result"] != "ACCEPTED")
# K2b: both channels compromised, type fp(t11x)
r_k2b = run("K2b", B8x_BYTES, [FP11x, FP11x], stmts_k2)
sc("K2b", "both channels compromised, fp(t11x)", "depends on minimum set", r_k2b,
   True, extras={"minimum_set": "2 reproducer keys + trust-state key + both channels + transport",
                 "accepted": r_k2b["result"] == "ACCEPTED"})
# K2c: one channel compromised
r_k2c = run("K2c", B8x_BYTES, [FP10, FP11x], stmts_k2)
sc("K2c", "one channel compromised", "CHANNEL_DISAGREEMENT", r_k2c,
   r_k2c["result"] == "CHANNEL_DISAGREEMENT")

# ========== CONFORMANCE VECTORS ==========
vectors = {}

def vec(vid, binary, fps, stmts_list, expected_code, target=TARGET, flags=None, evaluator=ADMITTER_DIGEST):
    stmts = to_stmts(stmts_list)
    r = GA.accept(binary, fps, stmts, target, evaluator, flags=flags, verifier=V, workdir=S)
    ok = r["result"] == expected_code if expected_code != "refuse" else r["result"] != "ACCEPTED"
    vectors[vid] = {"expected": expected_code, "observed": r["result"], "holds": ok}
    return r

vec("CV01_genuine", B8_BYTES, [FP10, FP10], FULL, "ACCEPTED")

# Root v1 below compiled minimum threshold (signed by 1 key, needs 2)
root1_weak = envelope("root+json", {"version": 1, "previous_digest": None, "keys": pub_map(ALL_V1),
                                     "grants": G1B, "revoked_keys": []}, ["r1"])
vec("CV02_root_below_threshold", B8_BYTES, [FP10, FP10],
    [root1_weak, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA8, FINAL8, REG8] + RP8, "ROOT_CHAIN_INVALID")

# Broken previous_digest link at v2 (chain stops at v1, no v2 state selectable)
root_badlink = envelope("root+json", {"version": 2, "previous_digest": "sha256:" + "0"*64,
    "keys": pub_map(ALL_V2), "grants": G2B, "revoked_keys": [kid("p2"),kid("p3")]}, ["r1","r2"])
vec("CV03_broken_link", B8_BYTES, [FP10, FP10],
    [ROOT1, root_badlink, TPS1, T1, T10, VA8, FINAL8, REG8] + RP8, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")

# Bad TSS signature
tss_badsig = envelope("trust-state+json", T10["payload"], ["ts1"], bad_sig=True)
fp_bad = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, tss_badsig["digest"])
vec("CV04_bad_tss_sig", B8_BYTES, [fp_bad, fp_bad],
    [ROOT1, ROOT2, TPS1, tss_badsig, T1, T9, VA8, FINAL8, REG8] + RP8,
    "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")

# Duplicate key in signatures (dedup means only counted once, but still passes)
dup_env = copy.deepcopy(RP8[0]["env"])
dup_env["signatures"].append(dup_env["signatures"][0])
dup_repro = {"purpose": "reproducer", "payload": RP8[0]["payload"], "digest": RP8[0]["digest"], "env": dup_env}
vec("CV05_dup_sig_key", B8_BYTES, [FP10, FP10],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + [dup_repro, RP8[1]], "ACCEPTED")

# Reproduction with two reproducer signatures (counts for none per exactly-one rule)
rep_two = repro("R8", SRC8, INP8, TARGET, B8_D, TBM8_D, None, signers=["p1","p4"])
vec("CV06_two_rep_sigs", B8_BYTES, [FP10, FP10],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + [rep_two], "refuse")

# Reproduction naming wrong source
rep_wrong_src = repro("R8", SRC7, INP8, TARGET, B8_D, TBM8_D, "p4")
vec("CV07_rep_wrong_source", B8_BYTES, [FP10, FP10],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + [RP8[0], rep_wrong_src], "refuse")

# KS-7 violation in v2 (chain stops at v1, state referencing v2 not selectable)
vec("CV08_ks7_chain_stops", B8_BYTES, [FP10, FP10],
    [ROOT1, root_v2_ks7, TPS1, T1, T10, VA8, FINAL8, REG8] + RP8, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")

# Verification records below minimum (min=2, only 1 attestation)
t10_min2 = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1_MIN2["digest"]}},
     "prior_states": PRIOR10, "registrations": [REG7["digest"], REG8["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]), "revocations": REVS9}, ["ts1"])
fp_min2 = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1_MIN2["digest"], 10, t10_min2["digest"])
vec("CV09_ver_below_min", B8_BYTES, [fp_min2, fp_min2],
    [ROOT1, ROOT2, TPS1_MIN2, T1, T5, T6, T7, T9, t10_min2, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8,
    "VERIFICATION_RECORDS_BELOW_MINIMUM")

# REJECTED attestation held
vec("CV10_rejected", B8_BYTES, [FP10, FP10], FULL + [VA8_REJ], "ARTIFACT_SOURCE_REJECTED")

# Registration not referenced by TSS
t10_noreg = envelope("trust-state+json",
    {"sequence": 10, "issued_at": "2026-09-13T00:00:00Z",
     "references": {"root": {"version": 2, "digest": ROOT2["digest"]},
                    "trust_policy": {"version": 1, "digest": TPS1["digest"]}},
     "prior_states": PRIOR10, "registrations": [REG7["digest"]],
     "published_binaries": sorted([B7_D, B7x_D, B8_D]), "revocations": REVS9}, ["ts1"])
fp_noreg = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, t10_noreg["digest"])
vec("CV11_reg_not_in_tss", B8_BYTES, [fp_noreg, fp_noreg],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, t10_noreg, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8,
    "RELEASE_UNREGISTERED")

# Registration below threshold (signed by one key)
reg8_weak = envelope("release-registration+json", REG8["payload"], ["g1"])
vec("CV12_reg_below_threshold", B8_BYTES, [FP10, FP10],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, reg8_weak] + RP7 + RP7x + RP8,
    "RELEASE_UNREGISTERED")

# Release-final missing
stmts_no_final = [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, REG7, REG8] + RP7 + RP7x + RP8
vec("CV13_final_missing", B8_BYTES, [FP10, FP10], stmts_no_final, "RELEASE_FINAL_UNVERIFIED")

# Target not registered
reg8_notgt = envelope("release-registration+json", dict(REG8["payload"], targets=["aarch64-darwin"]), ["g1","g2"])
t10_notgt = envelope("trust-state+json",
    dict(T10["payload"], registrations=[REG7["digest"], reg8_notgt["digest"]]), ["ts1"])
fp_notgt = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, t10_notgt["digest"])
vec("CV14_target_not_registered", B8_BYTES, [fp_notgt, fp_notgt],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, t10_notgt, VA7, VA8, FINAL7, FINAL8, REG7, reg8_notgt] + RP7 + RP7x + RP8,
    "TARGET_NOT_REGISTERED")

# FTC violation in v2 (chain stops at v1, state referencing v2 not selectable)
vec("CV15_ftc_chain_stops", B8_BYTES, [FP10, FP10],
    [ROOT1, root_v2_ftc, TPS1, T1, T10, VA8, FINAL8, REG8] + RP8, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")

# Registration equivocation (two registrations for same release)
reg8_alt = envelope("release-registration+json", dict(REG8["payload"], sequence=9), ["g1","g2"])
t10_equi = envelope("trust-state+json",
    dict(T10["payload"], registrations=[REG7["digest"], REG8["digest"], reg8_alt["digest"]]), ["ts1"])
fp_equi = fp(LINEAGE, 2, ROOT2["digest"], 1, TPS1["digest"], 10, t10_equi["digest"])
vec("CV16_equivocation", B8_BYTES, [fp_equi, fp_equi],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, t10_equi, VA7, VA8, FINAL7, FINAL8, REG7, REG8, reg8_alt] + RP7 + RP7x + RP8,
    "REGISTRATION_EQUIVOCATION")

# Binary not in published_binaries (for skip_published detection)
vec("CV17_not_published", B8_BYTES, [FP10_nopub, FP10_nopub],
    [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10_nopub, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8,
    "BINARY_NOT_PUBLISHED")

# ========== MUTANT ANALYSIS ==========
MUTANTS = ["any_state", "skip_channel_agreement", "skip_channel_quorum", "skip_revocation",
           "quorum_one", "skip_conflict", "skip_published", "skip_source_equality",
           "ignore_signer_revocation", "multi_signer_counts", "count_statements_not_keys",
           "skip_registration_reference", "skip_registration_equivocation", "skip_verification_records",
           "skip_rejected", "skip_final_restrictor", "skip_ftc", "skip_ks7", "skip_root_link",
           "skip_tbm", "allow_self_evaluation", "install_reread_path", "skip_genuine_binary_rule",
           "skip_record_protection", "skip_record_expiry", "skip_self_revocation", "skip_fresh_vts"]

# Bundle for mutant tests: includes new world objects
STMTS_BADLINK = [ROOT1, root_v2_badlink, TPS1, T1, T5, T6, T7, T9, tss_badlink, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8
STMTS_KS7 = [ROOT1, root_v2_ks7, TPS1, T1, T5, T6, T7, T9, tss_ks7, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8
STMTS_FTC = [ROOT1, root_v2_ftc, TPS1, T1, T5, T6, T7, T9, tss_ftc, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8
STMTS_NOPUB = [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10_nopub, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8
STMTS_BADTBM = [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8_badtbm

ACCEPT_VECTORS = {
    "MV01_genuine": (B8_BYTES, [FP10,FP10], FULL, "ACCEPTED"),
    "MV02_revoked": (B7_BYTES, [FP10,FP10], FULL, "BINARY_REVOKED"),
    "MV03_unregistered": (BPLANTED_BYTES, [FP10,FP10], FULL, "refuse"),
    "MV04_quorum": (B8_BYTES, [FP10,FP10],
        [ROOT1,ROOT2,TPS1,T1,T5,T6,T7,T9,T10,VA7,VA8,FINAL7,FINAL8,REG7,REG8]+RP7+RP7x+[RP8[0]], "refuse"),
    "MV05_conflict": (B8_BYTES, [FP10,FP10], FULL+[conflict_rep], "REPRODUCTION_CONFLICT"),
    "MV06_unpublished": (B8_DIFF, [FP10,FP10], FULL, "refuse"),
    "MV07_wrong_src": (B8_BYTES, [FP10,FP10],
        [ROOT1,ROOT2,TPS1,T1,T5,T6,T7,T9,T10,VA7,VA8,FINAL7,FINAL8,REG7,REG8]+RP7+RP7x+[RP8[0],rep_wrong_src], "refuse"),
    "MV08_two_sigs": (B8_BYTES, [FP10,FP10],
        [ROOT1,ROOT2,TPS1,T1,T5,T6,T7,T9,T10,VA7,VA8,FINAL7,FINAL8,REG7,REG8]+RP7+RP7x+[rep_two], "refuse"),
    "MV09_state_mismatch": (B8_BYTES, [FP5,FP5], FULL, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH"),
    "MV10_channel_disagree": (B8_BYTES, [FP10,FP5], FULL, "CHANNEL_DISAGREEMENT"),
    "MV11_channel_quorum": (B8_BYTES, [FP10], FULL, "CHANNEL_QUORUM_NOT_MET"),
    "MV12_self_eval": (B8_BYTES, [FP10,FP10], FULL, "SELF_EVALUATION_REFUSED"),  # evaluator=B8_D
    "MV13_root_weak": (B8_BYTES, [FP10,FP10],
        [root1_weak,ROOT2,TPS1,T1]+RP8, "ROOT_CHAIN_INVALID"),
    "MV14_bad_link": (B8_BYTES, [fp_badlink,fp_badlink], STMTS_BADLINK, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH"),
    "MV15_ks7": (B8_BYTES, [fp_ks7,fp_ks7], STMTS_KS7, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH"),
    "MV16_ftc": (B8_BYTES, [fp_ftc,fp_ftc], STMTS_FTC, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH"),
    "MV17_rejected": (B8_BYTES, [FP10,FP10], FULL+[VA8_REJ], "ARTIFACT_SOURCE_REJECTED"),
    "MV18_ver_min": (B8_BYTES, [fp_min2,fp_min2],
        [ROOT1,ROOT2,TPS1_MIN2,T1,T5,T6,T7,T9,t10_min2,VA7,VA8,FINAL7,FINAL8,REG7,REG8]+RP7+RP7x+RP8, "VERIFICATION_RECORDS_BELOW_MINIMUM"),
    "MV19_no_final": (B8_BYTES, [FP10,FP10], stmts_no_final, "RELEASE_FINAL_UNVERIFIED"),
    "MV20_no_reg_ref": (B8_BYTES, [fp_noreg,fp_noreg],
        [ROOT1,ROOT2,TPS1,T1,T5,T6,T7,T9,t10_noreg,VA7,VA8,FINAL7,FINAL8,REG7,REG8]+RP7+RP7x+RP8, "RELEASE_UNREGISTERED"),
    "MV21_equivocation": (B8_BYTES, [fp_equi,fp_equi],
        [ROOT1,ROOT2,TPS1,T1,T5,T6,T7,T9,t10_equi,VA7,VA8,FINAL7,FINAL8,REG7,REG8,reg8_alt]+RP7+RP7x+RP8, "REGISTRATION_EQUIVOCATION"),
    "MV22_not_published": (B8_BYTES, [FP10_nopub,FP10_nopub], STMTS_NOPUB, "BINARY_NOT_PUBLISHED"),
    "MV23_bad_tbm": (B8_BYTES, [FP10,FP10], STMTS_BADTBM, "REPRODUCTION_QUORUM_NOT_MET"),
}

# Run unmutated
base_results = {}
for vid, (b, fps, st, exp) in ACCEPT_VECTORS.items():
    ev = B8_D if vid == "MV12_self_eval" else ADMITTER_DIGEST
    stmts = to_stmts(st)
    r = GA.accept(b, fps, stmts, TARGET, ev, verifier=V, workdir=S)
    base_results[vid] = r["result"]

# Run mutants
mutant_table = {}
for m in MUTANTS:
    changed = []
    for vid, (b, fps, st, exp) in ACCEPT_VECTORS.items():
        ev = B8_D if vid == "MV12_self_eval" else ADMITTER_DIGEST
        stmts = to_stmts(st)
        r = GA.accept(b, fps, stmts, TARGET, ev, flags={m: True}, verifier=V, workdir=S)
        if r["result"] != base_results[vid]:
            changed.append({"vector": vid, "base": base_results[vid], "mutant": r["result"]})
    # install discipline under this mutant (INS1 shape; added by AR-0011 so the install mutant is evaluated)
    _dest = os.path.join(S, "ins1", "mut-" + m)
    _ri = GA.install_from_buffer(B8_BYTES, _dest, B8_D, flags={m: True}, source_path=swap_path)
    if _ri["reread_equal"] != r_ins1_buf["reread_equal"]:
        changed.append({"vector": "INS1_buffer", "base": r_ins1_buf["reread_equal"], "mutant": _ri["reread_equal"]})
    # gov_run mutants
    for gov_m in ("skip_genuine_binary_rule", "skip_record_protection", "skip_record_expiry",
                  "skip_self_revocation"):
        if m == gov_m:
            flags_gov = {m: True}
            # CI1_40d: ADMISSION_RECORD_EXPIRED without mutant
            r_g = GA.gov_run(b8_path, "C2", rec_dir_ci, NOW_EPOCH + 40 * 86400, [], "C0_C2", flags=flags_gov)
            if r_g["result"] != "ADMISSION_RECORD_EXPIRED":
                changed.append({"vector": "CI1_40d_gov", "base": "ADMISSION_RECORD_EXPIRED", "mutant": r_g["result"]})
            # CI self-revocation
            r_g4 = GA.gov_run(b8_path, "C2", rec_dir_ci, NOW_EPOCH + 20*86400, [B8_D], "C0_only", flags=flags_gov)
            if r_g4["result"] != "BINARY_REVOKED_SELF":
                changed.append({"vector": "CI1_rev_gov", "base": "BINARY_REVOKED_SELF", "mutant": r_g4["result"]})
            # INS2 C3 same-uid protection
            r_g3 = GA.gov_run(inst_same, "C3", rec_dir_ins2, NOW_EPOCH, [], "C0_C2", flags=flags_gov)
            if r_g3["result"] != "TCB_WRITABLE_BY_GOVERNED_ACCOUNT":
                changed.append({"vector": "INS2_C3_gov", "base": "TCB_WRITABLE_BY_GOVERNED_ACCOUNT", "mutant": r_g3["result"]})
    # install_reread_path: only distinguishable in atomic swap scenario; note in analysis
    # skip_fresh_vts
    if m == "skip_fresh_vts":
        vts_test = os.path.join(S, "mut_vts")
        vts_sub = os.path.join(vts_test, "vts-" + LINEAGE[:16])
        os.makedirs(vts_sub, exist_ok=True)
        with open(os.path.join(vts_sub, "evil.json"), "w") as f:
            json.dump({"evil": True}, f)
        _, _, moved_m = GA.write_admission_record(rec_vts1, vts_test, LINEAGE, flags={m: True})
        if moved_m is None:
            changed.append({"vector": "VTS1_mut", "base": "moved", "mutant": "not_moved"})
    mutant_table[m] = {"detected": bool(changed), "distinguishing": changed[:5], "count": len(changed)}

# ========== VARIANT A (registration on root keys) ==========
ROOT1A_lineage = ROOT1A["digest"]
TPS1A = envelope("trust-policy+json", TPS1["payload"], ["r1","r2"])
T1A = envelope("trust-state+json",
    dict(T1["payload"], references={"root": {"version": 1, "digest": ROOT1A_lineage},
                                    "trust_policy": {"version": 1, "digest": TPS1A["digest"]}}), ["ts1"])
T9A_payload = copy.deepcopy(T9["payload"])
T9A_payload["references"] = {"root": {"version": 2, "digest": ROOT2A["digest"]},
                              "trust_policy": {"version": 1, "digest": TPS1A["digest"]}}
T9A_payload["registrations"] = [REG7A["digest"], REG8A["digest"]]
T9A_payload["published_binaries"] = sorted([B7_D, B7x_D])
T9A = envelope("trust-state+json", T9A_payload, ["ts1"])
TBM8A = make_tbm(2, 1, 9, T9A["digest"], SRC8, INP8, lineage=ROOT1A_lineage)
B8A_BYTES, B8A_D = make_binary("B8A", TBM8A)
RP8A = [repro("R8", SRC8, INP8, TARGET, B8A_D, sha256d(canon(TBM8A)), k) for k in ("p1","p4")]
T10A_payload = copy.deepcopy(T10["payload"])
T10A_payload["references"] = {"root": {"version": 2, "digest": ROOT2A["digest"]},
                               "trust_policy": {"version": 1, "digest": TPS1A["digest"]}}
T10A_payload["registrations"] = [REG7A["digest"], REG8A["digest"]]
T10A_payload["published_binaries"] = sorted([B7_D, B7x_D, B8A_D])
T10A = envelope("trust-state+json", T10A_payload, ["ts1"])
FP10A = fp(ROOT1A_lineage, 2, ROOT2A["digest"], 1, TPS1A["digest"], 10, T10A["digest"])
FULL_A = [ROOT1A, ROOT2A, TPS1A, T1A, T9A, T10A, VA7, VA8, FINAL7, FINAL8, REG7A, REG8A] + RP8A
r_varA = run("varA", B8A_BYTES, [FP10A, FP10A], FULL_A)
variant_check = {"variant_A_result": r_varA["result"], "matches_variant_B": r_varA["result"] == r00["result"]}

# ========== OUTPUT ==========
all_holds = all(s["holds"] for s in scenarios.values())
vec_holds = sum(1 for v in vectors.values() if v["holds"])
mut_detected = sum(1 for m in mutant_table.values() if m["detected"])
undetected = [m for m, v in mutant_table.items() if not v["detected"]]

output = {
    "scenarios": scenarios,
    "conformance_vectors": vectors,
    "mutant_table": mutant_table,
    "registration_variant_check": variant_check,
    "summary": {
        "scenarios_total": len(scenarios),
        "scenarios_hold": sum(1 for s in scenarios.values() if s["holds"]),
        "scenarios_failing": [k for k, s in scenarios.items() if not s["holds"]],
        "vectors_total": len(vectors),
        "vectors_hold": vec_holds,
        "vectors_failing": [k for k, v in vectors.items() if not v["holds"]],
        "mutants_total": len(MUTANTS),
        "mutants_detected": mut_detected,
        "mutants_undetected": undetected,
        "openssl_calls": V.calls,
    },
    "undetected_mutant_analysis": {},
}

for m in undetected:
    if m == "ignore_signer_revocation":
        output["undetected_mutant_analysis"][m] = (
            "Equivalent while KS-7 holds: a revoked key is never granted, "
            "so skipping the global revocation list makes no difference. "
            "Combined with skip_ks7 (allowing revoked-granted keys) would reveal it.")
    elif m == "install_reread_path":
        output["undetected_mutant_analysis"][m] = (
            "Only distinguishable when a TOCTOU swap occurs between "
            "install_from_buffer's write and its re-read. In standard tests the "
            "buffer-written file is re-read immediately and matches. "
            "The INS1 scenario demonstrates the risk the buffer discipline prevents.")
    elif m == "count_statements_not_keys":
        output["undetected_mutant_analysis"][m] = (
            "Equivalent when each reproduction statement has exactly one "
            "signing key (enforced by the exactly-one-signature filter at step 6). "
            "Two statements by the same key map to the same key in counting by keys, "
            "so statement counting and key counting coincide.")
    else:
        output["undetected_mutant_analysis"][m] = "Requires further investigation."

# Replace paths
txt = json.dumps(output, indent=1, sort_keys=True, default=str)
txt = txt.replace(S, "<scratch>")
txt = txt.replace(BASE_SCRATCH, "<scratch-base>")
txt = txt.replace(HERE, "<evidence>")
if GOV:
    txt = txt.replace(os.path.dirname(GOV), "<legacy-bin>")
txt = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt)
txt = re.sub(r"/tmp/fa5-base/[^\"\s]*", "<scratch>", txt)

json_path = os.path.join(HERE, "FA5-first-admission.json")
with open(json_path, "w") as f:
    f.write(txt)
print(txt)
