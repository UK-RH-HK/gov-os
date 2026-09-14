#!/usr/bin/env python3
"""gov-admit reference -- admission-predicate/1 bootstrap executor for RoT-1 revision 5 (AR-0011).

EVIDENCE ONLY.  Patterns adapted from:
  specialist-a/evidence/gov_accept_reference.py  SHA-256 56f101df8ac2055a8088220e5fb5f6f05350ddecfcb3c4821796efba87571b11
  specialist-b/evidence/F2-first-tcb-admission.py SHA-256 4f052150205c391eac7cb26ba7e3d6a2fe241ae09e44a75ad4b2272bf8bb52f4

Implements: accept(), install_from_buffer(), admission records, gov_run().
Signing: external (test harness uses cryptography Ed25519).
Verification: platform OpenSSL CLI (openssl pkeyutl -verify -pubin -rawin) with cache.
"""
import base64, hashlib, json, os, subprocess, sys, tempfile

sys.dont_write_bytecode = True

TYPE_PREFIX = "application/vnd.rot1r5."
TYPE_PURPOSE = {
    TYPE_PREFIX + "root+json": "root",
    TYPE_PREFIX + "trust-policy+json": "trust-policy",
    TYPE_PREFIX + "trust-state+json": "trust-state",
    TYPE_PREFIX + "release-registration+json": "release-registration",
    TYPE_PREFIX + "binary-reproduction+json": "reproducer",
    TYPE_PREFIX + "verification-attestation+json": "verification-attestation",
    TYPE_PREFIX + "release-final+json": "release-final",
}
COMPILED_MIN = {"root": 2, "trust-policy": 2, "release-registration": 2, "reproducer": 2}
ED25519_SPKI_PREFIX = bytes.fromhex("302a300506032b6570032100")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256d(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def pae(ptype, body):
    t = ptype.encode()
    return b"DSSEv1 %d %s %d %s" % (len(t), t, len(body), body)


def state_fingerprint(lineage, root_v, root_d, pol_v, pol_d, seq, state_d):
    epoch = {"lineage": lineage, "root_version": root_v, "root_digest": root_d,
             "policy_version": pol_v, "policy_digest": pol_d,
             "state_sequence": seq, "state_digest": state_d}
    return "gov-state:%s:%d:%s" % (lineage[7:15], seq, hashlib.sha256(canon(epoch)).hexdigest()[:32])


class Verifier:
    def __init__(self, workdir):
        self.w = tempfile.mkdtemp(prefix="v5-", dir=workdir)
        self.cache = {}
        self.calls = 0

    def verify(self, pub_raw, msg, sig):
        k = (pub_raw, hashlib.sha256(msg).digest(), sig)
        if k in self.cache:
            return self.cache[k]
        self.calls += 1
        pem = (b"-----BEGIN PUBLIC KEY-----\n"
               + base64.encodebytes(ED25519_SPKI_PREFIX + pub_raw)
               + b"-----END PUBLIC KEY-----\n")
        n = len(self.cache)
        pp, pm, ps = (os.path.join(self.w, "%d.%s" % (n, x)) for x in ("pem", "msg", "sig"))
        for path, data in ((pp, pem), (pm, msg), (ps, sig)):
            with open(path, "wb") as f:
                f.write(data)
        r = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", pp,
                            "-rawin", "-in", pm, "-sigfile", ps],
                           capture_output=True, text=True)
        ok = r.returncode == 0 and "Successfully" in r.stdout
        self.cache[k] = ok
        return ok


def load_statements(d):
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        try:
            env = json.load(open(os.path.join(d, fn)))
            body = base64.b64decode(env["payload"], validate=True)
            payload = json.loads(body)
        except Exception:
            continue
        pt = env.get("payloadType", "")
        purpose = TYPE_PURPOSE.get(pt)
        if purpose is None or canon(payload) != body:
            continue
        out.append({"file": fn, "type": pt, "purpose": purpose, "body": body,
                    "payload": payload, "digest": sha256d(body), "sigs": env.get("signatures", [])})
    return out


