#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate J (Contract v3:594-616)
#   J1 research becomes evidence: question/reason, method, sources/data, measurements, uncertainty, conclusion,
#      confidence, influenced decisions/tasks
#   J2 experiment lifecycle: hypothesis/question, method/data, reproducibility, results, interpretation,
#      decision influence, production merge prohibited where experimental
cd "$(dirname "$0")" && . ./lib.sh
M=jprobe; machine $M && seed_spec && seed_acceptance_test
mkdir -p "$MROOT/bench"; echo "order_id,cents" > "$MROOT/bench/checkout.csv"
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm bench >/dev/null 2>&1

echo "== J1.b1-b7  every J1 field is required before a research output is governed evidence"
check_eq "$(code research record --fields '{"question":"which cache?"}')" RESEARCH_INCOMPLETE "J1.1 question-only record refused"
MISS="$(emsg research record --fields '{"question":"which cache?"}' | python3 -c "import json,sys;print(','.join(sorted(json.load(sys.stdin)['details']['missing'])))")"
check_eq "$MISS" "conclusion,confidence,measurements,method,reason,sources/data,uncertainty" "J1.2 the refusal names each missing J1 field"
for f in reason method sources measurements uncertainty conclusion confidence; do
  FIELDS="$(python3 - "$f" <<'PY'
import json,sys
d={"question":"Which cache backend keeps p99 under 50ms?","reason":"the checkout path misses its budget",
   "method":"load test both backends at 2x peak","sources":["bench/checkout.csv"],
   "measurements":[{"backend":"redis","p99_ms":31}],"uncertainty":"single region",
   "conclusion":"redis meets the budget","confidence":0.8}
d.pop(sys.argv[1]); print(json.dumps(d))
PY
)"
  check_eq "$(code research record --fields "$FIELDS")" RESEARCH_INCOMPLETE "J1.3 a record missing '$f' alone is refused"
done

echo "== J1  a complete record becomes EVIDENCE; a draft does not"
RID="$(res research record --fields '{"question":"Which cache backend keeps p99 under 50ms?","reason":"the checkout path misses its latency budget","method":"load test both backends at 2x peak with the production traffic shape","sources":["bench/checkout.csv"],"measurements":[{"backend":"redis","p99_ms":31},{"backend":"memcached","p99_ms":44}],"uncertainty":"single region; cold-start not measured","conclusion":"redis meets the budget with margin","confidence":0.8}' | python3 -c "import json,sys;print(json.load(sys.stdin)['research']['id'])")"
SH="$(res research show "$RID")"
check_eq "$(echo "$SH" | python3 -c "import json,sys;print(json.load(sys.stdin)['research']['research_state'])")" CONCLUDED "J1.4 complete record is CONCLUDED"
check_eq "$(echo "$SH" | python3 -c "import json,sys;print(json.load(sys.stdin)['research']['state_class'])")" EVIDENCE "J1.5 a concluded record stands as EVIDENCE"
DR="$(res research record --draft --fields '{"question":"is a queue needed?"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['research']['id'])")"
check_eq "$(res research show "$DR" | python3 -c "import json,sys;print(json.load(sys.stdin)['research']['state_class'])")" NARRATIVE "J1.6 a draft is held reference-only (NARRATIVE), not evidence"

echo "== J1.b8  influenced decisions/tasks are derived, reported when unrecorded, and back-filled"
TID="$(res task create --class implementation --objective "Adopt the cache the research chose" --feature F-0001 --status READY --allowed 'src/**,tests/**' --fields "{\"requirements\":[\"REQ-0001\"],\"role\":\"backend-engineer\",\"evidence_refs\":[\"$RID\"]}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
INF="$(res research show "$RID" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['influences']))")"
echo "   influences (before sync): $INF"
check "$(echo "$INF" | python3 -c "import json,sys;print(1 if '$TID' in json.load(sys.stdin)['derived'] else 0)")" "J1.7 a task that relies on the research is derived as an influence" "$INF"
FND="$(res research check | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['findings']))")"
check "$(echo "$FND" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if any(f['code']=='INFLUENCE_NOT_RECORDED' and '$TID' in f['message'] for f in d) else 0)")" "J1.8 an unrecorded influence is reported as a finding" "$FND"
g research sync >/dev/null
INF2="$(res research show "$RID" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['influences']))")"
check "$(echo "$INF2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if '$TID' in d['recorded'] and not d['not_recorded'] else 0)")" "J1.9 sync records the influence backlink" "$INF2"
BT="$(res task create --class implementation --objective "cites the research in an undeclared field" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"role\":\"backend-engineer\",\"research\":[\"$RID\"]}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
echo "   NOTE (not asserted): a task citing the research in an undeclared field ($BT) derives $(res research show "$RID" | python3 -c "import json,sys;print(json.load(sys.stdin)['influences']['derived'])")"

