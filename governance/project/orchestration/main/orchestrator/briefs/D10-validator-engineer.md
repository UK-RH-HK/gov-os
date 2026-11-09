# D-10's red-fix list: two of the plan validator's five FAILs are the validator's own reads (W2-139, DAEO-ongl)

You are a fresh **product-spec** worker (W2-139 is a product-spec ticket; the plan validator is a plan tool under `docs/plan/tools/`), launched under W2-139's ticket (`.tickets/DAEO-ongl.md`). Its S3 wants a green run of
the plan validator. W2-139 merged with five FAILs that were already on `w2/integrate`, and DEC-1112 (3) put them on
D-10's red-fix list. The CTO traced all five tonight. Three are records or waits, and the CTO handles them. Two are
the validator reading the plan wrongly. They are yours.

## The validator today
`python3 docs/plan/tools/validate_w2.py` at integrate `adec4718a`: `RESULT: 5 FAIL, 5 NOT RUN`.

1. **`wave2-tickets`:** "ids on one side only: W2-59 (.tickets/ only) … W2-85 (.tickets/ only)" (31 ids).
   - `check_wave2_tickets` reads W2 ids only from §1's ticket table (`wbs()`).
   - But the WBS says, in §1, line 241: "The later tickets (W2-59 onwards) are in §2's cards only."
   - Their cards are §2's `#### W2-59 …` headings (for example line 1130).
   - The plan is as designed; the validator does not read §2.
2. **`ticket-contract-ids-exist`:** "not in the Contract: CAP-1 (W2-20), CAP-2 (W2-20)".
   - The `CAP` pattern, `(?<![A-Za-z0-9])CAP-\d+…`, matches inside `ACT-OLLAMA-CAP-1` and `ACT-OLLAMA-CAP-2`, ACT names
     that W2-20's ticket and others cite.
   - Those are not Contract ids.

## The task
1. `docs/plan/tools/validate_w2.py`:
   - (a) The WBS's W2 ids are §1's table **and** §2's card headings (`#### W2-<id> …`; read the WBS to fix the exact
     heading form, bold or not). The check's PASS line names how many came from each.
     - An id in neither place, or in the WBS but with no ticket, still fails as before.
     - Keep `wbs()`'s baseline paragraph reading as it is.
   - (b) An id preceded by a hyphen (part of a longer name such as `ACT-OLLAMA-CAP-1`) is not a Contract id. This
     applies wherever `CAP` is used: the tickets, the acceptance citations, the CIT-P lines, the baseline.
     - Make sure no real citation is lost: compare the sets the pattern finds before and after over `.tickets/`,
       `tests/acceptance/`, `docs/changes/*-CIT-P.md` and the WBS, and report every difference.
2. Unit cases in `tests/unit/plan/test_validate_w2.py`, as its existing ones are:
   - (a) a planted WBS with one id only in a §2 card passes `wave2-tickets`;
   - (a) a card id with no ticket fails it;
   - (b) `ACT-OLLAMA-CAP-1` in a ticket is not reported, while a bare `CAP-1` that the Contract lacks still is.
3. Run, and report the counts before and after:
   - the validator itself: expected `3 FAIL` after (contract-items-delivered, contract-items-cited-by-tests,
     triage-counts; those are the CTO's);
   - `tests/unit/plan`;
   - `tests/acceptance/W2-51` (the validator's own acceptance suite; its cases plant WBS files, so watch them);
   - `tests/acceptance/W2-49/test_w2_49_validator_lines.py`, run only (W2-49's folder is this ticket's judged
     acceptance folder: you may run it and see names and failure messages, but never read its code, DEC-820 (c)).
   - **If a W2-51 or W2-49 case pins the old reading** (for example it expects a §2-only id to fail), do not change
     any test. Return PACKAGES with the case's name, its message and your recommendation.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-139-d10`, branch `w2/W2-139-d10`. It is integrate at `adec4718a`,
  plus the CTO's ticket commit `4771fba13` (both files in W2-139's paths).
- Write only `docs/plan/tools/validate_w2.py` and `tests/unit/plan/test_validate_w2.py`.
- Never search into `tests/acceptance/W2-49/`: `EMG-common.md`'s exclusion rule, with `W2-49` as the folder.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-139-d10/src` and `TMPDIR=/tmp/gov-os-emg-w139d10`;
  - pytest with `-q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-139-d10` only, with `--trailer "Task: DAEO-ongl" --trailer "Implements: DEC-1109, DEC-1112"`
  `--trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - the validator's line before and after;
  - the pattern's differences over the repository;
  - each suite's counts;
  - the head commit.
