# W2-116 — the engineer's brief (DAEO-f58b)

You are the engineer for **W2-116** (`.tickets/DAEO-f58b.md`): the integration branch's store in the product,
double-buffered, refreshed after every merge into the integration branch, and the store every launched worker's
retrieval reads. The owner wants it built, tested and reviewed before re-pin window 4, which puts it live (DEC-1087
(3)).
- Read the ticket in full first, above all its **DEC-1087 (3) note** and its **TESTS-READY note**.
- **This pass:** S1, S3 (widened to every worker), S4 and S5, and the three failure lines. S2 is not this pass.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-116`, branch `w2/W2-116`: `w2/integrate` with the designer's
  cases merged in (`c3406602`).
- **Your paths:** `src/gov/rebuild/integration.py`, `src/gov/rebuild/command.py`, `src/gov/launch/store.py`,
  `src/gov/launch/launcher.py`, `src/gov/retrieve/command.py`, `tests/unit/rebuild/test_w2_116*`,
  `tests/unit/launch/test_w2_116*`, `docs/changes/W2-116-evidence.md`.
- **You never read `tests/acceptance/W2-116/`** (DEC-957, DEC-1056). Run those cases only through `gov accept W2-116`.

## The interface the tests assume (build to it)
1. **`gov rebuild --integration <branch>`,** run in the project. The link is the path `integration_store` names in
   `governance/project/rebuild.yaml` (W2-122's key). The two halves are detached worktrees beside the link. It builds
   into the half not in use, at the branch's head, seeded from the ready half (W2-122's seed), so only what changed is
   re-embedded. It switches the link (an atomic rename) only when the build succeeded, the semantic store recreated
   included. At an unchanged head it does nothing.
2. **A seed from a store behind the head** names the base's head commit (12 hex digits or more) and says `behind`. A
   seed at the head does not say `behind`.
3. **`gov launch`** sets an environment variable in the session's env (the launcher's settings `env` block) that a plain
   `gov retrieve` reads when no `--root` is given, so it answers from the integration store. A designer's retrieval
   never reads a ticket worktree's store.
4. **A re-index never empties the semantic index;** a model-less re-index reports the facet unavailable. A failed
   re-index leaves the previous index.

## What the CTO's tools did, which this replaces (read them)
- `.gov-runtime/scratch/orchestrator/tools/refresh_integration_store.sh`: the double buffer and the lock;
- `seed_store.py`;
- `rebuild_pinned.sh`: the rebuild with the code that searches; a search check before the switch.

**The product rebuild uses the code it runs under** (the ticket's note), so the pinned gov's store always matches the
pinned code.

## Tests and evidence
- **Unit tests** go in your two `test_w2_116*` paths, on planted git repositories with the stand-in embedder. No GPU,
  no model, never the real `~/gov-os-worktrees/W2-00-store`.
- **The evidence record:**
  - one row per KPI line of this pass;
  - how the double buffer keeps the ready half answering;
  - where a search's question-vector cache goes (the ticket's N-4);
  - the hook line the owner's operator installs in window 4 to run the refresh after a hand merge (state it; do not
    install it).
- **Every run** goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **`gov accept W2-116`:** run with `HOME=/home/usain` (no model is started). Report its counts.
- **Also run** `tests/unit/rebuild`, `tests/unit/launch` and `tests/unit/retrieve` with
  `-m "not local_only" -k "not real and not green_here and not time_limit"`.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **No GPU job.**
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.**
- **Commit** on `w2/W2-116` with
  `--trailer "Task: DAEO-f58b" --trailer "Implements: DEC-1087" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include:
- the diff's size;
- the unit tests;
- `gov accept`'s counts;
- the regression counts;
- the hook line for window 4.
