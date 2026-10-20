# Brief: reviewer — W2-59 (DAEO-kh9l), the CIT-P's second and last independent review (CAP-33, DEC-413), read-only

You are a fresh reviewer. Ticket `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`, at the head `@@HEAD@@`, and its acceptance tests pass. It is a judge change, so its change-impact proposal, `docs/changes/W2-59-CIT-P.md`, and the final code need an independent review before the owner approves it (CAP-33). A first review failed on one finding (F1), since fixed. **This is the second and last review (DEC-413):** nothing is committed after the head you probe except your probe record. You probe that head for behaviour the tests miss. **You write nothing.** You wrote none of this code (DEC-137).

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

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kh9l`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`) and `git rev-parse HEAD` (expect `@@HEAD@@`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test. (A probe of the pinned judge itself builds a stand-in pin from this worktree in your temporary folder, as the ticket's acceptance tests do; never touch the owner's pin under `~/.local/`.)
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return which questions you asked and whether the answers helped.
- **Reads are open (DEC-820, Policy 2).** Reviewers read everything: tests and code alike. Four things stay refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on a ticket, for its counterpart: the engineer never reads `tests/acceptance/W2-59/`, the test designer never reads this ticket's implementation (this binds those two roles, not you); (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Name the files you need under `governance/project/` one by one. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`, in this worktree or anywhere.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit (never of the branch `w2/W2-59-old`), no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing (a virtual environment a probe makes in your temporary folder, installing only a wheel built from this worktree with `--no-index`, is not an install). No push, merge, rebase or tag. Never `sudo`.
- **Never copy the repository or a folder of it** (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch, with single named files copied in. Build a wheel without writing into this worktree (the acceptance tests' support file under `tests/acceptance/W2-59/` shows a form that keeps the source tree clean).
- Nothing under a `.gov-runtime/` folder (DEC-673), in `~/.local`, or in `~/gov-os-workbench`; never list or read `~/gov-os-workbench`. Dev-tier probes use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists, and `git status` may list sandbox placeholder files at the worktree's root: conclude nothing from either.
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855).
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kh9l.md` (read-only): its KPI lines and its `allowed_paths` (`src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/retrieval/retrieve_check.py`, `src/gov/cli/main.py`, `pyproject.toml`, `.rulesync/hooks.jsonc`, `tests/unit/check/**`, `tests/unit/cli/**`, `tests/unit/retrieval/**`, `docs/changes/W2-59-CIT-P.md`).
- The sources, in `docs/DECISION_REGISTER.md`: DEC-822, DEC-835, DEC-854, DEC-831, DEC-864, DEC-877; and DEC-412, DEC-413, DEC-732, DEC-579, DEC-750, DEC-754, DEC-853, DEC-491, CAP-33 (`docs/contract/`), ADR-0001.
- The CIT-P, `docs/changes/W2-59-CIT-P.md`; the ticket's acceptance tests `tests/acceptance/W2-59/`; the code at the head (`git diff w2/integrate...HEAD` names this ticket's changes; `git log --oneline --first-parent c76cddf5..HEAD` its commits).
- The first review's record (failed on F1), as the lead kept it: `/home/usain/gov-os-worktrees/W2-59/.gov-runtime/scratch/lead/probes/PR-DAEO-kh9l-rev1-DRAFT-fail.md`. Its F2 is answered by the remade history (below); its F3, F4, F5 and F7 are already rows W2-L375 to W2-L378 (DEC-877 item 5): do not raise them again unless the head changed them; its F6 (CIT-P text) was corrected in run 2.

## What is in scope

1. **F1's fix, commit `92f91614`** (the hook lines start each governance program with the pin's interpreter and `-E`; tests in `6e0bf627`; the CIT-P's count in `0c630012`). In every session, a launched worker's included (it inherits `PYTHONPATH=<worktree>/src`; your own session carries it), does each line of `.rulesync/hooks.jsonc` run through `sh -c` import the pin's installed package and never the tree's? Is the preToolUse line still blocking when the pin cannot be found or its interpreter cannot run? Is the owner's rollback to an editable install's own `gov` still followed? Does `gov launch` still recognise the guard? Does W2-62's session-start hook still run under the new line? Does `-E` drop anything a hook program or the pin needs?
2. **The remade history (DEC-412, DEC-877 item 1).** The orchestrator remade `w2/W2-59` from `c76cddf5`: the merge of `w2/integrate` at `74d22909` is now `e48a601d` (with `Task: DAEO-kh9l`, `Role: orchestrator`, `Implements: DEC-750, DEC-877`), in place of `3eadca4c`, which had no trailers; the ten later commits were re-applied unchanged: `6d4925ab`→`70cfbcf9`, `45c6bfae`→`912ddc63`, `fc8f8494`→`164d4c64`, `cface154`→`06250aee`, `9b9faac3`→`03727f84`, `6e95cd41`→`6e0bf627`, `e791465b`→`92f91614`, `3c2d88b5`→`0c630012`, `aa83876d`→`61d0a4a2`, `3d6a27f8`→`d3e594bf`. The old branch is kept read-only as `w2/W2-59-old` (read it with `git log`, `git show`, `git diff`, `git rev-parse`; never check it out). Judge: is `e48a601d` git's own merge of its parents (`git merge-tree --write-tree` of its two parents against its tree; expected `6b2943c8`)? Is each re-applied commit the same change, with the same author role and trailers, as the old one? Do the new head `d3e594bf` and the old head have the same tree? Does `gov close`'s work-without-a-task gate (`_check_unmeasured` in `src/gov/close/command.py`) still find anything in this branch's history that names no task (run it as the first review did, with the close's own functions, read-only)?
3. **Run 3's merge `3dbd766d`** of `w2/integrate` at `97fc656a` (W2-53's close, W2-63, the path map's `test_inputs`, DEC-865 to DEC-877): trailers (`Task: DAEO-kh9l`, `Role: orchestrator`, `Implements: DEC-750`), git's own merge of its parents, nothing of either side dropped, none of this ticket's files touched.
4. **The CIT-P at the head** (commit `a3aefd89` replaced the old ids with the new ones and added one paragraph on the remake; its brief allowed nothing else to change). Is every statement true of the head: what changes, what stays, the risks, the rollback, the owner acts and their order, the rows? Is anything the change does missing? Note: §4's "Two questions stay open" and §7's "Open, with the orchestrator" for P-W2-59-5, -6 and -7 predate DEC-877, which decided them (P-W2-59-5 (a) with row W2-M394; P-W2-59-6 (a), as built; P-W2-59-7 row W2-M393); judge that with the two lines like any other finding.
5. **Anything else this ticket's change does that the tests miss**, under the threat model: the judge running every declared check with its own interpreter and package whatever the project holds; the project root read from the project under check, not the install path (DEC-835), in both kernel layouts; the baseline and `gov --version` from an installed wheel.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work or fails open, with its two lines (`Ordinary work: …`, `Consequence: …`). Say also what you probed and found sound. You repair nothing (MR-4).

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

    # Probe record: W2-59 (DAEO-kh9l), the CIT-P's second review

    - **What was probed:** …
    - **What it found:** findings first, most severe first, each with its two lines; then what was sound.

`judgement: fail` only if a finding is "Ordinary work: yes" with "Consequence: fails open" or "loses work"; otherwise `pass`. (`implementer_session` is the run-1 engineer's, who wrote the code; the run-2 engineers `60f94512-08b4-4f38-b076-d119f53a949e` (the CIT-P) and `3837368c-8114-4589-8cd5-1f1aab31cfd3` (F1's fix) and the run-3 engineer `6777ce4f-51d3-4437-8669-ca80330b7ce5` (the CIT-P's ids) changed the rest.)

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
