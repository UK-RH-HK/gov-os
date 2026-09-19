# DERIVED COPY (P2-AR-0034, WS-3 round 3) of release/capability-baseline/audit-0/beta-r/evidence/D6-rebuild-guarantee.py
# ORIGINAL-PROBE-ID: beta-r/D6-rebuild-guarantee
# Changes, and nothing else (every check line and criterion is unchanged):
#  (1) `lib` is imported from the original probe's directory (this copy lives in the WS-3 round-3 evidence directory);
#  (2) the claimed task t1 is a `documentation` task with no feature link, instead of an `implementation` task of
#      F-0001: under WS-5 round 2 (BC-P2-34/16, merged) an implementation task whose inherited acceptance test has no
#      recorded independent author is not runnable, so the unedited probe stops at `task claim` on both binaries; the
#      probe needs A live claim, not that kind of task;
#  (3) the pinned-reranker override (`set_overrides(... reranker.provider ...)`) is not applied: under WS-7 round 2
#      (BC-P2-39, merged) the probe's hand-declared reranker never runs unregistered, so every `memory query` of the
#      snapshot fails; the D6-b2-A-pin line therefore measures the unregistered plugin's refusal instead.
"""D6 Rebuild guarantee (Contract v3 lines 350-354) — family duty: ACTUALLY delete derived state and rebuild.

A live project (tasks, a claim, a pending gate, an open CIT, checkpoints, a registered plugin) is snapshotted:
authoritative tracked state hash, claims, `gov status` (fresh-agent view), index manifest hash, derived-store content
hashes and a fixed set of retrieval answers. Then:
  A. framework §19 deletion: vector/SQLite index, graph projection, generated views (everything the product's own
     REPOSITORY_CONTRACT classifies as `generated` under governance/generated/**, plus .governance-runtime/state.db)
     -> rebuild -> compare.
  B. the whole .governance-runtime/ (the product's contract classifies `.governance-runtime/**` as `derived`)
     -> rebuild -> compare.
  C. fresh clone at a DIFFERENT absolute path -> rebuild -> compare derived state; and a same-path rebuild twice.
"""
import hashlib
import json
import shutil
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "audit-0" / "beta-r" / "evidence" / "lib"))  # (1)
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("d6")
g.ok("rebuild-memory")
# live governed state
t1 = g.ok("task", "create", "--class", "documentation", "--objective", "Totals A", "--status", "READY", "--allowed", "docs/**")["id"]  # (2)
t2 = g.ok("task", "create", "--class", "implementation", "--objective", "Totals B", "--status", "READY", "--allowed", "src/**")["id"]
g.ok("task", "claim", t1)
gate = g.ok("gate", "create", "--question", "Adopt nightly reconciliation window?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R2"}))["id"]
cit = g.ok("cit", "propose", "--proposal", "Tighten totals", "--trigger", "behaviour_change", "--targets", "REQ-0001")["id"]
g.ok("checkpoint", "create", "--next-action", "continue totals", "--task", t1)
(root / "tools/probe-plugins").mkdir(parents=True, exist_ok=True)
shutil.copy(PLUGINS / "logging_reranker.py", root / "tools/probe-plugins/logging_reranker.py")
desc = BASE / "d6-rerank.yaml"
desc.write_text(yaml.safe_dump({"plugin_id": "logging-reranker", "capability": "rerank", "version": "1", "languages": [],
                                "command": ["python3", "tools/probe-plugins/logging_reranker.py"]}))
reg = g.run("plugins", "register", "--descriptor", str(desc))
log("register logging-reranker ->", reg.get("ok"), (reg.get("error") or {}).get("code"), "pin:", (reg.get("result") or {}).get("pin"))
# (3) set_overrides(root, {"MEMORY_POLICY.reranker.provider": "logging-reranker"})
commit_all(root, "live state")
g.ok("rebuild-memory")
g.ok("adapters", "generate", show=False)
g.ok("tools", "registry", show=False)
commit_all(root, "generated views refreshed")

QUERIES = ["REQ-0001", "why integer cents rationale", "compute_total", '"append-only ledger"', "what depends on F-0001"]


def tracked_authoritative():
    files = [f for f in git(root_cur, "ls-files").splitlines() if not f.startswith("governance/generated/") and f != "framework.json" and "__pycache__" not in f]
    hsh = hashlib.sha256()
    for f in sorted(files):
        p = root_cur / f
        if p.is_file():
            hsh.update(f.encode() + b"\0" + p.read_bytes())
    return hsh.hexdigest()[:16], len(files)


def derived_hashes(r):
    def hq(sql):
        return hashlib.sha256(json.dumps(sorted(q(r, sql)), default=str).encode()).hexdigest()[:16]
    return {"artifacts": hq("SELECT artifact_id, path, content_hash, status, state_class, namespace, path_class FROM artifacts"),
            "chunks": hq("SELECT chunk_id, content_hash FROM chunks"), "vectors": hq("SELECT chunk_id, vec FROM vectors"),
            "edges": hq("SELECT src, type, dst FROM edges"), "symbols": hq("SELECT symbol_id, kind, lineno FROM symbols"),
            "fts": hq("SELECT chunk_id, text FROM chunks_fts")}


