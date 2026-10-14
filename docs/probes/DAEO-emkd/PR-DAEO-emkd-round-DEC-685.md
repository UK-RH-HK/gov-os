---
type: probe
task: DAEO-emkd
reviewer_session: 62a8c15e-f87c-4ae3-99ca-f2d12a976017
implementer_session: f28972a7-7076-4db5-acf5-ac98ac02addc
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: d430db176cf4ef7c7394ed7939dc84226e3b6057
---

# Probe record: W1-02 round, the guard refuses a tool it does not know, `MultiEdit` judged like `Edit` (DEC-685)

- **What was probed.** The round's code at `d430db17` on `w1/W1-02` (one lead session since
  `6ba41665`): `MultiEdit` among the write tools, judged by its file path; one explicit list of 17
  known tools that write no project file and run no command (`Agent`, `Task`, `Skill`, `ToolSearch`,
  `WebFetch`, `WebSearch`, `ListAgents`, `SendMessage`, `TaskStop`, `TodoWrite`, `TaskCreate`,
  `TaskUpdate`, `TaskList`, `TaskGet`, `AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode`); every
  other tool name refused, where it was allowed before. The code change is `5fe02536` (33 lines
  added, 7 removed). The branch is merged directly at the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through
  `gov launch independent-auditor`, read-only, other than the implementers. It wrote nothing to the
  repository; the worktree was at `d430db17` when it left.
- **What held.** In stand-in projects, open and frozen:
  - 9,288 hook calls with spellings near a known name (case, spaces, control characters, look-alikes,
    prefixes, very long names) and with non-string or missing names: none allowed; a non-string name
    ends in the hook's failure answer, which blocks the call;
  - 946 pairs of `Edit` and `MultiEdit` over 11 actors and 43 path shapes: no pair differs in
    decision, exit code or reason; nothing in the list of edits reaches a path;
  - the 17 listed tools are allowed for every actor; `Monitor`, an `mcp__` name and the other
    unlisted names are refused, open and frozen;
  - live in the reviewer's own session: an unlisted tool was refused with the round's reason, so the
    hook has no matcher here; a listed tool passed;
  - `WebFetch` with a `file://` URL is allowed by the guard and refused by the tool itself
    ("Invalid URL"); a URL that spells a held-out path is refused by the held-out rule;
  - every declared actor still reads, writes in its own paths, runs Bash and starts a subagent; no
    tool the launcher, the kernel or the adapter sources name is refused;
  - the largest decision time on large inputs was 0.28 s; the freeze reading, the failure answer and
    the deadline are untouched;
  - the open point DP-13 (which reason answers first) turns no deny into an allow;
  - of the 736 new cases, 326 fail and 410 pass on the guard modules before the round; the 38
    rewritten cases swap an unknown-tool carrier of free text for a listed one with the same
    assertion, none weaker.
- **Findings and their judgement.** None for the merge. Named residuals for
  `governance/project/bootstrap.md` and the Wave 2 list: a skill's text can carry inline shell
  execution that the CLI runs without a Bash tool call (medium; read from the binary, not tried; no
  skill source of the kernel uses it; not new with the round); the launcher's wiring check accepts a
  hook matcher of the three write tools only, under which unknown tools would not reach the guard
  (medium; the kernel registers no matcher); `Agent` with worktree isolation creates a worktree by
  itself; `SendMessage` reaches other sessions; the guard does not judge `WebFetch`'s URL against
  the read rule of the two protected files and relies on the tool's own refusal; an extra path field
  of `Edit` or `MultiEdit` is ignored; harmless tools are now refused (`Monitor`, `Artifact`,
  `Workflow`, the scheduling tools, every `mcp__` name).
- **Not probed.** A real `MultiEdit` call (the installed CLI 2.1.292 offers no such tool); a real
  subagent start; a real skill with inline shell; this repository's two protected files; the suites
  beyond the round's files (the lead ran the whole of `tests/`: 13,120 passed, serial 263 passed).
- **Judgement.** Pass: no fail-open hole that ordinary work produces, the ticket loop is not stopped,
  nothing breaks a Wave 1 exit criterion (DEC-584).
