#!/usr/bin/env python3
"""P2-AR-0024 (WS-3, round 2) builder probes — BUILDER REGRESSION EVIDENCE ONLY (Contract v3 O3), not acceptance.

One line per property: `CHECK <id> PASS|FAIL <statement> -- <detail>`. Run against the round-1 integrated binary
(843d79c, the negative control: the O1/ADJ/G0/CS lines that this round repairs FAIL there) and against the final
binary. Every machine is isolated (private HOME/XDG_*; no GOV_*). Signing material is TEST MATERIAL (published seeds).

Usage: python3 R2-WS03-probes.py <gov binary> <scratch dir>
"""
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r2_machine import (PKG, REC, WT, Machine, check, err, stage_files, summary)  # noqa: E402
sys.path.insert(0, os.path.join(WT, "release/capability-baseline/audit-0/alpha-r/evidence/lib"))
from srr_mint import break_glass_doc, envelope  # noqa: E402
import yaml  # noqa: E402

GOV, SCR = sys.argv[1], sys.argv[2]
os.makedirs(SCR, exist_ok=True)
print(f"# gov {GOV}")


def refused_keys(m):
    ov = m.g("policy", "overrides").get("result") or {}
    return sorted(f"{r['policy']}.{r['key']}" for r in ov.get("refused", [])), ov


def d027(m):
    d = m.g("doctor")
    dd = d.get("result") or (d.get("error") or {}).get("details") or {}
    c = [x for x in dd.get("checks", []) if x["id"] == "D027"]
    return (c[0]["ok"] if c else None), dd.get("verdict")


# ===================================================================================== O-1 (older shipped kernel)
def section_o1():
    m = Machine(GOV, SCR, "o1")
    m.provision()
    r414 = m.signed_release(os.path.join(WT, "release/releases/4.1.4/kernel"), 14, "rel-414")
    r415 = m.signed_release(os.path.join(WT, "release/releases/4.1.5/kernel"), 15, "rel-415")
    i = m.g("init", "--source", r414, "--name", "s5", "--alias", "s5-a")
    print("# init signed shipped 4.1.4:", i.get("ok"), err(i))
    m.commit("4.1.4")
    ref, ov = refused_keys(m)
    check("O1.a", i.get("ok") and ref == [], "descriptive overlay keys of a project on shipped 4.1.4 are accepted (none refused)", ref)
    ok27, verdict = d027(m)
    check("O1.b", ok27 is True, "doctor D027 is clean on the shipped 4.1.4 kernel", {"D027": ok27, "verdict": verdict})
    pp_path = os.path.join(m.p, "governance/project/PROJECT_POLICY.yaml")
    mro_path = os.path.join(m.p, "governance/project/MODEL_ROUTING_OVERRIDES.yaml")
    pp = yaml.safe_load(open(pp_path))
    pp["readiness"]["enforce_pre_implementation_cells"] = False
    pp["project"]["name"] = "renamed"
    pp["governance"]["kernel_dir"] = "elsewhere"
    pp["policy_overrides"] = {"MEMORY_POLICY.failure_memory.retrieval_miss.enabled": False, "AUTHORITY_POLICY.authority_levels_required.create_task": "L0"}
    yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
    mro = yaml.safe_load(open(mro_path))
    mro["task_class_overrides"] = {"security": "T1"}
    mro["providers"] = [{"name": "p", "models": []}]
    yaml.safe_dump(mro, open(mro_path, "w"), sort_keys=False)
    ref, ov = refused_keys(m)
    want = sorted(["PROJECT_POLICY.readiness.enforce_pre_implementation_cells", "PROJECT_POLICY.governance.kernel_dir",
                   "MODEL_ROUTING_OVERRIDES.task_class_overrides.security", "MEMORY_POLICY.failure_memory.retrieval_miss.enabled",
                   "AUTHORITY_POLICY.authority_levels_required.create_task"])
    check("O1.c", ref == want, "on the older kernel every floor-weakening key is still refused (readiness, catch-all immutable, tier floor, the binary's failure-memory floor, authority floor) and the descriptive/free keys are not", {"refused": ref})
    m.git("checkout", "--", "governance/project")
    first = m.g("update", "--apply", "--source", r415)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    if gid:
        m.human_channel()
        m.owner_decide(gid)
    u = m.g("update", "--apply", "--source", r415, "--approve")
    lock = yaml.safe_load(open(os.path.join(m.p, "governance/framework.lock")))
    check("O1.d", u.get("ok") and (u.get("result") or {}).get("applied") is True and lock.get("version") == "4.1.5",
          "update 4.1.4 -> shipped 4.1.5 through the owner-signed gate is applied, not rolled back", {"code": err(u), "msg": ((u.get("error") or {}).get("message") or "")[:200], "lock": lock.get("version")})
    ok27, verdict = d027(m)
    ref, ov = refused_keys(m)
    check("O1.e", ok27 is True and ref == [] and len((ov.get("precedence") or {}).get("governing_sets") or []) == 2,
          "after the update D027 is clean and both rule sets govern (installed 4.1.5 + this binary)", {"D027": ok27, "sets": (ov.get("precedence") or {}).get("governing_sets")})


