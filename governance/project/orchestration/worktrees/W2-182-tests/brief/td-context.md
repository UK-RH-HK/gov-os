{
  "ticket": "DAEO-5y8d",
  "ticket_text": "---\nid: DAEO-5y8d\nwbs_id: W2-182\nexternal-ref: W2-182\ntitle: The nightly's drift reds of 2026-11-13 fixed by test revision (W1-32's command list, W1-18 and W2-123's rebuild answer, W2-121 S1's race, W2-136 S10, W2-23 S6)\ntype: task\nclass: implementation\nrole: independent-test-designer\nprofile: LITE\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-13\ndeps: []\nallowed_paths:\n- tests/acceptance/W1-32/test_w1_32_command_set.py\n- tests/acceptance/W1-32/README.md\n- tests/acceptance/W1-18/test_w1_18_on_demand_start.py\n- tests/acceptance/W1-18/README.md\n- tests/acceptance/W2-123/test_w2_123_retry.py\n- tests/acceptance/W2-123/README.md\n- tests/acceptance/W2-121/test_s1_lock_off_status.py\n- tests/acceptance/W2-121/README.md\n- tests/acceptance/W2-136/test_w2_136_never_a_gate.py\n- tests/acceptance/W2-136/README.md\n- tests/acceptance/W2-23/test_w2_23_space.py\n- tests/acceptance/W2-23/README.md\n- docs/probes/DAEO-5y8d/**  # the probe record\n- template/.rulesync/hooks.jsonc  # E (a): the template's hooks source gains context_watch.py (a product-spec worker's line, not a test designer's)\nkpis:\n  success:\n  - 'B: W1-32''s recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail'\n  - 'C: W1-18''s and W2-123''s cases expect REBUILD_FAILED where a rebuild''s asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try''s record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)'\n  - 'R: W2-121 S1 takes its second snapshot only after the fake launched job''s .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job''s late write [DEC-1163 (6)] Verify: the case passes 20 runs in a row under the nightly''s load (beside a busy loop of 20 workers); it still fails when a stand-in status writes a file'\n  - 'D: W2-136 S10''s scan allows `src/gov/session_watch` to call gov plan (W2-159''s S5: session-watch reads the dispatcher''s ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105] Verify: the case passes on w2/integrate; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it'\n  - 'E: the template''s hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` as the root `.rulesync/hooks.jsonc` does (ACT-CONTEXT-WATCH-1), and W2-23 S6 expects the seven kernel hooks [DEC-1163 (6) E (a)] Verify: W2-23 S6 passes on w2/integrate; a planted eighth hook script with no wiring fails it; `python3 -m gov.adapters.portability` exits 0 on the template'\n  failure:\n  - 'A revised case that no longer catches what it guards, or any case lowered, skipped or marked. Verify: each revised case fails on a planted break of what it guards (the S lines above); `git diff` adds no skip, xfail or flaky mark'\nnon_goals:\n- no product code changes (src/gov/**); the behaviours these cases record were decided and landed by W2-45, W2-121, W2-23, W2-159, W2-160, W2-124 and W2-176\n- not the 2 timing cases that pass alone under the nightly beside the leads (W2-112, W2-145 S4): environment, DEC-1159 (1)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1163, DEC-1156, DEC-1150, DEC-1159, DEC-105, DEC-781]\nacceptance_tests: {path: tests/acceptance/W2-182/}\n---\n\n# W2-182 The nightly's drift reds of 2026-11-13\n\nThe owner's DEC-1163 (6), route (a): one small gap ticket for the five red-alone cases of the nightly of 2026-11-13 that\nare not the Node 18 PATH (fixed by 8f68e0c7c). Each records a behaviour the owner already decided and that has landed;\nevery ticket that broke them is closed. Analysis: `.gov-runtime/scratch/orchestrator/drafts/nightly-20261113-analysis.md`.\n\n- **B** (W1-32): `dispatch` (W2-121, merge 787b097ac), `adapters` (W2-23), `session-watch` (W2-159), `wait` (W2-160).\n- **C** (W1-18, W2-123): W2-124's \"a rebuild without its asked-for semantic store fails named\" (799b2b65f, merge a2f28ccf3).\n- **R** (W2-121 S1): a race in the test under load (passes alone).\n- **D** (W2-136 S10 against W2-159 S5): the owner's (a).\n- **E** (W2-23 S6): W2-176's 7th kernel hook (context_watch.py, hand merge 3430341c4) never reached `template/.rulesync/hooks.jsonc`; the owner's (a).\n\nA test designer revises the cases (`Rewrite-Reason: DEC-1163 (6)`); a product-spec worker adds the template's hook line; a narrow independent check; the land.\n",
  "authority": [
    {
      "id": "DEC-1163",
      "sha256": "e1bd7ee781e8a0456154e41042d2b09120832f81ec18890ab2327906e88979cb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e1bd7ee781e8a0456154e41042d2b09120832f81ec18890ab2327906e88979cb",
      "reason": "declared in sources",
      "tokens": 5259
    },
    {
      "id": "DEC-1156",
      "sha256": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "reason": "declared in sources",
      "tokens": 1044
    },
    {
      "id": "DEC-1150",
      "sha256": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DEC-1159",
      "sha256": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "reason": "declared in sources",
      "tokens": 515
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-781",
      "sha256": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "reason": "declared in sources",
      "tokens": 446
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1163",
      "sha256": "e1bd7ee781e8a0456154e41042d2b09120832f81ec18890ab2327906e88979cb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e1bd7ee781e8a0456154e41042d2b09120832f81ec18890ab2327906e88979cb",
      "reason": "declared in sources",
      "tokens": 5259
    },
    {
      "id": "DEC-1156",
      "sha256": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "eb2ce730d1a2fe9397a2e538eaa9937b51b77c0f6403c6485490c675bfd9c8c3",
      "reason": "declared in sources",
      "tokens": 1044
    },
    {
      "id": "DEC-1150",
      "sha256": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DEC-1159",
      "sha256": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f9e0adb68e1139164a412821770f348a67c4014b293a52cf317fc8add6d64e74",
      "reason": "declared in sources",
      "tokens": 515
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-781",
      "sha256": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "3c5c0a13f63d85efe48c245589742df7ff93cad2d930202c184ce2f0f562c29a",
      "reason": "declared in sources",
      "tokens": 446
    }
  ],
  "supplementary": [
    {
      "id": "666cf15132edc492a1404394",
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "text": "| 13 | L6 | `.gov-runtime/store.db`: graph + FTS5 + sqlite-vec from W1 | one integration store at the integration head, outside the trees, two halves behind a link, rebuilt by the `reference-transaction` hook after every update, seeded, switched only on a complete build, daily backstop; no store per worktree; `GOV_STORE`; designers search only it; built with the pinned code | DEC-963, DEC-1087 (3) |\n| 14 | L6 | frontmatter graph | the stated links as typed edges (W2-92) | DEC-1074 (5) |\n| 15 | L6 | \u2014 | no cold rebuild (seeding, W2-122); each text embedded once (vector cache, W2-126) | DEC-1032 (1), (3)(iv), DEC-1033 (2)(d), DEC-1039 (1) |\n| 16 | L6 | \u2014 | a rebuild that does not recreate its asked-for semantic store fails, named; `--no-embeddings` skips it | DEC-1015 (4), DEC-530 |\n| 17 | L7 | Copier, signed tags, lock | + the first numbered, frozen release after the lift's re-pin; the pin ladder by hand until W3 | DEC-1090 (5), DEC-1089 (2) |\n\n",
      "tokens": 240
    },
    {
      "id": "3e9245b2d9bfc2663b2c72e2",
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "text": "## Answers to the checks\n\n**1. The exact sets are still exact. Yes.**\n- **An unrecorded command still fails.** W1-32's `extra` assertion (`test_w1_32_command_set.py:92-93`) is unchanged.\n- **A recorded command gone from `gov --help` still fails.** The `gone` assertion (`:90-91`) is unchanged.\n- **The pins are exact.**\n  - W1-32's pin (`:84-85`) holds W1-07's list, minus `release`, to exactly the eight names.\n  - W1-07's count case (`test_w1_07_recorded_commands.py:50-51`) holds exactly the nine.\n  - Adding or dropping a name fails both.\n- **`lock` stays a module command.**\n  - `RECORDED_MODULE_COMMANDS = (\"lock\",)` is unchanged in both lists.\n  - W1-32 `:86` and `:94` still pass.\n  - W1-07's `lock` case and W1-26's two `lock` skill cases are untouched.\n- **`release` alone stays excused.** `EXCUSED_UNTIL_RECORDED = (\"release\",)` is unchanged, and `release` is in neither list.\n- **No assertion was weakened.** W1-26's file changed only in docstrings and one comment.\n\n**2. The three are real commands. Yes. The cited decisions are right for `links` and `plan`, but not for `brief` (F1).**\n",
      "tokens": 275
    },
    {
      "id": "60b5e3ffbc5335f387e22a50",
      "path": "tests/acceptance/W1-32/README.md",
      "text": "\n**D-10's red fix, the command set (2026-11-10, W2-20 `DAEO-r30l`; DEC-753, DEC-1088, DEC-1074 (7), DEC-1109; a fresh test designer, Rewrite-Reason):** `test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones` failed on \"gov has commands the command list does not record: ['brief', 'links', 'plan']\". W1-07's lines now record the three; the pinned set is `accept`, `brief`, `ci`, `launch`, `links`, `plan`, `resources`, `telemetry`, still exact. Unchanged: any other unrecorded command fails, a recorded command gone from `gov --help` fails, `lock` is none of `gov`'s, `release` alone is excused until recorded (DEC-753). Green on this branch alone.\n",
      "tokens": 171
    },
    {
      "id": "4e4a6b7e2829be65a40ddd40",
      "path": "governance/project/orchestration/closes/W2-176-DAEO-ktiw.md",
      "text": "# W2-176 (DAEO-ktiw) closed: merged by hand on the owner's word (DEC-1141 (4))\n\n- Commit merged: 3b6c5cb79d39, the bytes the owner approved (DEC-1142 (1): `template/governance/kernel/hooks/context_watch.py` sha256 213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242, no token cap); merge 3430341c4 (`git merge --no-ff`, one command, the ticket's trailer); profile STANDARD\n- The merge check before it (`hand_merge_check.sh`, a scratch clone of w2/integrate e538af6290ae merged with 3b6c5cb79d39; `log/hm-W2-176-c.txt`): `tests/unit/hooks` 196 passed, 1 skipped; `tests/unit` 3,944 passed, 2 failed: W2-153's two composition cases, a shared base red on w2/integrate itself, cleared by W2-175's merge just before this one\n- After the merge, at 3430341c4 (through heavy_slot.sh): the two W2-176 hook cases and W2-153's composition cases green (179 passed with W2-175's acceptance)\n- The CIT-P record set APPROVED with the delta review's F2 (`decisions_carried` names DEC-1141, not the replaced DEC-1118) riding the approval edit (DEC-1142 (1), DEC-802)\n- Next: ACT-CONTEXT-WATCH-1 (`5bdfa098`, the owner's yes 10:22) by the owner's operator; its `check` answers \"state before\" at 3430341c4\n",
      "tokens": 300
    },
    {
      "id": "DAEO-ktiw",
      "path": ".tickets/DAEO-ktiw.md",
      "text": "## Approved (the owner, DEC-1142 (1), 2026-11-12 ~09:50)\n\nThe CIT-P approved at `3b6c5cb79d39` (`context_watch.py` sha256 `213882efd7b8...`). Its delta review's F1 (a): S2 amended above to drop the two file names the no-cap bytes no longer print, no new bytes; F2 (the record's `decisions_carried`) rides the approval edit. Hand merge after S6 and the unit suites (DEC-1141 (4)); then ACT-CONTEXT-WATCH-1 (a), the matcher `Bash`.\n",
      "tokens": 108
    },
    {
      "id": "DEC-1142",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1142 \u2014 The morning of 11-12: W2-176's no-cap bytes approved; P-W2-23-8 (a); W2-115 PK-1 (a)+(c); W2-148 S15 option 2; the operator hours as built; the ticket table (kept after the fact, four parked); no new ticket or split without the owner; the two-refusal stop covers another form of the same effect\n- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~09:50; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`); (8) and (9) standing \u00b7 **Under:** CAP-33, DEC-974, DEC-1010, DEC-1052, DEC-903, DEC-1104, DEC-1136, DEC-1140, DEC-1141 \u00b7 **Changes:** DEC-903 (its overlay list names the template's `close.yaml`)\n- **Decision:**\n  - (1) **W2-176's CIT-P approved at `3b6c5cb79d39`** (`template/governance/kernel/hooks/context_watch.py` sha256\n    `213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242`: no token cap, every session reminded at 85 % of its own\n    model's window; R8 fixed); its delta review's F1 (a): S2 amended to drop the two file names, no new bytes; F2 rides the approval edit.\n    ACT-CONTEXT-WATCH-1: (a), the matcher `Bash`.\n",
      "tokens": 288
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "## 4. Owner's approval\n\nThe approval of `3a580a4b4d42` was withdrawn by the owner (2026-11-12): those bytes carry the cap. Pending for the new\nbytes: independent review of `c10be8fd0266` (section 3.8), then the owner approves the bytes of section 2 at the\nticket's final head.\n\nApproved by the owner on 2026-11-12 (DEC-1142 (1)): \"W2-176's CIT-P approved at 3b6c5cb79d39\", `context_watch.py` sha256\n`213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242` (no token cap), after the delta review READY; the delta review's\nF1 (a) amended S2 with no new bytes, and its F2 rides this approval edit (`decisions_carried` names DEC-1141). Merged by hand at\n3430341c4 (DEC-1141 (4)); ACT-CONTEXT-WATCH-1 (`5bdfa098`) registers the hook.\n\n",
      "tokens": 185
    },
    {
      "id": "0aefbaabfc3e17cfdf83030c",
      "path": "governance/project/orchestration/packages/ACT-CONTEXT-WATCH-1.md",
      "text": "> bash $A/apply.sh verify        # exit 0\n> git diff --name-status         # expect exactly two M: .claude/settings.json and .rulesync/hooks.jsonc\n> git commit -m \"ACT-CONTEXT-WATCH-1: register context_watch.py as a PostToolUse hook, matcher Bash, so every session hands over before compaction (DEC-1140 (1)(b))\" --trailer \"Task: DAEO-ktiw\" --trailer \"Implements: DEC-1140\" --trailer \"Role: owner\" -- .claude/settings.json .rulesync/hooks.jsonc\n> ```\n> - **If the first `sha256sum` shows no file or another hash,** W2-176 has not merged (or not as approved): stop, apply nothing, tell the CTO.\n>   (`apply.sh` refuses by itself with exit 6.)\n> - **If `check` stops** (\"moved: <path>\"), send its line to the CTO and apply nothing (`apply.sh` writes nothing).\n> - **If `git diff --name-status` lists anything besides the two,** commit anyway: the `--` paths limit the commit.\n> - **Undo:** `bash $A/apply.sh undo`, then the same `git commit` with the subject `ACT-CONTEXT-WATCH-1 undone`.\n> - No restart of anything is needed for the files; running sessions pick up the new hook at their next start (section 8).\n\n",
      "tokens": 278
    },
    {
      "id": "39a1b96701942e77807b92c9",
      "path": "governance/project/orchestration/packages/ACT-CONTEXT-WATCH-1.md",
      "text": "## 5. The operator's steps: the message\n> **ACT-CONTEXT-WATCH-1 (DEC-1140 (1)(b)): register W2-176's context watch as a PostToolUse hook (matcher Bash).**\n> Class (b), by hand, **after W2-176 has merged**: your yes first: **`yes ACT-CONTEXT-WATCH-1 5bdfa098`**. In the main tree, about two minutes:\n> ```\n> cd /home/usain/Dynamic-Agentic-Engineering-OS\n> test -z \"$(git status --porcelain)\" && test ! -e .git/MERGE_HEAD && echo clean     # expect: clean\n> sha256sum template/governance/kernel/hooks/context_watch.py   # expect 213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242 (W2-176 merged)\n> A=.gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1\n> sha256sum $A/manifest.json     # expect 5bdfa0981808513db3d9fceeb30f13ba11ea72ea28528ef40664bfe9a931da5a\n> bash $A/apply.sh check         # exit 0: \"state before; template/governance/kernel/hooks/context_watch.py in place as approved\"\n> bash $A/apply.sh apply         # exit 0\n> bash $A/apply.sh verify        # exit 0\n> git diff --name-status         # expect exactly two M: .claude/settings.json and .rulesync/hooks.jsonc\n",
      "tokens": 275
    },
    {
      "id": "4686d408b20946f19665f088",
      "path": "governance/project/orchestration/packages/ACT-MORNING-SEQUENCE-20261112.md",
      "text": "> sha256sum template/governance/kernel/hooks/context_watch.py   # expect 213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242 (W2-176 merged)\n> A=.gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1\n> sha256sum $A/manifest.json     # expect 5bdfa0981808513db3d9fceeb30f13ba11ea72ea28528ef40664bfe9a931da5a\n> bash $A/apply.sh check         # exit 0: \"state before; ... in place as approved\"\n> bash $A/apply.sh apply         # exit 0\n> bash $A/apply.sh verify        # exit 0\n> git diff --name-status         # expect exactly two M: .claude/settings.json and .rulesync/hooks.jsonc\n> git commit -m \"ACT-CONTEXT-WATCH-1: register context_watch.py as a PostToolUse hook, matcher Bash, so every session hands over before compaction (DEC-1140 (1)(b), DEC-1141)\" --trailer \"Task: DAEO-ktiw\" --trailer \"Implements: DEC-1140, DEC-1141\" --trailer \"Role: owner\" -- .claude/settings.json .rulesync/hooks.jsonc\n> ```\n> Then tell the CTO \"done\". Running sessions pick up the new hook at their next start.\n",
      "tokens": 252
    },
    {
      "id": "b27fc2139fd6d85a5d159205",
      "path": "governance/project/orchestration/packages/ACT-MORNING-SEQUENCE-20261112.md",
      "text": "## Part 2: after the CTO says \"merged\" (about 5 minutes)\n\n> **Two ACTs by hand, in this order.**\n>\n> **9. ACT-CLAUDE-COPIES-5** (the six `.claude/skills` copies for W2-11's round-2 kernel skills)\n> ```\n> cd /home/usain/Dynamic-Agentic-Engineering-OS\n> test -z \"$(git status --short --untracked-files=no)\" && test ! -e .git/MERGE_HEAD && echo clean\n> G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-5\n> sha256sum $G/manifest.json      # expect e602d5960dccf62100cb8bc151ae3363fe3e8eb4d96ed8c9e29fe045450f0c91\n> bash $G/apply.sh check && bash $G/apply.sh apply\n> F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 6\n> git commit -m \"ACT-CLAUDE-COPIES-5: the six .claude/skills copies for W2-11's round-2 kernel skills (6 files)\" --trailer \"Task: DAEO-sdxk\" --trailer \"Implements: DEC-315, DEC-992\" --trailer \"Role: owner\"\n> ```\n>\n> **10. ACT-CONTEXT-WATCH-1** (register W2-176's context watch as a PostToolUse hook, matcher Bash; DEC-1140 (1)(b), DEC-1141)\n> ```\n> sha256sum template/governance/kernel/hooks/context_watch.py   # expect 213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242 (W2-176 merged)\n",
      "tokens": 293
    },
    {
      "id": "edc5bac1cda1d1fa5efda596",
      "path": "governance/project/orchestration/packages/P1-MORNING-20261112.md",
      "text": "### P1-3 W2-176's corrected bytes\n1. **Question:** approve `context_watch.py` `213882efd7b8` (head `3b6c5cb79d39`; no cap; R8 fixed; delta review READY).\n2. **Options on its F1** (the CTO's reminder no longer names DECIDED-NOT-DONE.md and report-state.json): (a) amend S2, no new\n   bytes; (b) name both for every main-tree orchestrator, new bytes and a re-review.\n3. **Costs:** (a) one ticket line; (b) a build and a review.\n4. **Recommendation:** approve (`W2-176 CIT-P approved at 3b6c5cb79d39`) with (a).\n5. **Confidence:** high.\n6. **Blocks:** W2-176's hand merge and ACT-CONTEXT-WATCH-1 (`5bdfa098`).\n\n",
      "tokens": 152
    }
  ],
  "supplementary_query": "The nightly's drift reds of 2026-11-13 fixed by test revision (W1-32's command list, W1-18 and W2-123's rebuild answer, W2-121 S1's race, W2-136 S10, W2-23 S6)\nB: W1-32's recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail\nC: W1-18's and W2-123's cases expect REBUILD_FAILED where a rebuild's asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try's record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)\nR: W2-121 S1 takes its second snapshot only after the fake launched job's .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job's late write [DEC-1163 (6)] Verify: the case passes 20 runs in a row under the nightly's load (beside a busy loop of 20 workers); it still fails when a stand-in status writes a file\nD: W2-136 S10's scan allows `src/gov/session_watch` to call gov plan (W2-159's S5: session-watch reads the dispatcher's ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105] Verify: the case passes on w2/integrate; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it\nE: the template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` as the root `.rulesync/hooks.jsonc` does (ACT-CONTEXT-WATCH-1), and W2-23 S6 expects the seven kernel hooks [DEC-1163 (6) E (a)] Verify: W2-23 S6 passes on w2/integrate; a planted eighth hook script with no wiring fails it; `python3 -m gov.adapters.portability` exits 0 on the template\nA revised case that no longer catches what it guards, or any case lowered, skipped or marked. Verify: each revised case fails on a planted break of what it guards (the S lines above); `git diff` adds no skip, xfail or flaky mark",
  "further_batch": [
    {
      "id": "2662235bd4b4c6c6773e6329",
      "path": "tests/acceptance/W2-20/README.md"
    },
    {
      "id": "66349faaf13003b1c10bae3f",
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md"
    },
    {
      "id": "ADOPT-A1",
      "path": "governance/adoption/A1-inventory.md"
    },
    {
      "id": "ADOPT-A2",
      "path": "governance/adoption/A2-classification.md"
    },
    {
      "id": "ADOPT-A3",
      "path": "governance/adoption/A3-target-path-map.md"
    },
    {
      "id": "faaad177cf13b8b65ba2bd87",
      "path": "tests/acceptance/W2-16/README.md"
    },
    {
      "id": "1f4658b1d48e211bb5e1ddf9",
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
    },
    {
      "id": "67292306db11eae7c1c77842",
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "666cf15132edc492a1404394",
          "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md"
        },
        {
          "id": "3e9245b2d9bfc2663b2c72e2",
          "path": "governance/project/orchestration/reviews/D10-commands-review.md"
        },
        {
          "id": "60b5e3ffbc5335f387e22a50",
          "path": "tests/acceptance/W1-32/README.md"
        },
        {
          "id": "4e4a6b7e2829be65a40ddd40",
          "path": "governance/project/orchestration/closes/W2-176-DAEO-ktiw.md"
        },
        {
          "id": "DAEO-ktiw",
          "path": ".tickets/DAEO-ktiw.md"
        },
        {
          "id": "DEC-1142",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "0aefbaabfc3e17cfdf83030c",
          "path": "governance/project/orchestration/packages/ACT-CONTEXT-WATCH-1.md"
        },
        {
          "id": "39a1b96701942e77807b92c9",
          "path": "governance/project/orchestration/packages/ACT-CONTEXT-WATCH-1.md"
        },
        {
          "id": "4686d408b20946f19665f088",
          "path": "governance/project/orchestration/packages/ACT-MORNING-SEQUENCE-20261112.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "b27fc2139fd6d85a5d159205",
          "path": "governance/project/orchestration/packages/ACT-MORNING-SEQUENCE-20261112.md"
        },
        {
          "id": "edc5bac1cda1d1fa5efda596",
          "path": "governance/project/orchestration/packages/P1-MORNING-20261112.md"
        },
        {
          "id": "2662235bd4b4c6c6773e6329",
          "path": "tests/acceptance/W2-20/README.md"
        },
        {
          "id": "66349faaf13003b1c10bae3f",
          "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md"
        },
        {
          "id": "ADOPT-A1",
          "path": "governance/adoption/A1-inventory.md"
        },
        {
          "id": "ADOPT-A2",
          "path": "governance/adoption/A2-classification.md"
        },
        {
          "id": "ADOPT-A3",
          "path": "governance/adoption/A3-target-path-map.md"
        },
        {
          "id": "faaad177cf13b8b65ba2bd87",
          "path": "tests/acceptance/W2-16/README.md"
        },
        {
          "id": "1f4658b1d48e211bb5e1ddf9",
          "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
        },
        {
          "id": "67292306db11eae7c1c77842",
          "path": "docs/assessment/2026-10/I4-records-plan-rest.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "1f4658b1d48e211bb5e1ddf9",
      "reason": "budget exceeded"
    },
    {
      "id": "2662235bd4b4c6c6773e6329",
      "reason": "budget exceeded"
    },
    {
      "id": "66349faaf13003b1c10bae3f",
      "reason": "budget exceeded"
    },
    {
      "id": "67292306db11eae7c1c77842",
      "reason": "budget exceeded"
    },
    {
      "id": "ADOPT-A1",
      "reason": "budget exceeded"
    },
    {
      "id": "ADOPT-A2",
      "reason": "budget exceeded"
    },
    {
      "id": "ADOPT-A3",
      "reason": "budget exceeded"
    },
    {
      "id": "faaad177cf13b8b65ba2bd87",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-5y8d): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 11963,
  "budget": {
    "limit": 12000,
    "used": 11963
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-045",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "a331eb7fc882b5bedb217e6b98802fcf6e95096c32cb2b45cbedbdb7774850e8"
}
