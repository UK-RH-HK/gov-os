---
milestone: "Memory in use, 2026-11-02 to 2026-11-16 (the owner's request of 2026-11-16)"
commit: 4416b8403a386da14cd2a9f7a631846e4a8e2a1b
author: independent auditor (fresh, read-only), returned as text; saved verbatim in substance by the CTO (the guard refused the auditor's own write under drafts/)
evidence: /tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/acd80751-ac8f-4230-9bae-15c678a54895/scratchpad/memaudit-use/ (scan.py, roles.py, aggregate.py, retr_detail.py; out/*.json)
---

# Part 5: memory in use

## 1. Method and coverage
2,594 transcript files, 1,749 sessions with activity, 301 launch records, 453 result logs (11-02 to 11-16). Role by: launch
record; a lead result log naming the session; the 13 CTO sessions by id; the first "You are …" line; the folder. Memory
calls: shell commands starting `gov retrieve`, `gov context`, `gov brief` (not heredoc bodies, quoted text or piped greps;
`--help` and `gov context --json` separate). Greps sorted: id lookups (allowed), code, state, concept searches. "Same need"
judged on the first concept grep of the first 10 sessions per role by session id: CTO 1/10, subagents 5/10, leads 1/10,
engineers 2/10, test designers 2/10, reviewers 0/10. All 141 retrieves tagged by purpose; 48 were questions; for each:
how much of the bundle was seen, faults, a second search within 15 calls, a grep/read within 5 calls, bundle ids used and
their rank. Not read: the operator agent's transcripts and OPERATOR1 copies; WALLS and sets rehearsal folders; `-tmp-*`
fixtures and skill-eval folders; act-permissions and claude-copies folders; 845 empty sessions; 10 launched sessions with
no transcript; the live session acd80751 (no cost record yet). Skipped as possible evaluation content: 21 retrieves in 3
readiness-review subagents (11-08 01:03-01:09), counted, not quoted. Nothing under ~/gov-os-eval, hidden, held out or
secret was opened.

## 2. Tables
**A. Memory calls against greps and reads**

| role | sessions | retrieve: questions / checks / dev tests | context / --json | brief | greps | concept greps | est. memory-need greps | register greps and reads | reads (of docs, tickets) |
|---|---|---|---|---|---|---|---|---|---|
| CTO | 13 | 6/18/19 | 8/4 | 222 | 3,658 | 998 | ~100 | 379 | 3,920 (880) |
| CTO subagents | 487 | 3/1/19 (+21 evaluation probes) | 1/10 | 51 | 11,166 | 2,577 | ~1,290 | 1,705 | 11,199 (3,198) |
| leads | 266 | 20/1/0 | 339/34 | 2 | 3,794 | 607 | ~60 | 312 | 4,758 (774) |
| engineers | 230 | 8/0/0 | 0 | 1 | 2,769 | 274 | ~55 | 104 | 4,097 (637) |
| test designers | 357 | 7/0/0 | 0 | 1 | 3,266 | 392 | ~78 | 205 | 5,309 (599) |
| reviewers | 261 | 1/0/0 | 0/4 | 2 | 3,508 | 683 | <70 | 346 | 4,259 (1,207) |
| product-spec | 51 | 3 | 0 | 0 | 240 | 99 | n/a | 68 | 397 |
| research | 5 | 0 | 0 | 0 | 41 | 15 | n/a | 14 | 68 |
| product CTOs | 12 | 0/8/0 | 0 | 61 | 353 | 136 | n/a | 1 | 794 |
| product workers | 52 | 0 | 0 | 0 | 430 | 218 | n/a | 0 | 535 |

**B. Question retrieves**

| role | calls (sessions) | whole bundle seen | cut short or filtered | preview only | used | used an item ranked 2nd or lower | missed, then a second search | missed, no second search | grep/read within 5 calls | degraded / failed | median latency |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CTO | 6 (2) | 2 | 1 | 0 | 1 | 0 | 1 | 4 | 3 | 3/0 | 1.0 s |
| subagents | 3 (3) | 0 | 1 | 2 | 2 | 1 | 0 | 1 | 3 | 0/0 | 2.6 s |
| leads | 20 (16) | 8 | 11 | 0 | 11 | 10 | 1 | 8 | 18 | 0/0 | 4.9 s |
| engineers | 8 (7) | 3 | 3 | 2 | 2 | 1 | 0 | 6 | 7 | 5/2 | 2.6 s |
| test designers | 7 (5) | 2 | 3 | 2 | 4 | 0 | 1 | 3 | 7 | 4/2 | 3.7 s |
| reviewers | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 1/0 | n/a |

**C. Refusals and brief gaps.** Leads' `gov context`: 143 of 373 refused (CONTEXT_OVER_CEILING 103 on 50 tickets;
BLOCKED, the store lacks a decision, 24 on 13; STORE_MISSING 16 on 14). 84 of 245 lead returns name the ceiling as a
brief gap; 18 built briefs by hand (~448 minutes by their estimates); `--budget` raised to 8,000-40,000. CTO and subagent
`gov brief` refusals: NON_GOALS_MISSING 83, BRIEF_NOT_READY 35, KPI_NO_VERIFY 33, EST_LOC_OVER 30, others ~36;
CONTEXT_OVER_CEILING 8. Product CTOs: BRIEF_NOT_READY 10, PLACEHOLDER_LEFT 10. Workers' brief_gaps "none" in 194 of 195.

**D. Cost**

| role | USD (sessions) | input / output tokens (M) | memory's share of tool output | concept/topic share |
|---|---|---|---|---|
| CTO | 3,450 (12; very likely includes subagents) | 6,581 / 11.9 | 0.7% | 36% |
| subagents | not recorded separately | 5,905 / 32.0 | 0.2% | 38% |
| leads | 877 (259) | 2,006 / 11.0 | 2.3% | 22% |
| engineers | 726 (227) | 1,814 / 10.9 | 0% | 21% |
| test designers | 880 (356) | 2,024 / 15.5 | 0% | 13% |
| reviewers | 717 (261) | 1,169 / 11.2 | 0% | 27% |
| product-spec / research | 40 / 5 | | | 49% / 22% |
| product CTOs / workers | 122 / 69 | | 3.8% / 0% | 40% / 76% |

A lead's bundle: median 8,660 characters (~2,200 tokens). The product logs no retrieve timings.

## 3. Findings (all in scope, reachable in ordinary work; none fails open or loses work, so none blocks; F1 needs the owner)
- **F1. Launched workers are told not to use memory (DEC-1065), and when they tried it was degraded.** 835 of 848 worker sessions made no retrieve; of 16 calls, 10 degraded (embedder unreachable from the sandbox), 4 failed, 2 whole. Change (product): give the embedder single-socket sandbox access as W2-127 did for the reranker; then a package for the owner to replace brief.md's "No `gov retrieve` in the sandbox" with "Ask memory first … Search again once".
- **F2. The CTO's subagents almost never use memory.** 3 question retrieves against ~1,290 memory-need greps; 74 of 488 prompts mention memory. Change (template): a memory block in every subagent prompt (role-cto.md, "Launching work").
- **F3. `gov context` refuses 38 % of the leads' calls** (table C). Change (product and facts): size the ceiling to the ticket, trimming first; `--root {STORE_TREE}` in facts.yaml's context.run; refresh the store on every decision-record commit or read an unindexed mandatory decision from the register by id; always fill `{STEP:context_ceiling}`.
- **F4. Leads cut the bundle short and seldom search again.** 11 of 20 cut (9 with `| head -40..120`); 1 of 9 misses had a second search; 18 of 20 went straight to grep/read; when used, 10 of 11 used an item ranked 2nd or lower. Change: "read every item, never head or cut, cite the ids used" in the retrieval skill step 7, role-lead.md line 21, brief.md; product: `gov retrieve` prints a one-line index of all items first.
- **F5. The CTO uses memory for service checks, not its own questions** (18 checks, 19 dev tests, 6 questions; ~100 memory-need greps). Change (template): w2-orchestrator.md: ask memory once, then once more in own words, before grepping for a concept; "what did DEC-n decide" by id in the register.
- **F6. The product keeps no log of memory use** (DEC-836 asks for it in the digest). Change (product): one line per memory call to `.gov-runtime/memory-use.jsonl` (role, ticket, query hash, stop reason, items, characters, latency, refusal); the digest reads it.
- **F7. Product CTOs and adopters don't use memory** (EXAMIN CTO 0 retrieves in 664 calls; adopters' 8 were "readme" smoke checks). Change (template): role-cto's memory line in both fixed first messages and the adopted repository's CLAUDE.md.
- **F8. role-reviewer.md has no memory line** (1 retrieve against 346 register greps and reads). Change: add brief.md's memory lines.
- **F9. A copyable retrieve command is malformed** (`{CMD:retrieve}` with `"{QUESTION}"` unfilled in 23 briefs). Change: `gov retrieve --root {STORE_TREE} "<question>"`, or `gov brief` refuses an unfilled placeholder.

Probed and sound: register greps are mostly id lookups; leads rerank bundles they read; latency 1-5 s and bundle ~2,200 tokens fine; workers follow DEC-1065; no hidden content reached a working session.

## 4. Conformance
| item | class | evidence |
|---|---|---|
| DEC-836 | WEAKENED | w2-orchestrator.md, .claude/templates/brief.md |
| DEC-1092 (1) | WEAKENED | retrieval SKILL.md, brief.md |
| DEC-1098 (1) | WEAKENED | register, retrieval SKILL.md |
| DEC-1065 | OK | brief.md |
| role-lead "Ask memory, not the register" | WEAKENED | role-lead.md |
| context ceiling step (DEC-1027) | WEAKENED | facts.yaml, role-lead.md |

```verdict
{"kpis": [{"kpi": "Q1 uses memory first", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "Q2 uses it well", "verdict": "fail", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "Q3 finds what it needs", "verdict": "fail", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "Q4 what it costs", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