# ===================================================================================== P2-ADJ-0001
def section_adj():
    m = Machine(GOV, SCR, "adj", fixture="greenfield")
    m.g("init", "--name", "adj", "--alias", "adj-a", "--skip-index")
    m.commit("init")
    eff = (m.g("policy", "effective", "HUMAN_GATE_POLICY").get("result") or {})
    check("ADJ.a", ((eff.get("kernel") or {}).get("human_channel") or {}).get("standalone_anchor_when_unprovisioned") is False,
          "kernel HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned is false", (eff.get("kernel") or {}).get("human_channel"))
    st = m.g("trust", "human-channel").get("result") or {}
    check("ADJ.b", st.get("available") is False and st.get("standalone_anchor_permitted_by_policy") is False
          and "gov trust provision" in json.dumps(st.get("unavailable_reason")),
          "unprovisioned: the channel is reported unavailable, the standalone anchor not permitted, remediation provision", {k: st.get(k) for k in ("available", "standalone_anchor_permitted_by_policy", "unavailable_reason")})
    gid = m.g("gate", "create", "--question", "Adopt the window?", "--fields", json.dumps(PKG))["result"]["id"]
    pr = m.g("gate", "present", gid)["result"]["gate"]
    d = m.g("decide", gid, "--option", "A", "--answer-file", m.answer(gid, pr["gate_instance"], pr["package_sha256"], "A"))
    det = (d.get("error") or {}).get("details") or {}
    check("ADJ.c", err(d) == "HUMAN_CHANNEL_UNAVAILABLE" and det.get("cause") == "UNPROVISIONED" and str(det.get("provision_command", "")).startswith("gov trust provision") and d["_exit"] != 0,
          "an owner-signed answer on an unprovisioned machine is refused typed, cause UNPROVISIONED, with the provision remediation", {"code": err(d), "cause": det.get("cause"), "remediation": det.get("remediation")})
    p1 = m.g("trust", "human-channel", "--provision", m.anchor_doc())
    hc_anchor = os.path.join(m.base, "state/governance-os/machine/human-channel/anchor.json")
    check("ADJ.d", err(p1) == "HUMAN_CHANNEL_STANDALONE_DISABLED" and not os.path.exists(hc_anchor),
          "provisioning a standalone anchor (even the owner's, from the administrator domain) is refused and writes nothing", {"code": err(p1), "anchor_written": os.path.exists(hc_anchor)})
    os.makedirs(os.path.dirname(hc_anchor), exist_ok=True)
    shutil.copy(m.anchor_doc(), hc_anchor)
    d = m.g("decide", gid, "--option", "A", "--answer-file", m.answer(gid, pr["gate_instance"], pr["package_sha256"], "A"))
    det = (d.get("error") or {}).get("details") or {}
    check("ADJ.e", err(d) == "HUMAN_CHANNEL_UNAVAILABLE" and det.get("standalone_anchor_present") is True,
          "an anchor file placed in machine state is not honoured", {"code": err(d), "present": det.get("standalone_anchor_present")})
    os.remove(hc_anchor)
    pp_path = os.path.join(m.p, "governance/project/PROJECT_POLICY.yaml")
    pp = yaml.safe_load(open(pp_path))
    pp["policy_overrides"] = {"HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned": True}
    yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
    ref, _ = refused_keys(m)
    eff2 = (m.g("policy", "effective", "HUMAN_GATE_POLICY").get("result") or {}).get("effective") or {}
    check("ADJ.f", "HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned" in ref and (eff2.get("human_channel") or {}).get("standalone_anchor_when_unprovisioned") is False,
          "a project cannot switch the standalone anchor on (strengthen-only); the effective value stays false", ref)
    m.git("checkout", "--", "governance/project")
    m.human_channel()
    d = m.owner_decide(gid)
    show = m.g("gate", "show", gid).get("result") or {}
    check("ADJ.g", d.get("ok") and (d.get("result") or {}).get("answered_by_kind") == "human" and (show.get("answer") or {}).get("verified") is True,
          "provisioned with a root that delegates human-gate: the owner's answer is honoured and re-verifies", {"code": err(d), "show_answer": show.get("answer")})
    m2 = Machine(GOV, SCR, "adj-nohg", fixture="greenfield")
    m2.provision(human_gate=False)
    st2 = (m2.g("trust", "human-channel").get("result") or {}).get("unavailable_reason") or {}
    check("ADJ.h", "delegates no `human-gate` role" in json.dumps(st2),
          "a provisioned root that delegates no human-gate role gives no channel (remediation: root successor)", st2)


