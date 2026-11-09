# W2-20 — the independent review (DAEO-r30l), round 2 (the last)

You are a fresh, read-only independent reviewer. Review round 2 of **W2-20** (`.tickets/DAEO-r30l.md`: read it in full,
every KPI line S1 to S21, the failure lines and the body's settled points): the machine-wide resource gate. This is
the last review round (DEC-1010: at most two): judge whether every line now holds.

Round 1 (its findings quoted at the end) was **NOT READY** on F1 (concurrent launches all pass the memory check). The
CTO, as moderator, ruled: round 3 fixes **F1**, **F2** (the CPU rule no longer counts the embedding servers twice: the
designer revised the cases first, round 7: `busy_cores_1m + max(0, p95(shared) − now(shared)) + max(0, p95(query) −
now(query)) < nproc`, with the reading `embedding_cpu_now`), **F4**, **F6** and **F8**; **the configuration format is
frozen from `28fbcfebf`** (the machine's file was written from it by ACT-GATE-CONFIG-2; a designer case pins it; round 3
must not have changed any key's name, nesting, value form or meaning); S16's case was revised (the slot's real share;
one background before the plain run, its median netting both runs); F3, F5, F7, F9, F10 are rows.

## What to review
- Round 3's change against round 2 and the designer's rounds 4 to 7 (`git log` on `w2/W2-20` in
  `/home/usain/gov-os-worktrees/W2-20` names the commits; `git diff c90771b74..HEAD` is round 3), and the whole branch
  against `w2/integrate` where you need it.
- **The CTO's runs outside the sandbox** are in the paragraph at the end of this brief.

## Check
- **F1:** launches that start together are counted against each other; no window between the check and the
  registration; a launch that ends early leaves no entry; the lock cannot be left held (a crash, SIGKILL).
- **F2:** the rule as the designer stated it, `embedding_cpu_now` measured over the same minute as the busy cores, an
  unreadable reading shutting the gate; a rebuild-like load no longer shuts it where real CPU room exists.
- **F4, F6, F8** as ruled; **the frozen format** (compare `src/gov/resources/config.py` and every reader of the file
  with `28fbcfebf`'s).
- Every KPI line and failure line still holds, as round 1 found; nothing new fails open.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes, and nothing that writes under the real `~/.gov-os/`
  (tests read-only with `-p no:cacheprovider`, through the heavy slot; planted HOMEs only). No GPU job; never the
  Ollama servers or the reranker service. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never
  open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words.
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per line, every finding with its two
  lines and `scope: in|out`, and at the end the fenced `verdict` block, one entry per line S1 to S21 and F1 to F6:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R2-F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`.

## Round 1's findings, as written

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


**The CTO's runs outside the sandbox on round 3 (head 2bb6f70b6):** S16's measured case, twice, each started after the 1-minute load fell below 1.5, background sampled once before the plain run and taken as the median: run 1 PASSED (background median 0.15, p95 0.70; with the slot 3.01 gross, 2.86 net; without 20.00 gross; time +1 %); run 2 FAILED by 0.003 (background median 0.10, p95 1.19; with the slot 3.10 gross, 3.003 net against share 2 + 1 = 3; time +1 %). In both runs the slot's programs ran on exactly 2 CPUs. `gov accept W2-20` and `W2-136` and W2-112's socket cases are running as you start (the engineer's sandboxed runs: W2-20 168 passed, 0 failed, 1 skipped; W2-136 76/76). Judge S16 on these readings: is the KPI line ('keeps the machine's busy cores within the slot's share plus one') met by the product, with the excess the measurement's (the planted suite's driver and the sampler outside the slot) or the product's?
