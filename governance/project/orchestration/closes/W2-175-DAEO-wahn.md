# W2-175 (DAEO-wahn) closed: merged by hand on the owner's word (DEC-1141 (4)), after ACT-CLAUDE-COPIES-5

- Commit merged: 4c0c73472fd8, the bytes the owner approved (DEC-1139: the seven role templates at 1.0.1); merge 61cae50dc (`git merge --no-ff`, one command, the ticket's trailer); profile STANDARD
- Order (DEC-1141 (4)): COPIES-4, W2-11 (6f2234f40), COPIES-5 (a2a74f22f, the owner's operator), then this merge
- The merge check before it (`hand_merge_check.sh`, a scratch clone of w2/integrate e538af6290ae merged with 4c0c73472fd8, TMPDIR outside the runs folder; `log/hm-W2-175-c.txt` in the CTO's scratch): `tests/acceptance/W2-175` 51 passed; `tests/unit` 3,851 passed, 0 failed
- After the merge, at 3430341c4 (through heavy_slot.sh): W2-175's acceptance and W2-153's two composition cases (red on integrate since COPIES-4, cleared by this merge) green, 179 passed with W2-176's cases
- Kernel bytes: as approved at 4c0c73472fd8 (DEC-1139); the CIT-P record set APPROVED
- Closed: 2026-11-12, by the orchestrator under DEC-953 items 1 and 5, DEC-1141 (4)
