#!/usr/bin/env bash
# Scratch probe (never committed): the W1-40 openspec case with its fixture line flipped to RED / non-zero exit,
# in a copy whose repo root links back to W2-45's tree.
R=/home/usain/gov-os-worktrees/W2-45
X=/tmp/gov-os-lead-W2-45/w140probe
rm -rf $X; mkdir -p $X/tests/acceptance
for p in src template governance lefthook.yml .github pyproject.toml docs; do [ -e $R/$p ] && ln -s $R/$p $X/$p; done
cp $R/tests/acceptance/conftest.py $X/tests/acceptance/
cp -r $R/tests/acceptance/W1-40 $X/tests/acceptance/W1-40
rm -rf $X/tests/acceptance/W1-40/__pycache__
python3 /home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/w1-40-flip.py $X/tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py
diff $R/tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py $X/tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py
mkdir -p /tmp/gov-os-lead-W2-45/w140tmp
export TMPDIR=/tmp/gov-os-lead-W2-45/w140tmp PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$R/src
export HOME=$R/.gov-runtime/scratch/empty-home
cd $X
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -p no:xdist --rootdir $X \
  tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py 2>&1 | tail -15
