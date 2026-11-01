# Brief: product-spec worker, DAEO-zpdj (W2-105), run 1

You are a fresh product-spec worker, in ticket mode. Ticket: DAEO-zpdj (W2-105), profile STANDARD. You work only in
the worktree `/home/usain/gov-os-worktrees/W2-105` on branch `w2/W2-105`. You implement the ticket to its
specification and KPIs, never to the tests.

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zpdj','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-zpdj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-105` and `w2/W2-105`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another (no command longer than about nine minutes). Return
  only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This
  worktree has no store yet (its rebuild is queued behind the machine's rebuild lock), so retrieve from the
  integration branch's store, a read: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`
  (capture stdout only; it writes progress to stderr). It holds `w2/integrate`, which has none of this ticket's
  acceptance tests. Never one giant query (DEC-860): a large question in batches
  (`--batch-size`, then `--continue <token>`). A code question (DEC-859) uses the code-graph tool's own traversal
  (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Policy 2 (DEC-820), reads open, writes closed:**
  (c) you never read this ticket's acceptance tests: nothing under `tests/acceptance/W2-105/` (and nothing in the
  tests worktree `/home/usain/gov-os-worktrees/W2-105-tests`), by any tool. You may run them and read their results
  (names, pass or fail, failure messages), never their source.
  (d) never read the hidden half of any evaluation set.
  Never read secrets or keys, never print one; never read the held-out qualification material's contents; never read
  or name the qualification oracle. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders instead. Count every refusal you
  meet and list it in your return.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal
  absolute paths; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/ps/`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed for the ticket, do not work around it: return it as a package.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). No
  clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session
  `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it. Never write `.gov-runtime/**`
  outside `.gov-runtime/scratch/`. No subagents that write.
- Install nothing (raise it as a P1 in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** the lead's 20 GB and 1,000,000 files and folders are shared; your share is 4 GB and
  200,000 files and folders outside the tracked tree. `TMPDIR` is set by the launcher's sandbox: keep it. Keep
  pytest's own retention (never `--basetemp`); use `-o tmp_path_retention_policy=failed`. Clean up what you made.
- **Machine load (DEC-847):** before a suite run, wait while both the 1- and 15-minute loads are at or above the CPU
  count.

## What you read

- The ticket file `.tickets/DAEO-zpdj.md` (read-only): its KPI lines and its `allowed_paths`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-966 (item 1), DEC-172, DEC-957 (the install rule), DEC-965.
  Cite a decision for a rule only after reading that the decision says it.
- `governance/project/orchestration/packages/P-W2-90-1.md` (P1-A).
- The file of the ticket, `template/.rulesync/permissions.jsonc`, and for the form how rulesync reads it
  (`template/.rulesync/` and its other sources).

## Ticket mode: what you write

The owner chose P-W2-90-1 P1-A option (a) (DEC-966 item 1): the template's install block is removed, so an adopted
product's CTO session reaches the guard's install rule and can ask the owner, as this repository does since DEC-172.
- In `template/.rulesync/permissions.jsonc`, the deny rules for `npm install*` and `pip install*` are removed.
- Every other rule there (the `.tickets/**` edit deny and the `sudo *` bash deny) stays exactly as it is; nothing is
  added. The file stays valid for rulesync (JSON with comments).
- Only inside this path of the ticket's `allowed_paths`: `template/.rulesync/permissions.jsonc`. Never the acceptance
  tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion: write what the specification asks and add no rule of your own (MR-6).
- Check your own work without reading the acceptance tests: the file parses as JSON once its comments are taken out,
  and holds exactly the two remaining rules.

## Commit

Before committing, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only
`*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only your path, in one commit, with the
trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-105: the template's install deny rules removed (DEC-966 item 1)" --trailer "Task: DAEO-zpdj" --trailer "Role: product-spec" --trailer "Implements: DEC-966" --trailer "Implements: DEC-172" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`.

## The acceptance tests (DEC-963)

The test designer works in parallel in its own worktree. After your commit, check whether
`/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/TESTS-READY` exists. If it does, run
`git merge --no-ff --no-commit w2/W2-105-tests`, then
`git commit -m "W2-105: merge the acceptance tests" --trailer "Task: DAEO-zpdj" --trailer "Role: product-spec" --trailer "Implements: DEC-966"`
in this worktree (check `git log --oneline -3` after) and run the acceptance tests once, reading results only:
`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -m pytest tests/acceptance/W2-105 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
to its end (never `-x`). If it does not exist yet, do not wait for it: return; the lead merges and runs them.

## Return

Your commit's hash (12 digits); the file written and its diff stat; the `gov.__file__` line; whether TESTS-READY
existed, and if so the merge commit and the acceptance tests' counts and failure messages; the `gov retrieve` queries
you ran and whether they helped; the guard refusals you met; anything you could not place or were refused, as a
package.

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
