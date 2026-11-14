# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-5 (fix round after review 2, F1)

You are a fresh independent test designer for DAEO-6f0s (W2-184). Batches td-1 to td-4 are merged and green
(`tests/acceptance/W2-184/`, 451 cases under `gov accept W2-184`). The FULL review's round 2 (the probe) failed on one
finding, F1; the owner decided it (P-W2-184-1 (a), DEC-1010; the ticket's last paragraph). Write the cases for the
described behaviour below (DEC-136). The interface carries it as amendment **5.1a**. Do not read the engineer's work
on this ticket (`src/gov/launch/`), and do not read the review records' code pointers: test the behaviour as described.
You are launched on Opus because the ticket is promoted (a fail-open finding in its round-1 record, DEC-1120 (3)).

Context: the ticket text and its sources, as `gov context` gives them:
  /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-td-5.md (JSON).

## The behaviour (round 2's F1, as the owner decided it)
Today a launch reads the ticket's probe records (`docs/probes/<ticket name>/**/*.md`) only under its own launch root.
A test designer is launched from the ticket's *tests* worktree (a second git worktree of the same repository, on its
own branch), where the probe records committed on the ticket branch are absent; so on a promoted ticket it starts on
the table's model, and an Opus model after `--` is refused. Decided: the launch also reads `docs/probes/<name>/` under
each worktree root that the ticket's launch records (in the shared record folder) name. Cases, at least:

1. **The promotion reaches the tests worktree.** A fixture repository with a ticket worktree and a tests worktree
   (two real git worktrees of one repository, so they share one main checkout and one record folder; FULL or
   STANDARD ticket, a `criticality.yaml`). A probe record with a fail-open finding (and, as a second case, two
   records with `judgement: fail`) is committed on the ticket branch only. An engineer is launched from the ticket
   worktree (its launch record names that root). Then an independent test designer launched from the tests worktree:
   its launch record shows `model_source: "promotion"`, the Opus model, and
   `promotion: {"reason": ..., "record": "docs/probes/<id>/..."}` (the root-relative path); and the same launch with
   the Opus model after `--` is accepted, not refused.
2. **A deleted root is skipped.** A launch record of the ticket naming a root that no longer exists (deleted
   worktree, or a planted record naming a missing folder): the launch is not refused for it and behaves as the other
   roots give.
3. **No probe record anywhere: as before.** Launch records name roots, but no root holds `docs/probes/<id>/`: the
   test designer's launch is on the table's model, `promotion: null`, and an Opus model after `--` is refused naming
   both (as today).
4. **Nothing that refuses today stops refusing:** a probe record whose front matter is not YAML, found only under the
   other root, refuses the launch naming the file; a launch record file in the record folder that is not JSON refuses
   (as the review count does).
5. **Counted once:** the same record (same root-relative path) under both roots counts once: one record with
   `judgement: fail` present in both trees is not "two failed reviews" (no promotion).
6. **Other tickets' launch records do not widen the search:** a root named only by a *different* ticket's launch
   records is not read for this ticket, even when it holds `docs/probes/<this id>/` with a fail-open record.
Name, per case, what it fails on at the current head (cases 1, 5 and 6 depend on the new reading; 2-4 may pass today:
say which).

Use the existing support (`tests/acceptance/W2-184/w2_184_support.py`, `conftest.py`, the S5 cases in
`test_w2_184_s5_promotion.py`) for the stand-in CLI and the fixture project; build the second worktree with
`git worktree add` inside your `$TMPDIR` fixture. Put the cases in a new file
`tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py` (and support additions in `w2_184_support.py` if needed;
keep every existing case). Add a line to the folder's `README.md`. Every commit that rewrites or adds to the decided
behaviour carries `Rewrite-Reason: DEC-1010, P-W2-184-1 (a)` in its trailer paragraph.

**Do not open, list or read anything under `fixtures/evaluation/` or any `hidden` folder.**

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (at e99c8059c). Write only
  `tests/acceptance/W2-184/` (and scratch under your tree's `.gov-runtime/scratch/`).

## How to run tests (every pytest through heavy_slot.sh)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once more in other words.
Report the new cases' red/green at your tree's head, with the failing lines of the red ones.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s) tests: review round 2's F1: a test designer launched from the tests worktree sees the ticket's probe records (P-W2-184-1 (a))" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1120, DEC-1010" --trailer "Rewrite-Reason: DEC-1010, P-W2-184-1 (a)" -- tests/acceptance/W2-184
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments)

