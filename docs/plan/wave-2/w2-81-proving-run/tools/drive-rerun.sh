#!/usr/bin/env bash
# W2-81 proving run, the re-run: starts one Sonnet adopter per repository, at most two at a time, each start under the
# resource gate (drive.sh of the 0.1.4 run, with the three changes of adopter-brief-rerun.md section 7).
#   RELEASE=<version> GOV_MSG_ADDRESS=<the starter's address> drive-rerun.sh      (run detached)
# State: <run>/driver/<repo>.{pid,status,exit,ended}; logs in <run>/outputs/<repo>/logs/.
#   - GOV_MSG_ADDRESS is required: it is the address of whoever starts the run, and is given to every adopter, so that no
#     session the run launches ends with a message to an inbox that is not the starter's (2026-11-20: 29 end messages
#     went to the live CTO's inbox because the scrubbed environment dropped it and the launcher defaults to `cto`).
#   - HOME is the operator's real one (the adopter's and the landing's pytest resolve there).
#   - PATH holds ~/.nvm/versions/node/v22.23.3/bin after ~/.local/bin, so `ccusage` (tool-registry.yaml, 20.0.26) resolves.
set -u
: "${RELEASE:?set RELEASE to the release the run measures}"
: "${GOV_MSG_ADDRESS:?set GOV_MSG_ADDRESS to the address of whoever starts the run (refused without it)}"
RUN=/home/usain/gov-os-runs/W2-81/run-$RELEASE
TOOLS=/home/usain/gov-os-runs/W2-81/tools-$RELEASE
PATHV=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin
REPOS=(python-app rust-workspace typescript-monorepo legacy-docs secret-history python-app-clean)
mkdir -p "$RUN/driver"
ticket() { python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]["coordination"])' "$RUN/setup.json" "$1"; }
start() {
  local r=$1 t; t=$(ticket "$r")
  mkdir -p "$RUN/outputs/$r/logs"
  (
    cd "$RUN/repos/$r" || exit 2
    env -i PATH="$PATHV" HOME="$HOME" LANG=C.UTF-8 GOV_ROLE=orchestrator GOV_TICKET="$t" GOV_MSG_ADDRESS="$GOV_MSG_ADDRESS" \
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
