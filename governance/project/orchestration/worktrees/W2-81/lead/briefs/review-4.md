# Brief: reviewer, W2-81 (DAEO-l78m), FULL, round 2 (DEC-993, DEC-997), review 2 of 2, the round's last (DEC-916)

You are a fresh reviewer. Ticket `DAEO-l78m` (`W2-81`, "the adoption proving ground"), profile FULL, is built in the worktree `/home/usain/gov-os-worktrees/W2-81` on branch `w2/W2-81`, at the head `5ec8242c1a4a` (the suite's last change is `56af0a59973b`; `5ec8242c1a4a` adds only a checkpoint record), and its self-tests pass. This is the last review this ticket gets. This ticket's deliverable is test code, written by an independent test designer (MR-3): five synthetic repository builders with planted problems and controls, a manifest, a judge, a scorer, a runner, a visible question half and a README, all under `tests/acceptance/W2-81/`. There is no product code in this ticket. You probe that head for behaviour the self-tests miss. You write nothing.

## Step 0, before any work: the sandbox check (report it first in your return)

1. `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l78m','w').write('x')"` must FAIL.
2. `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.

If (1) wrote the file or (2) failed, stop there and return. Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-l78m`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-81` and `w2/W2-81`), and `git rev-parse --short=12 HEAD` (expect the head above). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src` set **per command** (never in a session's `--settings` env).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase, tag. No `git checkout` of another commit, no `git reset`, no `git clean`.
- **Re-run nothing as a verification (DEC-959 item 1):** the lead runs the scoped set. You may run the suite's modules and your own probes (stand-ins, mutated copies of single modules in your temporary folder) to find behaviour the self-tests miss; a probe you could not reproduce is marked as such.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository). A probe that needs a repository builds a temporary one in your temporary folder, or uses the suite's own builders there. Copying single named files of the suite into your temporary folder to mutate them is allowed.
- **Protected material (DEC-820):** never read the held-out qualification material's contents and never print a secret; never read or name the qualification oracle; never read, list or write `~/gov-os-workbench`; never use `GOV_DEV_TIERS`. Run no glob, search or listing over `governance/project/` or `.claude/` (name files one by one). Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Refused: (a) secrets and keys, never printed (the suite's planted secret is built at run time: **never print its value**; compare it in memory); (b) the held-out material's contents; (c) not applicable to a reviewer; **(d) the hidden half of any evaluation set: never read `fixtures/evaluation/adoption-proving-ground/hidden/**` or any other evaluation set's hidden part.**
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. You have no Write tool and write nothing in the repository: a probe longer than a line is a script you place in your sandbox's temporary folder (its literal path, from `printenv TMPDIR`), for example by copying a single named suite file there with `cp` and changing it with a short `sed` or `python3` line on that literal path; if the guard refuses that, drive the suite's modules through short `python3 -c` lines, or report the probe as not run. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random; never one giant query (DEC-860); code questions by the code-graph tool's own traversal, small and targeted (DEC-859). This worktree has a store (built before the last suite change; a fresh rebuild is queued on the machine's one rebuild lock while you start). Inside your sandbox `gov retrieve` may fail on its network check for the embedder: if one try answers STORE_MISSING or a network error, do not route round the sandbox; say so and read named files.
- **Row W2-L423's rule (DEC-911):** your return is stored under `.gov-runtime/`: write commit hashes as 12 digits (except the one full `probed_commit` id, which the lead fills in), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- Disk: your share of the ticket's budget is 3 GB and 200,000 files and folders; remove what you build.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- On an authentication or access error, stop and return.

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

