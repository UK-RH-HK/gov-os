#!/usr/bin/env bash
# E-O5-01 — a tier run never executes the 35 doctor checks the catalogue declares at G1 and G5.
# Run against any provisioned, converged project (see heldout/t01_ac5_scheduler.py::provisioned).
#   ./E-O5-01-doctor-tier-gap.sh <project-root> <XDG_STATE_HOME> <gov-binary>
set -u
D="$1"; export XDG_STATE_HOME="$2"; G="$3"
run(){ "$G" --json --root "$D" --session eps --role orchestrator "$@" 2>&1; }
echo "### 1. the catalogue declares D001-D035 at tiers G1 and G5"
run health checks | python3 -c "
import json,sys; d=json.load(sys.stdin)['result']
docs=[c for c in d['checks'] if c['surface']=='doctor']
print('doctor checks in the catalogue :', len(docs))
print('declared tiers                 :', sorted({t for c in docs for t in c['tiers']}))
print('hard-blocking among them       :', len([c for c in docs if c['enforcement']['mode']=='hard-block']))
print('G5 tier membership (declared)  :', len(d['tiers'][5]['checks']), 'checks')"
echo
echo "### 2. a G5 tier run evaluates none of them, and reports the run complete"
run health run --tier G5 --event e-o5-01 | python3 -c "
import json,sys; d=json.load(sys.stdin); r=d.get('result') or d['error']['details']; s=r['summary']
ev=set(s['executed_checks'])|set(s['reused_checks'])
print('executed', s['executed'], 'reused', s['reused'], 'not_evaluated', s['not_evaluated'], 'complete', s['complete'])
print('doctor checks evaluated        :', len([c for c in ev if c.startswith('D0')]))
print('declared at G5 but unevaluated : D001..D035 (35 checks)')"
echo
echo "### 3. gov audit (the G5 full-audit host) does the same"
run audit | python3 -c "
import json,sys; d=json.load(sys.stdin); r=d.get('result') or d['error']['details']; s=r['summary']
ev=set(s['executed_checks'])|set(s['reused_checks'])
print('tier', r['tier'], 'executed', s['executed'], 'reused', s['reused'], 'doctor evaluated', len([c for c in ev if c.startswith('D0')]))"
echo
echo "### 4. consequence: the machine state reads GREEN over stale green evidence"
# bring the repository to a state where the last full run and the last doctor run both passed
run health run --event e-o5-01-settle >/dev/null; run audit >/dev/null
run health run --event e-o5-01-settle2 >/dev/null; run doctor >/dev/null
run health status | python3 -c "
import json,sys; d=json.load(sys.stdin); r=d.get('result') or d['error']['details']
print('baseline             :', r['state'], r['repository']['verdict'], 'current', r['governance_suite_currency']['current'])"
echo "// x $(date +%s)" >> "$D/src/e-o5-01.rs"; (cd "$D" && git add -A && git commit -q -m e-o5-01)
run health run --check health_slos --no-cache --event e-o5-01-partial >/dev/null
run health status | python3 -c "
import json,sys; d=json.load(sys.stdin); r=d.get('result') or d['error']['details']
print('state                :', r['state'])
print('repository verdict   :', r['repository']['verdict'])
print('green record current :', r['governance_suite_currency']['current'])
print('failing checks       :', [c['check'] for c in r['failing_checks']])
print('stale checks         :', len(r['stale_checks']))"
echo
echo "### 5. gov doctor executes them; the same state is then YELLOW"
run doctor >/dev/null
run health status | python3 -c "
import json,sys; d=json.load(sys.stdin); r=d.get('result') or d['error']['details']
print('state                :', r['state'])
print('failing checks       :', [(c['check'], c['max_severity'], c['enforcement']) for c in r['failing_checks']])"
