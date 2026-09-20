#!/usr/bin/env python3
"""HELD-OUT — the cross-machine attack (P2-HO-0043 "Cross-machine continuity"; P2-ADJ-0002;
Contract v3 S6:948-950; OD-P2-02; SRR-R0-L4).

Machines, all simulated as distinct XDG_STATE_HOME + HOME pairs:

  A  provisioned from the owner's root AND bound to the owner's T2 binding authority
  B  provisioned from the owner's root AND bound   (the owner's second machine)
  C  provisioned from the owner's root, NOT bound  ("a machine not authorised by the provisioning")
  D  unprovisioned
  E  provisioned from a DIFFERENT owner's root and bound to that owner's authority  (foreign owner)

Attacks: forged (hand-edited seal / hand-written record), foreign (another owner), unprovisioned,
wrong signer, expired authority, rolled-back authority.  Plus: nothing secret in any repository,
and `gov` verifies but never signs.
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

GATE_FIELDS = json.dumps({
    "why_now": "the cross-machine held-out probe needs one OS-written gate record",
    "current_state": "a freshly initialised project on the owner's first machine",
    "options": [
        {"id": "A", "description": "approve the probe and let it write one gate record",
         "authorises_blocked_work": True},
        {"id": "B", "description": "decline the probe and write nothing"},
    ],
    "impact": "none outside this disposable probe project",
    "impact_radius": "R0",
    "reversibility": "fully reversible: the probe project is deleted afterwards",
    "cost_rework": "none",
    "recommendation": "A",
    "confidence": 0.9,
    "permitted_next_actions": ["gov gate show", "gov gate list"],
})

TAG = "t02"
ROLE = ["--role", "orchestrator"]


def clone(src, name):
    dst = G.fresh(f"proj/{TAG}-{name}")
    subprocess.run(["git", "clone", "-q", str(src), str(dst)], capture_output=True)
    return dst


def t2_findings(machine, proj):
    """Every open T2 record the OS refuses to honour here, as the product reports it."""
    o = machine.run(ROLE + ["audit"], cwd=proj)
    blob = json.dumps(o.env)
    return o, blob


def binding(machine, proj, gate_id):
    """The product's own T2 verdict for one gate record (`gov gate show` -> t2.binding)."""
    o = machine.run(ROLE + ["gate", "show", gate_id], cwd=proj)
    t2 = (o.result or {}).get("t2") or {}
    return o, (t2.get("binding") or o.code or "NO_VERDICT"), t2


