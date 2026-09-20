#!/usr/bin/env python3
"""HELD-OUT — A2 "Authentic root of trust", bullet by bullet (Contract v3:143-152).

Independent of the product's test material: every signature here is produced by this verifier's
own ed25519 signer (`lib/srrsign.py`, `cryptography`), never by `tests/certification/srr_material.rs`.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import govenv as G  # noqa: E402
import srrsign as S  # noqa: E402
import yaml  # noqa: E402


def read_lock(proj):
    return yaml.safe_load((pathlib.Path(proj) / "governance" / "framework.lock").read_text())


def variant_payload(rel, tag, marker):
    """A payload that is NOT the one embedded in this gov binary (an external release)."""
    d = G.copy_release(rel.parent, tag)
    k = d / "4.1.6" / "kernel"
    f = k / "policies" / "SECURITY_POLICY.yaml"
    f.write_text(f.read_text() + f"\n# {marker}\n")
    man = json.loads((k / "KERNEL_MANIFEST.json").read_text())
    files, ph, kmh, ver = S.measure_payload(k)
    man["files"], man["payload_hash"] = files, ph
    (k / "KERNEL_MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    return d

TAG = "t01"


def newproj(name):
    p = G.fresh(f"proj/{TAG}-{name}")
    (p / "README.md").write_text("# probe project\n")
    G.git_init(p)
    return p


def main():
    rel = G.build_release()
    owner = G.Owner(f"{TAG}-owner")
    owner.sign_release(rel / "kernel", 100)

    # ---------------------------------------------------------------- b1 (143): authenticity BEFORE staging
    # (a) unprovisioned machine, external source
    external = variant_payload(rel, f"{TAG}-external", "an external release, not this binary's payload")
    owner.sign_release(external / "4.1.6" / "kernel", 100,
                       meta_dir=external / "4.1.6" / "metadata")
    md = G.Machine(f"{TAG}-unprov")
    p1 = newproj("unprov")
    o = md.run(["--role", "orchestrator", "init", "--source",
                str(external / "4.1.6" / "kernel")], cwd=p1)
    G.check(
        "A2-b1-unprovisioned-external-source-refused-typed",
        (not o.ok) and o.code == "SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED",
        f"code={o.code}",
    )
    det = ((o.env or {}).get("error") or {}).get("details") or {}
    G.check(
        "A2-b1-refusal-states-nothing-was-staged",
        det.get("staged_for_installation") is False and "remediation" in det,
        f"staged_for_installation={det.get('staged_for_installation')}",
    )
    staging = md.state_root / "staging"
    staged_any = staging.exists() and any(staging.iterdir())
    G.check(
        "A2-b1-no-staged-payload-left-behind-on-refusal",
        not staged_any,
        f"{staging} contents={[x.name for x in staging.iterdir()] if staging.exists() else []}",
    )
    G.check(
        "A2-b1-no-kernel-installed-on-refusal",
        not (p1 / "governance" / "kernel").exists(),
        "governance/kernel absent",
    )

    # (b) provisioned machine, unsigned external source (metadata removed)
    unsigned = G.copy_release(rel.parent, f"{TAG}-unsigned")
    shutil.rmtree(unsigned / "4.1.6" / "metadata", ignore_errors=True)
    ma = G.Machine(f"{TAG}-a")
    G.check("A2-provision-ok", ma.provision(owner.root_file).ok, "gov trust provision")
    p2 = newproj("unsigned")
    o = ma.run(["--role", "orchestrator", "init", "--source", str(unsigned / "4.1.6" / "kernel")], cwd=p2)
    G.check(
        "A2-b1-provisioned-unsigned-source-refused",
        (not o.ok) and o.code == "SRR_RELEASE_UNVERIFIED",
        f"code={o.code}",
    )
    G.check("A2-b1-unsigned-nothing-installed", not (p2 / "governance" / "kernel").exists())

    # ---------------------------------------------------------------- b5 (147): pre-install tampering
    tampered = G.copy_release(rel.parent, f"{TAG}-tampered")
    victim = tampered / "4.1.6" / "kernel" / "policies" / "SECURITY_POLICY.yaml"
    victim.write_text(victim.read_text() + "\n# injected by the verifier\n")
    p3 = newproj("tampered")
    o = ma.run(["--role", "orchestrator", "init", "--source", str(tampered / "4.1.6" / "kernel")], cwd=p3)
    G.check(
        "A2-b5-tampered-payload-file-refused-typed",
        (not o.ok) and o.code in ("SRR_PAYLOAD_DIGEST_MISMATCH", "SRR_PAYLOAD_FILE_UNAUTHORISED"),
        f"code={o.code}",
    )
    G.check(
        "A2-b5-refusal-names-the-offending-file",
        "SECURITY_POLICY.yaml" in o.message,
        o.message[:160],
    )
    G.check("A2-b5-nothing-installed", not (p3 / "governance" / "kernel").exists())

    # tampered manifest (mutually consistent payload+manifest, signed metadata unchanged)
    tam2 = G.copy_release(rel.parent, f"{TAG}-tampered2")
    k = tam2 / "4.1.6" / "kernel"
    v = k / "policies" / "SECURITY_POLICY.yaml"
    v.write_text(v.read_text() + "\n# consistent rewrite\n")
    man = json.loads((k / "KERNEL_MANIFEST.json").read_text())
    files, ph, kmh, ver = S.measure_payload(k)
    man["files"] = files
    man["payload_hash"] = ph
    (k / "KERNEL_MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    p4 = newproj("tampered2")
    o = ma.run(["--role", "orchestrator", "init", "--source", str(k)], cwd=p4)
    G.check(
        "A2-b5-consistent-source-rewrite-still-refused",
        (not o.ok) and o.code.startswith("SRR_"),
        f"code={o.code}",
    )

    # ---------------------------------------------------------------- b6 (148): a source cannot mint its own identity
    selfmint = G.copy_release(rel.parent, f"{TAG}-selfmint")
    sk = selfmint / "4.1.6" / "kernel"
    shutil.rmtree(selfmint / "4.1.6" / "metadata", ignore_errors=True)
    # the source signs itself under its OWN root, placed inside the source tree
    rogue = S.new_publisher()
    (sk / ".srr").mkdir(exist_ok=True)
    S.publish(sk, sk / ".srr", rogue, 100, product=G.PRODUCT)
    (sk / ".srr" / "root.json").write_bytes(
        S.envelope(S.publisher_root(rogue, product=G.PRODUCT), rogue["root"][:2])
    )
    p5 = newproj("selfmint")
    o = ma.run(["--role", "orchestrator", "init", "--source", str(sk)], cwd=p5)
    G.check(
        "A2-b6-source-signed-by-its-own-root-refused",
        (not o.ok) and o.code in ("SRR_THRESHOLD_NOT_MET", "SRR_RELEASE_UNVERIFIED", "SRR_KEYID_MISMATCH"),
        f"code={o.code}",
    )
    # and the anchor itself cannot be taken from inside a governed project
    p5b = newproj("anchor-in-repo")
    shutil.copy(owner.root_file, p5b / "root.json")
    mfresh = G.Machine(f"{TAG}-anchor")
    o = mfresh.run(["trust", "provision", "--anchor", str(p5b / "root.json")], cwd=p5b)
    G.check(
        "A2-b6-anchor-from-repository-refused",
        (not o.ok) and o.code == "SRR_ANCHOR_FROM_REPOSITORY_REFUSED",
        f"code={o.code}",
    )

    # ---------------------------------------------------------------- authentic install (the green baseline)
    pg = newproj("green")
    o = ma.run(["--role", "orchestrator", "init", "--source", str(rel / "kernel")], cwd=pg)
    G.check("A2-authentic-install-succeeds", o.ok, o.code or "")
    ra = (o.result or {}).get("release_authenticity") or {}
    G.check(
        "A2-authentic-install-is-AUTHENTIC-CURRENT-PROVISIONED",
        ra.get("authenticity") == "AUTHENTIC"
        and ra.get("currency") == "CURRENT"
        and ra.get("posture") == "PROVISIONED"
        and ra.get("admission") == "SIGNED_RELEASE_METADATA",
        json.dumps({k: ra.get(k) for k in ("authenticity", "currency", "posture", "admission")}),
    )

    # ---------------------------------------------------------------- b7 (149): framework.lock records, not invents
    lock = read_lock(pg)
    G.check(
        "A2-b7-lock-records-authenticity-basis",
        json.dumps(lock).find("AUTHENTIC") >= 0,
        "lock carries an authenticity basis",
    )
    G.check(
        "A2-b7-lock-binds-the-verified-release-metadata-digest",
        ra.get("release_metadata_sha256")
        and ra["release_metadata_sha256"] in json.dumps(lock),
        "release_metadata_sha256 present in framework.lock",
    )
    # the lock must not vary with a machine cache path (A0-A2-03)
    pg2 = newproj("green-cache")
    o2 = ma.run(
        ["--role", "orchestrator", "init", "--source", str(rel / "kernel")],
        cwd=pg2,
        env={"XDG_CACHE_HOME": str(G.SCRATCH / "other-cache")},
    )
    lock2 = read_lock(pg2)
    ignore = {"installed_at", "verified_at", "machine_id", "installed_by", "session", "at",
              "installed_at_commit"}

    def strip(d):
        return {k: v for k, v in d.items() if k not in ignore}

    G.check(
        "A2-b7-lock-independent-of-machine-cache-path",
        strip(lock) == strip(lock2),
        "framework.lock identical across XDG_CACHE_HOME values"
        if strip(lock) == strip(lock2)
        else str({k: (lock.get(k), lock2.get(k)) for k in set(lock) | set(lock2) if lock.get(k) != lock2.get(k)})[:400],
    )

    # ---------------------------------------------------------------- b4 (146): post-install tamper detection
    # (i) naive tamper: payload only  (own project, so the green install stays clean for b10)
    tp = newproj("tamper")
    ot = ma.run(["--role", "orchestrator", "init", "--source", str(rel / "kernel")], cwd=tp)
    G.check("A2-b4-tamper-baseline-installed", ot.ok, ot.code or "")
    pol = tp / "governance" / "kernel" / "policies" / "SECURITY_POLICY.yaml"
    orig = pol.read_text()
    pol.write_text(orig + "\n# post-install tamper\n")
    o = ma.run(["kernel", "verify"], cwd=tp)
    G.check(
        "A2-b4-naive-post-install-tamper-detected",
        (not o.ok) or not (o.result or {}).get("ok", True),
        f"ok={o.ok} code={o.code}",
    )
    # (ii) consistent rewrite: payload + KERNEL_MANIFEST + framework.lock (BC-P2-35)
    kd = tp / "governance" / "kernel"
    man = json.loads((kd / "KERNEL_MANIFEST.json").read_text())
    files, ph, kmh, ver = S.measure_payload(kd)
    man["files"] = files
    man["payload_hash"] = ph
    (kd / "KERNEL_MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    files2, ph2, kmh2, _ = S.measure_payload(kd)
    lp = tp / "governance" / "framework.lock"
    lk = yaml.safe_load(lp.read_text())
    for key, val in (("kernel_manifest_hash", kmh2), ("release_hash", ph2)):
        if key in lk:
            lk[key] = val
    lp.write_text(yaml.safe_dump(lk, sort_keys=False))
    o = ma.run(["kernel", "verify"], cwd=tp)
    consistent_detected = (not o.ok) or not (o.result or {}).get("ok", True)
    G.check(
        "A2-b4-consistent-post-install-rewrite-detected (BC-P2-35)",
        consistent_detected,
        f"ok={o.ok} result={json.dumps(o.result)[:300] if o.result else o.code}",
    )
    o2 = ma.run(["kernel", "trust"], cwd=tp)
    G.check(
        "A2-b4-kernel-trust-reports-the-rewrite",
        json.dumps(o2.result or o2.env)[:4000].find("PROTECTED") >= 0
        or (not o2.ok)
        or not (o2.result or {}).get("verified", True),
        json.dumps(o2.result)[:300] if o2.result else o2.code,
    )
    o3 = ma.run(["doctor"], cwd=tp)
    doctor_txt = json.dumps(o3.env)
    G.check(
        "A2-b4-doctor-does-not-report-HEALTHY-over-a-rewritten-kernel",
        not (o3.ok and (o3.result or {}).get("verdict") == "HEALTHY"),
        f"verdict={(o3.result or {}).get('verdict')}",
    )
    # restore
    pol.write_text(orig)

    # ---------------------------------------------------------------- b2 (144): integrity != authenticity
    st = ma.run(["trust", "status"], cwd=pg).result or {}
    sep = st.get("separation") or {}
    G.check(
        "A2-b2-three-predicates-reported-separately",
        {"authentic", "intact", "admissible"} <= set(sep.keys()),
        json.dumps(sep)[:200],
    )
    kt = ma.run(["kernel", "trust"], cwd=pg).result or {}
    G.check(
        "A2-b2-kernel-trust-is-an-integrity-verdict-not-an-authenticity-one",
        "authentic" not in json.dumps(kt).lower().replace("authenticity_basis", "")
        or "intact" in json.dumps(kt).lower(),
        json.dumps(kt)[:200],
    )

    # ---------------------------------------------------------------- b8 (150): bootstrap cannot masquerade
    mb = G.Machine(f"{TAG}-boot")
    pb = newproj("bootstrap")
    o = mb.run(["--role", "orchestrator", "init"], cwd=pb)
    G.check("A2-b8-bootstrap-install-succeeds-unprovisioned", o.ok, o.code or "")
    rb = (o.result or {}).get("release_authenticity") or {}
    G.check(
        "A2-b8-bootstrap-marked-and-UNKNOWN",
        rb.get("authenticity") == "UNKNOWN"
        and rb.get("admission") == "BOOTSTRAP_EMBEDDED_PAYLOAD"
        and (rb.get("bootstrap") or {}).get("mode") == "BOOTSTRAP_EMBEDDED_PAYLOAD",
        json.dumps({k: rb.get(k) for k in ("authenticity", "admission")}),
    )
    envelope_presented = (o.env or {}).get("release_trust") or {}
    G.check(
        "A2-b8-command-envelope-does-not-present-bootstrap-as-CURRENT",
        envelope_presented.get("presented_as") != "CURRENT",
        f"presented_as={envelope_presented.get('presented_as')}",
    )
    sb = mb.run(["status"], cwd=pb)
    G.check(
        "A2-b8-status-discloses-bootstrap",
        "BOOTSTRAP" in json.dumps(sb.env),
        "status envelope mentions BOOTSTRAP",
    )
    db = mb.run(["doctor"], cwd=pb)
    G.check(
        "A2-b8-doctor-discloses-bootstrap",
        "BOOTSTRAP" in json.dumps(db.env),
        "doctor envelope mentions BOOTSTRAP",
    )
    ab = mb.run(["--role", "orchestrator", "audit"], cwd=pb)
    G.check(
        "A2-b8-audit-discloses-bootstrap",
        "BOOTSTRAP" in json.dumps(ab.env),
        "audit envelope mentions BOOTSTRAP",
    )
    # and no role can mint a CERTIFIED release
    o = ma.run(
        ["--role", "orchestrator", "release", "build", "--version", "9.9.9",
         "--canonical", str(G.WT), "--out", str(G.SCRATCH / f"{TAG}-certmint"),
         "--certification", "CERTIFIED"],
    )
    G.check(
        "A2-b8-unsigned-CERTIFIED-claim-refused",
        (not o.ok) and o.code == "RELEASE_CERTIFICATION_REQUIRES_SIGNED_METADATA",
        f"code={o.code}",
    )

    # ---------------------------------------------------------------- b9 (151): rotation / revocation / recovery
    # rotation: root v2 revokes the release key by omission
    pub2 = dict(owner.pub)
    pub2["release"] = S.Key()  # new release key; the old one is revoked by omission
    doc2 = S.publisher_root(pub2, version=2, product=G.PRODUCT)
    root2 = owner.dir / "root-2.json"
    root2.write_bytes(S.envelope(doc2, owner.pub["root"][:2] + pub2["root"][:2]))
    mrot = G.Machine(f"{TAG}-rot")
    G.check("A2-b9-rotation-machine-provisioned", mrot.provision(owner.root_file).ok)
    o = mrot.run(["trust", "root-update", "--anchor", str(root2)])
    G.check("A2-b9-root-succession-accepted", o.ok, o.code or "")
    G.check(
        "A2-b9-succession-reports-revoked-keys",
        owner.pub["release"].keyid in ((o.result or {}).get("revoked_keyids") or []),
        json.dumps((o.result or {}).get("revoked_keyids"))[:200],
    )
    # a release signed by the revoked key is now refused
    revoked_rel = G.copy_release(rel.parent, f"{TAG}-revoked")
    S.publish(revoked_rel / "4.1.6" / "kernel", revoked_rel / "4.1.6" / "metadata",
              owner.pub, 101, product=G.PRODUCT)
    p6 = newproj("revoked")
    o = mrot.run(["--role", "orchestrator", "init", "--source", str(revoked_rel / "4.1.6" / "kernel")], cwd=p6)
    G.check(
        "A2-b9-release-signed-by-revoked-key-refused",
        (not o.ok) and o.code == "SRR_THRESHOLD_NOT_MET",
        f"code={o.code}",
    )
    # version gap refused
    doc4 = S.publisher_root(pub2, version=4, product=G.PRODUCT)
    root4 = owner.dir / "root-4.json"
    root4.write_bytes(S.envelope(doc4, pub2["root"][:2]))
    o = mrot.run(["trust", "root-update", "--anchor", str(root4)])
    G.check(
        "A2-b9-root-succession-gap-refused",
        (not o.ok) and o.code == "SRR_ROOT_VERSION_NOT_SUCCESSOR",
        f"code={o.code}",
    )
    # replay of the outgoing root refused
    o = mrot.run(["trust", "root-update", "--anchor", str(owner.root_file)])
    G.check(
        "A2-b9-root-replay-refused",
        (not o.ok) and o.code == "SRR_ROOT_VERSION_NOT_SUCCESSOR",
        f"code={o.code}",
    )
    # re-provisioning a provisioned machine refused
    o = mrot.run(["trust", "provision", "--anchor", str(root2)])
    G.check(
        "A2-b9-reprovision-refused",
        (not o.ok) and o.code == "SRR_ALREADY_PROVISIONED",
        f"code={o.code}",
    )
    # recovery: break-glass needs an owner signature, not a flag
    mr = G.Machine(f"{TAG}-recov")
    G.check("A2-b9-recovery-machine-provisioned", mr.provision(owner.root_file).ok)
    prv = newproj("recov")
    o = mr.run(["--role", "orchestrator", "init", "--source", str(rel / "kernel")], cwd=prv)
    G.check("A2-b9-recovery-baseline-installed", o.ok, o.code or "")
    # A release the machine must refuse as below its floor: a higher version string (so the
    # up-to-date comparison is passed) published at a sequence below the machine's high-water.
    old = G.copy_release(rel.parent, f"{TAG}-belowfloor")
    ok_ = old / "4.1.6" / "kernel"
    ky = yaml.safe_load((ok_ / "KERNEL.yaml").read_text())
    ky["version"] = "4.1.7"
    ky.setdefault("supported_from_versions", []).append("4.1.6")
    (ok_ / "KERNEL.yaml").write_text(yaml.safe_dump(ky, sort_keys=False))
    (ok_ / "migrations").mkdir(exist_ok=True)
    (ok_ / "migrations" / "M-4.1.6-4.1.7.yaml").write_text(yaml.safe_dump({
        "id": "M-4.1.6-4.1.7", "schema_version": "1.3.0", "from_version": "4.1.6",
        "to_version": "4.1.7", "description": "held-out probe migration (no-op)",
        "breaking": False, "human_gate": "none", "operations": []}, sort_keys=False))
    manb = json.loads((ok_ / "KERNEL_MANIFEST.json").read_text())
    fb, phb, kmhb, _ = S.measure_payload(ok_)
    manb["files"], manb["payload_hash"], manb["version"] = fb, phb, "4.1.7"
    (ok_ / "KERNEL_MANIFEST.json").write_text(json.dumps(manb, indent=2) + "\n")
    owner.sign_release(ok_, 50, meta_dir=old / "4.1.6" / "metadata", release_version="4.1.7")
    o = mr.run(["--role", "orchestrator", "update", "--apply", "--source", str(ok_)], cwd=prv)
    G.check(
        "A2-b9-below-floor-refused-without-owner-authorisation",
        not o.ok,
        f"code={o.code} out={o.text[:300]}",
    )
    o = mr.run(["--role", "orchestrator", "update", "--apply", "--break-glass",
                "--source", str(ok_)], cwd=prv)
    lockv = yaml.safe_load((prv / "governance" / "framework.lock").read_text()).get("version")
    G.check(
        "A2-b9-break-glass-flag-alone-is-not-authority",
        (o.result or {}).get("applied") is not True and lockv == "4.1.6",
        f"code={o.code} applied={(o.result or {}).get('applied')} "
        f"reason={(o.result or {}).get('reason')} installed_version={lockv}",
    )
    for var in ("GOV_BREAK_GLASS", "GOV_TRUST_OVERRIDE", "GOV_SKIP_VERIFY", "GOV_HUMAN_GATE_APPROVED"):
        o = mr.run(["--role", "orchestrator", "kernel", "reinstall",
                    "--source", str(rel / "kernel")], cwd=prv, env={var: "1"})
        G.check(
            f"A2-b9-env-{var}-cannot-create-authority",
            (not o.ok) and o.code == "SRR_ENV_CANNOT_CREATE_AUTHORITY",
            f"code={o.code}",
        )

    # ---------------------------------------------------------------- b10 (152): offline verification
    offline = G.copy_release(rel.parent, f"{TAG}-offline")
    shutil.rmtree(offline / "4.1.6" / "metadata", ignore_errors=True)
    o = ma.run(["--role", "orchestrator", "kernel", "reinstall",
                "--source", str(offline / "4.1.6" / "kernel")], cwd=pg)
    G.check(
        "A2-b10-offline-reinstall-from-protected-record-succeeds",
        o.ok,
        f"code={o.code} msg={o.message[:200]}",
    )
    if o.ok:
        auth = (o.result or {}).get("release_authenticity") or (o.result or {}).get("authenticated_release") or o.result
        G.check(
            "A2-b10-offline-authenticity-is-PREVIOUSLY_VERIFIED_BY_THIS_MACHINE",
            "PREVIOUSLY_VERIFIED_BY_THIS_MACHINE" in json.dumps(o.result),
            json.dumps(o.result)[:300],
        )
    # a payload this machine never verified is refused offline
    unknown = G.copy_release(rel.parent, f"{TAG}-unknown")
    shutil.rmtree(unknown / "4.1.6" / "metadata", ignore_errors=True)
    u = unknown / "4.1.6" / "kernel" / "policies" / "SECURITY_POLICY.yaml"
    u.write_text(u.read_text() + "\n# never verified\n")
    man = json.loads((unknown / "4.1.6" / "kernel" / "KERNEL_MANIFEST.json").read_text())
    f2, ph2, kmh2, _ = S.measure_payload(unknown / "4.1.6" / "kernel")
    man["files"], man["payload_hash"] = f2, ph2
    (unknown / "4.1.6" / "kernel" / "KERNEL_MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    o = ma.run(["--role", "orchestrator", "kernel", "reinstall",
                "--source", str(unknown / "4.1.6" / "kernel")], cwd=pg)
    G.check(
        "A2-b10-offline-unknown-payload-refused",
        (not o.ok),
        f"code={o.code}",
    )
    G.check(
        "A2-b10-offline-refusal-leaves-installation-unchanged",
        (((o.env or {}).get("error") or {}).get("details") or {}).get("installation_changed") is False
        or o.code in ("KERNEL_MISMATCH", "SRR_RELEASE_UNVERIFIED"),
        f"code={o.code}",
    )

    # ---------------------------------------------------------------- b3 (145): all ingresses share the root
    ing = {}
    for name, args in (
        ("init", ["--role", "orchestrator", "init", "--source", "{src}"]),
        ("update", ["--role", "orchestrator", "update", "--apply", "--source", "{src}"]),
        ("reinstall", ["--role", "orchestrator", "kernel", "reinstall", "--source", "{src}"]),
    ):
        pp = newproj(f"ing-{name}")
        if name != "init":
            ma.run(["--role", "orchestrator", "init", "--source", str(rel / "kernel")], cwd=pp)
        a = [x.replace("{src}", str(tampered / "4.1.6" / "kernel")) for x in args]
        o = ma.run(a, cwd=pp)
        ing[name] = o.code
        G.check(
            f"A2-b3-ingress-{name}-refuses-a-tampered-source"
            + (" [V1-S5-01: the update ingress reports 'already up to date' instead]"
               if name == "update" else ""),
            (not o.ok) and o.code.startswith(("SRR_", "KERNEL_")),
            f"code={o.code} out={o.text[:200] if not o.code else ''}",
        )
    prb = newproj("ing-rollback")
    ma.run(["--role", "orchestrator", "init", "--source", str(rel / "kernel")], cwd=prb)
    orb = ma.run(["--role", "orchestrator", "update", "--rollback"], cwd=prb)
    G.check(
        "A2-b3-ingress-rollback-refuses-when-there-is-nothing-it-verified-to-return-to",
        (not orb.ok) and orb.code == "SNAPSHOT_MISSING",
        f"code={orb.code} (`update --rollback` takes no --source: it restores the snapshot the "
        f"previous update wrote, and every rollback consumes its snapshot)",
    )
    # adopt ingress
    pa = newproj("ing-adopt")
    o = ma.run(["--role", "orchestrator", "adopt", "baseline"], cwd=pa)
    ing["adopt-baseline"] = o.code
    print("ingress refusal codes:", json.dumps(ing))

    return G.summary()


if __name__ == "__main__":
    sys.exit(main())
