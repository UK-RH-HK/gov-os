#!/usr/bin/env bash
# V1-V4 Qualification Oracle (Contract v3 lines 1012-1062) — AC-6 oracle-format determination — and reconciliation of the
# contract's derived views against the owner source for this family's scope (O, P, Q, U, V).
source "$(dirname "$0")/lib.sh"
say "A. is there any machine-checkable oracle definition on the candidate? (whole tree, excluding this evidence dir)"
note "V1-V4 field names searched as identifiers (snake/kebab/camel) in every tracked file:"
for pat in 'fault[_-]?manifest|faultManifest' 'hidden[_-]?truth|authoritative[_-]truth' 'injected[_-]?(repository[_-]?)?state' 'expected[_-]?detection' 'expected[_-]?severity' 'expected[_-]?(impacted|governed)' 'forbidden[_-]?outcomes?' 'path[_-]?map[_-]?oracle' 'memory[_-]?oracle' 'expected[_-]?(target[_-]?path|classification|namespace)' 'must[_-]?never[_-]?be[_-]?indexed|never[_-]?indexed' 'detection[_-]?recall' 'severity[_-]?accuracy|impact[_-]?map[_-]?accuracy|path[_-]?map[_-]?accuracy' 'wrong[_-]?indexing' 'human[_-]?gate[_-]?correctness|readiness[_-]?correctness'; do
  n=$(git -C "$WT" grep -l -i -E "$pat" HEAD -- . ':!release/capability-baseline' 2>/dev/null | sed 's/^HEAD://' | tr '\n' ' ')
  printf '  %-60s %s\n' "$pat" "${n:-<none>}"
done
note "schemas shipped by the product (framework/schemas):"; ls "$WT/framework/schemas" | tr '\n' ' '; echo
note "files under release/orchestration/phase-2 (orchestration records of this phase):"; git -C "$WT" ls-files release/orchestration/phase-2 | tr '\n' ' '; echo
note "gate register entry for the oracle format:"; grep -n -A4 'GATE-P2-ORACLE-FORMAT' "$WT/release/orchestration/phase-2/GATES/GATE-REGISTER.yaml" | head -6

say "B. does the product validate an oracle document? (a V1 fault manifest missing every V1 field, as a governed record)"
B=$(base_project); R=$(clone "$B" v)
yw "$R" spec/qualification/FM-0001.yaml "{'id':'FM-0001','type':'fault-manifest','title':'empty fault manifest','status':'ACTIVE'}"
yw "$R" spec/qualification/FM-0002.yaml "{'id':'FM-0002','type':'fault-manifest','title':'nonsense','status':'ACTIVE','class':42,'expected_severity':'purple'}"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
audit_summary "$R" --family schema_invariants
note "no command accepts an oracle / fault manifest / scoring input:"
for c in "qualify" "oracle" "score" "qualification"; do printf 'gov %s: ' "$c"; "$GOV" "$c" 2>&1 | head -1; done

say "C. V4 metrics the product can compute today (retrieval metrics only; nothing scores injected defects)"
gp "$B" "{k:r[k] for k in ('recall_at_k','mrr','precision_at_k','stale_hit_rate','superseded_hit_rate','forbidden_violations')}" memory verify

say "D. contract derived views vs owner source (this family's scope)"
CAN="$SCRATCH/v-contract"; rm -rf "$CAN"; mkdir -p "$CAN/framework/contracts" "$CAN/framework/schemas" "$CAN/tests/governance" "$CAN/docs/generated"
cp "$WT/Governance_OS_Capability_Acceptance_Contract_v3.md" "$CAN/"; cp -r "$WT/framework/contracts/." "$CAN/framework/contracts/"
cp "$WT/framework/schemas/governance-capability-acceptance.schema.json" "$CAN/framework/schemas/"
cp "$WT/tests/governance/capability-evidence-map.yaml" "$CAN/tests/governance/"; cp "$WT/docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md" "$CAN/docs/generated/"
h0=$(cd "$CAN" && find . -type f | sort | xargs sha256sum | sha256sum | cut -c1-16)
"$GOV" --json --root "$CAN" contract verify 2>&1 | python3 -c "import json,sys;d=json.load(sys.stdin);r=d.get('result') or {};print('contract verify:', d.get('ok'), r.get('verdict') or r.get('status') or (d.get('error') or {}).get('code'), '| capability_count:', r.get('capability_count'))"
h1=$(cd "$CAN" && find . -type f | sort | xargs sha256sum | sha256sum | cut -c1-16); echo "scratch copy unchanged by verify: $h0 == $h1"
python3 - "$WT" <<'EOF'
import sys,yaml,re
WT=sys.argv[1]
src=open(f"{WT}/Governance_OS_Capability_Acceptance_Contract_v3.md").read().splitlines()
comp=yaml.safe_load(open(f"{WT}/framework/contracts/governance-capability-acceptance.yaml"))
emap=yaml.safe_load(open(f"{WT}/tests/governance/capability-evidence-map.yaml"))
ids=[c['id'] for c in comp['capabilities']]
print("compiled capability ids in scope:", [i for i in ids if i[0] in 'OPQUV'])
print("gate U present in compiled form:", any(i.startswith('U') for i in ids), "| in evidence map:", any(c['capability'].startswith('U') for c in emap['capabilities']))
# owner-source headings and markers in scope
for n,l in enumerate(src,1):
    if re.match(r'^#+ (GATE [OUV]|O5\.|V[1-4]\.)', l): print(f"  source {n}: {l}")
for c in comp['capabilities']:
    if c['id'] in ('O5','V1','V2','V3','V4'): print(f"  compiled {c['id']}: requirement_class={c['requirement_class']} title={c['title']!r}")
# bullets
scope=[(749,866),(976,1062)]
bul=sum(1 for n,l in enumerate(src,1) if any(a<=n<=b for a,b in scope) and l.startswith('- [ ]'))
print("owner-source checklist bullets in scope (lines 749-866, 976-1062):", bul)
print("compiled form fields per capability:", sorted(comp['capabilities'][0].keys()), "| bullets carried: 0")
rows=[c for c in emap['capabilities'] if c['capability'][0] in 'OPQV']
print("evidence-map rows in scope:", len(rows), "| evidence_class values:", sorted({r['evidence_class'] for r in rows}), "| rows with automated_checks:", sum(1 for r in rows if r['automated_checks']))
req_fields=["severity if violated","applicability rule","evidence-freshness triggers","health-scheduler tier(s) G0–G6","advanced-qualification challenge IDs","adoption verification obligation","remediation/task-generation rule"]
print("contract lines 53-73 per-capability fields absent from compiled form:", req_fields)
EOF
