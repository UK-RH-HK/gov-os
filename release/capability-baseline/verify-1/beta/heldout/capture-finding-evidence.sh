#!/usr/bin/env bash
# Capture the three focused evidence artefacts that findings V1-BETA-03, V1-BETA-04 and V1-BETA-06 cite, as raw
# command output rather than as a PASS/FAIL line. Re-runnable exactly like the probes.
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"
ED="$BETA_WT/release/capability-baseline/verify-1/beta/evidence"
mkdir -p "$ED/currency" "$ED/ac7" "$ED/lexical"

# ---------------------------------------------------------------- V1-BETA-04: the first green record is not current
C=$(build_corpus_provisioned evcur)
{
  echo "# V1-BETA-04 — two consecutive \`gov audit\` runs on an untouched provisioned corpus"
  for i in 1 2 3 4; do
    gov "$C" audit > "$BETA_SCRATCH/evcur-$i.json" 2>&1
    python3 - "$BETA_SCRATCH/evcur-$i.json" "$i" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or d.get("error", {}).get("details") or {}
print(f"run {sys.argv[2]}: audit={r.get('audit')} verdict={r.get('verdict')} green={r.get('green')} "
      f"inputs_hash={str(r.get('inputs_hash'))[:12]}")
PY
  done
  echo
  echo "# which input classes the run itself changed (run 1 -> run 2):"
  python3 - "$BETA_SCRATCH/evcur-1.json" "$BETA_SCRATCH/evcur-2.json" <<'PY'
import json, sys
a = (json.load(open(sys.argv[1])).get("result") or {})["inputs"]
b = (json.load(open(sys.argv[2])).get("result") or {})["inputs"]
for k in sorted(set(a) | set(b)):
    if a.get(k) != b.get(k):
        print(f"  {k}: {str(a.get(k))[:12]} -> {str(b.get(k))[:12]}")
PY
  echo
  echo "# a task close refusing on a class that only its own G2 run wrote:"
  T=$(gov "$C" task create --class specification --objective "currency evidence" --status READY \
        --allowed 'spec/**' --fields '{"role":"product-spec-agent"}' | jget 'd["result"]["id"]')
  GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-cur gov "$C" task claim "$T" >/dev/null 2>&1
  PKT=$(GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-cur gov "$C" context compile "$T" | jget 'd["result"]["packet_hash"]')
  cat > "$C/spec/product/PRJ-cur.yaml" <<'Y'
id: PRJ-0009
type: project
title: Currency evidence output
status: ACTIVE
Y
  python3 - "$BETA_SCRATCH/evcur-ret.json" "$T" "$PKT" <<'PY'
import json, sys
json.dump({"task": sys.argv[2], "status": "success", "work_completed": "wrote the record",
           "files_changed": ["spec/product/PRJ-cur.yaml"], "files_read": [],
           "evidence": ["spec/product/PRJ-cur.yaml"],
           "tests": {"command": "probe", "status": "not_applicable_with_reason",
                     "reason": "a specification record carries no executable test"},
           "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
           "recommended_next_action": "gov continue", "context_packet_hash": sys.argv[3],
           "inputs_consumed": [], "outputs_produced": ["spec/product/PRJ-cur.yaml"],
           "requirements_implemented": [], "scenarios_implemented": [], "features_implemented": [],
           "decisions_applied": [], "constraints_applied": [], "acceptance_evidence": [], "deviations": []},
          open(sys.argv[1], "w"))
PY
  ( cd "$C" && git add -A && git commit -q -m "currency evidence work" ) >/dev/null 2>&1
  gov "$C" rebuild-memory --incremental >/dev/null 2>&1
  echo "  \$ gov audit   (once)"
  gov "$C" audit | jget 'json.dumps({"audit": (d.get("result") or {}).get("audit"), "green": (d.get("result") or {}).get("green")})'
  echo "  \$ gov task close $T"
  GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-cur gov "$C" task close "$T" --report "$BETA_SCRATCH/evcur-ret.json" \
    | jget 'json.dumps({"ok": d.get("ok"), "code": (d.get("error") or {}).get("code"), "message": (d.get("error") or {}).get("message")})'
  echo "  (spec/reports/memory-quality written by that close:)"
  ls "$C/spec/reports/memory-quality" 2>/dev/null | head -20
} > "$ED/currency/first-audit-not-current.out" 2>&1

