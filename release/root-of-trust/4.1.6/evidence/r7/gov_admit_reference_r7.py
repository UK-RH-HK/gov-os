#!/usr/bin/env python3
"""gov-admit and genuine-binary reference, revision 7, certified profile CP-1 (AR-0019).

EVIDENCE ONLY. Not the implementation. A new file: it does not import or modify `../r6/gov_admit_reference_r6.py` (kept as
history). Statement payloadType prefix `application/vnd.rot1r7.`. Real Ed25519 verification through the platform OpenSSL CLI;
the platform hash tool `sha256sum` for the operator procedure.

Certified-profile constants are COMPILED below and have no switch. `flags` exist only to revert one revision-7 rule at a time
to the revision-6 behaviour, for mutation analysis (`FA7` S7, `CUR7`, `ADM7`); a flag never enables an excluded mode.

Rules (normative text in `32`, `31`, `25` §5, `30`, `33`, `35`):
  FC-1′…FC-3′  operator procedure with platform tools: two trust codes, two state codes and two procedure digests read from the
               two designated sources agree; the first-contact authority payload hashes to the trust code; the admitter's
               SHA-256 is the one that payload lists for a certified target.
  FC-4′        compiled first-contact quorum 2 (never read from any statement).
  FC-5′        the first-contact authority record (FCA) is the statement whose digest is the typed trust code; it verifies at root
               threshold under the compiled lineage (FC-7′: lineage compiled into every admitter build).
  FC-6         lineage from the compiled value; bundle order never matters.
  FC-8′        the evaluator's own digest is listed by the FCA for the target, the target is certified, and the admitter is not
               revoked in the selected state or in held state.
  AP-3′        the selected Trust State is the statement whose digest is the typed state code; it verifies at the trust-state
               threshold (2), names the FCA and a Trust Policy at root threshold; its age is at most 24 h (FC-9, compiled).
  AP-R1…R6     re-admission applies the store: never a state, root, policy or FCA below held; never a candidate or admitter
               held revoked; never a TBM below the accepted-TBM high-water; never a release below the held security minimum.
  AP-4         negatives (binary, release, registration, final, candidate); revocation statements at the revocation threshold
               or root threshold; binary version floor.
  AP-5         registration at 2-of-3 referenced by the state; final at threshold 2, promoted from the registered candidate,
               kernel binding; REJECTED restrictor; >= 2 ACCEPTED attestations with distinct keys, executions and reports,
               bound to candidate, source, inputs, kernel and the registered environments.
  AP-SEC       computed security minimum (OP-11 (b)).
  AP-6         >= 2 distinct reproducer keys; registered environment and toolchain; matching reproductions span >= 2 independent
               supplier classes and >= 2 independent toolchain lineages (independence computed from the Trust Policy registry);
               conflict refuses; digest equals the registered binary digest (OP-9 (d)).
  AP-7, AP-8   publication; TBM (profile id, lineage, source, inputs, build) at or above the accepted-TBM high-water.
  R-STORE      two stores: the protected admission store decides first admission; the account verifier trust store never does;
               first admission moves the account store for the lineage aside; admissions are serialised.
  GB-1″…GB-6   records honoured only in the protected store and only when their admitter is listed; expiry; revoked self is
               C0-R; R-ART-2 accepted-TBM high-water at use; TCB location for C3 and ceremonies; decision rule of OP-7 (a).
"""
import base64, fcntl, hashlib, json, os, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone

sys.dont_write_bytecode = True

PROFILE_ID = "governance-os.rot1/CP-1"
TYPE_PREFIX = "application/vnd.rot1r7."
TYPE_PURPOSE = {
    TYPE_PREFIX + "root+json": "root",
    TYPE_PREFIX + "trust-policy+json": "trust-policy",
    TYPE_PREFIX + "first-contact-authority+json": "first-contact-authority",
    TYPE_PREFIX + "trust-state+json": "trust-state",
    TYPE_PREFIX + "revocation+json": "revocation",
    TYPE_PREFIX + "release-registration+json": "release-registration",
    TYPE_PREFIX + "registration-revocation+json": "release-registration",
    TYPE_PREFIX + "binary-reproduction+json": "reproducer",
    TYPE_PREFIX + "verification-attestation+json": "verification-attestation",
    TYPE_PREFIX + "release-final+json": "release-final",
}
# ---- compiled CP-1 constants (no switch) ---------------------------------------------------------------------------------------
PURPOSE_SHAPE = {  # purpose -> (exact key count or None, minimum threshold)
    "root": (3, 2), "trust-policy": (None, 2), "first-contact-authority": (None, 2), "release-registration": (3, 2), "trust-state": (3, 2),
    "revocation": (3, 2), "reproducer": (3, 1), "verification-attestation": (None, 1), "release-final": (None, 2), "release-candidate": (None, 1),
    "certification-status": (None, 2), "retrieval-profile": (None, 1)}
