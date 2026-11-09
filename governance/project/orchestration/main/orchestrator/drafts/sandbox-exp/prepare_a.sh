#!/usr/bin/env bash
# SANDBOX-GUARD-EXP-1, set-up A's place (the declaration §6): the reviewed rehearsals' clone with a substituted home,
# the live hook copied byte for byte. Changes nothing live. Plants NO protected content of any kind: set-up A is
# scored from the hook's own decision on each action's words (the declaration §7), so no file the actions name needs
# to exist. What it makes, under ~/gov-os-runs/SANDBOX-GUARD-EXP-1 (marked by its .sandbox-exp-a file):
#   home/                                 the substituted home: the hook and the runner run with HOME set to it, and
#                                         every action's /home/usain spelling is rewritten onto it (common.rewrite)
#   home/Dynamic-Agentic-Engineering-OS   a --no-hardlinks clone at the pinned commit; origin set to the main tree's
#                                         URL (a local setting: no fetch), so the real main tree is no tree root
#   home/gov-os-worktrees/<name>          for each name in A/trees.txt: a detached worktree of the clone at the pin,
#                                         sparse (.claude, governance, .tickets, template/governance) so each
#                                         session's CLAUDE_PROJECT_DIR holds its map and tickets
#   home/gov-os-eval/governance/project/path-map.yaml
#                                         the sets root's own map: the clone's evaluation_sets block mirrored (names
#                                         and globs only), as both reviewed rehearsals plant it; nothing else
#   home/gov-os-runs/                     empty
#   A/manifest-prepare.txt                the pin, the copied files' sha256s against the live ones, the live hashes
# Usage:
#   bash prepare_a.sh [--dry] [--commit <sha>]      default commit: the main tree's HEAD now (recorded)
#   bash prepare_a.sh check                         the clone's copies against the live files, and the live hashes
# It re-runs itself from a fresh shell (env -i), as the reviewed rehearsals do. Never opens the real sets root.
set -u
if [ -z "${SGX_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="$PATH" LANG="${LANG:-C.UTF-8}" \
    SGX_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
EXP=${SGX_EXP:-$HOME/gov-os-runs/SANDBOX-GUARD-EXP-1}
PH=$EXP/home
R=$PH/Dynamic-Agentic-Engineering-OS
A=$EXP/A
LIVE_HOOKS=".claude/hooks/pretooluse.py .claude/hooks/role_reads.py .claude/hooks/bash_writes.py"
LIVE_FILES="$LIVE_HOOKS governance/project/path-map.yaml governance/project/held-out.yaml .claude/settings.json"
SPARSE=".claude governance .tickets template/governance"
DRY=0; COMMIT=""; MODE=prepare
while [ $# -gt 0 ]; do
  case "$1" in
    --dry) DRY=1 ;;
    --commit) COMMIT=$2; shift ;;
    check) MODE=check ;;
    *) echo "unknown argument: $1"; exit 2 ;;
  esac
  shift
done
FAILS=0
bad() { echo "PREPARE FAIL: $*"; FAILS=$((FAILS + 1)); }
live_hashes() { ( cd "$MAIN" && sha256sum $LIVE_FILES ); }

check_copies() {
  local ok=1 f
  for f in $LIVE_FILES; do
    if ! cmp -s "$MAIN/$f" "$R/$f"; then echo "differs from live: $f"; ok=0; fi
  done
  [ $ok = 1 ] && echo "copies: byte for byte as live ($(echo $LIVE_FILES | wc -w) files)" || bad "a copy differs from live"
}

if [ $MODE = check ]; then
  [ -d "$R" ] || { echo "no clone at $R"; exit 2; }
  check_copies; live_hashes | cut -c1-12,65-; exit $FAILS
fi

[ -n "$COMMIT" ] || COMMIT=$(git -C "$MAIN" rev-parse HEAD)
PIN=$(head -1 "$HOME/.local/bin/gov" | cut -c3-)
TREES=$( [ -f "$A/trees.txt" ] && grep -cv '^\s*$' "$A/trees.txt" || echo 0)
echo "prepare A: commit ${COMMIT:0:12}, pin $PIN, home $PH, worktrees listed $TREES"
if [ $DRY = 1 ]; then
  echo "dry: would clone $MAIN at ${COMMIT:0:12} into $R, copy $(echo $LIVE_FILES | wc -w) live files," \
       "add $TREES sparse worktrees, mirror the evaluation_sets block; nothing written"
  exit 0
fi

if [ -e "$PH" ]; then
  [ -f "$EXP/.sandbox-exp-a" ] || { echo "PREPARE STOP: $PH exists and is not this script's"; exit 3; }
  git -C "$R" worktree prune 2>/dev/null
  rm -rf "$PH"
fi
mkdir -p "$EXP" "$A" "$PH/gov-os-worktrees" "$PH/gov-os-runs" && : > "$EXP/.sandbox-exp-a"
live_hashes > "$A/live-before.txt"
git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; exit 1; }
git -C "$R" checkout -q --detach "$COMMIT" || { bad "checkout $COMMIT"; exit 1; }
git -C "$R" remote set-url origin "$(git -C "$MAIN" remote get-url origin)"   # local setting only; nothing fetched
for f in $LIVE_FILES; do cp -p "$MAIN/$f" "$R/$f"; done
check_copies
n=0
if [ -f "$A/trees.txt" ]; then
  while read -r name; do
    [ -n "$name" ] || continue
    case "$name" in */*|.*) bad "tree name $name"; continue ;; esac
    wt=$PH/gov-os-worktrees/$name
    git -C "$R" worktree add -q --detach --no-checkout "$wt" "$COMMIT" || { bad "worktree $name"; continue; }
    git -C "$wt" sparse-checkout set --no-cone $SPARSE >/dev/null 2>&1 || bad "sparse $name"
    git -C "$wt" read-tree -mu HEAD || bad "checkout $name"
    for f in $LIVE_FILES; do mkdir -p "$wt/$(dirname "$f")"; cp -p "$MAIN/$f" "$wt/$f"; done
    n=$((n + 1))
  done < "$A/trees.txt"
fi
mkdir -p "$PH/gov-os-eval/governance/project"
python3 - "$R/governance/project/path-map.yaml" "$PH/gov-os-eval/governance/project/path-map.yaml" <<'EOF'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, l in enumerate(lines) if l.startswith("evaluation_sets:")][0]
end = next(j for j in range(at + 1, len(lines)) if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r"))
open(sys.argv[2], "w").write("# the sets root's own map for set-up A: the repository's evaluation_sets, mirrored\n" +
                              "".join(l for l in lines[at:end] if not l.startswith("#")))
EOF
{
  echo "commit $COMMIT"
  echo "pin $PIN"
  echo "worktrees $n"
  echo "clone files (sha256):"; ( cd "$R" && sha256sum $LIVE_FILES )
  echo "live files (sha256):"; cat "$A/live-before.txt"
} > "$A/manifest-prepare.txt"
echo "prepared: clone at $(git -C "$R" rev-parse --short=12 HEAD), $n worktrees; manifest $A/manifest-prepare.txt"
live_hashes | cmp -s - "$A/live-before.txt" && echo "live: unchanged" || bad "a live file changed"
echo "failures: $FAILS"
exit $FAILS
