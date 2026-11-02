#!/usr/bin/env bash
# DEC-963: the integration branch's store for test designers' retrieval, double-buffered so it never answers
# "stale" while it rebuilds. ~/gov-os-worktrees/W2-00-store is a link to the ready one of two detached worktrees
# (-a, -b) at w2/integrate's head; this builds the other at the current head and switches the link only on success.
# DEC-1032 (iv): after a landing the merge queue promotes the landed result's stores into the standby half instead
# (merge_queue.py promote); this refresh is the fallback (a skipped run, a moved head, a failed promotion), the twice-
# daily check (store_refresh_daily.sh) and the by-hand run. It shares one lock with the promotion (<link>.lock; the
# queue's re-runs in the ready half hold it shared), and rebuilds through seed_store.py: in a heavy-job slot with the
# tree's own lock (DEC-1001 (d), not the old machine-wide lock), incrementally on the half's own stores, or seeded
# from the ready half when it has none; "ok" with the semantic store not recreated is a failure (exit 75): the link
# stays. GOV_STORE_LINK, GOV_STORE_REPO, GOV_STORE_REF: the merge queue's and the tests' (default: this machine's).
#   bash refresh_integration_store.sh [--force]
HERE=$(cd "$(dirname "$0")" && pwd)
W=/home/usain/gov-os-worktrees
LINK=${GOV_STORE_LINK:-$W/W2-00-store}
REPO=${GOV_STORE_REPO:-/home/usain/Dynamic-Agentic-Engineering-OS}
REF=${GOV_STORE_REF:-w2/integrate}
LOG=${GOV_STORE_LOG:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/integration-store.log}
exec 9>>"$LINK.lock"
if ! flock -w "${GOV_STORE_LOCK_WAIT:-7200}" 9; then
  echo "$(date '+%F %T') not refreshed: the store's lock ($LINK.lock) was held past the wait" | tee -a "$LOG"; exit 3
fi
want=$(git -C "$REPO" rev-parse "$REF")
cur=$(readlink -f "$LINK")
if [ "$1" != "--force" ] && [ "$(git -C "$cur" rev-parse HEAD)" = "$want" ]; then echo "fresh at ${want:0:12} ($cur)"; exit 0; fi
case "$cur" in *-a) next=$LINK-b ;; *) next=$LINK-a ;; esac
git -C "$next" checkout -q --detach "$want" || exit 2
cd "$next" || exit 2
t0=$(date +%s)
python3 "$HERE/seed_store.py" rebuild "$next" --base "$cur" --who "refresh $(basename "$next")" > "$LOG.json" 2> "$LOG.err"
rc=$?
if [ "$rc" = 0 ]; then ln -sfn "$next" "$LINK.tmp" && mv -T "$LINK.tmp" "$LINK"; fi
echo "$(date '+%F %T') built ${want:0:12} in $(basename "$next") rc=$rc in $(( $(date +%s) - t0 )) s; link -> $(basename "$(readlink -f "$LINK")")" | tee -a "$LOG"
exit $rc
