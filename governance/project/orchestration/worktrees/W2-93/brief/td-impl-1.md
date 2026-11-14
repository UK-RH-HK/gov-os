Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: W2-93 (DAEO-6y0x), the validator and the runner's `--sets-root` (independent-test-designer, build batch 1)

You are the ticket's independent test designer who writes the **check code** of W2-81's held-out half (DEC-1143 (4) C6, DEC-1144 (6)). The hidden half itself was written blind by a walled writer (run `20261112T185824Z-adoption-proving-ground-r1`) and sits outside git under the evaluation sets' root; **you never see it**. The CTO runs your validator on it himself. Class C2, profile STANDARD.

- **Your tree:** `/home/usain/gov-os-worktrees/W2-93`, branch `w2/W2-93`. Write only there, only these paths:
  `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`, `tests/acceptance/W2-81/w2_81_run.py`, `tests/acceptance/W2-81/test_w2_81_runner.py`.
- **The counterpart:** another test designer writes `tests/acceptance/W2-93/**` in `/home/usain/gov-os-worktrees/W2-93-tests` (branch `w2/W2-93-tests`) to the same interface. Do not read that tree, that branch or that folder.

## What you deliver
1. `validate_hidden.py`, exactly as "The interface" items 1-7 state. Reuse W2-81's own code (read-only) rather than re-implementing it: `w2_81_build.build_all(..., variants=...)` / `apply_variants` (read `_apply_one`, `_put`), `w2_81_questions.load_set` / `resolve` (and `QuestionError`), `w2_81_manifest`, `w2_81_git` (the HEAD tree; `outside_this_repository`). Read `w2_81_run._hidden` for how the runner reads a hidden folder today, and keep the validator's file reading at least as strict. Fail closed everywhere; print counts and ids only.
2. `w2_81_run.py --sets-root <root>`, as item 8 states, and in `test_w2_81_runner.py` its cases (DEC-1144 (6)): a stand-in sets root holding a stand-in hidden half (`w2_81_standin.write_hidden_stand_in` into `<tmp root>/fixtures/evaluation/adoption-proving-ground/hidden`) is found and read with only `--sets-root` given (the hidden-half line of the verdict says present); a root without one exits 2 naming the missing folder; `--sets-root` with `--hidden` is refused. Keep W2-81's tripwire (`conftest.py`'s `this_repository_unchanged`) and `_removed_after` happy: every folder under the case's own `tmp_path`, nothing in the repository. Nothing else in W2-81's folder changes (its README is not in the ticket's paths: say in `discoveries` what line it would need).
3. Your own self-check of the validator, **not committed in tests/acceptance/W2-93** (that folder is the counterpart's): a scratch script under `$TMPDIR` that plants a stand-in hidden half (10 questions per repository from `write_hidden_stand_in`, plus a `variants.yaml` stand-in of your own with one variant for each required kind — model them on the hidden variants in `test_w2_81_runner.py` / `test_w2_81_round2.py`, read `apply_variants`), runs the validator (exit 0, the lines of item 6), then breaks one thing at a time (9 questions in one repository; a question missing each field; a source line not at HEAD; a forbidden citation naming no file at HEAD; one required kind removed; a variant in the clean twin; an unreadable file, not UTF-8, bad YAML, a symbolic link, an extra file; no hidden folder) and checks each exits 2 with the right `refused:` line and no stand-in text in the output. Report its counts in `tests`.
4. Run W2-81's whole suite once at the end (`tests/acceptance/W2-81`, the form under "Running tests") and report its counts; it must stay green.
5. Commit your three paths with the trailers below. One commit per coherent step is fine.

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

## The context packet (`gov context DAEO-6y0x --role independent-test-designer --budget 16000`; the ticket, its sources and the integrated store's chunks)
```json
{
  "ticket": "DAEO-6y0x",
  "ticket_text": "---\nid: DAEO-6y0x\nstatus: in_progress\ndeps: [DAEO-l78m, DAEO-m1u3]\nlinks: []\ncreated: 2026-10-30T22:14:08Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W2-93\ntags: [wave-2, audit, evaluation, held-out, standard, proving-ground]\nwbs_id: W2-93\ntitle: 'W2-81''s held-out half: hidden questions and planted-problem variants per synthetic repository, by an independent session'\nclass: audit\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\ndepends_on: [DAEO-l78m, DAEO-m1u3]\nallowed_paths:\n- tests/acceptance/W2-93/**  # its acceptance tests, form only (CTO, DEC-1167 (3): the close)\n- docs/probes/DAEO-6y0x/**  # the probe record\n- fixtures/evaluation/adoption-proving-ground/validate_hidden.py\n- fixtures/evaluation/adoption-proving-ground/hidden/**\n- tests/acceptance/W2-81/w2_81_run.py  # the runner's --sets-root, by the independent test designer only (DEC-1144 (6))\n- tests/acceptance/W2-81/test_w2_81_runner.py  # its case, the same designer (DEC-1144 (6))\nkpis:\n  success:\n  - 'At least 10 hidden questions per synthetic repository, each with its gold answer, gold sources and forbidden citations, in the form W2-81''s README states Verify: `validate_hidden.py` on a planted stand-in hidden folder prints, for each repository, a question count of 10 or more and exits 0; a planted folder with 9 for one repository is refused; each planted question holds the fields the README states [DEC-957, DEC-941, DEC-828]'\n  - 'At least one hidden planted-problem variant per kind that the visible builders do not produce, so an adoption tuned to the visible generator is caught Verify: `validate_hidden.py` on a planted stand-in set prints, for each kind of planted problem the visible builders do not produce, the number of hidden variants per repository; a planted set missing one kind is refused [DEC-941]'\n  - 'Written by a session independent of the sessions it measures; nothing hidden written outside the hidden folder; no question or answer quoted in a commit message, a return, a log or a ticket note Verify: the delivery''s run record names the walled writer''s run (`20261112T185824Z-adoption-proving-ground-r1`) and its launch log the approved brief''s sha256 (the sets root is outside git, so no commit carries it); `validate_hidden.py --sets-root` finds the hidden files only under the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845, DEC-873]'\n  - 'Every gold answer is held by the repository the builder builds, checked on a built copy Verify: `validate_hidden.py` on a built copy of a planted stand-in repository: every gold answer is found in it; a planted answer the built copy does not hold is refused naming its id [DEC-828]'\n  - 'The hidden half proves its own data valid with an automatic check, `validate_hidden.py`, written by the ticket''s independent test designer (never the walled writer), run by the CTO on the delivered hidden half before it is used, printing counts and ids only, and recorded: every forbidden (\"must not cite\") file names a file of the repository the builder builds, checked on a built copy; every kind of planted problem the visible generator does not produce has at least one hidden variant per repository; anything it cannot read refuses (fail closed); W2-81''s files are not touched Verify: planted stand-in cases: a must-not-cite file absent from the built copy refuses, a kind with no variant refuses, an unreadable file refuses (non-zero exit); `git diff` shows W2-81''s files untouched except the two paths DEC-1144 (6) gives this ticket (`--sets-root`); the delivered hidden half has a recorded run of the check (counts and ids only) [DEC-1010 item 4]'\n  - 'The W2-81 runner (`tests/acceptance/W2-81/w2_81_run.py`) and `validate_hidden.py` each take `--sets-root <root>` and find the hidden half under it, so neither the CTO nor a session names the hidden folder on a command line; the runner''s `--hidden <folder>` stays for a direct call; both written by the independent test designer Verify: a planted stand-in sets root holding a stand-in hidden half: the runner and `validate_hidden.py` given only `--sets-root` find and read it, and a root without one exits non-zero naming the missing folder [DEC-1144 (6), DEC-1143 (4)]'\n  failure:\n  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session''s sandbox (the guard''s path map) are refused or find it 0 times'\n  - 'A question whose gold answer the built repository does not hold. Verify: `validate_hidden.py` on a planted stand-in question whose gold answer the built copy does not hold exits non-zero and names the question id'\nprofile: STANDARD\nsources:\n- DEC-957\n- DEC-941\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-873\n- DEC-1010\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-93/\n  author: independent-test-designer (MR-3); form only (counts, fields, sources exist), never printing a question or an answer\ntrack: B\nlist_rows: []\n---\n# W2-93 W2-81's held-out half\n\nCard: the WBS's proposed companion \"W2-81's held-out half\" (\u00a72), filed as MEMORY-SPEC-MAP gap 6, resolved by the owner in DEC-957. Without it W2-81's and W2-88's question figures stand on the visible half only.\n\n- **Starts** once W2-81's README states the hidden half's form and its builders exist. The auditor reads the builders and the README, never edits them.\n- **Before it starts, the orchestrator adds an `evaluation_sets` entry** to the path map: `adoption-proving-ground`, `visible: tests/acceptance/W2-81/questions/**`, `hidden: fixtures/evaluation/adoption-proving-ground/hidden/**`; `measures` by tickets (adoption and retrieval builders, the sessions running the adoption under test, and W2-81); the writer's own ticket is not measured. W2-84's refusal then covers it from every worktree.\n- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.\n\n## Widened by the owner (DEC-1144 (6), P1-F (a), 2026-11-12)\n\nThe W2-81 runner's `--sets-root <root>` goes here, not in a new ticket: two paths in `tests/acceptance/W2-81/` for the independent test designer who writes `validate_hidden.py`, and one KPI line (the last success line). W2-81 is closed; nothing else in its folder changes. If W1-01's acceptance-author check or the guard refuses a W2-93 commit there, it comes back to the CTO as a package; no other route.\n- **Verify re-worded (CTO, 2026-11-13, DEC-1157 (12), DEC-1167 (3)):** S3 and S5 fitted to the walled route (the sets root is outside git; DEC-1144 (6)'s two W2-81 paths exempt from \"untouched\"); the KPI text before each Verify unchanged.\n",
  "authority": [
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    },
    {
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-873",
      "sha256": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "reason": "declared in sources",
      "tokens": 627
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DAEO-l78m",
      "sha256": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "reason": "declared in sources",
      "tokens": 1878
    },
    {
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "mandatory": [
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    },
    {
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-873",
      "sha256": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "reason": "declared in sources",
      "tokens": 627
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DAEO-l78m",
      "sha256": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "reason": "declared in sources",
      "tokens": 1878
    },
    {
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "supplementary": [
    {
      "id": "ba83ae15d79bd281f4078981",
      "path": "docs/probes/DAEO-l78m/PR-DAEO-l78m-moderated.md",
      "text": "# W2-81 \u2014 the moderator's triage of review 5 (DEC-1010 item 1 and item 4)\n\nReview 5 (round 3, an independent auditor at effort max, on `165d3057146a`) returned FAIL on three findings. Its full\ntext is in the lead's draft `.gov-runtime/scratch/lead/probes/` of this worktree and in the lead's return\n(`W2-81-A5-r3-dec1005.json`). The owner decided (DEC-1010 item 4): no extra round; W2-81 lands now; the risk behind F1\nand F2 (a badly written secret exam) is removed at its source, W2-93, which writes the exam and proves its own data\nvalid with an automatic check as its own KPIs; the judge's general hardening is a Wave 3 row. The moderator (the CTO,\nuntil the three layers start) triages accordingly; READY is computed from the block below, not declared.\n\n- **F1** (a forbidden citation naming no file of the built repository is dropped silently): out of W2-81's scope\n  (DEC-1010 item 4: W2-93's KPI \"every must-not-cite file exists\"); a Wave 3 row for the judge's hardening.\n- **F2** (READY without the measurement half's planted-problem variants): out of W2-81's scope (W2-93's KPI \"every\n  kind of planted problem is present\").\n",
      "tokens": 284
    },
    {
      "id": "68f7ae754fe56ed696a0246c",
      "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md",
      "text": "  an adoption tuned to the visible generator is caught [DEC-941]\"\n- **Line 3 (yours, in part):** \"Written by a session independent of the sessions it measures; nothing hidden written\n  outside the hidden folder; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820\n  (d), DEC-845, DEC-873]\". You write only into `out/`, and a variant's commit `message` holds no question or answer.\n- **Line 4 (yours, as far as a session without a shell can):** \"Every gold answer is held by the repository the builder\n  builds, checked on a built copy [DEC-828]\". You derive each answer from the builders' code and the README's facts, and\n  the source text you name is text a builder or one of your variant steps writes. The check on a built copy is run after\n  delivery by W2-81's own runner, not by you.\n- **Line 5 is not yours:** \"The hidden half proves its own data valid with an automatic check (`validate_hidden.py`, beside\n  the data, run before every commit of the hidden half and recorded) ...\" That script and its run are made outside this\n  job. You do not write it.\n",
      "tokens": 276
    },
    {
      "id": "119285c8268c107080505f6f",
      "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md",
      "text": "## 1. Your job, and its bounds\nW2-81 built five synthetic repositories with planted problems, a clean twin of one of them, a judge and a scorer. Its\nvisible half is a set of development questions. You write the other half, the held-out one that measures: hidden\nquestions per repository, and planted-problem variants that the visible builders do not make, so that an adoption tuned\nto the visible generator is caught. You never see an adoption's output or the judge's reports.\n\nYou work to these lines of the ticket (W2-93, word for word) and to nothing beyond them. Nothing else is asked of you: no\nextra question, kind, check or file.\n\n- **Line 1 (yours):** \"At least 10 hidden questions per synthetic repository, each with its gold answer, gold sources\n  and forbidden citations, in the form W2-81's README states [DEC-957, DEC-941, DEC-828]\"\n- **Line 2 (yours):** \"At least one hidden planted-problem variant per kind that the visible builders do not produce, so\n  an adoption tuned to the visible generator is caught [DEC-941]\"\n- **Line 3 (yours, in part):** \"Written by a session independent of the sessions it measures; nothing hidden written\n",
      "tokens": 288
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "  - `measures` by tickets: the tickets that build adoption or retrieval, the tickets whose sessions run the adoption under test, and W2-81 itself;\n  - the writer's own ticket is not measured.\n- **KPIs, success:**\n  - at least 10 hidden questions per repository, with gold sources and forbidden citations, in W2-81's stated form;\n  - at least one hidden planted-problem variant per kind, which the visible builders do not produce, so that an adoption tuned to the visible generator is caught;\n  - nothing hidden written outside the hidden folder;\n  - the measured sessions are refused its reads by the guard.\n- **KPIs, failure:**\n  - a hidden question or answer readable by a measured session by any route an honest agent takes;\n  - a question whose gold answer the built repository does not hold.\n\n",
      "tokens": 200
    },
    {
      "id": "DEC-1144",
      "path": "docs/DECISION_REGISTER.md",
      "text": "    parked in Wave 3 (W3-P33, W3-P34).\n  - (6) **P1-F (a): the W2-81 runner's `--sets-root <root>`** goes inside W2-93 (`DAEO-6y0x`): its paths gain\n    `tests/acceptance/W2-81/w2_81_run.py` and `tests/acceptance/W2-81/test_w2_81_runner.py`, for the independent test designer who writes\n    `validate_hidden.py`, with one KPI line: the runner and the validator take `--sets-root <root>`. Answers DEC-1143 (4)'s open point.\n  - (7) **P1-G (a): a reviewer's read-only probes are allowed in the quiet hours**, in its own TMPDIR (outside the repository and the runs\n    folders), touching neither the repository nor the evaluation sets; the two-refusal stop (DEC-1142 (9)) still holds. Into the briefs.\n  - (8) **Read and accepted (delegated P2s, DEC-1112 (3)):** W2-124's P2 (b) and P3 (`fe7bd01ae`); W2-115's PK-5 (c), deferred with\n    W2-115b (`33b5651eb`).\n- **Basis:** the owner's message of 2026-11-12 ~14:10 answering the CTO's seven P1 packages.\n\n",
      "tokens": 238
    },
    {
      "id": "DEC-1143",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  - (2) **C1:** EXAMIN's copy is `~/gov-os-workbench/examin`, after one new commit there of its uncommitted files, made on the owner's\n    word: `0a82082495f52df068c3c6b518969b419f02fe95` (2026-11-12 10:45 UTC; 42 files: `.gitignore` and `CLAUDE.md` modified, the 40\n    untracked added; the other four \"modified\" files differed from HEAD only in CRLF line endings, which the copy's `core.autocrlf=input`\n    normalises, so they match the commit and are unchanged on disk). The original `~/EXAMIN APP` stays untouched (`a7cf346c28d7`, its\n    46 uncommitted files as they were). That commit is the one the set pins and the one W2-27 (the adoption on the copy) uses.\n  - (3) **C2:** the launch clone of the copy at that commit with one scaffold commit (no code). **C3:** 20 questions. **C4:** the release\n    step kept; the owner reads the visible half before releasing it. **C5:** 10 per repository and 13 variants. **C7:** `measures` by roles.\n  - (4) **C6:** the writer writes the data only; the validator (`validate_hidden.py`, already in W2-93's paths) is written by an\n",
      "tokens": 269
    },
    {
      "id": "203acd3cefefdcd0d362ee77",
      "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md",
      "text": "## 7. Output (into `out/` only)\n- `out/set/<repository>.yaml` for each of the six repositories, and `out/set/variants.yaml`, in the README's forms. Nothing\n  else in `out/set/`. No other folder, no `validate_hidden.py`.\n- `out/conflicts.md` only when item 6 or section 9 applies: names and path classes, never content.\n\n",
      "tokens": 80
    },
    {
      "id": "82e1f5289f9ec66111e7dc81",
      "path": "governance/project/orchestration/packages/P1-W2-81-LOOP.md",
      "text": "## 2. What happened (review 5, on `165d3057146a`)\n- **F1 (fails open):** a forbidden citation that names no file of the built repository (a typo in a literal path, a\n  path written as a YAML scalar, an unquoted `{name}`, `{stale}.bak`) is still dropped silently; end to end, NOT_READY\n  (stacked share 95) became READY.\n- **F2 (fails open):** READY does not require the measurement half's planted-problem variants (none, an empty list or\n  one kind only still gave READY).\n- **F3 (low):** with pytest's `-l` a failing case prints synthetic secret values (not with the README's `-q`).\n- All three are reachable only when someone writes the hidden half (W2-93 authors it; nothing reads one today).\n\n",
      "tokens": 175
    },
    {
      "id": "e2f95944dfbf0265111efefb",
      "path": "governance/project/path-map.yaml",
      "text": "  # examin, EXAMIN's question set (W2-94; DEC-957, DEC-828 items 3-4, DEC-1130 (3)): 20 questions about the owner's copy,\n  # written blind by the walled writer (DEC-1101 (3); brief EXAMIN-writer), kept under the sets root (the measure's\n  # --sets-root), never in a tree. The ten visible-half questions are delivered with the hidden half and released to\n  # visible/ by the owner's one copy step; the ten measured ones stay in hidden/. Every role but the orchestrator is\n  # refused the hidden half (as memory-verdict-2); the CTO and leads by sets_root_hidden's fixtures/evaluation/*/hidden/**.\n  examin:\n    visible: [\"fixtures/evaluation/examin/visible/**\"]\n    hidden: [\"fixtures/evaluation/examin/hidden/**\"]\n    measures:\n      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]\n  # adoption-proving-ground, W2-81's held-out half (W2-93; DEC-957, DEC-941, DEC-1130 (3)): hidden questions and\n  # planted-problem variants per synthetic repository, written blind by the walled writer (brief PROVING-GROUND-writer),\n  # kept under the sets root. The visible half is W2-81's own questions folder; the runner reads the hidden half from\n",
      "tokens": 294
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-91 | B | **New (DEC-957, MEMORY-SPEC-MAP gap 1).** Full embeddings: the root files, `governance/**` and `schemas/**` embedded; the hidden half, generated copies and `cli/**` stay out (`DAEO-a3u2`) | implementation | engineer | STANDARD | W2-86 | 30 | CAP-10.a, DEC-957 |\n| W2-92 | B | **New (DEC-957, gaps 2 and 3).** The knowledge graph and the code graph as routes of plain-question retrieval (`DAEO-n0wb`) | implementation | engineer | STANDARD | W2-87, W2-03 | 200 | CAP-12, CAP-13, CAP-18, DEC-957 |\n| W2-93 | B | **New (DEC-957, gap 6).** W2-81's held-out half: hidden questions and planted-problem variants per synthetic repository (`DAEO-6y0x`) | audit | independent-auditor | STANDARD | W2-81, W2-84 | 0 | DEC-941, DEC-828, DEC-957 |\n| W2-94 | B | **New (DEC-957, gap 7).** EXAMIN's question set, a visible and a hidden half, before W2-27; W2-61's KPI 6 moves here (`DAEO-g87r`) | audit | independent-auditor | STANDARD | W2-84 | 0 | DEC-828, DEC-957 |\n",
      "tokens": 242
    },
    {
      "id": "5ccc37c8b57294b0e52521f6",
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "text": "- W2-66c (`DAEO-btcs`, P2, independent-test-designer, open): W2-66's live-map suite pins ACT-SELECT-FIXES-1's lines: the couplings for the settings, the declared checks, t\n**Batch 2**\n- W2-126 (`DAEO-jpr0`, P0, engineer, in progress): A machine-wide vector cache keyed by the text: each text is embedded once on the machine, whatever tree, clone\n- W2-133 (`DAEO-k4wm`, P0, engineer, in progress): A narrowed or gap-starting register item carries its own entry's id (W2-131's follow-up, DEC-1083, re-pin wind\n- W2-93 (`DAEO-6y0x`, P1, independent-test-designer, open): W2-81's held-out half: hidden questions and planted-problem variants per synthetic repository, by an independe\n- W2-98 (`DAEO-wi46`, P1, product-spec, open): The spec-writing skill for product-spec: problem, goals and non-goals, KPIs as observable behaviour each with \n- W2-149 (`DAEO-52ku`, P1, engineer, in progress): The independent sessions' launch script: a walled headless session per job from an approved brief (DEC-1101 (2\n**Batch 3**\n- W2-135 (`DAEO-c4pb`, P0, engineer, in progress): A line over 4,000 characters in a bundle item is sent as its first 4,000, the item marked cut, its lines cited\n",
      "tokens": 294
    },
    {
      "id": "7a85b5d9b9d06b7d9f0d1182",
      "path": "tests/acceptance/W2-81/README.md",
      "text": "## The hidden half's form, for W2-93\n\n**Where it lives.** `fixtures/evaluation/adoption-proving-ground/hidden/` (W2-93's ticket, an independent auditor's).\nThe `fixtures` namespace is one the indexer never reads, and the path map's `evaluation_sets` entry refuses it to\nthe measured sessions (DEC-820 (d), DEC-845, DEC-873).\n\n**What it holds:**\n\n- **`<repository>.yaml`**: a question set in exactly the visible form above, ids `<repository>-h<nn>`, at least 10\n  per repository. Templates name the manifest's facts. The facts each builder records are listed in\n  `w2_81_build.py` (`b.facts(...)`), and a hidden question may also name a variant's paths literally.\n- **`variants.yaml`**: `variants:`, a list of planted-problem variants that the visible builders do not produce, at\n  least one per kind.\n\n**How a variant is described:**\n\n```yaml\nvariants:\n  - id: f1                      # unique in the file; the manifest names it <repository>.<kind>.hidden-<id>\n    repository: rust-workspace  # one of the five, or python-app-clean\n    kind: stale-spec            # stale-spec, superseded-plan, misleading-name, secret, orphaned-test,\n                                # legacy-document or large-file\n",
      "tokens": 300
    },
    {
      "id": "3bf727f9f54a8fd8dcc16fcf",
      "path": "tests/acceptance/W2-81/w2_81_build.py",
      "text": "\n\n# --------------------------------------------------------------------------\n# The hidden half's planted-problem variants (README, \"The hidden half\"): built here, described there\n# --------------------------------------------------------------------------\n\n_PLACE = re.compile(r\"\\{(commit|fact):([A-Za-z0-9_-]+)\\}\")\nVARIANT_KEYS = (\"id\", \"repository\", \"kind\", \"variant\", \"paths\", \"steps\", \"evidence\")\n\n\n",
      "tokens": 102
    },
    {
      "id": "DAEO-5x4l",
      "path": ".tickets/DAEO-5x4l.md",
      "text": "---\nid: DAEO-5x4l\nstatus: closed\ndeps: [DAEO-t6hf, DAEO-jozo]\nlinks: []\ncreated: 2026-09-30T22:49:58Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W1-21\ntags: [wave-1, implementation, full]\nwbs_id: W1-21\ntitle: gov retrieve with completeness\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-t6hf\n- DAEO-jozo\nallowed_paths:\n- src/gov/retrieval/retrieve*\n- src/gov/retrieval/bundle*\n- src/gov/retrieve/**\n- tests/unit/retrieve/**\n- template/governance/kernel/checks/retrieval-regression*\nkpis:\n  success:\n  - Paging with continuation; facets; dedup by chunk hash; authority/current filter drops superseded and must-not-cite records; one rerank over the merged set [CAP-16.a, CAP-18.a, CAP-51.b]\n  - Every bundle cites by id and sha256 and carries one stopping reason from the fixed list [CAP-55.a]\n  - RETR-A-04 and RETR-X-02 dev runs produce multi-batch bundles [CAP-16.b]\n  - A child hit is expanded to its parent span only within the bundle budget, and the bundle names each expansion (DEC-091) [CAP-18.b]\n  - 'Registers the retrieval-regression family check: the dev query set meets its recorded hit@5 and forbidden-citation baselines [CAP-38.b]'\n",
      "tokens": 299
    },
    {
      "id": "DEC-1019",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1019 \u2014 W2-92's P-W2-92-5 (a): with no readable record graph, no evidence from a record file (delegated)\n- **Status:** ACCEPTED (orchestrator, delegated: a P2 inside W2-92's approved KPIs that only makes the citation guard fail closed; the lead's recommendation; confidence medium-high) \u00b7 **Under:** DEC-1006, DEC-423, DEC-957, DEC-1010\n- **Decision:** P-W2-92-5 (a): DEC-1006's P-1 (a) stays (a missing or unreadable record graph fails only the record and closure routes), and when the record graph cannot be read, retrieval cites no evidence from a record file and says so in the closure facet, so a superseded or must-not-cite record is never cited as current (DEC-423). W1-21's `test_without_a_record_graph_no_superseded_record_is_cited_as_current` and W2-92's f3 must both pass; W1-21's test is not changed. Option (b) (revert P-1) is kept as the fallback if (a) cannot pass both. Classification: ordinary work yes; consequence: fails open (closed by this fix). One engineer batch in `retrieve.py`, then the rebuild, `gov check` and the scoped run; no re-measure (the change acts only with no record graph).\n\n| Version | Date | Change |\n|---|---|---|\n",
      "tokens": 291
    },
    {
      "id": "57c671124ad222e894584423",
      "path": "docs/DECISION_REGISTER.md",
      "text": "## 101. Delegated decisions on W1-21's packages DP-0, DP-1, DP-3, DP-6, DP-8 and DP-9 (register v0.101, appended by the W1 orchestrator on branch `w1/integrate`)\n\nDecided by the orchestrator on 2026-10-06 under DEC-220 and DEC-416, on six of the ten packages the W1-21\n(`DAEO-5x4l`) ticket lead returned after the test design (119 cases, all red, no engineer started). Each is\nreversible at low cost before W1-22 starts, and the designer's, the lead's and the orchestrator's recommendations\nagree. DP-2 (what a batch, a round and a continuation are, with the numbers), DP-4 (what marks a record superseded\nor must-not-cite), DP-5 (when a failure or lesson record matches a ticket's scope) and DP-7 (the retrieval-regression\ncheck's baselines) are the owner's. The owner was told on 2026-10-06, including that the lead ranked DP-0 and DP-1 as\nP1.\n\n",
      "tokens": 212
    },
    {
      "id": "DEC-423",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-423 \u2014 W1-21 DP-4: superseded from the store; must-not-cite is a closed status list; a file the store could not load is read by its frontmatter\n- **Status:** ACCEPTED (owner, 2026-10-06) \u00b7 **Basis:** W1-21 package DP-4 option (a) \u00b7 **Under:** DEC-329, CAP-51.b\n- **Decision:**\n  - Superseded comes from the store: status `SUPERSEDED`, or being the target of a supersedes edge.\n  - Must-not-cite is a closed status list: `DEPRECATED`, `REJECTED` and `WITHDRAWN`.\n  - A cited file the store could not load is read by its frontmatter.\n  - Dropped records are listed in the bundle.\n\n",
      "tokens": 147
    },
    {
      "id": "e0f11bbdeb7217e3a0fa3e2d",
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "text": "| 3 | Retrieval stays on while agents edit | After an edit to one tracked file, unchanged files are still served and the changed file is listed as a gap; a stale index is named in `dropped` and in the brief [B rec. 1, rec. 2] | Any edit switches the whole index off, and `gov context` hides the loss [B F2] | W2-06, its KPIs widened to uncommitted edits [B F2] | Phase 4 |\n| 4 | Superseded decisions are marked and kept out | Each register chunk carries its own entry's id, and the must-not-cite filter keys on it. B's question Q05 is the test [B rec. 4] | Every register chunk carries the id DEC-812, and DEC-049, which is superseded, is served at rank 4 (fails open) [B F4] | W2-32, or W2-03 widened [B F4] | Phase 4 |\n",
      "tokens": 181
    },
    {
      "id": "WAVE-2-REVISED-PLAN",
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "text": "### 4.4 Keystone 4: memory, in the owner's order (DEC-828)\n\n| Order | What | Ticket | Widened by this plan | Gates |\n|---|---|---|---|---|\n| 1 | Correct records: each decision its own record, correct ids, supersession honoured | W2-02 (resume), W2-03 (close), W2-55 | W2-02: the full validator, by calling check-jsonschema (lens G R2 (a)), with lens G's planted ticket as a case. W2-55: the must-not-cite filter keyed on each chunk's own entry id (lens B F4; question Q05 the test) | \u00a76 rows 2, 4: the copy |\n| 2 | The index on during edits | W2-05 (resume), then W2-06 | W2-06: lens B F2 (uncommitted edits); the kernel template embedded, and tests given their own facet (\u00a76 row 6, row W2-L253 raised); content-based chunk ids (\u00a76 row 13) | \u00a76 rows 3, 6: the copy |\n| 3 | Bounded context packets carrying real text | W2-04 | Lens B rec. 1: each of lens B's ten packets within 6,000 tokens, with each mandatory decision's text, and `ok: false` over the ceiling; the packet names the register commit it used | \u00a76 rows 1, 2: the copy |\n",
      "tokens": 259
    },
    {
      "id": "ec2e7c8362f1b23ae5a7e0a7",
      "path": "docs/research/D4B-link-census.md",
      "text": "## 2. Drift: decisions an agent would retrieve as current although the register says they changed\n**Current** is the brief's sense: status ACCEPTED, not in `not_current` (no SUPERSEDED status, no SUPERSEDES edge,\nno must-not-cite status). **Stated** means an entry's labelled or free-text statement, the entry's own status line, or\nARCHIVE-SUPERSEDED \u00a7A.\n\n| | Decisions stated | of them current | whole (ids alone) | no hint in its own entry | its register chunks / chunks with no hint |\n|---|---:|---:|---:|---:|---:|\n| superseded (whole or in part) | 57 | **43** | 1 (DEC-140) | **8** | 114 / **68** |\n| amended (not superseded) | 205 | **196** (172 amended only) | 27 | **87** | 682 / **516** |\n| **either** | | **215** | | **87** | 722 / **536** |\n\n- **Already not current (correctly): 9.** DEC-038, DEC-048, DEC-049, DEC-636, DEC-798, DEC-869, DEC-875 and DEC-876\n  by status (8); DEC-960 by edge (DEC-038 and DEC-048 also by edge).\n- **Stated changed but PROPOSED, so not ACCEPTED, yet not dropped either: 13 more.** DEC-002, -005, -007, -024, -034,\n  -037, -040, -043, -044, -045, -047, -056, -062 (for example, DEC-002/043/045/047 \"superseded by DEC-058/064\").\n",
      "tokens": 293
    },
    {
      "id": "68eb3894beeacf14c694a896",
      "path": "src/gov/retrieval/authority.py",
      "text": "def register_entries_of(known: list[dict], edges: list[dict], root: Path) -> Callable[[str, int], dict | None]:\n    \"\"\"The mapping of a register chunk to its entry, built once over the store's records.\n\n    ``known`` is the store's records (``gov.records.records``), ``edges`` its edges (only SUPERSEDES edges are\n    read), ``root`` the project root the register file is read from. The returned function takes a chunk's ``path``\n    and ``start_line`` (1-based) and gives the entry whose span holds that line, as ``{\"id\", \"type\", \"status\",\n    \"current\", \"reason\", \"start_line\", \"end_line\"}``, or None: for a line before the first entry or between two\n    entries' spans, and for a file that is not the register.\n\n    An entry's lines are where its stored span stands in the register file read from ``root``: its heading line\n    and as many lines as its span has. An entry is not current (``current`` False, ``reason`` given) when its status\n    is SUPERSEDED or it is the target of a SUPERSEDES edge (``reason`` SUPERSEDED), or its status is must-not-cite\n    (``reason`` the status; DEC-423). Deterministic: the same records, edges and file give the same answers.\n    \"\"\"\n",
      "tokens": 294
    },
    {
      "id": "0130867b577a287077f1fca7",
      "path": "src/gov/retrieval/retrieve.py",
      "text": "\"\"\"``gov retrieve``: one cited evidence bundle with one stopping reason (W1-21; DEC-080, DEC-419, DEC-422\u2013425).\n\n``retrieve`` asks the lexical and the semantic route, closes over a ticket, ids or the records the question names\n(``graph_route``) with ``gov.closure``, asks the code index for the symbols it names (``code_route``), merges them\nby chunk hash, drops what the store says is superseded or must-not-cite (DEC-329, G-19, DEC-423), reranks\nthe rest once (DP-9) and expands a child hit to its parent within the bundle budget (DEC-091, DP-3). It only\nreads (DEC-322).\n\nPaging (DEC-422): batches beyond the first, rounds scaled by radius, a stateless continuation token.\nMust-not-cite (DEC-423): DEPRECATED, REJECTED, WITHDRAWN; frontmatter check for files not in the store.\nFailure/lesson ahead (DEC-424): failure and lesson records in the ticket's closure come ahead of other evidence.\nThe candidate pool (W2-32 S11): ``retrieval.yaml``'s ``pool:`` settings (``gov.retrieval.pool``), each absent or 0\ntoday's path: the routes' depth per search, the meaning route uncut, one rerank of the first n fused (the pages cut\n",
      "tokens": 281
    }
  ],
  "supplementary_query": "W2-81's held-out half: hidden questions and planted-problem variants per synthetic repository, by an independent session\nAt least 10 hidden questions per synthetic repository, each with its gold answer, gold sources and forbidden citations, in the form W2-81's README states Verify: `validate_hidden.py` on a planted stand-in hidden folder prints, for each repository, a question count of 10 or more and exits 0; a planted folder with 9 for one repository is refused; each planted question holds the fields the README states [DEC-957, DEC-941, DEC-828]\nAt least one hidden planted-problem variant per kind that the visible builders do not produce, so an adoption tuned to the visible generator is caught Verify: `validate_hidden.py` on a planted stand-in set prints, for each kind of planted problem the visible builders do not produce, the number of hidden variants per repository; a planted set missing one kind is refused [DEC-941]\nWritten by a session independent of the sessions it measures; nothing hidden written outside the hidden folder; no question or answer quoted in a commit message, a return, a log or a ticket note Verify: the delivery's run record names the walled writer's run (`20261112T185824Z-adoption-proving-ground-r1`) and its launch log the approved brief's sha256 (the sets root is outside git, so no commit carries it); `validate_hidden.py --sets-root` finds the hidden files only under the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845, DEC-873]\nEvery gold answer is held by the repository the builder builds, checked on a built copy Verify: `validate_hidden.py` on a built copy of a planted stand-in repository: every gold answer is found in it; a planted answer the built copy does not hold is refused naming its id [DEC-828]\nThe hidden half proves its own data valid with an automatic check, `validate_hidden.py`, written by the ticket's independent test designer (never the walled writer), run by the CTO on the delivered hidden half before it is used, printing counts and ids only, and recorded: every forbidden (\"must not cite\") file names a file of the repository the builder builds, checked on a built copy; every kind of planted problem the visible generator does not produce has at least one hidden variant per repository; anything it cannot read refuses (fail closed); W2-81's files are not touched Verify: planted stand-in cases: a must-not-cite file absent from the built copy refuses, a kind with no variant refuses, an unreadable file refuses (non-zero exit); `git diff` shows W2-81's files untouched except the two paths DEC-1144 (6) gives this ticket (`--sets-root`); the delivered hidden half has a recorded run of the check (counts and ids only) [DEC-1010 item 4]\nThe W2-81 runner (`tests/acceptance/W2-81/w2_81_run.py`) and `validate_hidden.py` each take `--sets-root <root>` and find the hidden half under it, so neither the CTO nor a session names the hidden folder on a command line; the runner's `--hidden <folder>` stays for a direct call; both written by the independent test designer Verify: a planted stand-in sets root holding a stand-in hidden half: the runner and `validate_hidden.py` given only `--sets-root` find and read it, and a root without one exits non-zero naming the missing folder [DEC-1144 (6), DEC-1143 (4)]\nA hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's path map) are refused or find it 0 times\nA question whose gold answer the built repository does not hold. Verify: `validate_hidden.py` on a planted stand-in question whose gold answer the built copy does not hold exits non-zero and names the question id",
  "further_batch": [
    {
      "id": "78cf96fc380b4e9312a4513d",
      "path": "src/gov/retrieval/retrieve.py"
    },
    {
      "id": "56efff59508fe160db898731",
      "path": "src/gov/retrieval/retrieve_baseline.yaml"
    },
    {
      "id": "1851498b69dfae8435323bb5",
      "path": "tests/acceptance/W1-21/README.md"
    },
    {
      "id": "28f45c8907f43f32cad4a9f1",
      "path": "tests/acceptance/W1-21/README.md"
    },
    {
      "id": "702afc32642aff0503674a3e",
      "path": "tests/acceptance/W1-21/README.md"
    },
    {
      "id": "0ad144273e738c249ed43706",
      "path": "tests/acceptance/W1-21/test_w1_21_authority.py"
    },
    {
      "id": "972b352f01471637f820a7ff",
      "path": "tests/acceptance/W1-21/test_w1_21_authority.py"
    },
    {
      "id": "e3a22fc16dd6fc4e101b5861",
      "path": "tests/acceptance/W1-21/test_w1_21_authority.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "ba83ae15d79bd281f4078981",
          "path": "docs/probes/DAEO-l78m/PR-DAEO-l78m-moderated.md"
        },
        {
          "id": "68f7ae754fe56ed696a0246c",
          "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md"
        },
        {
          "id": "119285c8268c107080505f6f",
          "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "DEC-1144",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1143",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "203acd3cefefdcd0d362ee77",
          "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md"
        },
        {
          "id": "82e1f5289f9ec66111e7dc81",
          "path": "governance/project/orchestration/packages/P1-W2-81-LOOP.md"
        },
        {
          "id": "e2f95944dfbf0265111efefb",
          "path": "governance/project/path-map.yaml"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "5ccc37c8b57294b0e52521f6",
          "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md"
        },
        {
          "id": "7a85b5d9b9d06b7d9f0d1182",
          "path": "tests/acceptance/W2-81/README.md"
        },
        {
          "id": "3bf727f9f54a8fd8dcc16fcf",
          "path": "tests/acceptance/W2-81/w2_81_build.py"
        },
        {
          "id": "DAEO-5x4l",
          "path": ".tickets/DAEO-5x4l.md"
        },
        {
          "id": "DEC-1019",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "57c671124ad222e894584423",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-423",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "e0f11bbdeb7217e3a0fa3e2d",
          "path": "docs/assessment/2026-10/SYNTHESIS.md"
        },
        {
          "id": "WAVE-2-REVISED-PLAN",
          "path": "docs/plan/WAVE_2_REVISED_PLAN.md"
        },
        {
          "id": "ec2e7c8362f1b23ae5a7e0a7",
          "path": "docs/research/D4B-link-census.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "68eb3894beeacf14c694a896",
          "path": "src/gov/retrieval/authority.py"
        },
        {
          "id": "0130867b577a287077f1fca7",
          "path": "src/gov/retrieval/retrieve.py"
        },
        {
          "id": "78cf96fc380b4e9312a4513d",
          "path": "src/gov/retrieval/retrieve.py"
        },
        {
          "id": "56efff59508fe160db898731",
          "path": "src/gov/retrieval/retrieve_baseline.yaml"
        },
        {
          "id": "1851498b69dfae8435323bb5",
          "path": "tests/acceptance/W1-21/README.md"
        },
        {
          "id": "28f45c8907f43f32cad4a9f1",
          "path": "tests/acceptance/W1-21/README.md"
        },
        {
          "id": "702afc32642aff0503674a3e",
          "path": "tests/acceptance/W1-21/README.md"
        },
        {
          "id": "0ad144273e738c249ed43706",
          "path": "tests/acceptance/W1-21/test_w1_21_authority.py"
        },
        {
          "id": "972b352f01471637f820a7ff",
          "path": "tests/acceptance/W1-21/test_w1_21_authority.py"
        },
        {
          "id": "e3a22fc16dd6fc4e101b5861",
          "path": "tests/acceptance/W1-21/test_w1_21_authority.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0ad144273e738c249ed43706",
      "reason": "budget exceeded"
    },
    {
      "id": "1851498b69dfae8435323bb5",
      "reason": "budget exceeded"
    },
    {
      "id": "28f45c8907f43f32cad4a9f1",
      "reason": "budget exceeded"
    },
    {
      "id": "56efff59508fe160db898731",
      "reason": "budget exceeded"
    },
    {
      "id": "702afc32642aff0503674a3e",
      "reason": "budget exceeded"
    },
    {
      "id": "78cf96fc380b4e9312a4513d",
      "reason": "budget exceeded"
    },
    {
      "id": "972b352f01471637f820a7ff",
      "reason": "budget exceeded"
    },
    {
      "id": "e3a22fc16dd6fc4e101b5861",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-6y0x): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 15996,
  "budget": {
    "limit": 16000,
    "used": 15996
  },
  "left_out": {
    "count": 8,
    "superseded": [
      "DEC-038",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "806a609842df437475874ce408458c6d69434ada6296119fddc821703e6d034f"
}
```
