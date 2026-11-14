# ACT-GUARD-FIX-5 withdrawn (DEC-1174 (1), owner, 2026-11-13)

Round 2 (manifest ef9078eb) failed its last review on F1, confirmed by the CTO's run (`reviews/act-guard-fix-5-f1-run.md`):
an apostrophe in a heredoc body's comment opened the whole call. The owner chose (b): W2-42a's merged parser is tested
for the case, then the live hook is brought to it as one ACT. The product parser refuses the four F1 calls (fails
closed) but also refuses harmless heredocs with an apostrophe in a comment, so it is fixed first in W2-42a's scope
(DEC-1164 (18)). Never queue this bundle. Records: `ACT-GUARD-FIX-5.review-round-1.md`, `ACT-GUARD-FIX-5.review-round-2.md`.
