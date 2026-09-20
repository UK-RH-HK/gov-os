#!/usr/bin/env bash
# C8 — failure memory (Contract v3:276-283). Seven kinds: bugs, failed approaches, wrong assumptions, retrieval
# misses, regressions, migration failures, tool failures.
#
# The test for each kind is the same: can the product, through a governed path, produce a DURABLE structured record
# of that kind that survives a full memory rebuild? A `failure_kind` constant and a unit test over it are not
# evidence of behaviour (Contract v3:93).
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus c8); gov "$ROOT" init --name c8probe >/dev/null 2>&1
S=$BETA_SCRATCH/c8
FDIR="$ROOT/spec/reports/failures"; MDIR="$ROOT/spec/reports/memory-quality"

kinds_on_disk() {
  python3 - "$FDIR" "$MDIR" <<'PY'
import os, sys, yaml
kinds = set()
for d in sys.argv[1:]:
    if not os.path.isdir(d): continue
    for f in os.listdir(d):
        if not f.endswith(".yaml"): continue
        try: r = yaml.safe_load(open(os.path.join(d, f)))
        except Exception: continue
        if isinstance(r, dict) and r.get("type") == "failure" and r.get("failure_kind"):
            kinds.add(r["failure_kind"])
print(" ".join(sorted(kinds)))
PY
}

# --- retrieval miss: the governed reporting path ------------------------------------------------------------------
gov "$ROOT" memory miss --query "how does the ledger handle refunds" --expected REQ-0001 --detail probe > "$S-miss.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1])).get('result') or {}
sys.exit(0 if r.get('kind')=='retrieval-miss' and r.get('id') else 1)" "$S-miss.json"
chk C8-retrieval-miss $? "a retrieval miss is recorded as a durable structured failure record" "no retrieval-miss record"

# --- tool failure: a pinned rerank plugin that does not resolve ---------------------------------------------------
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
s = open(p).read().replace(
    "policy_overrides: {}",
    'policy_overrides:\n  MEMORY_POLICY.reranker.provider: rerank-absent-probe\n  MEMORY_POLICY.reranker.version: "1"')
open(p, "w").write(s)
PY
gov "$ROOT" memory query "integer cents" --k 3 > "$S-rerank.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
sys.exit(0 if (not d.get('ok')) and 'RERANKER' in json.dumps(d.get('error')) else 1)" "$S-rerank.json"
chk C8-tool-failure-refusal $? "a pinned retrieval plugin that does not resolve is a typed refusal, never a silent fallback to the built-in" \
                               "a missing pinned reranker did not refuse"
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
s = open(p).read()
i = s.index("policy_overrides:")
j = s.index("staleness:")
open(p, "w").write(s[:i] + "policy_overrides: {}\n" + s[j:])
PY
gov "$ROOT" tools health > "$S-th.json" 2>&1
case "$(kinds_on_disk)" in *tool-failure*) pass C8-tool-failure "tool failures are recorded as durable structured failure records";;
  *) fail C8-tool-failure "no tool-failure record on disk after a failing plugin and a tool health run";; esac

# --- regression: a governed profile change whose held-out regression does not hold --------------------------------
# The held-out set `gov init` generates leaves its semantic paraphrase queries PENDING, so every embedder candidate
# measures identically on it and no candidate can be worse than the baseline. Author real semantic queries first, so
# that the regression branch this check is about can actually be reached (P2-ADJ-0003: not a vacuous precondition).
P=$(build_corpus_provisioned c8reg)
python3 - "$P" <<'PYX'
import sys, yaml
p = sys.argv[1] + "/governance/tests/memory/heldout.yaml"
d = yaml.safe_load(open(p))
d["queries"] = [q for q in d["queries"] if q.get("category") != "semantic_paraphrase"] + [
 {"id": "HQ-S01", "category": "semantic_paraphrase", "query": "why must monetary totals avoid floating point",
  "expected_refs": ["D-0001"], "forbidden": [], "k": 8, "route": "semantic"},
 {"id": "HQ-S02", "category": "semantic_paraphrase", "query": "what did we learn when production sums drifted",
  "expected_refs": ["L-0001"], "forbidden": [], "k": 8, "route": "semantic"},
 {"id": "HQ-S03", "category": "semantic_paraphrase", "query": "which study compared rounding strategies",
  "expected_refs": ["RES-0100"], "forbidden": [], "k": 8, "route": "semantic"},
]
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
# a floor the BASELINE meets and the degraded candidate does not (a strengthening override, allowed by precedence)
pp = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
txt = open(pp).read().replace(
    "policy_overrides: {}", "policy_overrides:\n  MEMORY_POLICY.regression.min_recall_at_k: 0.9")
