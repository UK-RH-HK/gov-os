# P1-REPIN-EMERGENCY: the emergency's query-side fixes reach agents only through a re-pin (draft, research agent, 2026-11-02 14:25)

For the owner (DEC-818's six parts). Asks for one decision (proposed DEC-1037), which changes DEC-954 Q8 (b), "ACT 2, one re-pin" (P-W2-110-4 cites it as item 6), under DEC-105: apply now. Estimates are marked *(est.)*.

## 1. Context

- `~/.local/bin/gov` is a symlink to `pin-5c401220/bin/gov`, whose first line names `pin-5c401220/bin/python`. That pin was installed from the wheel of `5c401220` on 28 Oct (sha256 `e4f35131…`). Its `gov/` package is byte-identical to `5c401220:src/gov` (checked with `diff -r`). `pin-6a4696eb` and `pin-fecb870c` are kept beside it, and so is `wheels/`.
- There are 862 commits from `5c401220` to `w2/integrate` (`a7182f6c`). They touch 60 `src/` files; `pyproject.toml` is unchanged. Since the 11-02 nightly's head (`9d605eba`), the only `src/` change is fix (b) (`semantic.py`, `ollama.py`).
- **Who runs the pin:**
  - every hook, all with `-E`, importing `gov` from the pin: PreToolUse (the five-rule hook), SessionStart (`gov.context.context`, which calls `retrieve`, then semantic and the reranker), Stop, SubagentStop, PreCompact;
  - the CTO's `gov retrieve` (`cd ~/gov-os-worktrees/W2-00-store && gov retrieve`, prompt §Retrieval);
  - auditors' and reviewers' `gov retrieve` (AUDITOR-common: bare);
  - any agent that follows the retrieval skill's bare `gov retrieve`.
- **Who does not run the pin:**
  - leads and their workers: retrieve, context, checks and launches use `PYTHONPATH=<tree>/src python3 -m gov.cli.main` (DEC-732, DEC-836);
  - rebuilds (`rebuild_slot.sh`, `seed_store.py`: `python3` with the tree's `src/`), `merge_queue.py`, `close_build.py` and the nightly, all on the clone's own `src/`;
  - the dispatcher and the log scan.

## 2. What happened

- ACT-QUERY-GPU-2 stopped at its pre-check, and that was right. The pin's `semantic.py` still has `NOT_ON_CPU` (line 55), `_on_cpu` (line 116) and the refusal at lines 186-187. The pin's `ollama.py` still starts the query server with `NO_GPU`. On the GPU, every pinned search would lose its semantic facet. Worse, a pinned search that finds the server down during the 10-second restart would start it again CPU-only.
- **18 frozen worktrees also hold the old gate in their own `src/`:** W2-04, W2-05, W2-104, W2-105, W2-11, W2-110, W2-114, W2-13, W2-55, W2-61h, W2-81, W2-86, W2-90b, W2-91, W2-92, W2-96, W2-97 and W2-126. Only W2-112, W2-122, W2-123 and EMG-query have fix (b). ACT-QUERY-GPU-2's rule already applies: each tree merges `w2/integrate` before its next search.
- The query server is on the CPU now (`size_vram` 0, 2.37 GB). The GPU uses 3.2 of 16.3 GB. Load is about 15.

## Assessment: fix → path to agents → needs the pin?

| Fix | Path to agents | Needs the pin? |
|---|---|---|
| (b) a question's vector from any device (`6ed6a5ae`) and the GPU kept on the query server's automatic start | pinned searches: the CTO, auditors, SessionStart context; trees after they merge | **Yes**, and it gates ACT-QUERY-GPU-2 |
| W2-123 bounded retry (landing ~15:00) | `semantic.py`/`ollama.py`: pinned searches; trees after merge; rebuilds through the tree | **Yes** for searches |
| W2-112 shared reranker (merge 17:30-18:30 *(est.)*) | `rerank.py` and `retrieve.py` inside the searching process | **Yes** for pinned searches; sandboxed sessions also need W2-127 |
| W2-126 vector cache (20:00-21:00 *(est.)*) | rebuilds through the tree at once; searches through `semantic.py` | **Yes** for searches only |
| W2-122 `gov rebuild --seed` | rebuilds run the tree's own code (`rebuild_slot.sh`, `seed_store.py`, `close_build.py`) | No |
| Interim rule: a reranker waits for a GPU slot, never the CPU (ACT-RERANK-WAIT-1) | a `.pth` in `reranker-venv`; it wraps every worker, the pinned one included | No (live) |
| Dispatcher v4.6, seeding (`seed_store.py`, `merge_queue.py`), `server_log_scan.py` | the CTO's tools on system `python3` | No (live) |
| ACT-QUERY-CPUS-1 (CPUs 8-11, nice 0) | server-side only | No (interim) |
| Other code a re-pin brings: W2-87 (authority order), W2-55 (the register's done and superseded entries left out), W2-108 (freshness and status worked out once per process), `gov accept` (W2-96), `gov release` (W2-16) | pinned searches and SessionStart context; bare `gov accept` (the pin has no `accept` today) | **Yes** |

**Verdict:** most of the emergency's agent-facing gains need the pin: the query on the GPU, the retry, the shared reranker and memory's quick wins, for every pinned search and every resume. Rebuilds and the CTO's tools already work.

## 3. Why it matters

- **DEC-1033 item 4:** fix (b) is "the vector from any device *and* the query server on the GPU". It cannot be in, and the emergency cannot be lifted, until the pin carries the code.
- **Measured today:**
  - query median 15 s, p95 53 s (09:00-13:00);
  - 8.8-10.1 s per question at 14:16;
  - target on the GPU: p95 under 1 s.
- **Pinned searches** never use the shared reranker. Each one loads a private 0.6B reranker, or waits up to 20 s for a slot, or goes unranked.
- **Memory's quick wins** (W2-87, W2-55, W2-108), measured by W2-61, reach the trees but not the CTO's searches or any session's resume context.

## 4. Options

### (a) Emergency re-pin from `w2/integrate`, in two windows (recommended)

**Window 1: ~15:30-16:15** *(est.)*, after the W2-122 and W2-123 landing is verified.
- Head H1 is that landing's commit, or a later commit that changes records only.
- It brings: fix (b), the retry, the quick wins, `gov accept`.
- ACT-QUERY-GPU-2 follows in the same window.

**Window 2: ~18:30-19:00** *(est.)*, right after W2-112 lands, with W2-112's own ACT, so the 19:30 after figures include it.
- Head H2. The delta from H1 is retrieval files only (the freeze lets only fixes land), so it carries little risk.
- W2-126 comes in if it has landed. Otherwise its search part waits for ACT 2: with the query under 1 s, it adds little to searches *(est.)*.

**(a′) Single re-pin at ~18:30:** one window less (about 45 minutes of the operator's time *(est.)*), but the query fix comes 3 hours later and the after figures slip.

**Procedure** (modelled on ACT-REPIN-2; in a plain terminal, not a Claude session, DEC-928 item 3). The CTO writes `pin/REPIN-COMMANDS-<H>.sh` and a registry script. `N=~/.local/share/gov-os/pin-<H>`.

1. **Before (the CTO):**
   - `git archive H`;
   - two reproducible wheel builds (`SOURCE_DATE_EPOCH` = H's commit time) with the same sha256;
   - the trailer gate clean;
   - refresh the integration store once by hand (seeded; it is at `6ebd7b56`).
2. **Regression, an emergency substitute for P-REPIN-2's fresh full run** (a full run cannot fit on this machine now):
   - the 11-02 nightly on `9d605eba`: 32 reds, all traced, none in the judge's guard code;
   - plus the delta's own tested and reviewed landings (fix b reviewed PASS; W2-122 and W2-123 through the merge queue);
   - tonight's 04:00 nightly then runs the whole suite on the re-pinned head, with the rollback ready.
   - This is a named deviation, for your decision.
3. **Install beside the old pin** (A1-A3 as ACT-REPIN-2): a new venv `--system-site-packages`, then `pip install --no-deps --no-index` of the wheel. The old pin stays untouched.
4. **Checks before the switch, through `$N` by its path:**
   - `$N/bin/gov --help` lists `accept` and `release`;
   - `grep -c NOT_ON_CPU $N/lib/python3.12/site-packages/gov/retrieval/semantic.py` prints `0`;
   - the dependencies import (`yaml`, `sqlite_vec`, `pytest`, `xdist`, `pytest_timeout`);
   - `cd ~/gov-os-worktrees/W2-00-store && $N/bin/gov retrieve "what decides a close" --json`: both facets available, the time noted;
   - `$N/bin/gov context DAEO-sdxk --json` and `--in-force`;
   - `$N/bin/gov launch --help` and `$N/bin/gov accept --help`;
   - SessionStart, Stop and PreCompact run with `$N/bin/python -E` on sample events: exit 0;
   - **the guard:** `guard4_check.py` (54 planted cases), `test_guard_fix_3.py` and `hook_timing.py`, run against `$N/bin/python`. All three read the interpreter from `~/.local/bin/gov`, so the CTO first adds a one-line `GOV_PIN_PY` override to each.
5. **Quiet point:**
   - no close and no nightly running, and no ACT in progress (DEC-1028 item 6: `log/act-in-progress.txt` written);
   - the W2-112 lead between batches;
   - `pgrep -af pin-5c401220` shows only sub-second hooks.
   - Processes in flight finish on the old code, because the old directory stays.
6. **Switch, atomically** (`ln -sfn` unlinks first, and a hook in that gap refuses):
   ```
   ln -s "$N/bin/gov" ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
   ```
   Then: `readlink -f`, `smoke_repin2.sh` (the exact hook line: allow, refuse, and refuse with no judge), one live tool call from the CTO session, and the registry commit (`Role: owner`, `Implements: DEC-1037`).
7. **Then ACT-QUERY-GPU-2:**
   - its Step 0 extended: `readlink -f ~/.local/bin/gov` names `pin-<H>`, and `$N`'s `semantic.py` has no `NOT_ON_CPU`;
   - wait for the old pin to drain with `timeout 300 sh -c 'while pgrep -f pin-5c401220 >/dev/null; do sleep 2; done'`. The interpreter path is in argv for gov commands and hooks, and an old pin's rerank worker shows the old pin's `site-packages` path;
   - then its steps 1-5, then the CTO sets `gpu_expected`.
   - GPU room *(est.)*: embedder 3.2 + query server 2.4 + W2-112's service 3.3 + one private reranker about 3.3, about 12.2 of 16.3 GB.

**Rollback, in one step:**
```
ln -s ~/.local/share/gov-os/pin-5c401220/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
```
Then revert the registry commit. **If ACT-QUERY-GPU-2 has run, undo it first** (its "Undo": the server back to the CPU). The old pin refuses GPU vectors.

**Running leads:** each session's next tool call runs the new judge's hook. Its next pinned search and its next resume use the new code. Leads' own verification is unchanged (it runs the tree's `src/`).

**Stores:** no rebuild is needed.
- Today's stores are built by head code (the W2-68 `fingerprints` table is present in the main store and in W2-00-store), and the new pin reads them natively.
- The query-vector cache keeps its table and key form: 91 and 102 `cpu` rows are reused, and `gpu` rows are added after the move. Rolled back, the old pin ignores the `gpu` rows.
- The freeze mirror's key is unchanged (sha256 of the git common directory).

**What changes for the guard** (the five-rule hook imports the pinned `reads`, `heldout`, `install` and `decide`):
- `_extract_bash_write_targets` and `_expand_token` are unchanged, so rules 1 and 5 are unchanged;
- `install.py` and `heldout.py` are unchanged, so rule 4 and the held-out rule are unchanged;
- `reads.py` gains W2-84: the hidden part under every tree and in the runs root, fail closed when a worktree cannot be listed or a folder cannot be walked. That strengthens rules 2 and 3. **Risk (medium-low):** new refusals, or time against the 20-second deadline with about 70 worktrees. `hook_timing.py` and `guard4_check.py` catch both before the switch;
- `decide()`'s freeze look-up by absolute git (W2-05) is used only by the template hook, which is not wired here;
- every signature the hook uses (`acting_role`, `_hidden`, `_Part`, `_Judge.tool`, `_ticket`, `HIDDEN_REFUSAL`, `_UNRESOLVABLE`) is the same.

**Other changes and their risk:**
- `gov close` and `check`, the batch and the fingerprints: not used by this repository's closes (`close_build.py` runs the clone's code). Low.
- `retrieve` JSON gains `left_out` and reorders results by authority: additive. Low.
- Packaging: `pyproject` is unchanged and the new packages have an `__init__`. Low.
- W2-110's three reds (P-W2-110-4) are **not** cleared: W2-110 is not on `w2/integrate`.

### (b) A narrow hot-patch of the pin's `semantic.py` and `ollama.py`

`75f18d11`'s diff applies cleanly to the pin's files (I checked with `git apply --check` on an export).
- **Cost:** about 15 minutes *(est.)*.
- **Risk:** the pin then matches no commit and no wheel, and the registry entry and its sha256 no longer hold. Any `pip` reinstall silently reverts it. The combination was never tested.
- **Better form (b2):** a side commit (`5c401220` + `75f18d11`, plus W2-123 later), built as a wheel. The pin then matches a commit and the guard is untouched. But W2-112's `retrieve.py` conflicts with W2-87 there, so a second narrow build would be needed for (a)'s gains, and memory's quick wins still never reach pinned searches.

### (c) Wait for ACT 2 (about 10-12 Nov, per P-W2-110-4)

- The query stays on the CPU for 8-10 days, on ACT-QUERY-CPUS-1's interim: target under 2 s, unmeasured.
- The shared reranker and the quick wins go unused by pinned searches.
- The emergency stays open unless you redefine fix (b) as done.

## 5. Recommendation

**(a)**, two windows. Confidence **medium-high**. The large judge delta is taken once, early in the evening, with hours to watch it. The guard's only behavioural change, W2-84's reads, is checked before the switch. The rollback is one rename, with the GPU move undone first.

If ACT-QUERY-CPUS-1 already gives under 2 s, the urgency drops, but not the need: the GPU move, the reranker and the quick wins still need the pin.

## 6. What it blocks, and what waiting costs

- **It blocks:** ACT-QUERY-GPU-2; fix (b) "in", so the after figures and the lifting of the emergency and the freeze (DEC-1033 item 4); W2-112's value for pinned searches; bare `gov accept`.
- **Waiting costs:** today 9-53 s per pinned question (median 15 s), against under 1 s *(est., the ACT's target)* for the CTO, auditors and every resume. Pinned searches keep loading private rerankers (warm p95 3.8 s through the service, measured by W2-112) or going unranked. Four CPUs stay held by the query server.
- **What the agents gain:**
  - questions answered in about 1 s *(est.)*;
  - retries instead of a lost semantic facet;
  - one shared reranker on the GPU (window 2);
  - authority-ordered results without the register's dead entries, at resume and in the CTO's searches;
  - `gov accept` as a bare command;
  - the hidden half refused under every tree.

**Your decision (proposed DEC-1037):** (a), (a′), (b2) or (c). Under (a), the CTO prepares the window 1 script and checks once the W2-122 and W2-123 landing is verified, and pings you for the plain-terminal ACT.
