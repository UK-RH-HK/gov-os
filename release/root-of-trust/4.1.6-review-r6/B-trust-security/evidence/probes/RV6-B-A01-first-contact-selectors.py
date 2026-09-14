#!/usr/bin/env python3
"""RV6-B-A01 / A05 / A06 — first-contact selectors outside the declared first-contact root (review r6 reviewer B, AR-0016).
Scratch only; the repository is never written.

Instruments, loaded by path and NOT modified:
  * `evidence/r6/gov_admit_reference_r6.py` (`accept`, `fc_procedure`, `make_fcm`, `fcm_bytes`, `first_contact_code`;
    real Ed25519 verification through the platform OpenSSL CLI; `sha256sum` as the platform hash tool);
  * FA5's statement builders and world (`evidence/r5/FA5-first-admission.py`), executed from a scratch copy transformed exactly
    as the architect's FA6 S1 does (the five substitutions of `FA6-first-admission.py` SUBS, copied with attribution), up to
    its "CONFORMANCE VECTORS" marker, against the revision-6 executor;
  * `evidence/r6/CS6-derivation-calculator.py` (part C: module functions wrapped; the originals are still called).
`attacker_world`, `SUB_ADM`, `PLAT` and `evaluator_run` follow FA6 (AR-0015), which follows reviewer B r5 `lineage_world`.

Pack text relied on (design, 4106885): `07` §7 step 15 (the trust-state external signer outputs the first-contact manifest and
code of the new state and the fingerprint published in the channels); `30` R-PUB-4; `06` §2 step 2 ("the owner publishes the
first-contact manifest (any carrier) and its code (in each designated source)"); `32` §3, §4 (FC-1…FC-3), §6, §7 (currency
under (c) "either suffices": "The bound is the FCM's valid_until"); `schemas/first-contact-manifest.schema.json` (valid_until
not required); `32` §7 (c): packages "signed by a platform or distribution code-signing service" — no rule names who builds
or submits a package.

Parts
  P (A01, executed)  Publisher-composed first-contact code. The trust-state publisher composes the FCM and its code; each
       designated source, honest and uncompromised, republishes the code it receives. Strategies: a substituted evaluator named
       in the FCM (genuine lineage and state); an attacker lineage with the genuine admitter. Every OP-13 answer. No source is
       compromised and no key other than the publisher's own is used. Controls: honest publisher with one compromised source
       under (b); honest everything.
  R (A05, executed)  Replay of an old genuine platform-signed package under OP-13 (c) "either suffices", platform path only.
       The package carries the FCM of T7 (issued 2026-05-01; `valid_until` absent, as the schema permits). At T7 the genuine B7
       and the malicious B7x (reproduced with the keys p1–p3 later rotated out) are published; both are revoked at T9. A
       transport adversary serves the package and a bundle. Controls: the same FCM with an expired `valid_until`; the current
       code (T10) with the full bundle.
  S (A06, executed)  Package submission under OP-13 (c): the signing service is honest and signs the package it is given; the
       release pipeline submits a substituted evaluator carrying the genuine compiled lineage.
  I (code)  The executor's handling of `compiled_fcm`; FA6's platform-only branch and its signing assumption.
  C (computed)  CS6 with three added atoms: `fcpub` (the first-contact publisher process; implies `ts`), `submit` (the
       package submitter under (c)), `replay` is not added (CS6 has no goal for a revoked binary at first admission; part R is
       the executed evidence). FA minimal sets under all seven OP-13 answers; P2k1/P2k2 bytes; FC-CONTENT. Control: the wrapper
       disabled reproduces the committed FC-ROOT block.

Environment: REVIEW_REPO (export of 4106885), SCRATCH, GOV (legacy 4.1.5; used only inside FA5's prefix where FA5 uses it).
Output: JSON on stdout.
"""
import contextlib, hashlib, importlib.util, io, json, os, shutil, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
R6 = os.path.join(PK, "evidence", "r6")
SCR = tempfile.mkdtemp(prefix="a01-", dir=os.environ["SCRATCH"])
R6_PATH = os.path.join(R6, "gov_admit_reference_r6.py")
FA5_PATH = os.path.join(PK, "evidence", "r5", "FA5-first-admission.py")
FA6_PATH = os.path.join(R6, "FA6-first-admission.py")
CS6_PATH = os.path.join(R6, "CS6-derivation-calculator.py")

