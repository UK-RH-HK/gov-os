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
import json
r = {"type": "result", "is_error": False, "num_turns": 3, "session_id": "stub-1", "result": "task: stub\nstatus: DONE"}
if os.environ.get("STUB_COST"):
    r.update(total_cost_usd=float(os.environ["STUB_COST"]), usage={"input_tokens": 7, "output_tokens": 100,
             "cache_read_input_tokens": 9000, "cache_creation_input_tokens": 500})
print(json.dumps(r))
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
  LAUNCH_TRIPWIRE=$W/trip.py LAUNCH_TRIAL_DIR=$W/trial LAUNCH_MODEL=claude-opus-5-5  # RUBRIC-2: the model is always named
CLS=(--class C2)  # every launch here names its class (RUBRIC-2); section 12 tests it absent, invalid and promoted
LOG=$R/.gov-runtime/scratch/lead/log DEST=$R/.gov-runtime/scratch/brief
lw() { rm -f "$W"/rec/*; (cd "$R" && bash "$T" "${CLS[@]}" "$@") > "$W/stdout" 2> "$W/stderr"; }

# 1. usage and refusals before anything is written
lw --fg reviewer high "$W/briefs/W2-99-eng.md"; check "not a worker role: exit 2" '[ $? = 2 ]'
lw --fg engineer hard "$W/briefs/W2-99-eng.md"; check "not an effort: exit 2" '[ $? = 2 ]'
lw --fg engineer high "$W/briefs/none.md"; check "no brief: exit 2" '[ $? = 2 ]'
(cd "$W/main" && LAUNCH_TREE=$W/main bash "$T" --class C2 --fg engineer high "$W/briefs/W2-99-eng.md") > /dev/null 2>&1
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

# 10. spend in one unit and the runaway brake (DAEO-sdxk, DEC-1091): the line, the brake, the refusal, the clear
SP=$W/main/.gov-runtime/scratch/orchestrator/log/spend.jsonl BK=$W/main/.gov-runtime/scratch/orchestrator/log/brake
IB=$W/main/.gov-runtime/scratch/orchestrator/dispatch/inbox
lastline() { tail -n 1 "$SP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1]))" "$1"; }
check "spend: every session so far has its line, no cost for a session that reports none" '[ "$(lastline "d[\"cost_usd\"]")" = None ] && [ "$(lastline "d[\"wbs\"]")" = W2-99 ]'
lw --fg --projection-usd x engineer high "$W/briefs/W2-99-eng.md"; check "spend: a projection that is not a number: exit 2" '[ $? = 2 ]'
STUB_COST=1.5 lw --fg --projection-usd 1 engineer high "$W/briefs/W2-99-eng.md"; rc=$?
last=$(ls -t "$LOG"/*.summary | head -n 1)
check "spend: the line carries cost_usd, output and cache tokens apart, the ticket, the projection" '[ $rc = 0 ] && [ "$(lastline "(d[\"cost_usd\"], d[\"output_tokens\"], d[\"cache_read_tokens\"], d[\"cache_creation_tokens\"], d[\"input_tokens\"], d[\"ticket\"], d[\"projection_usd\"], d[\"kind\"])")" = "(1.5, 100, 9000, 500, 7, '"'"'T-eng'"'"', 1.0, '"'"'launched'"'"')" ]'
check "spend: no line has a tokens field" '! grep -q "\"tokens\"" "$SP"'
check "spend: the summary says it was recorded; under twice the projection, no brake" 'grep -q "spend recorded (projection 1)" "$last" && [ ! -e "$BK/W2-99.json" ] && ! ls "$IB"/*-spend-brake.txt > /dev/null 2>&1'
STUB_COST=0.6 lw --fg engineer high "$W/briefs/W2-99-eng.md"
last=$(ls -t "$LOG"/*.summary | head -n 1)
check "brake: past twice the projection (2.1 > 2.0): the brake file, one inbox item with its W2 line, named in the summary" '[ -e "$BK/W2-99.json" ] && [ $(ls "$IB"/*-spend-brake.txt | wc -l) = 1 ] && grep -q "^W2: W2-99$" "$IB"/*-spend-brake.txt && grep -q "BRAKE W2-99" "$last"'
lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "brake: the next launch for W2-99 is refused (exit 5), nothing started" '[ $rc = 5 ] && [ ! -e "$W/rec/argv" ] && grep -q "runaway brake holds W2-99" "$W/stderr"'
ORCH=$W/main/.gov-runtime/scratch/orchestrator python3 "$HERE/spend.py" check > /dev/null
check "brake: a second check writes no second item" '[ $(ls "$IB"/*-spend-brake.txt | wc -l) = 1 ]'
ORCH=$W/main/.gov-runtime/scratch/orchestrator python3 "$HERE/spend.py" clear W2-99 --note "test" > /dev/null
lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "brake: cleared by the CTO, the launch goes on and the cost counts afresh" '[ $rc = 0 ] && [ ! -e "$BK/W2-99.json" ] && [ -e "$W/rec/argv" ]'
printf -- '---\nbudget_usd: 3\n---\n# W2-99 engineer, budgeted\n' > "$W/briefs/W2-99-budget.md"
lw --fg engineer high "$W/briefs/W2-99-budget.md"
check "spend: with no --projection-usd, the brief's budget is the projection" '[ "$(lastline "d[\"projection_usd\"]")" = 3.0 ] && grep -q "projection 3" "$W/stderr"'

# 11. review findings 7 and 9: the brake is keyed on the ticket's own wbs_id; a bare or zero projection is refused
lw --fg engineer high "$W/briefs/W2-99-eng.md" --projection-usd; check "a --projection-usd with no value: exit 2" '[ $? = 2 ]'
lw --fg --projection-usd 0 engineer high "$W/briefs/W2-99-eng.md"; check "a projection of 0: exit 2" '[ $? = 2 ] && [ ! -e "$W/rec/argv" ]'
lw --fg --projection-usd; check "--projection-usd last, no value: exit 2" '[ $? = 2 ]'
LAUNCH_TICKET=T-other lw --fg engineer high "$W/briefs/W2-99-eng.md"
check "the spend line's W2 is the ticket file's wbs_id (W2-98), not the folder's" '[ "$(lastline "(d[\"wbs\"], d[\"ticket\"])")" = "('"'"'W2-98'"'"', '"'"'T-other'"'"')" ]'
mkdir -p "$BK"; echo '{}' > "$BK/W2-98.json"
LAUNCH_TICKET=T-other lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "the brake on the ticket's own W2 refuses its launch from another folder (exit 5)" '[ $rc = 5 ] && [ ! -e "$W/rec/argv" ]'
rm "$BK/W2-98.json"

# 12. RUBRIC-2 (DEC-1120 (3)): the class required and validated, the model always named, the spend line's four fields
CLS=(); lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "class: none given -> exit 2, nothing started, the reason named" '[ $rc = 2 ] && [ ! -e "$W/rec/argv" ] && grep -q "^launch_worker: --class is required" "$W/stderr"'
lw --fg --class C9 engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "class: C9 -> exit 2, nothing started" '[ $rc = 2 ] && [ ! -e "$W/rec/argv" ] && grep -q "not a class: C9" "$W/stderr"'
lw --fg --class c2 engineer high "$W/briefs/W2-99-eng.md"; check "class: lower case c2 -> exit 2" '[ $? = 2 ] && [ ! -e "$W/rec/argv" ]'
lw --fg engineer high "$W/briefs/W2-99-eng.md" --class C2; check "class: after the positionals (a usage error) -> exit 2" '[ $? = 2 ] && [ ! -e "$W/rec/argv" ]'
lw --fg --class; check "class: --class last, no value -> exit 2" '[ $? = 2 ]'
for c in C0 C1 C2 C3; do
  lw --fg --class $c engineer high "$W/briefs/W2-99-eng.md"; check "class: $c is accepted" '[ $? = 0 ] && [ -e "$W/rec/argv" ]'
done
CLS=(--class C2)
LAUNCH_MODEL= lw --fg engineer high "$W/briefs/W2-99-eng.md"; rc=$?
check "model: LAUNCH_MODEL empty, no --model -> exit 2, nothing started, the reason named" '[ $rc = 2 ] && [ ! -e "$W/rec/argv" ] && grep -q "no model named" "$W/stderr"'
(unset LAUNCH_MODEL; lw --fg engineer high "$W/briefs/W2-99-eng.md"); rc=$?
check "model: LAUNCH_MODEL unset -> exit 2 (no default model any more), nothing started" '[ $rc = 2 ] && [ ! -e "$W/rec/argv" ] && grep -q "no model named" "$W/stderr"'
lw --fg --model; check "model: --model last, no value -> exit 2" '[ $? = 2 ]'
LAUNCH_MODEL= lw --fg --model claude-haiku-5 engineer high "$W/briefs/W2-99-eng.md"
check "model: --model alone names it: on the launch line and on the dry run's" 'grep -q "^launch engineer T-eng -- -p --model claude-haiku-5 --effort high " "$W/rec/argv" && grep -q -- "--model claude-haiku-5 " "$W/rec/dry_args"'
LAUNCH_MODEL=claude-opus-5-5 lw --fg --model claude-sonnet-5-5 engineer high "$W/briefs/W2-99-eng.md"
check "model: --model wins over LAUNCH_MODEL" 'grep -q -- "-p --model claude-sonnet-5-5 --effort" "$W/rec/argv"'
check "model: no model is built into the tool (no default left)" '! grep -q "claude-opus-5-5\|claude-sonnet-5-5" "$T"'
lw --fg --promoted "" engineer high "$W/briefs/W2-99-eng.md"; check "promoted: an empty reason -> exit 2, nothing started" '[ $? = 2 ] && [ ! -e "$W/rec/argv" ]'
lw --fg --promoted; check "promoted: no value -> exit 2" '[ $? = 2 ]'
# the spend line: model, class, tier, promoted beside the old fields
STUB_COST=0.4 lw --fg --class C1 --model claude-sonnet-5-5 --promoted "two failed reviews (DEC-1120 (3))" engineer high "$W/briefs/W2-99-eng.md"
last=$(ls -t "$LOG"/*.summary | head -n 1)
check "spend line: model, class, tier, promoted, and the old fields kept" '[ "$(lastline "(d[\"model\"], d[\"class\"], d[\"tier\"], d[\"promoted\"], d[\"cost_usd\"], d[\"ticket\"], d[\"role\"], d[\"extra\"][\"effort\"])")" = "('"'"'claude-sonnet-5-5'"'"', '"'"'C1'"'"', '"'"'sonnet'"'"', '"'"'two failed reviews (DEC-1120 (3))'"'"', 0.4, '"'"'T-eng'"'"', '"'"'engineer'"'"', '"'"'high'"'"')" ]'
check "spend line: the stderr launch line names the model, the class and the promotion" 'grep -q "model claude-sonnet-5-5; class C1; promoted: two failed reviews" "$W/stderr"'
STUB_COST=0.4 lw --fg engineer xhigh "$W/briefs/W2-99-eng.md"
check "spend line: not promoted -> promoted null; the tier of LAUNCH_MODEL (opus); class C2" '[ "$(lastline "(d[\"model\"], d[\"class\"], d[\"tier\"], d[\"promoted\"])")" = "('"'"'claude-opus-5-5'"'"', '"'"'C2'"'"', '"'"'opus'"'"', None)" ]'
STUB_COST=0.4 lw --class C0 --model claude-haiku-5 --fg independent-auditor medium "$W/briefs/W2-99-review.md"
check "spend line: a haiku launch -> tier haiku, class C0" '[ "$(lastline "(d[\"tier\"], d[\"class\"])")" = "('"'"'haiku'"'"', '"'"'C0'"'"')" ]'
STUB_COST=0.4 lw engineer high "$W/briefs/W2-99-eng.md"
ex=$(sed -n 's/^launch_worker: wait with: bash .*wait_for.sh //p' "$W/stdout"); WAIT_FOR_EVERY=1 bash "$HERE/wait_for.sh" "$ex" 60 > /dev/null
check "spend line: a detached launch carries the same fields" '[ "$(lastline "(d[\"model\"], d[\"class\"], d[\"tier\"])")" = "('"'"'claude-opus-5-5'"'"', '"'"'C2'"'"', '"'"'opus'"'"')" ]'
# old lines still parse: a 17-key line, a free-form one and an old-style summary, beside the new ones
ORCHD=$W/main/.gov-runtime/scratch/orchestrator
printf '%s\n' '{"at": "2026-11-09 10:00", "what": "old normal line", "kind": "launched", "ticket": "T-o", "wbs": "W2-97", "role": "engineer", "cost_usd": 1.0, "cost_source": "x", "input_tokens": null, "output_tokens": 5, "cache_read_tokens": null, "cache_creation_tokens": null, "projection_usd": 4.0, "note": null, "orig_tokens": null, "orig_cost": null, "extra": {"effort": "high"}}' '{"at": "2026-11-09 11:00", "what": "free form", "kind": "agent", "tokens": 5, "cost": "2.00 USD (x)"}' >> "$SP"
out=$(ORCH=$ORCHD python3 "$HERE/spend.py" sum 2>&1); rc=$?
check "old lines: spend.py sum reads the log with old and new lines mixed; the old W2's cost is counted" '[ $rc = 0 ] && grep -q "^W2-97: 1.00 USD" <<< "$out"'
ORCH=$ORCHD python3 "$HERE/spend.py" check > /dev/null; check "old lines: spend.py check still runs" '[ $? = 0 ]'
check "old lines: the old line is left as written in the file (17 keys, no model)" '! grep "old normal line" "$SP" | grep -q "\"model\""'

rm -rf "$W"
echo "$([ $fails = 0 ] && echo PASS || echo "FAILED $fails") test_launch_worker.sh"
[ $fails = 0 ]
