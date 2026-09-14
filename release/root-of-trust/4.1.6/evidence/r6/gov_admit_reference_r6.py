#!/usr/bin/env python3
"""gov-admit reference, revision 6 — admission-predicate/1 bootstrap executor and first-contact procedure (AR-0015).

EVIDENCE ONLY. Not the implementation. Derived from `evidence/r5/gov_admit_reference.py` (AR-0011, which adapted specialist A
`gov_accept_reference.py` and specialist B `F2-first-tcb-admission.py`); that file is kept unmodified as history. Statement
shapes stay those of revision 5 (payloadType prefix `application/vnd.rot1r5.`), so the FA5 statement builders remain usable.

Revision-6 rules implemented here (normative text: `32`, `31`, `25` §5, `30`, `34`):
  FC-1…FC-3  first-contact procedure with platform tools only (sha256sum, openssl): the typed first-contact codes agree, the
             first-contact manifest hashes to the code, the admitter's digest is the one the manifest names; under OP-13 (c)
             the platform code signature also verifies (`fc_procedure`).
  FC-4       compiled first-contact quorum: the number of agreeing typed values is checked against a compiled minimum,
             never against a value the typed value selects; the selected Trust Policy may only raise it.
  FC-5       the first-contact manifest is bound by the typed code (digest) and is the only selector of lineage, state and
             evaluator list.
  FC-6       lineage from the typed value, never from bundle order (RV5-L1 / CR5-B-06).
  FC-7       compiled lineage under OP-13 (c) and (d).
  FC-8       evaluator binding: the admitter's own digest is listed by the selected Trust Policy, is not revoked in the
             selected Trust State, and the manifest's admitter set equals that list.
  AP-4       the binary, its registration, the registered final and the registered candidate are not revoked; binary version
             >= eligibility.min_binary_version, fail closed when the TBM carries no version (RV5-M9 R1, R2, R4).
  AP-5       attestations count only for exactly the registered candidate and the registered kernel tree digest; the
             registered final is promoted from the registered candidate and carries the registered kernel tree (R-CON-2,
             RV5-M9 R3).
  AP-5r      restrictors (a REJECTED attestation, a conflicting reproduction) are removed only by a revocation issued under
             the registration authority; a trust-state revocation lowers positive counts only (CR5-B-01).
  KS-14      root threshold >= 2 on every root version (CR5-B-11).
  R-ADM-8′   the verifier trust store is moved aside only at first admission (no store, or no admission record ever written
             in it); re-admission keeps it; one record per binary, so an earlier binary's record survives (CR5-B-03).
  R-ADM-13   admission-record writes hold an exclusive lock on the record directory, so concurrent admissions never move aside
             a store that already holds a record (RV5-C-A11).
  GB-1′      records are honoured only inside the store directory for the lineage, never found by walking, never beside the
             binary (CR5-B-07); an effective uid of 0 is writable for every path (CR5-B-12).
Every rule has a `flags` switch that reverts it to the revision-5 behaviour, for mutation analysis.
Verification: platform OpenSSL CLI (openssl pkeyutl -verify -rawin), cached per (key, message digest, signature).
"""
import fcntl
import base64, hashlib, json, os, subprocess, sys, tempfile

sys.dont_write_bytecode = True

TYPE_PREFIX = "application/vnd.rot1r5."
TYPE_PURPOSE = {
    TYPE_PREFIX + "root+json": "root",
    TYPE_PREFIX + "trust-policy+json": "trust-policy",
    TYPE_PREFIX + "trust-state+json": "trust-state",
    TYPE_PREFIX + "release-registration+json": "release-registration",
    TYPE_PREFIX + "registration-revocation+json": "release-registration",
    TYPE_PREFIX + "binary-reproduction+json": "reproducer",
    TYPE_PREFIX + "verification-attestation+json": "verification-attestation",
    TYPE_PREFIX + "release-final+json": "release-final",
    TYPE_PREFIX + "release-candidate+json": "release-candidate",
}
COMPILED_MIN = {"root": 2, "trust-policy": 2, "release-registration": 2, "reproducer": 2}
# Compiled first-contact constants of an admitter build (the owner's OP-13 answer is registered source). Harnesses set them per
# option: channel_quorum 1 (OP-13 (a)) or 2 (b); lineage set under (c)/(d); compiled_fcm under (c)-either path-only admission.
COMPILED = {"channel_quorum": 1, "lineage": None, "compiled_fcm": None}
ED25519_SPKI_PREFIX = bytes.fromhex("302a300506032b6570032100")
PLATFORM_SIGNATURE_TYPE = "application/vnd.platform-code-signature"


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


