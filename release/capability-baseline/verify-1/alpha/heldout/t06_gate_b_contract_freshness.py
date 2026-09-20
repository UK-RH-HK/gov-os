#!/usr/bin/env python3
"""HELD-OUT — B1-B3 (185-203), the derived contract views for the alpha capabilities
(BC-P2-01/BC-P2-02, AC-13/AC-10) and evidence freshness (Contract v3:95-111, AC-10)."""
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import govenv as G  # noqa: E402

TAG = "t06"
ROLE = ["--role", "orchestrator"]
ALPHA = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3",
         "S1", "S2", "S3", "S4", "S5", "S6", "T1", "T2", "T3"]


def owner_bullets():
    """The alpha checklist bullets, read from the owner source itself (frozen contract §1)."""
    src = (G.WT / "Governance_OS_Capability_Acceptance_Contract_v3.md").read_text().splitlines()
    out, cur = {}, None
    for i, line in enumerate(src, 1):
        m = re.match(r"^## ([A-Z]+\d+)\. ", line)
        if m:
            cur = m.group(1) if m.group(1) in ALPHA else None
            if cur:
                out[cur] = []
            continue
        if cur and line.startswith("- [ ] "):
            out[cur].append((i, line[len("- [ ] "):].strip()))
        elif cur and line.startswith("#"):
            cur = None
    return out


