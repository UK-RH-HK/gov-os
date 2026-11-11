#!/bin/bash
# Shared setup of the rehearsal of ACT-PATHMAP-EXP-1 (sourced by rehearse-1.sh and rehearse-2.sh). The live tree is only read.
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts
ME=$D/pathmap-exp-1/ACT-PATHMAP-EXP-1
EX=$D/examin-sets/ACT-EXAMIN-SETS-1
RD=$D/accepted-reds-1/acts/ACT-ACCEPTED-REDS-1
C=/home/usain/gov-os-runs/W2-00/pathmap-exp-1/clone
export TMPDIR=/home/usain/gov-os-runs/W2-00/pathmap-exp-1/tmp
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
MAP=governance/project/path-map.yaml
T1='tests/unit/retrieval/test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_one_namespace'
T2='tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace'
n=${N:-0}; fail=${FAIL:-0}
step() { echo; echo "## $*"; }
expect() { # expect <label> <wanted exit> <command...>
  local label="$1" want="$2"; shift 2
  out="$("$@" 2>&1)"; rc=$?
  echo "\$ $*"; [ -n "$out" ] && echo "$out" | head -8
  n=$((n+1))
  if [ "$rc" = "$want" ]; then echo "  [ok] $label: exit $rc"; else echo "  [FAIL] $label: exit $rc, wanted $want"; fail=$((fail+1)); fi
}
h() { sha256sum "$1" | cut -c1-12; }
cd "$C" || exit 9
