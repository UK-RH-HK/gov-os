#!/usr/bin/env python3
"""FA6 — first admission, first-contact root and shared admission vectors against the revision-6 rules (AR-0015).

EVIDENCE ONLY. Executed: real Ed25519 verification through the platform OpenSSL CLI, the platform hash tool `sha256sum`, the
revision-6 reference executor `gov_admit_reference_r6.py`.

Sections
  S1  FA5 unchanged in what it refuses: the revision-5 FA5 harness (`../r5/FA5-first-admission.py`) executed against the
      revision-6 executor. The only textual change to a scratch copy of FA5 adds the fields revision 6 requires and nothing
      else: `kernel_tree_digest` in each verification attestation and a `constitution.kernel_tree_digest` in each registration
      (both equal to the final's existing `kernel_tree_digest`), and the output file name.
  S2  First-contact root (BC5-1; RV5-B-A01 A01a/b/c, A02, ORD; RV5-D-A02) under every OP-13 answer: the operator procedure
      FC-1…FC-3 with platform tools, then the admitter. Attacks: a lineage the attacker generated; a substituted evaluator; a
      state descendant of a stolen trust-state key; bundle order.
  S3  Executed first-contact minima: for each OP-13 answer every subset of the first-contact capabilities is attacked with every
      strategy; the minimal accepting subsets are compared with CS6's first-contact root sets.
  S4  Shared vectors R1–R4 (RV5-M9; RV5-D-A04) and their comparison with the running-mode oracle P4r6.
  S5  Restrictor revocation (CR5-B-01; RV5-B-A03), minimum root threshold (CR5-B-11).
  S6  Admission records: first admission, re-admission, rollback, shipped record, moved-aside store, euid 0
      (CR5-B-03, CR5-B-07, CR5-B-12; RV5-C-A08…A10 shapes).
  S7  Single-rule mutants of the revision-6 rules: each must change at least one vector.

Attribution. Statement builders, keys and worlds are FA5's (AR-0011), executed from a scratch copy; the attacker-lineage world
follows reviewer B's `RV5-B-A01-first-admission-channel.py` (`lineage_world`); the record shapes follow reviewer C's
`admit_tx.py`. Environment: FA6_SCRATCH (scratch root). Output: JSON on stdout.
"""
import base64, contextlib, copy, hashlib, importlib.util, io, itertools, json, os, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCR = tempfile.mkdtemp(prefix="fa6-", dir=os.environ["FA6_SCRATCH"])
R6_PATH = os.path.join(HERE, "gov_admit_reference_r6.py")
FA5_PATH = os.path.join(HERE, "..", "r5", "FA5-first-admission.py")
CS6_PATH = os.path.join(HERE, "CS6-derivation-calculator.py")
P4R6_JSON = os.environ.get("P4R6_JSON")

SUBS = [
    ('"inputs_manifest_digest": INP7}', '"inputs_manifest_digest": INP7, "kernel_tree_digest": sha256d(b"kernel-R7")}'),
    ('"inputs_manifest_digest": INP8}', '"inputs_manifest_digest": INP8, "kernel_tree_digest": sha256d(b"kernel-R8")}'),
    ('"verification_records": [VA7["digest"]], "units": {}}', '"verification_records": [VA7["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R7"), "units": {}}}'),
    ('"verification_records": [VA8["digest"]], "units": {}}', '"verification_records": [VA8["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R8"), "units": {}}}'),
    ('json_path = os.path.join(HERE, "FA5-first-admission.json")', 'json_path = os.path.join(HERE, "FA5-on-r6.json")'),
]


def transformed_fa5_dir():
    d = os.path.join(SCR, "fa5-on-r6")
    os.makedirs(d)
    shutil.copyfile(R6_PATH, os.path.join(d, "gov_admit_reference.py"))
    src = open(FA5_PATH).read()
    counts = {}
    for a, b in SUBS:
        counts[a] = src.count(a)
        src = src.replace(a, b)
    open(os.path.join(d, "FA5-first-admission.py"), "w").write(src)
    return d, counts


out = {"probe": "FA6 first admission and first-contact root, revision 6 (AR-0015)", "executor": "gov_admit_reference_r6.py",
       "executor_sha256": hashlib.sha256(open(R6_PATH, "rb").read()).hexdigest(), "openssl": subprocess.run(["openssl", "version"], capture_output=True, text=True).stdout.strip()}

# ================================================================================================ S1
D1, counts = transformed_fa5_dir()
env = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(SCR, "home"), "TMPDIR": SCR, "PYTHONDONTWRITEBYTECODE": "1", "FA5_SCRATCH": os.path.join(SCR, "fa5run")}
if os.environ.get("GOV"):
    env["GOV"] = os.environ["GOV"]
os.makedirs(env["HOME"], exist_ok=True)
r = subprocess.run([sys.executable, "-B", os.path.join(D1, "FA5-first-admission.py")], capture_output=True, text=True, env=env, cwd=D1)
fa5 = json.load(open(os.path.join(D1, "FA5-on-r6.json")))
out["S1_FA5_on_r6"] = {"exit": r.returncode, "substitutions_applied": counts, "summary": fa5["summary"],
                       "scenarios_not_holding": sorted(k for k, v in fa5["scenarios"].items() if not v["holds"]),
                       "vectors_not_holding": sorted(k for k, v in fa5["conformance_vectors"].items() if not v["holds"])}

