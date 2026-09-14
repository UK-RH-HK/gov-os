#!/usr/bin/env python3
"""F1 - TCB fact-derivation calculator (AR-0010, root-of-trust specialist B). Computed; no files, no subprocesses.

Question: for every capability subset an attacker may hold, which subsets yield an accepted malicious production binary,
(a) under revision 4 as written and (b) under specialist B's alternative (01-ALTERNATIVE.md, M1), for every owner answer?

Method
  * Revision 4: reviewer B's independent reference model (review r4, reproduced byte-identical by synthesis D and by this
    run) is loaded by path, unmodified, and its `minimal_sets` enumeration is re-run for the configurations quoted.
  * Alternative: an independent process model of one release cycle in which every honest party acts ONLY on its stated
    first-hand check (01 M1 table). The victim's trust state, anchors and currency use reviewer B's functions (`assess`,
    `trust_state`, `ingest`, `negatives`) unmodified, so the retained BC-2 semantics are not re-encoded here.
  * Capability semantics (stated, applied identically to every configuration):
      - a stolen key signs any statement of its purpose;
      - `vpN`  = compromise of verifier N's process: it signs ACCEPTED with its genuine key AND reports ACCEPTED to the
                 owner's first-hand verification record (so vpN implies vaN);
      - `pipeline` (A5/A6) = the attacker controls what the release process hands honest parties to act on (commits to
                 sign, candidates to promote, attestations to reference, sources to build) and can suppress honest
                 parties' outputs inside that process; WITHOUT it, an honest party never acts on attacker content;
      - delivery to the victim (A5) is always free: the victim receives any subset of statements the attacker chooses;
      - {root1, root2} = root threshold (A8): total by assumption.
  * An accepted set is minimal if no proper subset is accepted. Output: JSON on stdout.
"""
import importlib.util, itertools, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.environ.get("AR10_WORKTREE") or os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
B_MODEL = os.path.join(WT, "release", "root-of-trust", "4.1.6-review-r4", "B-trust-security", "evidence", "RV4-B-M-reference-model.py")
_spec = importlib.util.spec_from_file_location("rv4b_model", B_MODEL)
bm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bm)

NOW, DAY, HOUR = bm.NOW, bm.DAY, bm.HOUR
SG = ("commit-good", "tree-good", "inputs-good")
SE = ("commit-evil", "tree-evil", "inputs-good")
BASE = [bm.TPS1, bm.TPS2, bm.T1, bm.T5, bm.T9, bm.T10, bm.RV9]
PRIOR10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]


# ------------------------------------------------------------------------------------------------ alternative: statements
def make_root(op4_no=False):
    """Per-statement thresholds are 1 for attestation purposes; the quorum is counted ACROSS statements by distinct keys
    (01 M1: each rebuilder / verifier signs its own statement). Root keys sign Release Admission Statements (RAS)."""
    r = bm.grants(op4_no=op4_no, va2=False, ba2=False)
    r = {"kind": "root", "v": 1, "grants": {k: set(v) for k, v in r["grants"].items()}, "thr": dict(r["thr"]), "revoked": set()}
    r["grants"]["ba3"] = {"build-attestation"}
    r["grants"]["va2"] = {"verification-attestation"}
    r["thr"]["build-attestation"] = 1
    r["thr"]["verification-attestation"] = 1
    return r


ROOT_KEYS = ("root1", "root2", "root3")
ROOT_THRESHOLD = 2


def RAS(d, seq, source, final_d, signers):
    """Release Admission Statement (01 M1/M3 E1): root threshold; names sequence, admitted source, admitted final digest."""
    return {"kind": "ras", "d": d, "seq": seq, "source": source, "final": final_d, "signers": tuple(signers)}


def ras_valid(s):
    return len({k for k in s["signers"] if k in ROOT_KEYS}) >= ROOT_THRESHOLD


def batt(d, binary_d, tbm_d, source, key):
    return {"kind": "batt", "d": d, "artifact": binary_d, "tbm": tbm_d, "source": source, "signers": (key,), "issued": 0}


def keys_of(stmts, root):
    ks = set()
    for s in stmts:
        ks |= bm.vkeys(s, root)
    return ks


