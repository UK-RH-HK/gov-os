# Brief: engineer, W2-110 (DAEO-3r1j), run 1

You are a fresh engineer. Ticket: `DAEO-3r1j` (`W2-110`), profile FULL. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-110` on branch `w2/W2-110`. You build the code to fulfil the ticket's specification
and its KPIs (DEC-957's work order), never to make the acceptance tests pass. You are a headless session: nobody
answers questions while you work, and only your final message is read.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-3r1j','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-3r1j`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-110` and `w2/W2-110`). If
anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src` set per command
  (never in a session's `--settings` env). Show it once with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -c "import gov; print(gov.__file__)"` and quote it.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This
  worktree has no store yet (the lead rebuilds it after you), so retrieve from the integration branch's store, which
  holds `w2/integrate` (this ticket's base and later merges, none of this ticket's tests):
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). For this ticket's own
  files, read them in this worktree. Never one giant query or context (DEC-860): a large question is
  taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question
  uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a
  load of the whole graph (DEC-859).
- **Policy 2 (DEC-820), reads open, writes closed.** You read freely: the whole repository, git history, other
  worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out
  qualification material (its file names may be seen); never read or name the qualification oracle; (c) **the
  counterpart's work on this ticket: you never read `tests/acceptance/W2-110/`** (in this worktree, in
  `/home/usain/gov-os-worktrees/W2-110-tests`, or on branch `w2/W2-110-tests`), by any tool; you may run those tests and
  see their names, results and failure messages, never their source; (d) the hidden half of any evaluation set, by
  whoever is measured by it.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that
  start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form,
  search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no
  backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Put anything longer in a script file under
  `/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/eng/` with the Write tool and run that file. A refused form
  is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another; return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A test
  that needs a repository builds a temporary one. Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists:
  conclude nothing from it; code that reads a flag is tried in a temporary repository.
- Install nothing (a tool you need is returned as a P1 package). No sudo. Never write `.gov-runtime/**` outside
  `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never
  the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** 6 GB and 300,000 files and folders, outside the tracked tree, as your share of the
  ticket's 20 GB / 1,000,000. Your temp folder is the one the sandbox sets (keep it); otherwise
  `TMPDIR=/tmp/gov-os-lead-W2-110`. Keep pytest's own retention; never a per-run `--basetemp`; run pytest with
  `-o tmp_path_retention_policy=failed`. Remove every temp tree you made as soon as it is no longer needed. Measure
  your scratch (`du -s --inodes`, `du -sh`) at the end and give the figures in `evidence`. If you pass the budget,
  stop the heavy work, clean what you can, and return.
- Every suite is run to its end, never with `-x`. Never run the full test suite.

## What you read

- The ticket file `.tickets/DAEO-3r1j.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-971 (item 4), DEC-957 (the install rule: only the CTO's own
  session asks the owner), DEC-966 (item 1), DEC-163 (the research exception), DEC-083 (DEC-040 amended), DEC-135.
- `governance/project/orchestration/packages/P1-MORNING-2026-10-31.md`, item 4.
- **The model:** this repository's own five-rule hook, `.claude/hooks/pretooluse.py`, rule 4: how it recognises the
  CTO (the orchestrator on the coordination ticket W2-00, hard-coded there) and the words it refuses with.
- The code you change: `template/governance/kernel/hooks/pretooluse.py` (its install branch) and
  `src/gov/guard/install.py`; the guard's ticket reading in `src/gov/guard/decide.py` (read only; W2-60b holds it).
- How a project is generated from the template and its hook lines run: `copier.yml`, `template/.rulesync/hooks.jsonc`.

## The specification (the lead's design, decided)

The product's kernel guard asks the owner about an install only in the CTO's own session, and refuses every other
session (DEC-957, DEC-971 item 4):

1. **The one key.** The coordination ticket is named by the top-level key `coordination_ticket` in the project's
   `governance/project/roster.yaml` (the project's overlay, which `copier update` never overwrites), set at adoption;
   never written in the code. Its value names a ticket of the project's `.tickets/` folder either by the ticket's id
   (its file name without `.md`, the form `GOV_TICKET` takes) or by its WBS id (`wbs_id` in the front matter), the way
   the kernel guard already resolves a session's ticket.
2. **The CTO** is a session whose role (`GOV_ROLE`) is `orchestrator`, whose acting role is `orchestrator` (the main
   thread, or a declared orchestrator subagent in that session, as the install rule reads the acting role today), and
   whose ticket (`GOV_TICKET`) resolves to the same ticket as the key. Its install is **asked** of the owner, with
   today's prompt (the tool-registry record required) and today's record and before-snapshot.
3. **Every other session is refused** — a lead (the orchestrator on another ticket), an orchestrator with no ticket,
   every other role, a session with no role, a role subagent of another type in the CTO's session, an orchestrator
   subagent in a session that is not the CTO's — and the refusal tells the session to raise the install as a P1
   escalation to the CTO, who asks the owner.
4. **Fail closed.** No `roster.yaml`, no key, an empty or non-text value, a file that cannot be read or parsed, a key
   naming no ticket of the project, or any error while reading it: every session's install is refused, the CTO's
   included, and the refusal names the file and the key and says how to set it. Never an ask, never a pass-through,
   never a crash that lets the call through.
5. **Unchanged:** sudo refused to every role; a frozen project refusing installs (before any role is looked at); the
   research role's one exception inside its experiment folder (DEC-163), with or without the key; the owner's prompt
   for an approved install; every Bash call that is not an install; `decide()`; this repository's own five-rule hook.

## What you write

- Only inside the ticket's `allowed_paths`: `template/governance/kernel/hooks/pretooluse.py` (its install branch
  only), `src/gov/guard/install.py`, and builder tests in `tests/unit/guard/test_w2_110*`.
- **Shared file:** `src/gov/guard/install.py` is also covered by W2-05's paths (running; it does not change the install
  rule). Touch only the install decision's own range: add what you need, change nothing else in that file.
- Builder tests (your own test-driven development) in `tests/unit/guard/test_w2_110*.py`, as regression evidence only:
  each line of the specification above, success and failure.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Never make a guard decision fail open: each
  failure KPI must still refuse.
- **Earlier tests that enforce the old rule (DEC-866).** Some earlier tests assert that any orchestrator is asked with
  no coordination-ticket key (for example `tests/unit/install/test_install.py`'s hook-integration cases and acceptance
  suites such as W1-04). They will turn red under DEC-957's rule. **Do not edit them and do not bend the code to
  them;** run `tests/unit/install/` and `tests/unit/guard/` and list in your return every case that turns red, with
  what it asserts. The decision to revise them is not yours.
- **The acceptance tests arrive while you work (DEC-963).** The test designer works in parallel in its own worktree.
  When `/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/TESTS-READY` exists, run them once, reading
  results only:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -m pytest tests/acceptance/W2-110 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
  If it does not exist when your code and unit tests are done, commit and return; the lead runs them.

## Commit

Before you commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your paths, with the trailers in the final block:

    git commit -m "W2-110: a product's CTO-only install rule in the kernel guard" --trailer "Task: DAEO-3r1j" --trailer "Role: engineer" --trailer "Implements: DEC-971, DEC-957" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. Put in them: the sandbox check's result; the `gov.__file__` line; your commit's hash (12 digits); the files
changed and the lines added and removed; the tests you ran with their results (unit tests; the acceptance tests if
they were ready); the earlier tests that turned red, by case; whether you used `gov retrieve` and how often; read
refusals met; your scratch figures; any package (question, why now, options, impact, reversibility, cost,
recommendation, confidence).

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
