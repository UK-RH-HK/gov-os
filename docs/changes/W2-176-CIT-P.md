---
id: W2-176-CIT-P
type: change-impact-proposal
status: ACCEPTED
date: 2026-11-12
branch: w2/W2-176
base: 1798e82f1201
ticket: DAEO-ktiw (W2-176)
author: ticket lead (W2-176)
review: read-only independent auditors (CAP-33), round 1 READY at 13fd1dd34e32, round 2 (the last, DEC-1010) READY at 7894a35e116f; the cap removed at c10be8fd0266 (section 3.8), not yet reviewed
approval: owner, 2026-11-12, "W2-176's CIT-P approved at 3b6c5cb79d39" (DEC-1142 (1)): context_watch.py sha256 213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242; the earlier approval of 3a580a4b4d42 (the 200,000 cap) withdrawn (DEC-1141 (2)); merged by hand at 3430341c4 (DEC-1141 (4))
decisions_carried: [DEC-1140, DEC-1141, DEC-264, DEC-259, DEC-838, DEC-901, DEC-445, DEC-208, DEC-250, DEC-315, CAP-33]
state_class: EVIDENCE
---

# W2-176: change-impact proposal (CIT-P) on the PreCompact hook and a new PostToolUse context watch

This change makes every session hand over before compaction: the PreCompact hook tells the compaction summary to begin
with a read-the-handover-first line, and a new PostToolUse hook reminds a session once per context window, at 85 % of
its own model's window (no session has a token cap: the owner, 2026-11-12, section 3.8), to write its checkpoint
and update its files. It changes a kernel hook and adds one, so it goes through CIT-P (CAP-33). It sets no compaction
threshold and stops nothing (DEC-838).

**Status: PROPOSED; approval withdrawn, new bytes await review and approval.** Round 1 was READY; the CTO decided its
packages (section 3.2 to 3.4); round 2, the last (DEC-1010), was READY at `7894a35e116f` (section 3.5). The owner
withdrew the approval of `3a580a4b4d42` on 2026-11-12, because those bytes carry the 200,000 cap, and ordered the cap
removed for every session; it is removed at `c10be8fd0266` (section 3.8). The sha256 column of section 2 is that of
the new head. The new bytes await independent review and the owner's approval (section 4).

## 1. Evidence and corroboration

| # | Evidence | Source | State before this change |
|---|---|---|---|
| E1 | The owner's order: "a session that knows its context limit and, when close to compaction, writes its checkpoint, updates every file that needs it, and hands over in the compaction summary with a reminder to read the handover first ... bring it back live for every session: yours, leads and workers." | DEC-1140 (1)(b), 2026-11-11 ~23:05 | Ordered |
| E2 | The CTO's search of 11-11: the PreCompact checkpoint (W1-29) and the SessionStart RESUME HERE injection on compact (W2-62) are live in `.claude/settings.json` | Ticket body; `.claude/settings.json` PreCompact and SessionStart entries | Live |
| E3 | The "knows its limit" half was the 300k auto-compact window (W1-49, DEC-208), retired by DEC-838 for usage; no hook was ever fed the context utilisation | DEC-208, DEC-838, DEC-445 (its residual) | Retired; never built |
| E4 | Never built: the read-first line in the compaction summary, and a reminder near the window's end | Ticket body | Missing |

Corroboration (official documentation, code.claude.com/docs/en/hooks and /model-config, read for CLI 2.1.322 on
2026-11-11):

- "When a PreCompact hook exits 0 and doesn't block, Claude Code uses its stdout as instructions for the compaction
  summary" (cap 10,000 characters). "Claude Code discards a PreCompact hook's `systemMessage` and `continue` fields."
  Exit 2 or `"decision": "block"` blocks compaction.
- PostToolUse input carries the common fields (`session_id`, `transcript_path`, `cwd`, `hook_event_name`) and the
  tool's fields; only SessionStart carries a `model`. Context is added with
  `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}}`.
- "Fable models, Sonnet 5 and later, Haiku 5.5, and Opus 4.7 and later run with the 1M window by default"; Haiku 5.5
  "auto-compact[s] at about 967K tokens by default", so 85 % (850K) comes first.