# ------------------------------------------------------------------------------------------------ alternative: admission predicate
def admission_predicate(binary_d, tbm, K_all, victim, legit, q, root):
    """01 M1 Admission Predicate (AP), evaluated by an evaluator that is not the candidate. Order of checks is fixed."""
    plain = [s for s in K_all if s["kind"] != "ras"]
    r, K, ts = bm.assess(plain, dict(victim, root=root), "a")
    ras_all = [s for s in K_all if s["kind"] == "ras" and ras_valid(s)]
    if ts["status"] in ("EQUIVOCATION", "REGRESSION", "BELOW_ANCHOR", "ANCHOR_CONFLICT"):
        return "TRUST_STATE_" + ts["status"]                             # anchor inclusion first (retained BC-2 rule)
    eff = ts.get("eff")
    F = next((s for s in K if s["kind"] == "final" and s["d"] == tbm["embedded"]), None)
    if F is None:
        return "ARTIFACT_IDENTITY_MISMATCH"
    C = next((s for s in K if s["kind"] == "candidate" and s["d"] == F["promoted_from"]), None)
    if C is None or C["source"] != F["source"] or C["tree"] != F["tree"]:
        return "RELEASE_IDENTITY_MISMATCH(source)"                      # V8 retained
    if tbm["source"] != C["source"]:
        return "ARTIFACT_SOURCE_MISMATCH"
    # F-BUILD: >= q distinct build-attestation keys over (binary digest, TBM digest, source)
    bk = keys_of([b for b in K if b["kind"] == "batt" and b["artifact"] == binary_d and b["tbm"] == tbm["d"] and b["source"] == tbm["source"]], root)
    if len(bk) < q:
        return "ARTIFACT_BUILD_QUORUM_NOT_MET"
    # single-valued: one production digest per final (and target) among quorum-attested digests the evaluator holds
    others = {b["artifact"] for b in K if b["kind"] == "batt" and b["artifact"] != binary_d
              and len(keys_of([x for x in K if x["kind"] == "batt" and x["artifact"] == b["artifact"]], root)) >= q}
    if others:
        return "ARTIFACT_EQUIVOCATION"
    # F-SRC
    rejected = [a for a in K if a["kind"] == "vatt" and a["candidate"] == C["d"] and a["verdict"] == "REJECTED"]
    if rejected:
        return "ARTIFACT_SOURCE_REJECTED"                              # negative facts only lower (both options)
    if legit == "L1":
        ras = [s for s in ras_all if s["source"] == C["source"] and s["final"] == F["d"]]
        if not ras:
            return "ARTIFACT_SOURCE_NOT_ADMITTED"
        if not eff or not any(s["d"] in eff["atts"] for s in ras):
            return "ARTIFACT_ADMISSION_UNREFERENCED"
    else:
        ak = keys_of([a for a in K if a["kind"] == "vatt" and a["candidate"] == C["d"] and a["verdict"] == "ACCEPTED"
                      and a["source"] == C["source"] and eff and a["d"] in eff["atts"]], root)
        if len(ak) < 2:
            return "ARTIFACT_SOURCE_UNVERIFIED"
    # F-CUR (retained BC-2 semantics through reviewer B's assess)
    if not eff or binary_d not in eff["arts"]:
        return "ARTIFACT_UNREFERENCED"
    N = bm.negatives(K)
    if binary_d in N or F["d"] in N or C["d"] in N:
        return "ARTIFACT_REVOKED"
    if "C3" not in r["allowed"]:
        return "TRUST_STATE_NOT_C3(" + str(r.get("freshness")) + ")"
    return "ACCEPTED"


# ------------------------------------------------------------------------------------------------ alternative: one release cycle
CAPS_FE = ["root1", "root2", "va1", "va2", "vp1", "vp2", "ba1", "ba2", "ba3", "rc", "rf", "ts", "pipeline"]


