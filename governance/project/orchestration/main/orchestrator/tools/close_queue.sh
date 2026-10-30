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
PENDING=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-PENDING
# DEC-942 item 4: closes first. CLOSE-PENDING holds new leads until the first close starts (the lead chain reads it);
# it goes on every exit.
date '+%F %T close queue: '"$*" > "$PENDING"
trap 'rm -f "$PENDING"' EXIT
date '+%F %T close queue: lock set' > "$LOCK"
# One verification run at a time (DEC-942 item 5): the queue holds the verification lock for its whole run, so a
# running full run ends first and none starts beside the closes. Then quiet (the 1-minute load below 3 for 5 minutes,
# no nightly), for at most 20 minutes: closes never starve for a quiet window (item 4); the start load is logged.
exec 9> /tmp/gov-os-verify.lock
date '+%F %T waiting for the verification lock' >> "$LOG/queue.txt"
flock 9
date '+%F %T verification lock held' >> "$LOG/queue.txt"
quiet=0; waited=0
while [ "$quiet" -lt 5 ] && [ "$waited" -lt 20 ]; do
  if [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ] && awk '{exit !($1 < 3)}' /proc/loadavg; then quiet=$((quiet + 1)); else quiet=0; fi
  sleep 60; waited=$((waited + 1))
done
while [ -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
date '+%F %T quiet ('"$quiet"' quiet minutes of '"$waited"'; load '"$(cut -d' ' -f1-3 /proc/loadavg)"')' >> "$LOG/queue.txt"
for item in "$@"; do
  # An item is <tk id> or <tk id>:<DEC-n>, the owner's decision that lifts the ticket's escalation (DEC-862 (a)).
  ticket=${item%%:*}; lift=""
  [ "$item" != "$ticket" ] && lift="--owner-decision ${item#*:}"
  stop() { date '+%F %T '"$ticket"' STOPPED BEFORE THE CLOSE: '"$1" >> "$LOG/queue.txt"; rm -f "$LOCK"; exit 2; }
  # After a clean close, a stop leaves its outputs uncommitted; it says so (2026-10-29: it was labelled "before").
  stop_after() { date '+%F %T '"$ticket"' STOPPED AFTER THE CLOSE (exit 0), OUTPUTS NOT COMMITTED: '"$1" >> "$LOG/queue.txt"; rm -f "$LOCK"; exit 3; }
  # DEC-898: free disk space and free inodes above the floor, or no close.
  disk=$(bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh 2>&1) || stop "$disk"
  # (c) a fresh checkpoint of the ticket, committed before the rebuild.
  gov checkpoint --ticket "$ticket" --role orchestrator --trigger ticket-transition \
    --next "gov close $ticket (pre-close gate passed)" --json > "$LOG/checkpoint-$ticket.json" 2>&1 || stop "gov checkpoint failed"
  git add docs/checkpoints/ && git commit -q -m "$ticket: checkpoint before its close (DEC-868)" \
    --trailer "Task: $ticket" --trailer "Implements: DEC-868" --trailer "Role: orchestrator" \
    --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/checkpoints/ \
    > "$LOG/checkpoint-commit-$ticket.txt" 2>&1 || stop "the checkpoint could not be committed"
  date '+%F %T rebuild before '"$ticket" >> "$LOG/queue.txt"
  # DEC-939 item 2 (ii), interim until W2-76: one store rebuild at a time on the machine.
  flock /tmp/gov-os-rebuild.lock gov rebuild > "$LOG/rebuild-$ticket.json" 2> "$LOG/rebuild-$ticket.err" || stop "gov rebuild failed"
  # DEC-911 (b): row W2-L423's early warning, after the rebuild so the stores are as the check will read them; a file
  # holding the rule's keyword stops the queue before any close is spent (paths only; the backstop is gate (b), (e)).
  python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py \
    > "$LOG/keyword-warn-$ticket.txt" 2>&1 || stop "row W2-L423's early warning: $(head -5 "$LOG/keyword-warn-$ticket.txt" | tr '\n' ' ')"
  # (a) collection, in one process, as the close runs the regression (its environment: the tree's src).
  # The full listing goes to a temp file and only its errors and summary are kept: test ids can hold row W2-L423's
  # keywords (W2-69's own case names one), and the log lives under .gov-runtime/ (DEC-911, DEC-923).
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src \
    python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /tmp/gov-os-queue-collect.txt 2>&1
  code=$?
  { grep -E '^ERROR|errors? during collection' /tmp/gov-os-queue-collect.txt; tail -1 /tmp/gov-os-queue-collect.txt; } > "$LOG/collect-$ticket.txt"
  rm -f /tmp/gov-os-queue-collect.txt
  if [ "$code" -ne 0 ] || grep -q -E '^ERROR|errors? during collection' "$LOG/collect-$ticket.txt"; then
    stop "collection failed (exit $code): $(grep -E '^ERROR' "$LOG/collect-$ticket.txt" | head -3 | tr '\n' ' ')"
  fi
  date '+%F %T collect ok: '"$(tail -1 "$LOG/collect-$ticket.txt")" >> "$LOG/queue.txt"
  # (f) the suites that read the records themselves (the register, the path map, the registry, the record copies),
  # which the orchestrator's own record commits can turn red (DEC-882, DEC-885): stop before the close, uncounted.
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src \
    python3 -m pytest -q -p no:cacheprovider --no-header tests/acceptance/W1-06/test_w1_06_approvals.py \
    tests/acceptance/W1-08/test_w1_08_path_map.py tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py \
    tests/acceptance/W1-07/test_w1_07_envelope.py > "$LOG/records-$ticket.txt" 2>&1 \
    || stop "a suite that reads the records is red: $(grep -E '^FAILED|^ERROR' "$LOG/records-$ticket.txt" | head -3 | tr '\n' ' ')"
  date '+%F %T records ok: '"$(tail -1 "$LOG/records-$ticket.txt")" >> "$LOG/queue.txt"
  # (g) DEC-892: the live tests' allowlisted hosts are reachable; if not, hold and retry (every 10 min, up to 6 times),
  # rather than spend a close on a network failure (W2-63's close of 2026-10-22, static.crates.io).
  tries=0
  until python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/net_check.py > "$LOG/net-$ticket.txt" 2>&1; do
    tries=$((tries + 1))
    date '+%F %T network not ready ('"$tries"'): '"$(grep unreachable "$LOG/net-$ticket.txt" | head -3 | tr '\n' ' ')" >> "$LOG/queue.txt"
    [ "$tries" -ge 6 ] && stop "the allowlisted hosts stayed unreachable for an hour: $(grep unreachable "$LOG/net-$ticket.txt" | tr '\n' ' ')"
    sleep 600
  done
  date '+%F %T network ok: '"$(tail -1 "$LOG/net-$ticket.txt")" >> "$LOG/queue.txt"
  # (b) gov check after the rebuild, no commit in between.
  gov check --json > "$LOG/check-$ticket.json" 2> "$LOG/check-$ticket.err" || stop "gov check is not green (exit $?)"
  # (e) every commit of the ticket (Task: <id>) carries Implements: (the close's trailer gate, TRAILER_MISSING),
  # unless the path map's accepted_history names it.
  # As the close reads it (_check_trailers): the trailers base, the accepted history, and DEC-436's merges that add
  # nothing (W2-62's stop of 2026-10-21 named two such merges beside its claim commit).
  missing=$(PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 \
    /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/trailer_gate.py "$ticket" 2>&1) \
    || stop "commits of $ticket lack a trailer, as the close reads them: $(echo "$missing" | tail -n +2 | tr '\n' ' ')"
  # (h) the close's work-without-a-task gate, with the pinned judge's code (W2-58's refused close of 2026-10-22).
  # The interpreter is read from the pinned gov's own first line, so the gate follows every re-pin (DEC-922).
  pinpy=$(head -1 /home/usain/.local/bin/gov | sed 's/^#!//')
  [ -x "$pinpy" ] || stop "the pinned gov names no interpreter that runs: $pinpy"
  unmeasured=$("$pinpy" -E \
    /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/unmeasured_gate.py "$ticket" 2>&1) \
    || stop "work without a task in $ticket's range, as the close reads it: $(echo "$unmeasured" | head -4 | tr '\n' ' ')"
  # (d) the working tree is the commit being closed: nothing modified, staged or untracked (TREE_NOT_COMMITTED).
  # Read as the close reads it (gov.close.repo.tree_differences): a file ignored only by an uncommitted .gitignore
  # counts (W2-02's refused close of 2026-10-21), which git status does not show.
  # The tool's own exit decides (2026-10-29): a pipe through head hid a crash, so the gate passed on no output.
  PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 \
    /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/tree_diff.py "$ticket" \
    > "$LOG/tree-$ticket.txt" 2>&1 \
    || stop "the working tree is not the commit, as the close reads it, or the tool failed (exit $?): $(head -5 "$LOG/tree-$ticket.txt" | tr '\n' ' ')"
  date '+%F %T check ok; close '"$ticket"' (load '"$(cut -d' ' -f1 /proc/loadavg)"')' >> "$LOG/queue.txt"
  # W2-66 (DEC-889 item 2, P-IS-2 (a)): the close's record-reading tests read gate (b)'s own gov check result.
  rm -f "$PENDING"
  gov close "$ticket" $lift --check-result "$LOG/check-$ticket.json" --json > "$LOG/close-$ticket.json" 2> "$LOG/close-$ticket.err"; code=$?
  echo "$code" > "$LOG/close-$ticket.exit"
  date '+%F %T close '"$ticket"' exit '"$code" >> "$LOG/queue.txt"
  # Owner 2026-10-27: a refused close must end the queue with a non-zero status (it was `break`, then exit 0).
  [ "$code" -eq 0 ] || { date '+%F %T '"$ticket"' CLOSE REFUSED (exit '"$code"'); queue stopped' >> "$LOG/queue.txt"; rm -f "$LOCK"; exit 4; }
  # The interim skip guard (owner, DEC-899 item 7), until W2-57 lands: the full regression's skip count must be the
  # expected 31, or the queue stops here, before the close's outputs are committed (a silent rulesync skip, I4 F2).
  skips=$(python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_gate.py "$LOG/close-$ticket.json" 2>&1) \
    || { date '+%F %T '"$ticket"' STOPPED AFTER THE CLOSE, OUTPUTS NOT COMMITTED: '"$skips" >> "$LOG/queue.txt"; rm -f "$LOCK"; exit 3; }
  date '+%F %T '"$skips" >> "$LOG/queue.txt"
  # A clean close leaves its ticket file and close record uncommitted; commit them, so that the next ticket's
  # gate (d) finds a clean tree (as W2-53's outputs were committed, a1565e56).
  git add ".tickets/$ticket.md" "docs/close/$ticket/" "docs/checkpoints/$ticket/" > "$LOG/outputs-$ticket.txt" 2>&1 || stop_after "the close's outputs could not be staged"
  gitleaks git --staged --redact --no-banner --config .gitleaks.toml . >> "$LOG/outputs-$ticket.txt" 2>&1 || stop_after "gitleaks flagged the close's outputs"
  git commit -q -m "$ticket closed by gov close (exit 0, $(date '+%F %H:%M')): the ticket, its close record and its closing checkpoint" \
    --trailer "Task: $ticket" --trailer "Implements: DEC-868" --trailer "Role: orchestrator" \
    --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- ".tickets/$ticket.md" "docs/close/$ticket/" "docs/checkpoints/$ticket/" \
    >> "$LOG/outputs-$ticket.txt" 2>&1 || stop_after "the close's outputs could not be committed"
  date '+%F %T outputs of '"$ticket"' committed: '"$(git log -1 --format=%h)" >> "$LOG/queue.txt"
done
rm -f "$LOCK"
date '+%F %T lock removed' >> "$LOG/queue.txt"
