---
id: DAEO-ktiw
status: in_progress
deps: []
links: [DAEO-zsvl, DAEO-32n6, DAEO-juee]
created: 2026-11-11T23:21:47Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-176
tags: [wave-2, kernel, hooks, cit-p, standard]
wbs_id: W2-176
title: 'Context awareness before compaction, live for every session: the compaction summary opens with the read-the-handover-first line, and a once-per-session reminder near the window''s end (DEC-1140 (1)(b))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: STANDARD
depends_on: []
waits_on: []
allowed_paths:
- template/governance/kernel/hooks/precompact.py
- template/governance/kernel/hooks/context_watch.py
- tests/unit/hooks/test_w2_176*
- tests/unit/hooks/test_resume_hooks.py   # assert-only updates for S1's stdout line (the CTO, P1 (a), 2026-11-12)
- tests/unit/hooks/test_w29_hooks.py      # the same
- docs/changes/W2-176-CIT-P.md
# .claude/settings.json out of the paths: the PostToolUse registration of context_watch.py is a class (b) ACT after the owner's approval (DEC-315, class-rules row agents-skills-kernel)
reads:
- template/governance/kernel/hooks/**
- .claude/settings.json
- .rulesync/hooks.jsonc
- template/.rulesync/hooks.jsonc
- src/gov/checkpoint/**
- tests/acceptance/W1-29/**
- tests/acceptance/W1-49/**
- tests/acceptance/W2-62/**
needs:
- template/governance/kernel/hooks/precompact.py   # W1-29's checkpoint hook, live since 9274e678350d
- template/governance/kernel/hooks/sessionstart.py # W2-62's RESUME HERE injection on compact, clear and resume
est_loc: 160
kpis:
  success:
  - line: "S1 On every compaction (trigger auto or manual), precompact.py prints one plain-text line on stdout, which Claude Code merges into the compaction instructions: it tells the summary to begin with \"READ FIRST:\" and the path of the session's checkpoint with its RESUME HERE section (the orchestrator and leads: the CHECKPOINT path the hook already writes), or \"READ FIRST: your brief and your record\" with their paths (workers); its checkpoint writing and its systemMessage on error are unchanged [DEC-1140 (1)(b), DEC-208, DEC-250]"
    verify: "tests/unit/hooks/test_w2_176_precompact.py: the hook fed a planted PreCompact event (trigger auto, then manual) for GOV_ROLE orchestrator and for engineer prints exactly one stdout line starting with the instruction and naming the right path; the W1-29 and W1-49 acceptance cases pass unchanged in the ticket's worktree through the heavy-job gate"
  - line: "S2 context_watch.py, a PostToolUse hook, reads the session's transcript_path tail, takes the last assistant message's usage (input plus cache tokens), divides it by the session's window (the model's window from a small table: Opus 5.5 1,000,000; Sonnet 5.5 and Haiku 5.5 their documented windows; unknown models 200,000; every session against its own model's window, with no cap, DEC-1141 (3)), skips events that carry agent_id (subagents), and at 85 % or more injects, once per context window (re-armed when usage falls below 50 %, after a compaction), additionalContext telling the session to write its checkpoint now, update every file that needs it (the checkpoint the precompact hook names for the session; the role's own records beyond it are the role's to keep: DEC-1142 (1) F1 (a)), and begin its compaction summary with the read-first line; the text says it is a handover aid, not a stop or an early compaction (DEC-901's precedent, DEC-838 (2)) [DEC-1140 (1)(b), DEC-445]"
    verify: "tests/unit/hooks/test_w2_176_context_watch.py: planted transcripts at 50 %, 84 %, 85 % and 99 % of a planted window: no output below 85 %, one additionalContext at 85 %, none on the next call in the same session (a state file under the session's .gov-runtime/scratch), the wording holds the three duties and the not-a-stop sentence; an Opus 5.5 transcript uses 1,000,000"
  - line: "S3 context_watch.py is fast and fails safe: it reads only the transcript's last 256 KiB, returns within 100 ms on a 50 MB transcript, and on any error (no transcript, unreadable usage, an unknown event) prints nothing and exits 0, so it never slows or blocks a tool call"
    verify: "tests/unit/hooks/test_w2_176_context_watch.py: a 50 MB planted transcript measured under 100 ms (median of 5); a missing path, a malformed last line and an empty event each give exit 0 and no stdout"
  - line: "S4 The change goes through CAP-33 as a kernel template delta, recorded in docs/changes/W2-176-CIT-P.md: the evidence (the owner's order, the search of 11-11: hooks live, the window retired by DEC-838, never built: the summary line and the reminder), the proposal with each file's base and new sha256, the independent review's READY, the owner's approval, the promotion; the registration of context_watch.py in .claude/settings.json (PostToolUse) is named as the class (b) ACT that follows the approval [DEC-1140 (1)(b), CAP-33, DEC-315]"
    verify: "docs/changes/W2-176-CIT-P.md has a section per CAP-33 step; the sha256 column equals sha256sum of each file at the ticket's head"
  failure:
  - line: "F1 Neither hook sets or reads a compaction threshold (no CLAUDE_CODE_AUTO_COMPACT_WINDOW, no --autocompact), returns a decision field (allow, deny, ask, block), or writes outside the session's .gov-runtime/scratch; a planted denial-shaped output is never produced [DEC-838 (1), w2-orchestrator.md §4, §12]"
    verify: "tests/unit/hooks/test_w2_176_context_watch.py and test_w2_176_precompact.py: the source holds no window variable; every output parsed has no decision key; a write-tracing run lists only the scratch state file; tests/acceptance/W1-49/test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own passes"
  - line: "F2 The ticket's diff names only its four paths; no .claude/ file, no settings, no other hook changes"
    verify: "git diff --name-only <base>..HEAD of the ticket's branch lists only the allowed paths"
non_goals:
- the .claude/settings.json registration (a class (b) ACT after the owner's approval)
- any change to sessionstart.py (its RESUME HERE injection on compact already works, W2-62)
- any compaction threshold or early stop (DEC-838)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources:
- DEC-1140
- DEC-1118
- DEC-264
- DEC-259
- DEC-838
- DEC-901
- DEC-445
- DEC-208
- DEC-250
- DEC-315
- CAP-33
acceptance_tests:
  path: tests/unit/hooks/
  author: engineer (STANDARD, unit cases beside the hooks; the W1-29, W1-49 and W2-62 acceptance suites as the regression)
track: A
list_rows: []
---
# W2-176 Context awareness before compaction, live for every session

**Why (the owner, 2026-11-11 ~23:05, DEC-1140 (1)(b)):** "a session that knows its context limit and, when close to
compaction, writes its checkpoint, updates every file that needs it, and hands over in the compaction summary with a
reminder to read the handover first, so it resumes as fresh as needed ... bring it back live for every session: yours,
leads and workers."

**What the search found (CTO's helper, 11-11 23:30):** the PreCompact checkpoint (W1-29) and the SessionStart RESUME HERE
injection on compact (W2-62) are live (`.claude/settings.json:15-37`; PreCompact last fired 11-11 03:25); the emergency
did not switch them off. The "knows its limit" half was the 300k auto-compact window (W1-49, DEC-208), retired by DEC-838
on 10-19 for usage; no hook was ever fed the context utilisation (DEC-445's residual). Never built: the read-first line in
the compaction summary, and a reminder near the window's end. CLI 2.1.322 merges a PreCompact hook's stdout into the
compaction instructions and gives every hook `transcript_path`. DEC-1128 does not cover this (it is about switched-off
controls and new guard refusals); DEC-1140 (1)(b) is the order.

**Class C3** (kernel hooks): engineer and reviewer on Opus, high (RUBRIC-2). Profile STANDARD: unit cases by the engineer
beside the hooks, one independent review of the delta (CAP-33), then the owner's approval of the bytes, then the
registration ACT.

- **Delegated (the CTO, DEC-1112 (3), 2026-11-12), run 1's packages:** P1 (a): the two older hook test files added to the
  paths for assert-only updates (the read-first line first, the JSON object on the last line; DEC-264, DEC-259 read with
  DEC-1140). P2 (a): the reminder's report-state path corrected (the CTO's file is
  `.gov-runtime/scratch/orchestrator/log/report-state.json`), with R7 (OSError caught in `newest()`), by a fresh engineer.
  P3: R2 (a), subagent events skipped; R1: re-armed once usage falls below 50 % (S2 above). P4: [replaced by DEC-1141 (3): no token cap; every session is reminded at 85 % of its own model's window; HANDOVER_CAP
  and the CTO-only branch removed]. Then review round 2, the last one (DEC-1010).
- **DEC-1141 (2026-11-12):** the owner withdrew the approval of `3a580a4b4d42` (its bytes carry the cap); the cap and the CTO-only
  branch are removed, R8 fixed, the delta reviewed, the new bytes to the owner.

## Approved (the owner, DEC-1142 (1), 2026-11-12 ~09:50)

The CIT-P approved at `3b6c5cb79d39` (`context_watch.py` sha256 `213882efd7b8...`). Its delta review's F1 (a): S2 amended above to drop the two file names the no-cap bytes no longer print, no new bytes; F2 (the record's `decisions_carried`) rides the approval edit. Hand merge after S6 and the unit suites (DEC-1141 (4)); then ACT-CONTEXT-WATCH-1 (a), the matcher `Bash`.
