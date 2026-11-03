#!/usr/bin/env bash
# The CTO's checkpoint, written straight to .gov-runtime/scratch/checkpoints/<ticket>/ (the writer's "automatic"
# destination, DEC-444, the one the Stop hook uses), never under docs/checkpoints/ and never moved by hand (owner,
# 2026-11-02 ~16:20, DEC-1038: two slips that day came from moving `gov checkpoint`'s file). The CTO does not run
# `gov checkpoint` in the main tree; it runs this.
#     bash cto_checkpoint.sh "<next action>" [<input path> ...]
# Prints the record's path. Exits 1, naming the paths, if anything under docs/checkpoints/ changed.
set -euo pipefail
R=${CTO_CHECKPOINT_ROOT:-/home/usain/Dynamic-Agentic-Engineering-OS}
TICKET=${CTO_CHECKPOINT_TICKET:-DAEO-sdxk}
PY=$(head -1 "${CTO_CHECKPOINT_GOV:-$HOME/.local/bin/gov}" | sed 's/^#!//')
[ -n "${1:-}" ] || { echo "usage: cto_checkpoint.sh \"<next action>\" [input ...]" >&2; exit 2; }
before=$(git -C "$R" status --porcelain -- docs/checkpoints)
out=$(cd "$R" && "$PY" -E - "$R" "$TICKET" "$@" <<'EOF'
import sys
from pathlib import Path
from gov.checkpoint.record import write
root, ticket, nxt, inputs = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4:]
r = write(root, ticket, "stop", nxt, inputs, dest="automatic")
print(r.get("path") if isinstance(r, dict) else r)
EOF
)
after=$(git -C "$R" status --porcelain -- docs/checkpoints)
[ "$before" = "$after" ] || { echo "CHECKPOINT WROTE UNDER docs/checkpoints/: $after" >&2; exit 1; }
case "$out" in *.gov-runtime/scratch/checkpoints/*) echo "$out";; *) echo "unexpected path: $out" >&2; exit 1;; esac