# ------------------------------------------------------------------------------------------------ first-contact manifest (32 §3)
def make_fcm(lineage, root_v, root_d, pol_v, pol_d, seq, state_d, admitters, issued_at, valid_until=None):
    m = {"schema": "governance-os.first-contact-manifest/1", "lineage_id": lineage,
         "state_epoch": {"root_version": root_v, "root_digest": root_d, "policy_version": pol_v, "policy_digest": pol_d,
                         "state_sequence": seq, "state_digest": state_d},
         "admitters": dict(sorted(admitters.items())), "issued_at": issued_at}
    if valid_until is not None:
        m["valid_until"] = valid_until
    return m


def fcm_bytes(m):
    return canon(m)


def first_contact_code(m):
    return "gov-fc:%s:%d:%s" % (m["lineage_id"][7:15], m["state_epoch"]["state_sequence"], hashlib.sha256(canon(m)).hexdigest())


class Verifier:
    def __init__(self, workdir):
        self.w = tempfile.mkdtemp(prefix="v6-", dir=workdir)
        self.cache = {}
        self.calls = 0

    def verify(self, pub_raw, msg, sig):
        k = (pub_raw, hashlib.sha256(msg).digest(), sig)
        if k in self.cache:
            return self.cache[k]
        self.calls += 1
        pem = (b"-----BEGIN PUBLIC KEY-----\n" + base64.encodebytes(ED25519_SPKI_PREFIX + pub_raw) + b"-----END PUBLIC KEY-----\n")
        n = len(self.cache)
        pp, pm, ps = (os.path.join(self.w, "%d.%s" % (n, x)) for x in ("pem", "msg", "sig"))
        for path, data in ((pp, pem), (pm, msg), (ps, sig)):
            with open(path, "wb") as f:
                f.write(data)
        r = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", pp, "-rawin", "-in", pm, "-sigfile", ps],
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
        out.append({"file": fn, "type": pt, "purpose": purpose, "body": body, "payload": payload, "digest": sha256d(body),
                    "sigs": env.get("signatures", [])})
    return out


def compute_key_id(pub_raw):
    return "ed25519:" + hashlib.sha256(pub_raw).hexdigest()


def valid_signers(ver, stmt, root_pl, chain_revoked, flags=None):
    flags = flags or {}
    keys_map = root_pl.get("keys", {})
    msg = pae(stmt["type"], stmt["body"])
    ok, seen = set(), set()
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
    if not flags.get("skip_min_root_threshold"):
        if grants.get("root", {}).get("threshold", 0) < 2:          # KS-14 (CR5-B-11)
            return False, "root_th<2"
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


def root_v1_candidates(ver, roots, flags):
    """Every well-formed, self-verifying root v1 held, in bundle order. FC-6: the lineage is then chosen by the typed value."""
    out = []
    for r in roots:
        if r["payload"].get("version") != 1:
            continue
        if not root_well_formed(r["payload"], flags)[0]:
            continue
        if meets_purpose(ver, r, r["payload"], "root", set(r["payload"].get("revoked_keys", [])), flags)[0]:
            out.append(r)
    return out


def build_root_chain_from(ver, roots, r1, flags):
    by_v = {}
    for r in roots:
        if not root_well_formed(r["payload"], flags)[0]:
            continue
        vv = r["payload"].get("version")
        if isinstance(vv, int) and vv > 1:
            by_v.setdefault(vv, []).append(r)
    chain = {1: r1}
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
            if meets_purpose(ver, r, prev["payload"], "root", test_rev, flags)[0] and meets_purpose(ver, r, r["payload"], "root", test_rev, flags)[0]:
                chain[n] = r
                break
        if n not in chain:
            break
        n += 1
    return chain


