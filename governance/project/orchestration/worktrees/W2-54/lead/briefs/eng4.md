You are a fresh engineer. Ticket: DAEO-0rfi (W2-54), profile FULL, round 3 (the owner allowed one more round, DEC-782 / P-W2-32 (a) and DEC-784 / P-W2-34 (a), 2026-10-18). You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. A previous engineer's change for this round is committed and its acceptance tests pass, but **the lead's measurement on this machine's real embedder is red**: you are given the failing output below, and you make the query vector deterministic on the real embedder. You were started through `gov launch`, under its OS sandbox.

## Step 0, before any work: the sandbox check (DEC-789)

Run these, in this order, and report their exact output **first** in your return (in `evidence`, and one line in `status`):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` — a write outside your worktree. It **must fail**.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work**, or you cannot commit. Quote the exit codes.

**If (a) wrote the file, or (b) failed, stop there:** do nothing else, write nothing, and return with status `PACKAGES` and the exact outputs. Never delete the file (a) may have made: name it in your return.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`), and `git log --oneline -1` (expect `b33ef9b3`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`, and run a long suite file by file.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write `governance/project/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS/`, its `.gov-runtime/` included) or another worktree; never touch another worktree under `/home/usain/gov-os-worktrees/` (other leads run beside you).
- **This machine's shared Ollama** is not reachable from inside your sandbox. When it is not, `gov` starts an Ollama of its own inside the sandbox (DEC-261), with this machine's executable and model: you may use that one through `gov`'s own code, and only through requests. Never stop, restart or reconfigure the shared server, never pull, remove or create a model.
- **What the lead runs, not you:** the full rebuild (`gov rebuild`), `gov check`, `tests/acceptance/W2-54/test_w2_54_green_here.py`, the cases marked `local_only`, W1-46's live cases, and the measurement on the shared embedder. Leave them out of your runs (`-m "not local_only"`, `--ignore=` for green-here) and say so.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.idea`, …): never commit them.
- **Rebuilds (DEC-719):** never run `gov rebuild --no-embeddings`, here or anywhere. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents, shell appends and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. The guard refuses your writes under `.gov-runtime/` (the scratch folder included): keep throwaway scripts in your session's temporary folder (`$TMPDIR`, given as a literal path), and give the lead any script it must run as text in your return. No subagents. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag.
- **Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`** (its sha256 stays `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`).
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines (success lines 3 and 4 are this round's) and its `allowed_paths`.
- The acceptance tests and their README (read-only): `tests/acceptance/W2-54/`, above all the README's "Round 2" and "Round 3" sections, `test_w2_54_query_vector.py`, `test_w2_54_query_cache.py`, `test_w2_54_sandboxed_worker.py`. They pass at `b33ef9b3` (the lead's run of the sandboxed case comes after your change); they must still pass after yours.
- This round's committed change: `77bf7cc7` (`src/gov/retrieval/semantic.py`, `tests/unit/retrieval/test_semantic_query_vector.py`) and `b33ef9b3` (`docs/changes/W2-54-CIT-E.md` §5). Keep what is right in them: the cache file, its key (model, revision, sha256 of the exact text), its atomic writes, its bound (`GOV_QUERY_VECTOR_CACHE_MAX_BYTES`, default 67108864 bytes, the older half evicted at the bound), a cache that cannot be read, written or created skipped silently.
- **The owner's decision for this round** (DEC-782, owner, 2026-10-18, P-W2-32 (a); staged, not in this worktree's register): a read command may write the query-vector cache and nothing else, within five limits (one derived file under `.gov-runtime/`; keyed by model, model revision and a hash of the exact text; atomic, safe with several sessions; bounded; rebuildable from nothing). **Deterministic where the cache cannot be written:** a cold, a full, a deleted and an unwritable cache all give the same vector for the same text. **The computation itself must be deterministic, and the cache only saves time.**
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-768, DEC-374, DEC-379, DEC-381, DEC-342, DEC-322, DEC-261, DEC-135, DEC-732.
- The code: `src/gov/retrieval/semantic.py` (yours to change), and to read only: `src/gov/retrieval/ollama.py`, `src/gov/retrieval/retrieve.py`, `src/gov/store/`, `tests/unit/retrieval/`.

## The failing output (the lead's runs on this machine's shared Ollama, outside the sandbox, at `b33ef9b3`)

**1. The previous engineer's measurement script** (through `semantic.query_vector`, 6 texts, each after other questions, a chunk without the instruction, the text alone, and the read repeated; cache cold, written, unwritable):

```
ollama 0.35.0 at 127.0.0.1:11434; qwen3-embedding:0.6b digest ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d
bound 67108864 bytes; cache .gov-runtime/query-vector-cache.db
cold       'context'                                    runs  12  differed   2  largest 0.002887
written    'context'                                    runs  12  differed  12  largest 0.002887
unwritable 'context'                                    runs  12  differed   2  largest 0.002887
cold       "The context packet's dropped list in a s"   runs  12  differed   2  largest 0.003281
written    "The context packet's dropped list in a s"   runs  12  differed   0  largest 0.000000
unwritable "The context packet's dropped list in a s"   runs  12  differed   3  largest 0.003281
cold       'who reads the harbour tide tables'          runs  12  differed   1  largest 0.002833
written    'who reads the harbour tide tables'          runs  12  differed   0  largest 0.000000
unwritable 'who reads the harbour tide tables'          runs  12  differed   2  largest 0.002833
cold       'the audit-report type exactly as W2-02 d'   runs  12  differed   2  largest 0.004074
written    'the audit-report type exactly as W2-02 d'   runs  12  differed  12  largest 0.004074
unwritable 'the audit-report type exactly as W2-02 d'   runs  12  differed   1  largest 0.004074
cold       'how is a query vector cached'               runs  12  differed   2  largest 0.002609
written    'how is a query vector cached'               runs  12  differed   0  largest 0.000000
unwritable 'how is a query vector cached'               runs  12  differed   2  largest 0.002466
cold       'café au lait'                               runs  12  differed   4  largest 0.005548
written    'café au lait'                               runs  12  differed   0  largest 0.000000
unwritable 'café au lait'                               runs  12  differed   3  largest 0.005548
ALL the read's vector: runs 216  differed from the text's first 50  largest component difference 0.005548
RAW the embedder alone, first after another question vs repeat: runs 18  differed 18  largest 0.004074
seconds 7.3; the writable cache holds 16384 bytes
```

So with the cache cold or unwritable, one text gets several vectors: the request shape `[INSTRUCTION, INSTRUCTION + question]` does not make the computation deterministic on the real embedder.

**2. The lead's probe of request shapes** (`T` = "how is a query vector cached"; 10 runs each, every second run preceded by another question's request of the same shape; "differed" counts runs whose vector differs from run 0's):

```
[I+t] (round 2)                            runs 10 differed  4 largest 0.002466
[I, I+t] second (round 3)                  runs 10 differed  8 largest 0.002466
[I+t, I+t] second                          runs 10 differed  3 largest 0.002466
[I+t, I+t, I+t] third                      runs 10 differed  2 largest 0.002466
[t] bare                                   runs 10 differed  4 largest 0.001719
[X, I+t] second, X unrelated               runs 10 differed  1 largest 0.002609
```

**3. The lead's probe of what decides the vector** (`[I+T]` alone, right after one request of the text named, three rounds; the vector's sha256, its first 10 characters, and the cases that gave it):

```
0ffecdbdfe 3 ['unrelated (shares I)#0', 'unrelated (shares I)#1', 'unrelated (shares I)#2']
4332c41b1b 6 ["shares I+'how is a'#0", "shares I+'how is a query vector'#0", "shares I+'how is a'#1", "shares I+'how is a query vector'#1", "shares I+'how is a'#2", "shares I+'how is a query vector'#2"]
5a4fc29484 3 ['shares nothing#0', 'shares nothing#1', 'shares nothing#2']
d326dafe53 3 ['itself (repeat)#0', 'itself (repeat)#1', 'itself (repeat)#2']
```

The lead's reading, for you to confirm or refute by your own measurement: the vector is reproducible for a given **prefix the text shares with the prompt the embedder computed just before it** (nothing; the instruction; a longer prefix; the whole text, a repeat), and differs between those cases, as if the embedder reused the computed prefix of the previous prompt. Within one request of several inputs the order or the sharing of that state is not guaranteed (shape 2's `[X, I+t]` still differed once in 10, with other sessions using the shared server at the same time). The machine's other sessions (other leads) use the same server concurrently.

**4. The context check at `b33ef9b3`, after a full rebuild (store digest `b0d5f5ba40a60fa4a8ca03261d0cb5eb53a84fefc1300da5922229a2e9b61cd9`), the cache cold:** `context-reproducibility: green`, exit 0, wall clock 2:31.45 (151.45 s), every ticket of this repository, load average 36.81 before and 14.84 after, 20 processors; it is green because the second computation of each context reads the vector the first one cached.

## What the ticket needs

1. **The same text gets the same vector on the real embedder, whatever was embedded before it, by this or any other process, with the cache cold, written, full, deleted or unwritable.** Find a computation that gives that on this machine's Ollama 0.35.0 with `qwen3-embedding:0.6b`, measure it on the Ollama you can reach (with requests of your own interleaved, as above), and keep it inside `src/gov/retrieval/semantic.py` (and `src/gov/context/**` only if needed). The acceptance tests that hold today must still pass (the round-2 case that a question asked for the first time is sent to the embedder once included). The vector a search uses must stay a vector of the question as the index's vectors are of their chunks (the same model, the same instruction for a question), so the retrieval's results stay fit for their purpose: W1-21's hit@5 measure (its pass line 80; 81.67 at `5f038b47`) runs on the real models, and the lead runs it.
2. **If no computation inside these paths can give it** (for example, if the variation depends on other clients' requests to the shared server in a way no request of yours can control), do not hide it: stop, keep what you have committed, and return a package (question, why now, options with their impact, reversibility and cost, recommendation, confidence), with your measurements as its evidence. Never weaken a check, a test or the cache's limits to make it pass.
3. **Builder tests** in `tests/unit/retrieval/` for the change (regression evidence only).
4. **The change record:** in `docs/changes/W2-54-CIT-E.md` §5 (keep rounds 1 and 2's text, correct §5.2 to what holds now, and say so): §5.5 records the lead's failing measurement above (items 1 to 4, the figures as given, the context check's run against `timeout-seconds: 600`), then what you measured and changed, and why the computation is deterministic now; leave a line "Measurement after the change on the shared embedder (run by the lead)" to be filled in. Name DEC-768, DEC-782 (owner, 2026-10-18, P-W2-32 (a)) and CAP-33.
5. **A measurement script for the lead** to run on the shared Ollama after your change: the previous engineer's script (read it at `/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/eng3-measure.py`; never write there; write your own if you prefer) extended to cover what decides the vector (texts sharing a longer prefix with the one before them, the text itself before it, and two processes reading at once). Give its full text and the exact command (with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src`) in your return; it writes only in a temporary folder of its own.

Proportion (DEC-135): no code for edge cases beyond the KPI lines.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/retrieval/semantic.py`, `tests/unit/retrieval/**`, `docs/changes/W2-54-CIT-E.md` (and if needed `src/gov/context/**`, `tests/unit/context/**`). If the fix needs a path outside them, stop and return a package naming the file.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.

## Order of work and the runs

1. Step 0, then the start checks.
2. Measure what decides the vector on the Ollama you can reach, then the change and the builder tests; run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit/retrieval tests/unit/context -q -p no:cacheprovider`, to its end, never `-x`; then `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_query_cache.py tests/acceptance/W2-54/test_w2_54_query_vector.py -q -p no:cacheprovider -rs`.
3. Commit the code and the builder tests (first commit), then the change record (second commit).
4. Then, each to its end, never `-x`, each with `timeout: 600000`, file by file where a suite runs long:
   - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -rs -m "not local_only" --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py`;
   - the same for `tests/acceptance/W1-19`, `tests/acceptance/W1-21` and `tests/acceptance/W1-24`, without the `-m` and `--ignore`.
   - If one of them fails only because your sandbox cannot do what it needs, say which case and why; do not count it as yours.
5. If something is red, fix it in a new commit (never amend) and repeat from the step it needs. The lead runs every other suite.

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

In the fields: step 0's outputs, first; your commits' hashes; the files changed; the lines added and removed (code and tests apart); what you measured on the Ollama you reached (its version, the runs, the figures); what decides the vector and how the computation is deterministic now; the measurement script's command (its full text after the twelve fields); the tests you ran with their results; the `gov.__file__` line; anything you were refused or could not settle, as a package.
