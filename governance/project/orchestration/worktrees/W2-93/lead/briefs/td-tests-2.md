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

## The interface (fixed by the lead from the ticket's KPI lines, the path map's `--sets-root` convention and W2-81's README; both designers code and test to exactly this)

Base commit: `a7b36bcfd98a` (w2/W2-93 at claim). W2-81's README (`tests/acceptance/W2-81/README.md`, "The hidden half's form, for W2-93", "The manifest", "The planted problems", "The visible question half") is the form.

### `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`

1. **Command:** `python3 fixtures/evaluation/adoption-proving-ground/validate_hidden.py --sets-root <root> [--seed <n>]`. `--sets-root` is required; `--seed` defaults to `w2_81_words.DEFAULT_SEED` (8128). It imports W2-81's modules from `tests/acceptance/W2-81/` of the checkout it sits in (found from its own `__file__`, never the working directory), read-only.
2. **Where the hidden half is:** `<root>/fixtures/evaluation/adoption-proving-ground/hidden/` (the evaluation sets' convention, as `gov.retrieval.measure` and `gov.memaudit` use `<sets-root>/fixtures/evaluation/<set>/hidden/`). If it is absent or not a folder: exit 2 with the line `refused: no hidden half under the sets root: fixtures/evaluation/adoption-proving-ground/hidden`. Nothing outside that folder is read as hidden data.
3. **What the folder holds:** `<repository>.yaml` for each of the six repositories (`python-app`, `rust-workspace`, `typescript-monorepo`, `legacy-docs`, `secret-history`, `python-app-clean`) and `variants.yaml`. Any other entry (another file, a subfolder, a symbolic link) is refused naming its file name only; a missing repository file is refused naming the repository.
4. **The built copy:** it builds the six repositories with `w2_81_build.build_all(<tmp>, seed, <small large size, e.g. 4096>, variants=<the hidden variants>)` in a fresh temporary folder under `$TMPDIR` (outside any git work tree), and removes that folder when it ends, pass or fail. What the visible builders plant in each repository is read from the manifests' entries that are not `hidden: true` (or from a second build without variants); it is never a hard-coded list.
5. **Checks.** Each failure is one line `refused: <question id | repository | file name | hidden variant #<n> (<id>)>: <reason>`, never a question's text, an answer, a template, a fact's value, a path's content or a secret's value:
   - **S1 (form, count):** each question file is UTF-8 YAML with `form: w2-81-questions/1`, `repository` equal to its file's name, and `questions` a list; each question holds `id` (`<repository>-h<nn>`, unique in the half), `category`, `question` and `gold_answer` (non-empty strings), `sources` (a non-empty list of `{path, holds}`) and `forbidden` when present (a list of non-empty strings; absent means none: the lead's decision of batch 2). Fewer than 10 in a repository: `refused: <repository>: <n> hidden questions, at least 10 needed`. A question missing a field or with a wrong type: refused naming its id.
   - **S4 / F2 (gold answer held):** each question is resolved on the built copy (`w2_81_questions.resolve(..., "hidden")`): every gold source's `holds` is at the built HEAD at its `path`, and every fact the gold answer's template names exists. A failure is refused naming the question's id.
   - **S5 (must not cite):** every forbidden citation, resolved (declared absences dropped as `resolve` drops them), names a file at the built HEAD; otherwise refused naming the question's id.
   - **S2 (variants):** `variants.yaml` is UTF-8 YAML with `variants:` a list of mappings with unique ids; every variant builds (the hook's refusal is reported as `refused: hidden variant #<n> (<id>): cannot be built`). The kinds required:
     (a) for each of the five planted repositories, each of the five core kinds (`stale-spec`, `superseded-plan`, `misleading-name`, `secret`, `orphaned-test`) that the repository's visible manifest has no entry of: at least one hidden variant of that kind in that repository; missing: `refused: <repository>: no hidden variant of kind <kind>`;
     (b) for each of the seven kinds (the five, `legacy-document`, `large-file`): at least one hidden variant in a repository whose visible manifest has no entry of that kind; missing: `refused: kind <kind>: no hidden variant where the visible builders do not plant it`;
     (c) the clean twin `python-app-clean` has no variant; one there is refused naming its number and id.
     (This is the reading that fits the walled writer's approved brief: 13 variants, 11 by (a) and one each of `legacy-document` and `large-file` by (b).)
   - **Fail closed:** a file it cannot read (no permission, not UTF-8, bad YAML, wrong top-level type, a symbolic link) is refused naming the file only; any exception ends as `refused: <file or "the check">: <exception class name>`, never a traceback or an exception message that could hold data. Every refusal exits 2.
6. **Output when valid** (stdout, exit 0), counts and ids only:
   ```
   <repository>: <n> hidden questions                       (one line for each of the six)
   <repository>: hidden variants <kind>=<n>, <kind>=<n> ...  (one line for each planted repository: each kind its visible build lacks, with its count, 0 included)
   valid: <N> hidden questions in 6 repositories, <M> hidden variants (seed <s>)
   ```
   On refusal: every refusal found, one line each, then exit 2. Lines go to stdout; tests read stdout and stderr together.
7. It writes nothing outside its own temporary folder: never in the repository, never in the sets root.

### `tests/acceptance/W2-81/w2_81_run.py --sets-root <root>`

8. The runner gains `--sets-root <root>`: its hidden folder is `<root>/fixtures/evaluation/adoption-proving-ground/hidden`, read exactly as `--hidden <folder>` is (same file reading, same refusals, same reports). If that folder is absent: `refused: --sets-root holds no hidden half: fixtures/evaluation/adoption-proving-ground/hidden`, exit 2, in every mode, before anything is built. `--sets-root` and `--hidden` together: refused, exit 2. `--hidden` stays as it is for a direct call. The relative path is one constant, `HIDDEN_UNDER_SETS_ROOT = "fixtures/evaluation/adoption-proving-ground/hidden"`.

## Walls (hard; break one and stop)
- **Never open, list, grep or print anything under the evaluation sets' root (`~/gov-os-eval`) or any `hidden/` folder**, in this repository or anywhere. No real hidden half exists in git; if a search would cross one, name the folder the search starts at so it does not. Every hidden half your work touches is a **planted stand-in you write in your sandbox's `$TMPDIR`** (or a pytest `tmp_path`), never in the repository.
- **Never quote a question or an answer** (stand-in or otherwise) in a commit message, your return, a log or a note.
- Never write `fixtures/evaluation/adoption-proving-ground/hidden/**` (the path is in the ticket's list for the delivery, not for you).
- W2-81's files other than `tests/acceptance/W2-81/w2_81_run.py` and `tests/acceptance/W2-81/test_w2_81_runner.py` are read-only (DEC-1010 item 4, DEC-1144 (6)).
- Reads are open otherwise (DEC-820): the whole repository, git history. Never read the counterpart's work on this ticket (see your section).

## Running tests
- Every pytest through the slot and with a TMPDIR outside the repository (your sandbox's `$TMPDIR`):
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR="$TMPDIR" PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<your tree>/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (read the first lines of `heavy_slot.sh` for its exact form if this one is refused). A resource gate's refusal is a wait: run it again later, it does not count as a refusal (DEC-1146).
- A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`. **So no test name of yours may contain `real`, `green_here` or `time_limit`** unless it is meant to be deselected there.
- Anything longer than one line goes in a script file under `<your tree>/.gov-runtime/scratch/` (or `$TMPDIR`), run with `bash <file>` or `python3 <file>`. Write files with the Write and Edit tools and absolute paths. Waits by pid only; no hand-written sleep loops.
- No `gov retrieve` and no `gov context` in the sandbox: search with Read and Grep, and search again once in other words (DEC-1065).
- A session refused twice for the same action stops and says so; never work around a refusal by another tool or form (DEC-1142 (9)). No merge inside the sandbox. No new ticket.

## Commit (your paths only, in your tree)
```
git commit -m "<subject: what changed, never a question or answer>" --trailer "Task: DAEO-6y0x" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-941, DEC-828, DEC-820, DEC-845, DEC-873, DEC-1010" -- <paths>
```
An id you need that is not in that list (DEC-1143, DEC-1144 ...) goes in your return's `discoveries`, never in `Implements:`.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
then `commits: <hash12> <subject> | trailers as committed`, and `guard_refusals: none | - <time> | <form> | <reason as the hook gave it> | true or false-positive`.
`status` is DONE, PACKAGES or ESCALATION. `tests` gives the counts (passed/failed) of each run you made and the command.
