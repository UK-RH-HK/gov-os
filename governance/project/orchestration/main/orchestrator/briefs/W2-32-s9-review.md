# W2-32 S9's cases: independent review, round 1 (DEC-1129 (1), DEC-1131)

Hand-built brief (DEC-1130 (1): W2-32 is reviewed and in progress; `gov brief` refuses it on KPI_NO_VERIFY for its
other lines and DEPENDS_NOT_CLOSED W2-15a). You are an independent auditor, read-only, a fresh session; RUBRIC-2 class
C2, Opus at high. Your worktree is on `w2/W2-32-s9-tests` at `669707a76` (the test designer's commit on top of
`1a3669e6a`, which re-worded S9). Write nothing in the repository; your record is your final message.

**One bar, two rounds (DEC-1131):** judge only the re-worded **S9 line** (in `.tickets/DAEO-0pyc.md`; quoted below) and
F1 being unchanged. Every finding names the KPI line it fails (S9 or F1) or is a row (out of scope, never a round).

> S9 K9's memory line (DEC-1083 (2), re-worded by DEC-1097 (1)(d)): on the verdict set, judged once on the declared
> configuration, right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it.
> Judged on the fresh 80 at window 4's pin: 78 of 79 right (98.7 %), 0 wrong claims, hit@5 67 of 79 (84.8 %)
> [FRESH-80-RESULT, DEC-1098 (1)]. ... [re-worded, DEC-1129 (1)]

Check: (1) the commit `669707a76` changes only `tests/acceptance/W2-32/README.md`, `w2_32_record.py`,
`test_w2_32_record.py`, with `Rewrite-Reason: DEC-1129 (1)`; (2) the S9 cases test the line's own words (85 % and 5 %
bars, 95 % target, hit@5 reported and never judged, the 79-question boundaries) and would be red on a wrong
implementation (read the cases; plant one wrong `s9_state` in a copy under your TMPDIR and run only
`test_w2_32_record.py` there); (3) the evidence-row case reads `docs/changes/W2-32-evidence.md` and requires the 80's
figures and `FRESH-80-RESULT`; (4) F1's code and cases unchanged (`git diff 1a3669e6a 669707a76`); (5) the README's KPI
map still parses for `gov accept` (the CTO's run gave 266 passed, 0 failed, 2 skipped). Never open `~/gov-os-runs/`,
`~/gov-os-eval/`, or any folder named hidden or memory-verdict.

Return: the twelve fields, then findings (F-ids, each with its KPI line, blocking yes/no, evidence, fix) and a verdict
READY or NOT READY.
