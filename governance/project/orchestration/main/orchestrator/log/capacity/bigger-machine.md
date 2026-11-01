# CAPACITY-1, section 6: a bigger machine (4, 6 or 10 times this one)

Draft for the owner, 2026-10-31 15:30. Figures are marked **(M)** measured or **(E)** estimated. Scripts beside this
file: `load_tickets.py`, `measure_runs.py`, `sim.py` (the scheduler), `ready_now.py`.

## Answer first

- **A machine 4 times this one would bring Wave 2's close about 1 day sooner** (E): 11-05 evening instead of 11-06
  evening. If runs are slower and more numerous than the model assumes, the gain is about 2 days. EXAMIN's copy
  would start about 1 day sooner.
- **6 or 10 times adds 0 to 7 hours more.** There are never more than about 22 ready tickets at once, and the last
  2.5 days are one ticket after another.
- **The gain stops on one chain of tickets** (E): W2-108 → W2-13 → W2-15a → W2-32 (memory) → ACT 2 (the owner) →
  the three layers (1 day) → W2-27 (EXAMIN's copy) → W2-28 → W2-29 → W2-30 → W2-46 → W2-47. From ACT 2 onward it
  takes about 3 days on any machine. Owner decisions only move it where one lands in the night (02:00 to 07:30).
- **On today's machine, a change in scheduling gains about 17 hours** (E): keep the files of that chain's next
  ticket free, so that W2-13 does not wait about 19 hours for files held by other memory tickets. That is most of
  what a 4× machine buys, and it costs nothing. Together with a 4× machine, the close moves to 11-05 02:00 to 09:30.
- **Ready now: 13 of 61 remaining tickets** (M, 15:20): 11 can start, and 2 more are queued while the load gate
  holds them. 6 are running, 5 are closing, 3 wait on the files of a running or closing ticket, 27 wait on open
  dependencies and 7 wait on sequencing rules.
- **Cost** (date read 2026-10-31): a 4× rented server runs about €200 a month (Hetzner dedicated) or about
  $4.30 to $4.45 an hour (AWS, GCP), which is $720 to $750 for a week left running. Setting one up takes **1 to
  2 days of work** (E). That is about the whole gain for Wave 2, so it pays back only from Wave 3 on. Upgrading the
  PC's memory helps the memory gate but not the 4× CPU, and 64 GB of DDR5 now costs $880 to $1,150 (M, price
  trackers, Sep to Oct 2026).

## 1. The model (sim.py)

| Input | Value | Source |
|---|---|---|
| Remaining tickets | 61 W2 tickets + ACT 2 + the three layers; dependencies from `depends_on`/`deps`, plus 10 sequencing lines (W2-108→W2-13, launcher.py chain W2-56→60a→60b→82→21, W2-11→W2-33, W2-52→W2-23/W2-83a, W2-04→W2-55, W2-86→W2-91, W2-11 r1→W2-60a); K9: W2-27 after its 43 open dependencies and the three layers | tickets (M), PLAN-GROWTH-1 |
| Paths | two tickets whose `allowed_paths` overlap never run at once; package-wide sweeps (`src/gov/**/*.py`) are split by file (DEC-942 item 1) | tickets (M) |
| Run time at today's load | LITE 2.4 h, STANDARD 3.3 h, FULL 4.5 h | 117 lead runs (M): medians LITE 2.3–2.4, STANDARD 3.2–3.3, FULL 3.7 overall and 5.9 recently with gate waits |
| Runs per ticket | 2.5 to DONE; tickets already built: 1 to 2; merged: close only | 34 tickets done (M: median 2.5, mean 2.8) |
| Slowdown with load | the CPU-bound part of a run (~55 %, E) slows as W2-108's eight runs did: ×1.0 at load/processor 0.5, ×1.37 at 1.0, ×2.5 at 1.8, ×3.9 at 3.2 | W2-108 (M: 300 to 2,414 s at load 10 to 63); nightly 5,623 s alone vs 14,838 s shared (M) |
| Load per job | ~10 per running lead or close; today's 6 leads plus closes ≈ 60 on 20 processors | gate log (M: load 50 to 90) |
| Close | ~3 h at today's load | batch of ten: rebuild 2,370 s + run 3,744 s; batch of four: 1,641 + 6,082 s at load 60 to 90 (M) |
| Serial points | one store rebuild at a time (DEC-962); the CTO's 0.25 h per lead return | lock (M); 0.25 h (E) |
| Owner | one decision per STANDARD/FULL ticket, 0.5 h while awake; a package sent 02:00 to 07:30 is answered 09:30 (DEC-973) | latencies 6 to 58 min, median ~16 (M) |
| ACT 2, the three layers | 12 h + the owner's act; 1 day | (E) |

