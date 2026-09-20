"""W4 — context compiler delivery proof (Contract v3:1106-1112). Held-out, P2-AR-0051."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def main():
    r = lib.Repo("w04")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.commit("seed")

    pkt = r.ok("context", "compile", "TASK-0001")
    det = pkt["deterministic_authority"]

    # ---- W4.1 mandatory authoritative inputs are loaded deterministically --------------------
    # deterministic == the same inputs and the same deterministic hash on a recompile, and each
    # input carries its NORMATIVE content, not just a reference.
    pkt2 = r.ok("context", "compile", "TASK-0001")
    req = (det.get("governing_requirements") or [])
    body_ok = bool(req) and "content" in req[0] and req[0]["content"].get("acceptance_criteria")
    lib.check("W4-01", "mandatory inputs are delivered with their normative content, reproducibly",
              pkt["deterministic_hash"] == pkt2["deterministic_hash"] and body_ok,
              json.dumps({"hash1": pkt["deterministic_hash"][:12],
                          "hash2": pkt2["deterministic_hash"][:12],
                          "requirement_keys": sorted(req[0].keys()) if req else None})[:400])

    # ---- W4.2 required separated from supplementary -----------------------------------------
    lib.check("W4-02", "required inputs and supplementary retrieval are separately hashed blocks",
              set(["deterministic_authority", "deterministic_hash", "input_manifest",
                   "manifest_hash", "retrieved_intelligence"]) <= set(pkt.keys())
              and "ranked_evidence" not in json.dumps(det),
              json.dumps(sorted(pkt.keys())))

    # ---- W4.4 exact input ids / versions / hashes recorded ----------------------------------
    ih = pkt["input_hashes"]
    vers = {x["id"]: x.get("version") for x in req}
    lib.check("W4-04", "the packet records each delivered input's exact id, version and hash",
              "REQ-0001" in ih and len(ih["REQ-0001"]) == 64 and vers.get("REQ-0001") == "1",
              json.dumps({"hashes": {k: v[:8] for k, v in ih.items()}, "versions": vers}))

    # the recorded hash is the real hash of the record's bytes
    import hashlib
    raw = open(r.path("spec/requirements/REQ-0001.yaml"), "rb").read()
    lib.check("W4-04b", "the recorded content hash is the SHA-256 of the record's bytes",
              hashlib.sha256(raw).hexdigest() == ih["REQ-0001"],
              "%s vs %s" % (hashlib.sha256(raw).hexdigest()[:16], ih["REQ-0001"][:16]))

    # ---- W4.5 the packet hash / provenance proves what the worker was supplied ---------------
    ph = pkt["packet_hash"]
    stored = r.ok("context", "show", "TASK-0001", "--hash", ph)
    same = stored["packet_hash"] == ph
    # the hash is sensitive to the normative content of a delivered input
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace(
              "CSV contains one row per ledger entry",
              "CSV contains one row per ledger entry and a trailing checksum row"))
    pkt3 = r.ok("context", "compile", "TASK-0001")
    sensitive = pkt3["packet_hash"] != ph and pkt3["deterministic_hash"] != pkt["deterministic_hash"]
    prov = pkt["provenance"]
    lib.check("W4-05", "a packet hash resolves back to the exact packet and changes with the "
                       "normative content of any delivered input",
              same and sensitive and bool(prov.get("repo_commit")) and "compiler" in prov,
              json.dumps({"resolves": same, "hash_sensitive": sensitive,
                          "provenance": list(prov.keys())}))
    # the superseding edit invalidated the previously delivered packet
    old = r.ok("context", "show", "TASK-0001", "--hash", ph)
    lib.check("W4-05b", "the superseded packet is marked invalidated, naming the inputs that changed",
              old.get("invalidated") is not None
              and "REQ-0001" in json.dumps(old.get("invalidated")),
              json.dumps(old.get("invalidated"))[:300])

    # ---- W4.6 a missing required input yields an explicit blocked state and a refusal --------
    r.put("spec/tasks/TASK-0006.yaml", """id: TASK-0006
