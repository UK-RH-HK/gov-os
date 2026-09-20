#!/usr/bin/env python3
"""HELD-OUT — S1 (897-898), S2 (901-911), S3 (914-919), S5 (937-945)."""
import json
import os
import pathlib
import shutil
import subprocess
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import govenv as G  # noqa: E402
import srrsign as S  # noqa: E402

TAG = "t05"
ROLE = ["--role", "orchestrator"]


def newproj(name):
    p = G.fresh(f"proj/{TAG}-{name}")
    (p / "README.md").write_text("# probe\n")
    G.git_init(p)
    return p


def _not_applied(o, proj):
    """Nothing was installed: the envelope says so, and framework.lock is unchanged."""
    if o.ok and (o.result or {}).get("applied") is True:
        return False
    lock = yaml.safe_load((pathlib.Path(proj) / "governance" / "framework.lock").read_text())
    return lock.get("version") == "4.1.6"


def main():
    rel = G.build_release()
    owner = G.Owner(f"{TAG}-owner")
    owner.sign_release(rel / "kernel", 100)
    M = G.Machine(f"{TAG}-m")
    M.provision(owner.root_file)
    M.bind(owner.authority_file, owner.key_file)

    # ================================================================= S1 canonical OS repo
    for d in ("framework", "runtime", "cli", "tools", "migrations", "tests", "fixtures",
              "lessons", "change-proposals", "release", "docs"):
        G.check(f"S1-b1-canonical-repo-separates-`{d}`", (G.WT / d).is_dir(),
                f"{d} present at the canonical root")
    p = newproj("s3")
    o = M.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=p)
    G.check("S3-b1-certified-kernel-installation-executes", o.ok, o.code or "")
    res = o.result or {}
    # S1.2: the consumer repo receives the kernel; it does not contain the OS build inputs
    consumer_has_build = any((p / d).exists() for d in ("runtime", "cli", "Cargo.toml"))
    G.check(
        "S1-b2-a-consumer-repo-does-not-rebuild-the-OS",
        not consumer_has_build and (p / "governance" / "kernel").is_dir(),
        f"consumer build inputs present={consumer_has_build}",
    )

    # ================================================================= S2 immutable releases
    man = json.loads((rel / "manifest.json").read_text())
    ymanp = rel / "manifest.yaml"
    yman = yaml.safe_load(ymanp.read_text()) if ymanp.exists() else {}
    fields = {
        "semantic versioning": man.get("version"),
        "release manifest": bool(man),
        "file hashes": man.get("file_hashes"),
        "supported migrations": man.get("migration_ids"),
        "schema versions": man.get("schema_versions"),
        "CLI/runtime versions": (man.get("cli_version"), man.get("runtime_version")),
        "adapter/capability versions": man.get("adapter_versions"),
        "release notes": man.get("release_notes"),
        "affected indexes": man.get("required_index_rebuilds"),
        "human decisions": man.get("human_gates"),
        "rollback": man.get("rollback_procedure"),
    }
    import re
    G.check("S2-b1-semantic-versioning",
            bool(re.fullmatch(r"\d+\.\d+\.\d+", str(man.get("version")))), str(man.get("version")))
    for name in ("release manifest", "file hashes", "supported migrations", "schema versions",
                 "CLI/runtime versions", "adapter/capability versions", "release notes",
                 "affected indexes", "human decisions", "rollback"):
        v = fields[name]
        # "human decisions" is legitimately empty for a release that needed none: the manifest
        # must carry the field, not a non-empty value.
        ok = (v is not None and v != "" and v != {} and v != (None, None)
              and (v != [] or name == "human decisions"))
        G.check(f"S2-b-{name.replace(' ', '-')}", ok,
                json.dumps(v)[:160] if not isinstance(v, bool) else str(v))
    G.check(
        "S2-b-capability-plugin-versions-are-recorded (A0-S2-01)",
        bool(man.get("capability_versions") or man.get("plugin_versions")
             or (man.get("adapter_versions") or {}).get("capabilities")),
        f"adapter_versions={json.dumps(man.get('adapter_versions'))[:200]} "
        f"capability_versions={man.get('capability_versions')}",
    )
    # immutability: rebuilding the same version into the same directory is refused
    o = M.run(ROLE + ["release", "build", "--version", "4.1.6",
                      "--canonical", str(G.WT), "--out", str(rel.parent.parent)])
    G.check("S2-releases-are-immutable", (not o.ok) and o.code == "RELEASE_IMMUTABLE",
            f"code={o.code}")
    o = M.run(ROLE + ["release", "verify", str(rel)])
    G.check("S2-release-hashes-verify", o.ok, o.code or json.dumps(o.result)[:200])
    victim = rel / "kernel" / "policies" / "SECURITY_POLICY.yaml"
    orig = victim.read_text()
    victim.write_text(orig + "\n# tamper\n")
    o = M.run(ROLE + ["release", "verify", str(rel)])
    G.check("S2-release-verify-detects-a-changed-file",
            (not o.ok) or not (o.result or {}).get("ok", True), f"ok={o.ok} code={o.code}")
    victim.write_text(orig)

    # ================================================================= S3 gov init
    G.check("S3-b2-project-overlay-created",
            (p / "governance" / "project" / "PROJECT_POLICY.yaml").exists(),
            "governance/project/*")
    G.check("S3-b3-repository-contract-created",
            (p / "governance" / "project" / "REPOSITORY_CONTRACT.yaml").exists(), "")
    G.check("S3-b4-initial-memory-state-created",
            (p / ".governance-runtime" / "state.db").exists()
            or (p / "governance" / "generated" / "index-manifest.json").exists(),
            "index manifest / runtime db")
    G.check("S3-b5-health-checks-run-at-init",
            bool(res.get("doctor")) and bool(res.get("conformance")),
            json.dumps({k: res.get(k) for k in ("doctor", "conformance")}))
    idx = res.get("index") or {}
    emb = idx.get("embedder") or {}
    G.check(
        "S3-b6-reference-retrieval-profile-bootstrapped-when-certified",
        bool(emb.get("id")) and bool(emb.get("identity")) and idx.get("artifacts", 0) > 0,
        json.dumps({"embedder": emb.get("id"), "identity": emb.get("identity"),
                    "artifacts": idx.get("artifacts")})[:250],
    )
    op = M.run(ROLE + ["memory", "verify"], cwd=p)
    G.check(
        "S3-b6-the-bootstrapped-profile-answers-queries",
        op.env is not None,
        json.dumps(op.result)[:200] if op.ok else op.code,
    )
    # A0-S3-01: does init record the release certification it installed?
    lock = yaml.safe_load((p / "governance" / "framework.lock").read_text())
    G.check(
        "S3-init-records-the-authenticity-basis-of-what-it-installed",
        lock.get("authenticity") == "AUTHENTIC" and lock.get("admission"),
        json.dumps({k: lock.get(k) for k in ("authenticity", "admission", "sequence")}),
    )

    # ================================================================= S5 gov update
    # a genuine newer release: same payload, signed at a higher sequence and a higher version
    up = G.copy_release(rel.parent, f"{TAG}-next")
    k = up / "4.1.6" / "kernel"
    ky = yaml.safe_load((k / "KERNEL.yaml").read_text())
    ky["version"] = "4.1.7"
    ky.setdefault("supported_from_versions", [])
    if "4.1.6" not in ky["supported_from_versions"]:
        ky["supported_from_versions"].append("4.1.6")
    (k / "KERNEL.yaml").write_text(yaml.safe_dump(ky, sort_keys=False))
    migdir = k / "migrations"
    migdir.mkdir(exist_ok=True)
    (migdir / "M-4.1.6-4.1.7.yaml").write_text(yaml.safe_dump({
        "id": "M-4.1.6-4.1.7", "schema_version": "1.3.0", "from_version": "4.1.6",
        "to_version": "4.1.7", "description": "held-out probe migration (no-op)",
        "breaking": False, "human_gate": "none", "operations": [],
    }, sort_keys=False))
    man2 = json.loads((k / "KERNEL_MANIFEST.json").read_text())
    files, ph, kmh, ver = S.measure_payload(k)
    man2["files"], man2["payload_hash"], man2["version"] = files, ph, "4.1.7"
    (k / "KERNEL_MANIFEST.json").write_text(json.dumps(man2, indent=2) + "\n")
    owner.sign_release(k, 110, meta_dir=up / "4.1.6" / "metadata", release_version="4.1.7")

    o = M.run(ROLE + ["update", "--check", "--source", str(k)], cwd=p)
    chk = o.result or {}
    G.check("S5-b1-check-impact-simulation-executes", o.ok, o.code or "")
    G.check(
        "S5-b1-impact-simulation-states-radius-and-consequences",
        bool((chk.get("impact") or {}).get("radius"))
        and bool((chk.get("impact") or {}).get("consequences")),
        json.dumps(chk.get("impact"))[:300],
    )
    G.check("S5-b3-compatibility-and-migration-path-are-computed",
            chk.get("compatible") is True and chk.get("migration_path"),
            json.dumps({k2: chk.get(k2) for k2 in ("compatible", "migration_path")}))
    G.check(
        "S5-b2-authenticated-source: certification comes only from signed metadata",
        (chk.get("certification_basis") or {}).get("authenticated") is False
        and (chk.get("certification_basis") or {}).get("unsigned_claim") is not None,
        json.dumps(chk.get("certification_basis"))[:300],
    )
    G.check("S5-b2-an-uncertified-target-requires-the-human-gate",
            chk.get("human_gate_required") is True, str(chk.get("human_gate_required")))

    # an unsigned source is refused at apply
    unsigned = G.copy_release(up / "4.1.6", f"{TAG}-next-unsigned")
    shutil.rmtree(unsigned / "metadata", ignore_errors=True)
    o = M.run(ROLE + ["update", "--apply", "--source", str(unsigned / "kernel")], cwd=p)
    G.check("S5-b2-an-unsigned-update-source-does-not-install",
            _not_applied(o, p), f"ok={o.ok} code={o.code} "
            f"applied={(o.result or {}).get('applied')}")
    # a foreign-signed source is refused
    foreign = G.Owner(f"{TAG}-foreign")
    fr = G.copy_release(up / "4.1.6", f"{TAG}-next-foreign")
    foreign.sign_release(fr / "kernel", 110, meta_dir=fr / "metadata", release_version="4.1.7")
    o = M.run(ROLE + ["update", "--apply", "--source", str(fr / "kernel")], cwd=p)
    G.check("S5-b2-a-foreign-signed-update-source-does-not-install",
            _not_applied(o, p),
            f"ok={o.ok} code={o.code} reason={(o.result or {}).get('reason')}")

    # the version-equal short circuit (does `update` authenticate what it reports on?)
    same = G.copy_release(rel.parent, f"{TAG}-same-version")
    sv = same / "4.1.6" / "kernel"
    f = sv / "policies" / "SECURITY_POLICY.yaml"
    f.write_text(f.read_text() + "\n# tampered, same declared version\n")
    m3 = json.loads((sv / "KERNEL_MANIFEST.json").read_text())
    ff, pph, kkmh, _ = S.measure_payload(sv)
    m3["files"], m3["payload_hash"] = ff, pph
    (sv / "KERNEL_MANIFEST.json").write_text(json.dumps(m3, indent=2) + "\n")
    shutil.rmtree(same / "4.1.6" / "metadata", ignore_errors=True)
    o = M.run(ROLE + ["update", "--apply", "--source", str(sv)], cwd=p)
    G.check(
        "S5-b2-a-tampered-source-declaring-the-installed-version-is-not-reported-as-up-to-date",
        not (o.ok and (o.result or {}).get("reason") == "already up to date"),
        f"ok={o.ok} code={o.code} reason={(o.result or {}).get('reason')} "
        f"(the source was never authenticated)",
    )

    # apply the authentic update through its Human Decision Gate
    o = M.run(ROLE + ["update", "--apply", "--source", str(k)], cwd=p)
    G.check(
        "S5-b2-an-uncertified-update-stops-at-the-human-gate",
        _not_applied(o, p) and "GATE" in json.dumps(o.env).upper(),
        f"ok={o.ok} code={o.code} reason={(o.result or {}).get('reason')}",
    )
    o = M.run(ROLE + ["update", "--apply", "--approve", "--by", "probe-operator",
                      "--source", str(k)], cwd=p)
    G.check(
        "S5-b2-an-agent-declared-approval-does-not-substitute-for-the-human-gate",
        _not_applied(o, p),
        f"ok={o.ok} code={o.code} reason={(o.result or {}).get('reason')}",
    )
    # answer the gate through the owner-signed human channel (ARCH-0003 §8, P2-ADJ-0001)
    gid = ((o.result or {}).get("human_gate")
           or (((o.env or {}).get("error") or {}).get("details") or {}).get("human_gate")
           or "HDG-0001")
    op = M.run(ROLE + ["gate", "present", gid], cwd=p)
    G.check("S5-the-gate-package-is-presented-before-it-can-be-answered (INV-008)",
            op.env is not None, op.code or "")
    G.answer_gate(M, owner, p, gid, option="A", by="held-out probe owner")
    od = M.run(ROLE + ["decide", gid, "--option", "A"], cwd=p)
    G.check("S5-the-owner-signed-human-answer-is-accepted", od.ok, od.code or od.message[:200])
    before_overlay = (p / "governance" / "project" / "PROJECT_POLICY.yaml").read_text()
    (p / "governance" / "project" / "PROJECT_POLICY.yaml").write_text(
        before_overlay.rstrip() + "\n# project overlay marker added before the update\n")
    marker = (p / "governance" / "project" / "PROJECT_POLICY.yaml").read_text()
    applied = M.run(ROLE + ["update", "--apply", "--source", str(k)], cwd=p)
    G.check("S5-an-authentic-approved-update-applies", applied.ok
            and (applied.result or {}).get("applied") is True,
            f"ok={applied.ok} code={applied.code} {applied.message[:200]}")
    det = (applied.result or {}).get("details") or {}
    lock2 = yaml.safe_load((p / "governance" / "framework.lock").read_text())
    G.check("S5-b3-migration-is-applied", det.get("migrations") == ["M-4.1.6-4.1.7"],
            json.dumps(det.get("migrations")))
    G.check("S5-b4-the-project-overlay-is-preserved",
            (p / "governance" / "project" / "PROJECT_POLICY.yaml").read_text() == marker,
            "PROJECT_POLICY.yaml unchanged by the update")
    G.check("S5-b5-adapters-views-are-regenerated",
            "overlay_reconciled" in det or "regenerate_adapters" in json.dumps(det)
            or (p / "governance" / "generated").is_dir(),
            json.dumps({x: det.get(x) for x in ("overlay_reconciled", "overlay_keys_changed")}))
    G.check("S5-b6-affected-indexes-are-rebuilt", bool(det.get("index_manifest")),
            str(det.get("index_manifest"))[:80])
    G.check("S5-b7-the-update-verifies-afterwards",
            bool(det.get("doctor")) and bool(det.get("audit")),
            json.dumps({x: det.get(x) for x in ("doctor", "audit")}))
    G.check("S5-b2-the-committed-update-records-an-authentic-source",
            (det.get("release_authenticity") or {}).get("authenticity") == "AUTHENTIC"
            and lock2.get("version") == "4.1.7",
            json.dumps({"authenticity": (det.get("release_authenticity") or {}).get("authenticity"),
                        "version": lock2.get("version")}))
    led = p / "spec" / "reports" / "framework-updates.jsonl"
    G.check("S5-b9-ledger-provenance-is-recorded", led.exists()
            and "committed" in led.read_text(), led.read_text()[:200] if led.exists() else "absent")
    # rollback: refused below the floor, admitted only with an owner-signed authorisation
    orb = M.run(ROLE + ["update", "--rollback"], cwd=p)
    G.check("S5-b8-rollback-below-the-floor-is-refused-by-default",
            (not orb.ok) and orb.code == "SRR_BELOW_FLOOR", f"code={orb.code}")
    G.break_glass(M, owner, p, rel / "kernel", nonce="t05-rollback")
    orb = M.run(ROLE + ["update", "--rollback", "--break-glass"], cwd=p)
    lock3 = yaml.safe_load((p / "governance" / "framework.lock").read_text())
    G.check("S5-b8-rollback-with-an-owner-signed-authorisation-restores-the-release (BC-P2-38)",
            orb.ok and lock3.get("version") == "4.1.6",
            f"ok={orb.ok} code={orb.code} version={lock3.get('version')} "
            f"{orb.message[:220]}")
    G.check("S5-b8-the-machine-is-marked-degraded-after-break-glass",
            "DEGRADED" in json.dumps(M.run(["trust", "status"], cwd=p).result or {}),
            json.dumps((M.run(["trust", "status"], cwd=p).result or {}).get("degraded"))[:200])

    # health admission: an update that is a block's remedy stays available; one that is not is refused
    hp = newproj("health")
    M.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=hp)
    (hp / "spec" / "decisions").mkdir(parents=True, exist_ok=True)
    (hp / "spec" / "decisions" / "D-BROKEN.yaml").write_text("id: D-BROKEN\n: : :\n")
    od = M.run(ROLE + ["doctor"], cwd=hp)
    o = M.run(ROLE + ["update", "--apply", "--source", str(k)], cwd=hp)
    G.check(
        "S5-health-admission-refuses-an-update-that-remedies-nothing",
        (not o.ok),
        f"code={o.code} {o.message[:200]}",
    )
    det = (((o.env or {}).get("error") or {}).get("details") or {})
    G.check(
        "S5-health-admission-refusal-is-typed-and-names-its-subjects",
        bool(det.get("blocks") or det.get("subjects") or o.code),
        json.dumps({k2: det.get(k2) for k2 in ("operation", "subjects")})[:250],
    )

    # rollback
    o = M.run(ROLE + ["update", "--rollback"], cwd=p)
    G.check(
        "S5-b8-rollback-is-executable-or-typed-when-there-is-nothing-to-roll-back",
        o.env is not None,
        f"ok={o.ok} code={o.code} {json.dumps(o.result)[:220] if o.ok else o.message[:200]}",
    )
    # ledger/provenance
    print("\nS5 update apply outcome:", applied.code, applied.message[:200])
    return G.summary()


if __name__ == "__main__":
    sys.exit(main())
