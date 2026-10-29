You are a fresh reviewer (brief A3 of the Wave 2 prompt). Ticket `DAEO-2gc7` (W2-68), "Batched closes, reuse on the same code, and two fingerprints", profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-68` on branch `w2/W2-68`, at the head `fd88e61072eb`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing: no file of the repository, no commit; your findings and the probe record's content are in your final message.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-2gc7`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-68` and `w2/W2-68`), and `git rev-parse --short=12 HEAD` (expect `fd88e61072eb`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another, each well inside the tool's time limit; nothing started in the background is ever read.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no commit, no write in this worktree. No subagents that write. Install nothing. No push, merge, rebase or tag.
- Never copy the repository or a folder of it (no recursive copy, sync, archive, second worktree or clone of this repository). A probe that needs a repository builds a temporary one from scratch in your sandbox's temporary folder (W2-66's and W2-68's acceptance support modules build such projects; import them, never copy them). Remove what you build when done.
- Run no glob, no search and no listing over `governance/project/` (name the files you need there one by one); never read `.claude/settings.json`. Never read the held-out material's contents, never read or name the qualification oracle, never print a secret. Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try.
- **The machine:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `.../CLOSE-RUNNING` exists, run at most a single test file; before any test run, wait while the 1-minute load is above 20. Every multi-test run carries `-o tmp_path_retention_policy=failed`; do not set `TMPDIR`. Run the code under test with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src` set per command, and show `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory:** for what you need to know, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src python3 -m gov.cli.main retrieve "<question>" --json` (in batches for a large question, never one giant query); a code question uses the code-graph tool's own small traversals. Say whether you used it.
- **Row W2-L423's rule:** in your return, write commit hashes as 12 digits, except the `probed_commit` line of the probe record, which takes the full id.

## What you read

You read everything (DEC-820): tests and code alike.

- The ticket file `.tickets/DAEO-2gc7.md`: its KPI lines (success and failure) and its `allowed_paths` with their limits.
- Its card in `docs/plan/WAVE_2_WBS.md` §2, and in `docs/DECISION_REGISTER.md`: DEC-883, DEC-884 item 4, DEC-889 items 2 and 4, DEC-890, DEC-880, DEC-899, DEC-936, DEC-487, DEC-757.
- The design note `docs/research/W2-68-batched-close.md` (its sections 11 and 12 hold over the earlier ones).
- The change: `git diff w2/integrate...HEAD` (new `src/gov/close/batch.py`, `src/gov/close/fingerprint.py`; `src/gov/close/command.py`, `src/gov/close/repo.py`, `src/gov/store/`), its builder tests, and the acceptance tests `tests/acceptance/W2-68/` with their README.
- W2-66's selection and evidence it builds on: `src/gov/close/select.py`, `evidence.py`, `nightly.py`, `governance/project/test-map.yaml`.

## What you probe for

Behaviour the acceptance tests miss, **above all any path that lets a close pass on a red run, on another fingerprint's run, or on a run on different code.** Then: a store accepted on another code fingerprint; a lexical index taken as fresh with changed records; a fingerprint that leaves out code (the path map and the test map above all) or that a commit's record-only list can be made to hide by ordinary edits; a cut run, a run without its JUnit XML, or a run with a failure being reused; reused evidence that hides a skip; a red that passes alone being bisected; a governance check result of another code being stated in place of the close's own; a batch that closes a ticket after a refusal or on a red run; and anything that could lose work (the batch's commits, its store loads, a refused close's leftovers). Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Judgement rules (word for word, `governance/project/briefs/JUDGEMENT.md`)

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


## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the twelve fields, the payload: **the probe record's full content**, ready for the lead to write to `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md`: a YAML frontmatter (`type: probe`, `task: DAEO-2gc7`, `reviewer_session: <your session id if you know it, else "see the lead's note">`, `reviewer_wrote_nothing: true`, `commissioned_by: orchestrator`, `judged_by: orchestrator`, `judgement: pass` or `fail`, `probed_commit: <the full id of the head>`), then the head probed, the method (what you ran), what you found sound, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only a finding with "yes" and "fails open" or "loses work" fails the probe. Your `evidence` line also gives the `gov.__file__` line, whether you used `gov retrieve`, and the read refusals you met.
