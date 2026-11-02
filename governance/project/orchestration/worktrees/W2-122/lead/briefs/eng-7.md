# Brief: engineer, DAEO-blwa (W2-122), STANDARD — run 2: KPI 5's behaviour taken out (DEC-1027 C)

You are a fresh engineer. Ticket: DAEO-blwa (W2-122), profile STANDARD, in the worktree
`/home/usain/gov-os-worktrees/W2-122` on branch `w2/W2-122`. The ticket's code (`gov rebuild --seed`) is built and
committed; `w2/integrate` has been merged in. You change one thing, building to the specification, never to a test.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-blwa','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

## Standing rules

**Read `/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/lead/briefs/eng-1.md` in full:** its sections
"Standing rules", "What you read" and "What you write" are your rules, word for word, with these differences:
its "What to build" is built (read `src/gov/rebuild/seed.py` and `src/gov/rebuild/command.py`); `TESTS-READY` exists;
`docs/changes/W2-122-evidence.md` is not yours to change. In short, from it:
- **DEC-732, word for word:** in this worktree, **every test run and every `gov` command used for verification runs
  this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src` set **per command** (never in a
  session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Policy 2 (DEC-820) (c) and (d):** you never read `tests/acceptance/W2-122/` (you may run it through `gov accept`
  only and see names, results and failure messages); you never read the hidden half of any evaluation set by which
  you are measured. Never read secrets or the held-out material's contents; never name the qualification oracle.
- **Retrieval (DEC-836):** use `gov retrieve` before reading files at random:
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`; batches for a large question
  (DEC-860: `--batch-size`, then `--continue <token>`); a code question through the code graph's traversal
  (`trace_path`, `search_graph`, `query_graph`), small and targeted (DEC-859).
- **Read refusals (DEC-849):** searches from the repository root, `governance/project/` or `.claude/` may be refused:
  take the refusal, search named folders, count them in your return.
- **Command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces; longer things in a script file under
  `.gov-runtime/scratch/eng/` written with the Write tool. **Refused twice for the same call: stop and say so.**
- **Budget (DEC-898):** 1 GB and 50,000 files and folders; `TMPDIR=/tmp/gov-os-lead-W2-122`; pytest's own retention;
  measure your scratch at the end. No real-tree rebuild (never `--no-embeddings` on a real tree). Row W2-L423's rule:
  12-digit hashes under `.gov-runtime/`. Install nothing; no merge, push, rebase, amend, reset; never ask the owner.
- Your paths: `src/gov/rebuild/seed.py`, `src/gov/rebuild/command.py`, `tests/unit/rebuild/test_w2_122*`.

## The decision and what to change

DEC-1027 C (owner, 2026-11-02): the ticket's KPI 5 (a full rebuild whose semantic store was asked for and not
recreated fails, `REBUILD_FAILED` with `store: semantic`) moved to its own ticket, W2-124 (`DAEO-mb2t`), with the
owner's rule that **adoption never fails for a missing embedder**. Read the ticket file `.tickets/DAEO-blwa.md` (no
KPI 5 any more) and `.tickets/DAEO-mb2t.md`.

So: take that behaviour out of this ticket's change. **A full rebuild whose semantic store is not recreated (the
endpoint unavailable, hung or failing part way) answers as it did at the ticket's base** — `git show
w2/integrate:src/gov/rebuild/command.py` shows that base: the rebuild succeeds, and its answer's `stores.semantic` is
`{"status": "not_recreated", "reason": ...}` (with the `embedding` note where there is one), exactly as before. The
module docstring's sentence about `REBUILD_FAILED` goes too.

**What must stay fail closed (the seed's own KPIs, untouched):** a tree is a warm base only when its stores are
complete. Today the stores' record (`stores.json`) is written after every rebuild with embeddings asked for; with the
failure gone, a rebuild whose semantic store was **not** recreated must **not** write that record (it was removed at
the rebuild's start and stays removed), so such a tree is refused as a base, named, and a seed from it never copies a
partial semantic store. Check the seeded path too (a seeded rebuild whose semantic stage then fails). Everything else
of the seed is unchanged; `--no-embeddings` is unchanged.

## Then

1. Your unit tests in `tests/unit/rebuild/test_w2_122*.py`: adjust those that asserted `REBUILD_FAILED` to the
   behaviour above, and add one showing that an unrecreated semantic store leaves no record. Run
   `tests/unit/rebuild/` (one folder, to its end, no `-x`) and quote its counts.
2. Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit`
   file. Commit with the trailers in the final block:

       git commit -m "W2-122: a rebuild without its semantic store answers as at its base; no record, so no warm base (DEC-1027 C)" --trailer "Task: DAEO-blwa" --trailer "Role: engineer" --trailer "Implements: DEC-1027, DEC-1014" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

   then quote `git log --oneline -2` and `git status --short`.
3. Do not run `gov accept` yet: the lead merges the test designer's retirement of KPI 5's cases after you return and
   runs it. Say that you did not.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Also say: the sandbox check's result; whether you used `gov retrieve`; the read refusals met. Refused twice for the
same call: stop and say so.
