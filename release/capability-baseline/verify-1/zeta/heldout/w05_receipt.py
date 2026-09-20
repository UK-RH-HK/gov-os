"""W5 — consumption receipt and implementation traceability (Contract v3:1114-1126).

Held-out, P2-AR-0051. Includes the S0-W5-01 attack: a document that satisfies the published
worker-return schema must be usable as the task-close receipt.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def impl_task(r, tid="TASK-0001"):
    lib.seed_task(r, tid, fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", tid, "READY")
    r.ok("task", "claim", tid, role="backend-engineer", session="impl1")
    return tid


def main():
    r = lib.Repo("w05")
    lib.seed_green(r)
    tid = impl_task(r)
    r.put("src/export.rs", "// implements REQ-0001\npub fn export() {}\n")
    files = ["src/export.rs"]
    r.ok("rebuild-memory", "--incremental")
    r.ok("verify", "product")

    # ---- W5.1-W5.6 the receipt contract demands every W5 field ------------------------------
    pkt = r.ok("context", "compile", tid)
    c = pkt["receipt_contract"]
    need = {"context_packet_hash", "inputs_consumed", "outputs_produced",
            "requirements_implemented", "scenarios_implemented", "decisions_applied",
            "acceptance_evidence", "deviations", "unresolved"}
    lib.check("W5-01", "the packet's receipt contract requires every W5 field",
              need <= set(c["required_fields"]), json.dumps(c["required_fields"]))

    # a close with none of them is refused, naming every missing field
    bare = {"work_completed": "did the work", "tests": {"status": "passed"},
            "files_changed": files}
    out = r.close(tid, bare, role="backend-engineer", session="impl1")
    err = out.get("error") or {}
    codes = [e["code"] for e in (err.get("details") or {}).get("errors") or []]
    lib.check("W5-07", "task close refuses a completion with no consumption receipt",
              not out.get("ok") and err.get("code") == "RECEIPT_INVALID"
              and "RECEIPT_FIELDS_MISSING" in codes and "INPUT_NOT_ACKNOWLEDGED" in codes,
              json.dumps(err)[:400])

    # ---- W5.7 fabricated / out-of-manifest traceability is detected --------------------------
    fab = r.receipt(tid, files, work="did the work")
    fab["requirements_implemented"] = ["REQ-9999"]
    out = r.close(tid, fab, role="backend-engineer", session="impl1")
    err = out.get("error") or {}
    codes = [e["code"] for e in (err.get("details") or {}).get("errors") or []]
    lib.check("W5-07b", "a fabricated requirement id in the receipt is refused by name",
              not out.get("ok") and "REQ-9999" in json.dumps(err), json.dumps(codes))

    fab = r.receipt(tid, files, work="did the work")
    fab["inputs_consumed"] = [x.split("@")[0] + "@" + "0" * 64 for x in fab["inputs_consumed"]]
    out = r.close(tid, fab, role="backend-engineer", session="impl1")
    lib.check("W5-07c", "a receipt acknowledging inputs at the wrong content hash is refused",
              not out.get("ok"), json.dumps(out.get("error"))[:300])

    fab = r.receipt(tid, files, work="did the work")
    fab["acceptance_evidence"] = []
    out = r.close(tid, fab, role="backend-engineer", session="impl1")
    codes = [e["code"] for e in ((out.get("error") or {}).get("details") or {}).get("errors") or []]
    lib.check("W5-05", "a declared acceptance test with no evidence is refused",
              not out.get("ok") and "TEST_EVIDENCE_MISSING" in codes, json.dumps(codes))

    # ---- W5.8 undocumented / untraceable implementation is detected --------------------------
    # source written into the tree but not declared in the receipt
    r.put("src/secret_helper.rs", "// undeclared implementation\npub fn helper() {}\n")
    rec = r.receipt(tid, files, work="did the work")
    out = r.close(tid, rec, role="backend-engineer", session="impl1")
    err = out.get("error") or {}
    lib.check("W5-08", "implementation present in the tree but absent from the receipt is refused "
                       "by path",
              not out.get("ok") and err.get("code") == "MUTATION_SCOPE_VIOLATION"
              and "src/secret_helper.rs" in json.dumps(err), json.dumps(err)[:350])
    os.rename(r.path("src/secret_helper.rs"), os.path.join(r.state, "secret_helper.rs"))

    # ---- a well-formed receipt closes, and the trace becomes graph edges --------------------
    rec = r.receipt(tid, files, work="implemented the CSV export")
    out = r.close(tid, rec, role="backend-engineer", session="impl1")
    lib.check("W5-00", "a complete, honest receipt closes the task",
              out.get("ok"), json.dumps(out.get("error"))[:400])
    if not out.get("ok"):
        return lib.summary()
    rpt = out["result"].get("report") or out["result"].get("report_id")

    # ---- W5.1-W5.6 the persisted receipt records each W5 item --------------------------------
    import yaml
    d = yaml.safe_load(open(r.path("spec/reports/%s.yaml" % rpt)))
    present = {k: bool(d.get(k) is not None) for k in
               ("inputs_consumed", "outputs_produced", "requirements_implemented",
                "scenarios_implemented", "decisions_applied", "constraints_applied",
                "acceptance_evidence", "deviations", "unresolved", "context_packet_hash")}
    lib.check("W5-02", "the persisted receipt records inputs consumed, outputs, what was "
                       "implemented, what was applied, test evidence, deviations and unknowns",
              all(present.values()), json.dumps(present))

    # ---- W5.9 outputs link back to the authoritative upstream inputs ------------------------
    up = r.ok("artefact", "lineage", rpt, "--direction", "up")
    reach = json.dumps(up)
    task = r.ok("artefact", "show", tid)
    outs = [e for e in task["edges"] if e["type"] == "PRODUCES"]
    lib.check("W5-09", "the close report traces up to the requirement, scenario and decision it "
                       "names, and the task records the outputs it produced",
              all(x in reach for x in ("REQ-0001", "SCN-0001", "D-0100")) and bool(outs),
              json.dumps({"upstream_reach": [n.get("node") for n in up.get("reach", [])][:12],
                          "task_produces": outs})[:400])

    # the code file is reachable from the requirement (requirement -> ... -> code)
    down = r.ok("artefact", "lineage", "REQ-0001", "--direction", "down")
    nodes = json.dumps(down)
    lib.check("W5-09b", "the requirement reaches the produced code through the close receipt",
              "src/export.rs" in nodes or rpt in nodes,
              json.dumps([n.get("node") for n in down.get("reach", [])])[:400])

    # ---- S0-W5-01: a worker-return-schema-valid document IS the close receipt ----------------
    schema = json.load(open(r.path("governance/kernel/schemas/worker-return.schema.json")))
    tid2 = impl_task(r, "TASK-0002")
    r.put("src/export2.rs", "// implements REQ-0001 (second pass)\npub fn export2() {}\n")
    r.ok("rebuild-memory", "--incremental")
    r.ok("verify", "product")
    base = r.receipt(tid2, ["src/export2.rs"], work="second implementation")
    wr = {
        "task": tid2,
        "status": "success",                       # worker-return vocabulary, not report.status
        "work_completed": base["work_completed"],
        "files_changed": base["files_changed"],
        "tests": base["tests"],
        "context_packet_hash": base["context_packet_hash"],
        "inputs_consumed": base["inputs_consumed"],
        "outputs_produced": base["outputs_produced"],
        "requirements_implemented": base["requirements_implemented"],
        "scenarios_implemented": base["scenarios_implemented"],
        "features_implemented": base["features_implemented"],
        "decisions_applied": base["decisions_applied"],
        "constraints_applied": base["constraints_applied"],
        "acceptance_evidence": base["acceptance_evidence"],
        "deviations": [],
        "unresolved": [],
        # the rest of the published worker-return contract
        "evidence": ["tests/export_acceptance.rs::export_two_rows"],
        "discoveries": [],
        "risks": [],
        "lessons": [],
        "proposed_decisions": [],
        "recommended_next_action": "gov continue",
    }
    try:
        import jsonschema
        jsonschema.validate(wr, schema)
        valid = True
        why = ""
    except ImportError:
        req = set(schema.get("required") or [])
        valid = req <= set(wr)
        why = "jsonschema unavailable; checked required fields only: %s" % sorted(req)
    except Exception as e:  # noqa: BLE001
        valid = False
        why = str(e)[:200]
    out = r.close(tid2, wr, role="backend-engineer", session="impl1")
    lib.check("W5-10", "a document valid against the published worker-return schema is accepted "
                       "as the task-close receipt (S0-W5-01)",
              valid and out.get("ok"),
              json.dumps({"schema_valid": valid, "why": why,
                          "close": out.get("error")})[:400])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
