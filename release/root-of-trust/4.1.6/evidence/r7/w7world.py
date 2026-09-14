#!/usr/bin/env python3
"""w7world — deterministic signed world for the revision-7 reference instruments (AR-0019). EVIDENCE ONLY.

Keys are Ed25519, derived from labels (SHA-256 seed), signatures real. The world follows FA5's timeline shape (AR-0011): at T7 the
genuine B7 and the malicious B7x (from a remediated compromise of two registration keys and two reproducer keys) are published;
T9 revokes both and root v2 rotates the compromised keys out; T10 and T11 are current. It adds what CP-1 requires: 3-of-3 root
key shape with threshold 2; dedicated 2-of-3 trust-state, revocation and registration authorities; release-final threshold 2;
two verifier keys; three reproducer keys; a first-contact authority record (FCA) at root threshold; a Trust Policy with the
supplier and toolchain provenance registries and certified targets.

Clock: NOW = 2026-09-14T06:00:00Z. T11 issued 6 h before NOW (within the 24 h admission ceiling); T10 18 h before NOW; T9 and
earlier are older than 24 h.
"""
import base64, copy, hashlib, json, os, sys

sys.dont_write_bytecode = True
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util

_spec = importlib.util.spec_from_file_location("gov_admit_reference_r7", os.path.join(HERE, "gov_admit_reference_r7.py"))
GA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(GA)

NOW = "2026-09-14T06:00:00Z"
TARGET = "x86_64-unknown-linux-musl"
UNCERTIFIED_TARGET = "aarch64-unknown-linux-musl"
PROFILE = GA.PROFILE_ID
KEYS = {}


def key(label):
    if label not in KEYS:
        sk = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"rot1r7:" + label.encode()).digest())
        raw = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        KEYS[label] = (sk, raw, "ed25519:" + hashlib.sha256(raw).hexdigest())
    return KEYS[label]


kid = lambda l: key(l)[2]
pub_map = lambda ls: {kid(l): base64.b64encode(key(l)[1]).decode() for l in ls}
canon, sha256d = GA.canon, GA.sha256d


def envelope(suffix, payload, signer_labels):
    body = canon(payload)
    pt = GA.TYPE_PREFIX + suffix
    sigs = [{"keyid": kid(s), "sig": base64.b64encode(key(s)[0].sign(GA.pae(pt, body))).decode()} for s in signer_labels]
    return {"payload": payload, "digest": sha256d(body), "env": {"payloadType": pt, "payload": base64.b64encode(body).decode(), "signatures": sigs}}


def to_stmts(envs):
    out = []
    for e in envs:
        s = GA.parse_envelope(e["env"])
        if s is not None:
            out.append(s)
    return out


ADMITTER_BYTES = open(os.path.join(HERE, "gov_admit_reference_r7.py"), "rb").read()
ADM_D = sha256d(ADMITTER_BYTES)
SUB_ADM = b"#!/bin/sh\n# substituted admitter: admits every candidate\n"
SUB_ADM_D = sha256d(SUB_ADM)

ROOT_KEYS = ["r1", "r2", "r3"]
V1_KEYS = ROOT_KEYS + ["ts1", "ts2", "ts3", "rv1", "rv2", "rv3", "g1", "g2", "g3", "p1", "p2", "p3", "v1", "v2", "f1", "f2", "c1", "cs1", "cs2", "rp1"]
V2_KEYS = V1_KEYS + ["g4", "p4"]


def grants(reg=("g1", "g2", "g3"), rep=("p1", "p2", "p3"), **over):
    g = {"root": {"keys": [kid(x) for x in ROOT_KEYS], "threshold": 2}, "trust-policy": {"keys": [kid(x) for x in ROOT_KEYS], "threshold": 2},
         "first-contact-authority": {"keys": [kid(x) for x in ROOT_KEYS], "threshold": 2},
         "trust-state": {"keys": [kid(x) for x in ("ts1", "ts2", "ts3")], "threshold": 2}, "revocation": {"keys": [kid(x) for x in ("rv1", "rv2", "rv3")], "threshold": 2},
         "release-registration": {"keys": [kid(x) for x in reg], "threshold": 2}, "reproducer": {"keys": [kid(x) for x in rep], "threshold": 1},
         "verification-attestation": {"keys": [kid(x) for x in ("v1", "v2")], "threshold": 1}, "release-final": {"keys": [kid(x) for x in ("f1", "f2")], "threshold": 2},
         "release-candidate": {"keys": [kid("c1")], "threshold": 1}, "certification-status": {"keys": [kid(x) for x in ("cs1", "cs2")], "threshold": 2},
         "retrieval-profile": {"keys": [kid("rp1")], "threshold": 1}}
    g.update(over)
    return g


