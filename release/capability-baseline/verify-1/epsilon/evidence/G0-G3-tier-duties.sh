#!/usr/bin/env bash
# O5 G0 and G3 tier duties on cap2-candidate-1 (P2-AR-0050).
#   ./G0-G3-tier-duties.sh <project-root> <XDG_STATE_HOME> <gov-binary>
# G3: does `handoff create` perform the claims/decisions/gates/checkpoint-freshness duty at its trigger?
# G0: is every privileged/mutating command guarded?
set -u
D="$1"; export XDG_STATE_HOME="$2"; G="$3"; R=(--root "$D" --session s --role orchestrator)
echo "### G3 — handoff.create runs the G3 tier and judges input currency"
# a task that declares a decision as an input; deliver its packet, THEN change that decision
T=$("$G" --json "${R[@]}" task create --objective "G3 freshness" --title "G3f" --class governance \
      --allowed "docs/g3" --fields '{"decisions":["D-G3"]}' | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
"$G" --json "${R[@]}" task status "$T" READY >/dev/null
"$G" --json --root "$D" --session w --role change-controller task claim "$T" >/dev/null
"$G" --json --root "$D" --session w --role change-controller context compile "$T" >/dev/null
sed -i "s|^chosen_option: .*|chosen_option: OPT-$(date +%s)|" "$D/spec/decisions/D-G3.yaml"
(cd "$D" && git add -A && git commit -q -m "a delivered input changed")
"$G" --json "${R[@]}" rebuild-memory --incremental >/dev/null
"$G" --json --root "$D" --session w --role change-controller handoff create --task "$T" --to-role backend-engineer 2>&1 | python3 -c "
import json,sys; d=json.load(sys.stdin); r=d.get('result') or d['error']
print('health   :', json.dumps(r.get('health')))
print('freshness:', json.dumps(r.get('freshness', {}).get('state')), json.dumps(r.get('stale_inputs'))[:200])
print('policy   :', str(r.get('freshness', {}).get('policy'))[:200])"
echo
echo "### G0 — every privileged/mutating command is guarded (census under FREEZE_WRITES)"
"$G" --json "${R[@]}" freeze-writes >/dev/null
for c in "task create --objective x --title x --class governance --allowed docs/x" \
         "task status TASK-0001 READY" "gate create --question q --fields {}" \
         "adapters generate" "memory heldout-starter" "adopt baseline" \
         "telemetry emit --name x --attrs {}" "plugins list"; do
  printf '%-58s %s\n' "$c" "$("$G" --json "${R[@]}" $c 2>&1 | python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception: print('NO_JSON'); raise SystemExit
print('OK' if d['ok'] else (d.get('error') or {}).get('code','ERR'))" 2>/dev/null)"
done
"$G" --json "${R[@]}" resume >/dev/null
echo "(telemetry emit and plugins list are machine-local derived state / read-only, allowed by design)"
