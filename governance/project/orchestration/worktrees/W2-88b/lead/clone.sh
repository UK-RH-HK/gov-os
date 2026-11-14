#!/usr/bin/env bash
# W2-88b clones (the lead, outside the sandbox; network). Copies only, under ~/gov-os-runs/W2-88b/ (P2 (a)).
set -u
L=/home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/lead
R=/home/usain/gov-os-runs/W2-88b
export GIT_OPTIONAL_LOCKS=0
mkdir -p "$R/github" "$R/logs"
echo "start $(date -Is)"
# ~/workspace: F2 snapshot, local clone (no hardlinks, reads only), F2 snapshot again
python3 -I "$L/snapshot.py" /home/usain/workspace "$L/f2-workspace-before-2.json"
git clone --no-hardlinks --quiet /home/usain/workspace "$R/workspace" ; echo "workspace clone rc=$?"
python3 -I "$L/snapshot.py" /home/usain/workspace "$L/f2-workspace-after-clone.json"
python3 -I - "$L/f2-workspace-before-2.json" "$L/f2-workspace-after-clone.json" <<'PY'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:])
keys = ["paths", "mtime_digest", "head", "git_status_sha256", "git_status_lines"]
print("F2 workspace unchanged by the clone:", all(a[k] == b[k] for k in keys), {k: (a[k], b[k]) for k in keys if a[k] != b[k]})
PY
# GitHub: full clones, then pin
clone() { # name url commit
  git clone --quiet "$2" "$R/github/$1" && git -C "$R/github/$1" checkout --quiet --detach "$3"
  echo "$1 rc=$? head=$(git -C "$R/github/$1" rev-parse HEAD) files=$(git -C "$R/github/$1" ls-files | wc -l) commits=$(git -C "$R/github/$1" rev-list --count HEAD) du=$(du -sb "$R/github/$1" | cut -f1)"
}
clone redis https://github.com/redis/redis.git ee8e7f70152404649ac947157fd662d11b4a00d5
clone grafana https://github.com/grafana/grafana.git a00ff430d41e74022eb54361c9741e224e150021
echo "workspace head=$(git -C "$R/workspace" rev-parse HEAD) files=$(git -C "$R/workspace" ls-files | wc -l) du=$(du -sb "$R/workspace" | cut -f1)"
echo "end $(date -Is)"