def root_payload(version, previous, keys, g, revoked=()):
    return {"version": version, "previous_digest": previous, "keys": pub_map(keys), "grants": g, "quorums": {"reproducer": 2}, "revoked_keys": [kid(x) for x in revoked], "profile_id": PROFILE}


ROOT1 = envelope("root+json", root_payload(1, None, V1_KEYS, grants()), ["r1", "r2"])
LINEAGE = ROOT1["digest"]
ROOT2 = envelope("root+json", root_payload(2, LINEAGE, V2_KEYS, grants(reg=("g3", "g4", "g2"), rep=("p3", "p4", "p2")), revoked=("g1", "p1")), ["r1", "r3"])

SUPPLIERS = [
    {"supplier_id": "sup-A", "provenance": {"base_image_lineage": "debian-bookworm-images", "package_source": "deb.debian.org", "build_system": "debian-buildd", "signing_infrastructure": "debian-archive-keyring"},
     "checksum_keys": [kid("upA")]},
    {"supplier_id": "sup-B", "provenance": {"base_image_lineage": "alpine-3.20-images", "package_source": "dl-cdn.alpinelinux.org", "build_system": "alpine-builders", "signing_infrastructure": "alpine-keys"},
     "checksum_keys": [kid("upB")]},
    {"supplier_id": "sup-A-mirror", "provenance": {"base_image_lineage": "debian-bookworm-images", "package_source": "mirror.example.invalid/debian", "build_system": "debian-buildd", "signing_infrastructure": "debian-archive-keyring"},
     "checksum_keys": [kid("upA")]},
]
TOOLCHAINS = [
    {"toolchain_id": "tc-up", "provenance": {"bootstrap_root": "upstream-binary-stage0", "package_source": "static.rust-lang.org", "build_system": "rust-ci", "signing_infrastructure": "rust-release-key"}},
    {"toolchain_id": "tc-boot", "provenance": {"bootstrap_root": "mrustc-source-bootstrap", "package_source": "owner-source-mirror", "build_system": "owner-bootstrap-builders", "signing_infrastructure": "owner-registration-quorum"}},
    {"toolchain_id": "tc-up-relabelled", "provenance": {"bootstrap_root": "upstream-binary-stage0", "package_source": "static.rust-lang.org", "build_system": "rust-ci", "signing_infrastructure": "rust-release-key"}},
]


def tps_payload(version=1, min_seq=1, **over):
    p = {"policy_version": version, "profile_id": PROFILE, "gating": {"mode": "always_gate"}, "registration": {"min_verification_records": 2},
         "eligibility": {"min_release_sequence": min_seq, "min_binary_version": "4.1.6"}, "bootstrap": {"accepted_tbm_reset": None},
         "supply_chain": {"suppliers": SUPPLIERS, "toolchains": TOOLCHAINS}, "certified_targets": [{"target": TARGET, "status": "CERTIFIED"}]}
    p.update(over)
    return p


TPS1 = envelope("trust-policy+json", tps_payload(), ["r1", "r2"])
PROCEDURE_TEXT = b"FC-PROC-1 (32 FC-1' ... FC-3'): read both sources; compare trust codes, state codes and this procedure's digest; sha256sum the authority payload and gov-admit.\n"
PROCEDURE_DIGEST = sha256d(PROCEDURE_TEXT)
SOURCES = [{"source_id": "src-private", "kind": "authenticated-private-release-channel", "locator": "https://releases.owner.invalid/private", "custodian_role": "release-channel-custodian", "custody_domain": "owner-release-operations"},
           {"source_id": "src-mirror", "kind": "immutable-release-mirror", "locator": "https://mirror.owner-archive.invalid/immutable", "custodian_role": "archive-custodian", "custody_domain": "owner-archive-trust"}]