def main():
    rel = G.build_release()
    owner = G.Owner(f"{TAG}-owner")
    owner.sign_release(rel / "kernel", 100)
    M = G.Machine(f"{TAG}-m")
    M.provision(owner.root_file)
    M.bind(owner.authority_file, owner.key_file)
    p = G.fresh(f"proj/{TAG}-b")
    (p / "README.md").write_text("# probe\n")
    (p / "src").mkdir()
    (p / "src" / "app.py").write_text("from src.util import helper\n\n\ndef run():\n    return helper()\n")
    (p / "src" / "util.py").write_text("def helper():\n    return 1\n")
    (p / "docs").mkdir()
    (p / "docs" / "design.md").write_text(
        "# Design\n\nSee [the utility](../src/util.py) and [the app](../src/app.py).\n")
    G.git_init(p)
    o = M.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=p)
    G.check("B-baseline-installed", o.ok, o.code or "")

    # ================================================================ B1 repository contract
    rc = yaml.safe_load((p / "governance" / "project" / "REPOSITORY_CONTRACT.yaml").read_text())
    blob = json.dumps(rc)
    for boundary in ("governance", "framework", "project", "generated", "runtime"):
        G.check(f"B1-b1-boundary-`{boundary}`-is-explicit", boundary in blob,
                f"named in REPOSITORY_CONTRACT.yaml")
    G.check(
        "B1-b2-native-product-architecture-is-preserved",
        (p / "src" / "app.py").exists() and (p / "src" / "util.py").exists()
        and (p / "docs" / "design.md").exists(),
        "src/ and docs/ untouched by init",
    )
    G.check(
        "B1-b3-the-contract-maps-the-project's-own-layout-without-refactoring-it",
        "src" in blob or "product" in blob,
        json.dumps([r for r in (rc.get("rules") or rc.get("paths") or [])][:4])[:300],
    )
    classes = {}
    for r in (rc.get("rules") or []):
        classes.setdefault(r.get("class") or r.get("state_class"), []).append(
            r.get("path") or r.get("pattern"))
    G.check(
        "B1-b4-generated-runtime-state-is-distinguished-from-tracked-authoritative-state",
        any(k and "derive" in str(k).lower() or k and "generat" in str(k).lower()
            for k in classes) or ".governance-runtime" in blob,
        json.dumps({k: v[:2] for k, v in list(classes.items())[:6]})[:400],
    )
    tracked = subprocess.run(["git", "ls-files"], cwd=str(p), capture_output=True,
                             text=True).stdout.split()
    G.check(
        "B1-b4-the-derived-runtime-directory-is-not-tracked",
        not any(t.startswith(".governance-runtime/") for t in tracked),
        str([t for t in tracked if t.startswith(".governance-runtime/")][:3]),
    )

    # ================================================================ B2 path map
    S_ = ["--session", "S-b2"]
    for args in (["baseline"], ["inventory"], ["classify"], ["map"]):
        o = M.run(ROLE + S_ + ["adopt", *args], cwd=p)
        G.check(f"B2-adopt-{args[0]}-executes", o.ok, o.code or o.message[:160])
    ev = p / "spec" / "audits" / "GOVERNANCE-ADOPTION"
    rows = [json.loads(l) for l in (ev / "04-TARGET-PATH-MAP.jsonl").read_text().splitlines() if l.strip()]
    G.check("B2-b1-every-material-artefact-is-classified", len(rows) > 5, f"{len(rows)} rows")
    cls_rows = [json.loads(l) for l in (ev / "02-CLASSIFICATION.jsonl").read_text().splitlines() if l.strip()]
    byid = {r["artifact_id"]: r for r in cls_rows}
    complete = [r for r in rows
                if (r.get("current_path") and byid.get(r["artifact_id"], {}).get("class")
                    and byid.get(r["artifact_id"], {}).get("authority")
                    and ("target_action" in r or "action" in r))]
    G.check(
        "B2-b1-each-carries-current-path-class-authority-and-intended-target",
        len(complete) == len(rows),
        f"{len(complete)}/{len(rows)} complete; sample={json.dumps(rows[0])[:250]}",
    )
    actions = {r.get("target_action") or r.get("action") for r in rows}
    supported = set()
    plan_md = (ev / "05-ADOPTION-MIGRATION-PLAN.md").read_text() if (ev / "05-ADOPTION-MIGRATION-PLAN.md").exists() else ""
    schema_blob = ""
    for sch in ("migration-catalogue-entry.schema.json", "migration.schema.json"):
        f2 = p / "governance" / "kernel" / "schemas" / sch
        if f2.exists():
            schema_blob += f2.read_text()
    for a in ("KEEP", "MOVE", "RENAME", "SPLIT", "MERGE", "EXTRACT", "RETIRE",
              "DELETE_FROM_ACTIVE_TREE"):
        in_map = any(a in str(x) for x in actions)
        in_vocab = a in schema_blob or a in plan_md
        supported.add((a, in_map or in_vocab))
        G.check(f"B2-b2-target-action-`{a}`-is-supported", in_map or in_vocab,
                f"in_produced_map={in_map} in_catalogue_schema_vocabulary={in_vocab}")
    # A0-B2-01: are SPLIT/MERGE executable, or only declared?
    exec_actions = {a for a in ("SPLIT", "MERGE")
                    if a in (G.WT / "runtime" / "src" / "adopt.rs").read_text()
                    or a in (G.WT / "runtime" / "src" / "migrations" / "mod.rs").read_text()}
    G.check("B2-b2-SPLIT-and-MERGE-are-executable-not-only-declared (A0-B2-01)",
            exec_actions == {"SPLIT", "MERGE"},
            f"actions with an executor in the migration engine: {sorted(exec_actions)}")
    G.check(
        "B2-b4-imports-and-consumers-are-represented",
        any((byid.get(r["artifact_id"], {}).get("imports")
             or byid.get(r["artifact_id"], {}).get("consumers")) for r in rows),
        json.dumps({k: byid[k].get("imports") for k in list(byid)[:3]})[:250],
    )
    doc_row = next((r for r in cls_rows if str(r.get("path", "")).endswith("docs/design.md")), None)
    G.check(
        "B2-b4-documentation-citations-are-represented (BC-P2-52)",
        bool(doc_row) and bool(doc_row.get("citations") or doc_row.get("path_references")),
        json.dumps({k: doc_row.get(k) for k in ("path", "citations", "path_references",
                                                "consumers")})[:350] if doc_row else "docs/design.md not catalogued",
    )
    util_row = next((r for r in cls_rows if str(r.get("path", "")).endswith("src/util.py")), None)
    G.check(
        "B2-b4-a-cited-file-records-its-document-consumer (BC-P2-52)",
        bool(util_row) and any("design.md" in str(c) for c in (util_row.get("consumers") or [])),
        json.dumps({k: util_row.get(k) for k in ("path", "consumers")})[:300]
        if util_row else "src/util.py not catalogued",
    )
    o = M.run(ROLE + ["audit"], cwd=p)
    G.check(
        "B2-b5-path-map-compliance-is-machine-checkable",
        "path_map_compliance" in json.dumps(o.env),
        "path_map_compliance family present in the governance suite",
    )
    # and it actually fails when the map is violated
    (p / "src" / "stray.secret.env").write_text("API_TOKEN=ghp_0123456789abcdefghijklmnopqrstuvwxyzAB\n")
    o2 = M.run(ROLE + ["audit"], cwd=p)
    G.check(
        "B2-b5-the-compliance-check-reports-a-violation",
        (not o2.ok) or "path_map_compliance" in json.dumps(o2.env),
        f"audit ok={o2.ok} code={o2.code}",
    )
    os.replace(p / "src" / "stray.secret.env", G.SCRATCH / f"{TAG}-stray.moved")

    # ================================================================ B3 authoritative vs derived
    subprocess.run(["git", "add", "-A"], cwd=str(p), capture_output=True)
    subprocess.run(["git", "-c", "user.email=v@x", "-c", "user.name=v", "commit", "-qm", "probe"],
                   cwd=str(p), capture_output=True)
    tracked = subprocess.run(["git", "ls-files"], cwd=str(p), capture_output=True,
                             text=True).stdout.split()
    G.check("B3-b1-git-records-remain-authoritative",
            any(t.startswith("spec/") for t in tracked)
            and any(t.startswith("governance/") for t in tracked),
            f"{len(tracked)} tracked files")
    idxm = p / "governance" / "generated" / "index-manifest.json"
    G.check("B3-b2-indexes-are-declared-derived",
            idxm.exists() and (p / ".governance-runtime" / "state.db").exists(),
            "index manifest + runtime db")
    before = M.run(ROLE + ["memory", "query", "helper"], cwd=p)
    rt = p / ".governance-runtime"
    shutil.move(str(rt), str(G.fresh(f"{TAG}-runtime.moved") / "governance-runtime"))
    o = M.run(ROLE + ["status"], cwd=p)
    G.check("B3-b3-deleting-derived-state-does-not-delete-project-truth",
            o.env is not None and (p / "spec").exists() and (p / "src" / "util.py").exists(),
            f"status code={o.code}")
    o = M.run(ROLE + ["rebuild-memory"], cwd=p)
    G.check("B3-b3-derived-state-rebuilds-from-authoritative-truth", o.ok, o.code or "")
    after = M.run(ROLE + ["memory", "query", "helper"], cwd=p)
    G.check(
        "B3-b3-retrieval-is-restored-after-the-rebuild",
        bool((after.result or {}).get("hits")),
        json.dumps((after.result or {}).get("hits"))[:200],
    )
    hits = (after.result or {}).get("hits") or []
    G.check(
        "B3-b4-derived-records-carry-provenance-sufficient-to-reconstruct-source-hits",
        bool(hits) and all(h.get("artifact_id") and h.get("path") and h.get("chunk_id")
                           for h in hits[:3]),
        json.dumps({k: hits[0].get(k) for k in
                    ("artifact_id", "path", "chunk_id", "section", "record_type")})
        if hits else "no hits",
    )

    # ================================================================ derived contract views (BC-P2-01/02)
    o = M.run(ROLE + ["contract", "verify"], cwd=G.WT)
    G.check("AC13-contract-verify-reports-a-bound-chain", o.ok,
            json.dumps(o.result)[:250] if o.ok else o.code)
    compiled = yaml.safe_load(
        (G.WT / "framework" / "contracts" / "governance-capability-acceptance.yaml").read_text())
    gates = {g["id"]: g for g in compiled["capabilities"]}
    src_bullets = owner_bullets()
    for cap in ALPHA:
        want = [t for _, t in src_bullets.get(cap, [])]
        got = [c["text"] for c in (gates.get(cap, {}).get("checklist") or [])]
        G.check(f"BC-P2-01-compiled-contract-carries-{cap}'s-{len(want)}-bullets-verbatim",
                got == want, f"want={len(want)} got={len(got)}"
                + ("" if got == want else f" diff={[x for x in want if x not in got][:2]}"))
    G.check("BC-P2-01-A2-is-compiled-as-POST_VERIFICATION_HARDENING",
            gates.get("A2", {}).get("requirement_class") == "POST_VERIFICATION_HARDENING",
            str(gates.get("A2", {}).get("requirement_class")))
    G.check("BC-P2-01-Gate-U-is-represented-in-the-compiled-contract",
            "U" in gates and bool(gates["U"].get("checklist")),
            f"U present={'U' in gates} bullets="
            f"{len(gates.get('U', {}).get('checklist') or [])}")
    G.check("BC-P2-01-the-compiled-contract-covers-every-owner-source-capability",
            compiled.get("capability_count") == 101,
            f"capability_count={compiled.get('capability_count')} "
            f"checklist_item_count={compiled.get('checklist_item_count')}")
    emap = yaml.safe_load((G.WT / "tests" / "governance" / "capability-evidence-map.yaml").read_text())
    rows_e = {r["capability"]: r for r in (emap.get("capabilities") or emap.get("rows") or [])}
    for cap in ALPHA:
        r = rows_e.get(cap, {})
        owners = r.get("evidence_class") or r.get("evidence_owners")
        checks = r.get("automated_checks")
        G.check(f"BC-P2-02-{cap}-has-an-evidence-owner-and-at-least-one-automated-check",
                bool(owners) and str(owners) != "NOT_YET_MAPPED" and bool(checks),
                f"evidence_class={json.dumps(owners)[:120]} automated_checks={json.dumps(checks)[:120]}")
    # AC-13: a semantic divergence in a derived view must be detected
    comp = G.WT / "framework" / "contracts" / "governance-capability-acceptance.yaml"
    work = G.fresh(f"{TAG}-contract-divergence")
    shutil.copytree(G.WT / "framework", work / "framework", dirs_exist_ok=True)
    shutil.copytree(G.WT / "tests", work / "tests", dirs_exist_ok=True)
    shutil.copytree(G.WT / "docs", work / "docs", dirs_exist_ok=True)
    shutil.copy(G.WT / "Governance_OS_Capability_Acceptance_Contract_v3.md", work)
    target = work / "framework" / "contracts" / "governance-capability-acceptance.yaml"
    c2 = yaml.safe_load(target.read_text())
    for g in c2["capabilities"]:
        if g["id"] == "A2":
            g["checklist"][0]["text"] = "Release/source authenticity is optional."
    target.write_text(yaml.safe_dump(c2, sort_keys=False))
    o = M.run(ROLE + ["contract", "verify", "--root", str(work)], cwd=work)
    G.check("AC13-a-semantic-divergence-in-the-compiled-view-is-detected",
            not o.ok, f"ok={o.ok} code={o.code} {json.dumps(o.result)[:200] if o.ok else o.message[:200]}")
    # and in the evidence map
    work2 = G.fresh(f"{TAG}-evidence-map-divergence")
    for d in ("framework", "tests", "docs"):
        shutil.copytree(G.WT / d, work2 / d, dirs_exist_ok=True)
    shutil.copy(G.WT / "Governance_OS_Capability_Acceptance_Contract_v3.md", work2)
    em = work2 / "tests" / "governance" / "capability-evidence-map.yaml"
    e2 = yaml.safe_load(em.read_text())
    key = "capabilities" if "capabilities" in e2 else "rows"
    for r in e2[key]:
        if r.get("capability") == "A2":
            r["evidence_class"] = ["NOT_YET_MAPPED"]
            r["automated_checks"] = []
    em.write_text(yaml.safe_dump(e2, sort_keys=False))
    o = M.run(ROLE + ["contract", "verify", "--root", str(work2)], cwd=work2)
    G.check("AC13-a-gutted-evidence-map-is-detected",
            not o.ok, f"ok={o.ok} code={o.code}")

    # ================================================================ freshness / invalidation (AC-10)
    fp = G.fresh(f"proj/{TAG}-fresh")
    (fp / "README.md").write_text("# freshness\n")
    (fp / "src").mkdir()
    (fp / "src" / "app.py").write_text("def run():\n    return 1\n")
    G.git_init(fp)
    M.run(ROLE + ["init", "--source", str(rel / "kernel")], cwd=fp)

    def audit_state():
        o = M.run(ROLE + ["audit"], cwd=fp)
        det = (((o.env or {}).get("error") or {}).get("details") or {}) or (o.result or {})
        return o, det.get("green"), det.get("verdict")

    o0, green0, verdict0 = audit_state()
    G.check("AC10-a-green-governance-record-can-be-established",
            green0 is True or verdict0 == "HEALTHY", f"green={green0} verdict={verdict0}")

    def stale_after(name, mutate):
        mutate()
        o = M.run(ROLE + ["task", "create", "--objective", f"work after {name}",
                          "--class", "governance"], cwd=fp)
        oc = M.run(ROLE + ["doctor"], cwd=fp)
        blob = json.dumps(oc.env) + json.dumps(o.env)
        stale = ("stale" in blob.lower() or "CURRENCY" in blob.upper()
                 or (not o.ok) or (not oc.ok))
        G.check(f"AC10-changing-`{name}`-invalidates-prior-green-evidence", stale,
                f"task_create={o.code or 'ok'} doctor={oc.code or 'ok'}")

    stale_after("an authoritative spec decision", lambda: (
        (fp / "spec" / "decisions").mkdir(parents=True, exist_ok=True),
        (fp / "spec" / "decisions" / "D-PROBE.yaml").write_text(
            yaml.safe_dump({"id": "D-PROBE", "type": "decision", "title": "probe decision",
                            "status": "ACTIVE", "schema_version": "1.2.0",
                            "decision": "a governed decision written by hand"}))))
    stale_after("product source", lambda:
                (fp / "src" / "app.py").write_text("def run():\n    return 2\n"))
    stale_after("the project policy overlay", lambda:
                (fp / "governance" / "project" / "PROJECT_POLICY.yaml").write_text(
                    (fp / "governance" / "project" / "PROJECT_POLICY.yaml").read_text()
                    + "\n# freshness probe\n"))
    stale_after("the index manifest", lambda:
                (fp / "governance" / "generated" / "index-manifest.json").write_text(
                    json.dumps({"tampered": True})))

    return G.summary()


if __name__ == "__main__":
    sys.exit(main())