type: task
title: missing-input task
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise the blocked delivery state
feature: F-0001
required_inputs:
  - {id: REQ-9999, reason: a requirement that does not exist}
""")
    p6 = r.ok("context", "compile", "TASK-0006")
    named = "REQ-9999" in json.dumps(p6["input_manifest"]["missing_inputs"])
    # and dispatch refuses it rather than proceeding
    cont = r.run("continue", "--claim", session="dispatch1")
    res = cont.get("result") or {}
    offered = res.get("task") == "TASK-0006" or res.get("claimed") == "TASK-0006"
    listed_blocked = "TASK-0006" in json.dumps(res.get("blocked") or [])
    lib.check("W4-06", "a missing required input makes the packet BLOCKED and names the input",
              p6["delivery_state"] == "BLOCKED" and named,
              json.dumps(p6["input_manifest"]["missing_inputs"])[:300])
    lib.check("W4-06b", "a BLOCKED task is not dispatched by `gov continue --claim`; it is "
                        "reported as blocked with the missing input named",
              not offered and listed_blocked, json.dumps(res)[:400])

    # ---- W4.3 token pressure: supplementary drops first, mandatory is never displaced --------
    base = r.ok("context", "compile", "TASK-0001")
    pp = r.read("governance/project/PROJECT_POLICY.yaml").replace(
        "policy_overrides: {}",
        'policy_overrides: {"CONTEXT_POLICY.max_packet_chars": 12000}')
    r.put("governance/project/PROJECT_POLICY.yaml", pp)
    small = r.ok("context", "compile", "TASK-0001")
    dropped = small["budget"]["dropped_supplementary_slices"]
    delivered = lambda p: {k: p["deterministic_authority"].get(k) for k in
                           ("feature", "governing_requirements", "active_decisions",
                            "architecture", "interfaces", "scenarios", "test_designs",
                            "datasets", "evidence_inputs", "other_inputs")}
    mand_intact = (small["input_hashes"] == base["input_hashes"]
                   and delivered(small) == delivered(base))
    lib.check("W4-03", "under token pressure supplementary slices drop and the mandatory block "
                       "is byte-identical",
              dropped > 0 and mand_intact,
              json.dumps({"dropped": dropped, "budget": small["budget"],
                          "mandatory_unchanged": mand_intact}))

    # when the mandatory block alone exceeds the budget it is still delivered whole, and the
    # over-budget condition is disclosed explicitly (W4:1109 "explicit governed failure/degradation")
    pp = r.read("governance/project/PROJECT_POLICY.yaml").replace(
        '"CONTEXT_POLICY.max_packet_chars": 12000', '"CONTEXT_POLICY.max_packet_chars": 2000')
    r.put("governance/project/PROJECT_POLICY.yaml", pp)
    tiny = r.ok("context", "compile", "TASK-0001")
    still_whole = (tiny["input_hashes"] == base["input_hashes"]
                   and delivered(tiny) == delivered(base))
    disclosed = tiny["budget"]["over_budget"] is True and bool(tiny.get("warning"))
    lib.check("W4-03b", "an over-budget mandatory block is delivered whole and the over-budget "
                        "state is disclosed",
              still_whole and disclosed,
              json.dumps({"whole": still_whole, "budget": tiny["budget"],
                          "warning": bool(tiny.get("warning"))}))
    # is that disclosure a *governed* failure/degradation, or only a field a reader may ignore?
    dispatchable = r.run("continue", session="dispatch2")
    lib.check("W4-03c", "the over-budget packet's delivery_state stays COMPLETE (recorded: the "
                        "disclosure is a warning field, not a governed failure state)",
              tiny["delivery_state"] == "COMPLETE",
              "delivery_state=%s supplementary_state=%s" % (tiny["delivery_state"],
                                                            tiny["supplementary_state"]))
    _ = dispatchable
    pp = r.read("governance/project/PROJECT_POLICY.yaml").replace(
        'policy_overrides: {"CONTEXT_POLICY.max_packet_chars": 2000}', "policy_overrides: {}")
    r.put("governance/project/PROJECT_POLICY.yaml", pp)

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
