---
type: probe
task: DAEO-3r1j
reviewer_session: b6ad0885-16ef-49f0-a0fc-44cccf84ef62
implementer_session: 0047deab-bb2b-4ee5-b6f8-23852a7fab6d
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 1920abfa17bf377a94ba8d9ef750ec6495ba25b3
---

# Probe record: W2-110 (DAEO-3r1j)

- **What was probed:** The kernel hook's CTO-only install rule at 1920abfa17bf (code of 5bdde1e9d5c6), run as code in temporary projects on this worktree's `src` (DEC-732), about 1,180 hook calls:
  - 37 session forms;
  - 73 forms of the key, the roster and the ticket files: missing, broken, unreadable, linked, duplicated, odd spacing and quoting;
  - 520 calls compared between the base's hook and the head's hook for decision, words and side effects: sudo, the research exception in and out of its folder, frozen and unmarked flags, calls that install nothing, the guard's earlier refusals, and the owner's prompt with its snapshot and record;
  - the head's hook under the owner's real pinned `gov` (no CTO rule), run with `-E`;
  - 10,000 tickets against the 20 s deadline;
  - no PyYAML, and a failing lookup;
  - the model (rule 4) on the deliberate cases.

  Scope was checked against the ticket's paths and W2-05's branch. The reviewer wrote nothing to the repository. Python cached two git-ignored bytecode files from one `gov retrieve` run; the sandbox check wrote one blob.
- **What it found:**
  - **F1, low.** A lead whose ticket file is a symbolic link to the coordination ticket's file is asked; the model asks it too.
    Ordinary work: no, because a link planted at a ticket's name is a deliberate construction (DEC-801) and the template refuses edits under `.tickets/`.
    Consequence: other
  - **F2, low.** With two tickets carrying the coordination ticket's WBS id and the key written as that WBS id, the ticket whose file name sorts first is the coordination ticket: a lead on it is asked and the true CTO is refused. Written as the ticket's id, the key opens nothing; the model asks both sessions. Proposed hardening: refuse when the WBS id names more than one ticket.
    Ordinary work: no, because it needs a second ticket filed with the coordination ticket's own WBS id; none of this repository's 170 tickets shares a WBS id.
    Consequence: other
  - **F3, low.** The template's orchestrator role file (both copies) still says the guard asks on every install, for a lead too. Nothing in the template names the `coordination_ticket` key or says the CTO's session carries the coordination ticket in `GOV_TICKET`, and the CTO's refusal without it does not name `GOV_TICKET`. This rides with the "set at adoption" package (product-spec).
    Ordinary work: yes, because a product's lead or CTO follows its role file.
    Consequence: other
  - **F4, info.** Under the owner's pinned `gov` (pin-5c401220), every install in a product is refused, the CTO's included, with "update the pinned gov"; everything else is unchanged. The pin must be renewed after the merge.
    Ordinary work: yes, because every product on this machine uses that pin today.
    Consequence: other
  - **F5, very low.** When the rule itself cannot run (no PyYAML, or a lookup error), the refusal says the key "is not set" although the roster is fine. It still refuses.
    Ordinary work: no, because the pinned interpreter ships PyYAML and the lookup did not raise on any real input probed.
    Consequence: other
- **Sound:**
  - Only the orchestrator session on the coordination ticket, by id or WBS id, and its orchestrator subagent are asked. Every lead, worker, subagent, role-less session, ticket-less session and odd ticket or role spelling is refused and told to raise a P1 escalation to the CTO.
  - Every missing, empty, non-text, misplaced, unparsable or unreadable key, and every key naming no ticket, refuses every session (the CTO's included) and says how to set the key.
  - No call ended with an exit code other than 0, and none ran near the deadline.
  - Sudo, the research exception, the freeze, calls that install nothing, the order of the rules, and the CTO's prompt, before-snapshot and record are identical to the base in 372 of 520 compared calls. The rest differ only where an ask became a refusal, or in the refusal's words.
  - The change stays within the ticket's paths. `install.py` gains one import and an appended block; W2-05's branch does not touch it.
- **Verdict:** pass. No finding answers yes to both questions. F1, F2 and F5 are rows for the Wave 3 hardening pass; F3 and F4 fail closed and go to the follow-up package and the rollout.