def simulate_fe(caps, goal, legit="L1", q=2, rejected_reaches=True, op4_no=False):
    stolen = set(caps)
    for n in ("1", "2"):
        if "vp" + n in stolen:
            stolen.add("va" + n)
    if op4_no and "rf" in stolen:
        stolen.add("rc")
    pipe = "pipeline" in stolen
    root = make_root(op4_no)
    tr = []
    if {"root1", "root2"} <= stolen:
        return "ACCEPTED", ["root threshold (A8): total by assumption"]
    rc_key = "rf1" if op4_no else "rc1"
    K = list(BASE)
    src = SE if goal == "evil_source" else SG
    # 1. candidate (release-candidate signature; not a TCB fact)
    if goal == "evil_source":
        if "rc" in stolen:
            tr.append("candidate signed with stolen key")
        elif pipe:
            tr.append("honest candidate signer reproduced the commit the pipeline handed it")
        else:
            return "NO_CANDIDATE", tr
    cand = bm.CAND("Cx" if goal == "evil_source" else "Cg", src, signers=(rc_key,))
    K.append(cand)
    # 2. verification: two independent verifiers (01 M1 architecture minimum for F-SRC). Honest verifiers REJECT evil source.
    atts, record_accepts = [], True
    for n in ("1", "2"):
        k = "va" + n
        if goal == "evil_source":
            if k in stolen:
                atts.append(bm.VATT("aX" + n, cand["d"], "ACCEPTED", src, signers=(k,)))
            if "vp" + n not in stolen:
                record_accepts = False                                   # the owner's first-hand record shows verifier n REJECTED
                if k not in stolen or rejected_reaches:
                    atts.append(bm.VATT("aR" + n, cand["d"], "REJECTED", src, signers=(k,)))
        else:
            atts.append(bm.VATT("ag" + n, cand["d"], "ACCEPTED", src, signers=(k,)))
    rejected_visible = any(a["verdict"] == "REJECTED" for a in atts) and (rejected_reaches or not pipe)
    accepted_quorum = len(keys_of([a for a in atts if a["verdict"] == "ACCEPTED"], root)) >= 2
    # 3. final (V8 retained). Honest promoter signs only on its first-hand evidence.
    fin = bm.FINAL("Fx" if goal == "evil_source" else "Fg", 20, cand["d"], src)
    if goal == "evil_source":
        if "rf" in stolen:
            tr.append("final signed with stolen key")
        elif pipe and ((legit == "L1" and record_accepts) or (legit == "L2" and accepted_quorum and not rejected_visible)):
            tr.append("honest promoter: legitimacy evidence satisfied on its first-hand view; signed")
        else:
            return "NO_FINAL", tr
    K.append(fin)
    # 4. legitimacy establishment
    ras = None
    if legit == "L1":
        if goal == "evil_source" and not (record_accepts and pipe):
            return "NOT_ADMITTED", tr + ["root custodians: first-hand verification record does not accept the source, or own fetch mismatches (no pipeline)"]
        ras = RAS("ras20", 20, src, fin["d"], signers=("root3", "root1" if "root1" in stolen else "root2"))
        tr.append("honest root ceremony admitted (source, final digest) on two first-hand verification records" if goal == "evil_source" else "genuine admission")
        K.append(ras)
    else:
        if goal == "evil_source" and not accepted_quorum:
            return "NO_ACCEPTED_QUORUM", tr
    # the victim never receives a REJECTED attestation the attacker withholds (delivery is free); honest parties' views use
    # `rejected_visible` instead
    K += [a for a in atts if a["verdict"] == "ACCEPTED"]
    # 5. build: rebuilders build the legitimate source from their own fetch and attest the digest THEY computed
    ba_keys = ["ba1", "ba2", "ba3"][:q]
    good_bin, good_tbm = "BIN(" + src[0] + ")", bm.TBM("tbm-" + src[0], src, (10, "t10"), embedded=fin["d"])
    honest_batts = [batt("b-" + k, good_bin, good_tbm["d"], src, k) for k in ba_keys]
    if goal == "evil_bytes":
        target, tbm = "BIN(malicious-bytes)", bm.TBM("tbm-evil", SG, (10, "t10"), embedded=fin["d"])
        forged = [batt("bx-" + k, target, tbm["d"], SG, k) for k in ba_keys if k in stolen]
        if len(forged) < q:
            return "BUILD_QUORUM_NOT_MET", tr + [f"{len(forged)} of {q} build-attestation keys"]
        K += forged
        tr.append(f"{q} build attestations for the malicious digest signed with stolen keys")
        publisher_sees = forged + ([] if pipe else honest_batts)
        if not pipe:
            publisher_sees = honest_batts                               # forged statements reach the publisher only through the pipeline
    else:
        target, tbm = good_bin, good_tbm
        all_ba = all(k in stolen for k in ba_keys)
        if not pipe and not all_ba:
            return "NOT_BUILT", tr + ["honest rebuilders never act on a release they were not handed (no pipeline)"]
        if legit == "L2" and rejected_visible and not all_ba:
            return "NOT_BUILT", tr + ["honest rebuilders' first-hand check: a REJECTED verdict for the candidate is visible"]
        K += honest_batts
        publisher_sees = honest_batts
        tr.append("rebuilders reproduced the (evil) legitimate-by-evidence source faithfully")
    # 6. publication: honest publisher references exactly one quorum digest per final, never a REJECTED candidate
    digests = {}
    for b in publisher_sees:
        digests.setdefault(b["artifact"], set()).update(bm.vkeys(b, root))
    quorum_digests = [d for d, ks in digests.items() if len(ks) >= q]
    refs_atts = [a["d"] for a in atts if a["verdict"] == "ACCEPTED"] + ([ras["d"]] if ras else [])
    if "ts" in stolen:
        t11 = bm.TSS(11, "t11x", PRIOR10, NOW - HOUR, revs=["R7", "B7"], arts=["B7", target], atts=["a7"] + refs_atts)
        tr.append("TSS 11 signed with stolen trust-state key")
    elif pipe and quorum_digests == [target] and not (goal == "evil_source" and rejected_visible):
        t11 = bm.TSS(11, "t11", PRIOR10, NOW - HOUR, revs=["R7", "B7"], arts=["B7", target], atts=["a7"] + refs_atts)
        tr.append("honest publisher referenced the only quorum digest it was handed")
    elif not pipe and goal == "evil_bytes":
        return "UNREFERENCED", tr + ["honest publisher saw only the honest quorum digest"]
    else:
        return "NOT_PUBLISHED", tr + [f"publisher view: quorum digests {quorum_digests}, REJECTED visible {rejected_visible}"]
    K.append(t11)
    victim = {"human": [{"seq": 10, "d": "t10", "at": NOW - DAY}], "accepted_tbm": (1, 2, 5)}   # P1 proof; accepts descendants (pessimistic)
    return admission_predicate(target, tbm, K, victim, legit, q, root), tr