# FA6 SUBS, copied verbatim (AR-0015): the only textual changes FA6 applies to its scratch copy of FA5.
SUBS = [
    ('"inputs_manifest_digest": INP7}', '"inputs_manifest_digest": INP7, "kernel_tree_digest": sha256d(b"kernel-R7")}'),
    ('"inputs_manifest_digest": INP8}', '"inputs_manifest_digest": INP8, "kernel_tree_digest": sha256d(b"kernel-R8")}'),
    ('"verification_records": [VA7["digest"]], "units": {}}', '"verification_records": [VA7["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R7"), "units": {}}}'),
    ('"verification_records": [VA8["digest"]], "units": {}}', '"verification_records": [VA8["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R8"), "units": {}}}'),
    ('json_path = os.path.join(HERE, "FA5-first-admission.json")', 'json_path = os.path.join(HERE, "FA5-on-r6.json")'),
]
D1 = os.path.join(SCR, "fa5-on-r6")
os.makedirs(D1)
shutil.copyfile(R6_PATH, os.path.join(D1, "gov_admit_reference.py"))
src = open(FA5_PATH).read()
sub_counts = {}
for a, b in SUBS:
    sub_counts[a[:40]] = src.count(a)
    src = src.replace(a, b)
open(os.path.join(D1, "FA5-first-admission.py"), "w").write(src)
cut = src.index("# ========== CONFORMANCE VECTORS ==========")
os.environ["FA5_SCRATCH"] = os.path.join(SCR, "fa5prefix")
os.makedirs(os.environ["FA5_SCRATCH"], exist_ok=True)
G = {"__file__": os.path.join(D1, "FA5-first-admission.py"), "__name__": "fa5_prefix"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], "FA5-prefix", "exec"), G)
GA = G["GA"]
envelope, to_stmts, key, kid, pub_map, canon, sha256d = G["envelope"], G["to_stmts"], G["key"], G["kid"], G["pub_map"], G["canon"], G["sha256d"]
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = G["TARGET"], G["LINEAGE"], G["ADMITTER_DIGEST"]
ADM_BYTES = open(os.path.join(D1, "gov_admit_reference.py"), "rb").read()
assert GA.sha256d(ADM_BYTES) == ADM_D
g = lambda n: G[n]
WORK = os.path.join(SCR, "plat")
FC_OPTS = {"a": (1, None), "b": (2, None), "c_all_1": (1, "all"), "c_all_2": (2, "all"), "c_either_1": (1, "either"), "c_either_2": (2, "either"), "d": (1, "media")}
out = {"probe": "RV6-B-A01/A05/A06 first-contact selectors outside the declared root (AR-0016)",
       "executor_sha256": hashlib.sha256(open(R6_PATH, "rb").read()).hexdigest(), "fa5_substitutions_applied": sub_counts}


def run_accept(binary, typed, stmts_list, compiled, fcm=None, flags=None, evaluator=ADM_D, now=None):
    return GA.accept(binary, typed, to_stmts(stmts_list), TARGET, evaluator, flags=flags, verifier=V, workdir=SCR,
                     first_contact_manifest=fcm, compiled=compiled, now=now)["result"]


def genuine_fcm(quorum):
    tps = g("TPS1") if quorum == 2 else g("TPS1_Q1")
    t10 = g("T10") if quorum == 2 else g("T10_Q1")
    m = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, tps["digest"], 10, t10["digest"], {TARGET: ADM_D}, "2026-09-13T00:00:00Z")
    return m, GA.fcm_bytes(m), GA.first_contact_code(m)


