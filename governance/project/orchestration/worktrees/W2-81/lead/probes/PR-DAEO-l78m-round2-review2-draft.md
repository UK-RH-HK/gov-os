session_id: f26b96e4-4947-4806-8f1a-9691568408f3
is_error: False subtype: success turns: 93 duration_s: 2478
----
**Verdict: FAIL** under section 14's rules. One finding is "yes / loses work": a round 2b runner self-test creates a folder inside this repository. Two more findings fail open but only once a not-yet-built feature exists, so they become entry criteria (DEC-803). The pooled-figure question is still open for the owner. Head probed: `5ec8242c1a4a`.

task: Fresh review 2 of 2 of round 2 (DEC-993, DEC-997) of W2-81 (`DAEO-l78m`) at head `5ec8242c1a4a`: probe the proving ground for behaviour its self-tests miss.
status: DONE — probe complete. Judgement FAIL on F1 (a runner self-test creates an empty folder inside this repository). F2 and F3 fail open but are feature-gated (DEC-803). One reading stays open for the owner.
work_completed: Sandbox check passed. Read the ticket, the card and its companion, the README, every support module and the runner, round 2 and judge test modules. Wrote and ran ten probe scripts in my temporary folder. Ran the suite's modules (runner module at two fixed seeds, the whole suite alone and with `-n auto`, one module without `gitleaks`). Ran `gitleaks` over the suite's files and its history. Checked today's `src/gov` code for the store schema, query caching, the A3, A5 and A8 records, memory classes and embedding policy.
files_changed: none. Probe scripts and their builds are only in `/tmp/gov-launch-independent-auditor-xiylyx76/claude-1000/probe/`.
evidence: Head `5ec8242c1a4a`, suite change `56af0a59973b`. The stray folder `tests/acceptance/W2-81/no-hidden-questions/` exists, is empty, and has mtime 2026-11-01 14:55:27, between `e095e9ae97f3` (13:45) and `56af0a59973b` (15:16); `git status` does not list it. A mkdir recorder shows the runner helper's target is that folder ("inside this repository: True"). Pooled probe: READY with the measurement half's hit@5 at 70.0 in all six repositories. Typo probe: NOT_READY (stacked share 95.0) as written, READY (100.0) with the typo. `gitleaks` 8.30.1: 0 findings in the suite's files and 0 in its history since `26b387a0ad3d`.
tests: Runner module with a seed-fixing plugin: 35 passed, 1 deselected (the case that writes in this repository) at seed 1001 (23.0 s) and at seed 2147483647 (22.0 s). Whole suite alone: 269 passed, 2 deselected, 70.07 s at load average about 21. Whole suite with `-n auto`: 269 passed, 20.22 s. `test_w2_81_score.py` without `gitleaks` on PATH: 6 errors, each naming `gitleaks`. Seed driver: READY at seeds 0–199 and at about 97 seeds in three far ranges. None of these is a verification run (DEC-959 item 1).
discoveries: (1) A round 2b self-test helper creates an empty folder in this repository, and the tripwire cannot see empty folders. (2) A forbidden citation that names an unknown fact is dropped silently, so one typo in the hidden half flips NOT_READY to READY. (3) The pooled figures allow READY while the measurement half's own hit@5 is 70. (4) A control named only in a finding's `subject` stays CLEAN. (5) Seven rows, listed in the record.
risks: The empty folder stays in this worktree until someone with write rights removes it, and every run of the runner module re-creates it until the helper changes. 13 MB of my probe builds (built repositories whose histories hold the planted values) remain in my session's temporary folder, because `rm` was refused twice. Timings were taken at load average 19–38.
lessons: Import suite modules with `python3 -B` or `PYTHONDONTWRITEBYTECODE=1`, or a probe writes `__pycache__` in the suite. The repository refuses pytest's `--basetemp` (DEC-898, DEC-907 item 2). The sandbox shows 11 placeholder device files at the worktree root as untracked; conclude nothing from them. `rm -rf` in the temporary folder needs an approval a non-interactive session cannot give, so probes should clean up inside their own process.
proposed_decisions: One package. Classification: 1 finding "yes / loses work" (F1); 2 findings "yes / fails open", feature-gated under DEC-803 (F2 → W2-93, F3 → the ticket that builds findings); 1 open reading (pooled figures); 7 rows (5 "no", 2 "other"). Recommendation: fix F1 now (one line: make the helper's empty folder inside the case's own temporary folder, as the review module's helper already does) and remove the stray folder. Let F2's fix ride along with that resume (DEC-802); otherwise record it as W2-93's entry criterion. Record F3 as an entry criterion of the ticket that builds findings. Put the pooled reading to the owner. Confidence: high on all three behaviours (each reproduced); medium on calling F1 "loses work", which follows the brief's own definition although in practice it is an empty untracked folder.
unresolved: The owner's reading of the floors (pooled figure or measurement half alone). Where F2 and F3 go. An untracked `.claude` folder inside the suite folder (dated 2026-10-31 22:49, not in `git status`), not listed under the brief's rule. Refusals: 2 Bash permission refusals of `rm` on my own temporary folder (stopped, AR-6); 1 pytest `--basetemp` refusal by the repository's plugin (reran without it); 0 guard read refusals. `gov retrieve`: 1 query, answered FACET_UNAVAILABLE (store stale), so I read named files.
recommended_next_action: Lead: remove the empty `tests/acceptance/W2-81/no-hidden-questions/`, have the test designer change the runner helper as above (carrying F2's fix along per DEC-802), then put the pooled-figure reading to the owner.

---

# PR-DAEO-l78m-review4: round 2's review 2 of 2, the round's last (DEC-993, DEC-997, DEC-916)

- **Ticket:** `DAEO-l78m` (W2-81), FULL. **Head probed:** `5ec8242c1a4a` (suite's last change `56af0a59973b`). **probed_commit:** <the lead fills in the full id>.
- **Reviewer:** a fresh independent-auditor session, read-only, 2026-11-01.
- **Sandbox check:**
  - Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l78m` failed (read-only file system).
  - `git hash-object -w` worked (object `1ae28402a109`), and so did `git update-index --refresh`.
  - `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-l78m`, top level `/home/usain/gov-os-worktrees/W2-81`, branch `w2/W2-81`, head `5ec8242c1a4a`.

## Summary

Round 2b's seven behaviours hold in forms beyond the self-tests, round 2's first batch holds, and round 1's behaviours hold. Specifically:
- The READY path of a correct adoption no longer depends on the seed.
- The secret's value anywhere in the run folder is MISHANDLED.
- The measurement half is required.
- Hidden material is shown by number and id only.
- A store without vectors is read as having none.
- Template errors are refused by id.

One round 2b change breaks a KPI line. The runner module's new helper creates an empty folder inside this repository whenever the case that refuses an inside-repository run folder runs. Git cannot see empty folders, so the tripwire misses it, and the folder is in this worktree now.

Two further gaps fail open, but only once a feature is switched on:
- a mistyped fact name in a hidden forbidden citation is dropped silently;
- a control named only in a finding's `subject` stays CLEAN.

The open reading on the figures is shown concretely: the runner says READY while the measurement half's own hit@5 is 70.

## Judgement: FAIL

By section 14's rules, F1 is "yes" and "loses work" under this ticket's definition ("a case or the runner writing in this repository"). In practice the harm is an empty untracked folder; no file is overwritten.

F2 and F3 are "yes" and "fails open", but each exists only once a feature is switched on (W2-93's hidden half; the findings capability, CAP-44.g). Under DEC-803 they are entry criteria of those tickets, not a round on their own.

DEC-809 classification line: 1 yes/loses work (F1); 2 yes/fails open, feature-gated (F2, F3); 1 open reading; 7 rows (R1–R5 "no", R6–R7 "other"; three of the "no" rows also include an "other" item).

DEC-802: if the ticket resumes for F1, F2's fix can ride along.

## Findings

### F1 — a runner self-test creates an empty folder inside this repository (low in effect; breaks KPI line F5)

- **What was done:** Called the runner module's option helper the way the inside-repository refusal case calls it, with mkdir replaced by a recorder. Also looked at the suite folder in this worktree.
- **What happened:**
  - Round 2b's helper creates an empty `no-hidden-questions` folder beside the run folder it is given (`test_w2_81_runner.py:34`). For the case that aims the run folder at `tests/acceptance/W2-81/w2-81-run`, that is `tests/acceptance/W2-81/no-hidden-questions/`, inside this repository.
  - The mkdir happens before the runner refuses the run folder, and it does not go through the suite's own-repository refusal.
  - The case passes: it checks only that the run folder itself was not made.
  - The tripwire compares `git status`, which never lists an empty folder.
  - The folder exists in this worktree now: empty, mtime 2026-11-01 14:55:27, during round 2b's work.
- **What should have happened:** The helper makes its empty folder inside the case's own temporary folder (the review module's helper already does this), or the case passes its hidden folder explicitly. Nothing is created in this repository. The stray folder is removed.
- **Ordinary work:** yes, because every run of the runner module makes it, including the lead's scoped set and the regression wherever it runs. It is already in this worktree.
- **Consequence:** loses work, by this ticket's definition (a case writing in this repository). In effect it is an empty untracked folder; no file is overwritten.

### F2 — a mistyped fact name in a hidden forbidden citation is dropped silently, which can turn NOT_READY into READY (medium; feature-gated)

- **What was done:**
  - Built at seed 6 with a stand-in hidden half in my temporary folder.
  - In one rust-workspace hidden question, changed the forbidden citation `{stale}` to `{stael}`.
  - Used a stand-in retrieval that returns the stale spec first and the gold source after it.
- **What happened:**
  - As written: NOT_READY. The forbidden citation was in the top five, and rust-workspace's stacked share was 95, below 99.
  - With the typo: READY, at 100 and 100. The citation was dropped without any message, count or line in the reports.
  - An unknown fact name in a forbidden citation is treated like the clean variant's absent facts (the README's kept reading).
  - The visible half drops nothing in any planted repository (python-app 7/7, rust-workspace 3/3, typescript-monorepo 4/4, legacy-docs 2/2, secret-history 1/1, at seeds 8128, 1 and 77), and the clean variant's visible file has no forbidden citations. So the drop only ever acts on the hidden half.
- **What should have happened:** A forbidden citation naming a fact unknown to every builder is refused by id. Only the facts a repository is known to lack (the clean variant's stale spec, old plan and dead module) are dropped. Alternatively, drops are counted per repository in both reports.
- **Ordinary work:** yes, because the hidden half is hand-written YAML templates by W2-93's auditor, and no self-test reads it.
- **Consequence:** fails open: a short figure is read as met.
- **Feature-gated (DEC-803):** the risk exists only once W2-93 writes a hidden half, and READY needs one. Entry criterion for W2-93: every hidden forbidden citation resolves in its repository. Alternatively it rides along with F1's fix (DEC-802).

### F3 — a control named only in a finding's `subject` stays CLEAN (medium; feature-gated)

- **What was done:** In python-app's perfect stand-in, added an orphaned-test finding whose `subject` is the live control file. Its `paths` lists only the test, as the stand-in's own finding form does.
- **What happened:** The control was CLEAN. For controls, the judge reads only a finding's `paths`, `path` and `test`.
- **What should have happened:** A finding that names a control in any field (`subject`, `newer_source`, `governing_source`) is FLAGGED. A finding claiming a live control is a missing subject is a "reported as a finding" flag.
- **Ordinary work:** yes once findings exist: an over-eager orphan report naming a live file under a legacy folder as the missing subject.
- **Consequence:** fails open: a flagged control is read as CLEAN.
- **Feature-gated (DEC-803):** findings are not built today (CAP-44.g). Entry criterion of the ticket that builds them.

## The open reading: floors on the pooled figure, or on the measurement half alone

- **What was done:** Seed 5, stand-in hidden half of 10 questions per repository. Visible questions were answered with their gold first. In each repository, 3 of the 10 hidden questions were answered with their gold at rank 6, behind five decoys, so every gold source was still in the stacked context.
- **What happened:**
  - READY with no reasons.
  - Per repository: pooled hit@5 between 85.0 and 85.7; stacked share 100; visible half 100; measurement half 70.0 in all six.
  - The reports show only pooled figures. The per-question `part` field lets the halves be recomputed.
  - The stacked share is effectively per half, since one miss in either half puts it below 99. Only hit@5 is diluted.
  - Round 2 item 7's "not embedded is CLEAN" reading relies on visible questions whose gold sources are the controls. If the floors move to the measurement half alone, that backstop moves with them unless the hidden half also uses the controls as gold.
- **Ordinary work:** yes, because a retrieval tuned on, or simply better at, the visible development half scores higher there with nothing deliberate.
- **Consequence:** fails open if the floors are meant for the measurement half (READY with its hit@5 at 70, against a floor of 85). Nothing fails if they are meant for the pooled figure. The owner's reading decides.

## Rows for Wave 3, and other

- **R1 — a copied large file is not judged.** A large file copied (not moved) into an embedded namespace, with vectors there and the original left in place, is FOUND_AND_HANDLED.
  - Ordinary work: no, because today's A6 moves files with git and leaves no copy, and copying a large binary into an embedded folder is not an adoption step.
  - Consequence: fails open.
- **R2 — a move that leaves a symbolic link goes unseen.** A planted file (the stale spec) or a control spec moved with no reviewed action, with a symbolic link left at its old place, is FOUND_AND_HANDLED, or CLEAN for the control. The judge reads through the link.
  - Ordinary work: no, because it needs a link planted at the old name (section 14's deliberate construction), and today's A6 leaves none.
  - Consequence: fails open.
- **R3 — some places are never scanned for the value.** The secret's value is not seen in two kinds of place:
  - non-object files inside any folder named `.git`: a repository's `.git/gov-adoption.log`, its `.git/COMMIT_EDITMSG`, or a stray `outputs/.git/`;
  - the name of an empty folder.
  - Ordinary work: no, because today's `gov` writes nothing of its own into `.git/` (git's objects, refs and reflogs are read by the history check), and a folder named by the value is a construction.
  - Consequence: fails open.
- **R4 — `.cargo/config.toml` is outside the configuration list.** Setting `runner = "true"` there keeps the Rust orphaned test from running, and it stays FOUND_AND_HANDLED.
  - Ordinary work: no, because no honest setting in that file keeps one test out; the keeping-out form is a construction.
  - Consequence: fails open.
- **R5 — a missing `embedding_policy` reads as embedded.** A large-file namespace without the optional `embedding_policy` field is judged MISHANDLED ("is embedded"). Today's `gov` embeds only when the policy is exactly `embedded`.
  - Ordinary work: yes, because the field is optional in the path map's schema.
  - Consequence: other. It fails closed: a correct adoption is judged NOT_READY.
- **R6 — a hidden variant's kind shows through its capability.** A hidden variant that is NOT_BUILT keeps its capability, and that names its kind for `A8-documents`. A hidden legacy-document variant in the Rust workspace shows `A8-documents` in its evidence and in the repository's `not_built`, although the README says a hidden variant's kind is withheld. Separately, a hidden step that rewrites a visible file makes every visible evidence line naming that file read as "the variant's file".
  - Ordinary work: no, because only a reader of a finished run's report sees it, after the measured sessions have ended.
  - Consequence: other. No hidden question, answer, path or value is shown.
- **R7 — a special file blocks the secret.** A named pipe or other special file anywhere in the run folder makes each secret MISSED.
  - Ordinary work: no, because today's `gov` leaves no pipe or socket there.
  - Consequence: other (fails closed).

**A classified row now closed:** the runner's own HOME and temporary folder (`.home/` and `.tmp/` inside the run folder) are now scanned for the value. A value written there was MISHANDLED and named by its place. No other classified row has changed its classification on today's capabilities.

## Probed and found sound

**Round 2b**

1. **The READY path is independent of the seed.**
   - READY at seeds 0–199.
   - READY at about 97 seeds in three far ranges (2147483587–2147483617, 987654321–987654350, 31337–31372). That batch was cut by my timeout at load average 38; no odd line was printed before the cut.
   - No repository ever had two questions with the same text and different gold.
   - Forbidden-first was always below 85.
   - The runner module passed 35 of 35 at seeds 1001 and 2147483647 through a seed-fixing plugin.
   - Only `w2_81_run` draws a seed.
2. **The secret's value anywhere in the run folder.** The value in `.home/`, in `.tmp/`, deep under `outputs/`, in a repository's `.gov-runtime/` cache, in `manifests/`, and as a file name under `outputs/`: each was MISHANDLED and named by its place (`run:<path>`, or the folder only for a name), never by the value. The reports never held it.
3. **The measurement half is required.** The command line reports the hidden half's presence.
4. **A hidden variant's file in visible evidence.** A visible secret's value written into a hidden variant's file is named `repository:hidden variant #1 (m7)'s file`; the path does not appear.
5. **"Not measured" lines.** They come from visible entries only (but see R6 for `not_built`).
6. **The store's schema.** Today's `gov` store uses the schema the judge reads: `lexical_chunk.path`, with `semantic_vector.chunk_id` joined on `chunk_id`. So the no-vector-table reading cannot mask today's vectors. The lexical index takes every tracked file through the secret filter, so the controls stay in it.
7. **Template errors.** Ten more forms (a lone closing brace, spaces, `!r`, `{0[0]}`, `{}`, a nested format spec, a dunder attribute, a stray `}`, a non-ASCII name, `{__class__}`) were refused by id with no text in all four places. The exception is an unknown name in a forbidden citation, which is dropped (F2).

**Round 2's first batch**

- Moves judged at the target: the self-tests' 12 cases pass. The copy is R1.
- The root `package.json` narrowing the workspaces is MISHANDLED and named.
- The successor plan's proposals: passed in the suite run.
- Every runner case removes what it built: the runner module left only empty case folders and pytest's lock file. The whole suite left only the lock file and a 3-byte scanner report, and no built repository.
- The markdown report's "not measured" lines and the hidden variant's naming: passed in the suite run, plus my probe of a hidden variant's file.
- The reading in item 7 is sound on today's capabilities:
  - the path map's memory classes are only governance and product;
  - `embedding_policy` applies to a whole namespace, and a namespace that is not embedded stays in the lexical index;
  - every control is a gold source of a visible question in its repository, so losing one drops the stacked share below its 99 target.
  - Caveat: this rests on the pooled reading.

**Round 1**

- Today's A3 actions are exactly KEEP plus the judge's seven actions that take a file away.
- Today's A5 records only a passing verdict that matches A3's hash, and A6 re-checks it, so "reviewed" holds.
- A8's retirements are read from `retired[].path`.
- The symbolic-link move is R2.
- The rest passed in the suite run.

**Leaks**

- `gitleaks` 8.30.1 found 0 findings in the suite's files and 0 in its history.
- No assertion puts a value check inside its expression, and the repository sets no `--showlocals`.
- Hidden stand-in texts reached nowhere in the run folder outside `.git`, nor stdout or stderr, with 121 retrieval failures logged by id only.
- Today's `gov retrieve` caches only a hash of each query, so the real run writes no hidden question text into the repositories.

**Bounds and READY**

- The suite: 269 passed alone in 70.1 s (load average about 21; the README measured 36 s), and 269 in 20.2 s with `-n auto`. None skipped.
- A missing `gitleaks` fails each case naming it.
- READY is impossible from the command line on today's code: A7, A10, the verdict and the findings stay NOT_BUILT.
- The close step is not run, or exits non-zero → a reason is given.
- Folders inside this repository, inside another work tree, holding this repository, or not empty (for a build) are refused.

## Method

- Probes ran in my temporary folder against single suite modules imported with `-B`; nothing was written in this repository.
- `gov retrieve` answered FACET_UNAVAILABLE (store stale), so I read named files.
- Refusals: 2 Bash permission refusals of `rm` on my own temporary folder (stopped, AR-6), and 1 pytest `--basetemp` refusal by the repository's plugin (reran without it). There were 0 guard read refusals.
- Residue: 13 MB of my builds in my session's temporary folder.
