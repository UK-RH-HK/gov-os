# DERIVED COPY (P2-AR-0032, round-2 integration builder) of
#   release/capability-baseline/repair-1/r2-ws06/evidence/SUPP-ws06-r2.py (P2-AR-0027, WS-6).
# ORIGINAL-PROBE-ID: ws06-r2-supplementary
# Changes, and nothing else:
#  (1) LIB (the beta-r harness, imported read-only) is resolved from this copy's location;
#  (2) owner_answer(): P2-ADJ-0001 (WS-3, merged) turned the standalone human-gate anchor off, so instead of
#      provisioning one the machine is provisioned with the throw-away root that delegates `human-gate` to the same
#      test owner key and the installed kernel is re-verified (p2ar0032_root_channel.provision, WS-3's own method).
#  (3) R5 fixture: the task claimed only to create a live claim is a documentation task — WS-5 (P2-AR-0026,
#      BC-P2-16) makes an implementation task with no declared scenarios/acceptance tests not claimable.
# Every check, its scenario and its PASS criterion are P2-AR-0027's.
"""P2-AR-0027 (WS-6 repair builder, round 2) supplementary behaviour probe — REGRESSION EVIDENCE ONLY (Contract v3 O3).

Situations the audit-of-record probes do not reach on the integrated tree, run against target/release/gov through the
beta-r harness (imported read-only from release/capability-baseline/audit-0/beta-r/evidence/lib; nothing there is
edited). Human answers use WS-3's test-material signer (repair-1/ws03/evidence/hc_owner.py, published seed 7).

R1  IP-8 / delta-r L3.b5.11 exactly as the probe words it (the unedited L3 probe stops earlier, at b5.6, on WS-3's
    T2 refusal): `memory select builtin:128 --by anyone` under a declared `human` role records no human approval.
R2  BC-P2-30: an owner-signed answer to the change gate is the ONLY thing that makes the decision human_approved; a
    hand edit of that decision (any field) breaks its T2 binding and the profile is then reported GOVERNED_UNVERIFIED,
    not GOVERNED; restoring the bytes the OS wrote restores it.
R3  BC-P2-30: a gate answered B (decline) authorises nothing (GATE_DECLINED) and nothing is pinned.
R4  BC-P2-30: a post-reindex regression that does not hold rolls the change back (previous pins and index restored,
    the audit record and a failure record say why). Exercised with the UNMEASURED case: a held-out set below
    MEMORY_POLICY.regression.min_queries cannot establish the regression, so the change is refused and rolled back.
R5  BC-P2-31: the rebuild report and `gov memory profile` are observable; `os_state` names the stores still kept in
    the derived runtime directory by their writers (until the integration points move them).
R6  BC-P2-28: `gov rebuild-memory` raises graph-integrity findings in its report (G1) — not only `gov memory integrity`.
"""
import json
import os
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path

HERE = Path(__file__).resolve()
LIB = HERE.parents[5] / "audit-0" / "beta-r" / "evidence" / "lib"  # (1)
sys.path.insert(0, str(HERE.parent))
import p2ar0032_root_channel  # noqa: E402  (2)
sys.path.insert(0, str(LIB))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

HC = str(WT / "release/capability-baseline/repair-1/ws03/evidence/hc_owner.py")


def owner_answer(g, gid, option):
    st = g.run("trust", "human-channel", show=False)
    if not (st.get("result") or {}).get("available"):  # (2)
        p2ar0032_root_channel.provision(lambda *a: g.as_role("orchestrator").run(*a, show=False), str(g.root),
                                        tempfile.mkdtemp(prefix="p2ar0027-admin-"))
    pr = g.ok("gate", "present", gid, show=False)["gate"]
    d = tempfile.mkdtemp(prefix="p2ar0027-owner-")
    af = os.path.join(d, f"answer-{gid}-{option}.json")
    subprocess.run([sys.executable, HC, "answer", af, gid, pr["gate_instance"], pr["package_sha256"], option], check=True, capture_output=True)
    return g.ok("decide", gid, "--option", option, "--answer-file", af)


root, g = build_rich("supp-r2")
g.ok("rebuild-memory")

section("R1 IP-8 / L3.b5.11: a declared `human` role cannot make select record human approval")
v = g.as_role("human").run("memory", "select", "builtin:128", "--by", "anyone")
decs = sorted(p.name for p in (root / "spec/decisions").glob("D-*.yaml"))
human_true = [d for d in decs if (yaml.safe_load((root / "spec/decisions" / d).read_text()) or {}).get("human_approved") is True]
check("R1-L3.b5.11", not v.get("ok") and (v.get("error") or {}).get("code") == "AUTHORITY_DENIED" and not human_true,
      "`memory select builtin:128 --by anyone` under a declared human role is refused and no decision records human_approved=true")

section("R3 a declined change gate authorises nothing")
b = g.ok("memory", "benchmark", "--candidate", "current", "--candidate", "builtin:64", "--record")
res = b["research_record"]
pp_before = (root / "governance/project/PROJECT_POLICY.yaml").read_text()
p1 = g.ok("memory", "select", "builtin:64", "--research", res)
owner_answer(g, p1["human_gate"], "B")
d = g.run("memory", "select", "builtin:64", "--research", res, "--gate", p1["human_gate"])
check("R3-declined", (d.get("error") or {}).get("code") == "GATE_DECLINED" and (root / "governance/project/PROJECT_POLICY.yaml").read_text() == pp_before,
      "an owner answer declining the change (B) is refused as authorisation and the pins are unchanged")

