# Brief: engineer, DAEO-u4oz (W2-04), profile FULL, run 1

You are a fresh engineer. Ticket: `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`. You build the ticket to its specification and its KPIs, never to the tests.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-u4oz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-04` and `w2/W2-04`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return.
- **Memory used (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet (the machine's heavy-job slots were full; the lead rebuilds it before verification), so retrieve from the integration branch's store, a read: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. It holds `w2/integrate` as of its last refresh; this worktree is `w2/integrate` plus the ticket's claim, so read the files here for anything newer. Do not run `gov retrieve` in this worktree (it would answer STORE_MISSING). **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-04/`**, by any tool, here or in `/home/usain/gov-os-worktrees/W2-04-tests` or on any branch (`w2/W2-04-tests` included), nor any change the test designer makes to `tests/acceptance/W1-24/`; you may run the acceptance tests and see their names, results and failure messages; (d) the hidden half of any evaluation set (W2-61's measure's hidden half among them).
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/eng/` with the Write tool and run that file (if the Write tool refuses that folder, use your session's own scratchpad). A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one. No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 10 GB and 500,000 files and folders, outside the tracked tree. Keep the sandbox's own `TMPDIR` (do not set it yourself: the lead's temp folder is not writable inside the sandbox, and pytest would then write into the worktree; if a `pytest-of-*` folder appears in the worktree, say so). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- **Never `gov rebuild --no-embeddings`.** Do not rebuild this worktree's store yourself (the lead rebuilds it in a heavy-job slot, DEC-1001); if you need a fresh store, say so in your return. Tests that need a store build their own in a temporary folder.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, `docs/DECISION_REGISTER.md`, the plan files or `governance/project/path-map.yaml`. Never run `gov close`, `gov adopt` or `gov pause`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md` (read-only): its seven success KPI lines, its failure line and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-04`).
- The sources: CAP-15 and CAP-15.a to CAP-15.g (`docs/contract/CONTRACT_v4.md`); DEC-860 in `docs/DECISION_REGISTER.md`; DEC-135 (proportion), DEC-768 (the dropped list's one order), DEC-552 and DEC-568 (what no longer stands), DEC-866 (supersession).
- The list rows named in the specification, in `docs/plan/WAVE_2_LIST.md`, and their source lines in `governance/project/bootstrap.md`. **A row's state is re-checked against the code (DEC-718):** a row you find already fixed is reported with the commit that fixed it (`git log -S` on the guarding line); the lead's own look suggests W2-H034, W2-L088, W2-L180 and W2-M215 were fixed at `b0fd24d2` (W1-30 piece 11, DEC-552, DEC-568): confirm or correct it.
- The code: `src/gov/context/` (`__init__.py`, `command.py`, `context_check.py`), as W2-55 (merged) and W2-54 left it: keep W2-55's register filter (`left_out`) and `--in-force`, and W2-54's one order of `dropped`; do not undo them. And what it uses: `src/gov/retrieval/retrieve.py` (`retrieve()`, its batches and continuation tokens), `src/gov/retrieval/lexical.py`, `src/gov/retrieval/semantic.py`, `src/gov/retrieval/authority.py`, `src/gov/retrieval/synthesis.py` (`validate_notes`), `src/gov/store/loader.py` and `src/gov/records/queries.py` (the register entries' span and `content_hash`, W2-03), `src/gov/cli/main.py` (the output envelope and exit codes), the check `template/governance/kernel/checks/` entry that runs `gov.context.context_check` (its time limit).

The specification below fixes the public forms. It is the same text the test designer has.

## The specification (W2-04, run 1): the same text for the test designer and the engineer

Sources: the ticket's KPI lines (`.tickets/DAEO-u4oz.md`), CAP-15 and its items CAP-15.a to CAP-15.g (`docs/contract/CONTRACT_v4.md` §CAP-15), DEC-860 (retrieval in batches, ranked and stacked; never one giant query or context), W2-03's register entries (each decision with its own span and `content_hash`), and the list rows W2-H034, W2-L088, W2-L180, W2-L183, W2-L219, W2-M126, W2-M134, W2-M215, W2-M228, W2-M239, W2-M294, W2-M330 (`docs/plan/WAVE_2_LIST.md`; their sources are lines of `governance/project/bootstrap.md`: B:2340, B:1298, B:2341, B:2368, B:1300, B:1365, B:2339, B:2654, B:2782, B:1296). The public forms fixed below were settled by the lead inside the KPIs (a named error, three packet keys) so that tests and code written in parallel meet; anything not fixed here is the implementer's choice and is not tested.

The public interfaces: `gov context <ticket> [--json] [--budget N] [--brief] [--dry-run]` (`python3 -m gov.cli.main context …`, its JSON envelope `{"ok", "command", "result", "error": {"code", "message", "details"}}`, exit 0 on success, non-zero on an error); the in-process `gov.context.context(root, ticket, *, brief=False, budget=None, dry_run=False)`; the context-reproducibility check `python3 -m gov.context.context_check`, run in the project root (exit 0 green, non-zero otherwise, its lines on stdout); the store's records and register entries (`gov.records.records(root)` gives a register entry's `content_hash`, the sha256 of its span, W2-03).

**S1. The ceiling, and the ticket's own text (KPI 1; CAP-15, CAP-15.d).**
- The ceiling is `--budget N` tokens when given, else 6,000. A token is counted as the packet already counts it: the text's length in characters divided by 4, rounded up.
- Every packet that is returned with `ok: true` has `tokens <= budget.limit`, and `budget.used == tokens`. `tokens` counts the ticket's own text, every mandatory input's text as it is read (S3), and every supplementary item's text.
- The packet carries the ticket's own file text, verbatim and whole (front matter and body), under the key `ticket_text`. It is never dropped or shortened, whatever the pressure: under pressure the supplementary block is dropped first (CAP-15.d).

**S2. The refusal over the ceiling (KPI 2; AR-1, F-M5).**
- When the ticket's own text plus its mandatory inputs alone exceed the ceiling, `gov context` refuses: `ok: false`, error code `CONTEXT_OVER_CEILING`, a non-zero exit, a message that names the ticket, the ceiling and the mandatory size, and `details` holding at least `ticket`, `limit` and `mandatory_tokens`. With `--brief`, no packet file is written.
- It never returns `ok: true` with `tokens` over `budget.limit`, and supplementary items never take a packet over its ceiling.
- The failure KPI's case: DAEO-03pw (seven sources: DEC-070, DEC-088, DEC-092, DEC-096, MR-4, CAP-47, CAP-59; 814,821 tokens at the audit, because each decision was counted as the whole register) either fits (`ok: true`, under the ceiling) or refuses with `CONTEXT_OVER_CEILING`.

**S3. Each decision named by its own hash (KPI 3; W2-03, AR-1).**
- A mandatory input that is an entry of the decision register is read as its own span, never as the whole register file: its `sha256` (and its `constraint`) is the entry's own `content_hash`, the value the store gives for that id, and its token cost is its span's.
- Changing another entry of the register leaves its `sha256` unchanged; changing its own text changes it.
- A mandatory input that is a file of its own (a capability, a ticket, a specification) keeps its file's sha256, as today.

**S4. Reproducible (KPI 4; AR-9, W2-M239, W2-M294, W2-M330).**
- Two builds of one ticket's context give the same packet `hash`: in one process, in two separate processes, and on two stores each rebuilt from the same commit.
- The packet, and so its hash, is the same whether or not the semantic index answers (a live semantic index, or an unavailable one).
- Supplementary items of equal relevance (ties) are ordered by their `path`, then their `id`, whatever order the store, the index or the process gives them.
- The context-reproducibility check gives the same result on a stale store and on a fresh one, or it reports a stale store (built from another commit than `HEAD`) as unmeasured, by name, with a non-zero exit; it is never green on a stale store and red on a fresh one for the same tree.

**S5. An unreadable mandatory record (KPI 5; W2-H034, W2-L088, W2-M215, failure KPI).**
- A mandatory input whose file, or whose register span, cannot be read, or is missing, blocks the context (`BLOCKED`, non-zero exit, naming the id and the file) or is listed as not read (`"read": false`); it is never shown as read with the sha256 of empty content or with 0 tokens.
- A mandatory input whose record is SUPERSEDED, RETIRED or REJECTED does not satisfy the source: the context is `BLOCKED`, naming the id and its status.

**S6. The supplementary query (KPI 6; W2-M126).**
- The supplementary query is built from the ticket's KPI lines and its title, not from the title's first long word; the packet carries the query it used under the key `supplementary_query`.
- A planted document that matches only words of the ticket's KPI lines (none of its title's) can reach the supplementary block.

**S7. Batches, ranked and stacked; what is left is named (KPI 7; DEC-860).**
- The supplementary evidence is gathered by retrieval in batches, taken in order of relevance, and stacked in that order into the room the ceiling leaves after the ticket's text and the mandatory inputs. When room is left after one batch, the next batch is taken; the stack stops when the room or the evidence ends. No single query is asked for all evidence at once, and no batch is larger than the room can use.
- Stacking is strict rank order: it stops at the first item that does not fit; nothing ranked below an item that was left out is stacked.
- The packet names what it left for a further batch under the key `further_batch`: a list, in rank order, of `{"id", "path"}` of the ranked items that were not stacked for lack of room, beginning with the first one that did not fit, at most one batch long; an empty list when nothing was left.
- The `supplementary` block keeps its item form (`id`, `path`, `text`, `tokens`), in rank order. The `dropped` list keeps W2-54's form and its one order; a supplementary lookup failure is named there by its kind (W2-L180), never always as "index unavailable".

**S8. The context-reproducibility check's shapes (W2-M228, W2-L219).**
- A file of the ticket folder that the store holds no record of (a README, a ticket in a subfolder) is named and keeps the check red (it fails closed); when such files are the only content, the message says so, never "every ticket's context computation failed".
- A ticket file whose name ends otherwise than in lowercase `.md` (`.MD`, `.markdown`) is named and measured or refused by name, never unseen.
- Two ticket files that carry the same id are named as a duplicate id, and the check is not green.

**S9. One read of the ticket (W2-L183).** A context reads the ticket file once: its sources, dependencies, KPI lines, title and text all come from that one read.

**S10. Synthesis notes (W2-M134; CAP-15.f).** When the project holds synthesis notes (`.gov-runtime/synthesis/notes.json`), `gov context` runs their validator and acts on the result: notes that fail it are never presented as valid; the packet says whether they passed and names the failure codes. A project with no notes is unchanged.

**Never fail open.** An over-ceiling packet refuses; an unreadable record blocks or is marked not read; a stale store is not measured as fresh; a lookup failure is named, never hidden.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/context/**`, `src/gov/retrieval/supplementary*` (a new module there is yours, if you want one), `tests/unit/context/**`.
- **Read only, held by running tickets:** W2-13 holds `src/gov/retrieval/lexical*`, `src/gov/retrieval/fusion*`, `src/gov/retrieve/**` and `tests/unit/retrieval/**`; W2-92 holds `src/gov/retrieval/graph_route.py`, `code_route.py` and the route list in `src/gov/retrieval/retrieve.py`. You may call their public functions; you change none of their files. If your change needs one of them, stop and return it as a package. Prefer the narrowest, most stable call (W2-13 is changing the lexical side while you work): say in your return which of their functions you call.
- **S4's "with or without a live semantic index":** the packet must not depend on whether the semantic facet answers. Choose how (for example a supplementary block built only from the deterministic facets), say in your return what you chose and why, and what it costs in recall.
- **The context-reproducibility check on this repository:** it computes every ticket's context twice, and W2-55's lead found it red by its time limit once already. Time `cd /home/usain/gov-os-worktrees/W2-04 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m gov.context.context_check` once your build is committed (in the foreground; if it would pass ten minutes, time a sample of tickets instead and give the figure per ticket) and give the time and the result against the check's own time limit in your return. This needs this worktree's store, which is not built yet: if it is still missing when your build is committed, do not rebuild it; say so, and the lead measures these on the rebuilt store. Also give `gov context DAEO-03pw --json`'s outcome on this worktree's store (ok and tokens, or the error code) and the token figure of two or three other tickets, under the same condition.
- **Row W2-M133** (the check runner's provenance `inputs_hash`) lives in `src/gov/check/runner.py`, outside your paths: do not touch it; the lead names it.
- Builder tests in `tests/unit/context/` (your own test-driven development), as regression evidence only. Keep the existing ones green, or name each one this specification contradicts, with its reason.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows. Never make a check fail open: each failure KPI must still refuse. Estimate: about 220 lines of code and some builder tests.
- **DEC-866:** when something you touch still enforces a superseded decision, do not fix it silently and do not bend the code to it: name it in your return (old decision, new decision, file and line).
- **The acceptance tests (DEC-963):** the independent test designer writes them from the same specification, in parallel, in its own worktree. Build to the specification. **Commit your work before you run any long suite.** When your build is committed, look for `/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/TESTS-READY`: if it is there, run the acceptance tests once, reading results only, **through `gov accept` only**: `cd /home/usain/gov-os-worktrees/W2-04 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m gov.cli.main accept DAEO-u4oz --json` (pass or fail per KPI line and the counts; never a test's source, assertion text or traceback; never `pytest` on `tests/acceptance/` yourself). If it is not there, return: the lead merges the tests and resumes you. A test you think is wrong is returned as a package, never worked around; you never bend the code to a test against the specification.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-927 item 2: `Implements:` holds only decision and Contract ids the register and the store hold):

    git commit -m "<subject>" --trailer "Task: DAEO-u4oz" --trailer "Role: engineer" --trailer "Implements: CAP-15.d, DEC-860" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After each commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commits' hashes (12 digits); the files changed; the lines added and removed (code and tests apart); the builder tests and any `gov accept` run with their results; the rows and their state (fixed here, or already fixed at which commit); which W2-13 and W2-92 functions you call; your S4 choice; the context check's time and result, and the DAEO-03pw figure; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; anything you were refused or could not settle, as a package.

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
