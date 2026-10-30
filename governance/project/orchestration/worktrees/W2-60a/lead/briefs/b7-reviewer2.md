You are a fresh reviewer (brief A3), for review 2, the ticket's last (DEC-413). Ticket DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`, at the head `e34e07b7ce32`, and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard or the launcher fail open. **You write nothing:** no file of the repository, no commit. You return the probe record's content in your final message; the lead writes it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a` and `w2/W2-60a`), and `git rev-parse --short=12 HEAD` (expect the head above). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, rebase, merge, push or tag. Write no file of the repository. No subagents that write.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used it.
- **Reads (DEC-820):** you read everything, tests and code alike. Refused only: (a) secrets and keys, never printed (the CLI's credentials file under `~/.claude/` included); (b) the contents of the held-out qualification material (its names may be seen), and never read or name the qualification oracle; (d) the hidden half of any evaluation set. **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`): take the refusal, never another form, search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. A probe that needs a script or a repository writes it in your session's own temp folder (`$TMPDIR` as the launcher set it; use its literal path) with the Bash tool's `printf` into a literal path, or not at all; never in the worktree. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try.**
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`); a probe repository is built from scratch in your temp folder, copying single named files only, never `governance/project/`. Never write in `~/gov-os-workbench`. Install nothing.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in your return write commit hashes as 12 digits (the lead expands the probed head in the record it writes), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** your share is 2 GB and 100,000 files and folders; your temp folder goes when the session ends.
- **The nightly (DEC-933, DEC-936):** before each test run, check with `test -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING`; while it exists (from 02:00 most nights), run at most a single test file at a time, never a suite. Run no whole suite in any case: single files and your own probes only.
- Your sandbox has no network: you cannot start a live Claude session. You probe the launcher with a stand-in CLI (as `tests/acceptance/W2-60a/w2_60a_support.py` and `tests/acceptance/W1-46/w1_46_support.py` build one: a program at `<test home>/.local/bin/claude` that records its arguments, environment and settings), and you read the live facts from the research record.

## What you read

- The ticket file `.tickets/DAEO-cv58.md`: its KPI lines, failure lines and `allowed_paths` (src/gov/launch/launcher.py, src/gov/launch/role.py, src/gov/launch/record.py, tests/unit/launch/test_role*, tests/unit/launch/test_launch_record*, docs/changes/W2-60a-CIT-E.md, docs/research/W2-60-rules-probe.md).
- **The design and the measurements:** `docs/changes/W2-60a-CIT-E.md` (the whole note) and `docs/research/W2-60-rules-probe.md` (the lead's live measurements).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-826 (Q1, Q5), DEC-838, DEC-839, DEC-832, DEC-801, DEC-786, DEC-941; today's launcher refusals DEC-313, DEC-218, DEC-233, DEC-315, DEC-386, DEC-392, DEC-728, DEC-743, DEC-751, DEC-873; ADR-0001 (`docs/adr/ADR-0001-threat-model.md`).
- W2-56's ticket `.tickets/DAEO-wnnz.md`, its paragraph "Beside W2-60a" (what is W2-56's, not this ticket's).
- The ticket's acceptance tests `tests/acceptance/W2-60a/` and the earlier tests it revised (`git diff --stat a1629f1860ca e34e07b7ce32 -- tests/`), and the code at the head: `git diff a1629f1860ca e34e07b7ce32 -- src/`.

## Review 1 and round 2 (what changed since)

Review 1 (head 3b32a1070af1) failed on two findings, fixed in round 2 (tests 8379a8c66f79, code 3f0aaa5ed70d, note e34e07b7ce32):
- F1: the project's command files under `.claude/commands/` were loadable skills that no launch record named;
- F2: `--setting-sources project,local` dropped the owner's user-level `permissions.ask` and `permissions.deny` rules (an `rm` that a `-p` worker is asked for today, and so refused, would have run).
Ride-alongs (DEC-802): further compaction spellings in the repository's settings, and `--fallback-model`, `--chrome`, `--ide`, `--system-prompt-snapshot` refused after `--`. Review 1's rows (R1's other options, R3 to R6, F3, E1) are residuals the lead returns; do not re-raise them unless round 2 changed them. **Probe round 2's changes above all**, then everything the list below asks, at the new head.

## What you probe for

Above all, **whether any path lets a launch start with:**
- no role text (the role file's text not appended, or appended from another file than the one recorded);
- a skill unrecorded, or recorded from another copy than the one the session loads;
- a model other than the role's (any spelling after `--`, a settings file, the environment the launcher builds);
- a compaction threshold (any spelling the launcher's line, its settings or the repository's settings could carry; the process environment is W2-56's: name it, it is not this ticket's finding);
- a user-level agent, skill or connector, or model-side memory.

**Also:** whether a launch record can be missing, be written after the start, or name another session (including a resume, and a resume of a session started before this change); whether a record or its folder can be written by the session; and **whether any refusal the launcher makes today no longer refuses** (DEC-313's, DEC-218's, DEC-233's, DEC-315's, W2-58's (DEC-873), the role and ticket checks, the signal handling of DEC-392 and the temp folder of DEC-386).

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Say also what you probed and found sound.

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

Your last message, complete in itself. The twelve fields come first, each as a labelled line. Then: the step-0 result; the head you probed; **the probe record's content**, in this form, ready for the lead to write:

```
---
type: probe
task: DAEO-cv58
reviewer_session: <your session id, from the environment or the CLI's log; else "not known">
implementer_session: e4fca52c-08d5-47ca-833c-2a068fbca603
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator role)
judged_by: ticket lead (orchestrator role)
judgement: <pass | fail>
probed_commit: <the head, 12 digits; the lead writes it in full>
---

# Probe record: W2-60a (DAEO-cv58), review 2

## Summary
<what was probed, by whom, how>

## Findings
<each finding: what was done, what happened, what should have happened, its severity, and the two lines
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`>

## Probed and found sound
<each probe that found nothing>
```

A finding is a described behaviour, never code (DEC-136). The judgement is `fail` only when a finding has "Ordinary work: yes" with "Consequence: fails open" or "loses work".

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

The twelve fields come first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
