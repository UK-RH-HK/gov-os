You are a fresh reviewer (brief A3), for review 3, the ticket's last (DEC-951 item 4: the owner's exception to DEC-413; there is no fourth round). Ticket DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`, at the head `0e11b5db743d`, and its acceptance tests pass (the lead's results are below). You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard or the launcher fail open. **You write nothing:** no file of the repository, no commit. You return the probe record's content in your final message; the lead writes it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-cv58`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a` and `w2/W2-60a`), and `git rev-parse --short=12 HEAD` (expect the head above). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, rebase, merge, push or tag. Write no file of the repository. No subagents that write.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used it.
- **Reads (DEC-820):** you read everything, tests and code alike. Refused only: (a) secrets and keys, never printed (the CLI's credentials file under `~/.claude/` included); (b) the contents of the held-out qualification material (its names may be seen), and never read or name the qualification oracle; (c) does not bind you (you are the reviewer, not a counterpart); (d) the hidden half of any evaluation set. **DEC-849:** if the guard refuses a read, take the refusal, never another form, search named folders instead, and count the refusals in your return.
- **Command forms:** a probe that needs a script or a repository writes it in your session's own temp folder (`$TMPDIR` as the launcher set it; use its literal path), never in the worktree. A refused command is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try.**
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree` of this repository, `git clone`); a probe repository is built from scratch in your temp folder (a `git worktree add` of that probe repository is allowed), copying single named files only, never `governance/project/`. Never write in `~/gov-os-workbench`. Install nothing.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in your return write commit hashes as 12 digits (the lead expands the probed head in the record it writes), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** the ticket's budget is 20 GB and 1,000,000 files and folders; your share is 2 GB and 100,000; your temp folder goes when the session ends.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite. You read the tests, the code and the lead's results below; you run your own probes (with a stand-in CLI), and a single test file only where a probe needs it.
- Your sandbox has no network: you cannot start a live Claude session. You probe the launcher with a stand-in CLI (as `tests/acceptance/W2-60a/w2_60a_support.py` builds one: a program at `<test home>/.local/bin/claude` that records its arguments, environment and settings). The CLI's own behaviour you read from its code and help, marked so. Your time budget is about 100 minutes.

## What you read

- The ticket file `.tickets/DAEO-cv58.md`: its KPI lines, failure lines and `allowed_paths`.
- The design, `docs/changes/W2-60a-CIT-E.md` (its round 3 section above all), and `docs/research/W2-60-rules-probe.md`.
- **Review 2's record (failed):** `/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/probes/PR-DAEO-cv58-review2-DRAFT-fail.md` (F1 and its residuals R1 to R9).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-951 (item 4), DEC-413, DEC-826 (Q1, Q5), DEC-838, DEC-839, DEC-233, DEC-313, DEC-801, DEC-786; ADR-0001 (`docs/adr/ADR-0001-threat-model.md`).
- Round 3's change: `git diff e3bdc0cba595 0e11b5db743d` (code `1b32b5b24d40`, tests `7bbfd34f85ba`, `cb8f1b6088ef`, `22ceb1e241a0`, `0c0b2549db06`), and the whole ticket's code at the head: `git diff a1629f1860ca 0e11b5db743d -- src/`.

## Round 3: the five items, and nothing else (DEC-951 item 4)

- **(i)** For a launch from a linked worktree, the repository-settings check also reads the main checkout's `.claude/settings.local.json` (the file CLI 2.1.292 loads as a worktree session's local settings), and refuses on it exactly what it refuses on the tree's own copy (DEC-233, DEC-313, the hooks check, the agent key, every compaction spelling). Fail closed: a main checkout that cannot be found, or a local file there that exists and cannot be read or parsed, refuses with the cause; the look-up is `record.py`'s (now `main_checkout`). A main checkout with no local file adds no refusal; a launch from the main checkout is unchanged.
- **(ii)** In a tree with no `template/`, the role file is read from `governance/kernel/roles/<role>.md`; the recorded path and hash are those of the file read.
- **(iii)** Fixture role files for 26 unit cases in `tests/unit/launch/` (`test_runs.py`, `test_w1_28.py`, `test_w1_32.py`); nothing else in those cases changes.
- **(iv)** The nightly-route line for `tests/acceptance/W2-60a/test_w2_60a_live_sessions.py` in `tests/acceptance/serial-only.txt`.
- **(v)** W2-58's live phantom-deletion fixture writes its role file before the fixture's commit.

**The lead's results at this head:** the red check at the base (tests worktree, code before round 3): the 10 new cases red for their README reasons (9 "did not refuse", the adopted case refused for want of `template/governance/kernel/roles/engineer.md`); the 26 unit cases 26 passed; W1-30 r11 50 passed; W2-57 serial list 2 passed. At `a600fdfd2fe9` (this head less the checkpoint record): the new file, the 26 unit cases and the builder tests 116 passed; the engineer's run of the older W2-60a cases 200 passed and 1 failed (W2-56's known case, the caller's `CLAUDE_CODE_AUTO_COMPACT_WINDOW` reaching the session's process); W2-58's phantom-deletion pair run live, alone, by the lead: 2 passed. The scoped selection (scope `scoped`, no core change) is queued on the machine's gate and runs beside you; its results go into the lead's return.

## What you probe for

**Above all: whether any route reaches a worker's local settings unchecked:**
- a worktree launch, and the main checkout's file;
- a launch from the main checkout;
- a `.git` file that points elsewhere (another repository, a missing directory, a relative `gitdir:`, a `commondir` file);
- a main-checkout file that is a link, unreadable, not JSON, or names a key in another spelling;
- the tree's own file;
- settings or setting sources given after `--`.

**Also:**
- whether the adopted layout lets a launch take role text from anywhere but the file it records (a `template` that is a file or a link, both layouts present, neither present);
- whether any refusal the launcher makes today no longer refuses (DEC-313's, DEC-218's, DEC-233's, DEC-315's, W2-58's (DEC-873), the role and ticket checks, the record's, the signal handling of DEC-392 and the temp folder of DEC-386), including the order in which a broken `.git` is now refused;
- whether (iii) or (v) lowers an expectation of the cases they touch.

Review 2's residuals (R1 to R9) and review 1's stay residuals: do not re-raise them unless round 3 changed them. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Say also what you probed and found sound.

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
implementer_session: 100abccd-a36a-469a-9b37-2a9b35a7e109
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator role)
judged_by: ticket lead (orchestrator role)
judgement: <pass | fail>
probed_commit: <the head, 12 digits; the lead writes it in full>
---

# Probe record: W2-60a (DAEO-cv58), review 3

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
