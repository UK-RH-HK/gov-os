#!/usr/bin/env bash
# The close queue in one quiet window (DEC-780, DEC-806), with the pre-close gate (DEC-868):
#   hold the leads with the close lock and wait until their running batches have ended; then for each ticket:
#   (c) a fresh `gov checkpoint --ticket` record, committed; the full rebuild; (a) `pytest --collect-only` over
#   the whole tests folder in one process, as the close runs it; (b) `gov check`, with no commit since the
#   rebuild; and only then `gov close`, once. Any gate failure stops the queue before the close, with its cause.
#   The queue stops at the first refusal. Usage: close_queue.sh <tk id> [<tk id> ...]. Literal paths only.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
LOG=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-queue-$(date +%Y%m%d-%H%M)
LOCK=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
mkdir -p "$LOG"
date '+%F %T close queue: lock set' > "$LOCK"
quiet=0
while [ "$quiet" -lt 5 ]; do
  if awk '{exit !($1 < 3)}' /proc/loadavg; then quiet=$((quiet + 1)); else quiet=0; fi
  sleep 60
done
date '+%F %T quiet' >> "$LOG/queue.txt"
for item in "$@"; do
  # An item is <tk id> or <tk id>:<DEC-n>, the owner's decision that lifts the ticket's escalation (DEC-862 (a)).
  ticket=${item%%:*}; lift=""
  [ "$item" != "$ticket" ] && lift="--owner-decision ${item#*:}"
  stop() { date '+%F %T '"$ticket"' STOPPED BEFORE THE CLOSE: '"$1" >> "$LOG/queue.txt"; rm -f "$LOCK"; exit 2; }
  # (c) a fresh checkpoint of the ticket, committed before the rebuild.
  gov checkpoint --ticket "$ticket" --role orchestrator --trigger ticket-transition \
    --next "gov close $ticket (pre-close gate passed)" --json > "$LOG/checkpoint-$ticket.json" 2>&1 || stop "gov checkpoint failed"
  git add docs/checkpoints/ && git commit -q -m "$ticket: checkpoint before its close (DEC-868)" \
    --trailer "Task: $ticket" --trailer "Role: orchestrator" \
    --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/checkpoints/ \
    > "$LOG/checkpoint-commit-$ticket.txt" 2>&1 || stop "the checkpoint could not be committed"
  date '+%F %T rebuild before '"$ticket" >> "$LOG/queue.txt"
  gov rebuild > "$LOG/rebuild-$ticket.json" 2> "$LOG/rebuild-$ticket.err" || stop "gov rebuild failed"
  # (a) collection, in one process, as the close runs the regression (its environment: the tree's src).
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src \
    python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$LOG/collect-$ticket.txt" 2>&1
  code=$?
  if [ "$code" -ne 0 ] || grep -q -E '^ERROR|errors? during collection' "$LOG/collect-$ticket.txt"; then
    stop "collection failed (exit $code): $(grep -E '^ERROR' "$LOG/collect-$ticket.txt" | head -3 | tr '\n' ' ')"
  fi
  date '+%F %T collect ok: '"$(tail -1 "$LOG/collect-$ticket.txt")" >> "$LOG/queue.txt"
  # (b) gov check after the rebuild, no commit in between.
  gov check --json > "$LOG/check-$ticket.json" 2> "$LOG/check-$ticket.err" || stop "gov check is not green (exit $?)"
  # (d) the working tree is the commit being closed: nothing modified, staged or untracked (TREE_NOT_COMMITTED).
  dirty=$(git status --porcelain | head -5 | tr '\n' ' ')
  [ -z "$dirty" ] || stop "the working tree is not clean: $dirty"
  date '+%F %T check ok; close '"$ticket"' (load '"$(cut -d' ' -f1 /proc/loadavg)"')' >> "$LOG/queue.txt"
  gov close "$ticket" $lift --json > "$LOG/close-$ticket.json" 2> "$LOG/close-$ticket.err"; code=$?
  echo "$code" > "$LOG/close-$ticket.exit"
  date '+%F %T close '"$ticket"' exit '"$code" >> "$LOG/queue.txt"
  [ "$code" -eq 0 ] || break
done
rm -f "$LOCK"
date '+%F %T lock removed' >> "$LOG/queue.txt"
