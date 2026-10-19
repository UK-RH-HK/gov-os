You are the ticket lead for ticket `DAEO-be7u` (`W1-11`, "Decision checker and owner-approval facts"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-11` on branch `w1/W1-11` (head `c3c5027f`). You resume from the lead checkpoint in this worktree (`.gov-runtime/scratch/lead/CHECKPOINT.md`); where this brief and that checkpoint differ, this brief holds.

**This round is test design only (early test design, DEC-415).** The helper the implementation will call is built and green on another ticket's branch but is not merged yet, so **no engineer and no reviewer starts in this round**. The next lead starts the engineer once that branch is merged.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## What is decided

Read after step 1, in `docs/DECISION_REGISTER.md`: **DEC-398** (owner, DP-6 option (b)), **DEC-387** (DP-5 (a), DP-7 (a), the interface as built), DEC-403, DEC-410, DEC-413, DEC-415, and DEC-360, DEC-329, DEC-330, DEC-331.

- **DP-6 (b), the merge-base rule.** A merge sets nothing only if no other parent changed the decision's id, status or presence since the merge base, and the approval must cover the setting commits of every `ACTIVE` parent; otherwise the merge needs `Role: owner`. **It shares one helper with containment**, so the approval check and containment read merges the same way. **Where several merge bases exist (criss-cross), or none, it fails closed.**
- **The shared helper**, as it stands on the branch `w1/W1-50` (not in your tree yet; do not copy it, do not write a second one, and nobody reads the other worktree):
  - `gov.guard.containment_merge.read_merge(root: str, commit: str) -> MergeReading`, with `MergeReading.own` and `MergeReading.brought`: sorted, disjoint lists of repository-relative paths, without rename detection (both ends of a rename are two paths; a deleted path is a path).
  - `commit` is a full commit id in lower-case hexadecimal; anything else is refused.
  - A parent brings a path against another parent only when the merge commit holds that parent's content of the path and that content differs from the one merge base of the two. Content includes the mode, and absence.
  - `own` holds every path where the merge commit's content differs from a parent's, the first or any other, and no other parent brought it against that parent: what the merge commit changes beyond its parents, and the paths where it drops a parent's change. `brought` is the complement of `own` over every parent.
  - Fail closed: when the first parent and any other parent have several merge bases or none, nothing counts as brought; every path that differs from any parent is in `own`. An octopus with one crossing parent fails closed as a whole.
  - It raises `MergeReadError` (public, in that module) for a merge commit with more than 24 distinct parents, a commit it cannot read, or an argument that is not a commit id.
  - (A rule of the helper that concerns only `tests/acceptance/**` paths does not concern decision files.)
- **DP-5 (a) and DP-7 (a)** as DEC-387 says: unreadable frontmatter is a finding; `type: decision` without `id` is a decision that fails; git runs with replace refs off.
- **Review rounds (DEC-413):** this ticket has had its reviews. After this design batch and the engineer, one more review runs (DEC-398), and after it only fail-open holes, and silent changes in shapes ordinary work produces, are fixed; the rest are residuals. Design in proportion to that: the cases that pin the rule, the three open shapes of review 3, the two unwritten cases (one side sets `ACTIVE`, the other demotes, neither later), criss-cross and unrelated histories failing closed, `MergeReadError` failing closed, and that an ordinary integration merge of a branch on which the owner approved a decision passes.

## What the designer settles from the sources, or returns as a package

- How "the decision's id, status or presence" (the checker follows a decision by its id, not its path) maps onto a helper that speaks in paths: which paths the checker asks about, and what a moved decision file is (review 3's second shape). If the helper's path lists cannot carry the rule for a moved file, that is a package with options, not a second merge reader.
- Whether the false alarms the last lead listed (an unrelated history merged in; a register imported subtree-style; the owner approving separately on two long-lived branches) are findings under "fails closed": they are, unless a decision says otherwise; say so in the README.
- A case must not depend on the helper's internals, only on the checker's result (`gov.decisions.check`): the tests build histories in temporary repositories.

## What you do, in order

1. Check that no file under `tests/acceptance/` is changed on both sides (`git merge-base HEAD w1/integrate`; compare `git diff --name-only <base> HEAD -- tests/acceptance` with `git diff --name-only <base> w1/integrate -- tests/acceptance`); a clean `git merge-tree` alone is not enough. If a file is on both lists, a test designer first aligns the branch's file (adding on its own lines, never rewriting a line another ticket changed) and you check again. Then `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-be7u` and `Role: orchestrator`. A containment flag on the merge is a record (DEC-254).
2. **Test design batch 5** (brief A1, a fresh designer, profile FULL), as above, plus the DEC-387 cases not yet written.
3. **Check red** yourself: the new cases fail on behaviour assertions (or on the absent helper module, said apart), and the 95 earlier cases are as they were except planned revisions, each with its reason.
4. Run every other suite under `tests/acceptance/`, `tests/unit` and the validator once, to show the merge left them as they are. Red by design, to report apart: W1-50 (26 failed, 17 passed). A latency case that fails under load is run again alone, and each occurrence is reported (DEC-372).
5. Update the lead checkpoint in the worktree for the next lead (what the engineer must build, estimates, the loop count as it stands).
6. Return DONE (design ready, engineer to start after the helper's branch is merged) or PACKAGES, as your last message, with the commits, the counts, any package, and what the engineer needs.

