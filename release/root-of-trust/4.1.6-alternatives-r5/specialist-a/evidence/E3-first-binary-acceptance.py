#!/usr/bin/env python3
"""E3 (AR-0009, specialist A) — BC4-2: first TCB acceptance with real Ed25519 signatures, executed.

A toy lineage is built with deterministic Ed25519 keys (Python `cryptography` for SIGNING only). The proposal's
independent executor `gov_accept_reference.py` (Python stdlib + platform OpenSSL for VERIFYING) judges candidate binaries
with exactly three trust inputs: a typed state fingerprint, the binary bytes it measures, and statements from any source.
Revision 4's documented first-binary paths are implemented on the same world as controls:
  r4 path (b): independent tooling checking A2-A6 only (06 §2 step 6 (b); 25 §5), root metadata whose lineage id equals
               the channel's;
  r4 path (c): build from source and compare `gov version --trust` (lineage, TBM digest) with the channel and the build
               attestation (06 §2 step 6 (c)).
Candidates are shell scripts that create a marker file if executed, so "the candidate is never executed" is observable.

Scenarios: RV4-B-A03 (FB1 revoked binary; FB2 remediated compromise with root v1 metadata), RV4-B-A04 (moved-tag
planted binary; Phase 4 self-verification), RV4-D-A04 (ceremony ordering), RV3-D-A15 analogue, plus new attacks N-FB*.
Mutants: each `flags` switch of the reference executor is run against every vector; a mutant is detected when at least one
vector's result changes.

Environment: GOV (legacy 4.1.5, for the Phase 4 register check), GOV_REVIEW_SCRATCH (scratch). Output: JSON on stdout.
"""
import base64, copy, hashlib, importlib.util, json, os, re, shutil, stat, subprocess, sys, tempfile

sys.dont_write_bytecode = True
from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gov_accept_reference", os.path.join(HERE, "gov_accept_reference.py"))
GA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GA)
SCR = tempfile.mkdtemp(prefix="e3-", dir=os.environ["GOV_REVIEW_SCRATCH"])
GOV = os.environ.get("GOV")
TARGET = "x86_64-linux"


# ------------------------------------------------------------------------------------------------ owner-side primitives
# (independent of the executor's code: the owner's canonical JSON, PAE and fingerprint are re-implemented here)
def ocanon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def odigest(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def opae(t, body):
    tb = t.encode()
    return b"DSSEv1 " + str(len(tb)).encode() + b" " + tb + b" " + str(len(body)).encode() + b" " + body


def ofingerprint(lineage, rv, rd, pv, pd, seq, sd):
    e = {"lineage": lineage, "root_version": rv, "root_digest": rd, "policy_version": pv, "policy_digest": pd, "state_sequence": seq, "state_digest": sd}
    return "gov-state:" + lineage[7:15] + ":" + str(seq) + ":" + hashlib.sha256(ocanon(e)).hexdigest()[:32]


KEYS = {}


def key(label):
    if label not in KEYS:
        sk = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"ar-0009-e3:" + label.encode()).digest())
        raw = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        KEYS[label] = (sk, raw, "ed25519:" + hashlib.sha256(raw).hexdigest())
    return KEYS[label]


kid = lambda label: key(label)[2]
T = {"root": "application/vnd.sam.root+json", "trust-policy": "application/vnd.sam.trust-policy+json", "trust-state": "application/vnd.sam.trust-state+json",
     "reproduction": "application/vnd.sam.reproduction+json",
     # revision-4-shaped statements for the controls (unknown to the proposal executor, which ignores them)
     "r4-candidate": "application/vnd.r4.release-candidate+json", "r4-final": "application/vnd.r4.release-final+json",
     "r4-verification": "application/vnd.r4.verification-attestation+json", "r4-build": "application/vnd.r4.build-attestation+json",
     "r4-artifact": "application/vnd.r4.artifact-final+json"}


def envelope(kind, payload, signers, bad_sig=False):
    body = ocanon(payload)
    sigs = []
    for s in signers:
        sk, raw, k = key(s)
        sig = sk.sign(opae(T[kind], body))
        if bad_sig:
            sig = bytes([sig[0] ^ 1]) + sig[1:]
        sigs.append({"keyid": k, "sig": base64.b64encode(sig).decode()})
    return {"kind": kind, "payload": payload, "digest": odigest(body),
            "env": {"payloadType": T[kind], "payload": base64.b64encode(body).decode(), "signatures": sigs}}


