Batch 5 of the same work: the KPI 3 evidence file. Your standing rules are those of
`/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/lead/briefs/eng-1.md` ("Standing rules", "Commit"), and of
the repair brief you ran (`eng-4.md`), unchanged: DEC-732, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src` per
command; never read `tests/acceptance/W2-122/`; no here-documents or variable write targets (write the file with the
Write tool); row W2-L423's rule (12-digit hashes; under `docs/` a full hash is allowed, but use 12 digits here too);
refused twice for the same call, stop and say so. Do not rebuild anything and do not run any measurement yourself.

Write `docs/changes/W2-122-evidence.md`, the implementer's evidence of KPI 3 (DEC-996 item 3 A), from the lead's
measurements below. It is a plain, honest record: say what was measured, how, on what, and what was **not** measured
and why. Keep it short (about 60 to 100 lines). It holds:

1. **What KPI 3 asks** (quote the ticket's third success line) and **how it was measured:** by the lead, in its own
   session (not a sandbox), on the shared embedding server (127.0.0.1:11434, `qwen3-embedding:0.6b`, revision
   `ac6da0dfba84`, the GPU), each rebuild through the machine's heavy-job slot (`rebuild_slot.sh`), the embedding
   requests counted by a pass-through proxy in front of the server (one per run: every POST to `/api/embed` and its
   number of inputs), the semantic stage's seconds read from the rebuild's own `timing.semantic_s`, and how many other
   rebuilds ran beside it sampled every 30 s from the process table.
2. **The figures** (a table):

| run | tree | seed | semantic_s | total_s | embed requests | chunks embedded | other rebuilds beside it |
|---|---|---|---|---|---|---|---|
| cold | new worktree at `800cca6fba83`, empty `.gov-runtime/` | none | 4709.2 | 4761.6 | 1701 | 54,425 | two others 74 % of samples, one other 25 % (158 samples); never alone |
| seeded, nothing changed | this worktree at `800cca6fba83`, its first rebuild | `seeded` from the cold run's tree; copied `.gov-runtime/store.db` and the code-graph home | 0.7 | 30.8 | 0 | 0 | two others (1 sample) |
| seeded, one file changed | a throwaway worktree at `800cca6fba83` with `docs/plan/WAVE_2_WBS.md` edited (one line appended) and one untracked file added | `seeded` from the same base | 20.3 | 57.7 | 10 | 320 (exactly that file's 320 chunks; the untracked file is not indexed) | one other (1 sample) |
| cold, first attempt (failed) | new worktree at `dda239e827fc` | none | — | 3013 s wall before failing | 1023 before the failure | 32,736 | one rebuild (itself) in every sample |

   Other stage seconds of the two seeded runs: record 4.0 / 5.1, lexical 0.6 / 2.0, secrets 7.2 / 9.3, codeintel
   22.5 / 26.1, compaction 1.9 / 2.4. Cold: record 6.2, lexical 17.4, secrets 15.2, codeintel 26.1, compaction 2.6.
   Wall times include the wait for a slot (cold: 5942 s wall, of which about 1,180 s waiting; seeded, one file:
   475 s wall).
3. **KPI 1 on this repository:** the seeded store of this worktree against the cold run's store, at the same commit:
   the rebuild digests are equal (`b5408db1250c7b8a…`), and all 54,425 chunk vectors are equal (each joined on its
   chunk id, path and lines, the vector compared by its sha256). Same commit, so this is the expected case; the
   planted-repository acceptance cases cover files added, changed and removed.
4. **Alone and with two others:** the machine had at least one other rebuild running throughout the measurement
   window (2026-11-01 23:00 to 2026-11-02 01:50), so no run is "alone" in the strict sense; the cold figure is a cold
   rebuild with two others beside it most of the time, which is the condition SIZING-1 describes (3,000 to 3,750 s
   with three at once); the seeded figures were taken with one and two others beside them. A cold rebuild strictly
   alone was **not measured** (it would need an idle machine and about 80 minutes of a slot). Say so plainly.
5. **The failed first attempt:** the shared server's runner was reloaded during the run; an embed request failed
   after 1,023 of about 1,700, and the rebuild answered `REBUILD_FAILED` naming the semantic store (KPI 5 doing its
   work: before this ticket it would have answered ok over a partial store).
6. **What the figures mean, briefly:** the seeded first rebuild's semantic stage took 0.7 s and 20.3 s against
   4,709 s cold, with 0 and 10 embedding requests against 1,701; the code graph is rebuilt from scratch either way
   (about 25 s: the copied code-graph home is replaced by the indexer, your batch-1 finding); a seed is refused, and
   the rebuild runs cold, wherever the running `gov` code differs from the base's (your fingerprint choice), so in
   this repository a worktree whose ticket changes `src/gov/**` does not seed (the first attempt's base, at
   `dda239e827fc`, could not have seeded this worktree after the repair commit).

Then commit only that file, after checking the hooks folder, with the trailers in the final block:

    git commit -m "W2-122: KPI 3 evidence, seeded against cold on this repository" --trailer "Task: DAEO-blwa" --trailer "Role: engineer" --trailer "Implements: DEC-1014, DEC-996" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Quote `git log --oneline -2` and `git status --short`, then run
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
once and report pass or fail per KPI line and the counts.

Return in the twelve fields first, each as a labelled line (task, status, work_completed, files_changed, evidence,
tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), any payload after them.
