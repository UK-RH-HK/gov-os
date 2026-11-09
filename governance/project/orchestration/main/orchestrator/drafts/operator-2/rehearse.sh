#!/usr/bin/env bash
# ACT-OPERATOR-2: the rehearsal, end to end, in a scratch clone with a planted HOME (DEC-1057). Changes nothing live.
#   bash rehearse.sh            the log: rehearsal.log beside this file
# Layout ($BASE = ~/gov-os-runs/OPERATOR2-rehearsal):
#   $BASE/Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone at the main tree's head, w2/integrate checked out
#   $BASE/home                              the planted HOME: gov-os-operator/ (the live install copied, its settings the
#                                           rehearsal's; the owner's files planted), .gov-os/guard-calls (planted), a
#                                           dummy sets root, the CTO session's planted transcript
#   $BASE/replay/calls.jsonl                the planted call set (the after-settings' `calls`)
# The operator's walled session is the real `claude` (the cheapest model, about $0.02 each), with the real HOME for its
# sign-in only; every file the operator reads or writes is the planted HOME's.
if [ -z "${OP2_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="/usr/local/bin:/usr/bin:/bin" \
    LANG="${LANG:-C.UTF-8}" OP2_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/operator-2
BASE=$HOME/gov-os-runs/OPERATOR2-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
SR_NAME="gov-os-""eval"
PR=$PH/$SR_NAME
TMPD=/tmp/gov-os-op2-rehearsal
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
D=$R/$SUB/drafts/operator-2
LOG=$HERE/rehearsal.log
OPR="python3 $HERE/op2_rehearsal.py"
SB=$BASE/settings.before.json
SA=$BASE/settings.after.json
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
say() { printf '\n== %s (%s)\n' "$1" "$(date -u '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
expect() {  # $1 file, $2 extended regex the file must hold, $3 what
  grep -Eq "$2" "$1" && echo "ok: $3" || bad "$3 (wanted /$2/ in $(basename "$1"))"; }
AP() { ( cd "$R" && HOME=$PH bash "$D/apply.sh" "$1" --settings-before "$SB" --settings-after "$SA" ); }

live_hashes() {
  ( cd "$HOME/gov-os-operator" && find . -path ./log -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum )
  echo "log/ entries: $(ls "$HOME/gov-os-operator/log" | LC_ALL=C sort | tr '\n' ' ')"
  ( cd "$MAIN" && sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml .claude/settings.json \
      governance/project/operator/*.py )
  sha256sum "$HOME/.claude/settings.json"
  /usr/bin/crontab -l 2>/dev/null | sha256sum | cut -c1-12 | sed 's/^/live crontab: /'
}

say "prepare: the clone, the planted HOME, the install copied from the live one (read only)"
date -u '+start %Y-%m-%dT%H:%M:%SZ'
live_hashes > "$BASE.live-before.txt" 2>&1 || true
if [ -e "$BASE" ]; then
  [ -f "$BASE/.op2-rehearsal" ] || { echo "REHEARSAL STOP: $BASE exists and is not this script's"; exit 3; }
  chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"
fi
chmod -R u+w "$TMPD" 2>/dev/null; rm -rf "$TMPD"; mkdir -p "$TMPD" "$BASE/hooks-safe" "$BASE/replay" "$BASE/claude-bin" && : > "$BASE/.op2-rehearsal"
mv "$BASE.live-before.txt" "$BASE/live-before.txt"
head=$(git -C "$MAIN" rev-parse HEAD)
git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; exit 1; }
git -C "$R" config core.hooksPath "$BASE/hooks-safe"
git -C "$R" checkout -q -B w2/integrate "$head" || bad "checkout"
git -C "$R" config user.name "op2 rehearsal"; git -C "$R" config user.email "op2@localhost"
mkdir -p "$R/$SUB/drafts" "$R/$SUB/log" "$R/$SUB/acts"
cp -a "$HERE" "$R/$SUB/drafts/"; rm -rf "$D/backup" "$D/backup.undone-"* "$D/rehearsal.log" "$D/__pycache__"
echo "clone at $(git -C "$R" rev-parse --short=12 HEAD); the tree's operator code: $(cd "$R" && sha256sum governance/project/operator/opcommon.py governance/project/operator/operator_run.py | cut -c1-12 | tr '\n' ' ')"
# the planted HOME: the owner's operator files (planted), the live install copied (read only), the queue, the log
O=$PH/gov-os-operator
mkdir -p "$O/.claude" "$O/hooks" "$O/log" "$PH/.gov-os/guard-calls" "$PR/fixtures/evaluation/memory-verdict/hidden" "$PR/indep-walls"
printf 'DUMMY planted\n' > "$PR/fixtures/evaluation/memory-verdict/hidden/p01.yaml"
printf '# Operator console (planted copy of the owner'"'"'s note)\n' > "$O/CLAUDE.md"
printf '{"permissions": {"allow": ["Bash"]}}\n' > "$O/.claude/settings.json"
printf '# planted log_command.py\n' > "$O/hooks/log_command.py"
printf '2026-11-01T10:00:00\texit=0\tplanted\n' > "$O/log/2026-11-01.log"
cp -a "$HOME/gov-os-operator/install" "$O/install"; rm -rf "$O/install/__pycache__"
mkdir -m 0700 "$O/queue"
printf '#!/bin/sh\nexec env HOME=/home/usain /home/usain/.local/bin/claude "$@"\n' > "$BASE/claude-bin/claude"
chmod 0755 "$BASE/claude-bin/claude"
printf '#!/bin/sh\nprintf "%%s\\n" "$1" >> %s/pushes.log\n' "$BASE" > "$BASE/push.sh"; chmod 0755 "$BASE/push.sh"
python3 - "$SB" "$SA" "$R" "$PH" "$BASE" <<'EOF'
import json, sys
sb, sa, r, ph, base = sys.argv[1:]
d = {"repo": r, "home": ph, "claude": f"{base}/claude-bin/claude", "push_cmd": [f"{base}/push.sh"],
     "budget_usd": "1", "session_timeout_s": 1500}
open(sb, "w").write(json.dumps(d, indent=1) + "\n")
d["calls"] = f"{base}/replay/calls.jsonl"
open(sa, "w").write(json.dumps(d, indent=1) + "\n")
EOF
# the planted install's before state: the live code, the rehearsal's settings, APPROVED in sha256sum's form
chmod u+w "$O/install" "$O/install/operator-settings.json" "$O/install/APPROVED"
cp "$SB" "$O/install/operator-settings.json"
( cd "$O/install" && find . -path ./__pycache__ -prune -o -type f ! -name APPROVED -print | sed 's#^\./##' | LC_ALL=C sort \
    | xargs sha256sum > "$BASE/APPROVED.planted" ) && cat "$BASE/APPROVED.planted" > "$O/install/APPROVED"
chmod 0444 "$O/install/operator-settings.json" "$O/install/APPROVED"
( cd "$O" && find CLAUDE.md .claude hooks log/2026-11-01.log -type f | LC_ALL=C sort | xargs sha256sum ) > "$BASE/owner-files-before.txt"
echo "planted install: $(ls "$O/install" | wc -l) entries, APPROVED $(sha256sum "$O/install/APPROVED" | cut -c1-12); live install APPROVED $(sha256sum "$HOME/gov-os-operator/install/APPROVED" | cut -c1-12)"

say "suites on the clone (the code the install will carry): W2-148 acceptance, tests/unit/operator"
( cd "$R" && HOME=$TMPD PYTHONUSERBASE=/home/usain/.local TMPDIR=$TMPD PYTHONPATH=$R/src $SLOT python3 -m pytest \
    tests/acceptance/W2-148 -q -p no:cacheprovider -o tmp_path_retention_policy=failed ) > "$BASE/accept.txt" 2>&1
tail -1 "$BASE/accept.txt"; expect "$BASE/accept.txt" " passed" "W2-148 acceptance ran"
grep -Eq "failed|error" <(tail -1 "$BASE/accept.txt") && bad "W2-148 acceptance has a failure"
( cd "$R" && HOME=$TMPD PYTHONUSERBASE=/home/usain/.local TMPDIR=$TMPD PYTHONPATH=$R/src $SLOT python3 -m pytest \
    tests/unit/operator -q -p no:cacheprovider -o tmp_path_retention_policy=failed ) > "$BASE/unit.txt" 2>&1
tail -1 "$BASE/unit.txt"; grep -Eq "failed|error" <(tail -1 "$BASE/unit.txt") && bad "tests/unit/operator has a failure"

say "apply.sh: check, apply, a second apply, check, undo, check, apply again"
AP check > "$BASE/ap-check1.txt" 2>&1; cat "$BASE/ap-check1.txt"; expect "$BASE/ap-check1.txt" "check: ready to apply" "check: ready"
AP apply > "$BASE/ap-apply1.txt" 2>&1; cat "$BASE/ap-apply1.txt"; expect "$BASE/ap-apply1.txt" "^state applied" "applied"
expect "$BASE/ap-apply1.txt" "own APPROVED check: ok" "the install's own APPROVED check"
AP apply > "$BASE/ap-apply2.txt" 2>&1 && bad "a second apply ran" || echo "a second apply: refused ($(tail -1 "$BASE/ap-apply2.txt"))"
AP check | tail -1 | tee "$BASE/ap-check2.txt"; expect "$BASE/ap-check2.txt" "already applied" "check: already applied"
( cd "$O/install" && sha256sum opcommon.py operator_run.py operator-settings.json APPROVED | cut -c1-12,65- )
AP undo > "$BASE/ap-undo1.txt" 2>&1; cat "$BASE/ap-undo1.txt"; expect "$BASE/ap-undo1.txt" "state before" "undone"
AP check | tail -1 | tee "$BASE/ap-check3.txt"; expect "$BASE/ap-check3.txt" "ready to apply" "check: ready again"
( cd "$O/install" && sha256sum -c --quiet APPROVED ) && echo "after undo: every install file matches the before APPROVED"
: > "$O/queue/20990101T000000-ACT-X.req"
AP apply > "$BASE/ap-held.txt" 2>&1 && bad "apply ran with a request waiting" || echo "a request waiting: refused ($(tail -1 "$BASE/ap-held.txt"))"
rm -f "$O/queue/20990101T000000-ACT-X.req"
: > "$O/install/act-in-progress.txt" 2>/dev/null || { chmod u+w "$O/install"; : > "$O/install/act-in-progress.txt"; }
AP apply > "$BASE/ap-freeze.txt" 2>&1 && bad "apply ran under the freeze" || echo "the freeze held: refused ($(tail -1 "$BASE/ap-freeze.txt"))"
rm -f "$O/install/act-in-progress.txt"
rm -rf "$D/backup.undone-"*
AP apply > "$BASE/ap-apply3.txt" 2>&1; tail -2 "$BASE/ap-apply3.txt"; expect "$BASE/ap-apply3.txt" "^state applied" "applied again"

say "the launcher as the cron runs it, nothing queued: the re-installed APPROVED holds"
OP2_TMP=$TMPD $OPR launch "$R" "$PH" "$BASE" | tee "$BASE/launch-idle.txt"
expect "$BASE/launch-idle.txt" '"result": "idle"' "the launcher: idle, its APPROVED check passed"

say "a class-(a) path-map ACT through every gate, the call set and the guard's log agreeing (the replay check)"
$OPR plant-replay "$R" "$PH" "$BASE" agree
$OPR bundle-p "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-1 opr2-new-1 | tee "$BASE/bundle-1.txt"
$OPR queue "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-1
OP2_TMP=$TMPD $OPR launch "$R" "$PH" "$BASE" | tee "$BASE/launch-1.txt"
expect "$BASE/launch-1.txt" '"result": "launched"' "the launcher started the walled session"
$OPR show "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-1 | tee "$BASE/show-1.txt"
expect "$BASE/show-1.txt" "log apply applied votes=\\{'code': 'a', 'claim': 'a', 'review': 'a'\\}" "ACT-OPR2-PATHMAP-1 applied, votes a/a/a"
expect "$BASE/show-1.txt" "replay\\(calls=3, turned=\\[\\]" "its after-check replayed the 3 calls after the both-way check: none turned"
grep -c "opr2-new-1" "$R/governance/project/path-map.yaml" | sed 's/^/the clone map holds the new glob: /'
git -C "$R" log -1 --format='%h %s%n%b' | head -12
msha=$(python3 -c "import json,sys; print(json.loads(open(sys.argv[1]).readline())['manifest_sha256'])" "$BASE/bundle-1.txt")
$OPR owner "$R" "$PH" "$BASE" "undo ACT-OPR2-PATHMAP-1 ${msha:0:8}"
OP2_TMP=$TMPD $OPR undo "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-1 | tee "$BASE/undo-1.txt"
expect "$BASE/undo-1.txt" '"result": "undone"' "ACT-OPR2-PATHMAP-1 undone by the owner's line"

say "the same kind of ACT with a logged live call the call set does not hold: refused at the after-check, undone"
$OPR plant-replay "$R" "$PH" "$BASE" missing
$OPR bundle-p "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-2 opr2-new-2 | tee "$BASE/bundle-2.txt"
$OPR queue "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-2
OP2_TMP=$TMPD $OPR launch "$R" "$PH" "$BASE" | tee "$BASE/launch-2.txt"
expect "$BASE/launch-2.txt" '"result": "launched"' "the launcher started the walled session"
$OPR show "$R" "$PH" "$BASE" ACT-OPR2-PATHMAP-2 | tee "$BASE/show-2.txt"
cat "$BASE/launch-2.txt" "$BASE/show-2.txt" "$BASE/pushes.log" > "$BASE/told-2.txt" 2>/dev/null
expect "$BASE/told-2.txt" 'log after-check undone .*missing from the set' "ACT-OPR2-PATHMAP-2 refused at its after-check, the mismatch named, undone"
expect "$BASE/told-2.txt" 'notice P1 undo' "a P1 notice"
c=$(grep -c "opr2-new-2" "$R/governance/project/path-map.yaml"); echo "the clone map holds the second glob: $c"
[ "$c" = 0 ] && echo "ok: the refused ACT left the map as before" || bad "the refused ACT's glob stayed"
cat "$BASE/pushes.log" 2>/dev/null | tail -3 | cut -c1-240

say "the real call set (the CTO's builder over the real transcripts) against the real guard log, by the installed check"
python3 "$MAIN/$SUB/tools/build_replay_calls.py" --out "$BASE/real-calls.jsonl" --hours 48 > "$BASE/real-build.txt" 2>&1
tail -4 "$BASE/real-build.txt"
$OPR real-check "$R" "$PH" "$BASE" "$BASE/real-calls.jsonl" | tee "$BASE/real-check.txt"
rm -f "$BASE/real-calls.jsonl"

say "apply.sh undo, then check: the planted install as before"
rm -rf "$O/queue/"*.req 2>/dev/null
AP undo > "$BASE/ap-undo2.txt" 2>&1; tail -2 "$BASE/ap-undo2.txt"; expect "$BASE/ap-undo2.txt" "state before" "undone at the end"
AP check | tail -1 | tee "$BASE/ap-check4.txt"; expect "$BASE/ap-check4.txt" "ready to apply" "check: ready to apply at the end"
( cd "$O" && find CLAUDE.md .claude hooks log/2026-11-01.log -type f | LC_ALL=C sort | xargs sha256sum ) > "$BASE/owner-files-after.txt"
cmp -s "$BASE/owner-files-before.txt" "$BASE/owner-files-after.txt" && echo "ok: the owner's planted files unchanged" || bad "the owner's planted files changed"

say "live files: unchanged"
live_hashes > "$BASE/live-after.txt" 2>&1 || true
if cmp -s "$BASE/live-before.txt" "$BASE/live-after.txt"; then echo "ok: live files unchanged ($(wc -l < "$BASE/live-after.txt") lines hashed)"
else diff "$BASE/live-before.txt" "$BASE/live-after.txt" | head -20; bad "a live file changed"; fi
du -sh "$BASE" "$TMPD" 2>/dev/null | sed 's/^/scratch: /'
date -u '+end %Y-%m-%dT%H:%M:%SZ'
echo "failures: $FAILS"