# ------------------------------------------------------------------------------------------------ the world
ALL1 = ["r1", "r2", "r3", "ts1", "rep1", "rep2", "rep3", "rf1", "rc1", "va1", "ba1", "ra1", "ra2"]
ALL2 = ALL1 + ["rep4", "rep5", "ra3", "ra4", "ba2"]
pub = lambda labels: {kid(l): base64.b64encode(key(l)[1]).decode() for l in labels}
grants1 = {"root": {"keys": [kid(x) for x in ("r1", "r2", "r3")], "threshold": 2}, "trust-policy": {"keys": [kid(x) for x in ("r1", "r2", "r3")], "threshold": 2},
           "trust-state": {"keys": [kid("ts1")], "threshold": 1}, "reproducer": {"keys": [kid(x) for x in ("rep1", "rep2", "rep3")], "threshold": 2},
           "release-final": {"keys": [kid("rf1")], "threshold": 1}, "release-candidate": {"keys": [kid("rc1")], "threshold": 1},
           "verification-attestation": {"keys": [kid("va1")], "threshold": 1}, "build-attestation": {"keys": [kid("ba1")], "threshold": 1},
           "release-artifact": {"keys": [kid("ra1"), kid("ra2")], "threshold": 2}}
ROOT1 = envelope("root", {"kind": "root", "version": 1, "keys": pub(ALL1), "grants": grants1, "revoked_keys": [], "previous_digest": None}, ["r1", "r2", "r3"])
LINEAGE = ROOT1["digest"]
grants2 = copy.deepcopy(grants1)
grants2["reproducer"] = {"keys": [kid(x) for x in ("rep1", "rep4", "rep5")], "threshold": 2}
grants2["release-artifact"] = {"keys": [kid("ra3"), kid("ra4")], "threshold": 2}
grants2["build-attestation"] = {"keys": [kid("ba2")], "threshold": 1}
ROOT2 = envelope("root", {"kind": "root", "version": 2, "keys": pub(ALL2), "grants": grants2, "revoked_keys": [kid(x) for x in ("rep2", "rep3", "ra1", "ra2", "ba1")],
                          "previous_digest": LINEAGE}, ["r1", "r2"])


def src(tag):
    return {"release_commit": "c-" + tag, "source_tree_digest": "sha256:" + hashlib.sha256(("tree-" + tag).encode()).hexdigest(),
            "build_inputs_digest": "sha256:" + hashlib.sha256(("inputs-" + tag).encode()).hexdigest()}


S7, S8, S7B = src("4.1.7"), src("4.1.8"), src("4.1.7b")
REL = lambda rid, seq, s: {"release_id": rid, "sequence": seq, "source": s, "targets": [TARGET]}
TPS1 = envelope("trust-policy", {"kind": "trust-policy", "version": 1, "lineage": LINEAGE, "releases": [REL("R7", 7, S7), REL("R7b", 7, S7B)]}, ["r1", "r2"])
TPS2 = envelope("trust-policy", {"kind": "trust-policy", "version": 2, "lineage": LINEAGE, "releases": [REL("R7", 7, S7), REL("R7b", 7, S7B), REL("R8", 8, S8), REL("R8b", 9, S8)]}, ["r1", "r2"])

MARKERS = os.path.join(SCR, "markers")
os.makedirs(MARKERS)
BINDIR = os.path.join(SCR, "binaries")
os.makedirs(BINDIR)


def binary(name, reports):
    body = ("#!/bin/sh\n# " + name + "\n: > \"${E3_MARKERS:-/nonexistent}/" + name + "\"\n"
            "if [ \"$1\" = version ] && [ \"$2\" = --trust ]; then printf '%s\\n' '" + json.dumps(reports) + "'; fi\n")
    p = os.path.join(BINDIR, name)
    open(p, "w").write(body)
    os.chmod(p, 0o755)
    return p, odigest(body.encode())


TBM = lambda s, tag: {"lineage": LINEAGE, "source": s, "tag": tag}
tbm_d = lambda t: odigest(ocanon(t))
TBM7, TBM8 = TBM(S7, "7"), TBM(S8, "8")
B7, B7_D = binary("B7-genuine-revoked", {"lineage": LINEAGE, "tbm_digest": tbm_d(TBM7)})
B7X, B7X_D = binary("B7x-malicious-remediated", {"lineage": LINEAGE, "tbm_digest": tbm_d(TBM7)})
B8, B8_D = binary("B8-genuine-current", {"lineage": LINEAGE, "tbm_digest": tbm_d(TBM8)})
B8X, B8X_D = binary("B8x-malicious", {"lineage": LINEAGE, "tbm_digest": tbm_d(TBM8)})
B8B, B8B_D = binary("B8b-genuine-unpublished", {"lineage": LINEAGE, "tbm_digest": tbm_d(TBM8)})
BPL, BPL_D = binary("Bplanted-moved-tag", {"lineage": LINEAGE, "tbm_digest": tbm_d(TBM8)})


