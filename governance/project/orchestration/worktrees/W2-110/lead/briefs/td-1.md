# Brief: independent test designer, W2-110 (DAEO-3r1j), run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-3r1j` (`W2-110`), profile FULL. You work only in the
tests worktree `/home/usain/gov-os-worktrees/W2-110-tests` on branch `w2/W2-110-tests` (DEC-963). You never read or
write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-110`). You write the ticket's acceptance tests from
its KPI lines and its sources, in parallel with the engineer, and you show them red. You are a headless session:
nobody answers questions while you work, and only your final message is read.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-3r1j','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-3r1j`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-110-tests` and
`w2/W2-110-tests`). If anything differs, stop and say so. If your session starts in another folder, `cd` to the tests
worktree for every command.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src` set per
  command (never in a session's `--settings` env). Your tests, once merged into the ticket's worktree and run from
  there, must exercise that worktree's code: take every path relative to the test file
  (`Path(__file__).resolve().parents[3]`), never a fixed worktree path, and say how in your README.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>"`
  (a read; that store holds `w2/integrate` as of its last refresh, at most about half a day old). Never this ticket's
  worktree's store. For what changed since, read `w2/integrate` itself with `git show w2/integrate:<path>`. Never one
  giant query or context (DEC-860): a large question is taken in batches (`--batch-size`, then `--continue <token>`),
  ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`,
  `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/install.py`, `tests/unit/guard/test_w2_110*`),
  and name in your return any such result you were served.
- **Policy 2 (DEC-820), reads open, writes closed.** You read freely: the whole repository, git history, other
  worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out
  qualification material (its file names may be seen); never read or name the qualification oracle; (c) **the
  counterpart's work on this ticket: you never read this ticket's implementation** — the engineer's work in
  `/home/usain/gov-os-worktrees/W2-110` and any change on branch `w2/W2-110` to the three implementation paths above;
  you read the existing code only as it stands on `w2/integrate` (`git show w2/integrate:<path>`) or in your own
  worktree at its base (`695eea48139f`), which holds no implementation; (d) the hidden half of any evaluation set, by
  whoever is measured by it.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that
  start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form,
  search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no
  backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Put anything longer in a script file under
  `/home/usain/gov-os-worktrees/W2-110-tests/.gov-runtime/scratch/td/` with the Write tool and run that file. A
  refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another; return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this
  repository). A test that needs a repository builds a temporary one (a generated project from the template, as below,
  is built file by file the way W1-39's and W2-90's support code already does). Never write in `~/gov-os-workbench`;
  dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists:
  conclude nothing from it.
- Install nothing (a tool you need is returned as a package). No sudo. Never write `.gov-runtime/**` outside
  `.gov-runtime/scratch/`. No subagents that write. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never
  the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** 8 GB and 400,000 files and folders, outside the tracked tree, as your share of the
  ticket's 20 GB / 1,000,000. Your temp folder is the one the sandbox sets (keep it); otherwise
  `TMPDIR=/tmp/gov-os-lead-W2-110`. Keep pytest's own retention; never a per-run `--basetemp`; run pytest with
  `-o tmp_path_retention_policy=failed`. Remove every temp tree you made as soon as it is no longer needed. Measure
  your scratch (`du -s --inodes`, `du -sh`) at the end and give the figures in `evidence`. If you pass the budget,
  stop the heavy work, clean what you can, and return.
- Every suite is run to its end, never with `-x`.

## What you read

- The ticket file `.tickets/DAEO-3r1j.md` (read-only): its KPI lines, its sources.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-971 (item 4), DEC-957 (the install rule: only the CTO's own
  session asks the owner), DEC-966 (item 1), DEC-163 (the research role's install exception), DEC-083 (DEC-040
  amended: installs an `ask` for the orchestrator, denied to every other role, sudo stays with the owner), DEC-221,
  DEC-462, DEC-491, DEC-866.
- `governance/project/orchestration/packages/P1-MORNING-2026-10-31.md`, item 4.
- **The model:** this repository's own five-rule hook, `.claude/hooks/pretooluse.py`, its rule 4: how it recognises
  the CTO (the orchestrator on the coordination ticket W2-00) and the words it refuses with. Read it freely; it is not
  this ticket's implementation.
- How a project is generated and its hook lines run as Claude Code runs them: `tests/acceptance/W2-90/` (its
  `w2_90_kernel_wiring.py`), `tests/acceptance/W2-106/` (README and support: the stand-in pin, a line run as
  `sh -c <line>`), `tests/acceptance/W2-59/`, and W1-38's and W1-39's support code. Reuse their support by import
  where you can; copy nothing of theirs into your folder that you could import.
- The kernel guard's install rule as it stands on the base, through its tests: `tests/acceptance/W1-04/` (and its
  README), for the decision forms (ask, deny, allow) and how a hook result is read.

## The behaviour to test (from the KPI lines and the sources)

The product's kernel guard (the PreToolUse hook a generated project runs) decides an install command in a Bash call:

1. **The CTO is asked.** In a project generated from the template (copier, then rulesync generate), an install by the
   orchestrator on the project's coordination ticket is asked of the owner (`ask`), with the owner's prompt as it is
   today (the approval names that a tool-registry record is required).
2. **Every other session is refused,** and the refusal tells the session to raise the install as a P1 escalation (to
   the CTO, who asks the owner), as this repository's hook does after DEC-957: a lead (the orchestrator on another
   ticket), an orchestrator with no ticket, an engineer, an independent test designer, product-spec, an independent
   auditor, a research session outside its experiment folder, a session with no role; a role subagent of another type
   inside the CTO's session; an orchestrator subagent inside any session that is not the CTO's.
3. **The configuration (the public interface, DEC-971 item 4):** the coordination ticket is named by one key in the
   project's own configuration, set at adoption and never written in the code: the top-level key
   `coordination_ticket` in the project's `governance/project/roster.yaml`. Its value names a ticket of the project's
   `.tickets/` folder either by the ticket's id (its file name without `.md`, the form `GOV_TICKET` takes) or by its
   WBS id (`wbs_id` in the ticket's front matter). The session is the CTO when its role (`GOV_ROLE`) is `orchestrator`,
   it acts as the orchestrator (the main thread, or an orchestrator subagent in that session), and its ticket
   (`GOV_TICKET`, by id or WBS id) is the same ticket as the key's.
4. **Fail closed.** With no `roster.yaml`, no such key, an empty or non-text value, a file that cannot be read or
   parsed, or a key that names no ticket of the project, every session's install is refused, the CTO's included, and
   the refusal says how to set it (it names the file and the key). Never an `ask` and never a pass-through.
5. **Nothing else changes:** sudo is refused to every role (the CTO included); the research role's one exception
   holds (an install inside its own experiment folder is let through, DEC-163, with or without the key); a frozen
   project refuses installs (the CTO's included); the owner's prompt for an approved install is as before; a Bash call
   that is not an install is decided as before.
6. **Failure KPIs, each must have a test that would catch it:** a lead's or a worker's install in a generated project
   asked or allowed; the CTO's install refused when the coordination ticket is set; a missing or unreadable key read as
   "ask everyone"; sudo, the research exception or the freeze changed.

Profile FULL: thorough on these lines, no combinatorial expansion beyond them (DEC-221). Generate the project once per
session (or per module) and copy or adjust it per case, so the suite stays fast; a case that needs a different roster
or ticket set writes those files in its own copy. Commands are only text in the hook's input: nothing is installed,
nothing reaches the network.

**Earlier tests that enforce the old rule (DEC-866).** Several earlier suites assert the rule DEC-957 and DEC-971
item 4 change ("any orchestrator is asked", with no coordination-ticket key in their fixtures), for example in
`tests/acceptance/W1-04/`. **Do not edit any of them.** Find them, and list each case in your return (file, test id,
what it asserts, the decision it still enforces and the one that changes it) as a package for the lead: the decision
to revise them is not yours or the lead's.

## What you write

- Only under `tests/acceptance/W2-110/` in the tests worktree. No throwaway implementation left in the tree.
- A README that maps each KPI line (success and failure) to its tests and gives each test's expected red reason on
  the base, and says how the tests run the code of the worktree they sit in.
- Red first: run your suite to its end with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance/W2-110 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`;
  the cases fail for the reason your README states (on the base, every orchestrator is asked, so the lead's case asks
  and the no-key case asks), and the cases that guard what already holds (sudo, research, freeze) pass — name them.
- Also run once `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance/W2-110 --collect-only -q -p no:cacheprovider`
  to show no collection error.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact,
  reversibility, cost, recommendation, confidence).

## Commit

Commit only `tests/acceptance/W2-110/`, with the trailers in the final block:

    git commit -m "W2-110: acceptance tests for a product's CTO-only install rule" --trailer "Task: DAEO-3r1j" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-971, DEC-957" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. Put in them: the sandbox check's result; your commit's hash (12 digits); the test count; each KPI line with its
tests; the red result as you saw it (counts, and the reason); the earlier tests that enforce the old rule (the list
above); whether you used `gov retrieve` and how often; P-R1 results served; read refusals met; your scratch figures.

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