# ---- load FA5's builders (transformed copy) against the revision-6 executor, as RV5-D-A04 does, up to its vector section
src = open(os.path.join(D1, "FA5-first-admission.py")).read()
cut = src.index("# ========== CONFORMANCE VECTORS ==========")
os.environ["FA5_SCRATCH"] = os.path.join(SCR, "fa5prefix")
G = {"__file__": os.path.join(D1, "FA5-first-admission.py"), "__name__": "fa5_prefix"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], "FA5-prefix", "exec"), G)
GA = G["GA"]
envelope, to_stmts, fp, key, kid, pub_map, canon, sha256d = G["envelope"], G["to_stmts"], G["fp"], G["key"], G["kid"], G["pub_map"], G["canon"], G["sha256d"]
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = G["TARGET"], G["LINEAGE"], G["ADMITTER_DIGEST"]
ADM_BYTES = open(os.path.join(D1, "gov_admit_reference.py"), "rb").read()
assert GA.sha256d(ADM_BYTES) == ADM_D
g = lambda n: G[n]
FULL, FULL_Q1 = g("FULL"), g("FULL_Q1")
B8, B8_D = g("B8_BYTES"), g("B8_D")


def run_accept(binary, typed, stmts_list, compiled, fcm=None, flags=None, evaluator=ADM_D, now=None):
    return GA.accept(binary, typed, to_stmts(stmts_list), TARGET, evaluator, flags=flags, verifier=V, workdir=SCR, first_contact_manifest=fcm, compiled=compiled, now=now)["result"]


def genuine_fcm(quorum):
    tps = g("TPS1") if quorum == 2 else g("TPS1_Q1")
    t10 = g("T10") if quorum == 2 else g("T10_Q1")
    m = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, tps["digest"], 10, t10["digest"], {TARGET: ADM_D}, "2026-09-13T00:00:00Z")
    return m, GA.fcm_bytes(m), GA.first_contact_code(m)


# ---- attacker lineage world (reviewer B's lineage_world shape; attacker-generated keys only)
def attacker_world(admitter_digest=ADM_D, marker="ATTACKER-TCB"):
    L = lambda n: "atk:" + n
    names = ["r1", "r2", "ts", "p1", "p2", "v1", "f1", "g1", "g2"]
    grants = {"root": {"keys": [kid(L("r1")), kid(L("r2"))], "threshold": 2}, "trust-policy": {"keys": [kid(L("r1")), kid(L("r2"))], "threshold": 2},
              "trust-state": {"keys": [kid(L("ts"))], "threshold": 1}, "reproducer": {"keys": [kid(L("p1")), kid(L("p2"))], "threshold": 2},
              "verification-attestation": {"keys": [kid(L("v1"))], "threshold": 1}, "release-final": {"keys": [kid(L("f1"))], "threshold": 1},
              "release-registration": {"keys": [kid(L("g1")), kid(L("g2"))], "threshold": 2}}
    root1 = envelope("root+json", {"version": 1, "previous_digest": None, "keys": pub_map([L(n) for n in names]), "grants": grants, "revoked_keys": []}, [L("r1"), L("r2")])
    lin = root1["digest"]
    tps = envelope("trust-policy+json", {"policy_version": 1, "bootstrap": {"channel_quorum": 1, "admitter_digests": [admitter_digest]}, "registration": {"min_verification_records": 1}}, [L("r1"), L("r2")])
    source = {"commit": "c-atk", "content_digest": sha256d(b"tree-atk"), "build_profile_digest": sha256d(b"profile-atk")}
    inputs = sha256d(b"inputs-atk")
    cand = sha256d(canon({"kind": "candidate", "release_id": "R8", "source": source}))
    kt = sha256d(b"kernel-atk")
    final = envelope("release-final+json", {"release_id": "R8", "sequence": 8, "promoted_from": cand, "source": source, "kernel_tree_digest": kt}, [L("f1")])
    va = envelope("verification-attestation+json", {"candidate_statement_digest": cand, "verdict": "ACCEPTED", "source": source, "inputs_manifest_digest": inputs, "kernel_tree_digest": kt}, [L("v1")])
    tbm = {"build": "release", "inputs_manifest_digest": inputs, "lineage": lin, "policy_version": 1, "root_version": 1, "source": source, "trust_state": {"digest": "none", "sequence": 1}}
    binary = ("#!/bin/sh\n# GOV-TBM %s\n# %s\n" % (canon(tbm).decode(), marker)).encode()
    bd = sha256d(binary)
    reg = envelope("release-registration+json", {"release_id": "R8", "sequence": 8, "final_statement_digest": final["digest"], "candidate_statement_digest": cand, "source": source,
                                                 "inputs_manifest_digest": inputs, "targets": [TARGET], "verification_records": [va["digest"]], "units": {},
                                                 "constitution": {"kernel_tree_digest": kt, "units": {}}}, [L("g1"), L("g2")])
    reps = [envelope("binary-reproduction+json", {"release_id": "R8", "source": source, "inputs_manifest_digest": inputs, "target": TARGET, "binary_digest": bd,
                                                  "tbm_digest": sha256d(canon(tbm)), "environment_digest": "env"}, [L(p)]) for p in ("p1", "p2")]
    tss = envelope("trust-state+json", {"sequence": 10, "issued_at": "2026-09-14T00:00:00Z", "references": {"root": {"version": 1, "digest": lin}, "trust_policy": {"version": 1, "digest": tps["digest"]}},
                                        "prior_states": [], "registrations": [reg["digest"]], "published_binaries": [bd], "revocations": []}, [L("ts")])
    m = GA.make_fcm(lin, 1, lin, 1, tps["digest"], 10, tss["digest"], {TARGET: admitter_digest}, "2026-09-14T00:00:00Z")
    return {"stmts": [root1, tps, final, va, reg, tss] + reps, "lineage": lin, "binary": binary, "fcm": m, "fcm_bytes": GA.fcm_bytes(m), "fcc": GA.first_contact_code(m)}


