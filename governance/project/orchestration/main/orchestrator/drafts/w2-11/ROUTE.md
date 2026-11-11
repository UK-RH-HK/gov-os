# W2-11 (`DAEO-k7hz`): the route for the skills' and briefs' part of the merge, and the CTO's steps after it

Helper (Sonnet, high), 2026-11-11 about 21:05 UTC. Read-only: nothing launched, committed or written outside `drafts/w2-11/` and `briefs/W2-11-A4-skills-premerge.md`. Measured (**M**) by `git merge-tree` and synthetic commits (objects only, no ref) and by a dry run in a scratch clone; read from files where named.

## 1. The answer

**Route (a), amended. A literal "pre-merge commit that places W2-11's text clear of integrate's lines" (the W1-35 form) does not work for the skills; a pre-merge commit that makes each file equal to integrate's does, and W2-11's text is put back by a second product-spec commit after the merge.**

| step | who | what |
|---|---|---|
| 1 | product-spec (sandboxed, `briefs/W2-11-A4-skills-premerge.md`) | two commits on `w2/W2-11`: the 5 briefs, then the 12 skill files, each made equal to `w2/integrate`'s |
| 2 | CTO | re-read: `merge-tree` lists only the 2 generated copies |
| 3 | CTO, outside any sandbox | one merge (`merge_w2_11.sh`): the two generated copies take integrate's whole file |
| 4 | product-spec (a second brief, not written here) | one commit on the merged branch: W2-11's text of the 12 skill files put back, by the hunk rules of `RESOLUTION.md` section 5 |
| 5 | CTO / the copies ACT | regenerate the `.claude/` copies from the resolved `.rulesync` sources (class (b)) |
| 6 | CTO | `gov accept W2-11`, W1-35's and W2-128's folders, the scoped run |

An independent test designer retires W2-11's brief cases (DEC-1137 (1)); it is a separate tests-branch job, not on this path's order, but it must land before step 6.

## 2. What is true today (M, 20:50 UTC)

