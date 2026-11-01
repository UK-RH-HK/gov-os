# Brief: independent test designer, DAEO-u4oz (W2-04), profile FULL, run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-04-tests` on branch `w2/W2-04-tests` (DEC-963); you never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-04`). You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with the engineer, and you show them red.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-u4oz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-04-tests` and `w2/W2-04-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return. Your tests must call the code of the tree they run in (a child process with that tree's `src/` on `PYTHONPATH`, as `tests/acceptance/W2-55/w2_55_support.py` and `tests/acceptance/W2-03/w2_03_support.py` do), so that once merged into the ticket's worktree they exercise its code; your README says how.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, **only from the integration branch's store:** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store or files. For what changed on `w2/integrate` since that store's refresh, read `git show w2/integrate:<path>`. **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`), and name in your return any such result you were served (DEC-820 (c)). You may read those files **as they stand on `w2/integrate`** (`git show w2/integrate:<path>`): that is the existing code, not this ticket's work.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, the files `git -C /home/usain/gov-os-worktrees/W2-04 diff --name-only w2/integrate...HEAD` names other than tests, nor anything in `/home/usain/gov-os-worktrees/W2-04` that differs from `w2/integrate`; (d) the hidden half of any evaluation set. Writes stay inside the paths named under "What you write", in this worktree.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-04-tests/.gov-runtime/scratch/td/` with the Write tool and run that file (if the Write tool refuses that folder, use your session's own scratchpad). A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one from scratch (`tmp_path`). No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 5 GB and 250,000 files and folders, outside the tracked tree. Keep the sandbox's own `TMPDIR` (do not set it yourself: the lead's temp folder is not writable inside the sandbox, and pytest would then write into the worktree; if a `pytest-of-*` folder appears in the worktree, say so). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the register or plan files. Never run `gov close`, `gov adopt` or `gov pause`; never `gov rebuild --no-embeddings`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md` (read-only): its seven success KPI lines and its failure line, its `allowed_paths` and its sources; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-04`) and §0 (rules for every ticket).
- The sources: CAP-15 and CAP-15.a to CAP-15.g (`docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml`); DEC-860 in `docs/DECISION_REGISTER.md`; DEC-221 (tests in proportion), DEC-462, DEC-491, DEC-866, DEC-768 (the dropped list's one order).
- The list rows above, in `docs/plan/WAVE_2_LIST.md`, and their source lines in `governance/project/bootstrap.md` (named in the specification).
- The existing public interfaces as they stand on `w2/integrate`: `gov context <ticket> --json` and its options, `gov.context.context(...)`, `python3 -m gov.context.context_check`, `gov.store.load(root)`, `gov.records.records(root)` (a register entry's `content_hash`), `gov retrieve --json`, `src/gov/cli/main.py`'s output envelope; and how earlier suites drive them: `tests/acceptance/W1-24/` (the packet's first suite), `tests/acceptance/W2-03/` (planted registers and entry records), `tests/acceptance/W2-54/` (the dropped list's order), `tests/acceptance/W2-55/` (planted repositories, child processes on this tree's `src/`, the semantic route unavailable).

The specification below fixes the public forms. It is the same text the engineer has.

{{SPEC}}

## The behaviour to test, by KPI line (FULL: thorough; every KPI line's success and failure and the edge cases the rows name, no combinatorial expansion)

1. KPI 1 (S1): a packet under pressure keeps `ticket_text` whole and verbatim and drops supplementary items first; every `ok: true` packet has `tokens <= budget.limit` and `budget.used == tokens`, at the default ceiling and at a `--budget` given; a ticket whose text is large but whose total still fits is served whole.
2. KPI 2 (S2): mandatory inputs alone over the ceiling refuse with `CONTEXT_OVER_CEILING`, `ok: false`, a non-zero exit, the details named, and with `--brief` no packet file written; one token under the line still fits. The failure KPI's DAEO-03pw shape: reproduce it in a planted repository (a ticket with those seven kinds of source and a register as large as this repository's), and show it fits or refuses, never `ok: true` over the ceiling. A case on this repository's own ticket is optional: if you write one, it reads the store of the tree it runs in, never rebuilds it, and your README says it needs that store (the lead rebuilds before verification; your tests worktree has no store).
3. KPI 3 (S3): a decision's `sha256` equals its entry's `content_hash` from the store, not the register file's hash; editing another entry leaves it unchanged, editing its own text changes it; its token cost is its span's (a ticket citing one short decision of a very large register fits).
4. KPI 4 (S4): equal packet hashes in one process, across two processes, and across two stores rebuilt from one commit, with planted ties in the supplementary block (identical text at different paths), the ties in `path` then `id` order; equal hashes with the semantic index unavailable and with it available. No network: the deterministic cases run with the semantic route unavailable; a case that needs a live local embedder is marked `local_only` and says in the README what it needs. The context check on a stale store (built from another commit than `HEAD`) is unmeasured by name and non-zero, or gives the fresh store's result; never green stale and red fresh.
5. KPI 5 and the failure line (S5): an unreadable or missing mandatory file, and a register entry whose span cannot be read, block or are marked `"read": false`, never shown read with the empty sha256 or 0 tokens; SUPERSEDED, RETIRED and REJECTED records each block a mandatory source, naming the status.
6. KPI 6 (S6): `supplementary_query` is built from the KPI lines and the title (it holds words of the KPI lines, it is not the first long word alone), and a planted document that matches only the KPI lines' words reaches the supplementary block.
7. KPI 7 (S7): with more matching evidence than one batch and room for it all, the stack holds more than one batch, in rank order; with less room, the stack stops at the first item that does not fit, and `further_batch` begins with that item, in rank order, holds no stacked item and is at most one batch long; with room for everything, `further_batch` is empty. A supplementary lookup failure is named in `dropped` by its kind.
8. The rows W2-M228 and W2-L219 (S8): the context check names an unheld file and stays red, with the accurate message when it is the only content; a ticket file named `.MD` or `.markdown` is named, never unseen; a duplicate id is named and not green.
9. S9 and S10 (rows W2-L183, W2-M134) are worth one case each if you can reach them through the public interfaces (for S10: planted notes that fail the validator are reported as failing in the packet, never as valid); if a behaviour cannot be observed from outside, say so in the README and write no test of internals.

## What you write

- Only inside `tests/acceptance/W2-04/` in this worktree, plus W1-24's acceptance cases (`tests/acceptance/W1-24/`), which the WBS names for revision in this ticket (WBS §2, "Revisions of files that an open ticket already holds ride in that ticket instead: … W2-04 W1-24's"): revise a W1-24 case only where this specification contradicts it (for example the packet's token count now including `ticket_text`, or a decision's sha256 now its entry's own hash), lower no other expectation, and name each such case with its reason. Any other earlier ticket's test that this specification contradicts (W2-54's, W2-55's, or any other): do not revise it; name it (file, case, why) in your return.
- No throwaway implementation is left in the tree.
- Behaviour through the public interfaces above, never internals. Deterministic, no network; each child-process call has a time limit. Tests that need a repository build a temporary one.
- A `README.md` that maps each KPI line (and each row) to its tests and gives the expected red reason of each, and says how the tests reach the code of the tree they run in.
- Test module names begin `test_w2_04_`; no test package or module may shadow a standard-library module; a `conftest.py`, if any, only for this folder.
- **Red first:** run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04-tests/src python3 -m pytest tests/acceptance/W2-04 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to its end (never `-x`); they fail for the reason the README states (the base has none of the new behaviour), and none fails for a defect of the test itself (a collection error, a typo, a missing fixture). A case the base already satisfies (rows fixed earlier, such as the RETIRED and REJECTED blocks) passes on the base: say which, in the README and your return. If you revised W1-24 cases, run `tests/acceptance/W1-24` too and report its counts.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, with the trailers in the final block; the W1-24 revisions, if any, in a commit of their own that also carries `--trailer "Rewrite-Reason: W2-04's KPIs (CAP-15.d, DEC-860): <the case and why>"`:

    git commit -m "W2-04: acceptance tests (independent test designer)" --trailer "Task: DAEO-u4oz" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-15.d, DEC-860" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After each commit, show `git log --oneline -3` and `git status --short`.

## Return

Your commits' hashes (12 digits); the test count; the KPI lines and rows with their tests; the red result as you saw it (counts, and the reason for each failing group); the cases that pass on the base and why; every earlier test you revised or would revise, with its reason; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; any P-R1 result you were served; any package.

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