echo "== J2  experiment lifecycle (hypothesis/question, method/data)"
check_eq "$(code experiment design --fields '{"title":"cache bake-off"}')" EXPERIMENT_DESIGN_INCOMPLETE "J2.1 a design with no hypothesis/method/data is refused"
check_eq "$(code experiment design --fields '{"hypothesis":"h","method":"m","inputs":[{"path":"bench/checkout.csv"}],"outputs":["src/cache/**"]}')" EXPERIMENT_OUTPUT_IN_PRODUCTION "J2.2 an experiment whose declared output is in the production tree is refused at design"
EID="$(res experiment design --fields '{"hypothesis":"redis keeps checkout p99 under 50ms at 2x peak","method":"replay the production traffic shape against both backends for 30 minutes","inputs":[{"path":"bench/checkout.csv"}],"outputs":["spec/experiments/cache-bakeoff/**"]}' | python3 -c "import json,sys;print(json.load(sys.stdin)['experiment']['id'])")"
check_eq "$(res experiment show "$EID" | python3 -c "import json,sys;print(json.load(sys.stdin)['experiment']['experiment_state'])")" DESIGNED "J2.3 a complete design is DESIGNED"
check_eq "$(code experiment conclude "$EID" --fields '{"interpretation":"x","decision_influence":"y","confidence":0.9}')" EXPERIMENT_TRANSITION_INVALID "J2.4 concluding before the run is refused (lifecycle is enforced)"
g experiment run "$EID" --results '{"redis_p99_ms":31,"memcached_p99_ms":44}' --environment "linux-x86_64, 8 vCPU" >/dev/null
SHOW="$(res experiment show "$EID")"
check_eq "$(echo "$SHOW" | python3 -c "import json,sys;print(json.load(sys.stdin)['experiment']['experiment_state'])")" RUNNING "J2.5 a recorded run moves it to RUNNING (results recorded)"
check "$(echo "$SHOW" | python3 -c "import json,sys;d=json.load(sys.stdin)['experiment'];print(1 if d['runs'][0].get('results_sha256') and d['runs'][0].get('inputs') else 0)")" "J2.6 the run binds its results and its inputs by digest" ""

echo "-- reproducibility is judged by the OS from the runs, not declared"
AGREE="$(res experiment reproduce "$EID" --results '{"redis_p99_ms":31,"memcached_p99_ms":44}' --environment "linux-x86_64, 8 vCPU")"
check "$(echo "$AGREE" | python3 -c "import json,sys;print(1 if json.load(sys.stdin)['run']['agrees'] else 0)")" "J2.7 an agreeing reproduction is judged to agree" "$AGREE"
DIS="$(res experiment reproduce "$EID" --results '{"redis_p99_ms":320,"memcached_p99_ms":44}' --environment "linux-x86_64, 8 vCPU")"
check "$(echo "$DIS" | python3 -c "import json,sys;d=json.load(sys.stdin);print(0 if d['run']['agrees'] else 1)")" "J2.8 a disagreeing reproduction is judged not to agree" "$DIS"
REPRO="$(res experiment show "$EID" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['experiment']['reproducibility']))")"
echo "   reproducibility after one agreeing and one disagreeing run: $REPRO"
check "$(python3 -c "
import json;d=json.loads('''$REPRO''');print(1 if d.get('status') not in (None,'REPRODUCIBLE') else 0)")" "J2.9 a disagreement leaves reproducibility short of REPRODUCIBLE" "$REPRO"

g experiment conclude "$EID" --fields '{"interpretation":"redis meets the budget; memcached does not","decision_influence":"informs the storage decision for F-0001","confidence":0.8,"reproducibility":{"procedure":"re-run scripts/bakeoff.sh with the recorded dataset","environment":"linux-x86_64, 8 vCPU"}}' >/dev/null
SHOW="$(res experiment show "$EID")"
check_eq "$(echo "$SHOW" | python3 -c "import json,sys;print(json.load(sys.stdin)['experiment']['experiment_state'])")" CONCLUDED "J2.10 conclusion records interpretation and decision influence"

echo "== J2  production merge prohibited where experimental"
ET="$(res task create --class experiment --objective "Run the cache bake-off" --feature F-0001 --status READY --allowed 'spec/experiments/**,src/**' --fields "{\"role\":\"ai-ml-engineer\",\"experiment\":\"$EID\",\"requirements\":[\"REQ-0001\"]}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
check_eq "$(res task show "$ET" | python3 -c "import json,sys;print(json.load(sys.stdin)['production_merge_allowed'])")" "False" "J2.11 an experiment-class task records production_merge_allowed: false"
ROLE=ai-ml-engineer g task claim "$ET" >/dev/null
mkdir -p "$MROOT/spec/experiments/cache-bakeoff"; echo measured > "$MROOT/spec/experiments/cache-bakeoff/run.log"
echo 'pub fn cache_backend() -> &'"'"'static str { "redis" }' >> "$MROOT/src/lib.rs"
R="$(receipt "$ET" exp-close "bake-off done; wired redis into the product" "spec/experiments/cache-bakeoff/run.log,src/lib.rs" passed)"
C="$(ROLE=ai-ml-engineer code task close "$ET" --report "$R")"
check_eq "$C" PRODUCTION_MERGE_NOT_ALLOWED "J2.12 an experiment task whose mutations land in the production tree cannot close"
CHK="$(res experiment check)"
check "$(echo "$CHK" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin)).lower();print(1 if 'production' in s else 0)")" "J2.13 experiment check reports production-merge detection" "$(echo "$CHK" | head -c 300)"
# the same work, kept out of production, closes
git -C "$MROOT" checkout -- src/lib.rs 2>/dev/null
g rebuild-memory --incremental >/dev/null 2>&1
R2="$(receipt "$ET" exp-close-2 "bake-off done, results kept out of production" "spec/experiments/cache-bakeoff/run.log" passed)"
C2="$(ROLE=ai-ml-engineer code task close "$ET" --report "$R2")"
echo "   close with the production write reverted -> $C2"
check "$([ "$C2" != PRODUCTION_MERGE_NOT_ALLOWED ] && echo 1 || echo 0)" "J2.15 the production-merge refusal is scoped: it disappears once the production write is gone" "still $C2"

summary
