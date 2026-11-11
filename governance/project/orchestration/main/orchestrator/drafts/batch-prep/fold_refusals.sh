#!/usr/bin/env bash
# Folds each `gov brief` refusal (briefs/<W2>-<step>.md.err) into briefs/<W2>-<step>.md, a finding, not a brief.
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/briefs
cd "$D" || exit 1
for e in *.md.err; do
  base="${e%.err}"
  w2step="${base%.md}"
  {
    echo "# REFUSED, not a brief: gov brief lead ${w2step%%-*}-${w2step#*-} (live pin pin-797495bdfc70), 2026-11-11"
    echo
    echo "Command: \`gov brief lead <ticket> --run <kind>\` from the main tree (the file name is \`<W2>-<kind>\`). Exit 1, nothing on stdout. Its stderr, copied:"
    echo
    echo '```'
    cat "$e"
    echo '```'
  } > "$base"
  rm -f "$e" "$base.out"
done
ls -1