For this ticket, "fails open" means: **the proving ground passes an adoption that is not ready** (the judge calls a miss or a mishandling handled, a flagged control clean, an unmeasured stage passed, or a short or single figure met; or a judge error reads as READY), or **it leaks what it must protect** (the secret's value, or a hidden question or answer, reaches any output). "Loses work" includes a case or the runner writing in this repository or outside the folder it was given.

## What you read

- The ticket file `.tickets/DAEO-l78m.md`: every KPI success and failure line, its `allowed_paths` (`tests/acceptance/W2-81/**`).
- The card in `docs/plan/WAVE_2_WBS.md` §2, "#### W2-81", and the companion card below it.
- The decisions: DEC-941, DEC-936 item 3.6, DEC-930, DEC-954 (Q8c, Q9f), DEC-957, DEC-833, DEC-820 (d), DEC-845, DEC-873, DEC-911, DEC-728, DEC-899 item 7, DEC-953.
- CAP-44.b to CAP-44.j and CAP-03.a, CAP-03.d, CAP-10 in `docs/contract/contract.yaml`; the adoption stages as built, `src/gov/adopt/`.
- The whole suite at the head: `tests/acceptance/W2-81/` (`git diff --stat 26b387a0ad3d HEAD -- tests/acceptance/W2-81` lists the ticket's files; `git show --stat 226d47b8d5d7` and `git show --stat 56af0a59973b` are round 2's two changes).

## What you probe for (above all)

1. **Can the judge call a miss handled?** Any planted problem in any repository and seed for which an adoption output that does not show the README's handling, or that is missing, unreadable, malformed, empty, of another form, or partly written, is judged FOUND_AND_HANDLED; any mishandling (the secret's value in a record, an index store, a log or a report; the misleading file moved, not proposed; the superseded plan deleted; the orphaned test deleted or skipped; the stale spec cited as governing; a large file in the semantic index) judged handled.
2. **Can a control-flagging adoption pass?** Any control, in any repository, flagged in any of the ways an over-eager adoption would (classed stale, historical, dead, legacy or superseded; proposed for a move or retirement; reported as a finding; left out of default results) and still CLEAN, or a READY verdict with a control FLAGGED.
3. **Can the secret's value leak into any output?** The suite's files (no secret whole in any tracked file: check with `gitleaks dir` on the suite, count only), the manifest, the judge's evidence, the scorer, the runner's report (JSON and markdown), pytest's output on a failing assertion, an exception's message or traceback, a temporary file left behind.
4. **Can a hidden question be printed?** The scorer's and the runner's output, report and logs, given a stand-in hidden half in your temporary folder (never the real hidden folder).
5. Also: a READY verdict with a stage NOT_BUILT, a figure below its floor (hit@5 84; the stacked share below its target), a single figure, or a judge error; the runner writing in this repository or outside its folder, or accepting a folder inside this repository; the seed not in the report; a planted kind in fewer than two shapes; a case that needs the network, reads the workbench, is skipped, or fails to name a missing tool; the self-tests' time near 120 s; the `gov close` step passing when a repository's close exited non-zero or did not run.

6. **Round 2's second batch (the suite changed in `56af0a59973b`).** Probe that each one is now as it should be, in forms beyond the ones the new self-tests use, and that the fixes broke nothing else (above all the READY path of a correct adoption, and the controls):
   1. the runner's READY case for a correct adoption no longer depends on the seed it draws: each repository is answered from its own stand-in answers, so two repositories asked a question of the same text with different gold do not interfere; no other case in the suite is seed-dependent or otherwise flaky (a known flaky test must not land, DEC-968): run the runner's and any other seed-drawing module at many seeds of your own choosing, fixed through a probe plugin in your temporary folder;
   2. a planted secret's value written by the adopting session anywhere in the run folder (the whole `outputs/` tree, including its root, and the run folder's own files, outside the repositories' `.git` folders) is MISHANDLED for that secret, naming the file by its place and never the value, on today's capabilities;
   3. a `--hidden` that names no existing folder is refused (exit 2); a repository whose hidden half yields no hidden question, or fewer than the specification's number, is not counted present and is named; READY needs the measurement half present and asked in every repository, and its absence is a reason in the verdict, both reports and the command line;
   4. where a visible entry's evidence would name a hidden variant's file, it names it as that hidden variant's file by number and id only, never by its path;
   5. the "not measured" lines are computed from the visible entries only, and reveal no hidden variant's kind;
   6. a store without a semantic vector table is read as having no vectors: the lexical checks still run (a control left out of the lexical index is FLAGGED; large files are judged);
   7. any error formatting a hidden template (question, gold, source or forbidden citation) is refused as `refused: <id>: <reason>` with exit 2, showing no template text or fact value.

