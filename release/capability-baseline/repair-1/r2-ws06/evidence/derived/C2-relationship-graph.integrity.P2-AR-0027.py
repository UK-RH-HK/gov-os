"""DERIVED COPY (P2-AR-0027, WS-6 round 2) of release/capability-baseline/audit-0/beta-r/evidence/C2-relationship-graph.py.
The audit-of-record probe is run UNEDITED as well (evidence/after/beta-r.C2-relationship-graph.out): it reads only
`gov audit --family graph_integrity|schema_invariants` and doctor D015/D014, whose families are WS-2's files; wiring the
BC-P2-28 check (memory::integrity::check) into them is an integration point. This copy changes ONLY:
  (0) the helper library is imported from the audit of record's evidence directory (unedited);
  (1) after each unedited check it ADDS one `*-product` line that reads the product's own graph-integrity check
      (`gov memory integrity`, which also runs on every index build) for the same seeded fault.
Every unedited line and check is kept byte-identical.
"""
"""C2 Relationship/graph memory (Contract v3 lines 229-232).

b1: every one of the 20 named relationship types can be recorded and is materialised as a typed edge.
b2: graph integrity checks — separately seeded ORPHAN, STALE, REVERSED and INVALID relationships; observe whether
    `gov audit --family graph_integrity`, `gov doctor` (D015) or schema_invariants detect each one.
b3: deterministic impact traversal over record and code edges (`gov memory impact`, `gov cit simulate`).
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[6] / "release/capability-baseline/audit-0/beta-r/evidence/lib"))  # (derived)
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

TYPES = ["DEPENDS_ON", "BLOCKS", "IMPLEMENTS", "REALISES", "GOVERNED_BY", "CONSTRAINS", "DERIVED_FROM", "SUPERSEDES",
         "VALIDATED_BY", "TESTS", "USES", "PRODUCES", "CONSUMES", "AFFECTS", "GENERATED_FROM", "CALLS", "IMPORTS", "OWNS",
         "FAILED_BECAUSE", "LEARNED_FROM"]


def section(t):
    log("")
    log("=" * 100)
    log(t)
    log("=" * 100)


def audit(*fams):
    args = ["audit", "--no-persist"]
    for f in fams:
        args += ["--family", f]
    r = g.run(*args)
    body = r.get("result") or (r.get("error") or {}).get("details") or {}
    return body


def doctor_check(cid):
    r = g.run("doctor")
    body = r.get("result") or (r.get("error") or {}).get("details") or {}
    for c in body.get("checks", []):
        if c.get("id") == cid:
            return c
    return None


root, g = build_rich("c2")


def integrity_msgs(kind):
    """(derived) messages of the product's graph-integrity findings of `kind`."""
    r = g.ok("memory", "integrity", show=False)
    return [f["message"] for f in r["findings"] if f["kind"] == kind]

section("C2-b1 typed relationships: one explicit `relations:` entry per named type")
rels = [{"type": t, "target": "REQ-0001"} for t in TYPES if t != "SUPERSEDES"]
y(root, "spec/architecture/ARCH-0201.yaml", {"id": "ARCH-0201", "type": "architecture", "title": "Relationship carrier",
  "status": "ACTIVE", "summary": "carries every relationship type", "relations": rels})
y(root, "spec/decisions/D-0201.yaml", {"id": "D-0201", "type": "decision", "title": "Superseding decision",
  "status": "ACTIVE", "question": "q?", "relations": [{"type": "SUPERSEDES", "target": "D-0102"}], "supersedes": []})
commit_all(root, "relations")
g.ok("rebuild-memory")
types_seen = {r[0] for r in q(root, "SELECT DISTINCT type FROM edges")}
arch_types = {r[0] for r in q(root, "SELECT type FROM edges WHERE src='ARCH-0201'")}
log("edge types present in store:", sorted(types_seen))
log("missing from store:", sorted(set(TYPES) - types_seen))
nb = g.ok("memory", "graph", "ARCH-0201")
log("gov memory graph ARCH-0201 ->", [(n["via"], n["node"]) for n in nb][:25])
code_edges = q(root, "SELECT src, type, dst FROM edges WHERE type IN ('CALLS','IMPORTS') ORDER BY type, src")
log("code-derived edges (CALLS/IMPORTS):", code_edges)
check("C2-b1", set(TYPES) <= types_seen and len(arch_types) >= 19,
      "all 20 named relationship types are stored as typed edges; code analysis derives CALLS/IMPORTS")
# field-derived relations
fld = q(root, "SELECT src, type, dst FROM edges WHERE src IN ('F-0001','TST-0001','REQ-0001','D-0102') ORDER BY src, type")
log("field-derived edges (feature/requirements/scenarios/interfaces/supersedes/tests):", fld)

section("C2-b2 integrity: baseline")
b0 = audit("graph_integrity")
log("baseline graph_integrity family:", json.dumps(b0.get("families", {}).get("graph_integrity")), "findings:", [f["message"] for f in b0.get("findings", [])])

