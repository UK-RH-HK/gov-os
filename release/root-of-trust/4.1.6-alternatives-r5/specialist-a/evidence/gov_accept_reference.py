#!/usr/bin/env python3
"""gov-accept reference — prototype of the independent first-binary acceptance executor (AR-0009, specialist A).

PROPOSAL EVIDENCE ONLY. Not the Governance OS implementation, not signed, not a release tool.

It implements the single acceptance function `accept()` of 01-ALTERNATIVE.md §3.3 for a machine that has no trusted `gov`:
  trust inputs  (1) a state fingerprint typed from an independent channel; the fingerprint commits to the lineage id, the
                    root version and digest, the Trust Policy version and digest and the Trust State sequence and digest;
                (2) the SHA-256 of the candidate binary, measured here by reading the file once;
                (3) statements from any source (carriers only).
  compiled in   nothing but the algorithm (no keys, no Trust Policy, no Trust State);
  clock         none;
  candidate     never executed.
Signature verification uses the platform OpenSSL CLI (`openssl pkeyutl -verify -rawin`, Ed25519) and Python stdlib only.

Statement envelope (toy DSSE): {"payloadType", "payload" (base64 of canonical JSON), "signatures": [{"keyid", "sig"}]};
PAE = "DSSEv1 <len type> <type> <len body> <body>"; statement digest = sha256(payload bytes).

`flags` switches individual checks off; E3 uses them as single-rule mutants to measure the conformance vectors' power.
CLI: gov_accept_reference.py --fingerprint FP --statements DIR --target T [--install DEST] BINARY   (JSON on stdout)
"""
import base64, hashlib, json, os, subprocess, sys, tempfile

sys.dont_write_bytecode = True
ED25519_SPKI_PREFIX = bytes.fromhex("302a300506032b6570032100")
TYPE_PURPOSE = {
    "application/vnd.sam.root+json": "root",
    "application/vnd.sam.trust-policy+json": "trust-policy",
    "application/vnd.sam.trust-state+json": "trust-state",
    "application/vnd.sam.reproduction+json": "reproducer",
}
COMPILED_MIN_QUORUM = 2


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def pae(ptype, body):
    t = ptype.encode()
    return b"DSSEv1 %d %s %d %s" % (len(t), t, len(body), body)


def fingerprint(lineage, root_v, root_d, pol_v, pol_d, seq, state_d):
    epoch = {"lineage": lineage, "root_version": root_v, "root_digest": root_d, "policy_version": pol_v, "policy_digest": pol_d,
             "state_sequence": seq, "state_digest": state_d}
    return f"gov-state:{lineage[7:15]}:{seq}:{hashlib.sha256(canon(epoch)).hexdigest()[:32]}"


class Verifier:
    def __init__(self, workdir):
        self.w = tempfile.mkdtemp(prefix="acc-", dir=workdir)
        self.cache = {}
        self.calls = 0

    def verify(self, pub_raw, msg, sig):
        k = (pub_raw, hashlib.sha256(msg).digest(), sig)
        if k in self.cache:
            return self.cache[k]
        self.calls += 1
        pem = b"-----BEGIN PUBLIC KEY-----\n" + base64.encodebytes(ED25519_SPKI_PREFIX + pub_raw) + b"-----END PUBLIC KEY-----\n"
        n = len(self.cache)
        p, m, s = (os.path.join(self.w, f"{n}.{x}") for x in ("pem", "msg", "sig"))
        open(p, "wb").write(pem)
        open(m, "wb").write(msg)
        open(s, "wb").write(sig)
        r = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", p, "-rawin", "-in", m, "-sigfile", s],
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
        if env.get("payloadType") not in TYPE_PURPOSE or canon(payload) != body:
            continue  # unknown type or non-canonical payload
        out.append({"file": fn, "type": env["payloadType"], "purpose": TYPE_PURPOSE[env["payloadType"]], "body": body,
                    "payload": payload, "digest": sha(body), "sigs": env.get("signatures", [])})
    return out


