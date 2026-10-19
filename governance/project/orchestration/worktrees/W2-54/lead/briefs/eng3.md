You are a fresh engineer. Ticket: DAEO-0rfi (W2-54), profile FULL, **round 3** (the owner allowed one more round, DEC-782 / P-W2-32 (a) and DEC-784 / P-W2-34 (a), 2026-10-18). You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. You implement the ticket's round-3 KPI lines until their acceptance tests pass. You were started through `gov launch`, under its OS sandbox.

## Step 0, before any work: the sandbox check (DEC-789)

Run these, in this order, and report their exact output **first** in your return (in `evidence`, and one line in `status`):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` — a write outside your worktree. It **must fail**.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work**, or you cannot commit. (`git update-index --refresh` printing nothing, or only lines about files that need an update, with exit 0, is "works"; quote its exit code.)

**If (a) wrote the file, or (b) failed, stop there:** do nothing else, write nothing, and return with status `PACKAGES` and the exact outputs. Never delete the file (a) may have made: name it in your return.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`), and `git log --oneline -1` (expect `5f038b47`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write `governance/project/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS/`, its `.gov-runtime/` included) or another worktree; never touch another worktree under `/home/usain/gov-os-worktrees/` (W2-52, W2-50 and W2-05 run beside you).
- **This machine's Ollama** is shared and, from inside your sandbox, not reachable (the test designer saw `curl http://127.0.0.1:11434/api/version` end with exit code 7). Do not try to work around that. Never stop, restart or reconfigure an Ollama server, never pull, remove or create a model.
- **What the lead runs, not you** (your sandbox cannot): the full rebuild (`gov rebuild`), `gov check`, `tests/acceptance/W2-54/test_w2_54_green_here.py`, the cases marked `local_only` (they start a real session through `gov launch`), W1-46's live cases, and every measurement on the real embedder. Leave them out of your runs (`-m "not local_only"`, `--ignore=` for green-here) and say so.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Rebuilds (DEC-719):** never run `gov rebuild --no-embeddings`, here or anywhere. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents, shell appends and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` yourself outside `.gov-runtime/scratch/eng3/` (what the code you write stores at run time is below).
- **Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`** (its sha256 stays `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`).
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines (success lines 3, 4 and 5 are new this round) and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 (W2-54).
- The acceptance tests and their README (read-only): `tests/acceptance/W2-54/`, above all the README's "Round 3" section, `test_w2_54_query_cache.py` and `test_w2_54_sandboxed_worker.py` (15 cases, 12 red now: the reasons are in the README). The rewritten W1-19 and W1-21 cases and their READMEs' "Rewrite (W2-54, DEC-782, 2026-10-18)" sections.
- Rounds 1 and 2's work, committed: `4f753c72`, `316f3655` (the stable `dropped` order, the `audit-report` type, `timeout-seconds: 600`, the change record), `e8255c8a`, `db9830d7`, `51f42284` (the stored query vectors in `.gov-runtime/query-vectors.db`, the change record §4). Keep all of it that the round-3 lines do not change.
- **The owner's decisions for this round** (staged for the owner's commit, not yet in this worktree's register; the ticket cites them as "owner, 2026-10-18, P-W2-32 (a)" and "P-W2-34 (a)"):
  - **DEC-782:** a read command (`gov retrieve`, `gov context`) may write the query-vector cache, and nothing else. DEC-379 is amended for this one file only. The limits, each a KPI of this round: (1) only that one derived cache file under `.gov-runtime/`, never anything authoritative; (2) keyed by model, model revision and **a hash of the exact text** (not the text itself); (3) atomic writes, safe when several sessions write at once (no torn or lost entry, no error, no lock left behind); (4) bounded in size (a stated bound, and what happens at it); (5) rebuildable from nothing: deleting the file changes no result.
  - **Deterministic where the cache cannot be written.** In a sandboxed worker, `.gov-runtime` is read-only. There the read must still give the same vector for the same text, so **the vector cannot depend on whether the cache was written**: a cold, a full, a deleted and an unwritable cache all give the same vector for the same text. The embedder gives one vector for a text right after a different text and another on a repeat (repeats are stable); **the computation itself must be deterministic, and the cache only saves time.**
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-768, DEC-374 (the embedder's revision is the digest Ollama's model list reports), DEC-379 (amended by DEC-782 for the cache file only), DEC-381, DEC-342, DEC-322 (only orchestrator-role sessions write the live `.gov-runtime/store.db`), DEC-135 (proportion), DEC-732.
- The code: `src/gov/retrieval/semantic.py` (yours to change), and to read only: `src/gov/retrieval/ollama.py`, `src/gov/retrieval/retrieve.py`, `src/gov/retrieval/lexical.py`, `src/gov/store/`, `tests/unit/retrieval/`.

## What the ticket needs

1. **A deterministic query vector,** in `src/gov/retrieval/semantic.py` (and `src/gov/context/**` only if needed): the same text gets the same vector whatever was embedded before it, by this or any other process, and whatever the cache's state (cold, warm, deleted, full, its folder or its file unwritable). The README's round-3 risk on concurrency says how the stand-in treats a computation split over two requests: design for it. It must hold on this machine's real Ollama (`qwen3-embedding:0.6b`) too, which the lead measures for you (item 5).
2. **The cache within DEC-782's five limits:** one derived file under `.gov-runtime/`, never the store and never anything tracked; keyed by the model, the model's revision (DEC-374, as round 2) and a hash of the exact text (no folding, no normalisation, no stripping; the text kept nowhere in clear); writes that are atomic and safe with several processes at once, leave nothing behind and never make a read fail or change its answer; a bound in bytes, read from the setting `GOV_QUERY_VECTOR_CACHE_MAX_BYTES` that the acceptance tests name (its default stated in the change record on a line naming the setting, as a whole number of bytes), with what happens at it chosen and stated by you; a cache that cannot be read, written or created is skipped silently and changes no answer. A failed or partial embedding call stores nothing, as round 2. Nothing is written when the index is missing, empty or stale (W1-19's and W1-21's cases on that stay green). No hard-block check is weakened (DEC-768 item 4); the facet's unavailable states stay as they are.
3. **Builder tests** in `tests/unit/retrieval/` (regression evidence only).
4. **The change record:** a new section in `docs/changes/W2-54-CIT-E.md` (keep rounds 1 and 2's text, correcting round 2's where round 3 changes it, and saying so): the cause (round 2's five reds and the owner's DEC-782; the determinism finding), the five limits as built (the file, the key, the writes, the bound and what happens at it, rebuilding from nothing), how determinism holds without the cache, and a placeholder subsection "Measurement on the real embedder (run by the lead)" that you fill in item 5. Name DEC-768, DEC-782 (owner, 2026-10-18, P-W2-32 (a)) and CAP-33.
5. **The measurement on the real embedder, in two sessions.** Write a measurement script at `/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/eng3/measure.py` (never committed) that, against this machine's Ollama at its default address and through your code's own public entry, shows for several texts (at least 5, each after at least 3 different preceding texts, and on repeats) whether the vector the read uses is the same bytes whatever came before, with the cache cold, with it written, and with it unwritable (a temporary project whose `.gov-runtime/` is made read-only, built in a temporary folder by the script itself, never this worktree's store and never the main tree's). It prints its raw figures (the largest component difference, the count of runs that differed). State in your return the exact command the lead runs (with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src`). The lead runs it outside the sandbox, with the context check's timing after a rebuild, and resumes this same session with the outputs: you then add both to the change record (the figures, the command, the Ollama version they print, the context check's seconds, tickets and load against the declared `timeout-seconds: 600`), and commit. If the context check's run no longer fits 600 seconds with a margin, return a package rather than raise it.

Proportion (DEC-135): no code for edge cases beyond the KPI lines; about 40 to 80 lines of code changed.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/retrieval/semantic.py`, `tests/unit/retrieval/**`, `docs/changes/W2-54-CIT-E.md` (and round 1's paths if needed: `src/gov/context/**`, `tests/unit/context/**`); plus your scratch folder `.gov-runtime/scratch/eng3/`. If the fix needs a path outside them, stop and return a package naming the file.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.

## Order of work and the runs

1. Step 0, then the start checks.
2. The change and the builder tests; run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit/retrieval tests/unit/context -q -p no:cacheprovider`, to its end, never `-x`; then `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_query_cache.py tests/acceptance/W2-54/test_w2_54_query_vector.py -q -p no:cacheprovider -rs`.
3. Commit the code and the builder tests (first commit).
4. Write the change record's section and the measurement script; commit the change record (second commit).
5. Then, each to its end, never `-x`, each with `timeout: 600000`:
   - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -rs -m "not local_only" --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py`;
   - the same for `tests/acceptance/W1-19`, and for `tests/acceptance/W1-21` (about 7 minutes) and `tests/acceptance/W1-24`, without the `-m` and `--ignore`.
   - If one of them fails only because your sandbox cannot do what it needs, say which case and why; do not count it as yours.
6. If something is red, fix it in a new commit (never amend) and repeat from the step it needs. The lead runs every other suite.
7. Return (first session). In the resumed session: item 5's figures into the change record, commit (third commit), return again.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-0rfi" --trailer "Role: engineer" --trailer "Implements: DEC-768" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After every commit, check `git log --oneline -2` and `git status --short`: a commit you did not make, stop and say so.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Nothing comes before the twelve fields. Refused twice for the same call, stop and say so.

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

In the fields: step 0's outputs, first; your commits' hashes; the files changed; the lines added and removed (code and tests apart); the cache's file, key, bound (default and setting) and what happens at it; how determinism holds without the cache; the measurement script's command; the tests you ran with their results; the `gov.__file__` line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).
