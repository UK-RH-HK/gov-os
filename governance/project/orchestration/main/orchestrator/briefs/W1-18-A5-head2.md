You are the ticket lead for ticket `DAEO-1ve2` (`W1-18`, "Ollama on-demand lifecycle and fallback"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-18` on branch `w1/W1-18`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). STANDARD has no reviewer step.

## State of this ticket

- An earlier lead ran a first test batch: head `71651e81`, one test (no always-on unit), red as stated. Its checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; read it. It returned three packages, all decided now. They are recorded on `w1/integrate`, which this branch does not contain yet. In full:
  - **DEC-260 (DP-1, owner):** one function, `gov.retrieval.ollama.ensure_available(*, timeout_s, env=None)`. It returns `available`, `started`, `facet`, `state` and `warning`, and never raises when the daemon is unavailable. The executable comes from `GOV_OLLAMA_BIN`, then `ollama` on `PATH`, then `~/.local/ollama/bin/ollama`. The endpoint comes from `OLLAMA_HOST` (default `127.0.0.1:11434`); healthy means `GET /api/version` answers 200. The default total deadline is 20 s, covering the probe, the start and the wait for health. `src/gov/retrieval/__init__.py` is added to the ticket's `allowed_paths`.
  - **DEC-261 (DP-2, owner):** `gov` starts `ollama serve` on demand and never stops it; it sets no keep-alive override and creates no unit. Ollama's 5-minute idle unload frees the model's memory. There is no `stop`.
  - **DEC-257 (DP-3, delegated):** when Ollama is unavailable, the result names facet `semantic`, state `FACET_UNAVAILABLE` and a non-empty warning that names Ollama and says results are FTS-only; the warning is also written once to standard error. No file is written. The module does not set a bundle's stopping reason.
- Ollama is not on this machine's PATH. Nothing is installed. Tests are deterministic and use no outside network: a stand-in `ollama` executable (through `GOV_OLLAMA_BIN`) and a stand-in loopback endpoint (through `OLLAMA_HOST`) in a temporary directory.

## What you do, in order

1. **Test design batch 2** (brief A1, a fresh designer, profile STANDARD, DEC-221), with the three decisions above: about ten tests, every KPI line's success and failure plus the key edge cases (endpoint already up: nothing started; endpoint down and the stand-in starts: `started` true; no executable, or one that never becomes healthy: unavailable within the deadline with the facet state and the warning; the whole call returns well inside 30 s).
2. **Check red** yourself.
3. **Before the engineer starts, the ticket file in this worktree must carry the new allowed path**, because the guard reads it here. It arrives only by taking `w1/integrate` into this branch, and that is allowed only once the main orchestrator has resumed merges. Check: `git ls-tree -d --name-only w1/integrate tests/acceptance/ | grep W1-50`. 
   - If `tests/acceptance/W1-50` is listed, run `git merge w1/integrate` on this branch with a message whose last paragraph has `Task: DAEO-1ve2` and `Role: orchestrator`, resolve nothing by hand (if it conflicts, abort the merge and return PACKAGES saying so), and confirm `.tickets/DAEO-1ve2.md` lists `src/gov/retrieval/__init__.py`. The containment hook will flag that merge; it is a record, not a defect (DEC-254); mention it in your summary.
   - If it is not listed yet, write your checkpoint and return `LEAD_CHECKPOINT` saying "waiting for merges to resume"; do not start the engineer and do not edit the ticket file.
4. **Engineer** (brief A2, fresh). About 40 LOC; proportion rule DEC-135.
5. **Verify** every suite and the validator. Suites of tickets still in flight elsewhere (W1-08, W1-46, W1-49, W1-50) may be red on this branch from their own missing deliverables; confirm that and report them apart.
6. Return DONE with the whole ticket's summary. Learning metrics so far: KPI disputes 3 (DP-1 to DP-3).

