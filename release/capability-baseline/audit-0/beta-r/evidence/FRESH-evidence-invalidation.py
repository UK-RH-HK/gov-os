"""Evidence freshness for the beta capabilities (Contract v3 lines 95-111; frozen AC-10: invalidation must be SHOWN).

The product's evidence currency mechanism: a green governance-suite audit record carries `inputs_hash`
(verification::inputs_hash over governance/kernel, governance/project, governance/tests, spec/decisions,
governance/framework.lock); `latest_green` is current only while that hash is unchanged. The suite families that own
beta evidence are index_freshness, graph_integrity, memory_retrieval_regression, context_reproducibility,
recovery_rebuild, fresh_agent_reconstruction, concurrency_claims, secrets_sensitivity_indexing.

For each Contract v3 invalidation input class relevant to beta, change it and observe whether the green record becomes
STALE (inputs_hash differs) and whether re-running the suite would now give a different result.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

root, g = build_rich("fresh")
g.ok("rebuild-memory")
commit_all(root, "baseline")


def green_audit():
    a = body_of(g.run("audit"))
    return a


def current_inputs_hash():
    # the same inputs the product hashes; recomputed by running a no-persist audit and reading its inputs_hash
    a = body_of(g.run("audit", "--no-persist", "--family", "schema_invariants", show=False))
    return a.get("inputs_hash")


base = green_audit()
log("baseline audit:", base.get("audit"), base.get("verdict"), "green:", base.get("green"), "inputs_hash:", str(base.get("inputs_hash"))[:16])
mrr0 = base.get("families", {}).get("memory_retrieval_regression", {})
log("baseline memory_retrieval_regression detail:", mrr0.get("detail"))

rows = []


def probe(label, input_class, mutate, revert=None, rebuild=True):
    mutate()
    commit_all(root, label)
    if rebuild:
        g.run("rebuild-memory", show=False)
    ih = current_inputs_hash()
    stale = ih != base.get("inputs_hash")
    now = body_of(g.run("audit", "--no-persist", show=False))
    mrr = now.get("families", {}).get("memory_retrieval_regression", {}).get("detail", {})
    changed = (now.get("verdict") != base.get("verdict")) or (mrr.get("recall_at_k") != mrr0.get("detail", {}).get("recall_at_k"))
    log(f"[{input_class}] {label}: green record STALE={stale} | re-run verdict {now.get('verdict')} recall={mrr.get('recall_at_k')} "
        f"(baseline recall={mrr0.get('detail', {}).get('recall_at_k')}) failed={mrr.get('failed')}")
    rows.append((input_class, label, stale, changed))
    if revert:
        revert()
        commit_all(root, "revert " + label)
        g.run("rebuild-memory", show=False)


section("inputs that DO invalidate")
pp0 = (root / "governance/project/PROJECT_POLICY.yaml").read_text()
probe("MEMORY_POLICY retrieval profile override (embedding dims)", "model/retrieval profile",
      lambda: set_overrides(root, {"MEMORY_POLICY.embedding.dimensions": 128}),
      lambda: (root / "governance/project/PROJECT_POLICY.yaml").write_text(pp0))
rc0 = (root / "governance/project/REPOSITORY_CONTRACT.yaml").read_text()
probe("path map: docs/** no longer semantically indexed", "project path map",
      lambda: (root / "governance/project/REPOSITORY_CONTRACT.yaml").write_text(rc0.replace("pattern: docs/**\n  class: narrative\n  owner_role: routine-documentation\n  semantic_index: true", "pattern: docs/**\n  class: narrative\n  owner_role: routine-documentation\n  semantic_index: false")),
      lambda: (root / "governance/project/REPOSITORY_CONTRACT.yaml").write_text(rc0))
hf = root / "governance/tests/memory/heldout.yaml"
h0 = hf.read_text()
probe("held-out set edited", "governing contract/policy (test inputs)",
      lambda: hf.write_text(h0.replace("k: 8", "k: 1", 1)), lambda: hf.write_text(h0))

section("inputs that do NOT invalidate (content the memory families measure)")
held = yaml.safe_load((root / "governance/tests/memory/heldout.yaml").read_text())
targets = [e[len("file:"):] for qq in held["queries"] if not qq.get("pending") for e in qq.get("expected_refs", [])
           if e.startswith("file:src/") or e.startswith("file:tests/")]
victim = targets[0]
log("held-out target chosen for deletion:", victim, "| queries expecting it:", [qq["id"] for qq in held["queries"] if "file:" + victim in qq.get("expected_refs", [])])
vtext = (root / victim).read_text()
probe(f"relevant source file deleted ({victim}, a held-out target)", "relevant source files",
      lambda: (root / victim).unlink(), lambda: (root / victim).write_text(vtext))
req = (root / "spec/requirements/REQ-0001.yaml").read_text()
probe("authoritative spec (requirement) rewritten", "authoritative spec",
      lambda: (root / "spec/requirements/REQ-0001.yaml").write_text(req.replace("exact integer cents", "approximate cents")),
      lambda: (root / "spec/requirements/REQ-0001.yaml").write_text(req))
probe("index manifest changed by a rebuild of new content", "relevant index manifest",
      lambda: write(root, "docs/extra.md", "# Extra\n\nNew operational note about settlement.\n"),
      lambda: (root / "docs/extra.md").unlink())

section("summary")
for r in rows:
    log(f"  {r[0]:<42} STALE={r[2]!s:<5} result-changed-on-rerun={r[3]!s:<5} {r[1]}")
check("FRESH-profile", rows[0][2], "a retrieval-profile change invalidates prior green governance evidence")
check("FRESH-pathmap", rows[1][2], "a path-map change invalidates prior green governance evidence")
check("FRESH-source", rows[3][2], "a relevant source change that alters memory regression results invalidates prior green evidence")
check("FRESH-spec", rows[4][2], "an authoritative spec change invalidates prior green evidence for the memory families")
check("FRESH-manifest", rows[5][2], "an index-manifest change invalidates prior green index/memory evidence")
summary()
