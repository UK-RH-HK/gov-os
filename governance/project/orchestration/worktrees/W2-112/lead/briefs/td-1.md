You are a fresh independent test designer (MR-3). Ticket: DAEO-clon (W2-112), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-112-tests` on branch `w2/W2-112-tests` (DEC-963). You never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-112`. You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with an engineer who builds from the same KPIs, and you show them red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-clon','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-clon`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-112-tests` and `w2/W2-112-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525); never read or name the qualification oracle; never print a secret (DEC-820 (a), (b)). Never list, glob, search or write in `~/gov-os-workbench` (DEC-723).
- **Policy 2 (c) and (d) (DEC-820):** reads are open, except: you never read this ticket's implementation (the files `git diff --name-only w2/integrate...w2/W2-112` names, other than your own tests, and anything in `/home/usain/gov-os-worktrees/W2-112`); and nobody reads the hidden half of an evaluation set (`fixtures/evaluation/*/hidden/`). You read the existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`) or in your own worktree (which is the ticket's base).
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, and only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && PYTHONPATH=/home/usain/gov-os-worktrees/W2-00-store/src python3 -m gov.cli.main retrieve "<question>" --json` (a read; never this ticket's worktree's store). **P-R1:** drop unread any result whose path lies under this ticket's implementation paths (`src/gov/retrieval/rerank.py`, `src/gov/retrieval/rerank_worker.py`, `src/gov/retrieval/rerank_service.py`, `tests/unit/retrieval/test_w2_112*`, `docs/research/W2-112-shared-reranker.md`) and name in your return any such result you were served. (The base versions of `rerank.py` and `rerank_worker.py`, as they stand on `w2/integrate`, are the existing public behaviour and you may read them with `git show w2/integrate:<path>`.)
- **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112-tests/src` set per command (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your tests must not hard-code any worktree path: once merged into the ticket's worktree and run there with that worktree's `PYTHONPATH`, they must exercise that worktree's code. Your README says how.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; put anything longer in a script file under `/tmp/gov-os-lead-W2-112/td/` and run that file.
- No subagents that write. Install nothing: a tool you need is returned as a package (P1). Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No clone, copy or programme file under a `.gov-runtime/` folder (DEC-673).
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A test that needs a repository builds a temporary one from scratch. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Scratch budget (DEC-898):** your share is 4 GB and 200,000 files and folders, outside the tracked tree. `TMPDIR=/tmp/gov-os-lead-W2-112` (keep the sandbox's own temp folder where it sets one, and count it). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed. Measure your scratch (`du -s --inodes`, `du -sh`) at the end and give the figures in `evidence`. Passing the budget: stop, clean, return.
- **No real model, no GPU, no network in the tests:** your tests must be deterministic and run on any machine, in a sandbox, without the real reranker environment and without the GPU. Never touch the shared Ollama servers (ports 11434, 11435) or the real `~/.local/share/gov-os/reranker-venv`; never take the real lock files `/tmp/gov-os-rerank-gpu-0.lock` or `-1.lock`. Point `HOME` at a temporary folder in every test that could start a reranker or a service, so nothing real is touched and no real service is started.
- Refused twice for the same call: stop and say so; no third try (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- An authentication or access error (401, 403, "Failed to authenticate"): stop and return with status `AUTH_REQUIRED`.

## What you read

- `.tickets/DAEO-clon.md` (read-only): its KPI lines (success and failure), `allowed_paths` and sources.
- The sources: in `docs/DECISION_REGISTER.md`, DEC-979 (item 4), DEC-374, DEC-397, DEC-1031 (item 2), DEC-1032; `docs/adr/ADR-0002*` §2; and `governance/project/orchestration/packages/P-RERANKER-1.md` (the owner's proposal this ticket implements: the socket's place, the lock, the idle end, the queue, the fallbacks), `governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md` (the GPU budget) and `governance/project/orchestration/packages/ACT-RERANK-GPU-SLOTS-1.md` (the stopgap the service replaces).
- Also: DEC-135, DEC-136, DEC-182, DEC-221, DEC-462, DEC-476, DEC-491, DEC-820, DEC-963.
- The existing public behaviour, as it stands on `w2/integrate`: `gov.retrieval.rerank` — `rerank(query, candidates, reranker=None)` (candidates in the order of their scores, each with `rerank_score`; equal scores keep the order given; with no reranker the candidates come back as given, without scores), `default_reranker()` (the loader of the pinned reranker; None when the environment is absent), `MODEL`, `REVISION`, `PYTHON_REL` (the reranker environment's interpreter under `HOME`: `.local/share/gov-os/reranker-venv/bin/python`, DEC-397). The reranker today runs from that interpreter, uses `sentence_transformers.CrossEncoder(MODEL, revision=REVISION)` and its `predict(pairs)`, offline (`HF_HUB_OFFLINE=1`). The search's bundle (`gov retrieve --json`, `gov.retrieval.retrieve`) carries `merge.reranked` (false when the order is unranked, DEC-374). Read no private part of an implementation to learn what a test should expect.

## The behaviour to test (in the words of the KPI lines and P-RERANKER-1)

1. **One process for every session:** the same pinned model, revision and environment as today; it listens on a local Unix socket in the user's own folder (P-RERANKER-1 names `~/.cache/gov-os/rerank.sock`), mode 0600, no network port; started on demand by the first search that needs it, under a lock, so two searches starting together start exactly one service; it ends itself after a set idle time.
2. **Many sessions at once:** 20 concurrent searches answered by that one process, each with its own scores for its own texts (never another's), in arrival order; a cap on a request's texts; a time limit per request.
3. **The same answers:** for the same inputs on the same device, the order and the scores match a private reranker's (within float rounding; ties keep the given order).
4. **Fallback:** if the service is down (cannot start, does not answer within about 2 s, or answers with an error), the search falls back to a private reranker as today; where that cannot start either, the fused order is kept and the result is unranked (no scores; the bundle's marking); a search never fails or hangs because of the service; each fallback is logged. (A killed service mid-run is the central case.)
5. **The GPU budget (DEC-1032):** the service checks free GPU memory before it loads; it never starts on the GPU when less than its share is free (it starts on the CPU, named, and alerts); never more than one copy on the GPU. The fallback private reranker runs on the CPU only when the service is down.
6. **Failure KPIs:** a search that fails, hangs, or returns another session's scores because of the service; two services started at once, or a socket another user can open; answers that differ from a private reranker's on the same inputs and device — each must be shown not to happen.

**How to test without the real model (your design; a suggestion):** a temporary `HOME` holding a stand-in reranker environment at `HOME/.local/share/gov-os/reranker-venv/bin/python` (for example a real `python3 -m venv` made in the temp folder, with a stand-in `sentence_transformers` package in its site-packages whose `CrossEncoder` accepts any arguments and keyword arguments and scores deterministically, for example from the texts, and which can record its device, its process id, and a delay). Make the stand-ins tolerant: the engineer may pass extra keyword arguments (such as a device) or call the model through the library's public API in another permitted way. Kill the service process (found through its socket's peer or through process listing filtered by your temporary `HOME`) to test the fallback. Mark such tests so they never leave a process running (a fixture that ends every process started under its `HOME`).

**Where the KPI's words need surfaces outside the ticket's allowed paths:** the bundle is built in `src/gov/retrieval/retrieve.py` and `gov status` lives in `src/gov/status/`, neither in this ticket's `allowed_paths`. The lead has raised this scope question as a package. Put the tests that need the literal bundle marking `rerank: unavailable`, the bundle naming the CPU, or `gov status`'s fallback count in a file of their own (for example `test_w2_112_surfaces.py`), and say in the README that they depend on that package; test everything else through `gov.retrieval.rerank`'s public behaviour and the socket. Measurements (memory, the real GPU, the 20 visible questions) are the research document's, not tests: do not test the real model or the GPU.

## What you write

- Only inside `tests/acceptance/W2-112/` in your worktree. No throwaway implementation left in the tree. Do not write `tests/acceptance/serial-only.txt` unless a test truly cannot run in parallel; if so, name it in your return.
- FULL: thorough, but no combinatorial expansion beyond what a KPI demands (DEC-221). Every KPI line gets at least one test, failure lines included. Keep the suite's run time reasonable (each test well under a minute; the stand-in's delays short).
- Behaviour through public interfaces, never internals. Deterministic, no network.
- A README that maps each KPI line to its tests and gives the expected red reason of each (against the base, where the service does not exist yet), and says how the tests exercise the worktree's own `src/` (DEC-732).
- Red first: run `TMPDIR=/tmp/gov-os-lead-W2-112 PYTHONPATH=/home/usain/gov-os-worktrees/W2-112-tests/src python3 -m pytest tests/acceptance/W2-112 -q -p no:cacheprovider` to the end, never with `-x`; they fail for the reasons the README states. Also run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-112-tests/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` and quote its last line: no collection error (no module name that shadows a standard-library or another test module).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). If a KPI requires revising an earlier ticket's acceptance test, name it; do not touch it.

## Commit

Commit only your test paths, in one commit (`git commit ... -- tests/acceptance/W2-112`), with the trailers in the final block:

    git commit -m "W2-112 (DAEO-clon): acceptance tests for the shared reranker service" --trailer "Task: DAEO-clon" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-979,DEC-374,DEC-1032" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`.

## Return

One message, your last, complete in itself. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put the sandbox check's result first inside `evidence`. Also give: your commit's hash (12 digits); the test count; each KPI line with its tests; the red reason as you saw it; the `gov.__file__` line; the collection line; every earlier test you would rewrite, with its reason; the read refusals you met (count); whether you used `gov retrieve` and how often; any P-R1 result you were served; your scratch figures.

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

Refused twice for the same call: stop and say so; no third try.
