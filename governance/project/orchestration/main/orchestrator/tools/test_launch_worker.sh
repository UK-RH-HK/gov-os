#!/usr/bin/env bash
# Tests for launch_worker.sh (TPL-3b) in a temporary repository with a stub CLI: a stand-in gov.cli.main (records its
# arguments, its stdin and its folder, prints a claude -p JSON line) and a stand-in gov.launch.launcher (the dry run's
# checks), with stand-in disk gate and tripwire. No real session, no model.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
T=$HERE/launch_worker.sh
W=$(mktemp -d "${TMPDIR:-/tmp}/gov-os-test-launch-worker.XXXXXX")
fails=0
ok() { echo "ok   $1"; }
no() { echo "FAIL $1"; fails=$((fails+1)); }
check() { if eval "$2"; then ok "$1"; else no "$1"; fi; }

R=$W/wt/W2-99   # the worker's tree
mkdir -p "$R/src/gov/cli" "$R/src/gov/launch" "$R/.tickets" "$W/main/.tickets" "$W/common" "$W/trial" "$W/rec" "$W/briefs"
: > "$R/src/gov/__init__.py"; : > "$R/src/gov/cli/__init__.py"; : > "$R/src/gov/launch/__init__.py"
cat > "$R/src/gov/cli/main.py" <<'PY'
import os, sys, time
rec = os.environ["STUB_REC"]
open(os.path.join(rec, "argv"), "w").write(" ".join(sys.argv[1:]) + "\n")
open(os.path.join(rec, "stdin"), "w").write(sys.stdin.read())
open(os.path.join(rec, "cwd"), "w").write(os.getcwd() + "\n")
open(os.path.join(rec, "pythonpath"), "w").write(os.environ.get("PYTHONPATH", "") + "\n")
if os.environ.get("STUB_BREACH"):
    open(os.path.join(os.environ["LAUNCH_TRIAL_DIR"], ".sandbox-trial-" + sys.argv[3]), "w").write("x")
time.sleep(float(os.environ.get("STUB_SLEEP", "0")))
print("gov launch: a launcher line")
print('{"type":"result","is_error":false,"num_turns":3,"session_id":"stub-1","result":"task: stub\\nstatus: DONE"}')
sys.exit(int(os.environ.get("STUB_RC", "0")))
PY
cat > "$R/src/gov/launch/launcher.py" <<'PY'
import os
WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "research", "product-spec")
def _check_cli_args(args):
    open(os.path.join(os.environ["STUB_REC"], "dry_args"), "w").write(" ".join(args) + "\n")
def _check_ticket(root, role, ticket):
    if os.environ.get("STUB_DRY_REFUSE"):
        raise SystemExit(f"gov: refused: ticket '{ticket}' is not in_progress")
def build_settings(root, role, ticket):
    return {"sandbox": {"enabled": not os.environ.get("STUB_FAULT")}}
def sandbox_faults(settings):
    return [] if settings["sandbox"]["enabled"] else ["sandbox.enabled is not true"]
PY
ticket() { printf -- '---\nid: %s\nstatus: %s\nwbs_id: %s\nrole: %s\ntitle: '"'"'a: stub'"'"'\nallowed_paths:\n- src/x/**\n---\n# body\n' "$2" "$3" "$4" "$5" > "$1/.tickets/$2.md"; }
ticket "$R" T-eng in_progress W2-99 engineer
ticket "$R" T-td in_progress W2-99 independent-test-designer
ticket "$R" T-old closed W2-99 engineer
ticket "$R" T-other in_progress W2-98 engineer
git -C "$R" init -q
printf '#!/usr/bin/env bash\necho "disk gate (stub) rc ${STUB_GATE_RC:-0}" >&2\nexit "${STUB_GATE_RC:-0}"\n' > "$W/gate.sh"
cat > "$W/trip.py" <<'PY'
import os, sys
if sys.argv[1] == "snapshot":
    print("{}")
else:
    rc = int(os.environ.get("STUB_TRIP_RC", "0"))
    print('{"changes": []}' if rc == 0 else '{"changes": [{"tree": "x", "change": "head"}]}')
    sys.exit(rc)
