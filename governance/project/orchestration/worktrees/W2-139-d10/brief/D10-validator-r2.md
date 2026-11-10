Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-139-d10/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the plan validator, round 2 (W2-139, DAEO-ongl)

You are a fresh **product-spec** worker, launched under W2-139's ticket (`.tickets/DAEO-ongl.md`, a product-spec
ticket; the plan validator is a plan tool under `docs/plan/tools/`). Round 1 (`d76e79996`) made the validator read
§2's card ids and stopped it from reading `CAP-n` inside a longer name. Its independent review is NOT READY on one
finding. You fix it.

## The review's findings (`governance/project/orchestration/reviews/D10-validator-review.md`)
- **F1 (blocks: in scope, ordinary work, fails open):** three-digit W2 ids are read on neither side.
  - `W2_ID` (`validate_w2.py:20`), the §1 row pattern (`:110`) and the new `CARD` pattern all take exactly two digits.
  - So 51 tickets (W2-100 to W2-153) and 28 §1 rows (W2-100 to W2-127) are never read, and `wave2-tickets` PASSes
    over tickets with no WBS entry.
  - The CTO has now added the missing records on `w2/integrate` (`34f97dfea`: cards for W2-128 to W2-153, filed with
    none). Your worktree has them merged in (`4b4ca0c12`).
- **F4 (fix it too; cheap):** unit case 1 checks its counts by substring (`"3 W2 ids" in reason` also accepts "13 W2
  ids"). Pin the line by equality.
- **F2 and F3** are rows, not yours to fix:
  - F2: `CAP-22.b-CAP-22.c` reads only the first id; no file uses that form.
  - F3: a card for a ticket whose §1 row was removed passes; the counts show it.

## The task
1. `docs/plan/tools/validate_w2.py`: W2 ids of two or three digits (an optional letter suffix as today) everywhere
   the validator reads them: the tickets' `wbs_id`/`external-ref`, §1's rows, §2's card headings. Update the
   docstrings that say "two digits" or "W2-59 onwards" as needed.
2. `tests/unit/plan/test_validate_w2.py`:
   - a case with a three-digit ticket with no WBS entry (FAIL), one with its card (PASS) and one in a §1 row (PASS);
   - unit case 1's counts compared by equality.
3. Run, and report the counts before and after:
   - the validator over your worktree: expected `2 FAIL` (contract-items-delivered CAP-22.c,
     contract-items-cited-by-tests), with `wave2-tickets` PASS naming the three-digit ids too. If it FAILs on an id,
     name it: the records are the CTO's;
   - `tests/unit/plan`;
   - `tests/acceptance/W2-51`;
   - `tests/acceptance/W2-49/test_w2_49_validator_lines.py`, run only, never read (DEC-820 (c));
   - all with `--optin=lifted,breadth`.
   - If a W2-51 or W2-49 case pins the two-digit reading, change no test: return PACKAGES.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-139-d10`, branch `w2/W2-139-d10`, at `4b4ca0c12`.
- Write only `docs/plan/tools/validate_w2.py` and `tests/unit/plan/test_validate_w2.py`.
- Never search into `tests/acceptance/W2-49/`: `EMG-common.md`'s exclusion rule, with `W2-49` as the folder.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-139-d10/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - pytest with `-q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite.
- Commit on `w2/W2-139-d10` only, with `--trailer "Task: DAEO-ongl" --trailer "Implements: DEC-1109, DEC-1112"`
  `--trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 20 minutes. Return the twelve fields, short:
  - the validator's line before and after;
  - each suite's counts;
  - the head commit.
