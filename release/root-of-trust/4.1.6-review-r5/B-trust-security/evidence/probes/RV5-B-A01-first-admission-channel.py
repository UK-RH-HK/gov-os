#!/usr/bin/env python3
"""RV5-B-A01 / A02 / A03 — first admission under a channel adversary, the evaluator's selector, and restrictor revocation
(review r5 reviewer B, AR-0012). Scratch only; nothing in the repository is written.

Instrument (loaded by path, NOT modified): the architect's reference executor
`release/root-of-trust/4.1.6/evidence/r5/gov_admit_reference.py` (admission-predicate/1, bootstrap mode; real Ed25519
verification through the platform OpenSSL CLI). Statements are signed here with `cryptography` Ed25519 keys derived from
labels, as the architect's FA5 harness does; statement shapes are those `accept()` reads.

  A01  Channel-selected lineage. A channel page (A20) shows the fingerprint of a lineage whose every key the attacker
       generated. The attacker serves its own bundle (it is the download). No genuine key is used. OP-13 (a) and (b),
       including the case where the channel quorum comes from the Trust Policy the typed fingerprint selects.
  A02  The evaluator's selector. The executor source is inspected for any use of `bootstrap.admitter_digests` or of the
       admitter's own revocation; an evaluator that skips negatives (substituted, or genuine but defective) is run.
  A03  Restrictor revocation. Genuine lineage; stolen keys p1, p2 (reproducers) and ts (trust state); a compromised channel
       shows the thief's descendant t11x. Honest reproductions of the genuine digest are HELD (no transport withholding).
       t11x publishes the malicious digest and lists the honest reproductions in `revocations`.
  ORD  Statement-order dependence of the executor's root selection (availability): a self-signed root v1 served first.

Environment: REVIEW_REPO (export of cdb4e14), SCRATCH. Output: JSON on stdout.
"""
import base64, hashlib, importlib.util, inspect, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
SCR = os.environ["SCRATCH"]
GA_PATH = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r5", "gov_admit_reference.py")
spec = importlib.util.spec_from_file_location("gov_admit_reference", GA_PATH)
GA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GA)

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

S = tempfile.mkdtemp(prefix="rv5b-a01-", dir=SCR)
V = GA.Verifier(S)
TARGET = "x86_64-linux"
KEYS = {}


def key(label):
    if label not in KEYS:
        sk = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"rv5b-a01:" + label.encode()).digest())
        raw = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        KEYS[label] = (sk, raw, "ed25519:" + hashlib.sha256(raw).hexdigest())
    return KEYS[label]


def kid(label):
    return key(label)[2]


def stmt(suffix, payload, signers):
    body = GA.canon(payload)
    pt = GA.TYPE_PREFIX + suffix
    sigs = [{"keyid": kid(s), "sig": base64.b64encode(key(s)[0].sign(GA.pae(pt, body))).decode()} for s in signers]
    return {"type": pt, "purpose": GA.TYPE_PURPOSE[pt], "body": body, "payload": payload, "digest": GA.sha256d(body), "sigs": sigs,
            "signer_labels": list(signers)}


def make_binary(marker, lineage, source, inputs):
    tbm = {"build": "release", "lineage": lineage, "source": source, "inputs_manifest_digest": inputs}
    b = ("#!/bin/sh\necho %s\n# GOV-TBM %s\n" % (marker, json.dumps(tbm, sort_keys=True))).encode()
    return b, GA.sha256d(b), GA.parse_tbm(b)[1]


