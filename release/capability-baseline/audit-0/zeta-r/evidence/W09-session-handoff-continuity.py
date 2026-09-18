"""W9 Session/handoff continuity of mandatory inputs (Contract v3 lines 1154-1160), incl. AC-16 N <-> W9.
 c1 required-input manifest persists across session end
 c2 checkpoint records input IDs/versions/hashes or equivalent state reference
 c3 model/provider switch reconstructs the same authoritative task inputs
 c4 fresh agent reconstructs mandatory inputs without prior chat
 c5 compaction cannot silently remove mandatory project state
 c6 handoff with stale/missing required-input state is blocked or explicitly degraded
"""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

INPUT_KEYS = ("governing_requirements", "active_decisions", "conflicting_decisions", "scenarios", "interfaces", "architecture", "acceptance_criteria", "dependency_state", "allowed_writes", "prohibited_writes")
def inputs(pk):
    return {k: pk["deterministic_authority"][k] for k in INPUT_KEYS}

root, g = new_project("w9")
base_spec(root, req_ids=("REQ-0001",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["2 x 199 = 398"]})
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "i64 cents", "status": "ACTIVE", "chosen_option": "A", "affects": ["F-0001"]})
commit(root, "spec")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)
commit(root, "task")
g.ok("rebuild-memory", quiet=True)
s1 = g.with_(session="S-one")
p1 = s1.ok("context", "compile", "TASK-0001", quiet=True)
ck1 = s1.ok("checkpoint", "create", "--next-action", "implement totals", "--task", "TASK-0001", "--trigger", "before_session_close", quiet=True)
log("checkpoint at session close: " + json.dumps(ck1))
# c1 manifest persists across session end (new process, new session id, no shared memory)
s2 = g.with_(session="S-two-fresh")
t = s2.ok("task", "show", "TASK-0001", quiet=True)
obs("W9-c1-manifest-persists", t.get("requirements") == ["REQ-0001"] and t.get("scenarios") == ["SCN-0001"], f"fresh session reads TASK-0001 requirements={t.get('requirements')} scenarios={t.get('scenarios')} from the governed task record")
# c2 checkpoint records input ids/versions/hashes or an equivalent state reference
keys = sorted(ck1.keys())
obs("W9-c2-checkpoint-input-ids", any(k in ck1 for k in ("inputs", "input_ids", "required_inputs")) or "REQ-0001" in json.dumps(ck1), f"checkpoint keys: {keys}; mentions REQ-0001: {'REQ-0001' in json.dumps(ck1)}")
obs("W9-c2-checkpoint-state-reference", ck1.get("context_packet_hash") == p1["packet_hash"] and bool((ck1.get("memory_snapshot") or {}).get("index_manifest_hash")), f"context_packet_hash={str(ck1.get('context_packet_hash'))[:12]} (== packet {p1['packet_hash'][:12]}); memory_snapshot={ck1.get('memory_snapshot')}")
# does the checkpoint's state reference actually move when a mandatory input's normative content changes?
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0001.yaml")); d["statement"] = "Totals SHALL round to whole units."; d["acceptance_criteria"] = ["2 x 199 = 398"]
write_record(root, "spec/requirements/REQ-0001.yaml", d)
commit(root, "normative statement added to REQ-0001 (outside the context brief)")
g.ok("memory", "rebuild", "--incremental", quiet=True)
p1b = s1.ok("context", "compile", "TASK-0001", quiet=True)
ck1b = s1.ok("checkpoint", "create", "--next-action", "implement totals", "--task", "TASK-0001", quiet=True)
obs("W9-c2-packet-hash-tracks-input-content", ck1b.get("context_packet_hash") != ck1.get("context_packet_hash") and p1b["deterministic_hash"] != p1["deterministic_hash"], f"checkpoint context_packet_hash before/after REQ-0001 statement change: {str(ck1.get('context_packet_hash'))[:12]} / {str(ck1b.get('context_packet_hash'))[:12]}; deterministic_hash before/after: {p1['deterministic_hash'][:12]} / {p1b['deterministic_hash'][:12]} (packet_hash moved only because the RETRIEVED block's excerpts changed: {p1b['deterministic_hash'] == p1['deterministic_hash']})")
obs("W9-c2-index-hash-tracks-input-content", (ck1b.get("memory_snapshot") or {}).get("index_manifest_hash") != (ck1.get("memory_snapshot") or {}).get("index_manifest_hash"), f"checkpoint memory_snapshot.index_manifest_hash before/after: {str((ck1.get('memory_snapshot') or {}).get('index_manifest_hash'))[:12]} / {str((ck1b.get('memory_snapshot') or {}).get('index_manifest_hash'))[:12]}")
# does the checkpoint's index state reference reflect an input change made just before it? (no rebuild in between)
con = db(root); live_before = con.execute("SELECT value FROM meta WHERE key='index_manifest_hash'").fetchone(); con.close()
live_before = json.loads(live_before[0]) if live_before else None
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0001.yaml")); d["acceptance_criteria"] = ["2 x 199 = 398", "negative quantities rejected"]
write_record(root, "spec/requirements/REQ-0001.yaml", d); commit(root, "REQ-0001 changed immediately before a checkpoint")
fr_before_ck = g.ok("memory", "freshness", quiet=True)
ck_lag = s1.ok("checkpoint", "create", "--next-action", "implement totals", "--task", "TASK-0001", quiet=True)
rec = (ck_lag.get("memory_snapshot") or {}).get("index_manifest_hash")
obs("W9-c2-state-reference-current-at-checkpoint", rec != live_before, f"live index_manifest_hash just before REQ-0001 changed={str(live_before)[:12]}; index freshness when the checkpoint was taken: fresh={fr_before_ck.get('fresh')} stale={fr_before_ck.get('stale')}; checkpoint {ck_lag.get('id')} records {str(rec)[:12]} (equal to the pre-change state: {rec == live_before}); checkpoints::create records memory_snapshot before its own incremental rebuild")
g.ok("memory", "rebuild", "--incremental", quiet=True)
p1b = s1.ok("context", "compile", "TASK-0001", quiet=True)   # reference packet for c3-c5 after the input change above
fc = ck1.get("files_changed") or []
obs("W9-c2-checkpoint-files-changed-paths-exist", all(os.path.exists(os.path.join(root, f)) for f in fc), f"checkpoint files_changed as recorded: {fc}; paths that do not exist in the repository: {[f for f in fc if not os.path.exists(os.path.join(root, f))]}")
# c3 model/provider switch: nothing model-specific enters the authority block; checkpoint before_model_switch
ms = s1.ok("checkpoint", "create", "--next-action", "resume on another provider", "--task", "TASK-0001", "--trigger", "before_model_switch", quiet=True)
obs("W9-c3-before-model-switch-checkpoint", ms.get("trigger") == "before_model_switch", f"checkpoint trigger={ms.get('trigger')} id={ms.get('id')}")
envs = [{}, {"GOV_MODEL": "provider-a/model-x", "OPENAI_API_KEY": "", "ANTHROPIC_MODEL": "m1"}, {"GOV_MODEL": "provider-b/model-y", "GOV_ADAPTER": "generic"}]
hashes = []
for i, e in enumerate(envs):
    gi = Gov(root, session=f"S-model-{i}", role="orchestrator", machine=g.machine, env=e)
    hashes.append(gi.ok("context", "compile", "TASK-0001", quiet=True)["deterministic_hash"])
