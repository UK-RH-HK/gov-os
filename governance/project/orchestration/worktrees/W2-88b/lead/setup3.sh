#!/usr/bin/env bash
# W2-88b run 3 (DEC-1176 (2)): the copies in the ticket's layout ~/gov-os-runs/W2-88b/<name>/, logs in <name>-logs/.
# Removes run 2's superseded outputs (its ~/workspace clone and every file that names it, the stand-in-verdict run's
# results), all of them this ticket's own outputs under its own runs folder; no original is touched.
set -u
R=/home/usain/gov-os-runs/W2-88b
cd "$R" || exit 2
echo "setup3 start $(date -Is)"
rm -rf "$R/workspace" "$R/out" "$R/results" "$R/work" "$R/logs" "$R/clone.log"
# grafana: run 2's clone was only read (MA writes nothing in the repository); it stands at the pinned commit
mv "$R/github/grafana" "$R/grafana"
git -C "$R/grafana" checkout --quiet --detach a00ff430d41e74022eb54361c9741e224e150021
# redis: run 2's clone carries the stand-in run's commits: a fresh local copy at the pinned commit, then the old one goes
git clone --no-hardlinks --quiet "$R/github/redis" "$R/redis"
git -C "$R/redis" checkout --quiet --detach ee8e7f70152404649ac947157fd662d11b4a00d5
git -C "$R/redis" remote set-url origin https://github.com/redis/redis.git
rm -rf "$R/github"
for n in grafana redis; do
  mkdir -p "$R/$n-logs"
  echo "$n head=$(git -C "$R/$n" rev-parse HEAD) files=$(git -C "$R/$n" ls-files | wc -l) status_lines=$(git -C "$R/$n" status --porcelain --ignored | wc -l) origin=$(git -C "$R/$n" remote get-url origin) refs_gov=$(git -C "$R/$n" for-each-ref refs/gov | wc -l)"
done
echo "setup3 end $(date -Is)"
