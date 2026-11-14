# W2-37 (DAEO-6n5k) closed: hand-merged with its CIT-P at 1.1.0 and P-7, its copies applied, closed by DEC-953's practices

- Hand-merged into w2/integrate by the CTO, 72c6def88: gov impact; the change skill's impact section at version 1.1.0 (CIT-P a25b02a7, the owner's yes, DEC-1166 (4); kernel gate ok on those bytes, cdf43a49); P-7 (a), `impact` in commands.py and W1-07's and W1-32's lists (DEC-812 item 6); W2-37 in `_CBM_SUITES`
- Reviews: the FULL review (READY) and three narrow checks (DEC-1163 (7), version 1.1.0, P-7 (a)), all PASS, committed as `docs/probes/DAEO-6n5k/` (0ee2de2d9)
- Its .claude copies by ACT-CLAUDE-COPIES-9, applied by the operator agent (e437c799c); the landing check after it GREEN (5579 tests, 0 failed)
- Check on w2/integrate at 454771c4e (a clean worktree, through heavy_slot.sh): `gov accept W2-37` pass, 120 passed, 0 failed, 0 skipped (its 21 code-graph cases ran); W2-11 four-places and W1-35 :845, :991: 34 passed
- The merge commit's Task and Role trailers are not parsed (a blank line before the attribution lines; the landing check's P1 on 72c6def88, P1-LANDING-72C6 with the owner); its body names Task: DAEO-6n5k
- Rows (ride along when W2-37 next changes, DEC-802): the count case's rename with tests/optin-lifted-breadth.txt:42 (a test designer); conftest.py:566 matches `_CBM_SUITES` on parts relative to the tests folder (the CTO, DEC-1156 (7))
- Closed: 2026-11-13, by the orchestrator under DEC-953 items 1 and 5, DEC-1132 (1)
