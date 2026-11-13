# W2-11 (DAEO-k7hz) closed: merged by hand on the owner's word (DEC-1144 (1)), then closed on a green run

- Commit merged (the lead's final, verified result): 6ba93fc8bf35; merge 6f2234f40 (`git merge --no-ff`, one command, W2-11's trailer); profile STANDARD
- Why by hand: its seven copy cases could be green only after ACT-CLAUDE-COPIES-5, which applies only after this merge (its before state is W2-11's skill bytes); the queue refuses any red, so it ejected W2-11 at 12:51. An exception to DEC-989 by the owner (P1-A (a), DEC-1144 (1)), beside DEC-1141 (4)'s two
- The merge check before the merge (`hand_merge_check.sh`, a scratch clone of w2/integrate f7085136de3c merged with 6ba93fc8bf35, TMPDIR outside the runs folder; `log/hm-W2-11.txt` in the CTO's scratch):
  - `tests/acceptance/W2-11`: 186 passed, 7 failed, 1 skipped; the seven are exactly the copy cases (`test_every_copy_carries_the_kernel_skills_body[test-design, orchestration]`, `test_the_skill_carries_one_version_in_all_four_places[discovery, orchestration, retrieval, test-design]`, `test_the_file_teaches_no_superseded_rule[.claude/skills/orchestration/SKILL.md]`)
  - `tests/unit`: 3,808 passed, 2 failed: W2-153's two composition cases, red on w2/integrate itself since COPIES-4 (a shared base red; W2-175's merge clears them)
- ACT-CLAUDE-COPIES-5 applied by the owner's operator after the merge: a2a74f22f (6 files)
- The green run after it, at w2/integrate f0ef62f39314 (through heavy_slot.sh): `tests/acceptance/W2-11`: 193 passed, 1 skipped, 0 failed
- Kernel bytes: as approved by the owner's CIT-P at dca382f3069f (DEC-1141 (1)); W2-11's commits since touch only `docs/changes/` records
- Review: STANDARD, two rounds; PASS (`docs/changes/W2-11-CITP-REVIEW-r*.md`)
- Closed: 2026-11-12, by the orchestrator under DEC-953 items 1 and 5, DEC-1144 (1)
