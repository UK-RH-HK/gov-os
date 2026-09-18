#!/usr/bin/env bash
# P2-AR-0010 — E4 Concurrency/task claims (Contract v3 lines 387-392).
source "$(dirname "$0")/lib.sh"
R=$(mkproj e4)
echo "project: $R"
mk() { g "$R" orchestrator S0 task create --id "$1" --class documentation --objective "$1" --status READY "${@:2}" >/dev/null; }
release_all() { for t in $(g "$R" orchestrator S0 claims list | python3 -c 'import json,sys;[print(c["task_id"]) for c in json.load(sys.stdin)["result"]]'); do g "$R" orchestrator S0 task release "$t" --force >/dev/null; done; }
claims() { g "$R" orchestrator S0 claims list | python3 -c 'import json,sys;[print("   ",c["task_id"],c["session_id"],c["role"],"expires",c["expires_at"],"expired" if c["expired"] else "") for c in json.load(sys.stdin)["result"]]'; }

hdr "E4.b1 sessions claim tasks (claim record: task, session, role, lease)"
mk TASK-A --allowed 'docs/**'
g "$R" backend-engineer S-alpha task claim TASK-A | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  claim:",{k:r[k] for k in ["task_id","session_id","role","claimed_at","expires_at"]},"baseline files:",r["baseline"]["files"])'
echo "  task status now: $(grep task_status "$R/spec/tasks/TASK-A.yaml")"
echo "  claim store: $(ls "$R/.governance-runtime/" | grep claims)"
cmd "is there any worktree/branch identity in a claim? (schema of the claims table)"
python3 -c 'import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);print("  ",c.execute("select sql from sqlite_master where name=\"claims\"").fetchone()[0])' "$R/.governance-runtime/claims.db"
cmd "the same session re-claiming renews its own lease"
gq "$R" backend-engineer S-alpha task claim TASK-A

hdr "E4.b2 claim collision is detected (sequential)"
cmd "a second session claims TASK-A while S-alpha holds it"
gq "$R" frontend-engineer S-beta task claim TASK-A
cmd "the second session tries to close / release it without --force"
rep=$(report_file "$R" b "x" "" passed)
gq "$R" frontend-engineer S-beta task close TASK-A --report "$rep"
gq "$R" frontend-engineer S-beta task release TASK-A

hdr "E4.b2.race claim collision under true concurrency (3 sessions launched simultaneously per trial)"
release_all
TRIALS=${TRIALS:-15}
multi=0; single=0; zero=0
for i in $(seq 1 $TRIALS); do
  t="TASK-RACE$i"; mk "$t"
  for s in X Y Z; do ( g "$R" backend-engineer "S-$s$i" task claim "$t" > "/tmp/e4race.$$.$s" 2>&1; echo $? > "/tmp/e4race.$$.$s.rc" ) & done
  wait
  ok=0; codes=""
  for s in X Y Z; do rc=$(cat /tmp/e4race.$$.$s.rc); [ "$rc" = 0 ] && ok=$((ok+1)); codes="$codes $s:$(python3 -c 'import json,sys
try:
  e=json.load(open(sys.argv[1])); print("OK" if e["ok"] else e["error"]["code"])
except Exception as x: print("NONJSON")' /tmp/e4race.$$.$s)"; done
  holder=$(g "$R" orchestrator S0 claims list | python3 -c 'import json,sys;print([c["session_id"] for c in json.load(sys.stdin)["result"] if c["task_id"]==sys.argv[1]])' "$t")
  printf '  trial %2d: successes=%d [%s] final holder=%s\n' "$i" "$ok" "$codes" "$holder"
  if [ $ok -gt 1 ]; then multi=$((multi+1)); elif [ $ok = 1 ]; then single=$((single+1)); else zero=$((zero+1)); fi
  release_all
done
echo "  SUMMARY: trials=$TRIALS  more-than-one-session-told-it-holds-the-claim=$multi  exactly-one=$single  none=$zero"
rm -f /tmp/e4race.$$.*

hdr "E4.b3 claims survive derived-memory rebuild"
mk TASK-B
gq "$R" backend-engineer S-gamma task claim TASK-B
echo "  before:"; claims
cmd "delete the derived index (state.db) and rebuild; then gov memory rebuild (full)"
rm -f "$R/.governance-runtime/state.db"*
gq "$R" orchestrator S0 rebuild-memory
gq "$R" orchestrator S0 memory rebuild
echo "  after:"; claims
cmd "the claim still binds: another session is refused"
gq "$R" frontend-engineer S-delta task claim TASK-B
cmd "claims live in .governance-runtime/claims.db: a fresh clone (no runtime dir) has no claims (derived runtime is machine-local)"
( cd "$R" && git add -A && git commit -qm c )
C=$PROBES/e4-clone; rm -rf "$C"; git clone -q "$R" "$C"
g "$C" orchestrator S0 claims list | python3 -c 'import json,sys;print("  clone claims:",json.load(sys.stdin)["result"])'

