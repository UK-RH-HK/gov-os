You are the ticket lead for ticket `DAEO-9nys` (`W2-67`, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, a test-revision ticket whose role is engineer (DEC-907), working only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`.

**This is run 4: the review of rounds 2 and 3** (DEC-916, DEC-920). `git log --oneline -1` must show `a74e9c67`. `git status --short` must show only `?? tests/acceptance/W1-27/w2_67_td4_plant.py`: leave it; it goes with the worktree. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first.

## The decisions (on `w2/integrate`)

- **DEC-916 (the owner's, standing):** a ticket run in rounds gets up to two reviews per round declared in its plan. Your rounds 2 and 3 are declared; run together, one review of both counts as one review of each. A failed review gives one more, the last, for both. A third is only the owner's exception.
- **DEC-920 (delegated), on your run 3 packages:**
  - **P-W2-67-V1:** W2-66's KPI 12 case is DEC-919's known red (row W2-L440). It does not stop your DONE; the TD1C-A fixture stays in `tests/acceptance/W1-27/conftest.py`.
  - **TD6-1 (b):** W2-L420's case keeps asserting the close's counted finding at the context step, with its reason recorded. The uncounted reading is row W2-L442.
  - **Rows:** TD7-A, TD8-A, the core-authority finding and the worksteal re-measure are rows W2-L443 to W2-L446. TD8-B is the weekly sweep's.
  - **TD7-B and the untracked plant** stay in your worktree.

## This run's order

1. **A fresh FULL reviewer** (brief A3 with `JUDGEMENT.md` word for word, role `independent-auditor`, read-only, launched sandboxed, `--effort max`) on `a74e9c67`. It judges rounds 2 and 3:
   - W1-30's 13 cases, each red under its plant (PF2 shown under PF2b, as recorded);
   - W2-L420's docstrings;
   - W2-50's four declared-limit cases;
   - TD1C-A's code-graph clean-up;
   - the static guard's f-string case;
   - the 13 bounded nested-run functions and P1's `TMPDIR`.

   Point it to your plant records (`.gov-runtime/scratch/td-6/plant/PLANTS.md`, `td-7/plant/RECORD.md`, td-8's README) and your red checks (`log/red6.txt`, `red7.txt`, `red8.txt`). Its question is whether any revision only looks red-then-green, or weakens what a case caught before.
2. **If it passes:** commit its probe record under `docs/probes/DAEO-9nys/` (DEC-733) and return DONE.
3. **If it fails** on a finding an honest agent can hit in ordinary work that fails open or loses work:
   - one test-design batch (fresh, sandboxed, `--effort xhigh`), given the finding as described behaviour;
   - then a fresh engineer if builder files need it;
   - then the full verification in the close's form, under the lock, with the retention option and the disk gate first, and the JUnit XML under `/tmp/gov-os-lead-W2-67/`;
   - then a second and last review.
   - Any other finding is a residual you return.
4. **Return** DONE (the probe passed). The orchestrator merges W2-67 after the first re-pin. Otherwise PACKAGES.

**Estimate:** about 1.5 to 2 hours for the review; about 4 hours more if it fails.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