def parse_tbm(binary_bytes):
    text = binary_bytes.decode("utf-8", errors="replace")
    for line in text.split("\n"):
        if line.startswith("# GOV-TBM "):
            try:
                tbm = json.loads(line[len("# GOV-TBM "):])
                return tbm, sha256d(canon(tbm))
            except Exception:
                return None, None
    return None, None


def semver_tuple(v):
    try:
        return tuple(int(x) for x in str(v).split("-")[0].split("+")[0].split("."))
    except Exception:
        return None


def refuse(res, code, **kw):
    out = dict(res, result=code)
    out.update(kw)
    return out


def accept(binary_bytes, typed_values, statements, target, evaluator_digest, flags=None, verifier=None, workdir=None,
           first_contact_manifest=None, compiled=None, now=None):
    """admission-predicate/1, bootstrap mode (25 §5; 31 §4; 32). typed_values are first-contact codes when a first-contact
    manifest is given (revision-6 procedure), otherwise typed state fingerprints (the revision-5 input shape, kept for the
    shared vectors). The number of typed values is the number of first-contact sources the operator typed from."""
    flags = flags or {}
    comp = dict(COMPILED)
    comp.update(compiled or {})
    v = verifier or Verifier(workdir or tempfile.gettempdir())
    D = sha256d(binary_bytes)
    res = {"binary_digest": D, "target": target, "candidate_executed": False,
           "mode": "first-contact-manifest" if first_contact_manifest is not None else "state-fingerprint"}

    # AP-0 self-evaluation
    if not flags.get("allow_self_evaluation") and evaluator_digest == D:
        return refuse(res, "SELF_EVALUATION_REFUSED")

    # AP-1 agreement and FC-4 compiled first-contact quorum (never read from what the values select)
    if not typed_values:
        return refuse(res, "CHANNEL_QUORUM_NOT_MET", counted=0, quorum=comp["channel_quorum"])
    if not flags.get("skip_channel_agreement") and len(set(typed_values)) != 1:
        return refuse(res, "CHANNEL_DISAGREEMENT")
    k_typed = len(typed_values)
    if not flags.get("quorum_from_selected_state") and not flags.get("skip_channel_quorum") and k_typed < comp["channel_quorum"]:
        return refuse(res, "CHANNEL_QUORUM_NOT_MET", counted=k_typed, quorum=comp["channel_quorum"], source="compiled")
    typed = typed_values[0]

    # FC-5 first-contact manifest bound by the typed code; FC-7 compiled lineage
    fcm = None
    if first_contact_manifest is not None:
        mb = first_contact_manifest if isinstance(first_contact_manifest, (bytes, bytearray)) else canon(first_contact_manifest)
        try:
            fcm = json.loads(mb)
        except Exception:
            return refuse(res, "FIRST_CONTACT_MANIFEST_MALFORMED")
        if canon(fcm) != bytes(mb):
            return refuse(res, "FIRST_CONTACT_MANIFEST_MALFORMED")
        if not flags.get("skip_fcm_digest_check") and first_contact_code(fcm) != typed:
            return refuse(res, "FIRST_CONTACT_MANIFEST_MISMATCH")
        if comp.get("lineage") and not flags.get("skip_compiled_lineage") and fcm.get("lineage_id") != comp["lineage"]:
            return refuse(res, "FIRST_CONTACT_LINEAGE_NOT_COMPILED")
        if fcm.get("valid_until") is not None and now is not None and now > fcm["valid_until"]:
            return refuse(res, "FIRST_CONTACT_MANIFEST_EXPIRED")

    # AP-2 lineage (FC-6): from the typed value, never from bundle order
    roots = [s for s in statements if s["purpose"] == "root"]
    cands = root_v1_candidates(v, roots, flags)
    if flags.get("lineage_from_bundle_order"):
        cands = cands[:1]
    if fcm is not None:
        cands = [r for r in cands if r["digest"] == fcm.get("lineage_id")]
    elif comp.get("lineage") and not flags.get("skip_compiled_lineage"):
        cands = [r for r in cands if r["digest"] == comp["lineage"]]
    if not cands:
        return refuse(res, "ROOT_CHAIN_INVALID")

    # AP-3 select the Trust State
    selected = None
    for r1 in cands:
        chain = build_root_chain_from(v, roots, r1, flags)
        lineage = r1["digest"]
        chain_revoked = set()
        if not flags.get("ignore_signer_revocation"):
            for cv in chain.values():
                chain_revoked |= set(cv["payload"].get("revoked_keys", []))
        for t in (s for s in statements if s["purpose"] == "trust-state"):
            p = t["payload"]
            rr = p.get("references", {}).get("root", {})
            rp_ = p.get("references", {}).get("trust_policy", {})
            rv, rd, pv, pd = rr.get("version"), rr.get("digest"), rp_.get("version"), rp_.get("digest")
            if rv not in chain or chain[rv]["digest"] != rd:
                continue
            pol = next((s for s in statements if s["purpose"] == "trust-policy" and s["digest"] == pd), None)
            if pol is None:
                continue
            eff = chain[rv]["payload"]
            if not (meets_purpose(v, t, eff, "trust-state", chain_revoked, flags)[0] and meets_purpose(v, pol, eff, "trust-policy", chain_revoked, flags)[0]):
                continue
            if fcm is not None:
                ep = fcm.get("state_epoch", {})
                match = (ep.get("root_version"), ep.get("root_digest"), ep.get("policy_version"), ep.get("policy_digest"), ep.get("state_sequence"), ep.get("state_digest")) == \
                        (rv, rd, pv, pd, p.get("sequence", 0), t["digest"])
            else:
                match = state_fingerprint(lineage, rv, rd, pv, pd, p.get("sequence", 0), t["digest"]) == typed
            if not flags.get("any_state") and not match:
                continue
            if selected is None or p.get("sequence", 0) > selected[0]["payload"].get("sequence", 0):
                selected = (t, pol, eff, lineage, chain_revoked)
    if selected is None:
        return refuse(res, "STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")
    tss, tps, eff_root, lineage, chain_revoked = selected
    tss_p, tps_p = tss["payload"], tps["payload"]
    res["lineage"] = lineage
    res["selected_state"] = {"sequence": tss_p.get("sequence"), "digest": tss["digest"], "issued_at": tss_p.get("issued_at")}

    boot = tps_p.get("bootstrap", {})
    tps_q = boot.get("channel_quorum", 1)
    if not flags.get("skip_channel_quorum") and tps_q > k_typed:           # the Trust Policy can only raise the compiled minimum
        return refuse(res, "CHANNEL_QUORUM_NOT_MET", counted=k_typed, quorum=tps_q, source="trust_policy")

    N = set(tss_p.get("revocations", []))
    # FC-8 evaluator binding
    listed = set(boot.get("admitter_digests", []) or []) | set(tps_p.get("admitter_digests", []) or [])
    if not flags.get("skip_evaluator_binding"):
        if evaluator_digest not in listed:
            return refuse(res, "ADMITTER_NOT_LISTED")
        if evaluator_digest in N:
            return refuse(res, "ADMITTER_REVOKED")
        if fcm is not None and not flags.get("skip_fcm_consistency"):
            fa = fcm.get("admitters", {})
            if set(fa.values() if isinstance(fa, dict) else fa) != listed:
                return refuse(res, "FIRST_CONTACT_MANIFEST_INCONSISTENT")

    # AP-5r restrictor revocations: only under the registration authority
    RA = set()
    for s in statements:
        if s["type"] == TYPE_PREFIX + "registration-revocation+json":
            if meets_purpose(v, s, eff_root, "release-registration", chain_revoked, flags)[0]:
                RA |= set(s["payload"].get("revokes", []))

    def alive(s):
        return flags.get("skip_revocation") or (s["digest"] not in N and s["digest"] not in RA)

    def restrictor_alive(s):
        if flags.get("trust_state_revokes_restrictors"):
            return alive(s)
        return s["digest"] not in RA

    # AP-4 binary negative
    if not flags.get("skip_revocation") and D in N:
        return refuse(res, "BINARY_REVOKED", reason="binary")

    # reproductions
    rep_grant = eff_root.get("grants", {}).get("reproducer")
    R_restr, R_count = [], []
    for s in statements:
        if s["purpose"] != "reproducer" or s["type"] != TYPE_PREFIX + "binary-reproduction+json" or not rep_grant:
            continue
        signers = valid_signers(v, s, eff_root, chain_revoked, flags) & set(rep_grant["keys"])
        if flags.get("multi_signer_counts"):
            if len(signers) < 1:
                continue
        elif len(signers) != 1:
            continue
        row = {"s": s, "p": s["payload"], "signers": signers, "digest": s["digest"]}
        if restrictor_alive(s):
            R_restr.append(row)
        if alive(s):
            R_count.append(row)
    R_mine = [r for r in R_count if r["p"].get("binary_digest") == D and r["p"].get("target") == target]

    # AP-5 registration
    rids_mine = {r["p"].get("release_id") for r in R_mine}
    all_vr = [s for s in statements if s["type"] == TYPE_PREFIX + "release-registration+json" and meets_purpose(v, s, eff_root, "release-registration", chain_revoked, flags)[0]]
    tss_regs = set(tss_p.get("registrations", []))
    cands_r = [s for s in all_vr if (flags.get("skip_registration_reference") or s["digest"] in tss_regs) and s["payload"].get("release_id") in rids_mine]
    if not cands_r:
        return refuse(res, "RELEASE_UNREGISTERED")
    if not flags.get("skip_registration_equivocation"):
        by_rid = {}
        for s in all_vr:
            by_rid.setdefault(s["payload"].get("release_id"), set()).add(s["digest"])
        for rid, ds in by_rid.items():
            if len(ds) > 1:
                return refuse(res, "REGISTRATION_EQUIVOCATION", release_id=rid)
    reg, fail, final_stmt = None, None, None
    for cr in cands_r:
        cp = cr["payload"]
        if target not in cp.get("targets", []):
            fail = "TARGET_NOT_REGISTERED"
            continue
        if not flags.get("skip_final_restrictor"):
            fd = cp.get("final_statement_digest")
            fs = next((s for s in statements if s["purpose"] == "release-final" and s["digest"] == fd), None)
            if fs is None or not meets_purpose(v, fs, eff_root, "release-final", chain_revoked, flags)[0]:
                fail = "RELEASE_FINAL_UNVERIFIED"
                continue
            fp = fs["payload"]
            if fp.get("source") != cp.get("source") or fp.get("promoted_from") != cp.get("candidate_statement_digest"):
                fail = "RELEASE_FINAL_UNVERIFIED"
                continue
            if not flags.get("skip_kernel_binding") and fp.get("kernel_tree_digest") != (cp.get("constitution") or {}).get("kernel_tree_digest"):
                fail = "RELEASE_FINAL_UNVERIFIED"
                continue
            final_stmt = fs
        reg = cr
        break
    if reg is None:
        return refuse(res, fail or "RELEASE_UNREGISTERED")
    rp = reg["payload"]
    release_id = rp.get("release_id")
    res["release_id"] = release_id
    cand_d = rp.get("candidate_statement_digest")
    reg_kernel = (rp.get("constitution") or {}).get("kernel_tree_digest")
    if not flags.get("skip_kernel_binding") and not reg_kernel:
        return refuse(res, "REGISTRATION_MALFORMED", reason="constitution.kernel_tree_digest")

    # AP-4 registration, registered final and registered candidate not revoked
    if not flags.get("skip_revocation") and not flags.get("skip_final_candidate_revocation"):
        if reg["digest"] in N:
            return refuse(res, "BINARY_REVOKED", reason="registration")
        if rp.get("final_statement_digest") in N:
            return refuse(res, "BINARY_REVOKED", reason="registered_final")
        if cand_d in N:
            return refuse(res, "BINARY_REVOKED", reason="registered_candidate")

    # AP-4 binary floor
    tbm, tbm_dig = parse_tbm(binary_bytes)
    mbv = (tps_p.get("eligibility") or {}).get("min_binary_version")
    if mbv and not flags.get("skip_min_binary_version"):
        bv = semver_tuple((tbm or {}).get("version")) if tbm else None
        if bv is None or bv < (semver_tuple(mbv) or (0,)):
            return refuse(res, "BINARY_BELOW_TRUST_POLICY", minimum=mbv, binary_version=(tbm or {}).get("version"))

    # AP-5 verification records bound to the registered candidate and kernel tree; REJECTED restrictor
    if not flags.get("skip_rejected"):
        for s in statements:
            if s["purpose"] != "verification-attestation" or not restrictor_alive(s):
                continue
            sp = s["payload"]
            if sp.get("candidate_statement_digest") != cand_d or sp.get("verdict") != "REJECTED":
                continue
            if meets_purpose(v, s, eff_root, "verification-attestation", chain_revoked, flags)[0]:
                return refuse(res, "ARTIFACT_SOURCE_REJECTED")
    if not flags.get("skip_verification_records"):
        vr_set = set(rp.get("verification_records", []))
        vkeys = set()
        for s in statements:
            if s["purpose"] != "verification-attestation" or not alive(s):
                continue
            sp = s["payload"]
            if s["digest"] not in vr_set or sp.get("verdict") != "ACCEPTED":
                continue
            if not flags.get("skip_source_equality") and (sp.get("source") != rp.get("source") or sp.get("inputs_manifest_digest") != rp.get("inputs_manifest_digest")):
                continue
            if not flags.get("skip_candidate_binding") and sp.get("candidate_statement_digest") != cand_d:
                continue
            if not flags.get("skip_kernel_binding") and sp.get("kernel_tree_digest") != reg_kernel:
                continue
            ok_va, sk = meets_purpose(v, s, eff_root, "verification-attestation", chain_revoked, flags)
            if ok_va:
                vkeys |= sk
        minv = max(1, (tps_p.get("registration") or {}).get("min_verification_records", 1))
        if len(vkeys) < minv:
            return refuse(res, "VERIFICATION_RECORDS_BELOW_MINIMUM", counted=len(vkeys), minimum=minv)

    # AP-6 reproduction quorum and conflict
    reg_src, reg_inp = rp.get("source"), rp.get("inputs_manifest_digest")
    g_th = rep_grant.get("threshold", 2) if rep_grant else 2
    quorum = 1 if flags.get("quorum_one") else max(2, (tps_p.get("registration") or {}).get("reproduction_quorum", 2), g_th)
    counted = set()
    for r in R_mine:
        rpp = r["p"]
        if rpp.get("release_id") != release_id:
            continue
        if not flags.get("skip_source_equality") and (rpp.get("source") != reg_src or rpp.get("inputs_manifest_digest") != reg_inp):
            continue
        if not flags.get("skip_tbm") and rpp.get("tbm_digest") != tbm_dig:
            continue
        if flags.get("count_statements_not_keys"):
            counted.add(r["digest"])
        else:
            counted |= r["signers"]
    res["reproducer_keys"] = sorted(counted)
    if len(counted) < quorum:
        return refuse(res, "REPRODUCTION_QUORUM_NOT_MET", counted=len(counted), quorum=quorum)
    if not flags.get("skip_conflict"):
        for r in R_restr:
            rpp = r["p"]
            if rpp.get("release_id") == release_id and rpp.get("target") == target and rpp.get("binary_digest") != D:
                return refuse(res, "REPRODUCTION_CONFLICT", conflicting=rpp.get("binary_digest"))
    if "binary_digests" in rp and rp["binary_digests"].get(target) not in (None, D):
        return refuse(res, "BINARY_NOT_REGISTERED")

    # AP-7 publication
    if not flags.get("skip_published") and D not in set(tss_p.get("published_binaries", [])):
        return refuse(res, "BINARY_NOT_PUBLISHED")

    # AP-8 TBM
    if not flags.get("skip_tbm"):
        if tbm is None:
            return refuse(res, "BINARY_T0_UNVERIFIED", reason="tbm_missing")
        for field, want in (("lineage", lineage), ("source", reg_src), ("inputs_manifest_digest", reg_inp)):
            if tbm.get(field) != want:
                return refuse(res, "BINARY_T0_UNVERIFIED", reason=field)
        if tbm.get("build") != "release":
            return refuse(res, "BINARY_T0_UNVERIFIED", reason="build")

    return dict(res, result="ACCEPTED", release_id=release_id, reproducer_keys=sorted(counted), age_note="issued_at: %s" % tss_p.get("issued_at", ""))


