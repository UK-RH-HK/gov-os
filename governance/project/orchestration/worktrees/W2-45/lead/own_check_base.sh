#!/usr/bin/env bash
# Lead: this repository's own gov check at the tree's head (S2/S3/S4 reds by check id), JSON to the log folder.
cd /home/usain/gov-os-worktrees/W2-45 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/lead/log
env TMPDIR=/tmp/gov-os-lead-W2-45 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-45-tests/src \
  python3 -m gov.cli.main check --json --root /home/usain/gov-os-worktrees/W2-45 > "$OUT/own-check-$1.json" 2> "$OUT/own-check-$1.err"
echo "exit $?" > "$OUT/own-check-$1.exit"
python3 - "$OUT/own-check-$1.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
body = d.get("result") or (d.get("error") or {}).get("details") or {}
print("top time_limit_s:", body.get("time_limit_s"))
for c in body.get("checks", []):
    codes = [f.get("code") for f in c.get("findings", []) if isinstance(f, dict)]
    if c.get("status") != "GREEN":
        print(c["id"], c.get("severity"), c.get("status"), c.get("elapsed_s"), c.get("time_limit_s"), codes[:6])
EOF