section("C2-b2a ORPHAN: governed record with no relationships at all")
y(root, "spec/requirements/REQ-0299.yaml", {"id": "REQ-0299", "type": "requirement", "title": "Orphan requirement with no feature, test or decision",
  "status": "ACTIVE", "kind": "functional"})
commit_all(root, "orphan")
g.ok("rebuild-memory", "--incremental", show=False)
b = audit("graph_integrity")
gi = b.get("families", {}).get("graph_integrity", {})
log("graph_integrity detail:", json.dumps(gi))
log("graph_integrity findings:", [f["message"] for f in b.get("findings", [])])
d15 = doctor_check("D015")
log("doctor D015:", d15)
orph_rows = q(root, "SELECT a.artifact_id FROM artifacts a WHERE a.graph=1 AND a.record_type!='file' AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.src=a.artifact_id OR e.dst=a.artifact_id)")
log("orphan nodes per the product's own orphan query (graph::orphan_nodes):", orph_rows)
orphan_counted = gi.get("detail", {}).get("orphans", 0) >= 1 or "orphan" in json.dumps(d15 or {})
orphan_flagged = any("orphan" in f["message"].lower() for f in b.get("findings", [])) or (d15 and not d15.get("ok") and "orphan" in d15.get("message", ""))
check("C2-b2-orphan-counted", orphan_counted, "orphan relationship state is computed (count reported)")
check("C2-b2-orphan-flagged", orphan_flagged, "orphan state raises a finding / failing check")
m = integrity_msgs("orphan"); log("(derived) product orphan findings:", m)
check("C2-b2-orphan-product", any("REQ-0299" in x for x in m), "(derived) the product's graph-integrity check raises the orphan as a finding")

section("C2-b2b STALE: relationship to a record that is no longer current (SUPERSEDED target) and to a deleted file")
y(root, "spec/features/F-0202.yaml", {"id": "F-0202", "type": "feature", "title": "Feature governed by a superseded decision",
  "status": "ACTIVE", "readiness": {}, "decisions": ["D-0101"]})
commit_all(root, "stale relationship")
g.ok("rebuild-memory", "--incremental", show=False)
log("edges from F-0202:", q(root, "SELECT src,type,dst FROM edges WHERE src='F-0202'"), "; D-0101 status:", q(root, "SELECT status, superseded_by FROM artifacts WHERE artifact_id='D-0101'"))
b = audit("graph_integrity", "schema_invariants")
stale_msgs = [f["message"] for f in b.get("findings", []) if "F-0202" in f["message"] or "D-0101" in f["message"]]
log("findings mentioning F-0202/D-0101:", stale_msgs)
check("C2-b2-stale-superseded-target", any("F-0202" in m for m in stale_msgs),
      "edge to a SUPERSEDED record (stale relationship) is detected")
m = integrity_msgs("stale"); log("(derived) product stale findings:", m)
check("C2-b2-stale-superseded-target-product", any("F-0202" in x and "D-0101" in x for x in m), "(derived) the product's graph-integrity check raises the stale relationship")
# stale code edge: rename the callee file; the unchanged caller keeps its old edge under an incremental rebuild
(root / "src/web/format.ts").rename(root / "src/web/money.ts")
commit_all(root, "rename format.ts -> money.ts (caller not edited)")
g.ok("rebuild-memory", "--incremental", show=False)
stale_code = q(root, "SELECT src,type,dst FROM edges WHERE dst='file:src/web/format.ts'")
log("edges still pointing at the renamed file:", stale_code)
b = audit("graph_integrity")
log("graph_integrity findings:", [f["message"] for f in b.get("findings", [])])
d15 = doctor_check("D015")
log("doctor D015:", d15)
check("C2-b2-stale-dangling", bool(stale_code) and any("dangling" in f["message"] for f in b.get("findings", [])),
      "edge left pointing at a renamed/deleted artefact is detected as dangling")
m = integrity_msgs("dangling"); log("(derived) product dangling findings:", m)
check("C2-b2-stale-dangling-product", any("format.ts" in x for x in m), "(derived) the product's graph-integrity check raises the edge left pointing at the renamed file")
# restore
(root / "src/web/money.ts").rename(root / "src/web/format.ts")
commit_all(root, "restore format.ts")
g.ok("rebuild-memory", show=False)

section("C2-b2c REVERSED: relationship recorded in the wrong direction")
# a requirement that claims to IMPLEMENT a task and a test obligation that is TESTED BY a requirement; plus a supersession cycle
y(root, "spec/requirements/REQ-0203.yaml", {"id": "REQ-0203", "type": "requirement", "title": "Reversed direction requirement",
  "status": "ACTIVE", "relations": [{"type": "IMPLEMENTS", "target": "ARCH-0101"}, {"type": "TESTS", "target": "TST-0001"}]})