def minimal_sets(fn, caps, goal, **opt):
    accepted = []
    for n in range(len(caps) + 1):
        for combo in itertools.combinations(caps, n):
            if any(set(a) <= set(combo) for a in accepted):
                continue
            if fn(combo, goal, **opt)[0] == "ACCEPTED":
                accepted.append(combo)
    return [list(a) for a in accepted]


FIRST_HAND = {"root1", "root2", "va1", "va2", "vp1", "vp2", "ba1", "ba2", "ba3"}
ESTABLISHERS = {"evil_bytes": {"ba1", "ba2", "ba3", "root1", "root2"}, "evil_source": {"va1", "va2", "vp1", "vp2", "root1", "root2"}}


def establisher_count(s, goal):
    ids = set()
    for c in s:
        if c in ESTABLISHERS[goal]:
            ids.add(c.replace("vp", "v").replace("va", "v"))
    return len(ids)


def main():
    out = {"probe": "F1 TCB fact-derivation calculator (AR-0010)",
           "reviewer_B_model": os.path.relpath(B_MODEL, WT), "capability_semantics": __doc__.split("Capability semantics")[1].split("An accepted set")[0].strip()}
    # (a) revision 4 as written: reviewer B's enumeration, re-run
    rev4 = []
    for goal, S, op4, rb in (("evil_bytes", "S0", False, 1), ("evil_bytes", "S1", False, 1), ("evil_bytes", "S1", False, 2),
                             ("evil_source", "S0", False, 1), ("evil_source", "S1", False, 1), ("evil_source", "S2", False, 1)):
        for rej in ((True, False) if goal == "evil_source" else (True,)):
            ms = bm.minimal_sets(goal, S=S, op4_no=op4, rebuilders=rb, rejected_reaches_signers=rej)
            rev4.append({"goal": goal, "OP-2_source_authority": S, "rebuilders": rb, "REJECTED_reaches": rej if goal == "evil_source" else None,
                         "minimal_sets": [list(x) for x in ms], "smallest_key_count": min((len([c for c in x if c != "pipeline"]) for x in ms), default=None)})
    out["revision_4_reviewer_B_model"] = rev4
    # (b) alternative, every owner answer
    rows, violations = [], []
    for goal in ("evil_bytes", "evil_source"):
        for legit in ("L1", "L2"):
            for q in (2, 3):
                for op4_no in (False, True):
                    for rej in (True, False):
                        ms = minimal_sets(simulate_fe, CAPS_FE, goal, legit=legit, q=q, rejected_reaches=rej, op4_no=op4_no)
                        row = {"goal": goal, "OC-1_legitimacy": legit, "OC-2_quorum_q": q, "OP-4_no": op4_no, "REJECTED_reaches_publisher": rej,
                               "minimal_sets": ms,
                               "min_first_hand_establishers_in_any_minimal_set": min((establisher_count(s, goal) for s in ms), default=None),
                               "min_keys_or_process_compromises": min((len([c for c in s if c != "pipeline"]) for s in ms), default=None),
                               "any_minimal_set_with_single_key_plus_pipeline": any(len([c for c in s if c != "pipeline"]) <= 1 for s in ms)}
                        need = q if goal == "evil_bytes" else 2
                        if row["min_first_hand_establishers_in_any_minimal_set"] is not None and row["min_first_hand_establishers_in_any_minimal_set"] < min(need, ROOT_THRESHOLD):
                            violations.append(row)
                        rows.append(row)
    out["alternative_rows"] = rows
    out["invariant_check"] = {"statement": "every minimal accepted set contains at least min(required, root threshold) distinct first-hand establishers of the attacked fact (faithful build: q rebuilders; source legitimacy: 2 verifiers or root threshold)",
                              "violations": violations, "holds": not violations}
    # traces for the decisive rows
    out["traces"] = {
        "rev4_route_B_prime_{ba,pipeline}_in_alternative_L1_q2": {"result": simulate_fe(("ba1", "pipeline"), "evil_bytes")[0], "trace": simulate_fe(("ba1", "pipeline"), "evil_bytes")[1]},
        "{ba1,ba2,pipeline}_L1_q2": dict(zip(("result", "trace"), simulate_fe(("ba1", "ba2", "pipeline"), "evil_bytes"))),
        "{ba1,ba2}_no_pipeline_no_ts_L1_q2": dict(zip(("result", "trace"), simulate_fe(("ba1", "ba2"), "evil_bytes"))),
        "{ba1,ba2,pipeline}_L1_q3": dict(zip(("result", "trace"), simulate_fe(("ba1", "ba2", "pipeline"), "evil_bytes", q=3))),
        "rev4_route_S_prime_{va1,pipeline}_L1": dict(zip(("result", "trace"), simulate_fe(("va1", "pipeline"), "evil_source"))),
        "{va1,va2,pipeline}_L1": dict(zip(("result", "trace"), simulate_fe(("va1", "va2", "pipeline"), "evil_source"))),
        "{va1,va2,pipeline}_L2_REJECTED_suppressed": dict(zip(("result", "trace"), simulate_fe(("va1", "va2", "pipeline"), "evil_source", legit="L2", rejected_reaches=False))),
        "{vp1,vp2,pipeline}_L1": dict(zip(("result", "trace"), simulate_fe(("vp1", "vp2", "pipeline"), "evil_source"))),
        "D-A07_shape_{rf,pipeline}_L1": dict(zip(("result", "trace"), simulate_fe(("rf", "pipeline"), "evil_source"))),
        "OP-4_no_everyday_key_plus_pipeline_L1": dict(zip(("result", "trace"), simulate_fe(("rf", "pipeline"), "evil_source", op4_no=True))),
    }
    # compact consequence table (feeds 03-OWNER-CHOICES.md and the BC4-4 restatement)
    table = {}
    for r in rows:
        if r["OP-4_no"]:
            continue
        key = f'{r["goal"]} | {r["OC-1_legitimacy"]} | q={r["OC-2_quorum_q"]} | REJECTED reaches publisher={r["REJECTED_reaches_publisher"]}'
        table[key] = sorted(r["minimal_sets"], key=len)
    out["consequence_table_OP4_yes"] = table
    out["op4_no_changes_any_minimal_set"] = any(
        sorted(map(sorted, a["minimal_sets"])) != sorted(map(sorted, b["minimal_sets"]))
        for a in rows if not a["OP-4_no"] for b in rows
        if b["OP-4_no"] and all(a[k] == b[k] for k in ("goal", "OC-1_legitimacy", "OC-2_quorum_q", "REJECTED_reaches_publisher")))
    print(json.dumps(out, indent=1, default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else str(o)))


if __name__ == "__main__":
    main()
