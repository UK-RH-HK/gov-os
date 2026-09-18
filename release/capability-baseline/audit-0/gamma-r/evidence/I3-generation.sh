#!/usr/bin/env bash
# P2-AR-0010 — I3 Dynamic generation (Contract v3 lines 571-583): for each of the 11 sources, trigger the source event
# through the product and count task records before/after; then show the only other route (manual create + link).
source "$(dirname "$0")/lib.sh"
R=$(mkproj i3)
echo "project: $R"
ntasks() { ls "$R/spec/tasks" 2>/dev/null | grep -c '^TASK-'; }
ev() { # ev <bullet> <label> <command...>  : run a source event, report task delta
  local b="$1" l="$2"; shift 2
  local before after out; before=$(ntasks); out=$("$@" 2>&1); after=$(ntasks)
  printf '  [%-22s] %-58s tasks before=%-3s after=%-3s generated=%s\n' "$b" "$l" "$before" "$after" "$((after-before))"
  printf '      event result: %s\n' "$(python3 -c '
import json,sys
t=sys.argv[1]
try:
    e=json.loads(t)
except Exception:
    print(t.strip()[:160]); sys.exit()
r=e.get("result")
keys=["status","verdict","cit_status","decision","answered_by_kind","lessons_created","capability_gap","missing","pass","measured","created_tasks","exit","counts"]
summ={k:r[k] for k in keys if isinstance(r,dict) and k in r}
err=(e.get("error") or {})
print("ok=%s %s %s" % (e.get("ok"), err.get("code") or "", json.dumps(summ)[:220]))' "$out")"
}
write_feature "$R" F-0001 "$(readiness_json 'performance_capacity,security_privacy' '')"
( cd "$R" && git add -A && git commit -qm i3 )

