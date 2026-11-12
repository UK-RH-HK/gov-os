{
  "ticket": "DAEO-ktiw",
  "ticket_text": "---\nid: DAEO-ktiw\nstatus: in_progress\ndeps: []\nlinks: [DAEO-zsvl, DAEO-32n6, DAEO-juee]\ncreated: 2026-11-11T23:21:47Z\ntype: task\npriority: 1\nassignee: product-spec\nexternal-ref: W2-176\ntags: [wave-2, kernel, hooks, cit-p, standard]\nwbs_id: W2-176\ntitle: 'Context awareness before compaction, live for every session: the compaction summary opens with the read-the-handover-first line, and a once-per-session reminder near the window''s end (DEC-1140 (1)(b))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: STANDARD\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- template/governance/kernel/hooks/precompact.py\n- template/governance/kernel/hooks/context_watch.py\n- tests/unit/hooks/test_w2_176*\n- tests/unit/hooks/test_resume_hooks.py   # assert-only updates for S1's stdout line (the CTO, P1 (a), 2026-11-12)\n- tests/unit/hooks/test_w29_hooks.py      # the same\n- docs/changes/W2-176-CIT-P.md\n# .claude/settings.json out of the paths: the PostToolUse registration of context_watch.py is a class (b) ACT after the owner's approval (DEC-315, class-rules row agents-skills-kernel)\nreads:\n- template/governance/kernel/hooks/**\n- .claude/settings.json\n- .rulesync/hooks.jsonc\n- template/.rulesync/hooks.jsonc\n- src/gov/checkpoint/**\n- tests/acceptance/W1-29/**\n- tests/acceptance/W1-49/**\n- tests/acceptance/W2-62/**\nneeds:\n- template/governance/kernel/hooks/precompact.py   # W1-29's checkpoint hook, live since 9274e678350d\n- template/governance/kernel/hooks/sessionstart.py # W2-62's RESUME HERE injection on compact, clear and resume\nest_loc: 160\nkpis:\n  success:\n  - line: \"S1 On every compaction (trigger auto or manual), precompact.py prints one plain-text line on stdout, which Claude Code merges into the compaction instructions: it tells the summary to begin with \\\"READ FIRST:\\\" and the path of the session's checkpoint with its RESUME HERE section (the orchestrator and leads: the CHECKPOINT path the hook already writes), or \\\"READ FIRST: your brief and your record\\\" with their paths (workers); its checkpoint writing and its systemMessage on error are unchanged [DEC-1140 (1)(b), DEC-208, DEC-250]\"\n    verify: \"tests/unit/hooks/test_w2_176_precompact.py: the hook fed a planted PreCompact event (trigger auto, then manual) for GOV_ROLE orchestrator and for engineer prints exactly one stdout line starting with the instruction and naming the right path; the W1-29 and W1-49 acceptance cases pass unchanged in the ticket's worktree through the heavy-job gate\"\n  - line: \"S2 context_watch.py, a PostToolUse hook, reads the session's transcript_path tail, takes the last assistant message's usage (input plus cache tokens), divides it by the session's window (the model's window from a small table: Opus 5.5 1,000,000; Sonnet 5.5 and Haiku 5.5 their documented windows; unknown models 200,000; for the CTO's own session, GOV_TICKET the coordination ticket, the model's window, DEC-1140 (4); for every lead and worker the smaller of the model's window and 200,000, DEC-1118 (A)), skips events that carry agent_id (subagents), and at 85 % or more injects, once per context window (re-armed when usage falls below 50 %, after a compaction), additionalContext telling the session to write its checkpoint now, update every file that needs it (the role's own list: the CTO's RESUME HERE, DECIDED-NOT-DONE, report-state; a lead's CHECKPOINT; a worker's record), and begin its compaction summary with the read-first line; the text says it is a handover aid, not a stop or an early compaction (DEC-901's precedent, DEC-838 (2)) [DEC-1140 (1)(b), DEC-445]\"\n    verify: \"tests/unit/hooks/test_w2_176_context_watch.py: planted transcripts at 50 %, 84 %, 85 % and 99 % of a planted window: no output below 85 %, one additionalContext at 85 %, none on the next call in the same session (a state file under the session's .gov-runtime/scratch), the wording holds the three duties and the not-a-stop sentence; an Opus 5.5 transcript uses 1,000,000\"\n  - line: \"S3 context_watch.py is fast and fails safe: it reads only the transcript's last 256 KiB, returns within 100 ms on a 50 MB transcript, and on any error (no transcript, unreadable usage, an unknown event) prints nothing and exits 0, so it never slows or blocks a tool call\"\n    verify: \"tests/unit/hooks/test_w2_176_context_watch.py: a 50 MB planted transcript measured under 100 ms (median of 5); a missing path, a malformed last line and an empty event each give exit 0 and no stdout\"\n  - line: \"S4 The change goes through CAP-33 as a kernel template delta, recorded in docs/changes/W2-176-CIT-P.md: the evidence (the owner's order, the search of 11-11: hooks live, the window retired by DEC-838, never built: the summary line and the reminder), the proposal with each file's base and new sha256, the independent review's READY, the owner's approval, the promotion; the registration of context_watch.py in .claude/settings.json (PostToolUse) is named as the class (b) ACT that follows the approval [DEC-1140 (1)(b), CAP-33, DEC-315]\"\n    verify: \"docs/changes/W2-176-CIT-P.md has a section per CAP-33 step; the sha256 column equals sha256sum of each file at the ticket's head\"\n  failure:\n  - line: \"F1 Neither hook sets or reads a compaction threshold (no CLAUDE_CODE_AUTO_COMPACT_WINDOW, no --autocompact), returns a decision field (allow, deny, ask, block), or writes outside the session's .gov-runtime/scratch; a planted denial-shaped output is never produced [DEC-838 (1), w2-orchestrator.md \u00a74, \u00a712]\"\n    verify: \"tests/unit/hooks/test_w2_176_context_watch.py and test_w2_176_precompact.py: the source holds no window variable; every output parsed has no decision key; a write-tracing run lists only the scratch state file; tests/acceptance/W1-49/test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own passes\"\n  - line: \"F2 The ticket's diff names only its four paths; no .claude/ file, no settings, no other hook changes\"\n    verify: \"git diff --name-only <base>..HEAD of the ticket's branch lists only the allowed paths\"\nnon_goals:\n- the .claude/settings.json registration (a class (b) ACT after the owner's approval)\n- any change to sessionstart.py (its RESUME HERE injection on compact already works, W2-62)\n- any compaction threshold or early stop (DEC-838)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources:\n- DEC-1140\n- DEC-1118\n- DEC-264\n- DEC-259\n- DEC-838\n- DEC-901\n- DEC-445\n- DEC-208\n- DEC-250\n- DEC-315\n- CAP-33\nacceptance_tests:\n  path: tests/unit/hooks/\n  author: engineer (STANDARD, unit cases beside the hooks; the W1-29, W1-49 and W2-62 acceptance suites as the regression)\ntrack: A\nlist_rows: []\n---\n# W2-176 Context awareness before compaction, live for every session\n\n**Why (the owner, 2026-11-11 ~23:05, DEC-1140 (1)(b)):** \"a session that knows its context limit and, when close to\ncompaction, writes its checkpoint, updates every file that needs it, and hands over in the compaction summary with a\nreminder to read the handover first, so it resumes as fresh as needed ... bring it back live for every session: yours,\nleads and workers.\"\n\n**What the search found (CTO's helper, 11-11 23:30):** the PreCompact checkpoint (W1-29) and the SessionStart RESUME HERE\ninjection on compact (W2-62) are live (`.claude/settings.json:15-37`; PreCompact last fired 11-11 03:25); the emergency\ndid not switch them off. The \"knows its limit\" half was the 300k auto-compact window (W1-49, DEC-208), retired by DEC-838\non 10-19 for usage; no hook was ever fed the context utilisation (DEC-445's residual). Never built: the read-first line in\nthe compaction summary, and a reminder near the window's end. CLI 2.1.322 merges a PreCompact hook's stdout into the\ncompaction instructions and gives every hook `transcript_path`. DEC-1128 does not cover this (it is about switched-off\ncontrols and new guard refusals); DEC-1140 (1)(b) is the order.\n\n**Class C3** (kernel hooks): engineer and reviewer on Opus, high (RUBRIC-2). Profile STANDARD: unit cases by the engineer\nbeside the hooks, one independent review of the delta (CAP-33), then the owner's approval of the bytes, then the\nregistration ACT.\n\n- **Delegated (the CTO, DEC-1112 (3), 2026-11-12), run 1's packages:** P1 (a): the two older hook test files added to the\n  paths for assert-only updates (the read-first line first, the JSON object on the last line; DEC-264, DEC-259 read with\n  DEC-1140). P2 (a): the reminder's report-state path corrected (the CTO's file is\n  `.gov-runtime/scratch/orchestrator/log/report-state.json`), with R7 (OSError caught in `newest()`), by a fresh engineer.\n  P3: R2 (a), subagent events skipped; R1: re-armed once usage falls below 50 % (S2 above). P4: leads and workers are\n  reminded against 200,000 (DEC-1118 (A)), the CTO's session against its model's window (DEC-1140 (4)); in this batch,\n  not a follow-up. Then review round 2, the last one (DEC-1010).\n",
  "authority": [
    {
      "id": "DEC-1140",
      "sha256": "5fb65794dd5b4385d26f9732683498f0ae598071411852c40b97b3c433b61f7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5fb65794dd5b4385d26f9732683498f0ae598071411852c40b97b3c433b61f7e",
      "reason": "declared in sources",
      "tokens": 3788
    },
    {
      "id": "DEC-1118",
      "sha256": "c6b461ccd033f89858c85eeeb862b0c68aab9020a4da804b8fb88142de49506c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c6b461ccd033f89858c85eeeb862b0c68aab9020a4da804b8fb88142de49506c",
      "reason": "declared in sources",
      "tokens": 556
    },
    {
      "id": "DEC-264",
      "sha256": "ad5d311b6aa4809702a6f7e82983b51924463e14aa8f8324582f5cd3457acd84",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ad5d311b6aa4809702a6f7e82983b51924463e14aa8f8324582f5cd3457acd84",
      "reason": "declared in sources",
      "tokens": 391
    },
    {
      "id": "DEC-259",
      "sha256": "394eb734975a062443564eb7f05c9626f012d2670d93444a01a88c4d0fbcfe5e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "394eb734975a062443564eb7f05c9626f012d2670d93444a01a88c4d0fbcfe5e",
      "reason": "declared in sources",
      "tokens": 237
    },
    {
      "id": "DEC-838",
      "sha256": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "reason": "declared in sources",
      "tokens": 321
    },
    {
      "id": "DEC-901",
      "sha256": "d4d65a9a71201647f265f20d70ee10b82b342edc07aec6bd12292d4ef1ea9f16",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d4d65a9a71201647f265f20d70ee10b82b342edc07aec6bd12292d4ef1ea9f16",
      "reason": "declared in sources",
      "tokens": 440
    },
    {
      "id": "DEC-445",
      "sha256": "4e8f3f9f1081e652e224c4bc026084e2efdeeb40f94f3d169823959c2293b6fc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4e8f3f9f1081e652e224c4bc026084e2efdeeb40f94f3d169823959c2293b6fc",
      "reason": "declared in sources",
      "tokens": 108
    },
    {
      "id": "DEC-208",
      "sha256": "b6fd283cf66a7f5e825b1f68d87ccff5d27581b07a6398d5da16e4542be63a35",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b6fd283cf66a7f5e825b1f68d87ccff5d27581b07a6398d5da16e4542be63a35",
      "reason": "declared in sources",
      "tokens": 467
    },
    {
      "id": "DEC-250",
      "sha256": "03bf47a37c3838f5f924b07db8f02f69fa689673ce852b59066733763f99694e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "03bf47a37c3838f5f924b07db8f02f69fa689673ce852b59066733763f99694e",
      "reason": "declared in sources",
      "tokens": 334
    },
    {
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1140",
      "sha256": "5fb65794dd5b4385d26f9732683498f0ae598071411852c40b97b3c433b61f7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5fb65794dd5b4385d26f9732683498f0ae598071411852c40b97b3c433b61f7e",
      "reason": "declared in sources",
      "tokens": 3788
    },
    {
      "id": "DEC-1118",
      "sha256": "c6b461ccd033f89858c85eeeb862b0c68aab9020a4da804b8fb88142de49506c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c6b461ccd033f89858c85eeeb862b0c68aab9020a4da804b8fb88142de49506c",
      "reason": "declared in sources",
      "tokens": 556
    },
    {
      "id": "DEC-264",
      "sha256": "ad5d311b6aa4809702a6f7e82983b51924463e14aa8f8324582f5cd3457acd84",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ad5d311b6aa4809702a6f7e82983b51924463e14aa8f8324582f5cd3457acd84",
      "reason": "declared in sources",
      "tokens": 391
    },
    {
      "id": "DEC-259",
      "sha256": "394eb734975a062443564eb7f05c9626f012d2670d93444a01a88c4d0fbcfe5e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "394eb734975a062443564eb7f05c9626f012d2670d93444a01a88c4d0fbcfe5e",
      "reason": "declared in sources",
      "tokens": 237
    },
    {
      "id": "DEC-838",
      "sha256": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "reason": "declared in sources",
      "tokens": 321
    },
    {
      "id": "DEC-901",
      "sha256": "d4d65a9a71201647f265f20d70ee10b82b342edc07aec6bd12292d4ef1ea9f16",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d4d65a9a71201647f265f20d70ee10b82b342edc07aec6bd12292d4ef1ea9f16",
      "reason": "declared in sources",
      "tokens": 440
    },
    {
      "id": "DEC-445",
      "sha256": "4e8f3f9f1081e652e224c4bc026084e2efdeeb40f94f3d169823959c2293b6fc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4e8f3f9f1081e652e224c4bc026084e2efdeeb40f94f3d169823959c2293b6fc",
      "reason": "declared in sources",
      "tokens": 108
    },
    {
      "id": "DEC-208",
      "sha256": "b6fd283cf66a7f5e825b1f68d87ccff5d27581b07a6398d5da16e4542be63a35",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b6fd283cf66a7f5e825b1f68d87ccff5d27581b07a6398d5da16e4542be63a35",
      "reason": "declared in sources",
      "tokens": 467
    },
    {
      "id": "DEC-250",
      "sha256": "03bf47a37c3838f5f924b07db8f02f69fa689673ce852b59066733763f99694e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "03bf47a37c3838f5f924b07db8f02f69fa689673ce852b59066733763f99694e",
      "reason": "declared in sources",
      "tokens": 334
    },
    {
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "supplementary": [],
  "supplementary_query": "Context awareness before compaction, live for every session: the compaction summary opens with the read-the-handover-first line, and a once-per-session reminder near the window's end (DEC-1140 (1)(b))\n{'line': 'S1 On every compaction (trigger auto or manual), precompact.py prints one plain-text line on stdout, which Claude Code merges into the compaction instructions: it tells the summary to begin with \"READ FIRST:\" and the path of the session\\'s checkpoint with its RESUME HERE section (the orchestrator and leads: the CHECKPOINT path the hook already writes), or \"READ FIRST: your brief and your record\" with their paths (workers); its checkpoint writing and its systemMessage on error are unchanged [DEC-1140 (1)(b), DEC-208, DEC-250]', 'verify': \"tests/unit/hooks/test_w2_176_precompact.py: the hook fed a planted PreCompact event (trigger auto, then manual) for GOV_ROLE orchestrator and for engineer prints exactly one stdout line starting with the instruction and naming the right path; the W1-29 and W1-49 acceptance cases pass unchanged in the ticket's worktree through the heavy-job gate\"}\n{'line': \"S2 context_watch.py, a PostToolUse hook, reads the session's transcript_path tail, takes the last assistant message's usage (input plus cache tokens), divides it by the session's window (the model's window from a small table: Opus 5.5 1,000,000; Sonnet 5.5 and Haiku 5.5 their documented windows; unknown models 200,000; for the CTO's own session, GOV_TICKET the coordination ticket, the model's window, DEC-1140 (4); for every lead and worker the smaller of the model's window and 200,000, DEC-1118 (A)), skips events that carry agent_id (subagents), and at 85 % or more injects, once per context window (re-armed when usage falls below 50 %, after a compaction), additionalContext telling the session to write its checkpoint now, update every file that needs it (the role's own list: the CTO's RESUME HERE, DECIDED-NOT-DONE, report-state; a lead's CHECKPOINT; a worker's record), and begin its compaction summary with the read-first line; the text says it is a handover aid, not a stop or an early compaction (DEC-901's precedent, DEC-838 (2)) [DEC-1140 (1)(b), DEC-445]\", 'verify': \"tests/unit/hooks/test_w2_176_context_watch.py: planted transcripts at 50 %, 84 %, 85 % and 99 % of a planted window: no output below 85 %, one additionalContext at 85 %, none on the next call in the same session (a state file under the session's .gov-runtime/scratch), the wording holds the three duties and the not-a-stop sentence; an Opus 5.5 transcript uses 1,000,000\"}\n{'line': \"S3 context_watch.py is fast and fails safe: it reads only the transcript's last 256 KiB, returns within 100 ms on a 50 MB transcript, and on any error (no transcript, unreadable usage, an unknown event) prints nothing and exits 0, so it never slows or blocks a tool call\", 'verify': 'tests/unit/hooks/test_w2_176_context_watch.py: a 50 MB planted transcript measured under 100 ms (median of 5); a missing path, a malformed last line and an empty event each give exit 0 and no stdout'}\n{'line': \"S4 The change goes through CAP-33 as a kernel template delta, recorded in docs/changes/W2-176-CIT-P.md: the evidence (the owner's order, the search of 11-11: hooks live, the window retired by DEC-838, never built: the summary line and the reminder), the proposal with each file's base and new sha256, the independent review's READY, the owner's approval, the promotion; the registration of context_watch.py in .claude/settings.json (PostToolUse) is named as the class (b) ACT that follows the approval [DEC-1140 (1)(b), CAP-33, DEC-315]\", 'verify': \"docs/changes/W2-176-CIT-P.md has a section per CAP-33 step; the sha256 column equals sha256sum of each file at the ticket's head\"}\n{'line': \"F1 Neither hook sets or reads a compaction threshold (no CLAUDE_CODE_AUTO_COMPACT_WINDOW, no --autocompact), returns a decision field (allow, deny, ask, block), or writes outside the session's .gov-runtime/scratch; a planted denial-shaped output is never produced [DEC-838 (1), w2-orchestrator.md \u00a74, \u00a712]\", 'verify': 'tests/unit/hooks/test_w2_176_context_watch.py and test_w2_176_precompact.py: the source holds no window variable; every output parsed has no decision key; a write-tracing run lists only the scratch state file; tests/acceptance/W1-49/test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own passes'}\n{'line': \"F2 The ticket's diff names only its four paths; no .claude/ file, no settings, no other hook changes\", 'verify': \"git diff --name-only <base>..HEAD of the ticket's branch lists only the allowed paths\"}",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 9202,
  "budget": {
    "limit": 12000,
    "used": 9202
  },
  "hash": "2798c81f801d6eb9c9a7c70e148b615e438859e6e2b6a6b24ca11bbe0c63fc7e"
}
