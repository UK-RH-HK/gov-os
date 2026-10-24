You are a fresh reviewer. Ticket DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`, at the head `6eb5a93f`, and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard or a gate fail open. You write nothing: you return the probe record's content, and the lead writes and commits it. Return each finding as a described behaviour, with its severity. Your budget is about 90 minutes.

**This is the third and last review of this ticket, the owner's one exception to DEC-413 (DEC-912 items 3 and 4).** If you find another fail-open case an honest agent can hit, no fourth round starts: the lead returns it to the owner as a package. So judge each finding strictly by the rules below, and say plainly which findings fail the probe and which are rows.

The history:
- **The first review** (head `9174e358`) failed on F1 (a moved file seen only at its new path), F2 (the root `tests/conftest.py` scoped; the overlap rule ignoring a ticket's declared acceptance folder, DEC-892; a path held only by tickets without a suite placed) and F3 (`tests/acceptance/W1-27/test_w2_67_copies.py` loads other suites' conftests by file path, no coupling), each "yes" and "fails open"; its rows "yes / other": F4 (deselected cases not named), F5 (the own suite misnamed for a declared folder), F6 (the test map's note on scripts wrong), F7 (the nightly's bisect counting "not found" as bad), and a feature-gated row (the check result taken as given).
- **The second review** (head `5634d430`) found F1 to F6 answered, and failed on two new findings: **P1** (medium), a test-map target (record-reading, every-close or coupling) whose file or test function was renamed is still named `selected` and runs nothing, with no widening; **P2** (low), W1-28's held-out copy check (DEC-385) scans every Python file under `tests/acceptance/`, but the test map coupled only `tests/acceptance/**_support.py` to it. Its rows: R1 (a renamed helper imported inside a function not followed; no / fails open), R2 (`pyproject.toml` placed by W1-07 alone; no / fails open), R3 (F7 reproduced; yes / other), R4 (an unreadable `--check-result` holds back a counted containment refusal by one run; yes / other), and the feature-gated row. Its draft record: `/home/usain/gov-os-worktrees/W2-66/.gov-runtime/scratch/lead/probes/PR-DAEO-c1uz-review2-fail-draft.md`; the first review's beside it.
- **The owner's decision DEC-912:** item 1, W1-01's merge rule passes a merge whose every changed acceptance file equals git's own merge of its parents (made by W2-70's round 2, merged into `w2/integrate` and then into this branch); item 3, P1 and P2 fixed here with two new KPI lines in the ticket file; item 4, this is the last round.
- **Since `5634d430`:** the merge `02b62e03` of `w2/integrate` (DEC-910 to DEC-912, W2-69's secrets work, the KPI lines); a fresh test designer's `e9c639f1` (P1's cases, `test_w2_66_unresolved_targets.py`) and `952193ae` (P2's live-map cases), with the README's "Interface" items 1, 3 and 6 revised; a fresh engineer's `73a40277` (P1: `select.py` resolves each selected target at the head and widens with `UNRESOLVED_TARGET`) and `0f0f6cb2` (P2: the live map couples `tests/acceptance/**.py` to `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`); the second merge `052a3b9b` of `w2/integrate` (W2-70's round 2, `3ff8ba51`: W1-01's revised merge rule, DEC-912 item 1); and the lead's checkpoint record `6eb5a93f` (CP-DAEO-c1uz-0015).

Judge: are F1 to F6, P1 and P2 answered at this head; does the new code (the target resolution, the widening, the new coupling) do something the tests miss; and the head as a whole, as below. Two risks the workers named, for you to judge: a target naming one parameter set (`f::test_x[a]`) still resolves when that parameter id is renamed, because a parameter set is read as its function (the README's interface); a node id whose case is inherited from a base class or defined inside an `if` or `try` block at module level is judged gone and widens the run.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`) and `git log --oneline -1` (expect `6eb5a93f`). If anything differs, stop and say so. Inside the sandbox `git status --short` may list character devices 1,3 owned by nobody (`.bashrc`, `.gitconfig`, `.idea`, `docs/source` and the like): those are the sandbox's placeholders, not changes.

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
- **Row W2-L423's rule (owner, standing, DEC-911):** in your return and the probe record, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". A full hash beside one of them turns the secrets-indexing check red.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A single command is cut at 10 minutes: run no full suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree. Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write no file of the repository and make no commit. No subagents. Install nothing. No push, merge, rebase or tag. Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (only inside fixture projects you build), and nobody runs `docs/plan/tools/validate_s1.py`. The guard refuses Bash here-documents with `>` and Bash commands with backticks: write probe files with the Write tool in your temporary folder, and search with the Grep tool.
- You never ask or notify the owner (no question box, no `owner-ping`).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md`: its KPI lines (success and failure, the two DEC-912 lines included) and its `allowed_paths` (`src/gov/close/select.py`, `src/gov/close/nightly.py`, `src/gov/close/evidence.py`, `src/gov/close/command.py` (the calls, `--full`, the record's lines and the retention option only), `governance/project/test-map.yaml`, `template/governance/kernel/schemas/test-map.schema.json`, `template/governance/project/test-map.yaml`, `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`, `docs/research/W2-66-scoped-close.md`), and its body.
- The card: `docs/plan/WAVE_2_WBS.md` §2, "#### W2-66"; W2-07's card ("W2-66 writes the record's evidence lines, W2-07 the gates").
- The sources, in `docs/DECISION_REGISTER.md`: DEC-912, DEC-880 (item 2), DEC-883, DEC-884, DEC-889, DEC-890, DEC-891, DEC-892, DEC-896, DEC-899, DEC-903, DEC-904, DEC-905, DEC-906, DEC-385, DEC-726, DEC-852 (item 3), DEC-866; lens I's synthesis `docs/assessment/2026-10/I-SYNTHESIS.md` (§4's W2-66 block, P-IS-1, P-IS-2).
- The list rows `W2-H044` and `W2-M153` in `docs/plan/WAVE_2_LIST.md`.
- The ticket's change: `git diff --stat w2/integrate...HEAD`, `git log --format='%h %s%n%(trailers:only,unfold)' w2/integrate..HEAD`, `git diff 5634d430 HEAD -- src/ governance/project/test-map.yaml tests/acceptance/W2-66 tests/unit/close`; the acceptance tests `tests/acceptance/W2-66/` (README with its "Interface"); the code at the head.
- **Known at this head (the lead's verification):** at `6eb5a93f`, after a full rebuild: collection 16,426 of 16,428 tests (2 deselected), no error; `gov check` exit 0 (YELLOW only on core-decision-citations and openspec-validate, as before); the full parallel run in the close's form, 16,131 passed, 30 skipped, 0 failed (49:46), W1-01's `test_only_the_test_designer_commits_to_acceptance_tests` and `test_the_integration_merges_of_this_repository_pass` now green; the serial-only cases run alone after it, 265 passed (16:08). Also known: a typical scoped close spends most of its time in one W2-54 record-reading case that runs `gov check` itself (P-W2-66-a, a residual).

## What you probe for

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open. For this ticket in particular:

- **P1 answered:** a selected record-reading, every-close or coupling target whose file or test function is renamed or gone, in the ordinary ways a test designer does it (a file renamed, a function renamed, a class or method renamed, a parametrised case, a target that is a folder), widens the run to the full regression and is named; a target that resolves does not widen; resolution reads the tree closed, not a working-tree file.
- **P2 answered:** a change to any file W1-28's scan reads selects W1-28's check, and the check's target the map names exists and runs those cases.
- **Fail-open selection, at the head as a whole:** a change an honest agent makes in ordinary work that a scoped close does not reach although a suite that would catch it exists (a coupling the test map misses; a path placed by `record_only` that holds code; a shared-core member missed; an unplaced path, a missing, unreadable or schema-invalid test map, or an unknown base that does not widen; the base read from a record that is not green or not an ancestor).
- **The evidence block:** a scoped run stated as full or the reverse; a skip, a left-out suite or a failure not named; a record without its JUnit XML or failure text; W2-07's judged paths under `class_evidence` and this ticket's block under `evidence`, both surviving in the record, the answer and a refusal.
- **The merge with W2-07:** every gate of W2-07 still runs and refuses as on `w2/integrate`; the scope does not let a refusal pass or a counted refusal go uncounted.
- **The per-test limit and the retention option** on every run of the close and the nightly.
- **The nightly command:** a red it does not report, a flaky candidate bisected, a selection miss without the test map's correction, a run that writes outside its record.

Run the code; do not judge it by reading alone (fixture projects, the selection on given paths, `gov close` inside fixture projects, single acceptance files). A finding you could not reproduce is marked as such.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound, and for each of F1 to F6, P1 and P2 whether it is answered. Your verdict: `pass` (no finding that is both "yes" and "fails open" or "loses work") or `fail`. The lead passes findings on; you repair nothing (MR-4).

After the twelve fields, as the payload `PROBE_RECORD:`, the record's body as the lead will commit it under `docs/probes/DAEO-c1uz/`: what was probed (the head, the ticket's change, the merges), who probed (your session, read-only, sandboxed, effort max), the threat-model line, the earlier findings and whether each is answered, each new finding with its two lines, the rows, what was found sound, and the verdict. The lead adds the front matter.

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