def lineage_world(prefix, channel_quorum, marker, revoke_binary=False):
    """A complete lineage: root v1, Trust Policy v1, one registered release with a verification record, two one-signature
    reproductions of `marker`'s binary, and a Trust State (sequence 10) publishing it. Every key belongs to `prefix`."""
    L = lambda n: f"{prefix}:{n}"
    names = ["r1", "r2", "ts", "p1", "p2", "v1", "f1", "g1", "g2"]
    grants = {"root": {"keys": [kid(L("r1")), kid(L("r2"))], "threshold": 2},
              "trust-policy": {"keys": [kid(L("r1")), kid(L("r2"))], "threshold": 2},
              "trust-state": {"keys": [kid(L("ts"))], "threshold": 1},
              "reproducer": {"keys": [kid(L("p1")), kid(L("p2"))], "threshold": 2},
              "verification-attestation": {"keys": [kid(L("v1"))], "threshold": 1},
              "release-final": {"keys": [kid(L("f1"))], "threshold": 1},
              "release-registration": {"keys": [kid(L("g1")), kid(L("g2"))], "threshold": 2}}
    w = {"prefix": prefix, "L": L}
    w["root1"] = stmt("root+json", {"version": 1, "previous_digest": None, "keys": {kid(L(n)): base64.b64encode(key(L(n))[1]).decode() for n in names},
                                    "grants": grants, "revoked_keys": []}, [L("r1"), L("r2")])
    w["lineage"] = w["root1"]["digest"]
    w["tps1"] = stmt("trust-policy+json", {"policy_version": 1, "bootstrap": {"channel_quorum": channel_quorum}, "registration": {"min_verification_records": 1}},
                     [L("r1"), L("r2")])
    w["source"] = {"release_commit": hashlib.sha1(prefix.encode()).hexdigest(), "content_digest": GA.sha256d(("tree-" + prefix).encode())}
    w["inputs"] = GA.sha256d(("inputs-" + prefix).encode())
    cand = GA.sha256d(GA.canon({"kind": "candidate", "release_id": "4.1.6", "source": w["source"]}))
    w["final"] = stmt("release-final+json", {"release_id": "4.1.6", "source": w["source"], "promoted_from": cand}, [L("f1")])
    w["va"] = stmt("verification-attestation+json", {"candidate_statement_digest": cand, "verdict": "ACCEPTED", "source": w["source"], "inputs_manifest_digest": w["inputs"]}, [L("v1")])
    w["binary"], w["binary_digest"], w["tbm_digest"] = make_binary(marker, w["lineage"], w["source"], w["inputs"])
    w["reg"] = stmt("release-registration+json", {"release_id": "4.1.6", "sequence": 1600, "targets": [TARGET], "final_statement_digest": w["final"]["digest"],
                                                 "candidate_statement_digest": cand, "source": w["source"], "inputs_manifest_digest": w["inputs"],
                                                 "verification_records": [w["va"]["digest"]]}, [L("g1"), L("g2")])
    w["reps"] = [stmt("binary-reproduction+json", {"release_id": "4.1.6", "source": w["source"], "inputs_manifest_digest": w["inputs"], "target": TARGET,
                                                   "binary_digest": w["binary_digest"], "tbm_digest": w["tbm_digest"], "environment_digest": GA.sha256d(p.encode())}, [L(p)])
                 for p in ("p1", "p2")]
    w["tss"] = stmt("trust-state+json", {"sequence": 10, "issued_at": "2026-09-14T00:00:00Z",
                                         "references": {"root": {"version": 1, "digest": w["root1"]["digest"]}, "trust_policy": {"version": 1, "digest": w["tps1"]["digest"]}},
                                         "registrations": [w["reg"]["digest"]], "published_binaries": [w["binary_digest"]],
                                         "revocations": [w["binary_digest"]] if revoke_binary else []}, [L("ts")])
    w["fingerprint"] = GA.state_fingerprint(w["lineage"], 1, w["root1"]["digest"], 1, w["tps1"]["digest"], 10, w["tss"]["digest"])
    w["statements"] = [w["root1"], w["tps1"], w["final"], w["va"], w["reg"], w["tss"]] + w["reps"]
    return w


def run(binary, fps, statements, flags=None, evaluator="sha256:" + "ad" * 32):
    r = GA.accept(binary, fps, statements, TARGET, evaluator, flags=flags, verifier=V, workdir=S)
    return {k: r.get(k) for k in ("result", "binary_digest", "lineage", "release_id", "reproducer_keys", "counted", "quorum", "conflicting") if k in r}


genuine_q2 = lineage_world("genuine-owner", 2, "GENUINE-4.1.6")       # owner chose OP-13 (b)
genuine_q1 = lineage_world("genuine-owner-q1", 1, "GENUINE-4.1.6-q1")  # owner chose OP-13 (a)
attacker = lineage_world("channel-attacker", 1, "MALICIOUS-BINARY")    # every key is the attacker's own
genuine_labels = {l for w in (genuine_q2, genuine_q1) for s in w["statements"] for l in s["signer_labels"]}
attacker_labels = {l for s in attacker["statements"] for l in s["signer_labels"]}

