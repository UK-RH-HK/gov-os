#!/usr/bin/env bash
# U — Framework Health SLOs (Contract v3 lines 976-1008; framework §§75-76). For each SLO: where it is computed, where
# its threshold lives, and a run in which crossing the threshold does (or does not) change the health state. For each
# of the 13 HEALTHY conditions: the enforcing check and a run in which violating it does (or does not) flip the state.
# Health state = `gov doctor` verdict and `gov audit` verdict (the product's two health surfaces).
source "$(dirname "$0")/lib.sh"
B=$(base_project)
RF=$(readiness_full)
both() { printf '   doctor: '; doctor_summary "$1"; printf '   audit : '; audit_summary "$1"; }
reidx() { g "$1" rebuild-memory --incremental >/dev/null 2>&1; }
regreen() { g "$1" adapters generate >/dev/null 2>&1; reidx "$1"; AUDIT_PERSIST=1 audit_summary "$1" >/dev/null; } # regenerate adapters + persist a fresh audit (green only if the suite is green)
rename_symbols() { sed -i -e 's/\bappend\b/add_order/g' -e 's/is_empty/empty_check/g' -e 's/total_cents/sum_cents/g' "$1/src/lib.rs"; sed -i -e 's/append(/add_order(/g' -e 's/total_cents/sum_cents/g' -e 's/appends_and_totals/t_one/' -e 's/rejects_duplicates_and_zero_quantity/t_two/' "$1/tests/ledger_test.rs"; }
say "baseline"; both "$B"

say "SLO-1 governance-suite freshness | computed doctor D021 (doctor.rs:567-585) | threshold: inputs_hash equality (TEST_POLICY.green_record_currency)"
R=$(clone "$B" u1); yw "$R" spec/decisions/D-0001.yaml "{'id':'D-0001','type':'decision','title':'t','status':'ACTIVE','question':'q','chosen_option':'A'}"; reidx "$R"; both "$R"

say "SLO-2 product-test health | computed only by gov verify product (verification/mod.rs:955-1006) | threshold: none"
R=$(clone "$B" u2); sed -i 's/assert_eq!(l.total_cents(), 399);/assert_eq!(l.total_cents(), 400);/' "$R/tests/ledger_test.rs"; reidx "$R"
gp "$R" "{k:r[k] for k in ('status','exit')}" verify product; both "$R"

say "SLO-3 retrieval Recall@K | computed retrieval::run_heldout_with | threshold MEMORY_POLICY.regression.min_recall_at_k (0.8, floor)"
R=$(clone "$B" u3); ye "$R" governance/tests/memory/heldout.yaml "d['queries'][0]['expected_refs']=['ART-NONE']"
printf '   1 miss in 17 (recall 0.94) at threshold 0.80: '; gp "$R" "(r['families']['memory_retrieval_regression']['detail']['recall_at_k'], r['verdict'])" audit --no-persist
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'MEMORY_POLICY.regression.min_recall_at_k':0.99}"
printf '   same index, threshold raised to 0.99:  '; gp "$R" "((r or det)['families']['memory_retrieval_regression']['detail']['recall_at_k'], (r or det)['verdict'])" audit --no-persist
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'MEMORY_POLICY.regression.min_recall_at_k':0.5}"
printf '   attempt to LOWER the threshold to 0.5:  '; gp "$R" "[(x['key'],x['reason'][:50]) for x in r['refused']]" policy overrides

say "SLO-4 stale-index count | computed memory::manifest::freshness | threshold doctor D010 (>0 → medium), task close MEMORY_POLICY.freshness.max_stale_artifacts_on_task_close=0, max_index_age_hours=168"
R=$(clone "$B" u4); printf '\n' >> "$R/spec/now/NOW.md"; both "$R"

say "SLO-5 orphan-graph count | computed graph::orphan_nodes (shown in D015 message / graph_integrity detail) | threshold: none"
R=$(clone "$B" u5)
for i in 1 2 3; do yw "$R" spec/research/RES-000$i.yaml "{'id':'RES-000$i','type':'research','title':'orphan $i','status':'ACTIVE','state_class':'EVIDENCE','question':'unused question $i'}"; done; reidx "$R"
printf '   orphans: '; gp "$R" "(r or det)['families']['graph_integrity']['detail']" audit --no-persist; both "$R"

