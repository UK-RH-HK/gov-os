# Brief: independent test designer, DAEO-zpdj (W2-105), run 1

You are a fresh independent test designer (MR-3). Ticket: DAEO-zpdj (W2-105), profile STANDARD. You work only in the
tests worktree `/home/usain/gov-os-worktrees/W2-105-tests` on branch `w2/W2-105-tests`; you never read or write the
ticket's own worktree (`/home/usain/gov-os-worktrees/W2-105`). You write the ticket's acceptance tests from its KPI
lines and its sources, in parallel with the implementer (DEC-959 item 7, DEC-963), and you show them red.

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zpdj','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-zpdj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-105-tests` and
  `w2/W2-105-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another (no command longer than about nine minutes; split a
  long run into parts). Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
  — For you, in the tests worktree, "this worktree" is `/home/usain/gov-os-worktrees/W2-105-tests`: use
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105-tests/src` (you never read the ticket's worktree). Your tests must
  read the template and the `gov` code **relative to the repository they sit in** (as
  `tests/acceptance/W2-90/w2_90_kernel_wiring.py` does with `Path(__file__).resolve().parents[3]`), so that when the
  lead merges them into the ticket's worktree and runs them there, they judge that worktree's template and code.
  Your README says how, with the `gov.__file__` line.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve
  "<question>" --json`. Never this ticket's worktree's store. For what changed on `w2/integrate` since that store's
  refresh, read `git show w2/integrate:<path>`. Never one giant query (DEC-860): a large question in batches
  (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question (DEC-859) uses
  the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load
  of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation path
  (`template/.rulesync/permissions.jsonc`) **as it stands in the ticket's worktree or on branch `w2/W2-105`**, and
  name in your return any such result you were served. Reading that file **as it stands on `w2/integrate`, before
  this ticket** (`git show w2/integrate:template/.rulesync/permissions.jsonc`), is reading the existing code, which you
  may do.
- **Policy 2 (DEC-820), reads open, writes closed:**
  (c) you never read this ticket's implementation: no file that branch `w2/W2-105` changes against `w2/integrate`
  (`git diff --name-only w2/integrate...w2/W2-105` names them), other than your own tests. Never read anything in
  `/home/usain/gov-os-worktrees/W2-105`.
  (d) never read the hidden half of any evaluation set.
  Never read secrets or keys, never print one; never read the held-out qualification material's contents; never read
  or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name
  only and clone into a temporary folder.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders instead. Count every refusal you
  meet and list it in your return.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces; put anything longer in a script file under
  `/home/usain/gov-os-worktrees/W2-105-tests/.gov-runtime/scratch/td/` with the Write tool and run it.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). Tests
  that need a project build a temporary one (generated from the template the way W2-90's helper and W1-39's and
  W1-38's support modules already do it, file by file). No clone, copy or programme file under any `.gov-runtime/`
  folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude
  nothing from it. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Install nothing (raise it as a P1 in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** the lead's 20 GB and 1,000,000 files and folders are shared; your share is 8 GB and
  400,000 files and folders outside the tracked tree. `TMPDIR` is set by the launcher's sandbox: keep it. Keep
  pytest's own retention (never `--basetemp`); use `-o tmp_path_retention_policy=failed`. Clean up every temp tree
  you made when done. Give `du -sh` and `du -s --inodes` of your scratch at the end.
- **Machine load (DEC-847):** before a suite run, wait while both the 1- and 15-minute loads are at or above the
  CPU count.

## What you read

- The ticket file `.tickets/DAEO-zpdj.md` (read-only): its KPI lines, `allowed_paths` and sources.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-966 (item 1), DEC-172, DEC-957 (the install rule), DEC-965,
  DEC-163 (research's install exception), DEC-664 (the template's test-folder rule taken out), DEC-866 (supersession),
  DEC-732, DEC-820.
- `governance/project/orchestration/packages/P-W2-90-1.md` (P1-A: what this ticket fixes, and the 3 cases it blocks).
- How a project is generated from the template and how Claude Code's permission rules and the guard's hook are judged
  together: `tests/acceptance/W2-90/README.md` and `tests/acceptance/W2-90/w2_90_kernel_wiring.py` (read them; do not
  change them); W1-39's and W1-38's support modules (`assemble_source`, `create_project_and_run`,
  `run_rulesync_generate`, and W1-38's hook harness, which reads a call's decision as the harness does: a settings
  deny rule first, then the hook); W1-05's `test_an_install_by_the_orchestrator_asks_the_owner` and
  `test_an_install_by_any_other_role_is_denied`, and W1-46's research install cases, as they stand.
- The kernel's guard as a product runs it, on `w2/integrate`: `template/governance/kernel/hooks/pretooluse.py` (its
  install branch) and `src/gov/guard/install.py`. These are not this ticket's implementation; they are the install
  rule the generated project's sessions reach once nothing denies an install first.
- W1-38's and W1-39's suites (KPI 4 names them).

## The behaviour to test (the KPI lines, in their words)

Success:
1. A project generated from the template (copier, then rulesync generate) holds no deny rule for `npm install*` or
   `pip install*` in its generated settings [DEC-966 item 1, DEC-172].
2. In that project, an install in the CTO's session (the orchestrator role on its coordination ticket) reaches the
   guard's install rule and is asked; in every other session, leads included, it is refused by the guard, as this
   repository's after DEC-957 [DEC-966 item 1, DEC-957].
3. Every other permission and deny rule of the template is unchanged: the generated project's rules counted and
   compared before and after, by name, only the two install rules gone [DEC-966 item 1].
4. The template's own suites (W1-38, W1-39) pass on the change [DEC-966 item 1, DEC-965].

Failure:
- A generated project still denies an install before the guard is asked.
- An install in a session other than the CTO's is asked or allowed.
- Any other permission or deny rule added, removed or changed.
- W1-38 or W1-39 red on the change.

**The lead's reading of KPI 2 (the lead returns the rest as a package; do not decide it yourself):** this ticket's
only implementation path is the template's permission source. A product's install rule is the kernel's guard as it
stands on `w2/integrate`; it does not know a "coordination ticket", so it cannot tell the CTO's session from a lead's
(both are the orchestrator role), and it keeps research's install inside its own experiment folder (DEC-163; W1-46
success 6, which DEC-965 expects this ticket to turn green). Test KPI 2 for what the ticket's change decides:
- an install (`npm install …` and `pip install …`) in an orchestrator session of the generated project is not denied
  by any settings rule and reaches the guard, whose answer is `ask`;
