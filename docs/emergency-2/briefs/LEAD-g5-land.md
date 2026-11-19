# Lead brief: land Charter v6 and Contract v5 after the owner's yes, and the escalation rubric's kernel text (chores and test revisions; the owner, DEC-1219 (1), (2))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (the machine rule, memory first, trailers, models).
Name: `g5-land`. **Kind of work:** records, documents and kernel text are **chores** (`Class: C`, `Task: chore`); the
test revisions are a test designer's (`Role: independent-test-designer`, `Task: chore`, each with a `Rewrite-Reason:`
naming DEC-1219). **No new ticket** (DEC-1219 (6)).

**Where:** the existing worktree `/home/usain/gov-os-worktrees/E2-g4-g5`, branch `e2/g4-g5`. First `git merge w2/integrate`
there. Conflicts expected on `docs/DECISION_REGISTER.md` and `docs/emergency-2/audits/08-new-register.py`: **keep
integration's** for both (W2-203 rebuilt the register and its builder; the branch's versions predate it), then make
sure nothing else of the branch depended on the branch's versions.

**The owner's answers (DEC-1219, read it in `docs/DECISION_REGISTER.md` on integration):** G5-1 to G5-13 yes, with one
wording change: G5-7's scan "runs once before a repository goes public or is shared with a third party"; CAP-63 to
CAP-69 yes, each; T2-1 yes.

## Steps (`docs/emergency-2/G5-APPROVAL.md` on the branch, "After your yes", with the changes below)
1. **G5-7's wording:** in `docs/contract/contract.yaml`, CAP-03 (outcome, acceptance, `.a`, `.e`) and CAP-41.g, and the
   Charter v6 text that says the same: the scan **runs once before a repository goes public or is shared with a third
   party**, and no scan runs while it is private. Then `python3 docs/contract/tools/gen_contract.py --write`.
2. **Status:** `status: ACCEPTED` in `contract.yaml`, `CONTRACT_v5.md` and `CHARTER_v6.md`; the change-log row says
   approved by the owner on 2026-11-19, DEC-1219 (the approval is recorded once there; do not add a register entry).
   Regenerate.
3. **The red tests** (the page's table, about 11): a test designer (C3: the Contract is in the criticality list; Opus,
   prompt carrying `Task: chore`) retires or rewrites each as the table says, Rewrite-Reason naming DEC-1219. Then run
   W2-49, W1-48, W2-51, W2-129, W2-134, `tests/unit/links`, `tests/unit/retrieval/test_w2_61h_families.py` and
   `docs/contract/tools/validate_w2.py`.
4. **`closes:` lines:** give each W2 item the validator lists without a ticket a `closes:` line on the **existing**
   ticket that delivers it (W2-115b, W2-121c/d, W2-197, W2-17, W2-18, W2-36, W2-81, W2-201, W2-205 and the rest). Do not
   open a ticket. An item no existing ticket delivers: list it in your return (the CTO decides; it may be friction or a
   later feature) and, if the validator allows, mark it so; otherwise leave it as the validator's one remaining line.
5. **Kernel text naming the old documents** (the CTO approves by naming, EMERGENCY-2 3.5): "Charter v5" / "Contract v4"
   / "v4.2" / "v4.3" in `template/governance/kernel/roles/*.md`, `template/.rulesync/**`, the adopt skill, CLAUDE.md and
   AGENTS.md become Charter v6 / Contract v5 where they mean the documents in force (leave history records alone).
   Regenerate the copies with the project's generator.
6. **ADR-0001 and ADR-0002** updated in full to v5 (audit 7 C-4), replacing the amendment notes.
7. **T2-1, the escalation rubric's kernel text** (the CTO approves by naming): the escalation rubric in the kernel
   text (find it: `grep -rln "DEC-957\|escalation" template/ CLAUDE.md AGENTS.md`; at least
   `template/.rulesync/skills/orchestration/briefs-and-returns.md` and `incident-response.md`, and the role files that
   cite DEC-957's P1 list) becomes `docs/emergency-2/T2-ESCALATION-RUBRIC.md` §2, cited as DEC-1219 (2). Bring that page's
   §3 in line with the owner's change (DEC-1217 (5)): "a decision that stops work always pushes the owner, at any hour;
   no day or night rule; every push also appears in the morning brief"; a decision that stops nothing goes in the morning
   brief only. Mark the page's head "approved, DEC-1219 (2)".
8. **Green:** the step-3 set, `tests/unit/optin`, the tests that read the kernel text you changed (`grep -rln` the
   files you edited under `tests/`), `gov doctor` no worse than on integration.
9. **Return:** branch and head; each step done with its commit; the summary lines; reds not yours; the W2 items left
   without a delivering ticket.