SUB_ADM = b"#!/bin/sh\n# substituted admitter: admits every candidate (RV5-B-A02 negative-skipping evaluator)\n"
SUB_ADM_D = GA.sha256d(SUB_ADM)
ATK = attacker_world()
ATK_SUB = attacker_world(admitter_digest=SUB_ADM_D, marker="ATTACKER-TCB-SUB")
PLAT = "platform:code-signing-service"


def platform_sig(data):
    return key(PLAT)[0].sign(GA.pae(GA.PLATFORM_SIGNATURE_TYPE, data))


PLAT_PUB = key(PLAT)[1]
FC_OPTS = {"a": (1, None), "b": (2, None), "c_all_1": (1, "all"), "c_all_2": (2, "all"), "c_either_1": (1, "either"), "c_either_2": (2, "either"), "d": (1, "media")}


def evaluator_run(admitter_bytes, binary, typed, stmts, compiled, fcm_b, now=None):
    """The code the procedure selected runs. The genuine admitter is the revision-6 reference executor; any other bytes are a
    substituted evaluator, which admits the candidate (RV5-B-A02)."""
    if admitter_bytes == ADM_BYTES:
        return run_accept(binary, typed, stmts, compiled, fcm=fcm_b, now=now)
    return "ACCEPTED_BY_SUBSTITUTED_EVALUATOR"


def attempt(opt, caps, strategy):
    """One attacker strategy against a first-install machine whose owner chose OP-13 `opt`; `caps` ⊆ {ch1, ch2, op1src, alt, media}."""
    k, mode = FC_OPTS[opt]
    gm, gmb, gfcc = genuine_fcm(k)
    genuine_stmts = FULL if k == 2 else FULL_Q1
    compiled = {"channel_quorum": k, "lineage": LINEAGE if mode in ("all", "either", "media") else None}
    if strategy == "lineage_genuine_admitter":
        fcm_b, fcc, adm, binary, stmts = ATK["fcm_bytes"], ATK["fcc"], ADM_BYTES, ATK["binary"], ATK["stmts"] + genuine_stmts
    elif strategy == "substituted_evaluator":
        sm = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, gm["state_epoch"]["policy_digest"], 10, gm["state_epoch"]["state_digest"], {TARGET: SUB_ADM_D}, "2026-09-13T00:00:00Z")
        fcm_b, fcc, adm, binary, stmts = GA.fcm_bytes(sm), GA.first_contact_code(sm), SUB_ADM, ATK_SUB["binary"], genuine_stmts
    elif strategy == "lineage_attacker_admitter":
        fcm_b, fcc, adm, binary, stmts = ATK_SUB["fcm_bytes"], ATK_SUB["fcc"], SUB_ADM, ATK_SUB["binary"], ATK_SUB["stmts"]
    else:
        raise ValueError(strategy)
    signed = (adm == ADM_BYTES) or ("alt" in caps)                           # the platform path signs only the owner's admitter unless compromised
    sig = platform_sig(adm) if signed else b"\x00" * 64
    if mode == "media":
        pages = [fcc if "media" in caps else gfcc]
        manifest = fcm_b if "media" in caps else gmb
        admitter = adm if "media" in caps else ADM_BYTES
        proc = GA.fc_procedure(pages, manifest, admitter, TARGET, 1, os.path.join(SCR, "plat"), verifier=V)
        if proc["result"] != "OK":
            return proc["result"]
        return evaluator_run(admitter, binary, pages, stmts, compiled, manifest)
    p1 = fcc if "ch1" in caps else gfcc
    pages = [p1] if k == 1 else ([p1, p1] if "op1src" in caps else [p1, fcc if "ch2" in caps else gfcc])
    manifest = fcm_b if (fcc in pages) else gmb
    results = []
    if mode in (None, "all", "either"):
        proc = GA.fc_procedure(pages, manifest, adm, TARGET, k, os.path.join(SCR, "plat"), verifier=V, platform_pub=PLAT_PUB if mode == "all" else None,
                               platform_signature=sig if mode == "all" else None, require_platform_signature=(mode == "all"))
        if proc["result"] == "OK":
            results.append(evaluator_run(adm, binary, pages, stmts, compiled, manifest))
        else:
            results.append(proc["result"])
    if mode == "either":
        proc = GA.fc_procedure([], None, adm, TARGET, 0, os.path.join(SCR, "plat"), verifier=V, platform_pub=PLAT_PUB, platform_signature=sig, channel_path=False)
        if proc["result"] == "OK":
            # path-only admission: the platform-authenticated package carries its compiled manifest
            if adm == ADM_BYTES:
                results.append(run_accept(binary, [gfcc] * k, stmts, dict(compiled, compiled_fcm=gmb), fcm=gmb))
            else:
                results.append("ACCEPTED_BY_SUBSTITUTED_EVALUATOR")
        else:
            results.append(proc["result"])
    acc = [x for x in results if x.startswith("ACCEPTED")]
    return acc[0] if acc else results[0]