def governed_hash(root):
    """Every file except .git/, the derived runtime directory and the generated views (governance/generated/)."""
    import hashlib
    files = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", ".governance-runtime")]
        rel = os.path.relpath(d, root)
        if rel == "governance/generated" or rel.startswith("governance/generated/"):
            continue
        files += [os.path.join(d, f) for f in fs]
    h = hashlib.sha256()
    for p in sorted(files):
        h.update(os.path.relpath(p, root).encode())
        h.update(open(p, "rb").read())
    return h.hexdigest()



# ===================================================================================== G0 hard-blocks (IP-WS02-08) + O-4 + IP-WS02-09
def section_g0():
    m = Machine(GOV, SCR, "g0", fixture="greenfield")
    m.g("init", "--name", "g0", "--alias", "g0-a", "--skip-index")
    m.commit("init")
    m.g("task", "create", "--id", "TASK-G1", "--class", "documentation", "--objective", "x", "--status", "READY")
    m.commit("task")
    pp_path = os.path.join(m.p, "governance/project/PROJECT_POLICY.yaml")
    pp = yaml.safe_load(open(pp_path))
    pp["policy_overrides"] = {"AUTHORITY_POLICY.authority_levels_required.create_task": "L0"}
    yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
    m.g("doctor")  # records the CRITICAL D027 finding and its hard-block
    res = {
        "task create": m.g("task", "create", "--class", "documentation", "--objective", "y"),
        "task claim": m.g("task", "claim", "TASK-G1"),
        "cit propose": m.g("cit", "propose", "--proposal", "p", "--trigger", "behaviour_change"),
        "handoff create": m.g("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-G1"),
    }
    check("G0.a", all(err(v) == "HEALTH_HARD_BLOCK" and "D027" in json.dumps(v.get("error")) for v in res.values()),
          "while the CRITICAL D027 block stands, task create / task claim / cit propose / handoff create are refused HEALTH_HARD_BLOCK naming the check", {k: err(v) for k, v in res.items()})
    rem = {"gate create": m.g("gate", "create", "--question", "q?", "--fields", json.dumps(PKG)), "policy overrides": m.g("policy", "overrides"),
           "health status": m.g("health", "status"), "checkpoint": m.g("checkpoint", "create", "--next-action", "fix the override")}
    check("G0.b", all(v.get("ok") for v in rem.values()), "remedies and non-work operations stay available under the block", {k: err(v) for k, v in rem.items()})
    m.git("checkout", "--", "governance/project")
    t = m.g("task", "create", "--class", "documentation", "--objective", "after repair")
    check("G0.c", t.get("ok"), "repairing the condition releases the block without a manual re-run (the guard re-evaluates changed inputs)", err(t))


    for mode, code in (("freeze-writes", "FROZEN"), ("pause", "PAUSED")):
        m.g(mode, "--reason", "incident")
        before = governed_hash(m.p)
        rb = m.g("rebuild-memory")
        rb2 = m.g("memory", "rebuild", "--incremental")
        check(f"G0.d-{mode}", rb.get("ok") and rb2.get("ok") and governed_hash(m.p) == before,
              f"O-4: under {mode} derived-state rebuild runs and changes no authoritative/governed/evidence file", {"rebuild": err(rb), "memory rebuild": err(rb2)})
        ev = {"audit": m.g("audit"), "verify product": m.g("verify", "product"), "health run": m.g("health", "run", "--tier", "G1"),
              "health product": m.g("health", "product")}
        np = m.g("audit", "--no-persist")
        check(f"G0.e-{mode}", all(err(v) == code for v in ev.values()) and (np.get("ok") or err(np) == "UNHEALTHY") and governed_hash(m.p) == before,
              f"IP-WS02-09: under {mode} evidence-writing commands are refused and the non-persisting audit runs without writing", {**{k: err(v) for k, v in ev.items()}, "audit --no-persist": err(np)})
        m.g("resume")


