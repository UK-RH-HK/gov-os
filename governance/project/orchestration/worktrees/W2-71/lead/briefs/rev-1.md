You are a fresh reviewer. Ticket DAEO-e8f0 (W2-71), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-71` on branch `w2/W2-71`, at the head `700102de5f4d`, and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. **Above all: can any real token pass?** You write nothing; you return the probe record's content, which the lead writes and commits. Return each finding as a described behaviour, with its severity. Your time budget is about 90 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-e8f0','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (the twelve fields below), saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-e8f0`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-71` and `w2/W2-71`), and `git rev-parse --short=12 HEAD` (expect `700102de5f4d`). If anything differs, stop and say so.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

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

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag.
- **Reads (DEC-820, Policy 2):** you read everything, tests and code alike. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it; never read or name the qualification oracle); (c) the counterpart's work applies to the test designer and the engineer, not to you; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return. Never read `.claude/settings.json`.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.
- **Row W2-L423's rule (owner, standing, DEC-911).** One gitleaks default rule takes a bare 40-hex string for a token when one of its two keywords stands in the same text. Its vendor's name is written here only in two parts, `"source" + "graph"`; its rule id is that name followed by `-access-token`; its two keywords are that name and `"sgp" + "_"`. In your messages, your commands' output you quote, and your return, **the rule's id and its two keywords are written only in parts**, never whole, in any case; commit hashes are written as 12 digits. Call it "row W2-L423's rule". Probe tokens are built at run time from parts or random hex in your temporary folder, never printed.
- **Protected material:** never print a secret. Never write in `~/gov-os-workbench`. Never copy the repository or a folder of it; a probe that needs a repository builds a temporary one from scratch in your temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Disk (DEC-898):** your share of the ticket's scratch budget is 2 GB and 100,000 files and folders. Do not set `TMPDIR` (the sandbox sets your temp folder). Remove what you make.
- **The machine:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run at most a single test file at a time and no suite; small probes are fine.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-e8f0.md`: its KPI lines and its `allowed_paths` (`src/gov/secrets/**`, `tests/unit/secrets_check/**`). The card W2-71 in `docs/plan/WAVE_2_WBS.md` §2; row W2-L423 in `docs/plan/WAVE_2_LIST.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-911 (item 4 above all), DEC-298, DEC-347, DEC-853, DEC-290, DEC-909, DEC-897, DEC-801 to DEC-809, DEC-413.
- The ticket's acceptance tests (`tests/acceptance/W2-71/`, with its README) and the code at the head to probe: `git diff w2/integrate...HEAD -- src/gov/secrets tests/unit/secrets_check`.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could make the secrets-indexing check or the pre-index filter fail open:

- any real token of any rule let through, in a file or a stored value (a SQLite value, an FTS page, freed space, a UTF-16 text), for the check and for the filter and the path-name judgement;
- a match let through that names no commit object of the repository being scanned (another repository's commit, a tree, a blob, a tag, an abbreviation, a 40-hex string beside a real commit's, a token that shares a line or a gitleaks fragment with an exempt hash);
- a verification that cannot run, errs or hangs, passing as clean; git asked of another repository than the project's (the environment, a parent repository, a linked worktree);
- a match or a finding printed, logged, put in an exception message or written to a file; a report file left anywhere; the clean-result record holding a finding or a clean verdict it should not keep;
- a file the check scanned before no longer scanned, a rule set skipped, an allowlist added, a scan that cannot finish passing as clean;
- the rule's id or a keyword written whole in a tracked file this ticket changed;
- the check's time: the verification within the existing limits.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound. Give, after the twelve fields, **the probe record's content** in Markdown, the body the lead puts under the record's front matter (the lead writes the front matter: type, task, sessions, judgement, probed commit): a heading, what was probed (the head, the diff), step 0's result, `Verdict: pass` or `Verdict: fail` (fail only for a finding with "yes" and "fails open" or "loses work") with the classification of every finding on one line (DEC-809), then each finding with its two lines, and what was found sound. Write commit hashes as 12 digits and the rule's keywords only in parts.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Refused twice for the same call: stop and say so.
