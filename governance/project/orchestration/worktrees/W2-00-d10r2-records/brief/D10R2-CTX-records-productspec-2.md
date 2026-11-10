Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-00-d10r2-records/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10: context-reproducibility's 34 errors, fixed in the ticket records (DEC-1123 (2))

You are a fresh **product-spec** worker for the CTO (orchestrator DAEO-sdxk), launched under W2-04's ticket (`.tickets/DAEO-u4oz.md`, the context packet's home, CAP-15.d). The owner decided (DEC-1123 (2), option
(a) of `governance/project/orchestration/packages/D10-RECORD-REDS.md` §1) that these records are fixed now, before
D-10's run 2. The check: `python3 -m gov.context.context_check` (a `gov check` family, hard-block).

## The red (your tree, store rebuilt at `adeba3758`): "0 ticket(s) failed, 34 error(s)"
A refusal over the 6,000-token ceiling is allowed (it reproduces and counts green): leave those alone. The errors are
tickets whose mandatory inputs the store cannot resolve. The check reports only a ticket's **first** unresolved input,
so a ticket may hold more: repeat until it is clean.
```
DAEO-057v W2-H021 | DAEO-0pyc W2-L065 | DAEO-0z8c W2-L160 | DAEO-2bdu W2-124 | DAEO-4k3l W2-128 | DAEO-6n5k W2-L319
DAEO-6ox0 W2-H052 | DAEO-cb2b W2-118 | DAEO-ecac W3-P09 | DAEO-emq1 W2-117 | DAEO-f58b W2-06 | DAEO-fau3 W2-H006
DAEO-i89t W2-L097 | DAEO-jip3 W2-25 | DAEO-jpr0 W2-123 | DAEO-jzvg W2-H026 | DAEO-k7hz W2-L256 | DAEO-kmcr W2-H035
DAEO-m4rq W2-61h | DAEO-mb2t W2-26 | DAEO-neam W2-H018 | DAEO-nn1s W2-24 | DAEO-nqa2 W2-106 | DAEO-qzca W2-129
DAEO-r30l W2-M188 | DAEO-rd0g W2-15b | DAEO-sdhj W2-M176 | DAEO-t8mp W2-11b | DAEO-u4oz W2-H034 | DAEO-w19l W2-M284
DAEO-wnnz W2-112 | DAEO-yadm W2-H015 | DAEO-zqvn W2-L233 | DAEO-swdu DEC-798 (SUPERSEDED: cannot satisfy a current requirement)
```
The ids are backlog rows (`W2-H…`, `W2-M…`, `W2-L…`, `W3-P…`, defined in `docs/plan/WAVE_2_LIST.md`,
`WAVE_2_TRIAGE.md`, `WAVE_2_WBS.md`) and WBS ids (`W2-112`, a ticket's `wbs_id`), which the store does not hold as
records.

## The task
1. Read `src/gov/context/__init__.py` (and what it calls) to learn exactly which ticket fields are mandatory inputs
   and which reference forms the store resolves (a decision id, a CAP, a file path, a heading). Say it in one line.
2. For each ticket, change only the offending references so the context builds: point each to a record the store
   holds that carries the same content (e.g. the plan file's path, or path plus heading, for a backlog row; the
   ticket's file for a WBS id; DEC-798's live successor for DAEO-swdu, from the register's "Superseded by"), or move
   it to optional inputs where the field allows. Never delete a requirement's meaning, never change a ticket's
   acceptance criteria, scope or status, and keep `closes`/`list_rows` bookkeeping if it is not a mandatory input.
   Many of these tickets are in progress in other worktrees: touch only the offending lines, so their merges stay clean.
3. Verify in your tree: rebuild the store, then the check, until it reads `0 ticket(s) failed, 0 error(s)` (green):
   `env -u PYTEST_ADDOPTS PYTHONPATH=$PWD/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /dev/null`
   then `env PYTHONPATH=$PWD/src python3 -m gov.context.context_check | tail -3`. Then W2-54's case once:
   `PYTHONPATH=$PWD/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_green_here.py -q -p no:cacheprovider -p no:xdist`.
   If the rebuild cannot reach the embedder from your session, say so and stop after the edits (the CTO verifies).

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-00-d10r2-records`, branch `w2/W2-00-d10r2-records` (at `adeba3758`, its
  store already seeded and rebuilt). Write only `.tickets/*.md`.

## Rules
- `EMG-common.md` holds. Never open the evaluation sets, the run folders or any held-out material. No installs, never
  the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-u4oz" --trailer "Implements: DEC-1123"
  --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`. Never merge,
  push, amend or rebase.
- Estimate: 45 minutes. Return the twelve fields, short: the mandatory fields and resolvable forms, per ticket the
  reference changed (old → new), the check's final line, W2-54's result, the head commit.
