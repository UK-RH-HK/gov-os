#!/usr/bin/env bash
# P2-AR-0029 — compare the audit-of-record probe outputs before (base 843d79c export) and after (this worktree) line by
# line: every `[..]`/`##` observation line and every AC16-X3 `X` verdict, with absolute scratch paths, 32-64 hex
# digests and ISO timestamps normalised (payload digests differ between the trees by construction).
# Usage: compare-probes.sh <before-label> <after-label>   (writes COMPARE-probes-<before>-vs-<after>.out here)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
B="$HERE/probes-$1"; A="$HERE/probes-$2"; OUT="$HERE/COMPARE-probes-$1-vs-$2.out"
norm() { grep -E '^\[|^##|^X |exit=' "$1" | sed -E 's#/tmp/[^ ]*##g; s/[0-9a-f]{32,64}/H/g; s/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+Z/T/g' | cut -c1-400; }
{
  echo "# before: $B"; echo "# after:  $A"
  for p in A2-01 A2-02 A2-03 A2-04 A2-05 A2-08 S5-update S6-cross-machine AC16-X3; do
    echo; echo "=================== $p (exit before: $(tail -1 "$B/$p.out") | after: $(tail -1 "$A/$p.out"))"
    diff <(norm "$B/$p.out") <(norm "$A/$p.out") && echo "(identical after normalisation)"
  done
} > "$OUT"
echo "$OUT"