open(pp, "w").write(txt)
PYX
RES=$(gov "$P" memory benchmark --candidate current --candidate builtin:8 --record | jget 'd["result"]["research_record"]')
G=$(gov "$P" memory select builtin:8 --research "$RES" | jget 'd.get("result",{}).get("human_gate","")')
if [ -n "$G" ]; then
  owner_answers "$P" "$G" A >/dev/null 2>&1
  gov "$P" memory select builtin:8 --research "$RES" --gate "$G" > "$S-sel8.json" 2>&1
fi
if grep -rq "failure_kind: regression" "$P/spec/reports/failures" 2>/dev/null; then
  pass C8-regression "a failed held-out regression on a governed profile change is recorded as a durable failure record"
else
  fail C8-regression "no regression failure record after a profile change whose regression failed: $(head -c 300 "$S-sel8.json")"
fi
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
e=json.dumps(d.get('error') or {})
sys.exit(0 if (not d.get('ok')) and 'PROFILE_REGRESSION_FAILED' in e and 'rolled back' in e else 1)" "$S-sel8.json"
chk C8-regression-rollback $? "the failed profile change is rolled back automatically and the refusal names the restored profile"                               "a profile change whose regression failed was not rolled back"
gov "$P" memory profile > "$S-prof.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
sys.exit(0 if '512-d' in r['profile'] else 1)" "$S-prof.json"
chk C8-regression-restored $? "after the rollback the live retrieval profile is the previous one" "the rolled-back profile was not restored"

# --- the four kinds with no writer --------------------------------------------------------------------------------
for k in bug failed-approach incorrect-assumption migration-failure; do
  case " $(kinds_on_disk) " in
    *" $k "*) pass "C8-$k" "a $k record exists in failure memory";;
    *) fail "C8-$k" "no governed path produces a '$k' failure record: 'gov memory miss' records only retrieval misses, and the product's only other writers are tool-failure and regression; the kind exists in the KINDS constant and in the schema only";;
  esac
done

# --- durability across a full rebuild ------------------------------------------------------------------------------
BEFORE=$(kinds_on_disk)
aside "$ROOT/.governance-runtime"
gov "$ROOT" rebuild-memory > "$S-rebuild.json" 2>&1
AFTER=$(kinds_on_disk)
[ -n "$BEFORE" ] && [ "$BEFORE" = "$AFTER" ]
chk C8-durable $? "failure memory survives deletion and full rebuild of derived state (kinds before=[$BEFORE] after=[$AFTER])" \
                  "failure memory did not survive a rebuild (before=[$BEFORE] after=[$AFTER])"

# a retrieval-miss record must never answer the query it records (it is deliberately not indexed)
gov "$ROOT" memory query "how does the ledger handle refunds" --k 8 > "$S-q.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1])).get('result') or {}
sys.exit(0 if not any('memory-quality' in h.get('path','') for h in r.get('hits',[])) else 1)" "$S-q.json"
chk C8-not-indexed $? "a recorded retrieval miss is never itself returned as the answer to the query it records" \
                      "the memory-quality record answers its own query"

summary
