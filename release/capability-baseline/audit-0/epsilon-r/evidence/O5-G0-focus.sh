#!/usr/bin/env bash
# O5 tier G0 — focused follow-up on commands the matrix (O5-G0-guard-matrix.out) showed mutating state while
# FREEZE_WRITES is active and/or as an L0 role. What exactly do they change?
source "$(dirname "$0")/lib.sh"
B=$(base_project)
snap() { ( cd "$1" && find spec governance framework.json -type f 2>/dev/null | sort | xargs sha256sum ) > "$2"; }
changed() { diff <(awk '{print $2" "$1}' "$1") <(awk '{print $2" "$1}' "$2") | grep '^[<>]' | awk '{print $2}' | sort -u | tr '\n' ' '; echo; }

say "1 init --force as independent-auditor (L0; install_kernel requires L4) while FREEZE_WRITES is active"
R=$(clone "$B" g0f-1)
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'MEMORY_POLICY.freshness.max_index_age_hours':24}"
( cd "$R" && git add -A && git commit -qm override ) >/dev/null 2>&1
gp "$R" "r['writes_frozen']" freeze-writes --reason "incident"
printf 'L0 task create (control): '; ROLE=independent-auditor gp "$R" "e.get('code') if e else 'ok'" task create --class documentation --objective x
snap "$R" "$SCRATCH/g0f-1.before"
printf 'L0 init --force: '; ROLE=independent-auditor gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'version':(r or {}).get('version')}" init --force --name g0f-1
snap "$R" "$SCRATCH/g0f-1.after"
printf 'files changed: '; changed "$SCRATCH/g0f-1.before" "$SCRATCH/g0f-1.after"
printf 'project override after re-init: '; python3 -c "import yaml; print(yaml.safe_load(open('$R/governance/project/PROJECT_POLICY.yaml')).get('policy_overrides'))"
printf 'control state after: '; python3 -c "import json; print(json.load(open('$R/.governance-runtime/control.json')))"

say "2 memory heldout-starter --force as L0 while frozen: the governed held-out retrieval test set is regenerated"
R=$(clone "$B" g0f-2)
ye "$R" governance/tests/memory/heldout.yaml "d['queries'].append({'id':'HQ-900','category':'semantic_paraphrase','query':'verifier-authored paraphrase','expected_refs':['file:src/lib.rs'],'k':8})"
python3 -c "import yaml; d=yaml.safe_load(open('$R/governance/tests/memory/heldout.yaml')); print('before: queries', len(d['queries']), 'has HQ-900:', any(q['id']=='HQ-900' for q in d['queries']))"
gp "$R" "r['writes_frozen']" freeze-writes --reason "incident"
printf 'L0 heldout-starter --force: '; ROLE=independent-auditor gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'r':r}" memory heldout-starter --force
python3 -c "import yaml; d=yaml.safe_load(open('$R/governance/tests/memory/heldout.yaml')); print('after : queries', len(d['queries']), 'has HQ-900:', any(q['id']=='HQ-900' for q in d['queries']), 'generated_by:', d.get('generated_by'))"

say "3 adopt baseline as L0 while frozen"
R=$(clone "$B" g0f-3); gp "$R" "r['writes_frozen']" freeze-writes --reason "incident"
snap "$R" "$SCRATCH/g0f-3.before"
printf 'L0 adopt baseline: '; ROLE=independent-auditor gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'stage':(r or {}).get('stage')}" adopt baseline
snap "$R" "$SCRATCH/g0f-3.after"; printf 'files changed: '; changed "$SCRATCH/g0f-3.before" "$SCRATCH/g0f-3.after"

say "4 audit (persist), adapters generate, tools registry while frozen"
R=$(clone "$B" g0f-4); gp "$R" "r['writes_frozen']" freeze-writes --reason "incident"
snap "$R" "$SCRATCH/g0f-4.before"
for c in "audit" "adapters generate" "tools registry"; do printf '%s: ' "$c"; gp "$R" "ok if ok else e.get('code')" $c; done
snap "$R" "$SCRATCH/g0f-4.after"; printf 'files changed: '; changed "$SCRATCH/g0f-4.before" "$SCRATCH/g0f-4.after"

say "5 route --record while frozen with a cost above BUDGET_POLICY: a human gate is minted under FREEZE_WRITES"
R=$(clone "$B" g0f-5); gp "$R" "r['writes_frozen']" freeze-writes --reason "incident"
python3 -c "import json; json.dump({'model':'m','provider':'p','task_class':'documentation','reasoning_effort':'low','cost':999.0,'latency_ms':10,'pass':True,'repair_count':0,'reviewer_findings':0},open('$SCRATCH/g0f-5.json','w'))"
printf 'route --record: '; gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'gate':(r or {}).get('human_gate'),'threshold':(r or {}).get('threshold_exceeded')}" route --record "$SCRATCH/g0f-5.json"
ls "$R/spec/decisions" "$R/spec/planning" 2>/dev/null | grep -i hdg; find "$R/spec" -name 'HDG-*'
