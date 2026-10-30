#!/usr/bin/env bash
# The test lock for a lead's full run (owner, DEC-954: closes take it ahead of any lead's full run).
#   bash verify_lock.sh <the run's command and arguments>
# While a close wants the lock (/tmp/gov-os-close-wants-lock names a live process), wait; then take
# /tmp/gov-os-verify.lock; if a close asked for it in the meantime, give it back and wait again. The command runs
# without the lock's descriptor, so nothing it leaves behind can keep the lock. Exits with the command's code.
FLAG=/tmp/gov-os-close-wants-lock
LOCK=/tmp/gov-os-verify.lock
close_waiting() {
  [ -e "$FLAG" ] || return 1
  pid=$(cat "$FLAG" 2>/dev/null)
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && return 0
  return 1  # a stale flag (its close has ended) is ignored
}
while true; do
  while close_waiting; do sleep 20; done
  exec 9>>"$LOCK"
  flock 9
  if close_waiting; then
    flock -u 9
    exec 9>&-
    sleep 20
    continue
  fi
  break
done
"$@" 9>&-
rc=$?
flock -u 9
exit $rc
