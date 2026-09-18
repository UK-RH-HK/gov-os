"""R3 Archive policy (Contract v3 lines 887-890).

b1 historical/superseded material excluded from default current retrieval (and retrievable when explicitly requested)
b2 Git history preferred over an unnecessary dead-code archive (brownfield dead code is removed, not archived)
b3 deliberate reference implementations may be retained explicitly (archive/code-reference/)
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa
import brownfield  # noqa

OLD_DESIGN = "# Ledger design v1 (historical)\n\nThe first ledger stored balances in a mutable table and recomputed nightly with float dollars.\n"
REF = '"""Reference implementation kept deliberately: v1 pricing algorithm (for comparison benchmarks)."""\n\n\ndef price_v1(weight_kg, zone):\n    return round(weight_kg * {"A": 3.1, "B": 4.2}[zone], 2)\n'
root, g = build_rich("r3", extra_files={"archive/spec/ledger-design-v1.md": OLD_DESIGN, "archive/code-reference/pricing_v1.py": REF})
g.ok("rebuild-memory")

section("R3-b1 historical/superseded excluded from default current retrieval")
rows = q(root, "SELECT artifact_id, path_class, status, default_retrieval, semantic, lexical FROM artifacts WHERE path LIKE 'archive/%' AND path NOT LIKE '%.gitkeep'")
log("archived artefacts in the index:", rows)
for qq in ["mutable table recomputed nightly with float dollars", '"mutable table"']:
    d = g.ok("memory", "query", qq, "--k", "6", show=False)
    h = g.ok("memory", "query", qq, "--k", "6", "--include-historical", show=False)
    log(f"{qq!r}: default -> {[x['artifact_id'] for x in d['hits']]} (excluded_by_authority={d['excluded_by_authority']}) | --include-historical -> {[x['artifact_id'] for x in h['hits']]}")
d = g.ok("memory", "query", "store money as floating point dollars", "--k", "6", show=False)
h = g.ok("memory", "query", "store money as floating point dollars", "--k", "6", "--include-historical", show=False)
log("superseded D-0101: default ->", [x["artifact_id"] for x in d["hits"]], "| --include-historical ->", [(x["artifact_id"], x["flags"]) for x in h["hits"] if x["artifact_id"] == "D-0101"])
arch_default = any(x["artifact_id"].startswith("file:archive/") for x in g.ok("memory", "query", "mutable table recomputed nightly with float dollars", "--k", "6", show=False)["hits"])
arch_explicit = any(x["artifact_id"].startswith("file:archive/") for x in g.ok("memory", "query", '"mutable table"', "--k", "6", "--include-historical", show=False)["hits"])
sup_default = "D-0101" in [x["artifact_id"] for x in d["hits"]]
sup_explicit = "D-0101" in [x["artifact_id"] for x in h["hits"]]
check("R3-b1-default", not arch_default and not sup_default, "archived and superseded material is excluded from default current-state retrieval")
check("R3-b1-explicit", arch_explicit and sup_explicit, "archived and superseded material is retrievable when explicitly requested (CLI --include-historical)")
log("NOTE: retrieval has an `include_archive` option (retrieval/mod.rs RetrieveOptions) but `gov memory query` exposes only --include-historical")

section("R3-b2 Git history preferred over dead-code archive (brownfield)")
broot = brownfield.prepare("r3-brown", extra_files={"archive/code-reference/pricing_v1.py": REF})
out = brownfield.run_stages(broot, "A6G", show=False)
EV = broot / "spec/audits/GOVERNANCE-ADOPTION"
cat = {json.loads(l)["current_path"]: json.loads(l) for l in (EV / "04-TARGET-PATH-MAP.jsonl").read_text().splitlines()}
for p in ["src/app/old_export.py", "docs/legacy_module.py", "archive/code-reference/pricing_v1.py"]:
    e = cat.get(p, {})
    log(f"{p}: class={e.get('current_class')} action={e.get('action')} target={e.get('target_path')} gate={e.get('requires_human_gate')} reason={str(e.get('reason'))[:100]}")
dead_gone = not (broot / "src/app/old_export.py").exists() and not (broot / "docs/legacy_module.py").exists()
dead_archived = [str(p.relative_to(broot)) for p in (broot / "archive").rglob("*") if p.is_file() and ("old_export" in p.name or "legacy_module" in p.name)]
hist = git(broot, "log", "--all", "--oneline", "--", "src/app/old_export.py")
log("dead code removed from active tree:", dead_gone, "| copies placed in archive/:", dead_archived, "| still in Git history:", bool(hist))
check("R3-b2", dead_gone and not dead_archived and bool(hist) and cat["src/app/old_export.py"]["action"] == "DELETE_FROM_ACTIVE_TREE",
      "unused code is removed from the active tree behind a human gate and preserved by Git history, not copied into an archive")

section("R3-b3 deliberate reference implementations retained explicitly")
kept = (broot / "archive/code-reference/pricing_v1.py").exists()
log("archive/code-reference/pricing_v1.py after adoption:", kept, "| catalogue:", {k: cat.get("archive/code-reference/pricing_v1.py", {}).get(k) for k in ["current_class", "action"]})
ref_row = q(root, "SELECT path_class, status, default_retrieval FROM artifacts WHERE path='archive/code-reference/pricing_v1.py'")
rd = g.ok("memory", "query", "price_v1", "--k", "5", show=False)
log("greenfield index row for the reference implementation:", ref_row, "| symbol query price_v1 (default):", [x["artifact_id"] for x in rd["hits"]])
pol = g.ok("policy", "effective", "ARCHIVE_POLICY", show=False)["effective"]
log("ARCHIVE_POLICY:", pol)
check("R3-b3", kept and cat.get("archive/code-reference/pricing_v1.py", {}).get("action") == "KEEP_IN_PLACE" and ref_row and ref_row[0][2] == 0,
      "a reference implementation placed under archive/code-reference/ is retained (not treated as dead code) and kept out of default retrieval")
summary()
