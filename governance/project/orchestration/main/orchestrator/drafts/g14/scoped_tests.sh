#!/usr/bin/env bash
# ACT-G14's scoped tests: a path-map change is in the test selection's shared core (it selects everything), so the
# ACT runs instead the unit tests that name governance/project/path-map.yaml (35 files, 747 tests on 2026-11-03),
# in the main tree, through the heavy slot. Usage: bash scoped_tests.sh   (prints pytest's last line)
set -u
M=/home/usain/Dynamic-Agentic-Engineering-OS
T=$M/.gov-runtime/scratch/orchestrator/tools
cd "$M" || exit 1
mapfile -t files < <(grep -rl "path-map.yaml" tests/unit --include=*.py | sort)
echo "scoped files: ${#files[@]}"
mkdir -p /tmp/gov-os-act-g14
PYTHONPATH=$M/src TMPDIR=/tmp/gov-os-act-g14 bash "$T/heavy_slot.sh" python3 -m pytest -q -n 6 \
  -o tmp_path_retention_policy=failed -p no:cacheprovider "${files[@]}" 2>&1 | tail -n 1
