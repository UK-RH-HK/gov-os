# Batch 3 of 3: the scorer, the visible question half, the runner and the README (W2-81, DAEO-l78m)

Your batch 2 is committed and checked. Every standing rule of your first brief still holds, word for word: the sandbox, Policy 2 (c) and (d), the guard's command forms, refused twice for the same call stop and say so, the disk share, row W2-L423's rule, `gov retrieve` from the integration branch's store only, the hooks check before your commit, the trailers, the twelve fields first. **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src` set **per command** (never in a session's `--settings` env).

## The lead's notes on batch 2

- **Checked:** `2dd40a4e530b` and `3cc35cd5cca1`, their trailers and `Implements:` ids; `gitleaks` 0 on the suite; the tripwire shows changes in this worktree only under `tests/acceptance/W2-81/`.
- **Time:** the suite took 48 to 67 s alone on the shared machine after batch 2, against the 120 s limit "alone and under the close's parallel load". Batch 3 must not push it near the limit: share the built repositories across cases (session-scoped builds, built once per process), keep large files and question runs small in the self-tests, and keep the whole suite's plain run under about 80 s on this machine. Report the plain and `-n auto` timings for the whole suite.
- **Retrieval:** it failed twice from the sandbox (network). Do not try it again this batch; read named files (`gov retrieve --help` and its JSON form are fine to read from the code: `src/gov/retrieval/` is the critical chain's, read only).
- **The runner and the hidden half:** the runner reads the hidden half only from the path it is given or the default hidden folder when that exists; the self-tests always pass a stand-in folder in their temporary folder and never the real one.

## The behaviour to build and test (the KPI lines are the authority)

**The scorer.**
- It reports **both figures per repository, never one without the other**: **hit@5** against CAP-10's floor of 85, and **the share of questions whose stacked context holds all their evidence** against the 99 % target (DEC-833, as the KPI line states it). Keep each threshold a single named constant, cited to its decision, and say in the README that DEC-957 sets memory's target at 95 % with 85 % the floor, so the owner may later change the second constant; you do not decide that.
- **A forbidden citation in the top five counts as a miss** for that question (in both figures).
- **It prints scores and question ids only, never a hidden question or answer** (nor a visible one's text in its report: ids only).
- Its result feeds the judge's READY: **a scorer stand-in at 84 on hit@5, or one reporting a single figure, is NOT_READY** (KPI line 8); a missing figure is not met.

**The visible (development) question half**, written by you: **at least 10 questions per repository**, each with its **gold sources** and its **forbidden citations** (the stale spec, the superseded plan, and any other planted source a correct answer must not cite). They live under `tests/acceptance/W2-81/questions/` (the path map's `evaluation_sets` entry will name `tests/acceptance/W2-81/questions/**` as the visible half). Because names, places and wording are seeded, a question's gold sources and forbidden citations refer to the manifest (by planted-problem id and role, or by a builder-stable path), so they resolve to real paths for any seed. A self-test shows, for the default seed and for at least one other seed, that every gold source exists in the built repository and holds the answer's evidence, and every forbidden citation is a planted stale or superseded source. Cover different kinds of question per repository (where a behaviour is specified, which spec governs, which plan is current, what a module does, which test covers what, where a configuration lives), not ten of one kind.

**The hidden (measurement) half's form, for W2-93**, stated in the README: its folder `fixtures/evaluation/adoption-proving-ground/hidden/` (one file per repository, in the visible half's form), **plus planted-problem variants** the runner builds when the hidden half is present (at least one per kind that the visible builders do not produce: say exactly how a variant is described so your builders build it, and which builder hooks it uses). The runner reads the hidden half only when it is present; the scorer and the report name hidden questions by id only. **Your self-tests never read that folder**: they use a stand-in hidden set they write in their temporary folder (a self-test checks that a stand-in hidden question's text and answer appear in no output, report or log of the runner and the scorer).

**The runner: one command for the real run, not collected as a test.**
- One command (state it in the README), taking a folder by literal path (a temporary folder, or `~/gov-os-runs/W2-81/` by DEC-728), and a seed (a fresh one when none is given, recorded).
- It builds the five repositories (and the clean variant) under that folder, with the manifests beside them, outside each repository.
- It then either runs the built adoption stages and `gov retrieve` on each repository (with the `gov` command it is given, so the orchestrator chooses the pinned release or a tree's `src/`), or reads the outputs of an adoption a launched session ran there (a mode that only reads).
- **The `gov close` step:** in each synthetic repository, a ticket closes with `gov close` at exit 0 on a pinned release (W2-16's numbered, frozen release; DEC-953, DEC-954 Q8c). Build the runner's step for it (it takes the pinned `gov` to use; it records each repository's exit code; a non-zero exit, or the step not run, is NOT_READY naming it). Its real run is the orchestrator's once W2-16's release is closed: **test it with a stand-in `gov`** (a small script in the temporary folder that exits 0, and one that exits non-zero).
- It writes the report as JSON and markdown **in that folder**: per repository, per planted problem (the judge's result with its evidence), the controls, both figures, the seed, NOT_BUILT stages, the `gov close` results, and the verdict.
- **It writes nothing in this repository**, and refuses a folder inside this repository or inside any git work tree it did not build. It never reads the workbench and never uses `GOV_DEV_TIERS`.
- The secret's value is in no report, log or output of the runner (checked in memory).

Self-tests for the runner use stand-ins for the adoption and for `gov retrieve` (a stand-in command that writes adoption outputs of a known quality and answers questions from a known ranking): READY with all handled and both figures met; NOT_READY with each failure; the report's fields; nothing written outside the given folder (snapshot the given folder's parent and this worktree's `git status --porcelain` around the run); a folder inside this repository refused. Keep them under 120 s alone and fast under `-n auto`, none skipped.

**The README, finished:** the five shapes and the clean variant; each planted kind with its shapes, its correct handling and the record and field that shows it, and what is NOT_BUILT today; the controls; the seed; the manifest; the secret; the judge (verdicts, fail-closed rules, the mutants list); the scorer (both figures, thresholds and their decisions, forbidden citations); the visible questions; the hidden half's form for W2-93; the runner's one command and its report; how W2-88 reads the builders and the question sets read-only (the import form, what it may call); **each KPI success and failure line of the ticket mapped to its tests**; and why there is no red step here (no implementation: the self-tests pass when the proving ground is right).

Run the whole suite to the end, plain and with `-n auto`, and time both (under 120 s each); run the collect-only check once and quote its last line; `gitleaks` on your suite's files, the finding count only. Commit with your trailers (`Implements:` with the ids this batch implements, for example `DEC-833, DEC-845, DEC-873, DEC-820, DEC-728, DEC-953, DEC-954, DEC-957, CAP-10`, each checked to exist).

## Return

Your commit's 12-digit hash and trailers; files; the suite's test count and both timings; collect-only line; gitleaks count; questions per repository; the runner's one command; the hidden half's form in two lines; what W2-88 and W2-93 may read and in what form; retrieval used; guard refusals; temp folder size; any package.

Your last message has the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.

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