def valid_signers(v, st, root_payload):
    keys = root_payload["keys"]
    revoked = set(root_payload.get("revoked_keys", []))
    msg = pae(st["type"], st["body"])
    ok = set()
    for s in st["sigs"]:
        kid = s.get("keyid")
        if kid not in keys or kid in revoked:
            continue
        try:
            sig = base64.b64decode(s["sig"], validate=True)
            pub = base64.b64decode(keys[kid])
        except Exception:
            continue
        if "ed25519:" + hashlib.sha256(pub).hexdigest() != kid:
            continue  # key id recomputed
        if v.verify(pub, msg, sig):
            ok.add(kid)
    return ok


def meets(v, st, root_payload, purpose, minimum=1):
    g = root_payload["grants"].get(purpose)
    if not g:
        return False, set()
    signers = valid_signers(v, st, root_payload) & set(g["keys"])
    return len(signers) >= max(g["threshold"], minimum), signers


def well_formed(root_payload, flags):
    """KS-7: no revoked key is granted any purpose."""
    if flags.get("skip_ks7_check"):
        return True
    revoked = set(root_payload.get("revoked_keys", []))
    return not any(revoked & set(g.get("keys", [])) for g in root_payload.get("grants", {}).values())


def root_chain(v, roots, flags):
    """Return {version: payload, digest} for the chain v1..vN whose every link verifies (dual threshold)."""
    by_v = {}
    for r in roots:
        if not well_formed(r["payload"], flags):
            continue
        by_v.setdefault(r["payload"].get("version"), []).append(r)
    chain = {}
    if 1 not in by_v:
        return chain
    for r1 in by_v[1]:
        ok, _ = meets(v, r1, r1["payload"], "root")
        if ok or flags.get("skip_root_signatures"):
            chain[1] = r1
            break
    n = 1
    while n in chain and (n + 1) in by_v:
        prev = chain[n]
        for r in by_v[n + 1]:
            if r["payload"].get("previous_digest") != prev["digest"] and not flags.get("skip_root_link"):
                continue
            ok_prev, _ = meets(v, r, prev["payload"], "root")
            ok_self, _ = meets(v, r, r["payload"], "root")
            if (ok_prev and ok_self) or flags.get("skip_root_signatures"):
                chain[n + 1] = r
                break
        n += 1
    return chain