def repro(rid, s, bdig, tbm, signer, env="env-1", signers=None):
    return envelope("reproduction", {"kind": "reproduction", "lineage": LINEAGE, "release_id": rid, "source": s, "target": TARGET, "binary_digest": bdig,
                                     "tbm_digest": tbm_d(tbm), "environment_digest": env}, signers or [signer])


RP7 = [repro("R7", S7, B7_D, TBM7, k) for k in ("rep1", "rep2", "rep3")]
RP7X = [repro("R7b", S7B, B7X_D, TBM7, k) for k in ("rep2", "rep3")]           # forged with stolen keys, later remediated
RP8 = [repro("R8", S8, B8_D, TBM8, k) for k in ("rep1", "rep4", "rep5")]
RP8B = [repro("R8b", S8, B8B_D, TBM8, k) for k in ("rep1", "rep4")]

# revision-4-shaped statements for the controls
C7 = envelope("r4-candidate", {"kind": "r4-candidate", "source": S7, "tree": "K7"}, ["rc1"])
A7 = envelope("r4-verification", {"kind": "r4-verification", "candidate": C7["digest"], "verdict": "ACCEPTED", "source": S7}, ["va1"])
F7 = envelope("r4-final", {"kind": "r4-final", "promoted_from_candidate": C7["digest"], "source": S7, "tree": "K7", "sequence": 7}, ["rf1"])
BA7 = envelope("r4-build", {"kind": "r4-build", "artifact_digest": B7_D, "tbm_digest": tbm_d(TBM7), "source": S7}, ["ba1"])
AR7 = envelope("r4-artifact", {"kind": "r4-artifact", "release": F7["digest"], "artifacts": [{"digest": B7_D, "tbm_digest": tbm_d(TBM7), "target": TARGET}]}, ["ra1", "ra2"])
BA7X = envelope("r4-build", {"kind": "r4-build", "artifact_digest": B7X_D, "tbm_digest": tbm_d(TBM7), "source": S7}, ["ba1"])
AR7X = envelope("r4-artifact", {"kind": "r4-artifact", "release": F7["digest"], "artifacts": [{"digest": B7X_D, "tbm_digest": tbm_d(TBM7), "target": TARGET}]}, ["ra1", "ra2"])
C8 = envelope("r4-candidate", {"kind": "r4-candidate", "source": S8, "tree": "K8"}, ["rc1"])
A8 = envelope("r4-verification", {"kind": "r4-verification", "candidate": C8["digest"], "verdict": "ACCEPTED", "source": S8}, ["va1"])
F8 = envelope("r4-final", {"kind": "r4-final", "promoted_from_candidate": C8["digest"], "source": S8, "tree": "K8", "sequence": 8}, ["rf1"])
BA8 = envelope("r4-build", {"kind": "r4-build", "artifact_digest": B8_D, "tbm_digest": tbm_d(TBM8), "source": S8}, ["ba2"])
AR8 = envelope("r4-artifact", {"kind": "r4-artifact", "release": F8["digest"], "artifacts": [{"digest": B8_D, "tbm_digest": tbm_d(TBM8), "target": TARGET}]}, ["ra3", "ra4"])


def tss(seq, root, tps, prior, revs, published, issued, r4_arts=(), r4_atts=(), signer="ts1", bad_sig=False):
    return envelope("trust-state", {"kind": "trust-state", "sequence": seq, "lineage": LINEAGE, "issued_at": issued,
                                    "references": {"root": {"version": root["payload"]["version"], "digest": root["digest"]},
                                                   "trust_policy": {"version": tps["payload"]["version"], "digest": tps["digest"]}},
                                    "prior_states": prior, "revocations": sorted(revs), "published_binaries": sorted(published),
                                    "artifacts": sorted(r4_arts), "attestations": sorted(r4_atts)}, [signer], bad_sig=bad_sig)