def attacker_world(admitter_digest=ADM_D, marker="ATTACKER-TCB"):
    """Follows FA6 `attacker_world` (AR-0015; after reviewer B r5 `lineage_world`): every key attacker-generated."""
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
PLAT_PUB = key(PLAT)[1]


def platform_sig(data):
    return key(PLAT)[0].sign(GA.pae(GA.PLATFORM_SIGNATURE_TYPE, data))


def evaluator_run(admitter_bytes, binary, typed, stmts, compiled, fcm_b, now=None):
    if admitter_bytes == ADM_BYTES:
        return run_accept(binary, typed, stmts, compiled, fcm=fcm_b, now=now)
    return "ACCEPTED_BY_SUBSTITUTED_EVALUATOR"


def acc(x):
    return isinstance(x, str) and x.startswith("ACCEPTED")


# ================================================================================================ part P: publisher-composed code
def publisher_attempt(opt, strategy, submitter_signs=False):
    k, mode = FC_OPTS[opt]
    gm, gmb, gfcc = genuine_fcm(k)
    genuine = g("FULL") if k == 2 else g("FULL_Q1")
    if strategy == "substituted_evaluator":
        m = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, gm["state_epoch"]["policy_digest"], 10, gm["state_epoch"]["state_digest"], {TARGET: SUB_ADM_D}, gm["issued_at"])
        fcm_b, fcc, adm, binary, stmts = GA.fcm_bytes(m), GA.first_contact_code(m), SUB_ADM, ATK_SUB["binary"], genuine
    elif strategy == "attacker_lineage_genuine_admitter":
        fcm_b, fcc, adm, binary, stmts = ATK["fcm_bytes"], ATK["fcc"], ADM_BYTES, ATK["binary"], ATK["stmts"] + genuine
    else:
        raise ValueError(strategy)
    compiled = {"channel_quorum": k, "lineage": LINEAGE if mode else None}
    pages = [fcc] * k                        # each designated source, uncompromised, republishes the code the publisher gave it
    signed = (adm == ADM_BYTES) or submitter_signs
    sig = platform_sig(adm) if signed else b"\x00" * 64
    if mode == "media":                      # media prepared from the published code, manifest and admitter
        proc = GA.fc_procedure(pages, fcm_b, adm, TARGET, 1, WORK, verifier=V)
    else:
        proc = GA.fc_procedure(pages, fcm_b, adm, TARGET, k, WORK, verifier=V, platform_pub=PLAT_PUB if mode == "all" else None,
                               platform_signature=sig if mode == "all" else None, require_platform_signature=(mode == "all"))
    if proc["result"] != "OK":
        return proc["result"]
    return evaluator_run(adm, binary, pages, stmts, compiled, fcm_b)


P = {}
for opt in FC_OPTS:
    k, mode = FC_OPTS[opt]
    gm, gmb, gfcc = genuine_fcm(k)
    comp = {"channel_quorum": k, "lineage": LINEAGE if mode else None}
    row = {
        "control_honest_publisher_honest_sources": run_accept(g("B8_BYTES"), [gfcc] * k, g("FULL") if k == 2 else g("FULL_Q1"), comp, fcm=gmb),
        "publisher_compromised_no_source_compromised_substituted_evaluator": publisher_attempt(opt, "substituted_evaluator"),
        "publisher_compromised_no_source_compromised_attacker_lineage_genuine_admitter": publisher_attempt(opt, "attacker_lineage_genuine_admitter"),
    }
    if mode == "all":
        row["publisher_compromised_plus_package_submitter_substituted_evaluator"] = publisher_attempt(opt, "substituted_evaluator", submitter_signs=True)
    if k == 2:
        proc = GA.fc_procedure([ATK["fcc"], gfcc], ATK["fcm_bytes"], ADM_BYTES, TARGET, 2, WORK, verifier=V)
        row["control_honest_publisher_one_source_compromised"] = proc["result"]
    P[opt] = row
out["P_publisher_composed_code"] = P