WHITELIST = {frozenset(("root", "trust-policy")), frozenset(("root", "first-contact-authority")), frozenset(("trust-policy", "first-contact-authority"))}
FIRST_CONTACT_QUORUM = 2
ADMISSION_STATE_MAX_AGE = timedelta(hours=24)
RECORD_VALIDITY = {"workstation": timedelta(days=90), "ci-image": timedelta(days=7)}
ANCHOR_VALIDITY = {"workstation": timedelta(days=90), "ci-image": timedelta(days=7)}
C3_CURRENCY = timedelta(hours=24)
MIN_VERIFICATION_RECORDS = 2
REPRODUCTION_QUORUM = 2
CLOCK_SKEW = timedelta(seconds=300)
METADATA_AGE_WARNING_DAYS = 30        # OP-5: used only by `display_age_warning`; no decision reads it
ED25519_SPKI_PREFIX = bytes.fromhex("302a300506032b6570032100")
C0_R = ("version", "doctor", "status", "kernel-trust-report", "trust-show")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256d(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def pae(ptype, body):
    t = ptype.encode()
    return b"DSSEv1 %d %s %d %s" % (len(t), t, len(body), body)


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def trust_code(lineage, fca_seq, fca_digest):
    return "gov-fct:%s:%d:%s" % (lineage[7:15], fca_seq, fca_digest.split(":", 1)[1])


def state_code(lineage, seq, tss_digest):
    return "gov-fcs:%s:%d:%s" % (lineage[7:15], seq, tss_digest.split(":", 1)[1])


def code_hash(code):
    return "sha256:" + code.rsplit(":", 1)[-1]


def display_age_warning(issued_at, now):
    """OP-5: informational text only."""
    age = ts(now) - ts(issued_at)
    return "trust metadata is %d days old" % age.days if age.days >= METADATA_AGE_WARNING_DAYS else None


class Verifier:
    def __init__(self, workdir):
        self.w = tempfile.mkdtemp(prefix="v7-", dir=workdir)
        self.cache = {}
        self.calls = 0

    def verify(self, pub_raw, msg, sig):
        k = (pub_raw, hashlib.sha256(msg).digest(), sig)
        if k in self.cache:
            return self.cache[k]
        self.calls += 1
        pem = b"-----BEGIN PUBLIC KEY-----\n" + base64.encodebytes(ED25519_SPKI_PREFIX + pub_raw) + b"-----END PUBLIC KEY-----\n"
        n = len(self.cache)
        pp, pm, ps = (os.path.join(self.w, "%d.%s" % (n, x)) for x in ("pem", "msg", "sig"))
        for path, data in ((pp, pem), (pm, msg), (ps, sig)):
            with open(path, "wb") as f:
                f.write(data)
        r = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", pp, "-rawin", "-in", pm, "-sigfile", ps], capture_output=True, text=True)
        ok = r.returncode == 0 and "Successfully" in r.stdout
        self.cache[k] = ok
        return ok


def parse_envelope(env):
    try:
        body = base64.b64decode(env["payload"], validate=True)
        payload = json.loads(body)
    except Exception:
        return None
    pt = env.get("payloadType", "")
    purpose = TYPE_PURPOSE.get(pt)
    if purpose is None or canon(payload) != body:
        return None
    return {"type": pt, "purpose": purpose, "body": body, "payload": payload, "digest": sha256d(body), "sigs": env.get("signatures", [])}


def key_id(pub_raw):
    return "ed25519:" + hashlib.sha256(pub_raw).hexdigest()


def signers(ver, stmt, root_pl, revoked, flags):
    keys = root_pl.get("keys", {})
    msg = pae(stmt["type"], stmt["body"])
    ok, seen = set(), set()
    for s in stmt["sigs"]:
        kid = s.get("keyid")
        if kid in seen or kid not in keys or (kid in revoked and not flags.get("ignore_signer_revocation")):
            continue
        seen.add(kid)
        try:
            pub = base64.b64decode(keys[kid])
            sig = base64.b64decode(s["sig"], validate=True)
        except Exception:
            continue
        if key_id(pub) == kid and ver.verify(pub, msg, sig):
            ok.add(kid)
    return ok


def meets(ver, stmt, root_pl, purpose, revoked, flags):
    g = root_pl.get("grants", {}).get(purpose)
    if not g:
        return False, set()
    s = signers(ver, stmt, root_pl, revoked, flags) & set(g["keys"])
    minimum = PURPOSE_SHAPE.get(purpose, (None, 1))[1]
    if flags.get("trust_state_threshold_1") and purpose == "trust-state":
        return len(s) >= 1, s                                          # mutant: the revision-6 single trust-state key
    return len(s) >= max(g["threshold"], minimum), s


def root_conforms(root_pl, flags):
    """KS rules of `05` §3 for CP-1: exact shapes, single-purpose keys, the reduced whitelist, no excluded purpose."""
    g = root_pl.get("grants", {})
    if root_pl.get("profile_id") != PROFILE_ID:
        return False, "profile_id"
    for p in g:
        if p not in PURPOSE_SHAPE:
            return False, "purpose_not_in_profile(%s)" % p                           # e.g. freshness-witness (EX-01)
    for p, (count, th) in PURPOSE_SHAPE.items():
        if p not in g:
            if p in ("root", "release-registration", "trust-state", "revocation", "reproducer", "release-final", "first-contact-authority"):
                return False, "purpose_missing(%s)" % p
            continue
        ks = g[p]["keys"]
        if count is not None and len(ks) != count:
            return False, "key_count(%s)" % p
        if p in ("release-final", "certification-status") and len(ks) < 2:
            return False, "key_count(%s)" % p
        if g[p]["threshold"] < th or g[p]["threshold"] > len(ks):
            return False, "threshold(%s)" % p
    if root_pl.get("quorums", {}).get("reproducer") != REPRODUCTION_QUORUM:
        return False, "reproducer_quorum"
    holders = {}
    for p, gg in g.items():
        for k in gg["keys"]:
            holders.setdefault(k, set()).add(p)
    for k, ps in sorted(holders.items()):
        for a in sorted(ps):                                                  # sorted: the reported pair is deterministic
            for b in sorted(ps):
                if a < b and frozenset((a, b)) not in WHITELIST:
                    return False, "pair_not_whitelisted(%s,%s)" % (a, b)       # KS-10″ (OP-2 (a) excluded), KS-15 (OP-4 "no" excluded)
    root_keys = set(g["root"]["keys"])
    if set(g["trust-policy"]["keys"]) != root_keys or set(g["first-contact-authority"]["keys"]) != root_keys:
        return False, "root_purposes_not_on_root_keys"
    if g["first-contact-authority"]["threshold"] < g["root"]["threshold"]:
        return False, "fca_threshold_below_root"
    return True, None


def root_chain(ver, statements, lineage, flags):
    """FC-6/FC-7′: root v1 is the root whose digest is the compiled lineage; later versions by dual threshold."""
    roots = [s for s in statements if s["purpose"] == "root"]
    r1 = next((r for r in roots if r["digest"] == lineage and r["payload"].get("version") == 1), None)
    if r1 is None:
        return None, "ROOT_CHAIN_INVALID"
    ok, why = root_conforms(r1["payload"], flags)
    if not ok:
        return None, "PROFILE_NONCONFORMANT:" + why
    if not meets(ver, r1, r1["payload"], "root", set(), flags)[0]:
        return None, "ROOT_CHAIN_INVALID"
    chain = {1: r1}
    n = 2
    while True:
        prev = chain[n - 1]
        nxt = None
        for r in roots:
            p = r["payload"]
            if p.get("version") != n or p.get("previous_digest") != prev["digest"]:
                continue
            if not root_conforms(p, flags)[0]:
                continue
            rev = set().union(*[set(c["payload"].get("revoked_keys", [])) for c in chain.values()]) | set(p.get("revoked_keys", []))
            if meets(ver, r, prev["payload"], "root", rev, flags)[0] and meets(ver, r, p, "root", rev, flags)[0]:
                nxt = r
                break
        if nxt is None:
            break
        chain[n] = nxt
        n += 1
    return chain, None


def parse_tbm(binary_bytes):
    for line in binary_bytes.decode("utf-8", errors="replace").split("\n"):
        if line.startswith("# GOV-TBM "):
            try:
                tbm = json.loads(line[len("# GOV-TBM "):])
                return tbm, sha256d(canon(tbm))
            except Exception:
                return None, None
    return None, None


def semver(v):
    try:
        return tuple(int(x) for x in str(v).split("-")[0].split("."))
    except Exception:
        return None


def independent_classes(ids, registry, attrs, keyfield=None):
    """Largest set of pairwise independent registry entries among `ids`. Independent: every provenance attribute differs, and
    (for suppliers) the checksum key sets are disjoint. Labels and ids are never compared."""
    ents = [registry[i] for i in sorted(set(ids)) if i in registry]
    best = 0
    for mask in range(1, 1 << len(ents)):
        sel = [ents[j] for j in range(len(ents)) if mask >> j & 1]
        ok = True
        for a in range(len(sel)):
            for b in range(a + 1, len(sel)):
                if any(sel[a]["provenance"][k] == sel[b]["provenance"][k] for k in attrs):
                    ok = False
                if keyfield and set(sel[a][keyfield]) & set(sel[b][keyfield]):
                    ok = False
        if ok:
            best = max(best, len(sel))
    return best


SUPPLIER_ATTRS = ("base_image_lineage", "package_source", "build_system", "signing_infrastructure")
TOOLCHAIN_ATTRS = ("bootstrap_root", "package_source", "build_system", "signing_infrastructure")


def refuse(res, code, **kw):
    out = dict(res, result=code)
    out.update(kw)
    return out


def accept(binary_bytes, trust_codes, state_codes, statements, target, evaluator_digest, path_class, now, compiled,
           store_floors=None, flags=None, verifier=None, workdir=None, offered=None):
    """admission-predicate/1, bootstrap mode, CP-1. `compiled` = {"lineage": ...} of this admitter build. `store_floors` = the
    restrictors read from the protected admission store and the account verifier trust store (None only at first admission).
    `offered` names excluded inputs a caller tries to supply (a platform package signature, a witness, a compiled manifest): each
    is refused before anything else (PROFILE_MODE_EXCLUDED)."""
    flags = flags or {}
    v = verifier or Verifier(workdir or tempfile.gettempdir())
    D = sha256d(binary_bytes)
    res = {"binary_digest": D, "target": target, "candidate_executed": False, "path_class": path_class}
    if offered:
        return refuse(res, "PROFILE_MODE_EXCLUDED", offered=sorted(offered))
    if path_class not in RECORD_VALIDITY:
        return refuse(res, "PROFILE_MODE_EXCLUDED", offered=["path_class:%s" % path_class])
    if evaluator_digest == D:
        return refuse(res, "SELF_EVALUATION_REFUSED")
    # FC-4′ compiled quorum over both codes
    q = 1 if flags.get("quorum_one") else FIRST_CONTACT_QUORUM
    if len(trust_codes) < q or len(state_codes) < q:
        return refuse(res, "FIRST_CONTACT_SOURCES_BELOW_QUORUM", read=[len(trust_codes), len(state_codes)], quorum=FIRST_CONTACT_QUORUM)
    if len(set(trust_codes)) != 1 or len(set(state_codes)) != 1:
        return refuse(res, "FIRST_CONTACT_DISAGREEMENT")
    lineage = compiled["lineage"]
    chain, why = root_chain(v, statements, lineage, flags)
    if chain is None:
        return refuse(res, why)
    top = chain[max(chain)]
    revoked_keys = set().union(*[set(c["payload"].get("revoked_keys", [])) for c in chain.values()])
    # FC-5′ FCA at root threshold
    fca = next((s for s in statements if s["purpose"] == "first-contact-authority" and s["digest"] == code_hash(trust_codes[0])), None)
    if fca is None:
        return refuse(res, "FIRST_CONTACT_AUTHORITY_NOT_HELD")
    fp = fca["payload"]
    if not flags.get("fca_unsigned_ok"):
        ok_fca = any(meets(v, fca, c["payload"], "first-contact-authority", revoked_keys, flags)[0] and meets(v, fca, c["payload"], "root", revoked_keys, flags)[0]
                     for c in chain.values() if c["payload"].get("version") == fp.get("root_version"))
        if not ok_fca:
            return refuse(res, "FIRST_CONTACT_AUTHORITY_UNVERIFIED")
    if fp.get("lineage") != lineage or trust_code(lineage, fp.get("fca_sequence", 0), fca["digest"]) != trust_codes[0]:
        return refuse(res, "FIRST_CONTACT_LINEAGE_NOT_COMPILED")
    if fp.get("profile_id") != PROFILE_ID or len(fp.get("sources", [])) != 2:
        return refuse(res, "PROFILE_NONCONFORMANT:fca")
    # FC-8′ evaluator binding and target certification
    if target not in fp.get("certified_targets", []):
        return refuse(res, "TARGET_NOT_CERTIFIED")
    if (fp.get("admitters") or {}).get(target) != evaluator_digest and not flags.get("skip_evaluator_binding"):
        return refuse(res, "ADMITTER_NOT_LISTED")
    # AP-3′ selected Trust State
    tss = next((s for s in statements if s["purpose"] == "trust-state" and s["digest"] == code_hash(state_codes[0])), None)
    if tss is None:
        return refuse(res, "STATE_NOT_HELD")
    tp = tss["payload"]
    rr = tp.get("references", {})
    rv = (rr.get("root") or {}).get("version")
    if rv not in chain or chain[rv]["digest"] != (rr.get("root") or {}).get("digest"):
        return refuse(res, "STATE_ROOT_NOT_IN_CHAIN")
    eff_root = chain[rv]["payload"]
    if not meets(v, tss, eff_root, "trust-state", revoked_keys, flags)[0]:
        return refuse(res, "TRUST_STATE_UNVERIFIED")
    if state_code(lineage, tp.get("sequence", 0), tss["digest"]) != state_codes[0]:
        return refuse(res, "FIRST_CONTACT_STATE_CODE_MISMATCH")
    fref = rr.get("first_contact_authority") or {}
    if fref.get("digest") != fca["digest"] and not flags.get("skip_fca_state_binding"):
        return refuse(res, "FIRST_CONTACT_AUTHORITY_MISMATCH")
    pol = next((s for s in statements if s["purpose"] == "trust-policy" and s["digest"] == (rr.get("trust_policy") or {}).get("digest")), None)
    if pol is None or not meets(v, pol, eff_root, "trust-policy", revoked_keys, flags)[0]:
        return refuse(res, "TRUST_POLICY_UNVERIFIED")
    pp = pol["payload"]
    if pp.get("profile_id") != PROFILE_ID or (pp.get("gating") or {}).get("mode") != "always_gate" or pp.get("registration", {}).get("min_verification_records") != MIN_VERIFICATION_RECORDS:
        return refuse(res, "PROFILE_NONCONFORMANT:trust_policy")
    for excluded in ("op7_mode", "witness_max_validity_hours", "channel_quorum", "revoked_self_scope", "op6_mode", "max_anchor_age_days"):
        if excluded in (pp.get("bootstrap") or {}):
            return refuse(res, "PROFILE_NONCONFORMANT:trust_policy.bootstrap.%s" % excluded)
    if "eligible_until" in (pp.get("eligibility") or {}):
        return refuse(res, "PROFILE_NONCONFORMANT:trust_policy.eligibility.eligible_until")
    # FC-9 admission state age (compiled 24 h)
    issued = ts(tp["issued_at"])
    nowt = ts(now)
    if issued > nowt + CLOCK_SKEW:
        return refuse(res, "STATEMENT_ISSUED_IN_FUTURE")
    if nowt - issued > ADMISSION_STATE_MAX_AGE and not flags.get("skip_state_age"):
        return refuse(res, "FIRST_CONTACT_STATE_TOO_OLD", age_hours=round((nowt - issued).total_seconds() / 3600, 1))
    res["selected_state"] = {"sequence": tp.get("sequence"), "digest": tss["digest"], "issued_at": tp["issued_at"]}
    # negatives: the selected state plus revocation statements it lists
    N = set(tp.get("revocations", []))
    for s in statements:
        if s["purpose"] == "revocation" and (meets(v, s, eff_root, "revocation", revoked_keys, flags)[0] or meets(v, s, eff_root, "root", revoked_keys, flags)[0]):
            if s["digest"] in set(tp.get("revocation_statements", [])):
                N |= set(s["payload"].get("revokes", []))
    held = store_floors or {}
    Nh = set(held.get("negatives", []))
    use_store = store_floors is not None and not flags.get("readmission_ignores_store")
    # AP-R1…R4 re-admission applies the store
    if use_store:
        if tp.get("sequence", 0) < held.get("state_sequence", 0):
            return refuse(res, "READMISSION_STATE_BELOW_HELD", held=held.get("state_sequence"), selected=tp.get("sequence"))
        if tp.get("sequence") == held.get("state_sequence") and held.get("state_digest") not in (None, tss["digest"]):
            return refuse(res, "TRUST_STATE_EQUIVOCATION")
        if rv < held.get("root_version", 0):
            return refuse(res, "READMISSION_ROOT_BELOW_HELD")
        if (rr.get("trust_policy") or {}).get("version", 0) < held.get("policy_version", 0):
            return refuse(res, "READMISSION_POLICY_BELOW_HELD")
        if fp.get("fca_sequence", 0) < held.get("fca_sequence", 0):
            return refuse(res, "FIRST_CONTACT_AUTHORITY_BELOW_HELD")
        if evaluator_digest in Nh:
            return refuse(res, "ADMITTER_REVOKED_IN_HELD_STATE")
    if evaluator_digest in N:
        return refuse(res, "ADMITTER_REVOKED")
    if D in N:
        return refuse(res, "BINARY_REVOKED", reason="binary")
    if use_store and D in Nh:
        return refuse(res, "BINARY_REVOKED_IN_HELD_STATE", reason="binary")
    # AP-5r registration-authority revocations
    RA = set()
    for s in statements:
        if s["type"] == TYPE_PREFIX + "registration-revocation+json" and meets(v, s, eff_root, "release-registration", revoked_keys, flags)[0]:
            RA |= set(s["payload"].get("revokes", []))
    alive = lambda s: s["digest"] not in N and s["digest"] not in RA
    # reproductions
    rg = eff_root.get("grants", {}).get("reproducer", {"keys": []})
    reps = []
    for s in statements:
        if s["purpose"] != "reproducer":
            continue
        sg = signers(v, s, eff_root, revoked_keys, flags) & set(rg["keys"])
        if len(sg) == 1:
            reps.append({"s": s, "p": s["payload"], "key": next(iter(sg))})
    mine = [r for r in reps if r["p"].get("binary_digest") == D and r["p"].get("target") == target and alive(r["s"])]
    rids = {r["p"].get("release_id") for r in mine}
    regs_all = [s for s in statements if s["type"] == TYPE_PREFIX + "release-registration+json" and meets(v, s, eff_root, "release-registration", revoked_keys, flags)[0]]
    by_rid = {}
    for s in regs_all:
        by_rid.setdefault(s["payload"].get("release_id"), set()).add(s["digest"])
    regs = [s for s in regs_all if s["digest"] in set(tp.get("registrations", [])) and s["payload"].get("release_id") in rids]
    if not regs:
        return refuse(res, "RELEASE_UNREGISTERED")
    reg = regs[0]
    if len(by_rid[reg["payload"]["release_id"]]) > 1:
        return refuse(res, "REGISTRATION_EQUIVOCATION")
    rp = reg["payload"]
    res["release_id"] = rp.get("release_id")
    if target not in rp.get("targets", []):
        return refuse(res, "TARGET_NOT_REGISTERED")
    for d, why in ((reg["digest"], "registration"), (rp.get("final_statement_digest"), "registered_final"), (rp.get("candidate_statement_digest"), "registered_candidate")):
        if d in N:
            return refuse(res, "BINARY_REVOKED", reason=why)
        if use_store and d in Nh:
            return refuse(res, "BINARY_REVOKED_IN_HELD_STATE", reason=why)
    if reg["digest"] in RA:
        return refuse(res, "BINARY_REVOKED", reason="registration_revoked_by_registration_authority")
    final = next((s for s in statements if s["purpose"] == "release-final" and s["digest"] == rp.get("final_statement_digest")), None)
    if final is None or not meets(v, final, eff_root, "release-final", revoked_keys, flags)[0]:
        return refuse(res, "RELEASE_FINAL_UNVERIFIED")
    fpl = final["payload"]
    kernel = (rp.get("constitution") or {}).get("kernel_tree_digest")
    if fpl.get("source") != rp.get("source") or fpl.get("promoted_from") != rp.get("candidate_statement_digest") or fpl.get("kernel_tree_digest") != kernel:
        return refuse(res, "RELEASE_FINAL_UNVERIFIED")
    # AP-SEC computed security minimum (OP-11 (b))
    ref_regs = [s["payload"] for s in regs_all if s["digest"] in set(tp.get("registrations", []))]
    sec_min = max([pp.get("eligibility", {}).get("min_release_sequence", 1)] + [r["sequence"] for r in ref_regs if r.get("security_relevant_change")])
    if use_store:
        sec_min = max(sec_min, held.get("security_minimum", 0))
    if not flags.get("skip_security_minimum") and rp.get("sequence", 0) < sec_min:
        return refuse(res, "RELEASE_BELOW_SECURITY_MINIMUM", minimum=sec_min, release_sequence=rp.get("sequence"))
    # binary version floor
    tbm, tbm_d = parse_tbm(binary_bytes)
    mbv = (pp.get("eligibility") or {}).get("min_binary_version")
    if mbv:
        bv = semver((tbm or {}).get("version"))
        if bv is None or bv < (semver(mbv) or (0,)):
            return refuse(res, "BINARY_BELOW_TRUST_POLICY")
    # AP-5 verification records
    envs = [e for e in rp.get("environments", []) if e.get("target") == target]
    env_ids = {e["environment_id"] for e in envs}
    for s in statements:
        if s["purpose"] == "verification-attestation" and s["digest"] not in RA:
            sp = s["payload"]
            if sp.get("candidate_statement_digest") == rp.get("candidate_statement_digest") and sp.get("verdict") == "REJECTED" and meets(v, s, eff_root, "verification-attestation", revoked_keys, flags)[0]:
                return refuse(res, "ARTIFACT_SOURCE_REJECTED")
    vkeys, vexec, vrep = set(), set(), set()
    for s in statements:
        if s["purpose"] != "verification-attestation" or not alive(s) or s["digest"] not in set(rp.get("verification_records", [])):
            continue
        sp = s["payload"]
        if sp.get("verdict") != "ACCEPTED" or sp.get("candidate_statement_digest") != rp.get("candidate_statement_digest") or sp.get("kernel_tree_digest") != kernel:
            continue
        if sp.get("source") != rp.get("source") or sp.get("inputs_manifest_digest") != rp.get("inputs_manifest_digest"):
            continue
        if not flags.get("skip_verification_environment") and not env_ids <= set(sp.get("environment_ids", [])):
            continue
        ok, sk = meets(v, s, eff_root, "verification-attestation", revoked_keys, flags)
        if not ok:
            continue
        if flags.get("count_attestation_signatures"):
            vkeys |= sk
            continue
        if sp.get("verifier_execution_id") in vexec or sp.get("verification_report_digest") in vrep or (sk & vkeys):
            continue
        vkeys |= sk
        vexec.add(sp.get("verifier_execution_id"))
        vrep.add(sp.get("verification_report_digest"))
    if len(vkeys) < MIN_VERIFICATION_RECORDS:
        return refuse(res, "VERIFICATION_RECORDS_BELOW_MINIMUM", counted=len(vkeys))
    # AP-6 reproduction quorum, diversity, conflict, registered digest
    reg_tc = {t["toolchain_id"] for t in rp.get("toolchains", []) if t.get("target") == target}
    counted, sup, tcs = set(), set(), set()
    env_supplier = {e["environment_id"]: e["supplier_id"] for e in envs}
    for r in mine:
        p = r["p"]
        if p.get("release_id") != rp.get("release_id") or p.get("source") != rp.get("source") or p.get("inputs_manifest_digest") != rp.get("inputs_manifest_digest"):
            continue
        if p.get("tbm_digest") != tbm_d or p.get("environment_id") not in env_ids or p.get("toolchain_id") not in reg_tc:
            continue
        counted.add(r["key"])
        sup.add(env_supplier[p["environment_id"]])
        tcs.add(p["toolchain_id"])
    res["reproducer_keys"] = sorted(counted)
    if len(counted) < REPRODUCTION_QUORUM:
        return refuse(res, "REPRODUCTION_QUORUM_NOT_MET", counted=len(counted))
    sc = pp.get("supply_chain") or {}
    suppliers = {x["supplier_id"]: x for x in sc.get("suppliers", [])}
    toolchains = {x["toolchain_id"]: x for x in sc.get("toolchains", [])}
    if flags.get("supplier_class_by_label"):
        n_sup = len(sup)
    else:
        n_sup = independent_classes(sup, suppliers, SUPPLIER_ATTRS, "checksum_keys")
    if n_sup < 2:
        return refuse(res, "ENVIRONMENT_DIVERSITY_NOT_MET", suppliers=sorted(sup))
    n_tc = len(tcs) if flags.get("toolchain_class_by_label") else independent_classes(tcs, toolchains, TOOLCHAIN_ATTRS)
    if n_tc < 2:
        return refuse(res, "TOOLCHAIN_DIVERSITY_NOT_MET", toolchains=sorted(tcs))
    for r in reps:
        p = r["p"]
        if p.get("release_id") == rp.get("release_id") and p.get("target") == target and p.get("binary_digest") != D and r["s"]["digest"] not in RA:
            return refuse(res, "REPRODUCTION_CONFLICT")
    if (rp.get("binary_digests") or {}).get(target) != D:
        return refuse(res, "BINARY_NOT_REGISTERED")
    # AP-7 publication
    if D not in set(tp.get("published_binaries", [])):
        return refuse(res, "BINARY_NOT_PUBLISHED")
    # AP-8 TBM
    if tbm is None or tbm.get("build") != "release" or tbm.get("profile_id") != PROFILE_ID:
        return refuse(res, "BINARY_T0_UNVERIFIED")
    for f, want in (("lineage", lineage), ("source", rp.get("source")), ("inputs_manifest_digest", rp.get("inputs_manifest_digest"))):
        if tbm.get(f) != want:
            return refuse(res, "BINARY_T0_UNVERIFIED", reason=f)
    if use_store and not flags.get("skip_accepted_tbm"):
        hw = held.get("accepted_tbm") or {}
        comp = (tbm.get("root_version", 0), tbm.get("policy_version", 0), tbm.get("state_sequence", 0))
        if comp < (hw.get("root", 0), hw.get("policy", 0), hw.get("state", 0)):
            return refuse(res, "BINARY_T0_ROLLBACK")
    return dict(res, result="ACCEPTED", lineage=lineage, fca_sequence=fp.get("fca_sequence"), age_note=display_age_warning(tp["issued_at"], now))


# ---------------------------------------------------------------------------------------------------------- operator procedure
def platform_sha256(data, workdir):
    os.makedirs(workdir, exist_ok=True)
    p = os.path.join(workdir, "fc7-" + hashlib.sha256(data).hexdigest()[:20])
    if not os.path.exists(p):
        with open(p, "wb") as f:
            f.write(data)
    r = subprocess.run(["sha256sum", p], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    return "sha256:" + r.stdout.split()[0]


def fc_procedure(pages, fca_payload_bytes, admitter_bytes, target, workdir, offered=None):
    """`32` FC-1′…FC-3′. `pages`: one dict per source actually read: {"trust_code", "state_code", "procedure_digest"}. There is no
    platform-signature step and no single-source route (EX-04, EX-05, EX-17, EX-18)."""
    if offered:
        return {"result": "PROFILE_MODE_EXCLUDED", "offered": sorted(offered)}
    if len(pages) < FIRST_CONTACT_QUORUM:
        return {"result": "FIRST_CONTACT_SOURCES_BELOW_QUORUM", "read": len(pages)}
    for f in ("trust_code", "state_code", "procedure_digest"):
        if len({p.get(f) for p in pages}) != 1:
            return {"result": "FIRST_CONTACT_DISAGREEMENT", "field": f}
    if platform_sha256(fca_payload_bytes, workdir) != code_hash(pages[0]["trust_code"]):
        return {"result": "FIRST_CONTACT_AUTHORITY_MISMATCH"}
    fca = json.loads(fca_payload_bytes)
    if target not in fca.get("certified_targets", []):
        return {"result": "TARGET_NOT_CERTIFIED"}
    if (fca.get("admitters") or {}).get(target) != platform_sha256(admitter_bytes, workdir):
        return {"result": "ADMITTER_DIGEST_MISMATCH"}
    if fca.get("procedure_digest") != pages[0]["procedure_digest"]:
        return {"result": "FIRST_CONTACT_PROCEDURE_MISMATCH"}
    return {"result": "OK", "admitter_digest": fca["admitters"][target]}


# ---------------------------------------------------------------------------------------------------------- source custodian
def custodian_publish(ver, statements, compiled_lineage, fca_digest, tss_digest, last_published, flags=None):
    """`32` R-FCS-1…R-FCS-3: a source custodian computes and publishes codes only for statements it verified first-hand: the FCA at
    root threshold under the lineage it holds from the root ceremony record; the Trust State at the trust-state threshold, naming
    that FCA, descending from the last state it published without dropping a revocation, registration or publication."""
    flags = flags or {}
    chain, why = root_chain(ver, statements, compiled_lineage, flags)
    if chain is None:
        return {"published": False, "reason": why}
    revoked = set().union(*[set(c["payload"].get("revoked_keys", [])) for c in chain.values()])
    fca = next((s for s in statements if s["digest"] == fca_digest and s["purpose"] == "first-contact-authority"), None)
    if fca is None or not any(meets(ver, fca, c["payload"], "first-contact-authority", revoked, flags)[0] for c in chain.values()):
        return {"published": False, "reason": "FIRST_CONTACT_AUTHORITY_UNVERIFIED"}
    tss = next((s for s in statements if s["digest"] == tss_digest and s["purpose"] == "trust-state"), None)
    if tss is None:
        return {"published": False, "reason": "STATE_NOT_HELD"}
    tp = tss["payload"]
    rv = (tp.get("references", {}).get("root") or {}).get("version")
    if rv not in chain or not meets(ver, tss, chain[rv]["payload"], "trust-state", revoked, flags)[0]:
        return {"published": False, "reason": "TRUST_STATE_UNVERIFIED"}
    if (tp.get("references", {}).get("first_contact_authority") or {}).get("digest") != fca_digest:
        return {"published": False, "reason": "FIRST_CONTACT_AUTHORITY_MISMATCH"}
    if last_published is not None:
        lp = last_published["payload"]
        if tp.get("sequence", 0) <= lp.get("sequence", 0):
            return {"published": False, "reason": "STATE_NOT_NEWER_THAN_PUBLISHED"}
        if {"sequence": lp["sequence"], "digest": last_published["digest"]} not in tp.get("prior_states", []):
            return {"published": False, "reason": "STATE_NOT_DESCENDANT"}
        for fld in ("revocations", "registrations", "published_binaries"):
            if not set(lp.get(fld, [])) <= set(tp.get(fld, [])):
                return {"published": False, "reason": "STATE_DROPS_%s" % fld.upper()}
    lineage = compiled_lineage
    return {"published": True, "trust_code": trust_code(lineage, fca["payload"]["fca_sequence"], fca["digest"]),
            "state_code": state_code(lineage, tp["sequence"], tss["digest"]), "procedure_digest": fca["payload"].get("procedure_digest")}


# ---------------------------------------------------------------------------------------------------------- stores and records
def protected_store(root_dir, lineage):
    return os.path.join(root_dir, "admission", lineage.split(":", 1)[1])


def account_store(root_dir, lineage):
    return os.path.join(root_dir, "account-vts", lineage.split(":", 1)[1])


def is_first_admission(root_dir, lineage, flags=None):
    """R-STORE-2: decided only by the protected admission store's marker, never by any file of the account store."""
    flags = flags or {}
    if flags.get("first_admission_from_account_store"):
        ad = os.path.join(account_store(root_dir, lineage), "admissions")
        return not (os.path.isdir(ad) and any(f.endswith(".json") for f in os.listdir(ad)))
    return not os.path.isfile(os.path.join(protected_store(root_dir, lineage), "admission-store.json"))


def read_floors(root_dir, lineage):
    """Restrictors only, merged from both stores (a planted higher floor can only refuse)."""
    out = {"state_sequence": 0, "root_version": 0, "policy_version": 0, "fca_sequence": 0, "security_minimum": 0, "negatives": [],
           "accepted_tbm": {"root": 0, "policy": 0, "state": 0}, "state_digest": None, "clock_high_water": ""}
    found = False
    for base in (protected_store(root_dir, lineage), account_store(root_dir, lineage)):
        p = os.path.join(base, "floors.json")
        if not os.path.isfile(p):
            continue
        found = True
        f = json.load(open(p))
        for k in ("state_sequence", "root_version", "policy_version", "fca_sequence", "security_minimum"):
            if f.get(k, 0) > out[k]:
                out[k] = f[k]
                if k == "state_sequence":
                    out["state_digest"] = f.get("state_digest")
        out["negatives"] = sorted(set(out["negatives"]) | set(f.get("negatives", [])))
        out["clock_high_water"] = max(out["clock_high_water"], f.get("clock_high_water") or "")
        a = f.get("accepted_tbm") or {}
        if (a.get("root", 0), a.get("policy", 0), a.get("state", 0)) > (out["accepted_tbm"]["root"], out["accepted_tbm"]["policy"], out["accepted_tbm"]["state"]):
            out["accepted_tbm"] = {"root": a.get("root", 0), "policy": a.get("policy", 0), "state": a.get("state", 0)}
    return out if found else None


def write_admission(record, floors_after, root_dir, lineage, flags=None):
    """R-ADM-7″, R-ADM-8″, R-ADM-13: serialised; first admission creates the protected store and moves the account store aside;
    re-admission keeps both and raises the floors; one record per binary."""
    flags = flags or {}
    ps = protected_store(root_dir, lineage)
    os.makedirs(os.path.dirname(ps), exist_ok=True)
    lock = os.open(os.path.join(os.path.dirname(ps), ".gov-admit.lock"), os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        first = is_first_admission(root_dir, lineage, flags)
        moved = None
        acc = account_store(root_dir, lineage)
        if first and os.path.isdir(acc) and not flags.get("skip_account_move_aside"):
            n = 0
            while os.path.exists(acc + ".pre-admission-%d" % n):
                n += 1
            moved = acc + ".pre-admission-%d" % n
            os.rename(acc, moved)
        os.makedirs(os.path.join(ps, "admissions"), exist_ok=True)
        if first:
            json.dump({"lineage": lineage, "created_at": record["admitted_at"], "first_admitted_digest": record["binary_digest"]}, open(os.path.join(ps, "admission-store.json"), "w"), sort_keys=True)
        rp = os.path.join(ps, "admissions", record["binary_digest"].split(":", 1)[1] + ".json")
        tmp = rp + ".tmp-%d" % os.getpid()
        json.dump(record, open(tmp, "w"), sort_keys=True, indent=1)
        os.replace(tmp, rp)
        prev = read_floors(root_dir, lineage) or {}
        merged = dict(floors_after)
        for k in ("state_sequence", "root_version", "policy_version", "fca_sequence", "security_minimum"):
            merged[k] = max(prev.get(k, 0), floors_after.get(k, 0))
        merged["negatives"] = sorted(set(prev.get("negatives", [])) | set(floors_after.get("negatives", [])))
        merged["clock_high_water"] = max(prev.get("clock_high_water") or "", floors_after.get("clock_high_water") or "", record["admitted_at"])  # R-CLK-1
        json.dump(merged, open(os.path.join(ps, "floors.json"), "w"), sort_keys=True)
        return {"record": rp, "first_admission": first, "account_store_moved_aside": moved}
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        os.close(lock)


def make_record(binary_digest, target, release_id, lineage, trust_code_, state_code_, admitter_digest, now, path_class):
    return {"schema": "governance-os.admission-record/3", "binary_digest": binary_digest, "target": target, "release_id": release_id, "lineage": lineage,
            "trust_code": trust_code_, "state_code": state_code_, "admitted_at": now, "admitter_digest": admitter_digest, "admitter_kind": "compiled-gov-admit",
            "path_class": path_class, "valid_until": (ts(now) + RECORD_VALIDITY[path_class]).strftime("%Y-%m-%dT%H:%M:%SZ")}


def tcb_location_protected(path):
    uid = os.geteuid()
    if uid == 0:
        return False
    cur = os.path.abspath(path)
    while True:
        try:
            st = os.stat(cur)
        except OSError:
            return False
        if st.st_uid == uid or os.access(cur, os.W_OK):
            return False
        parent = os.path.dirname(cur)
        if parent == cur:
            return True
        cur = parent


def gov_run(exe_bytes, action, root_dir, lineage, now, held_negatives, listed_admitters, anchor=None, flags=None, protected=True):
    """Genuine-binary rule and the OP-7 (a) decision rule for a running CP-1 binary. `anchor` = {"class", "anchored_at",
    "names_effective_state"}; `listed_admitters` = admitter digests of the FCA the effective state names. `protected` stands for the
    TCB-location predicate of the executable (the reference cannot create root-owned paths)."""
    flags = flags or {}
    own = sha256d(exe_bytes)
    base = {"action": action, "own_digest": own}
    if action in C0_R:
        return dict(base, result="ALLOWED")
    ps = protected_store(root_dir, lineage)
    rp = os.path.join(ps, "admissions", own.split(":", 1)[1] + ".json")
    if not os.path.isfile(rp):
        return dict(base, result="BINARY_NOT_ADMITTED")
    rec = json.load(open(rp))
    if rec.get("admitter_kind") != "compiled-gov-admit" or rec.get("admitter_digest") not in set(listed_admitters):
        return dict(base, result="RECORD_ADMITTER_NOT_LISTED")
    if rec.get("lineage") != lineage:
        return dict(base, result="TRUST_ROOT_LINEAGE_MISMATCH")
    floors = read_floors(root_dir, lineage) or {}
    if not flags.get("skip_clock_high_water"):
        # R-CLK-1 (24 §4.5): a clock earlier than anything this machine has already recorded (admission, floors, anchor) proves the
        # clock wrong; every age and validity computed from it is meaningless, so only C0-R remains.
        hw_clock = max(floors.get("clock_high_water") or "", rec.get("admitted_at") or "", (anchor or {}).get("anchored_at") or "", (anchor or {}).get("currency_at") or "")
        if hw_clock and ts(hw_clock) > ts(now) + CLOCK_SKEW:
            return dict(base, result="TRUST_CLOCK_BELOW_HIGH_WATER", scope="C0-R")
    if ts(rec["valid_until"]) < ts(now):
        return dict(base, result="ADMISSION_RECORD_EXPIRED")
    if own in set(held_negatives):
        return dict(base, result="BINARY_REVOKED_SELF", scope="C0-R")
    tbm, _ = parse_tbm(exe_bytes)
    hw = floors.get("accepted_tbm") or {}
    if not flags.get("skip_r_art_2") and tbm is not None:
        if (tbm.get("root_version", 0), tbm.get("policy_version", 0), tbm.get("state_sequence", 0)) < (hw.get("root", 0), hw.get("policy", 0), hw.get("state", 0)):
            return dict(base, result="BINARY_T0_ROLLBACK")
    if anchor is None:
        return dict(base, result="TRUST_STATE_UNANCHORED")
    if ts(now) - ts(anchor["anchored_at"]) > ANCHOR_VALIDITY[anchor["class"]]:
        return dict(base, result="TRUST_ANCHOR_EXPIRED")
    if action in ("C1", "C2"):
        return dict(base, result="ALLOWED")
    if action in ("C3", "confirm-state", "trust-gate-confirm"):
        if not protected:
            return dict(base, result="TCB_WRITABLE_BY_GOVERNED_ACCOUNT")
        if action == "C3" and not (anchor.get("names_effective_state") and ts(now) - ts(anchor.get("currency_at", anchor["anchored_at"])) <= C3_CURRENCY):
            return dict(base, result="TRUST_STATE_CURRENCY_UNPROVEN")
        return dict(base, result="ALLOWED")
    return dict(base, result="PROFILE_MODE_EXCLUDED")
