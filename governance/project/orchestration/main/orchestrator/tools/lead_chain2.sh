#!/usr/bin/env bash
# RETIRED (DEC-1012, the owner's "a rule broken twice becomes a mechanism"): leads start only through the dispatcher's
# ready list (dispatch/ready.txt, DEC-1007); hand-run chains were started with a trailing & twice (DEC-731). Override
# only for a test: GOV_CHAIN_OVERRIDE=1.
[ "${GOV_CHAIN_OVERRIDE:-}" = 1 ] || { echo "lead_chain2.sh is retired: add the ticket to .gov-runtime/scratch/orchestrator/dispatch/ready.txt (DEC-1012)" >&2; exit 2; }
# Starts queued ticket leads in order with no fixed ceiling (owner, DEC-942): each start waits until the measured
# gate is open (tools/gate_check.py), no ticket is ready to close and waiting for its close to start (CLOSE-PENDING,
# item 4), and it is not between 00:30 and 05:30 (item 5). Each lead is started detached (setsid -f), so stopping
# this chain stops no lead; the chain then waits until the new lead is counted (at most 10 minutes), so the next
# gate check sees its memory. Usage: lead_chain.sh <spec file>; each spec line: <W2> <ticket> <brief> <log file>
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
running() { pgrep -f -c 'GOV_ROLE":"orchestrator","GOV_TICKET' ; }
held() {
  # DEC-961: no hold for a waiting close and no night window; the gate's capacity alone decides.
  gate=$(python3 "$ORCH/tools/gate_check.py") || { echo "$gate"; return 0; }
  return 1
}
while read -r w2 id brief logf; do
  [ -z "$w2" ] && continue
  case "$w2" in \#*) continue ;; esac
  last=""
  while why=$(held); do
    [ "$why" != "$last" ] && echo "$(date '+%F %T') $w2 waits: $why" >&2
    last=$why; sleep 60
  done
  before=$(running)
  echo "$(date '+%F %T') starting $w2 ($id), $before lead(s) running" >&2
  setsid -f bash "$ORCH/tools/launch_when_gate_opens.sh" "$w2" "$id" "$brief" "$logf" \
    2> "$ORCH/log/$w2-$(date +%Y%m%d-%H%M)-launch.txt" < /dev/null
  sleep 120  # stagger (owner, 2026-10-29: five starts at once spiked the load to 155)
  n=0
  until [ "$(running)" -gt "$before" ] || [ "$n" -ge 10 ]; do sleep 60; n=$((n + 1)); done
done < "$1"
echo "$(date '+%F %T') chain done" >&2
