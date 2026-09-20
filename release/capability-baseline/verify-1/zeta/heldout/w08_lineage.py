"""W8 — forward and reverse lineage (Contract v3:1146-1152). Held-out, P2-AR-0051."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def reach(v):
    return {n["node"] for n in (v.get("reach") or [])}


def main():
    r = lib.Repo("w08")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", "TASK-0001", "READY")
    r.ok("task", "claim", "TASK-0001", role="backend-engineer", session="impl1")
    r.put("src/export.rs", "// implements REQ-0001\npub fn export() {}\n")
    r.ok("rebuild-memory", "--incremental")
    r.ok("verify", "product")
    rep = r.receipt("TASK-0001", ["src/export.rs"], work="implemented the CSV export")
    out = r.close("TASK-0001", rep, role="backend-engineer", session="impl1")
    assert out.get("ok"), json.dumps(out.get("error"))[:600]
    rpt = out["result"]["report"]

    # a governed release record shipping that work, validated by the audit evidence
    aud = r.run("audit")
    aid = ((aud.get("result") or (aud.get("error") or {}).get("details") or {}).get("audit"))
    r.put("spec/releases/REL-0001.yaml", """id: REL-0001
type: release
title: Ledger export 1.0
status: ACTIVE
version: "1.0"
derived_from: [TASK-0001, %s]
validated_by: [%s]
summary: the release that ships the CSV export
""" % (rpt, aid))
    r.commit("release")
    r.ok("rebuild-memory", "--incremental")

    # ---- W8.1 the forward chain -------------------------------------------------------------
    chain = {}
    for start, want in (("F-0001", {"SCN-0001", "REQ-0001", "TASK-0001"}),
                        ("SCN-0001", {"TO-0001"}),
                        ("REQ-0001", {"TASK-0001", rpt}),
                        ("D-0100", {"TASK-0001"}),
                        ("ARCH-0100", {"TASK-0001"}),
                        ("TASK-0001", {rpt, "file:src/export.rs"})):
        got = reach(r.ok("artefact", "lineage", start, "--direction", "down", "--depth", "8"))
        chain[start] = sorted(want - got)
    lib.check("W8-01", "the forward chain feature -> scenario -> requirement -> decision -> "
                       "architecture -> task -> code -> test -> evidence is walkable",
              not any(chain.values()), json.dumps(chain))
    rel = reach(r.ok("artefact", "lineage", rpt, "--direction", "down", "--depth", "8"))
    lib.check("W8-01b", "... and continues to the release record",
              "REL-0001" in rel, sorted(rel))

    # ---- W8.2 reverse impact ----------------------------------------------------------------
    up = reach(r.ok("artefact", "lineage", "REL-0001", "--direction", "up", "--depth", "8"))
    down_req = reach(r.ok("artefact", "lineage", "REQ-0001", "--direction", "down", "--depth", "8"))
    lib.check("W8-02", "reverse impact from a changed requirement reaches the implementation, "
                       "its tests and the release evidence",
              {"TASK-0001", rpt}.issubset(down_req)
              and ("REL-0001" in down_req or {"TASK-0001", rpt} <= up),
              json.dumps({"requirement_impact": sorted(down_req),
                          "release_upstream": sorted(up)})[:600])

    # the CIT impact simulation is the same question asked of a proposed change
    man = os.path.join(r.state, "m.json")
    with open(man, "w") as f:
        json.dump([{"op": "write_file", "path": "spec/requirements/REQ-0001.yaml",
                    "content": r.read("spec/requirements/REQ-0001.yaml").replace(
                        "one row per ledger entry", "one row per ledger entry plus a header"),
                    "reason": "header row"}], f)
    cit = r.run("cit", "propose", "--proposal", "header row", "--targets", "REQ-0001",
                "--manifest", man, role="change-controller")
    cid = (cit.get("result") or {}).get("id")
    sim = r.run("cit", "simulate", cid, role="change-controller") if cid else {}
    nodes = {a["node"] for a in ((sim.get("result") or {}).get("impact") or {}).get("affected") or []}
    lib.check("W8-02b", "a proposed change to the requirement names the affected implementation, "
                        "tests and evidence before it is applied",
              {"TASK-0001", "TO-0001", rpt}.issubset(nodes),
              json.dumps(sorted(nodes))[:400])

    # ---- W8.3 missing lineage link detection ------------------------------------------------
    r.put("spec/requirements/REQ-0500.yaml", """id: REQ-0500
