"""W2 — typed output -> input contracts (Contract v3:1082-1090). Held-out, P2-AR-0051."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def main():
    r = lib.Repo("w02")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.ok("research", "record", "--fields", json.dumps(lib.RESEARCH), role="research-agent")
    r.commit("seed")

    # ---- W2.1 relationship type explicit, and in the right direction ------------------------
    v = r.ok("artefact", "show", "REQ-0001")
    edges = v["edges"]
    consumes = [e for e in edges if e["type"] == "CONSUMES" and e["dst"] == "REQ-0001"]
    realises = [e for e in edges if e["type"] == "REALISES" and e["src"] == "REQ-0001"]
    lib.check("W2-01", "edges are typed and directed (task CONSUMES requirement, not the reverse)",
              bool(consumes) and bool(realises) and
              not [e for e in edges if e["type"] == "CONSUMES" and e["src"] == "REQ-0001"],
              json.dumps(edges))

    # ---- W2.2 required vs optional is explicit in the manifest -------------------------------
    r.put("spec/tasks/TASK-0002.yaml", """id: TASK-0002
type: task
title: optional-input task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise optional inputs
feature: F-0001
required_inputs:
  - {id: ARCH-0100, reason: the pipeline shape this work must respect}
optional_inputs:
  - {id: RES-0001, reason: background survey}
supplementary_context:
  - {id: D-0100, reason: prior art, not authority}
""")
    m = r.ok("context", "manifest", "TASK-0002")
    by = {i["id"]: i for i in m["inputs"]}
    req_opt_explicit = (by["ARCH-0100"]["required"] is True
                        and by.get("RES-0001", {}).get("required") is False)
    lib.check("W2-02", "required vs optional dependency is explicit per input",
              req_opt_explicit,
              json.dumps({k: (v["required"], v["slot"]) for k, v in by.items()}))
    supp = [s["id"] for s in m["supplementary_context"]]
    lib.check("W2-02b", "declared supplementary context is a separate, non-authority block",
              "D-0100" in supp, json.dumps(m["supplementary_context"])[:300])

    # ---- W2.3 authority semantics preserved across stages ------------------------------------
    pkt = r.ok("context", "compile", "TASK-0001")
    det = pkt["deterministic_authority"]
    classes = {}
    for block in ("governing_requirements", "active_decisions", "architecture", "interfaces",
                  "scenarios", "test_designs", "datasets", "evidence_inputs"):
        for x in det.get(block) or []:
            classes[x["id"]] = x.get("state_class")
    lib.check("W2-03", "every delivered input carries its authority class into the packet",
              all(v for v in classes.values()) and classes.get("REQ-0001") == "AUTHORITATIVE",
              json.dumps(classes))

    # ---- W2.4 research evidence cannot silently become a decision ---------------------------
    # RES-0001 influences D-0100. It must not be delivered as a decision, nor be usable as one.
    dec_ids = [x["id"] for x in det.get("active_decisions") or []]
    ev_ids = [x["id"] for x in det.get("evidence_inputs") or []]
    lib.check("W2-04", "research evidence is never delivered in the decision slot",
              "RES-0001" not in dec_ids, json.dumps({"decisions": dec_ids, "evidence": ev_ids}))
    # a task that declares research in its decisions field must be refused, not silently promoted
    r.put("spec/tasks/TASK-0003.yaml", """id: TASK-0003
type: task
title: research-as-decision task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: try to use research as a decision
feature: F-0001
decisions: [RES-0001]
""")
    m3 = r.ok("context", "manifest", "TASK-0003")
    e3 = [i for i in m3["inputs"] if i["id"] == "RES-0001"]
    blocked = m3["delivery_state"] == "BLOCKED" and any(
        p["blocking"] for i in e3 for p in i["problems"])
    lib.check("W2-04b", "research declared in the decision slot is refused, not promoted",
              blocked, json.dumps(e3)[:400])

    # ---- W2.5 lessons cannot silently become authoritative policy ---------------------------
    les = r.run("artefact", "show", "LES-0001")
    r.put("spec/lessons/LES-0001.yaml", """id: LES-0001