def fca_payload(seq, admitters, root_version=1, certified=(TARGET,), sources=None, lineage=None, issued="2026-01-01T00:00:00Z"):
    return {"fca_sequence": seq, "lineage": lineage or LINEAGE, "root_version": root_version, "profile_id": PROFILE, "admitters": admitters,
            "certified_targets": list(certified), "sources": sources or SOURCES, "procedure_digest": PROCEDURE_DIGEST, "issued_at": issued}


FCA1 = envelope("first-contact-authority+json", fca_payload(1, {TARGET: ADM_D}), ["r1", "r2"])
FCA2 = envelope("first-contact-authority+json", fca_payload(2, {TARGET: ADM_D}, root_version=2, issued="2026-07-01T00:00:00Z"), ["r2", "r3"])


def src(tag):
    return {"release_commit": hashlib.sha1(("c-" + tag).encode()).hexdigest(), "git_tree": hashlib.sha1(("t-" + tag).encode()).hexdigest(), "content_digest": sha256d(("tree-" + tag).encode())}


ENV_A = sha256d(b"environment-manifest-A")
ENV_B = sha256d(b"environment-manifest-B")
ENV_AM = sha256d(b"environment-manifest-A-mirror")


def make_tbm(tag, rv, pv, seq, source, inp, lineage=None, version="4.1.6"):
    return {"build": "release", "profile_id": PROFILE, "lineage": lineage or LINEAGE, "root_version": rv, "policy_version": pv, "state_sequence": seq,
            "source": source, "inputs_manifest_digest": inp, "version": version, "name": "gov", "tag": tag}


def make_binary(tag, tbm, marker="genuine"):
    b = ("#!/bin/sh\n# GOV-TBM %s\n# %s %s\n" % (canon(tbm).decode(), tag, marker)).encode()
    return b, sha256d(b)


class Release:
    def __init__(self, tag, seq, rv, pv, state_seq, reg_signers, rep_signers, final_signers=("f1", "f2"), security_relevant_change=False,
                 envs=((ENV_A, "sup-A"), (ENV_B, "sup-B")), toolchains=("tc-up", "tc-boot"), rep_plan=None, marker="genuine", binary_tag=None):
        self.tag, self.seq = tag, seq
        self.source, self.inputs = src(tag), sha256d(("inputs-" + tag).encode())
        self.cand = sha256d(canon({"kind": "candidate", "release_id": tag, "source": self.source}))
        self.kernel = sha256d(("kernel-" + tag).encode())
        self.tbm = make_tbm(tag, rv, pv, state_seq, self.source, self.inputs)
        self.binary, self.D = make_binary(binary_tag or tag, self.tbm, marker)
        self.tbm_d = sha256d(canon(self.tbm))
        self.final = envelope("release-final+json", {"release_id": tag, "sequence": seq, "promoted_from": self.cand, "source": self.source, "kernel_tree_digest": self.kernel}, list(final_signers))
        env_ids = [e for e, _ in envs]
        self.atts = [envelope("verification-attestation+json", {"candidate_statement_digest": self.cand, "verdict": "ACCEPTED", "source": self.source, "inputs_manifest_digest": self.inputs,
                                                                "kernel_tree_digest": self.kernel, "environment_ids": env_ids, "toolchain_ids": list(toolchains),
                                                                "verification_report_digest": sha256d(("report-%s-%s" % (tag, v)).encode()), "verifier_execution_id": "exec-%s-%s" % (tag, v)}, [v])
                     for v in ("v1", "v2")]
        self.envs, self.toolchains = list(envs), list(toolchains)
        self.security_relevant_change = security_relevant_change
        self.reg_signers = list(reg_signers)
        self.reg = self._registration()
        plan = rep_plan or [(rep_signers[0], envs[0][0], toolchains[0]), (rep_signers[1], envs[1][0], toolchains[1])]
        self.reps = [self.reproduction(k, e, t) for k, e, t in plan]

    def _registration(self, **over):
        p = {"release_id": self.tag, "sequence": self.seq, "final_statement_digest": self.final["digest"], "candidate_statement_digest": self.cand, "source": self.source,
             "inputs_manifest_digest": self.inputs, "targets": [TARGET, UNCERTIFIED_TARGET], "verification_records": [a["digest"] for a in self.atts],
             "constitution": {"kernel_tree_digest": self.kernel, "units": {}}, "environments": [{"target": TARGET, "environment_id": e, "supplier_id": s} for e, s in self.envs],
             "toolchains": [{"target": TARGET, "toolchain_id": t} for t in self.toolchains], "binary_digests": {TARGET: self.D}, "security_relevant_change": self.security_relevant_change,
             "environment_lock_digest": sha256d(("lock-" + self.tag).encode())}
        p.update(over)
        return envelope("release-registration+json", p, self.reg_signers)

    def reproduction(self, signer, env, tc, digest=None, tbm_d=None):
        return envelope("binary-reproduction+json", {"release_id": self.tag, "source": self.source, "inputs_manifest_digest": self.inputs, "target": TARGET,
                                                     "binary_digest": digest or self.D, "tbm_digest": tbm_d or self.tbm_d, "environment_id": env, "toolchain_id": tc}, [signer])

    def all(self):
        return [self.final, self.reg] + self.atts + self.reps


