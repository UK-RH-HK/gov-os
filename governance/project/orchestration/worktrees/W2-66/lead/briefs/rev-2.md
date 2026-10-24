You are a fresh reviewer. Ticket DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`, at the head `5634d430`, and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard or a gate fail open. You write nothing: you return the probe record's content, and the lead writes and commits it. Return each finding as a described behaviour, with its severity. Your budget is about 90 minutes.

**This is the second and last review of this ticket (DEC-413).** The first review (a fresh session, head `9174e358`) failed on three findings, each "yes" and "fails open": F1, a moved file seen only at its new path, so a move out of the shared core or out of another ticket's paths got a scoped close; F2, the root `tests/conftest.py` got a scoped close, the overlap rule ignored a ticket's declared acceptance folder (`acceptance_tests.path`, DEC-892), and a path held only by tickets without a suite was placed; F3, `tests/acceptance/W1-27/test_w2_67_copies.py` loads other suites' conftests by file path and no coupling followed them. Its rows "yes / other": F4 (deselected cases not named in the evidence), F5 (the own suite misnamed for a declared folder), F6 (the test map's note on scripts wrong), F7 (the nightly's bisect counting "not found" as bad; not reproduced; left a row), a feature-gated row (the check result taken as given; left a row). Since then: a fresh test designer wrote cases for F1 to F5 (`39b875bc`, `ee98e24a`, `cc7fb17f`, `7dc63f67`, `98c4be2f`, `6d17109b`; the README's "Interface" items 1, 2, 3 and 6 changed), and a fresh engineer built them and corrected the note (`45763156`, `16e98848`, `1ad4db0d`, `b3e60cbc`, `d3650169`). Probe whether F1 to F6 are answered at this head, and probe the new code (the declared-folder rule, the suiteless rule, the rename handling, the deselection naming, the live map's new entries) for new behaviour the tests miss, as well as the rest of the ticket as below. Your findings are final: a failing finding here goes to the owner, not to a third review.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`) and `git rev-parse HEAD` (expect `5634d4305a7c4f9b677bed6a6cea26ea53c96c94`). If anything differs, stop and say so. Inside the sandbox `git status --short` may list character devices 1,3 owned by nobody (`.bashrc`, `.gitconfig`, `.idea` and the like): those are the sandbox's placeholders, not changes.

