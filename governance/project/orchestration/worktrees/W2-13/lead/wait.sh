#!/bin/bash
# wait.sh <max seconds> <file>...: returns as soon as any named file holds a session's final JSON ("result")
# or is a non-empty exit file, or after <max seconds>. Prints which file is done, or "timeout".
max=$1; shift
end=$(( $(date +%s) + max ))
while [ "$(date +%s)" -lt "$end" ]; do
  for f in "$@"; do
    if [ -s "$f" ]; then
      case "$f" in
        *.exit) echo "done: $f"; exit 0 ;;
        *) if grep -q '"result"' "$f" 2>/dev/null; then echo "done: $f"; exit 0; fi ;;
      esac
    fi
  done
  sleep 20
done
echo timeout
