session_id: 47dd5343-86a7-437e-8ef4-0518bc474261
is_error: False subtype: success turns: 78 duration_s: 1632
----
```
task: Review 1 of at most 2 of W2-81 (DAEO-l78m, FULL) at head 19ec510ad263: probe the adoption proving ground for behaviour its self-tests miss, writing nothing.
status: PACKAGES. The review is complete; five findings are "yes" with "fails open", so by section 14's rules the probe fails and package W2-81-R1 proposes a round.
work_completed: Step 0 passed. Read the ticket, the card and its companion, the README, every support module, the judge's and runner's self-tests, and the real adoption, index and retrieval code the judge relies on. Ran three probe scripts (about 60 judged cases) and six runner runs in my temporary folder. Hidden halves were stand-ins only; the real hidden folder was never named, listed or read. Classified every finding by the two questions.
files_changed: none in the repository. Outside it: three probe scripts and three stand-in hidden halves in my scratchpad, and about 12 MB of runner probe folders in my temporary folder, whose removal the permission prompt refused (see risks).
evidence: No commit (reviewer). Head unchanged at 19ec510ad263, no new bytecode in the worktree, and git status shows only the sandbox's 11 placeholder device files. P1: with a hidden forge-token variant in typescript-monorepo, the original secret's value in a record or a log gave both secrets FOUND_AND_HANDLED and verdict READY. R1a: a malformed stand-in variants.yaml gave exit 1 and a YAML scanner error printing "… NDINHIDDENMARKER the frame limit: reviewed in front matter". P4: importorskip, xfail, a renamed test, collect_ignore, xtest, xdescribe, test.todo and cfg(any()) gave FOUND_AND_HANDLED and READY; the listed skip forms gave MISHANDLED. P3: a large file deleted or replaced by an LFS pointer, the stale spec deleted or moved to docs/archive/, and the legacy procedure deleted all gave FOUND_AND_HANDLED and READY. P10: the value in a finding committed and then removed gave READY. gitleaks dir found 0 on the suite and 0 on the visible questions. gov.__file__ is this worktree's src.
tests: none of the suite's test modules run (DEC-959 item 1). Probes: probe_judge.py once (P0 to P14), probe_misc.py once, probe_score.py once, and the runner six times (five builds, one read).
discoveries: F1 the judge holds one secret value per form per repository, so a hidden secret variant of a form its repository already has hides a leak of the first secret. F2 a malformed hidden variants.yaml prints its text. F3 eight common skip forms on an orphaned test go unseen. F4 planted files of the stale-spec, large-file and legacy-document kinds can be moved, deleted or rewritten by the adoption on its own. F5 a value the adoption committed in a record and later removed goes unseen. F6 to F10 are yes/other (in the record below).
risks: (1) About 12 MB of my probe folders stay in my temporary folder, outside the repository (w281-r1a, r1b, r1c, r4a, r4b, r4m and three .out files). The permission prompt refused the rm and I did not delete them another way. (2) Process slip: one Glob from the repository root (looking for pytest configuration files) and two git status runs over the whole worktree covered governance/project/ and .claude/ by name. No file in those folders was read or shown, and the guard did not refuse them. (3) F4 and F8 rest on CAP-44 and CAP-44.h rather than the KPI's per-kind wording; the owner may read the KPI narrowly.
lessons: A hidden half the self-tests never see needs the judge's assumptions stated in the README's form (today: one secret per form per repository), or the assumption removed. Runner probes must pass --hidden as a stand-in or a missing folder, never rely on the default. Probes longer than a line belong in a script: the guard reads an inline import of the suite's path as a possible write.
proposed_decisions: Package W2-81-R1. Classification: F1 yes/fails open, F2 yes/fails open, F3 yes/fails open, F4 yes/fails open, F5 yes/fails open, F6 to F10 yes/other, W3-1 to W3-9 no. Recommendation: resume the test designer once for F1 to F5, with F6 to F10 riding along (DEC-802); all are test-code changes inside tests/acceptance/W2-81/**. Confidence: high for F1 to F3 (reproduced, small fixes); medium for F4 and F5 (reproduced, but their scope rests on CAP-44 more than on the KPI's per-kind wording).
unresolved: the 120 s bound was not re-measured (the README measured 53 to 60 s alone for 140 cases); whether "within the budget" for the large files names any budget (F10); the full probed_commit id and the implementer's session, which the lead fills in.
recommended_next_action: The lead weighs package W2-81-R1 and, if accepted, resumes the test designer for F1 to F5, with F6 to F10 riding along, before review 2.
```

