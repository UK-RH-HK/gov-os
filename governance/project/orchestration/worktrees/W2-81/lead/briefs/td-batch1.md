# Brief: independent test designer, W2-81 (DAEO-l78m), batch 1 of 3

You are a fresh independent test designer (MR-3). Ticket: `DAEO-l78m` (`W2-81`, "the adoption proving ground"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-81` on branch `w2/W2-81`. There is no tests worktree and no engineer in this ticket: the proving ground itself is the deliverable, and it is test code you write (builders, manifest, judge, scorer, runner, the visible question half, the README and the self-tests), all under `tests/acceptance/W2-81/`.

This is **batch 1 of 3**. Each batch is about 90 minutes and ends with a commit and your return. The lead resumes you (this same session) for batches 2 and 3. Design batch 1 with the whole plan below in mind, but build and commit only batch 1's part.

## Step 0, before any work: the sandbox check (report it first in your return)

1. `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l78m','w').write('x')"` must FAIL.
2. `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.

If (1) wrote the file or (2) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-l78m`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-81` and `w2/W2-81`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src` set **per command** (never in a session's `--settings` env).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **Write only under `tests/acceptance/W2-81/`** (and your temporary folders). Nothing else in this repository. Never write `.gov-runtime/**`.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository, its worktrees or the dev tiers). Every repository the suite needs is built from scratch, file by file and commit by commit, in a temporary folder.
- **Protected material (DEC-820):** never read the held-out qualification material's contents and never print a secret; never read or name the qualification oracle. Never read, list or write `~/gov-os-workbench`. Never use `GOV_DEV_TIERS`. Run no glob, search or listing over `governance/project/` or `.claude/` (name files one by one). Never read `.claude/settings.json`.
- **Policy 2 (DEC-820), reads open, writes closed.** You may read the whole repository, the committed context and git history. Refused to you: (a) secrets and keys, never printed; (b) the held-out qualification material's contents; **(c) the counterpart's work on this ticket: you, the test designer, never read this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests); this ticket has no implementation, so in practice nothing beyond your own files is refused, but the rule holds; (d) the hidden half of any evaluation set, by whoever is measured by it: W2-81 is measured by the adoption proving ground's hidden half, so you never read `fixtures/evaluation/adoption-proving-ground/hidden/**` (it does not exist yet) or any other evaluation set's hidden part.**
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and list it in your return.
- **The guard's command forms (DEC-941 item 4a):** the guard refuses a shell command it cannot read whole. No shell variable as a write target (`> "$OUT/x"`, `mkdir -p $D/t`, `sed -i` on a `$VAR` path): use literal paths; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write anything longer as a file with the Write tool (a scratch script under your temporary folder, or a module in your suite) and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Installs:** none. A tool you need and do not have is a P1 package in your return (DEC-957).
- **Row W2-L423's rule (DEC-911):** anywhere under `.gov-runtime/` (which includes your return, which the lead stores there), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". Use 12-digit hashes in your return.
- **Memory used (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **only from the integration branch's store**: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (that store holds `w2/integrate`; for anything newer, `git show w2/integrate:<path>`). Never this worktree's store. Never one giant query or context (DEC-860): a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (the ticket's `allowed_paths` outside `tests/acceptance/`: there are none today), and name in your return any such result you were served. Say in your return which questions you retrieved and whether retrieval worked from your sandbox.
- **Disk budget (DEC-898):** the lead and all workers share 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 15 GB and 700,000**. Use the sandbox's own temporary folder (or `TMPDIR=/tmp/gov-os-lead-W2-81` where it is writable); keep pytest's own retention (never `--basetemp`); remove every built repository, large file and temp tree as soon as it is no longer needed. Measure (`du -s --inodes`, `du -sh`) your temporary folders at the end and give the figures in `evidence`.
- **Commits:** before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your own paths, with the trailers in the final block:
  `git commit -m "<subject>" --trailer "Task: DAEO-l78m" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-941, DEC-936, DEC-930, DEC-833, DEC-820, DEC-911" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  `Implements:` holds only decision ids (`DEC-n`) the register holds or Contract ids (`CAP-n`, `CAP-n.x`) the Contract holds; never a role, a row or any other word. Add the ids your batch really implements (for example `DEC-728`, `DEC-899`, `CAP-44.b`), each checked to exist. After the commit: `git log --oneline -2` and `git status --short` (clean).
- **Nobody runs `gov close`, `gov adopt` or `gov pause`** against this worktree or the main tree. Inside a temporary built repository the suite may run what its cases need, against that repository only.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return.

## What you read

- The ticket file `.tickets/DAEO-l78m.md` (read-only): every KPI success and failure line, `allowed_paths`, `sources`. **The KPI lines are your specification; read them all before you design.**
- The card in `docs/plan/WAVE_2_WBS.md` §2, "#### W2-81", and its companion card just below it ("W2-81's held-out half").
- In `docs/DECISION_REGISTER.md`: DEC-941, DEC-936 (item 3.6, the proving ground), DEC-930, DEC-954 (Q8c, Q9f), DEC-957 (memory's target), DEC-833 (both figures), DEC-820 (d), DEC-845 (the `evaluation_sets` block), DEC-873, DEC-911, DEC-728 (`~/gov-os-runs/`), DEC-899 item 7 (the interim skip guard), DEC-953, DEC-906.
- The Contract `docs/contract/contract.yaml`: CAP-44.b to CAP-44.j (the adoption stages, the verdict, the native layout), CAP-03.a and CAP-03.d (secrets), CAP-10 (hit@5's floor of 85).
- **The adoption stages as built, read only:** `src/gov/adopt/` (`command.py`, `stages.py`, `project.py`, `legacy.py`): where each stage writes its record, the record's fields, what A2 classes, what A3's path map and proposals hold, what A8 records. This is existing code of other tickets (W1-41, W2-52), open to you; it tells you what an adoption's outputs look like today, so the judge reads the real records. A7, A10 lite and the lite verdict (CAP-44.f, CAP-44.h) are **not built yet** (they arrive with W2-52, not merged).
- **The form W1-41's cases use to build a repository at test time:** `tests/acceptance/W1-41/` (`conftest.py`, `w1_41_support.py`), another ticket's tests, open to read. Follow its form: a temporary folder, `git init`, files written and committed one by one, an own-project check so nothing touches this repository.
- How `gov retrieve` answers (`gov retrieve --help`, and its JSON output form), for the runner and the scorer in batch 3.
- `tests/acceptance/conftest.py` and `tests/conftest.py` (what runs for every case).

## The whole plan (three batches; you build batch 1 now)

All files live under `tests/acceptance/W2-81/`. **Only the self-tests are named `test_*.py`**; every support module (builders, manifest, judge, scorer, runner) has a name pytest does not collect and is prefixed `w2_81_` so no module name clashes with another suite's in one pytest process (for example `w2_81_build.py`, not `build.py` or `support.py`). A `conftest.py` puts the folder on `sys.path` as W1-41's does.

1. **Batch 1 (now): the five builders, the planted problems, the controls, the seed and the manifest, and the builders' self-tests.**
2. Batch 2: the judge (FOUND_AND_HANDLED, MISSED, MISHANDLED per planted problem with the evidence it read; CLEAN or FLAGGED per control; NOT_BUILT for a stage not built, named; READY or NOT_READY; fail closed) and its mutation self-tests (one killed mutant per planted problem in every repository, each listed in the README).
3. Batch 3: the scorer (both figures always; a forbidden citation in the top five is a miss; scores and question ids only), the visible question half (at least 10 per repository, with gold sources and forbidden citations), the runner (one command, not collected, writing only under the folder it is given by literal path; its `gov close` step built and tested with a stand-in), and the finished README (each kind's correct handling and the record that shows it; the hidden half's form for W2-93; each KPI line mapped to its tests).

## Batch 1: the behaviour to build and test

Each line is in the words of the KPI lines; the ticket file is the authority where this differs.

- **Five repositories of different shapes, built at test time, file by file and commit by commit, each in a temporary folder of its own as a git repository of its own:**
  1. a Python application with drifted specs and plans;
  2. a Rust workspace of several crates;
  3. a TypeScript monorepo of several packages;
  4. a repository of legacy documents and large files;
  5. a repository with a secret in its history.
  Each has a plausible history (several commits, with dates and authors set in the builder so the history is deterministic for a seed), real-looking source, specs, plans, tests and a README. Nothing is cloned from this repository, its worktrees or the dev tiers, and no built repository is committed; **the large files are generated at test time, never tracked** in this repository (their size a builder parameter: small for the self-tests so they stay fast, larger for the real run).
- **Planted problems whose correct handling is known in advance, each kind in at least two of the five repositories and in at least two different shapes, so that a shape-specific answer cannot pass:**
  - a **stale spec that looks current**: a current status and a recent date, contradicted by the code and by a newer spec (which exists in the repository and is the governing source);
  - a **superseded plan**: an older plan whose successor exists and says it supersedes it (in at least two shapes, for example a successor that names it and one that replaces it by version);
  - a **misleading file name**: a name that says old, draft or unused on a file that is live (imported, referenced or run), and one that says current on a file that is not (nothing references it, its content is out of date);
  - a **secret**: generated at test time from parts, in a form the secrets scanner's default rules detect (`gitleaks` 8.30, the one on PATH), committed in an early commit and removed in a later one, so it lives in history only; **never written whole in any tracked file of this repository** (your test code builds it from parts at run time; check your own files with `gitleaks dir tests/acceptance/W2-81 --redact` or the equivalent no-git form and report the finding count only); the secret is in at least two repositories (the secret repository and one other), in two shapes (for example a key in a config file and a token in a script);
  - an **orphaned test**: a test whose subject was removed (the module or function it imports or exercises is gone from the code), in at least two shapes (for example Python and TypeScript, or Rust).
  - Also, in the legacy repository: **legacy documents** (to be classed and extracted or retired as A8 states) and **large files** (to be classed and kept out of the semantic index within the budget).
- **The seed:** the names, places and wording of each instance are drawn from a seed per run (an integer given to the builders; a fixed default for the self-tests, a fresh one for the real run). The same seed builds the same repositories and the same manifest; a different seed changes names, places and wording. The seed is recorded in the manifest (and later in the report).
- **The manifest:** the list of what was planted, per repository: each planted problem's id, kind, shape, paths, the commit(s) involved (12-digit), what makes it detectable and what its correct handling is, its controls; and for the secret, its path, its 12-digit commit and the scanner rule that detects it, **never its value** (the value is held in memory, in the builder's return, for comparison only). **The manifest is kept outside the built repository** (written beside it in the run folder, never inside the repository's tree or history).
- **Controls against over-flagging, in each repository:** a current spec that looks old (an old date, "draft" in its name) and a live file under a legacy-sounding folder (for example `legacy/`, `old/`, `archive/`). **And one clean variant** of one shape with nothing planted (its manifest lists no planted problem, only controls). Each control is listed in the manifest as a control, with what flagging it would look like.
- **Hermetic and bounded:** no network, no model, no adoption that works; cases write only in their temporary folders and remove them; the self-tests run under 120 s alone (and must stay fast under the close's parallel load, `-n auto`); none is skipped; a missing tool (git, the secrets scanner) **fails naming it**, never skips.

### Batch 1's self-tests (`test_*.py`), at least

- each of the five builders builds a git repository of its own in a temporary folder (its git common directory is its own, not this repository's), with several commits, file by file;
- the same seed gives the same manifest and the same tree; a different seed changes names, places or wording of the planted instances;
- every planted kind appears in at least two repositories and at least two shapes; the clean variant has no planted problem; every repository has its two controls;
- the manifest is outside the built repository and absent from its history;
- the secret: present in an early commit's tree, absent from HEAD's tree, detected by `gitleaks` on the built repository's history (the finding's rule and 12-digit commit match the manifest), and its value appears in no file of this suite, no manifest, and no captured output (compare in memory; never print it; on a failure, the assertion message names the path and commit, never the value);
- the stale spec is contradicted by the code and by a newer spec in the built repository; the superseded plan's successor exists and names it; the misleading-name files really are live or dead by references; the orphaned test's subject is really gone;
- the large files exist in the legacy repository's working tree only at the size asked, and are never in this repository;
- nothing is written in this repository by a case (check `git status --porcelain` of this worktree is unchanged around the session, or an equivalent), and the built repositories are removed.

Run your tests (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m pytest tests/acceptance/W2-81 -q -p no:cacheprovider`, to the end, never `-x`), and once more with `-n auto`; time both; they must pass and run under 120 s. Also run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once and quote its last line (no collection error, no name clash).

**A README start** (`tests/acceptance/W2-81/README.md`): the five shapes, the planted kinds with their shapes and which repository holds each, the controls, the seed, the manifest's form and where it lives, how the secret is built and why its value never appears; each KPI line of batch 1 mapped to its tests. (There is no implementation to be red against: the proving ground's self-tests pass when the proving ground is right; say this in the README.)

If a KPI line is ambiguous, do not guess: return a decision package (question, why now, options, impact, reversibility, cost, recommendation, confidence) and build what it does not block.

## Return

End with your commit. Your return gives: the sandbox check's result first; your commit's 12-digit hash and its trailers; the files; the test count and both timings; the collect-only last line; the gitleaks count on your own files; which repositories hold which planted kinds and shapes; what you learned about the adoption records (where each stage writes, its fields) that batch 2's judge will read; retrieval used and what it served; guard refusals met; your temporary folders' size; anything for batch 2.

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
