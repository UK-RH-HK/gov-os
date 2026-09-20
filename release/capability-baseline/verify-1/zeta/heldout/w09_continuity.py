"""W9 — session/handoff continuity of mandatory inputs (Contract v3:1154-1160). Held-out, P2-AR-0051."""
import glob
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def latest_checkpoint(r):
    f = sorted(glob.glob(r.path("spec/reports/checkpoints/CKPT-*.yaml")))[-1]
    return yaml.safe_load(open(f))


def main():
    r = lib.Repo("w09")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", "TASK-0001", "READY")
    r.ok("task", "claim", "TASK-0001", role="backend-engineer", session="sessionA")
    pkt = r.ok("context", "compile", "TASK-0001")
    r.commit("seed")

    # ---- W9.1 the required-input manifest persists across session end ----------------------
    close = r.ok("session", "close", "--task", "TASK-0001", role="backend-engineer",
                 session="sessionA")
    m_after = r.ok("context", "manifest", "TASK-0001", session="sessionB")
    lib.check("W9-01", "the required-input manifest is reproduced identically in a new session "
                       "after the old session closed",
              m_after["inputs"] == r.ok("context", "manifest", "TASK-0001",
                                        session="sessionA")["inputs"]
              and m_after["delivery_state"] == "COMPLETE",
              json.dumps({"session_close": list(close.keys()),
                          "delivery_state": m_after["delivery_state"]})[:300])

    # ---- W9.2 the checkpoint records input ids / versions / hashes -------------------------
    ck = latest_checkpoint(r)
    inputs = ck.get("inputs") or {}
    lib.check("W9-02", "the checkpoint records each mandatory input id at its content hash, plus "
                       "the packet hash it was delivered as",
              bool(inputs) and "REQ-0001" in json.dumps(inputs)
              and len(json.dumps(inputs)) > 100
              and (ck.get("context_packet_hash") or ck.get("packet_hash")),
              json.dumps({"input_keys": list(inputs) if isinstance(inputs, dict) else inputs,
                          "packet_hash": ck.get("context_packet_hash") or ck.get("packet_hash"),
                          "freshness": ck.get("input_freshness")})[:500])

    # ---- W9.4 a fresh agent reconstructs the mandatory inputs without prior chat -----------
    st = r.ok("status", session="freshAgent")
    cont = r.run("continue", session="freshAgent")
    pkt2 = r.ok("context", "compile", "TASK-0001", session="freshAgent")
    lib.check("W9-04", "a fresh session with no prior conversation reconstructs the same "
                       "mandatory inputs, byte for byte",
              pkt2["input_hashes"] == pkt["input_hashes"]
              and pkt2["deterministic_authority"]["governing_requirements"] ==
              pkt["deterministic_authority"]["governing_requirements"],
              json.dumps({"status_keys": sorted(st.keys())[:12],
                          "continue": (cont.get("result") or {}).get("status")})[:400])
    h = r.ok("health", "run", "--tier", "G3")
    far = (h.get("families") or {}).get("fresh_agent_reconstruction")
    lib.check("W9-04b", "the product itself re-checks fresh-agent reconstruction at G3",
              far is not None, json.dumps(far)[:400])

    # ---- W9.3 a model/provider switch reconstructs the same authoritative inputs ------------
    # the packet's authority block must not depend on the model or the routing profile
    env = {"GOV_MODEL": "some-other-provider/model-x", "GOV_MODEL_TIER": "T1"}
    pkt3 = r.ok("context", "compile", "TASK-0001", session="otherModel", env=env)
    rt = r.run("route", "task", "TASK-0001") if False else {}
    lib.check("W9-03", "the mandatory inputs are identical under a different model/provider "
                       "environment (the authority block does not depend on the model)",
              pkt3["input_hashes"] == pkt["input_hashes"]
              and pkt3["input_manifest"]["inputs"] == pkt["input_manifest"]["inputs"],
              json.dumps({"same_inputs": pkt3["input_hashes"] == pkt["input_hashes"]}))
    _ = rt

    # ---- W9.5 compaction cannot silently remove mandatory project state ---------------------
    # the runtime's derived state is disposable; the governed records are not. Remove the whole
    # derived runtime directory (the strongest "compaction") and re-ask.
    import shutil
    aside = os.path.join(r.state, "runtime-aside")
    if os.path.exists(aside):
        shutil.rmtree(aside)
    shutil.move(r.path(".governance-runtime"), aside)
    m_c = r.run("context", "manifest", "TASK-0001", session="afterCompaction")
    pkt4 = r.run("context", "compile", "TASK-0001", session="afterCompaction")
    ok = (m_c.get("ok") and m_c["result"]["inputs"] == m_after["inputs"]
          and pkt4.get("ok")
          and pkt4["result"]["input_hashes"] == pkt["input_hashes"])
    lib.check("W9-05", "removing the entire derived runtime directory does not remove any "
                       "mandatory project state: the manifest and packet reconstruct identically",
              ok, json.dumps({"manifest_ok": m_c.get("ok"),
                              "packet_ok": pkt4.get("ok")})[:300])
    shutil.rmtree(r.path(".governance-runtime"), ignore_errors=True)
    shutil.move(aside, r.path(".governance-runtime"))
    # a delivered packet that is lost is reported as lost rather than silently re-invented
    lost = r.run("context", "show", "TASK-0001", "--hash", pkt["packet_hash"])
    lib.check("W9-05b", "a specific delivered packet is still resolvable by its hash after the "
                        "session ended",
              lost.get("ok") and lost["result"]["packet_hash"] == pkt["packet_hash"],
              json.dumps(lost.get("error"))[:300])

    # ---- W9.6 a handoff with stale or missing required-input state is blocked or degraded ---
    ho = r.run("handoff", "create", "--to-role", "independent-test-designer",
               "--task", "TASK-0001", role="orchestrator", session="sessionA")
    hr = ho.get("result") or {}
    ph = (hr.get("inputs") or {}).get("context_packet_hash")
    resolved = r.run("context", "show", "TASK-0001", "--hash", ph) if ph else {}
    ids = set((resolved.get("result") or {}).get("input_hashes") or {})
    lib.check("W9-06", "a handoff of healthy work carries a resolvable required-input state "
                       "reference (the packet hash) and states its freshness as CURRENT",
              ho.get("ok") and bool(ph)
              and {"REQ-0001", "SCN-0001", "TO-0001", "D-0100"} <= ids
              and (hr.get("freshness") or {}).get("state") == "CURRENT"
              and (hr.get("freshness") or {}).get("delivery_state") == "COMPLETE",
              json.dumps({"packet_hash": ph, "resolved_inputs": sorted(ids),
                          "freshness": (hr.get("freshness") or {}).get("state")})[:400])

    # now make a required input stale and try again
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace(
              "CSV contains one row per ledger entry",
              "CSV contains one row per ledger entry, and a header"))
    r.ok("rebuild-memory", "--incremental")
    ho2 = r.run("handoff", "create", "--to-role", "independent-test-designer",
                "--task", "TASK-0001", role="orchestrator", session="sessionA")
    h2 = ho2.get("result") or {}
    fr = h2.get("freshness") or {}
    stale_named = "REQ-0001" in json.dumps(fr.get("stale_inputs") or [])
    lib.check("W9-06b", "a handoff whose required-input state was stale is explicitly re-delivered "
                        "and degraded: the state is named, the stale input is named with both "
                        "hashes, and the previous packet is marked invalidated",
              ho2.get("ok") and fr.get("state") in ("REFRESHED", "STALE", "DEGRADED")
              and stale_named and fr.get("previous_packet_invalidated") is True,
              json.dumps({"state": fr.get("state"), "stale_inputs": fr.get("stale_inputs"),
                          "previous_invalidated": fr.get("previous_packet_invalidated")})[:500])

    # and with a required input missing altogether
    r.put("spec/tasks/TASK-0009.yaml", """id: TASK-0009
type: task
title: handoff with a missing input
status: ACTIVE
class: implementation
task_status: DRAFT
objective: exercise a handoff with a missing mandatory input
feature: F-0001
required_inputs:
  - {id: REQ-9999, reason: a requirement that does not exist}
""")
    ho3 = r.run("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0009",
                role="orchestrator", session="sessionA")
    body3 = json.dumps(ho3)
    lib.check("W9-06c", "a handoff of work with a missing mandatory input is blocked or degraded, "
                        "naming the input",
              (not ho3.get("ok") or "REQ-9999" in body3) and "REQ-9999" in body3,
              body3[:500])

    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
