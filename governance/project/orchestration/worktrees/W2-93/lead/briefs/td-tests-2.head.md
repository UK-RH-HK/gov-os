# Brief: W2-93 (DAEO-6y0x), two revisions of `tests/acceptance/W2-93/` (independent-test-designer, tests batch 2)

You are a fresh independent test designer for this ticket's acceptance tests. Class C2, profile STANDARD.

- **Your tree:** `/home/usain/gov-os-worktrees/W2-93-tests`, branch `w2/W2-93-tests` (at `ceffc1d95633`, the first batch, already merged into `w2/W2-93` as `7add172a7`). Write only `tests/acceptance/W2-93/**` there.
- **The counterpart:** `validate_hidden.py` and the runner's `--sets-root` were written by another test designer in `/home/usain/gov-os-worktrees/W2-93` (branch `w2/W2-93`, commit `555169eb401a`). Do not read its new work (that commit's files `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`, and its changes to `tests/acceptance/W2-81/w2_81_run.py` and `test_w2_81_runner.py`).

## What happened
The merged folder ran 130 passed, 1 failed (`tests/acceptance/W2-93`, the whole-folder form):
```
FAILED tests/acceptance/W2-93/test_w2_93_validator.py::test_s1_a_question_missing_a_field_or_of_a_wrong_type_is_refused_naming_its_id[forbidden]
E   AssertionError: exit 0: ... assert 0 == 2   (the validator accepted a hidden question with no `forbidden` key)
```
and `gov accept W2-93` refused before running: `ACCEPT_MAP_UNREADABLE: ticket DAEO-6y0x: the README of tests/acceptance/W2-93/ has a map row naming no KPI line it can read`.

## The two revisions
1. **`forbidden` is optional (the lead's decision, recorded in the ticket's close; within S1's "in the form W2-81's README states").** W2-81's own visible half, which defines the form, leaves the key out in 46 of its 61 questions (the clean twin's carry none), and `w2_81_questions.resolve` reads it as `item.get("forbidden") or []`. So: a question **without** `forbidden` is valid (absent = no forbidden citation); a `forbidden` that is present must be a list of non-empty strings, else refused naming the id. Revise the S1 case: drop the `forbidden`-missing refusal; add a case that a stand-in whose questions have no `forbidden` key (for example in one repository) exits 0; keep `forbidden-not-a-list`, and add one for a list holding a non-string or an empty string, each refused naming the id. Update the README's S1 row to match.
2. **The README's map must be readable by `gov accept`.** Its parser is `parse_map` in `src/gov/accept/runner.py` (read it): every row of a table with a `KPI` and a `Tests` column must name a KPI line in its KPI cell (`S1` ... `S6`, `F1`, `F2`). The last row, "the stand-in (support)", names none. Map those two support cases to the lines they serve (S1 and S2), or move them out of the table into prose. Then check the map with `PYTHONPATH=<tree>/src python3 -c "from pathlib import Path; from gov.accept.runner import parse_map; print(sorted(parse_map(Path('<tree>/tests/acceptance/W2-93/README.md').read_text())))"` (expect the eight lines).
3. Run the whole folder once (the form under "Running tests"; on your branch the validator is absent, so its cases are red for that reason only, as in batch 1: check that the red reasons are only the missing script and the runner's unrecognised `--sets-root`, with no error of the tests' own). Commit with the trailers below and return.