T1 = tss(1, ROOT1, TPS1, [], [], [], "2026-01-01T00:00:00Z")
T5 = tss(5, ROOT1, TPS1, [[1, T1["digest"]]], [], [B7_D], "2026-03-01T00:00:00Z", r4_arts=[AR7["digest"]], r4_atts=[A7["digest"]])
T6 = tss(6, ROOT1, TPS1, [[1, T1["digest"]], [5, T5["digest"]]], [], [B7_D, B7X_D], "2026-04-01T00:00:00Z", r4_arts=[AR7["digest"], AR7X["digest"]], r4_atts=[A7["digest"]])
P9 = [[1, T1["digest"]], [5, T5["digest"]], [6, T6["digest"]]]
REVS = [B7_D, B7X_D] + [r["digest"] for r in RP7X]
T9 = tss(9, ROOT2, TPS2, P9, REVS, [B7_D, B7X_D, B8_D], "2026-08-01T00:00:00Z", r4_arts=[AR7["digest"], AR7X["digest"], AR8["digest"]], r4_atts=[A7["digest"], A8["digest"]])
T10 = tss(10, ROOT2, TPS2, P9 + [[9, T9["digest"]]], REVS, [B7_D, B7X_D, B8_D], "2026-09-13T00:00:00Z", r4_arts=[AR7["digest"], AR7X["digest"], AR8["digest"]], r4_atts=[A7["digest"], A8["digest"]])
FP10 = ofingerprint(LINEAGE, 2, ROOT2["digest"], 2, TPS2["digest"], 10, T10["digest"])
FP5 = ofingerprint(LINEAGE, 1, ROOT1["digest"], 1, TPS1["digest"], 5, T5["digest"])
ROOT_ID_CHANNEL = LINEAGE

FULL = [ROOT1, ROOT2, TPS1, TPS2, T1, T5, T6, T9, T10] + RP7 + RP7X + RP8 + [C7, A7, F7, BA7, AR7, BA7X, AR7X, C8, A8, F8, BA8, AR8]
STRIPPED_FB1 = [ROOT1, TPS1, T1, T5] + RP7 + [C7, A7, F7, BA7, AR7]
STRIPPED_FB2 = [ROOT1, TPS1, T1, T5, T6] + RP7X + [C7, A7, F7, BA7X, AR7X]


def write_dir(name, stmts):
    d = os.path.join(SCR, "stmts", name)
    os.makedirs(d)
    for i, s in enumerate(stmts):
        json.dump(s["env"], open(os.path.join(d, f"{i:03d}-{s['kind']}.json"), "w"), sort_keys=True)
    return d


# ------------------------------------------------------------------------------------------------ revision-4 controls
def r4_path_b(binary_path, stmts, channel_root_id, v):
    """06 §2 step 6 (b): A2-A6 with root metadata whose lineage id equals the channel's. No A7, A8 or A9."""
    data = open(binary_path, "rb").read()
    d = odigest(data)
    loaded = GA.load_statements(write_dir("r4b-" + str(len(os.listdir(os.path.join(SCR, "stmts"))) if os.path.exists(os.path.join(SCR, "stmts")) else "0"), stmts)) if False else None
    by_kind = {}
    for s in stmts:
        by_kind.setdefault(s["kind"], []).append(s)
    roots = sorted(by_kind.get("root", []), key=lambda r: r["payload"]["version"])
    if not roots or roots[0]["digest"] != channel_root_id:
        return "LINEAGE_MISMATCH"
    root = roots[-1]["payload"]  # the newest root metadata the tooling was given

    def ok(s, purpose):
        g = root["grants"].get(purpose)
        body = base64.b64decode(s["env"]["payload"])
        good = set()
        for sig in s["env"]["signatures"]:
            k = sig["keyid"]
            if k in root["keys"] and k not in root.get("revoked_keys", []) and k in g["keys"]:
                if v.verify(base64.b64decode(root["keys"][k]), opae(s["env"]["payloadType"], body), base64.b64decode(sig["sig"])):
                    good.add(k)
        return len(good) >= g["threshold"]
    arts = [a for a in by_kind.get("r4-artifact", []) if any(x["digest"] == d for x in a["payload"]["artifacts"]) and ok(a, "release-artifact")]
    if not arts:
        return "A2_FAIL"
    art = arts[0]
    fin = next((f for f in by_kind.get("r4-final", []) if f["digest"] == art["payload"]["release"] and ok(f, "release-final")), None)
    if not fin:
        return "A3_FAIL"
    entry = next(x for x in art["payload"]["artifacts"] if x["digest"] == d)
    ba = next((b for b in by_kind.get("r4-build", []) if b["payload"]["artifact_digest"] == d and b["payload"]["tbm_digest"] == entry["tbm_digest"]
               and b["payload"]["source"] == fin["payload"]["source"] and ok(b, "build-attestation")), None)
    if not ba:
        return "A4a_FAIL"
    cand = next((c for c in by_kind.get("r4-candidate", []) if c["digest"] == fin["payload"]["promoted_from_candidate"] and ok(c, "release-candidate")), None)
    att = next((a for a in by_kind.get("r4-verification", []) if cand and a["payload"]["candidate"] == cand["digest"] and a["payload"]["verdict"] == "ACCEPTED"
                and a["payload"]["source"] == fin["payload"]["source"] and ok(a, "verification-attestation")), None)
    held_tss = by_kind.get("trust-state", [])
    if not (cand and att and cand["payload"]["source"] == fin["payload"]["source"] and any(att["digest"] in t["payload"].get("attestations", []) for t in held_tss)):
        return "A4b_FAIL"
    if not any(art["digest"] in t["payload"].get("artifacts", []) for t in held_tss):
        return "A5_FAIL"
    return "PASS (A2-A6)"


