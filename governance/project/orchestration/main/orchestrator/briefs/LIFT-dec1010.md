# DEC-1010 and one rule for every role: a read-only investigation and recommendation (DEC-1128 (5))

Read `LIFT-common.md` first (scratch only, read-only everywhere else; no test runs). Role: research helper, Sonnet
high, class C1 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/dec1010/`.
Read DEC-1128 (5) and DEC-1010 in `docs/DECISION_REGISTER.md`, word for word, first.

## The owner's principle (DEC-1128 (5))
For every role, not only reviewers: work is judged against the ticket's KPI lines and specification, never
open-ended; at most two rounds; if the KPIs and specification are still not met after two, it comes to the owner with
the evidence. No change yet: report and recommend.

## Answer
1. **DEC-1010 today:** its exact wording (the relevant items, quoted), its status line and every "Changed by" or
   exception since (e.g. DEC-1105 for W2-20, DEC-1106 for W2-148, and any other), and its scope (which roles and which
   kinds of round it binds).
2. **Each role** (independent reviewer/auditor, independent test designer, engineer, product-spec; the probe; the
   research role if relevant): what it is judged against today (the role files under
   `template/governance/kernel/roles/`, `JUDGEMENT.md` wherever it lives — find it —, the kernel skills `audit`,
   `test-design`, `change`, the lead brief templates in `governance/project/briefs/`, the reviewer brief of the
   operator `governance/project/operator/reviewer-brief.md`); whether it works to known KPIs and a specification; how
   its findings are bounded (in scope against a KPI, or a row/out of scope); and any rule that lets a round open new
   scope.
3. **Rounds actually taken this week** (about 11-04 to 11-11), per ticket and per role: from the review records
   (`governance/project/orchestration/reviews/`, `.gov-runtime/scratch/orchestrator/reviews/`, `docs/probes/`), the
   tickets' notes, the lead logs' names (`.gov-runtime/scratch/orchestrator/log/`, `dispatch/started.txt`,
   `log/spend.jsonl` entries with round names), and commit subjects (`git log --since=2026-11-04` "round", "r2", "r3",
   "review"). W2-20's test designer reached round 7: confirm and explain. A table: ticket, role, rounds, why past two
   (scope opened, KPI unclear, real fault, environment), and whether the owner was asked.
4. **One rule for all roles,** your recommendation with confidence: its wording, and what it would change, by file
   and line: the briefs (lead and role brief templates, the twelve fields), JUDGEMENT.md, the role files, the kernel
   skills, the tickets (the KPI form, e.g. every finding must cite a KPI line or become a row), and the code that
   counts rounds if any (the close's counted refusals escalate at 3 today: `src/gov/close/`). Name what it would cost
   and what it could break (a real fail-open found in round 3).

## Write
`DEC1010-REVIEW.md` in your folder, plain language for the owner, sections 1-4. Return the twelve fields, short.
Estimate 1.5 h.