def status_view(gg):
    s = gg.ok("status", show=False)
    return {"records": s["records"], "next_task": s["next_task"], "runnable": s["tasks"]["runnable"], "counts": s["tasks"]["counts"],
            "gates": [x["id"] for x in s["human_gates"]], "open_cits": [x["id"] for x in s["open_transactions"]],
            "latest_checkpoint": (s.get("latest_checkpoint") or {}).get("id"), "index_fresh": s["memory"]["index_fresh"], "next_action": s["next_action"]}


def answers(gg):
    return {qq: [h["artifact_id"] for h in gg.ok("memory", "query", qq, "--k", "5", show=False)["hits"]] for qq in QUERIES}


def claims(gg):
    return [(c["task_id"], c["session_id"]) for c in gg.ok("claims", "list", show=False)]


def full_snapshot(gg, r):
    return {"auth": tracked_authoritative(), "manifest_hash": json.loads((r / "governance/generated/index-manifest.json").read_text())["manifest_hash"],
            "derived": derived_hashes(r), "status": status_view(gg), "answers": answers(gg), "claims": claims(gg),
            "plugin_registry": sorted((json.loads((r / "governance/generated/plugin-registry.json").read_text()).get("plugins") or {}).keys())
            if (r / "governance/generated/plugin-registry.json").exists() else None,
            "control": {k: gg.ok("status", show=False)["control"].get(k) for k in ("mode", "writes_frozen")}}


def compare(a, b, label):
    diffs = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
    log(f"[{label}] differences vs pre-deletion snapshot:", json.dumps(diffs, default=str)[:2500] if diffs else "NONE")
    return diffs


root_cur = root
g.ok("freeze-writes", "--reason", "d6 probe: emergency state must survive derived-state deletion")
S0 = full_snapshot(g, root)
log("PRE-DELETION SNAPSHOT:", json.dumps(S0, default=str)[:2500])

section("D6-A delete framework §19 derived state (index DB, graph, vectors, generated views)")
deleted = []
for f in [".governance-runtime/state.db", ".governance-runtime/state.db-wal", ".governance-runtime/state.db-shm"]:
    if (root / f).exists():
        (root / f).unlink()
        deleted.append(f)
for d in [".governance-runtime/context", ".governance-runtime/benchmarks"]:
    if (root / d).exists():
        shutil.rmtree(root / d)
        deleted.append(d + "/")
gen = root / "governance/generated"
deleted += ["governance/generated/" + str(p.relative_to(gen)) for p in gen.rglob("*") if p.is_file()]
shutil.rmtree(gen)
(root / "framework.json").unlink()
deleted.append("framework.json")
log("deleted:", deleted)
st_missing = g.run("status")
log("gov status with derived state deleted ->", st_missing.get("ok"), (st_missing.get("error") or {}).get("code"),
    (st_missing.get("result") or {}).get("next_action"))
rb = g.run("rebuild-memory")
log("gov rebuild-memory ->", rb.get("ok"), (rb.get("error") or {}).get("code"), (rb.get("error") or {}).get("message", "")[:200])
g.run("adapters", "generate")
g.run("tools", "registry")
SA = full_snapshot(g, root)
dA = compare(S0, SA, "A")
log("plugin registrations before/after:", S0["plugin_registry"], SA["plugin_registry"])
pl = g.ok("plugins", "list", show=False)
log("python-ast standing after rebuild:", [(u["plugin_id"]) for u in pl["usable"]], "denied:", [(d.get("plugin_id"), d.get("code")) for d in pl["denied"]])
# consequence of the lost registration: the implementation pin no longer protects the pinned reranker
impl = root / "tools/probe-plugins/logging_reranker.py"
orig = impl.read_text()
impl.write_text(orig + "\n# tampered after the registry was deleted\n")
tam = g.run("memory", "query", "reconciliation procedure", "--k", "3")
log("reranker implementation edited after registry deletion -> query:", tam.get("ok"), (tam.get("error") or {}).get("code"))
impl.write_text(orig)
git(root, "checkout", "--", "governance/generated/plugin-registry.json")
impl.write_text(orig + "\n# tampered with the registry restored from git\n")
tam2 = g.run("memory", "query", "reconciliation procedure", "--k", "3")
log("same edit with the registry restored from Git -> query:", tam2.get("ok"), (tam2.get("error") or {}).get("code"))
impl.write_text(orig)
check("D6-b2-A-registry", "plugin_registry" not in dA,
      "the OS-written plugin registry (the only proof of registration, TOOL_POLICY.plugins.registry_path) survives deletion of generated views")
check("D6-b2-A-pin", not tam.get("ok") and (tam.get("error") or {}).get("code") == "PLUGIN_PIN_MISMATCH",
      "a tampered pinned plugin still fails closed after the registry is lost (the descriptor carries the pin written at registration)")