def r4_path_c(binary_path, channel_root_id, build_attestation):
    """06 §2 step 6 (c): run `gov version --trust` of the built binary; compare lineage and TBM digest."""
    r = subprocess.run([binary_path, "version", "--trust"], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "E3_MARKERS": MARKERS})
    rep = json.loads(r.stdout.strip().splitlines()[-1])
    passed = rep["lineage"] == channel_root_id and rep["tbm_digest"] == build_attestation["payload"]["tbm_digest"]
    return {"result": "PASS" if passed else "FAIL", "compared_values_printed_by_candidate": rep, "external_digest_equals_attested": odigest(open(binary_path, "rb").read()) == build_attestation["payload"]["artifact_digest"]}


# ------------------------------------------------------------------------------------------------ run the executor
V = GA.Verifier(SCR)


def run_tool(label, binary_path, fp, stmts, target=TARGET, flags=None, cli=False):
    marker = os.path.join(MARKERS, os.path.basename(binary_path))
    before = os.path.exists(marker)
    d = write_dir(label + ("-m" if flags else ""), stmts) if not os.path.exists(os.path.join(SCR, "stmts", label + ("-m" if flags else ""))) else os.path.join(SCR, "stmts", label + ("-m" if flags else ""))
    if cli:
        r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "gov_accept_reference.py"), "--fingerprint", fp, "--statements", d, "--target", target, binary_path],
                           capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "TMPDIR": SCR, "PYTHONDONTWRITEBYTECODE": "1"})
        res = json.loads(r.stdout)
        res["exit"] = r.returncode
    else:
        res = GA.accept(open(binary_path, "rb").read(), fp, GA.load_statements(d), target, flags=flags, verifier=V)
    res["candidate_executed_marker_created"] = (not before) and os.path.exists(marker)
    return res


def cleanup_markers():
    for f in os.listdir(MARKERS):
        shutil.move(os.path.join(MARKERS, f), os.path.join(SCR, "executed-" + f))


out = {"probe": "E3 first-binary acceptance (AR-0009)", "executor": "gov_accept_reference.py (Python stdlib + OpenSSL " + subprocess.run(["openssl", "version"], capture_output=True, text=True).stdout.strip() + ")",
       "channel": {"root_id": ROOT_ID_CHANNEL, "state_fingerprint_t10": FP10}}
rows = []


def row(id_, attack, expected_secure, proposal, control=None, note=None):
    rows.append({"id": id_, "attack": attack, "expected_secure_outcome": expected_secure, "proposal": proposal, "revision4_control": control, "note": note})


# --- G: genuine current binary
row("G1", "genuine current binary B8, full statements, typed t10 fingerprint", "ACCEPTED",
    run_tool("G1", B8, FP10, FULL, cli=True), control=r4_path_b(B8, FULL, ROOT_ID_CHANNEL, V))
# --- RV4-B-A03 FB1: revoked binary, revocation withheld
row("FB1a", "RV4-B-A03: genuine B7 revoked in t9; transport serves root v1, TPS v1, t1, t5 and B7's statements; withholds t9, t10", "refused",
    run_tool("FB1a", B7, FP10, STRIPPED_FB1), control=r4_path_b(B7, STRIPPED_FB1, ROOT_ID_CHANNEL, V))
row("FB1b", "same binary, every statement served", "refused", run_tool("FB1b", B7, FP10, FULL))
# --- RV4-B-A03 FB2: remediated compromise, root v1 metadata
row("FB2a", "RV4-B-A03: B7x accepted earlier through stolen keys, remediated (root v2 removes the keys, t9 revokes B7x, reference kept); transport serves root v1 and the pre-remediation statements",
    "refused", run_tool("FB2a", B7X, FP10, STRIPPED_FB2), control=r4_path_b(B7X, STRIPPED_FB2, ROOT_ID_CHANNEL, V))
row("FB2b", "same binary, every statement served", "refused", run_tool("FB2b", B7X, FP10, FULL), control=r4_path_b(B7X, FULL, ROOT_ID_CHANNEL, V),
    note="revision 4 path (b) with root v2 metadata refuses (revoked build/artefact keys); with root v1 it passes (FB2a)")
