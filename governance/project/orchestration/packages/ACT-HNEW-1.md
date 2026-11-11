# ACT-HNEW-1: 16 new hidden questions, h25 to h40, written by the owner's operator from the rubric (DEC-1069 (4), (8))

For the owner's operator, acting as W2-61h's independent writer, in a plain terminal outside any Claude session. The
guard does not apply there. **Nothing about these questions reaches the CTO's session.** Report back only "done" and
the dry run's counts line.

## Read first
- **The rubric, version 2:** `docs/research/memory-measure-audit/RUBRIC.md` in the repository
  (`/home/usain/Dynamic-Agentic-Engineering-OS`, `w2/integrate`, merged at `cae30e43`). Every new question must pass
  R1-R11.
- **The hidden half's own audit:** `docs/research/memory-measure-audit/HIDDEN.md`, its R5 table: what the hidden 24
  lack.
- **The existing hidden files' form:** read `~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h21.yaml` to
  `h24.yaml` and copy it exactly; the measure parses it.
- **Stay blind:** read no measure result, no search result, nothing under `~/gov-os-runs/`, `docs/research/EXP-003/`
  or `.gov-runtime/`.

## What to write
Write `h25.yaml` to `h40.yaml` in `~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/` (mode 700), so that
the hidden 40 meet R5 as a whole. The hidden 24 today: decisions 9, code 9, the Contract and Charter 2, tickets 0, the
plan 0, none of the five 4. So of the 16:
- **at least 4 governed by the plan**, `docs/plan/` (R5: 10 % of 40);
- **at least 4 by tickets**, `.tickets/`;
- **at least 2 more by the Contract**, `docs/contract/`, to reach 4;
- **at least 3 on failure and lesson memory**, each citing a lesson or failure record (`docs/lessons/`, or a failure
  record named in the register);
- at least 2 on the kernel's skills or roles, if the 24 do not already hold 2 (`template/governance/kernel/skills/`,
  `roles/`);
- the rest across decisions and code, with no subsystem above 25 % of the hidden 40, and the category quotas of
  RUBRIC.md's R5 table for a 40-question half as closely as the domains allow.

**Each question must pass these items:**
- (R1) The answer is correct today, at `w2/integrate`'s head, from the governing source: never a superseded or
  PROPOSED decision, and test-harness code never governs a code fact (R1.3).
- (R2) The sources lie in what memory searches by meaning (the path map's embedded namespaces), or the question is
  marked as a keyword question.
- (R3) It is unambiguous.
- (R4) It is the kind of question an engineer, a test designer, a lead or an auditor really asks, not phrased from its
  own answer.
- (R7) Each entry is one whole piece of evidence.
- (R9) No fact is asked twice: check against the visible 40 in `fixtures/evaluation/memory-retrieval/visible/` and
  against the hidden 24.
- (R11) **No answer that changes with ordinary work** (counts, lists that grow, a ticket's status).
- Each source carries `commit:` (integrate's head when you write it) and its `lines:` or `heading:`, the heading
  copied exactly from the file.

## The check after
```
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py \
  ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden /home/usain/Dynamic-Agentic-Engineering-OS
ls ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden | wc -l      # 40
```
It must print `unresolved: 0`. Send the CTO "done" and the two lines.

## After it
1. **A cross-check:** W2-61h's role (an independent auditor, read-only, under the hidden-half rule) judges h25-h40
   against the rubric. It reports ids, rubric items and general reasons only.
2. **Then m6:** the 0.6B baseline on the 80.

## Rollback
Remove `h25.yaml` to `h40.yaml`; the hidden 24 are untouched.