log("docs/ARCHITECTURE.md §4 states:", [l.strip() for l in (WT / "docs/ARCHITECTURE.md").read_text().splitlines() if "Everything in `.governance-runtime/` is derived" in l])
check("D6-b1", rb.get("ok") and (root / ".governance-runtime/state.db").exists() and (root / "governance/generated/index-manifest.json").exists(),
      "all derived memory/index state (SQLite/FTS/vector/graph, manifests, generated views) can be deleted and rebuilt")
check("D6-b2-A", "auth" not in dA and "claims" not in dA and "control" not in dA and "status" not in dA,
      "after deleting framework §19 derived state: authoritative records, claims, emergency control state and governed status are preserved")
check("D6-b1-identical", "derived" not in dA and "manifest_hash" not in dA and "answers" not in dA,
      "the rebuilt index is identical (manifest hash, derived-store content, retrieval answers)")

section("D6-B delete the whole .governance-runtime/ (contract class `derived`)")
cls = [r for r in yaml.safe_load((root / "governance/project/REPOSITORY_CONTRACT.yaml").read_text())["paths"] if r["pattern"].startswith(".governance-runtime")]
log("REPOSITORY_CONTRACT rule for the runtime directory:", cls)
log("runtime directory contents before deletion:", sorted(str(p.relative_to(root)) for p in (root / ".governance-runtime").iterdir()))
shutil.rmtree(root / ".governance-runtime")
rb = g.run("rebuild-memory")
log("gov rebuild-memory ->", rb.get("ok"), (rb.get("error") or {}).get("code"))
SB = full_snapshot(g, root)
dB = compare(S0, SB, "B")
check("D6-b2-B", "claims" not in dB and "control" not in dB,
      "deleting the directory the product itself classifies as derived preserves claims and emergency control state")
g.run("resume")

section("D6-b3 fresh-agent reconstruction after rebuild")
fresh = g.as_session("S-fresh-agent")
fs = status_view(fresh)
log("fresh session gov status:", fs)
cont = fresh.run("continue")
log("fresh session gov continue ->", cont.get("ok"), (cont.get("result") or {}).get("status"), (cont.get("result") or {}).get("task"),
    (cont.get("error") or {}).get("code"))
same = {k: fs[k] for k in ["records", "gates", "open_cits", "latest_checkpoint"]} == {k: S0["status"][k] for k in ["records", "gates", "open_cits", "latest_checkpoint"]}
check("D6-b3", same and fs["index_fresh"] and cont.get("ok"),
      "a fresh agent (no prior conversation) reconstructs the same governed state (records, gates, open CITs, checkpoint, runnable work) after the rebuild")

section("D6-B consequences (run after the fresh-agent check so they do not perturb it)")
other_claim = g.as_session("S-intruder").run("task", "claim", t1)
log("after runtime deletion, another session claims the previously claimed task:", other_claim.get("ok"), (other_claim.get("error") or {}).get("code"))
g.ok("freeze-writes", "--reason", "re-freeze to show the gate would have applied", show=False)
wr = g.run("task", "create", "--class", "implementation", "--objective", "write under freeze", "--allowed", "src/**")
log("with control.json present, a mutating command under freeze ->", (wr.get("error") or {}).get("code"))
g.ok("resume", show=False)
g.as_session("S-intruder").run("task", "release", t1, show=False)

section("D6-b4 multi-machine / path-independent determinism")
g.ok("rebuild-memory", show=False)
h1 = json.loads((root / "governance/generated/index-manifest.json").read_text())["manifest_hash"]
d1 = derived_hashes(root)
g.ok("rebuild-memory", show=False)
h2 = json.loads((root / "governance/generated/index-manifest.json").read_text())["manifest_hash"]
log("same path, two consecutive full rebuilds: manifest hashes equal:", h1 == h2)
commit_all(root, "state before clone")
other = BASE / "elsewhere" / "deeper" / "clone-of-d6"
if other.exists():
    shutil.rmtree(other)
other.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["git", "clone", "-q", str(root), str(other)], check=True)
go = Gov(other, "S-machine-b")
doc = go.run("doctor")
log("machine B (different absolute path) gov doctor ->", body_of(doc).get("verdict"))
rbB = go.run("rebuild-memory")
log("machine B rebuild ->", rbB.get("ok"), (rbB.get("error") or {}).get("code"), (rbB.get("error") or {}).get("message", "")[:200])
hB = json.loads((other / "governance/generated/index-manifest.json").read_text())["manifest_hash"] if rbB.get("ok") else None
dB2 = derived_hashes(other) if rbB.get("ok") else {}
log("manifest hash machine A:", h1, "machine B:", hB)
log("derived-store content A vs B:", {k: (d1[k], dB2.get(k)) for k in d1 if d1[k] != dB2.get(k)} or "IDENTICAL")
abs_leak = q(other, "SELECT COUNT(*) FROM chunks WHERE text LIKE ?", (f"%{root}%",))[0][0] if rbB.get("ok") else None
log("chunks in machine B's index containing machine A's absolute path:", abs_leak)
check("D6-b4", h1 == h2 and rbB.get("ok") and hB == h1 and d1 == dB2,
      "rebuilds are deterministic at the same path and at a different absolute path (identical manifest hash and derived content)")
summary()