- A live transcript's assistant line carries `message.model` and `message.usage` (`input_tokens`,
  `cache_creation_input_tokens`, `cache_read_input_tokens`), and `isSidechain` for a subagent's lines.

## 2. Proposal

| File | Change | Base sha256 (at 1798e82f1201) | New sha256 (at c10be8fd0266) |
|---|---|---|---|
| `template/governance/kernel/hooks/precompact.py` | One plain-text line on stdout on every run, for every role: `Begin the compaction summary with this line: "READ FIRST: <path> ..."`, naming the orchestrator's or lead's CHECKPOINT and its RESUME HERE section, or a worker's brief and record. The checkpoint record, the state block and the systemMessage on error are unchanged; the line comes first, the systemMessage after it. `newest()` skips a file removed between listing and stat (R7) | `eb0174da477ff6f4eab7ca5bb133c667079830aa5c5c64f8f8d8337ad8c95086` | `ee19c22dc02e8ed7207dc535e55744e233d527635729a4d37ef252c8fa7e12cf` |
| `template/governance/kernel/hooks/context_watch.py` | New PostToolUse hook: reads the transcript's last 256 KiB, the last non-sidechain assistant usage over the window of the session's own model, for every session alike, with no cap (the table: Opus, Sonnet, Haiku 5.5 and Fable 5.2 1,000,000; a model not in the table 200,000, a model size, not a cap); skips events carrying `agent_id`; at 85 % or more, once per context window (a marker under `.gov-runtime/scratch/context_watch/`, made only once the text is built (R8), removed when usage falls below 50 %), additionalContext with the role's duties (an orchestrator, the CTO included: its CHECKPOINT via `checkpoint_rel` and its RESUME HERE section; a worker: its record) and the read-first line, and the sentence that it is a handover aid, not a stop and not an early compaction; the wording names no cap and no handover limit. Any error: no output, exit 0 | none (new file) | `213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242` (at `c10be8fd0266`, the cap removed, section 3.8; was `ed17fbb0e2b3…` at `4dec7ec3c72c`) |
| `tests/unit/hooks/test_w2_176_precompact.py` | 18 unit cases (S1, F1, R7) | none (new file) | n/a (tests) |
| `tests/unit/hooks/test_w2_176_context_watch.py` | 77 unit cases (S2, S3, F1, R1, R2, R8 and the cap's removal, section 3.8), including a 50 MB transcript under 100 ms | none (new file) | n/a (tests) |
| `tests/unit/hooks/test_resume_hooks.py`, `tests/unit/hooks/test_w29_hooks.py` | Assert-only updates of five cases to S1's stdout form (the read-first line first, the JSON object on the last line); the CTO's P1 (a) | (existing) | n/a (tests) |

The three options (DEC-105): apply now (recommended: the owner ordered it live for every session, DEC-1140 (1)(b));
defer (sessions keep compacting with no read-first line and no reminder); re-baseline (none: no closed specification
is contradicted beyond the five unit tests of section 3.2).

## 3. Independent review

### 3.1 Round 1: READY

A fresh read-only independent auditor (Opus 5.5, high, class C3), probe head `13fd1dd34e32` against base
`1798e82f1201`, session `8035d5c6-1335-4006-8790-318b38724476`. `verdict.py` reads its block as READY (no blocking
finding). KPI lines S1, S2, S3, F1 and F2: pass. Findings, none blocking:

| id | where | finding | scope / ordinary work / consequence |
|---|---|---|---|
| R1 | `context_watch.py:97-98` | The once-per-session marker is never cleared, so a session that compacts and fills again gets no second reminder (the S1 line still fires every time) | in / yes / other |
| R2 | `context_watch.py:87-100` | `agent_id` is ignored: if a subagent's PostToolUse event carries the main transcript, the subagent receives the main session's reminder and spends its marker (PLAUSIBLE: the docs do not say which transcript a subagent's event carries) | in / yes / other |
| R3 | `precompact.py:53-59, 68` | A worker's brief is the newest file in the tree's shared brief folder; overlapping launches in one tree can name another worker's brief | in / no / other |
| R4 | `test_resume_hooks.py:119,130,146,170`, `test_w29_hooks.py:278` | Five older unit tests pin the old stdout (empty, or one JSON object) and are red by S1; outside the ticket's paths | out / yes / other |
| R5 | `context_watch.py:22-29` | On 1M models the reminder fires at 850k, past the about 200k handover asked of leads and workers; with `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` it never fires (not set in the project) | out / yes / other |
| R6 | `context_watch.py:92`, `precompact.py:141` | Without `CLAUDE_PROJECT_DIR` the project root is the working directory (Claude Code sets it for every hook) | in / no / other |
| R7 | `precompact.py:59` | A file removed between listing and stat in `newest()` escapes before the line is printed | in / no / other |

### 3.2 The five older unit tests (R4)

`tests/unit/hooks/test_resume_hooks.py::test_an_unset_role_is_not_the_orchestrator`,
`::test_precompact_appends_one_block_and_sessionstart_warns`, `::test_a_checkpoint_precompact_cannot_write_is_left_as_it_was`,
`::test_a_write_that_fails_part_way_leaves_the_checkpoint_as_it_was` and
`tests/unit/hooks/test_w29_hooks.py::TestPreCompactCombined::test_checkpoint_failure_reports_systemmessage`. Their
assertions on the checkpoint and the message hold; only their stdout shape conflicts with S1. Package P1; the CTO
decided (a): the two files joined the ticket's paths for assert-only updates, done at `317955a4b`.

### 3.3 Found by the lead after round 1

`context_watch.py:70` named the CTO's report-state as `<root>/log/report-state.json`; the file is
`.gov-runtime/scratch/orchestrator/log/report-state.json`. Package P2; the CTO decided (a): corrected, with R7, at
`7894a35e1`.

### 3.4 The CTO's decisions on run 1's packages (DEC-1112 (3), 2026-11-12, recorded in the ticket)

P1 (a) and P2 (a) above; P3: R2 (subagent events skipped) and R1 (re-armed below 50 %) in this delta, not as ACT entry
criteria; P4: leads and workers reminded against `min(model window, 200,000)` (DEC-1118 (A)), the CTO's own session
against its model's window (DEC-1140 (4)), in this delta (it answers R5's DEC-1118 point). One fresh engineer batch
(Opus 5.5, high, class C3, session `b33af278-3a0b-4622-b7f5-dd4ad3a7dd43`): tests first at `317955a4b`, code at
`7894a35e1`.

### 3.5 Round 2 (the last, DEC-1010): READY

A fresh read-only independent auditor (Opus 5.5, high, class C3), probe head `7894a35e116f` against base
`1798e82f1201`, session `c07b0a81-dbea-40e1-8ada-31dbf17a0330`. `verdict.py` reads its block as READY (True, no
reasons). KPI lines S1, S2, S3, F1 and F2: pass; P1 to P4, R1, R2 and R7 checked as decided; the two older test files
changed only in assertions; a hostile `GOV_TICKET` (traversal, missing, directory, oversized, `class:` past 4 KiB or
in the body) falls to the 200,000 cap. One finding, not blocking:

| id | where | finding | scope / ordinary work / consequence |
|---|---|---|---|
| R8 | `context_watch.py:126-129` | The window's marker is made before the reminder text is built; if building it fails (for a lead, the import of `checkpoint_rel` from `precompact.py` beside it), that window's reminder is spent silently until usage falls below 50 %. Only a partial copy or rename of the hooks folder reaches it | in / no / other |

R3 and R6 stay recorded rows (ordinary work no, consequence other). R8 is recorded here; building the text before
the marker closes it, a candidate for the registration ACT's entry criteria or a follow-up (no third round, DEC-1010).

### 3.6 Verification at the final head

`lead_verify` at `7894a35e116f`: 4005 tests, 7 failed, 6 skipped. P1's five reds are gone. One case,
`tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`,
passed alone on a re-run (load-sensitive). Six `tests/unit/accept/test_w2_96_*` signal and timeout cases were also red
at round 1's verification and alone then; neither those tests nor this delta reference the other (the delta changes no
`src/` file), so they are not caused by this change. The engineer's runs: unit hooks folder 167 passed; W1-29, W1-49
and W2-62 acceptance regression 147 passed.