def compute_key_id(pub_raw):
    return "ed25519:" + hashlib.sha256(pub_raw).hexdigest()


def valid_signers(ver, stmt, root_pl, chain_revoked, flags=None):
    flags = flags or {}
    keys_map = root_pl.get("keys", {})
    msg = pae(stmt["type"], stmt["body"])
    ok = set()
    seen = set()
    revoked = chain_revoked if not flags.get("ignore_signer_revocation") else set()
    for s in stmt["sigs"]:
        kid = s.get("keyid")
        if kid in seen:
            continue
        seen.add(kid)
        if kid not in keys_map or kid in revoked:
            continue
        try:
            pub = base64.b64decode(keys_map[kid])
            sig = base64.b64decode(s["sig"], validate=True)
        except Exception:
            continue
        if compute_key_id(pub) != kid:
            continue
        if ver.verify(pub, msg, sig):
            ok.add(kid)
    return ok


def meets_purpose(ver, stmt, root_pl, purpose, chain_revoked, flags=None):
    flags = flags or {}
    g = root_pl.get("grants", {}).get(purpose)
    if not g:
        return False, set()
    signers = valid_signers(ver, stmt, root_pl, chain_revoked, flags) & set(g["keys"])
    minimum = COMPILED_MIN.get(purpose, 1)
    return len(signers) >= max(g["threshold"], minimum), signers


def root_well_formed(root_pl, flags=None):
    flags = flags or {}
    grants = root_pl.get("grants", {})
    revoked = set(root_pl.get("revoked_keys", []))
    keys_map = root_pl.get("keys", {})
    if not flags.get("skip_ks7"):
        for p, g in grants.items():
            ks = g.get("keys", [])
            th = g.get("threshold", 0)
            if not (1 <= th <= len(ks)):
                return False, "threshold_bounds(%s)" % p
            if revoked & set(ks):
                return False, "revoked_key_granted(%s)" % p
        seen = {}
        for kid, pub in keys_map.items():
            if pub in seen.values():
                for k2, p2 in seen.items():
                    if p2 == pub and k2 != kid:
                        return False, "dup_pub(%s,%s)" % (k2, kid)
            seen[kid] = pub
    if not flags.get("skip_ftc"):
        rg = grants.get("reproducer")
        if rg:
            if rg.get("threshold", 0) < 2:
                return False, "rep_th<2"
            rep_k = set(rg.get("keys", []))
            for p2, g2 in grants.items():
                if p2 != "reproducer" and (rep_k & set(g2.get("keys", []))):
                    return False, "rep_other_purpose(%s)" % p2
        rrg = grants.get("release-registration")
        if rrg:
            if rrg.get("threshold", 0) < 2:
                return False, "reg_th<2"
            rr_k = set(rrg.get("keys", []))
            root_g = grants.get("root", {})
            root_k = set(root_g.get("keys", []))
            opt_a = rr_k <= root_k and rrg["threshold"] >= root_g.get("threshold", 0)
            opt_b = all(not (rr_k & set(g2.get("keys", []))) for p2, g2 in grants.items() if p2 != "release-registration")
            if not (opt_a or opt_b):
                return False, "reg_key_constraint"
        vg = grants.get("verification-attestation")
        if vg:
            v_k = set(vg.get("keys", []))
            rep_k = set(grants.get("reproducer", {}).get("keys", []))
            rr_k = set(grants.get("release-registration", {}).get("keys", []))
            if v_k & (rep_k | rr_k):
                return False, "va_overlap"
    return True, None