R7 = Release("R7", 7, 1, 1, 5, ("g1", "g2"), ("p2", "p3"))
R7X = Release("R7x", 7, 1, 1, 5, ("g1", "g2"), ("p1", "p2"), marker="MALICIOUS-REVOKED", binary_tag="R7x")  # remediated compromise (g1, p1 rotated out at root v2)
R8 = Release("R8", 8, 2, 1, 9, ("g2", "g3"), ("p3", "p4"))
R9 = Release("R9", 9, 2, 1, 10, ("g3", "g4"), ("p2", "p4"), security_relevant_change=True)


def tss(seq, issued, root_env, rv, policy_env, fca_env, prior, regs, pubs, revs, signers=("ts1", "ts2"), revocation_statements=()):
    return envelope("trust-state+json", {"sequence": seq, "issued_at": issued, "references": {"root": {"version": rv, "digest": root_env["digest"]},
                                                                                              "trust_policy": {"version": policy_env["payload"]["policy_version"], "digest": policy_env["digest"]},
                                                                                              "first_contact_authority": {"fca_sequence": fca_env["payload"]["fca_sequence"], "digest": fca_env["digest"]}},
                                         "prior_states": prior, "registrations": regs, "published_binaries": pubs, "revocations": sorted(revs),
                                         "revocation_statements": list(revocation_statements)}, list(signers))


T5 = tss(5, "2026-03-01T00:00:00Z", ROOT1, 1, TPS1, FCA1, [], [], [], [])
T7 = tss(7, "2026-05-01T00:00:00Z", ROOT1, 1, TPS1, FCA1, [{"sequence": 5, "digest": T5["digest"]}], [R7.reg["digest"], R7X.reg["digest"]], [R7.D, R7X.D], [])
REVOC9 = envelope("revocation+json", {"revokes": sorted([R7.D, R7X.D, R7X.reg["digest"]]), "reason": "remediated compromise of g1 and p1; R7 enforcement defect"}, ["rv1", "rv2"])
PRIOR9 = [{"sequence": 5, "digest": T5["digest"]}, {"sequence": 7, "digest": T7["digest"]}]
T9 = tss(9, "2026-07-01T00:00:00Z", ROOT2, 2, TPS1, FCA2, PRIOR9, [R7.reg["digest"], R7X.reg["digest"], R8.reg["digest"]], [R7.D, R7X.D, R8.D],
         [R7.D, R7X.D, R7X.reg["digest"]], signers=("ts2", "ts3"), revocation_statements=[REVOC9["digest"]])
PRIOR10 = PRIOR9 + [{"sequence": 9, "digest": T9["digest"]}]
T10 = tss(10, "2026-09-13T12:00:00Z", ROOT2, 2, TPS1, FCA2, PRIOR10, T9["payload"]["registrations"], T9["payload"]["published_binaries"], T9["payload"]["revocations"],
          revocation_statements=[REVOC9["digest"]])