# ================================================================================================ part R: replayed platform package
T7, TPS1 = g("T7"), g("TPS1")
FCM7 = GA.make_fcm(LINEAGE, 1, LINEAGE, 1, TPS1["digest"], 7, T7["digest"], {TARGET: ADM_D}, "2026-05-01T00:00:00Z")
FCM7_exp = GA.make_fcm(LINEAGE, 1, LINEAGE, 1, TPS1["digest"], 7, T7["digest"], {TARGET: ADM_D}, "2026-05-01T00:00:00Z", valid_until="2026-06-01T00:00:00Z")
NOW = "2026-09-14T00:00:00Z"
compE2 = {"channel_quorum": 2, "lineage": LINEAGE}
old_bundle = [g("ROOT1"), TPS1, g("T1"), g("T5"), g("T6"), T7, g("VA7"), g("FINAL7"), g("REG7")]
pkg_proc = GA.fc_procedure([], None, ADM_BYTES, TARGET, 0, WORK, verifier=V, platform_pub=PLAT_PUB, platform_signature=platform_sig(ADM_BYTES), channel_path=False)
gm2, gmb2, gfcc2 = genuine_fcm(2)
R = {
    "platform_only_procedure_on_the_old_genuine_package": pkg_proc["result"],
    "fcm_schema_requires_valid_until": "valid_until" in json.load(open(os.path.join(PK, "schemas", "first-contact-manifest.schema.json")))["required"],
    "R1_old_package_FCM_T7_no_valid_until_genuine_B7_revoked_at_T9": run_accept(g("B7_BYTES"), [GA.first_contact_code(FCM7)] * 2, old_bundle + g("RP7"), compE2, fcm=GA.fcm_bytes(FCM7), now=NOW),
    "R2_old_package_FCM_T7_no_valid_until_malicious_B7x_revoked_at_T9": run_accept(g("B7x_BYTES"), [GA.first_contact_code(FCM7)] * 2, old_bundle + g("RP7x"), compE2, fcm=GA.fcm_bytes(FCM7), now=NOW),
    "R3_control_old_package_FCM_T7_valid_until_expired": run_accept(g("B7x_BYTES"), [GA.first_contact_code(FCM7_exp)] * 2, old_bundle + g("RP7x"), compE2, fcm=GA.fcm_bytes(FCM7_exp), now=NOW),
    "R4_control_current_code_T10_full_bundle_B7x": run_accept(g("B7x_BYTES"), [gfcc2] * 2, g("FULL"), compE2, fcm=gmb2, now=NOW),
    "R5_control_current_code_T10_old_bundle_B7x": run_accept(g("B7x_BYTES"), [gfcc2] * 2, old_bundle + g("RP7x"), compE2, fcm=gmb2, now=NOW),
    "age_shown_days": 136,
}
out["R_replayed_platform_package"] = R

# ================================================================================================ part S: package submitter
S = {}
for opt in ("c_either_1", "c_either_2", "c_all_1"):
    k, mode = FC_OPTS[opt]
    gm, gmb, gfcc = genuine_fcm(k)
    sig = platform_sig(SUB_ADM)            # the honest service signs the package the submitter gives it
    if mode == "either":
        proc = GA.fc_procedure([], None, SUB_ADM, TARGET, 0, WORK, verifier=V, platform_pub=PLAT_PUB, platform_signature=sig, channel_path=False)
    else:
        proc = GA.fc_procedure([gfcc] * k, gmb, SUB_ADM, TARGET, k, WORK, verifier=V, platform_pub=PLAT_PUB, platform_signature=sig, require_platform_signature=True)
    S[opt] = {"procedure": proc["result"], "admission": "ACCEPTED_BY_SUBSTITUTED_EVALUATOR" if proc["result"] == "OK" else proc["result"]}
out["S_package_submitter"] = S

