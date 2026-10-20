You are the ticket lead for ticket `DAEO-uudf` (`W1-08`, "Record schemas and templates"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-08` on branch `w1/W1-08`. You run the ticket loop for this one ticket. Its implementer is a product-spec worker (brief A4, ticket mode). STANDARD has no reviewer step.

## State of this ticket

- An earlier lead finished the loop: branch head `4b209505` (tests batch 2 `6e9b6d5c`, schemas and templates `079d7374`, path map `4b209505`), its own suite and every earlier suite green, the W1-46 suite red from its own ticket only. It returned two packages, now decided by the main orchestrator. They are recorded on `w1/integrate`, which this branch does not contain yet; **do not merge `w1/integrate` into this branch** (an open point with the owner about merge commits). The two decisions, in full:
  - **DEC-251 (DP-8):** both keys of `capabilities`, `code_intelligence` and `research_corpus`, are required. Each is a closed map with a required boolean `enabled`. `code_intelligence` also has `languages`, a non-empty list of strings when it is enabled. The path map already has this form; the schema is tightened to it.
  - **DEC-252 (DP-9):** `lesson_id` is `^L-[0-9]{4,}$`, the form of the carried lesson `L-0074`, in the shared definitions file and the lesson template.
- The earlier decisions (DEC-224 to DEC-230, DEC-238, DEC-239) are in this branch's register.

## What you do, in order

1. **A short test design round** (brief A1, a fresh designer, profile STANDARD, DEC-221), for DEC-251 and DEC-252 only: the success and failure of each, a handful of cases. These are tests added after implementation, reason "delegated decision". The designer may also strengthen the one weak test the earlier designer named (a defect in one system's `where` rule is caught for every identified system, not only the first), as a described behaviour.
2. **Check red** yourself: the new cases fail for the stated reason; the rest stay green.
3. **A small repair** by a fresh product-spec worker (brief A4, ticket mode): the `capabilities` schema and the `lesson_id` pattern with the lesson template's id.
4. **Verify** every suite and the validator. The W1-46 suite on this branch is red from its own ticket; confirm its failures name only its own missing deliverables and report it apart.
5. Return DONE with the whole ticket's summary: all commits on the branch, the residuals the earlier lead listed still standing (it listed eleven; say which change), and the learning metrics for the whole ticket (the earlier lead reported: KPI disputes 7 in batch 1 and 1 in batch 2, plus DP-9 raised by the lead; rewrites after implementation 0; LOC 664 added against 200; converged).

