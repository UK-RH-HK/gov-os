# Lead brief: the retired history out of the tree (G1) and record/w2 (G2) (a chore with tests retired, DEC-1214)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
Branch `e2/g1-retire` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-g1-retire`. `Task: emergency-2`,
`Class: Q`. Kernel text that names retired machinery may change where audit 5 lists it (the CTO approves by naming it).

**The owner's decision (DEC-1214 G1 (b) and (c), G2 (a)):** "`git rm` the retired code, tests, ACT bundles and prompts,
and also keep them on an archive branch, besides the tag `pre-emergency-2`. Before anything is removed: bundle the six
worktrees' unique commits and tar the live scratch tools. Memory's index is cleaned before the first fresh-80 measure."
"`origin/record/w2`: keep it, stop syncing, remove its worktree."

**Read:** audit 5 `docs/emergency-2/audits/05-repository.md` (each top folder and scratch tree: stays, archived,
deleted; the six worktrees; record/w2), EMERGENCY-2 §6.1 (what is retired: the guard, the sandbox, the box, the ACT
pipeline, the operator agent's launcher, `gov context` (NOT yours: the M1 lead retires it tonight), W2-186, W2-42).

**Steps, in order:**
1. **Safety first, outside the tree:** `git bundle` each of the six worktrees' unique commits (audit 5 names them; `git
   bundle create ~/.gov-os/backups/pre-g1/<name>.bundle <branch> ^w2/integrate`) and verify each (`git bundle verify`);
   `tar czf ~/.gov-os/backups/pre-g1/scratch-tools-<date>.tgz` of `.gov-runtime/scratch/orchestrator/tools` and the
   other live scratch tools audit 5 names. Write the list with sizes and sha256 to `~/.gov-os/backups/pre-g1/MANIFEST.txt`.
2. **The archive:** the local branch `archive/pre-emergency-2` at `w2/integrate`'s head as it is when you start, and the
   annotated tag `pre-emergency-2` there if it does not exist (pushing either is the owner's; never push).
3. **The removal on your branch:** `git rm` what audit 5 classes as retired code, retired tests (tests that assert only
   retired machinery), ACT bundles and old prompts; keep closed-ticket records (unindexed is G4/memory's business, not
   yours); update the path map, the test map and any list that names a removed path (R). Do not remove `src/gov/context`
   or its tests. Do not touch EXAMIN.
4. **G2:** remove the `record/w2` worktree (`git worktree remove`) and whatever syncs it (a cron line, a hook, a tool:
   find it); leave the branch and `origin/record/w2` as they are.
5. **Green:** `PYTHONPATH=<worktree>/src python3 -m gov.cli.main doctor --root <worktree>`; the acceptance folders of W1-01,
   W1-08, W2-91, W2-86 (the path map), and every folder whose tests named a removed path; `tests/unit` packages you
   touched. A test still asserting a removed thing is retired with it (T), with a Rewrite-Reason naming DEC-1214 G1.
6. **Memory's index:** list in your return what the index must drop (paths now removed, the archive) so the CTO cleans it
   before the fresh 80; do not rebuild the shared store.
Return the bundle manifest's path, the branch head, the count of files removed by class, and what you left and why.
