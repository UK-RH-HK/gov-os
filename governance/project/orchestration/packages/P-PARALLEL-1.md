# P-PARALLEL-1: the test designer and the engineer in parallel on one ticket, without two writers in one worktree (P1, for approval)

For the owner (DEC-962 item 4). Two of your rules conflict:
- **DEC-959 item 7:** the test designer and the engineer work on a ticket at the same time, both from the spec;
- **rule 6** (kept by DEC-962): one writing worker at a time per worktree.

**Until you decide:** rule 6 holds, so the test designer runs first and the engineer after it. The common lead brief and the queued briefs say so (DEC-962).

## 1. Context
- Today a ticket has one worktree, `~/gov-os-worktrees/<W2>`, on branch `w2/<W2>`. The lead starts every worker inside it.
- Two writing sessions in one tree collide in three ways:
  - each one's `git add` and `git commit` can pick up the other's files;
  - git's own lock (`index.lock`) refuses the second commit;
  - a test run sees the other's half-written files.
- Rule 6 exists because of collisions like these.
- The two workers' paths never overlap: the designer writes only `tests/acceptance/<W2>/`, and the engineer never writes there (guard rule 1). So the only thing to solve is the shared tree.

## 2. Options

### (a) Two worktrees, one per worker; the lead integrates
- The lead adds `~/gov-os-worktrees/<W2>-tests` (branch `w2/<W2>-tests`) and `~/gov-os-worktrees/<W2>-code` (branch `w2/<W2>-code`), both cut from the ticket branch's head. Its own worktree `<W2>` is the integration point.
- Each worker writes only in its own tree.
- When the designer commits, the lead merges `w2/<W2>-tests` into `w2/<W2>`. This is clean, because the paths are disjoint.
- When the engineer has built, it merges `w2/<W2>` into its own tree (bringing the tests), and runs them once (through `gov accept` once W2-96 lands). If the engineer has already ended, a fresh engineer in the code tree does the merge and the run.
- When both are done, the lead merges `w2/<W2>-code` into `w2/<W2>` and runs the scoped set once. Then QA and the return. The lead removes both extra worktrees and branches before returning.
- **Cost:** two extra worktrees per ticket. A worktree's tracked files are about 27 MB, but each needs its own store for `gov retrieve`: about 420 MB, and a 5 to 40 minute rebuild that waits for the machine's one-rebuild-at-a-time lock. The lead also does two more merges per ticket.
- **Risk:** low. Every tree has one writer.

### (b) The designer in its own worktree; the engineer in the ticket's (recommended)
- The lead adds one extra worktree, `~/gov-os-worktrees/<W2>-tests` (branch `w2/<W2>-tests`), for the test designer. The engineer works in the ticket's own worktree, as today.
- The designer writes and commits only in its tree. For `gov retrieve` it reads the ticket worktree's store, which is a read, so its tree needs no store and no rebuild.
- **When the designer's tests are committed,** the lead writes a marker in its scratch (`.gov-runtime/scratch/lead/TESTS-READY`, naming the commit). The engineer's brief says what happens next:
  - at its next step, or when it has built, the engineer runs `git merge --no-ff w2/<W2>-tests` in its own tree (its tree, its single write) and runs the acceptance tests once (through `gov accept` once W2-96 lands);
  - if it has already ended, the lead does that merge in the ticket tree, with no worker running there, and starts a fresh engineer to run the tests.

  Disjoint paths make the merge clean, and the designer's commits keep their own authorship and trailers.
- The lead removes the tests worktree and branch before returning.
- **Cost:** one extra worktree per ticket (about 27 MB), no extra store or rebuild, and one merge.
- **Risk:** low.
  - The engineer's merge writes the designer's committed files into its tree. That is a merge, not authorship: the five-rule hook reads `git merge` as no write to the acceptance tests, and the history names the designer.
  - A hurried engineer could edit those merged files afterwards. Rule 1 refuses that, as it does today.

### (c) One worktree, both writers, commits serialised by a lock
- **Cost:** none in disk.
- **Risk:** medium. A test run can still see the other's half-written files, and a shared index needs every commit to pass a lock. This is the collision rule 6 was made for, so I don't recommend it.

## 3. What changes, for (b)
- **The common lead brief:** the loop's steps 1 to 3 (the tests worktree, the marker, the merge, the engineer's single run), and the clean-up before the return.
- **The test designer's brief (A1):** its own worktree, and retrieval from the ticket worktree's store.
- **The engineer's brief (A2):** the marker, the merge, and the single run of the acceptance tests.
- **The prompt §3** (worktrees per ticket) and §6 (the loop).
- **Rule 6:** it now reads "one writing worker per worktree"; a ticket may have two worktrees.
- **The roles tickets:** W2-83b's playbook and W2-33's role files carry it.
- **Nothing in the guard changes.**

## 4. Recommendation
**(b), confidence medium-high.** It gives DEC-959's parallel order with one writer per tree, for one small worktree and one merge per ticket.

## 5. What it blocks, and what waiting costs
It blocks nothing: work goes on in sequence meanwhile. While it waits, each ticket loses roughly the length of its test designer's run (about 1 to 2 hours) of possible overlap.