type: requirement
title: Dangling requirement
status: ACTIVE
version: 1
kind: functional
governed_by: [D-9999]
acceptance_criteria: [it does something]
summary: names a decision that does not exist
""")
    chk = r.ok("artefact", "check")
    h = r.ok("health", "run", "--tier", "G5")
    gi = (h.get("families") or {}).get("graph_integrity") or {}
    blob = json.dumps(chk) + json.dumps(gi) + json.dumps(
        [f for f in h.get("findings") or [] if f.get("family") == "graph_integrity"])
    lib.check("W8-03", "a lineage link to a record that does not exist is detected by name",
              "D-9999" in blob, blob[:400])

    # ---- W8.4 stale lineage link detection --------------------------------------------------
    r.put("spec/decisions/D-0300.yaml", """id: D-0300
type: decision
title: Use RFC4180 CSV (revised)
status: ACTIVE
version: 2
question: Which CSV dialect?
options:
  - {id: RFC4180, description: the RFC 4180 dialect}
chosen_option: RFC4180
rationale: restated
supersedes: [D-0100]
summary: supersedes D-0100
""")
    chk = r.ok("artefact", "check")
    stale = [x for x in (chk.get("stale_links") or []) if x.get("stale_target") == "D-0100"]
    lib.check("W8-04", "a link from current work to a superseded record is detected as a stale "
                       "lineage link, naming both ends",
              bool(stale), json.dumps(chk.get("stale_links"))[:500])

    # ---- W8.5 cross-language / cross-repository relationships -------------------------------
    # the code graph indexes symbols and references across languages; a second ecosystem is added
    r.put("src/exporter.py",
          "import csv\n\n\n"
          "class Exporter:\n"
          "    def write(self, rows):\n"
          "        return csv.writer(rows)\n")
    r.put("src/export_check.py",
          "from exporter import Exporter\n\n\n"
          "def check_export(rows):\n"
          "    e = Exporter()\n"
          "    return e.write(rows)\n")
    r.put("pyproject.toml", "[project]\nname = 'exporter-tools'\nversion = '0.1.0'\n")
    r.commit("second ecosystem")
    reb = r.ok("rebuild-memory")
    eco = [e["id"] for e in (reb.get("ecosystems") or {}).get("ecosystems", [])]
    import sqlite3
    c = sqlite3.connect(r.path(".governance-runtime/state.db"))
    by_lang = dict(c.execute(
        "select language, count(*) from symbols group by 1").fetchall())
    py_edges = c.execute(
        "select count(*) from edges where src like '%.py' and type in ('CALLS','IMPORTS')"
    ).fetchone()[0]
    rs_edges = c.execute(
        "select count(*) from edges where src like '%.rs' and type in ('CALLS','IMPORTS')"
    ).fetchone()[0]
    c.close()
    lib.check("W8-05", "code-level relationships (calls, imports) are captured in more than one "
                       "language in the same repository",
              len(eco) >= 2 and len(by_lang) >= 2 and py_edges > 0 and rs_edges > 0,
              json.dumps({"ecosystems": eco, "symbols_by_language": by_lang,
                          "python_code_edges": py_edges, "rust_code_edges": rs_edges}))
    # cross-repository: recorded as not exercised here (single-repository probe), see the report
    lib.check("W8-05b", "recorded, not claimed: a single relationship spanning two languages "
                        "(FFI) and cross-repository relationships were not exercised; W8:1152 "
                        "makes them conditional (\"where in scope\")",
              True, "single-repository probe; no FFI convention declared in the repository contract")

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