obs("W9-c3-provider-switch-same-inputs", len(set(hashes)) == 1, f"deterministic_hash under three provider/model environments and sessions: {[h[:12] for h in hashes]}")
pr = g.with_(session="S-role", role="backend-engineer").ok("context", "compile", "TASK-0001", quiet=True)
obs("W9-c3-role-switch-same-inputs", inputs(pr) == inputs(p1b), f"backend-engineer vs orchestrator: mandatory input lists identical={inputs(pr) == inputs(p1b)} (whole deterministic_hash differs by acting role: {pr['deterministic_hash'] != p1b['deterministic_hash']})")
# c4 fresh agent reconstruction without prior chat
fresh = g.with_(session="S-fresh-agent")
st = fresh.ok("status", quiet=True)
cont = fresh.ok("continue", quiet=True)
pf = read_json(root, ".governance-runtime/context/TASK-0001.json")
obs("W9-c4-fresh-agent-reconstructs", cont.get("task") == "TASK-0001" and inputs(pf) == inputs(p1b), f"fresh session: status.next_action={st.get('next_action')!r}; continue -> task {cont.get('task')}; mandatory inputs identical to the prior session's packet: {inputs(pf) == inputs(p1b)}")
# c5 compaction: no product operation removes mandatory state; a before_compaction checkpoint is accepted; state reconstructs
cc = s1.ok("checkpoint", "create", "--next-action", "continue after compaction", "--task", "TASK-0001", "--trigger", "before_compaction", quiet=True)
after = g.with_(session="S-post-compaction").ok("context", "compile", "TASK-0001", quiet=True)
obs("W9-c5-compaction-cannot-remove-state", cc.get("trigger") == "before_compaction" and inputs(after) == inputs(p1b), f"before_compaction checkpoint {cc.get('id')}; post-'compaction' session (no conversational state) rebuilds identical mandatory inputs: {inputs(after) == inputs(p1b)}")
# c6 handoff with missing / stale required-input state
g.ok("task", "create", "--id", "TASK-0002", "--class", "implementation", "--objective", "Implement refunds", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-9999"], "decisions": ["D-9999"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)
h_missing = g.run("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0002")
hm = h_missing.get("result") or {}
obs("W9-c6-handoff-missing-inputs-blocked-or-degraded", (not h_missing.get("ok")) or any(k in hm for k in ("degraded", "blocked", "missing_inputs")), f"handoff for TASK-0002 (REQ-9999, D-9999 absent; no packet ever compiled) -> ok={h_missing.get('ok')}; inputs={hm.get('inputs')}; packet file exists: {os.path.exists(os.path.join(root, '.governance-runtime/context/TASK-0002.json'))}")
# stale: the packet for TASK-0001 was compiled; now its requirement changes; hand off without recompiling
pk_before = read_json(root, ".governance-runtime/context/TASK-0001.json")
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0001.yaml")); d["acceptance_criteria"] = ["2 x 199 = 400 (whole units)"]
write_record(root, "spec/requirements/REQ-0001.yaml", d)
commit(root, "REQ-0001 acceptance changed after packet compile")
g.ok("memory", "rebuild", "--incremental", quiet=True)
h_stale = g.run("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0001")
hs = h_stale.get("result") or {}
pk_after = read_json(root, ".governance-runtime/context/TASK-0001.json")
obs("W9-c6-handoff-stale-inputs-blocked-or-degraded", (not h_stale.get("ok")) or any(k in hs for k in ("degraded", "blocked", "stale_inputs")), f"handoff for TASK-0001 after its requirement changed -> ok={h_stale.get('ok')}; handed-off packet still carries pre-change criterion: {'2 x 199 = 398' in json.dumps(pk_after)}; packet unchanged: {pk_after == pk_before}")
# AC-16 N <-> W9: the before_handoff checkpoint records which state?
ckh = g.ok("checkpoint", "latest", quiet=True)
obs("AC16-NxW9-before-handoff-checkpoint-flags-stale-packet", "stale" in json.dumps(ckh).lower(), f"before_handoff checkpoint {ckh.get('id')} trigger={ckh.get('trigger')} context_packet_hash={str(ckh.get('context_packet_hash'))[:12]} == stale packet hash {pk_after['packet_hash'][:12]}: {ckh.get('context_packet_hash') == pk_after['packet_hash']}; staleness marker: {'stale' in json.dumps(ckh).lower()}")
dr = g.run("doctor", quiet=True)
dres = dr.get("result") or (dr.get("error") or {}).get("details") or {}
ckchecks = [c for c in dres.get("checks", []) if "checkpoint" in (c.get("name", "") + c.get("message", "")).lower()]
obs("AC16-NxW9-doctor-checkpoint-freshness", any(not c.get("ok") for c in ckchecks), f"doctor checks about checkpoints: {ckchecks}")
summary()
