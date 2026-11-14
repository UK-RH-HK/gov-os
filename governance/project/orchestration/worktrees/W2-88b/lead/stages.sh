#!/usr/bin/env bash
# W2-88b run 3, the smoke run (DEC-1176 (2)): gov adopt's stages on one copy, one log per stage under <name>-logs/.
#   stages.sh <name> pre      the adopter's path map (committed in the copy; no gov stage), MA, A0, A1, A2, MA-at-A3, A3, A4
#   stages.sh <name> post <verdict rel path>      A5 (the auditor's committed verdict), A6, A8, A9 (no --questions)
# The first stage that exits non-zero stops this copy's chain (the stages after it are not reached); the other copy's
# run is a separate process and goes on. Every stage runs through heavy_slot.sh (a slot's wait is a wait, in the log)
# and under a memory watchdog: below WATCH_KB of MemAvailable the stage's process group is killed and the log says so.
set -u
name=$1 phase=$2 verdict=${3:-}
R=/home/usain/gov-os-runs/W2-88b
W=/home/usain/gov-os-worktrees/W2-88b
root=$R/$name logs=$R/$name-logs out=$R/$name-out
SID=lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1   # the lead's session: every stage's --session
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
WATCH_KB=${WATCH_KB:-1572864}
mkdir -p "$logs" "$out" "$R/tmp"
export PYTHONPATH=$W/src PYTHONUSERBASE=/home/usain/.local TMPDIR=$R/tmp GIT_OPTIONAL_LOCKS=0
TSV=$logs/stages.tsv
[ -f "$TSV" ] || printf 'label\tstart\tend\texit_code\tmaxrss_kb\tcommand\n' > "$TSV"

stage() {  # label, then gov's arguments after `gov adopt --lite`
  local label=$1; shift
  local log=$logs/$label.log cmd="gov adopt --lite $* --root $root --session $SID"
  local start end rc pid avail killed=""
  start=$(date -Is)
  { echo "label: $label"; echo "command: $cmd"; echo "wrapper: env PYTHONPATH=$W/src PYTHONUSERBASE=/home/usain/.local TMPDIR=$R/tmp bash $SLOT /usr/bin/time -f maxrss_kb=%M ..."
    echo "start: $start"; echo "--- output ---"; } > "$log"
  setsid /usr/bin/time -o "$log.time" -f "maxrss_kb=%M elapsed_s=%e" bash "$SLOT" gov adopt --lite "$@" --root "$root" --session "$SID" >> "$log" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2> /dev/null; do
    avail=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)
    if [ "${avail:-0}" -lt "$WATCH_KB" ]; then
      killed="watchdog: MemAvailable ${avail} kB under ${WATCH_KB} kB at $(date -Is); process group $pid killed"
      kill -TERM -- "-$pid" 2> /dev/null; sleep 10; kill -KILL -- "-$pid" 2> /dev/null
      break
    fi
    sleep 5
  done
  wait "$pid"; rc=$?
  end=$(date -Is)
  local rss; rss=$(sed -n 's/^maxrss_kb=\([0-9]*\).*/\1/p' "$log.time" 2> /dev/null | tail -1)
  { echo "--- end ---"; [ -n "$killed" ] && echo "$killed"; echo "end: $end"; echo "exit_code: $rc"
    echo "maxrss_kb: ${rss:-unknown} (/usr/bin/time, the stage's process tree's largest process)"; } >> "$log"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$label" "$start" "$end" "$rc" "${rss:-}" "$cmd" >> "$TSV"
  echo "$label rc=$rc $start -> $end"
  [ "$rc" = 0 ] || { echo "chain stops at $label (rc=$rc): the stages after it are not reached"; exit 1; }
}

head_of() { git -C "$root" rev-parse HEAD; }

if [ "$phase" = pre ]; then
  echo "pre $name start $(date -Is) head $(head_of)"
  # The adopter's input, before any stage: a path map (one namespace holding every path, embedded, code intelligence on)
  # and a commit identity local to the copy. Committed in the copy; not a gov stage.
  git -C "$root" config --local user.name "W2-88b smoke run (lead)"
  git -C "$root" config --local user.email "smoke-run@example.invalid"
  mkdir -p "$root/governance/project"
  cat > "$root/governance/project/path-map.yaml" <<'YAML'
namespaces:
  all:
    paths:
    - '**'
    embedding_policy: embedded
    memory_class: governance
capabilities:
  code_intelligence:
    enabled: true
YAML
  git -C "$root" add -- governance/project/path-map.yaml
  git -C "$root" commit -q -m "the adopter's path map for the W2-88b smoke run (one namespace, embedded, code intelligence on)"
  { echo "label: setup"; echo "start/end: $(date -Is)"; echo "pinned: $(git -C "$root" rev-parse HEAD~1)"; echo "path map commit: $(head_of)"
    echo "exit_code: 0"; } > "$logs/setup.log"
  stage MA --stage MA --out "$out/ma"
  stage A0 --stage A0
  stage A1 --stage A1
  stage A2 --stage A2
  # A3's --assessment must hold memory-assessment.json for HEAD's commit (stages.py:348-365), and A0..A2 each commit:
  # the assessment is made again at A2's head for A3 to cite (MA's first run above is S2's MA row)
  stage MA-at-A3 --stage MA --out "$out/ma-at-a3"
  printf 'artefacts: []\n' > "$out/proposal.yaml"   # the adopter's proposal: no action (every artefact kept)
  stage A3 --stage A3 --map "$out/proposal.yaml" --assessment "$out/ma-at-a3"
  stage A4 --stage A4
  echo "pre $name end $(date -Is) head $(head_of) (A5 waits for the auditor's verdict)"
  echo "$(date -Is)" > "$logs/pre.done"
elif [ "$phase" = post ]; then
  [ -n "$verdict" ] || { echo "post needs the verdict's path"; exit 2; }
  echo "post $name start $(date -Is) head $(head_of)"
  stage A5 --stage A5 --verdict "$verdict"
  stage A6 --stage A6
  stage A8 --stage A8
  stage A9 --stage A9 --out "$out/a9"
  echo "post $name end $(date -Is) head $(head_of)"
  echo "$(date -Is)" > "$logs/post.done"
elif [ "$phase" = a6-on ]; then
  # run 4: the post phase from A6, after A5 completed and an A6 run was stopped by the lead's harness (not by gov)
  echo "a6-on $name start $(date -Is) head $(head_of)"
  stage A6 --stage A6
  stage A8 --stage A8
  stage A9 --stage A9 --out "$out/a9"
  echo "a6-on $name end $(date -Is) head $(head_of)"
  echo "$(date -Is)" > "$logs/post.done"
else
  echo "usage: stages.sh <name> pre | post <verdict> | a6-on"; exit 2
fi
