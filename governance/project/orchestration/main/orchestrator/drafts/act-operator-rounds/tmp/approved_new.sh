#!/usr/bin/env bash
# scratch: print the APPROVED sha apply.sh will write (apply.sh's own approved_sha, sourced from its text)
set -euo pipefail
A=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-operator-rounds/apply.sh
eval "$(sed -n '/^OLD_VERDICT=/,/^LIVE_APPROVED_BEFORE=/p' "$A")"
eval "$(sed -n '/^KEEP=/,/win_toast.ps1"$/p' "$A")"
eval "$(sed -n '/^approved_text()/,/^approved_sha()/p' "$A")"
echo "before: $(approved_sha "$OLD_VERDICT" "$OLD_RUN")"
echo "after:  $(approved_sha "$NEW_VERDICT" "$NEW_RUN")"
