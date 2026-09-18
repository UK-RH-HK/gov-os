#!/usr/bin/env bash
# P2-AR-0010 — freshness / invalidation (Contract v3 lines 95-111; frozen contract AC-10), for gamma's evidence inputs.
# A green governance-suite record is bound to verification::inputs_hash (governance/kernel, governance/project,
# governance/tests, spec/decisions, framework.lock). Each probe changes one input class and observes whether prior green
# evidence is treated as stale (a governance-touching task can no longer close on it) or the change fails closed.
source "$(dirname "$0")/lib.sh"
R=$(mkproj fresh)
echo "project: $R"
green() { g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null; g "$R" orchestrator S0 audit | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  audit:",r["verdict"],"green=",r["green"],"record=",r["audit"],"inputs_hash=",r["inputs_hash"][:16],[f["message"][:80] for f in r["findings"] if f["severity"] in ("medium","high","critical")])'; }
n=0
release_all() { for t in $(g "$R" orchestrator S0 claims list | python3 -c 'import json,sys;[print(c["task_id"]) for c in json.load(sys.stdin)["result"]]'); do g "$R" orchestrator S0 task release "$t" --force >/dev/null; done; }
probe() { # probe <label> <allowed-csv> <declared-extra-file-or-empty> <mutation-snippet-or-empty>
  n=$((n+1)); local t="TASK-GOV$n"; release_all
  g "$R" orchestrator S0 task create --id "$t" --class governance --objective "touch the overlay ($1)" --status READY --allowed "$2" >/dev/null
  ( cd "$R" && git add -A && git commit -qm "$t" )
  g "$R" backend-engineer S-w$n task claim "$t" >/dev/null
  echo "# $1" >> "$R/governance/project/NOTES.md"          # the task's own governance change
  g "$R" orchestrator S0 adapters generate >/dev/null       # keep derived adapters current so the suite can be green
  green                                                      # green record taken AFTER the task's own change
  if [ -n "$4" ]; then eval "$4"; echo "  input change applied after the green record: $1"; fi
  g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
  local files="governance/project/NOTES.md"; [ -n "$3" ] && files="$files,$3"
  printf '  close %s (declares %s): ' "$t" "$files"
  gq "$R" backend-engineer S-w$n task close "$t" --report "$(report_file "$R" g$n x "$files" passed)"
  ( cd "$R" && git add -A && git commit -qm "after $t" ); release_all
}
hdr "FRESH.0 control: green record taken after the task's own change, no other input change -> close succeeds"
probe "no input change" 'governance/project/**' '' ''
hdr "FRESH.1 project overlay input (E1/F2/F3/F4: TOOL_PERMISSIONS.yaml) changed after the green record"
probe "TOOL_PERMISSIONS.yaml edited" 'governance/project/**' 'governance/project/TOOL_PERMISSIONS.yaml' 'python3 -c "import yaml,sys;p=sys.argv[1];d=yaml.safe_load(open(p));d[\"roles\"][\"research-agent\"].append(\"RUN_TESTS\");yaml.safe_dump(d,open(p,\"w\"),sort_keys=False)" "$R/governance/project/TOOL_PERMISSIONS.yaml"'
hdr "FRESH.2 project skill (F1 input) added after the green record"
probe "project skill added" 'governance/project/**' 'governance/project/skills/SKL-P.yaml' 'mkdir -p "$R/governance/project/skills"; printf "id: SKL-P\nname: p\nversion: 1.0.0\nstatus: ACTIVE\nroles: [backend-engineer]\nmethod:\n  - {step: a}\nvalidation_scenarios:\n  - {id: V1, expect: x}\n" > "$R/governance/project/skills/SKL-P.yaml"'
hdr "FRESH.3 decision record (spec/decisions input) added after the green record"
probe "decision D-0500 added" 'governance/project/**' '' 'printf "{\"id\":\"D-0500\",\"type\":\"decision\",\"title\":\"new decision\",\"status\":\"ACTIVE\",\"chosen_option\":\"x\"}\n" > "$R/spec/decisions/D-0500.yaml"'
hdr "FRESH.4 plugin registry (F4 registration input, governance/generated) changed after the green record"
probe "plugin-registry.json edited" 'governance/project/**' '' 'python3 -c "import json,os,sys;p=sys.argv[1];d=json.load(open(p)) if os.path.exists(p) else {\"schema_version\":\"1.0.0\",\"plugins\":{}};d[\"plugins\"][\"x\"]={\"plugin_id\":\"x\"};json.dump(d,open(p,\"w\"))" "$R/governance/generated/plugin-registry.json"'
python3 -c "import json,sys;p=sys.argv[1];d=json.load(open(p));d['plugins'].pop('x',None);json.dump(d,open(p,'w'))" "$R/governance/generated/plugin-registry.json"; ( cd "$R" && git add -A && git commit -qm unx )
hdr "FRESH.5 feature record (H2/H3/I input; not a suite input — readiness and the DAG are computed live) added after the green record"
probe "feature F-9 added" 'governance/project/**,spec/features/**' 'spec/features/F-9.yaml' 'write_feature "$R" F-9 "$(readiness_json security_privacy \"\")"'
g "$R" orchestrator S0 readiness check F-9 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  live readiness of F-9 right after the change:",r["gaps"],"pre_implementation_ok=",r["pre_implementation_ok"])'
hdr "FRESH.6 kernel policy/taxonomy/roles/command-contract edits (E1/G/H inputs) fail closed immediately"
for f in roles/ROLES.yaml policies/AUTHORITY_POLICY.yaml taxonomy/READINESS_DIMENSIONS.yaml commands/COMMAND_CONTRACT.yaml policies/TOOL_POLICY.yaml; do
  cp "$R/governance/kernel/$f" /tmp/fk.$$.bak; echo "# local edit" >> "$R/governance/kernel/$f"
  printf '  %-36s edited -> task create: ' "$f"; gq "$R" orchestrator S0 task create --class research --objective x | cut -c1-140
  cp /tmp/fk.$$.bak "$R/governance/kernel/$f"
done
echo "# widen" >> "$R/governance/kernel/roles/ROLES.yaml"
g "$R" orchestrator S0 kernel trust | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  kernel trust verified=",r["verified"],"|",r["summary"][:200])'
( cd "$R" && git checkout -q -- governance/kernel )
hdr "FRESH.7 plugin implementation / skill method changes"
echo "  plugin implementation change -> PLUGIN_PIN_MISMATCH: F4-plugins.out section F4.b3/b4"
echo "  project skill method change without version bump -> nothing marked stale at skill level: F1-skills.out section F1.b3"
rm -f /tmp/fk.$$.bak
echo END
