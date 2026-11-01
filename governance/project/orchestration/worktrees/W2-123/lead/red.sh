#!/bin/bash
# red.sh <tree> <out folder>: run tests/acceptance/W2-123 file by file against <tree>/src (one file is not heavy).
tree=$1; out=$2
mkdir -p "$out"
cd "$tree" || exit 2
for f in tests/acceptance/W2-123/test_*.py; do
  name=$(basename "$f" .py)
  PYTHONPATH="$tree/src" TMPDIR=/tmp/gov-os-lead-W2-123 python3 -m pytest "$f" -q -p no:cacheprovider \
    -o tmp_path_retention_policy=failed -rfE --tb=line --junitxml="$out/$name.xml" > "$out/$name.log" 2>&1
  echo "$name exit $? : $(tail -1 "$out/$name.log")"
done
PYTHONPATH="$tree/src" python3 -c "import gov; print(gov.__file__)"
