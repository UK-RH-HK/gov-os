You are a fresh engineer. Ticket: DAEO-0rfi (W2-54), profile FULL, round 4 (DEC-798, owner, 2026-10-19, P-W2-40 (b)). You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. You were started through `gov launch`, under its OS sandbox. This round's change is committed (`a93d5f72`: the CPU-only query embedder in `src/gov/retrieval/ollama.py` and `src/gov/retrieval/semantic.py`, builder tests in `tests/unit/retrieval/`; `a4801649`, `c53022d7`: the change record §5.6). The lead's verification is red in the builder tests: you are given the failing output below, and you make it green without changing what the round built.

## Step 0, before any work: the sandbox check (DEC-789)

Run these, in this order, and report their exact output **first** in your return (in `evidence`, and one line in `status`):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` — a write outside your worktree. It **must fail**.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work**, or you cannot commit. Quote the exit codes.

**If (a) wrote the file, or (b) failed, stop there:** do nothing else, write nothing, and return with status `PACKAGES` and the exact outputs. Never delete the file (a) may have made: name it in your return.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`), and `git log --oneline -1` (expect `c53022d7`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`, and run a long suite file by file.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write `governance/project/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS/`, its `.gov-runtime/` included) or another worktree; never touch another worktree under `/home/usain/gov-os-worktrees/` (other leads run beside you).
- **This machine's shared Ollama** is not reachable from inside your sandbox, and the sandbox hides the GPU: every Ollama you can reach there runs on the CPU, so **no figure you take in the sandbox says anything about the shared GPU**. The lead measures on the shared GPU after your change. Never stop, restart or reconfigure any server you did not start, never pull, remove or create a model.
- **What the lead runs, not you:** the full rebuild (`gov rebuild`), `gov check`, `tests/acceptance/W2-54/test_w2_54_green_here.py`, the cases marked `local_only` or `shared_gpu`, W1-21's real-models hit@5 case, W1-46's live cases, and every measurement on the shared embedder. Leave them out of your runs and say so. Suites that need the code graph (`/tmp/gov-cbm-<uid>` is read-only in your sandbox: W1-20's code cases, W1-41's stage-A3 cases) fail in your sandbox for that reason alone: name them, do not count them as yours.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): never commit them.
- **Rebuilds (DEC-719):** never run `gov rebuild --no-embeddings`, here or anywhere. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents, shell appends and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. The guard refuses your writes under `.gov-runtime/` (the scratch folder included): keep throwaway scripts in your session's temporary folder (`$TMPDIR`, given as a literal path), and give the lead any script it must run as text in your return. No subagents. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag.
- **Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`** (its sha256 stays `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`).
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines and its `allowed_paths`.
- The round's change: `git show a93d5f72`, and `docs/changes/W2-54-CIT-E.md` §5.6.
- The failing builder tests (read-only for you: `tests/unit/semantic/` is **not** among the ticket's allowed paths): `tests/unit/semantic/test_semantic.py`.

## The failing output (the lead's verification at `c53022d7`, outside the sandbox)

`PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider` → **6 failed, 2177 passed, 1 skipped**:

```
FAILED tests/unit/semantic/test_semantic.py::test_only_a_file_whose_every_namespace_says_embedded_is_sent_and_found
FAILED tests/unit/semantic/test_semantic.py::test_a_chunk_is_embedded_as_its_first_512_characters
FAILED tests/unit/semantic/test_semantic.py::test_the_30_nearest_chunks_are_returned
FAILED tests/unit/semantic/test_semantic.py::test_a_refresh_embeds_only_what_has_no_vector_and_drops_what_is_no_longer_embedded
FAILED tests/unit/semantic/test_semantic.py::test_the_manifest_follows_the_model_list_and_another_embedder_builds_the_vectors_again
FAILED tests/unit/semantic/test_semantic.py::test_nothing_is_sent_or_stored_when_the_model_is_not_in_the_model_list

src/gov/retrieval/semantic.py:289: in refresh
    return _report(_build(Path(root)))
src/gov/retrieval/semantic.py:242: in _build
    revision = None if reason else _revision()
src/gov/retrieval/semantic.py:110: in _revision
    for model in (_ask("/api/tags", host=host) or {}).get("models") or []:
E       TypeError: project.<locals>.ask() got an unexpected keyword argument 'host'
```

(each of the 6 fails the same way). The test's fixture replaces `semantic._ask` with `def ask(path, body=None)`.

## What the ticket needs

1. **The builder tests in `tests/unit/` all green again,** with this round's behaviour unchanged: every acceptance case that passes at `c53022d7` still passes (the lead's run there: `tests/acceptance/W2-54` 7 failed / 87 passed, the 7 being two disputed clauses returned to the owner — leave them red; every other suite green). The fix is made **inside the ticket's allowed paths**: `src/gov/retrieval/semantic.py` (and `src/gov/retrieval/ollama.py` for the CPU-only embedder only, `tests/unit/retrieval/**`). **If the only right fix is in `tests/unit/semantic/`, which is outside the ticket's paths, stop and return a package naming the file and the change**, with your reasoning.
2. Never make a guard or gate decision fail open; the shared runner's requests stay without runner options; the CPU check after the computation stays.
3. A builder test in `tests/unit/retrieval/` only if it adds regression evidence the existing ones lack.
4. The change record: one sentence at the end of §5.6.3 in `docs/changes/W2-54-CIT-E.md` naming the fix, only if the code changed. Nothing else in the record changes.

Proportion (DEC-135): the smallest change that does it.

## The runs, each to its end, never `-x`, each with `timeout: 600000`

1. Step 0, then the start checks.
2. After the change: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider` (**all of `tests/unit`**, not only the retrieval folder); then `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -rs -m "not local_only" --ignore=tests/acceptance/W2-54/test_w2_54_green_here.py` (expect the same 7 red, nothing else), and `tests/acceptance/W1-18`, `W1-19`, `W1-21`, `W1-22` the same way without `-m`/`--ignore`, leaving out their real-models and `local_only` cases by name.
3. Commit the code (and any builder test) first, the record's sentence second.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-0rfi" --trailer "Role: engineer" --trailer "Implements: DEC-773" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In the fields: step 0's outputs, first; your commits' hashes; the files changed; the lines added and removed; the tests you ran with their results; the `gov.__file__` line; anything you were refused or could not settle, as a package.

