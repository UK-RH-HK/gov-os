Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the engineer's brief, round 3: the review's findings (DAEO-r30l)

You are a fresh engineer for **W2-20** (`.tickets/DAEO-r30l.md`). Round 2 and the designer's rounds 4 and 5 are on
`w2/W2-20` (head `4125133f4`): `gov accept W2-20` 163 passed, 0 failed, S16 skipped (S16's measured case passes outside
the sandbox); W2-136 76/76; W2-112's socket cases 37 passed. The independent review (round 1) is **NOT READY** on F1.
The CTO, as moderator, triages:

- **Fix (blocking):** **F1**: hold one machine-wide lock from the gate check until the session is registered (or
  register a provisional entry inside the same lock before releasing it), so launches that start together are
  counted against each other; a launch that ends before registering leaves no entry. A unit case starting several
  launches at once (stand-in CLI) shows that only those the memory rule admits start.
- **Fix too (cheap, in scope):** **F4** (a missing or malformed `oom_floor_bytes` is named, as S8 requires, never a
  silently skipped trip-wire); **F6** (an entry whose pid is alive but whose start time differs from the recorded
  `started` is stale and cleared; CPU history from before a restart is discarded at once instead of reading null);
  **F8** (a plan override is logged only once the gate admits the launch).
- **Rows, not this round:** F2 (the CPU rule's double count of the servers: the designer's stated interface; the CTO
  takes it up), F3 (S16's evidence: a designer revision, running beside you), F5, F7, F9, F10.

Add unit cases for each fix; update `docs/changes/W2-20-evidence.md` (F1, F4, F6, F8 and the rows named).

## The review's findings, as written (round 1)

**F1. Concurrent launches all pass the memory check.** `launcher.py:404` and `:390` run the check, then `_run` (`:457`) registers the session after `Popen`, with no lock in between. Several launches that start together each read the same session count, so each counts only itself as the new session. The memory rule then lets in up to k−1 sessions past its limit, at 2.04 GiB each. On this 23.5 GiB machine that limit is about 7–8 sessions.
Ordinary work: yes, because `launch_worker.sh` starts each worker with `setsid … &` and returns at once, and a CTO's parallel tool calls start launches at the same moment. Each check takes at least 0.25 s.
Consequence: fails open. scope: in (S19, S6).

**F2. The CPU rule counts the embedding servers twice.** `gate.py:92` adds busy cores, which already include the servers' current use, to each server's p95. That p95 is kept for a week, and each sample is an average since the previous reading. During store rebuilds the shared server's p95 can sit near 8 cores, so the gate shuts at about 12 busy cores of 20, whenever a rebuild runs. This is the designer's stated interface choice.
Ordinary work: yes, because rebuilds are frequent.
Consequence: other (honest launches falsely refused; the override exists). scope: in (S2, S12).

**F3. S16's evidence used the wrong share.** The case sets `share = affinity // slots`, which is 6. The slot's real CPU set is the 8 CPUs outside the servers' sets divided by 3, so 2 CPUs. Against the real share plus one (3), the recorded 3.13 is over. That figure counts the whole machine, including whatever else ran at the time. The confinement itself holds by construction (`sched_setaffinity`). So the KPI's aim is probably met, but the evidence does not show it.
Ordinary work: no, because this is about evidence, not product behaviour.
Consequence: other. scope: in (S16).

**F4. The trip-wire is silently off when `oom_floor_bytes` is missing or malformed.** `slots.py:366` skips the pass and says nothing. With today's file, every heavy job would run without a trip-wire.
Ordinary work: no, because the ACT required before merge writes the key; after that only a hand edit removes it.
Consequence: fails open. scope: in (S11, S8).

**F5. A listening socket with no readable owner reads as 0 CPU.** `machine.listener` returns None when no readable file descriptor holds the socket, and `embedding_cpu` (`:236`, `:253`) treats that as "not listening", 0.0 cores. A server run by another user would hit this.
Ordinary work: no, because on this machine both servers run as the user.
Consequence: fails open. scope: in (F5).

**F6. After a WSL restart, old state causes false refusals.** `machine.alive` ignores an entry's `started` time, so a reused pid counts as a live session with its working size until that process ends. Also, `cpu-stat.json` history from before the restart makes busy cores read as null ("the counters went back") for up to about a minute.
Ordinary work: yes, because `wsl --shutdown` kills launchers before their cleanup runs.
Consequence: other (fails closed). scope: in (S3, S2).

**F7. Two separate slot pools until the tooling moves.** `heavy_slot.sh` uses `/tmp/gov-os-heavy-slot-i.lock` and the product uses `~/.gov-os/machine/slots/`, so 3+3 heavy jobs can run at once. Neither `gov accept` nor `gov rebuild` takes a slot itself. S17's exclusion of the servers' CPUs leaves 2 CPUs per slot, against 6 today.
Ordinary work: yes, after the merge.
Consequence: other. scope: out (tooling and the decision).

**F8. A plan override is logged before the gate check runs.** `launcher.py:386–390`: if the gate then refuses, `launch.log` holds `OVERRIDE plan_override` for a lead that never started.
Ordinary work: yes.
Consequence: other. scope: in (S21).

**F9. Possible double count of the embedder's GPU share on WSL.** A GPU work kind with no listed process keeps its whole share (`gpu_room`). If WSL's `nvidia-smi` lists no compute processes, or names them so the kind reads as `other`, the embedder's share is held back on top of the free memory it already took. That would wrongly refuse a start that declares a GPU need.
Ordinary work: no, because no launch declares a GPU need today.
Consequence: other. scope: in (S14, S10).

**F10. The re-measure can only raise its figures, and nothing samples on a schedule.** `measure.remeasure` takes the largest of every sample ever kept (`samples.jsonl` is never trimmed). Nothing takes samples on a schedule, so the stale 2.04 GiB working size stays until someone samples by hand. That figure is named as due for re-measure, as S8 asks.
Ordinary work: yes.
Consequence: other. scope: in (S9).

## Verdict per line
- **Fail:** S6 and S19 (F1); S16 (F3, evidence only, does not block).
- **Pass with a non-blocking finding:** S2 and S12 (F2); S3 (F6); S7 (F7, out of scope); S8 and S11 (F4); S9 (F10); S10 and S14 (F9); S21 (F8); the F5 line (F5).
- **Pass, no finding:** S1, S4, S5, S13, S15, S17, S18, S20, F1, F2, F3, F4, F6.


## Where you work
- `/home/usain/gov-os-worktrees/W2-20`, branch `w2/W2-20`; your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`**: only `gov accept`'s results. Every Grep or Glob call that could reach it
  carries `!tests/acceptance/**`; recursive grep `--exclude-dir=acceptance`.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  your unit tests and `tests/unit/resources tests/unit/launch tests/unit/rebuild tests/unit/secrets_check`; then
  `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20` (about 18 minutes; in the
  background) and `accept W2-136`.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/` or any service; no GPU job. Never make a gate reading fail open.
- DEC-1080: Read and Grep tools; one simple command per Bash call. Search again once (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-20` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), each finding and what you changed, the new unit cases, the
unit, regression and `gov accept` counts with every red named.
