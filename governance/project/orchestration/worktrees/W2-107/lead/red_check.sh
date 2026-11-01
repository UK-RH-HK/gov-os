#!/bin/bash
# The red check: the merged acceptance tests run against the ticket's base (the tests branch = base + tests), in a
# scratch clone, to their end. Writes the result under /tmp/gov-os-lead-W2-107/red.*
set -u
export TMPDIR=/tmp/gov-os-lead-W2-107
C=/tmp/gov-os-lead-W2-107/red-clone
git clone -q --no-hardlinks --branch w2/W2-107-tests /home/usain/gov-os-worktrees/W2-107 "$C"
git -C "$C" log --oneline -1 > /tmp/gov-os-lead-W2-107/red.head
cd "$C" && PYTHONPATH="$C/src" python3 -c "import gov; print(gov.__file__)" > /tmp/gov-os-lead-W2-107/red.govfile
cd "$C" && PYTHONPATH="$C/src" python3 -m pytest tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/tmp/gov-os-lead-W2-107/red.xml > /tmp/gov-os-lead-W2-107/red.out 2>&1
echo $? > /tmp/gov-os-lead-W2-107/red.exit
