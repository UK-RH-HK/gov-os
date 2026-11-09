Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-56-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-56 — the independent test designer's brief, the second half: the guard-alone outcome (DAEO-wnnz)

You are the independent test designer for **W2-56** (`.tickets/DAEO-wnnz.md`: read it in full, with "The first half's
points settled" and the new "The guard-alone outcome (DEC-1112 (1))" section at its end). The first half's 157 cases
are in `tests/acceptance/W2-56/` (read its `README.md` first: the interface, the support module, the map and the "After
the experiment" table). This round writes the tests for the lines that table held back, now that the owner has
decided (DEC-1112 (1)): **W2-56 builds on the path-map guard alone, with today's launcher sandbox for workers
unchanged** (not generated from the path map; set-up B is a Wave 3 row). Profile FULL: every line's success and
failure, and the edges that fail open.

## What changed on the ticket (read the lines themselves; marked `[changed, DEC-1112 (1)]` or `[changed, DEC-1097 (8)]`)
- **S2, S3, F1:** the sandbox's write list stays today's (the session's temp folder, its run folder; the literal deny
  rules for `.gov-runtime/` outside scratch and, but for the test designer, `tests/acceptance/**`); nothing comes from
  the allowed paths. Write scope to the allowed paths (DEC-820 (4)) is the path-map guard's: a file-tool write or a
  Bash write the guard can name, outside them, is refused per worker role (`src/gov/guard/decide.py`, the hook in
  `template/governance/kernel/hooks/pretooluse.py`; drive it as event JSON, as earlier tickets' acceptance cases do).
  A name pattern (`test_batch*`) held by the guard's match, no sandbox entry made from it.
- **S11, F5 to W2-145's form** (merged: `src/gov/retrieval/rerank.py`, no private fallback; an unreachable service
  leaves the order unranked, named, one FALLBACK line in `rerank.log`, counted by `gov status`): a sandboxed session's
  unranked search must be counted where `gov status` counts, today lost because the session cannot write that log.
  The ticket leaves the way open (one log file on the write list, named, or another way): choose the interface, mark
  it *(choice)*, and give your recommendation.
- **Kept as written, now testable:** S1's sandboxed part (the daemon folder under the session's own temp folder),
  S7's `.git/*.lock` failure, S8 (the reranker's one socket in the sandbox block, from the same setting the service
  uses, DEC-1035 (2)), S9 (nothing else widens; `sandbox_faults` refuses any other change), S13 (gov check, gov rebuild
  and a suite inside the sandbox), F2's sandbox refusals (DEC-233's key, `sandbox_faults`, a sandbox that cannot be
  built), F4. S10 is the CTO's measurement (no case; map it `—` with "the CTO, outside the sandbox").
- If a changed line reads wrongly, untestably or against a decision, say so in a decision package with your
  recommendation and confidence; test the line as written meanwhile.

## How to test what only a real sandbox shows
- **Settings level first:** the `--settings` your stand-in CLI records (the first half's harness) shows the sandbox
  block: write list, deny rules, `network.allowUnixSockets`, `allowUnsandboxedCommands`, `strictAllowlist`. Most of
  S2, S3, S8, S9, F1, F2 and F4 is provable there, red or green on integrate for its own reason.
- **The operating system's refusal** (a script's write into another worktree, a second socket refused, S7's lock
  failure, S13's suite in the sandbox): where only a real sandboxed CLI session shows it, write **at most four** cases
  that start a real `claude -p` session through `gov launch` with one Bash command each (the cheapest model the CLI
  takes), skipped with a named reason unless `GOV_W2_56_REAL=1` is set; put `real_sandbox` in their names. The CTO runs
  them outside the sandbox. Say for each what it costs and what it proves that the settings-level case cannot.
- The planted reranker socket: a stand-in socket server under a planted HOME (W2-112's and W2-145's acceptance support
  show how), never the live service.

## Part 3: W1-27's cases (the designer's D-2, accepted)
Moving `DAEMON_BASE` breaks W1-27's W2-67 cases that hard-code `/tmp/gov-cbm-<uid>`
(`tests/acceptance/W1-27/test_w2_67_codegraph_folders.py`, `w2_67_codegraph.py`, `w2_67_codegraph_probe.py`). Revise
them so they hold both today and after W2-56's change: read the place through the interface you state for S1 (a name
in `gov.codeintel`, for example `DAEMON_BASE` or a function of the session's `TMPDIR`), keeping each case's own
claim. Each commit touching W1-27 carries `--trailer "Rewrite-Reason: DEC-1099 (1)"`. Show W1-27's W2-67 cases green
on integrate's code after the revision.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-56-tests`, branch `w2/W2-56-tests` (integrate merged in today, the
  ticket's changes with it). You write only `tests/acceptance/W2-56/` and the three W1-27 files above.
- Update the README: the new cases in the map (one id per KPI cell, full node ids, red or green on integrate and why),
  the interface section (add what the new cases assume: the sandbox block's keys and values, S11's count, the real
  cases' switch), and replace the "After the experiment" table with what this round did with each line.
- **Your record:** your whole return is your session's **final message**, in full: the launcher keeps it in this
  worktree's `.gov-runtime/scratch/lead/log/`.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)).** There is none yet on your branch: `src/gov/launch/`
  and `src/gov/codeintel/` there are today's integrate code, which you may read. Never open, grep or list the
  engineer's worktree (base name `W2-56`, `/home/usain/gov-os-worktrees/W2-56`) or the branch `w2/W2-56` if either
  appears; never `git show`, `git log -p` or `git diff` them.
- **The exclusion line (DEC-1093 (2)):** keep every Grep, Glob, find and recursive grep inside your own worktree, never
  from `/home/usain/gov-os-worktrees/` or `/home/usain/`; find carries `-path '*/gov-os-worktrees/W2-56' -prune` if it
  ever starts higher. If a search shows you a line of the implementation anyway, stop reading it and say so.
- **Search again once (DEC-1092 (1)):** two searches in all, then answer with path and lines or "not found".
- Planted folders only; no GPU, model, network or installs; never the live reranker service, `~/.local/bin`,
  `~/.gov-os/` or `~/.cache/gov-os/` for real.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, nor any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Run through the heavy slot that `EMG-common.md` names,** with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-tests/src`, your new files only first, then the whole
  `tests/acceptance/W2-56` once, then `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56-tests`
  (counts per line). Never the full suite.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-56-tests`, as you go, with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.
- Keep to the estimate: about 25 to 45 new cases, parametrised where the first half did.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the new case list (node id,
KPI line, red or green on integrate, and why), the W1-27 revision and its run, the commits, `gov accept`'s counts per
line, `TESTS-READY <head>`, and every decision package with your recommendation and confidence.
