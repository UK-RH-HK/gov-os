#!/usr/bin/env bash
# Run 3's proof: the W2-172 acceptance suite from a clone under a folder named `runs`, then in the worktree.
set -u
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
T=/tmp/gov-w2-172-lead3
EH=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home
OUT=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/lead/log/proof3
mkdir -p "$T/pt1" "$T/pt2" "$EH" "$OUT"
rm -rf "$T/gov-os-runs"
git clone -q /home/usain/gov-os-worktrees/W2-172 "$T/gov-os-runs/x/clone" && git -C "$T/gov-os-runs/x/clone" fetch -q origin w2/integrate:w2/integrate && git -C "$T/gov-os-runs/x/clone" checkout -q --detach origin/w2/W2-172 && git -C "$T/gov-os-runs/x/clone" merge -q --no-ff --no-edit w2/integrate
C="$T/gov-os-runs/x/clone"
echo "clone head (detached candidate merge with w2/integrate, as the queue): $(git -C "$C" rev-parse --short=12 HEAD) in $C" | tee "$OUT/clone.txt"
cd "$C" && TMPDIR="$T/pt1" bash "$HS" env HOME="$EH" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$C/src" python3 -m pytest "$C/tests/acceptance/W2-172" "$C/tests/acceptance/W2-171/test_w2_171_f5_paths.py" "$C/tests/acceptance/W2-170/test_w2_170_f5_paths.py" -q -rs -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --junitxml="$OUT/clone-junit.xml" >> "$OUT/clone.txt" 2>&1
echo "clone rc=$?" >> "$OUT/clone.txt"
W=/home/usain/gov-os-worktrees/W2-172
echo "tree head: $(git -C "$W" rev-parse --short=12 HEAD)" > "$OUT/tree.txt"
cd "$W" && TMPDIR="$T/pt2" bash "$HS" env HOME="$EH" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$W/src" python3 -m pytest tests/acceptance/W2-172 tests/acceptance/W2-171/test_w2_171_f5_paths.py tests/acceptance/W2-170/test_w2_170_f5_paths.py -q -rs -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --junitxml="$OUT/tree-junit.xml" >> "$OUT/tree.txt" 2>&1
echo "tree rc=$?" >> "$OUT/tree.txt"
tail -3 "$OUT/clone.txt"; tail -3 "$OUT/tree.txt"
