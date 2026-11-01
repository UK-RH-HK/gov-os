# Brief: engineer, DAEO-u4oz (W2-04), profile FULL, round 2 (a small batch)

You are a fresh engineer. Ticket: `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`, head `f36a8c4170a2`. The ticket's build is already committed there (`c5b771c61ada`, run 1's engineer); you add two small changes to it, decided by the CTO (DEC-1005, delegated). You build to the specification and its KPIs, never to the tests.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-u4oz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` and `git rev-parse --short=12 HEAD` (expect `/home/usain/gov-os-worktrees/W2-04`, `w2/W2-04` and `f36a8c4170a2`). If anything differs, stop and say so.

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

## The work (about 20 to 40 lines of code and a few builder tests)

1. **`supplementary_batches` (the addendum's S7a; P-W2-04-2 (A)).** Add the packet key: one entry per batch the context took (one batch is one of the context's own lookups of ranked evidence, today's read of at most ten ranked chunks, never more than the room left), in the order taken, each `{"items": [{"id", "path"}, …], "limit": n}`. Keep the block semantic-free. It is part of the packet and its `hash`, and deterministic.
2. **A dependency ticket counts by its front matter (the addendum's S1; P-W2-04-3 (b), CAP-15.b).** A ticket named in `deps` is read and counted as its id, status, title and KPI lines, not its whole file; its `sha256` stays its file's. The ticket's own text stays whole under `ticket_text`. About 20 lines.
3. Builder tests for both in `tests/unit/context/`; keep the existing ones green (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m pytest tests/unit/context -q -p no:cacheprovider -o tmp_path_retention_policy=failed`).
4. **The figures, read only on the integration store** (as run 1 did, with this worktree's `src/`): `cd /home/usain/gov-os-worktrees/W2-00-store && PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src timeout 900 python3 -m gov.context.context_check` once: its time and result (how many tickets now refuse over the ceiling, against run 1's 76 of 180); and `gov context DAEO-03pw --json`'s ok and tokens, under the same condition. Write nothing in that tree.

Only inside the ticket's `allowed_paths`: `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`. **Read only, held by running tickets:** W2-13 holds `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/retrieve/**` and `tests/unit/retrieval/**`; W2-92 holds `src/gov/retrieval/graph_route.py`, `code_route.py` and the route list in `src/gov/retrieval/retrieve.py`; you change none of their files (a need is a package). Never make a check fail open: the over-ceiling refusal, the unreadable-record block and the stale-store report stay as they are. Proportion (DEC-135): nothing beyond the two items. **DEC-866:** something you touch that still enforces a superseded decision is named in your return (old decision, new decision, file and line), never fixed silently.

**The acceptance tests:** the test designer is revising them in parallel; the lead merges them after your return and runs `gov accept` itself. You do not run `gov accept` or any acceptance test in this batch.

## Commit

Commit only your paths, with the trailers in the final block (`Implements:` holds only decision and Contract ids the register and the store hold):

    git commit -m "W2-04: <subject>" --trailer "Task: DAEO-u4oz" --trailer "Role: engineer" --trailer "Implements: CAP-15.b, CAP-15.d, DEC-860" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After the commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed (code and tests apart); the builder tests with their results; the figures of item 4; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; anything you were refused or could not settle, as a package.

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
