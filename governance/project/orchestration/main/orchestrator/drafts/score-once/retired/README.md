# Retired 2026-11-08 under DEC-1097 (15): never reuse as they are

live_window.sh, score_once_window.sh and extend_window.sh carry the F1 restore defect: their log pipe (exec > >(tee ...))
dies with the group on Ctrl-C/TERM, so the cleanup trap's writes can break and the live reranker's restore is not
guaranteed. e4_window.sh holds the fix (exec > >(trap '' INT TERM; exec tee -p -a LOG); cleanup under trap '' INT TERM PIPE).
A new window script starts from e4_window.sh, with its own review.
