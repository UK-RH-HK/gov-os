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