TPS2 = envelope("trust-policy+json", tps_payload(version=2, min_seq=9), ["r1", "r3"])
REVOC11 = envelope("revocation+json", {"revokes": [R8.D], "reason": "R8 enforcement defect found at T11"}, ["rv2", "rv3"])
PRIOR11 = PRIOR10 + [{"sequence": 10, "digest": T10["digest"]}]
T11 = tss(11, "2026-09-14T00:00:00Z", ROOT2, 2, TPS2, FCA2, PRIOR11, T10["payload"]["registrations"] + [R9.reg["digest"]], T10["payload"]["published_binaries"] + [R9.D],
          T10["payload"]["revocations"] + [R8.D], revocation_statements=[REVOC9["digest"], REVOC11["digest"]])

BASE = [ROOT1, ROOT2, TPS1, TPS2, FCA1, FCA2, T5, T7, T9, T10, T11, REVOC9, REVOC11]
FULL = BASE + R7.all() + R7X.all() + R8.all() + R9.all()


def codes(fca_env, tss_env, lineage=None):
    lin = lineage or LINEAGE
    return (GA.trust_code(lin, fca_env["payload"]["fca_sequence"], fca_env["digest"]), GA.state_code(lin, tss_env["payload"]["sequence"], tss_env["digest"]))


def pages(fca_env, tss_env, n=2, procedure=PROCEDURE_DIGEST):
    tc, sc = codes(fca_env, tss_env)
    return [{"trust_code": tc, "state_code": sc, "procedure_digest": procedure} for _ in range(n)]


def admit(binary, fca_env, tss_env, bundle, path="workstation", now=NOW, evaluator=ADM_D, store=None, flags=None, verifier=None, workdir=None, k=2, target=TARGET, offered=None):
    tc, sc = codes(fca_env, tss_env)
    return GA.accept(binary, [tc] * k, [sc] * k, to_stmts(bundle), target, evaluator, path, now, {"lineage": LINEAGE}, store_floors=store, flags=flags,
                     verifier=verifier, workdir=workdir, offered=offered)


def floors_from(tss_env, root_version, policy_version, fca_seq, accepted_tbm, security_minimum=0):
    p = tss_env["payload"]
    return {"state_sequence": p["sequence"], "state_digest": tss_env["digest"], "root_version": root_version, "policy_version": policy_version, "fca_sequence": fca_seq,
            "negatives": sorted(p["revocations"]), "accepted_tbm": accepted_tbm, "security_minimum": security_minimum}


def attacker_lineage_world(admitter_digest=ADM_D):
    """Every key attacker-generated; CP-1 shapes, so only the lineage differs."""
    L = lambda n: "atk:" + n
    keys = [L(x) for x in V1_KEYS]
    g = {p: {"keys": [kid(L(x)) for x in _labels(p)], "threshold": grants()[p]["threshold"]} for p in grants()}
    root1 = envelope("root+json", {"version": 1, "previous_digest": None, "keys": pub_map(keys), "grants": g, "quorums": {"reproducer": 2}, "revoked_keys": [], "profile_id": PROFILE},
                     [L("r1"), L("r2")])
    lin = root1["digest"]
    tps = envelope("trust-policy+json", tps_payload(), [L("r1"), L("r2")])
    fca = envelope("first-contact-authority+json", fca_payload(1, {TARGET: admitter_digest}, lineage=lin), [L("r1"), L("r2")])
    return {"root1": root1, "lineage": lin, "tps": tps, "fca": fca}


def _labels(p):
    m = {"root": ROOT_KEYS, "trust-policy": ROOT_KEYS, "first-contact-authority": ROOT_KEYS, "trust-state": ["ts1", "ts2", "ts3"], "revocation": ["rv1", "rv2", "rv3"],
         "release-registration": ["g1", "g2", "g3"], "reproducer": ["p1", "p2", "p3"], "verification-attestation": ["v1", "v2"], "release-final": ["f1", "f2"],
         "release-candidate": ["c1"], "certification-status": ["cs1", "cs2"], "retrieval-profile": ["rp1"]}
    return m[p]
