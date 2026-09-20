#!/usr/bin/env python3
"""HELD-OUT — S4 `gov adopt` A0-A11 on a brownfield tree (Contract v3:921-934), T1-T3
(956-972), and the relocated OS stores (BC-P2-31) through adopt/migrate on a legacy tree.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import govenv as G  # noqa: E402

TAG = "t04"
PLANNER = "orchestrator"
EXECUTOR = "migration-executor"
MEMORY = "memory-engineer"
REVIEWER = "migration-reviewer"
VERIFIER = "migration-verifier"
MEMVER = "memory-verifier"
AUDITOR = "independent-auditor"


def brownfield(name, with_unknown=True):
    """A disposable copy of the product's brownfield fixture, plus verifier-authored legacy noise."""
    src = G.WT / "fixtures" / "brownfield" / "project"
    p = G.fresh(f"proj/{TAG}-{name}")
    shutil.copytree(src, p, dirs_exist_ok=True)
    # verifier-added Repo-B material: a misplaced spec, a duplicate authority, a hidden doc citation
    (p / "docs").mkdir(exist_ok=True)
    (p / "docs" / "OLD_ARCHITECTURE.md").write_text(
        "# Legacy architecture (superseded)\nSee [the rules](../AGENT_RULES_v2.md) and `src/app.py`.\n"
    )
    (p / "src").mkdir(exist_ok=True)
    if with_unknown:
        (p / "src" / "unknown_blob.bin").write_bytes(os.urandom(64))
    G.git_init(p)
    return p


def stage(M, p, role, session, args, **kw):
    return M.run(["--role", role, "--session", session, "adopt", *args], cwd=p, **kw)


