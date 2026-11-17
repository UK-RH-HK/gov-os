---
id: DAEO-3d3o
wbs_id: W2-197
external-ref: W2-197
status: in_progress
deps: []
links: []
created: 2026-11-17T22:00:00Z
type: task
priority: 1
assignee: Usain
tags: [wave-2, emergency-2, memory, brief]
title: 'Memory used by construction: gov brief puts the ticket''s retrieval into every brief, every template says memory first, and every memory call is logged'
class: implementation
role: engineer
profile: STANDARD
state_class: AUTHORITATIVE
allowed_paths:
- src/gov/brief/**
- src/gov/retrieve/command.py
- src/gov/memory_use/**
- src/gov/adopt/facts.py
- governance/project/facts.yaml
- template/governance/kernel/templates/brief.md
- template/governance/kernel/templates/keys.yaml
- template/governance/kernel/templates/role-*.md
- template/governance/kernel/skills/retrieval/SKILL.md
- .claude/templates/**
- .claude/skills/retrieval/SKILL.md
- .claude/agents/**
- .rulesync/skills/retrieval/SKILL.md
- template/.rulesync/skills/retrieval/SKILL.md
- .rulesync/subagents/**
- template/.rulesync/subagents/**
- src/gov/_shipped/template/governance/kernel/templates/**
- src/gov/_shipped/template/governance/kernel/skills/retrieval/SKILL.md
- tests/unit/brief/**
- tests/unit/memory_use/**
- tests/unit/retrieval/test_w2_197_*.py
- tests/unit/adopt/test_w2_197_*.py
reads:
- docs/emergency-2/EMERGENCY-2.md
- docs/emergency-2/audits/02-memory-in-use.md
- docs/audit/emergency-2026-11/retro-P5-memory-use.md
- src/gov/retrieval/retrieve.py
- src/gov/adapters/portability.py
needs: []
waits_on: []
est_loc: 450
kpis:
  success:
  - line: "S1 Every `gov brief` output (each of the six roles, the lead's runs included) holds T-0's section `## What memory holds for this ticket`: the store's commit (12 hex) and folder, the query, the item count, the stop reason and whether it was reranked; one line per evidence item of the ticket's retrieval, in rank order, `<n>. <path>:<start>-<end> <id> <first non-empty line of the item, at most 100 characters>`, inside a fenced block; and two commands: the one that prints the same bundle whole (`gov retrieve --root <store> --ticket <ID> \"<query>\"`) and the one to search again in the session's own words (`gov retrieve --root <store> \"<your question>\"`). The retrieval is `gov.retrieval.retrieve.retrieve(<store>, <query>, ticket=<ID>, role=<the brief's role>)`; the query is the ticket's `title`, else its body's first `# ` heading, else its id; the store is `--store <dir>`, else `GOV_STORE`, else facts.yaml's `paths.store_tree` filled, else the root. `--json` adds `result.memory` (store, commit, query, stop_reason, reranked, refusal, items as {rank, path, start_line, end_line, id}) [EMERGENCY-2 5.4; audit 2 M1]"
    verify: "tests/acceptance/W2-197/: a planted store (lexical index and record store, no vectors, as W2-138's support builds it) and a READY ticket: for each role the brief holds the section, the store's commit, one index line per item of the library's own bundle for the same store, query, ticket and role, in the same order, and both commands; the --json result's memory matches; two runs give the same bytes"
  - line: "S2 The memory block is filtered for the brief's role as the role's own `gov retrieve` would be (DEC-1065 (2)): a test designer's block lists no item under its ticket's implementation paths, an engineer's none under its ticket's acceptance-test path [DEC-1065]"
    verify: "tests/acceptance/W2-197/: a planted store whose evidence for the ticket's query includes a file under the ticket's acceptance path and one under its implementation path, with a role_paths section like this repository's: the engineer's block omits the first, the test designer's the second"
  - line: "S3 T-0 (brief.md) says memory first for everyone: its Commands section holds `Ask memory first:` with `{CMD:retrieve}`, `read every item of the bundle, never head or cut it, and cite the ids you use`, then the search-again-once line; the line `No gov retrieve in the sandbox` and every `outside/inside the sandbox` split for retrieve are gone; no generated brief holds `{QUESTION}`, and every `{UPPER}` slot a generated brief still holds is a form key keys.yaml lists (the session's own forms: SUBJECT, COMMIT_PATHS, ...), QUESTION no longer among them [EMERGENCY-2 5.4, 5.7; audit 2 M2; P5 F1, F9]"
    verify: "tests/acceptance/W2-197/: text checks on template/governance/kernel/templates/brief.md; gov brief for each role on this tree's templates and facts yields no `{QUESTION}`, and each `{[A-Z]...}` slot left is a keys.yaml key"
  - line: "S4 Each role template (role-cto, role-lead, role-engineer, role-test-designer, role-reviewer, role-product-spec, role-research) holds the one shared memory line: `**Memory first:** {CMD:retrieve} before you grep for a concept; read every item of the bundle, never `head` or cut it, and cite the ids you use; if it does not answer, search once more in your own, different words; look a decision up by id in the register.`; so `{CMD:retrieve}` reaches every role's commands table; role-cto's \"Launching work\" says every subagent prompt opens with the memory block (ask memory first, read the whole bundle, search once more in its own words, say in the return how many retrieves helped); no role template keeps an outside/inside-the-sandbox split for retrieve [EMERGENCY-2 5.4; audit 2 M4; P5 F2, F4, F8]"
    verify: "tests/acceptance/W2-197/: each of the seven files holds the shared line verbatim; role-cto's Launching-work section holds the subagent memory block; gov brief's commands table for engineer, product-spec and independent-auditor has a retrieve row"
  - line: "S5 The retrieval skill's step 7 says: read every item of the bundle, never head or cut it, and cite the ids you use; and its text holds the shared memory line with `gov retrieve \"<question>\"` in place of `{CMD:retrieve}` [audit 2 M6, R10; P5 F4]"
    verify: "tests/acceptance/W2-197/: text checks on template/governance/kernel/skills/retrieval/SKILL.md"
  - line: "S6 The generated copies follow their sources: `.claude/templates/<stem>.md` equals the kernel template byte for byte; `src/gov/_shipped/` copies (brief.md, role-cto.md, the retrieval skill) equal theirs; `.rulesync/skills/retrieval/SKILL.md` and `template/.rulesync/skills/retrieval/SKILL.md` and `.claude/skills/retrieval/SKILL.md` carry the new step 7; each `.rulesync/subagents/<role>.md` equals `gov.adapters.portability.compose(root, role)` [audit 2 M10; W2-88, W2-153]"
    verify: "tests/acceptance/W2-197/ copy checks, and tests/unit/adapters and the W2-88 shipped-copy tests (tests/acceptance/W2-88, tests/unit/adopt/test_w2_88_shipped.py) green"
  - line: "S7 facts.yaml's retrieve form is `gov retrieve --root {STORE_TREE} \"<question>\"`; keys.yaml drops QUESTION and holds MEMORY_BLOCK; `gov adopt --facts` writes `gov retrieve \"<question>\"` [audit 2 M3, R7, R8; P5 F9]"
    verify: "tests/acceptance/W2-197/: governance/project/facts.yaml and keys.yaml read as YAML; gov.adopt.facts's retrieve form"
  - line: "S8 Every `gov retrieve` call and every `gov brief` memory retrieval appends one JSON line to the memory-use log: `GOV_MEMORY_LOG` when set, else `<main worktree of the caller's tree>/.gov-runtime/memory-use.jsonl` (the parent of `git rev-parse --git-common-dir`; the tree itself outside git). Fields: ts (UTC ISO), command (`retrieve`|`brief`), role (`--role`, else `GOV_ROLE`; the brief's role for a brief), ticket (`--ticket`, else `GOV_TICKET`; the brief's ticket), session (`--session`, else `GOV_SESSION`, else null), query_sha256 (the first 16 hex of the query's sha256; the query itself is never logged), stop_reason, items, characters (the evidence texts' total length), latency_ms, refusal (the error code, else null), store_commit, reranked, search_number (this session's retrieve count in the log, this call included; null with no session). A refused call (STORE_MISSING, STORE_UNREADABLE, CONTINUATION_INVALID, UNRESOLVED_IDS) is logged with its code [EMERGENCY-2 5.6; P5 F6; audit 2 M7]"
    verify: "tests/acceptance/W2-197/: gov retrieve on a planted store and on a missing one, and gov brief, with GOV_MEMORY_LOG set: one line each with every field of the right type; without it, the line lands in the main worktree's .gov-runtime/memory-use.jsonl when run from a linked worktree"
  - line: "S9 A reader the digest can use: `gov.memory_use.read(path=None, root=None, since=None)` returns the log's records (unreadable lines skipped and counted); `gov.memory_use.per_role_day(records)` counts retrieves, brief retrievals and refusals per day and role; `gov memory-use [--since YYYY-MM-DD] [--json]` prints one line per day and role, `<day> <role> retrieves <n> briefs <n> refused <n>` [EMERGENCY-2 5.6, 10.2; audit 2 M7]"
    verify: "tests/acceptance/W2-197/: a planted log of known lines (one malformed): read's records and skipped count, per_role_day's counts, the command's lines and --since"
  failure:
  - line: "F1 A store that is missing, unreadable or not reranked never refuses a brief: the brief is printed (exit 0) with the block saying `Memory not reached: <CODE> <detail>.` (or reranked false) and both commands, and stderr says `gov brief: MEMORY_UNAVAILABLE <detail>`; a ticket that is not READY is still refused as before"
    verify: "tests/acceptance/W2-197/: --store pointing at a missing folder: exit 0, the block's not-reached line, the stderr warning; W2-152's refusal cases unchanged"
  - line: "F2 A memory-use log that cannot be written (a folder in its place, no permission) never fails or changes a search or a brief: same stdout and exit code as with a writable log"
    verify: "tests/acceptance/W2-197/: GOV_MEMORY_LOG naming a folder: gov retrieve and gov brief give the same output and exit code"
  - line: "F3 Nothing else changes: gov context and its tests are untouched; W2-128's and W2-152's cases that asserted the old brief text or a brief that reads only its inputs are revised by the test designer, no other expectation lowered"
    verify: "tests/unit/brief, tests/unit/retrieval, tests/unit/adapters, tests/acceptance/W2-128, W2-88, W2-152 and tests/unit/optin green; git diff shows no change under src/gov/context"
non_goals:
- "gov context is not retired (the owner's decision, audit 2 decision 1)"
- "gov retrieve's printed shape (M8's index first, gaps behind a flag) is not changed"
- "CLAUDE.md, AGENTS.md and the other skills' memory lines (audit 2 M5, M6 beyond the retrieval skill) are not in this ticket"
- "the store refresh on every commit (M9) is not in this ticket"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-836, DEC-1065, DEC-1092, DEC-1098]
acceptance_tests: {path: tests/acceptance/W2-197/}
---
# Memory used by construction, and the memory-use log

# W2-197 Memory used by construction, and the memory-use log

Filed 2026-11-17 by the ticket lead on the CTO's brief (EMERGENCY-2 §5.4, §5.6, §5.7; §6.1 "Memory by construction; the memory-use log ... build"). The CTO approves the kernel text changes named here by that brief (§3.5).

**Problem (audit 2, `docs/emergency-2/audits/02-memory-in-use.md`; retro P5 F1-F9).** `gov brief` runs no retrieval and puts no memory into a brief; T-0 tells every launched worker not to use `gov retrieve`; its one copyable retrieve command carries an unfilled `{QUESTION}`; role-reviewer has no memory line; no template says read every item; and no log of memory use exists.

**Approach.** Audit 2's Table 2, rows M1 (the memory block), M2 (T-0), M3 (facts, keys, adopt facts; the retrieve form only), M4 (role templates), M6 (the retrieval skill only), M7 (the log and its reader), M10 (the generated copies).

**Interface.**
- `gov brief <role> <ticket> [--store <dir>] [--run ...] [--part ...] [--repair ...] [--json]`; T-0's `{MEMORY_BLOCK}` is filled by `gov.brief.memory` (the block of S1, or F1's not-reached line); stderr warning `gov brief: MEMORY_UNAVAILABLE <detail>`.
- The memory-use log: `GOV_MEMORY_LOG`, else `<main worktree>/.gov-runtime/memory-use.jsonl`; written by `gov.memory_use.append(record, root)`, which never raises.
- The reader: `gov.memory_use.read`, `gov.memory_use.per_role_day`, and `gov memory-use [--since <day>] [--json]`.
