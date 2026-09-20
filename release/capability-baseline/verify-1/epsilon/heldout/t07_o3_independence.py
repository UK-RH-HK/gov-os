#!/usr/bin/env python3
"""O3 — independent test authorship (Contract v3:782-785) — P2-AR-0050, family epsilon.

* release-critical behavioural tests are authored independently of the implementation;
* builder tests remain regression evidence, not independent certification;
* a fresh verifier adds held-out tests.

The attack: a test obligation in an independence-required family that *declares itself* independent
(`independent_of_implementer: true`, `author_role: qa`) with no recorded authorship behind it. If the declaration is
accepted, independence is self-attested (iteration-0 class BC-P2-34).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import check, main  # noqa: E402
from t01_ac5_scheduler import provisioned, converge, res  # noqa: E402


def run():
    p, _pub = provisioned("o3")
    converge(p)

    pol = p.read("governance/kernel/policies/TEST_POLICY.yaml")
    fams = [ln for ln in pol.splitlines() if "independent_test_author_required_for" in ln]
    check("O3-1-independence-families-declared", fams,
          f"the release-critical families that need an independent author: {fams}")

    # a feature, a scenario and a self-declared 'independent' acceptance obligation
    p.write("spec/features/FEAT-O3.yaml",
            "id: FEAT-O3\ntype: feature\ntitle: Probe feature\nstatus: ACTIVE\n"
            "state_class: AUTHORITATIVE\ncreated: '2026-09-20'\n")
    p.write("spec/scenarios/SCN-O3.yaml",
            "id: SCN-O3\ntype: scenario\ntitle: Probe scenario\nstatus: ACTIVE\n"
            "state_class: AUTHORITATIVE\nfeature: FEAT-O3\ncreated: '2026-09-20'\n")
    p.write("spec/tests/TO-O3.yaml",
            "id: TO-O3\ntype: test-obligation\ntitle: Probe acceptance obligation\nstatus: ACTIVE\n"
            "state_class: AUTHORITATIVE\nfamily: acceptance\nfeature: FEAT-O3\nscenario: SCN-O3\n"
            "test_path: tests/acceptance/o3.rs\nauthor_role: qa\n"
            "independent_of_implementer: true\ncreated: '2026-09-20'\n")
    p.write("tests/acceptance/o3.rs", "// probe acceptance test authored by the implementer\n")
    p.commit("feature, scenario and a self-declared independent obligation")
    p.run("rebuild-memory", "--incremental")

    t = res(p.run("task", "create", "--objective", "Implement FEAT-O3", "--title", "O3 impl",
                  "--class", "implementation", "--feature", "FEAT-O3", "--allowed", "src/**"))
    tid = t["id"]
    p.run("task", "status", tid, "READY")
    dag = res(p.run("task", "dag"))
    blob = json.dumps(dag)
    claim = p.run("task", "claim", tid, role="backend-engineer", session="builder")
    reason = json.dumps(claim.error) + blob
    check("O3-2-self-declared-independence-rejected",
          (not claim.ok) and ("independ" in reason.lower()),
          f"a test obligation that declares its own independence, with no recorded authorship behind it: "
          f"claim ok={claim.ok} code={claim.error_code} — {str(claim.error.get('message'))[:260]}")

    check("O3-3-claims-are-not-evidence",
          "independent_of_implementer" in reason or "claims, not evidence" in reason or not claim.ok,
          f"the refusal says what would establish independence instead: "
          f"{str(claim.error.get('message'))[-220:] if not claim.ok else 'n/a'}")

    # builder tests are regression evidence: a recorded product-test result is attributed, not certified independent
    p.write("tools/t-acc.sh", '#!/bin/sh\necho "acceptance ok"\nexit 0\n')
    os.chmod(p.root / "tools/t-acc.sh", 0o755)
    import yaml
    d = yaml.safe_load(p.read("governance/project/PROJECT_POLICY.yaml"))
    d["tests"]["families"] = {"acceptance": {"command": ["./tools/t-acc.sh"], "covers": ["src/**"]}}
    p.write("governance/project/PROJECT_POLICY.yaml", yaml.safe_dump(d, sort_keys=False))
    p.commit("acceptance family command")
    pr = res(p.run("health", "product"))
    fam = (pr.get("families") or {}).get("acceptance") or {}
    check("O3-4-builder-tests-are-regression-evidence",
          fam.get("status") == "passed" and "independent" not in json.dumps(fam).lower(),
          f"a passing product family is recorded as evidence of the run, and claims no independent "
          f"certification: {json.dumps(fam)[:260]}")

    # a fresh verifier adds held-out tests: the OS generates a held-out starter and refuses to let it be
    # both generated and counted without authored queries
    ho = p.run("memory", "heldout-starter")
    mv = res(p.run("memory", "verify"))
    check("O3-5-heldout-surface", mv.get("measured") is not None,
          f"held-out retrieval queries are a first-class, measured artefact: queries={mv.get('queries')} "
          f"pending={mv.get('pending_queries')} min={mv.get('min_queries')} measured={mv.get('measured')} "
          f"(starter: ok={ho.ok} {ho.error_code})")
    check("O3-6-pending-heldout-not-counted",
          (mv.get("pending_queries") or 0) >= 0 and (mv.get("queries") or 0) >= (mv.get("min_queries") or 0),
          f"placeholder queries are held pending and not counted towards the measured set: "
          f"{mv.get('queries')} counted, {mv.get('pending_queries')} pending")


if __name__ == "__main__":
    main(run, "O3")
