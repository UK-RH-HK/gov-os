#!/usr/bin/env bash
# Lead's red triage for W2-23 verify (head 01a1770ce53c): base run of the non-W2-96 reds, and the W2-96 signal cases alone.
set -u
TREE=/home/usain/gov-os-worktrees/W2-23
BASE=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/base
OUT=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/lead/log
mkdir -p /tmp/gov-os-lead-W2-23
[ -d "$BASE" ] || git -C "$TREE" worktree add --detach "$BASE" 219307d1d > /dev/null 2>&1
CASES=(
 "tests/acceptance/W1-26/test_w1_26_probe_records.py"
 "tests/acceptance/W1-08/test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records"
 "tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository"
 "tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace"
 "tests/unit/retrieval/test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_one_namespace"
 "tests/acceptance/W1-41/test_w1_41_migration.py::test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay"
)
cd "$BASE" && env HOME=$TREE/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$BASE/src TMPDIR=/tmp/gov-os-lead-W2-23 \
  timeout 900 python3 -m pytest "${CASES[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed > "$OUT/base-reds.txt" 2>&1
echo "base exit $?: $(tail -n 1 "$OUT/base-reds.txt")"
cd "$TREE" && env HOME=$TREE/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$TREE/src TMPDIR=/tmp/gov-os-lead-W2-23 \
  timeout 900 python3 -m pytest tests/unit/accept/test_w2_96_review3.py tests/unit/accept/test_w2_96_review4.py tests/unit/accept/test_w2_96_run2.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" > "$OUT/w2-96-alone.txt" 2>&1
echo "w2-96 alone exit $?: $(tail -n 1 "$OUT/w2-96-alone.txt")"
git -C "$TREE" worktree remove --force "$BASE" && echo "base worktree removed"
