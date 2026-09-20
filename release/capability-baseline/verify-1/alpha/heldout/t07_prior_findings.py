#!/usr/bin/env python3
"""HELD-OUT — first-hand disposition of the remaining iteration-0 alpha findings that the
capability probes above do not already re-establish (A0-A5-02, A0-A2-05, A0-A3-01, A0-A3-02,
A0-B1-01, A0-S4-01, A0-S5-01, S0-AC09-01)."""
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

TAG = "t07"
ROLE = ["--role", "orchestrator"]


def main():
    rel = G.build_release()
    owner = G.Owner(f"{TAG}-owner")
    owner.sign_release(rel / "kernel", 100)
    M = G.Machine(f"{TAG}-m")
    M.provision(owner.root_file)
    M.bind(owner.authority_file, owner.key_file)
    p = G.fresh(f"proj/{TAG}-p")
    (p / "README.md").write_text("# probe\n")
    (p / "src").mkdir()
    (p / "src" / "app.py").write_text("def run():\n    return 1\n")
    (p / "Makefile").write_text("all:\n\techo hi\n")
    (p / "pyproject.toml").write_text("[project]\nname='probe'\nversion='0'\n")
    G.git_init(p)
    o = M.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=p)
    G.check("prior-baseline-installed", o.ok, o.code or "")

    # ---------------------------------------------------------- A0-A5-02: CANCEL_AGENTS and claims
    t = M.run(ROLE + ["task", "create", "--objective", "claim probe", "--class", "governance"], cwd=p)
    tid = (t.result or {}).get("id")
    c = M.run(ROLE + ["task", "claim", tid], cwd=p, env={"GOV_SESSION": "S-claimer"}) if tid else None
    claims_before = M.run(ROLE + ["claims", "list"], cwd=p)
    M.run(ROLE + ["cancel-agents", "--reason", "probe"], cwd=p)
    claims_after = M.run(ROLE + ["claims", "list"], cwd=p)
    st = M.run(["status"], cwd=p)
    n_before = len((claims_before.result or {}).get("claims")
                   or (claims_before.result if isinstance(claims_before.result, list) else []) or [])
    n_after = len((claims_after.result or {}).get("claims")
                  or (claims_after.result if isinstance(claims_after.result, list) else []) or [])
    G.check(
        "A0-A5-02-CANCEL_AGENTS-revokes-the-claims-it-cancels",
        n_before == 0 or n_after < n_before,
        f"claims before={n_before} after={n_after} "
        f"(claim outcome={c.code if c and not c.ok else 'ok' if c else 'n/a'}); "
        f"control={json.dumps((st.result or {}).get('controls') or {})[:160]}",
    )
    M.run(ROLE + ["resume"], cwd=p)

    # ---------------------------------------------------------- A0-A2-05: interrupted swap leftovers
    before_dirs = {d.name for d in (p / "governance").iterdir() if d.is_dir()}
    o = M.run(ROLE + ["kernel", "reinstall", "--source", str(rel / "kernel")], cwd=p)
    after_dirs = {d.name for d in (p / "governance").iterdir() if d.is_dir()}
    leftovers = sorted(after_dirs - before_dirs)
    G.check(
        "A0-A2-05-a-completed-swap-leaves-no-superseded-kernel-tree-behind",
        not leftovers,
        f"new directories beside the installation: {leftovers}",
    )
    o = M.run(["trust", "recover-transactions"], cwd=p)
    G.check(
        "A0-A2-05-interrupted-install-transactions-are-replayable-and-reported",
        o.ok, f"code={o.code} replayed={json.dumps((o.result or {}).get('replayed'))[:150]}",
    )

    # ---------------------------------------------------------- A0-A3-01: customer/personal data
    (p / "src" / "customers.csv").write_text(
        "name,email,card\nJane Roe,jane@example.com,4111111111111111\n")
    M.run(ROLE + ["rebuild-memory"], cwd=p)
    q = M.run(ROLE + ["memory", "query", "4111111111111111"], cwd=p)
    G.check(
        "A0-A3-01-unclassified-customer-data-is-excluded-without-a-project-classification",
        "4111111111111111" not in json.dumps(q.env),
        json.dumps((q.result or {}).get("hits"))[:250],
    )
    od = M.run(ROLE + ["doctor"], cwd=p)
    G.check(
        "A0-A3-01-unclassified-personal-data-is-at-least-reported",
        "customers.csv" in json.dumps(od.env) or "secret" in json.dumps(od.env).lower(),
        f"doctor code={od.code}",
    )
    os.replace(p / "src" / "customers.csv", G.SCRATCH / f"{TAG}-customers.moved")

    # ---------------------------------------------------------- A0-A3-02: overlay granting permissions
    tp = p / "governance" / "project" / "TOOL_PERMISSIONS.yaml"
    orig = tp.read_text()
    d = yaml.safe_load(orig) or {}
    d.setdefault("policy_overrides", {})
    d["roles"] = {"research-agent": {"permissions": ["shell.exec", "fs.write", "net.any"]}}
    tp.write_text(yaml.safe_dump(d, sort_keys=False))
    o = M.run(ROLE + ["policy", "overrides"], cwd=p)
    oa = M.run(ROLE + ["audit"], cwd=p)
    blob = json.dumps(o.env) + json.dumps(oa.env)
    G.check(
        "A0-A3-02-an-overlay-that-grants-elevated-permissions-is-refused-or-reported",
        bool((o.result or {}).get("refused")) or (not oa.ok)
        or "TOOL_PERMISSIONS" in blob,
        f"refused={json.dumps((o.result or {}).get('refused'))[:200]} audit_ok={oa.ok}",
    )
    tp.write_text(orig)

    # ---------------------------------------------------------- A0-B1-01: root-level project files
    rc = yaml.safe_load((p / "governance" / "project" / "REPOSITORY_CONTRACT.yaml").read_text())
    o = M.run(ROLE + ["audit"], cwd=p)
    blob = json.dumps(o.env)
    G.check(
        "A0-B1-01-root-level-project-files-are-covered-by-the-repository-contract",
        "Makefile" not in blob or "unmapped" not in blob.lower(),
        f"contract rules={len(rc.get('rules') or [])}; audit mentions Makefile="
        f"{'Makefile' in blob}",
    )

    # ---------------------------------------------------------- A0-S4-01: the A0 safety baseline
    src = G.WT / "fixtures" / "brownfield" / "project"
    bp = G.fresh(f"proj/{TAG}-a0")
    shutil.copytree(src, bp, dirs_exist_ok=True)
    G.git_init(bp)
    M.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=bp)
    branch_before = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(bp),
                                   capture_output=True, text=True).stdout.strip()
    o = M.run(ROLE + ["--session", "S-a0", "adopt", "baseline"], cwd=bp)
    branch_after = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(bp),
                                  capture_output=True, text=True).stdout.strip()
    res = o.result or {}
    G.check("A0-S4-01-A0-pins-the-baseline-commit", bool(res.get("commit")), str(res.get("commit")))
    G.check("A0-S4-01-A0-reports-interrupted-work-and-a-freeze",
            res.get("interrupted") is not None and bool(res.get("freeze_advice")),
            json.dumps({k: res.get(k) for k in ("interrupted", "freeze_advice")})[:220])
    G.check(
        "A0-S4-01-A0-creates-an-adoption-branch-or-worktree",
        branch_after != branch_before or bool(res.get("branch")) or bool(res.get("worktree")),
        f"branch before={branch_before} after={branch_after} result_branch={res.get('branch')}",
    )
    G.check(
        "A0-S4-01-A0-takes-a-restorable-snapshot-of-the-tree",
        bool(res.get("snapshot")) or (bp / ".governance-state" / "adoption").exists(),
        f"snapshot={res.get('snapshot')}",
    )

    # ---------------------------------------------------------- A0-S5-01: refused update leaves no snapshot
    up = G.copy_release(rel.parent, f"{TAG}-next")
    k = up / "4.1.6" / "kernel"
    ky = yaml.safe_load((k / "KERNEL.yaml").read_text())
    ky["version"] = "4.1.7"
    ky.setdefault("supported_from_versions", []).append("4.1.6")
    (k / "KERNEL.yaml").write_text(yaml.safe_dump(ky, sort_keys=False))
    (k / "migrations").mkdir(exist_ok=True)
    (k / "migrations" / "M-4.1.6-4.1.7.yaml").write_text(yaml.safe_dump({
        "id": "M-4.1.6-4.1.7", "schema_version": "1.3.0", "from_version": "4.1.6",
        "to_version": "4.1.7", "description": "probe", "breaking": False,
        "human_gate": "none", "operations": []}, sort_keys=False))
    man = json.loads((k / "KERNEL_MANIFEST.json").read_text())
    files, ph, kmh, _ = S.measure_payload(k)
    man["files"], man["payload_hash"], man["version"] = files, ph, "4.1.7"
    (k / "KERNEL_MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    owner.sign_release(k, 110, meta_dir=up / "4.1.6" / "metadata", release_version="4.1.7")
    o = M.run(ROLE + ["update", "--apply", "--source", str(k)], cwd=p)
    snaps = p / ".governance-state" / "update"
    left = sorted(x.name for x in snaps.iterdir()) if snaps.exists() else []
    G.check(
        "A0-S5-01-a-refused-update-leaves-no-snapshot-behind",
        not left,
        f"update refused with {o.code}; snapshots left: {left}",
    )
    orb = M.run(ROLE + ["update", "--rollback"], cwd=p)
    G.check(
        "A0-S5-01-rollback-does-not-record-a-rollback-of-an-update-that-never-happened",
        (not orb.ok) and orb.code == "SNAPSHOT_MISSING",
        f"code={orb.code}",
    )

    # ---------------------------------------------------------- S0-AC09-01: product_identity on a tag
    pid = subprocess.run(
        ["python3", str(G.WT / "release" / "orchestration" / "phase-2" / "tools" / "product_identity.py"),
         "cap2-candidate-1"], cwd=str(G.WT), capture_output=True, text=True).stdout
    tagcommit = subprocess.run(["git", "rev-list", "-n1", "cap2-candidate-1"], cwd=str(G.WT),
                               capture_output=True, text=True).stdout.strip()
    printed = next((l.split(":", 1)[1].strip() for l in pid.splitlines()
                    if l.startswith("commit:")), "")
    G.check(
        "S0-AC09-01-product_identity-prints-the-commit-for-a-tag-name",
        printed == tagcommit,
        f"printed={printed} rev-list={tagcommit} (an annotated tag's object id is not its commit)",
    )

    return G.summary()


if __name__ == "__main__":
    sys.exit(main())