def accept(binary_bytes, fp, statements, target, flags=None, verifier=None, workdir=None):
    flags = flags or {}
    v = verifier or Verifier(workdir or tempfile.gettempdir())
    digest = sha(binary_bytes)
    res = {"binary_digest": digest, "target": target, "fingerprint": fp, "candidate_executed": False}
    try:
        _, lin8, seq_s, h32 = fp.split(":")
        seq = int(seq_s)
    except Exception:
        return dict(res, result="FINGERPRINT_MALFORMED")
    roots = [s for s in statements if s["purpose"] == "root"]
    chain = root_chain(v, roots, flags)
    if not chain:
        return dict(res, result="ROOT_CHAIN_INVALID")
    lineage = chain[1]["digest"]
    res["lineage"] = lineage
    # ---- select the Trust State whose epoch fingerprint equals the typed one (the only selector of state)
    selected = None
    for t in [s for s in statements if s["purpose"] == "trust-state"]:
        p = t["payload"]
        if p.get("sequence") != seq and not flags.get("any_state"):
            continue
        rv, rd = p["references"]["root"]["version"], p["references"]["root"]["digest"]
        pv, pd = p["references"]["trust_policy"]["version"], p["references"]["trust_policy"]["digest"]
        if rv not in chain or chain[rv]["digest"] != rd:
            if not flags.get("skip_root_link"):
                continue
        pol = next((s for s in statements if s["purpose"] == "trust-policy" and s["digest"] == pd), None)
        if pol is None:
            continue
        if not flags.get("any_state"):
            if fingerprint(lineage, rv, rd, pv, pd, p["sequence"], t["digest"]) != fp:
                continue
        eff_root = chain.get(rv, chain[max(chain)])["payload"]
        ok_t, _ = meets(v, t, eff_root, "trust-state")
        ok_p, _ = meets(v, pol, eff_root, "trust-policy")
        if not (ok_t and ok_p) and not flags.get("skip_state_signatures"):
            continue
        cand = (t, pol, eff_root)
        if selected is None or p["sequence"] > selected[0]["payload"]["sequence"]:
            selected = cand
    if selected is None:
        return dict(res, result="STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH")
    tss, tps, eff_root = selected
    res["selected_state"] = {"sequence": tss["payload"]["sequence"], "digest": tss["digest"], "issued_at": tss["payload"].get("issued_at")}
    revoked = set(tss["payload"].get("revocations", []))
    # ---- negatives
    if digest in revoked and not flags.get("skip_revocation"):
        return dict(res, result="BINARY_REVOKED")
    # ---- registration (selector of source and inputs) and reproduction quorum (observation of bytes)
    regs = {r["release_id"]: r for r in tps["payload"].get("releases", [])}
    quorum = max(COMPILED_MIN_QUORUM, (eff_root["grants"].get("reproducer") or {}).get("threshold", 0))
    if flags.get("quorum_one"):
        quorum = 1
    repros = []
    for s in statements:
        if s["purpose"] != "reproducer":
            continue
        if s["digest"] in revoked and not flags.get("skip_revocation"):
            continue
        g = eff_root["grants"].get("reproducer")
        if not g:
            continue
        signers = valid_signers(v, s, eff_root) & set(g["keys"])
        if flags.get("ignore_signer_revocation"):
            signers = valid_signers(v, s, dict(eff_root, revoked_keys=[])) & set(g["keys"])
        if len(signers) != 1 and not flags.get("multi_signer_counts"):
            continue  # a reproduction is first-person: exactly one reproducer key
        p = s["payload"]
        rel = regs.get(p.get("release_id"))
        if rel is None or (p.get("source") != rel["source"] and not flags.get("skip_source_equality")) or p.get("target") != target:
            continue
        if target not in rel.get("targets", []):
            continue
        for k in signers:
            repros.append((p["release_id"], p["binary_digest"], p.get("tbm_digest"), k, s["digest"]))
    mine = [r for r in repros if r[1] == digest]
    if not mine:
        return dict(res, result="RELEASE_UNREGISTERED_OR_NOT_REPRODUCED")
    release_id = mine[0][0]
    signers = {r[3] for r in mine if r[0] == release_id}
    if flags.get("count_statements_not_keys"):
        signers = {r[4] for r in mine if r[0] == release_id}
    res["release_id"] = release_id
    res["reproducers"] = sorted(signers)
    if len(signers) < quorum:
        return dict(res, result="REPRODUCTION_QUORUM_NOT_MET")
    other = {r[1] for r in repros if r[0] == release_id and r[1] != digest}
    if other and not flags.get("skip_conflict"):
        return dict(res, result="REPRODUCTION_CONFLICT", conflicting_digests=sorted(other))
    if digest not in tss["payload"].get("published_binaries", []) and not flags.get("skip_published"):
        return dict(res, result="BINARY_NOT_PUBLISHED")
    return dict(res, result="ACCEPTED")


def integrity_predicate(path):
    """Protected iff the file and every ancestor are owned by another uid and not writable by the effective uid."""
    uid = os.geteuid()
    p = os.path.abspath(path)
    cur = p
    while True:
        st = os.stat(cur)
        if st.st_uid == uid or os.access(cur, os.W_OK):
            return False, cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return True, None
        cur = parent


def install(binary_bytes, dest, expected_digest):
    tmp = dest + ".gov-accept.tmp"
    with open(tmp, "wb") as f:
        f.write(binary_bytes)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dest)
    reread = sha(open(dest, "rb").read())
    protected, writable_at = integrity_predicate(dest)
    return {"installed": dest, "reread_digest_equal": reread == expected_digest, "location_protected": protected,
            "first_writable_path": writable_at, "c3_capable_under_protected_install_rule": protected}


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fingerprint", required=True)
    ap.add_argument("--statements", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--install")
    ap.add_argument("binary")
    a = ap.parse_args(argv)
    data = open(a.binary, "rb").read()  # read once; never executed
    r = accept(data, a.fingerprint, load_statements(a.statements), a.target, workdir=os.environ.get("TMPDIR"))
    if a.install and r["result"] == "ACCEPTED":
        r["install"] = install(data, a.install, r["binary_digest"])
    print(json.dumps(r, indent=1, sort_keys=True))
    return 0 if r["result"] == "ACCEPTED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
