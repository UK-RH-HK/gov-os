Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: W2-93 (DAEO-6y0x), the narrow independent check (independent-auditor, read-only, one round)

You are a fresh, read-only reviewer (independent-auditor). You write nothing in any tree: your whole result is your last message, which the lead commits as the probe record. Class C2, profile STANDARD.

## What you probe
- **Head:** `0a693c61aecb4c985dde0cb2a50d5ba18908a488` of `w2/W2-93` in `/home/usain/gov-os-worktrees/W2-93`; the change is `git diff a7b36bcfd98a 0a693c61aecb` (9 files):
  - `fixtures/evaluation/adoption-proving-ground/validate_hidden.py` (new) and `--sets-root` in `tests/acceptance/W2-81/w2_81_run.py` with its cases in `tests/acceptance/W2-81/test_w2_81_runner.py`: commit `555169eb401a`, independent test designer session `b17b46d4-cc7a-4953-9d7a-565fc1a30089`;
  - `tests/acceptance/W2-93/**`: commits `ceffc1d95633` (session `de0923dd-e605-409f-891a-e6c269a2a582`) and `8d342fbcf775` (session `2270289a-91f2-456b-a48a-32be9ffb474b`), merged by the lead as `7add172a7` and `0a693c61a`.
- **The ticket:** `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6y0x.md` (its KPI lines S1-S6, F1, F2 and their Verify). The form is W2-81's README (`tests/acceptance/W2-81/README.md`, "The hidden half's form, for W2-93"). The interface the lead fixed for both designers is below. Context: the real hidden half (60 questions, 13 variants) was written blind by a walled writer under the brief `governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md`, kept outside git under the evaluation sets' root; the CTO runs `validate_hidden.py --sets-root` on it himself after landing.
- **Already run by the lead:** `gov accept W2-93`: pass, 133 passed, 0 failed, all eight lines; the scoped verification is running.

## What to judge (narrow: this change only)
1. Does `validate_hidden.py` do what S1, S2, S4, S5, S6 and F2 say, to the interface? In particular: can a hidden half that breaks a line (fewer than 10 questions, a missing field, a gold source line not at the built HEAD, a forbidden citation naming no file of the built copy, a required kind with no variant) pass with exit 0? Is the S2 rule computed from the visible build, not a fixed list?
2. **Fail closed and never shown:** can anything it cannot read pass? Can any output line (a refusal, an exception's message, a YAML parser's message with a snippet, a traceback) carry a question's text, an answer, a template, a fact's value or a secret? Does it write anything outside its own temporary folder, and remove that folder pass or fail?
3. `w2_81_run.py --sets-root`: found and read exactly as `--hidden`; a root without the folder refused (exit 2, naming it) in every mode before anything is built; both together refused; `--hidden` unchanged; nothing else in W2-81's behaviour changed (DEC-1010 item 4: W2-81's files untouched but these two).
4. Do the acceptance tests check each KPI line's Verify as written (form only: counts, fields, sources exist), on planted stand-ins only, with no case that passes vacuously? F1: do the guard cases really exercise a measured role's read, grep and `git log` against the real path map's `adoption-proving-ground` entry?
5. The lead's two decisions within the interface: the S2 reading (per repository, each core kind the visible build lacks; each of the seven kinds at least once where not visibly planted; no variant in the clean twin), and `forbidden` optional (absent = none, as W2-81's visible half has it in 15 of 61). Say if either fails a KPI line as written.

## Walls (hard)
- **Never open, list, grep or print anything under `~/gov-os-eval` or any `hidden/` folder.** Probe on planted stand-ins you write in your sandbox's `$TMPDIR` only (`tests/acceptance/W2-93/w2_93_standin.py` and `tests/acceptance/W2-81/w2_81_standin.write_hidden_stand_in` make them). Your read-only probes may run in your own `$TMPDIR` (DEC-1144 (7)).
- Never quote a question or an answer, stand-in or otherwise.
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR="$TMPDIR" PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-93/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`. A resource gate's refusal is a wait (DEC-1146). Refused twice for the same action: stop and say so; never work around a refusal (DEC-1142 (9)). No `gov retrieve`, no `gov context` in the sandbox: Read and Grep, then search again once in other words.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.


## Your return (your last message; the lead commits it as `docs/probes/DAEO-6y0x/PR-DAEO-6y0x.md`)
1. The front matter as you would have it (the lead fills the two session ids it knows):
```
---
type: probe
task: DAEO-6y0x
reviewer_session: <your session id if you know it, else "see launch log">
implementer_session: b17b46d4-cc7a-4953-9d7a-565fc1a30089
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass|fail
probed_commit: 0a693c61aecb4c985dde0cb2a50d5ba18908a488
---
```
2. A summary: what you read, what you ran (commands and counts), each KPI line's judgement with its evidence (file:line).
3. Every finding with an id (F1, F2 ... in your own numbering, prefix `R-`), scope (in|out), the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`, and where.
4. The fenced verdict block, exactly in this form, one entry per KPI line (`S1` ... `S6`, `F1`, `F2`):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

## Appendix: the interface the lead fixed for both designers (batch 2 changed one point: `forbidden` is optional; absent = none, present = a list of non-empty strings)
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
