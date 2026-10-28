#!/usr/bin/env bash
# cron's entry for the nightly (owner, standing, DEC-933 item 2, DEC-934). The owner's crontab runs it at 02:00:
#   0 2 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_cron.sh
#
# 1. Committed, reviewed code only: it refuses to run (a P1) unless this folder in the main tree is exactly its
#    commit at HEAD (no change, nothing staged, no untracked file). What runs is what was committed and reviewed.
# 2. The environment of a session, not cron's bare one: HOME, a UTF-8 locale, and the PATH the closes run with
#    (~/.local/bin for gov, rulesync, gitleaks and claude; nvm's node; the system's), so no test skips because
#    cron could not find a tool.
# 3. Logs, never discards: everything it and the nightly print goes to log/nightly/cron/<date>.log in the
#    orchestrator's scratch; rotate.sh keeps the logs under their budget before each run.
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
HERE=$REPO/governance/project/orchestration/nightly
ORCH=$REPO/.gov-runtime/scratch/orchestrator
LOGDIR=$ORCH/log/nightly/cron
PING=/home/usain/.local/bin/owner-ping
export HOME=/home/usain
export LANG=C.UTF-8
export PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v18.20.8/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/wsl/lib
mkdir -p "$LOGDIR"
exec >> "$LOGDIR/$(date +%F).log" 2>&1
echo "== $(date '+%F %T') nightly_cron: start"
REL=governance/project/orchestration/nightly
if ! git -C "$REPO" diff --quiet HEAD -- "$REL" || [ -n "$(git -C "$REPO" ls-files --others --exclude-standard -- "$REL")" ]; then
  echo "REFUSED: $REL in the main tree is not its commit at HEAD; the nightly does not run"
  git -C "$REPO" status --short -- "$REL"
  "$PING" "P1 NIGHTLY-NOT-RUN | the nightly's code differs from its commit | the orchestrator's package follows"
  exit 2
fi
echo "code: $REL at $(git -C "$REPO" log -1 --format=%h -- "$REL"), tree $(git -C "$REPO" rev-parse --short=12 "HEAD:$REL")"
bash "$HERE/rotate.sh"
bash "$HERE/nightly.sh" night
code=$?
echo "== $(date '+%F %T') nightly_cron: end, exit $code"
exit "$code"