- the same installs in the engineer, independent-test-designer, independent-auditor and product-spec sessions are
  refused, and refused **by the guard** (its hook's deny), not by a settings rule;
- research's install outside its experiment folder is refused by the guard.
Do not write a test that can only pass after a change outside the ticket's path (the "leads included" half and the
research exception). Name in your return what of KPI 2 your tests leave out and why; the lead packages it.

## Earlier tests (KPI 4)

KPI 4 requires W1-38 green on the change. `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py` pins the template's
permission source and the generated deny list as DEC-664's round left them, the two install rules included
(`OTHER_SOURCE_RULES`, `OTHER_GENERATED_RULES`, and the docstrings or messages that name them). That pin enforces what
DEC-966 item 1 now changes (DEC-866). Revise only what names the two install rules there, so that it pins the
template's rules with exactly those two gone, and lower no other expectation (the ticket-folder and sudo rules, and
"nothing else", stay pinned). Commit it as a second commit with `--trailer "Rewrite-Reason: DEC-966 item 1"`. Read
W1-38's README and W1-39's suites for any other pin of the two rules and treat it the same way (W1-38's README
lines that describe the generated deny rules may be updated to match, in the same commit). W1-05's and W1-46's cases
that name the install deny rules (the `NOT_MOVED_TO_THE_KERNEL` list and the comments around it) are **W2-90's next
round, not yours: do not edit them**; name them in your return.

## What you write

- Only under `tests/acceptance/W2-105/` in the tests worktree, plus the W1-38 (or W1-39) revision above.
- STANDARD: every KPI line's success and failure plus the key edge cases (both install commands; each non-orchestrator
  role; the two rules gone from the source and from the generated settings; every other rule, by name and count,
  unchanged against the template on `w2/integrate`). No combinatorial expansion beyond the KPIs. Behaviour through
  public interfaces; deterministic; no network.
- A `README.md` mapping each KPI line to its tests and its expected red reason, and saying how the tests run the code
  and template of the worktree they sit in (DEC-732), with the `gov.__file__` line.
- Red first: run your folder to its end (never `-x`) with
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105-tests/src python3 -m pytest tests/acceptance/W2-105 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
  They must fail on this base for the reason the README states (the generated settings deny the installs before the
  guard is asked). Tests that guard what already holds may pass on the base; name each with the reason. Then run the
  W1-38 file you revised the same way and report its result on the base (the revised cases red, for the stated
  reason).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact,
  reversibility, cost, recommendation, confidence).

## Commit

Before committing, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only
`*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only your test paths: one commit for
`tests/acceptance/W2-105/`, a second for the W1-38 revision, each with the trailers in the final block:

    git commit -m "W2-105: acceptance tests for the template's install block removed" --trailer "Task: DAEO-zpdj" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-966" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

(the second also with `--trailer "Rewrite-Reason: DEC-966 item 1"`). Then `git log --oneline -3` and
`git status --short`.

## Return

Your commits' hashes (12 digits); the test count; each KPI line with its tests; the red result as you saw it (counts,
time) and the red reason; the `gov.__file__` line; every earlier test you rewrote, with its reason; every other suite
you found pinning the two install rules (named, not edited); what of KPI 2 you left out and why; the `gov retrieve`
queries you ran and whether they helped; the guard refusals you met; any package.

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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