def build_root_chain(ver, roots, flags=None):
    flags = flags or {}
    by_v = {}
    for r in roots:
        ok, _ = root_well_formed(r["payload"], flags)
        if not ok:
            continue
        v = r["payload"].get("version")
        if isinstance(v, int):
            by_v.setdefault(v, []).append(r)
    chain = {}
    if 1 not in by_v:
        return chain
    for r1 in by_v[1]:
        rev = set(r1["payload"].get("revoked_keys", []))
        ok, _ = meets_purpose(ver, r1, r1["payload"], "root", rev, flags)
        if ok:
            chain[1] = r1
            break
    n = 2
    while n in by_v and (n - 1) in chain:
        prev = chain[n - 1]
        cum = set()
        for cv in chain.values():
            cum |= set(cv["payload"].get("revoked_keys", []))
        for r in by_v[n]:
            if not flags.get("skip_root_link") and r["payload"].get("previous_digest") != prev["digest"]:
                continue
            test_rev = cum | set(r["payload"].get("revoked_keys", []))
            ok_p, _ = meets_purpose(ver, r, prev["payload"], "root", test_rev, flags)
            ok_s, _ = meets_purpose(ver, r, r["payload"], "root", test_rev, flags)
            if ok_p and ok_s:
                chain[n] = r
                break
        if n not in chain:
            break
        n += 1
    return chain


def parse_tbm(binary_bytes):
    try:
        text = binary_bytes.decode("utf-8", errors="replace")
    except Exception:
        return None, None
    for line in text.split("\n"):
        if line.startswith("# GOV-TBM "):
            try:
                tbm = json.loads(line[len("# GOV-TBM "):])
                return tbm, sha256d(canon(tbm))
            except Exception:
                return None, None
    return None, None


