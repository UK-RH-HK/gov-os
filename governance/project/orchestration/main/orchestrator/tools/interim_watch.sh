#!/usr/bin/env bash
# Leads' interim results (owner, standing, DEC-952): every 2 minutes, each worktree's new commits since last seen; a
# commit whose subject reads as a key result (a baseline, a measure, figures, a finding, a probe record, a research
# record, a package) wakes the orchestrator: it prints the worktree, commit and subject, records it as seen in
# log/interim-seen.txt, and exits. Re-arm after each. The first run of a worktree marks its history seen silently.
SEEN=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/interim-seen.txt
touch "$SEEN"
KEY='baseline|measure|figures|hit@5|finding|probe record|research record|the record|PACKAGE|returns? PACKAGES'
while true; do
  for wt in /home/usain/gov-os-worktrees/*/; do
    name=$(basename "$wt")
    [ -e "$wt/.git" ] || continue
    if ! grep -q "^$name " "$SEEN"; then
      for c in $(git -C "$wt" log --format=%h -50 2>/dev/null); do echo "$name $c" >> "$SEEN"; done
      continue
    fi
    for c in $(git -C "$wt" log --format=%h -20 2>/dev/null); do
      grep -qxF "$name $c" "$SEEN" && continue
      echo "$name $c" >> "$SEEN"
      subj=$(git -C "$wt" log -1 --format=%s "$c")
      if echo "$subj" | grep -Eqi "$KEY"; then
        echo "$(date '+%F %T') $name $c $subj"
        exit 0
      fi
    done
  done
  sleep 120
done
