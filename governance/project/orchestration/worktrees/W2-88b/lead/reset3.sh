#!/usr/bin/env bash
# W2-88b run 3: attempt 1 of phase pre was killed by the harness ~20 s after the launching call returned (no stage
# failed). Its logs are kept under aborted-1/; each copy goes back to its pinned commit, with no refs/gov ref left.
set -u
R=/home/usain/gov-os-runs/W2-88b
mkdir -p "$R/aborted-1"
for pair in redis:ee8e7f70152404649ac947157fd662d11b4a00d5 grafana:a00ff430d41e74022eb54361c9741e224e150021; do
  n=${pair%%:*} c=${pair#*:}
  mv "$R/$n-logs" "$R/aborted-1/$n-logs"
  rm -rf "$R/$n-out"
  git -C "$R/$n" reset -q --hard "$c"
  git -C "$R/$n" clean -q -fdx
  for ref in $(git -C "$R/$n" for-each-ref --format='%(refname)' refs/gov); do git -C "$R/$n" update-ref -d "$ref"; done
  mkdir -p "$R/$n-logs"
  echo "$n head=$(git -C "$R/$n" rev-parse HEAD) status_lines=$(git -C "$R/$n" status --porcelain --ignored | wc -l) refs_gov=$(git -C "$R/$n" for-each-ref refs/gov | wc -l)"
done
rm -rf "$R/tmp"