def accept(binary_bytes, typed_fingerprints, statements, target, evaluator_digest,
           flags=None, verifier=None, workdir=None):
    flags = flags or {}
    v = verifier or Verifier(workdir or tempfile.gettempdir())
    D = sha256d(binary_bytes)
    res = {"binary_digest": D, "target": target, "candidate_executed": False}

    # 0 self-evaluation
    if not flags.get("allow_self_evaluation") and evaluator_digest == D:
        return dict(res, result="SELF_EVALUATION_REFUSED")

    # 1 channel agreement
    if not typed_fingerprints:
        return dict(res, result="CHANNEL_DISAGREEMENT")
    if not flags.get("skip_channel_agreement") and len(set(typed_fingerprints)) != 1:
        return dict(res, result="CHANNEL_DISAGREEMENT")
    fp_val = typed_fingerprints[0]

    # 3 root chain
    roots = [s for s in statements if s["purpose"] == "root"]
    chain = build_root_chain(v, roots, flags)
    if not chain:
        return dict(res, result="ROOT_CHAIN_INVALID")
    lineage = chain[1]["digest"]
    res["lineage"] = lineage

    chain_revoked = set()
    if not flags.get("ignore_signer_revocation"):
        for cv in chain.values():
            chain_revoked |= set(cv["payload"].get("revoked_keys", []))

    # 4 select trust state
    selected = None
    for t in (s for s in statements if s["purpose"] == "trust-state"):
        p = t["payload"]
        rr = p.get("references", {}).get("root", {})
        rp = p.get("references", {}).get("trust_policy", {})
        rv, rd = rr.get("version"), rr.get("digest")
        pv, pd = rp.get("version"), rp.get("digest")
        if rv not in chain or chain[rv]["digest"] != rd:
            continue
        pol = next((s for s in statements if s["purpose"] == "trust-policy" and s["digest"] == pd), None)
        if pol is None:
            continue
        eff = chain[rv]["payload"]
        ok_t, _ = meets_purpose(v, t, eff, "trust-state", chain_revoked, flags)
        ok_p, _ = meets_purpose(v, pol, eff, "trust-policy", chain_revoked, flags)
        if not (ok_t and ok_p):
            continue
        cfp = state_fingerprint(lineage, rv, rd, pv, pd, p.get("sequence", 0), t["digest"])
        if not flags.get("any_state") and cfp != fp_val:
            continue
        if selected is None or p.get("sequence", 0) > selected[0]["payload"].get("sequence", 0):
            selected = (t, pol, eff, rv)

    if selected is None:
        return dict(res, result="STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")

    tss, tps, eff_root, root_ver = selected
    tss_p, tps_p = tss["payload"], tps["payload"]
    res["selected_state"] = {"sequence": tss_p.get("sequence"), "digest": tss["digest"],
                             "issued_at": tss_p.get("issued_at")}

    boot = tps_p.get("bootstrap", {})
    if not flags.get("skip_channel_quorum") and boot.get("channel_quorum", 1) > len(typed_fingerprints):
        return dict(res, result="CHANNEL_QUORUM_NOT_MET")

    # 5 negatives
    N = set(tss_p.get("revocations", []))
    if not flags.get("skip_revocation") and D in N:
        return dict(res, result="BINARY_REVOKED")

    def alive(s):
        return flags.get("skip_revocation") or s["digest"] not in N

    # 6 reproductions
    R_all = []
    rep_grant = eff_root.get("grants", {}).get("reproducer")
    for s in statements:
        if s["purpose"] != "reproducer" or not alive(s):
            continue
        if not rep_grant:
            continue
        signers = valid_signers(v, s, eff_root, chain_revoked, flags) & set(rep_grant["keys"])
        if flags.get("multi_signer_counts"):
            if len(signers) < 1:
                continue
        elif len(signers) != 1:
            continue
        R_all.append({"s": s, "p": s["payload"], "signers": signers, "digest": s["digest"]})

    R_mine = [r for r in R_all if r["p"].get("binary_digest") == D and r["p"].get("target") == target]

    # 7 registration
    rids_mine = {r["p"].get("release_id") for r in R_mine}

    all_vr = []
    for s in statements:
        if s["purpose"] != "release-registration" or not alive(s):
            continue
        ok_r, _ = meets_purpose(v, s, eff_root, "release-registration", chain_revoked, flags)
        if ok_r:
            all_vr.append(s)

    tss_regs = set(tss_p.get("registrations", []))
    cands = []
    for s in all_vr:
        if not flags.get("skip_registration_reference") and s["digest"] not in tss_regs:
            continue
        if s["payload"].get("release_id") not in rids_mine:
            continue
        cands.append(s)

    if not cands:
        return dict(res, result="RELEASE_UNREGISTERED")

    if not flags.get("skip_registration_equivocation"):
        by_rid = {}
        for s in all_vr:
            by_rid.setdefault(s["payload"].get("release_id"), set()).add(s["digest"])
        for rid, ds in by_rid.items():
            if len(ds) > 1:
                return dict(res, result="REGISTRATION_EQUIVOCATION", release_id=rid)

    reg = None
    fail = None
    for cr in cands:
        cp = cr["payload"]
        if target not in cp.get("targets", []):
            fail = "TARGET_NOT_REGISTERED"
            continue
        if not flags.get("skip_final_restrictor"):
            fd = cp.get("final_statement_digest")
            fs = next((s for s in statements if s["purpose"] == "release-final" and s["digest"] == fd), None)
            if fs is None:
                fail = "RELEASE_FINAL_UNVERIFIED"
                continue
            ok_f, _ = meets_purpose(v, fs, eff_root, "release-final", chain_revoked, flags)
            if not ok_f:
                fail = "RELEASE_FINAL_UNVERIFIED"
                continue
            fp = fs["payload"]
            if fp.get("source") != cp.get("source") or fp.get("promoted_from") != cp.get("candidate_statement_digest"):
                fail = "RELEASE_FINAL_UNVERIFIED"
                continue
        reg = cr
        break

    if reg is None:
        return dict(res, result=fail or "RELEASE_UNREGISTERED")

    rp = reg["payload"]
    release_id = rp.get("release_id")
    res["release_id"] = release_id

    # 8 verification
    cand_d = rp.get("candidate_statement_digest")
    if not flags.get("skip_rejected"):
        for s in statements:
            if s["purpose"] != "verification-attestation" or not alive(s):
                continue
            if s["payload"].get("candidate_statement_digest") != cand_d or s["payload"].get("verdict") != "REJECTED":
                continue
            ok_va, _ = meets_purpose(v, s, eff_root, "verification-attestation", chain_revoked, flags)
            if ok_va:
                return dict(res, result="ARTIFACT_SOURCE_REJECTED")

    if not flags.get("skip_verification_records"):
        vr_set = set(rp.get("verification_records", []))
        vkeys = set()
        for s in statements:
            if s["purpose"] != "verification-attestation" or not alive(s):
                continue
            sp = s["payload"]
            if s["digest"] not in vr_set or sp.get("verdict") != "ACCEPTED":
                continue
            if sp.get("source") != rp.get("source") or sp.get("inputs_manifest_digest") != rp.get("inputs_manifest_digest"):
                continue
            ok_va, sk = meets_purpose(v, s, eff_root, "verification-attestation", chain_revoked, flags)
            if ok_va:
                vkeys |= sk
        reg_cfg = tps_p.get("registration", {})
        minv = max(1, reg_cfg.get("min_verification_records", 1))
        if len(vkeys) < minv:
            return dict(res, result="VERIFICATION_RECORDS_BELOW_MINIMUM", counted=len(vkeys), minimum=minv)

    # 9 quorum
    tbm, tbm_dig = parse_tbm(binary_bytes)
    reg_src = rp.get("source")
    reg_inp = rp.get("inputs_manifest_digest")
    g_th = rep_grant.get("threshold", 2) if rep_grant else 2
    rep_q = tps_p.get("registration", {}).get("reproduction_quorum", 2)
    quorum = max(2, rep_q, g_th)
    if flags.get("quorum_one"):
        quorum = 1

    counted = set()
    for r in R_mine:
        rpp = r["p"]
        if rpp.get("release_id") != release_id:
            continue
        if not flags.get("skip_source_equality"):
            if rpp.get("source") != reg_src or rpp.get("inputs_manifest_digest") != reg_inp:
                continue
        if not flags.get("skip_tbm") and rpp.get("tbm_digest") != tbm_dig:
            continue
        if flags.get("count_statements_not_keys"):
            counted.add(r["digest"])
        else:
            counted |= r["signers"]

    res["reproducer_keys"] = sorted(counted)
    if len(counted) < quorum:
        return dict(res, result="REPRODUCTION_QUORUM_NOT_MET", counted=len(counted), quorum=quorum)

    if not flags.get("skip_conflict"):
        for r in R_all:
            rpp = r["p"]
            if rpp.get("release_id") == release_id and rpp.get("target") == target and rpp.get("binary_digest") != D:
                return dict(res, result="REPRODUCTION_CONFLICT", conflicting=rpp.get("binary_digest"))

    # 10 publication
    if not flags.get("skip_published") and D not in set(tss_p.get("published_binaries", [])):
        return dict(res, result="BINARY_NOT_PUBLISHED")

    # 11 TBM
    if not flags.get("skip_tbm"):
        if tbm is None:
            return dict(res, result="BINARY_T0_UNVERIFIED", reason="tbm_missing")
        if tbm.get("lineage") != lineage:
            return dict(res, result="BINARY_T0_UNVERIFIED", reason="lineage")
        if tbm.get("source") != reg_src:
            return dict(res, result="BINARY_T0_UNVERIFIED", reason="source")
        if tbm.get("inputs_manifest_digest") != reg_inp:
            return dict(res, result="BINARY_T0_UNVERIFIED", reason="inputs")
        if tbm.get("build") != "release":
            return dict(res, result="BINARY_T0_UNVERIFIED", reason="build")

    # 12 accepted
    return dict(res, result="ACCEPTED", release_id=release_id,
                selected_state=res["selected_state"],
                reproducer_keys=sorted(counted),
                age_note="issued_at: %s" % tss_p.get("issued_at", ""))


