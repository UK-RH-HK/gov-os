#!/usr/bin/env bash
# The rehearsal of re-pin window 3 (DEC-1057: every ACT rehearsed end to end before the hand-over), changing nothing
# live: REPIN-COMMANDS-8284fb408bd4.sh runs as the operator will, but with its GOV_REPIN_* paths in a scratch mirror:
#   <S>/home/.local/bin/gov -> <S>/home/.local/share/gov-os/pin-9894b0cf/bin/gov (that folder a link to the live pin,
#   only read); <S>/home/gov-os-worktrees/W2-00-store{-a,-b} shared clones of the main tree at the live halves'
#   commits with copies of their stores (SQLite's backup; the live halves only read), the link on -a as live;
#   <S>/repo a shared clone for the registry commit; <S>/hold the CTO's hold.
# The real HOME stays: the shared reranker (~/.cache/gov-os/rerank.sock) and the machine-wide vector cache are the
# operator's, so the counts and times are the ones the operator will see (the vector cache keeps what the rehearsal
# embeds: the operator's re-embed then takes those vectors from it).
#     bash rehearse_repin5.sh [<scratch dir, default /tmp/gov-os-emg-repin3/r>]
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
O=$R/.gov-runtime/scratch/orchestrator/pin
S=${1:-/tmp/gov-os-emg-repin3/r}
LIVE=/home/usain/gov-os-worktrees
[ ! -e "$S" ] || { echo "$S exists: remove it first"; exit 2; }
mkdir -p "$S/home/.local/bin" "$S/home/.local/share/gov-os" "$S/home/gov-os-worktrees" "$S/tmp"
ln -s /home/usain/.local/share/gov-os/pin-9894b0cf "$S/home/.local/share/gov-os/pin-9894b0cf"
ln -s "$S/home/.local/share/gov-os/pin-9894b0cf/bin/gov" "$S/home/.local/bin/gov"
for h in a b; do
  src=$LIVE/W2-00-store-$h; dst=$S/home/gov-os-worktrees/W2-00-store-$h
  git clone -q --shared --no-checkout "$R" "$dst"
  git -C "$dst" checkout -q --detach "$(git -C "$src" rev-parse HEAD)"
  mkdir -p "$dst/.gov-runtime"
  for db in store.db query-vector-cache.db; do
    python3 - "$src/.gov-runtime/$db" "$dst/.gov-runtime/$db" <<'EOF'
import sqlite3, sys
a = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True); b = sqlite3.connect(sys.argv[2]); a.backup(b); b.close(); a.close()
EOF
  done
  cp -a "$src/.gov-runtime/codeintel" "$src/.gov-runtime/rebuild" "$dst/.gov-runtime/"
  echo "half $h: $(git -C "$dst" rev-parse --short=12 HEAD), store $(du -sh "$dst/.gov-runtime" | cut -f1)"
done
ln -s "$S/home/gov-os-worktrees/W2-00-store-$(readlink -f "$LIVE/W2-00-store" | sed 's/.*-//')" "$S/home/gov-os-worktrees/W2-00-store"
: > "$S/home/gov-os-worktrees/W2-00-store.lock"
git clone -q --shared "$R" "$S/repo"
echo "registry clone at $(git -C "$S/repo" rev-parse --short=12 HEAD) on $(git -C "$S/repo" branch --show-current)"
echo "rehearsal of re-pin window 3, $(date '+%F %T')" > "$S/hold"
echo "mirror ready: gov -> $(readlink "$S/home/.local/bin/gov"); store -> $(readlink "$S/home/gov-os-worktrees/W2-00-store")"
echo "======== the operator's script, against the mirror"
t0=$(date +%s)
rc=0
env GOV_REPIN_LINK_HOME="$S/home" GOV_REPIN_PINS="$S/home/.local/share/gov-os" \
    GOV_REPIN_STORE_LINK="$S/home/gov-os-worktrees/W2-00-store" GOV_REPIN_REGISTRY_REPO="$S/repo" \
    GOV_REPIN_HOLD="$S/hold" GOV_REPIN_TMP="$S/x" GOV_STORE_LOG="$S/integration-store.log" SEED_LOG="$S/seed.jsonl" \
    TMPDIR="$S/tmp" bash "$O/REPIN-COMMANDS-8284fb408bd4.sh" || rc=$?
echo "======== the script ended: exit $rc, $(( $(date +%s) - t0 )) s"
echo "the live gov link: $(readlink -f /home/usain/.local/bin/gov)"
echo "the live store link: $(readlink -f $LIVE/W2-00-store) at $(git -C "$(readlink -f $LIVE/W2-00-store)" rev-parse --short=12 HEAD)"
echo "the live pins: $(ls /home/usain/.local/share/gov-os | tr '\n' ' ')"
exit $rc
