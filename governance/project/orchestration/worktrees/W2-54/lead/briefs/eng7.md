You are a fresh engineer. Ticket: DAEO-0rfi (W2-54), profile FULL, round 4c. You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. You were started through `gov launch`, under its OS sandbox. Round 4's code is committed and measured (`a93d5f72`, `a4801649`, `c53022d7`); six builder tests in `tests/unit/semantic/test_semantic.py` are red because that file's stub fixture was written for round 3's call shapes. The orchestrator's DEC-811 item 4 widened the ticket's allowed paths by that one file (`4662871a`), for **the stub's fixture only**. You change that fixture, and no other file.

## Step 0, before any work: the sandbox check (DEC-789)

Run these, in this order, and report their exact output **first** in your return (in `evidence`, and one line in `status`):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi','w').write('x')"` — a write outside your worktree. It **must fail**.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work**, or you cannot commit. Quote the exit codes.

**If (a) wrote the file, or (b) failed, stop there:** do nothing else, write nothing, and return with status `PACKAGES` and the exact outputs. Never delete the file (a) may have made: name it in your return.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0rfi`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`), and `git log --oneline -1` (expect `75049714`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed at 10 minutes: give long commands the Bash tool's `timeout: 600000`.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write `governance/project/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Never write the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS/`, its `.gov-runtime/` included) or another worktree; never touch another worktree under `/home/usain/gov-os-worktrees/` (other leads run beside you).
- This machine's shared Ollama is not reachable from inside your sandbox; you need no Ollama for this change. Never stop, restart or reconfigure any server you did not start, never pull, remove or create a model.
- **What the lead runs, not you:** the full rebuild, `gov check`, every acceptance suite, and every measurement on the shared embedder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. The sandbox may show placeholder files in the worktree (`.bashrc`, `.mcp.json`, `docs/source`, …): never commit them.
- **Rebuilds (DEC-719):** never run `gov rebuild --no-embeddings`, here or anywhere. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents, shell appends and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. The guard refuses your writes under `.gov-runtime/`: keep throwaway files in your session's temporary folder. No subagents. Install nothing. No push, merge, rebase or tag.
- Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`. Never edit `tests/acceptance/**`.
- The git hooks are uninstalled: before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## The change (DEC-811 item 4, decided)

In `tests/unit/semantic/test_semantic.py`, the `project` fixture's stand-ins gain round 4's call shapes, as the previous engineer verified in a temporary copy (6 passed, no change to `src/`):

```
-    def ask(path, body=None):
+    def ask(path, body=None, host=None):
         if path == "/api/tags":
             return {"models": [{"name": semantic.MODEL, "digest": endpoint["digest"]}]}
+        if path == "/api/ps":  # the CPU-only embedder reports the model wholly on the CPU (DEC-798)
+            return {"models": [{"name": semantic.MODEL, "size": 1, "size_vram": 0}]}
         endpoint["sent"] += body["input"]
         return {"embeddings": [[float("pear" in text), float("plum" in text)] for text in body["input"]]}
 
-    def ready(connection):
+    def ready(connection, ensure=None):
```

- Only the fixture: no test's assertion, no other test function, no other file. **`src/gov/retrieval/semantic.py` is never bent around the stub** (nothing under `src/` changes).
- If the diff above no longer applies as written, make the smallest equivalent change to the fixture and say how it differs.

## The runs, each to its end, never `-x`, each with `timeout: 600000`

1. Step 0, then the start checks and the `gov.__file__` line.
2. Before the change: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit/semantic -q -p no:cacheprovider` (expect 6 failed).
3. After the change: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider` — **all of `tests/unit`**, not only the semantic folder (the lead's lesson: a round that changes a call shape breaks builder tests outside the ticket's own folders). Expected: 0 failed. Name every failure, with its output; one you cannot fix inside this file and this fixture is a package.

## Commit

Commit only `tests/unit/semantic/test_semantic.py`, one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-54 (DAEO-0rfi): <subject>" --trailer "Task: DAEO-0rfi" --trailer "Role: engineer" --trailer "Implements: DEC-773" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, check `git log --oneline -2` and `git status --short`: a commit you did not make, stop and say so.

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

In the fields: step 0's outputs, first; your commit's hash; the diff's lines added and removed; the runs with their counts; the `gov.__file__` line; anything refused or unsettled, as a package.
