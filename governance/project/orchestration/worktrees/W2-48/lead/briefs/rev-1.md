You are a fresh reviewer. Ticket DAEO-xxgp (W2-48, "Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-48` on branch `w2/W2-48`, at the head `5f201781b4cc1cd834ea6d4cff0ebdda7406869b`, and its acceptance tests pass but for one case held by a package (below). You probe that head for behaviour the tests miss. You write nothing.

Ticket DAEO-xxgp is implemented in this worktree and its acceptance tests pass. Probe the final code for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. Write nothing except the probe record the lead names. Return each finding as a described behaviour, with its severity.
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). The full text is `governance/project/briefs/JUDGEMENT.md`, which this brief carries word for word.
- You read everything, tests and code alike (DEC-820); you commit nothing (DEC-826 Q3).

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

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-xxgp','w').write('x')"` must fail.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, saying which.

## Your time: return within 100 minutes

The launcher's session is stopped after two hours of wall time, whatever it is doing, and a stopped session's return is lost. Plan to return within about 100 minutes; at 90 minutes, stop probing and return what you have, naming what you did not probe. Run every probe in the foreground (each Bash call under 10 minutes); nothing started in the background is ever read.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-xxgp`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-48` and `w2/W2-48`), and `git log --oneline -1` (expect `5f201781`). If anything differs, stop and say so.
- **DEC-732, the code under test (word for word from the lead's brief):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory used (DEC-836, DEC-859, DEC-860).** For what you need to know about the repository, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m gov.cli.main retrieve "<question>" --json` (inside the sandbox it may hang on its embedder's network call: give it `timeout 120`, and if it fails, say so and read the named files). Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve` and for what.
- **Reads (DEC-820, Policy 2).** You read everything, tests and code alike. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (d) the hidden half of any evaluation set, by whoever is measured by it. ((c), the counterpart's work, does not bind a reviewer.)
- **Read refusals (DEC-849).** Until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and list them in your return.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder, from scratch (the acceptance suite's support module `tests/acceptance/W2-48/w2_48_support.py` builds such projects; you may import it by path). No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673). Never touch this tree's own cache files.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: put probe scripts in your session's temporary folder with literal paths (the Write tool may be absent for you: then write probe files only inside your temporary folder, by `python3 -c` with literal paths).
- Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree (a probe runs `gov close` only in a temporary project it builds). Never run `gov rebuild --no-embeddings`.
- **The machine (DEC-847, DEC-780).** While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run no suite; before any suite run, wait while the 1-minute load is above 20.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- You never ask or notify the owner directly (DEC-850, DEC-855). On an authentication or access error, stop and return.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-xxgp.md`: its KPI lines and its `allowed_paths` (`src/gov/testcache/**`, `src/gov/close/cache*`, `src/gov/close/command.py` (the `--no-cache` option and the call into the cache only), `.coveragerc`, `tests/unit/testcache/**`, `docs/research/W2-48-cache-choice.md`).
- The sources, in `docs/DECISION_REGISTER.md`: DEC-726, DEC-083, DEC-843, DEC-852, DEC-869, **DEC-875**, **DEC-876** (read in full: its condition 1 is your focus).
- The decisions that apply: DEC-487 and DEC-500 (the close's run is the suite's own), DEC-527 and DEC-549 (the parallel run and the serial-only cases), DEC-757, DEC-762 (the close's results feed `accepted_reds` and `load_sensitive`), DEC-868 (the pre-close collection must not change), DEC-820 (Policy 2), DEC-866 (supersession), ADR-0001 (`docs/adr/ADR-0001-threat-model.md`).
- The owner's package DEC-876 answers: `governance/project/orchestration/packages/P-W2-48-5.md` (name the file).
- The ticket's acceptance tests (`tests/acceptance/W2-48/`, with its README), the code at the head (`git diff --stat w2/integrate...HEAD` names it; `src/gov/testcache/` with `child/sitecustomize.py` and `pytest_plugin/`, `src/gov/close/cache.py`, the ticket's lines in `src/gov/close/command.py`), the builder tests and the research record.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