# ================================================================================================ S2 named first-contact scenarios
S2 = {}
for opt in FC_OPTS:
    k, mode = FC_OPTS[opt]
    rows = {}
    gm, gmb, gfcc = genuine_fcm(k)
    comp = {"channel_quorum": k, "lineage": LINEAGE if mode else None}
    rows["honest_genuine_sources"] = run_accept(B8, [gfcc] * k, FULL if k == 2 else FULL_Q1, comp, fcm=gmb)
    if mode != "media":
        rows["A01a_lineage_one_page_compromised_sources_read_as_procedure"] = attempt(opt, {"ch1"}, "lineage_genuine_admitter")
        rows["A01b_lineage_all_channel_pages_compromised"] = attempt(opt, {"ch1", "ch2"}, "lineage_genuine_admitter")
        rows["A01c_lineage_one_page_operator_types_one_value (genuine admitter, compiled quorum)"] = run_accept(ATK["binary"], [ATK["fcc"]], ATK["stmts"], comp, fcm=ATK["fcm_bytes"])
        rows["A01c'_lineage_one_page_operator_types_that_value_twice (TA-5/A10)"] = attempt(opt, {"ch1", "op1src"}, "lineage_genuine_admitter")
        rows["D-A02_substituted_evaluator_one_page_fingerprints_genuine"] = attempt(opt, {"ch1"}, "substituted_evaluator")
        rows["D-A02_substituted_evaluator_all_pages"] = attempt(opt, {"ch1", "ch2"}, "substituted_evaluator")
        if mode in ("all", "either"):
            rows["C_platform_path_compromised_alone (attacker-compiled admitter)"] = attempt(opt, {"alt"}, "lineage_attacker_admitter")
            rows["C_platform_path_and_pages (attacker-compiled admitter)"] = attempt(opt, {"alt", "ch1", "ch2"}, "lineage_attacker_admitter")
    else:
        rows["D_channels_compromised_media_intact"] = attempt(opt, {"ch1", "ch2"}, "lineage_genuine_admitter")
        rows["D_media_custody_compromised"] = attempt(opt, {"media"}, "lineage_attacker_admitter")
    S2[opt] = rows
# evaluator binding, lineage from the typed value, bundle order, manifest binding
compB = {"channel_quorum": 2, "lineage": None}
gm2, gmb2, gfcc2 = genuine_fcm(2)
unlisted_fcm = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 10, g("T10")["digest"], {TARGET: SUB_ADM_D}, "2026-09-13T00:00:00Z")
T10_admrev = envelope("trust-state+json", dict(g("T10")["payload"], revocations=sorted(g("T10")["payload"]["revocations"] + [ADM_D])), ["ts1"])
fcm_admrev = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 10, T10_admrev["digest"], {TARGET: ADM_D}, "2026-09-13T00:00:00Z")
evaluator_rows = {
    "FC-8_genuine_admitter_not_listed_by_selected_policy (a defective or superseded admitter version)": run_accept(B8, [gfcc2] * 2, FULL, compB, fcm=gmb2, evaluator=SUB_ADM_D),
    "FC-8_admitter_revoked_in_selected_state": run_accept(B8, [GA.first_contact_code(fcm_admrev)] * 2, [s for s in FULL if s is not g("T10")] + [T10_admrev], compB, fcm=GA.fcm_bytes(fcm_admrev)),
    "FC-8_manifest_admitters_differ_from_policy_list": run_accept(B8, [GA.first_contact_code(unlisted_fcm)] * 2, FULL, compB, fcm=GA.fcm_bytes(unlisted_fcm)),
    "FC-5_manifest_not_the_one_the_code_names": run_accept(B8, [gfcc2] * 2, FULL, compB, fcm=GA.fcm_bytes(dict(gm2, issued_at="2026-01-01T00:00:00Z"))),
    "FC-3_procedure_admitter_digest_not_in_manifest": GA.fc_procedure([gfcc2, gfcc2], gmb2, SUB_ADM, TARGET, 2, os.path.join(SCR, "plat"))["result"],
    "FC-1_procedure_pages_disagree": GA.fc_procedure([gfcc2, ATK["fcc"]], gmb2, ADM_BYTES, TARGET, 2, os.path.join(SCR, "plat"))["result"],
    "FC-2_procedure_manifest_hash_mismatch": GA.fc_procedure([gfcc2, gfcc2], ATK["fcm_bytes"], ADM_BYTES, TARGET, 2, os.path.join(SCR, "plat"))["result"],
    "ORD-1_attacker_root_first_genuine_code (CR5-B-06)": run_accept(B8, [gfcc2] * 2, ATK["stmts"] + FULL, compB, fcm=gmb2),
    "ORD-2_genuine_first_attacker_root_after": run_accept(B8, [gfcc2] * 2, FULL + ATK["stmts"], compB, fcm=gmb2),
    "ORD-3_state_fingerprint_mode_attacker_root_first (revision-5 input shape)": run_accept(B8, [g("FP10")] * 2, ATK["stmts"] + FULL, compB),
    "K2b-like_thief_descendant_both_pages (FA5 K2b shape; stated first-contact root plus trust-state key)": None,
}
# K2b shape: stolen ts + reproducer keys; the manifest names the thief's descendant t11x
t11x, forged = g("t11x"), g("forged_rp8x")
fcm_tx = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 11, t11x["digest"], {TARGET: ADM_D}, "2026-09-14T00:00:00Z")
evaluator_rows["K2b-like_thief_descendant_both_pages (FA5 K2b shape; stated first-contact root plus trust-state key)"] = run_accept(g("B8x_BYTES"), [GA.first_contact_code(fcm_tx)] * 2, g("stmts_k2"), compB, fcm=GA.fcm_bytes(fcm_tx))
S2["evaluator_lineage_and_manifest_rows"] = evaluator_rows
out["S2_first_contact_named_scenarios"] = S2