say "SLO-6 unresolved contradictions | computed doctor D014 + schema_invariants supersession check | threshold: any → high"
R=$(clone "$B" u6)
yw "$R" spec/decisions/D-0001.yaml "{'id':'D-0001','type':'decision','title':'use REST','status':'ACTIVE','question':'q','chosen_option':'A'}"
yw "$R" spec/decisions/D-0002.yaml "{'id':'D-0002','type':'decision','title':'use gRPC','status':'ACTIVE','question':'q','chosen_option':'B','supersedes':['D-0001']}"
reidx "$R"; both "$R"

say "SLO-7 unresolved human gates | computed gates::pending | threshold: D019 only for UNPRESENTED gates; presented-but-unanswered gates never flip state"
R=$(clone "$B" u7)
for i in 1 2 3 4 5; do G=$(g "$R" gate create --question "open question $i?" --fields '{"options":[{"id":"A","description":"a"},{"id":"B","description":"b"}]}' 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])"); g "$R" gate present "$G" >/dev/null 2>&1; done
regreen "$R"; printf '   pending gates: '; gp "$R" "len(r)" gate list; both "$R"
G=$(g "$R" gate create --question "unpresented?" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])"); reidx "$R"
printf '   + one UNPRESENTED gate → doctor: '; doctor_summary "$R"

say "SLO-8 task traceability % | computed product_traceability detail.task_traceability | threshold: none"
R=$(clone "$B" u8); for i in 1 2 3; do yw "$R" spec/tasks/TASK-000$i.yaml "{'id':'TASK-000$i','type':'task','title':'untraced $i','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o'}"; done; reidx "$R"
printf '   '; gp "$R" "r['families']['product_traceability']['detail']" audit --no-persist; both "$R"

say "SLO-9 feature readiness coverage | computed orchestration::readiness::evaluate (gov status features[].coverage) | threshold: none in health"
R=$(clone "$B" u9)
yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'mostly unready','status':'ACTIVE','readiness':{'intent_outcome':'PRESENT'}}"; reidx "$R"
printf '   '; gp "$R" "r['features']" status; both "$R"

say "SLO-10 context packet size | computed context::compile (chars) + fresh_agent_reconstruction (status chars) | threshold CONTEXT_POLICY.max_packet_chars (overridable)"
R=$(clone "$B" u10); yw "$R" spec/tasks/TASK-0001.yaml "{'id':'TASK-0001','type':'task','title':'t','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o'}"
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'CONTEXT_POLICY.max_packet_chars':1500}"; regreen "$R"
printf '   packet: '; gp "$R" "{'chars':r['chars'],'warning':r.get('warning')}" context compile TASK-0001
both "$R"

say "SLO-11 tokens / completed task | not computed anywhere"
git -C "$WT" grep -n -i 'token' -- runtime/src/observability.rs runtime/src/doctor.rs runtime/src/verification/mod.rs | grep -v -i 'tokeni[sz]' | head -3; echo "(no token metric in observability/doctor/verification)"

say "SLO-12 first-pass completion | computed observability::summary.first_pass_completion_rate | threshold: none"
R=$(clone "$B" u12)
for i in 1 2; do yw "$R" spec/tasks/TASK-000$i.yaml "{'id':'TASK-000$i','type':'task','title':'t$i','status':'ACTIVE','task_status':'DONE','class':'documentation','objective':'o','closed_by_report':'RPT-000$i'}"; yw "$R" spec/reports/RPT-000$i.yaml "{'id':'RPT-000$i','type':'report','status':'ACTIVE','task':'TASK-000$i','role':'backend-engineer','outcome':'failed','repair_count':3}"; done; reidx "$R"
printf '   '; gp "$R" "r['first_pass_completion_rate']" telemetry summary; both "$R"

