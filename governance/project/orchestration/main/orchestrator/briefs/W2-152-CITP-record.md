# W2-152 (DAEO-o5x1): write the missing CIT-P record for its kernel schema change (the owner, DEC-1147 (1))

You are a product-spec worker in `/home/usain/gov-os-worktrees/W2-152` (branch `w2/W2-152`). You write exactly one file,
`docs/changes/W2-152-CIT-P.md` (in the ticket's allowed_paths), and make one commit on this branch. Nothing else.

## Why
W2-152 changed one kernel file, `template/governance/kernel/schemas/facts.schema.json`. It reached `w2/integrate` in the CTO's merge
`b0bbd373f` (2026-11-09 23:07) with no CIT-P record and no owner approval (CAP-33; DECIDED-NOT-DONE row 173). The owner approved it
after the fact on 2026-11-12: "W2-152 CIT-P approved at 09fc68645c0c, after the fact" (docs/DECISION_REGISTER.md, DEC-1147 (1)). The
record is written now so the change has its record before the ticket closes. It is a record of what happened, not a new proposal.

## The form
Follow `docs/changes/W2-146-CIT-P.md` on w2/integrate (read it: `git show w2/integrate:docs/changes/W2-146-CIT-P.md`) for the front
matter keys and section order, with these values:
- `id: W2-152-CIT-P`, `type: change-impact-proposal`, `status: APPROVED`, `date: 2026-11-12`, `branch: w2/W2-152`,
  `head: 09fc68645c0c (the code reviewed and merged)`, `ticket: DAEO-o5x1 (W2-152)`, `task: DAEO-o5x1`, `author: product-spec (written after
  the fact, DEC-1147)`, `review:` the round 2 READY (below), `approved: owner, 2026-11-12, after the fact (DEC-1147 (1))`,
  `decisions_carried: [DEC-1088]` (only the decisions the change itself carries), `decisions_applied: [DEC-1088, DEC-1050, DEC-1147]`,
  `state_class: EVIDENCE`.
- A first section stating plainly: the bytes were merged into w2/integrate on 11-09 at `b0bbd373f` before any approval; the owner approved
  them after the fact on 11-12; this record is written after the fact.

## The facts (verify each yourself with git before writing it)
- File: `template/governance/kernel/schemas/facts.schema.json`.
  sha256 before (`git show b0bbd373f^1:<file> | sha256sum`): `be3e204355c0dd4c98cc584b72a1cef5eaa4733ca9a7feec8684b728026af7a6`;
  after (`git show b0bbd373f:<file> | sha256sum`, and the same at 09fc68645c0c and on w2/integrate today):
  `3141d5da38d7a2a1dcf654f83354f4fc6f2ce16bb383c03d6a906e221bd6448c`. 15 lines added, 1 removed.
- The diff, verbatim, from `git diff b0bbd373f^1 b0bbd373f -- <file>`, in a fenced block.
- What it does: `ready` becomes a required key of the facts file, an object with one required `new_since`, an ISO date string; `gov brief`'s
  ready check refuses a ticket created on or after that date without `reads:`, `needs:` and `waits_on:` (DEC-1088 (3)). Commits: `16d052d2f`
  (the property), `09fc68645` (the fix round: `ready` added to `required`, review round 1's F3).
- What landed with it in `b0bbd373f`: `gov brief` (`src/gov/brief/`), `governance/project/facts.yaml` gaining `ready: new_since: "2026-11-10"`,
  the acceptance suite `tests/acceptance/W2-152/`, the unit cases, the evidence record (`git diff --stat b0bbd373f^1 b0bbd373f`).
- Review: `governance/project/orchestration/reviews/w2-152-r1.md` (two rounds, independent auditor; round 2 READY on 09fc68645c0c, 11-09);
  the probe record `docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md`. The review judged the code against the KPI lines, the facts schema included
  (S10; F3); it was not a CIT-P review.
- Impact: on this repository, the facts file already carries `ready`; an adopted repository has no facts file today (`gov adopt` writes
  none), so `gov brief` there refuses with BRIEF_FACTS_MISSING before it reads `ready`: the owner has that point as a separate item; name it
  in one line, propose nothing.

## Rules
- Write only `docs/changes/W2-152-CIT-P.md`. One commit: `git add docs/changes/W2-152-CIT-P.md && git commit -m "W2-152 (DAEO-o5x1): its CIT-P record, written after the fact (DEC-1147)" --trailer "Task: DAEO-o5x1" --trailer "Role: product-spec" --trailer "Implements: DEC-1147, DEC-1088" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`.
- No pytest is needed; if you run any, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with a TMPDIR outside the repository.
- Never open anything under the evaluation sets' root or any `hidden`, `memory-verdict*` folder. Single simple Bash commands.
- A session refused twice for an action by the guard, the sandbox or a hook stops and says so; it never reaches the same effect by another
  form. A resource gate's refusal is a wait (DEC-1146).
- Return: the twelve labelled fields, the commit id, and the file's sha256. Estimate: 15 minutes.