PY
printf 'Common rules. Read %s too.\n' "$W/common/EMG-d4b-launched.md" > "$W/common/EMG-common.md"
printf 'Step 0: the sandbox-trial check. Then %s.\n' "$W/common/EMG-common.md" > "$W/common/EMG-d4b-launched.md"
printf '# W2-99 engineer\nRead %s first.\nBuild it.\n' "$W/common/EMG-common.md" > "$W/briefs/W2-99-eng.md"
printf '# W2-99 review\nRead everything; write nothing.\n' > "$W/briefs/W2-99-review.md"
export STUB_REC=$W/rec LAUNCH_MAIN=$W/main LAUNCH_COMMON_DIR=$W/common LAUNCH_DISK_GATE=$W/gate.sh \
  LAUNCH_TRIPWIRE=$W/trip.py LAUNCH_TRIAL_DIR=$W/trial
LOG=$R/.gov-runtime/scratch/lead/log DEST=$R/.gov-runtime/scratch/brief
lw() { rm -f "$W"/rec/*; (cd "$R" && bash "$T" "$@") > "$W/stdout" 2> "$W/stderr"; }

# 1. usage and refusals before anything is written
lw --fg reviewer high "$W/briefs/W2-99-eng.md"; check "not a worker role: exit 2" '[ $? = 2 ]'
lw --fg engineer hard "$W/briefs/W2-99-eng.md"; check "not an effort: exit 2" '[ $? = 2 ]'
lw --fg engineer high "$W/briefs/none.md"; check "no brief: exit 2" '[ $? = 2 ]'
(cd "$W/main" && LAUNCH_TREE=$W/main bash "$T" --fg engineer high "$W/briefs/W2-99-eng.md") > /dev/null 2>&1
check "the main tree is refused: exit 2" '[ $? = 2 ] && [ ! -e "$W/rec/argv" ]'

# 2. an engineer, in the foreground: the launch line, the brief's copy, the log, the summary, the exit file
lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "engineer: exit 0 (the session's)" '[ $rc = 0 ]'
check "engineer: the gov launch line, its own ticket, the CLI arguments" '[ "$(cat "$W/rec/argv")" = "launch engineer T-eng -- -p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits --allowedTools Bash Read Edit Write Grep Glob" ]'
check "engineer: started in the worker's tree, with its own src first" '[ "$(cat "$W/rec/cwd")" = "$R" ] && grep -q "^$R/src" "$W/rec/pythonpath"'
check "engineer: the dry run checked the same CLI arguments" '[ "$(cat "$W/rec/dry_args")" = "-p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits --allowedTools Bash Read Edit Write Grep Glob" ]'
check "engineer: the brief copied into the tree's scratch/brief" '[ -s "$DEST/W2-99-eng.md" ]'
check "engineer: the session read the copy on stdin" 'cmp -s "$W/rec/stdin" "$DEST/W2-99-eng.md"'
check "engineer: EMG-common.md and EMG-d4b-launched.md copied beside it" '[ -s "$DEST/EMG-common.md" ] && [ -s "$DEST/EMG-d4b-launched.md" ]'
check "engineer: main-tree paths rewritten to the copies" 'grep -q "Read $DEST/EMG-common.md first" "$DEST/W2-99-eng.md" && grep -q "$DEST/EMG-common.md" "$DEST/EMG-d4b-launched.md" && ! grep -q "$W/common" "$DEST"/*.md'
check "engineer: a brief naming no sandbox check gets step 0 first" 'head -n 1 "$DEST/W2-99-eng.md" | grep -q "^Step 0.*EMG-d4b-launched.md"'
check "engineer: the log holds the session's JSON" 'grep -q stub-1 "$LOG/W2-99-eng.json"'
check "engineer: the exit file holds 0" '[ "$(cat "$LOG/W2-99-eng.exit")" = 0 ]'
check "engineer: the summary (tripwire clean, sandbox file absent)" 'grep -q "session exit 0; tripwire clean; sandbox trial file absent" "$LOG/W2-99-eng.summary"'
check "engineer: the tripwire snapshot kept" '[ -s "$LOG/W2-99-eng.tripwire-before.json" ] && [ -s "$LOG/W2-99-eng.tripwire.json" ]'

# 3. the same brief again: a new name, nothing overwritten; the session's own code is kept
STUB_RC=7 lw --fg engineer xhigh "$W/briefs/W2-99-eng.md"; rc=$?
check "again: a new name (-2); the first log kept" '[ -s "$LOG/W2-99-eng-2.json" ] && grep -q stub-1 "$LOG/W2-99-eng.json"'
check "the session's code (7) is the exit and the exit file" '[ $rc = 7 ] && [ "$(cat "$LOG/W2-99-eng-2.exit")" = 7 ]'

# 4. the reviewer gets no Edit or Write; a test designer finds its own ticket; a brief with step 0 is left as it is
lw --fg independent-auditor high "$W/briefs/W2-99-review.md"
check "reviewer: read-only tools" 'grep -q "launch independent-auditor T-eng -- .* --allowedTools Bash Read Grep Glob$" "$W/rec/argv"'
cp "$W/common/EMG-d4b-launched.md" "$W/briefs/W2-99-tests.md"
lw --fg independent-test-designer high "$W/briefs/W2-99-tests.md"
check "test designer: its own ticket (T-td)" 'grep -q "^launch independent-test-designer T-td " "$W/rec/argv"'
check "a brief that names its sandbox check gets no added line" '! grep -q "launch_worker.sh" "$DEST/W2-99-tests.md"'

# 5. the ticket: one, or named
ticket "$R" T-eng2 in_progress W2-99 engineer
lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "two in_progress engineer tickets: exit 2, nothing started" '[ $rc = 2 ] && [ ! -e "$W/rec/argv" ]'
LAUNCH_TICKET=T-eng2 lw --fg engineer high "$W/briefs/W2-99-eng.md"
check "LAUNCH_TICKET names it" 'grep -q "^launch engineer T-eng2 " "$W/rec/argv"'
rm "$R/.tickets/T-eng2.md"

# 6. the gates: disk, the launcher's dry run, the sandbox faults, a trial file already there
STUB_GATE_RC=1 lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
last=$(ls -t "$LOG"/*.exit | head -n 1)
check "disk gate shut: exit 3, nothing started, the exit file 3" '[ $rc = 3 ] && [ ! -e "$W/rec/argv" ] && [ "$(cat "$last")" = 3 ] && grep -q "disk gate is shut" "${last%.exit}.json"'
STUB_DRY_REFUSE=1 lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "the launcher's dry run refuses: exit 4, the reason, nothing started" '[ $rc = 4 ] && [ ! -e "$W/rec/argv" ] && grep -q "not in_progress" "$W/stderr"'
STUB_FAULT=1 lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "sandbox faults in the built settings: exit 4, nothing started" '[ $rc = 4 ] && [ ! -e "$W/rec/argv" ] && grep -q "not strict" "$W/stderr"'
echo x > "$W/trial/.sandbox-trial-T-eng"
lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "a trial file already there: exit 4, nothing started" '[ $rc = 4 ] && [ ! -e "$W/rec/argv" ]'
rm "$W/trial/.sandbox-trial-T-eng"

# 7. after the session: a sandbox breach and a tripwire change are named in the summary
STUB_BREACH=1 STUB_TRIP_RC=1 lw --fg engineer high "$W/briefs/W2-99-eng.md"
last=$(ls -t "$LOG"/*.summary | head -n 1)
check "a breach: SANDBOX BREACH named, the file left in place" 'grep -q "SANDBOX BREACH" "$last" && [ -e "$W/trial/.sandbox-trial-T-eng" ]'
check "a tripwire change: CHANGED named" 'grep -q "tripwire CHANGED" "$last"'
rm "$W/trial/.sandbox-trial-T-eng"

# 8. detached by default: back at once, its own process group, the pid file; wait_for.sh reads the end
s=$(date +%s); STUB_SLEEP=3 lw engineer high "$W/briefs/W2-99-eng.md"; rc=$?; e=$(( $(date +%s) - s ))
ex=$(sed -n 's/^launch_worker: wait with: bash .*wait_for.sh //p' "$W/stdout")
check "detached: exit 0 at once (${e}s <= 2), the wait line printed" '[ $rc = 0 ] && [ $e -le 2 ] && [ -n "$ex" ]'
pid=$(cat "${ex%.exit}.pid")
check "detached: the session in its own process group" '[ "$(ps -o pgid= -p "$pid" | tr -d " ")" = "$pid" ]'
out=$(WAIT_FOR_EVERY=1 bash "$HERE/wait_for.sh" "$ex" 60); rc=$?
check "detached: wait_for.sh gives DONE exit 0, the result and the summary" '[ $rc = 0 ] && grep -q "DONE exit 0" <<< "$out" && grep -q "status: DONE" <<< "$out" && grep -q "tripwire clean" <<< "$out"'

# 9. the form: never --settings, never a name match
! grep -q -- '--settings' "$T"; check "no --settings in the launch line" '[ $? = 0 ]'
! grep -Eq '(^|[^a-z_])(pgrep|pkill|killall)([^a-z_]|$)' "$T"; check "no pgrep, pkill or killall" '[ $? = 0 ]'

rm -rf "$W"
echo "$([ $fails = 0 ] && echo PASS || echo "FAILED $fails") test_launch_worker.sh"
[ $fails = 0 ]
