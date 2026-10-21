You are a fresh engineer. Ticket: DAEO-0rfi (W2-54), profile FULL, **round 2** (the owner widened the ticket for one more round, P-W2-30 (a), 2026-10-18). You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. You implement the ticket's new KPI line until its acceptance tests pass.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0rfi`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`), and `git log --oneline -1` (expect `4844e124`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000` and split a suite that runs longer (below).
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write `governance/project/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree's store (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/`) or another worktree's; never touch another worktree under `/home/usain/gov-os-worktrees/` (W2-50 and W2-05 run beside you, and the orchestrator's sweep runs in `sweep-0rfi`).
- **This machine's Ollama is shared** with the sessions beside you: use it only through requests (per-request `options` included). Never stop, restart or reconfigure the Ollama server, never pull, remove or create a model.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Rebuilds (DEC-719):** never run `gov rebuild --no-embeddings`. You may run the full rebuild `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main rebuild --json` in this worktree (about two minutes), and only that form. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` yourself outside `.gov-runtime/scratch/` (what the code you write stores at run time is below).
- **Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`** (its sha256 stays `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`).
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines (the second success line is new) and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 (W2-54).
- The acceptance tests and their README (read-only): `tests/acceptance/W2-54/`, above all the README's "Round 2" section and `test_w2_54_query_vector.py` (15 cases, 7 red now: the reasons are in the README).
- Round 1's work, committed: `4f753c72` and `316f3655` (the stable `dropped` order, the `audit-report` type, `timeout-seconds: 600` and the change record `docs/changes/W2-54-CIT-E.md`). Keep all of it.
- **The owner's decision for this round** (DEC-773, owner, 2026-10-18; staged for the owner's commit, not yet in this worktree's register; the ticket cites it as "owner, 2026-10-18, P-W2-30 (a)"):
  - Round 1's finding is accepted: the two computations of a ticket's context hold different items because the embedder returns a slightly different vector for a text when a different text was embedded just before it. Reproduced by the orchestrator: the first embedding of "context" after another text differed from its repeats by up to 0.001948 in a component. DEC-768's premise is corrected; the stable sort of the `dropped` list stays.
  - **The behaviour:** the same text always gets the same query vector. Query vectors are stored, keyed by the model, the model's revision and the exact text, and a stored vector is used whenever its key matches.
  - **Measured first:** whether an embedder setting (thread count, seed) also removes the variation, on this machine's Ollama, before the change, recorded in `docs/changes/W2-54-CIT-E.md` with the runs. **The stored vectors are used regardless** of what the measurement shows.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-768, DEC-374 (the embedder's revision is the digest Ollama's model list reports), DEC-379 (the semantic route's interface; "`refresh=False` never writes"), DEC-381, DEC-342, DEC-322 (only orchestrator-role sessions write the live `.gov-runtime/store.db`), DEC-135 (proportion), DEC-732.
- The code: `src/gov/retrieval/semantic.py` (yours to change), and to read only: `src/gov/retrieval/ollama.py`, `src/gov/retrieval/retrieve.py`, `src/gov/retrieval/lexical.py`, `src/gov/store/` (how the store's digest and the index's freshness are computed), `tests/unit/retrieval/`.

## What the ticket needs

1. **The measurement, first, before any code change.** On this machine's Ollama (`qwen3-embedding:0.6b`, through `/api/embed` as `semantic.py` sends a question: the model's instruction and the question), measure whether a per-request setting removes the variation: the default; a thread count (`options.num_thread`, e.g. 1 and the default); a seed (`options.seed`). For each setting, the same protocol: embed a text right after a different text, and its repeats, several times over (at least 5 runs each, with a few different preceding texts), and report the largest component difference between the first embedding after another text and the repeats, and whether any run differed at all. Keep the script under `.gov-runtime/scratch/` (never committed) and quote it, its command and its raw figures in the change record. The stored vectors are built whatever the result.
2. **The change, in `src/gov/retrieval/semantic.py` only** (DEC-773): the same text always gets the same query vector.
   - Query vectors are stored, keyed by the model, **the model's revision as Ollama's model list reports it at the time of the search** (DEC-374; the acceptance README's revision case explains why not the index's revision), and **the exact text** (no case folding, no whitespace or Unicode normalisation, no stripping); a stored vector is used whenever its key matches, and only then.
   - The first answer for a text is unchanged (the vector the embedder returns for it), and the vector stored is exactly the one that answer used (same bytes).
   - A failed or partial embedding call stores nothing, and the facet stays unavailable with no hit, as today.
   - Several processes may search one store at once (`gov check` runs checks side by side): when two compute the same key, one vector wins and every later search uses it; a write that loses or fails never makes a search fail or give a different answer from the stored one where one exists.
   - **Where they are kept:** in the project's own runtime folder (`<root>/.gov-runtime/`), never under `HOME`, never shared between projects or worktrees, never in another project's store. **Apart from the index and the record graph:** storing a query vector must not change the lexical or semantic index, their freshness or status, the record graph, or the store digest `gov rebuild` reports. **DEC-322** says only orchestrator-role sessions write the live `.gov-runtime/store.db`, and the retrieval's entry (so `gov context` and the context check) searches with `refresh=False`, which DEC-379 says never writes: keep the vectors **in a file of their own beside the store**, not in `store.db`, so that `store.db` is still written only by the sessions that wrote it before, and write nothing at all when the index is missing, empty or stale (W1-19's `test_a_search_that_may_not_write_reports_a_missing_index_and_writes_nothing` must stay green). State in the change record which file, why, and how DEC-379's and DEC-322's words stand beside it (the lead returns that text question to the owner as a package; it does not stop your work). If this cannot be done inside `semantic.py`, stop and return a package naming the path it needs.
   - No hard-block check is weakened (DEC-768 item 4); the facet's unavailable states (no `sqlite_vec`, no Ollama, no model, a stale index) stay as they are.
3. **Builder tests** in `tests/unit/retrieval/` (regression evidence only).
4. **The change record:** a new section in `docs/changes/W2-54-CIT-E.md` (keep round 1's text): the cause (round 1's finding, with its figures), the measurement (item 1: settings, runs, figures, the script and command, the Ollama version, the result), and the change (the key, where the vectors are kept, DEC-379 and DEC-322 as above), naming DEC-768, the owner's decision of 2026-10-18 (P-W2-30 (a)) and CAP-33.
5. **The context check's time limit still fits.** After the change, measure the context check again as round 1 did, **on a fresh index** (commit first, then the full rebuild, then: `uptime; nproc; /usr/bin/time -v env PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.context.context_check; uptime`, `timeout: 600000`), and add the run (seconds, tickets measured, load before and after, processors, the commit measured, the store's digest) to the change record. The declared `timeout-seconds: 600` stays unless the run no longer fits it with a margin; if it does not, return a package rather than raising it.

Proportion (DEC-135): no code for edge cases beyond the KPI lines; about 40 to 60 lines of code. Never make a check or a gate fail open.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/retrieval/semantic.py`, `tests/unit/retrieval/**`, `docs/changes/W2-54-CIT-E.md` (and round 1's paths, which you should not need: `src/gov/context/**`, `tests/unit/context/**`, the declaration's `timeout-seconds` line, `src/gov/check/schema.py`'s audit-report lines, the audit-report schema, `tests/unit/check/test_schema_audit_report*`).
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.

## Order of work and the runs

1. The measurement (item 1).
2. The change and the builder tests; run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit/retrieval tests/unit/context -q -p no:cacheprovider`, to its end, never `-x`; then `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_query_vector.py -q -p no:cacheprovider -rs`.
3. Commit the code and the builder tests (first commit).
4. Write the change record's section (measurement, cause, change); commit it (second commit).
5. The full rebuild (your commits staled the index; a stale index makes the context check falsely fast and green); then item 5's measurement; add it to the change record; commit (third commit).
6. The full rebuild again (your third commit staled the index); then, each to its end, never `-x`, each with `timeout: 600000`:
   - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_green_here.py -q -p no:cacheprovider -rs` (about six minutes: one `gov check`);
   - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -rs --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py`;
   - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider -rs` and the same for `tests/acceptance/W1-24`.
7. If something is red, fix it in a new commit (never amend), rebuild, and repeat from the step it needs. The lead runs every other suite.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-0rfi" --trailer "Role: engineer" --trailer "Implements: DEC-768" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After every commit, check `git log --oneline -2` and `git status --short`: a commit you did not make, stop and say so.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call, stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In the fields: your commits' hashes; the files changed; the lines added and removed (code and tests apart); the embedder-setting measurement (each setting, its runs, whether it removes the variation); where the vectors are kept and their key; the context check's run after the change (seconds, tickets, load) against the declared limit; the tests you ran with their results; the `gov.__file__` line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).
