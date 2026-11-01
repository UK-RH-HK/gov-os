You are a fresh independent reviewer (brief A3), read-only. Ticket: DAEO-k7hz (W2-11, "Briefs and the orchestration skill"), profile STANDARD, round 1 of two declared rounds (DEC-916). The ticket's round-1 work is on branch `w2/W2-11` in `/home/usain/gov-os-worktrees/W2-11`, head `095167b86fe3`, base `4c064bab02b4`. You judge its CIT-P, `docs/changes/W2-11-CIT-P.md` (CAP-33), for the owner's combined K3 CIT-P (DEC-954 Q7). You write nothing: you return the review record's content, and your lead commits it if it passes (DEC-733). Your budget: about 90 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work (if (b) is refused because your tools are read-only, say so; it does not stop you).
Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-k7hz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`). If anything differs, stop and say so.

## Your three questions (the lead's brief, step 3)
1. **Does any template, skill or role file still teach a superseded rule?** The files: `template/governance/kernel/templates/brief-*.md` (five), `template/governance/kernel/templates/skill.md`, `template/governance/kernel/skills/{orchestration,audit,test-design,qa-review}/**`, the version lines of every kernel skill, `template/governance/kernel/roles/orchestrator.md` (only DEC-866's sentences were in scope), and their rulesync sources (`.rulesync/`, `template/.rulesync/`). Superseded or changed rules to look for (DEC-866): `LEAD_CHECKPOINT` or a context-limit stop (DEC-838, DEC-837); a listing or search refusal over the governance folder or `.claude/`, or the held-out list's names unreadable (DEC-820, replacing DEC-508, DEC-525, DEC-557, DEC-162's "names a held-out path"); a fixed ceiling of tickets in flight (DEC-847); owner decisions recorded other than by decision-record commits (DEC-861, DEC-862); "tests first / written before implementation" where DEC-959 item 7 puts the work order in parallel; a full suite run outside the nightly (DEC-968); anything the register marks `SUPERSEDED by` or "Changed by". Check by value as well as by id.
2. **Does the skill template meet DEC-959 item 5** (and ROLES-RESEARCH-1 §2's opening): front matter (name, version, a third-person description of what and when); When / not when; Inputs; Steps as a checklist; Done when; Output and handover; Escalation (P3/P2/P1/Emergency); Never; Sources at the end; the body under about 150 lines with reference files one level deep; three test scenarios written before the text (check the commit order: scenarios in an earlier commit than the text); an imported skill adopted only licence-checked and passing its three scenarios. Does `qa-review` follow it?
3. **Do the kernel files carry nothing scoped to this repository** (W2 ticket ids, EXAMIN, this repository's main-tree paths and tools such as `select_tests.py`, `verify_lock.sh`, `disk_gate.sh`, `close_build.py`, `~/gov-os-worktrees`, this wave's figures given as the rule)? Such entries belong in the project prompt (the card's DEC-791 (ii) line, DEC-539).

Also judge, briefly: does the CIT-P state the evidence, the change (each file, versions before and after), its tests, impact, rollback, and what is outside this round, truthfully against the diff (`git diff 4c064bab..095167b86fe3 --stat` and the files)? Known and already packaged by the lead (do not re-find, but say if you disagree): the 16 generated copies under `.claude/` are not written (the launch sandbox denies `.claude/` writes); the generated copies can carry the version only as `metadata.version` (rulesync writes no top-level `version`; the launcher's reader, another ticket's code, reads `version`); the skill validator's failure KPI needs `src/`; DEC-808's schema fields are outside the paths; W1-35's `test_no_brief_is_named_like_a_record_template` contradicts W2-L258.

## What you read
Everything (DEC-820): the ticket `.tickets/DAEO-k7hz.md`, its card (`docs/plan/WAVE_2_WBS.md` §2, "#### W2-11"), `governance/project/orchestration/packages/ROLES-SPEC-1.md` (§3, §6.1 G13 to G15, §6.3, §7, §10), `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` (§2, §5.3), `governance/project/orchestration/packages/SWEEP-2026-10-20.md`, the register's DEC-959, DEC-866, DEC-820, DEC-861, DEC-862, DEC-847, DEC-837, DEC-838, DEC-430, DEC-808, DEC-791, DEC-951, DEC-957, DEC-968, DEC-981, the diff and the files, the tests (`tests/acceptance/W2-11/`) and their README. You re-run no suite (DEC-959 item 1); you may run single read-only commands (the skill validator, `git`, `grep`). Use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json` (in batches, never one giant query, DEC-860; a code question through the code-graph tool's own small traversals, DEC-859). Refused reads: (a) secrets, never printed; (b) the held-out material's contents; (d) the hidden half of any evaluation set; never read or name the qualification oracle. **DEC-849:** take a guard read refusal, never another form; count them.

**The code under test (DEC-732), word for word:** In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env).

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

For this review, a superseded rule still taught, a skill template that misses DEC-959 item 5, or repository-scoped text in a kernel file is a finding with severity; say for each whether it should block the CIT-P going to the owner. Findings are described behaviour, never code (DEC-136).

## The record's content (you return it; you write no file)
After the twelve fields, give the record in this form, for the lead to commit as `docs/probes/DAEO-k7hz/CITP-REVIEW-r1.md`:
```
---
type: probe
ticket: DAEO-k7hz
probed_commit: <the full 40-character id of the head you reviewed, from git rev-parse HEAD>
reviewer: independent-auditor (fresh session)
verdict: pass | fail
date: 2026-11-01
---
# CIT-P review, W2-11 round 1
## Scope
## Question 1: superseded rules
## Question 2: the skill template (DEC-959 item 5)
## Question 3: repository-scoped text in kernel files
## The CIT-P against the diff
## Findings (each: what, where, severity, Ordinary work: …, Consequence: …, blocks the CIT-P: yes|no)
## What was sound
```
(The full commit id belongs in this committed record, which the probe gate reads; in your return text outside the record, write commit ids as 12 digits.)

## Never
You write nothing, commit nothing, run no suite, install nothing, never ask or notify the owner. Commands the guard can read: no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. **Refused twice for the same call: stop and say so; no third try** (AR-6). On an authentication or access error, stop and return status `AUTH_REQUIRED`.

## Return
One message, your last. The twelve fields first, each as a labelled line; then the record's content; then `gov retrieve` use and the guard read refusals you met.

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

The twelve fields first, any payload after. Refused twice for the same call: stop and say so.
