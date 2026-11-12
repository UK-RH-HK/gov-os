---
id: W2-176-CIT-P
type: change-impact-proposal
status: DRAFT
date: 2026-11-12
branch: w2/W2-176
base: 1798e82f1201
ticket: DAEO-ktiw (W2-176)
author: ticket lead (W2-176)
review: one read-only independent auditor (CAP-33), round 1 READY at 13fd1dd34e32
decisions_carried: [DEC-1140, DEC-838, DEC-901, DEC-445, DEC-208, DEC-250, DEC-315, CAP-33]
state_class: EVIDENCE
---

# W2-176: change-impact proposal (CIT-P) on the PreCompact hook and a new PostToolUse context watch

This change makes every session hand over before compaction: the PreCompact hook tells the compaction summary to begin
with a read-the-handover-first line, and a new PostToolUse hook reminds a session once, at 85 % of its model's
context window, to write its checkpoint and update its files. It changes a kernel hook and adds one, so it goes
through CIT-P (CAP-33). It sets no compaction threshold and stops nothing (DEC-838).

**Status: DRAFT.** Round 1's review is READY (section 3), but the lead found one wrong path after it (section 3.3)
and five older unit tests outside the ticket's paths are red by S1 (section 3.2). Both go to the CTO as packages. The
sha256 column of section 2 is that of the round 1 head and will be rewritten at the ticket's final head.

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

| File | Change | Base sha256 (at 1798e82f1201) | New sha256 (at 13fd1dd34e32, round 1) |
|---|---|---|---|
| `template/governance/kernel/hooks/precompact.py` | One plain-text line on stdout on every run, for every role: `Begin the compaction summary with this line: "READ FIRST: <path> ..."`, naming the orchestrator's or lead's CHECKPOINT and its RESUME HERE section, or a worker's brief and record. The checkpoint record, the state block and the systemMessage on error are unchanged; the line comes first, the systemMessage after it | `eb0174da477ff6f4eab7ca5bb133c667079830aa5c5c64f8f8d8337ad8c95086` | `adde0bbeca5854d0da3fce5776f5db066a88a09301a1901b5cd7e8a37380605f` |
| `template/governance/kernel/hooks/context_watch.py` | New PostToolUse hook: reads the transcript's last 256 KiB, the last non-sidechain assistant usage over the model's window (Opus, Sonnet, Haiku 5.5 and Fable 5.2: 1,000,000; others 200,000); at 85 % or more, once per session (a marker under `.gov-runtime/scratch/context_watch/`), additionalContext with the role's duties and the read-first line, and the sentence that it is a handover aid, not a stop and not an early compaction. Any error: no output, exit 0 | none (new file) | `4f62182637698dbdf7f5d5c79480a3eb50be5505b6dc0418bd479dae5ca7ca18` |
| `tests/unit/hooks/test_w2_176_precompact.py` | 16 unit cases (S1, F1) | none (new file) | n/a (tests) |
| `tests/unit/hooks/test_w2_176_context_watch.py` | 34 unit cases (S2, S3, F1), including a 50 MB transcript under 100 ms (median 16.8 ms) | none (new file) | n/a (tests) |

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
assertions on the checkpoint and the message hold; only their stdout shape conflicts with S1. Package P1 to the CTO.

### 3.3 Found by the lead after round 1

`context_watch.py:70` names the CTO's report-state as `<root>/log/report-state.json`; the file is
`.gov-runtime/scratch/orchestrator/log/report-state.json` (checked in the main tree on 2026-11-12). In scope (S2: the
role's own list), ordinary work for the CTO. Package P2 to the CTO; a fix needs round 2 of the review (DEC-1010).

## 4. Owner's approval

Pending. The owner approves the bytes of section 2 at the ticket's final head.

## 5. Promotion

After the owner's approval: the ticket's branch lands through the queue, and the CTO runs the class (b) ACT that
registers `context_watch.py` under PostToolUse in `.claude/settings.json` (DEC-315; class-rules row
agents-skills-kernel). R1 and R2 are entry criteria of that ACT (the reviewer's recommendation). The PreCompact
registration is unchanged.
