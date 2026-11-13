#!/usr/bin/env bash
# Base-red check 2: the w2_153 pair (and the backstop) on the integrate side of this branch's base (33b5651eb, the
# second parent of 1d13922ef) and on w2/integrate's head now (ae806c3fe); detached worktrees, removed after.
set -u
T=/home/usain/gov-os-worktrees/W2-124
L=$T/.gov-runtime/scratch/lead/log
OUT=$L/base-check-2.txt
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
mkdir -p /tmp/w2-124-lead $T/.gov-runtime/scratch/empty-home
: > "$OUT"
for rev in 33b5651eb ae806c3fe; do
  B=/home/usain/gov-os-worktrees/W2-124-base-$rev
  git -C "$T" worktree add --detach "$B" "$rev" >> "$OUT" 2>&1
  git -C "$B" log --oneline -1 >> "$OUT"
  cd "$B" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src \
    bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
    "tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition" \
    "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition" \
    "tests/unit/resources/test_w2_157_backstop.py" 2>&1 | tail -8 >> "$OUT"
  echo "base $rev exit ${PIPESTATUS[0]}" >> "$OUT"
  cd "$T" && git -C "$T" worktree remove --force "$B" >> "$OUT" 2>&1
done
echo done > "$L/base-check-2.exit"
