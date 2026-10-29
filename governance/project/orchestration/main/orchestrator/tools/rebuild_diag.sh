#!/usr/bin/env bash
# P1-MORNING-2026-10-29 item 2: a main-tree rebuild, timed, with a sample every 30 s of what its process tree is
# doing (each process's state, wait channel and command), the load, and whether Ollama answers locally. Finds the
# stage that waits when a rebuild runs for hours. Writes log/rebuild-diag-<stamp>/.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
OUT=$ORCH/log/rebuild-diag-$(date +%Y%m%d-%H%M)
mkdir -p "$OUT"
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 2
{ echo "start $(date '+%F %T')"; echo "ollama: $(curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:11434/api/tags || echo none)"; } > "$OUT/summary.txt"
start=$(date +%s)
gov rebuild --json > "$OUT/rebuild.json" 2> "$OUT/rebuild.err" &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  {
    echo "== $(date '+%T') load $(cut -d' ' -f1-3 /proc/loadavg)"
    for p in $pid $(pgrep -P "$pid") $(for c in $(pgrep -P "$pid"); do pgrep -P "$c"; done); do
      [ -r "/proc/$p/stat" ] || continue
      echo "$p $(awk '{print $3}' "/proc/$p/stat") $(cat "/proc/$p/wchan" 2>/dev/null) $(tr '\0' ' ' < "/proc/$p/cmdline" | cut -c1-140)"
    done
  } >> "$OUT/samples.txt"
  sleep 30
done
wait "$pid"; code=$?
echo "end $(date '+%F %T') exit $code after $(( $(date +%s) - start )) s" >> "$OUT/summary.txt"
cat "$OUT/summary.txt"