rows = {}
rows["CTL-G1 genuine OP-13 (b): two genuine fingerprints"] = run(genuine_q2["binary"], [genuine_q2["fingerprint"]] * 2, genuine_q2["statements"])
rows["CTL-G2 genuine OP-13 (b): one genuine fingerprint (quorum read from the selected Trust Policy)"] = run(genuine_q2["binary"], [genuine_q2["fingerprint"]], genuine_q2["statements"])
rows["CTL-G3 architect CH2 shape: attacker bundle, genuine fingerprint typed"] = run(attacker["binary"], [genuine_q2["fingerprint"]] * 2, attacker["statements"])
rows["CTL-G4 one channel compromised, operator types both values"] = run(attacker["binary"], [attacker["fingerprint"], genuine_q2["fingerprint"]], attacker["statements"])
rows["A01a OP-13 (a): the one channel shows the attacker lineage's fingerprint; attacker bundle"] = run(attacker["binary"], [attacker["fingerprint"]], attacker["statements"])
rows["A01b OP-13 (b): both channels show the attacker lineage's fingerprint; attacker bundle"] = run(attacker["binary"], [attacker["fingerprint"]] * 2, attacker["statements"])
rows["A01c OP-13 (b) owner; one compromised channel; operator types the one value shown"] = run(attacker["binary"], [attacker["fingerprint"]], attacker["statements"])
rows["ORD-1 genuine fingerprint; bundle = attacker root first, then genuine statements (availability)"] = run(genuine_q1["binary"], [genuine_q1["fingerprint"]], attacker["statements"] + genuine_q1["statements"])
rows["ORD-2 genuine fingerprint; bundle = genuine statements first, then attacker root (control)"] = run(genuine_q1["binary"], [genuine_q1["fingerprint"]], genuine_q1["statements"] + attacker["statements"])

# ---- A02: the evaluator
src = inspect.getsource(GA.accept)
revoked_genuine = lineage_world("genuine-owner-rev", 2, "GENUINE-REVOKED", revoke_binary=True)
skip_negatives = {"skip_revocation": True}
rows["A02-control genuine admitter; genuine fingerprints; binary revoked in the selected state"] = run(revoked_genuine["binary"], [revoked_genuine["fingerprint"]] * 2, revoked_genuine["statements"])
rows["A02 evaluator that skips negatives (substituted, or a genuine but defective admitter version the channel lists)"] = run(revoked_genuine["binary"], [revoked_genuine["fingerprint"]] * 2, revoked_genuine["statements"], flags=skip_negatives)

# ---- A03: restrictor revocation by a stolen trust-state key (genuine lineage, stolen p1 p2 ts, compromised channel)
g = genuine_q1
L = g["L"]
evil_bin, evil_d, evil_tbm = make_binary("MALICIOUS-FOR-GENUINE-4.1.6", g["lineage"], g["source"], g["inputs"])
evil_reps = [stmt("binary-reproduction+json", {"release_id": "4.1.6", "source": g["source"], "inputs_manifest_digest": g["inputs"], "target": TARGET,
                                               "binary_digest": evil_d, "tbm_digest": evil_tbm, "environment_digest": GA.sha256d(b"forged")}, [L(p)]) for p in ("p1", "p2")]
honest_rep_digests = [r["digest"] for r in g["reps"]]


def t11x(revocations):
    return stmt("trust-state+json", {"sequence": 11, "issued_at": "2026-09-14T01:00:00Z",
                                     "references": {"root": {"version": 1, "digest": g["root1"]["digest"]}, "trust_policy": {"version": 1, "digest": g["tps1"]["digest"]}},
                                     "registrations": [g["reg"]["digest"]], "published_binaries": [g["binary_digest"], evil_d], "revocations": list(revocations)}, [L("ts")])


tx_plain = t11x([])
tx_rev = t11x(honest_rep_digests)
fp_plain = GA.state_fingerprint(g["lineage"], 1, g["root1"]["digest"], 1, g["tps1"]["digest"], 11, tx_plain["digest"])
fp_rev = GA.state_fingerprint(g["lineage"], 1, g["root1"]["digest"], 1, g["tps1"]["digest"], 11, tx_rev["digest"])
held = g["statements"] + evil_reps   # every honest statement is held: no transport withholding
rows["A03-control stolen p1 p2 ts; channel shows t11x publishing the malicious digest; honest reproductions held"] = run(evil_bin, [fp_plain], held + [tx_plain])
rows["A03 same, t11x also lists the honest reproductions in revocations (no transport)"] = run(evil_bin, [fp_rev], held + [tx_rev])
rows["A03-genuine binary under the thief's t11x (availability side)"] = run(g["binary"], [fp_rev], held + [tx_rev])

