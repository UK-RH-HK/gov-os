# Brief: engineer, DAEO-u4oz (W2-04), profile FULL, round 2, fix 1

You are a fresh engineer. Ticket: `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`, head `d020738197cc`. The ticket's build is already committed there (`c5b771c61ada`, run 1's engineer); with round 2 added (`d78d31f216ed`, after the CTO decision DEC-1005); you take one red acceptance case. You build to the specification and its KPIs, never to the tests.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-u4oz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` and `git rev-parse --short=12 HEAD` (expect `/home/usain/gov-os-worktrees/W2-04`, `w2/W2-04` and `d020738197cc`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return.
- **Memory used (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet (the lead rebuilds it after your batch), so retrieve from the integration branch's store, a read: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. It holds `w2/integrate` as of its last refresh; read the files here for this ticket's own code. Do not run `gov retrieve` in this worktree (it would answer STORE_MISSING). **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Run 1's engineer used none; use it at least for what you look up outside your own files.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-04/`**, by any tool, here or in `/home/usain/gov-os-worktrees/W2-04-tests` or on any branch (`w2/W2-04-tests` included), **nor the test designer's revisions of `tests/acceptance/W2-54/` and `tests/acceptance/W1-41/`** (anything on `w2/W2-04-tests` after `d2ff95b28a2e`); you may run acceptance tests and see their names, results and failure messages; (d) the hidden half of any evaluation set (W2-61's measure's hidden half among them).
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file in your session's own scratchpad (the Write tool refuses `.gov-runtime/scratch/eng/`) and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one. No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` and the untracked dotfiles at the top (`.bashrc`, `.idea`, …) show as placeholder device files: conclude nothing from them and never commit them.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 10 GB and 500,000 files and folders, outside the tracked tree. Keep the sandbox's own `TMPDIR` (do not set it yourself; if a `pytest-of-*` folder appears in the worktree, say so). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- **Never `gov rebuild --no-embeddings`.** Do not rebuild this worktree's store (the lead does, DEC-1001). Tests that need a store build their own in a temporary folder.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, `docs/DECISION_REGISTER.md`, the plan files or `governance/project/path-map.yaml`. Never run `gov close`, `gov adopt` or `gov pause`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md` (read-only) and CAP-15.b, CAP-15.d (`docs/contract/CONTRACT_v4.md`); DEC-860.
- This ticket's build as it stands here: `src/gov/context/__init__.py`, `src/gov/context/context_check.py`, `src/gov/retrieval/supplementary.py`, `tests/unit/context/`.
- The specification (run 1) and its addendum below; the addendum holds where they differ.

{{SPEC}}

## The work: one red acceptance case

The build so far: run 1's `c5b771c61ada` and round 2's `d78d31f216ed` (`supplementary_batches`, a dependency counted by its front matter). The test designer's revised acceptance tests are merged (`d020738197cc`). The lead ran `gov accept DAEO-u4oz` once: KPI lines success-1 to success-6 pass; **success-7 fails, 9 passed, 1 failed.** The failing case and its message, as the lead saw them (this is all you get of the test, DEC-096):

```
FAILED tests/acceptance/W2-04/test_w2_04_batches.py::test_further_batch_is_at_most_one_batch_long
AssertionError: `further_batch` is not the ranked items from the first that was not stacked, in the batches' order:
  [('c7fdb06840f7…', 'docs/ledger/page-03.md'), ('7367772094…', 'docs/ledger/page-04.md'), (… page-05 … page-09 …),
   ('f4e199a123e3…', 'docs/ledger/page-10.md'), ('bf2155fb6b2d…', 'docs/ledger/page-11.md'), ('1db82a3e8292…', 'docs/ledger/page-12.md')]
  read after the stack: [(… page-03.md), (… page-04.md), (… page-05.md), (… page-06.md), (… page-07.md), (… page-08.md), (… page-09.md)]
  Left contains 3 more items, first extra item: ('f4e199a123e3…', 'docs/ledger/page-10.md')
```

That is: under a tight `--budget`, the packet's `further_batch` names ten items, page-03 to page-12, but the batches in `supplementary_batches` read only up to page-09; three of the items in `further_batch` were never read by any batch the context took.

1. Judge it against the specification and its addendum (S7: "`further_batch`: … the ranked items that were not stacked for lack of room, beginning with the first one that did not fit, at most one batch long"; S7a: "The batches' items taken together, in order, are the rank order: … `further_batch` begins with the first ranked item that was not stacked"). If you judge the case's expectation (that `further_batch` continues the batches' own items, in their order, and names nothing no batch read) is within the specification, change the build so it holds, and keep every other rule of S7 and S7a (at most as long as the largest `limit`, strict rank order, no stacked item in it, an empty list when nothing was left, deterministic). Think about the edge where no batch can be taken at all (no room left after the mandatory inputs) and keep it consistent with S7 and S7a; say what you chose.
2. If you judge the expectation contradicts the specification, change nothing and return a package (question, why, options, impact, reversibility, cost, recommendation, confidence). Never bend the code to a test against the specification.
3. Builder tests in `tests/unit/context/` for the change; keep them all green (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m pytest tests/unit/context -q -p no:cacheprovider -o tmp_path_retention_policy=failed`).
4. **Commit first**, then run the acceptance tests once, reading results only, **through `gov accept` only**: `cd /home/usain/gov-os-worktrees/W2-04 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m gov.cli.main accept DAEO-u4oz --json` (run it in the background with the longest timeout your Bash tool allows and an exit-code file, then wait for it with short checks; it takes a few minutes). Pass or fail per KPI line and the counts; never a test's source, assertion text or traceback; never `pytest` on `tests/acceptance/` yourself. A test you think is wrong is a package, never worked around.

Only inside the ticket's `allowed_paths`: `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`. **Read only, held by running tickets:** W2-13 holds `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/retrieve/**` and `tests/unit/retrieval/**`; W2-92 holds `src/gov/retrieval/graph_route.py`, `code_route.py` and the route list in `src/gov/retrieval/retrieve.py`; you change none of their files. Never make a check fail open. Proportion (DEC-135): nothing beyond this case. **DEC-866:** something you touch that still enforces a superseded decision is named in your return, never fixed silently.

## Commit

Commit only your paths, with the trailers in the final block (`Implements:` holds only decision and Contract ids the register and the store hold):

    git commit -m "W2-04: <subject>" --trailer "Task: DAEO-u4oz" --trailer "Role: engineer" --trailer "Implements: CAP-15.b, CAP-15.d, DEC-860" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After the commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed (code and tests apart); the builder tests with their results; your judgement of the case and the `gov accept` result per KPI line; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; anything you were refused or could not settle, as a package.

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Right after the twelve fields: a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