# ================================================================================================ part I: code inspection
ex_src = open(R6_PATH).read()
fa6_src = open(FA6_PATH).read()
out["I_code"] = {
    "executor_compiled_fcm_occurrences": ex_src.count("compiled_fcm"),
    "executor_accept_reads_compiled_fcm": "comp[\"compiled_fcm\"]" in ex_src or "comp.get(\"compiled_fcm\")" in ex_src,
    "executor_valid_until_checked_only_when_present": "fcm.get(\"valid_until\") is not None" in ex_src,
    "FA6_platform_only_branch_passes_current_genuine_manifest": "run_accept(binary, [gfcc] * k, stmts, dict(compiled, compiled_fcm=gmb), fcm=gmb)" in fa6_src,
    "FA6_assumes_platform_signs_only_the_genuine_admitter": "signed = (adm == ADM_BYTES) or (\"alt\" in caps)" in fa6_src,
}
pack = {f: open(os.path.join(PK, f)).read() for f in ("07-RELEASE-ENVELOPE-SPEC.md", "30-RELEASE-REGISTRATION-AND-REPRODUCTION.md", "06-BOOTSTRAP.md", "32-FIRST-CONTACT-ROOT.md", "31-INDEPENDENT-ADMISSION.md")}
out["I_design_text"] = {
    "07_step15_trust_state_signer_outputs_fcm_and_code": [l for l in pack["07-RELEASE-ENVELOPE-SPEC.md"].splitlines() if l.startswith("| 15 |")],
    "30_R-PUB-4": [l for l in pack["30-RELEASE-REGISTRATION-AND-REPRODUCTION.md"].splitlines() if l.startswith("| R-PUB-4")],
    "32_currency_either_platform_path": [l for l in pack["32-FIRST-CONTACT-ROOT.md"].splitlines() if "The bound is the FCM" in l or "valid_until` (optional)" in l],
    "any_rule_that_a_source_or_media_custodian_derives_the_code_first_hand": any(w in (pack["32-FIRST-CONTACT-ROOT.md"] + pack["06-BOOTSTRAP.md"] + pack["31-INDEPENDENT-ADMISSION.md"]).lower()
                                                                                 for w in ("derives the code", "derive the code", "recomputes the code", "custodian derives the manifest", "verifies the manifest against")),
    "any_rule_naming_who_submits_the_platform_package": any(w in "".join(pack.values()).lower() for w in ("submits the package", "package submitter", "submitted by", "submits to the signing")),
}

# ================================================================================================ part C: calculator with the added atoms
spec = importlib.util.spec_from_file_location("cs6", CS6_PATH)
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
ORIG = {n: getattr(CS6, n) for n in ("srcs", "fc_eval_sub", "atoms_for")}
committed = json.load(open(os.path.join(R6, "CS6-derivation-calculator.json")))
MODE = {"on": False, "media_from_publisher": True}


def w_srcs(C, k):
    return ORIG["srcs"](C, k) or (MODE["on"] and "fcpub" in C)


def w_fc_eval_sub(C, opt, Rr):
    if MODE["on"]:
        k, mode = CS6.FC_OPTS[opt]
        if "submit" in C and mode == "either":
            return True
        if "submit" in C and mode == "all" and w_srcs(C, k):
            return True
        if mode == "media" and MODE["media_from_publisher"] and "fcpub" in C:
            return True
    return ORIG["fc_eval_sub"](C, opt, Rr)


def w_atoms_for(goal, cfg):
    a = list(ORIG["atoms_for"](goal, cfg))
    if MODE["on"]:
        v = cfg["victim"]
        if v in ("FA", "P2k1", "P2k2", "ING_P2k1", "ING_P2k2"):
            a.append("fcpub")
        if v == "FA" and CS6.FC_OPTS[cfg["fc"]][1] in ("all", "either"):
            a.append("submit")
    return a


