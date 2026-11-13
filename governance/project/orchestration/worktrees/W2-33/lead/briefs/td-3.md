# Brief td-3: independent test designer for DAEO-lrre (W2-33): revise three old-layout cases in W1-35

You are the independent test designer (MR-3) for ticket DAEO-lrre (W2-33). The owner has decided (DEC-1156 (3);
DEC-957 Q2) that the ticket lead has its own role file, `template/governance/kernel/roles/ticket-lead.md`, that
`orchestrator.md` loses its `## The ticket lead` section and is the CTO's file, and that the kernel roles folder grows
from six to nine files (the six plus `ticket-lead.md`, `qa-engineer.md`, `senior-engineer.md`; no
`independent-reviewer.md`). Three older cases in W1-35 assert the old layout. Under DEC-1156 (7) the CTO has added
`tests/acceptance/W1-35/test_w1_35_orchestration.py` to this ticket's paths so that you revise **exactly those cases**,
each with a `Rewrite-Reason:` comment. You never read the product-spec worker's work on this ticket (branch w2/W2-33
after `3df1ac2deb1b`; it is being written now): you write to the decision, not to the files.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-33-tests |
| branch | w2/W2-33-tests (base `3df1ac2deb1b`) |
| your one writable file | tests/acceptance/W1-35/test_w1_35_orchestration.py (not its support module, not its README, not W2-33's suite) |
| the ticket (current copy; its `## Interface` holds the files and line forms) | /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/context/DAEO-lrre.ticket.md |
| the cases to revise | `test_w1_35_orchestration.py`: class `TestTicketLeadSection` (from :201, the section of orchestrator.md, including `test_the_section_adds_no_labelled_field_to_the_role` and `test_the_roster_stays_at_the_same_roles` at :259-268) and `TestWording._texts` (:353) |
| the support module (read only) | tests/acceptance/W1-35/w1_35_orchestration_support.py (`ROLE_FILES` :65, `lead_section` :573, `REPOSITORY_VALUES` :99, `LANGUAGE_BOUND` :92) |
| an example of the Rewrite-Reason form | tests/acceptance/W1-35/w1_35_orchestration_support.py around :122; tests/acceptance/W2-32/test_w2_32_record.py |
| the decisions | docs/DECISION_REGISTER.md by id only: DEC-1156 (3) and (7), DEC-957 (Q2), DEC-236, DEC-959 item 3, DEC-534, DEC-539 |
| ROLES-SPEC-1 (approved) | governance/project/orchestration/packages/ROLES-SPEC-1.md §3.3 (the ticket lead) |
| context packet | /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/context/ctx-td.json |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065).

## What to revise (keep each case's intent; change what it reads)
1. `TestTicketLeadSection` reads the ticket lead's own file, `roles/ticket-lead.md`, in place of a section of
   `orchestrator.md`: what a lead is (an orchestrator-role session bound to one ticket and its worktree), what it does
   (runs its ticket's loop, starts its workers), what it never does (merge into the integration branch, edit the
   ticket files or the decision register, push), what it returns (DONE, PACKAGES, ESCALATION), and that it cites a
   CAP, DEC or MR id. Rename the class and its docstring to fit (keep `covers: S14`).
2. `test_the_section_adds_no_labelled_field_to_the_role` asserted the lead was text of the orchestrator role, not a
   field. Under DEC-1156 (3) it is a role file with its own fields; revise it to assert that `orchestrator.md` no longer
   holds a section whose heading names the ticket lead (support.lead_section returns None) and names `ticket-lead.md`.
3. `test_the_roster_stays_at_the_same_roles` (:259-268): the kernel roles folder holds exactly the nine files above
   (define the nine locally in the test file; the support module is not yours) and no `independent-reviewer.md`. The
   rulesync subagent sources (`template/.rulesync/subagents/`) are W2-153's and the copies ACT's, outside this ticket:
   drop that half of the assertion and say so in the Rewrite-Reason (do not assert their count).
4. `TestWording._texts` (:353): read `roles/ticket-lead.md` in place of the orchestrator's lead section, but exclude
   the machine-readable defaults lines the Interface requires in every role file (a line starting `- **Version:**`,
   `- **Launch default:**`, `- **Launch by criticality:**` or `- **Model tier:**`), since they carry a version number
   and a model id by the owner's decision; the wording checks hold for the rest of the file unchanged.
5. Each revised case carries a `# Rewrite-Reason: DEC-1156 (3), DEC-957 Q2: ...` comment saying what changed and why.
   Change nothing else in the file.

## Rules
- Run the revised cases (they are red now: `ticket-lead.md` does not exist on your base, and that is expected; say
  which are red and why, and that no other W1-35 case changed state). Every pytest through the heavy-slot gate,
  TMPDIR outside the repository (`mkdir -p /tmp/gov-w2-33-td3` first):
  `TMPDIR=/tmp/gov-w2-33-td3 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33-tests/src python3 -m pytest tests/acceptance/W1-35 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Run it once before your change too, to compare. A heavy-slot or resource refusal is a wait.
- No test named with `real`, `green_here` or `time_limit`. Paths compared with `Path.is_relative_to`, never a text
  search of a temporary path (DEC-1155).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/.
- Commit your one file only:
  `git commit -m "<subject>" --trailer "Task: DAEO-lrre" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-236, DEC-959" --trailer "Rewrite-Reason: DEC-1156 (3), DEC-957 Q2: the ticket lead has its own role file; the roles folder grows to nine" -- tests/acceptance/W1-35/test_w1_35_orchestration.py`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines before and after) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
