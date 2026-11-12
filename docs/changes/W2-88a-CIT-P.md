---
id: W2-88a-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-12
branch: w2/W2-88a
base: ba27e4c0d
head: f1ae5fecbc52 (the skill text; the next commit adds only this record)
ticket: DAEO-pg6i (W2-88a)
task: DAEO-pg6i
author: product-spec (W2-88a worker)
review: PENDING (independent review not yet made; the ticket lead records it)
decisions_read: [DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, DEC-1072, DEC-1071, DEC-1074, DEC-1083, DEC-1116, DEC-1050]
decisions_carried: [DEC-1150, DEC-1098, DEC-1130, DEC-1083]
state_class: EVIDENCE
---

# W2-88a: change-impact proposal (CIT-P) on the adopt skill

This change gives the adopt skill the two sections two tickets filed for it: A9's step (the Wave 0 memory practice, seven
steps in order, W2-88's S17) and the Verify pass for an adopted repository's tickets (W2-174's S5). The owner moved both
lines to one ticket of one role so the skill is written once under one CIT-P (DEC-1150 (1), DEC-995, DEC-996 (1)). The
kernel skill is a kernel file, so the owner approves its bytes before the merge (CAP-33). The practice record's section 6
(`docs/research/W2-88-memory-practice.md`, +13 -8) is refreshed to the same seven steps; it is not a kernel file.

## 1. What triggers the change

| # | Trigger | Source | State before this change |
|---|---|---|---|
| T1 | W2-88's S17: A9's step in the adopt skill states the practice in order (assess and plan; census the links and build the graph; the store with the standard and its refresh; the verdict and tuning sets written; the tuning set measured and the structure fixed until its halves agree within 5 points; the verdict set declared and measured once; every method and figure recorded) and points to the practice record | DEC-1150 (1) (moved word for word); DEC-1098 (1); DEC-1072 (2); DEC-1071 (1)-(3); DEC-1074 (4) | Open: the skill had no A9 step and said "A9 itself" is Wave 3 |
| T2 | W2-174's S5: the skill states the Verify pass (when it runs, who writes the clauses, what checks them, that the owner approves the rule once) | DEC-1150 (1) (moved word for word); DEC-1130; DEC-1083 | Open: the skill had no Verify section |
| T3 | This record: the kernel skill's sha256 before and after, the lines added or removed, the independent review and the owner's approval of the bytes before the merge; the two `.rulesync` copies equal the kernel copy | CAP-33; DEC-1116 | Open |

## 2. The kernel file: `template/governance/kernel/skills/adopt/SKILL.md`

| | sha256 |
|---|---|
| before (`ba27e4c0d`) | `641a347b9b14101dde711f3550f087e714e404575f780be2a3cd91ff2925102d` |
| after (`f1ae5fecbc52`) | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` |

The sha256 before is that of the file at the base `ba27e4c0d`; the sha256 after is that of the file as the latest commit of
this ticket that changes it holds it (`f1ae5fecbc52`).

25 lines added, 2 removed (`git diff --numstat ba27e4c0d f1ae5fecbc52 -- template/governance/kernel/skills/adopt/SKILL.md`:
`25 2 template/governance/kernel/skills/adopt/SKILL.md`).

The lines added:

```markdown
Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, the full A9 (its lite form, the Wave 0 memory practice, is the section below), A11 (full audit) and the full verdict.

## A9: Wave 0 memory practice

An adopted repository gets its memory built in Wave 0, in the order below (A9 lite). The practice record `docs/research/W2-88-memory-practice.md` holds the methods, the figures and the lessons behind each step.

1. Assess the repository and plan its refactoring for full indexing.
2. Census the stated links (records, front matter, trailers, text) and build the graph from them.
3. Build the store with the standard (Gov OS's memory standard, pinned and written in the A9 record) and its refresh (the store rebuilt after every merge, a failed build leaving the last good store in service). [DEC-1098 (1), DEC-1072 (2)]
4. Have the verdict set and the tuning set written, by independent writers under the rubric, both held outside every worktree. [DEC-1071 (1)-(3), DEC-1074 (4)]
5. Measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points. [DEC-1071 (1)-(3), DEC-1074 (4)]
6. Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]
7. Record every method and figure, in the adopted repository's copy of the practice record. [DEC-1072 (2)]

## Verify clauses for adopted tickets

A repository adopted by Gov OS brings tickets written before adoption, and the brief of a ticket is refused while a KPI line has no `Verify:` clause. The pass below gives such a ticket its clauses and leaves the ready check as it is. [DEC-1130, DEC-1083]

- The pass runs for a ticket about to launch, not for the whole tracker. [DEC-1130]
- A product-spec session writes the clauses; the tool never writes one. [DEC-1130, DEC-1050]
- Three things check the clauses: the tool, the ticket's test designer and the auditor's sample. [DEC-1130, DEC-1083]
- The owner approves the rule once, not ticket by ticket. [DEC-1130]

The tool is `gov adopt`. Its list option prints, for each open or in-progress ticket that has a KPI line with no verify, the ticket id and the labels of those lines, and the answers file names only the tickets about to launch. Its apply option takes the answers file (YAML, outside the repository: ticket id, then label, then clause) and checks it before it writes anything: every named ticket exists and is not closed, every named label exists, every line still lacking a verify is answered, and each clause is text of its own. It then appends ` Verify: <clause>` to the lines' text, editing the text only (no YAML dump, which would lose comments), and adds the marker `verify_pass: <date> <session>` to the ticket's front matter. [DEC-1130]
DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1130, CAP-44, CAP-54.
```

The lines removed (the Wave 3 sentence, rewritten so the skill no longer says "A9 itself" is Wave 3 while A9's Wave 0
practice has its own section; and the sources line, extended with the sources the new text cites):

```markdown
Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, A9 itself, A11 (full audit) and the full verdict.
DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, CAP-44, CAP-54.
```

Two choices of the writer, for the reviewer: (a) the Wave 3 sentence now reads "the full A9 (its lite form, the Wave 0
memory practice, is the section below)", since W2-88's S10 calls the Wave 0 build "A9 lite"; (b) the tool's two options
are named in the Verify section as W2-174 specifies them, and they land with W2-174's code (not built when this text was
written); the section names no `gov` subcommand but `gov adopt`, which exists. The front matter's `version` is not
changed here: the versioned promotion follows the owner's approval (CAP-33).

## 3. The copies

The three files are byte-equal (`cmp` exits 0 for both pairs), one generated source:

| File | sha256 |
|---|---|
| `template/governance/kernel/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` |
| `template/.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` |
| `.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` |

The `.claude/skills/adopt/SKILL.md` copy is out of this ticket's paths: the copies ACT generates it after the owner's
approval (DEC-315).

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended; the owner filed both lines for this ticket, DEC-1150 (1)) | The skill gains the two sections as in §2, the practice record's section 6 the same order | This ticket (25 lines added, 2 removed in the skill), its acceptance tests, one independent review, the owner's approval of the bytes |
| Defer | Keep the skill as at the base until W2-88's and W2-174's code land | An adopted repository's Wave 0 and its tickets' Verify clauses have no written method; W2-27 (EXAMIN's copy) would run without it |
| Re-baseline | Write the sections inside W2-88's and W2-174's own tickets | Two tickets of mixed roles write one kernel file under two CIT-Ps (against DEC-995, DEC-996) |

## 5. Impact

| Area | Impact |
|---|---|
| Adopted repositories | They receive the two sections with the skill; no code changes here |
| `docs/research/W2-88-memory-practice.md` | Section 6 only, to the seven steps' order; its notes kept after the seven |
| W2-88, W2-174, W2-88b | None; the code and the proofs are theirs |
| The guard, the schemas, `gov` code | None |

## 6. Independent review

The independent review of the skill's text, by a fresh read-only independent-auditor session, is pending.

verdict: PENDING

The ticket lead records the reviewer's session id and its result here after the review (CAP-33.d).

## 7. Owner's approval

Owner's approval of the skill's bytes (sha256 16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0): pending

To be filled by the owner before the merge (CAP-33): approve applying the changes in §2 (apply now), or choose defer or
re-baseline (§4).