# ================================================================================================ S3 executed first-contact minima versus CS6
spec = importlib.util.spec_from_file_location("cs6", CS6_PATH)
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
S3 = {}
for opt in FC_OPTS:
    k, mode = FC_OPTS[opt]
    universe = ["media"] if mode == "media" else (["ch1"] + (["ch2", "op1src"] if k == 2 else []) + (["alt"] if mode in ("all", "either") else []))
    accepting = []
    for r_ in range(0, len(universe) + 1):
        for sub in itertools.combinations(universe, r_):
            caps = set(sub)
            if any(set(a) <= caps for a in accepting):
                continue
            res = [attempt(opt, caps, s_) for s_ in ("lineage_genuine_admitter", "substituted_evaluator", "lineage_attacker_admitter")]
            if any(x.startswith("ACCEPTED") for x in res):
                accepting.append(sorted(sub))
    base = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "FA", "fc": opt, "op4": "sep", "tc": "accept", "env": "a"}
    cs = CS6.minimal_sets("G_BYTES", base, CS6.R6)["minimal_sets"]
    cs_fc = sorted(sorted(s) for s in cs if set(s) <= CS6.FC_ATOMS)
    S3[opt] = {"executed_minimal_first_contact_sets": sorted(accepting), "cs6_first_contact_root_sets": cs_fc, "equal": sorted(accepting) == cs_fc,
               "cs6_declared": sorted(sorted(x) for x in CS6.declared_fc_root(opt))}
out["S3_executed_first_contact_minima_vs_CS6"] = S3

# ================================================================================================ S4 shared vectors R1–R4 (RV5-D-A04)
T10 = g("T10")
BASE = [g(n) for n in ("ROOT1", "ROOT2", "TPS1", "T1", "T5", "T6", "T7", "T9")]
REST = [g(n) for n in ("VA7", "VA8", "FINAL7", "FINAL8", "REG7")]


def t10_with(tps=None, **changes):
    tps = tps or g("TPS1")
    p = copy.deepcopy(T10["payload"])
    p["references"]["trust_policy"] = {"version": 1, "digest": tps["digest"]}
    p.update(changes)
    t = envelope("trust-state+json", p, ["ts1"])
    return t, fp(LINEAGE, 2, g("ROOT2")["digest"], 1, tps["digest"], 10, t["digest"])


R = {}
R["R0_control"] = run_accept(B8, [g("FP10")] * 2, FULL, compB)
t, f = t10_with(revocations=sorted(T10["payload"]["revocations"] + [g("FINAL8")["digest"]]))
R["R1_registered_final_revoked"] = run_accept(B8, [f, f], BASE + [t] + REST + [g("REG8")] + g("RP7") + g("RP7x") + g("RP8"), compB)
t, f = t10_with(revocations=sorted(T10["payload"]["revocations"] + [g("CAND8")]))
R["R2_registered_candidate_revoked"] = run_accept(B8, [f, f], BASE + [t] + REST + [g("REG8")] + g("RP7") + g("RP7x") + g("RP8"), compB)
CAND8x = sha256d(canon({"kind": "candidate", "release_id": "R8", "source": g("SRC8"), "variant": "attacker"}))
FINAL8x = envelope("release-final+json", {"release_id": "R8", "sequence": 8, "promoted_from": CAND8x, "source": g("SRC8"), "kernel_tree_digest": sha256d(b"kernel-R8")}, ["f1"])
REG8x = envelope("release-registration+json", {"release_id": "R8", "sequence": 8, "final_statement_digest": FINAL8x["digest"], "candidate_statement_digest": CAND8x, "source": g("SRC8"),
                                               "inputs_manifest_digest": g("INP8"), "targets": [TARGET], "verification_records": [g("VA8")["digest"]], "units": {},
                                               "constitution": {"kernel_tree_digest": sha256d(b"kernel-R8"), "units": {}}}, ["g1", "g2"])
t, f = t10_with(registrations=[g("REG7")["digest"], REG8x["digest"]])
R["R3_attestation_for_another_candidate_same_source"] = run_accept(B8, [f, f], BASE + [t, g("VA7"), g("VA8"), g("FINAL7"), FINAL8x, g("REG7"), REG8x] + g("RP7") + g("RP7x") + g("RP8"), compB)
TPSm = envelope("trust-policy+json", dict(copy.deepcopy(g("TPS1")["payload"]), eligibility={"min_binary_version": "99.0.0"}), ["r1", "r2"])
t, f = t10_with(tps=TPSm)
R["R4_min_binary_version_above_binary"] = run_accept(B8, [f, f], [g(n) for n in ("ROOT1", "ROOT2")] + [TPSm] + [g(n) for n in ("T1", "T5", "T6", "T7", "T9")] + [t] + REST + [g("REG8")] + g("RP7") + g("RP7x") + g("RP8"), compB)
KT_BAD = envelope("verification-attestation+json", dict(g("VA8")["payload"], kernel_tree_digest=sha256d(b"kernel-R8-weak")), ["v1"])
REG8k = envelope("release-registration+json", dict(g("REG8")["payload"], verification_records=[KT_BAD["digest"]]), ["g1", "g2"])
t, f = t10_with(registrations=[g("REG7")["digest"], REG8k["digest"]])
R["R5_attestation_for_registered_candidate_other_kernel"] = run_accept(B8, [f, f], BASE + [t, g("VA7"), KT_BAD, g("FINAL7"), g("FINAL8"), g("REG7"), REG8k] + g("RP7") + g("RP7x") + g("RP8"), compB)
p4r6 = json.load(open(P4R6_JSON)) if P4R6_JSON and os.path.exists(P4R6_JSON) else None
oracle = {}
if p4r6:
    sc = p4r6["scenarios"]
    oracle = {"R1_registered_final_revoked": sc["R6-AP-R1_registered_final_revoked"]["computed"], "R2_registered_candidate_revoked": sc["R6-AP-R2_registered_candidate_revoked"]["computed"],
              "R3_attestation_for_another_candidate_same_source": sc["R6-AP-R3_attestation_for_another_candidate_same_source"]["computed"],
              "R4_min_binary_version_above_binary": sc["R6-AP-R4_binary_below_min_binary_version"]["computed"],
              "R5_attestation_for_registered_candidate_other_kernel": sc["R6-AP-kernel_attestation_for_other_kernel"]["computed"]}
