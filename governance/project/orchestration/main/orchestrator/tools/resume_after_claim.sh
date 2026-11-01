#!/usr/bin/env bash
# A lead refused at its first launch because its claim was not committed (2026-11-01, the CTO's slip): merge
# w2/integrate (which now holds the committed claim) into its worktree, build a resume brief from its first brief, and
# append it to a chain spec. Usage: resume_after_claim.sh <W2> <ticket id> <first brief file> <chain spec>
set -eu
W2=$1; ID=$2; FIRST=$3; SPEC=$4
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
WT=/home/usain/gov-os-worktrees/$W2
MSG=$(mktemp)
printf 'Merge w2/integrate into w2/%s: its claim, committed (the CTO'"'"'s slip of 2026-11-01)\n\nTask: %s\nRole: orchestrator\n' "$W2" "$ID" > "$MSG"
git -C "$WT" merge -q --no-ff -F "$MSG" w2/integrate
grep -q '^status: in_progress' "$WT/.tickets/$ID.md" || { echo "the claim is not in $WT" >&2; exit 3; }
H=$(git -C "$WT" rev-parse --short=12 HEAD)
OUT=$O/briefs/$W2-A5-resume-claim.md
{
  printf '# %s (%s): resume after LAUNCH_BLOCKED (the claim was not committed: the CTO'"'"'s slip)\n\n' "$W2" "$ID"
  printf '**Read this first.** Your first run was refused at its first launch because the CTO had not committed the claim. The claim is now committed and merged into this branch (head `%s`; the ticket reads in_progress). Resume from `.gov-runtime/scratch/lead/CHECKPOINT.md`: your briefs are ready; relaunch the worker(s) as planned. Rebuilds now take a heavy-job slot with the tree'"'"'s own lock (DEC-1001): `bash %s/tools/rebuild_slot.sh <tree>`, never `flock /tmp/gov-os-rebuild.lock`.\n\n---\n\n' "$H" "$O"
  cat "$FIRST"
} > "$OUT"
echo "$W2 $ID $(basename "$OUT") $W2-A5-resume-claim.json" >> "$SPEC"
echo "$W2 at $H; brief $OUT"