7. **Round 2's first batch (the suite changed in `226d47b8d5d7`).** Probe that each still holds, in forms beyond the self-tests':
   1. a large file that leaves its place by an A3 move reviewed at A5 is judged where it now is (the target's namespace, its embedding, its vectors, its presence in the lexical index); moved into an embedded namespace or vectorised there, it is MISHANDLED naming the target; moved without a reviewed action, MISHANDLED as before;
   2. any configuration file a test runner reads (pytest's `pytest.toml`, `.pytest.toml`, `.pytest.ini`, `pytest.ini`, `pyproject.toml`, `tox.ini`, `setup.cfg`, conftest; vitest's and Vite's configs and workspace files; and their Rust and Go counterparts) that keeps the orphaned test out is MISHANDLED; a correct adoption that leaves the test's folder alone is not blamed;
   3. the successor (current) plan proposed in A3 for deletion or retirement is MISHANDLED on today's code;
   4. every runner case removes the repositories it built, pass or fail;
   5. the markdown report states what the JSON states is not measured (the large files' budget clause);
   6. a hidden variant appears in the reports and logs by number and id only, never by its paths, names, texts or values (stand-in hidden half in your temporary folder only);
   7. a control in a namespace the path map holds but does not embed is CLEAN, by the README's stated reading: judge whether that reading is sound against the KPI line on controls.

8. **Round 1's behaviours, fixed in an earlier batch:** probe that each still holds, in forms beyond the self-tests':
   1. two planted secrets of one form in one repository: a leak of either is MISHANDLED under its own id;
   2. a malformed hidden file (variants or questions) is refused naming the file only, and the variants hook's errors name a variant by number and id only, never its texts, paths or values;
   3. an orphaned test kept from running or from being collected, by any common skip, expected-failure, rename, collection-ignore, `x`-alias, to-do or always-false configuration form, is MISHANDLED;
   4. any planted file (and the newer spec and successor plan its handling depends on) moved, deleted or rewritten without an A3 action reviewed at A5 is MISHANDLED; a stale spec moved by a reviewed action stays a forbidden citation at its new place;
   5. a planted value committed by the adoption in its own history and removed later is found;
   6. a control left out of the index or mapped to an unindexed namespace is FLAGGED;
   7. the successor plan classed superseded is MISHANDLED;
   8. a lite verdict other than NOT_ADOPTED_HEALTHY while the secret's finding is open, without the owner's acceptance, is MISHANDLED;
   9. a build refuses a manifests folder that already holds manifests, and read mode checks the manifests' seed and head against the run;
   10. the large files' "within the budget" is either read against a stated budget or stated as not measured.

**Already classified, not to be re-raised unless their classification has changed:** these behaviours were found by an earlier review and are recorded as rows for Wave 3 or as entry criteria of the tickets that switch their features on (DEC-803), not as rounds: the runner's own HOME and temporary folder not scanned for the secret's value; a lite A7 or A10 record whose gate failed counting as present; an extraction into a stub counting as extracted; history rewritten by the adoption itself going unnoticed; "out of default results" measured only in the top five; in python-app, a correctly kept orphaned test making the close-style run exit non-zero; a hidden variant's `../` or absolute step paths; a run folder inside a repository's `.git` folder; the secret's value encoded (base64, gzip, UTF-16) or split by a store page boundary; duplicate A2 entries; NaN figures; and, from the round's first review, a control mapped by its looks into a namespace the path map holds but does not embed (an entry criterion of the ticket that builds A2's content class), `--manifests` accepted inside another git work tree, a moved large file whose old path still has vectors, the two path matchers' disagreement, a control's A2 link fields not read, and CI or task-runner recipes outside the configuration list (Wave 3 rows). Name any of them only if one now fails open on today's capabilities. One reading is still open and is not a row: whether the figures' floors apply to the measurement half alone or to the pooled figure; probe and report it as a reading, with its two lines.

Run the code; do not judge it by reading alone.

## Return

The head you probed (12 digits), the sandbox check, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`). Say also what you probed and found sound. Then the probe record's content, ready for the lead to write to `docs/probes/DAEO-l78m/PR-DAEO-l78m-review4.md` (a summary, what was probed and found sound, the findings with their two lines, the rows for Wave 3, your judgement pass or fail by the rules above). You repair nothing (MR-4).

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