type: lesson
title: always quote fields containing commas
status: ACTIVE
summary: a lesson from an incident
""")
    sc = r.ok("artefact", "show", "LES-0001")["authoritative_status"]
    r.put("spec/tasks/TASK-0004.yaml", """id: TASK-0004
type: task
title: lesson-as-decision task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: try to use a lesson as a decision
feature: F-0001
decisions: [LES-0001]
""")
    m4 = r.ok("context", "manifest", "TASK-0004")
    e4 = [i for i in m4["inputs"] if i["id"] == "LES-0001"]
    lesson_blocked = m4["delivery_state"] == "BLOCKED" and any(
        p["blocking"] for i in e4 for p in i["problems"])
    lib.check("W2-05", "a lesson is not AUTHORITATIVE and cannot fill a decision slot",
              sc != "AUTHORITATIVE" and lesson_blocked,
              "lesson state_class=%s; %s" % (sc, json.dumps(e4)[:300]))

    # ---- W2.6 historical/retrieved material cannot replace current authoritative input -------
    # (the full superseded-input attack is W3-04/W10-02; here: authority class of a HISTORICAL record)
    r.put("spec/decisions/D-0099.yaml", """id: D-0099
type: decision
title: Use TSV (retired)
status: HISTORICAL
question: Which CSV dialect?
options:
  - {id: TSV, description: tab separated}
chosen_option: TSV
rationale: superseded approach
affects: [TASK-0005]
summary: historical decision
""")
    r.put("spec/tasks/TASK-0005.yaml", """id: TASK-0005
type: task
title: historical-decision task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise a historical decision
feature: F-0001
decisions: [D-0099]
""")
    m5 = r.ok("context", "manifest", "TASK-0005")
    e5 = [i for i in m5["inputs"] if i["id"] == "D-0099"]
    hist_blocked = m5["delivery_state"] == "BLOCKED" and any(
        p["blocking"] for i in e5 for p in i["problems"])
    pkt5 = r.ok("context", "compile", "TASK-0005")
    in_active = [x["id"] for x in pkt5["deterministic_authority"]["active_decisions"]]
    in_conflicting = [x["id"] for x in pkt5["deterministic_authority"]["conflicting_decisions"]]
    lib.check("W2-06", "a HISTORICAL record cannot satisfy a current authoritative input",
              hist_blocked and "D-0099" not in in_active and "D-0099" in in_conflicting,
              json.dumps({"blocked": hist_blocked, "active": in_active,
                          "conflicting": in_conflicting}))

    # ---- W2.7 output schemas define what downstream stages may consume ----------------------
    # the packet publishes a receipt contract naming exactly what the downstream stage must return,
    # and the worker-return / report schemas are the published contract for that stage.
    c = pkt["receipt_contract"]
    schemas = os.listdir(r.path("governance/kernel/schemas"))
    lib.check("W2-07", "the packet publishes the downstream consumption contract, schema-backed",
              bool(c.get("required_fields")) and bool(c.get("acknowledge_inputs"))
              and "worker-return.schema.json" in schemas and "report.schema.json" in schemas,
              json.dumps(list(c.keys())))

    # ---- W2.8 the relationship vocabulary is machine-usable ---------------------------------
    need = {"IMPLEMENTS", "TESTS", "VALIDATED_BY", "SUPERSEDES", "CONSTRAINS", "DERIVED_FROM",
            "CONSUMES", "PRODUCES", "GOVERNED_BY", "AFFECTS"}
    schema = json.load(open(r.path("governance/kernel/schemas/record.schema.json")))
    vocab = set(schema["properties"]["relations"]["items"]["properties"]["type"]["enum"])
    # machine-usable: a query walks them
    down = r.ok("artefact", "lineage", "REQ-0001", "--direction", "down")
    up = r.ok("artefact", "lineage", "TASK-0001", "--direction", "up")
    lib.check("W2-08", "the typed relation vocabulary exists and is walkable in both directions",
              need <= vocab and bool(down.get("nodes") or down.get("edges"))
              and bool(up.get("nodes") or up.get("edges")),
              "missing=%s down=%s up=%s" % (sorted(need - vocab), json.dumps(down)[:150],
                                            json.dumps(up)[:150]))

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