section("R2 human approval comes only from the verified owner answer; a hand-edited decision is not honoured")
p2 = g.ok("memory", "benchmark", "--candidate", "current", "--candidate", "builtin:32", "--record")
res2 = p2["research_record"]
s1 = g.ok("memory", "select", "builtin:32", "--research", res2)
owner_answer(g, s1["human_gate"], "A")
s2 = g.ok("memory", "select", "builtin:32", "--research", res2, "--gate", s1["human_gate"])
dec_path = root / f"spec/decisions/{s2['decision']}.yaml"
dec_text = dec_path.read_text()
dec = yaml.safe_load(dec_text)
prof = g.ok("memory", "profile", show=False)
check("R2-human-from-answer", s2.get("applied") and dec.get("human_approved") is True and dec.get("approved_by_kind") == "human"
      and dec["approval"]["answer"]["by_kind"] == "human" and prof["state"] == "GOVERNED",
      "the decision is human_approved because (and only because) the gate carries a verified owner-signed answer; the profile is GOVERNED")
dec["rationale"] = dec["rationale"] + " (edited by hand)"
dec_path.write_text(yaml.safe_dump(dec, sort_keys=False))
prof2 = g.ok("memory", "profile", show=False)
log("after a hand edit of the decision:", {k: prof2.get(k) for k in ("state", "decision", "binding")})
check("R2-hand-edit-not-honoured", prof2["state"] == "GOVERNED_UNVERIFIED",
      "a hand-edited profile decision no longer governs the profile (T2 binding broken -> GOVERNED_UNVERIFIED)")
dec_path.write_text(dec_text)  # the exact bytes the OS wrote: the binding verifies again
check("R2-restored-bytes-govern-again", g.ok("memory", "profile", show=False)["state"] == "GOVERNED", "restoring the exact bytes the OS wrote restores the governance")

section("R4 an unmeasurable regression is refused after re-indexing and rolled back")
hf = root / "governance/tests/memory/heldout.yaml"
held = yaml.safe_load(hf.read_text())
# the evidence binds the held-out set: the benchmark is taken on the reduced set
held_small = dict(held)
held_small["queries"] = held["queries"][:2]
hf.write_text(yaml.safe_dump(held_small, sort_keys=False))
commit_all(root, "held-out set below min_queries")
b3 = g.ok("memory", "benchmark", "--candidate", "current", "--candidate", "builtin:48", "--record")
pp_mid = (root / "governance/project/PROJECT_POLICY.yaml").read_text()
man_mid = json.loads((root / "governance/generated/index-manifest.json").read_text())["embedder"]
s3 = g.ok("memory", "select", "builtin:48", "--research", b3["research_record"])
owner_answer(g, s3["human_gate"], "A")
s4 = g.run("memory", "select", "builtin:48", "--research", b3["research_record"], "--gate", s3["human_gate"])
man_after = json.loads((root / "governance/generated/index-manifest.json").read_text())["embedder"]
fails = sorted(p.name for p in (root / "spec/reports/failures").glob("FAIL-*.yaml")) if (root / "spec/reports/failures").exists() else []
log("select with an unmeasurable regression ->", (s4.get("error") or {}).get("code"), "| rollback:", json.dumps(body_of(s4).get("rollback"))[:300], "| failure records:", fails)
check("R4-unmeasured-rolled-back", (s4.get("error") or {}).get("code") == "PROFILE_REGRESSION_UNMEASURED"
      and (root / "governance/project/PROJECT_POLICY.yaml").read_text() == pp_mid and man_after == man_mid and body_of(s4).get("audit"),
      "the change is refused after re-indexing, the audit record says why, and pins and index are back to the previous profile")
hf.write_text(yaml.safe_dump(held, sort_keys=False))
commit_all(root, "held-out set restored")

section("R5/R6 the rebuild report carries the profile state, the integrity findings and the misplaced OS state")
y(root, "spec/requirements/REQ-0299.yaml", {"id": "REQ-0299", "type": "requirement", "title": "Orphan", "status": "ACTIVE", "kind": "functional"})
commit_all(root, "orphan")
t = g.ok("task", "create", "--class", "documentation", "--objective", "Claim something", "--status", "READY", "--allowed", "src/**")["id"]  # (3)
g.ok("task", "claim", t, show=False)
rb = g.ok("rebuild-memory", "--incremental")
gi = rb.get("graph_integrity") or {}
log("rebuild graph_integrity counts:", gi.get("counts"), "| retrieval_profile:", (rb.get("retrieval_profile") or {}).get("state"), "| os_state:", [x["store"] for x in rb.get("os_state", [])])
check("R6-rebuild-raises-integrity", any(f.get("kind") == "orphan" and "REQ-0299" in f.get("message", "") for f in gi.get("findings", [])),
      "every index build raises graph-integrity findings in its report (G1)")
check("R5-rebuild-reports-state", (rb.get("retrieval_profile") or {}).get("state") in ("GOVERNED", "GOVERNED_UNVERIFIED", "KERNEL_DEFAULT", "UNGOVERNED", "UNGOVERNED_CHANGE")
      and "claims" in [x["store"] for x in rb.get("os_state", [])],
      "the rebuild report states the profile's governance state and names non-rebuildable stores still kept in the derived runtime directory")
summary()