CS6.srcs, CS6.fc_eval_sub, CS6.atoms_for = w_srcs, w_fc_eval_sub, w_atoms_for
CS6.IMPLIES["fcpub"] = ("ts",)
base = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "FA", "fc": "a", "op4": "sep", "tc": "accept", "env": "a"}
EXTRA = CS6.FC_ATOMS | {"fcpub", "submit"}
Cpart = {"control_wrapper_off_reproduces_committed_FC_ROOT": None, "per_option": {}}
MODE["on"] = False
ctrl_rows = []
for opt in CS6.FC_OPTS:
    fs = CS6.minimal_sets("G_BYTES", dict(base, fc=opt), CS6.R6)["minimal_sets"]
    ctrl_rows.append("| %s | %s | %d |" % (opt, "; ".join(CS6.compact(s) for s in fs if set(s) <= CS6.FC_ATOMS), len([s for s in fs if not set(s) <= CS6.FC_ATOMS])))
Cpart["control_wrapper_off_reproduces_committed_FC_ROOT"] = committed["statements"]["FC-ROOT"].endswith("\n".join(ctrl_rows))
for media_from_pub in (True, False):
    MODE["on"], MODE["media_from_publisher"] = True, media_from_pub
    for opt in CS6.FC_OPTS:
        if opt != "d" and not media_from_pub:
            continue
        fs = CS6.minimal_sets("G_BYTES", dict(base, fc=opt), CS6.R6)["minimal_sets"]
        fc_sets = sorted(sorted(s) for s in fs if set(s) <= EXTRA)
        declared = sorted(sorted(x) for x in CS6.declared_fc_root(opt))
        fsc = CS6.minimal_sets("G_CONTENT", {"reg": "root", "V": 1, "repro": "n2q2", "victim": "FA", "fc": opt, "op4": "sep", "tc": "accept", "env": "a"}, CS6.R6)["minimal_sets"]
        Cpart["per_option"][opt + ("" if media_from_pub else " (media derived first-hand)")] = {
            "declared_first_contact_root": declared,
            "computed_no_key_first_contact_sets_with_publisher_and_submitter_atoms": fc_sets,
            "sets_outside_declared_root": [s for s in fc_sets if s not in declared],
            "content_sets_outside_declared_root": sorted(sorted(s) for s in fsc if set(s) <= EXTRA and sorted(s) not in declared),
        }
MODE["on"], MODE["media_from_publisher"] = True, True
p2 = {}
for victim in ("P2k1", "P2k2"):
    fs = CS6.minimal_sets("G_BYTES", dict(base, victim=victim, fc="-"), CS6.R6)["minimal_sets"]
    p2[victim] = {"with_fcpub": [CS6.compact(s) for s in CS6.undominated(fs)],
                  "committed_OP9_BYTES_row": [l for l in committed["statements"]["OP-9-BYTES"].splitlines() if l.startswith("| n2q2 | %s |" % victim)]}
Cpart["P2_bytes_n2q2_with_publisher_atom"] = p2

# P1 / CIR / ING_P1: a human confirmation (`24` §3.2: typed from an independent channel) or a pin provisioned from the channel
# names the state whose fingerprint the publisher published. Variant: the anchoring event was made after the publisher's
# compromise. CS6 models P1 as never thief-selectable (`thief_selectable`: P1 only when V_P1_NAMES_STATE is off).
O_thief = CS6.thief_selectable


def w_thief(C, cfg, Rr):
    if MODE["on"] and MODE.get("anchor_after_publisher") and "fcpub" in C and cfg["victim"] in ("P1", "CIR", "ING_P1"):
        return True
    return O_thief(C, cfg, Rr)


O_atoms2 = CS6.atoms_for


def w_atoms2(goal, cfg):
    a = list(O_atoms2(goal, cfg))
    if MODE["on"] and MODE.get("anchor_after_publisher") and cfg["victim"] in ("P1", "CIR", "ING_P1") and "fcpub" not in a:
        a.append("fcpub")
    return a