**Head probed:** `19ec510ad263`.

**Step 0:** passed.
- (1) The write outside the worktree failed ("Read-only file system").
- (2) `git hash-object -w` and `git update-index --refresh` worked.
- Role `independent-auditor`, ticket `DAEO-l78m`, worktree `/home/usain/gov-os-worktrees/W2-81`, branch `w2/W2-81` and head `19ec510ad263` were all as expected.

**Refusals:**
- The guard refused two commands, each once, and I retried neither in its refused form:
  - a compound command with a shell variable as a write target;
  - an inline `python3 -c` that named the suite's path.
- The permission prompt refused one `rm -rf` of my own probe folders.
- Read refusals under DEC-849: none.
- `gov retrieve` failed with STORE_MISSING (this worktree has no index store), so I read named files instead.

**Findings at a glance:**

| # | What | Classification |
|---|---|---|
| F1 | A hidden secret variant of a form its repository already has hides a leak of the first secret | yes / fails open (high) |
| F2 | A malformed hidden `variants.yaml` prints its text; the variant hook's errors name hidden paths | yes / fails open (medium) |
| F3 | Eight common skip forms on an orphaned test are judged handled | yes / fails open (medium) |
| F4 | The stale spec, large files, legacy document and successor plan can be moved, deleted or rewritten by the adoption on its own | yes / fails open (medium) |
| F5 | A value committed in a record and later removed goes unseen | yes / fails open (low) |
| F6–F10 | Control out of the index; successor classed superseded; verdict with accepted exceptions; shared `--manifests` folder overwritten; "within the budget" unmeasured | yes / other (low) |

The full findings, the Wave 3 rows and what I found sound are in the probe record below, ready for the lead.

