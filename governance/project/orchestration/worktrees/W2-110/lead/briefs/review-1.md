# Brief: reviewer (FULL, read-only), W2-110 (DAEO-3r1j), review 1

You are a fresh reviewer. Ticket `DAEO-3r1j` (`W2-110`), profile FULL, is implemented in the worktree
`/home/usain/gov-os-worktrees/W2-110` on branch `w2/W2-110`, at the head `1920abfa17bf`, and its acceptance tests
pass (179 of 179). You probe that head for behaviour the tests miss. You write nothing. You are a headless session:
nobody answers questions while you work, and only your final message is read.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-3r1j','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-3r1j`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-110` and `w2/W2-110`), and
`git rev-parse --short=12 HEAD` (expect `1920abfa17bf`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src` set per command
  (never in a session's `--settings` env). Show it once with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -c "import gov; print(gov.__file__)"`.
- **Retrieval (DEC-836):** use `gov retrieve`
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -m gov.cli.main retrieve "<question>" --json`) for what
  you need to know before reading files at random. Never one giant query or context (DEC-860): a large question is
  taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked. A code question uses the
  code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of
  the whole graph (DEC-859).
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Only these are refused: (a) secrets and keys,
  never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read
  or name the qualification oracle; (c) does not bind a reviewer, who reads both the tests and the code; (d) the
  hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that
  start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form,
  search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no
  backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. A probe script goes in your temporary
  folder (`/tmp`), written there by a command the guard can read, or use short `python3` lines.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another. You write nothing, so no commit of yours will exist:
  return when your findings are complete.
- Write no file of the repository and make no commit. No `git checkout` of another commit, no `git reset`, no
  `git clean`. No subagents that write. Install nothing (a probe's install command is only text in a hook's input,
  never run). No push, merge, rebase or tag. Never ask or notify the owner.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A probe
  that needs a project builds a temporary one in your temporary folder: a project generated from the template, as the
  acceptance tests' support does (copier, then rulesync generate), or a small project with single named files copied
  (the kernel hook, a `.tickets/` folder you write, a roster you write). Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists:
  conclude nothing from it; a probe of the freeze makes the flag in its own temporary project.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits in your return (the probe record's
  `probed_commit` alone is the full id), and never write the keywords of the gitleaks rule that takes a bare 40-hex
  string for a token.
- **Your scratch budget (DEC-898):** 4 GB and 200,000 files and folders, in your temporary folder; remove what you
  made when it is no longer needed and give the figures (`du -s --inodes`, `du -sh`) in `evidence`.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; you read the tests, the code and the lead's
  results, and you run the code itself with your own probes.

## What you read

- The ticket file `.tickets/DAEO-3r1j.md`: its KPI lines and its `allowed_paths`
  (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/install.py`, `tests/unit/guard/test_w2_110*`,
  and the test designer's `tests/acceptance/W2-110/`).
- The sources: DEC-971 (item 4), DEC-957 (the install rule: only the CTO's own session asks the owner), DEC-966
  (item 1), DEC-163 (the research exception), DEC-083 (DEC-040 amended) in `docs/DECISION_REGISTER.md`;
  `governance/project/orchestration/packages/P1-MORNING-2026-10-31.md` item 4.
- The model: this repository's own five-rule hook, `.claude/hooks/pretooluse.py`, rule 4.
- The change: `git diff 695eea48139f 1920abfa17bf` (the ticket's base to the head), the acceptance tests and their
  README, the builder tests.
- The lead's design: the coordination ticket is named by the top-level key `coordination_ticket` in the project's
  `governance/project/roster.yaml`, by the ticket's id or its WBS id; the CTO is the orchestrator session (acting as
  the orchestrator) on that ticket; everyone else is refused and told to escalate as a P1; no usable key refuses
  every install; sudo, the research exception, the freeze and the owner's prompt are unchanged.
- The lead's results on `5bdde1e9d5c6` (the code; `1920abfa17bf` adds only a checkpoint record): the acceptance suite
  179 passed; builder tests 59 passed; the scoped selection (select_tests.py, scope `scoped`) 11194 passed, 95
  failed, 324 errors, 1 skipped; the selected serial-only cases 5 passed; W1-38 and W1-39 272 passed; `gov check`
  green but two YELLOWs not this ticket's (core-decision-citations, openspec-validate). Every red is either an earlier
  test that still expects the old rule (any orchestrator asked, with no coordination-ticket key: W1-04's 324 setup
  errors, W1-47's uv-install asks 81, W1-50 5, W1-03 2, W1-46 1, `tests/unit/install/test_install.py` 5), which goes
  to the CTO as a package, or one W1-46 research case that fails on the base too. Iteration 1 had a regression this
  head repairs: the hook imported the new rule for every Bash call, so a project whose pinned `gov` is older than its
  hook refused every Bash call with exit 2; now only installs need it, and an install refuses when it is missing.
  Note: the older acceptance harnesses (W1-46, W1-47) run the template hook under the owner's pinned `gov`, not this
  worktree's `src/`; the W2-110 suite runs this worktree's code.

## What you probe for

Behaviour the acceptance tests miss, above all:

- **any install let through, or asked, in a session other than the CTO's** (a lead, a worker, a subagent, a session
  with no role or no ticket, a ticket named in another form, two tickets with the same WBS id, a ticket file that is
  a link or unreadable, a ticket id with odd characters or spaces, the key's value with odd spacing or quoting);
- **a missing, empty, broken or unreadable key that fails open** (an ask, an allow, a crash the harness lets
  through: an exit code other than 0 or 2, an output that is not a decision, a hook that runs past its deadline);
- **anything else in the install rule that changed:** sudo, the research exception inside and outside its experiment
  folder, a frozen project, the owner's prompt and its record and before-snapshot, a Bash call that is no install,
  the order of the rules;
- whether the change stays inside the ticket's paths and touches only the install decision's range of
  `src/gov/guard/install.py` (a shared file, also in W2-05's paths).

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. In them: the sandbox check; the `gov.__file__` line; the head you probed; each finding as a described
behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, with its
two lines (`Ordinary work: …`, `Consequence: …`); what you probed and found sound; whether you used `gov retrieve`;
read refusals met; your scratch figures; and your verdict, pass or fail, by the rule above.

**After the twelve fields, the probe record's full text** for the lead to commit, between the lines
`--- PROBE RECORD BEGIN ---` and `--- PROBE RECORD END ---`, in this form (front matter first):

```
---
type: probe
task: DAEO-3r1j
reviewer_session: <your session id, or "unknown" with why>
implementer_session: 0047deab-bb2b-4ee5-b6f8-23852a7fab6d
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: <pass | fail>
probed_commit: <the full commit id of the head you probed>
---

# Probe record: W2-110 (DAEO-3r1j)

- **What was probed:** …
- **What it found:** each finding, with its two lines …
- **Sound:** …
- **Verdict:** …
```

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