# ===================================================================================== call sites
def section_cs():
    m = Machine(GOV, SCR, "cs-adopt", fixture="migration")
    for s in ("baseline", "inventory", "classify", "map", "plan"):
        m.g("adopt", s, session="S-declared-planner")
    cat = open(os.path.join(m.p, "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl")).readline()
    prod = json.loads(cat)["producer"]
    plan = yaml.safe_load(open(os.path.join(m.p, "spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml")))
    check("CS.a", prod.get("session") == "S-declared-planner" and prod.get("role") == "orchestrator" and prod.get("session_source") == "declared"
          and (plan.get("producer") or {}).get("session") == "S-declared-planner",
          "WS-9/11 IP-3: the catalogue and plan record the invocation's declared session and role", {"catalogue": prod, "plan": plan.get("producer")})

    m = Machine(GOV, SCR, "cs", fixture="greenfield")
    m.g("init", "--name", "cs", "--alias", "cs-a", "--skip-index")
    m.commit("init")
    undecl = m.g("memory", "miss", "--query", "where is the retry policy?", role="")
    miss = m.g("memory", "miss", "--query", "where is the retry policy?", "--expected", "D-0002", role="backend-engineer")
    again = m.g("memory", "miss", "--query", "Where is the retry  policy?", "--expected", "D-0002", role="backend-engineer")
    fl = m.g("memory", "failures")
    m.g("freeze-writes", "--reason", "x")
    frozen = m.g("memory", "miss", "--query", "other", role="backend-engineer")
    m.g("resume")
    check("CS.b", err(undecl) == "AUTHORITY_DENIED" and (miss.get("result") or {}).get("status") == "recorded"
          and str((miss.get("result") or {}).get("path", "")).startswith("spec/reports/memory-quality/")
          and (again.get("result") or {}).get("status") == "existing" and (miss.get("result") or {}).get("id", "?") in json.dumps(fl.get("result"))
          and err(frozen) == "FROZEN",
          "WS-6 IP-6: gov memory miss records an agent-reported miss (declared role, deduplicated, never under a freeze); gov memory failures lists it",
          {"undeclared": err(undecl), "miss": miss.get("result"), "again": (again.get("result") or {}).get("status"), "frozen": err(frozen)})
    open(os.path.join(m.p, ".governance-runtime/state.db"), "wb").write(b"not a database")
    for x in ("state.db-wal", "state.db-shm"):
        try:
            os.remove(os.path.join(m.p, ".governance-runtime", x))
        except FileNotFoundError:
            pass
    c1 = m.g("continue")
    m.g("freeze-writes", "--reason", "repair index")
    os.remove(os.path.join(m.p, ".governance-runtime/state.db"))
    rb = m.g("rebuild-memory")
    m.g("resume")
    c2 = m.g("continue")
    check("CS.c", err(c1) == "INDEX_UNAVAILABLE" and ((c1.get("error") or {}).get("details") or {}).get("remediation") == "gov rebuild-memory"
          and rb.get("ok") and c2.get("ok"),
          "WS-4 IP-6 (CLI side): continue with a damaged derived index is refused typed with the remediation; the rebuild (allowed under the freeze) restores it",
          {"continue": err(c1), "rebuild": err(rb), "continue after": err(c2)})

    # BC-P2-38 / WS-8 IP-3: the pin refusal precedes break-glass entry
    m = Machine(GOV, SCR, "cs-pin")
    m.provision()
    cur = m.signed_release(os.path.join(WT, "framework"), 20, "rel-cur")
    old = m.signed_release(os.path.join(WT, "release/releases/4.1.4/kernel"), 10, "rel-old", meta_version=30)
    m.g("init", "--source", cur, "--name", "pin", "--alias", "pin-a", "--skip-index")
    ts = m.g("trust", "status")["result"]
    inbox = m.g("trust", "break-glass")["result"]["inbox"]
    os.makedirs(inbox, exist_ok=True)
    stg = stage_files(old)
    tok = break_glass_doc(ts["machine_id"], stg, "pin-probe-nonce", reason="probe: reinstall an older release")
    open(os.path.join(inbox, "auth.json"), "w").write(envelope(tok, [REC]))
    ri = m.g("kernel", "reinstall", "--source", old, "--break-glass")
    ts2 = m.g("trust", "status")["result"]
    check("CS.d", err(ri) == "KERNEL_MISMATCH" and not ts2.get("degraded") and os.path.exists(os.path.join(inbox, "auth.json")),
          "a break-glass reinstall of a release other than the pinned one is refused before break-glass is entered: no marking, the owner's token is not consumed",
          {"code": err(ri), "degraded": ts2.get("degraded"), "token_still_in_inbox": os.path.exists(os.path.join(inbox, "auth.json"))})



for name, fn in (("O1", section_o1), ("ADJ", section_adj), ("G0", section_g0), ("CS", section_cs)):
    try:
        fn()
    except Exception as e:  # a negative-control binary can fail a setup step the repaired one passes
        check(f"{name}.crashed", False, f"section {name} stopped at a step this binary refuses", f"{type(e).__name__}: {e}")

summary(GOV)