**Calibration warning:** on today's machine the model closes 7 to 19 tickets a day. The last 1.5 days measured
about 8 (12 DONE, M), and today's batch of four was refused at 15:19 with 11 reds. So the base case is optimistic.
The "slower" row (runs ×1.4, hours ×1.3) is the more cautious reading.

## 2. Results (start 2026-10-31 14:30)

| Machine, leads at once | EXAMIN copy starts | Wave 2 closes (W2-47) | Peak leads used | Mean leads, first 48 h / whole wave |
|---|---|---|---|---|
| **1×, 6 (today)** | 11-05 10:51 | **11-06 18:44** | 6 | 5.9 / 2.8 |
| 1×, 6, critical files kept free | 11-04 17:23 | 11-06 01:58 | 6 | 5.9 / 3.2 |
| **4×, 24** | 11-04 10:31 | **11-05 18:23** | 20 | 6.6 / 3.0 |
| 4×, 12 | 11-04 10:31 | 11-05 18:23 | 12 | 5.4 / 2.5 |
| 4×, 6 (no overload) | 11-04 10:31 | 11-05 18:23 | 6 | 4.4 / 2.2 |
| 4×, 24, critical files kept free | 11-03 19:27 | 11-05 09:30 | 18 | 5.8 / 2.8 |
| 6×, 36 | 11-04 09:30 | 11-05 17:22 | 20 | 5.2 / 2.4 |
| 10×, 60 | 11-04 09:30 | 11-05 17:22 | 20 | 4.7 / 2.2 |
| 10×, 60, critical files kept free | 11-03 18:12 | 11-05 02:05 | 18 | 4.7 / 2.5 |
| Unlimited machine | 11-04 09:30 | 11-05 17:22 | 20 | 4.5 / 2.1 |
| *Slower: 1×, 6* | 11-07 09:30 | *11-09 09:35* | 6 | |
| *Slower: 4×, 24* | 11-05 11:23 | *11-07 10:28* | 20 | |
| *Slower: 10×, 60* | 11-05 09:30 | *11-07 09:35* | 20 | |
| *Slower, critical files kept free: 1× / 4× / 6× / 10×* | 11-06 12:43 / 11-04 19:36 / 11-04 11:57 / 11-04 10:53 | *11-08 11:48 / 11-06 18:41 / 11-06 11:02 / 11-06 09:57* | | |

What the table shows:
- **Ready tickets rise and fall.** The number ready at once peaks at 22 to 25 in the first day and a half, then falls
  to 1 once only the chain is left. More than about 20 leads at once is never used.
- **More leads on one machine is not faster.** On 4×, 6 leads arrive as soon as 24 do. With critical files kept
  free, 6 leads even close 7 hours sooner, because fewer leads load the machine less and the chain's ticket runs
  faster. Most of the gain comes from runs that are not slowed by overload, not from more leads.
- **The owner's night turns hours into days.** A milestone that ends after 02:00 waits until 09:30 (ACT 2 on 11-03
  or 11-04, W2-47's final decision). This is why 6× and 10× gain about 1 hour, or 7 when the night is missed.

## 3. Ready now (15:20, ready_now.py)

| State | Count | Tickets |
|---|---|---|
| **Ready to start** | **11** | W2-04, W2-11, W2-37, W2-56, W2-81, W2-86, W2-92, W2-94, W2-97, W2-104; W2-61h stacked on W2-84 (closing, DEC-786) |
| Ready, queued; the load gate holds them | 2 | W2-105, W2-52 (the chain log at 15:19: load 26.8 / 43.7 ≥ 20) |
| Running | 6 | leads W2-05, W2-67, W2-95, W2-96 (+ its test designer), W2-107; W2-108 returned PACKAGES (its scoped check held 90 min by the load gate) and waits for the CTO |
| Closing | 5 | W2-49, W2-76, W2-84, W2-106 (batch refused 15:19: 11 reds traced to the change, investigation now); W2-16 merged |
| Held by a running or closing ticket's files | 3 | W2-109 (W2-49), W2-110 (W2-67), W2-20 (W2-16, W2-96) |
| Held by a sequencing rule only | 7 | W2-13 (after W2-108), W2-33 (after W2-11 r1), W2-60a (after W2-11 r1 and W2-56), W2-82 (launcher.py chain), W2-23 and W2-83a (after W2-52), W2-55 (after W2-04) |
| Held by open dependencies | 27 | of which W2-100, W2-101 also after ACT 2; W2-27 (K9) waits on 39 open; W2-46 on 54; W2-24 on 13 |

