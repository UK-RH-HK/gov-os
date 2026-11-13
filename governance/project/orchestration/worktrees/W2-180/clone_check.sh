#!/usr/bin/env bash
# Spot check of the real cases (not the planted ones) in a clone of the head under /tmp: the head checked out as the
# branch w2/W2-170, as w2/W2-173, and detached. On its own branch each case judges the head's diff (which touches both
# folders, so each sees the other's folder as outside its paths and must fail); detached, each must skip.
set -u
C=/tmp/w2-180-clone-check
OUT=/home/usain/gov-os-worktrees/W2-180/.gov-runtime/scratch/lead/log/clone-check.txt
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
HEAD=$(git -C /home/usain/gov-os-worktrees/W2-180 rev-parse HEAD)
rm -rf "$C"
git clone -q --no-checkout /home/usain/gov-os-worktrees/W2-180 "$C"
git -C "$C" branch -q w2/integrate origin/w2/integrate
mkdir -p "$C.home"
run() {
  ( cd "$C" && env HOME="$C.home" PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH="$C/src" \
    bash "$HS" python3 -m pytest -q -rs -p no:cacheprovider -o tmp_path_retention_policy=failed \
    "tests/acceptance/W2-170/test_w2_170_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows" \
    "tests/acceptance/W2-173/test_w2_173_unchanged.py::test_f3_the_branch_changes_no_template_path_map_guard_approved_list_or_set_up_a_brief" \
    "tests/acceptance/W2-173/test_w2_173_unchanged.py::test_f4_the_branch_changes_only_the_ticket_s_paths" 2>&1 \
    | grep -E "^(FAILED|PASSED|SKIPPED|ERROR)|passed|failed|skipped|^E +(AssertionError|assert)" | cut -c1-300 )
}
{
  echo "clone of head ${HEAD:0:12}; w2/integrate $(git -C "$C" rev-parse --short=12 w2/integrate); $(date -u +%FT%TZ)"
  for b in w2/W2-170 w2/W2-173; do
    git -C "$C" checkout -q -B "$b" "$HEAD"
    echo "--- checked out as the branch $b"
    run
  done
  git -C "$C" checkout -q --detach "$HEAD"
  echo "--- detached HEAD at the head"
  run
}  > "$OUT" 2>&1
rm -rf "$C" "$C.home"
cat "$OUT"