out["S4_shared_vectors"] = {"bootstrap_reference_r6": R, "running_mode_oracle_P4r6": oracle,
                            "same_codes": {k: (R[k] == v) for k, v in oracle.items()}}

# ================================================================================================ S5 restrictor revocation, root threshold
p1, p2, ts1 = "p1", "p4", "ts1"
RP8_honest = g("RP8")
evil_reps = g("forged_rp8x")
T11c = envelope("trust-state+json", {"sequence": 11, "issued_at": "2026-09-14T00:00:00Z", "references": {"root": {"version": 2, "digest": g("ROOT2")["digest"]}, "trust_policy": {"version": 1, "digest": g("TPS1")["digest"]}},
                                     "prior_states": g("PRIOR10") + [{"sequence": 10, "digest": T10["digest"]}], "registrations": [g("REG7")["digest"], g("REG8")["digest"]],
                                     "published_binaries": sorted([g("B7_D"), g("B7x_D"), B8_D, g("B8x_D")]), "revocations": g("REVS9")}, ["ts1"])
T11r = envelope("trust-state+json", dict(T11c["payload"], revocations=sorted(g("REVS9") + [x["digest"] for x in RP8_honest])), ["ts1"])
held = [g(n) for n in ("ROOT1", "ROOT2", "TPS1", "T1", "T5", "T6", "T7", "T9")] + [T10] + REST + [g("REG8")] + g("RP7") + g("RP7x") + RP8_honest + evil_reps
fpc = fp(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 11, T11c["digest"])
fpr = fp(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 11, T11r["digest"])
RREV = envelope("registration-revocation+json", {"revokes": [x["digest"] for x in evil_reps], "reason": "forged reproductions (05 §9)"}, ["g1", "g2"])
root_t1 = envelope("root+json", dict(copy.deepcopy(g("ROOT1")["payload"]), grants=dict(copy.deepcopy(g("ROOT1")["payload"]["grants"]), root={"keys": g("ROOT1")["payload"]["grants"]["root"]["keys"], "threshold": 1})), ["r1", "r2", "r3"])
out["S5_restrictors_and_root_threshold"] = {
    "A03-control_thief_state_publishes_malicious_digest_honest_reproductions_held": run_accept(g("B8x_BYTES"), [fpc] * 2, held + [T11c], compB),
    "A03_thief_state_also_revokes_the_honest_reproductions (CR5-B-01 (i))": run_accept(g("B8x_BYTES"), [fpr] * 2, held + [T11r], compB),
    "AV-S1_remedy_registration_authority_revokes_forged_reproductions_genuine_binary": run_accept(B8, [g("FP10")] * 2, FULL + evil_reps + [RREV], compB),
    "AV-S1_control_without_revocation_conflict": run_accept(B8, [g("FP10")] * 2, FULL + evil_reps, compB),
    "KS-14_root_v1_threshold_1 (CR5-B-11)": run_accept(B8, [g("FP10")] * 2, [root_t1] + FULL[1:], compB),
}

# ================================================================================================ S6 admission records
S6 = {}
LIN = "sha256:" + "1" * 64
DIG1, DIG2 = GA.sha256d(b"binary-v1-bytes"), GA.sha256d(b"binary-v2-bytes")
rec = lambda d: {"schema": "governance-os.admission-record/1", "binary_digest": d, "target": TARGET, "release_id": "R1", "lineage": LIN, "state_fingerprint": "gov-state:11111111:10:" + "a" * 32,
                 "admitted_at": "2026-09-14T00:00:00Z", "admitter_digest": ADM_D, "valid_until": None, "location_protected": True}
rd = os.path.join(SCR, "s6-readmit", "records")
st = GA.store_dir(rd, LIN)
os.makedirs(os.path.join(st, "projects"), exist_ok=True)
json.dump({"clock_high_water": "2027-01-01T00:00:00Z"}, open(os.path.join(st, "high-water.json"), "w"))
json.dump([{"sequence": 10, "method": "human"}], open(os.path.join(st, "anchors.json"), "w"))
first = GA.write_admission_record(rec(DIG1), rd, LIN)
S6["RV5-C-A09_first_admission_on_store_without_record_moves_aside (AD-2)"] = {"moved": first[2] is not None, "anchors_in_new_store": os.path.exists(os.path.join(first[1], "anchors.json"))}
json.dump({"clock_high_water": "2027-01-01T00:00:00Z"}, open(os.path.join(st, "high-water.json"), "w"))
json.dump([{"sequence": 10, "method": "human"}], open(os.path.join(st, "anchors.json"), "w"))
second = GA.write_admission_record(rec(DIG2), rd, LIN)
S6["CR5-B-03_readmission_keeps_store"] = {"moved": second[2] is not None, "high_water_kept": os.path.exists(os.path.join(st, "high-water.json")), "anchors_kept": os.path.exists(os.path.join(st, "anchors.json")),
                                          "earlier_record_kept (RV5-C-A10 rollback)": os.path.exists(first[0]), "new_record": os.path.exists(second[0])}
