td-pin2-1 (session 37c7bdce-0b08-42f6-b1eb-800d3e4170c9, claude-sonnet-5-5, high, C2): DONE, commit ed0e54dfecfb6b1f6dfebefcfec360f599923f10.
Its launch logs (td-pin2-1.json/.summary/.exit/.tripwire.json) were under /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/lead/log/
and went with `git worktree remove` of the tests worktree; this note keeps what the lead read from them before the removal.
- summary: session exit 0; tripwire CHANGED: tests-tree head 67364dbea2fb -> ed0e54dfecfb and acceptance folder W2-130 (its own commit, its paths); sandbox trial file absent.
- step 0: sandbox trial write refused (read-only fs); git hash-object/update-index ok; no ollama/llama.
- pytest: changed files 24 passed; tests/acceptance/W2-130 81 passed; tests/acceptance/W2-175 51 passed; collect-only: 24 README-mapped ids collect.
- pinned tool: 3 S4 cases, S8 counts + left (measured_at), S8 before-counts (232efc47d), 2 propose-sources cases (parent).
- variant_findings (F3) left on the branch's tool (README line 61 and test_w2_130_audit.py say "HEAD's tool").
- planted: counts-after UNKNOWN_ID 56->55 (S8 counts red); left.D-9 DAEO-03dg 7->8 (S8 left red); drop DAEO-057v W2-H021 (S4 case 1); add W2-H998 (case 3 and 2); via W2-H021->W2-H022 (case 2); modified src first on PYTHONPATH: 8 pinned cases green, HEAD-wide S2 case red.
- discoveries: closed_missing and no_record S4 cases still read HEAD; red on a close/reopen (DAEO-057v closed; DAEO-03dg reopened) or a new unknown id (DEC-99999).
- proposed: pin variant_findings' tool; pin or re-baseline the two HEAD-reading S4 cases (recommend pin, medium-high).