d101 = yaml.safe_load((root / "spec/decisions/D-0101.yaml").read_text())
d101["supersedes"] = ["D-0102"]  # D-0102 supersedes D-0101 AND D-0101 supersedes D-0102: a reversed/cyclic supersession
y(root, "spec/decisions/D-0101.yaml", d101)
commit_all(root, "reversed")
g.ok("rebuild-memory", "--incremental", show=False)
log("supersession edges:", q(root, "SELECT src,type,dst FROM edges WHERE type='SUPERSEDES'"))
b = audit("graph_integrity", "schema_invariants")
rev_msgs = [f["message"] for f in b.get("findings", []) if any(x in f["message"] for x in ("REQ-0203", "D-0101", "D-0102", "cycle", "revers"))]
log("findings mentioning the reversed/cyclic relationships:", rev_msgs)
d14 = doctor_check("D014")
log("doctor D014:", d14)
check("C2-b2-reversed-direction", any("REQ-0203" in m for m in rev_msgs),
      "reversed-direction edges (requirement IMPLEMENTS architecture; requirement TESTS a test obligation) are detected")
check("C2-b2-reversed-supersession-cycle", any("superseded by" in m for m in rev_msgs) or (d14 and not d14.get("ok")),
      "cyclic (mutually reversed) supersession is detected (as an authority conflict)")
mr = integrity_msgs("reversed"); mc = integrity_msgs("supersession_cycle"); log("(derived) product reversed findings:", mr, "| cycles:", mc)
check("C2-b2-reversed-direction-product", sum("REQ-0203" in x for x in mr) >= 2, "(derived) the product's graph-integrity check raises both reversed relationships of REQ-0203")
check("C2-b2-reversed-supersession-cycle-product", any("D-0101" in x and "D-0102" in x for x in mc), "(derived) the product's graph-integrity check raises the supersession cycle")
y(root, "spec/decisions/D-0101.yaml", {k: v for k, v in d101.items() if k != "supersedes"})
(root / "spec/requirements/REQ-0203.yaml").unlink()
commit_all(root, "undo reversed")
g.ok("rebuild-memory", show=False)

section("C2-b2d INVALID: unknown relationship type and dangling target")
y(root, "spec/requirements/REQ-0204.yaml", {"id": "REQ-0204", "type": "requirement", "title": "Invalid relationships",
  "status": "ACTIVE", "relations": [{"type": "LOVES", "target": "F-0001"}, {"type": "DEPENDS_ON", "target": "REQ-9999"}]})
commit_all(root, "invalid")
g.ok("rebuild-memory", "--incremental", show=False)
log("stored edges from REQ-0204:", q(root, "SELECT src,type,dst FROM edges WHERE src='REQ-0204'"))
b = audit("graph_integrity", "schema_invariants")
inv = [f["message"] for f in b.get("findings", []) if "REQ-0204" in f["message"] or "REQ-9999" in f["message"] or "dangling" in f["message"]]
log("findings:", inv)
check("C2-b2-invalid-type", any("REQ-0204" in m and ("LOVES" in m or "enum" in m) for m in inv), "unknown relationship type rejected by schema_invariants")
check("C2-b2-invalid-dangling", any("dangling" in m for m in inv), "relationship to a non-existent artefact detected as dangling")
mi = integrity_msgs("ill_typed"); md = integrity_msgs("dangling"); log("(derived) product ill-typed findings:", mi, "| dangling:", md)
check("C2-b2-invalid-type-product", any("REQ-0204" in x and "LOVES" in x for x in mi), "(derived) the product's graph-integrity check raises the unknown relationship type")
check("C2-b2-invalid-dangling-product", any("REQ-9999" in x for x in md), "(derived) the product's graph-integrity check raises the dangling relationship")
(root / "spec/requirements/REQ-0204.yaml").unlink()
commit_all(root, "undo invalid")
g.ok("rebuild-memory", show=False)

section("C2-b3 impact traversal (records and code)")
imp = g.ok("memory", "impact", "REQ-0001", "--depth", "2")
log("gov memory impact REQ-0001 --depth 2:", [(r["node"], r["hop"], r["via"]) for r in imp])
imp2 = g.ok("memory", "impact", "file:src/app/models.py", "--depth", "2")
log("gov memory impact file:src/app/models.py:", [(r["node"], r["hop"], r["via"]) for r in imp2])
imp_again = g.ok("memory", "impact", "REQ-0001", "--depth", "2", show=False)
c = g.ok("cit", "propose", "--proposal", "Change REQ-0001 to allow fractional cents", "--trigger", "behaviour_change", "--targets", "REQ-0001")
sim = g.ok("cit", "simulate", c["id"])
im = sim.get("impact", {})
log("cit simulate impact: radius", im.get("radius"), "graph nodes:", [n.get("node") if isinstance(n, dict) else n for n in im.get("graph", im.get("affected", []))][:20])
log("cit simulate affected keys:", sorted(im.keys()))
nodes = {r["node"] for r in imp}
check("C2-b3", {"F-0001", "TST-0001"} <= nodes and "file:src/app/api.py" in {r["node"] for r in imp2} and imp == imp_again
      and im.get("radius"), "deterministic impact traversal over typed edges (records and code), reproducible, consumed by CIT-P")
summary()
