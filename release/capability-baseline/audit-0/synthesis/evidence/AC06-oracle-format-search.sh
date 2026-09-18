#!/usr/bin/env bash
# P2-AR-0007 AC-6: is there any machine-checkable Qualification Oracle format (V1-V4) on the candidate?
# Independent of epsilon-r: searches tracked files at HEAD (excluding the audit evidence trees, the owner source, its
# canonical import and the V8.2 UI), lists schemas, and checks the gate register. Run from the worktree root.
set -u
EXCL='^(release/capability-baseline/|release/orchestration/phase-2/(AGENT_RUNS|HANDOFFS)/|Governance_OS_Capability_Acceptance_Contract_v3.md|framework/contracts/source/|docs/generated/)'
echo "## tracked files whose NAME mentions oracle/fault/qualif/scoring (outside audit evidence):"
git ls-files | grep -Ei 'oracle|fault[-_]?manifest|qualif|scoring' | grep -Ev "$EXCL" || echo "  <none>"
echo "## tracked files whose CONTENT defines V1-V4 field identifiers (snake/kebab/camel):"
for pat in 'fault[_-]?id' 'hidden[_-]?authoritative[_-]?truth' 'injected[_-]?repository[_-]?state' 'expected[_-]?detection' 'expected[_-]?governed[_-]?action' 'forbidden[_-]?outcomes' 'expected[_-]?target[_-]?path' 'must[_-]?be[_-]?indexed' 'expected[_-]?retrieval[_-]?results' 'detection[_-]?recall' 'impact[_-]?map[_-]?accuracy' 'path[_-]?map[_-]?accuracy'; do
  hits=$(git grep -lEi "$pat" HEAD -- . | sed 's/^HEAD://' | grep -Ev "$EXCL" | tr '\n' ' ')
  printf '  %-40s %s\n' "$pat" "${hits:-<none>}"
done
echo "## kernel schemas (framework/schemas) naming oracle/fault/qualification:"; ls framework/schemas | grep -Ei 'oracle|fault|qualif|scor' || echo "  <none>"
echo "## gate register entry:"; grep -n -A3 'GATE-P2-ORACLE-FORMAT' release/orchestration/phase-2/GATES/GATE-REGISTER.yaml
echo "## CLI surface:"; for c in qualify oracle score qualification; do printf '  gov %-14s ' "$c"; target/release/gov "$c" --help >/dev/null 2>&1 && echo "exists" || echo "unrecognised"; done