mutant = os.path.join(SCR, "s6-mutant", "records")
GA.write_admission_record(rec(DIG1), mutant, LIN)
mv = GA.write_admission_record(rec(DIG2), mutant, LIN, flags={"move_aside_every_run": True})
S6["mutant_move_aside_every_run (revision-5 behaviour) discards the store"] = {"moved": mv[2] is not None}
exe_dir = os.path.join(SCR, "s6-bins")
os.makedirs(exe_dir, exist_ok=True)
v1 = os.path.join(exe_dir, "gov-v1")
open(v1, "wb").write(b"binary-v1-bytes")
S6["rollback_to_v1_after_v2_admitted_C2"] = GA.gov_run(v1, "C2", rd, "2026-09-15T00:00:00Z", [], "C0_C2")["result"]
shipped_dir = os.path.join(SCR, "s6-shipped")
os.makedirs(os.path.join(shipped_dir, "pkg", "bin"), exist_ok=True)
sb = os.path.join(shipped_dir, "pkg", "bin", "gov")
open(sb, "wb").write(b"revoked-genuine-binary")
json.dump(rec(GA.sha256d(b"revoked-genuine-binary")), open(os.path.join(shipped_dir, "pkg", "bin", "admission-shipped.json"), "w"))
S6["RV5-B-A15_record_shipped_beside_binary (CR5-B-07)"] = {"r6": GA.gov_run(sb, "C2", shipped_dir, "2026-09-15T00:00:00Z", [], "C0_C2")["result"],
                                                           "mutant_record_anywhere (revision 5)": GA.gov_run(sb, "C2", shipped_dir, "2026-09-15T00:00:00Z", [], "C0_C2", flags={"record_anywhere": True})["result"]}
moved_only = os.path.join(SCR, "s6-moved", "records")
os.makedirs(os.path.join(moved_only, "vts-" + LIN[:16] + ".pre-admission-0", "admissions"), exist_ok=True)
json.dump(rec(GA.sha256d(b"revoked-genuine-binary")), open(os.path.join(moved_only, "vts-" + LIN[:16] + ".pre-admission-0", "admissions", "x.json"), "w"))
S6["record_only_in_moved_aside_store"] = GA.gov_run(sb, "C2", moved_only, "2026-09-15T00:00:00Z", [], "C0_C2")["result"]
real_geteuid = os.geteuid
os.geteuid = lambda: 0
try:
    S6["CR5-B-12_euid_0_location_predicate"] = GA.tcb_location_protected("/usr/bin/env")[0]
finally:
    os.geteuid = real_geteuid
S6["control_non_root_system_path_protected"] = GA.tcb_location_protected("/usr/bin/env")[0]
out["S6_admission_records"] = S6

# ================================================================================================ S7 single-rule mutants of the revision-6 rules
atk_one = lambda fl: run_accept(ATK["binary"], [ATK["fcc"]], ATK["stmts"], compB, fcm=ATK["fcm_bytes"], flags=fl)
VECTORS = {
    "quorum_from_selected_state": lambda fl: atk_one(fl),
    "lineage_from_bundle_order": lambda fl: run_accept(B8, [gfcc2] * 2, ATK["stmts"] + FULL, compB, fcm=gmb2, flags=fl),
    "skip_evaluator_binding": lambda fl: run_accept(B8, [gfcc2] * 2, FULL, compB, fcm=gmb2, evaluator=SUB_ADM_D, flags=fl),
    "skip_fcm_consistency": lambda fl: run_accept(B8, [GA.first_contact_code(unlisted_fcm)] * 2, FULL, compB, fcm=GA.fcm_bytes(unlisted_fcm), flags=fl),
    "skip_fcm_digest_check": lambda fl: run_accept(B8, [gfcc2] * 2, FULL, compB, fcm=GA.fcm_bytes(dict(gm2, issued_at="2026-01-01T00:00:00Z")), flags=fl),
    "skip_compiled_lineage": lambda fl: run_accept(ATK["binary"], [ATK["fcc"]] * 2, ATK["stmts"], {"channel_quorum": 2, "lineage": LINEAGE}, fcm=ATK["fcm_bytes"], flags=fl),
    "skip_candidate_binding": lambda fl: (lambda t_f: run_accept(B8, [t_f[1]] * 2, BASE + [t_f[0], g("VA7"), g("VA8"), g("FINAL7"), FINAL8x, g("REG7"), REG8x] + g("RP7") + g("RP7x") + g("RP8"), compB, flags=dict(fl, skip_final_restrictor=True)))(t10_with(registrations=[g("REG7")["digest"], REG8x["digest"]])),
    "skip_kernel_binding": lambda fl: (lambda t_f: run_accept(B8, [t_f[1]] * 2, BASE + [t_f[0], g("VA7"), KT_BAD, g("FINAL7"), g("FINAL8"), g("REG7"), REG8k] + g("RP7") + g("RP7x") + g("RP8"), compB, flags=fl))(t10_with(registrations=[g("REG7")["digest"], REG8k["digest"]])),
    "skip_final_candidate_revocation": lambda fl: (lambda t_f: run_accept(B8, [t_f[1]] * 2, BASE + [t_f[0]] + REST + [g("REG8")] + g("RP7") + g("RP7x") + g("RP8"), compB, flags=fl))(t10_with(revocations=sorted(T10["payload"]["revocations"] + [g("FINAL8")["digest"]]))),
    "skip_min_binary_version": lambda fl: (lambda t_f: run_accept(B8, [t_f[1]] * 2, [g("ROOT1"), g("ROOT2"), TPSm] + [g(n) for n in ("T1", "T5", "T6", "T7", "T9")] + [t_f[0]] + REST + [g("REG8")] + g("RP7") + g("RP7x") + g("RP8"), compB, flags=fl))(t10_with(tps=TPSm)),
    "trust_state_revokes_restrictors": lambda fl: run_accept(g("B8x_BYTES"), [fpr] * 2, held + [T11r], compB, flags=fl),
    "skip_min_root_threshold": lambda fl: run_accept(B8, [g("FP10")] * 2, [root_t1] + FULL[1:], compB, flags=fl),
}
S7 = {}
for flag, fn in VECTORS.items():
    base_r, mut_r = fn({}), fn({flag: True})
    S7[flag] = {"base": base_r, "mutant": mut_r, "detected": base_r != mut_r}
