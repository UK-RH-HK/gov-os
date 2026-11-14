## The interface (fixed by the lead from the ticket's KPI lines, the path map's `--sets-root` convention and W2-81's README; both designers code and test to exactly this)

Base commit: `a7b36bcfd98a` (w2/W2-93 at claim). W2-81's README (`tests/acceptance/W2-81/README.md`, "The hidden half's form, for W2-93", "The manifest", "The planted problems", "The visible question half") is the form.

### `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`

1. **Command:** `python3 fixtures/evaluation/adoption-proving-ground/validate_hidden.py --sets-root <root> [--seed <n>]`. `--sets-root` is required; `--seed` defaults to `w2_81_words.DEFAULT_SEED` (8128). It imports W2-81's modules from `tests/acceptance/W2-81/` of the checkout it sits in (found from its own `__file__`, never the working directory), read-only.
2. **Where the hidden half is:** `<root>/fixtures/evaluation/adoption-proving-ground/hidden/` (the evaluation sets' convention, as `gov.retrieval.measure` and `gov.memaudit` use `<sets-root>/fixtures/evaluation/<set>/hidden/`). If it is absent or not a folder: exit 2 with the line `refused: no hidden half under the sets root: fixtures/evaluation/adoption-proving-ground/hidden`. Nothing outside that folder is read as hidden data.
3. **What the folder holds:** `<repository>.yaml` for each of the six repositories (`python-app`, `rust-workspace`, `typescript-monorepo`, `legacy-docs`, `secret-history`, `python-app-clean`) and `variants.yaml`. Any other entry (another file, a subfolder, a symbolic link) is refused naming its file name only; a missing repository file is refused naming the repository.
4. **The built copy:** it builds the six repositories with `w2_81_build.build_all(<tmp>, seed, <small large size, e.g. 4096>, variants=<the hidden variants>)` in a fresh temporary folder under `$TMPDIR` (outside any git work tree), and removes that folder when it ends, pass or fail. What the visible builders plant in each repository is read from the manifests' entries that are not `hidden: true` (or from a second build without variants); it is never a hard-coded list.
5. **Checks.** Each failure is one line `refused: <question id | repository | file name | hidden variant #<n> (<id>)>: <reason>`, never a question's text, an answer, a template, a fact's value, a path's content or a secret's value:
   - **S1 (form, count):** each question file is UTF-8 YAML with `form: w2-81-questions/1`, `repository` equal to its file's name, and `questions` a list; each question holds `id` (`<repository>-h<nn>`, unique in the half), `category`, `question` and `gold_answer` (non-empty strings), `sources` (a non-empty list of `{path, holds}`) and `forbidden` (a list). Fewer than 10 in a repository: `refused: <repository>: <n> hidden questions, at least 10 needed`. A question missing a field or with a wrong type: refused naming its id.
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
