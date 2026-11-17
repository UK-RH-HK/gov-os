---
name: release-hold-freezes-all-commits
description: "from \"release ready at C\" until the owner says \"released\", NOTHING is committed or landed on w2/integrate (gov release needs HEAD = C); only after \"released\" does the hold narrow to src/ and pyproject.toml until \"done\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-15T05:30:35.514Z
---

On 2026-11-15 I fixed C at bfd38ea1a (05:21), then made two record commits (register marks, two reopens) while the rehearsal ran. P-RELEASE-1 §4 checks `git rev-parse HEAD` = C and runs `gov release` at HEAD, so C had to move to 076cded14 and the full rehearsal was re-run (src/ unchanged).

**Why:** the owner's part 1 refuses if HEAD is not the C I announced. Every commit after the announcement, records included, breaks it. That includes test-only lands and the digests' package commits.

**How to apply:** finish all record commits before announcing. After "release ready at C", until "released": no commit on w2/integrate (`record/w2` syncs are fine, they never move w2/integrate), no land approvals, and the digest's package file is written but committed only after "released". After "released": record commits and non-src lands go on, while src/ and pyproject.toml stay frozen until "done". Related: [[act-in-progress-holds-operator]].

**Untracked files too (11-15 09:32):** part 1 checks `git status --porcelain --untracked-files=all` prints nothing, so a package or record written into the main tree before "released" (even uncommitted) breaks it. Keep such files in `.gov-runtime/scratch/` (ignored) until "released".

**No commit while land.py runs (11-16 01:2x):** I committed P-W2-81-VERDICT-1 while the queue was landing W2-153, which had merged onto the earlier head. Before every commit to w2/integrate, run `pgrep -af land.py` and wait for it to finish. The check belongs in the same Bash line as the commit (`pgrep -f "^/usr/bin/python3 .*tools/land[.]py" && echo WAIT || git commit …`; a bare `pgrep -f land.py` matches the checking shell's own command line and always says WAIT).

**CORRECTED 11-16 08:1x:** the anchored `^/usr/bin/python3 .*tools/land[.]py` misses a land I start myself as `python3 .gov-runtime/scratch/orchestrator/tools/land.py …` (W2-81's land ran unseen; my P-RELEASE-2 and package commits went in beside W2-15a's and W2-81's lands). Use `pgrep -f "python3 [^ ]*tools/land[.]py W2-" >/dev/null && echo WAIT` (the ticket argument appears in every land's command line and never in the checking shell's), and also look for `merge_queue.py run`.