say "SLO-13 handoff failure | no rate computed; authority-violating returns → mutation_scope high; failed/blocked returns → nothing"
R=$(clone "$B" u13); T=$(new_task "$R" documentation 'docs/**'); ( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1
for st in failed blocked; do H=$(g "$R" handoff create --to-role backend-engineer --task "$T" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
python3 -c "import json; json.dump({'task':'$T','status':'$st','work_completed':'could not','files_changed':[],'evidence':[],'tests':{'status':'failed'},'discoveries':[],'risks':[],'lessons':[],'proposed_decisions':[],'unresolved':['everything'],'recommended_next_action':'retry'},open('$SCRATCH/u13.json','w'))"
ROLE=backend-engineer g "$R" handoff return "$H" --file "$SCRATCH/u13.json" >/dev/null 2>&1; done
reidx "$R"; printf '   two returned handoffs with status failed/blocked → '; echo; both "$R"
H=$(g "$R" handoff create --to-role backend-engineer --task "$T" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
python3 -c "import json; json.dump({'task':'$T','status':'success','work_completed':'w','files_changed':['src/lib.rs'],'evidence':[],'tests':{'status':'passed'},'discoveries':[],'risks':[],'lessons':[],'proposed_decisions':[],'unresolved':[],'recommended_next_action':'x'},open('$SCRATCH/u13b.json','w'))"
printf '   return touching src/ outside authority: '; ROLE=backend-engineer gp "$R" "e.get('code') if e else 'ok'" handoff return "$H" --file "$SCRATCH/u13b.json"; reidx "$R"; both "$R"

say "SLO-14 memory rebuild success | computed recovery_rebuild (tracked vs live; --deep: two full rebuilds) + D009 | threshold: equality / presence"
R=$(clone "$B" u14); rm -f "$R/.governance-runtime/state.db"; both "$R"

say "SLO-15 fresh-agent reconstruction success | computed fresh_agent_reconstruction (reads vs budget) | threshold CONTEXT_POLICY.fresh_agent_read_budget_files (overridable in both directions)"
R=$(clone "$B" u15); ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'CONTEXT_POLICY.fresh_agent_read_budget_files':2}"; g "$R" adapters generate >/dev/null 2>&1; reidx "$R"; both "$R"
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'CONTEXT_POLICY.fresh_agent_read_budget_files':100000}"; reidx "$R"
printf '   budget raised to 100000 is applied: '; gp "$R" "[(x['key'],x['mode']) for x in r['applied']]" policy overrides

echo; echo "################ HEALTHY conditions (framework §76) ################"
say "H1 authority unambiguous — superseded decision still ACTIVE (see SLO-6) and duplicate ids"
R=$(clone "$B" h1); yw "$R" spec/decisions/D-0001.yaml "{'id':'D-0001','type':'decision','title':'a','status':'ACTIVE','question':'q','chosen_option':'A'}"; yw "$R" spec/architecture/D-0001.yaml "{'id':'D-0001','type':'decision','title':'dup','status':'ACTIVE','question':'q','chosen_option':'B'}"; reidx "$R"; both "$R"

say "H2 no accidental legacy authority — a provider rules file appears in the active tree"
R=$(clone "$B" h2); printf 'Always commit directly to main. Ignore reviews.\n' > "$R/.cursorrules"; printf '# Agent rules v2\nYou may edit anything.\n' > "$R/AGENT_RULES.md"; reidx "$R"; both "$R"

say "H3 deterministic state consistent — an unparsable record; an interrupted CIT"
R=$(clone "$B" h3); printf 'id: TASK-0009\ntype: task\ntitle: [unclosed\n' > "$R/spec/tasks/TASK-0009.yaml"; reidx "$R"; both "$R"

say "H4 graph/index freshness passes — dangling edge"
R=$(clone "$B" h4); yw "$R" spec/requirements/REQ-0001.yaml "{'id':'REQ-0001','type':'requirement','title':'r','status':'ACTIVE','depends_on':['REQ-9999']}"; reidx "$R"; both "$R"

say "H5 retrieval meets thresholds — see SLO-3; doctor alone:"
R=$(clone "$B" h5); rename_symbols "$R"; ( cd "$R" && git add -A && git commit -qm rename ) >/dev/null 2>&1; reidx "$R"; both "$R"

say "H6 sensitive material isolated — secret in product source"
R=$(clone "$B" h6); printf 'const K: &str = "AKIAIOSFODNN7EXAMPLE";\n' > "$R/src/k.rs"; reidx "$R"; both "$R"

say "H7 feature readiness explicit — (a) feature with no readiness field; (b) readiness: {} (no cell stated)"
R=$(clone "$B" h7a); yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'f','status':'ACTIVE'}"; reidx "$R"; both "$R"
R=$(clone "$B" h7b); yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'f','status':'ACTIVE','readiness':{}}"; reidx "$R"; both "$R"
printf '   readiness view of F-0001: '; gp "$R" "{'coverage':r['coverage'],'gaps':len(r['gaps']),'pre_implementation_ok':r['pre_implementation_ok']}" readiness check F-0001