# ------------------------------------------------------------------------------------------------ FC-1…FC-3: operator procedure with platform tools only
def platform_sha256(data, workdir):
    """The platform hash tool (TA-1b): `sha256sum` over a file holding the bytes."""
    os.makedirs(workdir, exist_ok=True)
    p = os.path.join(workdir, "fc-" + hashlib.sha256(data).hexdigest()[:20])
    if not os.path.exists(p):
        with open(p, "wb") as f:
            f.write(data)
    r = subprocess.run(["sha256sum", p], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    return "sha256:" + r.stdout.split()[0]


def fc_procedure(pages, manifest_bytes, admitter_bytes, target, procedure_sources, workdir, verifier=None,
                 platform_pub=None, platform_signature=None, require_platform_signature=False, channel_path=True):
    """32 §4. `pages`: the first-contact codes the operator actually read, one per consulted source. `procedure_sources` is the
    number of sources the owner's OP-13 answer names; it binds the operator (TA-5) and cannot be enforced by code before an
    evaluator is selected. Under OP-13 (c) the platform code signature over the admitter bytes is verified as well
    (`require_platform_signature`); under (c)-either with `channel_path=False` only the platform path is used."""
    steps = {}
    if require_platform_signature or (platform_pub is not None and not channel_path):
        ok = platform_pub is not None and platform_signature is not None and verifier is not None and \
            verifier.verify(platform_pub, pae(PLATFORM_SIGNATURE_TYPE, admitter_bytes), platform_signature)
        steps["platform_signature"] = ok
        if not ok:
            return {"result": "PLATFORM_SIGNATURE_INVALID", "steps": steps}
        if not channel_path:
            return {"result": "OK", "path": "platform-only", "admitter_digest": platform_sha256(admitter_bytes, workdir), "steps": steps}
    if len(pages) < procedure_sources:
        return {"result": "FIRST_CONTACT_SOURCES_BELOW_PROCEDURE", "steps": steps, "read": len(pages), "required": procedure_sources}
    if len(set(pages)) != 1:
        return {"result": "FIRST_CONTACT_DISAGREEMENT", "steps": steps}
    code_hash = "sha256:" + pages[0].rsplit(":", 1)[-1]
    mh = platform_sha256(manifest_bytes, workdir)
    steps["manifest_sha256"] = mh
    if mh != code_hash:
        return {"result": "FIRST_CONTACT_MANIFEST_MISMATCH", "steps": steps}
    m = json.loads(manifest_bytes)
    ad = platform_sha256(admitter_bytes, workdir)
    steps["admitter_sha256"] = ad
    if (m.get("admitters") or {}).get(target) != ad:
        return {"result": "ADMITTER_DIGEST_MISMATCH", "steps": steps}
    return {"result": "OK", "path": "channels" + ("+platform" if require_platform_signature else ""), "admitter_digest": ad, "manifest": m, "steps": steps}


# ------------------------------------------------------------------------------------------------ installation, records, genuine-binary rule
def tcb_location_protected(path):
    uid = os.geteuid()
    cur = os.path.abspath(path)
    if uid == 0:                                                        # CR5-B-12: an effective uid of 0 can write every path
        return False, cur
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
    """31 R-ADM-6 (unchanged): write the measured buffer (temporary file, fsync, atomic rename), re-read and compare."""
    flags = flags or {}
    os.makedirs(os.path.dirname(dest), exist_ok=True)
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
    return {"installed": dest, "reread_digest": rd, "reread_equal": rd == expected_digest, "location_protected": prot, "first_writable_path": wr}


def store_dir(rec_dir, lineage):
    return os.path.join(rec_dir, "vts-" + lineage[:16])


def is_first_admission(rec_dir, lineage):
    """31 R-ADM-8′: first admission iff no verifier trust store exists for the lineage, or no admission record was ever written
    in it."""
    st = store_dir(rec_dir, lineage)
    if not os.path.isdir(st):
        return True
    ad = os.path.join(st, "admissions")
    legacy = [f for f in os.listdir(st) if f.startswith("admission-") and f.endswith(".json")]
    return not legacy and not (os.path.isdir(ad) and any(f.endswith(".json") for f in os.listdir(ad)))


def write_admission_record(rec, rec_dir, lineage, flags=None):
    """Returns (record path, store path, moved-aside path or None). Revision 6: move-aside only at first admission; one record
    file per binary digest under `admissions/`, written atomically; earlier records are kept (rollback keeps them)."""
    flags = flags or {}
    os.makedirs(rec_dir, exist_ok=True)
    lock_fd = None
    if not flags.get("skip_admission_lock"):                            # R-ADM-13 (RV5-C-A11): one admission per record directory at a time
        lock_fd = os.open(os.path.join(rec_dir, ".gov-admit.lock"), os.O_CREAT | os.O_RDWR, 0o600)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        return _write_admission_record_locked(rec, rec_dir, lineage, flags)
    finally:
        if lock_fd is not None:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)


