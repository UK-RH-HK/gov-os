#!/usr/bin/env bash
# ACT-STOP-IDLE-1's rehearsal: apply.sh check|apply|undo in a clone of w2/integrate, the live files hashed before and
# after. Reads the live /proc, the CTO session's task and agent folders and the dispatcher's status (read only);
# writes only under ~/gov-os-runs/STOP-IDLE-1-rehearsal. Output: rehearsal.log beside this file.
set -u
A=$(cd "$(dirname "$0")" && pwd)
LIVE=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$LIVE/.gov-runtime/scratch/orchestrator
R=/home/usain/gov-os-runs/STOP-IDLE-1-rehearsal
C=$R/repo
CO=$C/.gov-runtime/scratch/orchestrator
FAILS=0
ok() { echo "  ok: $*"; }
bad() { echo "  FAIL: $*"; FAILS=$((FAILS + 1)); }
expect() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
live_hashes() {
  for f in .claude/settings.local.json .claude/settings.json .claude/hooks/pretooluse.py .claude/hooks/bash_writes.py \
           .claude/hooks/role_reads.py governance/project/path-map.yaml \
           governance/project/orchestration/tools/stop_waiter_check.py \
           governance/project/orchestration/tools/permission_request.py \
           governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py \
           .gov-runtime/scratch/orchestrator/log/stop-idle.log .gov-runtime/scratch/orchestrator/log/stop-idle-state.json \
           .gov-runtime/scratch/orchestrator/log/cto-session.txt; do
    if [ -e "$LIVE/$f" ]; then echo "$(sha256sum "$LIVE/$f" | cut -c1-64)  $f"; else echo "absent  $f"; fi
  done
}
SID=$(cat "$ORCH/log/cto-session.txt")
TRANSCRIPT=/home/usain/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/$SID.jsonl
echo "ACT-STOP-IDLE-1 rehearsal $(date '+%Y-%m-%d %H:%M:%S'); live HEAD $(git -C "$LIVE" rev-parse --short=9 HEAD)"

echo "1. The live files before"
live_hashes > "$R.live-before.txt" 2>/dev/null || { mkdir -p "$(dirname "$R")"; live_hashes > "$R.live-before.txt"; }
sed 's/^/  /' "$R.live-before.txt"
git -C "$LIVE" status --porcelain > "$R.git-before.txt"