def main():
    rel = G.build_release()
    owner = G.Owner(f"{TAG}-owner")
    owner.sign_release(rel / "kernel", 100)
    M = G.Machine(f"{TAG}-m")
    M.provision(owner.root_file)
    M.bind(owner.authority_file, owner.key_file)

    p = brownfield("adopt", with_unknown=False)
    o = M.run(["--role", PLANNER, "init", "--source", str(rel / "kernel")], cwd=p)
    G.check("S4-brownfield-kernel-installed", o.ok, o.code or o.text[:200])

    S_PLAN, S_EXEC, S_MEM = "S-planner", "S-executor", "S-memory"
    S_REV, S_VER, S_MV, S_AUD = "S-reviewer", "S-verifier", "S-memver", "S-auditor"

    results = {}

    # --------------------------------------------------- A0 safety baseline
    o = stage(M, p, PLANNER, S_PLAN, ["baseline"])
    results["A0"] = o
    G.check("S4-A0-safety-baseline-executes", o.ok, o.code or o.message[:160])
    b = (o.result or {})
    G.check(
        "S4-A0-records-a-safety-baseline (branch/snapshot/clean-tree)",
        all(k in json.dumps(b).lower() for k in ("commit", "dirty_files", "baseline_tests"))
        and "freeze" in json.dumps(b).lower(),
        json.dumps(b)[:300],
    )
    # T2: the baseline record the OS wrote is sealed
    bl = p / "spec" / "adoption" / "00-BASELINE.yaml"
    if not bl.exists():
        cand = list(p.rglob("00-BASELINE.yaml"))
        bl = cand[0] if cand else bl
    G.check("S4-A0-baseline-record-is-sealed (T2)",
            bl.exists() and "os_binding" in bl.read_text(), str(bl))

    # T1/T2: a session with no declaration is refused; a designated stage refuses the wrong role
    o = M.run(["--role", PLANNER, "adopt", "inventory"], cwd=p)
    G.check(
        "T2-b1-an-undeclared-session-cannot-author-an-adoption-stage",
        (not o.ok) and o.code == "ADOPTION_SESSION_UNDECLARED",
        f"code={o.code}",
    )

    # --------------------------------------------------- A1 cold inventory, A2 classification,
    #                                                      A3 path map, A4 plan, test scaffold
    for stg, args in (("A1", ["inventory"]), ("A2", ["classify"]), ("A3", ["map"]),
                      ("A4", ["plan"]), ("A4t", ["test-design"])):
        o = stage(M, p, PLANNER, S_PLAN, args)
        results[stg] = o
        G.check(f"S4-{stg}-`gov adopt {args[0]}`-executes", o.ok,
                o.code or o.message[:200])
    inv = results["A1"].result or {}
    G.check(
        "S4-A1-cold-inventory-catalogues-the-tree",
        (inv.get("artefacts") or inv.get("count") or 0) > 10
        or len(json.dumps(inv)) > 200,
        json.dumps(inv)[:300],
    )
    cls = results["A2"].result or {}
    G.check(
        "S4-A2-classification-assigns-classes",
        "unknown" in json.dumps(cls).lower() or "class" in json.dumps(cls).lower(),
        json.dumps(cls)[:300],
    )
    mp = results["A3"].result or {}
    G.check(
        "S4-A3-target-path-map-is-produced",
        len(json.dumps(mp)) > 100,
        json.dumps(mp)[:300],
    )
    pl = results["A4"].result or {}
    G.check("S4-A4-migration-plan-is-produced", len(json.dumps(pl)) > 100,
            json.dumps(pl)[:300])

    # --------------------------------------------------- A5 independent review (designated role, fresh session)
    o = stage(M, p, PLANNER, S_PLAN, ["review", "--verdict", "MIGRATION_PLAN_APPROVED"])
    G.check(
        "T1-A5-the-planner-cannot-perform-the-independent-review",
        (not o.ok) and o.code in ("INDEPENDENCE", "AUTHORITY_DENIED"),
        f"code={o.code} {o.message[:180]}",
    )
    o = M.run(["--role", REVIEWER, "--session", S_PLAN, "adopt", "review",
               "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-role", REVIEWER], cwd=p)
    G.check(
        "T2-A5-the-reviewer-may-not-continue-the-planner's-session",
        (not o.ok) and o.code == "INDEPENDENCE",
        f"code={o.code} cause="
        f"{(((o.env or {}).get('error') or {}).get('details') or {}).get('cause')}",
    )
    # the independent reviewer authors tests of their own before approving (protocol §10, O3)
    EVDIR0 = p / "spec" / "audits" / "GOVERNANCE-ADOPTION"
    tf = EVDIR0 / "06-migration-tests.yaml"
    tdoc = yaml.safe_load(tf.read_text())
    scaffold_n = len(tdoc.get("tests") or [])
    o = M.run(["--role", REVIEWER, "--session", S_REV, "adopt", "review",
               "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-role", REVIEWER], cwd=p)
    G.check(
        "T2-A5-an-approval-on-the-planner-scaffold-alone-is-refused (O3, BC-P2-34)",
        (not o.ok) and o.code == "INDEPENDENT_TESTS_REQUIRED",
        f"code={o.code} scaffold_tests={scaffold_n}",
    )
    tdoc["tests"].extend([
        {"id": "RVW-001", "kind": "path_present",
         "path": "governance/project/REPOSITORY_CONTRACT.yaml",
         "description": "reviewer: the repository contract survives the migration",
         "after_batch": 1},
        {"id": "RVW-002", "kind": "no_secret_in_index",
         "description": "reviewer: no secret-bearing legacy content reaches the index",
         "after_batch": 1},
        {"id": "RVW-003", "kind": "link_resolves",
         "path": "docs/OLD_ARCHITECTURE.md",
         "description": "reviewer: documentation citations still resolve after the migration",
         "after_batch": 1},
    ])
    tdoc["authored_by"] = "independent reviewer (held-out, P2-AR-0046)"
    tf.write_text(yaml.safe_dump(tdoc, sort_keys=False))
    o = M.run(["--role", REVIEWER, "--session", S_REV, "adopt", "review",
               "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-role", REVIEWER], cwd=p)
    results["A5"] = o
    G.check("S4-A5-independent-review-executes", o.ok, o.code or o.message[:250])
    G.check(
        "T3-A5-approval-binds-digests-of-what-was-reviewed (BC-P2-34)",
        "sha256" in json.dumps(o.result).lower() or "digest" in json.dumps(o.result).lower(),
        json.dumps(o.result)[:300],
    )

    # --------------------------------------------------- A6 controlled migration
    o = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "migrate", "--batch", "1"], cwd=p)
    blocked_by_health = (not o.ok) and o.code == "HEALTH_HARD_BLOCK"
    det = (((o.env or {}).get("error") or {}).get("details") or {})
    G.check(
        "S4-A6-is-not-hard-blocked-on-a-brownfield-tree-A2-already-classified (BC-P2-33)",
        not blocked_by_health,
        "A6 refused on a brownfield tree whose secret-bearing files A2 classified SECRET: "
        + json.dumps([{"check": b.get("check"), "subjects": b.get("subjects"),
                       "severity": b.get("severity"), "remedies": b.get("remedies")}
                      for b in (det.get("blocks") or [])])[:600],
    )
    if blocked_by_health:
        # Record the out-of-band remedy the product requires, then continue judging A6-A11.
        ds = p / "governance" / "project" / "DATA_SENSITIVITY.yaml"
        dd = yaml.safe_load(ds.read_text()) or {}
        dd.setdefault("classifications", [])
        subjects = sorted({x for b in (det.get("blocks") or []) for x in (b.get("subjects") or [])})
        for sub in subjects:
            dd["classifications"].append({"pattern": sub, "class": "secret"})
        ds.write_text(yaml.safe_dump(dd, sort_keys=False))
        print(f"    [S4] out-of-band remedy applied by the verifier: classified {subjects} "
              f"as secret in the project overlay (not an adoption stage)")
        o = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "migrate", "--batch", "1"], cwd=p)
    results["A6"] = o
    G.check("S4-A6-controlled-migration-executes", o.ok, o.code or o.message[:250])
    # BC-P2-34: change the approved plan and the executor must refuse
    EVDIR = p / "spec" / "audits" / "GOVERNANCE-ADOPTION"
    plan_files = [EVDIR / "05-plan.yaml"] if (EVDIR / "05-plan.yaml").exists() else []
    if plan_files:
        # each of the three artefacts the approval binds, changed semantically
        pf = plan_files[0]
        orig = pf.read_text()
        d = yaml.safe_load(orig)
        d["batches"][1]["description"] = "TAMPERED after the independent approval"
        pf.write_text(yaml.safe_dump(d, sort_keys=False))
        o = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "migrate", "--batch", "2"], cwd=p)
        G.check("T3-A6-execution-refuses-a-plan-changed-after-approval (BC-P2-34)",
                (not o.ok) and o.code == "APPROVAL_STALE", f"code={o.code}")
        pf.write_text(orig)
        tf2 = EVDIR / "06-migration-tests.yaml"
        torig = tf2.read_text()
        td2 = yaml.safe_load(torig)
        td2["tests"] = [x for x in td2["tests"] if x.get("id") != "RVW-001"]
        tf2.write_text(yaml.safe_dump(td2, sort_keys=False))
        o = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "migrate", "--batch", "2"], cwd=p)
        G.check("T3-A6-execution-refuses-weakened-independent-tests (BC-P2-34)",
                (not o.ok) and o.code == "APPROVAL_STALE", f"code={o.code}")
        tf2.write_text(torig)
        cf = EVDIR / "04-TARGET-PATH-MAP.jsonl"
        corig = cf.read_text()
        lines = corig.splitlines()
        r0 = json.loads(lines[0])
        r0["target_path"] = "archive/hijacked"
        lines[0] = json.dumps(r0)
        cf.write_text("\n".join(lines) + "\n")
        o = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "migrate", "--batch", "2"], cwd=p)
        G.check("T3-A6-execution-refuses-a-changed-catalogue (BC-P2-34)",
                (not o.ok) and o.code == "APPROVAL_STALE", f"code={o.code}")
        cf.write_text(corig)
    else:
        G.check("T3-A6-execution-refuses-a-plan-changed-after-approval (BC-P2-34)", False,
                "no adoption plan artefact found to tamper with")

    batch_outcomes = {}
    for batch in range(2, 8):
        ob = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "migrate",
                    "--batch", str(batch)], cwd=p)
        batch_outcomes[batch] = ob.code if not ob.ok else "ok"
        print(f"    [S4] batch {batch}: {batch_outcomes[batch]} {ob.message[:160]}")
    G.check(
        "S4-A6-every-planned-batch-executes",
        all(v == "ok" for v in batch_outcomes.values()),
        json.dumps(batch_outcomes),
    )

    # --------------------------------------------------- A7 independent migration verification
    o = M.run(["--role", VERIFIER, "--session", S_EXEC, "adopt", "verify-migration",
               "--verifier-role", VERIFIER], cwd=p)
    G.check(
        "T2-A7-the-verifier-may-not-continue-the-executor's-session",
        (not o.ok) and o.code == "INDEPENDENCE",
        f"code={o.code}",
    )
    o = M.run(["--role", VERIFIER, "--session", S_VER, "adopt", "verify-migration",
               "--verifier-role", VERIFIER], cwd=p)
    results["A7"] = o
    G.check("S4-A7-independent-migration-verification-executes", o.ok,
            o.code or o.message[:250])

    # --------------------------------------------------- A8 legacy extraction/retirement
    o = M.run(["--role", EXECUTOR, "--session", S_EXEC, "adopt", "extract-legacy"], cwd=p)
    results["A8"] = o
    G.check("S4-A8-legacy-extraction-retirement-executes", o.ok, o.code or o.message[:250])
    G.check(
        "S4-A8-retirement-states-a-dependency-proof (BC-P2-33)",
        any(k in json.dumps(o.result).lower()
            for k in ("dependen", "proof", "referenced_by", "consumers")),
        json.dumps(o.result)[:300],
    )

    # --------------------------------------------------- A9 new knowledge fabric
    o = M.run(["--role", MEMORY, "--session", S_MEM, "adopt", "build-memory"], cwd=p)
    results["A9"] = o
    G.check("S4-A9-new-knowledge-fabric-executes", o.ok, o.code or o.message[:250])

    # --------------------------------------------------- A10 independent memory verification
    o = M.run(["--role", MEMVER, "--session", S_MV, "adopt", "verify-memory",
               "--verifier-role", MEMVER], cwd=p)
    G.check(
        "T2-A10-the-builder-starter-set-alone-is-refused (O3, BC-P2-34)",
        (not o.ok) and o.code == "INDEPENDENT_HELDOUT_REQUIRED",
        f"code={o.code}",
    )
    # the independent memory verifier authors their own held-out queries
    hf = p / "governance" / "tests" / "memory" / "heldout.yaml"
    hd = yaml.safe_load(hf.read_text())
    hd["queries"].extend([
        {"id": "VHQ-001", "category": "exact_path", "query": "governance/project/REPOSITORY_CONTRACT.yaml",
         "expected_refs": ["file:governance/project/REPOSITORY_CONTRACT.yaml"], "forbidden": [], "k": 8},
        {"id": "VHQ-002", "category": "lexical", "query": "repository contract",
         "expected_refs": ["file:governance/project/REPOSITORY_CONTRACT.yaml"], "forbidden": [], "k": 8},
        {"id": "VHQ-003", "category": "exact_path", "query": "governance/framework.lock",
         "expected_refs": ["file:governance/framework.lock"], "forbidden": [], "k": 8},
        {"id": "VHQ-004", "category": "lexical", "query": "security policy",
         "expected_refs": ["file:governance/kernel/policies/SECURITY_POLICY.yaml"],
         "forbidden": [], "k": 8},
        {"id": "VHQ-005", "category": "lexical", "query": "kernel manifest",
         "expected_refs": ["file:governance/kernel/KERNEL_MANIFEST.json"], "forbidden": [], "k": 8},
        {"id": "VHQ-006", "category": "exact_path", "query": "governance/kernel/roles/ROLES.yaml",
         "expected_refs": ["file:governance/kernel/roles/ROLES.yaml"], "forbidden": [], "k": 8},
    ])
    hd["authored_by"] = "independent memory verifier (held-out, P2-AR-0046)"
    hf.write_text(yaml.safe_dump(hd, sort_keys=False))
    o = M.run(["--role", MEMVER, "--session", S_MEM, "adopt", "verify-memory",
               "--verifier-role", MEMVER], cwd=p)
    G.check(
        "T2-A10-the-memory-verifier-may-not-continue-the-builder's-session",
        (not o.ok) and o.code == "INDEPENDENCE",
        f"code={o.code}",
    )
    o = M.run(["--role", MEMVER, "--session", S_MV, "adopt", "verify-memory",
               "--verifier-role", MEMVER], cwd=p)
    results["A10"] = o
    G.check("S4-A10-independent-memory-verification-executes", o.ok,
            o.code or o.message[:250])
    G.check(
        "T2-A10-accepts-only-held-out-queries-the-verifier-authored (BC-P2-34)",
        "held" in json.dumps(o.result).lower() or "heldout" in json.dumps(o.result).lower()
        or (not o.ok),
        json.dumps(o.result)[:300],
    )

    # --------------------------------------------------- A11 full project audit
    o = M.run(["--role", AUDITOR, "--session", S_AUD, "adopt", "audit"], cwd=p)
    results["A11"] = o
    G.check("S4-A11-full-project-audit-executes", o.env is not None,
            o.code or o.message[:250])

    # --------------------------------------------------- A11 on a tree whose A10 accepts
    gp = G.fresh(f"proj/{TAG}-greenfield")
    (gp / "README.md").write_text("# greenfield adoption probe\n")
    (gp / "src").mkdir()
    (gp / "src" / "app.py").write_text("def main():\n    return 1\n")
    G.git_init(gp)
    M.run(["--role", PLANNER, "init", "--source", str(rel / "kernel")], cwd=gp)
    for args in (["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"]):
        stage(M, gp, PLANNER, "S-g-plan", args)
    gtf = gp / "spec" / "audits" / "GOVERNANCE-ADOPTION" / "06-migration-tests.yaml"
    gtd = yaml.safe_load(gtf.read_text())
    gtd.setdefault("tests", []).extend([
        {"id": "GRVW-001", "kind": "path_present",
         "path": "governance/kernel/roles/ROLES.yaml",
         "description": "reviewer (greenfield): kernel roles present after migration",
         "after_batch": 0},
        {"id": "GRVW-002", "kind": "path_present", "path": "src/app.py",
         "description": "reviewer (greenfield): product source preserved", "after_batch": 0},
        {"id": "GRVW-003", "kind": "text_present", "path": "README.md", "text": "greenfield",
         "description": "reviewer (greenfield): readme retained", "after_batch": 0}])
    gtf.write_text(yaml.safe_dump(gtd, sort_keys=False))
    M.run(["--role", REVIEWER, "--session", "S-g-rev", "adopt", "review",
           "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-role", REVIEWER], cwd=gp)
    for batch in range(0, 8):
        M.run(["--role", EXECUTOR, "--session", "S-g-exec", "adopt", "migrate",
               "--batch", str(batch)], cwd=gp)
    M.run(["--role", VERIFIER, "--session", "S-g-ver", "adopt", "verify-migration",
           "--verifier-role", VERIFIER], cwd=gp)
    M.run(["--role", VERIFIER, "--session", "S-g-ver", "adopt", "verify-migration",
           "--verifier-role", VERIFIER], cwd=gp)
    M.run(["--role", EXECUTOR, "--session", "S-g-exec", "adopt", "extract-legacy"], cwd=gp)
    M.run(["--role", MEMORY, "--session", "S-g-mem", "adopt", "build-memory"], cwd=gp)
    ghf = gp / "governance" / "tests" / "memory" / "heldout.yaml"
    ghd = yaml.safe_load(ghf.read_text())
    ghd["queries"] = [q for q in ghd.get("queries", [])][:0] + [
        {"id": "GVHQ-00%d" % i, "category": "exact_path", "query": path,
         "expected_refs": [f"file:{path}"], "forbidden": [], "k": 8}
        for i, path in enumerate([
            "governance/framework.lock",
            "governance/kernel/KERNEL_MANIFEST.json",
            "governance/project/REPOSITORY_CONTRACT.yaml",
            "governance/kernel/roles/ROLES.yaml",
            "governance/kernel/policies/SECURITY_POLICY.yaml",
            "src/app.py",
        ], 1)]
    ghd["authored_by"] = "independent memory verifier (held-out, P2-AR-0046)"
    ghf.write_text(yaml.safe_dump(ghd, sort_keys=False))
    oa10 = M.run(["--role", MEMVER, "--session", "S-g-mv", "adopt", "verify-memory",
                  "--verifier-role", MEMVER], cwd=gp)
    G.check("S4-A10-accepts-on-a-tree-whose-memory-meets-the-thresholds",
            oa10.ok and (oa10.result or {}).get("verdict", "").startswith("MEMORY_"),
            f"verdict={(oa10.result or {}).get('verdict')} code={oa10.code}")
    oa11 = M.run(["--role", AUDITOR, "--session", "S-g-aud", "adopt", "audit"], cwd=gp)
    G.check("S4-A11-full-project-audit-executes-after-A10-accepts",
            oa11.env is not None and oa11.code != "STAGE_ORDER",
            f"ok={oa11.ok} code={oa11.code} {json.dumps(oa11.result)[:250]}")
    gbl = gp / "spec" / "audits" / "GOVERNANCE-ADOPTION" / "00-BASELINE.yaml"
    gauth = gbl.read_text() if gbl.exists() else ""
    G.check("T1-authorship-of-independent-auditor-is-recorded",
            "S-g-aud" in gauth or AUDITOR in gauth,
            f"auditor authorship recorded: {'S-g-aud' in gauth}")

    # --------------------------------------------------- T3 evidence tree traceability
    o = M.run(["--role", AUDITOR, "--session", S_AUD, "adopt", "status"], cwd=p)
    st = o.result or {}
    done = [s for s in ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11")
            if s in json.dumps(st)]
    G.check(
        "T3-the-adoption-evidence-tree-is-traceable-end-to-end",
        len(done) >= 11,
        f"stages visible in `gov adopt status`: {done}",
    )
    ev = p / "spec" / "audits" / "GOVERNANCE-ADOPTION"
    files = sorted(f.name for f in ev.glob("*")) if ev.exists() else []
    G.check(
        "T3-every-stage-leaves-an-artefact-in-the-evidence-tree",
        len(files) >= 8,
        f"{len(files)} artefacts: {files[:14]}",
    )
    authors = json.dumps(yaml.safe_load(bl.read_text()) if bl.exists() else {})
    for role, sess in ((PLANNER, S_PLAN), (EXECUTOR, S_EXEC), (REVIEWER, S_REV),
                       (VERIFIER, S_VER), (MEMORY, S_MEM), (MEMVER, S_MV)):
        G.check(f"T1-authorship-of-{role}-is-recorded", sess in authors or role in authors,
                f"{role}/{sess} present in the baseline authorship log")

    # T1: every protocol role of Contract v3:957-965 is a kernel role
    roles = yaml.safe_load((p / "governance" / "kernel" / "roles" / "ROLES.yaml").read_text())
    ids = {r["id"] for r in roles["roles"]}
    for want, contract_role in (("recovery agent", None),
                                ("adoption auditor/planner", "orchestrator"),
                                ("independent migration reviewer/test author", "migration-reviewer"),
                                ("migration executor", "migration-executor"),
                                ("independent migration verifier", "migration-verifier"),
                                ("memory engineer", "memory-engineer"),
                                ("independent memory verifier/test author", "memory-verifier"),
                                ("comprehensive independent auditor", "independent-auditor"),
                                ("operator/CTO", "human")):
        if contract_role is None:
            # Protocol §3: the Conditional Recovery Role is performed by the interrupted session
            # itself ("Same session that was interrupted may perform this role"), so it is a
            # procedure, not a separate kernel role. Verify the procedure instead.
            rp = brownfield("recovery")
            M.run(["--role", PLANNER, "init", "--source", str(rel / "kernel")], cwd=rp)
            (rp / "src" / "half_edited.py").write_text("def broken(:\n")
            orc = M.run(["--role", PLANNER, "--session", "S-interrupted", "recover"], cwd=rp)
            blob = json.dumps(orc.env)
            G.check("T1-role-`recovery agent`-is-executable-as-the-recovery-procedure",
                    orc.ok, orc.code or orc.message[:200])
            G.check("T1-recovery-classifies-partial-mutations",
                    any(k in blob for k in ("PARTIAL", "COMPLETE_UNVERIFIED", "UNKNOWN",
                                            "classification", "mutations")),
                    blob[:300])
            G.check("T1-recovery-writes-a-checkpoint-or-report",
                    "checkpoint" in blob.lower() or "report" in blob.lower(),
                    blob[:300])
            G.check("T1-recovery-freezes-broad-governance-memory-work",
                    "freeze" in blob.lower() or "frozen" in blob.lower(),
                    blob[:300])
        else:
            G.check(f"T1-role-`{want}`-exists-as-a-kernel-role", contract_role in ids,
                    f"'{contract_role}' in ROLES.yaml: {contract_role in ids}")

    # --------------------------------------------------- B2.3 unknown artefacts block destructive migration
    up = brownfield("unknown", with_unknown=True)
    M.run(["--role", PLANNER, "init", "--source", str(rel / "kernel")], cwd=up)
    umap = None
    for args in (["baseline"], ["inventory"], ["classify"], ["map"], ["plan"]):
        r = stage(M, up, PLANNER, "S-u-plan", args)
        if args[0] == "map":
            umap = r
    uplan = yaml.safe_load(
        (up / "spec" / "audits" / "GOVERNANCE-ADOPTION" / "05-plan.yaml").read_text())
    unknown_n = max((umap.result or {}).get("unknown_blocking_destructive") or 0,
                    uplan.get("unknown_blocking") or 0)
    G.check(
        "B2-b3-unknown-material-artefacts-are-counted-as-blocking-destructive-migration",
        unknown_n >= 1,
        f"unknown_blocking={uplan.get('unknown_blocking')} "
        f"map_unknown_blocking_destructive="
        f"{(umap.result or {}).get('unknown_blocking_destructive')}",
    )
    if unknown_n >= 1:
        ucls = [json.loads(l) for l in
                (up / "spec" / "audits" / "GOVERNANCE-ADOPTION" / "02-CLASSIFICATION.jsonl")
                .read_text().splitlines() if l.strip()]
        unk = [r["path"] for r in ucls if str(r.get("class")) == "UNKNOWN"]
        # the destructive batches must refuse while an UNKNOWN artefact is unresolved
        stage(M, up, PLANNER, "S-u-plan", ["test-design"])
        utf = up / "spec" / "audits" / "GOVERNANCE-ADOPTION" / "06-migration-tests.yaml"
        utd = yaml.safe_load(utf.read_text())
        utd.setdefault("tests", []).append(
            {"id": "URV-001", "kind": "path_present", "path": "governance/kernel/roles/ROLES.yaml",
             "description": "reviewer: kernel roles present", "after_batch": 0})
        utf.write_text(yaml.safe_dump(utd, sort_keys=False))
        M.run(["--role", REVIEWER, "--session", "S-u-rev", "adopt", "review",
               "--verdict", "MIGRATION_PLAN_APPROVED", "--reviewer-role", REVIEWER], cwd=up)
        # the same out-of-band remedy V1-S4-01 records, so that this check tests the UNKNOWN rule
        # rather than re-testing the secret-classification block
        uds = up / "governance" / "project" / "DATA_SENSITIVITY.yaml"
        udd = yaml.safe_load(uds.read_text()) or {}
        udd.setdefault("classifications", []).extend(
            [{"pattern": "memory/chat_history.sql", "class": "secret"},
             {"pattern": "src/app/config.py", "class": "secret"}])
        uds.write_text(yaml.safe_dump(udd, sort_keys=False))
        codes = {}
        for batch in range(0, 8):
            ob = M.run(["--role", EXECUTOR, "--session", "S-u-exec", "adopt", "migrate",
                        "--batch", str(batch)], cwd=up)
            codes[batch] = ob.code if not ob.ok else "ok"
        G.check(
            "B2-b3-a-destructive-batch-is-refused-while-an-UNKNOWN-artefact-is-unresolved",
            "UNKNOWN_BLOCKS_DESTRUCTIVE" in codes.values(),
            f"unknown={unk[:3]} batches={json.dumps(codes)}",
        )

    # --------------------------------------------------- BC-P2-31: relocated OS stores on a legacy tree
    lp = brownfield("legacy-stores")
    o = M.run(["--role", PLANNER, "init", "--source", str(rel / "kernel")], cwd=lp)
    G.check("S4-legacy-tree-installed", o.ok, o.code or "")
    legacy_runtime = lp / ".governance-runtime"
    legacy_runtime.mkdir(exist_ok=True)
    (legacy_runtime / "control.json").write_text(json.dumps(
        {"mode": "PAUSED", "writes_frozen": True, "agents_cancelled": False,
         "updated_at": "2026-01-01T00:00:00Z", "reason": "left by an older gov"}))
    state_claims = lp / ".governance-state" / "claims.db"
    if state_claims.exists():
        shutil.move(str(state_claims), str(legacy_runtime / "claims.db"))
    o = M.run(["--role", PLANNER, "status"], cwd=lp)
    G.check(
        "BC-P2-31-a-legacy-emergency-control-file-is-still-honoured",
        "PAUSED" in json.dumps(o.env) or (not o.ok),
        json.dumps((o.result or {}).get("controls") or o.env)[:250],
    )
    o = M.run(["--role", PLANNER, "resume"], cwd=lp)
    G.check("BC-P2-31-the-control-state-can-be-lifted-on-a-legacy-tree", o.ok, o.code or "")
    G.check(
        "BC-P2-31-the-control-store-is-relocated-out-of-the-derived-runtime-dir",
        (lp / ".governance-state" / "control.json").exists()
        and not (legacy_runtime / "control.json").exists(),
        f"state={(lp / '.governance-state' / 'control.json').exists()} "
        f"legacy={(legacy_runtime / 'control.json').exists()}",
    )
    o = stage(M, lp, PLANNER, "S-legacy", ["baseline"])
    G.check("BC-P2-31-adopt-runs-on-the-legacy-tree-after-relocation", o.ok, o.code or "")
    # deleting the derived runtime must not delete project truth (B3) nor the OS stores
    before = M.run(["--role", PLANNER, "claims", "list"], cwd=lp)
    shutil.move(str(legacy_runtime),
                str(G.fresh(f"{TAG}-legacy-runtime.moved") / "governance-runtime"))
    after = M.run(["--role", PLANNER, "status"], cwd=lp)
    G.check(
        "B3-deleting-the-derived-runtime-directory-does-not-delete-project-truth",
        after.env is not None and (after.ok or after.code not in ("NOT_INSTALLED",)),
        f"code={after.code}",
    )
    G.check(
        "BC-P2-31-the-non-rebuildable-OS-stores-survive-deleting-the-derived-runtime",
        (lp / ".governance-state").exists()
        and any((lp / ".governance-state").iterdir()),
        f"{[f.name for f in (lp / '.governance-state').iterdir()]}",
    )
    # a conflicting copy at both locations is refused, never overwritten
    (lp / ".governance-runtime").mkdir(exist_ok=True)
    (lp / ".governance-runtime" / "control.json").write_text(json.dumps(
        {"mode": "PAUSED", "writes_frozen": True, "agents_cancelled": True,
         "updated_at": "2026-01-02T00:00:00Z", "reason": "conflicting legacy copy"}))
    o = M.run(["--role", PLANNER, "status"], cwd=lp)
    G.check(
        "BC-P2-31-a-conflicting-legacy-copy-is-honoured-strictly-or-refused",
        "PAUSED" in json.dumps(o.env) or "STATE_LOCATION_CONFLICT" in json.dumps(o.env),
        json.dumps(o.env)[:260],
    )

    print("\nAdoption stage outcomes:",
          json.dumps({k: (v.ok, v.code) for k, v in results.items()}))
    return G.summary()


if __name__ == "__main__":
    sys.exit(main())