hdr "I3 source events"
ev "I3.b1 readiness gaps" "gov readiness plan F-0001" g "$R" orchestrator S0 readiness plan F-0001
# failed tests: break the fixture's product test, run the product suite
sed -i 's/assert_eq!(/assert_ne!(/' "$R/tests/ledger_test.rs"
ev "I3.b2 failed tests" "gov verify product (a product test now fails)" g "$R" orchestrator S0 verify product
g "$R" orchestrator S0 task create --id TASK-FT --class implementation --objective "x" --status READY --allowed 'src/**' >/dev/null; g "$R" backend-engineer S-b task claim TASK-FT >/dev/null
ev "I3.b2 failed tests" "task close reporting tests.status=failed" g "$R" backend-engineer S-b task close TASK-FT --report "$(report_file "$R" ft x '' failed)"
git -C "$R" checkout -q -- tests/ledger_test.rs
# audit findings: make the suite find something (malformed feature cell + unknown claim + uncommitted state)
write_feature "$R" F-BAD '{"security_privacy":"N/A"}'
ev "I3.b3 audit findings" "gov audit (suite reports findings)" g "$R" orchestrator S0 audit
ev "I3.b3 audit findings" "gov doctor" g "$R" orchestrator S0 doctor
rm -f "$R/spec/features/F-BAD.yaml"
# research discoveries: a worker return with discoveries, and a research record
g "$R" orchestrator S0 handoff create --to-role research-agent --task TASK-FT >/dev/null
HID=$(ls "$R/spec/planning" | grep HND | head -1 | sed 's/.yaml//')
printf '{"task":"TASK-FT","status":"success","work_completed":"benchmark","files_changed":[],"evidence":[],"tests":{"status":"passed"},"discoveries":["u32 overflows at 4.2M cents: must change type"],"risks":["data loss"],"lessons":["check widths"],"proposed_decisions":["adopt u64"],"unresolved":["migration of stored totals"],"recommended_next_action":"create migration task"}' > "$R/.governance-runtime/ret.json"
ev "I3.b4 research discoveries" "handoff return with discoveries/unresolved/proposed decision" g "$R" research-agent S-r handoff return "$HID" --file "$R/.governance-runtime/ret.json"
# human decisions: a gate answered A and one answered B
G1=$(g "$R" orchestrator S0 gate create --question "Adopt u64?" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])'); g "$R" orchestrator S0 gate present "$G1" >/dev/null
ev "I3.b5 human decisions" "gov decide $G1 --option A (human)" g "$R" human S-h decide "$G1" --option A --by owner
G2=$(g "$R" orchestrator S0 gate create --question "Ship now?" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])'); g "$R" orchestrator S0 gate present "$G2" >/dev/null
ev "I3.b5 human decisions" "gov decide $G2 --option B (human declines)" g "$R" human S-h decide "$G2" --option B --by owner
# CIT effects: a committed CIT that affects a task
mkdir -p "$R/spec/requirements"; printf '{"id":"REQ-0001","type":"requirement","title":"totals","status":"ACTIVE","feature":"F-0001","kind":"functional","acceptance_criteria":["a"]}\n' > "$R/spec/requirements/REQ-0001.yaml"
g "$R" orchestrator S0 task create --id TASK-AFF --class implementation --objective "affected" --status READY --feature F-0001 --fields '{"requirements":["REQ-0001"]}' >/dev/null
( cd "$R" && git add -A && git commit -qm cit ); g "$R" orchestrator S0 rebuild-memory >/dev/null
printf '[{"op":"set_field","target":"REQ-0001","field":"acceptance_criteria","value":["a","b"]}]' > "$R/.governance-runtime/mf.json"
C=$(g "$R" orchestrator S0 cit propose --proposal "tighten" --trigger editorial --targets REQ-0001 --manifest "$R/.governance-runtime/mf.json" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
g "$R" orchestrator S0 cit simulate "$C" >/dev/null; g "$R" change-controller S-cc cit approve "$C" --by change-controller --method auto >/dev/null
ev "I3.b6 CIT effects" "gov cit execute $C (affects TASK-AFF)" g "$R" change-controller S-cc cit execute "$C"
echo "      TASK-AFF after the CIT: $(grep -E 'retest_required|retest_reason' "$R/spec/tasks/TASK-AFF.yaml" | tr '\n' ' ')"
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("      dag TASK-AFF:",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-AFF"])'
# lessons
ev "I3.b7 lessons" "(lesson L-0001 created by the handoff return above)" ls "$R/spec/lessons"
ev "I3.b7 lessons" "upstream prepare of a PROJECT lesson (only path lessons take)" g "$R" orchestrator S0 upstream prepare L-0001
# missing tools/skills
g "$R" orchestrator S0 task create --id TASK-NEED --class tooling --objective "needs a missing tool+skill" --status READY --fields '{"required_skills":["SKL-NOPE"],"required_tools":["TOOL-NOPE"]}' >/dev/null
ev "I3.b8 missing tools/skills" "gov tools resolve --capability quantum_compile (gap)" g "$R" tooling-engineer S-t tools resolve --capability quantum_compile
ev "I3.b8 missing tools/skills" "gov skills resolve TASK-NEED (missing skill)" g "$R" orchestrator S0 skills resolve TASK-NEED
ev "I3.b8 missing tools/skills" "gov continue (next work carries a skills gap)" g "$R" orchestrator S0 continue
# retrieval failures: a held-out query that cannot be satisfied
python3 - "$R/governance/tests/memory/heldout.yaml" <<'PY'
import yaml,sys; p=sys.argv[1]; d=yaml.safe_load(open(p)) or {}
# keep the generated queries (>= MEMORY_POLICY.regression.min_queries) but make every one expect an absent file
for q in d.get("queries",[]): q["expected_refs"]=["file:spec/does/not/exist.yaml"]
yaml.safe_dump(d,open(p,"w"),sort_keys=False)
PY
ev "I3.b9 retrieval failures" "gov memory verify (held-out query fails)" g "$R" orchestrator S0 memory verify
ev "I3.b9 retrieval failures" "gov memory query with zero hits" g "$R" orchestrator S0 memory query "zebra quantum nonexistent term"
git -C "$R" checkout -q -- governance/tests/memory/heldout.yaml 2>/dev/null
# security findings: a seeded secret in a product file
printf 'AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLEwJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n' > "$R/src/creds.rs"
ev "I3.b10 security findings" "gov audit with a seeded secret in src/creds.rs" g "$R" orchestrator S0 audit
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("      security-relevant findings:",[f["message"][:100] for f in r["findings"] if "secret" in f.get("message","").lower() or "creds" in f.get("message","")][:3])'
rm -f "$R/src/creds.rs"
# performance regressions
ev "I3.b11 performance regressions" "telemetry of a slow operation (latency 99999 ms)" g "$R" orchestrator S0 telemetry emit --name product.perf --attrs '{"latency_ms":99999,"baseline_ms":10}'
ev "I3.b11 performance regressions" "gov telemetry summary" g "$R" orchestrator S0 telemetry summary
grep -rln -i 'performance.regression\|perf_regression\|latency_regression' "$WT/runtime/src" | sed "s|$WT/||;s/^/      detector source: /"; echo "      (no detector source listed = the product has no performance-regression detector)"

hdr "I3 the only route for the other sources: manual task creation with a typed provenance link"
ids=""
for src in "RPT-0001:failed-tests-report" "AUD-0001:audit-finding" "$HID:research-discovery" "D-0001:human-decision" "L-0001:lesson"; do
  s=${src%%:*}; label=${src#*:}
  id=$(g "$R" orchestrator S0 task create --class repair --objective "from $label" --status READY --fields "{\"derived_from\":[\"$s\"]}" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
  ids="$ids $id:$s:$label"
done
g "$R" orchestrator S0 rebuild-memory >/dev/null
for x in $ids; do id=${x%%:*}; rest=${x#*:}; s=${rest%%:*}
  g "$R" orchestrator S0 memory graph "$id" --depth 1 | python3 -c 'import json,sys;print("  manual %-9s (from %-22s) -> %s" % (sys.argv[1],sys.argv[3],[(x["node"],x["via"]) for x in json.load(sys.stdin)["result"] if x["node"]==sys.argv[2]]))' "$id" "$s" "${rest#*:}"
done
echo END
