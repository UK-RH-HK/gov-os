#!/usr/bin/env bash
# Gamma held-out probe: E3 (typed A2A handoffs) and E4 (concurrency / task claims).
# Contract v3 E3 (:377-385): seven typed return elements that persist beyond conversation lifetime.
# Contract v3 E4 (:387-392): claimable units, collision detection, survival of derived-memory rebuild,
# governed stale-claim recovery, parallelism only where dependency/mutation constraints permit.
. "$(dirname "$0")/lib.sh"
newproj e34 --provision >/dev/null

T1=$(g orchestrator task create --class documentation --objective "first unit of work" --allowed "product/a/**" | jget "r['id']")
T2=$(g orchestrator task create --class documentation --objective "second unit of work" --allowed "product/d/**" | jget "r['id']")
T3=$(g orchestrator task create --class documentation --objective "disjoint unit of work" --allowed "product/b/**" | jget "r['id']")
for t in $T1 $T2 $T3; do g orchestrator task status "$t" READY >/dev/null; done

# --- E3 b1-b7: the typed return contract ---------------------------------------------------------
req=$(python3 -c "
import json
d=json.load(open('$PROJ/governance/kernel/schemas/worker-return.schema.json'))
need=['work_completed','files_changed','evidence','tests','discoveries','risks','lessons','proposed_decisions','unresolved','recommended_next_action']
miss=[x for x in need if x not in (d.get('required') or [])]
print(','.join(miss) or 'none')")
check "$req" "none" "E3 b1-b7: every typed return element is REQUIRED by the worker-return contract"

H=$(g orchestrator handoff create --to-role backend-engineer --task "$T1" | jget "r['id']")
check "${H:0:4}" "HND-" "E3: a typed handoff is created ($H)"
cat > "$LAB/ret.json" <<'J'
{"task":"T","status":"success","work_completed":"did the unit of work","files_changed":["product/a/x.txt"],
 "evidence":["product/a/x.txt written"],"tests":{"status":"not_applicable_with_reason","reason":"no product test configured"},
 "discoveries":["an undocumented assumption"],"risks":["the assumption may not hold"],
 "lessons":["record assumptions in the spec"],"proposed_decisions":["D: record assumptions"],
 "unresolved":["confirm the assumption"],"recommended_next_action":"confirm the assumption"}
J
python3 -c "
import json;d=json.load(open('$LAB/ret.json'));d['task']='$T1';json.dump(d,open('$LAB/ret.json','w'))"
r=$(g backend-engineer handoff return "$H" --file "$LAB/ret.json")
check "$(printf '%s' "$r" | jget "r['status']")" "RETURNED" "E3: a typed return is accepted and recorded"
# a lesson/proposed decision in the return becomes a governed (PROVISIONAL) record, not authority
check "$(printf '%s' "$r" | jget "'yes' if r['lessons_created'] else 'no'")" "yes" "E3 b5: a lesson in the return becomes a governed PROVISIONAL lesson record"

# persistence beyond the conversation: a brand-new process, a different session, reads every element
persisted=$(g orchestrator handoff return "$H" --file "$LAB/ret.json" >/dev/null 2>&1; python3 -c "
import yaml,glob
f=glob.glob('$PROJ/spec/**/$H.yaml',recursive=True)[0]
d=yaml.safe_load(open(f))['return']
need=['work_completed','files_changed','evidence','tests','discoveries','risks','lessons','proposed_decisions','unresolved','recommended_next_action']
print(','.join(x for x in need if x not in d) or 'all')")
check "$persisted" "all" "E3: every returned element persists in the governed record after the session ends"

# the same schema-valid worker return is usable as the task-close receipt (S0-W5-01)
python3 -c "
import json,yaml
d=json.load(open('$LAB/ret.json'))
h=yaml.safe_load(open([p for p in __import__('glob').glob('$PROJ/spec/**/$H.yaml',recursive=True)][0]))
d['context_packet_hash']=h['inputs']['context_packet_hash']
for k in ['inputs_consumed','outputs_produced','requirements_implemented','scenarios_implemented','features_implemented','decisions_applied','constraints_applied','acceptance_evidence','deviations']:
    d.setdefault(k,[])
json.dump(d,open('$LAB/ret-close.json','w'))"
g orchestrator task claim "$T1" >/dev/null
g memory-engineer rebuild-memory --incremental >/dev/null
cl=$(g orchestrator task close "$T1" --report "$LAB/ret-close.json")
code=$(printf '%s' "$cl" | jget "'OK' if d.get('ok') else d['error']['code']")
if [ "$code" = "OK" ]; then ok "E3/W5: a schema-valid worker return is accepted as the task-close receipt"
else bad "E3/W5: a schema-valid worker return is not accepted as the task-close receipt ($code)"; fi

# --- E4 b1: sessions/worktrees/tasks can be claimed ------------------------------------------------
c=$(GOV_SESSION=s-A g orchestrator task claim "$T2")
check "$(printf '%s' "$c" | jget "'yes' if d.get('ok') else 'no'")" "yes" "E4 b1: a task is claimed by a session"
iso=$(g orchestrator claims list | jget "','.join(sorted(k for k in (r[0] if isinstance(r,list) else r).keys() if k in ('worktree','git_dir','branch','head','scope','session_id')))")
check "$iso" "branch,git_dir,head,scope,session_id,worktree" "E4 b1/b3: a claim records its session, worktree and mutation scope"

# --- E4 b2: claim collision is detected (including truly concurrent claimants) -----------------------
c2=$(GOV_SESSION=s-B g orchestrator task claim "$T2" | jget "d['error']['code']")
check "$c2" "TASK_CLAIMED" "E4 b2: a second session's claim of a held task is refused"

# 8 concurrent claimants of one fresh task: exactly one may win
TC=$(g orchestrator task create --class documentation --objective "contended" --allowed "product/c/**" | jget "r['id']")
g orchestrator task status "$TC" READY >/dev/null
for i in 1 2 3 4 5 6 7 8; do
  ( cd "$PROJ" && GOV_SESSION="race-$i" "$GOV" --role orchestrator --json task claim "$TC" > "$LAB/race-$i.json" 2>&1 ) &
done
wait
won=$(python3 -c "
import json,glob
w=[f for f in glob.glob('$LAB/race-*.json') if json.load(open(f)).get('ok')]
print(len(w))")
check "$won" "1" "E4 b2: exactly one of 8 concurrent claimants wins (atomic claim)"

# --- E4 b3: claims survive derived-memory rebuild ---------------------------------------------------
before=$(g orchestrator claims list | jget "len(r)")
g memory-engineer rebuild-memory >/dev/null 2>&1
after=$(g orchestrator claims list | jget "len(r)")
check "$after" "$before" "E4 b3: every claim survives a full derived-memory rebuild ($before before, $after after)"

# --- E4 b4: stale claims have governed recovery ------------------------------------------------------
sw=$(g orchestrator claims sweep | jget "'ok' if d.get('ok') else d['error']['code']")
check "$sw" "ok" "E4 b4: a governed stale-claim recovery operation exists and runs (claims sweep)"
# force a claim to be expired, then show the sweep recovers it and the task becomes claimable again
python3 - <<PY
import sqlite3,glob,os
db=None
for c in ['$PROJ/.governance-state/claims.db','$XDG_STATE_HOME/governance-os/machine/claims.db']:
    if os.path.exists(c): db=c
if db:
    con=sqlite3.connect(db); con.execute("UPDATE claims SET expires_at='2000-01-01T00:00:00Z' WHERE task_id='$T2'"); con.commit()
    print('expired')
else: print('no claims db found')
PY
g orchestrator claims sweep >/dev/null
reclaim=$(GOV_SESSION=s-C g orchestrator task claim "$T2" | jget "'yes' if d.get('ok') else d['error']['code']")
check "$reclaim" "yes" "E4 b4: after governed recovery an expired claim no longer blocks the task"

# --- E4 b5: parallel work only where dependency/mutation constraints permit ---------------------------
# T3 has a disjoint mutation scope: a second session may hold it in parallel
par=$(GOV_SESSION=s-D g orchestrator task claim "$T3" | jget "'yes' if d.get('ok') else d['error']['code']")
check "$par" "yes" "E4 b5: a task with a disjoint mutation scope is claimable in parallel"
# a task whose scope overlaps a live claim is refused
TOV=$(g orchestrator task create --class documentation --objective "overlapping scope" --allowed "product/b/**" | jget "r['id']")
g orchestrator task status "$TOV" READY >/dev/null
ov=$(GOV_SESSION=s-E g orchestrator task claim "$TOV" | jget "d['error']['code'] if not d.get('ok') else 'ALLOWED'")
check "$ov" "CLAIM_SCOPE_CONFLICT" "E4 b5: a parallel claim whose mutation scope overlaps a live claim is refused"
# a dependency-blocked task is neither runnable nor claimable (BC-P2-16)
TD=$(g orchestrator task create --class documentation --objective "blocked by a dependency" --deps "$TOV" | jget "r['id']")
g orchestrator task status "$TD" READY >/dev/null
dep=$(GOV_SESSION=s-F g orchestrator task claim "$TD" | jget "d['error']['code'] if not d.get('ok') else 'ALLOWED'")
check "$dep" "TASK_NOT_RUNNABLE" "E4 b5: a dependency-blocked task cannot be claimed even when its stored status says READY"
summary
