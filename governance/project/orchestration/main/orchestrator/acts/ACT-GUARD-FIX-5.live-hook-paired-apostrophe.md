# The live hook's paired-apostrophe fail-open (W2-42a's P-03ub-APOS-2 (i), the CTO, 2026-11-13)

Found by W2-42a's test designer (td-4, b7112b6ca, 312 cases): in the live hook (`.claude/hooks/bash_writes.py`), an
engineer's write to `tests/acceptance/` placed between two comments that each hold an apostrophe, in a `bash` heredoc
body, is not seen (the two apostrophes read as one quoted span that hides the write). The product guard had the same
gap (part of the 50 fail-open cases W2-42a's fix closes). Same family as ACT-GUARD-FIX-5's F1 and F2. The owner's
coverage holds: the end-of-session check names any change outside a worker's paths (DEC-789) until the live hook copies
W2-42a's fixed parser by one ACT (DEC-1174 (1)). No sign of use. Recorded under (i); the fix is the guard's priority.
