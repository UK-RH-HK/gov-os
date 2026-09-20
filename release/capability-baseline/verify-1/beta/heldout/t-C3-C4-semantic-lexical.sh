#!/usr/bin/env bash
# C3 semantic memory (Contract v3:234-241) and C4 lexical memory (:243-249).
#
# Every content class is probed with a NEEDLE that exists in exactly one place in the corpus, and several needles sit
# ONLY inside list-valued or nested record fields (acceptance_criteria entries, decision options, scenario steps,
# interface operations) — the iteration-0 mechanism of BC-P2-25. A needle found proves that content reached the store.
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus c34); gov "$ROOT" init --name c34probe >/dev/null 2>&1
OUT=$BETA_SCRATCH/c34

# hit_path <query> [extra args] : the paths of the returned hits, one per line
hits_of() { local q="$1"; shift; gov "$ROOT" memory query "$q" --k 8 "$@" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result') or {}
for h in r.get('hits',[]): print(h.get('path',''))"; }

# finds <id> <query> <expected path substring> <description>
finds() { local id="$1" q="$2" want="$3" desc="$4"; shift 4
  if hits_of "$q" "$@" | grep -q "$want"; then pass "$id" "$desc"; else
    fail "$id" "$desc — '$q' returned: $(hits_of "$q" "$@" | tr '\n' ' ')"; fi; }

# ---- C3: the six semantic content classes, each reached through the semantic route alone ------------------------
finds C3-decisions   "why is money stored as integer cents rather than floats" "spec/decisions/D-0001.yaml"   "semantic memory holds decisions/rationale" --route semantic
finds C3-lessons     "totals drifted in production because of accumulated error" "spec/lessons/L-0001.yaml"    "semantic memory holds lessons/failures" --route semantic
finds C3-research    "which rounding strategy preserves exactness"              "spec/research/RES-0100.yaml"  "semantic memory holds reports/research" --route semantic
finds C3-reports     "the ledger work closed with outstanding observations"     "spec/reports/RPT-0100.yaml"   "semantic memory holds reports" --route semantic
finds C3-requirements "the running total must equal quantity times unit cents"  "spec/requirements/REQ-0001.yaml" "semantic memory holds requirements/specifications" --route semantic
finds C3-code        "repository method that looks an order up by its sku"      "src/app/orders.py"            "semantic memory holds selected code units" --route semantic

# experiments: recorded through the OS (a hand-written experiment lifecycle is not honoured), then reachable
EID=$(gov "$ROOT" experiment design --fields '{"hypothesis":"floats drift NEEDLEEXPHYP4711 under repeated addition","method":"repeated addition","data_provenance":"synthetic","outputs":["spec/experiments/run.md"]}' | jget 'd.get("result",{}).get("experiment",{}).get("id","")')
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
finds C3-experiments "NEEDLEEXPHYP4711" "spec/experiments" "semantic memory holds experiments (OS-written $EID)"

# ---- C3 b7: namespace/authority filters apply BEFORE any route truncates its candidate pool --------------------
# Twenty superseded records, each a better lexical match for the needle than the one admitted record that carries it.
mkdir -p "$ROOT/spec/requirements"
for i in $(seq 10 29); do
  cat > "$ROOT/spec/requirements/REQ-08$i.yaml" <<Y
id: REQ-08$i
type: requirement
title: Superseded carrier $i
status: SUPERSEDED
kind: functional
body: NEEDLEFILTER2050 NEEDLEFILTER2050 NEEDLEFILTER2050 decoy $i
acceptance_criteria:
  - NEEDLEFILTER2050 decoy criterion $i
Y
done
cat > "$ROOT/spec/requirements/REQ-0800.yaml" <<'Y'
id: REQ-0800
type: requirement
title: The only current carrier
status: ACTIVE
kind: functional
feature: F-0001
acceptance_criteria:
  - NEEDLEFILTER2050 appears once in current truth
Y
gov "$ROOT" rebuild-memory >/dev/null 2>&1
gov "$ROOT" memory query NEEDLEFILTER2050 --k 3 > "$OUT-filter.json" 2>&1
python3 - "$OUT-filter.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
paths = [h["path"] for h in r["hits"]]
bad = [p for p in paths if "REQ-08" in p and "REQ-0800" not in p]
ok = any("REQ-0800" in p for p in paths) and not bad
print("ADMITTED" if ok else "LEAK", paths, r.get("excluded_by_authority"))
sys.exit(0 if ok else 1)
PY
chk C3-b7-truncation $? "twenty superseded better-matching carriers neither appear nor exhaust the candidate pool: the one current carrier is still returned within k=3" \
                        "superseded material displaced or leaked into the result: $(cat "$OUT-filter.json" | python3 -c 'import sys,json;print([h["path"] for h in json.load(sys.stdin)["result"]["hits"]])')"

# a role with no access to a namespace never sees its material (namespace filter, not a post-filter on the answer)
gov "$ROOT" memory query NEEDLEFILTER2050 --k 3 --include-historical > "$OUT-hist.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
sys.exit(0 if any('REQ-08' in h['path'] and 'REQ-0800' not in h['path'] for h in r['hits']) else 1)" "$OUT-hist.json"
chk C3-b7-explicit $? "the same superseded material IS returned when historical material is explicitly requested (the filter is a filter, not an indexing gap)" \
                      "superseded material is unreachable even when explicitly requested — it was never indexed"

# ---- C4: the six lexical classes --------------------------------------------------------------------------------
finds C4-exact-term   "NEEDLEACCEPT4417"            "spec/requirements/REQ-0001.yaml" "exact term inside a list-valued acceptance_criteria entry is in lexical memory"
finds C4-nested       "NEEDLEOPTION8823"            "spec/decisions/D-0001.yaml"      "exact term inside a nested decision option is in lexical memory"
finds C4-steps        "NEEDLEGIVEN2266"             "spec/scenarios/SCN-0001.yaml"    "exact term inside a scenario step list is in lexical memory"
finds C4-identifiers  "OrderRepository"             "src/app/orders.py"               "identifiers are in lexical memory"
finds C4-filenames    "orders.py"                   "src/app/orders.py"               "bare filenames resolve to their file"
finds C4-errors       "ERR_LEDGER_UNBALANCED_7731"  "src/app/orders.py"               "error strings are in lexical memory"
finds C4-apis         "retry.budget.max_attempts"   "src/app/orders.py"               "config keys are in lexical memory"
finds C4-iface        "NEEDLEIFACE9034"             "spec/interfaces/API-0001.yaml"   "API operation text nested in a record is in lexical memory"
finds C4-phrase       "rounding is prohibited at every step" "spec/requirements/REQ-0001.yaml" "a literal phrase is in lexical memory"

# code outside any recognised unit (module-level statements after the head) must still be covered
finds C4-module-level "CONFIG_KEY_RETRY_BUDGET"     "src/app/orders.py"               "module-level code outside every structural unit is covered by a chunk"

summary