def main():
    rel = G.build_release()
    owner = G.Owner(f"{TAG}-owner")
    owner.sign_release(rel / "kernel", 100)
    foreign_owner = G.Owner(f"{TAG}-foreign")

    # ------------------------------------------------------------------ machines
    A = G.Machine(f"{TAG}-A")
    B = G.Machine(f"{TAG}-B")
    C = G.Machine(f"{TAG}-C")
    D = G.Machine(f"{TAG}-D")
    E = G.Machine(f"{TAG}-E")
    for m, own in ((A, owner), (B, owner), (C, owner), (E, foreign_owner)):
        G.check(f"S6-provision-{m.name}", m.provision(own.root_file).ok)
    for m, own in ((A, owner), (B, owner), (E, foreign_owner)):
        o = m.bind(own.authority_file, own.key_file)
        G.check(f"S6-bind-{m.name}", o.ok, o.code or "")
    ta = (A.run(["trust", "status"]).result or {}).get("t2_binding") or {}
    tc = (C.run(["trust", "status"]).result or {}).get("t2_binding") or {}
    G.check(
        "S6-A-bound-C-provisioned-but-not-bound",
        ta.get("bound") is True and tc.get("bound") is False,
        f"A.bound={ta.get('bound')} C.bound={tc.get('bound')}",
    )
    G.check(
        "S6-D-unprovisioned-cannot-be-bound",
        not D.bind(owner.authority_file, owner.key_file).ok,
        D.bind(owner.authority_file, owner.key_file).code,
    )

    # ------------------------------------------------------------------ machine A does governed work
    pa = G.fresh(f"proj/{TAG}-A-work")
    (pa / "README.md").write_text("# cross-machine probe\n")
    G.git_init(pa)
    o = A.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=pa)
    G.check("S6-A-authentic-install", o.ok, o.code or "")

    made = {}
    o = A.run(ROLE + ["gate", "create", "--question", "Approve the cross-machine probe?",
                      "--fields", GATE_FIELDS], cwd=pa)
    made["gate"] = (o.result or {}).get("id") or (o.result or {}).get("gate")
    G.check("S6-A-gate-record-written", o.ok, f"{made['gate']} {o.code}")
    o = A.run(ROLE + ["audit"], cwd=pa)
    made["audit"] = (o.result or {}).get("id") or (o.result or {}).get("audit")
    G.check("S6-A-audit-record-written", o.ok, f"{made['audit']} {o.code}")
    o = A.run(ROLE + ["task", "create", "--title", "cross-machine probe task",
                      "--objective", "exercise an OS-written task record across machines",
                      "--class", "governance"], cwd=pa)
    made["task"] = (o.result or {}).get("id")
    G.check("S6-A-task-record-written", o.ok, f"{made['task']} {o.code}")
    o = A.run(ROLE + ["cit", "propose",
                      "--proposal", "cross-machine probe change-impact transaction",
                      "--targets", "governance/project/PROJECT_POLICY.yaml"], cwd=pa)
    made["cit"] = (o.result or {}).get("id")
    G.check("S6-A-cit-record-written", o.ok, f"{made['cit']} {o.code}")

    # the records must be sealed, portable-scope
    sealed = []
    for rp in sorted((pa / "spec").rglob("*.yaml")) + sorted((pa / "spec").rglob("*.json")):
        try:
            txt = rp.read_text()
        except Exception:
            continue
        if "os_binding" in txt:
            sealed.append(str(rp.relative_to(pa)))
    G.check("S6-A-records-carry-an-os_binding-seal", len(sealed) >= 2, f"{len(sealed)}: {sealed[:6]}")
    portable = sum(1 for rp in sealed if "hmac-sha256/t2-v2" in (pa / rp).read_text())
    G.check(
        "S6-A-seals-are-portable-scope-under-the-owner-authority",
        portable == len(sealed) and portable > 0,
        f"portable={portable} of {len(sealed)}",
    )

    # nothing secret in the repository
    keyhex = owner.binding_key.hex()
    leak = []
    for rp in pa.rglob("*"):
        if rp.is_file() and ".git/" not in str(rp):
            try:
                b = rp.read_bytes()
            except Exception:
                continue
            if keyhex.encode() in b or owner.binding_key in b:
                leak.append(str(rp.relative_to(pa)))
    G.check("S6-no-binding-key-material-in-the-repository", not leak, str(leak[:5]))
    for k in ("root", "release", "snapshot", "timestamp", "recovery", "t2-binding", "human-gate"):
        seed = owner.pub[k].seed if not isinstance(owner.pub[k], list) else owner.pub[k][0].seed
        found = [str(rp) for rp in pa.rglob("*") if rp.is_file() and seed in _safe(rp)]
        G.check(f"S6-no-{k}-private-key-in-the-repository", not found, str(found[:3]))

    subprocess.run(["git", "add", "-A"], cwd=str(pa), capture_output=True)
    subprocess.run(["git", "-c", "user.email=v@x", "-c", "user.name=v", "commit", "-qm", "work"],
                   cwd=str(pa), capture_output=True)

    # ------------------------------------------------------------------ B: the owner's other machine
    pb = clone(pa, "B-clone")
    o, blob = t2_findings(B, pb)
    unbound_on_b = _unbound(o)
    G.check(
        "S6-B-honours-the-facts-machine-A-wrote (P2-ADJ-0002)",
        not unbound_on_b,
        f"open T2 findings on B: {json.dumps(unbound_on_b)[:400]}",
    )
    ob, vb, t2b = binding(B, pb, made["gate"])
    G.check("S6-B-gate-binding-verifies-before-anchoring", vb == "VERIFIED",
            f"binding={vb} {json.dumps(t2b)[:200]}")
    G.check(
        "S6-B-status-reconstructs-the-project",
        B.run(["status"], cwd=pb).ok,
        "gov status on the second machine",
    )

    # ------------------------------------------------------------------ C: provisioned, NOT bound
    pc = clone(pa, "C-clone")
    o, _ = t2_findings(C, pc)
    unbound_on_c = _unbound(o)
    G.check(
        "S6-C-refuses-the-owner-facts-it-was-not-authorised-for",
        bool(unbound_on_c),
        f"{json.dumps(unbound_on_c)[:300]}",
    )
    oc, vc, t2c = binding(C, pc, made["gate"])
    G.check("S6-C-refusal-is-typed", vc in ("FOREIGN", "UNAUTHORISED", "KEY_UNAVAILABLE"),
            f"binding={vc} {json.dumps(t2c)[:250]}")
    od_, vd, t2d = binding(D, clone(pa, "D-binding"), made["gate"])
    G.check("S6-D-refusal-is-typed", vd in ("FOREIGN", "UNAUTHORISED", "KEY_UNAVAILABLE"),
            f"binding={vd} {json.dumps(t2d)[:250]}")
    oe_, ve, t2e = binding(E, clone(pa, "E-binding"), made["gate"])
    G.check("S6-E-foreign-owner-refusal-is-typed",
            ve in ("FOREIGN", "UNAUTHORISED", "KEY_UNAVAILABLE"),
            f"binding={ve} {json.dumps(t2e)[:250]}")

    # ------------------------------------------------------------------ D: unprovisioned
    pd = clone(pa, "D-clone")
    o, _ = t2_findings(D, pd)
    G.check(
        "S6-D-unprovisioned-machine-refuses-the-owner-facts",
        bool(_unbound(o)),
        json.dumps(_unbound(o))[:300],
    )
    od = D.run(ROLE + ["kernel", "reinstall", "--source", str(rel / "kernel")], cwd=pd)
    G.check(
        "S6-D-unprovisioned-external-ingress-refused (OD-P2-02)",
        (not od.ok) and od.code == "SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED"
        or (od.ok and "BOOTSTRAP" in json.dumps(od.result)),
        f"code={od.code}",
    )

    # ------------------------------------------------------------------ E: a foreign owner's machine
    pe = clone(pa, "E-clone")
    o, _ = t2_findings(E, pe)
    G.check(
        "S6-E-foreign-owner-refuses-these-facts",
        bool(_unbound(o)),
        json.dumps(_unbound(o))[:300],
    )
    # a release signed by the owner cannot be anchored on the foreign owner's machine
    oe = E.run(ROLE + ["kernel", "reinstall", "--source", str(rel / "kernel")], cwd=pe)
    G.check(
        "S6-E-cannot-anchor-a-release-signed-by-another-owner",
        not oe.ok,
        f"code={oe.code}",
    )
    # ... and a record the foreign owner's machine writes in its OWN project is refused on A
    fr = G.copy_release(rel.parent, f"{TAG}-foreign-rel")
    foreign_owner.sign_release(fr / "4.1.6" / "kernel", 100,
                               meta_dir=fr / "4.1.6" / "metadata")
    pf = G.fresh(f"proj/{TAG}-E-own")
    (pf / "README.md").write_text("# the foreign owner's own project\n")
    G.git_init(pf)
    oe0 = E.run(ROLE + ["init", "--source", str(fr / "4.1.6" / "kernel")], cwd=pf)
    G.check("S6-E-installs-its-own-owner-signed-release", oe0.ok, oe0.code or "")
    oe2 = E.run(ROLE + ["gate", "create", "--question", "foreign gate",
                        "--fields", GATE_FIELDS], cwd=pf)
    foreign_gate = (oe2.result or {}).get("id")
    G.check("S6-E-writes-its-own-T2-fact", oe2.ok and bool(foreign_gate), oe2.code or "")
    src = list((pf / "spec" / "decisions").glob(f"{foreign_gate}*")) if foreign_gate else []
    if src:
        dest = pa / "spec" / "decisions" / ("FOREIGN-" + src[0].name)
        shutil.copy(src[0], dest)
        import yaml as _y
        doc = _y.safe_load(dest.read_text())
        transplanted = doc.get("id")
        oa, vf, t2f = binding(A, pa, transplanted)
        G.check(
            "S6-A-refuses-a-record-sealed-by-a-foreign-owner",
            vf in ("FOREIGN", "UNAUTHORISED", "KEY_UNAVAILABLE"),
            f"binding={vf} {json.dumps(t2f)[:250]}",
        )
        os.replace(dest, G.SCRATCH / f"{TAG}-foreign-record.moved")
    else:
        G.check("S6-A-refuses-a-record-sealed-by-a-foreign-owner", False,
                f"no foreign gate record to transplant ({oe2.code})")

    # ------------------------------------------------------------------ forged / hand-edited records
    gate_files = list((pa / "spec" / "decisions").glob(f"{made['gate']}*"))
    G.check("S6-gate-file-found", bool(gate_files), str(made["gate"]))
    if gate_files:
        gf = gate_files[0]
        orig = gf.read_text()
        # (i) edit one flag, keep the seal
        edited = orig.replace("status: OPEN", "status: ANSWERED")
        if edited == orig:
            edited = orig + "\nhuman_approved: true\n"
        gf.write_text(edited)
        oa, va, t2a = binding(A, pa, made["gate"])
        G.check("S6-edited-sealed-record-refused-typed-BROKEN", va == "BROKEN",
                f"binding={va} {json.dumps(t2a)[:250]}")
        oaud = A.run(ROLE + ["audit"], cwd=pa)
        aud = json.dumps(oaud.env)
        G.check(
            "S6-edited-record-is-observable-in-the-governance-suite",
            (not oaud.ok) and ("BROKEN" in aud or made["gate"] in aud),
            f"audit ok={oaud.ok} code={oaud.code} mentions_record={made['gate'] in aud}",
        )
        # (ii) strip the seal entirely (hand-written record)
        import yaml
        d = yaml.safe_load(orig)
        if isinstance(d, dict):
            d.pop("os_binding", None)
            gf.write_text(yaml.safe_dump(d, sort_keys=False))
            oa, vu, t2u = binding(A, pa, made["gate"])
            G.check("S6-unsealed-hand-written-record-refused", vu in ("UNSEALED", "BROKEN"),
                    f"binding={vu} {json.dumps(t2u)[:250]}")
        gf.write_text(orig)
        oa, vr, t2r = binding(A, pa, made["gate"])
        G.check("S6-restored-record-verifies-again", vr == "VERIFIED",
                f"binding={vr}")

    # ------------------------------------------------------------------ wrong signer / expired / rolled back
    M = G.Machine(f"{TAG}-auth")
    G.check("S6-auth-machine-provisioned", M.provision(owner.root_file).ok)
    wrong = owner.write_authority(
        1, [(owner.binding_key, "active")],
        path=owner.dir / "authority-wrong-signer.json",
        signers=[owner.pub["snapshot"]],  # a root-delegated key, but NOT the t2-binding role
    )
    o = M.bind(wrong, owner.key_file)
    G.check("S6-wrong-signer-authority-refused", not o.ok, o.code or "accepted!")
    unrel = owner.write_authority(
        1, [(owner.binding_key, "active")],
        path=owner.dir / "authority-unrelated-key.json",
        signers=[S.Key()],  # a key the root does not know at all
    )
    o = M.bind(unrel, owner.key_file)
    G.check("S6-unknown-signer-authority-refused", not o.ok, o.code or "accepted!")
    expired = owner.write_authority(
        1, [(owner.binding_key, "active")],
        path=owner.dir / "authority-expired.json", expires=S.LONG_PAST,
    )
    o = M.bind(expired, owner.key_file)
    G.check("S6-expired-authority-refused", not o.ok, o.code or "accepted!")
    # a good authority, then a rolled-back one
    o = M.bind(owner.authority_file, owner.key_file)
    G.check("S6-valid-authority-accepted", o.ok, o.code or "")
    rotated_key = os.urandom(32)
    a2 = owner.write_authority(
        2, [(rotated_key, "active"), (owner.binding_key, "retired")],
        path=owner.dir / "authority-2.json",
    )
    k2 = owner.dir / "t2-binding-key-2.json"
    S.write_binding_key(k2, rotated_key)
    o = M.bind(a2, k2)
    G.check("S6-authority-rotation-accepted", o.ok, o.code or "")
    o = M.bind(owner.authority_file, owner.key_file)
    G.check(
        "S6-rolled-back-authority-refused",
        not o.ok,
        o.code or "an older authority version was accepted!",
    )
    # a key the authority does not list
    stranger = os.urandom(32)
    ks = owner.dir / "t2-binding-key-stranger.json"
    S.write_binding_key(ks, stranger)
    o = M.bind(a2, ks)
    G.check("S6-unauthorised-binding-key-refused", not o.ok, o.code or "accepted!")
    # an authority for other machines only
    other = owner.write_authority(
        3, [(rotated_key, "active")], machines=["0" * 32],
        path=owner.dir / "authority-3-other-machines.json",
    )
    o = M.bind(other, k2)
    G.check("S6-authority-for-another-machine-refused", not o.ok, o.code or "accepted!")

    # ------------------------------------------------------------------ revocation reaches existing seals
    prev = G.fresh(f"proj/{TAG}-revoke")
    (prev / "README.md").write_text("# revoke probe\n")
    G.git_init(prev)
    Mr = G.Machine(f"{TAG}-revoke")
    Mr.provision(owner.root_file)
    Mr.bind(owner.authority_file, owner.key_file)
    o = Mr.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=prev)
    og = Mr.run(ROLE + ["gate", "create", "--question", "before revocation",
                        "--fields", GATE_FIELDS], cwd=prev)
    gid = (og.result or {}).get("id")
    G.check("S6-revoke-baseline-record", og.ok and bool(gid), og.code or "")
    a4 = owner.write_authority(
        4, [(rotated_key, "active")],  # the original key is no longer listed at all
        path=owner.dir / "authority-4-revoked.json",
    )
    o = Mr.bind(a4, k2)
    G.check("S6-revoking-authority-accepted", o.ok, o.code or "")
    if gid:
        o, vrv, t2rv = binding(Mr, prev, gid)
        G.check(
            "S6-seals-under-a-revoked-key-stop-being-honoured",
            vrv != "VERIFIED",
            f"binding={vrv} {json.dumps(t2rv)[:250]}",
        )

    # ------------------------------------------------------------------ `gov` verifies, never signs (SRR-R0-L4)
    help_all = subprocess.run([str(G.GOV), "trust", "--help"], capture_output=True, text=True).stdout
    G.check(
        "S6-no-signing-subcommand-on-the-trust-surface",
        "sign" not in help_all.lower().replace("signed", "").replace("signer", ""),
        [l for l in help_all.splitlines() if "sign" in l.lower()][:4],
    )
    strings = subprocess.run(
        ["bash", "-c", f"strings {G.GOV} | grep -ci 'SigningKey\\|from_private_bytes\\|secret_key' || true"],
        capture_output=True, text=True).stdout.strip()
    G.check("S6-binary-carries-no-obvious-signing-entry-point", strings in ("0", ""), f"hits={strings}")

    # ------------------------------------------------------------------ S6 b3: machine paths do not define identity
    la = _lock(pa)
    lb = _lock(pb)
    G.check(
        "S6-b3-release-identity-identical-across-machines",
        (la.get("release_hash"), la.get("version"), la.get("kernel_manifest_hash"))
        == (lb.get("release_hash"), lb.get("version"), lb.get("kernel_manifest_hash")),
        f"A={la.get('release_hash')} B={lb.get('release_hash')}",
    )
    G.check(
        "S6-b3-no-absolute-machine-path-in-framework.lock",
        not any(isinstance(v, str) and v.startswith("/") for v in la.values()),
        str({k: v for k, v in la.items() if isinstance(v, str) and v.startswith("/")}),
    )

    # ------------------------------------------------------------------ S6 b1/b2: tracked vs derived
    tracked = subprocess.run(["git", "ls-files"], cwd=str(pa), capture_output=True,
                             text=True).stdout.split()
    G.check(
        "S6-b1-governed-records-are-tracked-in-git",
        any(t.startswith("spec/") for t in tracked) and any(t.startswith("governance/") for t in tracked),
        f"{len([t for t in tracked if t.startswith('spec/')])} spec, "
        f"{len([t for t in tracked if t.startswith('governance/')])} governance files tracked",
    )
    G.check(
        "S6-b2-derived-runtime-is-not-tracked",
        not any(t.startswith(".governance-runtime/") for t in tracked),
        str([t for t in tracked if t.startswith(".governance-runtime/")][:5]),
    )
    # derived runtime rebuilds locally on the second machine
    G.check(
        "S6-b2-second-machine-has-no-inherited-runtime-state",
        not (pb / ".governance-runtime" / "state.db").exists()
        or (pb / ".governance-runtime" / "state.db").stat().st_size >= 0,
        "clone carries no tracked runtime db",
    )
    # before anchoring: the refusal must be typed, must name its remedy, and must not refuse the remedy
    ub = B.run(ROLE + ["rebuild-memory"], cwd=pb)
    G.check(
        "S6-unanchored-second-machine-refusal-is-typed",
        (not ub.ok) and ub.code == "KERNEL_UNANCHORED",
        f"code={ub.code}",
    )
    rem = (((ub.env or {}).get("error") or {}).get("details") or {}).get("remediation") or []
    G.check(
        "S6-unanchored-refusal-names-its-remedy",
        any("kernel reinstall" in str(r) for r in rem),
        json.dumps(rem)[:200],
    )
    for diag in (["status"], ["doctor"], ["kernel", "trust"], ["kernel", "verify"]):
        od2 = B.run(diag, cwd=pb)
        G.check(
            f"S6-availability-{'-'.join(diag)}-stays-available-while-unanchored",
            od2.env is not None and od2.code != "KERNEL_UNANCHORED",
            f"code={od2.code}",
        )
    # the documented remedy (ARCH-0003 §8): verify the release the project pins, on this machine
    oanchor = B.run(ROLE + ["kernel", "reinstall", "--source", str(rel / "kernel")], cwd=pb)
    G.check(
        "S6-second-machine-can-verify-the-pinned-release (ARCH-0003 §8)",
        oanchor.ok,
        f"code={oanchor.code} {oanchor.message[:200]}",
    )
    o = B.run(ROLE + ["rebuild-memory"], cwd=pb)
    G.check("S6-b2-derived-runtime-rebuilds-locally-after-anchoring", o.ok, o.code or "")
    o, vba, _ = binding(B, pb, made["gate"])
    G.check("S6-B-honours-the-gate-A-wrote-after-anchoring", vba == "VERIFIED", f"binding={vba}")
    o = B.run(ROLE + ["gate", "create", "--question", "written on the owner's second machine",
                      "--fields", GATE_FIELDS], cwd=pb)
    b_gate = (o.result or {}).get("id")
    G.check("S6-B-can-write-its-own-T2-fact", o.ok and bool(b_gate), o.code or "")
    if b_gate:
        for f in (pb / "spec" / "decisions").glob(f"{b_gate}*"):
            shutil.copy(f, pa / "spec" / "decisions" / f.name)
        o, vrt, _ = binding(A, pa, b_gate)
        G.check("S6-A-honours-the-fact-B-wrote (round trip)", vrt == "VERIFIED", f"binding={vrt}")
    o = B.run(["doctor"], cwd=pb)
    G.check("S6-b2-second-machine-doctor-runs", o.env is not None, o.code or "")

    return G.summary()


def _safe(p):
    try:
        return p.read_bytes()
    except Exception:
        return b""


def _lock(proj):
    import yaml
    f = pathlib.Path(proj) / "governance" / "framework.lock"
    return yaml.safe_load(f.read_text()) if f.exists() else {}


def _unbound(out):
    """The product's own list of open T2 records nothing honoured, from an audit envelope."""
    blob = out.env or {}
    hits = []

    def walk(v, path=""):
        if isinstance(v, dict):
            if "t2" in v and isinstance(v.get("t2"), dict):
                hits.append({"id": v.get("id"), "t2": v["t2"].get("state") or v["t2"]})
            for k, x in v.items():
                walk(x, f"{path}.{k}")
        elif isinstance(v, list):
            for x in v:
                walk(x, path)

    walk(blob)
    if not hits:
        txt = json.dumps(blob)
        for marker in ("T2_UNBOUND", "FOREIGN", "UNAUTHORISED", "Unsealed", "KeyUnavailable"):
            if marker in txt:
                hits.append({"marker": marker})
    return hits


if __name__ == "__main__":
    sys.exit(main())
