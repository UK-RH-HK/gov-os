#!/usr/bin/env bash
# The two code-graph PATH reds of lead_verify at 9f4878987, re-run alone (a) in this tree and (b) in an exported copy
# of the same head at a path with no "W2-37" component, to show conftest.py:566's match on the absolute path's parts.
set -u
C=/home/usain/gov-os-tmp/p7-pathcheck/tree
T=/home/usain/gov-os-tmp/p7-pathcheck/tmp
L=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/p7
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
H=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/empty-home
CASES="tests/acceptance/W2-56/test_w2_56_suite_daemon.py::test_s1_the_code_graph_tool_is_off_path_in_a_suite_other_than_w1_16_and_w1_20 tests/unit/codeintel/test_codeintel.py::test_the_running_suite_has_a_folder_of_its_own_and_no_code_graph_tool_on_path"
rm -rf /home/usain/gov-os-tmp/p7-pathcheck
mkdir -p "$C" "$T"
git -C /home/usain/gov-os-worktrees/W2-37 archive 9f4878987 | tar -x -C "$C"
git -C "$C" init -q && git -C "$C" add -A && git -C "$C" -c user.name=p7 -c user.email=p7@localhost commit -qm export
cd /home/usain/gov-os-worktrees/W2-37
env TMPDIR="$T" HOME="$H" PYTHONUSERBASE=/home/usain/.local PATH="/home/usain/.local/bin:$PATH" \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash "$HS" python3 -m pytest $CASES \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf > "$L/pathcheck-tree.txt" 2>&1
echo "tree exit=$?"; tail -4 "$L/pathcheck-tree.txt"
cd "$C"
env TMPDIR="$T" HOME="$H" PYTHONUSERBASE=/home/usain/.local PATH="/home/usain/.local/bin:$PATH" \
  PYTHONPATH="$C/src" bash "$HS" python3 -m pytest $CASES \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf > "$L/pathcheck-copy.txt" 2>&1
echo "copy exit=$?"; tail -4 "$L/pathcheck-copy.txt"
