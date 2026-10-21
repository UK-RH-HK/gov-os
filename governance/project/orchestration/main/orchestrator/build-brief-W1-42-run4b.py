"""Assemble the lead brief of run 4b on W1-42: run 4's brief under a top note with the owner's answer to PKG-C (DEC-682)."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
run4 = open(B + "W1-42-A5-run4.md", encoding="utf-8").read()
NOTE = """**READ THIS NOTE FIRST. It is newer than everything below and overrides it where they differ.**

A lead before you (run 4) stopped at piece 1, step 1, and returned the package PKG-C: no ORION code change was available on decided ground. **The owner has answered it (DEC-682, in `docs/DECISION_REGISTER.md` of this worktree, whose branch now holds a newer merge of `w1/integrate`; read DEC-682 and DEC-683 to DEC-685 with the decisions named below):**

- **ORION-im02 is the named dimension for acceleration: `ACCELERATION = LENGTH / (TIME * TIME)`, with the name `ACCELERATION`**, beside the module's existing named dimensions. The owner accepts MATH-SPEC-003's "Compound dimensions" section for this one constant; the rest of that document stays provisional. It is a new small feature; **the closed specification ORION-SPEC-DIMADD is not edited**. The ticket's `sources` name MATH-SPEC-003 (and nothing a-dev's store does not hold). Piece 1's step 1 is therefore decided: do not weigh candidates again, start at step 2.
- **By the book, as piece 1 says:** claimed, test designer first (behaviour: the constant exists under that name, equals length divided by time squared, the other named dimensions are unchanged), engineer, every commit with `Task:`, `Role:` and `Implements:`, one `gov close`, no exception, no disposition. It is the DEC-511 proof.
- **How the owner's acceptance reaches a-dev's records is part of "by the book":** if the product's method needs the acceptance recorded in a-dev before a ticket may source that section (a decision record, an answer to an open question, a status line), make that record with the role the method names for it (a product-spec worker through `gov launch`, or your own orchestrator commit if the method gives it to the orchestrator), citing the owner's words above, with the three trailers. Do not edit MATH-SPEC-003's status as a whole: one section is accepted, for one constant. If the method has no place for such a record, or `gov launch` refuses an implementation ticket that has no `specification` field, return that as a package at once, before any close.
- **From the earlier lead's reading of the close code (check it yourself, it is short):** the trailers gate judges only commits whose trailers hold `Task: ORION-im02`; the governance-checks gate runs only if a commit of the ticket, or a no-task commit in its range, changes a governance path, so keep ORION-im02's commits on its ticket file, its test folder, the reference module and its checkpoint folder, and make no commit without a `Task:` trailer; give ORION-im02 a `wbs_id` of its own, so that its acceptance folder is its own and ORION-im01's 84 cases run as regression; the programme's own tests are not run by the close, so you run them.
- Read `.gov-runtime/scratch/lead/CHECKPOINT.md` first: run 4's notes are at its top.
- **One more line for the exit report's "for the exit auditor" list:** DAEO-3ef2 (W1-38) was closed with the ticket tool under ESCALATION_BLOCKED by the owner's authorisation, its escalation coming from history alone (DEC-683); a W1-02 round on the guard and tools it does not know is running or done (DEC-685): name both, one line each, from the register.

---

"""
with open(B + "W1-42-A5-run4b.md", "w", encoding="utf-8") as f:
    f.write(NOTE + run4)
print(len(NOTE + run4))
