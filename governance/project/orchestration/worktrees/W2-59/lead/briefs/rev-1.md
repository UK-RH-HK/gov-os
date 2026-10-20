# Brief: reviewer — W2-59 (DAEO-kh9l), the CIT-P's independent review (CAP-33), read-only

You are a fresh reviewer. Ticket `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`, at the head `<HEAD>`, and its acceptance tests pass. It is a judge change, so it needs one independent review of its change-impact proposal, `docs/changes/W2-59-CIT-P.md`, and of the final code, before the owner approves it (CAP-33). You probe that head for behaviour the tests miss. **You write nothing.** You wrote none of this code (DEC-137).

Probe the final code for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. Write nothing except the probe record the lead names. Return each finding as a described behaviour, with its severity.
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). The full text is `governance/project/briefs/JUDGEMENT.md`, which this brief carries word for word.
- You read everything, tests and code alike (DEC-820); you commit nothing (DEC-826 Q3).

"The probe record the lead names" is, for you, no file: you return its content in your final message, and the lead writes and commits it (DEC-733).

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

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kh9l`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`) and `git rev-parse HEAD` (expect `<HEAD>`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test. (A probe of the pinned judge itself builds a stand-in pin from this worktree in your temporary folder, as the ticket's acceptance tests do; never touch the owner's pin under `~/.local/`.)
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return which questions you asked and whether the answers helped.
- **Reads are open (DEC-820, Policy 2).** Reviewers read everything: tests and code alike. Four things stay refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on a ticket, for its counterpart: the engineer never reads `tests/acceptance/W2-59/`, the test designer never reads this ticket's implementation (this binds those two roles, not you); (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Name the files you need under `governance/project/` one by one. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`, in this worktree or anywhere.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing (a virtual environment a probe makes in your temporary folder, installing only a wheel built from this worktree with `--no-index`, is not an install). No push, merge, rebase or tag. Never `sudo`.
- **Never copy the repository or a folder of it** (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch, with single named files copied in. Build a wheel without writing into this worktree (the acceptance tests' support file under `tests/acceptance/W2-59/` shows a form that keeps the source tree clean).
- Nothing under a `.gov-runtime/` folder (DEC-673), in `~/.local`, or in `~/gov-os-workbench`; never list or read `~/gov-os-workbench`. Dev-tier probes use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855).
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kh9l.md` (read-only): its KPI lines and its `allowed_paths` (`src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/retrieval/retrieve_check.py`, `src/gov/cli/main.py`, `pyproject.toml`, `.rulesync/hooks.jsonc`, `tests/unit/check/**`, `tests/unit/cli/**`, `tests/unit/retrieval/**`, `docs/changes/W2-59-CIT-P.md`).
- The sources, in `docs/DECISION_REGISTER.md`: DEC-822, DEC-835, DEC-854, DEC-831, DEC-864; and DEC-732, DEC-579, DEC-750, DEC-754, DEC-853, DEC-491, CAP-33 (`docs/contract/`), ADR-0001.
- The CIT-P, `docs/changes/W2-59-CIT-P.md`; the ticket's acceptance tests `tests/acceptance/W2-59/`; the code at the head (`git diff w2/integrate...HEAD` names this ticket's changes; `git log --oneline c5100159..HEAD` its commits).
- **The merge-back:** `3eadca4c` is this branch's merge of `w2/integrate` at `74d22909` (W2-62's session-start hook change, W2-50's secrets-scan fix and others). Its message lacks DEC-750's `Task:`/`Role:` trailers and names `DAEO-kl9l` by a typing error; `6d4925ab` records the correction (no amend). Judge whether it is git's own merge of its parents (`git merge-tree --write-tree 3eadca4c^1 3eadca4c^2` against `3eadca4c^{tree}`), whether it drops anything of either side, and what the missing trailers mean for the close's gates (`src/gov/close/`).
- **The three earlier cases revised (DEC-864 item 1), commit `45c6bfae`:** `tests/acceptance/W1-26/test_w1_26_planted_defects.py::test_planted_authority_defect_decision_checker_exception_not_swallowed`, `tests/acceptance/W1-22/test_w1_22_canaries.py::TestCanaryRunner::test_lexical_canary_hits_after_reindex` and `::test_semantic_canary_hits_after_reindex`. Judge whether each still guards its behaviour (an exception in the decision checker is never swallowed; canaries hit after a reindex), no expectation was lowered, nothing else changed, and the W1-26 plant cannot pass vacuously.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

In this change in particular (run the code; do not judge it by reading alone; a finding you could not reproduce is marked as such):
- **The judge (DEC-822 item 3):** does every declared check run with the judge's own interpreter and package, whatever the project holds (a `src/gov`, a `gov/` at its root, a decoy `python3` or `gov` on `PATH`)? Does any path let a project's code change an installed judge's verdict in ordinary work? Does the per-command `PYTHONPATH` still choose the code under test as DEC-732 needs?
- **The hook lines (DEC-822 step 2):** run each line of `.rulesync/hooks.jsonc` through `sh -c` as Claude Code does. With the pin present, through the link and through `PATH`; with it missing; with a link whose target is gone; with `HOME` unset or different. Is the preToolUse line ever not blocking when the pin cannot be found or its interpreter cannot run? Does `gov launch` still recognise the guard? Does W2-62's session-start hook (merged in) still run under the new line?
- **The project root (DEC-835):** do the canary runner and the retrieval-regression check read only the project under check, in both kernel layouts (DEC-579), from an installed wheel? Is any other module still finding repository files from its install path?
- **The baseline and `gov --version`:** shipped and read from an installed wheel; never a wrong commit.
- **The CIT-P:** is every statement in it true of the head (what changes, what stays, the risks, the rollback, the owner acts and their order, the decided packages as rows W2-M388, W2-M389, W2-M390, W2-L371)? Is anything the change does missing from it?

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work or fails open, with its two lines (`Ordinary work: …`, `Consequence: …`). Say also what you probed and found sound. The lead passes findings to a test designer; you repair nothing (MR-4).

**Your payload, after the twelve fields: the probe record's full content, ready to commit,** in this form (front matter first, then the body):

    ---
    type: probe
    task: DAEO-kh9l
    reviewer_session: <your session id, from `printenv CLAUDE_SESSION_ID` or your session's own id; say which>
    implementer_session: 5b7defda-73f6-4543-a7a2-b374758dcce5
    reviewer_wrote_nothing: true
    commissioned_by: orchestrator
    judged_by: orchestrator
    judgement: <pass | fail>
    probed_commit: <the full 40-character id of the head you probed>
    ---

    # Probe record: W2-59 (DAEO-kh9l), the CIT-P review

    - **What was probed:** …
    - **What it found:** findings first, most severe first, each with its two lines; then what was sound.

`judgement: fail` only if a finding is "Ordinary work: yes" with "Consequence: fails open" or "loses work"; otherwise `pass`. (`implementer_session` is the run-1 engineer's, who wrote the code; the run-2 engineer `60f94512-08b4-4f38-b076-d119f53a949e` changed only the CIT-P.)

Also give: the sandbox check's result (first in `evidence`), the `gov.__file__` line, the number of guard read refusals you met, and the `gov retrieve` questions you asked.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