def tcb_location_protected(path):
    uid = os.geteuid()
    cur = os.path.abspath(path)
    while True:
        try:
            st = os.stat(cur)
        except OSError:
            return False, cur
        if st.st_uid == uid or os.access(cur, os.W_OK):
            return False, cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return True, None
        cur = parent


def install_from_buffer(buf, dest, expected_digest, flags=None, source_path=None):
    """31 R-ADM-6: write the measured buffer (temporary file, fsync, atomic rename), then re-read the installed file and
    compare. Mutant `install_reread_path` (AR-0011 correction of the harness): install bytes re-read from the candidate's
    source path at install time instead of the measured buffer."""
    flags = flags or {}
    d = os.path.dirname(dest)
    os.makedirs(d, exist_ok=True)
    data = buf
    if flags.get("install_reread_path") and source_path:
        data = open(source_path, "rb").read()
    tmp = dest + ".gov-admit.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dest)
    rd = sha256d(open(dest, "rb").read())
    prot, wr = tcb_location_protected(dest)
    return {"installed": dest, "reread_digest": rd, "reread_equal": rd == expected_digest,
            "location_protected": prot, "first_writable_path": wr}


def write_admission_record(rec, rec_dir, lineage, flags=None):
    flags = flags or {}
    os.makedirs(rec_dir, exist_ok=True)
    vts = os.path.join(rec_dir, "vts-" + lineage[:16])
    moved = None
    if not flags.get("skip_fresh_vts") and os.path.isdir(vts):
        n = 0
        while os.path.exists(vts + ".pre-admission-%d" % n):
            n += 1
        dest = vts + ".pre-admission-%d" % n
        os.rename(vts, dest)
        moved = dest
    os.makedirs(vts, exist_ok=True)
    rp = os.path.join(vts, "admission-%s.json" % rec["binary_digest"][:24])
    with open(rp, "w") as f:
        json.dump(rec, f, sort_keys=True, indent=1)
    return rp, vts, moved


