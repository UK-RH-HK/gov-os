#!/usr/bin/env bash
T=/home/usain/gov-os-worktrees/W2-157
cd "$T" || exit 2
env HOME="$T/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/src" \
  python3 -c "import sys; from gov.cli.main import main; sys.exit(main(sys.argv[1:]))" accept W2-157 --root "$T" \
  > "$T/.gov-runtime/scratch/accept-157.out" 2>&1
echo "exit $?" >> "$T/.gov-runtime/scratch/accept-157.out"
