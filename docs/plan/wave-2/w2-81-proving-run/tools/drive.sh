#!/usr/bin/env bash
# W2-81 proving run on 0.1.4: starts one Sonnet adopter per repository, at most two at a time, each start under the
# resource gate. Usage: drive.sh   (run detached). State: <run>/driver/<repo>.{pid,status}; logs in <run>/outputs/<repo>/logs/.
set -u
RUN=/home/usain/gov-os-runs/W2-81/run-0.1.4
TOOLS=/home/usain/gov-os-runs/W2-81/tools-0.1.4
PATHV=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin
REPOS=(python-app rust-workspace typescript-monorepo legacy-docs secret-history python-app-clean)
mkdir -p "$RUN/driver"
ticket() { python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]["coordination"])' "$RUN/setup.json" "$1"; }
start() {
  local r=$1 t; t=$(ticket "$r")
  mkdir -p "$RUN/outputs/$r/logs"
  (
    cd "$RUN/repos/$r" || exit 2
    env -i PATH="$PATHV" HOME="$HOME" LANG=C.UTF-8 GOV_ROLE=orchestrator GOV_TICKET="$t" \
      claude -p "$(cat "$TOOLS/brief.md")" --model claude-sonnet-5-5 --effort high --output-format json \
      --permission-mode bypassPermissions > "$RUN/outputs/$r/logs/adopter-session.json" 2> "$RUN/outputs/$r/logs/adopter-session.err"
    echo "$?" > "$RUN/driver/$r.exit"
    date -u +%FT%TZ > "$RUN/driver/$r.ended"
  ) &
  echo $! > "$RUN/driver/$r.pid"; date -u +%FT%TZ > "$RUN/driver/$r.started"
  echo "$(date -u +%FT%TZ) started $r pid $(cat "$RUN/driver/$r.pid")" >> "$RUN/driver/driver.log"
}
running() { local n=0 r; for r in "${REPOS[@]}"; do [ -f "$RUN/driver/$r.pid" ] && [ ! -f "$RUN/driver/$r.exit" ] && n=$((n+1)); done; echo $n; }
for r in "${REPOS[@]}"; do
  while :; do
    if [ "$(running)" -lt 2 ] && env -i PATH="$PATHV" HOME="$HOME" gov resources --check >/dev/null 2>&1; then break; fi
    sleep 30
  done
  start "$r"; sleep 20
done
wait
echo "$(date -u +%FT%TZ) all ended" >> "$RUN/driver/driver.log"