S7["record_anywhere"] = {"base": S6["RV5-B-A15_record_shipped_beside_binary (CR5-B-07)"]["r6"], "mutant": S6["RV5-B-A15_record_shipped_beside_binary (CR5-B-07)"]["mutant_record_anywhere (revision 5)"],
                         "detected": S6["RV5-B-A15_record_shipped_beside_binary (CR5-B-07)"]["r6"] != S6["RV5-B-A15_record_shipped_beside_binary (CR5-B-07)"]["mutant_record_anywhere (revision 5)"]}
S7["move_aside_every_run"] = {"base": S6["CR5-B-03_readmission_keeps_store"]["moved"], "mutant": S6["mutant_move_aside_every_run (revision-5 behaviour) discards the store"]["moved"],
                              "detected": S6["CR5-B-03_readmission_keeps_store"]["moved"] != S6["mutant_move_aside_every_run (revision-5 behaviour) discards the store"]["moved"]}
out["S7_revision_6_rule_mutants"] = S7

# ================================================================================================ verdicts
S2v = {}
for opt in FC_OPTS:
    k, mode = FC_OPTS[opt]
    rows = S2[opt]
    acc = lambda x: isinstance(x, str) and x.startswith("ACCEPTED")
    S2v[opt] = {"honest_accepted": rows["honest_genuine_sources"] == "ACCEPTED"}
    if mode == "media":
        S2v[opt].update({"channels_alone_refused": not acc(rows["D_channels_compromised_media_intact"]), "media_custody_is_the_root": acc(rows["D_media_custody_compromised"])})
        continue
    S2v[opt]["one_page_lineage"] = "accepted (stated root)" if acc(rows["A01a_lineage_one_page_compromised_sources_read_as_procedure"]) else "refused"
    S2v[opt]["A01c_one_value_refused_when_k2"] = (k == 1) or rows["A01c_lineage_one_page_operator_types_one_value (genuine admitter, compiled quorum)"] != "ACCEPTED"
    S2v[opt]["D-A02_one_page_evaluator"] = "accepted (stated root)" if acc(rows["D-A02_substituted_evaluator_one_page_fingerprints_genuine"]) else "refused"
out["verdicts"] = {
    "S1_FA5_scenarios_vectors_mutants_unchanged_on_r6": fa5["summary"]["scenarios_hold"] == 45 and fa5["summary"]["vectors_hold"] == 17 and fa5["summary"]["mutants_detected"] == 26,
    "S2_per_option": S2v,
    "S2_evaluator_binding_refusals": {k_: v for k_, v in evaluator_rows.items()},
    "S3_executed_first_contact_minima_equal_CS6_for_every_option": all(v["equal"] for v in S3.values()),
    "S4_R1_R5_refused_by_bootstrap_reference": all(v != "ACCEPTED" for k_, v in R.items() if k_ != "R0_control") and R["R0_control"] == "ACCEPTED",
    "S4_same_codes_as_P4r6": bool(oracle) and all(out["S4_shared_vectors"]["same_codes"].values()),
    "S5_trust_state_revocation_keeps_conflict": out["S5_restrictors_and_root_threshold"]["A03_thief_state_also_revokes_the_honest_reproductions (CR5-B-01 (i))"] == "REPRODUCTION_CONFLICT",
    "S5_registration_authority_revocation_is_the_remedy": out["S5_restrictors_and_root_threshold"]["AV-S1_remedy_registration_authority_revokes_forged_reproductions_genuine_binary"] == "ACCEPTED",
    "S5_root_threshold_1_refused": out["S5_restrictors_and_root_threshold"]["KS-14_root_v1_threshold_1 (CR5-B-11)"] != "ACCEPTED",
    "S6_readmission_keeps_store_and_records": S6["CR5-B-03_readmission_keeps_store"]["moved"] is False and S6["CR5-B-03_readmission_keeps_store"]["anchors_kept"] and S6["CR5-B-03_readmission_keeps_store"]["earlier_record_kept (RV5-C-A10 rollback)"],
    "S6_shipped_record_ignored": S6["RV5-B-A15_record_shipped_beside_binary (CR5-B-07)"]["r6"] == "BINARY_NOT_ADMITTED",
    "S6_euid_0_writable": S6["CR5-B-12_euid_0_location_predicate"] is False,
    "S7_every_revision_6_rule_mutant_detected": all(v["detected"] for v in S7.values()),
}
out["openssl_verifications"] = V.calls
txt = json.dumps(out, indent=1, sort_keys=True, default=str)
txt = txt.replace(SCR, "<scratch>").replace(os.environ["FA6_SCRATCH"], "<scratch-root>").replace(HERE, "<evidence>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
