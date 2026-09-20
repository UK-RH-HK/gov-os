"""W7 — orphan / dead-output and unexplained-output detection (Contract v3:1138-1144).

Held-out, P2-AR-0051. Every class is injected and must be detected BY NAME, and the detection must
generate governed investigation work rather than deleting anything.
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def orphans(r, tier="G5"):
    h = r.ok("health", "run", "--tier", tier)
    fam = (h.get("families") or {}).get("lineage_orphans") or {}
    findings = [f for f in (h.get("findings") or []) if f.get("family") == "lineage_orphans"]
    return fam, findings


def main():
    r = lib.Repo("w07")
    lib.seed_green(r)

    # ---- inject one instance of every W7 class ----------------------------------------------
    # 1139: a completed authoritative output that declares a consumer nobody consumes
    r.put("spec/architecture/ARCH-0200.yaml", """id: ARCH-0200
type: architecture
title: Event bus boundary
status: ACTIVE
version: 1
consumers: [TASK-0900]
summary: an architecture record whose expected consumer never consumed it
""")
    # 1140: a requirement with no downstream implementation or test path
    r.put("spec/requirements/REQ-0900.yaml", """id: REQ-0900
type: requirement
title: Retention policy
status: ACTIVE
version: 1
kind: functional
acceptance_criteria: [records are retained for seven years]
summary: a requirement nothing implements or tests
""")
    # 1141: concluded research that named a decision it should feed, and that decision was taken
    # without citing it
    r.put("spec/decisions/D-0900.yaml", """id: D-0900
type: decision
title: Retention store choice
status: ACTIVE
version: 1
question: Where do we retain records?
options:
  - {id: objectstore, description: object storage}
  - {id: database, description: relational}
chosen_option: objectstore
rationale: decided without waiting for the survey
summary: a decision taken without consuming the research that was meant to feed it
""")
    res = dict(lib.RESEARCH)
    res["id"] = "RES-0900"
    res["influences"] = ["D-0900"]
    r.ok("research", "record", "--fields", json.dumps(res), role="research-agent")
    # 1142: an acceptance-level test obligation linked to no current requirement or scenario
    r.put("spec/tasks/TO-0900.yaml", """id: TO-0900
type: test-obligation
title: Unjustified acceptance test
status: ACTIVE
family: acceptance
test_path: tests/unjustified.rs
author_role: independent-test-designer
independent_of_implementer: true
summary: an acceptance test that justifies itself to nothing
""")
    r.put("tests/unjustified.rs", "#[test]\nfn unjustified() {}\n")
    # 1143: source code no governed work produced and no current spec names
    r.put("src/undocumented.rs", "// nothing governs this\npub fn undocumented() {}\n")
    r.commit("inject orphans")
    r.ok("rebuild-memory", "--incremental")
    tasks_before = set(os.listdir(r.path("spec/tasks")))
    files_before = sorted(os.listdir(r.path("src"))) + sorted(os.listdir(r.path("tests")))

    fam, findings = orphans(r)
    text = json.dumps(findings)
    detail = json.dumps(fam.get("detail") or {})
    blob = text + detail

    for cid, name, subject, bullet in (
            ("W7-01", "a completed output with an expected consumer and no actual consumer",
             "ARCH-0200", 1139),
            ("W7-02", "a requirement with no downstream implementation or test path",
             "REQ-0900", 1140),
            ("W7-03", "research that named a decision it should feed and was never consumed",
             "RES-0900", 1141),
            ("W7-04", "an acceptance test with no requirement or scenario", "TO-0900", 1142),
            ("W7-05", "implementation code with no active spec justification",
             "src/undocumented.rs", 1143)):
        lib.check(cid, "%s is detected by name (Contract v3:%d)" % (name, bullet),
                  subject in blob,
                  "not named in the lineage_orphans finding set; detected: %s" %
                  json.dumps([f.get("message", "")[:80] for f in findings])[:500])

    # each detection must name its subject, not only report a count
    orphan_findings = [f for f in findings if f.get("orphan")]
    subjects = [(f.get("orphan") or {}).get("subject") for f in orphan_findings]
    named = bool(subjects) and all(s for s in subjects)
    kinds = {k for k in ((fam.get("detail") or {}).get("by_kind") or {})}
    lib.check("W7-06", "every orphan finding names its subject and its contract line (never only "
                       "a count), and all five W7 kinds are represented",
              named and
              {"unconsumed-output", "spec-without-downstream-path", "unconsumed-research",
               "unjustified-acceptance-test", "unjustified-code"} <= kinds,
              json.dumps({"subjects": subjects, "by_kind": (fam.get("detail") or {}).get("by_kind")})[:700])

    # ---- W7.6 orphans produce governed investigation work, and nothing is deleted ------------
    tasks_after = set(os.listdir(r.path("spec/tasks")))
    new_tasks = sorted(tasks_after - tasks_before)
    inv = {}
    for f in new_tasks:
        d = yaml.safe_load(open(r.path("spec/tasks/" + f))) or {}
        i = d.get("investigates")
        if i:
            link = [x for x in (d.get("relations") or [])
                    if x.get("target") == i["subject"]]
            inv[i["subject"]] = (d["id"], d.get("generated_by"), link, i.get("kind"))
    files_after = sorted(os.listdir(r.path("src"))) + sorted(os.listdir(r.path("tests")))
    lib.check("W7-07", "each detected orphan gets one linked, governed investigation task and "
                       "nothing is deleted",
              set(subjects) <= set(inv)
              and all(v[1] == "health:lineage_orphans" and v[2] for v in inv.values())
              and files_before == files_after,
              json.dumps({"orphans": subjects, "investigations": inv,
                          "files_unchanged": files_before == files_after})[:800])

    # idempotent: a second suite run creates no duplicates
    before2 = set(os.listdir(r.path("spec/tasks")))
    orphans(r)
    after2 = set(os.listdir(r.path("spec/tasks")))
    lib.check("W7-07b", "re-running detection creates no duplicate investigations",
              before2 == after2, "new: %s" % sorted(after2 - before2))

    # ---- the remediation must not itself hide the orphan ------------------------------------
    fam2, findings2 = orphans(r)
    blob2 = json.dumps(findings2) + json.dumps(fam2.get("detail") or {})
    lib.check("W7-08", "the generated investigation does not count as a consumer: the orphans are "
                       "still reported after remediation is created",
              all(x in blob2 for x in ("ARCH-0200", "REQ-0900", "RES-0900", "TO-0900",
                                       "src/undocumented.rs")),
              json.dumps([f.get("code") for f in findings2])[:400])

    # ---- a genuinely consumed output is NOT reported (no blanket false positive) -------------
    # SCN-0001 and TO-0001 are genuinely consumed (TO-0001 validates SCN-0001/REQ-0001, and the
    # test file it names was produced by governed work), so neither may be reported.
    consumed = [f for f in findings2
                if ((f.get("orphan") or {}).get("subject") in
                    ("TO-0001", "SCN-0001", "file:tests/export_acceptance.rs"))]
    lib.check("W7-09", "outputs that are genuinely consumed are not reported as orphans "
                       "(no blanket false positive)",
              not consumed, json.dumps(consumed)[:400])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