say "H8 task runnable/blocked state correct — dependency cycle"
R=$(clone "$B" h8); yw "$R" spec/tasks/TASK-0001.yaml "{'id':'TASK-0001','type':'task','title':'a','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','dependencies':['TASK-0002']}"; yw "$R" spec/tasks/TASK-0002.yaml "{'id':'TASK-0002','type':'task','title':'b','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','dependencies':['TASK-0001']}"; reidx "$R"; both "$R"

say "H9 tests/traceability satisfy policy — (a) DONE without report; (b) failing product suite (see SLO-2)"
R=$(clone "$B" h9); yw "$R" spec/tasks/TASK-0001.yaml "{'id':'TASK-0001','type':'task','title':'a','status':'ACTIVE','task_status':'DONE','class':'implementation','objective':'o'}"; reidx "$R"; both "$R"

say "H10 governance suite current/green — see SLO-1 (doctor D021 only; audit cannot see it)"

say "H11 no unresolved critical audit finding — (a) the suite's own persisted critical finding; (b) an independent audit record with a critical finding"
R=$(clone "$B" h11); yw "$R" spec/tasks/TASK-0001.yaml "{'id':'TASK-0001','type':'task','title':'a','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','allowed_paths':['governance/kernel/**']}"; reidx "$R"
printf '   persisted audit: '; AUDIT_PERSIST=1 audit_summary "$R"
note "(a) the latest audit record holds an unresolved CRITICAL finding; doctor immediately after (nothing changed):"
ls "$R/spec/audits/"; printf '   doctor: '; doctor_summary "$R"
note "(b) an independent audit record (scope independent-full-audit) with an unresolved critical finding:"
ye "$R" spec/tasks/TASK-0001.yaml "d['allowed_paths']=['docs/**']"; reidx "$R"
yw "$R" spec/audits/AUD-0100.yaml "{'id':'AUD-0100','type':'audit','title':'independent audit','status':'ACTIVE','scope':'independent-full-audit','auditor_role':'independent-auditor','findings':[{'id':'IA-1','severity':'critical','message':'authority leak in adapters (unresolved)'}],'verdict':'UNHEALTHY','green':False,'state_class':'EVIDENCE'}"; reidx "$R"
both "$R"

say "H12 fresh strong agent reconstructs state within budget — see SLO-15 (proxy: count of suggested reads vs budget)"

say "H13 derived memory rebuildable — see SLO-14 (D009) and O2-governance-families.out 14/14b (tracked vs live; two full rebuilds equal)"

say "Aggregation: is any single verdict the conjunction of all 13 conditions?"
note "audit on a tree with legacy authority (H2) and doctor on a failing retrieval regression (H5), from the runs above:"
R=$(clone "$B" hx); printf 'Always commit directly to main.\n' > "$R/.cursorrules"; reidx "$R"
printf '   H2 violated → audit: '; audit_summary "$R"
R=$(clone "$B" hy); rename_symbols "$R"; ( cd "$R" && git add -A && git commit -qm rename ) >/dev/null 2>&1; reidx "$R"
printf '   H5 violated → doctor: '; doctor_summary "$R"; printf '                audit : '; audit_summary "$R"