def load_admission_records(rec_dir, binary_digest):
    recs = []
    if not os.path.isdir(rec_dir):
        return recs
    for root, dirs, files in os.walk(rec_dir):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            try:
                r = json.load(open(os.path.join(root, fn)))
                if r.get("binary_digest") == binary_digest:
                    recs.append((r, os.path.join(root, fn)))
            except Exception:
                continue
    return recs


def gov_run(exe_path, action, rec_dir, now, negatives_held, scope, flags=None):
    flags = flags or {}
    if flags.get("skip_genuine_binary_rule"):
        return {"result": "ALLOWED", "action": action}
    own = sha256d(open(exe_path, "rb").read())
    base = {"action": action, "own_digest": own}
    if action == "C0":
        return dict(base, result="ALLOWED")
    recs = load_admission_records(rec_dir, own)
    if not recs:
        return dict(base, result="BINARY_NOT_ADMITTED")
    valid = [(r, p) for r, p in recs if r.get("valid_until") is None or r["valid_until"] >= now]
    if not valid and not flags.get("skip_record_expiry"):
        return dict(base, result="ADMISSION_RECORD_EXPIRED")
    if not valid:
        valid = recs
    if not flags.get("skip_self_revocation") and own in set(negatives_held):
        if scope == "C0_only":
            return dict(base, result="BINARY_REVOKED_SELF", scope=scope)
        if scope == "C0_C2" and action in ("C3", "confirm-root", "confirm-state", "trust-gate-confirm"):
            return dict(base, result="BINARY_REVOKED_SELF", scope=scope)
    if action in ("C3", "confirm-root", "confirm-state", "trust-gate-confirm"):
        if not flags.get("skip_record_protection"):
            eok, ew = tcb_location_protected(exe_path)
            if not eok:
                return dict(base, result="TCB_WRITABLE_BY_GOVERNED_ACCOUNT", writable=ew)
            _, rp = valid[0]
            rok, rw = tcb_location_protected(rp)
            if not rok:
                return dict(base, result="TCB_WRITABLE_BY_GOVERNED_ACCOUNT", writable=rw)
    return dict(base, result="ALLOWED")


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fingerprint", action="append", required=True)
    ap.add_argument("--statements", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--evaluator-digest")
    ap.add_argument("--install")
    ap.add_argument("binary")
    a = ap.parse_args(argv)
    data = open(a.binary, "rb").read()
    ed = a.evaluator_digest or sha256d(open(os.path.realpath(__file__), "rb").read())
    stmts = load_statements(a.statements)
    r = accept(data, a.fingerprint, stmts, a.target, ed, workdir=os.environ.get("TMPDIR"))
    if a.install and r["result"] == "ACCEPTED":
        r["install"] = install_from_buffer(data, a.install, r["binary_digest"])
    print(json.dumps(r, indent=1, sort_keys=True))
    return 0 if r["result"] == "ACCEPTED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
