#!/usr/bin/env bash
# Tests for gpu_backstop.sh (the owner, 2026-11-05: pause by process group only, never by command text).
# A stand-in nvidia-smi sets the GPU reading; the real embedders' /api/ps and logs are read as in use.
set -u
T=$(cd "$(dirname "$0")" && pwd)/gpu_backstop.sh
W=$(mktemp -d /tmp/gov-os-test-backstop.XXXXXX)
fails=0
ok() { echo "ok   $1"; }
no() { echo "FAIL $1"; fails=$((fails+1)); }
fake() { printf '#!/usr/bin/env bash\necho "%s, 16303"\n' "$1" > "$W/nvsmi"; chmod +x "$W/nvsmi"; }
group() {  # start a sleeper in its own process group whose args name the old MARK text; print its pgid
  local f="$W/pid.$RANDOM"
  setsid bash -c "echo \$\$ > $f; exec -a research-retrieval-$1 sleep 120" < /dev/null > /dev/null 2>&1 &
  for _ in $(seq 1 50); do [ -s "$f" ] && break; sleep 0.1; done
  ps -o pgid= -p "$(cat "$f")" | tr -d ' '
}
state() { ps -o stat= -p "$1" 2>/dev/null | cut -c1; }
cleanup() { for g in "$@"; do kill -CONT -- "-$g" 2>/dev/null; kill -KILL -- "-$g" 2>/dev/null; done; }

# 1. no group named: refused, never a match by name
bash "$T" > /dev/null 2>&1; [ $? = 2 ] && ok "no group named: exit 2" || no "no group named: exit 2"
bash "$T" research-retrieval > /dev/null 2>&1; [ $? = 2 ] && ok "a name, not a pgid: exit 2" || no "a name, not a pgid: exit 2"
bash "$T" 1 > /dev/null 2>&1; [ $? = 2 ] && ok "pgid 1 refused" || no "pgid 1 refused"

# 2. a trip pauses the named group and only it (the decoy's args hold the same text)
A=$(group job); B=$(group decoy); mkdir -p "$W/inbox"
fake 16000
INBOX="$W/inbox" LOG="$W/log" NVSMI="$W/nvsmi" EVERY=1 timeout 30 bash "$T" "$A"; rc=$?
[ "$rc" = 0 ] && ok "trip exits 0" || no "trip exits 0 (rc $rc)"
[ "$(state "$A")" = T ] && ok "the named group is paused" || no "the named group is paused (state $(state "$A"))"
[ "$(state "$B")" = S ] && ok "the decoy with the same text is not paused" || no "the decoy is not paused (state $(state "$B"))"
grep -q "paused groups: $A" "$W/log" && ok "the log names the group" || no "the log names the group"
ls "$W/inbox"/*-gpu-stop.txt > /dev/null 2>&1 && grep -q "SIGSTOP): $A;" "$W"/inbox/*-gpu-stop.txt && ok "an inbox item names the group" || no "an inbox item names the group"
cleanup "$A" "$B"

# 3. below the limit nothing is paused, and the watcher ends when its group ends
C=$(group short); fake 5000
INBOX="$W/inbox2" LOG="$W/log2" NVSMI="$W/nvsmi" EVERY=1 timeout 40 bash "$T" "$C" &
BP=$!
sleep 3
[ "$(state "$C")" = S ] && ok "below the limit: not paused" || no "below the limit: not paused (state $(state "$C"))"
kill -KILL -- "-$C" 2>/dev/null
wait "$BP"; rc=$?
[ "$rc" = 0 ] && grep -q "end: every watched group has ended" "$W/log2" && ok "ends by itself when the group ends" || no "ends by itself (rc $rc)"
[ ! -e "$W/inbox2" ] || [ -z "$(ls "$W/inbox2")" ] && ok "no inbox item without a trip" || no "no inbox item without a trip"

rm -rf "$W"
echo "$([ $fails = 0 ] && echo PASS || echo "FAILED $fails")"
[ $fails = 0 ]
