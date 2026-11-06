# W2-131 — the independent test designer's brief (DAEO-r8vq)

You are the independent test designer for **W2-131** (`.tickets/DAEO-r8vq.md`): a register chunk in a bundle carries
its own entry's id, not DEC-999. It is a priority fix in re-pin window 4 (DEC-1082 (2)). Read the ticket in full
first; its KPI lines S1 to S3 are what you test. S4 is the CTO's check after the re-pin, not yours.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-131-tests`, branch `w2/W2-131-tests`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-131/`: the cases, a `conftest.py` if needed, and a `README.md` mapping each case's
  node id to the KPI line it covers.
- You may read any code on `w2/integrate` (DEC-963): `src/gov/retrieval/retrieve.py` (`retrieve()`'s inner `item()`
  and `_graph()`'s `record_of`), `src/gov/retrieval/authority.py` (`register_entries_of`), `src/gov/records/queries.py`,
  `src/gov/retrieval/supplementary.py` (line 95: the pattern the fix copies), and the existing tests
  `tests/unit/retrieval/test_w2_87_register.py` and `test_w2_92_follow.py` for how a planted repository and its store
  are built.
- There is no implementation of this ticket yet; you never read one.

## What the cases must show (from the ticket)
- **S1:** a planted repository with a register holding at least DEC-476, DEC-999 and DEC-1082, built into a store.
  - A query only DEC-476's text answers: its evidence item's `id` is `DEC-476`. Today it is DEC-999, so the case is
    red on integrate.
  - A hit in the register's preface carries its chunk id, not an entry id.
  - A parent expansion carries its first entry's id.
  - Where the item has W2-92 S9's `entry` key, `id` equals it.
- **S2:**
  - the path-to-record map that labels items holds no single entry's id for the register's path;
  - DEC-424's move still lifts a failure or lesson record in a ticket's closure.
- **S3:** apart from register items' ids, the bundle is unchanged: the evidence set, its order, the batches, the
  budget used, the gaps and the continuation. Compare it with what today's code gives on the same planted repository,
  the ids normalised.
- Every case must be **red on integrate for the right reason** (S1's ids), or green on integrate where it guards an
  invariant (S2's DEC-424 lift, S3's comparison). Say which, case by case.

## Rules
- No GPU, no model: the planted store uses the test fixtures' stand-in embedder or the lexical route alone, as the
  existing unit tests do. No measure, no `gov retrieve` on the real repository.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, and record their outcome on integrate.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-131-tests` with
  `git commit -m "..." --trailer "Task: DAEO-r8vq" --trailer "Implements: DEC-1082" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with:
- the case list (node id, KPI line, red or green on integrate, and why);
- the commit;
- anything in the ticket you found untestable or ambiguous, as `discoveries`.