hdr "E4.b4 stale (expired) claims have governed recovery"
cmd "age S-gamma's lease on TASK-B into the past (simulating a dead session) directly in claims.db"
python3 -c 'import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);c.execute("update claims set expires_at=\"2020-01-01T00:00:00Z\" where task_id=\"TASK-B\"");c.commit()' "$R/.governance-runtime/claims.db"
claims
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  suite concurrency_claims:",r["families"]["concurrency_claims"],[f["message"] for f in r["findings"] if f.get("family")=="concurrency_claims"])'
cmd "sweep by L1 (sweep_claims L3) is refused; recover --dry-run reports; recover (L3) sweeps and records a report"
gq "$R" backend-engineer S-x claims sweep
g "$R" change-controller S-cc recover --dry-run | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  dry-run items:",[i for i in r.get("items",[]) if i.get("kind")=="claims"])'
g "$R" change-controller S-cc recover | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  recover ok=",e["ok"],"actions=",r.get("actions"),"report=",r.get("report"))'
claims
ls "$R/spec/reports" | grep RPT | sed 's/^/  report: /'
cmd "alternatively an expired lease no longer blocks: a new session may take the task"
mk TASK-C; gq "$R" backend-engineer S-eps task claim TASK-C
python3 -c 'import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);c.execute("update claims set expires_at=\"2020-01-01T00:00:00Z\" where task_id=\"TASK-C\"");c.commit()' "$R/.governance-runtime/claims.db"
gq "$R" frontend-engineer S-zeta task claim TASK-C
cmd "force release of a live claim needs L3 (force_release_task)"
mk TASK-D; gq "$R" backend-engineer S-eta task claim TASK-D
gq "$R" product-spec-agent S-theta task release TASK-D --force
gq "$R" change-controller S-cc task release TASK-D --force

hdr "E4.b5 parallel work only where dependency / mutation constraints permit"
release_all
cmd "dependency: TASK-DEP-B depends on open TASK-DEP-A; both stored READY"
mk TASK-DEP-A; mk TASK-DEP-B --deps TASK-DEP-A
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  dag: TASK-DEP-B blocked:",[b["reasons"] for b in r["blocked"] if b["task"]=="TASK-DEP-B"])'
cmd "a session claims TASK-DEP-B directly (task claim checks only the stored task_status)"
gq "$R" backend-engineer S-dep task claim TASK-DEP-B
echo "  TASK-DEP-B status now: $(grep task_status "$R/spec/tasks/TASK-DEP-B.yaml")"
cmd "and closes it while its dependency is still open"
rep=$(report_file "$R" dep "did dependent work before its dependency" "" not_applicable_with_reason)
g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
gq "$R" backend-engineer S-dep task close TASK-DEP-B --report "$rep"
echo "  TASK-DEP-A status: $(grep task_status "$R/spec/tasks/TASK-DEP-A.yaml")  TASK-DEP-B status: $(grep task_status "$R/spec/tasks/TASK-DEP-B.yaml")"
cmd "gov continue --claim never offers a dependency-blocked task (it offers only DAG-runnable ones)"
mk TASK-DEP-C --deps TASK-DEP-A
g "$R" backend-engineer S-cont continue | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  continue offers:",r.get("task"),"parallel:",r.get("parallel_runnable"))'
release_all
cmd "mutation overlap: two READY tasks with the same allowed_paths are claimed concurrently by two sessions"
mk TASK-M1 --allowed 'src/**'; mk TASK-M2 --allowed 'src/**'; ( cd "$R" && git add -A && git commit -qm m )
gq "$R" backend-engineer S-m1 task claim TASK-M1
gq "$R" frontend-engineer S-m2 task claim TASK-M2
echo "// m1" >> "$R/src/lib.rs"; mkdir -p "$R/src/extra"; echo "// m2" > "$R/src/extra/m2.rs"
g "$R" orchestrator S0 rebuild-memory --incremental >/dev/null
cmd "first closer (S-m1, declares src/lib.rs); second closer (S-m2, declares src/extra/m2.rs)"
gq "$R" backend-engineer S-m1 task close TASK-M1 --report "$(report_file "$R" m1 x src/lib.rs passed)"
gq "$R" frontend-engineer S-m2 task close TASK-M2 --report "$(report_file "$R" m2 x src/extra/m2.rs passed)"
echo END