**Your focus, the owner's rule (DEC-876 condition 1): fail safe.** The cache reuses a test's earlier pass instead of running it. A reused pass that the test would not give if it ran is the fail-open of this ticket: a close, a lead's run or a W2-24/W2-46 record that says "passed" for a test that now fails. Anything the cache cannot see must make its test always run. Probe for **any ordinary way in which a change that alters a test's outcome leaves its earlier pass reused**, in the test's own process and in a process it starts, for example (the lead's list, not a limit): what a test or its child reads, lists, stats or executes inside and outside the project; the environment variables and the working directory it depends on; `git` and the other programs a test or its child runs (and the processes they start, such as hooks); fixtures and `conftest.py` of every scope; module-level state read without a line running; parametrized and class-based tests; xdist's parallel run and the serial-only run afterwards; the close's shared entries against a lead's local ones (a dirty tree, an untracked or ignored input, a worktree); an unreadable, truncated or older store; `--no-cache` and the nightly. The suite already proves the cases its README lists; four were added after the lead found them in this round (a child's read, `git` on the project's repository, a `.py` file read as text, a folder listing): check that the fix holds beyond the exact planted forms. Also judge: whether a failed or errored result can ever come back as reused or passed; whether a cache fault can ever read as "passed"; whether the close's record of reuse is honest (each reused test with the run and commit it came from); and anything else the KPI lines hold.

Run the code; do not judge it by reading alone. Build small temporary projects with git (the support module above, or your own) and run `python3 -m gov.testcache run --json tests` and `gov close` in them as the suite does. A finding you could not reproduce is marked as such. Keep probes small and deterministic.

**Known and not to be reported as new:** one acceptance case, `test_w2_48_close.py::test_a_test_that_failed_in_a_refused_close_runs_again_in_the_next_close`, is red at this head on purpose: a refused close's `test_cache` lists only its failed and errored tests, because W1-30's `test_w1_30_r11_parallel_runs.py::test_a_failing_case_of_the_parallel_run_is_named_as_before` forbids a refusal to name a passing case outside its `test_runs`, while the W2-48 suite's support wants every test listed; that conflict is a package for the orchestrator (P-W2-48-7). Also known: the cache cannot see a bare existence check (`os.path.exists`, `os.stat`: no audit event), a read made while the root `conftest.py` is imported, or a read by C code with no Python frame (the research record states them); judge whether any of these is ordinary in this repository's own suite, and say so with an example if it is.

The lead's own measurement of the time saved (DEC-876 condition 4) is in the research record's time-saved section; you may check that it says what was measured and how; you need not repeat it.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work or fails open, with its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound. The lead passes findings to a test designer; you repair nothing (MR-4).

Give, after the twelve fields, **the probe record's content** for the lead to commit, in this form (the lead writes it to `docs/probes/DAEO-xxgp/PR-DAEO-xxgp.md`):

```
---
type: probe
task: DAEO-xxgp
reviewer_session: <your session id if you know it, else "unknown">
implementer_session: <the lead fills it>
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: <pass | fail>
probed_commit: <the full hash of the head you probed>
---

# Probe record: W2-48 (DAEO-xxgp), <one line>

- **What was probed.** <the head; the suites run; the temporary projects built and what they cover>
- **What was found.** <each finding with its two lines; what holds>
- **Judgement.** <pass or fail, and why, by the judgement rules>
```

`judgement: fail` when, and only when, a finding is "Ordinary work: yes" with "Consequence: fails open" or "loses work".

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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

In the fields, give: the sandbox check's result (first); the head you probed; the `gov.__file__` line; each finding in short with its two lines; whether you used `gov retrieve`; the read refusals you met; then the probe record's content.
