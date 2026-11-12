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
  "supplementary": [
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "| `template/governance/kernel/hooks/context_watch.py` | New PostToolUse hook: reads the transcript's last 256 KiB, the last non-sidechain assistant usage over the model's window (Opus, Sonnet, Haiku 5.5 and Fable 5.2: 1,000,000; others 200,000); at 85 % or more, once per session (a marker under `.gov-runtime/scratch/context_watch/`), additionalContext with the role's duties and the read-first line, and the sentence that it is a handover aid, not a stop and not an early compaction. Any error: no output, exit 0 | none (new file) | `4f62182637698dbdf7f5d5c79480a3eb50be5505b6dc0418bd479dae5ca7ca18` |\n| `tests/unit/hooks/test_w2_176_precompact.py` | 16 unit cases (S1, F1) | none (new file) | n/a (tests) |\n| `tests/unit/hooks/test_w2_176_context_watch.py` | 34 unit cases (S2, S3, F1), including a 50 MB transcript under 100 ms (median 16.8 ms) | none (new file) | n/a (tests) |\n\nThe three options (DEC-105): apply now (recommended: the owner ordered it live for every session, DEC-1140 (1)(b));\ndefer (sessions keep compacting with no read-first line and no reminder); re-baseline (none: no closed specification\nis contradicted beyond the five unit tests of section 3.2).\n\n",
      "tokens": 295
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "# W2-176: change-impact proposal (CIT-P) on the PreCompact hook and a new PostToolUse context watch\n\nThis change makes every session hand over before compaction: the PreCompact hook tells the compaction summary to begin\nwith a read-the-handover-first line, and a new PostToolUse hook reminds a session once, at 85 % of its model's\ncontext window, to write its checkpoint and update its files. It changes a kernel hook and adds one, so it goes\nthrough CIT-P (CAP-33). It sets no compaction threshold and stops nothing (DEC-838).\n\n**Status: DRAFT.** Round 1's review is READY (section 3), but the lead found one wrong path after it (section 3.3)\nand five older unit tests outside the ticket's paths are red by S1 (section 3.2). Both go to the CTO as packages. The\nsha256 column of section 2 is that of the round 1 head and will be rewritten at the ticket's final head.\n\n",
      "tokens": 217
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "### 3.1 Round 1: READY\n\nA fresh read-only independent auditor (Opus 5.5, high, class C3), probe head `13fd1dd34e32` against base\n`1798e82f1201`, session `8035d5c6-1335-4006-8790-318b38724476`. `verdict.py` reads its block as READY (no blocking\nfinding). KPI lines S1, S2, S3, F1 and F2: pass. Findings, none blocking:\n\n| id | where | finding | scope / ordinary work / consequence |\n|---|---|---|---|\n| R1 | `context_watch.py:97-98` | The once-per-session marker is never cleared, so a session that compacts and fills again gets no second reminder (the S1 line still fires every time) | in / yes / other |\n| R2 | `context_watch.py:87-100` | `agent_id` is ignored: if a subagent's PostToolUse event carries the main transcript, the subagent receives the main session's reminder and spends its marker (PLAUSIBLE: the docs do not say which transcript a subagent's event carries) | in / yes / other |\n| R3 | `precompact.py:53-59, 68` | A worker's brief is the newest file in the tree's shared brief folder; overlapping launches in one tree can name another worker's brief | in / no / other |\n",
      "tokens": 272
    },
    {
      "id": "754e6e0de3c92c83cdaa1c5a",
      "path": "tests/unit/hooks/test_w2_176_context_watch.py",
      "text": "\"\"\"W2-176 (DAEO-ktiw) S2, S3 and F1 for context_watch.py: a once-per-session reminder near the window's end.\n\nThe hook runs as a subprocess fed planted PostToolUse events and planted transcripts. A planted window is set by\nrunning the hook through ``python3 -c`` with its module-level table replaced, so no case needs a huge transcript\n[DEC-1140 (1)(b), DEC-445, DEC-838, DEC-901].\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport os\nimport statistics\nimport subprocess\nimport sys\nimport time\nfrom pathlib import Path\n\nimport pytest\n\nREPO_ROOT = Path(__file__).resolve().parents[3]\nHOOKS = REPO_ROOT / \"template\" / \"governance\" / \"kernel\" / \"hooks\"\nHOOK = HOOKS / \"context_watch.py\"\nSTATE = \".gov-runtime/scratch/context_watch\"\nPLANTED_MODEL = \"planted-model-1\"\nPLANTED = {PLANTED_MODEL: 1000}\n\n# Runs the hook with its window table replaced by argv[2] (JSON).\n_PLANT = (\"import json, sys; sys.path.insert(0, sys.argv[1]); import context_watch as c; \"\n          \"c.CONTEXT_LIMITS.clear(); c.CONTEXT_LIMITS.update(json.loads(sys.argv[2])); c.main()\")\n\n\n",
      "tokens": 266
    },
    {
      "id": "046f0fc149373a4d11564b8b",
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "text": "### Finding 14. Superseded decisions still stated as current in this area's tests and in one decision\n\n- **W1-49** `test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own`: its assertion holds under DEC-838, but its failure message says \"the window is set in the owner's user-level settings (DEC-636)\", false since 2026-10-19 (`:50-53`). `README.md` section 1 keeps the rows \"SessionStart in the main tree\" (Wave 1's prompt) and \"The cap\" (cut and `truncated`); batch 6 says they are superseded but leaves them.\n- **W1-29** `TestCompactionPreservesState::test_auto_compact_threshold` is named for DEC-208's 300k setting, and `README.md` section 6 says \"The project sets it to approximately 300 000 tokens; the exact line is `\"autocompact\": 300000`\", the opposite of what W1-49 now asserts. The class docstrings \"`gov close` (W1-30) is not built\" are false: the close calls the watchdog (`src/gov/close/command.py:1096`).\n- **W1-18**: `w1_18_support.py:3` calls Ollama \"the stack's only daemon\" (DEC-798 added a second).\n- **W1-21**: `README.md:176` names `query-vectors.db`; the file is `query-vector-cache.db` (`semantic.py:67`).\n",
      "tokens": 292
    },
    {
      "id": "80c27dcb6c81ec3fd6d1679a",
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "text": "| `test_w1_49_registration.py::test_the_hook_file_exists_in_the_kernel_template` | W1-49 (DAEO-32n6) | **duplicate** | red-phase existence check; the suite's fixtures (W1-49 conftest.py:40) assert the same files exist | CAP-37.g | retire, keep the twin (owner: package R3) |\n| `test_w1_49_threshold.py::test_the_pinned_cli_has_an_auto_compact_window` | W1-49 (DAEO-32n6) | **obsolete** | proves the window can be configured (:80-86), for the 300k setting DEC-838 retired; the rule in force is held by test_a_session_on_this_machine_is_given_no_compaction_threshold (:57-78) | DEC-838 (supersedes DEC-636; changes DEC-208, DEC-248 c) | retire (owner: package R2) |\n| `test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own` | W1-49 (DAEO-32n6) | **valid and needed** | the assertion holds under DEC-838; its failure message still says the window is set in the owner's user-level settings (DEC-636, superseded) (:50-53) | DEC-838 | the orchestrator corrects the message (DEC-866; finding 14) |\n",
      "tokens": 257
    },
    {
      "id": "9c0494561f1a38639f42f7c9",
      "path": "tests/acceptance/W1-49/README.md",
      "text": "### 2.4 Batch 5: where the auto-compact window is set (DEC-665)\n\nThe owner's apply block of 2026-10-11 (commit `8bb34efe`) made `.claude/settings.json` rulesync's output. rulesync\nwrites no env block, and the window moved to the env block of the owner's user-level settings (DEC-636). Two cases of\n`test_w1_49_threshold.py` read the project's `env` key and were red on the integration branch from then on. The\nowner decided a rewrite to the decided state (DEC-665), as a separate designer pass inside the W1-38 round (DEC-669,\nticket `DAEO-3ef2`; `DAEO-32n6` is not reopened).\n\n**Rewritten after the implementation, reason \"owner decision, DEC-665\": 2 cases. Added: none. Removed: none.**\n\n| Before | Now | Decided state it holds | Fails when |\n|---|---|---|---|\n| `test_the_settings_set_the_auto_compact_window_as_an_env_key` | `test_the_project_settings_set_no_auto_compact_window_of_their_own` | rulesync writes no env block: the project's settings do not set the window (DEC-636), so no project entry is read in place of the user-level one (DEC-665) | the `env` key of the project's settings sets the variable; the settings file is missing or is not valid JSON |\n",
      "tokens": 292
    },
    {
      "id": "WAVE-2-LIST",
      "path": "docs/plan/WAVE_2_LIST.md",
      "text": "| W2-L368 | The secrets scan's reuse label prints a store's file name | engineer | The label names the store by an id, or the name is shown to have no secret (the Wave 3 hardening pass). | W2-50 run 8's probe F5, 2026-10-20 (ordinary work: no; DEC-864) |\n| W2-L369 | W2-54's sandboxed-worker test runs a real `gov launch` with the real HOME and leaves `~/gov-os-runs/W1-90/` behind on every regression | independent-test-designer | The test runs with a temporary HOME and leaves nothing behind (a test revision under its ticket's next round, or W2-24). | W2-50 run 8, 2026-10-20 (DEC-864) |\n| W2-L370 | W2-50's change-execution record has no section for DEC-853's scan fix | orchestrator | The CIT-E gains the section as a record-only follow-up at W2-50's close. | W2-50 run 8, 2026-10-20 (DEC-864) |\n| W2-L372 | W1-49's `test_the_project_settings_set_no_auto_compact_window_of_their_own` still cites DEC-636 in its message and docstring; its assertion is right under DEC-838 | independent-test-designer | The wording names DEC-838, with no change to the assertion, at the next touch of W1-49 (DEC-866). | W2-63 run 1, 2026-10-20 |\n",
      "tokens": 283
    },
    {
      "id": "9014a39320aaf8d8195ee92d",
      "path": "tests/acceptance/W1-49/test_w1_49_threshold.py",
      "text": "def test_the_project_settings_set_no_auto_compact_window_of_their_own(settings_env):\n    \"\"\"Success 3, rewritten after implementation (DEC-665). rulesync writes no env block (DEC-636): the generated\n    project settings do not set the window, so nothing in the project stands in front of the user-level entry.\n\n    Before: ``test_the_settings_set_the_auto_compact_window_as_an_env_key``.\n    \"\"\"\n    assert support.WINDOW_KEY not in settings_env, (\n        f\"the env key of {support.SETTINGS_REL} sets {support.WINDOW_KEY}: the window is set in the owner's \"\n        \"user-level settings (DEC-636), and a project entry would be read in its place\"\n    )\n",
      "tokens": 164
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "| `template/governance/kernel/hooks/precompact.py` | One plain-text line on stdout on every run, for every role: `Begin the compaction summary with this line: \"READ FIRST: <path> ...\"`, naming the orchestrator's or lead's CHECKPOINT and its RESUME HERE section, or a worker's brief and record. The checkpoint record, the state block and the systemMessage on error are unchanged; the line comes first, the systemMessage after it | `eb0174da477ff6f4eab7ca5bb133c667079830aa5c5c64f8f8d8337ad8c95086` | `adde0bbeca5854d0da3fce5776f5db066a88a09301a1901b5cd7e8a37380605f` |\n| `template/governance/kernel/hooks/context_watch.py` | New PostToolUse hook: reads the transcript's last 256 KiB, the last non-sidechain assistant usage over the model's window (Opus, Sonnet, Haiku 5.5 and Fable 5.2: 1,000,000; others 200,000); at 85 % or more, once per session (a marker under `.gov-runtime/scratch/context_watch/`), additionalContext with the role's duties and the read-first line, and the sentence that it is a handover aid, not a stop and not an early compaction. Any error: no output, exit 0 | none (new file) | `4f62182637698dbdf7f5d5c79480a3eb50be5505b6dc0418bd479dae5ca7ca18` |\n",
      "tokens": 293
    }
  ],
  "supplementary_query": "Context awareness before compaction, live for every session: the compaction summary opens with the read-the-handover-first line, and a once-per-session reminder near the window's end (DEC-1140 (1)(b))\n{'line': 'S1 On every compaction (trigger auto or manual), precompact.py prints one plain-text line on stdout, which Claude Code merges into the compaction instructions: it tells the summary to begin with \"READ FIRST:\" and the path of the session\\'s checkpoint with its RESUME HERE section (the orchestrator and leads: the CHECKPOINT path the hook already writes), or \"READ FIRST: your brief and your record\" with their paths (workers); its checkpoint writing and its systemMessage on error are unchanged [DEC-1140 (1)(b), DEC-208, DEC-250]', 'verify': \"tests/unit/hooks/test_w2_176_precompact.py: the hook fed a planted PreCompact event (trigger auto, then manual) for GOV_ROLE orchestrator and for engineer prints exactly one stdout line starting with the instruction and naming the right path; the W1-29 and W1-49 acceptance cases pass unchanged in the ticket's worktree through the heavy-job gate\"}\n{'line': \"S2 context_watch.py, a PostToolUse hook, reads the session's transcript_path tail, takes the last assistant message's usage (input plus cache tokens), divides it by the session's window (the model's window from a small table: Opus 5.5 1,000,000; Sonnet 5.5 and Haiku 5.5 their documented windows; unknown models 200,000; for the CTO's own session, GOV_TICKET the coordination ticket, the model's window, DEC-1140 (4); for every lead and worker the smaller of the model's window and 200,000, DEC-1118 (A)), skips events that carry agent_id (subagents), and at 85 % or more injects, once per context window (re-armed when usage falls below 50 %, after a compaction), additionalContext telling the session to write its checkpoint now, update every file that needs it (the role's own list: the CTO's RESUME HERE, DECIDED-NOT-DONE, report-state; a lead's CHECKPOINT; a worker's record), and begin its compaction summary with the read-first line; the text says it is a handover aid, not a stop or an early compaction (DEC-901's precedent, DEC-838 (2)) [DEC-1140 (1)(b), DEC-445]\", 'verify': \"tests/unit/hooks/test_w2_176_context_watch.py: planted transcripts at 50 %, 84 %, 85 % and 99 % of a planted window: no output below 85 %, one additionalContext at 85 %, none on the next call in the same session (a state file under the session's .gov-runtime/scratch), the wording holds the three duties and the not-a-stop sentence; an Opus 5.5 transcript uses 1,000,000\"}\n{'line': \"S3 context_watch.py is fast and fails safe: it reads only the transcript's last 256 KiB, returns within 100 ms on a 50 MB transcript, and on any error (no transcript, unreadable usage, an unknown event) prints nothing and exits 0, so it never slows or blocks a tool call\", 'verify': 'tests/unit/hooks/test_w2_176_context_watch.py: a 50 MB planted transcript measured under 100 ms (median of 5); a missing path, a malformed last line and an empty event each give exit 0 and no stdout'}\n{'line': \"S4 The change goes through CAP-33 as a kernel template delta, recorded in docs/changes/W2-176-CIT-P.md: the evidence (the owner's order, the search of 11-11: hooks live, the window retired by DEC-838, never built: the summary line and the reminder), the proposal with each file's base and new sha256, the independent review's READY, the owner's approval, the promotion; the registration of context_watch.py in .claude/settings.json (PostToolUse) is named as the class (b) ACT that follows the approval [DEC-1140 (1)(b), CAP-33, DEC-315]\", 'verify': \"docs/changes/W2-176-CIT-P.md has a section per CAP-33 step; the sha256 column equals sha256sum of each file at the ticket's head\"}\n{'line': \"F1 Neither hook sets or reads a compaction threshold (no CLAUDE_CODE_AUTO_COMPACT_WINDOW, no --autocompact), returns a decision field (allow, deny, ask, block), or writes outside the session's .gov-runtime/scratch; a planted denial-shaped output is never produced [DEC-838 (1), w2-orchestrator.md \u00a74, \u00a712]\", 'verify': 'tests/unit/hooks/test_w2_176_context_watch.py and test_w2_176_precompact.py: the source holds no window variable; every output parsed has no decision key; a write-tracing run lists only the scratch state file; tests/acceptance/W1-49/test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own passes'}\n{'line': \"F2 The ticket's diff names only its four paths; no .claude/ file, no settings, no other hook changes\", 'verify': \"git diff --name-only <base>..HEAD of the ticket's branch lists only the allowed paths\"}",
  "further_batch": [
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md"
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md"
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md"
    },
    {
      "id": "61f0902fbd23091b1fc07adc",
      "path": "template/governance/kernel/hooks/context_watch.py"
    },
    {
      "id": "bcccff61d6b4f2fa96ade1e4",
      "path": "template/governance/kernel/hooks/context_watch.py"
    },
    {
      "id": "11e758be9d950b514a8eb037",
      "path": "tests/unit/hooks/test_w2_176_context_watch.py"
    },
    {
      "id": "e8f79cfbb22adbeed80c9371",
      "path": "tests/unit/hooks/test_w2_176_context_watch.py"
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md"
    },
    {
      "id": "DAEO-pl6k",
      "path": ".tickets/DAEO-pl6k.md"
    },
    {
      "id": "DAEO-pl6k",
      "path": ".tickets/DAEO-pl6k.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "754e6e0de3c92c83cdaa1c5a",
          "path": "tests/unit/hooks/test_w2_176_context_watch.py"
        },
        {
          "id": "046f0fc149373a4d11564b8b",
          "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md"
        },
        {
          "id": "80c27dcb6c81ec3fd6d1679a",
          "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md"
        },
        {
          "id": "9c0494561f1a38639f42f7c9",
          "path": "tests/acceptance/W1-49/README.md"
        },
        {
          "id": "WAVE-2-LIST",
          "path": "docs/plan/WAVE_2_LIST.md"
        },
        {
          "id": "9014a39320aaf8d8195ee92d",
          "path": "tests/acceptance/W1-49/test_w1_49_threshold.py"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "61f0902fbd23091b1fc07adc",
          "path": "template/governance/kernel/hooks/context_watch.py"
        },
        {
          "id": "bcccff61d6b4f2fa96ade1e4",
          "path": "template/governance/kernel/hooks/context_watch.py"
        },
        {
          "id": "11e758be9d950b514a8eb037",
          "path": "tests/unit/hooks/test_w2_176_context_watch.py"
        },
        {
          "id": "e8f79cfbb22adbeed80c9371",
          "path": "tests/unit/hooks/test_w2_176_context_watch.py"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "DAEO-pl6k",
          "path": ".tickets/DAEO-pl6k.md"
        },
        {
          "id": "DAEO-pl6k",
          "path": ".tickets/DAEO-pl6k.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "11e758be9d950b514a8eb037",
      "reason": "budget exceeded"
    },
    {
      "id": "61f0902fbd23091b1fc07adc",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-pl6k",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-pl6k",
      "reason": "budget exceeded"
    },
    {
      "id": "W2-176-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "W2-176-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "W2-176-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "W2-176-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "bcccff61d6b4f2fa96ade1e4",
      "reason": "budget exceeded"
    },
    {
      "id": "e8f79cfbb22adbeed80c9371",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 11833,
  "budget": {
    "limit": 12000,
    "used": 11833
  },
  "left_out": {
    "count": 1,
    "superseded": [
      "DEC-636"
    ],
    "done": []
  },
  "hash": "707bab81feff925ac6074ae3e0eac4e0f7035d8855bef7af5f7e9786a19a4ae7"
}
