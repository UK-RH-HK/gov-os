# W2-20 — the narrow review (DAEO-r30l), DEC-1105's exception round: two points only

You are a fresh, read-only independent reviewer. The owner granted W2-20 one exception round to DEC-1010 (DEC-1105, the
register's last entry: read it). Review round 2 found W2-20 READY at `2bb6f70b6`; this review judges **only the two
points DEC-1105 opened**, nothing else:

1. **S16's measure** (`tests/acceptance/W2-20/test_w2_20_measured.py`, the designer's round 8, commit `bdc5e0525`):
   does it now measure the slot, not the machine? The "with the slot" figure is the busy cores on the slot's own CPUs
   (the `cpuN` lines of `/proc/stat` for the CPU set the slot gave its programs); an escape check shows the CPUs
   outside the set gained no more than the background plus one core; the bar is unchanged (share + 1; no more than
   20 % slower; without the slot the suite must exceed the share). Is the case sound (sampling, the set it reads, the
   escape check), and does it judge S16's KPI line ("keeps the machine's busy cores within the slot's share plus one")
   fairly?
2. **R2-F1's fix** (`src/gov/resources/machine.py`, the engineer's round 4, commit `057926aa3`; the designer's case
   `tests/acceptance/W2-20/test_w2_20_stale_samples.py`, commit `f12b7e00a`): a server whose kept samples (its current
   pid, at most 600 s old) have all expired is sampled afresh before the cpu rule reads it, so the gate never refuses
   a launch for stale readings; an unreadable server still reads null and shuts on cpu (F5). The samples moved to
   `~/.gov-os/machine/embedding-cpu.jsonl` (a cache; round 3's `server-cpu.json` is ignored and deleted); the p95 keeps
   round 7's week span. Check: no stale reading can shut the gate; nothing new fails open (a fresh sample that cannot
   be taken, a restarted server, a growing file); the configuration format is unchanged from `28fbcfebf`
   (`git diff 28fbcfebf..HEAD -- src/gov/resources/config.py` is empty).

## What to read
- `/home/usain/gov-os-worktrees/W2-20`, branch `w2/W2-20`: `git diff 2bb6f70b6..HEAD` (the designer's round 8 and the
  engineer's round 4), `docs/changes/W2-20-evidence.md`'s round-4 section, the ticket's S12, S16 and F5 lines.
- **The CTO's runs outside the sandbox** are in the paragraph at the end of this brief.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes, and nothing under the real `~/.gov-os/` (tests read-only,
  `-p no:cacheprovider`, through the heavy slot; planted HOMEs only). No GPU job; never the Ollama servers or the
  reranker service. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything under
  `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict on the two points, every finding with
  its two lines and `scope: in|out`, and at the end the fenced `verdict` block with exactly two entries:
  `{"kpis": [{"kpi": "S16", "verdict": "pass|fail", "findings": [...]}, {"kpi": "R2-F1", "verdict": "pass|fail", "findings": [{"id": "R3-F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`.

**The CTO's runs outside the sandbox on round 4 (head 057926aa3):** S16 twice, each after the 1-minute load fell below 1.5: run 1 PASSED (the slot's own 2 CPUs p95 2.00, limit 3; outside the set median 0.52 against a background median 0.15, gained +0.38, limit +1; without the slot 20.00 gross, 19.77 net; time +1 %); run 2 PASSED (the slot's CPUs p95 2.00; outside gained +0.18; without 19.81 net; time +1 %). `gov accept W2-20` 170 passed, 0 failed, 1 skipped (S16, run by hand); `gov accept W2-136` 76/76; W2-112's socket cases 37 passed. The round-4 engineer's launch was itself refused once by R2-F1 on round 3's code ("cpu: reading null … could not be sampled") and admitted on the retry, as round 2's review described.