Pending owner decisions: CAPACITY-1 itself and ACT-NIGHTLY-0400 (the crontab and the Windows wake). Neither holds a
ticket.

## 4. Cost (prices read 2026-10-31, third-party listings unless stated; confirm before ordering)

This machine: 20 logical processors and 23 GB for WSL (M). The Windows host's total RAM is unknown here; I could not
read it from WSL.

| Size | Rented option | Price | One week, left running |
|---|---|---|---|
| 4× (80+ threads, ~96 GB) | Hetzner AX162-R dedicated: EPYC 9454P, 96 threads, 256 GB | €199/month + €79 setup (Hetzner page; a 2026 setup-fee rise reported) | ~€278 (the first month) |
| | AWS c7i.24xlarge: 96 vCPU, 192 GiB, us-east-1 | $4.284/h (~$3,127/month) | ~$720 |
| | GCP c3-standard-88: 88 vCPU, us-central1 | $4.44/h (~$3,238/month) | ~$746 |
| 6× to 10× (120 to 200 threads) | AWS m7i.48xlarge: 192 vCPU, 768 GiB | $9.68/h (~$7,064/month) | ~$1,626 |
| | GCP c3-standard-176: 176 vCPU | $8.87/h (~$6,476/month) | ~$1,490 |
| | 2 × Hetzner AX162 (192 threads; two hosts, so the work is split) | ~€398/month + setup | ~€560 |
| PC: memory | 64 GB DDR5 kit (if the board takes DDR5; DDR4 not priced) | $880 to $1,150 (Sep to Oct 2026, after the DRAM shortage) | raises the memory gate, not the CPU |
| PC: CPU | a top desktop CPU gives ~1.6× the threads, not 4×; 4× means a workstation or server board | not priced; a new machine is several thousand dollars (E) | |

Hetzner's cloud CCX line rose about 128 % in June 2026 (CCX63: 48 vCPU at €853/month), so the dedicated line is the
cheap one. Spot or 3-year AWS prices are lower (c7i.24xlarge ~$1.2 to $1.9/h) but can be withdrawn mid-run.

## 5. Effort and risk of a remote machine

- **What moves:** only the CPU-heavy parts: test runs (closes, scoped verifications), store rebuilds, gitleaks, and
  the embedder and rerankers (ollama), in clones on the remote. The Claude sessions mostly wait on the model and
  can stay on the PC. Moving them too would mean the Claude credentials leave the PC.
- **Work needed (E, 1 to 2 days, one ticket):** a remote runner for `close_build.py`, `verify_lock.sh` and the
  opaque runner (W2-96), so they run over SSH and bring back the result; the repository moved by git over SSH to a
  private bare copy on the server (a push off the PC is the owner's decision); ollama and the embedding models
  installed there (an embedder across the network would add a round trip per chunk, so it must run beside the
  rebuild); the same Python and tool versions; and the gate taught a second machine.
- **Secrets:** the gitleaks rules run before any copy; keys and tokens never leave the PC; the server is reached
  by SSH key only.
- **Held-out material must never be copied:** if any of it is in the tracked tree, a plain clone would copy it. The
  remote needs a filtered clone that leaves those paths out, checked before the first copy, and evaluations on the
  hidden half stay on the PC.
- **Owner risks:** runaway cost (an hourly server left on; set a budget alarm and a stop date), a public endpoint
  (SSH only, no open ports), and data residency (the code and the decision register sit with a provider; choose the
  region). A second machine also means a second place where a run can fail.

## 6. Recommendation for this section

Do not rent for Wave 2: the gain (about 1 day, at most about 2) is about the same as the setup work. Take the free
17 hours first: keep the critical chain's files free (W2-13 next, then W2-15a and W2-32) and do not raise the
number of leads at once. If Wave 3 keeps this size of plan, a dedicated 4× server (about €200 a month) is the
cheapest step. Size it for 4× and not more: past 4×, the gain stops on the chain and on the owner's night.
