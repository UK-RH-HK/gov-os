#!/usr/bin/env bash
# DEC-963: the integration branch's store for test designers' retrieval, double-buffered so it never answers
# "stale" while it rebuilds. ~/gov-os-worktrees/W2-00-store is a link to the ready one of two detached worktrees
# (-a, -b) at w2/integrate's head; this builds the other at the current head and switches the link only on success.
# Run after code merges.   bash refresh_integration_store.sh [--force]
W=/home/usain/gov-os-worktrees
LINK=$W/W2-00-store
LOG=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/integration-store.log
want=$(git -C /home/usain/Dynamic-Agentic-Engineering-OS rev-parse w2/integrate)
cur=$(readlink -f "$LINK")
if [ "$1" != "--force" ] && [ "$(git -C "$cur" rev-parse HEAD)" = "$want" ]; then echo "fresh at ${want:0:12} ($cur)"; exit 0; fi
case "$cur" in *-a) next=$W/W2-00-store-b ;; *) next=$W/W2-00-store-a ;; esac
git -C "$next" checkout -q --detach "$want" || exit 2
cd "$next" || exit 2
t0=$(date +%s)
PYTHONPATH="$next/src" flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG.json" 2> "$LOG.err"
rc=$?
if [ "$rc" = 0 ]; then ln -sfn "$next" "$LINK.tmp" && mv -T "$LINK.tmp" "$LINK"; fi
echo "$(date '+%F %T') built ${want:0:12} in $(basename "$next") rc=$rc in $(( $(date +%s) - t0 )) s; link -> $(basename "$(readlink -f "$LINK")")" | tee -a "$LOG"
exit $rc
