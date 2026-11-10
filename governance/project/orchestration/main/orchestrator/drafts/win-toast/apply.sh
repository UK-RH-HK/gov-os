#!/usr/bin/env bash
# ACT-WIN-TOAST-1 (DEC-1112 (3), the CTO's delegated item 4, 2026-11-10): tools/win_toast.ps1 out of the test map's
# record_only list, since deadman.py runs it (W2-66's D-10 review, F2).
#   bash apply.sh check   the map hashes as built (before or after); changes nothing
#   bash apply.sh apply   a backup with its sha256, then the map replaced by test-map.candidate.yaml, then the hash after
#   bash apply.sh undo    the map back byte for byte from the backup
# One file changes: governance/project/test-map.yaml. Its record_only line for win_toast.ps1 becomes a comment that
# says why; nothing else changes. It changes only the tree it sits in (found from its own place:
# <tree>/.gov-runtime/scratch/orchestrator/drafts/win-toast/). It commits nothing: the operator's commit follows.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
MAP=governance/project/test-map.yaml
BEFORE=42e22dd70a05546e99fd7f2503c109a417ee6d1c11ebfddc42dfee5ff8f1a665
AFTER=45e785d12b14ff0f7e4c52507f4c529f2fff3e488c15864ec20bc53f17c2d348
BACKUP=$HERE/backup
sum() { sha256sum "$1" | cut -d' ' -f1; }
state() {
  local now; now=$(sum "$ROOT/$MAP")
  if [ "$now" = "$BEFORE" ]; then echo before
  elif [ "$now" = "$AFTER" ]; then echo applied
  else echo "unknown ($now)"; fi
}
cmd=${1:-}
case "$cmd" in
  check)
    [ "$(sum "$HERE/test-map.candidate.yaml")" = "$AFTER" ] || { echo "check: the candidate is not as built" >&2; exit 1; }
    s=$(state); echo "state $s"
    case "$s" in before) echo "check: ready to apply";; applied) echo "check: already applied";; *) echo "check: the map changed since this ACT was built; rebuild it" >&2; exit 1;; esac ;;
  apply)
    [ "$(state)" = before ] || { echo "apply: the map is not in the state this ACT was built on: $(state)" >&2; exit 1; }
    [ "$(sum "$HERE/test-map.candidate.yaml")" = "$AFTER" ] || { echo "apply: the candidate is not the reviewed one; nothing changed" >&2; exit 1; }
    mkdir -p "$BACKUP"; cp -p "$ROOT/$MAP" "$BACKUP/test-map.yaml"; sum "$BACKUP/test-map.yaml" > "$BACKUP/test-map.yaml.sha256"
    cp "$HERE/test-map.candidate.yaml" "$ROOT/$MAP"
    [ "$(state)" = applied ] || { cp -p "$BACKUP/test-map.yaml" "$ROOT/$MAP"; echo "apply: the result is not the reviewed map; restored the backup" >&2; exit 1; }
    echo "state $(state)" ;;
  undo)
    [ -f "$BACKUP/test-map.yaml" ] || { echo "undo: no backup" >&2; exit 1; }
    [ "$(sum "$BACKUP/test-map.yaml")" = "$(cat "$BACKUP/test-map.yaml.sha256")" ] || { echo "undo: the backup does not match its hash" >&2; exit 1; }
    [ "$(state)" = applied ] || { echo "undo: the map is not as this ACT left it ($(state)): a later change would be lost; nothing changed (use git revert)" >&2; exit 1; }
    cp -p "$BACKUP/test-map.yaml" "$ROOT/$MAP"
    echo "state $(state)" ;;
  *) echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
