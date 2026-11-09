# W2-145 — the engineer's brief, round 3: the review's F1 (DAEO-2tfd)

You are a fresh engineer for **W2-145** (`.tickets/DAEO-2tfd.md`). Rounds 1 and 2 are on `w2/W2-145` (head `e6f9bbaff`).
The CTO's runs outside the sandbox are green (`gov accept W2-145` 79/79, W2-112 52/52, W2-32 255/255). The independent
review is READY by its verdict block, but marks **S4 fail on F1**, which the CTO (moderator) takes into this round:

> **F1: with the pool on, a search the service cannot answer asks it twice and logs twice.** (S4, also P-1)
> `governance/project/retrieval.yaml:12` sets `rerank_depth: 40`. In `retrieve.py:477`, the pool's `rerank()` comes
> back unscored, so `pool_failed` is set and `pooled` stays None. Then `retrieve.py:576` calls `rerank(query, candidates,
> None)` again, which runs `default_reranker` → `_ask` a second time. Each `gov retrieve` therefore writes two FALLBACK
> lines (S4 asks for one line per search). It also waits twice: no answer within the time limit, about 2 × 30 s; start
> refused: the second attempt finds the lock free and starts a second service, with a second REFUSED line (when the
> refusal is "no GPU slot", a second 20 s wait, which P-1 forbids). Fix inside `allowed_paths`: in `rerank.py`, remember
> the service's failure for this process for a short window and return unranked with the same reason at once, with no
> second line.

**Your job:** fix F1 inside `src/gov/retrieval/rerank.py` (`retrieve.py` is not in the paths): within one search, a
second ask after the service's failure returns unranked at once with the same reason, writes no second `FALLBACK`
line, starts nothing and waits for nothing. Keep the window short and bounded (one search's span; state the value and
why), so a long-lived process asks a recovered service again on its next search. Add unit cases: two asks within the
window (one line, one start attempt at most, the second immediate), and an ask after the window (asked again). The
review's F2 (a search arriving during the service's idle end) and F3 are rows, not this round.

## Where you work
- `/home/usain/gov-os-worktrees/W2-145`, branch `w2/W2-145`; your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`** (W2-145's, and the revised W2-112 and W2-32 cases): only `gov accept`'s
  results. Every Grep or Glob call that could reach it carries `!tests/acceptance/**`; recursive grep
  `--exclude-dir=acceptance`. Unix sockets are refused in the sandbox; the CTO re-runs the socket cases outside.
- Update `docs/changes/W2-145-evidence.md`'s S4 row with the fix.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU; never the live service or the Ollama servers.
- DEC-1080: Read and Grep tools; one simple command per Bash call. Search again once (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-145` with
  `--trailer "Task: DAEO-2tfd" --trailer "Implements: DEC-1048, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Every run through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-145/src`. A small round; before you end, every run has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the window's value and why, the new unit cases,
the unit and `gov accept` counts you could run.
