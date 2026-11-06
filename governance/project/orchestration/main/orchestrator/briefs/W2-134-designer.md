# W2-134 — the independent test designer's brief (DAEO-m4rq)

You are the independent test designer for **W2-134** (`.tickets/DAEO-m4rq.md`): the memory measure re-anchors
line-cited gold in memory for the commit it measures, and never writes the sets root (W2-61h S8's code, DEC-1085
(2)). Read the ticket in full first, and W2-61h's S8 line in `.tickets/DAEO-h2k3.md`. The ticket's KPI lines S1 to S4
are what you test.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-134-tests`, branch `w2/W2-134-tests`. It is made from
  `w2/W2-61h-s7` (W2-61h S7's source families, not yet merged into integrate) with `w2/integrate` merged in, so S4's
  family case can run.
- You write only `tests/acceptance/W2-134/`: the cases, a `conftest.py` if needed, and a `README.md` mapping each case's
  node id to the KPI line it covers.
- You may read any code on your branch (DEC-963):
  - `src/gov/retrieval/measure.py` (how a set is loaded, how a line-cited gold source is matched, the `--sets-root`
    and `--kept` forms);
  - the re-anchoring pattern in `.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py` (how a block read at the
    source's own commit is found again at another root);
  - `tests/acceptance/W2-61h/` and `tests/acceptance/W2-61/` for how planted sets and planted repositories are built.
- There is no implementation of this ticket yet; you never read one.

## What the cases must show (from the ticket)
- **S1:** a planted git repository with two commits.
  - A gold source cites lines of a block at commit 1; commit 2 inserts lines above it, so the block moves down.
  - The measure on commit 2 scores a hit when the evidence holds the moved lines. Today it is red: the old lines are
    used.
  - An unmoved block keeps its lines.
- **S2:** a planted sets root, every file hashed before and after.
  - Two measures run one after the other, on commit 1 and on commit 2. Each scores against its own commit's lines.
  - Every file under the sets root is byte for byte unchanged.
- **S3:** a source whose block is deleted in commit 2.
  - It is named by question id and entry number only, with no label text, path or lines in the output.
  - It counts as not found.
- **S4:** with every cited block unmoved, the per-question lines and totals equal today's output for the same run, and
  a source-family hit (S7) still scores as before.
- Every case must be **red on your branch for the right reason**, or green where it guards an invariant (S2's
  hashes, S4's equality). Say which, case by case.

## Rules
- No GPU, no model: the cases run the measure's scoring on planted kept outputs (`--kept`) or on a stand-in
  retriever, as the existing W2-61h cases do. No `gov retrieve` on the real repository, no measure on real sets.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Your cases plant their own sets in a temporary directory.
- Run your cases through the heavy slot that `EMG-common.md` names, and record their outcome.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-134-tests` with
  `git commit -m "..." --trailer "Task: DAEO-m4rq" --trailer "Implements: DEC-1085" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with:
- the case list (node id, KPI line, red or green on your branch, and why);
- the commit;
- the interface your cases assume (function or command names, arguments), so the engineer builds to it;
- anything in the ticket you found untestable or ambiguous, as `discoveries`.