echo "2. The clone"
rm -rf -- "$R"; mkdir -p "$R"
git clone -q --no-hardlinks "$LIVE" "$C" && git -C "$C" checkout -q "$(git -C "$LIVE" rev-parse HEAD)"
cp -p "$LIVE/.claude/settings.local.json" "$C/.claude/settings.local.json"
mkdir -p "$CO/log" "$CO/dispatch" "$CO/drafts/stop-idle"
cp -p "$ORCH/log/cto-session.txt" "$CO/log/"
cp -p "$ORCH/dispatch/status.json" "$CO/dispatch/"
cp -p "$A/apply.sh" "$A/stop_idle_check.py" "$A/test_stop_idle_check.py" "$A/settings_edit.py" "$CO/drafts/stop-idle/"
CA=$CO/drafts/stop-idle
ok "clone at $(git -C "$C" rev-parse --short=9 HEAD); its settings.local.json $(sha256sum "$C/.claude/settings.local.json" | cut -c1-12)"
run() { STOPIDLE_REPO=$C bash "$CA/apply.sh" "$@"; }
waiter_tests() { (cd "$C" && python3 -m pytest -q -p no:cacheprovider tests/unit/orchestration/test_stop_waiter_check.py 2>&1 | tail -1 | sed "s/ in [0-9.]*s//"); }
waiter_cmd() { python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print([h["command"] for e in d["hooks"]["Stop"] for h in e["hooks"] if "stop_waiter_check.py" in h["command"]][0])' "$C/.claude/settings.local.json"; }
IN=$R/in-cto.json
printf '{"session_id": "%s", "transcript_path": "%s", "stop_hook_active": false, "hook_event_name": "Stop"}\n' "$SID" "$TRANSCRIPT" > "$IN"

echo "3. Before apply: the inbox waiter's hook and its tests"
W_BEFORE=$(waiter_tests); echo "  waiter tests: $W_BEFORE"
W_CMD_BEFORE=$(waiter_cmd)
W_OUT_BEFORE=$(bash -c "$W_CMD_BEFORE" < "$IN"; echo "rc=$?"); echo "  waiter hook on the CTO's input: '$W_OUT_BEFORE'"

echo "4. check, then apply, then check and apply again"
run check; RC=$?; expect "check exits 0 in state old" "[ $RC = 0 ]"
run apply; RC=$?; expect "apply exits 0" "[ $RC = 0 ]"
OUT=$(run check 2>&1); echo "$OUT" | sed 's/^/    /'; expect "check now reads state applied" 'grep -q "state: applied" <<< "$OUT"'
OUT=$(run apply 2>&1); expect "a second apply: already applied" 'grep -q "already applied" <<< "$OUT"'

echo "5. The clone's settings after apply"
python3 -I "$CA/settings_edit.py" verify "$LIVE/.claude/settings.local.json" "$C/.claude/settings.local.json"; RC=$?
expect "only the idle check's entry added (against the live file's bytes)" "[ $RC = 0 ]"
LIVE_EXPECT=$(python3 -I "$CA/settings_edit.py" expect "$LIVE/.claude/settings.local.json" "$LIVE")
expect "the same edit on the live bytes with the live path gives the pinned d715292711a2… (computed, not written)" \
  '[ "$LIVE_EXPECT" = d715292711a2c38fe7ea3830df3c1000b001c7348876f74902fd683981d98624 ]'

echo "6. After apply: the inbox waiter unaffected"
W_AFTER=$(waiter_tests); echo "  waiter tests: $W_AFTER"
expect "waiter tests the same before and after" '[ "$W_BEFORE" = "$W_AFTER" ] && grep -q "6 passed" <<< "$W_AFTER"'
expect "the waiter's command byte-identical" '[ "$(waiter_cmd)" = "$W_CMD_BEFORE" ]'
W_OUT_AFTER=$(bash -c "$W_CMD_BEFORE" < "$IN"; echo "rc=$?")
expect "the waiter's answer on the same input unchanged ('$W_OUT_AFTER')" '[ "$W_OUT_AFTER" = "$W_OUT_BEFORE" ]'

echo "7. The installed hook end to end, through its settings command, on the live state (read only)"
CMD=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print([h["command"] for e in d["hooks"]["Stop"] for h in e["hooks"] if "stop_idle_check.py" in h["command"]][0])' "$C/.claude/settings.local.json")
cp -p "$ORCH/dispatch/status.json" "$CO/dispatch/"
T0=$(date +%s%N); ANS=$(bash -c "$CMD" < "$IN"); RC=$?; T1=$(date +%s%N)
echo "  answer: '${ANS}' rc=$RC in $(( (T1 - T0) / 1000000 )) ms"
echo "  log: $(tail -1 "$CO/log/stop-idle.log" | cut -c1-400)"
expect "the CTO's session now: let through while its agents and workers run, exit 0" \
  '[ $RC = 0 ] && tail -1 "$CO/log/stop-idle.log" | grep -q "	through	running: "'
ANS=$(echo '{"session_id": "someone-else"}' | bash -c "$CMD"; echo "rc=$?")
expect "another session: no answer, exit 0" '[ "$ANS" = "rc=0" ]'
echo "  7b. The same command with the live state planted away (no agents, tasks or workers; a fresh open status)"
P=$R/planted; mkdir -p "$P/tasks" "$P/sub"; echo '[]' > "$P/procs.json"
python3 -I - "$CO/dispatch/status.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p))
d.update(lead_count=0, leads=[], jobs=[], pending_launches=[], close_running=False, land_running=False,
         gate_open=True, disk_open=True, admit=True)
d.setdefault("forecast", {}).setdefault("lead", {})["ok"] = True
json.dump(d, open(p, "w"))
PY
rm -f "$CO/log/stop-idle-state.json"
ENVP="GOV_STOPIDLE_TASKS=$P/tasks GOV_STOPIDLE_SUBAGENTS=$P/sub GOV_STOPIDLE_PROC=$P/procs.json GOV_STOPIDLE_PIDGLOBS="
ANS=$(env $ENVP bash -c "$CMD" < "$IN"); RC=$?
echo "  answer: $(cut -c1-600 <<< "$ANS")"
expect "idle with the live DECIDED-NOT-DONE's open items: block, naming them" \
  '[ $RC = 0 ] && grep -q "\"decision\": \"block\"" <<< "$ANS" && grep -q "#30 W2-56" <<< "$ANS"'
ANS=$(env $ENVP bash -c "$CMD" < "$IN"); echo "  the second stop: $(cut -c1-200 <<< "$ANS")"
expect "the second stop of the same turn: let through, named" 'grep -q "second stop this turn" <<< "$ANS"'
python3 -I - "$CO/dispatch/status.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["gate_open"] = False; d["gate"] = "SHUT (planted)"; json.dump(d, open(p, "w"))
PY
rm -f "$CO/log/stop-idle-state.json"
ANS=$(env $ENVP bash -c "$CMD" < "$IN"); echo "  gate shut: $(cut -c1-200 <<< "$ANS")"
expect "the gate shut: let through, named" 'grep -q "let through: the gate shut (SHUT (planted))" <<< "$ANS"'
mv "$C/governance/project/orchestration/packages/DECIDED-NOT-DONE.md" "$R/DND.aside"
python3 -I - "$CO/dispatch/status.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["gate_open"] = True; json.dump(d, open(p, "w"))
PY
ANS=$(env $ENVP bash -c "$CMD" < "$IN"); RC=$?; echo "  DECIDED-NOT-DONE missing: $(cut -c1-220 <<< "$ANS")"
expect "a parse error: named, not a block, exit 0, logged" \
  '[ $RC = 0 ] && grep -q "could not run" <<< "$ANS" && tail -1 "$CO/log/stop-idle.log" | grep -q "	error	"'
mv "$R/DND.aside" "$C/governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
mv "$C/governance/project/orchestration/tools/stop_idle_check.py" "$R/hook.aside"
ANS=$(bash -c "$CMD" < "$IN" 2>&1); RC=$?
expect "the hook file missing: exit 1 (a non-blocking error Claude Code shows), never 2: '$ANS'" '[ $RC = 1 ]'
mv "$R/hook.aside" "$C/governance/project/orchestration/tools/stop_idle_check.py"
cp -p "$ORCH/dispatch/status.json" "$CO/dispatch/"

echo "8. Planted faults refused"
cp -p "$CA/stop_idle_check.py" "$R/hook.keep"; echo "# edited after review" >> "$CA/stop_idle_check.py"
OUT=$(run check 2>&1); expect "an edit after review: check refuses" 'grep -q "REFUSED: stop_idle_check.py is not the reviewed file" <<< "$OUT"'
cp -p "$R/hook.keep" "$CA/stop_idle_check.py"

echo "9. undo"
run undo; RC=$?; expect "undo exits 0" "[ $RC = 0 ]"
expect "settings back to the live bytes (2b8909d236b7…)" \
  '[ "$(sha256sum "$C/.claude/settings.local.json" | cut -c1-64)" = 2b8909d236b70f8cef97eb23d5023b151dbc05e9ec879a189caee70bfb33d477 ]'
expect "the two files removed (untracked in the clone)" \
  '[ ! -e "$C/governance/project/orchestration/tools/stop_idle_check.py" ] && [ ! -e "$C/tests/unit/orchestration/test_stop_idle_check.py" ]'
expect "the clone's tree clean again" '[ -z "$(git -C "$C" status --porcelain)" ]'
OUT=$(run check 2>&1); expect "check reads state old again" 'grep -q "state: old" <<< "$OUT"'
cp -p "$C/.claude/settings.local.json" "$R/s.keep"
python3 -I -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["env"]["X"]="1"; open(p,"w").write(json.dumps(d,indent=2)+"\n")' "$C/.claude/settings.local.json"
OUT=$(run apply 2>&1); expect "a settings file changed since the rehearsal: apply refuses" 'grep -q "REFUSED: .*re-rehearse" <<< "$OUT"'
cp -p "$R/s.keep" "$C/.claude/settings.local.json"
W_UNDO=$(waiter_tests); expect "the waiter's tests after undo: $W_UNDO" '[ "$W_UNDO" = "$W_BEFORE" ]'

echo "10. The classifier's vote (governance/project/operator/act_class.py, read only), two manifests"
B=$R/bundle; mkdir -p "$B/before/repo/.claude" "$B/after/repo/.claude" \
  "$B/after/repo/governance/project/orchestration/tools" "$B/after/repo/tests/unit/orchestration"
cp -p "$LIVE/.claude/settings.local.json" "$B/before/repo/.claude/"
cp -p "$LIVE/.claude/settings.local.json" "$B/after/repo/.claude/"
python3 -I "$A/settings_edit.py" add "$B/after/repo/.claude/settings.local.json" "$LIVE" > /dev/null
cp -p "$A/stop_idle_check.py" "$B/after/repo/governance/project/orchestration/tools/"
cp -p "$A/test_stop_idle_check.py" "$B/after/repo/tests/unit/orchestration/"
cp -p "$A/apply.sh" "$B/apply.sh"
for which in settings-only full; do
  python3 -I - "$B" "$which" <<'PY'
import hashlib, json, sys
b, which = sys.argv[1], sys.argv[2]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t = [{"root": "repo", "path": ".claude/settings.local.json", "before": h(f"{b}/before/repo/.claude/settings.local.json"),
      "after": h(f"{b}/after/repo/.claude/settings.local.json")}]
if which == "full":
    for p in ("governance/project/orchestration/tools/stop_idle_check.py", "tests/unit/orchestration/test_stop_idle_check.py"):
        t.append({"root": "repo", "path": p, "before": None, "after": h(f"{b}/after/repo/{p}")})
json.dump({"id": "ACT-STOP-IDLE-1", "touched": t, "commands": []}, open(f"{b}/manifest.json", "w"))
PY
  V=$(python3 "$LIVE/governance/project/operator/act_class.py" "$B")
  echo "  $which: $(python3 -I -c 'import json,sys; v=json.loads(sys.argv[1]); print(v["class"], "|", [(f["path"], f["class"], f["row"]) for f in v["files"]], "| hits", [(x["kind"], x["class"]) for x in v["hits"]])' "$V")"
done

echo "11. The live files after"
live_hashes > "$R.live-after.txt"
if cmp -s "$R.live-before.txt" "$R.live-after.txt"; then ok "the live files hash as before (13 paths, the targets and the hook's log still absent)"; else bad "the live files changed:"; diff "$R.live-before.txt" "$R.live-after.txt"; fi
git -C "$LIVE" status --porcelain > "$R.git-after.txt"
if cmp -s "$R.git-before.txt" "$R.git-after.txt"; then ok "the live tree's git status unchanged"; else echo "  note: the live tree's git status moved (other sessions' work): $(diff "$R.git-before.txt" "$R.git-after.txt" | grep -c '^[<>]') lines"; fi
echo "  guard suites: not run, no guard file touched (.claude/hooks/**, the path map and the guard's code hash as before)"
echo "RESULT: $FAILS failure(s)"
exit "$FAILS"