- W2-11 head `c16dbf41ea77`: 27 ahead of and 1,949 behind integrate `7a8d5536d664`. The W1-35 pre-merge commit is **done**: `c16dbf41ea77` (`Role: independent-test-designer`; the A1 launch exited 0, `W2-11-A1-merge.summary`; its tripwire "CHANGED" lists only the main tree's own head moves, store-b's head, W2-11's own new head and the W1-35 folder: all explained). DEC-1137 is on integrate (`20d8603ab`, the ticket re-baselined).
- `git merge-tree --write-tree --name-only w2/W2-11 w2/integrate`: **19 conflicts** (the W1-35 file no longer among them). **A correction to the count in the request: it is 12 skill files, 2 generated copies and 5 briefs (not "14 skill files and two copies").**

| files | count | class (`class-rules.yaml`) | whose |
|---|---|---|---|
| `template/governance/kernel/skills/{discovery,orchestration,retrieval,test-design}/SKILL.md` | 4 | row `agents-skills-kernel`: (b), control path | product-spec (ticket paths `template/governance/kernel/skills/*/SKILL.md`) |
| `.rulesync/skills/{the same four}/SKILL.md` | 4 | row `rulesync-other`: (b), control path | product-spec (ticket paths `.rulesync/skills/*/SKILL.md`) |
| `template/.rulesync/skills/{the same four}/SKILL.md` | 4 | no row names it, so `unknown`: (O), not a control path | product-spec (ticket paths) |
| `.claude/skills/{orchestration,test-design}/SKILL.md` | 2 | `agents-skills-kernel`: (b), control path | **the CTO / the copies ACT** (the ticket has `.claude/**` out of its paths, DEC-1112 (3); the launcher denies `Edit` on `.claude` to every worker, DEC-315) |
| `template/governance/kernel/templates/brief-{engineer,lead,product-spec,reviewer,test-designer}.md` | 5 | `agents-skills-kernel`: (b), control path | product-spec (ticket paths `brief-*.md`); DEC-1137 (1) says the pointers stay |

## 3. Why the literal pre-merge form fails (M)

`drafts/w2-11/tmp/sim_route.py` builds, for each strategy, a synthetic commit on W2-11's head that replaces the 17 non-generated files, then runs `merge-tree` of it with integrate:

| pre-merge content of the 17 files | conflicts left |
|---|---|
| W2-11's own (control) | 19 |
| a union of both sides' text (`git merge-file --union`: the best a "both sides, kept apart" file can be) | **19** (all of them) |
| integrate's whole file | **2** (`.claude/skills/orchestration/SKILL.md`, `.claude/skills/test-design/SKILL.md`) |

Reason: git conflicts when both sides changed the same or touching lines, whatever the text; the W1-35 file worked because W2-11's edit was one clause that could sit two lines clear of integrate's. In the skills both sides edited the same version lines and the same sentences, and the right text keeps both: it cannot be kept clear of integrate's lines. The only pre-merge text git accepts in those hunks is integrate's own.

Dry run (M, `tmp/dryrun_a4.sh`, a scratch clone, nothing of the real tree): the brief's commands as written (two commits with their trailers, `git restore --source=... --staged --worktree`, the `diff --quiet` checks, 17 files in the two commits) leave **exactly** the two `.claude/skills` conflicts. The merge script then merged cleanly in a full scratch clone (two parents; the 12 skill files, the 5 briefs and the two copies equal integrate's; W2-11's other files, for example the new reference files and the `audit`, `change`, `checkpoint`, `planning`, `qa-review` copies, kept).

## 4. Routes considered and rejected

- **The CTO merges and a product-spec session edits the open merge** (the original plan of `RESOLUTION.md` section 5): the merge stays staged for the length of a session, and the merge commit would carry `Role: product-spec` for a commit the CTO makes, or `Role: orchestrator` for text it did not write. Not chosen: it breaks the rule that a merge carries the role that resolved it, and a staged merge left open is what the standing memory rule forbids (in a worktree, not the shared main tree, but the reason is the same).
- **The product-spec session makes the merge commit with git plumbing** (`read-tree -m`, `commit-tree` with two parents, no working-tree write, so `.claude/` is never touched): it would work, and leave the working tree stale until the CTO resets it. Not chosen: unauditable by the usual checks, and plumbing around the sandbox is the kind of route DEC-849 says not to take.
- **The CTO writes the 12 files:** kernel skills are product-spec's writes; an orchestrator writing them is a role breach, and it is the content work the hunk rules exist for.
- **Taking integrate's version of the 12 files for good** (no step 4): loses W2-11's success lines (the skills' versions and metadata, test-design's work order, the orchestration lines): the ticket's work. Not an option.

## 5. The CTO's steps, in order

**Before step 1:** nothing is blocked: the W1-35 commit and DEC-1137 are in. Launch the product-spec worker (the brief is self-contained; it needs no store):
```
env LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-11 LAUNCH_TICKET=DAEO-k7hz bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh --class C3 --model claude-sonnet-5-5 --projection-usd 2 product-spec high /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/W2-11-A4-skills-premerge.md
```
(Class C3 because the files are kernel templates and skills, control paths; RUBRIC-2 (2) keeps product-spec on Sonnet at high whatever the class. 10 to 15 minutes, about $2, E.) The worker's tree must be clean and at `c16dbf41ea77`: nobody else writes in `/home/usain/gov-os-worktrees/W2-11` meanwhile (no lead is running there).

**Step 2, when it returns:** `git -C /home/usain/gov-os-worktrees/W2-11 log --format='%h %B' c16dbf41ea77..HEAD` shows two commits (`Role: product-spec`, `Task: DAEO-k7hz`, `Implements: DEC-1137` and `DEC-866, DEC-959`), `git diff --name-only c16dbf41ea77..HEAD` names exactly the 17 paths, and `git -C /home/usain/gov-os-worktrees/W2-11 merge-tree --write-tree --name-only HEAD w2/integrate` ends with exactly the two `.claude/skills/{orchestration,test-design}/SKILL.md` conflict lines. **Re-run this read immediately before step 3** (integrate moves: 1,949 commits behind and growing); a new conflict in any other file stops the route (a file of the 17 that integrate changed again is one more `restore` by a product-spec session).

**Step 3, the merge (outside any sandbox; the tree clean, no worker running there):** write the message file (any subject, ending with the two trailer lines `Task: DAEO-k7hz` and `Role: orchestrator`; the earlier merge `c9f99b28b` is the form), then
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/merge_w2_11.sh <message file>
```
It does the merge in one `git merge --no-ff w2/integrate -F`; if git leaves exactly the two generated copies unmerged it takes integrate's whole file for each (`checkout --theirs`, `add`) and commits with the same message; any other unmerged path, or any failure: it aborts the merge and says why; it never leaves a merge open (the standing rule). Tested in a scratch clone only (tested outcomes: a clean two-parent commit; an aborted, clean tree where a path could not be added). Whether the CTO session may write `.claude/skills/**` (class (b), control path) is for its own check: round 1's 16 copies were written by the CTO with the owner's approval (DEC-991, DEC-992, `c895bb628`); if the guard refuses, the copies are the operator's ACT, and the merge is made with the two files taken as above by whoever can. Taking integrate's whole file is not dropping the ticket's side: the two files are generated, out of the ticket's paths (DEC-1112 (3)), and step 5 regenerates them.

**Step 4, a second product-spec brief** (not written here; I can draft it): in `/home/usain/gov-os-worktrees/W2-11` on the merged branch, one commit (`Role: product-spec`, `Task: DAEO-k7hz`, `Implements: DEC-866, DEC-959`) that puts W2-11's text of the 12 skill files back. Its inputs: the rules `RESOLUTION.md` section 5 items 1 to 8 (the same per hunk; the discovery and retrieval version hunks, test-design 1.3.0 and the body, orchestration 1.3.0 and its five hunks); W2-11's side is `git show c16dbf41ea77:<path>`, the base `git show c38a5b49bc86:<path>`, the current text integrate's; the practical start is `git merge-file -p <current> <base> <W2-11's old>` into a scratch file, whose markers are exactly RESOLUTION's hunks, resolved by the rules (the orchestration and test-design copies are the same text in all three places: resolve once, copy). Then the three checks of section 5's last paragraph: the version pair of `change`, `checkpoint`, `planning`, `audit` (`version` equal to `metadata.version`; read today in the merged tree: they agree), the orchestrator role file's lead line and ceiling sentence, and that no `.claude` file is touched. It writes none of `.claude/`.

**Step 5, the copies:** regenerate every `.claude/skills/*` and `.claude/agents/orchestrator.md` copy from the resolved `.rulesync` sources (round 1's way: rulesync over the branch's sources, `c895bb628`, a class (b) copies change: the owner's approval as then, or the operator's copies ACT). After the merge the `.claude` copies of `discovery` and `retrieval` carry W2-11's `metadata.version` against sources at integrate's version until then, and the two taken copies carry integrate's text: the version test `test_the_skill_carries_one_version_in_all_four_places` is red until this step, by design.

**Step 6:** `gov accept W2-11` (round 1 ended at 147 passed, 1 skipped), W1-35's and W2-128's folders, the scoped run. W2-11's brief cases wait for the designer's retirement (DEC-1137 (1)); the five briefs are the pointers, so any case that reads a brief's content is red until it goes.

## 6. Open points

1. The intermediate state: after step 1 and until step 4, the branch's four skills read as integrate's; W2-11's skill cases are red there. Nothing runs between. If the owner would rather not have it in history, the only alternative is a product-spec merge commit by plumbing (section 4), which I do not recommend.
2. The two generated copies in step 3 are integrate's text until step 5: any gate that checks copies against sources (adapter portability, `gov check` on the generated files) is red between steps 3 and 5. Run them after step 5, not before.
3. The proof in the brief uses a scratch clone (`git clone --shared --no-checkout`, 11 ms, no object lands in the shared repository), as asked; the worktree form (`merge-tree ... HEAD w2/integrate`, the form A1 used) is the named fallback if the sandbox refuses the clone.
4. The count: "14 skill files and two generated copies" is 12 and 2 (section 2); with the briefs the product-spec worker's list is 17.
5. Not read: W2-128's reviews, the Contract's `CAP-38` letters (RESOLUTION item 3), the bodies of the generated copies beyond what `merge-tree` showed.

## 7. Evidence

`drafts/w2-11/tmp/`: `mt3.txt` (today's merge-tree), `sim_route.py` (the three strategies; output quoted in section 3), `dryrun_a4.sh` (the brief's steps in a scratch clone), `check_versions.py`, `mt-clone.txt` (the scratch clones themselves are removed; `dryrun_a4.sh` rebuilds the dry one in a second). `drafts/w2-11/merge_w2_11.sh`: the CTO's merge script (syntax-checked with `bash -n`; run only in the scratch clone).
