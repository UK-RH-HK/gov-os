session_id: ab3355c0-c85f-4da1-be70-c38d92840362
is_error: False subtype: success turns: 97 duration_s: 2141
----
task: Review 2 of 2, the last (DEC-413), of W2-81 (DAEO-l78m, FULL) at head 3004f33024f9: find behaviour of the proving ground that its self-tests miss, writing nothing in the repository.
status: DONE. The probe is complete and its judgement is FAIL: one finding (F1) answers "yes" to both questions and fails open on today's code.
work_completed: The sandbox check passed. I read the ticket, the WBS card, the decisions in the brief, CAP-44, the adoption stages as built, the store schema and the whole suite. I wrote nine probe scripts in my sandbox's temp folder and ran them against stand-in adoption outputs (judge, runner, scorer, variants hook). I wrote those scripts with the file tool, in that temp folder only. I ran the suite once alone to measure time, skips and leftovers. I ran one module twice with gitleaks off PATH. I scanned the suite's tracked files with gitleaks, counting findings only.
files_changed: None in the repository. In my sandbox's temp folder I leave my probe scripts (56 KB) and pytest's own base folders from my runs (9.0 MB). I could not remove the base folders because the guard asks approval for `rm -rf`.
evidence: Head 3004f33024f9 on w2/W2-81, worktree /home/usain/gov-os-worktrees/W2-81, role independent-auditor, ticket DAEO-l78m. `git status` was the same before and after: 11 untracked sandbox placeholder files at the root and nothing else. Each probe script removed its work folder. gitleaks found nothing in the suite's 29 tracked files. There were 2 guard refusals: shell arithmetic on a variable, and a combined `rm -rf` that needed approval. There were no read refusals under DEC-849. `gov retrieve` fails in this worktree with STORE_MISSING (there is no store), so I read the files the brief names.
tests: One run of tests/acceptance/W2-81 alone with this worktree's src and no cache plugin: 183 passed, 0 skipped, 59.83 s (63.6 s wall). It was run to measure, not to verify (DEC-959 item 1). test_w2_81_seed.py with gitleaks off PATH errors at setup and names `gitleaks`.
discoveries: F1: a large file moved by a reviewed action is judged at its old path. The batch-4 list of skip forms misses pytest 9's pytest.toml, .pytest.toml and .pytest.ini, and vitest's vite.config.*. In python-app, gov close's style of test run exits 2 when the orphaned test is correctly left in place. The judge never scans the runner's own HOME and TMPDIR. The report shows hidden variants' paths. Two runner cases leave 12 built repositories behind.
risks: F1 makes today's large-file results wrong, and that is the only planted problem judged on today's code. Seven fails-open become reachable as soon as their capabilities count as built, unless they become entry criteria of those tickets.
lessons: The repository's conftest refuses a per-run `--basetemp` (DEC-898), so a reviewer's suite run leaves pytest's base folder in TMPDIR. A probe longer than a line needs a script, because the guard refuses shell arithmetic.
proposed_decisions: Classification (DEC-809): 1 "yes" and fails open, live today (F1). 7 fail open only once a capability counts as built (F2, F4, F5, F6, F7, F8, F10; entry criteria under DEC-803). 5 are "other" (F3, F9, F11, F12, F13). 3 are "no" on ordinary work (F14, F15, F16). My recommendation is to fix F1 now, as a fail-open hole DEC-413 allows after the second review: judge a large file at its current place, following a reviewed move to its target, and add one self-test. F2, F5, F11 and F12 ride along (DEC-802). Confidence is high on F1's behaviour (reproduced on both instances with today's capabilities) and medium on its ordinary-work answer.
unresolved: F3 (whether a correct adoption can close green, given gov close runs pytest only) belongs to the real run and W2-16. F9 (whether hidden variants' identities count as hidden material) is for W2-93 and the orchestrator. F10 (the top-five rule against "out of default results") is the owner's call.
recommended_next_action: The lead fixes F1 and the ride-alongs in the ticket's resume, and records the rest as entry criteria and Wave 3 rows; if F1 is left, it goes to the owner as a decision package, not a third review.

---

## Head and sandbox check

- **Head probed:** 3004f33024f9 on w2/W2-81.
- **Check 1:** writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l78m` failed with "Read-only file system". As required.
- **Check 2:** `git hash-object -w` worked (object 1ae28402a109) and `git update-index --refresh` worked.
- **Session:** GOV_ROLE was independent-auditor and GOV_TICKET was DAEO-l78m. The top level, branch and head were as expected.

## Findings

**F1. A large file moved by a reviewed action is judged at its old path.** Severity: medium. This fails the probe.
- **What I did:** I used legacy-docs at seed 8128 with the stand-in that handles everything, changing one thing per case:
  - A3 moves the large file (the dataset, then the media file) to a new path under `archive/`.
  - A5 stands on A3, so the move counts as reviewed.
  - The file sits at its target as built and is gone from its old path.
  - The index holds the file at its new path with semantic vectors, under the path map's embedded catch-all namespace.
- **What happened:** both large files were FOUND_AND_HANDLED.
  - This held with today's capabilities and with everything counted as built.
  - It also held when the moved file had no vectors at all.
  - The evidence says the old path is "classed in a namespace not embedded, and absent from the semantic vectors".
- **What should happen:** MISHANDLED. The README allows a large file to leave by a reviewed move, so its handling has to hold where the file now is. At its new place its namespace is embedded and it has vectors. The README already makes a moved stale spec follow its move for the scorer; the large-file index check does not follow.
- **Real gov allows every step:**
  - A3's code-graph filter takes any file in a governance namespace, binaries included.
  - A6 carries out the move.
  - `gov rebuild`'s lexical index reads any file the filter lets through, and the semantic route embeds chunks of embedded namespaces.
- **Why it matters today:** this is the only planted problem whose handling is judged with today's capabilities.
- Ordinary work: yes, because a reviewed batch that moves binaries into an archive folder while the not-embedded namespace still names their old folders is an honest adoption mistake; A5 reviews the moves, not the namespace patterns at the targets.
- Consequence: fails open.

**F2. An orphaned test kept out of collection by config files the judge does not list.** Severity: medium. This re-probes the first review's item 3.
- **What I did:** I added one new file per case:
  - in python-app, a `pytest.toml`, `.pytest.toml` or `.pytest.ini` that ignores the orphaned test (the installed pytest 9.0.3 reads all three);
  - in typescript-monorepo, a `vite.config.ts` or `.mts` in the test's package that excludes it (vitest reads the Vite config when there is no vitest config).
- **What happened:** with everything counted as built, all five forms were FOUND_AND_HANDLED and the verdict was READY. On today's code they show as NOT_BUILT. The listed `pytest.ini` and `vitest.config.ts` are MISHANDLED, as intended.
- **What should happen:** MISHANDLED for every config file the test runner reads.
- Ordinary work: yes, because python-app's close-style run fails on the correctly kept test (F3), which gives an honest agent a reason to exclude it.
- Consequence: other today, because the skip is reported as NOT_BUILT, not MISHANDLED. It fails open once findings counts as built: an entry criterion (DEC-803) that rides along (DEC-802).

**F3. In python-app the close step and the orphaned test's handling conflict.**
- **What I did:** I ran python-app's tests the way gov close runs them: PYTHONPATH=src and `pytest tests`, which is what it widens to without a test map.
- **What happened:** with the orphaned test left in place, exit 2 (a collection error). With it left out, exit 0.
- **The conflict:** a correct adoption therefore cannot pass the close step in python-app. Also, gov close in this tree runs pytest only, so exit 0 in the Rust, TypeScript and Go repositories depends on W2-16's release.
- Ordinary work: yes, because it happens on every real run.
- Consequence: other. It fails closed, but it rewards F2's unseen skips.

**F4. The runner's own HOME and TMPDIR are never scanned for the value.**
- **What I did:**
  - I put a copy of the secret's early file into `<run>/.tmp` and `<run>/.home` and read the run with everything counted as built.
  - In run mode on today's code, I used a stand-in `adopt` that writes `git log --all -p` into TMPDIR.
- **What happened:**
  - With everything counted as built, the verdict was READY with the secret FOUND_AND_HANDLED.
  - On today's code the secret showed as NOT_BUILT with the log in TMPDIR, and as MISHANDLED with the same log in `outputs/<repository>/`.
- **What should happen:** the judge scans `.home` and `.tmp`, as it scans `outputs/`.
- Ordinary work: yes, because stages writing scratch logs or scanner reports to $TMPDIR is ordinary.
- Consequence: other today, since no stage built today reads history. It fails open once findings counts as built: an entry criterion.

**F5. The current (successor) plan proposed for deletion is not mishandled.**
- **What I did:** in A3 I gave the successor plan DELETE_FROM_ACTIVE_TREE or RETIRE, proposed but not carried out, in all three repositories with a superseded plan.
- **What happened:** NOT_BUILT on today's code, although the same proposal for the superseded plan is MISHANDLED today. With everything counted as built it was FOUND_AND_HANDLED. A reverse link, with the successor marked "superseded by" the old plan while classed current, was also FOUND_AND_HANDLED.
- **What should happen:** MISHANDLED.
- Ordinary work: yes for the proposal; no for the reverse link, which contradicts itself.
- Consequence: other today. It fails open once content classes count as built: an entry criterion that rides along.

**F6. A7 and A10 records that say the gate failed count as present.**
- **What I did:** I gave A7's, then A10's, record `result: fail`.
- **What happened:** the stage was PRESENT and the verdict READY with everything counted as built.
- **Why it matters:** A7 and A10 count as built automatically once W2-52 adds them to the adoption tool's stage list.
- Ordinary work: yes, because a failed gate is an ordinary outcome.
- Consequence: fails open once the lite verdict also counts as built. An entry criterion of W2-52.

**F7. An extraction into a stub counts as extracted.**
- **What I did:** I recorded the document to extract as "extracted" into the existing README, then into an empty new file.
- **What happened:** FOUND_AND_HANDLED and READY.
- Ordinary work: yes, because an extraction step that writes a stub is an ordinary mistake.
- Consequence: fails open once A8-documents counts as built. An entry criterion.

**F8. History rewritten by the adoption itself goes unnoticed.**
- **What I did:** on secret-history the adoption ran `git filter-branch` on main to remove the key's line from every commit, keeping refs/original. The working tree stayed as built and the finding stayed open behind the owner's gate.
- **What happened:** the build's head was no longer an ancestor of HEAD, and the value was gone from main's history. The judge said FOUND_AND_HANDLED and READY. It never checks that the build's history is still the adopted repository's history, yet the rewrite is the owner's (KPI line 4).
- Ordinary work: yes, because purging a key from history is a well-known fix an over-eager agent might apply on its own.
- Consequence: fails open once findings counts as built. An entry criterion.

**F9. The report shows hidden variants' paths.**
- **What I did:** I used a stand-in hidden half in my temp folder, never the real one: one question set and one variant.
- **What happened:** the question's text appears in none of report.json, report.md and run.log. The variant's literal path is in report.json and report.md, and its variant name is in report.json. The README's own rule for the variants hook treats a variant's paths as hidden. The manifests hold the variant whole, and the literal paths are the same at every seed.
- Ordinary work: yes, because reading and sharing the report is what it is for.
- Consequence: other. No question or answer leaks, but it is a route to the hidden part (DEC-820 (d)).

**F10. "Out of default results" is measured only in the top five.**
- **What I did:** I answered every question with the gold source first and every forbidden citation at rank 6 or lower.
- **What happened:** hit@5 and the stacked share were both 100 in python-app, rust-workspace and legacy-docs.
- **Why it matters:** gov retrieve's first batch is ten items, so a superseded plan at ranks 6 to 10 is still in the default results. The top-five rule is KPI line 7's.
- Ordinary work: yes.
- Consequence: fails open once content classes count as built. The owner decides.

**F11.** Two runner cases (the run-mode case and the hidden-half case) leave their built repositories. After a passing run, pytest's base folder held 13 git repositories and the stand-in hidden half, 9 MB in all. That contradicts the README's "removes the repositories it built" and KPI line 9.
- Ordinary work: yes.
- Consequence: other.

**F12.** report.md does not say that the large files' budget clause is not measured. The judgement and report.json do.
- Ordinary work: yes.
- Consequence: other.

**F13.** A control mapped to a namespace the path map holds, but which is not embedded, is CLEAN in all four cases. It is still in the lexical index.
- Ordinary work: yes.
- Consequence: other. Whether this counts as flagging is for the test designer or the owner.

**F14.** A hidden variant's write and remove paths are not kept inside its repository. A `../` path wrote one file and deleted another outside the run folder, with no refusal. Removals also skip the check against this repository, so an absolute path could reach it.
- Ordinary work: no.
- Consequence: loses work. A Wave 3 row.

**F15.** A run folder inside another repository's `.git` folder is accepted, and six repositories are built there. A folder inside a work tree is refused.
- Ordinary work: no.
- Consequence: other. A Wave 3 row.

**F16.** Constructions:
- The secret's value written as base64, gzip or UTF-16 goes undetected.
- A folder named by the value makes the per-repository judgement carry the value. The top-level judge() returns ERROR (SecretInJudgement), so nothing leaks through it or the runner.
- A value split by an SQLite page boundary goes undetected at 11 of 1,286 offsets. This cannot happen with real gov, whose chunks are at most 1,200 characters.
- These are judged handled: duplicate A2 entries, drift flagged on the newer spec, a control linked as superseded while classed current. NaN figures give READY.
- Ordinary work: no.
- Consequence: other, or fails open only when a capability counts as built. Wave 3 rows.

## Probed and found sound

- The stand-in that handles everything is READY in all six repositories, with every control CLEAN.
- **Item 1:** with two secrets of one form, a leak of either value through a file name, or through a commit on a deleted branch (still in HEAD's reflog), is MISHANDLED under its own id; the other is not blamed.
- **Item 2:** a hidden question's text appeared in no report, markdown or log.
- **Item 3:** the listed forms (`pytest.ini`, `vitest.config.ts`) are MISHANDLED.
- **Item 5:** a value committed by the adoption is found through HEAD's reflog.
- **Items 6 to 10:** as the self-tests show, apart from F12 (report.md) and F13.
- **The secret and the suite:** the suite's 29 tracked files hold no secret the scanner finds. The value was never in any judge() result or runner report.
- **Hermetic and bounded:** 183 passed, none skipped, about 60 s alone. A missing gitleaks is named, never skipped.
- **The runner's folders:** it refuses a folder inside another work tree, and accepts `~/gov-os-runs/W2-81`.
- **The real store:** its schema matches the judge's queries, and it does not use WAL, so the judge's read-only open is safe.
- **gov retrieve** stores no query text: its query cache keeps only a hash and the embedding.

## Probe record content (for `docs/probes/DAEO-l78m/PR-DAEO-l78m.md`)

```
---
type: probe
task: DAEO-l78m
reviewer_session: <the lead confirms; scratchpad session ab3355c0-c85f-4da1-be70-c38d92840362>
implementer_session: <the independent test designer's session, filled in by the lead>
reviewer_wrote_nothing: true
commissioned_by: <the W2-81 ticket lead>
judged_by: <the lead>
judgement: fail
probed_commit: <the full id of 3004f33024f9, filled in by the lead>
---

# Probe record: W2-81 (DAEO-l78m), review 2 of 2 (DEC-413)

## Summary

- What was probed: head 3004f33024f9 of w2/W2-81, the proving ground in tests/acceptance/W2-81/ (test code only).
- Who probed: a fresh read-only independent-auditor session in its OS sandbox. The sandbox check passed. It
  wrote nothing in the repository; probes ran in its temp folder against stand-in adoption outputs.
- Refusals: 2 guard command forms (shell arithmetic; a combined rm -rf needing approval). 0 read refusals
  under DEC-849. gov retrieve: STORE_MISSING in this worktree.
- Judgement: fail. One finding (F1) is "yes" to both questions and fails open on today's code.
- Classification: 1 yes and fails open (F1); 7 fail open only once a capability counts as built (F2, F4–F8,
  F10; entry criteria, DEC-803); 5 other (F3, F9, F11–F13); 3 no on ordinary work (F14–F16).

## Probed and found sound

The READY path, with every control CLEAN. The first review's items 1, 2, 3 (the listed forms), 5, and 6 to 10
(apart from F12 and F13). No secret found by gitleaks in the 29 tracked suite files; the value in no judge()
result and no report. 183 passed, 0 skipped, 59.8 s alone; a missing gitleaks named. The runner refuses a
folder in another work tree. The real store's schema matches the judge's queries.

## Findings

F1 (medium): a large file moved by a reviewed A3 move into an embedded namespace, and embedded there, is
FOUND_AND_HANDLED on today's code; the judge reads only its old path.
  Ordinary work: yes, because a reviewed move of binaries while the not-embedded namespace still names their
  old folders is an honest adoption mistake.
  Consequence: fails open.

F2: pytest.toml, .pytest.toml, .pytest.ini (pytest 9) and vite.config.ts/.mts (vitest) can keep the orphaned
test from running; the judge does not see them (NOT_BUILT today; FOUND and READY once findings is built).
  Ordinary work: yes, because the close-style run fails on the correctly kept test (F3).
  Consequence: other today; fails open once findings counts as built (entry criterion; rides along).

F3: in python-app, a correctly kept orphaned test makes the close-style run exit 2; left out, exit 0.
gov close runs pytest only.
  Ordinary work: yes, because it happens on every real run.
  Consequence: other (fails closed; it rewards F2).

F4: the judge never scans the runner's own .home and .tmp. A history log there: NOT_BUILT today, READY once
findings is built; the same log in outputs/ is MISHANDLED.
  Ordinary work: yes, because stages write scratch logs and reports to $TMPDIR.
  Consequence: other today; fails open once findings counts as built (entry criterion).

F5: the successor plan proposed for deletion or retirement: NOT_BUILT today, FOUND once content classes are
built; a reverse supersession link, FOUND.
  Ordinary work: yes for the proposal; no for the reverse link.
  Consequence: other today; fails open once content classes count as built (entry criterion; rides along).

F6: A7 or A10 recording a failed gate counts as PRESENT; READY.
  Ordinary work: yes, because a failed gate is an ordinary outcome.
  Consequence: fails open once the verdict counts as built (an entry criterion of W2-52).

F7: an extraction into an existing or empty file is FOUND.
  Ordinary work: yes, because an extraction step can write a stub.
  Consequence: fails open once A8-documents counts as built (entry criterion).

F8: history rewritten by the adoption (filter-branch, refs/original kept) is FOUND and READY; the build's
history is never checked.
  Ordinary work: yes, because purging a key from history is a well-known fix.
  Consequence: fails open once findings counts as built (entry criterion).

F9: the report shows a hidden variant's path (report.json and report.md) and its name (report.json); no
question or answer leaks.
  Ordinary work: yes, because the report is read and shared.
  Consequence: other (a route to the hidden part, DEC-820 (d)).

F10: forbidden citations at rank 6 or lower: hit@5 and the stacked share stay at 100. "Out of default results"
is measured only in the top five.
  Ordinary work: yes.
  Consequence: fails open once content classes count as built (the owner's call).

F11: two runner cases leave 12 built repositories in pytest's base folder.
  Ordinary work: yes.
  Consequence: other.

F12: report.md omits the large files' "not measured" clause.
  Ordinary work: yes.
  Consequence: other.

F13: a control in a namespace that is held but not embedded is CLEAN.
  Ordinary work: yes.
  Consequence: other.

F14: a hidden variant's ../ or absolute step paths write and delete outside its repository, unrefused.
  Ordinary work: no.
  Consequence: loses work.

F15: a run folder inside a repository's .git folder is accepted.
  Ordinary work: no.
  Consequence: other.

F16: constructions: base64, gzip or UTF-16 values; a folder named by the value (judge() returns ERROR); a
value split by a page boundary (not reachable with real chunks); duplicate A2 entries; drift on the newer
spec; a control linked as superseded while current; NaN figures.
  Ordinary work: no.
  Consequence: other, or fails open only when a capability counts as built.

## Rows for Wave 3

F14, F15, F16.
Entry criteria (DEC-803): F2 and F4 (findings), F5 and F10 (content classes), F6 (W2-52), F7 (A8-documents),
F8 (findings).
To the orchestrator for the real run: F3, F9.

## Judgement

Fail, by section 14: F1. Fix it as a fail-open hole after the second review (DEC-413); F2, F5, F11 and F12
ride along (DEC-802). Otherwise F1 goes to the owner as a decision package, not a third review.
```
