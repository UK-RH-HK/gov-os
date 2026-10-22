
Every finding in your synthesis carries the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Findings you carry over keep their two lines from the reports. Where you would classify one differently, say so and why.

## The decision format the owner requires (DEC-818)

Every owner decision you propose is a package that stands on its own, because the owner and an outside adviser may lack context. It has six parts:
1. the context, in plain words, with its history and links;
2. what happened, with the evidence;
3. why it matters to the Gov OS's purpose;
4. the options, each with its consequence, cost and risk, and what it changes in the Contract, the specifications, the skills or the briefs;
5. a recommendation, with your confidence, and the threat-model classification of its findings on one line, before the recommendation (DEC-809);
6. what it blocks, and what waiting costs.

## Your synthesis

- **Where:** write it to `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/assessment/2026-10/I-SYNTHESIS.md`. The orchestrator copies it unchanged, byte for byte, to `docs/assessment/2026-10/I-SYNTHESIS.md`.
- **Who reads it:** the owner and an outside adviser who may lack context. Write in plain words, define every internal term at its first use, and keep each section readable on a phone: short paragraphs, lists, tables where they help.
- **Sections, in this order:**
  1. **The diagnosis, in one page:** what the test estate is worth today, what it fails to catch, and what it costs a close; the few things that matter most.
  2. **The combined counts:** per verdict and per area, functions and cases, with the close time each class costs today. Say what was not reviewed, and why.
  3. **What fails open or loses work:** every finding classified "yes" on both questions, and every planted fault that no test catches and that fails open or loses work. Say for each whether it needs a round now, rides along in a ticket that will run anyway (DEC-802), or is an entry criterion of a ticket that switches a feature on (DEC-803).
  4. **What it changes, by ticket.** One block per ticket, saying what goes into its card or ticket file, from which finding:
     - W2-66 (the test map: suites, the shared core, the record-only list);
     - W2-68 (its record-reading set; reuse; fingerprints);
     - W2-67 (per-test copies; the nested reruns; worksteal);
     - W2-57 (the serial-only list, `load_sensitive`, `accepted_reds`, and a route out for each entry);
     - W2-07 (its KPIs);
     - W2-19;
     - W2-69;
     - every ticket whose allowed paths or entry criteria a report says must change before it starts (for example W2-65, W2-04, W2-21, W2-27, W2-32 and W2-37).
     Flag every place where two reports propose different changes to the same ticket.
  5. **Retirements and rewrites:** one consolidated table of every test the reports propose to retire or rewrite, deduplicated across areas, with its verdict, its evidence, the decision or Contract item it rests on, its owning ticket, and the close time saved.
  6. **The owner decisions needed, each in the six-part format, in the order the work needs them:**
     - first those that gate the review point (W2-66, W2-67, W2-68, W2-57, W2-07, the re-pin plan);
     - then those that gate other tickets' starts;
     - then the rest.
     Merge the reports' packages where they ask the same question. Keep their ids (P-I1-n, P-I2-n, R/O items of I3, I4's) so each can be traced.
  7. **Disagreements and limits:** where the reports disagree, and what none of them could review.
- **Sources:** cite the report and its finding, package or table row for every claim.
- **When you have written it,** read it once more from the file.

## Your return (after the synthesis is written)

First, twelve labelled lines in this order:
1. task
2. status (DONE, PARTIAL or BLOCKED)
3. work_completed
4. files_changed
5. evidence
6. tests
7. discoveries
8. risks
9. lessons
10. proposed_decisions
11. unresolved
12. recommended_next_action

Then the synthesis's path, its top-level headings, and the list of owner decisions in their order. Nothing else.