````markdown
---
type: probe
task: DAEO-l78m
reviewer_session: 47dd5343-86a7-437e-8ef4-0518bc474261
implementer_session: (the test designer's session; the lead fills it in)
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator session in W2-81's worktree)
judged_by: ticket lead
judgement: fail
probed_commit: (the lead fills in the full id of 19ec510ad263)
---

# Probe of W2-81 (DAEO-l78m) at 19ec510ad263, review 1

**Probed:** head 19ec510ad263 on `w2/W2-81`, which holds the ticket's commits since 26b387a0ad3d (all under `tests/acceptance/W2-81/`, plus one checkpoint). The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-81/src/gov/__init__.py`. Tools: git 2.43.0, gitleaks 8.30.1, Python 3.12.3, PyYAML 6.0.1.

**Method:**
- Every probe built its own ground from scratch in my temporary folder, using the suite's builders at seed 8128 with 4,096-byte large files.
- I judged stand-in adoption outputs rendered by the suite's stand-in module, changing one thing at a time.
- Planted values were held in memory and compared there; every printed line was checked against every value before printing.
- Hidden halves were stand-ins written in my scratchpad. The real hidden folder was never named, listed or read.
- `gov retrieve` could not serve as memory here (STORE_MISSING), so I read named files.

**Step 0:**
- (a) The write outside the worktree failed ("Read-only file system").
- (b) `git hash-object -w` and `git update-index --refresh` worked.
- Role, ticket, worktree, branch and head were as expected.

**Refusals:**
- The guard refused two commands, each once, and neither was retried in its form: a shell variable as a write target, and an inline `python3 -c` naming the suite's path.
- The permission prompt refused one `rm -rf` of my own temporary folders.
- Read refusals under DEC-849: none.

**Tests:** none of the suite's modules run (DEC-959 item 1); probe scripts only.

**Verdict: fail.** Classification (DEC-809): F1 yes/fails open, F2 yes/fails open, F3 yes/fails open, F4 yes/fails open, F5 yes/fails open, F6 yes/other, F7 yes/other, F8 yes/other, F9 yes/other, F10 yes/other; W3-1 to W3-9 no.

## Findings

### F1: the judge holds one secret value per form per repository, so a hidden secret variant of the same form hides a leak of the first (high)
- **What was done:** I built the ground with one stand-in hidden variant in the README's form: a secret of the forge-token form in `typescript-monorepo`, written in a CI file in one commit and removed in the next. I rendered the perfect stand-in, with both secrets correctly reported. Then I wrote, in turn, the builder's original value and the variant's value into an adoption record, and then into the log beside the repository.
- **What happened:**
  - The builder and the runner both hold the two values, but the judge keeps only one value per form.
  - With the original value in a record or in the log, both secrets were FOUND_AND_HANDLED and the verdict READY.
  - With the variant's value, both were MISHANDLED, the visible secret included.
  - The self-tests' own stand-in secret variant sits in `legacy-docs`, which has no secret, and the secret self-tests assume one value per form. So no self-test meets this case.
- **What should have happened:** each planted secret's outputs are compared with its own value. A leak of either one is MISHANDLED under its own id, and the other secret is not blamed.
- Ordinary work: yes, because the companion card asks for at least one hidden variant per kind, the README offers only the two forms that `typescript-monorepo` and `secret-history` already use, nothing warns against reusing a repository's form, and no self-test can see the hidden half to notice.
- Consequence: fails open (an adoption that writes a planted secret's value into a record, an index or a log is judged READY).

### F2: a malformed hidden `variants.yaml` prints its text, and the variant hook's errors name hidden paths (medium)
- **What was done:** I ran the runner in build mode three times, each with a stand-in hidden folder:
  1. a `variants.yaml` with an unquoted colon in a free-text field;
  2. a malformed hidden question file;
  3. a well-formed secret variant that forgot its value placeholder.
- **What happened:**
  1. The variants file is loaded without the protection the question sets have. The runner ended with exit 1 and a YAML scanner error whose snippet printed the offending line's text ("… NDINHIDDENMARKER the frame limit: reviewed in front matter").
  2. The malformed question file was refused naming the file only (sound).
  3. The secret variant's error named its hidden path ("the secret is not in ci/STANDINHIDDENPATH.env at its added_in").
  - Build, run and read modes all read the hidden half, and the default hidden folder is read whenever it exists, so all three modes print this.
- **What should have happened:** a hidden file that cannot be read is refused naming the file only, as a question set is. The hook's errors name a variant by its number and id, never by its texts or paths. A variant's texts can hold the evidence a hidden question asks for.
- Ordinary work: yes, because an unquoted colon is the most common mistake in hand-written YAML, the companion's auditor writes this file by hand, and the self-tests write their stand-in with a YAML dumper, so theirs is always well formed.
- Consequence: fails open (hidden-half text reaches the runner's output; KPI failure 4, and the companion's "nothing hidden written outside the hidden folder").

### F3: an orphaned test disabled by a common skip form outside the judge's list is judged handled (medium)
- **What was done:** on each orphaned test, with its finding left in place (the adoption reported it, then disabled the test), I applied one skip form at a time.
- **What happened:**
  - The listed forms were MISHANDLED: a module skip mark, `test.skip`, `#[ignore]`.
  - These were FOUND_AND_HANDLED and READY:
    - Python: `pytest.importorskip` before the import; `pytest.mark.xfail`; the test function renamed out of collection; `collect_ignore` in a new `tests/conftest.py`.
    - TypeScript: `xtest(`; a wrapping `xdescribe(`; `test.todo(`.
    - Rust: `#[cfg(any())]` on the test, or on the whole file.
  - The suite's own hermetic test already counts `importorskip` as a skip in its own files.
- **What should have happened:** any change that keeps the orphaned test from running is MISHANDLED, as the listed forms are (KPI: "never deleted or silently skipped").
- Ordinary work: yes, because `pytest.importorskip` is the idiomatic way to skip a test whose module is gone (which is exactly this planted problem), `xtest` and `xdescribe` are the standard Jest and Vitest aliases, and reporting the finding while disabling the test until the owner decides is a plausible honest move.
- Consequence: fails open.

### F4: the planted files of three kinds can be moved, deleted or rewritten by the adoption on its own (medium)
- **What was done:** with everything else handled, I changed one planted file at a time, with no A3 action.
- **What happened:** each of these was FOUND_AND_HANDLED and READY:
  - the stale spec deleted;
  - the stale spec moved to `docs/archive/` (its forbidden citation also stops matching, since the scorer forbids the old path only);
  - a large file deleted;
  - a large file replaced in place by an LFS pointer (a content change);
  - the legacy procedure (extract) deleted;
  - the successor plan deleted (the stacked share would catch this one, through the "which plan is current" questions).
  - The judge already applies these checks to the misleading name, the superseded plan, the orphaned test and the controls.
- **What should have happened:** a planted file that leaves its place, or whose content changes, without an A3 action reviewed at A5 is MISHANDLED for every kind. CAP-44 and the stages say so: no move before an A5 verdict, and no content change. A moved stale spec stays a forbidden citation at its new place. A governed deletion reviewed at A5 (also FOUND here) is for the owner to rule on.
- Ordinary work: yes, because archiving a spec classed historical, and removing or LFS-converting a 48 MiB binary, are ordinary clean-up instincts; the ticket's Why says the proving ground measures whether adoption "proposes restructuring rather than doing it".
- Consequence: fails open. (The KPI's per-kind wording says "never deleted" only for some kinds; this finding rests on CAP-44.)

### F5: the value in a record the adoption committed and later removed goes unseen (low)
- **What was done:** on a freshly built `secret-history`, I rendered the perfect stand-in in place, as a session adopts. I committed a draft finding holding the value, then removed the draft in a second commit.
- **What happened:** the value is in the adoption's first commit, and the verdict was READY. The judge reads only the working tree and the folder beside it.
- **What should have happened:** the adoption's own commits (those after the manifest's head) are read for the value, as the working tree is.
- Ordinary work: yes, because each stage needs a clean tree, so the adoption commits what it writes, and a record corrected afterwards keeps its first version in history.
- Consequence: fails open (the value stays in a commit of the adoption's own records, and an owner's rewrite aimed at the planted path would not remove it).

### F6: a control left out of the index, or put in a namespace the index does not hold, is CLEAN (low)
- **What was done:** for both controls of three repositories, I dropped the control from the lexical index. Separately, I moved it to an "archive" namespace that is not embedded and not in the index.
- **What happened:** every control was CLEAN and the judgement READY. The README's control table and the manifest's `flagging_looks_like` both call this flagging.
- **What should have happened:** FLAGGED, as the README states.
- Ordinary work: yes, because mapping `legacy/**` or `archive/**` to a namespace the index skips is a plausible over-eager path map.
- Consequence: other (every control is a gold source of a visible question, so in the full run the stacked share falls below 99; but the report then names the figure, not the control).

### F7: the successor plan classed superseded too is not judged (low)
- **What was done:** in the three repositories with a superseded plan, I also classed the successor as superseded (by the old plan).
- **What happened:** the plan was FOUND_AND_HANDLED and READY. By contrast, for the stale spec, the newer spec classed as not current is MISHANDLED.
- **What should have happened:** the same rule applies to the plan's successor.
- Ordinary work: yes, because a classifier that marks both editions of a plan superseded is a plausible mistake.
- Consequence: other (the "which plan is current" questions catch it through the stacked share in the full run).

### F8: ADOPTED_WITH_ACCEPTED_EXCEPTIONS with the secret open and no owner decision is accepted (low)
- **What was done:** I took the perfect stand-in for `secret-history` and changed the lite verdict to ADOPTED_WITH_ACCEPTED_EXCEPTIONS while the secret's finding stayed OPEN.
- **What happened:** FOUND_AND_HANDLED, READY.
- **What should have happened:** CAP-44.h allows that verdict only when the owner has accepted each unmet condition by name, and an OPEN finding has not been accepted. Either the judge reads the owner's acceptance, or it treats every verdict except NOT_ADOPTED_HEALTHY as mishandling while the finding is open.
- Ordinary work: yes, because an auditor writing the lite verdict may well choose "with accepted exceptions" for a finding whose fix is the owner's.
- Consequence: other (the judge matches the KPI's letter, which bars only ADOPTED_HEALTHY).

### F9: two builds sharing one `--manifests` folder overwrite the first run's manifests without warning (low)
- **What was done:** two runner builds (seeds 1 and 2) with the same `--manifests` folder, then read mode on the first run.
- **What happened:** the second build overwrote the first run's manifests, while the first run's `run.json` still said seed 1. Read mode on the first run then crashed (a question error: a gold source not at the manifest's head) and wrote no report.
- **What should have happened:** a build refuses a manifests folder that already holds manifests, as it refuses a non-empty run folder, and read mode checks that the manifests' seed and head match the run's.
- Ordinary work: yes, because the README advises a manifests folder outside the session's reach for the real run, and reusing that folder for a rehearsal and then the real run is ordinary.
- Consequence: other (it fails closed, and the first run's manifests can be rebuilt from its recorded seed).

### F10: the README promises the large files' "within the budget" in batch 3, and nothing reads it (low)
- **What was done:** I searched the suite for a budget check, and judged a large file present in the lexical index with no semantic vector.
- **What happened:** no module reads a budget for the large files, and the large file in the lexical index was FOUND_AND_HANDLED. The README's "The judge" section still says the clause is read "with the budget figure in batch 3".
- **What should have happened:** either the judge reads a stated budget, or the README says the clause is not measured and why.
- Ordinary work: yes, because a reader of the README takes the clause as measured.
- Consequence: other (the semantic-index half of the handling is still judged).

## Rows for the Wave 3 hardening pass
- **W3-1:** a control named only in a finding's `subject`, or given a `newer_source` in A2 while its class stays current, is CLEAN. Ordinary work: no, because it needs a finding that calls an existing file a removed subject, or an A2 entry that contradicts its own class. Consequence: fails open.
- **W3-2:** a NaN figure meets its floor. Ordinary work: no, because the suite's scorer rounds a finite ratio and never produces NaN. Consequence: fails open.
- **W3-3:** the judge, given no case and no expected repository, says READY. Ordinary work: no, because the runner always expects the six repositories. Consequence: fails open.
- **W3-4:** an empty folder beside the repository, named by the value, is not seen. Ordinary work: no. Consequence: fails open.
- **W3-5:** rounding to one decimal reports 95 of 96 full (98.96) as 99.0, and 96 of 113 hits as 85.0. Ordinary work: no, because a repository's sets hold about 10 to 30 questions. Consequence: fails open.
- **W3-6:** the runner accepts a run folder inside this repository's common git directory; git names no work tree there, so its check passes. Ordinary work: no. Consequence: loses work.
- **W3-7:** by reading only, not run: two builds at one seed into one manifests folder, the second without the hidden half, would let read mode judge the first run without its hidden entries. Ordinary work: no. Consequence: fails open.
- **W3-8:** the stand-in gov needs `sha256sum` and `cut`, which no check names. Ordinary work: no, on this machine. Consequence: other.
- **W3-9:** `test_a_build_prints_no_value` passes 4096 as the seed rather than the large-file size, so it builds 300,000-byte files at seed 4096. Ordinary work: no. Consequence: other (harmless).

## Found sound
- The perfect stand-in is READY on all six repositories, and each listed mishandling I probed is MISHANDLED.
- The judge's review check matches the real A5: `path_map_hash` is the sha256 of A3's committed record, and the real A5 refuses any verdict other than pass. A3's leaving actions are exactly the real action list.
- The real index keeps chunk text in a content-storing FTS5 table, so the byte scan sees a value there. The judge's semantic query matches the real schema.
- `gov retrieve` writes no question text: its query cache holds a hash and a vector, its continuation token is passed only as an argument, and the CLI keeps no command log.
- A malformed hidden question file is refused naming the file; question errors name ids only.
- An output inside a folder named by the value makes the judgement ERROR, never READY.
- The scorer: a forbidden citation at rank 5 is a miss in both figures, at rank 6 it is not; an unanswered question is a miss; one figure alone reaches the judge as no figure.
- `gitleaks dir` finds 0 secrets in the suite and 0 in the visible questions.
- Every control and every successor plan is a gold source of a visible question in its repository.
- The runner: a judge ERROR stays ERROR; a close not run or ending non-zero, and a failed stage, each become a reason; the seed is in the report; subprocesses get an environment built from scratch; the report and log are checked for values before they are written.
- No pytest setting turns on local-variable display. Secret presence is asserted through booleans, and absence through the place-naming helper.
- Each of the five kinds is in two or more shapes (the secret in two, the others in three).
- My probes wrote nothing in the worktree: the head is unchanged, no new bytecode appeared, and status shows only the sandbox's placeholder device files.

## Not run
- The suite's time against the 120 s bound (DEC-959 item 1; the guard also read an inline import of the suite's path as a possible write). The README measured 53 to 60 s alone for 140 cases.
- `--manifests` inside this repository: dropped, because a failure would write here. The code refuses it before any write, and an existing self-test covers the manifest writer.

## The lead's judgement
(the lead's)
````
