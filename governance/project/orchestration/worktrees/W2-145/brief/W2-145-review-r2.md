Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-145/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-145 — the independent review (DAEO-2tfd), round 2 (the last)

You are a fresh, read-only independent reviewer. Review round 2 of **W2-145** (`.tickets/DAEO-2tfd.md`: read it in
full): no private reranker beside the shared service (DEC-1048 (5), DEC-1046 (1), DEC-1097 (8)). This is the last
review round (DEC-1010: at most two).

Round 1 was READY by its verdict block, but marked **S4 fail on F1**: with the pool on (`governance/project/retrieval.yaml`
`rerank_depth: 40`), a search the service cannot answer asked it twice (`retrieve.py:477` then `:576`), wrote two
`FALLBACK` lines and, on a refused start, started a second service and waited again (against P-1). The CTO took F1
into a round; F2 (a search arriving during the service's idle end) and F3 (stale "private" wording outside the paths)
are rows. Round 3 (`1be3e47de` on `w2/W2-145`) adds to `rerank.py` a memory of the service's failure, keyed by socket
path, interpreter and question and by the socket file's state at the failure: within `RECALL_S` (10 s) the same
question to the unchanged socket gets the first failure's reason at once, with no line, connect, start or wait.

## What to review
- `git diff e6f9bbaff..1be3e47de` in `/home/usain/gov-os-worktrees/W2-145`, and the whole branch against `w2/integrate`
  where you need it (`src/gov/retrieval/rerank.py`, the unit tests, `docs/changes/W2-145-evidence.md`).
- **The CTO's runs outside the sandbox** after round 3 are given to you in the line below (stand-ins only, a scratch
  HOME with no reranker environment, real-model cases excluded).

## Check
- **F1 fixed:** one `gov retrieve` with the pool on, against a service that cannot answer, gives one `FALLBACK` line,
  one start attempt at most and one wait at most; the bundle still names it unavailable with the reason.
- **Nothing new opened:** can the memory return a stale failure for a service that has come up (a new socket, a
  restart in place, a different question, after 10 s)? Can it ever return scores, or suppress a search's first ask?
  Is the memory bounded (pruned), thread-safe for concurrent searches in one process, and per process only?
- S1 to S6 still hold, as round 1 found.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes. Tests read-only (`-p no:cacheprovider`) through the
  heavy slot with `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty scratch HOME
  (with `PYTHONUSERBASE=/home/usain/.local`); Unix sockets are refused in your sandbox. No GPU; never the live service,
  its socket or the Ollama servers. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open
  anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words.
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per line, every finding with its two
  lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R2-F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S2" … "S6"]}`.

**The CTO's runs after round 3 (1be3e47de), outside the sandbox:** `gov accept W2-145`: pass {'passed': 79, 'failed': 0, 'skipped': 0}. The W2-145 acceptance folder, its unit file, `test_w2_112_shared_reranker.py`, `test_w2_32_rerank_fusion.py`, and the `tests/acceptance/W2-112`, `W2-32` and `W2-137` folders: 531 passed, 3 skipped, 0 failed.