# --- RV4-B-A04: planted binary from a moved tag, self-report
ctl_c = r4_path_c(BPL, ROOT_ID_CHANNEL, BA7 if False else BA8)
cleanup_markers()
row("FB3", "RV4-B-A04: binary built from a moved tag prints the genuine lineage and TBM digest", "refused (no value printed by the candidate is an input)",
    run_tool("FB3", BPL, FP10, FULL), control=ctl_c)
# --- Phase 4: a legacy consumer has no RoT-1 verifier
legacy = {}
if GOV:
    h = subprocess.run([GOV, "--help"], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": SCR})
    t = subprocess.run([GOV, "trust", "--help"], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": SCR})
    legacy = {"binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "top_level_help_mentions_verify_artifact": "verify-artifact" in h.stdout,
              "trust_subcommand_exit": t.returncode, "trust_help_mentions_verify_artifact": "verify-artifact" in (t.stdout + t.stderr)}
row("FB4", "11 Phase 4: a legacy consumer's first RoT-1 binary verified by that binary (self-validation), or by the legacy 4.1.5 gov", "the executor is neither the candidate nor a legacy binary",
    {"executor": "gov_accept_reference.py", "legacy_gov_register": legacy, "result_for_B8": run_tool("FB4", B8, FP10, FULL)["result"]},
    control={"revision4_phase4": "the candidate binary runs `gov trust verify-artifact` on itself (15 rule (16) forbids)"})
# --- RV4-D-A04: ceremony order (no TA-5 ceremony on an unaccepted binary)
executed_during_proposal = [r for r in rows if isinstance(r["proposal"], dict) and r["proposal"].get("candidate_executed_marker_created")]
row("DA04", "RV4-D-A04: confirm-root / confirm-state / in-gate fingerprint evaluated by the unaccepted binary", "no candidate code runs before acceptance; the typed values are consumed by the independent executor",
    {"proposal_runs_that_executed_a_candidate": len(executed_during_proposal), "typed_inputs_consumed_by": "gov_accept_reference.py", "lineage_confirmation": "the fingerprint commits to the lineage id (confirm-root is subsumed)"},
    control={"revision4": "06 §3 steps 1-4 run on the first-install binary", "path_c_executed_candidate": True})
# --- new attacks
row("N-FB1", "stale channel: the operator types the fingerprint of t5 (a cached channel page); B7 revoked later in t9", "residual RS-B1: accepted, labelled with the selected state's issued_at",
    run_tool("N-FB1", B7, FP5, FULL), note="the only selector of state is the typed fingerprint; channel currency is TA-5")
evil_root = envelope("root", {"kind": "root", "version": 1, "keys": pub(["x1", "x2", "xts", "xrep1", "xrep2"]),
                              "grants": {"root": {"keys": [kid("x1"), kid("x2")], "threshold": 2}, "trust-policy": {"keys": [kid("x1"), kid("x2")], "threshold": 2},
                                         "trust-state": {"keys": [kid("xts")], "threshold": 1}, "reproducer": {"keys": [kid("xrep1"), kid("xrep2")], "threshold": 2}},
                              "revoked_keys": [], "previous_digest": None}, ["x1", "x2"])
row("N-FB2", "attacker lineage (own root, TPS, TSS 10 and two reproductions of B8x), served instead of the owner's; operator types the owner's t10 fingerprint", "refused",
    run_tool("N-FB2", B8X, FP10, [evil_root] + [envelope("trust-policy", {"kind": "trust-policy", "version": 2, "lineage": evil_root["digest"], "releases": [REL("R8", 8, S8)]}, ["x1", "x2"])]),
    note="fingerprint = 128-bit prefix of SHA-256 over (lineage, root, policy, state): second-preimage work about 2^128; the 8-hex lineage label alone would be about 2^32")
row("N-FB3", "right binary, wrong target", "refused", run_tool("N-FB3", B8, FP10, FULL, target="aarch64-darwin"))
conflict = repro("R8", S8, B8X_D, TBM8, "rep1", env="forged")
row("N-FB4", "one stolen reproducer key signs a different digest for the same release and target", "refused (availability only)", run_tool("N-FB4", B8, FP10, FULL + [conflict]))
t11x = tss(11, ROOT2, TPS2, P9 + [[9, T9["digest"]], [10, T10["digest"]]], REVS, [B7_D, B7X_D, B8_D, B8X_D], "2026-09-14T00:00:00Z")
forged8x = [repro("R8", S8, B8X_D, TBM8, k, env="forged") for k in ("rep4", "rep5")]
row("N-FB5", "two stolen reproducer keys + stolen trust-state key publish B8x in t11x; transport withholds honest reproductions; operator types the owner's t10 fingerprint", "refused",
    run_tool("N-FB5", B8X, FP10, [s for s in FULL if s not in RP8] + forged8x + [t11x]))
row("N-FB6", "same, but the channel itself is compromised and publishes t11x's fingerprint", "accepted: channel compromise is outside TA-5",
    run_tool("N-FB6", B8X, ofingerprint(LINEAGE, 2, ROOT2["digest"], 2, TPS2["digest"], 11, t11x["digest"]), [s for s in FULL if s not in RP8] + forged8x + [t11x]),
    note="needs channel + trust-state key + two reproducer keys + transport")
# --- executor substitution and install binding
tool_path = os.path.join(HERE, "gov_accept_reference.py")
tool_digest = odigest(open(tool_path, "rb").read())
sub = os.path.join(SCR, "gov_accept_substituted.py")
open(sub, "w").write(open(tool_path).read().replace('return dict(res, result="BINARY_REVOKED")', 'pass'))
row("N-FB7", "transport substitutes the executor (a copy whose revocation check is removed)", "the operator's digest comparison with the channel refuses the substitute (TA-5)",
    {"channel_published_executor_digest": tool_digest, "substitute_digest": odigest(open(sub, "rb").read()), "comparison_refuses": odigest(open(sub, "rb").read()) != tool_digest})
dest_dir = os.path.join(SCR, "install", "bin")
os.makedirs(dest_dir)
dest = os.path.join(dest_dir, "gov")
data8 = open(B8, "rb").read()
acc = GA.accept(data8, FP10, GA.load_statements(os.path.join(SCR, "stmts", "G1")), TARGET, verifier=V)
inst = GA.install(data8, dest, acc["binary_digest"])
shutil.copyfile(BPL, dest)  # an A3 same-uid process replaces the installed binary after acceptance
row("N-FB8", "accepted bytes replaced after installation in a location the account can write (A3)", "C3 refused unless the install location is protected; residual stated otherwise",
    {"accept": acc["result"], "install": inst, "replacement_succeeded_same_uid": odigest(open(dest, "rb").read()) == BPL_D,
     "note": "a same-uid read-only mode is not protection (chmod); the predicate requires another owner"})
out["rows"] = rows

# ------------------------------------------------------------------------------------------------ conformance vectors and mutants
root2_weak = envelope("root", dict(ROOT2["payload"], note="owner error: signed by one root key"), ["r1"])
tss_on_weak = tss(10, root2_weak, TPS2, P9, REVS, [B8_D], "2026-09-13T00:00:00Z")
root2_badlink = envelope("root", dict(ROOT2["payload"], previous_digest="sha256:" + "0" * 64), ["r1", "r2"])
tss_on_badlink = tss(10, root2_badlink, TPS2, P9, REVS, [B8_D], "2026-09-13T00:00:00Z")
tss_badsig = tss(10, ROOT2, TPS2, P9, REVS, [B8_D], "2026-09-13T00:00:00Z", bad_sig=True)
dup_rep1 = [repro("R8", S8, B8_D, TBM8, "rep1", env="env-1"), repro("R8", S8, B8_D, TBM8, "rep1", env="env-2")]
two_sig = [repro("R8", S8, B8_D, TBM8, None, signers=["rep1", "rep4"])]
wrong_src = [repro("R8", S8, B8_D, TBM8, "rep1"), repro("R8", S7, B8_D, TBM8, "rep4")]
t10_c = tss(10, ROOT2, TPS2, P9 + [[9, T9["digest"]]], [B7_D], [B7_D, B7X_D, B8_D], "2026-09-13T00:00:00Z")
base_min = [ROOT1, ROOT2, TPS1, TPS2, T1, T5, T6, T9]
# owner error: root v2 that revokes rep2/rep3 but still grants them (violates KS-7); t10 on it publishes B7x (not revoked)
g_bad = copy.deepcopy(grants2)
g_bad["reproducer"] = {"keys": [kid(x) for x in ("rep1", "rep2", "rep3", "rep4", "rep5")], "threshold": 2}
root2_ks7 = envelope("root", dict(ROOT2["payload"], grants=g_bad), ["r1", "r2"])
t10_ks7 = tss(10, root2_ks7, TPS2, P9, [B7_D], [B7X_D, B8_D], "2026-09-13T00:00:00Z")
VECTORS = {
    "V01-genuine": (B8, FP10, FULL, "ACCEPTED"),
    "V02-revoked-stripped": (B7, FP10, STRIPPED_FB1, "refuse"),
    "V03-revoked-full": (B7, FP10, FULL, "refuse"),
    "V04-remediated-root-v1": (B7X, FP10, STRIPPED_FB2, "refuse"),
    "V05-planted": (BPL, FP10, FULL, "refuse"),
    "V06-single-reproduction": (B8, FP10, base_min + [T10, RP8[0]], "refuse"),
    "V07-conflict": (B8, FP10, FULL + [conflict], "refuse"),
    "V08-unpublished-with-quorum": (B8B, FP10, FULL + RP8B, "refuse"),
    "V09-reproduction-wrong-source": (B8, FP10, base_min + [T10] + wrong_src, "refuse"),
    "V10-same-key-twice": (B8, FP10, base_min + [T10] + dup_rep1, "refuse"),
    "V11-one-statement-two-keys": (B8, FP10, base_min + [T10] + two_sig, "refuse"),
    "V12-root-below-threshold": (B8, ofingerprint(LINEAGE, 2, root2_weak["digest"], 2, TPS2["digest"], 10, tss_on_weak["digest"]), [ROOT1, root2_weak, TPS2, tss_on_weak] + RP8, "refuse"),
    "V13-root-bad-link": (B8, ofingerprint(LINEAGE, 2, root2_badlink["digest"], 2, TPS2["digest"], 10, tss_on_badlink["digest"]), [ROOT1, root2_badlink, TPS2, tss_on_badlink] + RP8, "refuse"),
    "V14-state-bad-signature": (B8, ofingerprint(LINEAGE, 2, ROOT2["digest"], 2, TPS2["digest"], 10, tss_badsig["digest"]), [ROOT1, ROOT2, TPS2, tss_badsig] + RP8, "refuse"),
    "V15-revoked-signers-only": (B7X, ofingerprint(LINEAGE, 2, ROOT2["digest"], 2, TPS2["digest"], 10, t10_c["digest"]), base_min + [t10_c] + RP7X, "refuse"),
    "V16-root-grants-revoked-keys": (B7X, ofingerprint(LINEAGE, 2, root2_ks7["digest"], 2, TPS2["digest"], 10, t10_ks7["digest"]), [ROOT1, root2_ks7, TPS1, TPS2, t10_ks7] + RP7X, "refuse"),
}
MUTANTS = ["any_state", "skip_revocation", "quorum_one", "skip_conflict", "skip_published", "skip_source_equality", "ignore_signer_revocation",
           "count_statements_not_keys", "multi_signer_counts", "skip_root_link", "skip_root_signatures", "skip_state_signatures", "skip_ks7_check"]
vec_results = {}
for name, (b, fp, st, exp) in VECTORS.items():
    r = run_tool("vec-" + name, b, fp, st)
    vec_results[name] = {"expected": exp, "result": r["result"], "as_expected": (r["result"] == "ACCEPTED") == (exp == "ACCEPTED")}
mut = {}
for m in MUTANTS:
    changed = []
    for name, (b, fp, st, exp) in VECTORS.items():
        r = GA.accept(open(b, "rb").read(), fp, GA.load_statements(os.path.join(SCR, "stmts", "vec-" + name)), TARGET, flags={m: True}, verifier=V)
        if r["result"] != vec_results[name]["result"]:
            changed.append({"vector": name, "unmutated": vec_results[name]["result"], "mutant": r["result"]})
    mut[m] = {"detected": bool(changed), "distinguishing_vectors": changed}
out["conformance_vectors"] = vec_results
out["mutants"] = mut
out["equivalent_mutant_analysis"] = {"ignore_signer_revocation": "equivalent while KS-7 holds: a revoked key is never granted, so a signature by it never counts even when the revocation list is ignored; the KS-7 check itself is mutated as skip_ks7_check"}
out["summary"] = {
    "proposal_refuses_FB1_FB2_FB3": all(r["proposal"]["result"] != "ACCEPTED" for r in rows if r["id"] in ("FB1a", "FB1b", "FB2a", "FB2b", "FB3")),
    "revision4_path_b_accepts_FB1a_FB2a": [r["revision4_control"] for r in rows if r["id"] in ("FB1a", "FB2a")],
    "revision4_path_c_accepts_planted": ctl_c["result"],
    "proposal_accepts_genuine_G1": next(r for r in rows if r["id"] == "G1")["proposal"]["result"],
    "candidate_executed_by_proposal_executor": len(executed_during_proposal),
    "vectors_as_expected": sum(1 for v in vec_results.values() if v["as_expected"]), "vectors": len(vec_results),
    "mutants_detected": sum(1 for v in mut.values() if v["detected"]), "mutants": len(mut),
    "openssl_verifications": V.calls,
}
txt = json.dumps(out, indent=1, default=str).replace(SCR, "<scratch>").replace(HERE, "<evidence>")
if GOV:
    txt = txt.replace(os.path.dirname(GOV), "<legacy-bin>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad-path>", txt))
