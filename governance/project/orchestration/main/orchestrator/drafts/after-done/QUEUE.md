# Commits and starts queued behind the operator's "done" (CTO b2f0511f, 2026-11-12)
1. DEC-1141 (approvals: W2-11 stands, W2-176 withdrawn; (a) hand merges with S6/unit suites first; (b) CONTEXT-WATCH-1 after the nightly; W2-11 rows R6 accepted, R1/R5 rows, R4 to W2-33; no token cap for any session, replacing DEC-1118 (A) entirely; DEC-1140 (4)'s "Leads and helpers keep (A)" corrected as the CTO's addition) + DECISIONS-IN-FORCE (DEC-1118, DEC-1140 lines, DEC-1141 line) + "Changed by" on DEC-1118, DEC-1120 (2) + START-NEXT-SESSION lines 77, 139 + DECIDED-NOT-DONE row 98.
2. W2-52 land (a77ef5f20089) through the queue.
3. W2-11 hand merge (after ACT-4), then W2-175 hand merge (S6 254/0 and units first), then ACT-CLAUDE-COPIES-5 message to the operator.
4. W2-171: its Interface (drafts/w2-171-iface/INTERFACE.md, ten open items settled) into the ticket + DEC-1052, DEC-1129 sources; release run 2.
5. W2-173: P-1 (a): S5 reworded ("W2-149's cases pass, with the 8 cases' planted products in the fixed form"); tests/acceptance/W2-149/w2_149_support.py and W2-149's two unit cases into allowed_paths; release a resume (test-design batch, rebuild, lead_verify, gov accept W2-149 and W2-173, FULL review). P-2: file a small ticket for the hidden/dropped exclusion before 11-23.
6. W2-176: ticket S2 (no cap, every session at 85 % of its own window) + its new hook bytes for the owner; ACT-CONTEXT-WATCH-1 rebuilt on the new hash, short re-review.
7. W2-23: on the owner's P-W2-23-8 answer.
8. A new claim for the free slot (off-path: W2-154, W2-146, W2-34, W2-17/W2-19 as conflicts allow) after the nightly.
9. (03:12, structural notice after W2-52's land) DEC-989: add "Changed by: DEC-1141 (4) (two hand merges, W2-175 and W2-176)" (DEC-866). Drop `tests/acceptance/W1-41/...` from DAEO-kmcr and `tests/acceptance/W2-149/w2_149_support.py` from DAEO-qz4p once their designer batches are merged (the mutation notice).
10. ACT-OPERATOR-HOURS-1 round 2 (the last): rebuild so `check` refuses unless ACT-OPERATOR-HOURS-2's opcommon.py hash is live (keep 0210), or a stand-alone 0110 variant; file round 1's review (F1 blocking, F2-F6 rows) with its verdict block; then review round 2.
11. W2-121 part a (P-W2-121-5, the CTO's ruling 03:20): the six W2-96 reds in tests/unit/accept/test_w2_96_{run2,review3,review4} (signals and timeouts in gov accept's clean-up; red in 13 of 14 verifies across eight trees) are shared base reds: named in each return, not blocking (the queue traces unowned reds against the head without the batch); NOT added to skip_known.json (that list is for skips). Record the ruling in DAEO-cb2b's ticket; release its resume (re-verify 63130cf2d28a, then the FULL review, probe record). File a fix ticket for W2-96's six cases (C2) and put it in the next batch.
13. W2-115 (run 2 PACKAGES 03:28; acceptance 77/77 at 048abe062626): PK-2 (a) decided by the CTO (delegated P2): the four W2-77
    nightly-record key cases into W2-115's paths for a test-designer revision allowing `secrets_full_scan` (Rewrite-Reason DEC-966
    item 4). PK-1 to the owner at 08:00: W1-39's overlay test vs the template's close.yaml (DEC-903's overlay list); recommend (a)
    the test revision with (c) a register line naming close.yaml in DEC-903's list. Then W2-115's resume: the revisions, verify,
    the FULL review, probe record.
14. W2-173 run 2 (03:42): the build converged; it stopped before the FULL review for the night hold (its "ESCALATION_BLOCKED" is
    the night hold, not a gov escalation: nothing for the owner). After the nightly: release a resume (the review brief is
    written; CHECKPOINT NEXT line), then the probe record and the land.
12. For the morning package: one call refused at 03:20 under the quiet hours (a waiter started with a trailing `&`, DEC-731; not retried).