### 3.7 R8

R8 fixed at `4dec7ec3c72c` (the text built before the marker; red test at `f50d59033736`).

### 3.8 The cap removed (the owner, 2026-11-12)

The owner's order (chat, 2026-11-12 ~02:30; the CTO records it as DEC-1141, replacing DEC-1118 (A) entirely): no
session has a token cap; the CTO, leads, workers and helpers each use their model's full window and compact, the
checkpoint and handover written by the hook before compaction and the summary opening with the read-first line. The
owner withdrew the approval of `3a580a4b4d42`, because those bytes carry the cap. This replaces P4 (section 3.4) and
the CTO-only branch of DEC-1140 (4)'s delta.

- **Code** (`c10be8fd0266`): `HANDOVER_CAP` and the coordination-ticket test (`is_cto`) removed; every session's window
  is its own model's (`limit(model)`); the CTO's wording branch went with the test, so an orchestrator on the
  coordination ticket gets an orchestrator's text (its CHECKPOINT via `checkpoint_rel`, its RESUME HERE section) and no
  longer names `DECIDED-NOT-DONE.md` or `report-state.json` (P2's path is gone with the branch). Kept: R8's order, the
  re-arm below 50 %, the subagent skip, the 256 KiB tail, exit 0 on any error.
- **Tests first** (`e36a9c51b`, red on the hook at `4dec7ec3c72c`: 33 failed, 44 passed): a lead, an engineer or a test
  designer on each 1M model silent at 170k, 180k, 200k and 849,999 and reminded at 850k (18 red); no session (the
  CTO, a lead, an engineer, a test designer) reminded below 85 % of its own window, four 1M models and an unknown one
  (12 red: the non-CTO sessions on 1M models); an Opus transcript at 180k silent for every session (1 red); the
  coordination ticket changes nothing in the text (2 red); the wording names no 200k, limit or cap (green before and
  after, a guard). Removed: the CTO-only cases (DECIDED-NOT-DONE and report-state wording, the coordination-ticket
  identity cases, the 180k CTO/lead contrast). Two lead cases planted at 190k on Opus moved to 900k.
- **Green at `c10be8fd0266`**: the file 77 passed; `tests/unit/hooks` 197 passed, 36 deselected (`tests/conftest.py`'s
  own selection; none of this file's 77 among them); acceptance `W1-29` 42 passed, `W1-49` 63 passed, `W2-62` 42
  passed (one folder per run, `-m "not local_only" -k "not real and not green_here and not time_limit"`, `HOME` an
  empty folder).

## 4. Owner's approval

The approval of `3a580a4b4d42` was withdrawn by the owner (2026-11-12): those bytes carry the cap. Pending for the new
bytes: independent review of `c10be8fd0266` (section 3.8), then the owner approves the bytes of section 2 at the
ticket's final head.

Approved by the owner on 2026-11-12 (DEC-1142 (1)): "W2-176's CIT-P approved at 3b6c5cb79d39", `context_watch.py` sha256
`213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242` (no token cap), after the delta review READY; the delta review's
F1 (a) amended S2 with no new bytes, and its F2 rides this approval edit (`decisions_carried` names DEC-1141). Merged by hand at
3430341c4 (DEC-1141 (4)); ACT-CONTEXT-WATCH-1 (`5bdfa098`) registers the hook.

## 5. Promotion

After the owner's approval: the ticket's branch lands through the queue, and the CTO runs the class (b) ACT that
registers `context_watch.py` under PostToolUse in `.claude/settings.json` (DEC-315; class-rules row
agents-skills-kernel). R1 and R2 are closed in this delta (section 3.4); R8 may be named as that ACT's entry
criterion. The PreCompact registration is unchanged.