cs5 = json.load(open(os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r5", "CS5-tcb-capability-sets.json")))
cs5_rows = {k: v for k, v in cs5["minimal_sets_table"].items()
            if k.startswith(("G_BYTES|OP-2=root|OP-8=1|OP-9=n2q2|", "G_BYTES|OP-2=root|OP-8=2|OP-9=d_n3q3|", "G_SRC|OP-2=root|OP-8=2|OP-9=d_n3q3|"))
            and k.rsplit("|", 1)[1] in ("FA1", "FA2", "P2")}

out = {
    "probe": "RV5-B-A01/A02/A03 first admission, evaluator selector, restrictor revocation (AR-0012)",
    "instrument": "evidence/r5/gov_admit_reference.py (architect, unmodified; sha256 %s)" % hashlib.sha256(open(GA_PATH, "rb").read()).hexdigest(),
    "attacker_uses_genuine_keys_in_A01": sorted(attacker_labels & genuine_labels),
    "A03_stolen_genuine_keys": [L("p1"), L("p2"), L("ts")],
    "rows": rows,
    "A02_executor_source_references": {
        "admitter_digests_referenced": "admitter_digests" in src,
        "evaluator_digest_used_only_for_self_evaluation": src.count("evaluator_digest") == 2,
        "channel_quorum_read_from_selected_trust_policy": 'boot.get("channel_quorum"' in src,
        "lineage_taken_from_first_self_verifying_root_v1_in_the_bundle": 'lineage = chain[1]["digest"]' in src,
        "compiled_or_typed_root_id_input": bool(re.search(r"COMPILED_ROOT|compiled_lineage|TRUST_ROOT_ID|typed_root", src)),
        "revocations_taken_from_selected_tss_list": 'N = set(tss_p.get("revocations", []))' in src,
    },
    "architect_CS5_minimal_sets_for_the_same_victims (committed, read-only)": cs5_rows,
}
out["openssl_verifications"] = V.calls
R_ = rows
out["verdicts"] = {
    "genuine_controls_behave": R_["CTL-G1 genuine OP-13 (b): two genuine fingerprints"]["result"] == "ACCEPTED"
        and R_["CTL-G2 genuine OP-13 (b): one genuine fingerprint (quorum read from the selected Trust Policy)"]["result"] == "CHANNEL_QUORUM_NOT_MET"
        and R_["CTL-G3 architect CH2 shape: attacker bundle, genuine fingerprint typed"]["result"] != "ACCEPTED"
        and R_["CTL-G4 one channel compromised, operator types both values"]["result"] == "CHANNEL_DISAGREEMENT",
    "A01_zero_genuine_keys_used": not (attacker_labels & genuine_labels),
    "A01a_one_channel_admits_malicious_binary_OP13a": R_["A01a OP-13 (a): the one channel shows the attacker lineage's fingerprint; attacker bundle"]["result"] == "ACCEPTED",
    "A01b_two_channels_admit_malicious_binary_OP13b": R_["A01b OP-13 (b): both channels show the attacker lineage's fingerprint; attacker bundle"]["result"] == "ACCEPTED",
    "A01c_OP13b_enforced_only_if_operator_types_two": R_["A01c OP-13 (b) owner; one compromised channel; operator types the one value shown"]["result"] == "ACCEPTED",
    "A02_executor_never_consults_admitter_digests": not out["A02_executor_source_references"]["admitter_digests_referenced"],
    "A02_negative_skipping_evaluator_admits_revoked_binary": R_["A02 evaluator that skips negatives (substituted, or a genuine but defective admitter version the channel lists)"]["result"] == "ACCEPTED"
        and R_["A02-control genuine admitter; genuine fingerprints; binary revoked in the selected state"]["result"] == "BINARY_REVOKED",
    "A03_control_conflict_refuses": R_["A03-control stolen p1 p2 ts; channel shows t11x publishing the malicious digest; honest reproductions held"]["result"] == "REPRODUCTION_CONFLICT",
    "A03_trust_state_revocation_removes_conflict_without_transport": R_["A03 same, t11x also lists the honest reproductions in revocations (no transport)"]["result"] == "ACCEPTED",
    "ORD_executor_root_selection_depends_on_bundle_order": R_["ORD-1 genuine fingerprint; bundle = attacker root first, then genuine statements (availability)"]["result"] != "ACCEPTED"
        and R_["ORD-2 genuine fingerprint; bundle = genuine statements first, then attacker root (control)"]["result"] == "ACCEPTED",
}
txt = json.dumps(out, indent=1, sort_keys=True)
txt = txt.replace(S, "<scratch>").replace(SCR, "<scratch-root>").replace(REPO, "<repo>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