## The judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

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

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820):** you read everything, tests and code alike (DEC-820, DEC-826 Q3), except: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen): never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path; never read or name the qualification oracle; (c) does not bind you (you are no counterpart on this ticket); **(d) the hidden half of any evaluation set, if you are measured by it.** Never read `.claude/settings.json`. Never list, read or write in `~/gov-os-workbench`.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead (for example `src/gov/close`, `tests/acceptance/W2-66`), name the files you need under `governance/project/` one by one, and **count every refusal in your return**.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 3 GB and 150,000 files and folders.** Keep the sandbox's own `TMPDIR` and count it. Keep pytest's own temp-folder retention, never a per-run `--basetemp`, and pass `-o tmp_path_retention_policy=failed` on every pytest run you make (DEC-905). A probe that needs a repository builds a small temporary one in your temporary folder (W1-30's and W2-66's acceptance support modules build fixture projects a `gov close` accepts). Measure your scratch (`du -s --inodes` and `du -sh` of your `TMPDIR`) at the start and the end, and give the figures in your return's `evidence` line.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A single command is cut at 10 minutes: run no full suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree. Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write no file of the repository and make no commit. No subagents. Install nothing. No push, merge, rebase or tag. Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (only inside fixture projects you build), and nobody runs `docs/plan/tools/validate_s1.py`.
- You never ask or notify the owner (no question box, no `owner-ping`).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md`: its KPI lines (success and failure) and its `allowed_paths` (`src/gov/close/select.py`, `src/gov/close/nightly.py`, `src/gov/close/evidence.py`, `src/gov/close/command.py` (the calls, `--full`, the record's lines and the retention option only), `governance/project/test-map.yaml`, `template/governance/kernel/schemas/test-map.schema.json`, `template/governance/project/test-map.yaml`, `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`, `docs/research/W2-66-scoped-close.md`), and its body (the test designer's files; "Not in this ticket").
- The card: `docs/plan/WAVE_2_WBS.md` §2, "#### W2-66"; W2-07's card ("#### W2-07": "W2-66 writes the record's evidence lines, W2-07 the gates").
- The sources, in `docs/DECISION_REGISTER.md`: DEC-880 (item 2), DEC-883, DEC-884, DEC-889, DEC-890, DEC-891, DEC-892, DEC-896, DEC-899, DEC-903, DEC-904, DEC-905, DEC-906, DEC-726, DEC-852 (item 3), DEC-866; lens I's synthesis `docs/assessment/2026-10/I-SYNTHESIS.md` (§4's W2-66 block, P-IS-1, P-IS-2) and lens H's `docs/assessment/2026-10/H-test-strategy.md`.
- The list rows `W2-H044` and `W2-M153` in `docs/plan/WAVE_2_LIST.md`.
- The ticket's change: `git diff --stat w2/integrate...HEAD` and `git log --format='%h %s%n%(trailers:only,unfold)' w2/integrate..HEAD`; the merge `03f470a5` of `w2/integrate` (W2-07's gates) into this branch, whose message says how `command.py`'s conflict was resolved; the acceptance tests `tests/acceptance/W2-66/` (README with its "Interface"), the revised `tests/acceptance/W1-30/test_w1_30_regression_scope.py`, `tests/acceptance/W1-30/test_w1_30_close.py::test_regression_includes_other_acceptance_folders` and `tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay`; the code at the head.

- **The first review's record** (it failed, so it is not committed): `/home/usain/gov-os-worktrees/W2-66/.gov-runtime/scratch/lead/probes/PR-DAEO-c1uz-review1-fail-draft.md`.
- **Known at this head (the lead's verification at `5634d430`):** the full parallel run in the close's form is 15,747 passed, 30 skipped and 2 failed (29:13); the serial-only cases run alone after it. The two reds are W1-01's `test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests` and `test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass`, both on the merge `03f470a5`: "the merge commit itself changes tests/acceptance/W1-30/test_w1_30_close.py". Git's own merge combined two test designers' edits of that file; DEC-253's rule (`tests/acceptance/W1-01/w1_01_support.py`, `merge_offences`) passes a merge only when each acceptance file it changes equals one parent's. The lead returns it to the orchestrator as a package (the first review judged it "yes / other"); you need not find it again. Also known: a typical scoped close spends most of its time in one W2-54 record-reading case that runs `gov check` itself (the report's discovery), a residual.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open. For this ticket in particular:

- **Fail-open selection:** a change an honest agent makes in ordinary work that a scoped close does not reach although a suite that would catch it exists (a coupling the test map misses; a path placed by `record_only` that holds code; a shared-core member missed; an unplaced path, a missing, unreadable or schema-invalid test map, or an unknown base that does not widen to the full regression; the base read from a record that is not green or not an ancestor).
- **The evidence block:** a scoped run stated as full or the reverse; a skip, a left-out suite or a failure not named; a record without its JUnit XML or failure text; the merge's two `evidence` values (the block under `evidence`, W2-07's judged paths now under `class_evidence`) both surviving in the record, the answer and a refusal.
- **The merge with W2-07:** every gate of W2-07 (the commit gates, the pre-close gate, the class judgement, the disk reading, the repair ticket's commit) still runs and refuses as on `w2/integrate`; the scope does not let a refusal pass or a counted refusal go uncounted.
- **The per-test limit and the retention option:** a hung test that holds the close; a run of the close or the nightly without the limit or without `-o tmp_path_retention_policy=failed`; a missing pytest-timeout that does not refuse.
- **The nightly command:** a red it does not report, a flaky candidate bisected, a selection miss without the test map's correction, a run that writes outside its record.
- **The measured report and the fixture trial** in `docs/research/W2-66-scoped-close.md`: figures that its commands do not support.

Run the code; do not judge it by reading alone (fixture projects, the selection on given paths, `gov close` inside fixture projects, single acceptance files). A finding you could not reproduce is marked as such.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound. Your verdict: `pass` (no finding that is both "yes" and "fails open" or "loses work") or `fail`. The lead passes findings to a test designer; you repair nothing (MR-4).

After the twelve fields, as the payload `PROBE_RECORD:`, the record's body as the lead will commit it under `docs/probes/DAEO-c1uz/`: what was probed (the head, the ticket's change, the merge), who probed (your session, read-only, sandboxed, effort max), the threat-model line, each finding with its two lines, what was found sound, and the verdict. The lead adds the front matter.

Your return is one message. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
