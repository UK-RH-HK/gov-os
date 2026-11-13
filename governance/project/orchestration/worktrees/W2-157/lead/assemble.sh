#!/usr/bin/env bash
# Assemble td-1.md and eng-1.md: head + interface + the context packet + tail.
set -eu
B=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/briefs
for w in td eng; do
  {
    cat "$B/$w-1.head.md"
    cat "$B/interface.md"
    printf '\nThe ticket'"'"'s context packet (`gov context DAEO-ozyt --role %s --budget 12000`, built by your lead) follows; its `ticket_text` is the same ticket file as above.\n\n```json\n' \
      "$([ $w = td ] && echo independent-test-designer || echo engineer)"
    cat "$B/$w-1.context.md"
    printf '\n```\n'
    cat "$B/$w-1.tail.md"
  } > "$B/$w-1.md"
done
mkdir -p /home/usain/gov-os-worktrees/W2-157-tests/.gov-runtime/scratch/empty-home
grep -n '{[A-Z_]*}' "$B/td-1.md" "$B/eng-1.md" | grep -v '"' | head || true
wc -c "$B/td-1.md" "$B/eng-1.md"