# ------------------------------------------------- V1-BETA-03: the generated held-out set cannot discriminate
D=$(build_corpus_provisioned evac7)
{
  echo "# V1-BETA-03 — the GENERATED held-out set: which categories are measured, and what the benchmark separates"
  gov "$D" memory verify | jget 'json.dumps({"queries": (d.get("result") or {}).get("queries"), "pending": (d.get("result") or {}).get("pending_queries"), "by_category": (d.get("result") or {}).get("by_category")})'
  echo
  echo "# three embedder candidates on the generated set:"
  gov "$D" memory benchmark --candidate current --candidate builtin:64 --candidate builtin:8 | python3 -c "
import sys, json
r = json.load(sys.stdin)['result']
for row in r['rows']:
    print(f\"  {row['candidate']:<12} recall@k={row['recall_at_k']:.4f} mrr={row['mrr']:.4f} dims={row['dimensions']}\")
print('  recommended:', r['recommended'])"
  echo
  echo "# the same three candidates after authoring three real semantic paraphrase queries:"
  python3 - "$D" <<'PY'
import sys, yaml
p = sys.argv[1] + "/governance/tests/memory/heldout.yaml"
d = yaml.safe_load(open(p))
d["queries"] = [q for q in d["queries"] if q.get("category") != "semantic_paraphrase"] + [
 {"id": "HQ-S01", "category": "semantic_paraphrase", "query": "why must monetary totals avoid floating point",
  "expected_refs": ["D-0001"], "forbidden": [], "k": 8, "route": "semantic"},
 {"id": "HQ-S02", "category": "semantic_paraphrase", "query": "what did we learn when production sums drifted",
  "expected_refs": ["L-0001"], "forbidden": [], "k": 8, "route": "semantic"},
 {"id": "HQ-S03", "category": "semantic_paraphrase", "query": "which study compared rounding strategies",
  "expected_refs": ["RES-0100"], "forbidden": [], "k": 8, "route": "semantic"}]
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
  gov "$D" memory benchmark --candidate current --candidate builtin:64 --candidate builtin:8 | python3 -c "
import sys, json
r = json.load(sys.stdin)['result']
for row in r['rows']:
    sem = [c['recall'] for c in row['by_category'] if c['category'] == 'semantic_paraphrase']
    print(f\"  {row['candidate']:<12} recall@k={row['recall_at_k']:.4f} mrr={row['mrr']:.4f} semantic_recall={sem[0] if sem else None}\")
print('  recommended:', r['recommended'])"
} > "$ED/ac7/discrimination.out" 2>&1

# --------------------------------------------------------------- V1-BETA-06: OR-of-subtokens on an identifier
E=$(build_corpus evlex); gov "$E" init --name evlex >/dev/null 2>&1
{
  echo "# V1-BETA-06 — an identifier-shaped literal that exists in exactly one chunk of the corpus"
  echo "\$ gov memory query pyfindbysku_marker_0042 --k 5"
  gov "$E" memory query "pyfindbysku_marker_0042" --k 5 | python3 -c "
import sys, json
r = json.load(sys.stdin)['result']
for h in r['hits']:
    print(f\"  {h['score']:.5f}  {h['path']:<28} {h['section'][:34]:<34} contains-the-literal={'pyfindbysku_marker_0042' in h['excerpt']}\")"
} > "$ED/lexical/or-of-subtokens.out" 2>&1

echo "captured:"
for f in "$ED/currency/first-audit-not-current.out" "$ED/ac7/discrimination.out" "$ED/lexical/or-of-subtokens.out"; do
  echo "  $f ($(wc -l < "$f") lines)"
done