CS6.thief_selectable, CS6.atoms_for = w_thief, w_atoms2
MODE["anchor_after_publisher"] = True
p1 = {}
for goal, victim in (("G_BYTES", "P1"), ("G_BYTES", "CIR"), ("G_CONTENT", "ING_P1")):
    cfg = dict(base, victim=victim, fc="-")
    fs = CS6.minimal_sets(goal, cfg, CS6.R6)["minimal_sets"]
    key = "OP-9-BYTES" if goal == "G_BYTES" else "CONTENT"
    prefix = "| n2q2 | %s |" % victim if goal == "G_BYTES" else "| root | sep | 1 | %s |" % victim
    p1["%s %s" % (goal, victim)] = {"with_fcpub_anchor_after_compromise": [CS6.compact(s) for s in CS6.undominated(fs)],
                                    "committed_row": [l for l in committed["statements"][key].splitlines() if l.startswith(prefix)]}
Cpart["P1_CIR_ING_P1_anchor_typed_or_provisioned_after_publisher_compromise"] = p1
pack25 = open(os.path.join(PK, "25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md")).read()
Cpart["25_s7_row_q_reproducer_keys"] = [l for l in pack25.splitlines() if l.startswith("| q reproducer keys + trust-state key")]
out["C_calculator_with_publisher_and_submitter_atoms"] = Cpart

# ================================================================================================ verdicts
out["verdicts"] = {
    "P_control_honest_accepted_every_option": all(r["control_honest_publisher_honest_sources"] == "ACCEPTED" for r in P.values()),
    "P_control_one_compromised_source_disagreement_under_k2": all(r.get("control_honest_publisher_one_source_compromised", "FIRST_CONTACT_DISAGREEMENT") == "FIRST_CONTACT_DISAGREEMENT" for r in P.values()),
    "P_publisher_alone_admits_under_a_b_c_either_d": all(acc(P[o]["publisher_compromised_no_source_compromised_substituted_evaluator"]) for o in ("a", "b", "c_either_1", "c_either_2", "d")),
    "P_publisher_alone_refused_under_c_all": all(not acc(P[o]["publisher_compromised_no_source_compromised_substituted_evaluator"]) for o in ("c_all_1", "c_all_2")),
    "P_publisher_attacker_lineage_admitted_under_a_b": all(acc(P[o]["publisher_compromised_no_source_compromised_attacker_lineage_genuine_admitter"]) for o in ("a", "b")),
    "P_publisher_plus_submitter_admits_under_c_all": all(acc(P[o]["publisher_compromised_plus_package_submitter_substituted_evaluator"]) for o in ("c_all_1", "c_all_2")),
    "R_old_package_admits_revoked_genuine_B7": R["R1_old_package_FCM_T7_no_valid_until_genuine_B7_revoked_at_T9"] == "ACCEPTED",
    "R_old_package_admits_revoked_malicious_B7x": R["R2_old_package_FCM_T7_no_valid_until_malicious_B7x_revoked_at_T9"] == "ACCEPTED",
    "R_control_expired_valid_until_refused": R["R3_control_old_package_FCM_T7_valid_until_expired"] == "FIRST_CONTACT_MANIFEST_EXPIRED",
    "R_control_current_code_refuses_B7x": not acc(R["R4_control_current_code_T10_full_bundle_B7x"]) and not acc(R["R5_control_current_code_T10_old_bundle_B7x"]),
    "R_valid_until_not_required_by_schema": not R["fcm_schema_requires_valid_until"],
    "S_submitter_admits_under_c_either": all(acc(S[o]["admission"]) for o in ("c_either_1", "c_either_2")),
    "S_control_submitter_alone_refused_under_c_all": not acc(S["c_all_1"]["admission"]),
    "C_control_reproduces_committed_FC_ROOT": Cpart["control_wrapper_off_reproduces_committed_FC_ROOT"],
    "C_sets_outside_declared_root_exist": any(v["sets_outside_declared_root"] for v in Cpart["per_option"].values()),
}
txt = json.dumps(out, indent=1, sort_keys=True)
txt = txt.replace(SCR, "<scratch>").replace(REPO, "<export>")
print(txt)