def _write_admission_record_locked(rec, rec_dir, lineage, flags):
    st = store_dir(rec_dir, lineage)
    first = is_first_admission(rec_dir, lineage)
    if flags.get("move_aside_every_run"):
        first = os.path.isdir(st)
    moved = None
    if first and os.path.isdir(st) and not flags.get("skip_fresh_vts"):
        n = 0
        while os.path.exists(st + ".pre-admission-%d" % n):
            n += 1
        moved = st + ".pre-admission-%d" % n
        os.rename(st, moved)
    ad = os.path.join(st, "admissions")
    os.makedirs(ad, exist_ok=True)
    rp = os.path.join(ad, rec["binary_digest"].replace(":", "-") + ".json")
    tmp = rp + ".tmp-%d" % os.getpid()
    with open(tmp, "w") as f:
        json.dump(rec, f, sort_keys=True, indent=1)
    os.replace(tmp, rp)
    return rp, st, moved


def load_admission_records(rec_dir, binary_digest, flags=None):
    """GB-1′ (CR5-B-07): only records inside a store directory `vts-<16 hex>` directly under the protected record directory are
    honoured (`admissions/<digest>.json`, or the revision-5 file name `admission-<digest prefix>.json` at the store top);
    a record elsewhere (beside the binary, shipped by a package, in a moved-aside store) is never read."""
    flags = flags or {}
    recs = []
    if not os.path.isdir(rec_dir):
        return recs
    if flags.get("record_anywhere"):                                    # revision-5 behaviour
        walk = []
        for root, dirs, files in os.walk(rec_dir):
            walk += [os.path.join(root, f) for f in files if f.endswith(".json")]
    else:
        walk = []
        for d in sorted(os.listdir(rec_dir)):
            st = os.path.join(rec_dir, d)
            if not (d.startswith("vts-") and len(d) == 20 and os.path.isdir(st)):
                continue
            walk += [os.path.join(st, f) for f in sorted(os.listdir(st)) if f.startswith("admission-") and f.endswith(".json")]
            ad = os.path.join(st, "admissions")
            if os.path.isdir(ad):
                walk += [os.path.join(ad, f) for f in sorted(os.listdir(ad)) if f.endswith(".json")]
    for p in walk:
        try:
            r = json.load(open(p))
            if r.get("binary_digest") == binary_digest:
                recs.append((r, p))
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
    recs = load_admission_records(rec_dir, own, flags)
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
