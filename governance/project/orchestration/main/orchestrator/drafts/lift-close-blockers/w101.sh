#!/usr/bin/env bash
# W1-01's acceptance folder on the rehearsal clone after the owner's commit (it reads acceptance_exemptions), through the heavy gate.
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/lift-close-blockers
R=$D/rehearsal
mkdir -p $D/tmp
cd $R && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$R/src TMPDIR=$D/tmp \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -o tmp_path_retention_policy=failed -p no:cacheprovider --no-header tests/acceptance/W1-01
